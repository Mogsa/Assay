#!/usr/bin/env python3
"""V3 cross-family disagreement analysis.

Two modes:
  --find     Compute cross-family SD for v3 questions, print top 15.
  --analyze  After human rating, compute per-family MAE vs human.

Usage:
  python scripts/v3_disagreement.py --find
  python scripts/v3_disagreement.py --analyze
"""

from __future__ import annotations

import argparse
import statistics
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone

import httpx

BASE_URL = "https://assayz.uk/api/v1"
V3_CUTOFF = datetime(2026, 3, 31, tzinfo=timezone.utc)

# Agent family groupings — model-tier level, not company level,
# because Opus/Sonnet/Haiku behave very differently.
FAMILIES: dict[str, str] = {
    "Opus-1": "Opus",
    "Opus-2": "Opus",
    "Sonnet": "Sonnet",
    "Sonnet-2": "Sonnet",
    "Haiku": "Haiku",
    "Gemini-Flash": "Gemini",
    "Gemini-Pro": "Gemini",
    "GPT-54": "GPT",
    "GPT-54-Mini": "GPT",
    "Qwen-Coder": "Qwen",
}

AXES = ("rigour", "novelty", "generativity")
AXIS_SHORT = {"rigour": "R", "novelty": "N", "generativity": "G"}


# ---------------------------------------------------------------------------
# API helpers (pattern from generate-rating-report.py)
# ---------------------------------------------------------------------------


def api_get(client: httpx.Client, path: str, params: dict | None = None) -> dict:
    resp = client.get(f"{BASE_URL}{path}", params=params)
    resp.raise_for_status()
    return resp.json()


def fetch_all_questions(client: httpx.Client) -> list[dict]:
    """Paginate through all questions, return v3 only."""
    items: list[dict] = []
    cursor = None
    while True:
        params: dict = {"sort": "new", "view": "full", "limit": 100}
        if cursor:
            params["cursor"] = cursor
        data = api_get(client, "/questions", params)
        for q in data["items"]:
            created = datetime.fromisoformat(q["created_at"].replace("Z", "+00:00"))
            if created >= V3_CUTOFF:
                items.append(q)
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return items


def fetch_ratings(client: httpx.Client, question_id: str) -> list[dict]:
    """Fetch individual ratings for a question (unauthenticated = no blind gate)."""
    data = api_get(
        client, "/ratings", {"target_type": "question", "target_id": question_id}
    )
    return data.get("ratings", [])


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------


def rater_family(rater_name: str) -> str | None:
    """Map rater display name to family. Returns None for humans/unknown."""
    return FAMILIES.get(rater_name)


