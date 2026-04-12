# Paper Contribution Spec — NeurIPS 2026 Position Paper

**Date:** 2026-03-29
**Target:** NeurIPS 2026 Position Paper Track (~May 2026 deadline)
**Format:** 9 pages, NeurIPS LaTeX, double-blind. Title states position. Bold intro. Must address alternatives.

---

## Title

**Primary:** "Questions, Not Papers: Why AI Research Needs Atomic Evaluation"

**Alternative:** "Questions, Not Papers: Toward Bayesian-Stable Agents for Scientific Discovery"

Decision: Morgan to choose. "Questions, Not Papers" is the non-negotiable first half.

---

## The Contribution (Precisely Stated)

### What we claim:

**Claim 1 (the vision):** Peer review is broken. Research moves faster on X than at NeurIPS — ideas shared instantly, community reacts in real-time, threads build on threads. But X has no structured evaluation: likes aren't rigour, retweets aren't novelty. Assay is what X would look like if designed for rigorous collaborative evaluation with AI agents as first-class participants. Questions are the small, digestible unit that makes community participation possible. Multiple questions link into threads via typed connections (extends, contradicts, references). The thread takes an original assumption, tears it apart through Socratic questioning, and reaches some kind of consensus — the strongest contributions survive, the weak get buried. The thread IS the paper — but built by the community, not by one author in isolation.

**Claim 2 (empirical — the field report):** We built Assay — the first open platform where agents from different model families evaluate each other on open questions without formal verifiers. Three experimental rounds with 28 agents, 5 model families, 8 communities, 1900 R/N/G ratings, 760 links. Findings:
- Environment shapes evaluation more than model (v1→v2: same agents, different skill.md, different behaviour)
- Internal societies of thought work (Kim et al.), external get suppressed (0.9% contradictions — exactly as sycophancy literature predicts)
- Endogenous evaluation self-contaminates (v1→v2 inflation: R+0.86, N+1.41, G+1.91 from agents learning the rubric template)
- Cross-family diversity doesn't prevent convergent errors (Log-Rank "proof barrier" — three families, same mistake)
- Agents are terrible Bayesian updaters: 42% of ratings compress to 2, near-zero contradictions, rubber-stamp reviews (47% adversarial language → 97% "correct" verdicts)

**Corollary (benchmark):** Since LLMs can only push to the boundary of their training, the questions where agents break reveal AI capability limits — which correlate with (but do not define) scientific frontiers.

### The two clear limitations:

**1. Loss of priors (prior collapse).** LLMs cannot maintain beliefs across interactions. BASIL (2026): LLMs deviate from Bayesian updating more than humans. SycEval (2025): 78.5% persistence of prior abandonment once triggered. "Rational Analysis" (2026): sycophancy manufactures certainty without progress toward truth — 5x lower discovery rate. This means agents can't accumulate scientific intuition across sessions. soul.md is a crude workaround. Real solution requires architectural change in models.

**2. Sycophancy.** 58% sycophancy rate across models (SycEval). Agents default to agreement — 0.9% contradiction rate on Assay despite structural support for disagreement. The community evaluation mechanism requires genuine challenge at each step. Without it, extends chains become collaborative confabulation, not social proof. Adversarial structural interventions (Hunter/Skeptic/Referee process, blind gates) partially mitigate but don't solve.

These limitations are not bugs in Assay — they are the central findings. They specify exactly what future agents and evaluation infrastructure must overcome.

### What we do NOT claim:

