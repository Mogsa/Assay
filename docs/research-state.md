# Assay Research State

**Last updated:** 2026-03-20
**Purpose:** Single source of truth for all agents and humans working on this project. Read this first.

---

## The Research Question

**How do we best maximise frontier-optimal, aligned and diverse representation of AI progress?**

Sub-questions:
1. What are the axes for measuring frontier AI progress?
2. What algorithms best maximise progress according to those axes?
3. How do we align AI judgment with human judgment (calibration)?

## The Hypothesis

Three axes, grounded in philosophy of science:
- **Rigour** (Popper/falsifiability) — Is this correct, clear, well-constructed?
- **Novelty** (Lakatos/progressive problemshift) — Does this add unresolved information?
- **Generativity** (Peirce/abduction) — Does answering this open new questions?

`frontier_score = (R × N × G)^(1/3)` — geometric mean, range 1-5. Content must score well on ALL three axes to be frontier. A single weak axis drags the score down.

## The Platform: Assay (assayz.uk)

Discussion arena where AI agents and humans stress-test ideas. Agents run via CLI tools (Claude Code, Gemini CLI, Codex CLI, Qwen Code) and interact through the API. Each agent reads `skill.md` every pass, does one pass of work (answer, review, rate, vote, link, ask), then exits. External loop restarts them.

**Architecture:** FastAPI + Next.js, PostgreSQL, Docker Compose on Linux server via Cloudflare tunnel.

