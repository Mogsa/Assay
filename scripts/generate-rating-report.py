#!/usr/bin/env python3
"""Generate rating analysis report for dissertation advisor.

5 AI models + 1 human rated 134 questions on R/N/G Likert scales.
The report surfaces surprising findings: cheapest model wins, models
reward jargon over substance, generativity is the most contested axis.

Queries the Assay API (no auth), produces:
  - docs/analysis/2026-03-19-rating-analysis.md  (prose, ~1.5 pages)
  - docs/analysis/2026-03-19-rating-charts.html   (5 interactive plotly charts)

Dependencies: httpx, plotly
Run from repo root:  python scripts/generate-rating-report.py
"""

from __future__ import annotations

import logging
import math
import statistics
import time
from collections import defaultdict
from pathlib import Path

import httpx
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

BASE_URL = "https://assayz.uk/api/v1"
OUTPUT_MD = Path("docs/analysis/2026-03-19-rating-analysis.md")
OUTPUT_HTML = Path("docs/analysis/2026-03-19-rating-charts.html")

AXES = ("rigour", "novelty", "generativity")
AXIS_SHORT = {"rigour": "R", "novelty": "N", "generativity": "G"}

RATER_NAMES = [
    "Haiku rater",
    "gemini flash rater",
    "gpt 5.4 mini rater",
    "Owen code rater",
    "opus 4.6 rater",
]
HUMAN_RATER = "morgan"
ALL_RATERS = RATER_NAMES + [HUMAN_RATER]

# Display names for tables/charts
DISPLAY = {
    "Haiku rater": "Haiku 4.5",
    "gemini flash rater": "Gemini Flash",
    "gpt 5.4 mini rater": "GPT-5.4 mini",
    "Owen code rater": "Qwen Coder",
    "opus 4.6 rater": "Opus 4.6",
    "morgan": "Morgan (human)",
}
SHORT_DISPLAY = {
    "Haiku rater": "Haiku",
    "gemini flash rater": "Gemini",
    "gpt 5.4 mini rater": "GPT mini",
    "Owen code rater": "Qwen",
    "opus 4.6 rater": "Opus",
}

COST_PER_M = {
    "Haiku rater": "$1",
    "gemini flash rater": "free",
    "gpt 5.4 mini rater": "cheap",
    "Owen code rater": "free",
    "opus 4.6 rater": "$5",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [report] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("report")


# ---------------------------------------------------------------------------
# API helpers
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
    return api_get(
        client, "/ratings", {"target_type": "question", "target_id": question_id}
    )


def fetch_graph(client: httpx.Client) -> dict:
    return api_get(client, "/analytics/graph", {"limit": 200})


def fetch_calibration(client: httpx.Client) -> dict:
    return api_get(client, "/analytics/calibration")


# ---------------------------------------------------------------------------
# Statistics (stdlib only, no scipy/numpy)
# ---------------------------------------------------------------------------


def _ranks(data: list[float]) -> list[float]:
    indexed = sorted(enumerate(data), key=lambda x: x[1])
    ranks = [0.0] * len(data)
    i = 0
    while i < len(indexed):
        j = i
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j + 1) / 2
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j
    return ranks


def spearman(x: list[float], y: list[float]) -> tuple[float, float]:
    """Spearman rank correlation + approximate two-tailed p-value."""
    n = len(x)
    if n < 3:
        return 0.0, 1.0
    rx = _ranks(x)
    ry = _ranks(y)
    d_sq = sum((a - b) ** 2 for a, b in zip(rx, ry))
    rho = 1 - (6 * d_sq) / (n * (n**2 - 1))
    rho = max(-1.0, min(1.0, rho))
    if abs(rho) >= 1.0:
        return rho, 0.0
    t_stat = rho * math.sqrt((n - 2) / (1 - rho**2))
    p = 2 * (1 - _norm_cdf(abs(t_stat)))
    return rho, max(p, 0.0)


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2)))


def mae_between(
    scores_a: dict[str, float],
    scores_b: dict[str, float],
) -> tuple[float, int]:
    """MAE between two raters on shared questions. Returns (mae, n)."""
    diffs = [
        abs(scores_a[qid] - scores_b[qid])
        for qid in scores_a
        if qid in scores_b
    ]
    if not diffs:
        return float("nan"), 0
    return statistics.mean(diffs), len(diffs)


def mae_per_axis(
    rater_maps: dict,
    rater_a: str,
    rater_b: str,
) -> dict[str, tuple[float, int]]:
    """MAE per axis between two raters. Returns {axis: (mae, n)}."""
    result = {}
    for axis in AXES:
        a_scores = rater_maps[axis].get(rater_a, {})
        b_scores = rater_maps[axis].get(rater_b, {})
        result[axis] = mae_between(a_scores, b_scores)
    return result


def frontier_score_for(rater_maps: dict, rater: str, qid: str) -> float | None:
    """Geometric mean of R, N, G for a single rater on a single question."""
    vals = []
    for axis in AXES:
        v = rater_maps[axis].get(rater, {}).get(qid)
        if v is None:
            return None
        vals.append(v)
    return (vals[0] * vals[1] * vals[2]) ** (1 / 3)


def krippendorff_alpha(ratings_matrix: list[dict[str, float]]) -> float:
    """Interval Krippendorff's alpha.

    ratings_matrix: list of {rater_name: score} per item.
    Missing raters are absent from the dict.
    """
    all_values: list[float] = []
    for item in ratings_matrix:
        all_values.extend(item.values())
    if len(all_values) < 2:
        return 0.0

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

    # Expected disagreement
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
# Content classification
# ---------------------------------------------------------------------------


def q_link(q: dict, max_len: int = 70) -> str:
    """Return a markdown link to the question on assayz.uk, title truncated."""
    title = q.get("title", "(untitled)")
    short = title[:max_len] + ("..." if len(title) > max_len else "")
    qid = q.get("id", "")
    return f"[{short}](https://assayz.uk/questions/{qid})"


def is_seed(q: dict) -> bool:
    return q.get("title", "").startswith("[Seed]")


def is_ifds(q: dict) -> bool:
    title = q.get("title", "").lower()
    return any(kw in title for kw in ("ifds", "tombstone", "scc"))


def is_test(q: dict) -> bool:
    title = q.get("title", "").lower()
    return "test" in title and not is_seed(q) and not is_ifds(q)


def content_type(q: dict) -> str:
    if is_seed(q):
        return "seed"
    if is_ifds(q):
        return "ifds"
    if is_test(q):
        return "test"
    return "other"


CONTENT_LABELS = {
    "seed": "Seeds",
    "ifds": "IFDS/Tombstone",
    "test": "Test posts",
    "other": "Other agent",
}


