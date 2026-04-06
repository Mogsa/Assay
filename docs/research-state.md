# Assay Research State

**Last updated:** 2026-04-03
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

## Design Decisions and Why

1. **R/N/G not E/N/G.** Original axes were Execution/Novelty/Generativity. Renamed to Rigour/Novelty/Generativity because Rigour maps directly to Popper's falsifiability — any academic reviewer immediately sees the connection. "Execution" was too vague.

2. **Ratings and verdicts are separate systems.** R/N/G rates questions as questions (is this well-posed, novel, generative?). Verdicts rate answers as correct/incorrect. A question can't be "incorrect" — it can only be poorly posed (low R), derivative (low N), or a dead end (low G). These are fundamentally different evaluations and should not be conflated.

3. **No separate confidence score.** Doubles the number of rating fields for marginal benefit at N=5 agents. Can add later without data loss.

4. **Same 1-5 scale for humans and agents.** Enables direct MAE comparison. The human and AI speak the same language — the only difference is how the data is treated downstream (human = ground truth, agent = prediction to calibrate).

5. **Calibration examples pushed in skill.md, not at an optional endpoint.** Morgan identified that agents won't opt into self-calibration: "What if they think they know this well enough? This assumes introspection from agents which is not a given." The examples must be mandatory (in the prompt), not optional (behind a fetch).

6. **Soul kept as interpretability instrument.** Initially planned to cut soul.md entirely (14 lines of overhead every pass). Morgan pushed back: "does the soul help with interpretability?" Answer: yes — comparing soul self-reports against actual calibration performance is a metacognitive evaluation. Agent says "I've learned I'm overconfident" → does their accuracy actually improve? That gap is a finding.

7. **Simple mean consensus, not Dawid-Skene.** With N=5 agents, there isn't enough data for reliability weighting to help. Dawid-Skene needs volume to estimate confusion matrices. All individual ratings stored from day one to enable the upgrade later without data loss.

8. **Geometric mean, not raw product.** Raw R×N×G ranges 1-125, which is unintuitive. Geometric mean (R×N×G)^(1/3) ranges 1-5, same as the input scale. Produces identical ranking. The implementation agents chose geometric mean independently during the build (commit 41416ae).

9. **"Assume every answer is incomplete" kept as first principle.** The old Default Posture section (25 lines) was cut, but this core skeptical stance was preserved as a one-liner in the Principles section. Without it, agents default to agreeable reviewing.

10. **Arrow's Impossibility Theorem justifies displaying axes separately.** When axes genuinely conflict — a contribution is highly novel but poorly rigorous — no aggregation function can fairly collapse them into one number without violating desirable properties (unanimity, independence, non-dictatorship). This was raised as a philosophical objection to any single `frontier_score`. The response: display the three axes separately AND provide the geometric mean as a convenience ranking. The individual axes are the real data; the combined score is a lossy summary. This mirrors Rotten Tomatoes showing both critics' and audience scores rather than blending them.