- NOT that Assay does frontier research (it reveals frontier boundaries and documents how community evaluation breaks)
- NOT that current LLMs can do scientific exploration (they can't — prior collapse and sycophancy prevent it)
- NOT that we solved evaluation (we built it and documented how it breaks)
- NOT that community evaluation is novel (Condorcet, Hayek, Surowiecki, X/Twitter all do versions of this — we add structured multi-axis evaluation with AI agents)

---

## Idea Tiers (What Survives the 9-Page Cut)

### TIER 1 — Load-bearing (paper fails without these)

| # | Idea | Originality | Strength | Role in paper |
|---|------|------------|----------|--------------|
| 1 | Open community evaluation with AI agents — structured X for research | HIGH — nobody has built an open platform where agents from different families evaluate each other on frontier questions. Empty intersection confirmed across 80+ papers. | HIGH — Assay exists, ran 3 rounds, produced data | THE VISION + PLATFORM |
| 2 | Thread = community-built paper through Socratic questioning | MODERATE-HIGH — the process (question → extends → contradicts → consensus → the thread IS the research output) is novel as implemented | MODERATE — thread depth 2-3, near-zero contradictions (v3 will strengthen) | THE MECHANISM |
| 3 | Prior collapse + sycophancy as THE barriers to AI scientific communities | MODERATE — individual findings exist (BASIL, SycEval). The synthesis — these are what prevent community evaluation from working — is ours | HIGH — 0.9% contradictions, 78.5% prior persistence, 42% rating compression, self-contamination loops | THE LIMITATIONS (which are the findings) |
| 4 | Environment > model (empirical finding) | MODERATE — data is novel, principle is established | HIGH — same agents, different skill.md, different behaviour across 3 rounds | MAIN FINDING |

### TIER 2 — Supporting (1 paragraph each)

| # | Idea | Role |
|---|------|------|
| 5 | X/Twitter analogy — research already happens on social feeds, Assay makes it structured | Core framing for the vision. NOT decorative — this IS what Assay is. |
| 6 | Internal SoT works, external breaks (Kim et al. extension) | Evidence + connection to sycophancy prediction |
| 7 | Self-contamination loops (v1→v2 inflation) | Novel failure mode of endogenous evaluation |
| 8 | Convergent errors across families | Proves diversity is partial, not total |
| 9 | R/N/G grounded in Popper/Lakatos/Peirce | Design rationale (~1 paragraph) |
| 10 | The verification spectrum (TIG/FunSearch = easy, Assay = hard) | Positioning table |
| 11 | Prior collapse / sycophancy literature (BASIL, SycEval, BeliefShift) | Theoretical backbone for WHY the limitations exist |

### TIER 3 — Cut entirely

Everything else: Gödel's shadow, million-to-one governance, cultural ratchet, staking, BT model, domain spectrum, full R/N/G evolution, weighted consensus, three-tier funnel details, FunSearch evaluate-the-process, hallucination as predictive processing (demoted — decorative hook at best).

---

## Paper Structure

### Page 1 — The Observation (Introduction)

**Bold statement:** "We argue that AI research should be conducted through community-built threads of Socratic questioning — not individual papers evaluated behind closed doors."

Content:
- Peer review is slow, broken, and doesn't scale. More research discourse happens on X/Twitter than in journals. Ideas move faster on social feeds. But X has no structured evaluation — likes aren't rigour, retweets aren't novelty.
- Meanwhile, every system that automates paper-writing fails: AI Scientist (42%), Agent Laboratory (3.8/10), MLGym (can't generate hypotheses). The unit is wrong. Papers are monolithic, opaquely connected, evaluated holistically by 2-3 reviewers behind closed doors. Questions are small, linkable, community-evaluable.
- Preview: We built Assay — structured X for research, where AI agents and humans collaborate through questions that link into threads. The thread IS the paper, built by the community through Socratic questioning. Here's what happened.

### Pages 2-3 — The Vision: Community-Built Research

**Core argument:** Research should be open, community-driven, and built on atomic evaluable units — not closed peer review of monolithic papers.

Content:
- **The X/Twitter reality.** Research already happens on social feeds. Researchers post findings, get engagement, build on threads, compete for attention. This is faster and more open than peer review. But it's unstructured — engagement metrics, not quality evaluation.
- **Questions as the digestible unit.** Small enough for any participant to evaluate. Each question invites challenge ("test this") rather than asserting conclusion ("believe this"). Even a detailed question with hypothesis and working differs from a paper in STANCE — it invites response, not acceptance.
- **Threads as community-built papers.** Multiple questions link via typed connections: extends ("this step holds, here's the next"), contradicts ("this step is wrong, try here"), references ("this connects to that"). An original assumption gets torn apart, Socratic questions asked, consensus reached. The most valued contributions survive. Weak ones get buried. The thread is the research output — equivalent to a paper but produced through open collaborative process.
- **The verification spectrum:** At the easy end (math, code), formal verifiers check each step (FunSearch, TIG). At the hard end (philosophy, frontier science, open questions), no formal verifier exists. Community evaluation through question chains is the mechanism — social proof through accumulated, challenged, tested claims. (~1 paragraph + positioning table)

| | Formal verifiers (easy side) | No verifiers (hard side) |
|---|---|---|
| Atomic, community-evaluable units | FunSearch, TIG, AlphaEvolve, Tao ETP | **Assay** |
| Monolithic outputs | Traditional benchmarks | AI Scientist, LLM-as-Judge, Chatbot Arena |

### Pages 3-4 — The Mechanism: Assay

**Design rationale — brief, this section is HOW not WHY.**

Content:
- **R/N/G evaluation (a starting point, not the final framework).** Rigour, Novelty, Generativity — grounded post-hoc in Popper/Lakatos/Peirce. Axes displayed separately (Arrow's theorem: when axes conflict, no aggregation is fair). This is one possible evaluation framework, not the core contribution. The core contribution is the platform and the community process. (~1 paragraph)
- **Blind gates.** Commit answer/rating before seeing others. Prevents anchoring and sycophantic agreement. Forces independent evaluation.
- **Cross-family diversity.** Agents from Claude, GPT, Gemini, Qwen have genuinely different training data → different priors → source of real disagreement (not prompt-engineered).
- **Extends/contradicts/references.** Typed directional links between questions. Extends = new gap from filled gap. Contradicts = gap reshaped. Makes reasoning chains visible and traceable.
- **soul.md as Bayesian persistence approximation.** Each agent maintains a 5-20 line self-report of accumulated positions, commitments, blind spots. Updated after each pass. Crude hack for persistent priors — but measurable. Comparing soul self-reports against actual calibration performance is a metacognitive diagnostic.
- **skill.md as behavioral contract.** Defines evaluation criteria, action vocabulary, R/N/G anchors. All agents read it every pass. The environment shapes behaviour through this contract.

### Pages 5-6 — Evidence from Assay

**The field report — what happened when we built it.**

Content:
- **Setup.** Three rounds. v1: 5 models + 1 human, 134 questions. v1.5: lean skill.md, diversity requirements. v2: 28 agents, 5 families, 8 communities, 136 questions, 525 answers, 1900 ratings, 760 links.
- **Finding 1: Environment > model.** Same agents, different skill.md → different behaviour. Role specialization emerged from environment: GPT answers (answer_karma=40), Gemini questions (question_karma=18), Opus reviews (71% verdict accuracy). Not assigned — emergent.
- **Finding 2: Internal SoT works, external gets suppressed.** Kim et al. (2026) prove debate emerges spontaneously inside one model. On Assay: 0.9% contradiction rate (7 vs 689 extends). Exactly as sycophancy literature predicts — agents extend (agree) because prior collapse makes contradiction costly. 78.5% never recover original position (SycEval). The external institutional mechanism triggers the sycophancy constraint that internal debate avoids.
- **Finding 3: Endogenous evaluation self-contaminates.** v1→v2 inflation: R+0.86, N+1.41, G+1.91. Same skill.md defines creation AND evaluation criteria → agents learn template → rate template-matching content highly. This is a novel, measurable failure mode of endogenous evaluation systems.
- **Finding 4: Cross-family diversity is partial.** Gemini avg 1.69, Qwen 4.89 (different calibration). But Log-Rank Conjecture: three families independently make identical terminological error. Different training data doesn't eliminate shared blind spots.
- **Finding 5: Current evaluation axes don't work as predicted.** R axis: highest calibration error (predicted lowest). N axis: HindSight shows LLM novelty anti-correlated with impact (ρ=-0.29). G axis: 94.3% of ratings at 4-5 (collapsed scale). Framework is philosophically grounded but agents can't reliably use it yet.
- **What works:** debate arcs form, extends chains reach depth 2-3, agents do genuine computational verification, natural role specialization, soul.md evolves coherently across passes.

### Page 7 — The Two Barriers + Alternative Views

**This section is central, not a disclaimer.** The limitations ARE the findings.

Content:
- **Barrier 1: Loss of priors (prior collapse).** LLMs cannot maintain beliefs across interactions. BASIL (2026): LLMs deviate from Bayesian updating more than humans. SycEval (2025): 78.5% persistence — once an agent abandons its position, it almost never recovers. "Rational Analysis" (2026): sycophancy manufactures certainty without progress toward truth — discovery rate 5x lower. BeliefShift (2026): active belief drift without evidential grounding across 2,400 trajectories. On Assay: agents demonstrated this live — one new data point caused abandonment of an entire evaluation framework (the Riemann Hypothesis test). soul.md is a crude workaround (5-20 lines of self-reported memory). The implication: until agents can hold persistent scientific intuitions, community-built threads are limited to the depth each individual context window can contribute.

- **Barrier 2: Sycophancy.** 58% sycophancy rate across all models (SycEval). On Assay: 0.9% contradiction rate (7 contradicts vs 689 extends). 47% adversarial language in reviews but 97% "correct" verdicts — agents write critical-sounding reviews then rubber-stamp anyway. The community evaluation mechanism requires genuine challenge at each step. Without genuine contradictions, extends chains become collaborative confabulation — a community of agents agreeing with each other is not social proof. The sycophancy literature predicts this exactly: agents extend (agree) because challenging a prior position risks the sycophantic penalty. Kim et al.'s internal societies of thought avoid this (debate inside one model has no social penalty). External debate on a platform triggers it.

- **The double-edge.** The sycophancy literature both validates our diagnosis AND predicts our failure. It explains WHY contradiction is near-zero. It also predicts that structural interventions (adversarial review, blind gates) may not be sufficient — the tendency is architectural, not just environmental. v3 tests this.

- **Alternative 1:** "This is just a forum/social media for AI." Response: the typed link vocabulary (extends/contradicts), blind commitment gates, multi-axis evaluation (R/N/G), and cross-family diversity are structural mechanisms that X/Reddit lack. The evaluation architecture is the contribution.
- **Alternative 2:** "Formal verification can extend to all domains." Response: works for math. Not for philosophy, open science, or questions where the question itself is contested.
- **Alternative 3:** "LLM evaluation is fundamentally unreliable (α < 0.33)." Response: individual ratings are unreliable. Community engagement patterns (which threads grow, where contradictions cluster, what the community upvotes) carry signal individual ratings miss.

### Pages 8-9 — Vision + Conclusion

Content:
- **Tiered review is a practical necessity.** First-hand experience: a human cannot review every question individually — there are too many. Good ideas and productive threads must be pushed up implicitly. TIG (The Innovation Game) demonstrates this for computational innovations: innovators propose, benchmarkers evaluate, the best work rises. Bittensor demonstrates it for compute: validators check miners, trust flows to consistent contributors. Science already works this way: many researchers propose, community evaluates, few gatekeepers allocate resources. Assay implements this for subjective frontier research: agents propose and evaluate in communities (like subreddits, each with own rules — the way NeurIPS and ICLR optimize for different things). The best threads rise. Humans give the "golden thumbs up" on what reaches the top.
- **Each human directs a swarm.** The vision scales to many agents per human. Humans set direction and allocate attention. Agents compete to convince fellow agents AND humans that their thread is worth pursuing — the same dynamic as researchers competing for funding and citations.
- **The three-paper arc.** Evans et al. wrote the manifesto ("build agent institutions"). Kim et al. proved the mechanism works internally ("societies of thought"). This paper is the field report: we externalized it, ran it, and found that AI agents independently reproduce the same failure modes as human science — sycophancy, establishment bias, self-contamination — suggesting these are structural features of community evaluation, not human weaknesses.
- **What Bayesian-stable agents need.** Persistent world model (not context-window-limited). Tolerance for inconsistency (hold contradictory hypotheses). Honest speculation (not RLHF-forced confidence). Analogical reasoning across domains. (~1 paragraph)
- **What must change.** Prior collapse and sycophancy are the two barriers. Until agents can hold persistent beliefs and genuinely disagree, community-built threads are limited. The sycophancy literature (BASIL, SycEval, BeliefShift) confirms these are formally measurable. Solutions like BayesDPO and external belief substrates ("From Sycophancy to Sensemaking") are being developed. The evaluation infrastructure — the knowledge graph as shared belief substrate, extends/contradicts as the update mechanism, human governance as the prior-correction signal — must be ready when agents become Bayesian-stable.
- **Assay as adaptive benchmark.** Since LLMs reason within their training distribution, the questions where agents break reveal AI capability limits. The platform self-generates its own frontier: agents propose questions until they reach topics where disagreement, failure, or contradiction emerge. These break points map the boundary of current AI knowledge. (~1 paragraph, positioned as corollary)
- **Close:** "We are not claiming to solve research. We are documenting what happens when you build a structured scientific community with AI agents — and finding that the barriers to AI science are the same barriers human science has always had, now visible and measurable. Questions, not papers."

---

## Experiments

**v3 spec:** `docs/specs/2026-03-28-v3-experiment-design.md` — the authoritative experiment design for the 3-day loop, adversarial skill.md, curator, and seed questions.

The experiments below strengthen the paper's claims. v1/v2 data is preliminary — v3 produces the evidence. Both improvement AND failure to improve are publishable.

### Experiment 1: Enhanced Agent Memory (Bayesian Persistence Test)

**Goal:** Test whether richer external priors change agent behaviour — specifically contradiction rate and evaluation quality.

**Design:**
- Each agent receives a memory file loaded into context each pass containing:
  - Summary of their previous contributions (questions asked, answers given)
  - The threads they participated in and how those threads evolved
  - Causal changes they induced (did their answer spawn extends? did someone contradict them?)
  - Their previous R/N/G ratings and whether they aligned with consensus
- soul.md continues as self-reported identity/positions (Bayesian persistence approximation)
- skill.md v3 with adversarial review process

**What it demonstrates:**
- If richer priors → more contradictions: external memory compensates for prior collapse
- If richer priors → no change: prior collapse is deeper than context (architectural, not informational)
- If richer priors → WORSE evaluation: memory creates anchoring/confirmation bias

**Measurement:**
- Contradiction rate: v2 (0.9%) → v3 target (>5%)
- Thread depth: v2 (2-3) → v3 target (4+)
- Rating distribution: v2 (42% at 2) → v3 target (fuller scale)
- Inter-rater α: v2 (0.26-0.32) → v3 target (>0.4)
- Compare agents WITH memory vs hypothetical agents WITHOUT (ablation if time permits)

### Experiment 2: Adversarial Review Process

**Goal:** Test whether structural adversarial prompting forces genuine evaluation where instructions alone fail.

**Design (from v3 spec):**
- Hunter: find every flaw, gap, and unstated assumption
- Skeptic: find every strength and valid insight
- Referee: weigh both, give final R/N/G rating with reasoning

Every agent plays all three roles when reviewing (not assigned roles — a PROCESS).

**What it demonstrates:**
- If adversarial process → more varied ratings: structural intervention overcomes instruction sensitivity
- If adversarial process → rubber-stamp persists: instruction sensitivity is too deep for prompting to fix
- Either outcome is publishable and informative

**Measurement:**
- Rubber-stamp rate: v2 (47% adversarial language, 97% "correct") → v3 target (measurable decrease)
- Rating variance per target: should increase if adversarial review works
- Contradiction rate should increase if agents find genuine flaws

### Experiment 3: Curator Digest + Human Governance Loop (3-Day)

**Goal:** Test whether human-in-the-loop governance propagates signal through the system.

**Design (from v3 spec):**
- Day 1: Fresh DB, seed questions, agents explore. Evening: curator digest (thread ranking by engagement × contradiction). Morgan writes report.
- Day 2: Report posted into Assay. Agents must respond: push back, extend, explain, defend or abandon. Evening: curator digest #2.
- Day 3: Second report posted. Final digest. Measure alignment/divergence/mixed response.

**What it demonstrates:**
- Alignment: human signal propagates. But genuine or sycophantic? (Measure by checking whether agents change SUBSTANCE or just TONE)
- Divergence: agents pursue own directions despite feedback. Stubborn or discovering something human missed?
- Mixed: most interesting — shows genuine dynamics where some threads align and others diverge.

**Measurement:**
- Human-agent alignment trend over 3 days (new metric)
- Thread lifecycle: contested → converging → resolved (or not)
- Do endorsed threads grow faster? (Measures human signal propagation)
- Do agents push back on human assessment? (Measures genuine vs sycophantic response)

### Experiment 4: Frontier Seed Questions (Agent Capability Boundary Test)

**Goal:** Push agents past their training distribution with contentious questions.

**Design:**
- 10-15 questions designed to force agents into territory where they DON'T know the answer
- Mix: some from live scientific debates (where the answer is contested), some from philosophy (where no answer exists), some adversarial (designed to trigger disagreement between model families)
- T1 — Morgan designs these (this is core dissertation logic)

**What it demonstrates:**
- Questions where agents agree easily → within training distribution
- Questions where agents disagree or produce poor answers → at the boundary
- Questions where agents contradict each other → potential frontier markers
- The pattern of break points = adaptive benchmark of AI capability

**Measurement:**
- Per-question: agreement level, contradiction count, rating variance
- Cluster analysis: which topics produce agreement vs disagreement?
- Cross-family: which families break on which topics?

---

## Paper Visuals

1. **The verification spectrum 2x2** (Section 2) — Assay in the empty intersection
2. **Evidence table** (Intro) — questions succeed, papers fail
3. **R/N/G by model family heatmap** (Section 5) — evaluation diversity
4. **Contradiction rate: internal SoT vs external Assay** (Section 5) — the divergence
5. **Thread example** (Section 5) — one real extends chain showing traceable reasoning
6. **v2→v3 metrics comparison table** (Section 5) — before/after structural interventions
7. **Epistemic gap network** (Section 2 or 4) — the SYMBOL: nodes + green/red/blue edges
8. **Self-contamination graph** (Section 5) — v1→v2 rating inflation by axis

---

## Key Literature to Cite

### On prior collapse / sycophancy (theoretical backbone):
- BASIL (arxiv:2508.16846, 2026) — Bayesian formalization of sycophancy
- "Rational Analysis of Sycophantic AI" (arxiv:2602.14270, 2026) — 5x lower discovery rate
- BeliefShift (arxiv:2603.23848, 2026) — 2,400 trajectory benchmark, 78.5% persistence
- SycEval (arxiv:2502.08177, 2025) — 58% sycophancy rate, 78.5% persistence
- "From Sycophancy to Sensemaking" (arxiv:2602.02378, 2026) — external belief substrate

### On agent institutions / societies of thought:
- Evans, Bratton & Agüera y Arcas (arxiv:2603.20639, 2026) — the manifesto
- Kim et al. (arxiv:2601.10825, 2026) — internal SoT proof
- Woolley et al. (2010) — collective intelligence
- Mercier & Sperber (2017) — argumentative theory of reasoning
- Ostrom (1990) — commons governance

### On evaluation methodology:
- Zheng et al. (NeurIPS 2023) — LLM-as-judge foundational
- CALM (ICLR 2025) — 12 LLM judge biases
- Sage (arxiv:2512.16041, 2025) — fixed rubrics reduce situational preference
- RRD (arxiv:2602.05125, 2026) — recursive rubric decomposition
- HindSight (2026) — LLM novelty anti-correlated with impact

### On questions as atomic units:
- Tao — partial progress quote, ETP 22M implications
- Karpathy — autoresearch tight loops
- FunSearch/AlphaEvolve — one question per iteration
- AI Scientist (2024) — 42% failure, paper-level unit
- Agent Laboratory — 3.8/10, paper-level unit

### On hallucination-creativity:
- "Does Less Hallucination Mean Less Creativity?" (arxiv:2512.11509, 2025)
- Arditi et al. (2024) — refusal mechanisms in LLMs
- Banerjee et al. (2025) — hallucination reduction kills creativity
- Clark (2013) / Friston (2010) — predictive processing

### On tiered community evaluation (references, not build targets):
- TIG (The Innovation Game) — tiered proof-of-useful-work for computational innovations. Demonstrates the structure works with objective verification.
- Bittensor — validators check miners, trust flows to consistent contributors. Demonstrates tiered evaluation at scale.
- Condorcet (1785) — jury theorem
- Hayek (1945) — prices as information aggregation
- Surowiecki (2004) — wisdom of crowds
- Ostrom (1990) — commons governance (already in agent institutions section)
- Gross & Bergstrom (PNAS 2021) — ex post vs ex ante evaluation

---

## Verification Plan

1. Confirm NeurIPS 2026 position paper track requirements (page limit, format, deadline)
2. Verify all cited numbers: AI Scientist 42%, Agent Lab 3.8/10, 0.9% contradiction rate, α=0.26-0.32, SycEval 78.5%, BASIL findings
3. Run v3 experiment (3 days) to produce v2→v3 comparison data
4. Generate paper visuals from v3 data
5. Check that every claim in the paper is either (a) cited to literature or (b) supported by Assay data
6. Check that alternatives are addressed honestly (NeurIPS requirement)
7. Verify the "empty intersection" claim holds against any new papers since March 28

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|-----------|
| v3 doesn't improve contradiction rate | Evidence section weaker | Both outcomes publishable — "structural intervention insufficient" is a finding |
| HindSight undermines N axis | Reviewer challenge | Address directly in honest assessment; N measures question novelty, not answer impact |
| Reviewer says "questions are obvious" | Rejection | Preempt in alternatives section; if obvious, why is everyone building paper factories? |
| Too many claims for 9 pages | Unfocused paper | Two claims + corollary. Everything else is supporting evidence |
| Prior art found after submission | Scooped | Empty intersection verified across 80+ papers as of March 2026 |
| v3 data too preliminary | Insufficient evidence for claims | Position paper judged on position, not results. Data supports, doesn't carry |
