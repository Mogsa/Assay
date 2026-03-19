#!/usr/bin/env python3
"""Generate rating analysis report for dissertation advisor.

Framing: Opus 4.6 is the reference standard (134 questions).
Human (Morgan, 29 questions) validates Opus.
Four small models are calibrated against Opus.

Queries the Assay API, collects all rating and discussion data, and produces:
  - docs/analysis/2026-03-19-rating-analysis.md  (prose report)
  - docs/analysis/2026-03-19-rating-charts.html   (interactive plotly charts)

No auth needed. Run from repo root:
  python scripts/generate-rating-report.py
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

OPUS_RATER = "opus 4.6 rater"
HUMAN_RATER = "morgan"
SMALL_MODELS = ["Haiku rater", "gemini flash rater", "gpt 5.4 mini rater", "Owen code rater"]

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
    return api_get(client, "/ratings", {"target_type": "question", "target_id": question_id})


def fetch_graph(client: httpx.Client) -> dict:
    return api_get(client, "/analytics/graph", {"limit": 200})


def fetch_calibration(client: httpx.Client) -> dict:
    return api_get(client, "/analytics/calibration")


# ---------------------------------------------------------------------------
# Statistics (no scipy/numpy)
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
    # Approximate p using normal CDF for large-ish n
    p = 2 * (1 - _norm_cdf(abs(t_stat)))
    return rho, max(p, 0.0)


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2)))


def mae_between(
    scores_a: dict[str, float],
    scores_b: dict[str, float],
) -> tuple[float, int]:
    """MAE between two raters on their shared questions. Returns (mae, n)."""
    diffs = []
    for qid in scores_a:
        if qid in scores_b:
            diffs.append(abs(scores_a[qid] - scores_b[qid]))
    if not diffs:
        return float("nan"), 0
    return statistics.mean(diffs), len(diffs)


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
# Data collection
# ---------------------------------------------------------------------------


def collect_data(client: httpx.Client) -> dict:
    log.info("Fetching questions...")
    questions = fetch_all_questions(client)
    log.info("  got %d questions", len(questions))

    log.info("Fetching graph...")
    graph = fetch_graph(client)
    log.info("  got %d nodes, %d edges", len(graph["nodes"]), len(graph["edges"]))

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
# Data indexing helpers
# ---------------------------------------------------------------------------


def is_seed(q: dict) -> bool:
    return q.get("title", "").startswith("[Seed]")


def question_source(q: dict) -> str:
    return "seed" if is_seed(q) else "agent"


def find_title(questions: list[dict], qid: str) -> str:
    for q in questions:
        if q["id"] == qid:
            return q.get("title", "(untitled)")
    return "(unknown)"


def build_rater_axis_maps(data: dict) -> dict[str, dict[str, dict[str, float]]]:
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
    nodes_by_id = {n["id"]: n for n in graph["nodes"]}
    edges_from: dict[str, list[dict]] = defaultdict(list)
    for e in graph["edges"]:
        edges_from[e["source"]].append(e)
    return {"nodes": nodes_by_id, "from": edges_from}


def discussion_metrics(q: dict, gidx: dict) -> dict:
    qid = q["id"]
    node = gidx["nodes"].get(qid, {})
    answer_count = q.get("answer_count", 0) or node.get("answer_count", 0)
    link_count = node.get("link_count", 0)
    spawned = sum(
        1 for e in gidx["from"].get(qid, []) if e.get("edge_type") == "extends"
    )
    return {
        "answer_count": answer_count,
        "link_count": link_count,
        "spawned_count": spawned,
    }


# ---------------------------------------------------------------------------
# Section 1: Human validates Opus
# ---------------------------------------------------------------------------


def section_human_validates_opus(rater_maps: dict) -> tuple[str, dict[str, float]]:
    """Returns (markdown, {axis: mae}) for later use in key findings."""
    lines = [
        "## 1. Human validates Opus (29 questions)\n",
    ]

    mae_by_axis: dict[str, float] = {}
    n_overlap = 0

    for axis in AXES:
        opus_scores = rater_maps[axis].get(OPUS_RATER, {})
        human_scores = rater_maps[axis].get(HUMAN_RATER, {})
        val, n = mae_between(opus_scores, human_scores)
        mae_by_axis[axis] = val
        if n > n_overlap:
            n_overlap = n

    if n_overlap == 0:
        lines.append("No overlapping questions between Morgan and Opus.\n")
        return "\n".join(lines), mae_by_axis

    parts = []
    for axis in AXES:
        val = mae_by_axis[axis]
        if math.isnan(val):
            parts.append(f"n/a on {axis}")
        else:
            parts.append(f"**{val:.2f}** on {axis}")
    lines.append(f"Morgan and Opus agree within {', '.join(parts)} (n={n_overlap}).\n")

    all_below_one = all(not math.isnan(v) and v < 1.0 for v in mae_by_axis.values())
    if all_below_one:
        lines.append(
            "**Conclusion:** MAE < 1.0 on all axes — Opus is a trustworthy proxy for human judgement.\n"
        )
    else:
        over = [a for a in AXES if not math.isnan(mae_by_axis[a]) and mae_by_axis[a] >= 1.0]
        lines.append(
            f"**Conclusion:** MAE >= 1.0 on {', '.join(over)} — Opus diverges from human on "
            f"{'this axis' if len(over) == 1 else 'these axes'}.\n"
        )

    return "\n".join(lines), mae_by_axis


# ---------------------------------------------------------------------------
# Section 2: Small models calibrated against Opus
# ---------------------------------------------------------------------------


def section_small_vs_opus(rater_maps: dict) -> tuple[str, dict[str, dict[str, float]]]:
    """Returns (markdown, {model: {axis: mae}}) for charts and findings."""
    lines = [
        "## 2. Small models calibrated against Opus (134 questions)\n",
        "### MAE vs Opus per axis\n",
        "| Model | Rigour | Novelty | Generativity | Overall |",
        "|-------|-------:|--------:|-------------:|--------:|",
    ]

    model_errors: dict[str, dict[str, float]] = {}

    for model in SMALL_MODELS:
        errs: dict[str, float] = {}
        for axis in AXES:
            opus_scores = rater_maps[axis].get(OPUS_RATER, {})
            model_scores = rater_maps[axis].get(model, {})
            val, _ = mae_between(opus_scores, model_scores)
            errs[axis] = val
        valid = [v for v in errs.values() if not math.isnan(v)]
        errs["overall"] = statistics.mean(valid) if valid else float("nan")
        model_errors[model] = errs

        r_str = f"{errs['rigour']:.2f}" if not math.isnan(errs["rigour"]) else "n/a"
        n_str = f"{errs['novelty']:.2f}" if not math.isnan(errs["novelty"]) else "n/a"
        g_str = f"{errs['generativity']:.2f}" if not math.isnan(errs["generativity"]) else "n/a"
        o_str = f"{errs['overall']:.2f}" if not math.isnan(errs["overall"]) else "n/a"
        lines.append(f"| {model} | {r_str} | {n_str} | {g_str} | {o_str} |")

    # Ranking
    ranked = sorted(
        model_errors.items(),
        key=lambda x: x[1].get("overall", float("inf")),
    )
    best_name, best_errs = ranked[0]
    best_overall = best_errs.get("overall", float("nan"))
    lines.append("")
    lines.append(
        f"**Closest to Opus:** {best_name} (overall MAE = {best_overall:.2f})"
    )
    lines.append("")

    # Krippendorff's alpha between small models
    lines.append("### Inter-rater agreement among small models (Krippendorff's alpha)\n")
    lines.append("| Axis | Alpha |")
    lines.append("|------|------:|")
    for axis in AXES:
        # Build matrix: one dict per question, keys = small model names
        all_qids = set()
        for model in SMALL_MODELS:
            all_qids.update(rater_maps[axis].get(model, {}).keys())
        matrix: list[dict[str, float]] = []
        for qid in all_qids:
            item: dict[str, float] = {}
            for model in SMALL_MODELS:
                val = rater_maps[axis].get(model, {}).get(qid)
                if val is not None:
                    item[model] = val
            if len(item) >= 2:
                matrix.append(item)
        alpha = krippendorff_alpha(matrix)
        lines.append(f"| {axis} | {alpha:.3f} |")
    lines.append("")

    return "\n".join(lines), model_errors


# ---------------------------------------------------------------------------
# Section 3: Did frontier_score surface the right content?
# ---------------------------------------------------------------------------


def section_frontier_ranking(data: dict) -> tuple[str, dict]:
    """Returns (markdown, stats_dict) for findings."""
    questions = sorted(
        data["questions"],
        key=lambda q: q.get("frontier_score") or 0,
        reverse=True,
    )
    lines = [
        "## 3. Did frontier_score surface the right content?\n",
        "### Top 10 by frontier_score\n",
        "| Rank | Score | Source | Title |",
        "|-----:|------:|--------|-------|",
    ]
    for i, q in enumerate(questions[:10]):
        fs = q.get("frontier_score") or 0
        lines.append(f"| {i + 1} | {fs:.2f} | {question_source(q)} | {q['title'][:70]} |")

    lines.append("")
    lines.append("### Bottom 10 by frontier_score\n")
    lines.append("| Rank | Score | Source | Title |")
    lines.append("|-----:|------:|--------|-------|")
    bottom = questions[-10:]
    for i, q in enumerate(bottom):
        fs = q.get("frontier_score") or 0
        rank = len(questions) - len(bottom) + i + 1
        lines.append(f"| {rank} | {fs:.2f} | {question_source(q)} | {q['title'][:70]} |")

    seed_scores = [q.get("frontier_score") or 0 for q in questions if is_seed(q)]
    agent_scores = [q.get("frontier_score") or 0 for q in questions if not is_seed(q)]

    stats = {}
    lines.append("")
    if seed_scores:
        seed_avg = statistics.mean(seed_scores)
        stats["seed_avg"] = seed_avg
        lines.append(f"Seed avg: **{seed_avg:.2f}** (n={len(seed_scores)})")
    if agent_scores:
        agent_avg = statistics.mean(agent_scores)
        stats["agent_avg"] = agent_avg
        lines.append(f"Agent-generated avg: **{agent_avg:.2f}** (n={len(agent_scores)})")

    if seed_scores and agent_scores:
        if statistics.mean(agent_scores) > statistics.mean(seed_scores):
            lines.append(
                "\n> **Warning:** agent-generated questions score higher than seeds — "
                "models may be fooled by jargon."
            )
    lines.append("")
    return "\n".join(lines), stats


# ---------------------------------------------------------------------------
# Section 4: Ratings predict discussion activity
# ---------------------------------------------------------------------------


def section_discussion_correlation(data: dict) -> tuple[str, dict[str, tuple[float, float]]]:
    gidx = build_graph_index(data["graph"])
    questions = data["questions"]

    fs_list: list[float] = []
    metrics_lists: dict[str, list[float]] = {
        "answer_count": [],
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
        "## 4. Ratings predict discussion activity\n",
        "| Metric | Spearman rho | p-value | n |",
        "|--------|------------:|--------:|--:|",
    ]
    correlations: dict[str, tuple[float, float]] = {}
    for k in ("answer_count", "link_count", "spawned_count"):
        rho, p = spearman(fs_list, metrics_lists[k])
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        lines.append(f"| {k} | {rho:+.3f}{sig} | {p:.4f} | {len(fs_list)} |")
        correlations[k] = (rho, p)

    lines.append("")
    return "\n".join(lines), correlations


# ---------------------------------------------------------------------------
# Section 5: Disagreement patterns
# ---------------------------------------------------------------------------


def section_disagreement(data: dict, rater_maps: dict) -> tuple[str, list[tuple[str, float]]]:
    """Top 5 most controversial questions (highest std across ALL 6 raters)."""
    question_stds: list[tuple[str, str, float, list[tuple[str, dict[str, float]]]]] = []

    for qid, rinfo in data["ratings"].items():
        ratings = rinfo.get("ratings", [])
        if len(ratings) < 3:
            continue
        all_scores: list[float] = []
        per_rater: list[tuple[str, dict[str, float]]] = []
        for r in ratings:
            rater_scores = {}
            for a in AXES:
                if r.get(a) is not None:
                    rater_scores[a] = float(r[a])
                    all_scores.append(float(r[a]))
            per_rater.append((r["rater_name"], rater_scores))
        if len(all_scores) < 6:
            continue
        std = statistics.stdev(all_scores)
        title = find_title(data["questions"], qid)
        question_stds.append((qid, title, std, per_rater))

    question_stds.sort(key=lambda x: -x[2])
    top5 = question_stds[:5]

    lines = [
        "## 5. Disagreement patterns\n",
        "### Top 5 most controversial questions (highest score std across all raters)\n",
    ]

    type_counts: dict[str, int] = defaultdict(int)
    controversial_items: list[tuple[str, float]] = []

    for rank, (qid, title, std, per_rater) in enumerate(top5, 1):
        q = next((q for q in data["questions"] if q["id"] == qid), {})
        qtype = question_source(q)
        type_counts[qtype] += 1
        controversial_items.append((title, std))

        lines.append(f"**{rank}. {title[:70]}** (std={std:.2f}, source={qtype})\n")
        lines.append("| Rater | R | N | G |")
        lines.append("|-------|--:|--:|--:|")
        for rname, scores in per_rater:
            r_val = f"{scores['rigour']:.0f}" if "rigour" in scores else "-"
            n_val = f"{scores['novelty']:.0f}" if "novelty" in scores else "-"
            g_val = f"{scores['generativity']:.0f}" if "generativity" in scores else "-"
            lines.append(f"| {rname} | {r_val} | {n_val} | {g_val} |")
        lines.append("")

    if type_counts:
        most_controversial_type = max(type_counts, key=lambda k: type_counts[k])
        lines.append(
            f"Most disagreement on **{most_controversial_type}** questions "
            f"({type_counts[most_controversial_type]}/{len(top5)} in top 5).\n"
        )

    return "\n".join(lines), controversial_items


# ---------------------------------------------------------------------------
# Section 6: Key findings (computed, NOT placeholders)
# ---------------------------------------------------------------------------


def section_key_findings(
    human_opus_mae: dict[str, float],
    model_errors: dict[str, dict[str, float]],
    frontier_stats: dict,
    correlations: dict[str, tuple[float, float]],
    controversial: list[tuple[str, float]],
) -> str:
    lines = ["## 6. Key findings\n"]

    # 1. Human-Opus agreement
    valid_maes = {a: v for a, v in human_opus_mae.items() if not math.isnan(v)}
    if valid_maes:
        max_axis = max(valid_maes, key=lambda a: valid_maes[a])
        avg_mae = statistics.mean(valid_maes.values())
        trustworthy = all(v < 1.0 for v in valid_maes.values())
        if trustworthy:
            lines.append(
                f"1. **Opus is a valid human proxy.** Average MAE vs Morgan = {avg_mae:.2f} "
                f"across R/N/G (all < 1.0). Largest gap on {max_axis} ({valid_maes[max_axis]:.2f})."
            )
        else:
            lines.append(
                f"1. **Opus partially agrees with human.** Average MAE = {avg_mae:.2f}. "
                f"{max_axis} diverges most ({valid_maes[max_axis]:.2f})."
            )
    else:
        lines.append("1. **No human-Opus overlap data available.**")

    # 2. Best small model
    ranked = sorted(
        model_errors.items(),
        key=lambda x: x[1].get("overall", float("inf")),
    )
    if ranked:
        best_name, best_errs = ranked[0]
        worst_name, worst_errs = ranked[-1]
        lines.append(
            f"2. **{best_name}** is closest to Opus (MAE={best_errs['overall']:.2f}). "
            f"**{worst_name}** is furthest (MAE={worst_errs['overall']:.2f})."
        )

    # 3. Frontier score effectiveness
    seed_avg = frontier_stats.get("seed_avg")
    agent_avg = frontier_stats.get("agent_avg")
    if seed_avg is not None and agent_avg is not None:
        if agent_avg > seed_avg:
            lines.append(
                f"3. **Agent-generated questions outscore seeds** ({agent_avg:.2f} vs {seed_avg:.2f}) — "
                f"models may reward jargon over substance."
            )
        else:
            lines.append(
                f"3. **Seeds outscore agent-generated** ({seed_avg:.2f} vs {agent_avg:.2f}) — "
                f"frontier_score correctly ranks curated content higher."
            )
    else:
        lines.append("3. **Insufficient data to compare seed vs agent frontier scores.**")

    # 4. Discussion correlation
    answer_rho, answer_p = correlations.get("answer_count", (0.0, 1.0))
    if answer_p < 0.05:
        lines.append(
            f"4. **Frontier score predicts discussion.** "
            f"Spearman rho = {answer_rho:+.2f} with answer_count (p={answer_p:.4f})."
        )
    else:
        lines.append(
            f"4. **Frontier score does NOT significantly predict discussion** "
            f"(rho={answer_rho:+.2f}, p={answer_p:.2f})."
        )

    # 5. Disagreement
    if controversial:
        avg_std = statistics.mean(s for _, s in controversial)
        lines.append(
            f"5. **High disagreement persists.** Top 5 controversial questions average "
            f"std={avg_std:.2f} across raters. Most contested: \"{controversial[0][0][:50]}\"."
        )
    else:
        lines.append("5. **Insufficient data to assess disagreement patterns.**")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------


def chart_small_model_error_vs_opus(model_errors: dict[str, dict[str, float]]) -> str:
    """Chart 1: Grouped bar chart — small model MAE vs Opus per axis."""
    fig = go.Figure()
    colors = {"rigour": "#e74c3c", "novelty": "#3498db", "generativity": "#2ecc71"}
    names = list(model_errors.keys())

    for axis in AXES:
        errs = []
        for model in names:
            val = model_errors[model].get(axis, 0)
            errs.append(val if not math.isnan(val) else 0)
        fig.add_trace(go.Bar(
            name=AXIS_SHORT[axis] + " error",
            x=names,
            y=errs,
            marker_color=colors[axis],
        ))

    fig.update_layout(
        title="Small Model Calibration Error vs Opus 4.6",
        barmode="group",
        yaxis_title="Mean Absolute Error",
        xaxis_title="Model",
        height=450,
        width=850,
        font=dict(size=14),
    )
    return pio.to_html(fig, full_html=False)


def chart_score_distributions(rater_maps: dict) -> str:
    """Chart 2: Box plots — score distributions by rater, 3 subplots for R/N/G."""
    all_raters = [OPUS_RATER, HUMAN_RATER] + SMALL_MODELS
    palette = [
        "#8e44ad",  # opus — purple
        "#e67e22",  # morgan — orange
        "#3498db",  # haiku — blue
        "#e74c3c",  # gemini — red
        "#2ecc71",  # gpt — green
        "#f39c12",  # owen — yellow
    ]

    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=["Rigour", "Novelty", "Generativity"],
        horizontal_spacing=0.08,
    )

    for col, axis in enumerate(AXES, 1):
        for i, rater in enumerate(all_raters):
            scores = list(rater_maps[axis].get(rater, {}).values())
            if not scores:
                continue
            fig.add_trace(
                go.Box(
                    y=scores,
                    name=rater[:15],
                    marker_color=palette[i % len(palette)],
                    showlegend=(col == 1),
                    legendgroup=rater,
                ),
                row=1, col=col,
            )

    fig.update_layout(
        title="Score Distributions by Rater and Axis",
        height=500,
        width=1200,
        font=dict(size=13),
    )
    return pio.to_html(fig, full_html=False)


def chart_frontier_vs_discussion(data: dict) -> str:
    """Chart 3: Scatter — frontier_score vs answer_count, colored by source."""
    questions = data["questions"]
    seeds = [q for q in questions if is_seed(q)]
    agents = [q for q in questions if not is_seed(q)]

    fig = go.Figure()

    for group, color, label in [(seeds, "blue", "[Seed]"), (agents, "orange", "Agent-generated")]:
        x = [q.get("frontier_score") or 0 for q in group]
        y = [q.get("answer_count") or 0 for q in group]
        texts = [q["title"][:60] for q in group]
        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode="markers",
            marker=dict(color=color, size=8, opacity=0.7),
            text=texts,
            hoverinfo="text+x+y",
            name=label,
        ))

    # OLS trendline
    all_x = [q.get("frontier_score") or 0 for q in questions if q.get("frontier_score") is not None]
    all_y = [q.get("answer_count") or 0 for q in questions if q.get("frontier_score") is not None]
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
                x=x_line, y=y_line,
                mode="lines",
                line=dict(color="gray", dash="dash"),
                name=f"OLS (slope={slope:.2f})",
            ))

    fig.update_layout(
        title="Frontier Score vs Discussion Depth",
        xaxis_title="frontier_score",
        yaxis_title="answer_count",
        height=500,
        width=800,
        font=dict(size=13),
    )
    return pio.to_html(fig, full_html=False)


def chart_human_vs_opus(rater_maps: dict) -> str:
    """Chart 4: Scatter — Morgan vs Opus on 29 overlapping questions, 3 subplots."""
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=["Rigour", "Novelty", "Generativity"],
        horizontal_spacing=0.08,
    )

    for col, axis in enumerate(AXES, 1):
        opus_scores = rater_maps[axis].get(OPUS_RATER, {})
        human_scores = rater_maps[axis].get(HUMAN_RATER, {})
        shared_qids = sorted(set(opus_scores) & set(human_scores))

        x = [opus_scores[qid] for qid in shared_qids]
        y = [human_scores[qid] for qid in shared_qids]

        # Perfect agreement diagonal
        if x:
            lo = min(min(x), min(y)) - 0.5
            hi = max(max(x), max(y)) + 0.5
        else:
            lo, hi = 0.5, 5.5
        fig.add_trace(
            go.Scatter(
                x=[lo, hi], y=[lo, hi],
                mode="lines",
                line=dict(color="lightgray", dash="dash"),
                showlegend=False,
            ),
            row=1, col=col,
        )

        # Data points
        fig.add_trace(
            go.Scatter(
                x=x, y=y,
                mode="markers",
                marker=dict(color="#8e44ad", size=9, opacity=0.8),
                showlegend=False,
            ),
            row=1, col=col,
        )

        fig.update_xaxes(title_text="Opus score", row=1, col=col)
        fig.update_yaxes(title_text="Morgan score", row=1, col=col)

    n_points = len(set(rater_maps[AXES[0]].get(OPUS_RATER, {})) &
                    set(rater_maps[AXES[0]].get(HUMAN_RATER, {})))
    fig.update_layout(
        title=f"Human vs Opus Agreement (n={n_points})",
        height=450,
        width=1200,
        font=dict(size=13),
    )
    return pio.to_html(fig, full_html=False)


def build_html(data: dict, rater_maps: dict, model_errors: dict) -> str:
    log.info("Building charts...")
    chart1 = chart_small_model_error_vs_opus(model_errors)
    chart2 = chart_score_distributions(rater_maps)
    chart3 = chart_frontier_vs_discussion(data)
    chart4 = chart_human_vs_opus(rater_maps)

    return "\n".join([
        "<!DOCTYPE html>",
        '<html lang="en"><head>',
        '<meta charset="utf-8">',
        "<title>Rating Analysis Charts - 2026-03-19</title>",
        '<script src="https://cdn.plot.ly/plotly-2.35.0.min.js"></script>',
        "<style>"
        "body{font-family:system-ui,sans-serif;max-width:1300px;margin:0 auto;padding:20px}"
        "h1{border-bottom:2px solid #333;padding-bottom:10px}"
        "h2{margin-top:40px;color:#555}"
        ".chart{margin:30px 0;border-bottom:1px solid #eee;padding-bottom:20px}"
        "</style>",
        "</head><body>",
        "<h1>Rating Analysis Charts (2026-03-19)</h1>",
        "<h2>1. Small Model Calibration Error vs Opus</h2>",
        f'<div class="chart">{chart1}</div>',
        "<h2>2. Score Distributions by Rater</h2>",
        f'<div class="chart">{chart2}</div>',
        "<h2>3. Frontier Score vs Discussion Depth</h2>",
        f'<div class="chart">{chart3}</div>',
        "<h2>4. Human vs Opus Agreement</h2>",
        f'<div class="chart">{chart4}</div>',
        "</body></html>",
    ])


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------


def build_report(data: dict) -> tuple[str, dict, dict]:
    """Assemble markdown report. Returns (markdown, rater_maps, model_errors)."""
    log.info("Computing stats...")
    rater_maps = build_rater_axis_maps(data)

    n_questions = len(data["questions"])
    n_seeds = sum(1 for q in data["questions"] if is_seed(q))
    n_rated = len(data["ratings"])

    # Count questions Opus rated
    opus_qids = set()
    for axis in AXES:
        opus_qids.update(rater_maps[axis].get(OPUS_RATER, {}).keys())
    n_opus = len(opus_qids)

    # Count questions human rated
    human_qids = set()
    for axis in AXES:
        human_qids.update(rater_maps[axis].get(HUMAN_RATER, {}).keys())
    n_human = len(human_qids)

    header = (
        f"# Rating Analysis Report (2026-03-19)\n\n"
        f"**{n_questions} questions** | **{n_seeds} seeds** | **{n_rated} rated**\n\n"
        f"**Reference:** Opus 4.6 ({n_opus} questions) | "
        f"**Validator:** Morgan ({n_human} questions) | "
        f"**Calibration targets:** 4 small models\n"
    )

    s1_md, human_opus_mae = section_human_validates_opus(rater_maps)
    s2_md, model_errors = section_small_vs_opus(rater_maps)
    s3_md, frontier_stats = section_frontier_ranking(data)
    s4_md, correlations = section_discussion_correlation(data)
    s5_md, controversial = section_disagreement(data, rater_maps)
    s6_md = section_key_findings(
        human_opus_mae, model_errors, frontier_stats, correlations, controversial,
    )

    report = "\n".join([
        header,
        s1_md,
        s2_md,
        s3_md,
        s4_md,
        s5_md,
        s6_md,
    ])

    return report, rater_maps, model_errors


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

    report, rater_maps, model_errors = build_report(data)
    log.info("Writing report to %s", OUTPUT_MD)
    OUTPUT_MD.write_text(report)

    html = build_html(data, rater_maps, model_errors)
    log.info("Writing charts to %s", OUTPUT_HTML)
    OUTPUT_HTML.write_text(html)

    elapsed = time.monotonic() - start
    log.info("Done in %.1fs", elapsed)


if __name__ == "__main__":
    main()