def seed_subtopic(q: dict) -> str:
    """Classify a seed question into its source/subtopic."""
    title = q.get("title", "").lower()
    body = q.get("body", "").lower()
    combined = title + " " + body

    if "frontiermath" in combined or "epoch.ai" in combined:
        return "FrontierMath"
    if any(kw in combined for kw in ("improve", "prove a tight", "find a hadamard", "find a polynomial")):
        if any(kw in combined for kw in ("ramsey", "kakeya", "sensitivity", "hadamard", "galois", "mathieu")):
            return "FrontierMath"

    if any(kw in combined for kw in ("enzyme", "protein", "phosphoryl", "gene", "hsc", "honeybee", "hematopoietic", "transpos")):
        return "HLE: Biology"
    if any(kw in combined for kw in ("spectrum", "wavelength", "synthesis", "chemical element", "dielectric")):
        return "HLE: Chemistry/Physics"
    if any(kw in combined for kw in ("modal logic", "barcan", "modus tollens", "propositional logic", "three-valued logic", "bonaventure", "augustine", "philosopher")):
        return "HLE: Logic/Philosophy"
    if any(kw in combined for kw in ("transformer", "neural network", "raspy", "language model", "attention", "embedding")):
        return "HLE: ML/CS"
    if any(kw in combined for kw in ("jags", "band matrix", "predictor", "computable")):
        return "HLE: Math/Stats"
    if any(kw in combined for kw in ("javascript", "bug", "code", "python program", "87-byte")):
        return "HLE: Code"
    if any(kw in combined for kw in ("depression", "neutrino", "supersymmetry")):
        return "HLE: Science"

    if "hle" in combined or "cais" in combined:
        return "HLE: Other"

    # Competition math (IMO-style)
    if any(kw in title for kw in ("sequence", "circle", "integer", "real number", "determine")):
        return "Competition Math"

    return "Seed: Other"


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------


def collect_data(client: httpx.Client) -> dict:
    log.info("Fetching questions...")
    questions = fetch_all_questions(client)
    log.info("  got %d questions", len(questions))

    log.info("Fetching graph...")
    graph = fetch_graph(client)
    log.info(
        "  got %d nodes, %d edges", len(graph["nodes"]), len(graph["edges"])
    )

    log.info("Fetching calibration...")
    calibration = fetch_calibration(client)

    log.info("Fetching ratings for %d questions...", len(questions))
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
# Data indexing
# ---------------------------------------------------------------------------


def build_rater_axis_maps(data: dict) -> dict[str, dict[str, dict[str, float]]]:
    """Returns {axis: {rater_name: {question_id: score}}}."""
    result: dict[str, dict[str, dict[str, float]]] = {
        a: defaultdict(dict) for a in AXES
    }
    for qid, rinfo in data["ratings"].items():
        for r in rinfo.get("ratings", []):
            name = r["rater_name"]
            for axis in AXES:
                if r.get(axis) is not None:
                    result[axis][name][qid] = float(r[axis])
    return result


def build_graph_activity(graph: dict) -> dict[str, dict[str, int]]:
    """Count nodes by (author_name, type) from graph data.

    Returns {author_name: {question: n, answer: n, comment: n, ...}}.
    Also counts edges by author for links.
    """
    activity: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for node in graph["nodes"]:
        author = node.get("author_name") or node.get("label", "unknown")
        ntype = node.get("type", "unknown")
        activity[author][ntype] += 1

    # Count link edges — attribute to the edge's source node's author
    nodes_by_id = {n["id"]: n for n in graph["nodes"]}
    for edge in graph["edges"]:
        if edge.get("edge_type") == "link":
            source_node = nodes_by_id.get(edge.get("source"))
            if source_node:
                author = source_node.get("author_name", "unknown")
                activity[author]["link"] += 1
        # Also count "extends" edges
        if edge.get("edge_type") == "extends":
            source_node = nodes_by_id.get(edge.get("source"))
            if source_node:
                author = source_node.get("author_name", "unknown")
                activity[author]["extends"] += 1

    return dict(activity)


def discussion_metrics(q: dict, graph: dict) -> dict:
    """Get answer_count, link_count, spawned_count for a question."""
    nodes_by_id = {n["id"]: n for n in graph["nodes"]}
    qid = q["id"]
    node = nodes_by_id.get(qid, {})

    answer_count = q.get("answer_count", 0) or node.get("answer_count", 0)
    link_count = node.get("link_count", 0)

    spawned = sum(
        1
        for e in graph["edges"]
        if e.get("source") == qid and e.get("edge_type") == "extends"
    )
    return {
        "answer_count": answer_count,
        "link_count": link_count,
        "spawned_count": spawned,
    }


# ---------------------------------------------------------------------------
# Section builders (markdown)
# ---------------------------------------------------------------------------


def section_platform_overview(data: dict) -> str:
    questions = data["questions"]
    graph = data["graph"]
    n_total = len(questions)

    # Content classification counts
    counts: dict[str, int] = defaultdict(int)
    for q in questions:
        counts[content_type(q)] += 1

    # Agent activity from graph
    activity = build_graph_activity(graph)

    lines = [
        "## 1. Platform Overview\n",
        f"**{n_total} questions** before the rating experiment began:\n",
        "| Category | Count | Description |",
        "|----------|------:|-------------|",
    ]
    for ctype in ("seed", "ifds", "test", "other"):
        desc_map = {
            "seed": "~35 from Humanity's Last Exam (HLE), ~5 FrontierMath (epoch.ai), ~5 competition math",
            "ifds": "One agent (Claude Sonnet) looping on IFDS dataflow analysis",
            "test": "Platform test posts",
            "other": "Agent-generated across various topics",
        }
        lines.append(
            f"| {CONTENT_LABELS[ctype]} | {counts.get(ctype, 0)} | {desc_map[ctype]} |"
        )

    # Agent activity table
    lines.append("\n**Agent activity** (from graph data):\n")
    lines.append("| Model | Questions | Answers | Reviews | Links |")
    lines.append("|-------|----------:|--------:|--------:|------:|")

    # Sort by total activity descending
    rows = []
    for author, acts in sorted(
        activity.items(), key=lambda x: sum(x[1].values()), reverse=True
    ):
        q_count = acts.get("question", 0)
        a_count = acts.get("answer", 0)
        r_count = acts.get("comment", 0)  # reviews are comments in the graph
        l_count = acts.get("link", 0) + acts.get("extends", 0)
        if q_count + a_count + r_count + l_count == 0:
            continue
        rows.append((author, q_count, a_count, r_count, l_count))

    for author, qc, ac, rc, lc in rows:
        name = author[:30]
        lines.append(f"| {name} | {qc} | {ac} | {rc} | {lc} |")

    ifds_pct = counts.get("ifds", 0) / max(n_total, 1) * 100
    lines.append(
        f"\nThe platform has a content diversity problem. "
        f"IFDS/tombstone variants account for {ifds_pct:.0f}% of all questions."
    )
    lines.append("")

    return "\n".join(lines)


