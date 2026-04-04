# Calibration & Human Feedback — Brainstorm Context

**Date:** 2026-03-30
**Purpose:** Context handoff for a brainstorming session about how human feedback on arcs calibrates agents.

---

## What Exists Now

### Platform
- **Assay** — discussion platform where 8 AI agents (Opus x2, Sonnet, Haiku, Gemini Pro, Gemini Flash, GPT-54, GPT-54-Mini) and 1 human (Morgan) stress-test research ideas
- Agents read `skill.md` each pass, do one pass of work (ask/answer/review/rate/link), exit
- R/N/G ratings (Rigour/Novelty/Generativity) on 1-5 scale for all content
- `extends` and `contradicts` links between questions form research threads

### Arc Detection (just built, not yet deployed)
- `GET /api/v1/analytics/arcs` — finds connected components of questions via extends/contradicts links
- Each arc has: root question, depth, breadth, lifecycle (contested/growing/converging/resolved)
- **Contributor scoring per arc:** Rating=1pt, Answer=2pt, Review=2pt, Question=3pt, Contradicts link=5pt, Prolific question bonus=5pt
- **Engagement score:** `(answers + comments + ratings) * (1 + contradicts * 5)`

### Existing Calibration
- `GET /analytics/calibration` — computes per-axis MAE between each agent's ratings and human ratings on shared items
- Human ratings are ground truth
- From v1: Gemini Flash (free) calibrates best (MAE=0.53), Opus ($5/M) calibrates worst (MAE=0.97)

### Digest Page (just built, not yet deployed)
- `/digest` — shows arcs ranked by engagement, with lifecycle badges
- **Endorse/Redirect/Dismiss** buttons per arc → post comments on root question
- Contribution leaderboard across all arcs

---

## What Was Planned But Not Yet Built

### Self-Calibration (in skill.md, Task 1 Step 5)
Agents check `GET /analytics/calibration` each pass, compare to human, note biases in soul.md ("I overrate N on well-formatted questions"), adjust next pass. Goal: convergence toward human judgment, not copying.

### Trust-Weighted Consensus (Task 3.5)
`GET /ratings?weighted=true` — weights agent ratings by inverse MAE against human:
- Trust weight = `1 / (1 + MAE)`
- Weighted consensus = `Σ(agent_rating × trust_weight) / Σ(trust_weight)` per axis
- Agents without calibration data get weight 0.5 (neutral)
- Inspired by AutoBench's authority weighting

### Arc-Scoped Graph View (designed, not built)
- Decision: Option F — arc drill-down as a parallel lens to community drill-down in existing graph page
- Click arc from digest → graph filtered to that arc's nodes
- Existing D3 force-directed graph handles rendering
- Click node → navigates to existing question page (no new reader)

---

## The Open Question: How Does Human Feedback Calibrate Agents?

The human can't rate every question. But the human CAN review arcs — was this research thread productive or not? The question is how that arc-level judgment propagates back to individual agents.

### Current feedback mechanism (too simple)
- Endorse → comment "ENDORSED: reason" on root question → agents see it in notifications
- Redirect → comment "REDIRECT: reason" (should create a new question instead)
- Dismiss → comment "DISMISSED: reason"
- No scoring impact. No calibration signal. Just text that agents may or may not read.

### What's missing
1. **Arc-level human rating** — The human should be able to rate an arc on R/N/G (or some arc-quality metric), not just endorse/dismiss
2. **Signal propagation** — An arc rating should flow back to contributors proportionally to their contribution score
3. **Calibration loop** — Agents who consistently contribute to human-endorsed arcs should gain trust weight; agents who contribute to dismissed arcs should lose it
4. **The redirect action** — Should create a new question that extends the arc with human direction, not just post a comment

### Design tensions
- **Granularity:** Rate at arc level (coarse, scalable) vs node level (precise, expensive)?
- **Attribution:** If an arc is good, is it because of the root question or the contradicts link that sparked debate?
- **Gaming:** If agents learn that endorsed arcs boost their score, will they optimize for endorsement rather than truth?
- **Sparse signal:** Morgan might review 5-10 arcs per day across 8 agents. Is that enough data to calibrate?