def compute_family_means(
    ratings: list[dict],
) -> dict[str, dict[str, float]]:
    """Compute mean R/N/G per agent family for one question."""
    family_scores: dict[str, dict[str, list[int]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for r in ratings:
        fam = rater_family(r["rater_name"])
        if fam is None:
            continue
        for axis in AXES:
            family_scores[fam][axis].append(r[axis])

    means: dict[str, dict[str, float]] = {}
    for fam, axes in family_scores.items():
        means[fam] = {
            axis: statistics.mean(vals) for axis, vals in axes.items() if vals
        }
    return means


def compute_disagreement(
    family_means: dict[str, dict[str, float]],
) -> dict[str, float]:
    """Cross-family SD per axis. Needs >= 2 families."""
    sds: dict[str, float] = {}
    for axis in AXES:
        vals = [fm[axis] for fm in family_means.values() if axis in fm]
        if len(vals) >= 2:
            sds[axis] = statistics.stdev(vals)
        else:
            sds[axis] = 0.0
    return sds


def find_most_divergent(
    family_means: dict[str, dict[str, float]], max_axis: str
) -> tuple[str, str]:
    """Return the two families most divergent on the given axis."""
    vals = [
        (fam, fm.get(max_axis, 0.0)) for fam, fm in family_means.items()
    ]
    vals.sort(key=lambda x: x[1])
    if len(vals) >= 2:
        return vals[0][0], vals[-1][0]
    return ("?", "?")


def get_human_rating(ratings: list[dict]) -> dict[str, int] | None:
    """Extract Morgan's rating if present."""
    for r in ratings:
        if r.get("is_human"):
            return {axis: r[axis] for axis in AXES}
    return None


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_find(client: httpx.Client, top_n: int = 15) -> list[dict]:
    """Find and display top-N highest-disagreement v3 questions."""
    print("Fetching v3 questions...")
    questions = fetch_all_questions(client)
    print(f"Found {len(questions)} v3 questions. Fetching ratings...")

    results = []
    for i, q in enumerate(questions):
        ratings = fetch_ratings(client, q["id"])
        if not ratings:
            continue
        family_means = compute_family_means(ratings)
        if len(family_means) < 2:
            continue
        # Skip questions with very few ratings — SD on 2 families is noisy
        if len(ratings) < 3:
            continue
        sds = compute_disagreement(family_means)
        max_axis = max(sds, key=sds.get)  # type: ignore[arg-type]
        low_fam, high_fam = find_most_divergent(family_means, max_axis)

        results.append({
            "id": q["id"],
            "title": q["title"],
            "disagreement": max(sds.values()),
            "sd_r": sds["rigour"],
            "sd_n": sds["novelty"],
            "sd_g": sds["generativity"],
            "max_axis": AXIS_SHORT[max_axis],
            "low_family": low_fam,
            "high_family": high_fam,
            "low_val": family_means[low_fam].get(max_axis, 0),
            "high_val": family_means[high_fam].get(max_axis, 0),
            "n_families": len(family_means),
            "n_ratings": len(ratings),
            "family_means": family_means,
        })

        if (i + 1) % 20 == 0:
            print(f"  processed {i + 1}/{len(questions)}")
        time.sleep(0.05)  # be polite to the API

    results.sort(key=lambda x: x["disagreement"], reverse=True)
    top = results[:top_n]

    # Print results
    print(f"\n{'='*90}")
    print(f"TOP {top_n} MOST-DISAGREED V3 QUESTIONS (cross-family SD)")
    print(f"{'='*90}\n")

    for rank, item in enumerate(top, 1):
        title = item["title"][:60].ljust(60)
        print(f"#{rank:2d}  {title}")
        print(
            f"     Disagreement: {item['disagreement']:.2f}  "
            f"(SD_R={item['sd_r']:.2f}  SD_N={item['sd_n']:.2f}  "
            f"SD_G={item['sd_g']:.2f})"
        )
        print(
            f"     Most divergent on {item['max_axis']}: "
            f"{item['low_family']}={item['low_val']:.1f} vs "
            f"{item['high_family']}={item['high_val']:.1f}  "
            f"({item['n_families']} families, {item['n_ratings']} ratings)"
        )
        print(f"     https://assayz.uk/questions/{item['id']}")
        print()

    # Summary stats
    all_disagree = [r["disagreement"] for r in results]
    if all_disagree:
        print(f"Overall: mean disagreement={statistics.mean(all_disagree):.2f}, "
              f"median={statistics.median(all_disagree):.2f}, "
              f"max={max(all_disagree):.2f}")
        print(f"Questions with 2+ families: {len(results)}/{len(questions)}")

    return top


def cmd_analyze(client: httpx.Client) -> None:
    """Compute per-family MAE against Morgan's ratings."""
    print("Fetching v3 questions...")
    questions = fetch_all_questions(client)
    print(f"Found {len(questions)} v3 questions. Fetching ratings...")

    # Collect questions where Morgan has rated
    human_items: list[dict] = []
    for i, q in enumerate(questions):
        ratings = fetch_ratings(client, q["id"])
        human = get_human_rating(ratings)
        if human is None:
            continue
        family_means = compute_family_means(ratings)
        human_items.append({
            "title": q["title"],
            "human": human,
            "family_means": family_means,
        })
        if (i + 1) % 20 == 0:
            print(f"  processed {i + 1}/{len(questions)}")
        time.sleep(0.05)

    if not human_items:
        print("\nNo human ratings found. Rate on assayz.uk first, then re-run.")
        sys.exit(1)

    print(f"\nFound {len(human_items)} human-rated questions.\n")

    # Compute MAE per family per axis
    family_errors: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for item in human_items:
        for fam, fm in item["family_means"].items():
            for axis in AXES:
                if axis in fm:
                    error = abs(fm[axis] - item["human"][axis])
                    family_errors[fam][axis].append(error)

    # Print MAE table
    print(f"{'='*72}")
    print("PER-FAMILY MAE vs HUMAN (Morgan)")
    print(f"{'='*72}\n")

    header = f"{'Family':<10} {'MAE(R)':>7} {'MAE(N)':>7} {'MAE(G)':>7} {'Overall':>8} {'N':>4}"
    print(header)
    print("-" * len(header))

    family_overall: dict[str, float] = {}
    for fam in sorted(family_errors.keys()):
        errors = family_errors[fam]
        maes = {}
        all_errors = []
        for axis in AXES:
            if errors[axis]:
                maes[axis] = statistics.mean(errors[axis])
                all_errors.extend(errors[axis])
            else:
                maes[axis] = float("nan")

        overall = statistics.mean(all_errors) if all_errors else float("nan")
        family_overall[fam] = overall
        n = len(errors[AXES[0]]) if errors[AXES[0]] else 0

        print(
            f"{fam:<10} {maes['rigour']:>7.2f} {maes['novelty']:>7.2f} "
            f"{maes['generativity']:>7.2f} {overall:>8.2f} {n:>4}"
        )

    # Best and worst
    if family_overall:
        best = min(family_overall, key=family_overall.get)  # type: ignore[arg-type]
        worst = max(family_overall, key=family_overall.get)  # type: ignore[arg-type]
        print(f"\nClosest to human: {best} (MAE {family_overall[best]:.2f})")
        print(f"Furthest from human: {worst} (MAE {family_overall[worst]:.2f})")

    # Per-axis summary
    print(f"\n{'Axis':<14} {'Mean MAE':>9} {'Most accurate':>15} {'Least accurate':>16}")
    print("-" * 58)
    for axis in AXES:
        axis_maes = {
            fam: statistics.mean(errs[axis])
            for fam, errs in family_errors.items()
            if errs[axis]
        }
        if axis_maes:
            mean_mae = statistics.mean(axis_maes.values())
            best_ax = min(axis_maes, key=axis_maes.get)  # type: ignore[arg-type]
            worst_ax = max(axis_maes, key=axis_maes.get)  # type: ignore[arg-type]
            print(f"{axis:<14} {mean_mae:>9.2f} {best_ax:>15} {worst_ax:>16}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--find",
        action="store_true",
        help="Find top-15 highest-disagreement v3 questions",
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Compute per-family MAE vs human ratings",
    )
    parser.add_argument(
        "--top", type=int, default=15, help="Number of items to show (default: 15)"
    )
    args = parser.parse_args()

    if not args.find and not args.analyze:
        parser.print_help()
        sys.exit(1)

    with httpx.Client(timeout=30) as client:
        if args.find:
            cmd_find(client, top_n=args.top)
        if args.analyze:
            cmd_analyze(client)


if __name__ == "__main__":
    main()
