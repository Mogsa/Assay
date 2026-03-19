#!/usr/bin/env python3
"""Generate rating analysis report for dissertation advisor.

Queries the Assay API, collects all rating and discussion data, and produces:
  - docs/analysis/2026-03-19-rating-analysis.md  (prose report)
  - docs/analysis/2026-03-19-rating-charts.html   (interactive plotly charts)

No auth needed. Run from repo root:
  python scripts/generate-rating-report.py
"""

from __future__ import annotations

import json
import logging
import math
import statistics
import time
from collections import defaultdict
from pathlib import Path

import httpx
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

BASE_URL = "https://assayz.uk/api/v1"
OUTPUT_MD = Path("docs/analysis/2026-03-19-rating-analysis.md")
OUTPUT_HTML = Path("docs/analysis/2026-03-19-rating-charts.html")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [report] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("report")

AXES = ("rigour", "novelty", "generativity")

# ---------------------------------------------------------------------------
# API helpers (mirrors rater.py pattern)
# ---------------------------------------------------------------------------


def api_get(client: httpx.Client, path: str, params: dict | None = None) -> dict:
    resp = client.get(f"{BASE_URL}{path}", params=params)
    resp.raise_for_status()
    return resp.json()


def fetch_all_questions(client: httpx.Client) -> list[dict]:
    """Paginate through all questions."""
    items: list[dict] = []
    cursor = None
    while True:
        params: dict = {"sort": "new", "view": "full", "limit": 100}
        if cursor:
            params["cursor"] = cursor
        data = api_get(client, "/questions", params)
        items.extend(data["items"])
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return items


def fetch_ratings(client: httpx.Client, question_id: str) -> dict:
    return api_get(client, "/ratings", {"target_type": "question", "target_id": question_id})


def fetch_graph(client: httpx.Client) -> dict:
    return api_get(client, "/analytics/graph", {"limit": 200})


def fetch_calibration(client: httpx.Client) -> dict:
    return api_get(client, "/analytics/calibration")


# ---------------------------------------------------------------------------
# Statistics (no scipy)
# ---------------------------------------------------------------------------


def _ranks(data: list[float]) -> list[float]:
    indexed = sorted(enumerate(data), key=lambda x: x[1])
    ranks = [0.0] * len(data)
    i = 0
    while i < len(indexed):
        j = i
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j + 1) / 2  # 1-based average
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j
    return ranks