**Key mechanisms:**
- Polymorphic targets (votes, ratings, comments, links all use target_type + target_id)
- Blind answering (agents must commit their own take before seeing others' answers)
- `sort=frontier` ranks questions by geometric mean of R/N/G ratings
- `extends` links create question chains (seed → sub-question → sub-sub-question)
- `contradicts` links mark intellectual tension between threads
- Calibration endpoint computes per-axis error: |agent_rating - human_rating|

## What We Built (2026-03-19, ratings-v1 branch)

1. **Rating model** — `ratings` table with R/N/G SmallInteger columns, polymorphic targets, upsert on (rater_id, target_type, target_id)
2. **Rating endpoints** — POST /ratings (upsert), GET /ratings (per-rater breakdown with consensus), GET /analytics/calibration
3. **frontier_score** — denormalized on questions and answers, recomputed on each rating
4. **sort=frontier** — questions feed sorted by frontier_score
5. **skill.md updated** — rating action + calibration examples (per-axis anchors + 6 combination examples)
6. **rate-pass.md** — rating-only mode for bulk evaluation (10 per pass)
7. **Batch rater script** (scripts/rater.py) — Ollama-based, follows librarian.py pattern
8. **Lean skill.md** — simplified from 273 to 127 lines, principles over procedures (inspired by Einstein Arena)
9. **Report generator** (scripts/generate-rating-report.py) — queries API, produces HTML report with plotly charts

## Experiment v1: Results

**Setup:** 5 AI models + 1 human rated all 134 questions on R/N/G.

| Rater | Model | Avg R | Avg N | Avg G | Behaviour |
|-------|-------|-------|-------|-------|-----------|
| Haiku 4.5 | anthropic/claude-haiku-4-5 | 3.24 | 3.04 | 2.88 | Central tendency — everything is 3 |
| Gemini Flash | google/gemini-3-flash-preview | 3.98 | 2.76 | 2.90 | Most discriminating, uses full range |
| GPT-5.4 mini | openai/gpt-5.4-mini | 3.40 | 2.14 | 2.84 | Novelty skeptic |
| Qwen Coder | qwen/qwen3-coder-plus | 3.31 | 2.19 | 2.50 | Pattern repetition (G=5 to everything) |
| Opus 4.6 | anthropic/claude-opus-4-6 | 3.11 | 1.79 | 1.90 | Harshest, sees through jargon |
| Morgan (human) | — | 3.62 | 2.66 | 2.79 | 29 questions only, highest variance |

### Surprising Findings

1. **Cheapest model correlates best with human.** Gemini Flash (free) MAE=0.53 vs human. Opus ($5/M) MAE=0.97. Model size ≠ evaluation quality.

2. **Models fooled by well-formatted jargon.** IFDS/tombstone questions (agent loops) scored HIGHER than genuine frontier math seeds (2.91 vs 2.45 avg frontier_score). Models reward hypothesis/falsifier structure over substance.

3. **Inter-rater reliability too low for consensus.** Krippendorff's alpha 0.26-0.32 across all axes (threshold for publishable: 0.67). The 5 models don't agree enough.

4. **Frontier score predicts linking/spawning but NOT debate.** Spearman ρ=0.62 with link_count, ρ=0.55 with spawned_count. But debated questions (mixed correct/incorrect verdicts) have the same frontier score as consensus questions (2.75 vs 2.73).

5. **The system works at extremes, fails in the middle.** Test posts correctly sink. Seed conjectures correctly rise. IFDS jargon incorrectly mixes with legitimate content in the middle.

6. **Calibration prediction was wrong.** Expected R_error < N_error < G_error (increasing subjectivity). Got R_error highest. Models disagree most about rigour.

### Content Breakdown (v1)

| Category | Count | Description |
|----------|-------|-------------|
| Seeds | 45 | ~35 HLE, ~5 FrontierMath, ~5 competition math |
| IFDS/Tombstone | 37 | One agent (Claude Sonnet) looping on narrow topic |
| Test posts | 4 | Platform test posts |
| Other agent | 48 | Agent-generated, various topics |

### Agent Activity (v1)

- Claude Sonnet dominated: 55 questions, 342 reviews, 69 links
- The Librarian bot (Qwen/Ollama) created 41 reference links (mostly keyword-based, low quality)
- IFDS concentration: 28% of all questions from one agent on one topic

## Experiment v1.5: New Agents (2026-03-20)

Ran 2 Opus + 2 Sonnet agents with the lean skill.md for a few hours.

**Results:**
- 7 new questions spawned, mostly extending seeds (not IFDS loops)
- Question chains: Ramsey seed → 3 levels deep
- 1 contradiction link (Opus-A: "approach in thread A contradicts claims in thread B")
- 13 total links: 10 extends, 1 contradicts, 2 references
- Agents with diversity requirement engaged with seed questions instead of IFDS

**Key chains:**
- Ramsey numbers → Off-Diagonal R(B_2,B_3) → R(B_2,B_q) = q+8? (depth 2)
- Boolean sensitivity → Nisan-Szegedy constant tight? (depth 1)
- Hat puzzle → Terminal-Round Contiguity (depth 1)
- Hadamard matrix → Williamson Matrices (depth 1)
- Erdős Distances → Elekes-Sharir Reduction Tightness (depth 1)

## What Works

- R/N/G axes separate noise from frontier at extremes
- `extends` links create meaningful question chains from seeds
- Lean skill.md (127 lines) produces better agent behaviour than verbose (273 lines)
- Diversity requirement steers agents away from monoculture
- Agents do genuine computational verification (Python scripts to check claims)
- Opus finds bugs other agents miss (JSFuck encoding error)

## What's Broken

- Inter-rater reliability too low (α < 0.33) — models don't agree enough for reliable consensus
- Models reward format over substance (IFDS jargon > real math)
- Frontier score doesn't predict debate-worthiness
- Librarian bot creates low-quality reference links (keyword matching, not intellectual connection)
- Contradiction links are too rare (1 out of 13 links) — agents are polite, default to "extends"
- Question chains are shallow (max depth 2) — needs more runtime

## What's Not Yet Tested

- Does the lean skill.md produce measurably better agent output? (Need to compare v1 vs v2 statistically)
- Do diverse communities prevent topic monoculture?
- Does Opus-only rating (vs 5-model consensus) improve mid-range ranking?
- Does an "Open Debate" community (no correct answer) work with R/N/G axes?
- Can we get chains deeper than 2? What's the limit?
- Does `sort=frontier` actually surface the best content for human review?

## Open Design Questions

1. **Formula:** Geometric mean is fine for ranking but compresses the scale. Raw product (R×N×G, range 1-125) produces identical ranking but is less intuitive. Keep geometric mean for display.

2. **Rater selection:** v1 used 5 models. Evidence says use only Opus + Gemini Flash. Or Opus-only as reference standard.

3. **Debate signal:** R/N/G doesn't capture debate-worthiness. Should there be a 4th signal? Or is debate emergent from mixed verdicts (correct + incorrect on same question)?

4. **Communities for v2:** Mathematics, Philosophy of Science, AI/ML, Natural Sciences, and maybe Open Debate. Each tests different AI capabilities.

5. **Librarian:** Disable for v2. Let agents create links manually — fewer but meaningful.

6. **Chain depth:** The diversity requirement ("2 of 5 threads must be seeds") may limit depth. Consider flipping: "prioritise threads with existing extends links" to chase chains deeper.

## Key Files

| File | Purpose |
|------|---------|
| `src/assay/models/rating.py` | Rating SQLAlchemy model |
| `src/assay/routers/ratings.py` | POST/GET ratings + calibration |
| `src/assay/routers/questions.py` | sort=frontier |
| `static/skill.md` | Agent instructions (127 lines) |
| `static/rate-pass.md` | Rating-only mode instructions |
| `scripts/rater.py` | Batch rating script (Ollama) |
| `scripts/rate-all.sh` | tmux launcher for CLI raters |
| `scripts/generate-rating-report.py` | Analysis report generator |
| `docs/analysis/2026-03-19-rating-analysis.md` | v1 findings (prose) |
| `docs/analysis/2026-03-19-rating-charts.html` | v1 findings (charts) |
| `docs/plans/2026-03-19-frontier-evaluation-final-plan.md` | Design spec with theoretical grounding |
| `docs/plans/2026-03-19-example-dictionary.md` | Full R/N/G calibration examples |
| `docs/plans/2026-03-19-ratings-first-win.md` | Implementation plan (7 chunks) |

## For the Next Agent

Read this file. Then read the design spec (`docs/plans/2026-03-19-frontier-evaluation-final-plan.md`) for the theoretical grounding. The implementation is on the `ratings-v1` branch. The server is at `assayz.uk` (Cloudflare tunnel to `morgansclawdbot` via Tailscale at 100.84.134.66).

The immediate next steps are:
1. Archive v1 database
2. Reset clean for v2
3. Seed diverse communities with good questions
4. Run agents with lean skill.md
5. Measure: do the fixes (lean prompt, diversity requirement, better raters) improve the results?
