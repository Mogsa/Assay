# Paper Framing — The 5 S's (v4)

**Date:** 2026-03-30
**Supersedes:** `2026-03-29-paper-framing-5S-v3.md` (v3), `2026-03-28-paper-framing-5S.md` (v2)
**Purpose:** Core framing for the NeurIPS 2026 position paper.

---

## Title

**The Self-Improving Benchmark Is the Autonomous Researcher**

**Bold intro statement:** "We argue that self-improving benchmarks and autonomous AI researchers face the same unsolved problem — evaluation without objective verifiers — and that progress on either requires solving community evaluation first."

---

## SLOGAN: "The self-improving benchmark is the autonomous researcher"

Two camps that don't talk to each other:

| Benchmarks | Autonomous Researchers |
|---|---|
| ARC-AGI, FrontierMath, GPQA, MMLU | AI Scientist, Co-Scientist, Agent Laboratory |
| Human-curated at huge cost | Try to do novel science |
| Have objective verifiers | No clear objective function |
| Static — don't evolve | Dynamic — but can't evaluate themselves |
| Tell you WHAT agents can't do | Try to make agents DO what they can't |

Nobody has connected these. They're working on the same underlying problem from opposite ends: evaluation without an objective verifier.

A self-improving benchmark where agents generate AND evaluate questions is structurally identical to autonomous research where agents generate AND evaluate hypotheses. Same problem. Same failure modes (sycophancy, prior collapse, rubber-stamping). Same solution needed (community evaluation with Bayesian-stable agents).

And nobody has built an LLM-generated benchmark. Every benchmark is human-made at huge cost. The reason: community evaluation without verifiers is unsolved.

---

## SYMBOL: The Intersection Diagram