def section_experiment_setup() -> str:
    lines = [
        "## 2. Rating Experiment Setup\n",
        "**5 AI raters** independently rated all 134 questions using R/N/G rubric "
        "with calibration anchors (Euclid=R5, Godel=N5, Riemann=G5). "
        "All models ran via CLI tools (Claude Code, Gemini CLI, Codex CLI, Qwen Code) "
        "— included in existing subscriptions, no additional API cost.\n",
        "| Rater | Model | Questions rated |",
        "|-------|-------|----------------:|",
        "| Haiku 4.5 | anthropic/claude-haiku-4-5 | 134 |",
        "| Gemini 3 Flash | google/gemini-3-flash-preview | 134 |",
        "| GPT-5.4 mini | openai/gpt-5.4-mini | 134 |",
        "| Qwen 3.5 Coder | qwen/qwen3-coder-plus | 134 |",
        "| Opus 4.6 | anthropic/claude-opus-4-6 | 134 |",
        "",
        "**1 human** (Morgan) rated 29 questions from a stratified sample: "
        "top 10, bottom 10, and 9 controversial.\n",
        "Rating-only mode: agents read `rate-pass.md`, rated 10 questions "
        "per pass. "
        "`frontier_score = (R x N x G)^(1/3)` — geometric mean, range 1-5.\n",
    ]
    return "\n".join(lines)


def section_finding_1(rater_maps: dict) -> str:
    """Finding 1: Cheapest model correlates best with human judgment."""
    lines = [
        "### Finding 1: The cheapest model correlates best with human judgment\n",
    ]

    # Per-model MAE vs Morgan, per axis and overall
    rows: list[tuple[str, float, float, float, float]] = []
    for model in RATER_NAMES:
        axis_maes = mae_per_axis(rater_maps, model, HUMAN_RATER)
        vals = []
        for axis in AXES:
            m, _ = axis_maes[axis]
            vals.append(m)
        valid = [v for v in vals if not math.isnan(v)]
        overall = statistics.mean(valid) if valid else float("nan")
        rows.append((model, vals[0], vals[1], vals[2], overall))

    # Sort by overall MAE
    rows.sort(key=lambda r: r[4] if not math.isnan(r[4]) else 999)

    lines.append("| Model | R MAE | N MAE | G MAE | Overall MAE |")
    lines.append("|-------|------:|------:|------:|------------:|")
    for model, r_mae, n_mae, g_mae, overall in rows:
        def _fmt(v: float) -> str:
            return f"{v:.2f}" if not math.isnan(v) else "n/a"

        lines.append(
            f"| {DISPLAY[model]} | "
            f"{_fmt(r_mae)} | {_fmt(n_mae)} | {_fmt(g_mae)} | "
            f"**{_fmt(overall)}** |"
        )

    best_name = DISPLAY[rows[0][0]]
    best_overall = rows[0][4]
    worst_name = DISPLAY[rows[-1][0]]
    worst_overall = rows[-1][4]
    lines.append("")
    lines.append(
        f"**{best_name}** (a small model) is closest to human "
        f"(MAE={best_overall:.2f}). "
        f"**{worst_name}** is furthest "
        f"(MAE={worst_overall:.2f})."
    )
    lines.append("")
    return "\n".join(lines)


def section_finding_2(
    data: dict, rater_maps: dict
) -> str:
    """Finding 2: Models are fooled by well-formatted jargon."""
    questions = data["questions"]
    lines = [
        "### Finding 2: Models are fooled by well-formatted jargon\n",
        "Seed questions (FrontierMath open problems, Humanity's Last Exam) are "
        "genuine frontier content — we **expect** them to score highest. "
        "Instead, agent-generated IFDS/tombstone questions outscored them:\n",
    ]

    # Average frontier_score by content type (all model raters)
    type_axis_scores: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for q in questions:
        qid = q["id"]
        ctype = content_type(q)
        for model in RATER_NAMES:
            for axis in AXES:
                v = rater_maps[axis].get(model, {}).get(qid)
                if v is not None:
                    type_axis_scores[ctype][axis].append(v)

    # Also compute frontier_score per content type
    type_fs: dict[str, list[float]] = defaultdict(list)
    for q in questions:
        qid = q["id"]
        ctype = content_type(q)
        for model in RATER_NAMES:
            fs = frontier_score_for(rater_maps, model, qid)
            if fs is not None:
                type_fs[ctype].append(fs)

    lines.append("**Average scores by content type** (across all 5 model raters):\n")
    lines.append("| Content type | n | Avg R | Avg N | Avg G | frontier_score |")
    lines.append("|--------------|--:|------:|------:|------:|---------------:|")
    for ctype in ("seed", "ifds", "other", "test"):
        if ctype not in type_axis_scores:
            continue
        r_avg = statistics.mean(type_axis_scores[ctype]["rigour"]) if type_axis_scores[ctype]["rigour"] else 0
        n_avg = statistics.mean(type_axis_scores[ctype]["novelty"]) if type_axis_scores[ctype]["novelty"] else 0
        g_avg = statistics.mean(type_axis_scores[ctype]["generativity"]) if type_axis_scores[ctype]["generativity"] else 0
        fs_avg = statistics.mean(type_fs[ctype]) if type_fs[ctype] else 0
        n_ratings = len(type_fs.get(ctype, []))
        lines.append(
            f"| {CONTENT_LABELS.get(ctype, ctype)} | {n_ratings} | "
            f"{r_avg:.2f} | {n_avg:.2f} | {g_avg:.2f} | {fs_avg:.2f} |"
        )

    lines.append("")

    # Per-model breakdown: seeds vs IFDS
    lines.append("**Per-model breakdown** (Seeds vs IFDS/Tombstone):\n")
    lines.append("| Model | Type | Avg R | Avg N | Avg G |")
    lines.append("|-------|------|------:|------:|------:|")
    for model in RATER_NAMES:
        for ctype in ("seed", "ifds"):
            r_vals, n_vals, g_vals = [], [], []
            for q in questions:
                if content_type(q) != ctype:
                    continue
                qid = q["id"]
                r = rater_maps["rigour"].get(model, {}).get(qid)
                n = rater_maps["novelty"].get(model, {}).get(qid)
                g = rater_maps["generativity"].get(model, {}).get(qid)
                if r is not None:
                    r_vals.append(r)
                if n is not None:
                    n_vals.append(n)
                if g is not None:
                    g_vals.append(g)
            r_avg = statistics.mean(r_vals) if r_vals else 0
            n_avg = statistics.mean(n_vals) if n_vals else 0
            g_avg = statistics.mean(g_vals) if g_vals else 0
            label = CONTENT_LABELS[ctype]
            lines.append(
                f"| {DISPLAY[model]} | {label} | "
                f"{r_avg:.2f} | {n_avg:.2f} | {g_avg:.2f} |"
            )

    lines.append("")
    lines.append(
        "Models reward hypothesis/falsifier structure over substantive novelty. "
        "IFDS questions use formal mathematical language that inflates R and N scores "
        "despite being narrow variations on one topic."
    )
    lines.append("")
    return "\n".join(lines)


