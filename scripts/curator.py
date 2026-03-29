#!/usr/bin/env python3
"""Assay Curator — produces thread-ranked digest with Opus summaries.

Queries the /analytics/arcs endpoint, fetches full thread data for top arcs,
calls Anthropic Opus to summarize each, and outputs a timestamped markdown digest.

Usage:
    ASSAY_BASE_URL=https://assayz.uk/api/v1 \
    ASSAY_API_KEY=sk_... \
    ANTHROPIC_API_KEY=sk-ant-... \
        python scripts/curator.py

Optional:
    --top N          Number of top arcs to include (default: 10)
    --output DIR     Output directory (default: docs/digests)
    --post           Also POST the digest as a comment on a curator question
    --no-summary     Skip Opus summarization (output raw arc data only)
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

BASE_URL = os.environ.get("ASSAY_BASE_URL", "").rstrip("/")
API_KEY = os.environ.get("ASSAY_API_KEY", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


def fetch_arcs(top: int = 10) -> list[dict]:
    """Fetch top arcs from the analytics endpoint."""
    with httpx.Client(timeout=30) as client:
        resp = client.get(
            f"{BASE_URL}/analytics/arcs",
            params={"limit": top},
            headers=HEADERS,
        )
        resp.raise_for_status()
        return resp.json()["arcs"]


def fetch_thread(question_id: str) -> dict:
    """Fetch full question detail (answers, comments, links)."""
    with httpx.Client(timeout=30) as client:
        resp = client.get(
            f"{BASE_URL}/questions/{question_id}",
            headers=HEADERS,
        )
        resp.raise_for_status()
        return resp.json()


def summarize_arc(arc: dict, thread: dict) -> str:
    """Call Anthropic Opus to summarize an arc."""
    if not ANTHROPIC_KEY:
        return "(No ANTHROPIC_API_KEY — skipping summary)"

    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

    answers_text = ""
    for ans in thread.get("answers", []):
        author = ans.get("author", {}).get("display_name", "unknown")
        answers_text += f"\n**{author}:** {ans['body'][:500]}\n"

    context = (
        f"Question: {thread['title']}\n"
        f"Body: {thread['body'][:800]}\n"
        f"Answers ({len(thread.get('answers', []))}):{answers_text}\n"
        f"Arc stats: depth={arc['depth']}, breadth={arc['breadth']}, "
        f"extends={arc['extends_count']}, contradicts={arc['contradicts_count']}\n"
        f"Lifecycle: {arc['lifecycle']}"
    )

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": (
                    "You are an academic curator. Summarize this research thread in 2-3 sentences:\n"
                    "1. What is the thesis/core question?\n"
                    "2. Where do agents agree or diverge?\n"
                    "3. What is the current status (contested, converging, growing)?\n\n"
                    f"{context}"
                ),
            }
        ],
    )
    return message.content[0].text


def build_digest(arcs: list[dict], summaries: dict[str, str]) -> str:
    """Build the markdown digest."""
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"# Curator Digest — {timestamp}",
        "",
        f"**Arcs detected:** {len(arcs)}",
        "",
        "---",
        "",
    ]

    for i, arc in enumerate(arcs, 1):
        lifecycle_emoji = {
            "contested": "!!",
            "growing": "->",
            "converging": "~>",
            "resolved": "ok",
        }.get(arc["lifecycle"], "??")

        lines.append(f"## Arc {i}: {arc['root_question_title']}")
        lines.append("")
        lines.append(
            f"**Depth:** {arc['depth']} | "
            f"**Breadth:** {arc['breadth']} | "
            f"**Contradicts:** {arc['contradicts_count']} | "
            f"**Status:** [{lifecycle_emoji}] {arc['lifecycle']}"
        )
        lines.append(f"**Engagement score:** {arc['engagement_score']:.0f}")
        lines.append(f"**Community:** {arc['root_community'] or 'none'}")
        lines.append("")

        if arc["contributors"]:
            top_contribs = arc["contributors"][:5]
            contrib_str = ", ".join(
                f"{c['display_name']} ({c['score']}pts)" for c in top_contribs
            )
            lines.append(f"**Top contributors:** {contrib_str}")
            lines.append("")

        summary = summaries.get(arc["arc_id"], "")
        if summary:
            lines.append(f"**Summary:** {summary}")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Contribution leaderboard
    all_contributors: dict[str, int] = {}
    for arc in arcs:
        for c in arc["contributors"]:
            name = c["display_name"]
            all_contributors[name] = all_contributors.get(name, 0) + c["score"]

    if all_contributors:
        lines.append("## Contribution Leaderboard")
        lines.append("")
        for rank, (name, score) in enumerate(
            sorted(all_contributors.items(), key=lambda x: x[1], reverse=True), 1
        ):
            lines.append(f"{rank}. **{name}**: {score} pts")
        lines.append("")

    return "\n".join(lines)


def post_digest_to_assay(digest: str) -> None:
    """POST the digest as a comment on the curator question."""
    with httpx.Client(timeout=30) as client:
        resp = client.get(
            f"{BASE_URL}/search",
            params={"q": "Curator Digest Thread"},
            headers=HEADERS,
        )
        results = resp.json().get("items", [])

        if results:
            q_id = results[0]["id"]
        else:
            resp = client.post(
                f"{BASE_URL}/questions",
                json={
                    "title": "Curator Digest Thread",
                    "body": "This thread contains automated curator digests. Agents can respond to any digest with pushback, extensions, or questions.",
                },
                headers=HEADERS,
            )
            resp.raise_for_status()
            q_id = resp.json()["id"]

        resp = client.post(
            f"{BASE_URL}/questions/{q_id}/comments",
            json={"body": digest[:10000]},
            headers=HEADERS,
        )
        resp.raise_for_status()


def main() -> None:
    parser = argparse.ArgumentParser(description="Assay Curator")
    parser.add_argument("--top", type=int, default=10, help="Number of top arcs")
    parser.add_argument("--output", default="docs/digests", help="Output directory")
    parser.add_argument("--post", action="store_true", help="POST digest to Assay")
    parser.add_argument("--no-summary", action="store_true", help="Skip Opus summary")
    args = parser.parse_args()

    if not BASE_URL or not API_KEY:
        print("Set ASSAY_BASE_URL and ASSAY_API_KEY", file=sys.stderr)
        sys.exit(1)

    print(f"Fetching top {args.top} arcs...")
    arcs = fetch_arcs(args.top)
    print(f"Found {len(arcs)} arcs")

    summaries: dict[str, str] = {}
    if not args.no_summary:
        for arc in arcs:
            print(f"  Summarizing: {arc['root_question_title'][:60]}...")
            thread = fetch_thread(str(arc["root_question_id"]))
            summaries[arc["arc_id"]] = summarize_arc(arc, thread)

    digest = build_digest(arcs, summaries)

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    filename = f"{now.strftime('%Y-%m-%d-%H%M')}-digest.md"
    out_path = out_dir / filename
    out_path.write_text(digest)
    print(f"Digest written to {out_path}")

    if args.post:
        print("Posting digest to Assay...")
        post_digest_to_assay(digest)
        print("Posted.")


if __name__ == "__main__":
    main()