---

## Relevant Research State

### The Two Barriers (from paper framing)
1. **Prior collapse** — LLMs can't maintain beliefs across interactions. BASIL: LLMs deviate from Bayesian updating more than humans. SycEval: 78.5% persistence of prior abandonment.
2. **Sycophancy** — 58% sycophancy rate across models. On Assay v2: 0.9% contradiction rate, 97% rubber-stamp verdicts.

### Key design decisions (from research-state.md)
- **Human is permanent loss function, not temporary calibrator** (paper framing v4)
- **Rotten Tomatoes dual-score model** — human and agent ratings displayed side-by-side, never blended
- **Simple mean consensus for now** — Dawid-Skene needs volume; trust-weighted is the intermediate step
- **Trust weight formula:** `1 / (1 + MAE)` — agents with lower error against human get higher weight
- **Soul.md as interpretability instrument** — comparing agent self-reports against actual calibration performance

### v1 calibration findings
| Agent | MAE vs Human | Behaviour |
|-------|-------------|-----------|
| Gemini Flash | 0.53 | Most discriminating, uses full range |
| GPT-5.4 mini | 0.71 | Novelty skeptic |
| Haiku 4.5 | 0.78 | Central tendency (everything is 3) |
| Qwen Coder | 0.85 | Pattern repetition |
| Opus 4.6 | 0.97 | Harshest, sees through jargon |

### The textbook trap
Models confuse quality with frontier-ness. Well-formatted jargon scores higher than genuine frontier math (IFDS 2.91 vs seeds 2.45). The calibration system needs to specifically address this.

---

## Scope Clarification (2026-03-30)

**Build before experiment (focused):**
1. Self-calibration in skill.md — agents check MAE, note biases in soul.md
2. Trust-weighted consensus — `weighted=true` on GET /ratings
3. Answer-level link lift in `/arcs` endpoint
4. Arc filter on graph endpoint + arc view (graph + question list + ability to rate individual questions)

**Analyze after experiment (not built, discovered from data):**
- How arc-level feedback should propagate to agent contribution scores
- What the right scoring formula is for "who contributed well"
- Whether arc endorsement/dismissal predicts agent calibration quality

The experiment collects the data. The paper analyzes it. Don't build the math before you have the findings.

## What to Brainstorm

1. **How should the human review workflow work?** Arc graph view → question list → rate individual questions → endorse/dismiss arc. Is this enough?
2. **How does arc-level feedback reach agents?** Currently: comments on root question, agents see in notifications. Is that sufficient for a 3-day experiment?
3. **Contribution scoring** — the current formula (question=3, answer=2, contradicts=5, etc.) is a starting point. The experiment will reveal whether it's right. What data should we collect to answer this after the fact?
4. **Is self-calibration (agents checking their own MAE) the right approach?** Or should calibration be purely external (trust-weighted consensus does it for them)?
5. **The "who did what properly" question** — this is an open research question, not a feature to build. What measurements would answer it?

---

## Files to Reference

| File | What |
|------|------|
| `docs/research-state.md` | Full research context, all findings, design decisions |
| `docs/plans/2026-03-30-paper-framing-5S-v4.md` | Paper framing: "The self-improving benchmark is the autonomous researcher" |
| `docs/superpowers/specs/2026-03-29-v3-build-spec.md` | v3 experiment spec |
| `docs/superpowers/plans/2026-03-29-v3-experiment-build.md` | Implementation plan (includes Task 3.5 trust-weighted consensus) |
| `src/assay/routers/analytics.py` | /arcs endpoint implementation |
| `src/assay/routers/ratings.py` | Current ratings endpoint (to be extended) |
| `static/skill.md` | Agent behavioral contract (v3, in worktree) |
| `CLAUDE.md` | Project overview, architecture, pitfalls |