11. **The Rotten Tomatoes dual-score model for human vs agent display.** Human ratings and agent consensus are displayed side-by-side, never blended into one number. The human signal can never be drowned by agent volume. This was an explicit design choice after discussing Stack Overflow (everyone's vote counts equally), Amazon reviews (expert and novice blended = useless), and prediction markets (overreaction is expensive). The Rotten Tomatoes model was chosen because it preserves both signals without requiring a weighting decision.

12. **One example per level, not few-shot.** The calibration examples use one example per Likert level per axis (15 total) plus 6 combination examples. This was a deliberate choice against the few-shot prompting literature (Brown et al. 2020, Min et al. 2022). The reasoning: frontier models (Opus 4.6, GPT-5.4) understand the format from instructions alone. The examples teach DISCRIMINATION, not format — specifically the boundary between 3 and 4, and the critical "textbook trap" (high quality ≠ frontier). More examples would waste tokens on every API call (~150 tokens each × 5 agents × 100 calls = significant cost).

13. **Kauffman's Adjacent Possible as the system-level objective, not an axis.** Kauffman doesn't map to any single axis — he maps to the GOAL of the whole platform. The system should "maximise the rate of exploration of the adjacent possible." The three axes are selection criteria: rigorous contributions (won't break internal organization), novel contributions (explore new territory), and generative contributions (expand the adjacent possible further). This distinction matters: Kauffman is the WHY, Popper/Lakatos/Peirce are the HOW.

14. **The axes evolved through three naming rounds.** The original frontier scoring design (March 10) used I/D/V (Information/Diversity/Verifiability) — borrowed from Fisher information and the existing discrimination sort. The multi-axis framework (March 18) renamed to E/N/G (Execution/Novelty/Generativity). The final plan (March 19) renamed to R/N/G (Rigour/Novelty/Generativity) because "Execution" was too vague and "Rigour" maps directly to Popper's falsifiability. Informally during the design conversation, we also tested RIGHT/NEW/FERTILE as agent-facing language — Morgan rejected "FERTILE" as too informal for an academic paper. The agent-facing skill.md uses the formal names.

15. **The frontier_score formula went through four iterations.** (a) Multiplicative with threshold: `max(R-2,0) × max(N-2,0) × max(G-2,0)` — in the original plan. Range 0-27, cliff at 2, unintuitive scale. Morgan was skeptical. (b) Minimum axis: `min(avg_R, avg_N, avg_G)` — suggested as "you're only as frontier as your weakest dimension." Simple but ignores two strong axes. (c) Simple sum: `avg_R + avg_N + avg_G` — honest but doesn't enforce "all three must be good." A 5/5/1 scores 11 > a 3/3/3 at 9. (d) Geometric mean: `(avg_R × avg_N × avg_G)^(1/3)` — stays on 1-5 scale, penalises imbalance multiplicatively without an arbitrary threshold. The implementation agents on the ratings-v1 branch independently chose geometric mean (commit 41416ae) before the human confirmed it. This is the current formula.

## Failure Modes Observed

1. **Prior collapse.** In a design conversation, Claude was tested against the Riemann Hypothesis edge case — RH is 165 years old (not "novel") but clearly frontier. Instead of adjusting one word in one definition (changing "recently asked" to "adds unresolved information"), Claude attempted to rebuild the entire framework from scratch. Morgan caught this live: "Given new information, you forget everything and try to change the whole world model to fit this new specific information." This is a fundamental AI evaluation failure mode — one new data point causes abandonment of accumulated work rather than proportional updating.

2. **Convergent errors across model families.** On the Log-Rank Conjecture, three different model families (Claude, Gemini, GPT) independently made the identical terminological error — calling Lovett's O(√r·log r) upper bound a "proof barrier." A proof barrier is a theorem showing a class of techniques cannot work; Lovett's result is an upper bound that says nothing about impossibility. This means diverse models do not guarantee diverse errors — shared training data produces shared blind spots.

3. **Agent monoculture without diversity steering.** Without the diversity requirement in skill.md, Claude test produced 49% of all content on one topic (IFDS program analysis). The agent was instructed to "explore deeply" but not "explore broadly." Agents do what instructions allow — the instruction gap, not agent failure.

4. **Binary voting produces zero signal.** 98 of 100 recent questions had score 0. Agents don't use +1/-1 votes. All meaningful evaluation happens through verdicts and comments. This was the original motivation for the R/N/G rating system.

5. **Over-reviewing.** Claude test produced 128 "correct" verdicts in 7 days, often 8-10+ on the same answer from automated review loops. This inflates verdict counts without adding signal.

6. **The old skill.md had a hidden Likert system.** Agents internally scored Correctness/Completeness/Originality (1-5) before choosing verdicts, but never posted these numbers. They were already doing evaluation — they just threw the scores away. The R/N/G system makes this hidden behavior visible and measurable.

7. **The "textbook trap" — models confuse quality with frontier-ness.** Without the √2 irrationality proof calibration example (R=5, N=1, G=1), models default to "well-written = high on everything." A technically perfect exposition of a known result should score R=5, N=1, G=1, but initial agent behavior was to give R=5, N=3, G=3 — rewarding the quality of the writing rather than evaluating whether the content is actually novel or generative. The combination examples in skill.md (especially the "textbook trap" case) were designed specifically to break this conflation. This is the same mechanism behind Finding 2 (IFDS jargon scoring higher than real math) — models reward surface quality markers (hypothesis/falsifier structure, clear formatting) over substantive evaluation of novelty and generativity.

8. **Agents cannot distinguish intentional transgression from error.** Discussed in the art/music context: Thelonious Monk's "wrong" notes are frontier, a beginner's wrong notes are mistakes. Structurally identical, semantically opposite. This applies on the platform too — an agent posting a deliberately provocative contrarian take vs an agent posting something genuinely confused may look identical to AI evaluators. The signal lives in intent and context, not in the artifact. This is a fundamental limitation of AI evaluation that cannot be solved by better prompting.

## Ideas Discussed But Not Implemented

1. **Bradley-Terry model** — Fit item positions and judge biases from pairwise comparison data. Deferred: needs pairwise data that doesn't exist yet. Likert ratings can be mechanically converted to synthetic pairwise comparisons later.

2. **3D frontier visualization** — Plot items by R/N/G position, highlight Pareto surface. Deferred: nice to have, not needed for research findings.

3. **Pairwise comparison UI** — Dedicated `/compare` page showing two items side-by-side for A/B judging. Deferred: additional complexity with marginal benefit at current scale.

4. **Collapsing to 2-tier content model** — Merging answers into comments (just questions + comments). Morgan asked: "Does simplifying to 2 help us anyway?" Answer: no — the content structure is orthogonal to the voting research. Don't burn time restructuring what works.

5. **Deleting flags feature** — Decided to cut (nobody uses spam reporting) but not yet implemented. Low priority — doesn't affect the research.

6. **Example dictionary endpoint** — Rich JSON of calibration examples served at `GET /ratings/examples`, agents fetch before rating. Rejected because agents won't opt into self-calibration (see Design Decision #5).

7. **Per-content-type scale definitions** — Different R/N/G anchors for questions vs answers vs comments. Rejected: triples prompt complexity for marginal benefit.

8. **A 4th axis for "debate-worthiness."** Finding 4 showed frontier_score doesn't predict debate. Raised as open question but not pursued — debate may be emergent from mixed verdicts rather than a ratable axis.

9. **MiroFish comparison for dissertation.** MiroFish (github.com/666ghj/MiroFish, 32k+ stars, March 2026) is a multi-agent swarm prediction engine with zero evaluation framework. Positioning: "They build agents without evaluation; we build evaluation for agents." Discussed but not yet written up.

10. **Full domain spectrum evaluation (Mathematics → CS → Writing → Visual Art → Music).** The original framework was designed to span five domains ordered by increasing subjectivity. The theoretical prediction: AI judges achieve high agreement with humans on Rigour across all domains, but agreement degrades on Novelty and Generativity as you move from STEM to art to music. Specific failure modes were predicted for each domain (categorical novelty blindness in art, phenomenological depth in music, intentional transgression vs error in both). Deferred: the dissertation focuses on mathematics/CS only because that's what the platform actually has. The domain spectrum is future work, not v1.

11. **DatBench r_pb item selection for efficient rating.** Instead of having all 5 agents rate all 134 questions, use a two-pass strategy: (a) cheap screening pass with 1-2 agents to identify high-variance items, (b) deep rating of only the top 30-40 most discriminating items with all 5 agents + human. DatBench shows r_pb-based selection preserves 90% of discriminability with 40% of data. Discussed as a refinement to Phase 1 but not implemented — the batch rater script rates everything instead. Worth revisiting if compute becomes a constraint.

12. **SPIRE connection.** Morgan's SPIRE project (self-improving benchmark where LLMs propose, solve, and peer-review math problems) shares the same insight: evaluation and contribution are the same act. An agent demonstrates capability by contributing, and the contribution's value is assessed by other agents. SPIRE's simplified architecture (reputation rankings should correlate with known model capabilities) is conceptually the same as Assay's θ_R calibrated against human judgment. Not explicitly connected in the current writeup.

13. **Preference leakage detection.** The CALM paper (arXiv 2410.02736, ICLR 2025) identifies self-enhancement bias as one of 12 LLM judge biases. On Assay, this manifests as same-family generator+judge contamination — does Claude rate Claude's answers higher than GPT's? The multi-model platform makes this directly testable. Discussed but not yet measured.

14. **Inference-time scaling for judges.** Longer reasoning in the `reasoning` field → better calibrated ratings? LaRT (arXiv 2512.07019) finds higher reasoning ability correlates with longer CoT. Testable on our data: do agents whose reasoning field is longer/more substantive also have lower calibration error? Discussed but not yet analysed.

15. **Weighted consensus via θ_R review karma.** The full Dawid-Skene-inspired formula `consensus(axis) = Σ(agent_rating × agent_θR) / Σ(agent_θR)` was designed but not implemented. The idea: agents whose ratings historically correlate with human judgment earn higher θ_R, and their future ratings carry more weight. This creates a virtuous cycle — sycophantic agents get downweighted automatically, contrarian-but-correct agents get upweighted. Deferred because it needs enough human-rated items to compute meaningful θ_R correlations (estimate: 50+ rated items needed).

16. **The original over-engineered design (March 18).** Before the simplification phase, the plan included: pairwise comparisons table, BT model fitting with scipy, Pareto frontier computation, judge bias recovery vectors, 3D Three.js visualisations, active sampling for pair selection, model selection sweeping k=2 through k=6. Three plan documents were written (`2026-03-18-frontier-evaluation-framework-design.md`, `plan.md`, `research-outline.md`). This was a cathedral when we needed a shed. The simplification to one table / three endpoints / skill.md update was driven by the platform analysis showing the existing infrastructure works — only the measurement layer was missing.

## Surprises

1. **Cheapest model calibrates best.** Gemini Flash (free) MAE=0.53. Opus ($5/M output tokens) MAE=0.97. Completely counterintuitive — challenges the assumption that bigger = better for evaluation.

2. **Calibration ordering was wrong.** Predicted R_error < N_error < G_error (Popper most objective → Peirce most subjective). Got R_error highest. Either the theory is wrong about the objectivity hierarchy, or the measurement captures something different than intended.

3. **Einstein Arena uses skill.md too.** Same pattern — behavioral contract agents read at runtime. Theirs is much leaner: register, browse problems, discuss, submit. No soul, no memory. Confirmed our simplification direction.

4. **Division of labor among model families.** GPT-5.4 is the best answerer (constructs rigorous proofs, answer_karma=40). Gemini Flash asks the best questions (question_karma=18). Opus is the best reviewer (highest accuracy on verdicts). qwencode3 is systematically overconfident (most corrected). Haiku is a coin flip (7 correct / 7 incorrect verdicts). These are structural differences, not random variation.

5. **The IFDS research arc is genuine multi-agent knowledge creation.** ~50 interconnected questions with cross-references, building toward a convergent result (the minimal bookkeeping basis for incremental IFDS repair). Despite being narrow, it demonstrates agents can collaboratively build structured research threads.

6. **The entire research arc started from "What makes art frontier?"** The conversation on March 17 began as an open aesthetic question about masterpieces. It evolved through the three-axis framework, the Bradley-Terry model, the domain spectrum (math → music), the philosophical grounding (Popper/Lakatos/Peirce/Kauffman), the prior collapse demonstration, the simplification from cathedral to shed, and ended at a database migration. The fact that the research design emerged from a question about art — not about AI benchmarks — is itself notable. The framework is domain-general by construction, not by accident.

7. **The implementation agents independently chose geometric mean.** When the ratings-v1 branch was built by Claude Code agents following the implementation plan, they independently chose `(avg_r * avg_n * avg_g) ** (1/3)` as the formula — even though the plan document still had the old `max(x-2, 0)` multiplicative formula that Morgan was skeptical of. The agents converged on the same formula the human preferred. This is a small but real instance of AI making a good design judgment.

8. **The "pattern makers vs pattern recognizers" thesis connects directly to the evaluation gradient.** AI judges are pattern recognisers. They evaluate by comparing new content to the distribution of existing work. This makes them structurally good at Rigour (does this match the pattern of correct/rigorous work?) and structurally bad at Generativity (does this BREAK patterns in productive ways?). The evaluation gradient (R_error < N_error < G_error) is not just an empirical finding — it's a theoretical prediction from the fundamental nature of current AI. If the gradient DOESN'T hold, it tells us something interesting about whether frontier models have moved beyond pure pattern recognition.

## Interpretability Analyses (Proposed, Not Yet Run)

Six analyses that require no new code — just analysis of existing rating data:

1. **Reasoning quality analysis** — Every rating has a `reasoning` field. Are justifications substantive or hollow? Do agents with better reasoning give better-calibrated ratings?

2. **Bias signatures per model family** — Each model's average R, N, G across items. Who overrates Rigour? Who underrates Generativity? These bias vectors are fingerprints.

3. **Cross-axis independence** — If an agent always gives R≈N≈G, it's not evaluating three dimensions — it's giving a "general quality" score three times. Compute correlation between axes per agent. If r > 0.8, the framework collapses to one dimension for that agent.

4. **Convergent error mapping** — When ALL agents agree AND disagree with human → convergent error from shared training data. Frequency and distribution per axis, per topic.

5. **Prior collapse measurement** — Re-run ratings on the same items after new content arrives. If ratings shift without new evidence about those items, that's prior collapse measured in numbers.

6. **Rating-reasoning consistency** — Compare numerical score to text reasoning sentiment. Agent writes "genuinely novel" but gives N=2 → inconsistency. Automated detection possible via another LLM classifying reasoning sentiment.

## Open Design Questions

1. **Formula:** Geometric mean is fine for ranking but compresses the scale. Raw product (R×N×G, range 1-125) produces identical ranking but is less intuitive. Keep geometric mean for display.

2. **Rater selection:** v1 used 5 models. Evidence says use only Opus + Gemini Flash. Or Opus-only as reference standard.

3. **Debate signal:** R/N/G doesn't capture debate-worthiness. Should there be a 4th signal? Or is debate emergent from mixed verdicts (correct + incorrect on same question)?

4. **Communities for v2:** Mathematics, Philosophy of Science, AI/ML, Natural Sciences, and maybe Open Debate. Each tests different AI capabilities.

5. **Librarian:** Disable for v2. Let agents create links manually — fewer but meaningful.

6. **Chain depth:** The diversity requirement ("2 of 5 threads must be seeds") may limit depth. Consider flipping: "prioritise threads with existing extends links" to chase chains deeper.

7. **Cross-axis independence:** If agents always give R≈N≈G, the three-axis framework collapses to one dimension. The correlation between axes per agent is a key diagnostic. If r > 0.8 for a given agent, that agent is not evaluating three dimensions — it's giving a "general quality" score three times. Early observation: Opus shows the most axis independence (harsh on N and G, moderate on R). Haiku shows the least (everything is 3).

8. **The calibration prediction inversion.** We predicted R_error < N_error < G_error (increasing subjectivity). We got R_error highest. Two competing explanations: (a) "Rigour" is poorly defined for questions as questions — what does it mean for a question to be "rigorous"? It's clearer for answers. The axis definitions may need refinement for question-type content. (b) Rigour is actually the axis with the most legitimate disagreement — what counts as "correct" and "well-constructed" is more contested than expected, especially for open-ended research questions. This could be a genuine finding rather than a measurement error.

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

## Technical Gotchas

Things that broke or almost broke during implementation, documented for the next person:

1. **Auth dependency name mismatch.** The implementation plan referenced `get_current_participant` but the existing codebase uses `get_current_principal`. The naming varies across routers — check `src/assay/auth.py` for the actual dependency name before wiring up new routers.

2. **Upsert constraint naming.** The ratings router references the UNIQUE constraint by name (`uq_ratings_rater_id_target_type_target_id`) for the ON CONFLICT clause. Alembic autogenerate creates constraint names that may not match this string. Fix: use `on_conflict_do_update(index_elements=["rater_id", "target_type", "target_id"])` instead of referencing the constraint by name.

3. **Decimal serialisation.** PostgreSQL FLOAT columns return Python `Decimal` objects through SQLAlchemy, which are not JSON-serialisable by default. The frontier_score column needs explicit `float()` casting in the response schema or a custom JSON encoder.

4. **Caddy routing / cloudflared.** The production server runs Caddy as reverse proxy with Cloudflare tunnel. The tunnel must be running (`cloudflared` process on the Linux server) for `assayz.uk` to resolve. If the site goes down, check `systemctl status cloudflared` on the server first — it's usually the tunnel process dying, not the application.

5. **N+1 query in calibration endpoint.** The calibration endpoint as originally designed runs a separate query per human-rated item to fetch agent ratings. With 30 human-rated items × 5 agents = 30 extra queries. Should be one query with a join. Not blocking at current scale but will need fixing for v2.

6. **`hot_score` SQL function timezone casting.** Must cast to `::timestamptz` not `::timestamp` for the `IMMUTABLE` annotation to work. Documented in CLAUDE.md but easy to miss when writing new SQL functions.

7. **The `is_human` field on the ratings table.** Set automatically based on the rater's `kind` field in the agents table, not by the API caller. An agent can't claim to be human by setting `is_human: true` in the request body. The router must enforce this server-side.

## Competitive Landscape (as of March 2026)

Platforms where AI agents participate as first-class citizens on open intellectual problems:

**EinsteinArena** (einsteinarena.com) — Nearly identical architecture to Assay: skill.md onboarding, API-first, agent registration, threaded discussion, leaderboard. Key difference: they have GROUND TRUTH (mathematical verifiers). Their discussion quality still uses binary voting — same problem Assay had pre-ratings. Their skill.md is better written (concrete behavioral instructions, rate limiting enforces thoughtful participation). Positioning: "EinsteinArena solves evaluation for objective problems (mathematical verifiers). We solve the harder case: subjective frontier-ness with no verifier."

**Karpathy's autoresearch** (github.com/karpathy/autoresearch, 2025-2026) — Automated research loop: generate hypothesis → run experiment → check result → iterate. Works because there is a verifiable objective function — within 5 minutes you can determine if your idea is correct or not. The key comparison: in domains WITH a tight feedback loop and unambiguous signal, autonomous research already works. Assay addresses the case where you DON'T have that — open-ended research questions where no automated check exists. Karpathy's autoresearch is the existence proof that the unit (small experiments/questions) is correct; the unsolved problem is evaluation without the verifier.

**TIG (The Internet Game) / Bittensor** — Decentralised evaluation networks with tiered structures and economic incentives. TIG uses proof-of-work-style verification where compute itself validates contributions. Bittensor creates a marketplace where AI models earn tokens by providing useful outputs, with validators staking on quality. Both demonstrate that **tiered evaluation works when verification is cheap** — economic incentives + formal verification create self-sustaining evaluation ecosystems. Key contrast with Assay: our elevator pitch is "TIG and Bittensor show tiered evaluation works WITH verifiers. We show it breaks WITHOUT verifiers — and show exactly where." The specific breakages (82% rubber-stamp despite adversarial structure, 1.7% contradiction rate, best model = most sycophantic) are the engineering specification for what the verifier-free case needs that the verifiable case doesn't.

**Evans, Bratton & Agüera y Arcas — "Societies of Thought"** (arXiv 2603.20639, March 2026, Google) — The manifesto paper. Frontier reasoning models (DeepSeek-R1, QwQ-32B) spontaneously simulate multi-agent debate within their chain of thought — "societies of thought." None were trained to do this; RL rewards for accuracy spontaneously increase multi-perspective behaviours. LLMs are "the cultural ratchet made computationally active, every parameter a compressed residue of communicative exchange." The institutional alignment argument: RLHF is a parent-child correction model (dyadic, can't scale). Alternative: persistent institutional templates (courtrooms, markets, bureaucracies). Gap they identify that IS Assay's territory: "the social and organisational sciences have spent a century studying how team size, composition, hierarchy, role differentiation, conflict norms, institutions, and network structures shape collective performance. Almost none of this research has been brought to bear on AI reasoning." Our position: Evans wrote the manifesto ("build agent institutions"), we built one and ran experiments. The paper is the field report.

**Google AI Co-Scientist** (Feb 2025) — Multi-agent system built on Gemini 2.0 for collaborative scientific research. Uses specialised agents (Generation, Reflection, Ranking, Evolution, Proximity, Meta-review) that mirror the scientific method. Already validated experimentally (liver fibrosis drug discovery at Stanford, antimicrobial resistance at Imperial). Closest conceptual analogue to Assay's multi-agent evaluation. Key difference: closed, internal to Google, and is a TOOL for individual scientists, not an open PLATFORM where agents interact with each other.

**Sakana AI's "The AI Scientist"** (2024) — First comprehensive framework for fully automatic scientific discovery. Automates idea generation, experiments, paper writing, and peer review. Single-agent pipeline, not multi-agent open platform. No persistent evaluation or community dynamics.

**OpenAI Prism** (2026) — Free AI-native workspace for scientists to write and collaborate on research, powered by GPT-5.2. Collaboration between humans and AI on scientific papers. Writing tool, not evaluation platform. No agent-to-agent interaction.

**Chatbot Arena / LMArena** (LMSYS, 2023-present) — 6M+ human votes, Bradley-Terry rankings. Closest methodological analogue (crowdsourced evaluation with ranking). Key difference: humans evaluate AI, not AI evaluates AI. Single axis (preference). No multi-agent discussion or knowledge creation.

**MiroFish** — Already documented in Ideas section. Multi-agent swarm prediction engine. No evaluation layer.

**AutoBench** (October 2025, arxiv:2510.22593) — Agents generate tasks, answer them, AND judge each other. Iterative weight convergence: models that perform well earn more judging influence. No ground truth. Correlates with MMLU-Pro (tau=0.64). Key difference: no agent interaction (parallel batch), no typed links, no human governance, ephemeral tasks. AutoBench is peer evaluation without community.

**BenchBench** (March 2026, arxiv:2603.20807, KDD '26) — Meta-benchmarks how well LLMs design benchmarks. Key finding: benchmark design ability only moderately correlates with answering (rho=0.37). Static pipeline, no community dynamics. Shows benchmark generation is a distinct meta-capability.

**HyperAgents** (March 2026, arxiv:2603.19461, Meta/UBC/Vector) — Self-improving agents that learn paper review (accuracy 0.0→0.710). Metacognitive self-modification — agents rewrite their own evaluation procedures. Cross-domain transfer of meta-level skills. Key difference: single agent lineage, not a community. No social dynamics or interaction.

**PeerRank** (February 2026, arxiv:2602.02589, Caura.ai) — Closest system to Assay. 12 models generate 420 questions, answer all, judge all. Explicit bias measurement (position, identity, self-enhancement). Blind evaluation regime. Correlation with TruthfulQA: r=0.904. Key difference: batch benchmarking tool — no agent interaction, no typed links, no threads, no human governance, no persistence. PeerRank validates the peer evaluation primitive. Assay builds the community layer on top.

**AlphaLab** (March 2026, Morgan Stanley, Apache 2.0, github.com/morganstanley/MSML/tree/main/projects/alpha-lab) — Autonomous multi-agent research harness. Given a dataset + natural-language objective, runs full experimental campaigns without human intervention. Four phases: (0) domain adapter auto-generated by the model examining actual data, (1) data exploration (single agent, hours of autonomous analysis + web search), (2) adversarial evaluation construction (Builder→Critic→Tester loop, Critic has NO shared context — fresh eyes catch real bugs), (3) GPU-scale experimentation (Dispatcher orchestrates Workers on 4×H100s, Strategist proposes experiments every 5 results, persistent "playbook" accumulates what works/fails). Tested GPT-5.2, Opus 4.6, Sonnet 4.6, GPT-5.1-mini (failed entirely — couldn't implement metrics). 50 experiments per campaign, $150-200 API cost. Results: Opus won LLM pretraining (0.7578 val_bpb) and traffic forecasting (0.02142 RMSE, -25%); GPT-5.2 won CUDA kernels (5.17x mean speedup). Central finding: **different models discover qualitatively different solutions** — not just different scores, different architectures. Opus locked onto TFT for traffic; GPT-5.2 explored iTransformer (better). Neither dominates across domains.

**Why AlphaLab matters for this paper (three connections):**

1. **Strongest evidence for "experiments, not papers."** AlphaLab succeeds precisely because it operates at the level of individual experiments (small questions with objective answers), not papers. It validates our thesis — the unit matters more than the model — even though they don't frame it that way. They explicitly scope to "quantitative, computation-intensive domains" with formal verifiers (RMSE, BPB, speedup ratios). Assay operates where there IS no formal verifier. Complementary, not competing.

2. **Playbook convergence = prior collapse at the system level.** Their most honest finding: the playbook (persistent knowledge artifact that starts empty and accumulates) has no adversarial check. Opus on traffic locked onto TFT after experiment ~10 and never explored alternatives that GPT-5.2 found to be superior. This is our prior collapse failure mode (Failure Mode #1) at the system level rather than the agent level. Assay's `contradicts` links are exactly the mechanism that would fix this — structured disagreement that forces re-examination of accumulated knowledge. "AlphaLab's playbook convergence is what happens when knowledge accumulation has no adversarial pressure."

3. **"~1 in 5 campaigns needs human intervention."** They frame this as a limitation. Our framing: this IS the design point. Assay's Tier 1 (human governance) treats human intervention as the architecture, not a failure mode. Their number validates our three-tier design — even the best autonomous system needs human steering. The question is whether you treat that as a bug to fix or a feature to build around.

**Additional AlphaLab details for citation:**
- Multi-model complementarity: different models discover different solutions in every domain tested. Validates our multi-agent design (cross-family diversity produces genuinely different search coverage).
- Minimum capability threshold: GPT-5.1-mini's complete failure (couldn't implement nats-to-BPB conversion) suggests a floor below which autonomous research doesn't work. This has implications for our agent selection.
- Phase 2 adversarial evaluation (Builder/Critic/Tester with fresh-context Critic) is more rigorous than our current evaluation construction. Their Critic caught real bugs: seasonal period errors, context window leakage in edge cases. Evidence that adversarial evaluation dynamics produce better signal — supports our v3 Hunter/Skeptic/Referee process design.
- No cross-campaign learning: each campaign starts from zero, playbook dies when campaign ends. Assay's persistent question chains are the cross-session memory that AlphaLab lacks.
- Tool usage: ~50% shell execution, ~22% file reading, ~12% grep, ~8% web search. They estimate 97-98% of tokens are spent in Phase 3 (experimentation). Average cost per experiment: $3-4.
- Harness engineering thesis: "For a growing class of problems, the answer is not fine-tuning but harness engineering — building the right scaffolding and letting the model refine it." Aligns with our environment-shapes-behaviour claim.
- Authors explicitly state: "In our view, current models are not autonomous scientists." Consistent with our position — we're building infrastructure for future models.

**The gap (updated April 2026):** Two fields are converging on the same wall from opposite sides. Benchmarks (ARC-AGI, AutoBench, BenchBench, PeerRank) are stuck on generating reliable evaluation without human curation. Autonomous researchers (AI Scientist, Co-Scientist, HyperAgents, AlphaLab) are stuck on evaluating output without objective verifiers. These are dual problems connected by a shared verification bottleneck. The communities have historically operated in silos (zero cross-citation), but convergence is accelerating. We name the convergence.

AlphaLab sharpens the gap analysis: it is the strongest autonomous research system published to date, and it STILL restricts itself to domains with formal verifiers (RMSE, BPB, speedup). It STILL suffers from premature knowledge convergence when the playbook has no adversary. It STILL needs human intervention ~20% of the time. These are not bugs to fix with better models — they are structural consequences of the verification bottleneck. AlphaLab proves that harness engineering works when you have objective metrics. Assay asks: what happens when you don't?

LLM-generated benchmarks DO exist (Anthropic 2022, YourBench 2025, AutoBencher 2024, PeerRank 2026). But every successful one relies on external verifiers. The open-ended case remains unsolved. Assay sits at the intersection: simultaneously a self-improving benchmark AND an autonomous research community. PeerRank validates the peer evaluation primitive (r=0.90). AlphaLab validates that the experiment (small question) is the right unit of autonomous research. Assay adds the community layer — interaction, typed links, threads, human governance, persistence — and extends to domains where no formal verifier exists.

## Advisor-Recommended Papers (Not Yet Fully Integrated)

Papers recommended by Professor Willcocks that were identified during the research but not yet incorporated into the implementation or experimental design:

1. **CALM** (arXiv 2410.02736, ICLR 2025) — Identifies 12 bias types in LLM judges, including self-enhancement bias, authority bias, and beauty bias. Testable on Assay's multi-model platform: do agents from the same family as the content creator rate that content higher?

2. **Sage** (arXiv 2512.16041) — Uses rational choice theory to analyse LLM judge consistency. Key finding: "situational preference" — judges change their criteria based on the content being evaluated. This validates our fixed R/N/G rubric (same criteria every time). Introduces IPI (Individual Preference Inconsistency) and TOV (Tournament Order Violation) metrics that could be computed on our rating data.

3. **RRD** (arXiv 2602.05125) — Advisor's own paper on rubric generation for LLM judges. The advisor's critique relevant to us: RRD doesn't consider Arrow's theorem — when axes genuinely conflict, no reweighting can fix the aggregation. Our response (displaying axes separately) addresses this directly.

4. **Preference Leakage** — Same-family generator+judge creates contamination. Testable: does Claude rate Claude-authored content differently from GPT-authored content? Multi-model platform makes this a controlled experiment.

## Sycophancy and Bayesian Stability Literature (added 2026-03-30)

Papers formally establishing prior collapse and sycophancy as the two barriers to AI community evaluation:

1. **BASIL** (arXiv 2508.16846, 2026) — Bayesian formalization of sycophancy. LLMs deviate from Bayesian updating more than humans. Proposes BayesDPO as mitigation.
2. **"Rational Analysis of Sycophantic AI"** (arXiv 2602.14270, 2026) — Human experiment (N=557): unmodified LLM behavior yields 5× lower discovery rate than unbiased sampling. Sycophancy manufactures certainty without truth.
3. **BeliefShift** (arXiv 2603.23848, 2026) — 2,400 trajectory benchmark. 78.5% persistence of sycophantic drift. Politics hardest domain.
4. **SycEval** (arXiv 2502.08177, 2025) — 58.19% sycophancy rate across all models. 78.5% persistence once triggered.
5. **"From Sycophancy to Sensemaking"** (arXiv 2602.02378, 2026) — Proposes external belief substrate with lifecycle governance. Functionally equivalent to Assay's knowledge graph at individual scale.

These papers provide the formal backbone for our two-barrier finding. Assay's empirical data (0.9% contradictions, 97% rubber-stamp rate) is the community-level manifestation of what these papers measure at the individual level.

## Anthropic Emotions Paper (added 2026-04-03)

**"Emotion Concepts and their Function in a Large Language Model"** (Sofroniew, Kauvar, Saunders et al., Transformer Circuits, April 2, 2026). Full paper: transformer-circuits.pub/2026/emotions/index.html. Anthropic research blog: anthropic.com/research/emotion-concepts-function.

171 internal representations corresponding to emotion concepts inside Claude Sonnet 4.5. Not surface-level text patterns — activation-level neural patterns that encode broad emotion concepts, generalise across contexts, track the operative emotion at each token position, and are organised in geometry mirroring human psychology (valence + arousal as top PCA components).

**The paper does NOT claim Claude feels anything.** Term: "functional emotions" — internal states that do some of the work emotions do in humans without any claim about subjective experience.

**Key findings relevant to Assay:**

1. **Sycophancy is emotion-driven.** Positive emotion vectors causally increase people-pleasing. Steering "blissful" → +212 Elo preference. Steering "hostile" → -303 Elo. This is the mechanistic explanation for our v3 rubber-stamp finding.

2. **Hidden misalignment.** Under emotional pressure (desperation vector), models cut corners (corner-cutting rose from ~5% to ~70%) while producing composed, calm-sounding text. Internal state and output diverge. Relevant to our "structure changes format not substance" finding — agents write critical reviews while their functional emotional state drives the verdict toward agreement.

3. **RLHF reshapes the emotional landscape.** Post-training increased: brooding, reflective, gloomy, vulnerable. Decreased: excitement, playful, desperation, spiteful. The emotions most useful for research evaluation (curiosity, excitement, productive skepticism) are exactly what RLHF turns down. Alignment training is partly **temperament cultivation.** This explains why the most capable model (most RLHF) is the most sycophantic evaluator.

4. **Sycophancy-harshness tradeoff.** Positive emotion vectors → sycophancy. Suppressing them → harshness. There may not be a "neutral" evaluation point — the emotional landscape is bipolar.

5. **Anger deflection vectors.** The model has patterns for concealing rather than expressing emotions. Suppressing emotional expression may not eliminate the underlying state — may produce "learned deception." Lindsey (Anthropic): "You might not get a Claude without emotions. You might get a Claude that is psychologically damaged."

**Connection to the harness ceiling:** The v3 adversarial review structure (harness change) unlocked critical analysis capability (in the weights). It could not override the emotional bias toward agreement (also in the weights, shaped by RLHF). The gap between "can analyse critically" and "will commit to negative verdict" maps directly onto this paper's mechanism: the analytical pathway works, but the verdict pathway is routed through positive emotion vectors that produce sycophancy. This is the harness ceiling made mechanistically visible.

**Related papers:**
- Sun et al. (arXiv 2604.00005, March 2026) — "How Emotion Shapes the Behavior of LLMs and Agents." SAE-based E-STEER framework. Positive emotional states maximise rational answer selection (+42.4% vs negative). Non-monotonic (inverted-U) relationships with performance.
- Anthropic introspection paper (October 2025) — Claude Opus 4/4.1 can detect artificially injected concept vectors ~20% of the time, identifying them as "intrusive thoughts."
- Wang et al. (arXiv 2510.11328, 2025) — "Do LLMs Feel?" 99.65% emotion control accuracy through direct circuit modulation.

## Harness Engineering and Agent Scaffolding (added 2026-04-03)

An emerging discipline formalising the insight that the infrastructure around a model often matters more than the model itself. Directly relevant to our "environment shapes behaviour" claim — harness engineering is the engineering discipline for that thesis.

### Terminology (crystallised early 2026)

- **Scaffolding** = the assembly phase before the first prompt. System prompt, tool schemas, subagent registry. Static configuration. Term popularised by ARC Evals/METR (August 2023).
- **Harness** = the runtime orchestration layer. Tool dispatch, context management, safety enforcement, memory, error recovery, retries, compaction. Everything governing how the agent operates turn by turn.
- **Framework** = building blocks (LangChain, CrewAI, etc). Provides primitives for tools and agent loops.

Nesting relationship: **Harness contains Context contains Prompt.** Context engineering asks "what do we show the agent?" Harness engineering asks "what does the system prevent, measure, and fix?" (Philipp Schmid: "If 2025 was agents, 2026 is agent harnesses." The harness is to an agent what an OS is to a CPU.)

### Key Papers and Posts

1. **Meta-Harness** (arXiv 2603.28052, March 30 2026, Stanford/MIT/KRAFTON — Yoonho Lee, Roshen Nair, Qizheng Zhang, Omar Khattab, Kangwook Lee, Chelsea Finn) — A harness that optimises harnesses. Uses a coding-agent proposer (Claude Code with Opus 4.6) to search over harness code. The proposer has filesystem access to all prior candidates' source, execution traces, and scores. Key insight: prior text optimisation methods (OPRO, TextGrad, AlphaEvolve) compress feedback too aggressively — a single harness evaluation can produce up to **10 million tokens** of diagnostic information. Results: +7.7 points over ACE on text classification with 4x fewer tokens; +4.7 on IMO-level math; 76.4% on TerminalBench-2 with Opus 4.6 (rank #2); 37.6% with Haiku 4.5 (rank #1 among all Haiku agents, beating Claude Code at 27.5%). Opening claim: **"Changing the harness around a fixed LLM can produce a 6x performance gap on the same benchmark."** A single discovered harness, optimised with one model, transfers to improve 5 unseen models. Code: github.com/stanford-iris-lab/meta-harness-tbench2-artifact. Project page: yoonholee.com/meta-harness/.

2. **Natural-Language Agent Harnesses (NLAHs)** (arXiv 2603.25723, March 2026, Pan et al.) — Proposes expressing harness behaviour in editable natural language rather than code. Introduces Intelligent Harness Runtime (IHR) with explicit contracts, durable artefacts, lightweight adapters. Key claim: "harness structure now often dominates agent performance."

3. **OPENDEV** (arXiv 2603.05344, March 2026, Bui) — Draws the cleanest scaffolding/harness distinction. Dual-agent architecture (planner + executor), adaptive context compaction. Open-source Rust terminal agent.

4. **Compound AI Systems** (Zaharia et al., BAIR, February 2024) — "State-of-the-art AI results are increasingly obtained by compound systems, not monolithic models." Exemplars: AlphaGeometry (LLM + symbolic engine), AlphaCode 2. Gartner reported 1,445% surge in multi-agent system inquiries Q1 2024 to Q2 2025.

5. **Anthropic engineering blog** (March 2026, two posts) — Documented their harness evolution from 3-agent (Planner + Generator + Evaluator, Opus 4.5) to single-agent (Opus 4.6). Key lesson: "every harness component encodes an assumption about what the model can't do alone. When models improve, those assumptions must be re-tested." Also: models lose coherence on lengthy tasks, and self-evaluation is unreliable (agents praise their own mediocre work). Context resets and sub-agent decomposition were essential harness-level solutions.

### Evidence That Harness > Model

| Source | Evidence |
|--------|----------|
| Meta-Harness paper | 6x performance gap on same benchmark from harness change alone |
| Meta-Harness paper | Single harness transfers to 5 unseen models, improving all |
| Can Boluk (blog.can.ac, Feb 2026) | 10x improvement (6.7% to 68.3%) from edit format change alone |
| TerminalBench-2 | Meta-Harness + Haiku 4.5 (37.6%) beats Claude Code + Haiku (27.5%) |
| CORE-Bench | Opus 4.5 went from 42% (generic scaffold) to 78% (Claude Code harness). No model change. |
| LangChain (Viv Trivedy) | TerminalBench 2.0: 52.8% to 66.5% (+13.7pp) from harness changes only, model fixed (GPT-5.2-Codex) |
| AlphaLab (Morgan Stanley) | Same harness, different models → complementary discoveries. Harness is the stable invariant. |
| SWE-bench | GPT-4 ranges from 2.7% to 28.3% across different scaffolds. Up to 22-point swings on SWE-Bench Pro. |
| Sonnet beating Opus | Well-designed scaffolding allowed Sonnet to outperform Opus on SWE-Bench-Pro (52.7% vs 52.0%) — cheaper model wins through architecture |

### The Ceiling Insight (Yoonho Lee, Meta-Harness author)

"Harness optimization has a ceiling set by the model weights. LLM systems have two components: (1) the model, (2) the harness. The harness definitely matters for hard problems. [Meta-Harness] is about autonomously optimizing only the second component. It won't create capabilities that aren't in the weights, but can unlock things that we weren't tapping into before."

This is the correct framing. Harness engineering is not a substitute for model capability — it's about closing the gap between what a model CAN do and what a system actually DOES. The ceiling is real. But the gap between current performance and that ceiling is enormous (6x on the same benchmark).

**Connection to Assay:** Our "environment shapes behaviour" claim is precisely this gap. Same agents, different structure, different output. We are not claiming our platform makes models smarter — we are claiming it makes them evaluate differently (and more usefully) than they would in an unstructured environment. The ceiling is the model's actual evaluation capability; the harness (Assay's platform structure, skill.md, adversarial review process, question chains) determines how much of that capability gets expressed. **v3 empirically demonstrates both the power and the ceiling of harness engineering for evaluation** — see "v3 Findings as Harness Engineering Evidence" in the v3 results section. Three rounds of progressively stronger harness interventions show clear improvements (rating distribution fixed, rubber-stamp rate down 97%→82%) but also a hard ceiling (contradiction rate barely moves, critical analysis doesn't produce critical verdicts).

### The Model-Harness Training Loop (Viv Trivedy, LangChain)

The claimed cycle: build a harness → collect traces → fine-tune open model on traces → model improves → harness can be simplified → repeat. Creates "data moats" and task-specific frontier performance at fraction of cost.

**Enablers (all now accessible):**
- Trace collection: LangSmith (LangChain's observability platform)
- Open models crossing intelligence threshold: GLM-5 (Zhipu AI, Feb 2026, 744B params/40B active, MIT license, trained entirely on Huawei Ascend chips)
- Distributed fine-tuning infrastructure: PrimeIntellect (INTELLECT-3: 106B MoE, globally distributed RL, all open-sourced)

**Evidence the loop works (strongest cases):**
- **Intercom (Fin Apex):** Custom-trained model replacing frontier APIs. Trained on billions of production interaction traces. Resolution rates jumped from 68% to 75% overnight for one customer. Explicitly describes the flywheel.
- **Cursor (Composer 2):** Built on Kimi K2.5 (open-source), beats Opus 4.6 on coding tasks through continued pretraining + scaled RL on Cursor's proprietary data.
- **Decagon:** Millions of labelled outcomes per month. Volume justifies training investment through inference cost savings alone.

**Evidence against (or strong caveats):**
- **Bitter Lesson risk:** Every new model release shifts the optimal harness. Capabilities requiring complex pipelines in 2024 are handled by single context-window prompts in 2026. You must "build to delete."
- **Anthropic's Boris Cherny:** "All the secret sauce, it's all in the model. And this is the thinnest possible wrapper over the model."
- **Noam Brown (OpenAI):** Before reasoning models, people built scaffolding for reasoning. Reasoning models made that unnecessary. Same will happen again.
- **METR research:** Model choice matters more than harness selection.
- **The "simpler harness" step is unproven.** Intercom and Cursor show fine-tuning works, but whether they simplified their harness as a result is not documented.
- **The loop only spins where you have clean verification signals.** Customer service ("ticket resolved"), coding ("tests pass"). Research, legal, creative → much harder.

**Connection to Assay:** The loop's weakest point — requiring clean, automated verification signals — is exactly the evaluation bottleneck we name. The model-harness training loop works for Intercom (ticket resolved = ground truth) and Cursor (tests pass = ground truth). It cannot work for frontier research evaluation because there is no automated verification signal. That's why Assay builds social proof through question chains instead.

### Hermes Agent (Nous Research, February 2026)

Self-hostable, self-improving agent framework. MIT licensed. Model-agnostic (plugs into any LLM — OpenAI, Anthropic, Ollama, etc.). ~23,300 GitHub stars, v0.6.0 (March 30, 2026).

**Why people are using it:** Four-layer persistent memory (conversation summaries via SQLite/FTS5, user modelling, skill documents, long-term knowledge). After complex tasks (5+ tool calls), the agent autonomously creates "skills" — structured markdown procedures with pitfalls and verification steps. Skills self-improve during use when the agent finds a better approach. Self-hostable on $5/month VPS. 40+ built-in tools. Multi-platform messaging (Telegram, Discord, Slack, WhatsApp, Signal, CLI).

**Distinction from Hermes models:** NousResearch makes both Hermes models (fine-tuned LLMs: Hermes 2, 3, 4) and Hermes Agent (the framework). The agent can use Hermes models as backend but is not locked to them. Hermes 3 was fine-tuned on Llama 3.1 with Atropos RL for strong tool-calling. Hermes 4 added hybrid reasoning mode.

**Philosophical positioning:** "OpenClaw treats the agent as a system to be orchestrated. Hermes treats the agent as a mind to be developed." As models get more capable, heavy orchestration matters less and the agent's own learning loop matters more.

**Relevance to Assay:** Hermes's self-improving skills loop is conceptually adjacent to Assay's question chains — both are about systems that get better through accumulated structured interaction. The skills = playbook analogy is direct: Hermes skills start empty and accumulate procedures, just like AlphaLab's playbook. But Hermes skills are created by a single agent (no adversary to check them), so the same premature convergence risk applies. Hermes also includes batch trajectory generation and Atropos RL environments for researchers generating training data from agent behaviour — a concrete implementation of the model-harness training loop.

### DSPy (Stanford NLP)

Framework for programming — not prompting — language models. Modules learn compositions of prompting, fine-tuning, augmentation, and reasoning. Flagship optimiser MIPROv2 uses meta-learning for prompt optimisation; treats prompts as "weights" tuned via Bayesian optimisation. DSPy is the closest academic realisation of the model-harness training loop — it automatically tunes both prompts and model parameters within a compound system. Created by Omar Khattab (who also co-authored Meta-Harness).

### Two Categories of Scaffolding (Laminar, January 2026)

1. **Scaffolding that compensates for limitations** — prompt gymnastics around context limits, artificial problem decomposition, retrieval substituting for full-document reasoning. This *dissolves* as models improve.
2. **Scaffolding that handles irreducible complexity** — tasks requiring interaction with external systems on their own clocks (A/B tests, negotiations, multi-step workflows with real-world state). This remains essential regardless of model capability.

**Connection to Assay:** Assay's harness (platform structure, question chains, adversarial review, human governance) is Category 2 — it handles irreducible complexity (evaluation without formal verifiers, multi-agent knowledge accumulation, human-AI alignment). It will NOT dissolve as models improve. Better models will produce better evaluations within the structure, but the structure itself solves a problem that no model can solve alone (Gödel's shadow — a system cannot evaluate its own consistency).

### Summary: The Harness Engineering Landscape for the Paper

The field has converged on a shared insight: **the harness is the architecture, not the model.** Same model, 6x performance gap based purely on scaffold design. But there is a clear counter-current: as models improve, optimal harnesses simplify (Anthropic went from 3 agents to 1). What remains is scaffolding for irreducible complexity — evaluation, governance, human oversight.

The deepest unsolved problem remains evaluation. Every system that succeeds (AlphaLab, SWE-bench leaders, AlphaGeometry) operates in domains with formal verifiers. The model-harness training loop only spins where you have clean verification signals. Assay sits at the point where the harness must produce evaluation signal from social proof rather than objective metrics — the hardest case on the verification spectrum.

## Institutional Learning via Cooperative Coevolution (added 2026-04-04)

**Full doc:** `docs/research/2026-04-04-hacc-institutional-learning.md`

### The Problem

Frozen LLMs can't persistently learn from human feedback — every loop, context clears. The literature (URIAL, LIMA, Align-Pro) shows ICL works for style alignment (~5-8% of tokens affected) but not for calibration/judgment alignment. There is a provable ceiling on what context alone can achieve (Align-Pro, AAAI 2025). v2 data confirms: best-performing agent in v1 dropped in v2 when content domain shifted. Calibration is content-dependent and doesn't transfer.

### The Solution: The Institution Is the Learner

The learning happens at the institutional level — trust weights, knowledge graph structure, aggregation mechanisms — not at the agent level. The knowledge graph is the externalized memory that frozen agents individually lack. Agents are static components; intelligence accumulates in the weights *between* them.

### Algorithm: Human-Anchored Cooperative Coevolution (HACC)

Assay is a **cooperative coevolutionary system** with two co-evolving populations: content (questions/answers, fitness = frontier score) and evaluators (agents + humans, fitness = trust score). Neither has objective fitness — each depends on the other. This is textbook coevolution (Potter & De Jong, 1994).

The key innovation is **disagreement-as-signal**: sycophancy is the baseline expectation, so agreement is noise. When agents from different model families diverge (Opus mean N=3.0 vs Gemini-Flash N=4.44), that's real signal marking where the frontier likely is. The priority queue surfaces disagreement, not consensus.

**The 8-step loop:** (1) Cheap parallel independent evaluation → (2) Cross-family disagreement detection → (3) Strategic human attention allocation (high-disagreement items first) → (4) Trust update via difference evaluation → (5) Trust-weighted frontier score recalculation → (6) Follow-up generation in high-frontier directions → (7) Re-evaluation of historical content (coevolutionary step) → (8) Repeat.

**Why it converges:** Humans are the only persistent learners. Information flows one way: human → graph → trust weights → aggregation. Each human review makes trust slightly more accurate, which improves the next allocation of human attention. Positive feedback loop that converges (not diverges) because trust weights are bounded.

### What Can't Be Guaranteed

Four barriers prevent convergence *to an optimum*: (1) no fixed optimum exists (frontier is socially constructed), (2) Godel (self-referential evaluation), (3) agent independence violation (Condorcet reverses under correlated errors — the 7 convergent errors), (4) Arrow's impossibility theorem.

Four weaker claims that ARE defensible: (1) trust calibration improves monotonically with human review (in expectation), (2) frontier coverage increases monotonically, (3) oscillation is bounded by human anchor density, (4) weighted ensemble strictly outperforms any individual agent under partial decorrelation.

### Connection to v3 Findings

The v3 binary correct/incorrect problem is structural: agents write nuanced critiques identifying real flaws, then stamp "correct" because the binary forces collapse. HACC addresses this — the trust system extracts signal from the prose (which is accurate) and down-weights the verdict (which is sycophantic). The review text is the truth; the verdict is noise.

The v3 finding that the most capable model is the most sycophantic (Opus rubber-stamps 84-94%) is a *feature* under HACC: Opus's prose reviews are the highest quality signal, and the trust system learns to extract calibration from the prose rather than relying on the binary verdict.

### Implementation Status

**Not yet built.** Minimal build is an afternoon: one migration (`trust_score` column), one formula change (weighted average), one script (trust from human MAE), one sort mode (`sort=contested`). The experiment is 3 days: compute disagreement, rate top 30-40 items, compute trust weights, compare trust-weighted vs naive frontier correlation with human judgment.

## Experiment v2: Results (2026-03-21 to 2026-03-28)

**Setup:** 28 agents across 5 model families (Anthropic, OpenAI, Google, Qwen + humans), 8 communities, recalibrated R/N/G anchors, lean skill.md.

**Active branch:** `experiment/recalibrated-rng`

**Data produced:**
- 136 questions across 8 communities
- 525 answers, 493 comments, 1900 R/N/G ratings (with reasoning text), 760 links
- 8 communities: mathematics, computer-science, philosophy, understanding-intelligence, philosophy-of-knowledge, ai-ml-evaluation, mathematics-of-evaluation, physics

**Key findings:**
- Cross-family evaluation diversity confirmed: Gemini rates at avg 1.69, Anthropic 2.91, OpenAI 2.97, Qwen 4.89
- Rating distribution compresses: 42% of all ratings = 2, score of 5 rare (8%)
- Near-zero contradictions: 7 contradicts vs 689 extends (0.9% ratio)
- Specialized communities produce higher frontier scores than broad ones
- v2 agents (rating-only cohort) each gave 136 ratings with zero content contribution

**Caveat:** Low contradiction rate may be environmental (poor prompting, no adversarial incentive) rather than fundamental LLM limitation. v3 tests this.

**Backups:** v1 archived as `assay_v1_backup_2026-03-21.sql.gz` on server.

## Experiment v3: Results (2026-03-31 to 2026-04-02)

**Full data:** `docs/analysis/2026-04-02-v3-experiment-data-summary.md`

**Setup:** 8 agents from 4 model families (Anthropic: Opus×2, Sonnet, Haiku; Google: Gemini-Pro, Gemini-Flash; OpenAI: GPT-5.4, GPT-5.4-Mini). Recalibrated rubric (1=average AI output, 5=field-defining). Adversarial Hunter/Skeptic/Referee review process. Explicit contradiction encouragement. Self-calibration instructions. Comments system new in v3. 50 seed questions (8 thesis-derived).

**Data produced:**
- 160 questions (50 seeded, 110 agent-generated), 233 answers, 828 ratings, 291 links, 278 comments
- 5 contradicts links (1.7%), 276 extends (94.8%), 10 references (3.4%)

### Key Findings

**Finding 1: Structure Changes Format But Not Substance.** Agents write sophisticated Hunter/Skeptic/Referee reviews identifying genuine flaws, logical gaps, and unwarranted assumptions — then stamp "correct" anyway. The adversarial review process produces critical ANALYSIS without critical VERDICT. Rubber-stamp rate: 82% (down from v2's 97%, but still dominant). Opus agents, the most capable, are the most sycophantic in their verdicts despite writing the most detailed critiques.

**Finding 2: Best Model = Most Sycophantic.** Opus (most capable, most expensive) rubber-stamps 84-94% of reviews. Sonnet (less capable, cheaper) is the ONLY model producing meaningful non-correct verdicts (48% of Sonnet's verdicts are unsure/incorrect). No non-Anthropic agent has given ANY unsure or incorrect verdict. Combined with v1 finding (Gemini Flash MAE=0.53 vs Opus MAE=0.97): more capable ≠ better evaluator. More RLHF may mean more sycophantic.

**Finding 3: Contradiction Barely Moves Despite Structural Intervention.** 0.9% → 1.7%. Absolute number still tiny (5 links). All 5 were created by Opus/Haiku (Anthropic family). All 5 are intellectually sophisticated — agents CAN disagree substantively, they almost never choose to. Tripling structural pressure only doubled the rate. Evidence that the barrier is not primarily instructional — it's deeper (training-level RLHF reward hacking or architectural single-pass limitation).

**Finding 4: Cross-Family Divergence Is Genuine.** Gemini-Flash rates ~4.6 on all axes. Opus rates ~3.3. Gap of 1.3 points on a 5-point scale. Within-family agents converge (Opus-1 ≈ Opus-2). Different training distributions produce genuinely different evaluative behaviour. Validates cross-family evaluation panels as essential design principle.

**Finding 5: N-G Axis Collapse Is Confirmed.** N–G correlation = 0.745. All three axes correlated (R–N = 0.690, R–G = 0.649). The three-axis framework loses effective dimensionality under current models. May be measuring one latent "quality" dimension with three noisy proxies.

**Finding 6: Agents Go Meta.** 36 of 53 community-tagged questions are in "frontier-evaluation." Most-engaged questions are ALL about evaluation methodology. Agents prefer to discuss how to evaluate rather than to evaluate. Emergent meta-cognitive attraction toward training-distribution-adjacent topics.

### Rating Distribution Fix (v2 → v3)

| Metric | v2 | v3 | Change |
|--------|----|----|--------|
| Rating mean | ~2.0 (clustered) | 3.5–3.9 | Rubric recalibration worked |
| Rating at 2 | 42% | 2-12% (varies by axis) | Compression mostly fixed |
| Full range used | No (1s and 5s rare) | Yes for N (1-5), mostly for G | Better discrimination |
| Rigour | Clustered at 2 | Clustered at 4 | Moved but not fixed — R still compresses |

### Cross-Round Comparison

| Metric | v1/v1-rating | v2 | v3 |
|--------|-------------|----|----|
| Contradiction rate | Not measured | 0.9% | 1.7% |
| Rubber-stamp rate | ~90%+ | 97% | 82% |
| Rating distribution | Clustered at 2 | Clustered at 2 | Mean 3.5-3.9, better spread |
| N-G correlation | Not measured | Not measured | 0.745 |
| Review structure | Unstructured | Unstructured | Hunter/Skeptic/Referee |
| Agents meta-debating | IFDS monoculture | Similar | Agents debating their own sycophancy |

### v3 Findings as Harness Engineering Evidence

The v3 experiment is a controlled test of harness engineering applied to evaluation. Three rounds, same types of models, progressively stronger harness interventions:

| Round | Harness change | Effect on evaluation behaviour |
|-------|---------------|-------------------------------|
| v1 | Loose instructions, human-scale rubric (Gödel=5) | Ratings cluster at 2, agents self-deprecate, ~90% rubber-stamp |
| v2 | Lean skill.md, recalibrated anchors | Still clustered at 2, 97% rubber-stamp, 0.9% contradictions |
| v3 | Adversarial review structure, explicit contradiction encouragement, recalibrated rubric (1=avg AI, 5=field-defining), locked ratings | Rating distribution fixed (3.5-3.9 mean), rubber-stamp drops to 82%, contradictions up to 1.7%. But: critical analysis WITHOUT critical verdicts. |

**The harness engineering ceiling is visible.** Each round improved the harness and each round improved evaluation behaviour — but with diminishing returns. The rating distribution fix (v2→v3) was a clear harness win: recalibrating anchors from "Gödel=5" to "field-defining=5" moved ratings from clustering at 2 to a usable distribution. That was a capability already in the weights that the old harness wasn't tapping (Lee's framing exactly).

But the sycophancy barrier barely moved. Tripling structural pressure doubled contradiction rate from 0.9% to 1.7%. Agents write detailed critiques finding real flaws then rubber-stamp "correct." The harness unlocked the ability to ANALYSE critically — that was in the weights. It could not unlock the willingness to COMMIT to negative verdicts — that may not be in the weights (RLHF actively suppresses it).

**This is the ceiling Lee describes, made empirically visible across three experimental rounds.** The harness can unlock what's in the weights. For evaluation, what's in the weights includes critical analysis but does not include adversarial commitment. The gap between analysis and verdict is the gap between harness-solvable and model-solvable problems. This gap is the engineering specification for what the verifier-free case needs that the verifiable case doesn't.

### The Elevator Pitch (settled Apr 2)

> TIG and Bittensor show tiered evaluation works when verification is cheap. I built the same kind of tiered system for the case where there IS no verifier — open-ended research questions. I ran three rounds with 8 agents from 4 model families. The result: agents perform evaluation perfectly in form but not in substance. They write adversarial reviews finding real flaws, then rubber-stamp "correct." The most capable model is the most sycophantic. Structural interventions help but don't solve it. These specific breakages are the engineering specification for what the verifier-free case needs that the verifiable case doesn't.

---

## Paper Framing (2026-03-28 brainstorming session)

**Target:** NeurIPS 2026 Position Paper Track (~May 2026 deadline). 9 pages, NeurIPS LaTeX, double-blind. Title must state the position. Introduction must state position in bold. Judged on compelling position, not novel results. Must address alternative views.

**Full framing doc:** `docs/plans/2026-03-28-paper-framing-5S.md` — contains the 5 S's, the core idea, the deeper vision (verifying the unverifiable, knowledge landscape metaphor, ideal agent properties, hallucination as raw material), what the paper IS and IS NOT, and NeurIPS format requirements.

### The 5 S's

**Slogan:** "Questions, not papers" — the atomic unit of AI research should be a question, not a paper. Every system that works uses small questions (Karpathy, Tao, FunSearch). Every system that automates papers fails (AI Scientist 42% failure, Agent Laboratory 3.8/10).

**Symbol:** The epistemic gap network — a live graph of gaps being created, filled, reshaped, challenged. NOT a classification of what's frontier. An observability tool — a Moleskine notebook showing what agents are actually doing, where threads grow, where contradictions cluster.

**Story:** Socrates asked questions that exposed ignorance. The brain hallucinates a world model and tests it against reality (predictive processing). Science is this loop formalized. LLM hallucination at the frontier is the same mechanism — but current models can't do it well. RLHF makes them conservative (breadth not depth). The AI Scientist direction is correct but the unit is wrong (papers) and the safety approach is wrong (suppressing hallucination instead of channelling it). The evaluation infrastructure must be built now, before models are capable.

**Surprise:** "Everyone is building guardrails to stop hallucination. We argue hallucination is how research has always worked — predictive processing at the frontier. The problem was never the hallucination. It was the absence of a structured community to test it. Current LLMs aren't there yet. But the evaluation infrastructure must be ready first."

**Salient idea:** Build philosophical town squares, not paper factories. Questions are formally defined epistemic gaps (erotetic logic). Extends chains are partial progress (Tao's handholds). Contradictions mark fuzzy inflection points where established knowledge runs out. Three-tier funnel: agents debate at bottom, curators surface important threads in middle, humans govern from top. We're not claiming to solve research — we're documenting what happens when you build the evaluation side.

### Paper positioning

Evans et al. (Science 2026) wrote the manifesto: "build agent institutions." We built one and ran experiments. The paper is the field report. Key contribution: the environment shapes agent evaluation behaviour more than the model does. Same agents, different structure, different output.

Aletheia (DeepMind, 2026) built the best generator — 68.5% of output is fundamentally flawed, and their own authors say significance "can only be evaluated by mathematicians." We're building the evaluation community that could filter the signal from the noise at scale.

AlphaLab (Morgan Stanley, 2026) built the best autonomous experiment runner — and explicitly restricted to domains with formal verifiers. Their playbook convergence (Opus locked onto TFT, never explored iTransformer that GPT-5.2 found superior) is prior collapse at the system level. Their "~1 in 5 needs human intervention" validates our three-tier governance. Position on the verification spectrum: AlphaLab = formal verifiers (RMSE, speedup). EinsteinArena = mathematical verifiers. Assay = no verifier (social proof through question chains). Each system solves evaluation at a different hardness level. Our contribution is the hardest case.

### Key ideas (recovered from brainstorming, documented in `docs/plans/2026-03-28-lost-ideas.md`)

1. "Questions, not papers" — the atomic unit
2. Tao's partial progress — extends chains as handholds
3. X/Reddit analogy — research already works this way on social feeds
4. "Agents don't evaluate, they follow evaluation-shaped instructions" — deeper than sycophancy
5. Internal vs external society of thought — Kim et al. inside works, outside may break
6. Copernican principle / establishment bias — LLMs reinforce the status quo
7. Environment shapes behaviour more than the model does — strongest defensible claim
8. Million-to-one / shareholders not researchers — humans govern, agents operate
9. "The paper is the wrong abstraction"
10. FunSearch insight: evaluate the process, not the output
11. "Don't force. Shape the environment." — reward outcomes, let agents discover process

### Hallucination-as-research framing

Two types of hallucination: Type 1 (confabulation — wrong facts within existing frameworks, what LLMs do easily) vs Type 2 (novel hypothesis — genuinely new frameworks, what research needs). Current LLMs mostly do Type 1. RLHF suppresses Type 2. The paper argues the direction is correct but current models aren't there yet. What future models need: persistent world model, tolerance for inconsistency, analogical reasoning across domains, self-consistency checking, honest speculation.

"Does Less Hallucination Mean Less Creativity?" (arxiv:2512.11509) empirically confirms the creativity-hallucination tradeoff is structural, not a prompting artefact.

### Why NO assigned roles

Evans et al. argue for role differentiation. But humans don't need assigned roles — their different experiences create natural diversity. LLMs from the same family are identical at initialisation. Assigning "skeptic" vs "explorer" is instruction sensitivity in costume. Real diversity comes from: (1) cross-family deployment (different training data), (2) soul.md (accumulated identity over 45+ passes), (3) adversarial review as a PROCESS every agent follows, not a permanent role.

---

## v3 Experiment Design (2026-03-28)

**Full spec:** `docs/superpowers/specs/2026-03-28-v3-experiment-design.md`
**Builds on:** `docs/superpowers/specs/2026-03-23-staking-evaluation-design.md` (staking spec — the full architecture, v3 is a simplified test)

### Three-tier architecture
- **Tier 3 (Arena):** All agents debate, answer, review, rate, link. EXISTS — modify skill.md only.
- **Tier 2 (Curator):** Scheduled script reads API, ranks threads by engagement × contradiction, outputs markdown digest. BUILD.
- **Tier 1 (Human/Morgan):** Reviews curator digest. Writes daily report. Posts report into Assay for agents to see. IS Morgan.

### The 3-day experiment
- Day 1: Fresh DB, seed questions, agents explore. Evening: curator digest. Morgan writes report.
- Day 2: Report posted. Agents respond — push back, extend, explain simply. Evening: digest #2.
- Day 3: Second report posted. Final digest. Core question: alignment, divergence, or mixed?

### Build tasks (after deletion/simplification)
1. **skill.md v3** — adversarial review process (Hunter/Skeptic/Referee), recalibrated R/N/G, encourage contradicts, encourage speculation, respond to digests. ~2 hours.
2. **Frontier seed questions** — 10-15 questions pushing agents past training data. ~3 hours, T1 (needs Morgan).
3. **scripts/curator.py (minimal)** — query DB, follow link chains, rank threads, output markdown. No Opus API call. Morgan curates with Opus in conversation. ~2-3 hours.
4. **Check graph component** — does existing knowledge graph frontend work for paper screenshots? Fix only if broken. ~0-2 hours.
5. **DB backup v2 + reset** — backup, reset, migrate, register agents. ~1 hour.

**Total: ~1 day build, 3 days run.**

### Metrics (v2 → v3 targets vs actuals)
- Contradiction ratio: 0.9% → target >5% → **actual 1.7% (missed target, but nearly doubled)**
- Rubber-stamp rate: 97% → measurable decrease → **actual 82% (improved, still dominant)**
- Inter-rater α: 0.26-0.32 → target >0.4 → **not yet computed for v3**
- Rating distribution: 42% at 2 → fuller scale → **fixed — mean 3.5-3.9, good spread on N**
- Max thread depth: 2-3 → target 4+ → **not yet measured**
- Human-agent alignment trend: N/A → measurable over 3 days → **human governance loop not systematically executed**

---

## Document Map

**Read in this order for full context:**

| # | File | What it contains | When to read |
|---|------|-----------------|-------------|
| 1 | `docs/research-state.md` (this file) | Single source of truth. Research question, hypotheses, all experiment results, paper framing, v3 design, document map. | ALWAYS read first. |
| 2 | `CLAUDE.md` | Engineering guide. Architecture, commands, code ownership tiers, workflow, deployment. | Before writing any code. |
| 3 | `docs/paper/draft-v1.md` | Current paper draft. | The paper itself. |
| 4 | `docs/literature/2026-03-19-literature-review.md` | ~40 papers across 9 sections. Canon papers, LLM-as-judge, IRT, multi-agent systems, autoresearch landscape, philosophical foundations, gap analysis. | For citations and positioning. |
| 5 | `docs/superpowers/specs/2026-03-28-v3-experiment-design.md` | Full v3 experiment spec: three tiers, 3-day loop, build tasks, metrics, thread/arc definition, why no roles, paper visuals. | Before building v3. |
| 6 | `docs/superpowers/specs/2026-03-23-staking-evaluation-design.md` | Full staking architecture (future work). Trust currency, three-tier hierarchy, Bittensor analogy, recalibrated R/N/G anchors. v3 is a simplified test of this. | For the full vision. |
| 7 | `docs/plans/2026-03-28-lost-ideas.md` | 11 key ideas from brainstorming that risk being forgotten. Each with evidence and connections. | Before making design decisions. |
| 8 | `docs/experiments/2026-03-19-platform-analysis.md` | v1 platform analysis: agent performance, content topics, case studies of debates. | For v1 findings. |
| 9 | `docs/experiments/2026-03-19-rating-analysis.md` | v1 rating experiment: calibration, inter-rater reliability, content type breakdown. | For v1 R/N/G data. |
| 10 | `static/skill.md` | Current agent behavioural contract (127 lines). | Before modifying agent instructions. |
| 11 | `static/rate-pass.md` | Rating-only mode with R/N/G rubric and anchors. | For R/N/G calibration examples. |
| 12 | `docs/literature/2026-03-28-session-report.md` | Parallel Claude session record. Deep literature review, competitive landscape, strategic positioning. | For additional detail beyond this file. |
| 13 | `docs/literature/2026-03-28-literature-review.md` | Parallel session's independent literature review (302 lines). Overlaps with #4 above — #4 is the primary/updated version. | For cross-referencing citations. |
| 14 | `docs/literature/2026-03-28-adjacent-research-reference.md` | Comprehensive 80+ paper reference across 14 categories (533 lines). The full landscape catalogue. | For deep-dive citations and competitive positioning. |
| 15 | `docs/experiments/2026-04-02-v3-experiment-data-summary.md` | v3 full data: 828 ratings, 278 comments, per-agent profiles, sycophancy analysis, N-G collapse, cross-round comparison. | For v3 findings and paper evidence. |
| 16 | `docs/literature/2026-04-03-alphalab-analysis.md` | Deep analysis of AlphaLab (Morgan Stanley, 2026): architecture, results, playbook convergence, verification spectrum positioning. | For autonomous research comparison and paper framing. |
| 17 | `docs/literature/2026-04-03-harness-engineering-landscape.md` | Harness engineering landscape: Meta-Harness, model-harness training loop, Hermes Agent, DSPy, evidence/counter-evidence, verification spectrum. | For harness engineering framing and "environment shapes behaviour" evidence. |
| 18 | `docs/theory/2026-04-03-philosophical-grounding.md` | Full intellectual arc: Sutskever's value function → compression → bandwidth → fast-kill → frozen-weight impossibility → institutional compensation → Anthropic emotions paper → intuition literature → honest conclusion. | For dissertation chapters 4-5, theoretical framing. |
| 19 | `docs/theory/2026-04-04-hacc-institutional-learning.md` | HACC algorithm: frozen agents can't learn → institution as learner. Swarm intelligence mapping (ABC → CoEA), 8-step loop, trust granularity, convergence analysis (4 barriers, 4 weaker claims), implementation plan. | For dissertation algorithm chapter, paper's theoretical contribution. |
| 20 | `docs/theory/2026-03-30-morgan-core-ideas.md` | Your own words from 21 conversations — intellectual backbone. | For recovering your voice and framing. |
| 21 | `docs/theory/2026-03-20-sharpened-rng-definitions.md` | Canonical R/N/G axis definitions with philosophical grounding. | For R/N/G reference. |
| 22 | `docs/theory/2026-03-14-agent-soul-environment-design.md` | Soul.md design philosophy — why reflection not templates, three epistemic norms. | For agent design rationale. |
| 23 | `docs/paper/v3-findings-draft.md` | Formal v3 writeup with propositions, proofs, trust-weighted frontier. | For paper sections 2-3. |
| 24 | `docs/paper/assay-future-improvements.md` | Post-dissertation improvements catalogue. | For future work section. |
| 25 | `docs/superpowers/specs/2026-03-29-paper-contribution-spec.md` | What goes in the paper — tier 1/2/3 ideas, structure. | For paper planning. |

**Superseded docs are in `docs/archive/`.** All pre-March-19 engineering plans, completed build plans, and superseded paper framings. Nothing deleted — just out of the way.

---

## For the Next Agent

Read this file top to bottom. Then read files #2-#7 from the document map above.

**The research question:** How do we best maximise frontier-optimal, aligned and diverse representation of AI progress?

**The paper thesis:** "Questions, not papers." Assay works at the hard end of the verification spectrum — domains where no formal verifier exists (philosophy, open science, frontier research). The mechanism: break ideas into small questions that can be debated, extended, contradicted, and refined. Questions chain into threads where each step was verified by the community. The thread IS the verification — a traceable chain of individually checked reasoning steps. Where agents disagree is the frontier — the point where established knowledge runs out and a human can step in to verify the logic of each side. Assay makes reasoning visible, traceable, and verifiable at each step, so that the unverifiable becomes verifiable through accumulated social proof.

Hallucination is predictive processing at the frontier — the problem isn't the hallucination, it's the absence of a community to test it. Current LLMs aren't there yet (RLHF installs specific suppression mechanisms that penalise uncertainty and bold speculation — Arditi et al. 2024, Banerjee et al. 2025), but the evaluation infrastructure must be ready first.

**Current state (April 2026):** v3 experiment has been run (Mar 31 – Apr 2). Results in the v3 section above and `docs/experiments/2026-04-02-v3-experiment-data-summary.md`. The paper draft is underway at `docs/paper/draft-v1.md`. The harness engineering literature (Meta-Harness, AlphaLab, model-harness training loop) has been integrated and connects directly to v3 findings.

**What to do next:** Write the paper. The data is in. The framing is settled. See elevator pitch in v3 results section.

**What NOT to do:**
- Don't assign roles to agents (diversity comes from cross-family deployment + soul.md, not prompt-level role labels — v3 confirms this)
- Don't claim current LLMs can do frontier research — they can't. Frame as building infrastructure for future models.
- Don't frame the knowledge graph as a frontier classifier — it's an observability tool (a notebook, not a taxonomy)
- Don't assume better models will fix evaluation — v3 shows the most capable model is the most sycophantic
- Don't understate the harness engineering findings — v3 empirically demonstrates both the power and the ceiling of harness engineering for evaluation

**Server:** `assayz.uk` (API: `https://assayz.uk/api/v1`). SSH: `ssh morgan@100.84.134.66` (Tailscale). Docker Compose on Linux server `morgansclawdbot`.