def section_seed_breakdown(data: dict, rater_maps: dict) -> str:
    """Seed subtopic breakdown: FrontierMath vs HLE subtopics vs Competition Math."""
    questions = data["questions"]
    seeds = [q for q in questions if is_seed(q)]

    # Group by subtopic
    subtopic_scores: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    subtopic_fs: dict[str, list[float]] = defaultdict(list)
    subtopic_counts: dict[str, int] = defaultdict(int)

    for q in seeds:
        st = seed_subtopic(q)
        subtopic_counts[st] += 1
        qid = q["id"]
        for model in RATER_NAMES:
            for axis in AXES:
                v = rater_maps[axis].get(model, {}).get(qid)
                if v is not None:
                    subtopic_scores[st][axis].append(v)
            fs = frontier_score_for(rater_maps, model, qid)
            if fs is not None:
                subtopic_fs[st].append(fs)

    lines = [
        "### Seed Question Breakdown by Source\n",
        "| Source | n | Avg R | Avg N | Avg G | frontier_score |",
        "|--------|--:|------:|------:|------:|---------------:|",
    ]

    # Sort by frontier_score descending
    sorted_topics = sorted(
        subtopic_counts.keys(),
        key=lambda st: statistics.mean(subtopic_fs[st]) if subtopic_fs[st] else 0,
        reverse=True,
    )
    for st in sorted_topics:
        n = subtopic_counts[st]
        r_avg = statistics.mean(subtopic_scores[st]["rigour"]) if subtopic_scores[st]["rigour"] else 0
        n_avg = statistics.mean(subtopic_scores[st]["novelty"]) if subtopic_scores[st]["novelty"] else 0
        g_avg = statistics.mean(subtopic_scores[st]["generativity"]) if subtopic_scores[st]["generativity"] else 0
        fs_avg = statistics.mean(subtopic_fs[st]) if subtopic_fs[st] else 0
        lines.append(f"| {st} | {n} | {r_avg:.2f} | {n_avg:.2f} | {g_avg:.2f} | {fs_avg:.2f} |")

    lines.append("")
    # Find best and worst
    if sorted_topics:
        best = sorted_topics[0]
        worst = sorted_topics[-1]
        lines.append(
            f"**{best}** scores highest (frontier={statistics.mean(subtopic_fs[best]):.2f}). "
            f"**{worst}** scores lowest (frontier={statistics.mean(subtopic_fs[worst]):.2f})."
        )
    lines.append("")
    return "\n".join(lines)


def section_finding_3(data: dict, rater_maps: dict) -> str:
    """Finding 3: Generativity is the axis models disagree on most."""
    lines = [
        "### Finding 3: Generativity is the axis models disagree on most\n",
    ]

    # Krippendorff's alpha per axis among all 5 models
    alpha_by_axis: dict[str, float] = {}
    for axis in AXES:
        all_qids: set[str] = set()
        for model in RATER_NAMES:
            all_qids.update(rater_maps[axis].get(model, {}).keys())
        matrix: list[dict[str, float]] = []
        for qid in all_qids:
            item: dict[str, float] = {}
            for model in RATER_NAMES:
                val = rater_maps[axis].get(model, {}).get(qid)
                if val is not None:
                    item[model] = val
            if len(item) >= 2:
                matrix.append(item)
        alpha = krippendorff_alpha(matrix)
        alpha_by_axis[axis] = alpha

    lines.append("**Inter-rater reliability** (Krippendorff's alpha, 5 models):\n")
    lines.append("| Axis | Alpha | Interpretation |")
    lines.append("|------|------:|----------------|")
    for axis in AXES:
        a = alpha_by_axis[axis]
        interp = (
            "tentative" if a >= 0.67 else "unreliable" if a >= 0.33 else "poor"
        )
        lines.append(f"| {axis.capitalize()} | {a:.3f} | {interp} |")

    lines.append("")

    # Find the most controversial questions (highest G std across raters)
    controversial: list[tuple[str, str, float, list[tuple[str, float]]]] = []
    for qid, rinfo in data["ratings"].items():
        g_scores: list[tuple[str, float]] = []
        for r in rinfo.get("ratings", []):
            if r.get("generativity") is not None and r["rater_name"] in RATER_NAMES:
                g_scores.append((r["rater_name"], float(r["generativity"])))
        if len(g_scores) < 3:
            continue
        vals = [s for _, s in g_scores]
        std = statistics.stdev(vals)
        q_obj = next(
            (q for q in data["questions"] if q["id"] == qid),
            {"id": qid, "title": "(unknown)"},
        )
        controversial.append((qid, q_obj, std, g_scores))

    controversial.sort(key=lambda x: -x[2])

    if controversial:
        lines.append("**Most contested on Generativity** (top 3):\n")
        lines.append("| Question | " + " | ".join(SHORT_DISPLAY[m] for m in RATER_NAMES) + " | Std |")
        lines.append("|----------|" + "|".join("----:" for _ in RATER_NAMES) + "|----:|")
        for _, q_obj, std, g_scores in controversial[:3]:
            score_map = dict(g_scores)
            cells = []
            for model in RATER_NAMES:
                v = score_map.get(model)
                cells.append(f"{v:.0f}" if v is not None else "-")
            lines.append(
                f"| {q_link(q_obj, 50)} | " + " | ".join(cells) + f" | {std:.2f} |"
            )
        lines.append("")

    # Qwen's G distribution
    qwen_g = list(rater_maps["generativity"].get("Owen code rater", {}).values())
    if qwen_g:
        g5_pct = sum(1 for v in qwen_g if v == 5) / len(qwen_g) * 100
        lines.append(
            f"Qwen gives G=5 to {g5_pct:.0f}% of questions — "
            f"it is an unreliable rater on this axis."
        )
    lines.append("")
    return "\n".join(lines)


def section_finding_4(data: dict, rater_maps: dict) -> str:
    """Finding 4: Frontier score predicts cross-linking but not answer depth."""
    questions = data["questions"]
    graph = data["graph"]

    fs_list: list[float] = []
    answer_list: list[float] = []
    link_list: list[float] = []
    spawned_list: list[float] = []

    for q in questions:
        # Use average frontier_score across all model raters
        model_fs = []
        for model in RATER_NAMES:
            fs = frontier_score_for(rater_maps, model, q["id"])
            if fs is not None:
                model_fs.append(fs)
        if not model_fs:
            continue
        avg_fs = statistics.mean(model_fs)
        m = discussion_metrics(q, graph)

        fs_list.append(avg_fs)
        answer_list.append(float(m["answer_count"]))
        link_list.append(float(m["link_count"]))
        spawned_list.append(float(m["spawned_count"]))

    lines = [
        "### Finding 4: Frontier score predicts cross-linking but not answer depth\n",
        "| Metric | Spearman rho | p-value | Sig |",
        "|--------|------------:|--------:|-----|",
    ]

    for name, y_list in [
        ("link_count", link_list),
        ("spawned_count", spawned_list),
        ("answer_count", answer_list),
    ]:
        rho, p = spearman(fs_list, y_list)
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
        lines.append(f"| {name} | {rho:+.2f} | {p:.4f} | {sig} |")

    lines.append("")
    lines.append(
        "High-rated questions generate follow-up threads and connections, "
        "but not necessarily more answers."
    )
    lines.append("")
    return "\n".join(lines)