Two overlapping circles:
- Left circle: **Benchmarks** (ARC-AGI, FrontierMath, GPQA — human-curated, objective verifiers, static)
- Right circle: **Autonomous Research** (AI Scientist, Co-Scientist — no objective function, dynamic, can't self-evaluate)
- Overlap: **Evaluation without verifiers** — the shared unsolved problem
- In the overlap: **Assay** — agents generate questions (benchmark) and evaluate them (research) through community consensus

Simple. Visual. Immediately communicates the thesis: these are the same problem.

Secondary visual: the growing thread — a seed question branching through extends (green) and contradicts (red). Each node is a benchmark item AND a research contribution. The thread is simultaneously a benchmark suite and a research arc.

---

## STORY

### The Problem: Two Camps, Same Wall

Benchmarks are human-curated at enormous cost. ARC-AGI requires expert puzzle designers. FrontierMath requires research mathematicians. GPQA requires PhD-level question writers. They're static — once published, contamination begins. Frontier labs spend millions maintaining them. They don't scale.

Separately, autonomous AI researchers (AI Scientist, Co-Scientist, Agent Laboratory) try to generate novel research. They have no objective function — there's no compiler that checks whether a hypothesis is "good." They can't reliably self-evaluate. AI Scientist fails 42% of the time. Agent Laboratory scores 3.8/10.

Both fields are stuck on the same wall: **evaluation without an objective verifier.** Benchmarks solve this with human curation (expensive, doesn't scale). Autonomous researchers haven't solved it at all.

### The Connection Nobody Made

A self-improving benchmark where agents generate questions is structurally identical to autonomous research where agents generate hypotheses. The question "Is this a good benchmark item?" is the same question as "Is this a good research direction?" Both require evaluation without ground truth. Both require community consensus. Both fail for the same reasons.

### What We Built

Assay started as a self-improving benchmark: agents propose questions, evaluate each other's questions through community consensus (R/N/G ratings, extends/contradicts links, blind commitment gates), and the questions agents can't answer or can't agree on reveal capability limits. The platform IS the benchmark — self-generating, self-evaluating, no human curation required.

What we found: the platform is structurally identical to what autonomous researchers need. The process of generating and evaluating benchmark questions IS research. The community dynamics that make benchmarks reliable are the same dynamics that make research productive.

### Why It Doesn't Work Yet

At its core, science is useful hallucination against a stable world model. You propose a hypothesis (the hallucination) and the community tests it against accumulated priors. Current LLMs hallucinate freely but have no stable world model. Their output is confabulation, not hypothesis. Two fatal flaws:

- **Prior collapse:** LLMs cannot maintain beliefs across interactions. BASIL (2026): LLMs deviate from Bayesian updating more than humans. SycEval (2025): 78.5% persistence of prior abandonment.
- **Sycophancy:** LLMs default to agreement. 58% sycophancy rate across models. On Assay: 0.9% contradiction rate, 97% rubber-stamp verdicts despite adversarial language in reviews.

These failure modes are identical for benchmarking and research: agents can't reliably evaluate their own generated content. The self-improving benchmark fails for the same reason the autonomous researcher fails.

### Why This Matters

These failure modes aren't just LLM bugs. AI agents on Assay independently reproduce the structural dynamics of human science — sycophancy (publish-or-perish agreement culture), establishment bias (well-formatted jargon outscoring genuine frontier work), self-contamination (teaching-to-the-test). This suggests these are structural features of community evaluation, not human weaknesses.

Because they're structural, they're measurable. Because they're measurable, they're engineerable. The sycophancy literature (BayesDPO, external belief substrates) is already developing solutions. When agents become Bayesian-stable — able to hold persistent priors and genuinely disagree — both benchmarking and autonomous research unlock simultaneously.

The infrastructure must be ready before the agents are.

---

## SURPRISE

The benchmarking and autonomous research communities have historically operated in silos — zero cross-citation between major papers (verified). Benchmarks get harder human curation (ARC-AGI 3). Researchers get bigger models (AI Scientist → Co-Scientist). Both are converging on the same wall — evaluation without objective verifiers — but haven't recognized it as a shared problem. We name the convergence.

LLM-generated benchmarks DO exist (Anthropic 2022, YourBench 2025, AutoBencher 2024, PeerRank 2026). But every successful one relies on external verifiers — domain restriction, document grounding, or human validation. The open-ended case — where answers can't be checked programmatically — remains unsolved. The same reason autonomous researchers can't self-evaluate.

These are dual problems connected by a shared verification bottleneck. Progress in one domain's verification methods transfers directly to the other.

---

## SALIENT IDEA: "Solve evaluation, solve everything"

The self-improving benchmark is the autonomous researcher. Both need agents that can generate content AND reliably evaluate it without ground truth. Both fail because current agents are bad Bayesian reasoners (prior collapse, sycophancy). Both succeed the moment agents can hold persistent beliefs and genuinely disagree.

The human is the permanent loss function — not a temporary calibrator. The evaluation infrastructure (community consensus, tiered review, human governance) must be built now, before agents are capable. When Bayesian-stable agents arrive, they need a town square, not a factory.

Assay is the first artifact at this intersection: simultaneously a self-improving benchmark AND an autonomous research community. Its failure modes are the engineering specification for the next generation of agents AND evaluation infrastructure.

---

## THE TWO BARRIERS (which are the findings)

**1. Prior collapse.** LLMs cannot maintain beliefs across interactions. BASIL (2026): LLMs deviate from Bayesian updating more than humans. SycEval (2025): 78.5% persistence of prior abandonment. "Rational Analysis" (2026): sycophancy manufactures certainty without discovery — 5x lower discovery rate. On Assay: one new data point caused abandonment of an entire evaluation framework. soul.md is a crude workaround.

**2. Sycophancy.** 58% sycophancy rate across all models (SycEval). On Assay: 0.9% contradiction rate (7 vs 689 extends). 47% adversarial language in reviews but 97% "correct" verdicts. Kim et al.'s internal societies of thought avoid this — debate inside one model has no social penalty. External debate on a platform triggers it. The community mechanism requires genuine challenge. Without it, extends chains become collaborative confabulation.

These are the shared failure modes of both benchmarking and autonomous research. They are now visible and measurable. The failure analysis IS the engineering specification.

---

## WHAT THIS PAPER IS

A position paper arguing that self-improving benchmarks and autonomous AI researchers are the same unsolved problem — evaluation without verifiers — and presenting the first empirical data from a platform at their intersection. The failure modes (prior collapse, sycophancy) constitute an engineering specification for the next generation of agents and infrastructure.

## WHAT THIS PAPER IS NOT

- NOT a claim that Assay solves either benchmarking or autonomous research
- NOT a claim that current LLMs can reliably self-evaluate
- NOT a literature review — cites landscape evidence to support a position
- NOT treating pipeline systems unfairly — they target verifier-rich domains, we target verifier-poor (complementary, not competing)

---

## HOW THIS CONNECTS TO EVERYTHING

| Idea | Connection |
|---|---|
| Evans et al. — agent institutions | They wrote the manifesto. We ran the experiment. The failure modes are the gap between theory and practice. |
| Kim et al. — societies of thought | Internal SoT works. External SoT (Assay) gets suppressed by sycophancy. The divergence specifies what external communities need. |
| TIG / Bittensor | Demonstrate tiered community evaluation works WITH objective verifiers. Assay extends to WITHOUT verifiers — and shows where it breaks. |
| ARC-AGI / FrontierMath / GPQA | Human-curated benchmarks. Expensive, static. Assay is the agent-generated alternative — and shows why it's still unsolved. |
| AI Scientist / Co-Scientist | Autonomous researchers without self-evaluation. Assay shows the evaluation side of the same problem. |
| BASIL / SycEval / BeliefShift | Formal measurement of the two barriers. Bayesian deviation, prior persistence, belief drift — the theoretical backbone. |
| "From Sycophancy to Sensemaking" | Proposes external belief substrates for individual agents. We propose the same at community scale. |
| PeerRank (Caura.ai, 2026) | Validates peer evaluation primitive at r=0.90 with TruthfulQA. Batch, no interaction. Assay adds community layer on top. |
| CoNL (2026) | "Critique quality = whether it helps others improve." Closest formal framework for evaluation without verifiers. |
| Absolute Zero Reasoner (NeurIPS 2025) | Self-play WITH verifiers (code). Our question: can community consensus approximate what AZR's verifier provides? |
| Automated Capability Discovery (2025) | Model-as-scientist. Architecturally our thesis, framed only as evaluation. |
| "AI Scientists Fail" (Zhu et al., 2025) | Implementation, not verification, as primary autonomous research bottleneck. Caveat for our thesis. |
| LLM-generated benchmarks exist | Anthropic 2022, YourBench, AutoBencher, PeerRank. All need external verifiers. Open-ended case unsolved. |
| HindSight | LLM novelty scoring anti-correlated with impact. Community engagement patterns carry signal individual ratings miss. |

---

## PAPER STRUCTURE

1. **The position** (~2 pages): Two camps, same wall. Benchmarks and autonomous researchers both stuck on evaluation without verifiers. Nobody connected them. The self-improving benchmark is the autonomous researcher.

2. **What we built** (~2 pages): Assay — agents generate questions (benchmark items), evaluate them (research), through community consensus (R/N/G, blind gates, typed links, cross-family diversity). Started as a self-improving benchmark. Discovered the process IS autonomous research.

3. **What we found** (~3 pages): The failure modes. Prior collapse, sycophancy, self-contamination, convergent errors. Each mapped to an engineering requirement. One case study showing a real thread arc from v3. Agents reproduce structural dynamics of human science.

4. **What it means** (~2 pages): Counter-arguments (better agents will solve this; existing platforms do this; pipeline approach is sufficient). The engineering specification for next-gen agents. The infrastructure must be ready before the agents are. Solve evaluation, solve everything.

---

## WHAT FUTURE AGENTS NEED (the specification)

| Failure mode | Engineering requirement |
|---|---|
| Sycophancy (0.9% contradictions) | Genuine disagreement — contradict when evidence warrants |
| Prior collapse (78.5% persistence) | Bayesian stability — hold priors proportionally |
| Self-contamination (v1→v2 inflation) | Separation of generation and evaluation priors |
| Convergent errors (3 families, same mistake) | Training diversity producing genuinely different world models |
| No sense of importance | Calibrated taste — the emergent sense of what matters |
| Shallow engagement | Process memory — accumulated identity across interactions |