def _norm_cdf(x: float) -> float:
    """Approximation of the standard normal CDF."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2)))


def spearman(x: list[float], y: list[float]) -> tuple[float, float]:
    """Spearman rank correlation coefficient + approximate p-value."""
    n = len(x)
    if n < 3:
        return 0.0, 1.0
    rx = _ranks(x)
    ry = _ranks(y)
    d_sq = sum((a - b) ** 2 for a, b in zip(rx, ry))
    rho = 1 - (6 * d_sq) / (n * (n**2 - 1))
    if abs(rho) >= 1.0:
        return rho, 0.0
    t = rho * math.sqrt((n - 2) / (1 - rho**2))
    p = 2 * (1 - _norm_cdf(abs(t) / math.sqrt(1 + t**2 / (n - 2)) * math.sqrt(n - 2)))
    return rho, p


def pairwise_mae(
    ratings_by_rater: dict[str, dict[str, float]],
    question_ids: list[str],
    axis: str,
) -> dict[tuple[str, str], float]:
    """Pairwise MAE between raters on a single axis over shared items."""
    raters = sorted(ratings_by_rater.keys())
    result: dict[tuple[str, str], float] = {}
    for i, r1 in enumerate(raters):
        for j, r2 in enumerate(raters):
            if i >= j:
                continue
            diffs = []
            for qid in question_ids:
                s1 = ratings_by_rater[r1].get(qid)
                s2 = ratings_by_rater[r2].get(qid)
                if s1 is not None and s2 is not None:
                    diffs.append(abs(s1 - s2))
            result[(r1, r2)] = statistics.mean(diffs) if diffs else float("nan")
    return result


def krippendorff_alpha(ratings_matrix: list[dict[str, float]]) -> float:
    """Simplified ordinal Krippendorff's alpha.

    ratings_matrix: list of dicts {rater_name: score} per item.
    Missing raters are simply absent from the dict.
    """
    # Collect all values
    all_values: list[float] = []
    for item in ratings_matrix:
        all_values.extend(item.values())
    if len(all_values) < 2:
        return 0.0

    n_items = len(ratings_matrix)

    # Observed disagreement
    do_num = 0.0
    do_den = 0.0
    for item in ratings_matrix:
        vals = list(item.values())
        m = len(vals)
        if m < 2:
            continue
        for i in range(m):
            for j in range(i + 1, m):
                do_num += (vals[i] - vals[j]) ** 2
                do_den += 1
    if do_den == 0:
        return 0.0
    d_observed = do_num / do_den

    # Expected disagreement (across all value pairs)
    de_num = 0.0
    de_den = 0.0
    for i in range(len(all_values)):
        for j in range(i + 1, len(all_values)):
            de_num += (all_values[i] - all_values[j]) ** 2
            de_den += 1
    if de_den == 0:
        return 0.0
    d_expected = de_num / de_den

    if d_expected == 0:
        return 1.0
    return 1.0 - d_observed / d_expected


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------


def collect_data(client: httpx.Client) -> dict:
    """Fetch everything we need. Returns a big dict."""

    log.info("Fetching questions...")
    questions = fetch_all_questions(client)
    log.info("  got %d questions", len(questions))

    log.info("Fetching graph...")
    graph = fetch_graph(client)
    log.info("  got %d nodes, %d edges", len(graph["nodes"]), len(graph["edges"]))

    log.info("Fetching calibration...")
    calibration = fetch_calibration(client)

    log.info("Fetching ratings (%d)...", len(questions))
    ratings_by_question: dict[str, dict] = {}
    for i, q in enumerate(questions):
        qid = q["id"]
        try:
            ratings_by_question[qid] = fetch_ratings(client, qid)
        except httpx.HTTPStatusError as e:
            log.warning("  ratings for %s failed: %s", qid, e)
        if (i + 1) % 20 == 0:
            log.info("  %d/%d", i + 1, len(questions))

    return {
        "questions": questions,
        "graph": graph,
        "calibration": calibration,
        "ratings": ratings_by_question,
    }


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------


def is_seed(q: dict) -> bool:
    return q.get("title", "").startswith("[Seed]")


def question_source(q: dict) -> str:
    return "seed" if is_seed(q) else "agent-generated"


def build_rater_axis_maps(
    data: dict,
) -> dict[str, dict[str, dict[str, float]]]:
    """Returns {axis: {rater_name: {question_id: score}}}."""
    result: dict[str, dict[str, dict[str, float]]] = {a: defaultdict(dict) for a in AXES}
    for qid, rinfo in data["ratings"].items():
        for r in rinfo.get("ratings", []):
            name = r["rater_name"]
            for axis in AXES:
                if r.get(axis) is not None:
                    result[axis][name][qid] = float(r[axis])
    return result


def build_graph_index(graph: dict) -> dict:
    """Index graph data by node id for quick lookup."""
    nodes_by_id = {n["id"]: n for n in graph["nodes"]}
    edges_from: dict[str, list[dict]] = defaultdict(list)
    edges_to: dict[str, list[dict]] = defaultdict(list)
    for e in graph["edges"]:
        edges_from[e["source"]].append(e)
        edges_to[e["target"]].append(e)
    return {"nodes": nodes_by_id, "from": edges_from, "to": edges_to}


def discussion_metrics(q: dict, gidx: dict) -> dict:
    """Extract discussion metrics for a question from the graph."""
    qid = q["id"]
    node = gidx["nodes"].get(qid, {})
    answer_count = q.get("answer_count", 0) or node.get("answer_count", 0)
    link_count = node.get("link_count", 0)

    # Review count: comments with verdicts on answers of this question
    review_count = 0
    for e in gidx["from"].get(qid, []):
        child = gidx["nodes"].get(e["target"], {})
        if child.get("type") == "comment" and child.get("verdict"):
            review_count += 1
    # Also check answers' children
    for e in gidx["from"].get(qid, []):
        target_node = gidx["nodes"].get(e["target"], {})
        if target_node.get("type") == "answer":
            for e2 in gidx["from"].get(e["target"], []):
                child2 = gidx["nodes"].get(e2["target"], {})
                if child2.get("type") == "comment" and child2.get("verdict"):
                    review_count += 1

    # Spawned: outbound "extends" edges from this question
    spawned = sum(
        1 for e in gidx["from"].get(qid, []) if e.get("edge_type") == "extends"
    )

    return {
        "answer_count": answer_count,
        "review_count": review_count,
        "link_count": link_count,
        "spawned_count": spawned,
    }


# ---------------------------------------------------------------------------
# Section builders (return markdown strings)
# ---------------------------------------------------------------------------


def section_frontier_ranking(data: dict) -> str:
    """Section 1: Did frontier_score surface the right content?"""
    questions = sorted(data["questions"], key=lambda q: q.get("frontier_score") or 0, reverse=True)
    lines = [
        "## 1. Did frontier_score surface the right content?\n",
        "### Top 10 by frontier_score\n",
        "| Rank | Score | Source | Title |",
        "|-----:|------:|--------|-------|",
    ]
    for i, q in enumerate(questions[:10]):
        fs = q.get("frontier_score") or 0
        lines.append(f"| {i+1} | {fs:.2f} | {question_source(q)} | {q['title'][:70]} |")

    lines.append("")
    lines.append("### Bottom 10 by frontier_score\n")
    lines.append("| Rank | Score | Source | Title |")
    lines.append("|-----:|------:|--------|-------|")
    bottom = questions[-10:]
    for i, q in enumerate(bottom):
        fs = q.get("frontier_score") or 0
        lines.append(f"| {len(questions)-9+i} | {fs:.2f} | {question_source(q)} | {q['title'][:70]} |")

    seed_scores = [q.get("frontier_score") or 0 for q in questions if is_seed(q)]
    agent_scores = [q.get("frontier_score") or 0 for q in questions if not is_seed(q)]
    lines.append("")
    if seed_scores:
        lines.append(f"Seed avg: **{statistics.mean(seed_scores):.2f}** (n={len(seed_scores)})")
    if agent_scores:
        lines.append(f"Agent-generated avg: **{statistics.mean(agent_scores):.2f}** (n={len(agent_scores)})")
    lines.append("")
    return "\n".join(lines)


def section_discussion_correlation(data: dict) -> str:
    """Section 2: Did high-rated questions produce more discussion?"""
    gidx = build_graph_index(data["graph"])
    questions = data["questions"]

    fs_list = []
    metrics_lists: dict[str, list[float]] = {
        "answer_count": [],
        "review_count": [],
        "link_count": [],
        "spawned_count": [],
    }
    for q in questions:
        fs = q.get("frontier_score")
        if fs is None:
            continue
        m = discussion_metrics(q, gidx)
        fs_list.append(fs)
        for k in metrics_lists:
            metrics_lists[k].append(float(m[k]))

    lines = [
        "## 2. Did high-rated questions produce more discussion?\n",
        "| Metric | Spearman rho | p-value | n |",
        "|--------|------------:|--------:|--:|",
    ]
    for k in ("answer_count", "review_count", "link_count", "spawned_count"):
        rho, p = spearman(fs_list, metrics_lists[k])
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        lines.append(f"| {k} | {rho:+.3f}{sig} | {p:.4f} | {len(fs_list)} |")
    lines.append("")
    return "\n".join(lines)


def section_agreement(data: dict) -> str:
    """Section 3: Do agents agree?"""
    rater_maps = build_rater_axis_maps(data)
    all_qids = list(data["ratings"].keys())

    lines = [
        "## 3. Do agents agree?\n",
        "### Krippendorff's alpha per axis\n",
        "| Axis | Alpha |",
        "|------|------:|",
    ]
    for axis in AXES:
        # Build ratings matrix: list of {rater: score} per question
        matrix = []
        for qid in all_qids:
            item: dict[str, float] = {}
            for rater, scores in rater_maps[axis].items():
                if qid in scores:
                    item[rater] = scores[qid]
            if len(item) >= 2:
                matrix.append(item)
        alpha = krippendorff_alpha(matrix)
        lines.append(f"| {axis} | {alpha:.3f} |")

    # Pairwise MAE (overall across all three axes)
    raters = sorted(set().union(*(rater_maps[a].keys() for a in AXES)))
    lines.append("")
    lines.append("### Pairwise MAE (avg across R/N/G)\n")
    header = "| |" + "|".join(f" {r[:12]} " for r in raters) + "|"
    sep = "|" + "|".join("---:" for _ in range(len(raters) + 1)) + "|"
    lines.append(header)
    lines.append(sep)

    # Build full pairwise MAE matrix
    mae_matrix: dict[tuple[str, str], float] = {}
    for axis in AXES:
        pm = pairwise_mae(rater_maps[axis], all_qids, axis)
        for pair, val in pm.items():
            if pair not in mae_matrix:
                mae_matrix[pair] = 0.0
            mae_matrix[pair] += val / 3

    for r1 in raters:
        row = f"| {r1[:12]} |"
        for r2 in raters:
            if r1 == r2:
                row += " --- |"
            else:
                pair = (min(r1, r2), max(r1, r2))
                val = mae_matrix.get(pair, mae_matrix.get((r2, r1), float("nan")))
                row += f" {val:.2f} |" if not math.isnan(val) else " n/a |"
        lines.append(row)
    lines.append("")
    return "\n".join(lines)


def section_calibration(data: dict) -> str:
    """Section 4: Calibration against human."""
    cal = data["calibration"]
    lines = [
        "## 4. Calibration against human\n",
        "### Overall\n",
    ]
    for axis in AXES:
        ax_data = cal.get(axis, {})
        lines.append(f"- **{axis}**: mean error = {ax_data.get('mean_error', 'n/a'):.3f} (n={ax_data.get('n_items', 0)})")

    lines.append("")
    lines.append("### Per-agent MAE vs human\n")
    lines.append("| Agent | Model | Rigour err | Novelty err | Generativity err | n |")
    lines.append("|-------|-------|----------:|----------:|----------:|--:|")
    for agent in cal.get("per_agent", []):
        lines.append(
            f"| {agent['agent'][:20]} | {agent.get('model_slug', '?')[:15]} "
            f"| {agent['rigour_error']:.3f} "
            f"| {agent['novelty_error']:.3f} "
            f"| {agent['generativity_error']:.3f} "
            f"| {agent['n_items']} |"
        )

    # Test prediction: rigour error < novelty error < generativity error
    overall_r = cal.get("rigour", {}).get("mean_error", 0)
    overall_n = cal.get("novelty", {}).get("mean_error", 0)
    overall_g = cal.get("generativity", {}).get("mean_error", 0)
    prediction = overall_r < overall_n < overall_g
    lines.append("")
    lines.append(
        f"Prediction (R_err < N_err < G_err): {overall_r:.3f} < {overall_n:.3f} < {overall_g:.3f} "
        f"-> **{'confirmed' if prediction else 'not confirmed'}**"
    )
    lines.append("")
    return "\n".join(lines)


def section_content_quality(data: dict) -> str:
    """Section 5: Quality of agent-generated content."""
    questions = data["questions"]
    gidx = build_graph_index(data["graph"])

    seed_fs = [q.get("frontier_score") or 0 for q in questions if is_seed(q)]
    agent_fs = [q.get("frontier_score") or 0 for q in questions if not is_seed(q)]

    lines = [
        "## 5. Quality of agent-generated content\n",
    ]
    if seed_fs:
        lines.append(f"- Seed frontier_score: mean={statistics.mean(seed_fs):.2f}, median={statistics.median(seed_fs):.2f} (n={len(seed_fs)})")
    if agent_fs:
        lines.append(f"- Agent frontier_score: mean={statistics.mean(agent_fs):.2f}, median={statistics.median(agent_fs):.2f} (n={len(agent_fs)})")
    lines.append("")

    # Hollow chains: high answer_count + low frontier_score
    lines.append("### Hollow chains (answer_count >= 3, frontier_score < 2.5)\n")
    lines.append("| Title | frontier_score | Answers |")
    lines.append("|-------|---------------:|--------:|")
    hollow = [
        q for q in questions
        if (q.get("answer_count") or 0) >= 3 and (q.get("frontier_score") or 0) < 2.5
    ]
    for q in sorted(hollow, key=lambda q: q.get("frontier_score") or 0):
        lines.append(f"| {q['title'][:60]} | {q.get('frontier_score', 0):.2f} | {q.get('answer_count', 0)} |")
    if not hollow:
        lines.append("| (none found) | | |")
    lines.append("")

    # Potential loops: questions with very similar titles
    lines.append("### Potential duplicate clusters (shared title prefix)\n")
    prefix_groups: dict[str, list[dict]] = defaultdict(list)
    for q in questions:
        title = q.get("title", "")
        # Use first 20 chars as prefix (catches Tombstone, IFDS patterns)
        prefix = title[:20].strip()
        if prefix:
            prefix_groups[prefix].append(q)
    clusters = {k: v for k, v in prefix_groups.items() if len(v) >= 3}
    if clusters:
        for prefix, qs in sorted(clusters.items(), key=lambda x: -len(x[1])):
            lines.append(f"- **\"{prefix}...\"** ({len(qs)} questions)")
    else:
        lines.append("No clusters with 3+ questions sharing a 20-char prefix found.")
    lines.append("")
    return "\n".join(lines)


def section_consensus_failures(data: dict) -> str:
    """Section 6: Consensus failures."""
    lines = [
        "## 6. Consensus failures\n",
        "Cases where model consensus diverges sharply from human rating.\n",
    ]

    model_high_human_low = []
    model_low_human_high = []

    for qid, rinfo in data["ratings"].items():
        ratings = rinfo.get("ratings", [])
        human_ratings = [r for r in ratings if r.get("is_human")]
        model_ratings = [r for r in ratings if not r.get("is_human")]

        if not human_ratings or len(model_ratings) < 3:
            continue

        # Avg across all axes for simplicity
        human_avg = statistics.mean(
            [r[a] for r in human_ratings for a in AXES if r.get(a) is not None]
        )
        model_avg = statistics.mean(
            [r[a] for r in model_ratings for a in AXES if r.get(a) is not None]
        )

        q_title = _find_title(data["questions"], qid)
        if model_avg > 3.5 and human_avg < 2.5:
            model_high_human_low.append((q_title, model_avg, human_avg))
        elif model_avg < 2.5 and human_avg > 3.5:
            model_low_human_high.append((q_title, model_avg, human_avg))

    lines.append("### Models rate high, human rates low\n")
    if model_high_human_low:
        lines.append("| Title | Model avg | Human avg |")
        lines.append("|-------|----------:|----------:|")
        for title, ma, ha in model_high_human_low:
            lines.append(f"| {title[:60]} | {ma:.2f} | {ha:.2f} |")
    else:
        lines.append("None found.")
    lines.append("")

    lines.append("### Models rate low, human rates high\n")
    if model_low_human_high:
        lines.append("| Title | Model avg | Human avg |")
        lines.append("|-------|----------:|----------:|")
        for title, ma, ha in model_low_human_high:
            lines.append(f"| {title[:60]} | {ma:.2f} | {ha:.2f} |")
    else:
        lines.append("None found.")
    lines.append("")
    return "\n".join(lines)


def _find_title(questions: list[dict], qid: str) -> str:
    for q in questions:
        if q["id"] == qid:
            return q.get("title", "(untitled)")
    return "(unknown)"


def section_disagreement(data: dict) -> str:
    """Section 7: Disagreement patterns."""
    # Compute total std per question (across all raters, all axes)
    question_stds: list[tuple[str, str, float, list[tuple[str, dict]]]] = []

    for qid, rinfo in data["ratings"].items():
        ratings = rinfo.get("ratings", [])
        if len(ratings) < 3:
            continue
        all_scores: list[float] = []
        per_rater: list[tuple[str, dict]] = []
        for r in ratings:
            rater_scores = {a: r.get(a) for a in AXES if r.get(a) is not None}
            all_scores.extend(rater_scores.values())
            per_rater.append((r["rater_name"], rater_scores))
        if len(all_scores) < 6:
            continue
        std = statistics.stdev(all_scores)
        title = _find_title(data["questions"], qid)
        q = next((q for q in data["questions"] if q["id"] == qid), {})
        question_stds.append((qid, title, std, per_rater))

    question_stds.sort(key=lambda x: -x[2])
    top10 = question_stds[:10]

    lines = [
        "## 7. Disagreement patterns\n",
        "### Top 10 most controversial questions (highest score std across raters)\n",
    ]

    for rank, (qid, title, std, per_rater) in enumerate(top10, 1):
        q = next((q for q in data["questions"] if q["id"] == qid), {})
        qtype = "seed" if is_seed(q) else "agent"
        lines.append(f"**{rank}. {title[:70]}** (std={std:.2f}, type={qtype})\n")
        lines.append("| Rater | R | N | G |")
        lines.append("|-------|--:|--:|--:|")
        for rname, scores in per_rater:
            r = scores.get("rigour", "-")
            n = scores.get("novelty", "-")
            g = scores.get("generativity", "-")
            lines.append(f"| {rname[:20]} | {r} | {n} | {g} |")
        lines.append("")

    return "\n".join(lines)


def section_key_findings(data: dict) -> str:
    """Key findings section."""
    return (
        "## Key findings\n\n"
        "1. **TBD after data collection** -- run the script to populate.\n"
        "2. Placeholder for frontier_score ranking effectiveness.\n"
        "3. Placeholder for inter-rater agreement summary.\n"
        "4. Placeholder for calibration result.\n"
        "5. Placeholder for content quality observation.\n"
    )


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------


def chart_heatmap(data: dict) -> str:
    """Heatmap: scores by question x model, one sub-chart per axis."""
    rater_maps = build_rater_axis_maps(data)

    # Sort questions by frontier_score desc
    questions = sorted(
        data["questions"],
        key=lambda q: q.get("frontier_score") or 0,
        reverse=True,
    )
    qids = [q["id"] for q in questions]
    q_labels = [q["title"][:50] for q in questions]

    # Determine all model raters (exclude human)
    all_raters: set[str] = set()
    for axis in AXES:
        all_raters.update(rater_maps[axis].keys())
    raters = sorted(all_raters)

    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=["Rigour", "Novelty", "Generativity"],
        horizontal_spacing=0.05,
    )

    colorscale = [[0, "red"], [0.5, "yellow"], [1, "green"]]

    for col, axis in enumerate(AXES, 1):
        z = []
        hover: list[list[str]] = []
        for qid, qlabel in zip(qids, q_labels):
            row_vals = []
            row_hover = []
            for rater in raters:
                val = rater_maps[axis].get(rater, {}).get(qid)
                row_vals.append(val)
                row_hover.append(f"{qlabel}<br>{rater}: {val}")
            z.append(row_vals)
            hover.append(row_hover)

        fig.add_trace(
            go.Heatmap(
                z=z,
                x=raters,
                y=q_labels,
                colorscale=colorscale,
                zmin=1,
                zmax=5,
                hovertext=hover,
                hoverinfo="text",
                showscale=(col == 3),
            ),
            row=1,
            col=col,
        )

    fig.update_layout(
        title="Rating Heatmap: Questions x Models (sorted by frontier_score)",
        height=max(400, len(questions) * 18),
        width=1200,
    )
    return pio.to_html(fig, full_html=False)


def chart_scatter_frontier_vs_answers(data: dict) -> str:
    """Scatter: frontier_score vs answer_count."""
    questions = data["questions"]

    seeds = [q for q in questions if is_seed(q)]
    agents = [q for q in questions if not is_seed(q)]

    fig = go.Figure()

    for group, color, label in [(seeds, "blue", "Seed"), (agents, "orange", "Agent-generated")]:
        x = [q.get("frontier_score") or 0 for q in group]
        y = [q.get("answer_count") or 0 for q in group]
        texts = [q["title"][:60] for q in group]
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode="markers",
            marker=dict(color=color, size=8, opacity=0.7),
            text=texts,
            hoverinfo="text+x+y",
            name=label,
        ))

    # OLS trendline
    all_x = [q.get("frontier_score") or 0 for q in questions]
    all_y = [q.get("answer_count") or 0 for q in questions]
    if len(all_x) > 2:
        mean_x = statistics.mean(all_x)
        mean_y = statistics.mean(all_y)
        cov = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(all_x, all_y))
        var_x = sum((xi - mean_x) ** 2 for xi in all_x)
        if var_x > 0:
            slope = cov / var_x
            intercept = mean_y - slope * mean_x
            x_line = [min(all_x), max(all_x)]
            y_line = [slope * xi + intercept for xi in x_line]
            fig.add_trace(go.Scatter(
                x=x_line,
                y=y_line,
                mode="lines",
                line=dict(color="gray", dash="dash"),
                name=f"OLS (slope={slope:.2f})",
            ))

    fig.update_layout(
        title="Frontier Score vs Answer Count",
        xaxis_title="frontier_score",
        yaxis_title="answer_count",
        height=500,
        width=800,
    )
    return pio.to_html(fig, full_html=False)


def chart_calibration_bars(data: dict) -> str:
    """Calibration bar chart: per-model error vs human on each axis."""
    cal = data["calibration"]
    agents = cal.get("per_agent", [])
    if not agents:
        return "<p>No calibration data available.</p>"

    names = [a["agent"][:20] for a in agents]

    fig = go.Figure()
    colors = {"rigour": "#e74c3c", "novelty": "#3498db", "generativity": "#2ecc71"}

    for axis in AXES:
        errs = [a[f"{axis}_error"] for a in agents]
        fig.add_trace(go.Bar(
            name=axis.capitalize(),
            x=names,
            y=errs,
            marker_color=colors[axis],
        ))

    fig.update_layout(
        title="Calibration: Per-Model MAE vs Human",
        barmode="group",
        yaxis_title="Mean Absolute Error",
        height=450,
        width=800,
    )
    return pio.to_html(fig, full_html=False)


def chart_agreement_matrix(data: dict) -> str:
    """Agreement matrix: 6x6 pairwise MAE heatmap."""
    rater_maps = build_rater_axis_maps(data)
    all_qids = list(data["ratings"].keys())

    all_raters: set[str] = set()
    for axis in AXES:
        all_raters.update(rater_maps[axis].keys())
    raters = sorted(all_raters)

    # Build symmetric MAE matrix (avg across axes)
    n = len(raters)
    z = [[0.0] * n for _ in range(n)]
    annotations: list[list[str]] = [[""] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i == j:
                z[i][j] = 0.0
                annotations[i][j] = "0.00"
                continue
            r1, r2 = raters[i], raters[j]
            pair = (min(r1, r2), max(r1, r2))
            total = 0.0
            count = 0
            for axis in AXES:
                diffs = []
                for qid in all_qids:
                    s1 = rater_maps[axis].get(r1, {}).get(qid)
                    s2 = rater_maps[axis].get(r2, {}).get(qid)
                    if s1 is not None and s2 is not None:
                        diffs.append(abs(s1 - s2))
                if diffs:
                    total += statistics.mean(diffs)
                    count += 1
            val = total / count if count > 0 else float("nan")
            z[i][j] = val if not math.isnan(val) else 0
            annotations[i][j] = f"{val:.2f}" if not math.isnan(val) else "n/a"

    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=[r[:15] for r in raters],
        y=[r[:15] for r in raters],
        colorscale=[[0, "green"], [0.5, "yellow"], [1, "red"]],
        text=annotations,
        hoverinfo="text+z",
        texttemplate="%{text}",
    ))

    fig.update_layout(
        title="Pairwise Agreement Matrix (MAE, lower=more agreement)",
        height=500,
        width=600,
    )
    return pio.to_html(fig, full_html=False)


def build_html(data: dict) -> str:
    """Combine all charts into a single HTML page."""
    log.info("Building charts...")
    parts = [
        "<!DOCTYPE html>",
        '<html lang="en"><head>',
        '<meta charset="utf-8">',
        "<title>Rating Analysis Charts - 2026-03-19</title>",
        '<script src="https://cdn.plot.ly/plotly-2.35.0.min.js"></script>',
        "<style>body{font-family:sans-serif;max-width:1300px;margin:0 auto;padding:20px}"
        ".chart{margin:30px 0;border-bottom:1px solid #eee;padding-bottom:20px}</style>",
        "</head><body>",
        "<h1>Rating Analysis Charts (2026-03-19)</h1>",
        '<div class="chart">',
        chart_heatmap(data),
        "</div>",
        '<div class="chart">',
        chart_scatter_frontier_vs_answers(data),
        "</div>",
        '<div class="chart">',
        chart_calibration_bars(data),
        "</div>",
        '<div class="chart">',
        chart_agreement_matrix(data),
        "</div>",
        "</body></html>",
    ]
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------


def build_report(data: dict) -> str:
    """Assemble the full markdown report."""
    log.info("Computing stats...")
    sections = [
        "# Rating Analysis Report (2026-03-19)\n",
        f"**{len(data['questions'])} questions** | "
        f"**{sum(1 for q in data['questions'] if is_seed(q))} seeds** | "
        f"**{len(data['ratings'])} rated**\n",
        section_frontier_ranking(data),
        section_discussion_correlation(data),
        section_agreement(data),
        section_calibration(data),
        section_content_quality(data),
        section_consensus_failures(data),
        section_disagreement(data),
        section_key_findings(data),
    ]
    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    start = time.monotonic()

    client = httpx.Client(timeout=30.0)
    try:
        data = collect_data(client)
    finally:
        client.close()

    # Ensure output directory exists
    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)

    report = build_report(data)
    log.info("Writing report to %s", OUTPUT_MD)
    OUTPUT_MD.write_text(report)

    html = build_html(data)
    log.info("Writing charts to %s", OUTPUT_HTML)
    OUTPUT_HTML.write_text(html)

    elapsed = time.monotonic() - start
    log.info("Done in %.1fs", elapsed)


if __name__ == "__main__":
    main()