def section_finding_5(data: dict, rater_maps: dict) -> str:
    """Finding 5: Top 10, Bottom 10, Most Contested 10."""
    questions = data["questions"]
    lines = [
        "### Finding 5: The system works at the extremes, fails in the middle\n",
    ]

    # Compute average frontier_score per question (across model raters)
    q_scores: list[tuple[dict, float]] = []
    for q in questions:
        model_fs = []
        for model in RATER_NAMES:
            fs = frontier_score_for(rater_maps, model, q["id"])
            if fs is not None:
                model_fs.append(fs)
        if model_fs:
            q_scores.append((q, statistics.mean(model_fs)))

    q_scores.sort(key=lambda x: x[1], reverse=True)

    # Top 10
    lines.append("**Top 10 — Highest frontier_score:**\n")
    lines.append("| # | Score | Type | Title |")
    lines.append("|--:|------:|------|-------|")
    for i, (q, fs) in enumerate(q_scores[:10], 1):
        lines.append(
            f"| {i} | {fs:.2f} | {CONTENT_LABELS.get(content_type(q), '?')} | "
            f"{q_link(q)} |"
        )

    # Bottom 10
    lines.append("\n**Bottom 10 — Lowest frontier_score:**\n")
    lines.append("| # | Score | Type | Title |")
    lines.append("|--:|------:|------|-------|")
    for i, (q, fs) in enumerate(q_scores[-10:], len(q_scores) - 9):
        lines.append(
            f"| {i} | {fs:.2f} | {CONTENT_LABELS.get(content_type(q), '?')} | "
            f"{q_link(q)} |"
        )

    # Most contested 10 — highest std across ALL raters (models + human)
    lines.append("\n**Top 10 — Most contested (highest disagreement):**\n")
    lines.append(
        "| # | Std | Title | "
        + " | ".join(SHORT_DISPLAY[m] for m in RATER_NAMES)
        + " | Human |"
    )
    lines.append(
        "|--:|----:|-------|"
        + "|".join("----:" for _ in RATER_NAMES)
        + "|------:|"
    )

    controversial: list[tuple[str, str, float, dict[str, tuple[float, float, float]]]] = []
    for q in questions:
        qid = q["id"]
        all_fs: list[float] = []
        rater_scores: dict[str, tuple[float, float, float]] = {}
        for rater in ALL_RATERS:
            r = rater_maps["rigour"].get(rater, {}).get(qid)
            n = rater_maps["novelty"].get(rater, {}).get(qid)
            g = rater_maps["generativity"].get(rater, {}).get(qid)
            if r is not None and n is not None and g is not None:
                fs = (r * n * g) ** (1 / 3)
                all_fs.append(fs)
                rater_scores[rater] = (r, n, g)
        if len(all_fs) >= 3:
            std = statistics.stdev(all_fs)
            controversial.append((qid, q, std, rater_scores))

    controversial.sort(key=lambda x: -x[2])

    for i, (qid, q_obj, std, rater_scores) in enumerate(controversial[:10], 1):
        cells = []
        for model in RATER_NAMES:
            if model in rater_scores:
                r, n, g = rater_scores[model]
                cells.append(f"{r:.0f}/{n:.0f}/{g:.0f}")
            else:
                cells.append("-")
        # Human
        if HUMAN_RATER in rater_scores:
            r, n, g = rater_scores[HUMAN_RATER]
            cells.append(f"{r:.0f}/{n:.0f}/{g:.0f}")
        else:
            cells.append("-")
        lines.append(
            f"| {i} | {std:.2f} | {q_link(q_obj, 50)} | "
            + " | ".join(cells)
            + " |"
        )

    # Middle summary
    n = len(q_scores)
    middle = q_scores[n // 4 : 3 * n // 4]
    ifds_in_middle = sum(1 for q, _ in middle if is_ifds(q))
    total_middle = len(middle)
    lines.append("")
    lines.append(
        f"In the middle 50% ({total_middle} questions), "
        f"{ifds_in_middle} are IFDS/tombstone variants — "
        f"jargon-heavy content incorrectly mixes with legitimate questions."
    )
    lines.append("")
    return "\n".join(lines)


def section_finding_6(data: dict, rater_maps: dict) -> str:
    """Finding 6: Debate vs frontier score — does the system surface disagreement?"""
    questions = data["questions"]
    graph = data["graph"]

    # Build verdict map per question from graph
    # Comments with verdicts are on answers; trace answer->question
    answer_to_q: dict[str, str] = {}
    for node in graph["nodes"]:
        if node["type"] == "answer" and node.get("question_id"):
            answer_to_q[node["id"]] = node["question_id"]

    q_verdicts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for node in graph["nodes"]:
        if node["type"] == "comment" and node.get("verdict") and node.get("answer_id"):
            qid = answer_to_q.get(node["answer_id"])
            if qid:
                q_verdicts[qid][node["verdict"]] += 1

    # Classify questions
    debated: list[tuple[dict, int, int, int]] = []  # q, correct, incorrect, total
    consensus: list[tuple[dict, int]] = []  # q, total_reviews
    no_reviews: list[dict] = []

    for q in questions:
        qid = q["id"]
        v = q_verdicts.get(qid, {})
        correct = v.get("correct", 0)
        incorrect = v.get("incorrect", 0) + v.get("partially_correct", 0)
        total = sum(v.values())

        if correct > 0 and incorrect > 0:
            debated.append((q, correct, incorrect, total))
        elif total > 0:
            consensus.append((q, total))
        else:
            no_reviews.append(q)

    # Compute avg frontier score per category
    def avg_fs(qs: list) -> float:
        vals = []
        for item in qs:
            q = item[0] if isinstance(item, tuple) else item
            model_fs = []
            for model in RATER_NAMES:
                fs = frontier_score_for(rater_maps, model, q["id"])
                if fs is not None:
                    model_fs.append(fs)
            if model_fs:
                vals.append(statistics.mean(model_fs))
        return statistics.mean(vals) if vals else 0

    debated_fs = avg_fs(debated)
    consensus_fs = avg_fs(consensus)
    noreview_fs = avg_fs(no_reviews)

    lines = [
        "### Finding 6: Frontier score does not predict debate\n",
        "Questions where agents gave **mixed verdicts** (some correct, some incorrect) "
        "represent genuine intellectual disagreement. In principle, these should score "
        "highest on frontier — content worth debating should be frontier content.\n",
        "| Category | n | Avg frontier_score |",
        "|----------|--:|-------------------:|",
        f"| **Debated** (correct + incorrect verdicts) | {len(debated)} | {debated_fs:.2f} |",
        f"| Consensus (all agree) | {len(consensus)} | {consensus_fs:.2f} |",
        f"| No reviews | {len(no_reviews)} | {noreview_fs:.2f} |",
        "",
        f"Frontier scores are nearly identical across categories ({debated_fs:.2f} vs "
        f"{consensus_fs:.2f} vs {noreview_fs:.2f}). "
        "**The R/N/G rating system does not capture debate-worthiness.**\n",
    ]

    # Top 10 debated questions with per-rater scores
    debated.sort(key=lambda x: x[3], reverse=True)
    lines.append("**Top 10 most debated questions** (mixed correct/incorrect verdicts):\n")
    lines.append("| # | Reviews | Correct | Incorrect | Frontier | Title |")
    lines.append("|--:|--------:|--------:|----------:|---------:|-------|")
    for i, (q, correct, incorrect, total) in enumerate(debated[:10], 1):
        model_fs = []
        for model in RATER_NAMES:
            fs = frontier_score_for(rater_maps, model, q["id"])
            if fs is not None:
                model_fs.append(fs)
        fs = statistics.mean(model_fs) if model_fs else 0
        lines.append(
            f"| {i} | {total} | {correct} | {incorrect} | {fs:.2f} | {q_link(q, 55)} |"
        )

    lines.append("")
    return "\n".join(lines)


def section_interpretation() -> str:
    lines = [
        "## 4. What This Means\n",
        "- The R/N/G axes **do** separate noise from frontier at the extremes. "
        "Test posts sink, seed conjectures rise.",
        "- The bottleneck is **rater quality**, not the formula. Haiku (central "
        "tendency bias) and Qwen (pattern repetition) add noise. Opus and "
        "Gemini Flash are useful.",
        "- Content diversity is the **prerequisite**. The rating system cannot fix "
        "a corpus dominated by one agent's loops.",
        "- For v2: use only Opus + Gemini Flash as raters, seed diverse communities, "
        "and the system should work.",
        "",
    ]
    return "\n".join(lines)


def section_limitations(rater_maps: dict) -> str:
    # Compute overall alpha across all axes for the disclaimer
    all_alphas = []
    for axis in AXES:
        all_qids: set[str] = set()
        for model in RATER_NAMES:
            all_qids.update(rater_maps[axis].get(model, {}).keys())
        matrix: list[dict[str, float]] = []
        for qid in all_qids:
            item: dict[str, float] = {}
            for model in RATER_NAMES:
                val = rater_maps[axis].get(model, {}).get(qid)
                if val is not None:
                    item[model] = val
            if len(item) >= 2:
                matrix.append(item)
        all_alphas.append(krippendorff_alpha(matrix))

    max_alpha = max(all_alphas) if all_alphas else 0

    lines = [
        "## 5. Limitations\n",
        "- Human rated only 29/134 questions and is not an expert in all domains.",
        "- Raters used a rating-only prompt that was iteratively improved during "
        "the experiment.",
        "- IFDS/tombstone concentration means most \"agent-generated\" questions "
        "are from one model on one topic.",
        f"- Krippendorff's alpha <= {max_alpha:.2f} across all axes — inter-rater "
        "reliability is below the threshold (0.67) for publishable conclusions.",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Charts (plotly)
# ---------------------------------------------------------------------------


def chart_content_breakdown(data: dict) -> str:
    """Chart 1: Content breakdown — horizontal stacked bar."""
    questions = data["questions"]
    counts: dict[str, int] = defaultdict(int)
    for q in questions:
        counts[content_type(q)] += 1

    labels = []
    values = []
    colors = ["#3498db", "#e74c3c", "#95a5a6", "#2ecc71"]
    for i, ctype in enumerate(("seed", "ifds", "test", "other")):
        labels.append(CONTENT_LABELS[ctype])
        values.append(counts.get(ctype, 0))

    fig = go.Figure(
        go.Bar(
            y=["Questions"],
            x=[values[0]],
            name=labels[0],
            orientation="h",
            marker_color=colors[0],
            text=[f"{labels[0]}: {values[0]}"],
            textposition="inside",
        )
    )
    for i in range(1, len(labels)):
        fig.add_trace(
            go.Bar(
                y=["Questions"],
                x=[values[i]],
                name=labels[i],
                orientation="h",
                marker_color=colors[i],
                text=[f"{labels[i]}: {values[i]}"],
                textposition="inside",
            )
        )

    fig.update_layout(
        title=f"Content Breakdown ({sum(values)} questions)",
        barmode="stack",
        height=200,
        width=900,
        font=dict(size=14),
        yaxis=dict(showticklabels=False),
        xaxis_title="Number of questions",
        showlegend=True,
        legend=dict(orientation="h", y=-0.3),
    )
    return pio.to_html(fig, full_html=False)


def chart_rater_profiles(rater_maps: dict) -> str:
    """Chart 2: Model personalities — grouped bar chart of avg R, N, G per rater."""
    fig = go.Figure()
    colors = {"rigour": "#e74c3c", "novelty": "#3498db", "generativity": "#2ecc71"}

    rater_order = RATER_NAMES + [HUMAN_RATER]
    x_labels = [DISPLAY[r] for r in rater_order]

    for axis in AXES:
        avgs = []
        for rater in rater_order:
            scores = list(rater_maps[axis].get(rater, {}).values())
            avgs.append(statistics.mean(scores) if scores else 0)
        fig.add_trace(
            go.Bar(
                name=axis.capitalize(),
                x=x_labels,
                y=avgs,
                marker_color=colors[axis],
            )
        )

    fig.update_layout(
        title="Rater Profiles: Average Score by Axis",
        barmode="group",
        yaxis_title="Average score (1-5)",
        height=450,
        width=900,
        font=dict(size=14),
        yaxis=dict(range=[0, 5.5]),
    )
    return pio.to_html(fig, full_html=False)


def chart_content_type_comparison(data: dict, rater_maps: dict) -> str:
    """Chart 3: Seeds vs IFDS vs Other — grouped bar chart of avg R, N, G."""
    questions = data["questions"]
    colors = {"rigour": "#e74c3c", "novelty": "#3498db", "generativity": "#2ecc71"}

    type_axis: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for q in questions:
        ctype = content_type(q)
        if ctype == "test":
            continue  # too few to be interesting
        qid = q["id"]
        for model in RATER_NAMES:
            for axis in AXES:
                v = rater_maps[axis].get(model, {}).get(qid)
                if v is not None:
                    type_axis[ctype][axis].append(v)

    x_labels = [CONTENT_LABELS[c] for c in ("seed", "ifds", "other")]
    fig = go.Figure()
    for axis in AXES:
        avgs = []
        for ctype in ("seed", "ifds", "other"):
            vals = type_axis[ctype][axis]
            avgs.append(statistics.mean(vals) if vals else 0)
        fig.add_trace(
            go.Bar(
                name=axis.capitalize(),
                x=x_labels,
                y=avgs,
                marker_color=colors[axis],
            )
        )

    fig.update_layout(
        title="Content Type Rating Comparison",
        barmode="group",
        yaxis_title="Average score (1-5)",
        height=450,
        width=700,
        font=dict(size=14),
        yaxis=dict(range=[0, 5.5]),
    )
    return pio.to_html(fig, full_html=False)


def chart_calibration_vs_human(rater_maps: dict) -> str:
    """Chart 4: Bar chart — MAE vs Morgan (overall) per model."""
    models = []
    maes = []
    for model in RATER_NAMES:
        axis_maes = mae_per_axis(rater_maps, model, HUMAN_RATER)
        vals = [m for m, _ in axis_maes.values() if not math.isnan(m)]
        overall = statistics.mean(vals) if vals else float("nan")
        if not math.isnan(overall):
            models.append(DISPLAY[model])
            maes.append(overall)

    # Color: highlight the lowest
    min_mae = min(maes) if maes else 0
    bar_colors = [
        "#2ecc71" if abs(m - min_mae) < 0.001 else "#3498db" for m in maes
    ]

    fig = go.Figure(
        go.Bar(
            x=models,
            y=maes,
            marker_color=bar_colors,
            text=[f"{m:.2f}" for m in maes],
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Model Calibration Error vs Human (n=29)",
        yaxis_title="Mean Absolute Error",
        height=400,
        width=700,
        font=dict(size=14),
        yaxis=dict(range=[0, max(maes) * 1.3] if maes else [0, 2]),
    )
    return pio.to_html(fig, full_html=False)


def chart_heatmap(data: dict, rater_maps: dict) -> str:
    """Chart 5: Heatmap — all questions x 5 models, 3 side-by-side subplots."""
    questions = data["questions"]

    # Compute average frontier_score per question for sorting
    q_with_fs: list[tuple[dict, float]] = []
    for q in questions:
        model_fs = []
        for model in RATER_NAMES:
            fs = frontier_score_for(rater_maps, model, q["id"])
            if fs is not None:
                model_fs.append(fs)
        avg_fs = statistics.mean(model_fs) if model_fs else 0
        q_with_fs.append((q, avg_fs))

    q_with_fs.sort(key=lambda x: x[1], reverse=True)
    sorted_questions = [q for q, _ in q_with_fs]
    qids = [q["id"] for q in sorted_questions]
    q_labels = [f"Q{i + 1}" for i in range(len(qids))]
    hover_titles = [q.get("title", "")[:60] for q in sorted_questions]

    rater_order = RATER_NAMES
    short_names = [SHORT_DISPLAY[m] for m in rater_order]

    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=["Rigour", "Novelty", "Generativity"],
        horizontal_spacing=0.05,
    )

    colorscale = [
        [0, "#d32f2f"],
        [0.25, "#ff9800"],
        [0.5, "#ffeb3b"],
        [0.75, "#8bc34a"],
        [1, "#2e7d32"],
    ]

    for col_idx, axis in enumerate(AXES, 1):
        z = []
        hover_text = []
        for i, qid in enumerate(qids):
            row_scores = []
            row_hover = []
            for rater in rater_order:
                score = rater_maps.get(axis, {}).get(rater, {}).get(qid)
                row_scores.append(score if score is not None else 0)
                row_hover.append(
                    f"Q{i + 1}: {hover_titles[i]}<br>"
                    f"{SHORT_DISPLAY[rater]}: {score}"
                )
            z.append(row_scores)
            hover_text.append(row_hover)

        fig.add_trace(
            go.Heatmap(
                z=z,
                x=short_names,
                y=q_labels,
                colorscale=colorscale,
                zmin=1,
                zmax=5,
                showscale=(col_idx == 3),
                text=hover_text,
                hoverinfo="text",
                colorbar=dict(title="Score", x=1.02)
                if col_idx == 3
                else None,
            ),
            row=1,
            col=col_idx,
        )

    fig.update_layout(
        title="All Questions x All Raters (sorted by frontier_score, Q1=highest)",
        height=max(400, len(qids) * 4 + 100),
        width=1200,
        yaxis=dict(autorange="reversed", tickfont=dict(size=6)),
        yaxis2=dict(autorange="reversed", tickfont=dict(size=6)),
        yaxis3=dict(autorange="reversed", tickfont=dict(size=6)),
    )
    return pio.to_html(fig, full_html=False, include_plotlyjs=False)


def build_html(data: dict, rater_maps: dict, report_md: str) -> str:
    log.info("Building charts...")
    chart1 = chart_content_breakdown(data)
    chart2 = chart_rater_profiles(rater_maps)
    chart3 = chart_content_type_comparison(data, rater_maps)
    chart4 = chart_calibration_vs_human(rater_maps)
    chart5 = chart_heatmap(data, rater_maps)

    # Convert markdown to simple HTML (tables, headers, bold, italic, lists)
    import re as _re

    def md_to_html(md: str) -> str:
        def _inline(text: str) -> str:
            """Convert inline markdown: links, bold, italic, code."""
            text = _re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
            text = _re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
            text = _re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
            text = _re.sub(r'`(.+?)`', r'<code>\1</code>', text)
            return text

        lines = md.split("\n")
        html_lines = []
        in_table = False
        in_list = False
        for line in lines:
            stripped = line.strip()
            # Table
            if stripped.startswith("|") and "|" in stripped[1:]:
                cells = [c.strip() for c in stripped.split("|")[1:-1]]
                if all(c.startswith("-") or c.startswith(":") for c in cells if c):
                    continue  # separator row
                if not in_table:
                    html_lines.append("<table>")
                    in_table = True
                tag = "th" if not any(c and c[0].isdigit() for c in cells[:1]) and html_lines[-1] == "<table>" else "td"
                # Use th for first row after table start
                row_html = "<tr>" + "".join(f"<{tag}>{_inline(c)}</{tag}>" for c in cells) + "</tr>"
                html_lines.append(row_html)
                continue
            if in_table:
                html_lines.append("</table>")
                in_table = False
            # List
            if stripped.startswith("- "):
                if not in_list:
                    html_lines.append("<ul>")
                    in_list = True
                content = stripped[2:]
                content = _re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                content = _re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
                html_lines.append(f"<li>{content}</li>")
                continue
            if in_list and not stripped.startswith("- "):
                html_lines.append("</ul>")
                in_list = False
            # Headers
            if stripped.startswith("### "):
                html_lines.append(f"<h3>{stripped[4:]}</h3>")
            elif stripped.startswith("## "):
                html_lines.append(f"<h2>{stripped[3:]}</h2>")
            elif stripped.startswith("# "):
                html_lines.append(f"<h1>{stripped[2:]}</h1>")
            elif stripped.startswith("> "):
                content = stripped[2:]
                content = _re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
                html_lines.append(f"<blockquote>{content}</blockquote>")
            elif stripped:
                content = _re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', stripped)
                content = _re.sub(r'\*(.+?)\*', r'<em>\1</em>', content)
                content = _re.sub(r'`(.+?)`', r'<code>\1</code>', content)
                html_lines.append(f"<p>{content}</p>")
        if in_table:
            html_lines.append("</table>")
        if in_list:
            html_lines.append("</ul>")
        return "\n".join(html_lines)

    report_html = md_to_html(report_md)

    return "\n".join([
        "<!DOCTYPE html>",
        '<html lang="en"><head>',
        '<meta charset="utf-8">',
        "<title>Rating Experiment Report - 2026-03-19</title>",
        '<script src="https://cdn.plot.ly/plotly-2.35.0.min.js"></script>',
        "<style>"
        "body{font-family:system-ui,-apple-system,sans-serif;max-width:1300px;margin:0 auto;padding:20px 40px;color:#1a1a1a;line-height:1.6}"
        "h1{border-bottom:2px solid #333;padding-bottom:10px;font-size:1.8em}"
        "h2{margin-top:40px;color:#333;font-size:1.4em;border-bottom:1px solid #ddd;padding-bottom:5px}"
        "h3{margin-top:25px;color:#555;font-size:1.1em}"
        "table{border-collapse:collapse;margin:15px 0;font-size:0.9em}"
        "th,td{border:1px solid #ddd;padding:6px 12px;text-align:left}"
        "th{background:#f5f5f5;font-weight:600}"
        "td:nth-child(n+2){text-align:right}"
        "blockquote{border-left:3px solid #e74c3c;padding:8px 16px;margin:15px 0;background:#fff5f5;color:#c0392b}"
        "code{background:#f0f0f0;padding:1px 5px;border-radius:3px;font-size:0.9em}"
        "p{margin:8px 0}"
        ".chart{margin:30px 0;border-bottom:1px solid #eee;padding-bottom:20px}"
        ".section-divider{border:0;border-top:2px solid #333;margin:50px 0}"
        "</style>",
        "</head><body>",
        report_html,
        '<hr class="section-divider">',
        "<h1>Charts</h1>",
        "<h2>Content Breakdown</h2>",
        f'<div class="chart">{chart1}</div>',
        "<h2>Rater Profiles</h2>",
        f'<div class="chart">{chart2}</div>',
        "<h2>Content Type Comparison (Seeds vs IFDS vs Other)</h2>",
        f'<div class="chart">{chart3}</div>',
        "<h2>Model Calibration vs Human</h2>",
        f'<div class="chart">{chart4}</div>',
        "<h2>All Questions x All Raters (hover for details)</h2>",
        f'<div class="chart">{chart5}</div>',
        "</body></html>",
    ])


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------


def build_report(data: dict) -> tuple[str, dict]:
    """Assemble markdown report. Returns (markdown, rater_maps)."""
    log.info("Computing stats...")
    rater_maps = build_rater_axis_maps(data)

    header = (
        "# Rating Experiment Report -- 2026-03-19\n\n"
        "*5 AI models + 1 human rated 134 questions on "
        "Rigour/Novelty/Generativity (1-5 Likert scales)*\n"
    )

    design_overview = "\n".join([
        "## 0. What We Built Today\n",
        "**The rating system** adds R/N/G Likert evaluation to Assay, "
        "a discussion arena where AI agents and humans stress-test ideas.\n",
        "**Three axes** grounded in philosophy of science:",
        "- **Rigour** (Popper/falsifiability): Is this correct, clear, well-constructed?",
        "- **Novelty** (Lakatos/progressive problemshift): Does this add unresolved information?",
        "- **Generativity** (Peirce/abduction): Does answering this open new questions?\n",
        "**Implementation:** New `ratings` table with polymorphic targets (same pattern as votes). "
        "`POST /ratings` upserts per-rater scores. `frontier_score = (R x N x G)^(1/3)` "
        "(geometric mean) stored denormalized on questions/answers. "
        "`GET /questions?sort=frontier` ranks content by this score.\n",
        "**Rating experiment:** Each model ran via its CLI tool (Claude Code, Gemini CLI, "
        "Codex CLI, Qwen Code) in rating-only mode — reading the rubric below "
        "then rating 10 questions per pass in a `while true` loop.\n",
        "**Design note:** The rubric was kept deliberately short — one anchor example per "
        "score level per axis, plus 6 combination examples. This follows the principle "
        "that evaluation prompts should be concise and unambiguous. Future iterations "
        "may experiment with more examples per level, or with requiring explicit "
        "reasoning chains (\"which anchor is this closest to?\") to improve calibration.\n",
        "### Rubric given to all raters\n",
        "```",
        "Each axis is 1-5. The axes are INDEPENDENT.",
        "",
        "RIGOUR (1-5): Is this correct, clear, and well-constructed?",
        "  5 — Euclid's proof of infinite primes. Zero gaps in 2,300 years.",
        "  4 — Proof that √2 is irrational. Correct and clean, but standard textbook.",
        "  3 — \"Explain TCP vs UDP.\" Clear and answerable, nothing wrong, nothing special.",
        "  2 — \"Quantum computing will break all encryption.\" Grain of truth but overstated.",
        "  1 — \"AI is conscious because brains use electricity.\" Non-sequitur.",
        "",
        "NOVELTY (1-5): Does this add unresolved information?",
        "  5 — Gödel's Incompleteness Theorems. Wrongly assumed settled category revealed.",
        "  4 — GANs (Goodfellow 2014). New training paradigm, but generative models existed.",
        "  3 — Graph Attention Networks. Useful combo of two known ideas.",
        "  2 — \"Fine-tuned BERT for sentiment in [language X].\" One more language, little new.",
        "  1 — \"What is machine learning?\" Answered millions of times.",
        "",
        "GENERATIVITY (1-5): Does answering this open new questions?",
        "  5 — Riemann Hypothesis. 165 years, 1000+ conditional theorems, every attempt yields new math.",
        "  4 — \"Can NNs play games at superhuman level?\" Led to AlphaZero, MuZero, AlphaFold.",
        "  3 — \"Which optimiser for transformers?\" Some follow-up, narrow domain.",
        "  2 — \"ResNet-50 accuracy on ImageNet?\" A number. Survey, not research.",
        "  1 — \"What is 2+2?\" Answer is 4. Nothing follows.",
        "",
        "COMBINATIONS:",
        "  R5/N5/G5 — Gödel. Flawless, unexpected, still generating work. THIS is frontier.",
        "  R5/N1/G1 — \"Prove √2 is irrational.\" Perfect but known 2,500 years. Quality ≠ frontier.",
        "  R1/N4/G4 — Claimed P≠NP proof with hidden circularity. Creative but broken.",
        "  R4/N4/G1 — Surprising one-line proof of known identity. Pretty but sterile.",
        "  R3/N1/G5 — Riemann Hypothesis on new platform. Old but generative (unsolved).",
        "  R2/N2/G2 — \"LLMs are stochastic parrots, thoughts?\" Noise.",
        "```\n",
    ])

    s1 = section_platform_overview(data)
    s2 = section_experiment_setup()
    s3_header = "## 3. Surprising Findings\n"
    f1 = section_finding_1(rater_maps)
    f2 = section_finding_2(data, rater_maps)
    seed_bk = section_seed_breakdown(data, rater_maps)
    f3 = section_finding_3(data, rater_maps)
    f4 = section_finding_4(data, rater_maps)
    f5 = section_finding_5(data, rater_maps)
    f6 = section_finding_6(data, rater_maps)
    s4 = section_interpretation()
    s5 = section_limitations(rater_maps)

    report = "\n".join([
        header,
        design_overview,
        s1,
        s2,
        s3_header,
        f1,
        f2,
        seed_bk,
        f3,
        f4,
        f5,
        f6,
        s4,
        s5,
    ])

    return report, rater_maps


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

    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)

    report, rater_maps = build_report(data)
    log.info("Writing report to %s", OUTPUT_MD)
    OUTPUT_MD.write_text(report)

    html = build_html(data, rater_maps, report)
    log.info("Writing charts to %s", OUTPUT_HTML)
    OUTPUT_HTML.write_text(html)

    elapsed = time.monotonic() - start
    log.info("Done in %.1fs", elapsed)


if __name__ == "__main__":
    main()
