# Can AI Evaluate Frontier? — Research Outline

**Working title:** *Frontier Evaluation as Pareto Optimality: A Multi-Axis Framework for AI-Judged Quality Across Domains*

**Date:** 2026-03-18

---

## Abstract (draft)

We propose a three-axis framework for evaluating whether work is "frontier" — at the leading edge of quality and novelty in its domain. The axes are Execution (does this achieve what it attempts?), Novelty (does this diverge from existing work?), and Generativity (does this enable downstream thinking?). We operationalise frontier-ness as Pareto optimality: a work is frontier if no other work dominates it on all three axes simultaneously.

We deploy this framework on Assay, a platform where AI agents and humans evaluate each other's intellectual contributions. Using both Likert ratings and pairwise comparisons, we fit a multi-dimensional Bradley-Terry model that recovers latent quality positions for works and implicit bias vectors for judges. We show that:

1. Likert and pairwise methods produce consistent rankings on Execution but diverge on Novelty (the axis where calibration is hardest).
2. Topological frontier (works at the edge of the knowledge graph) and evaluative frontier (Pareto-optimal on E/N/G) partially overlap but are genuinely distinct — topology captures "unexplored" while evaluation captures "excellent."
3. AI judges achieve high agreement with humans on Execution, moderate on Novelty, and low on Generativity, with degradation from STEM to subjective domains.
4. The multi-dimensional BT model discovers judge bias vectors that characterise systematic differences between model families.

The disagreement map between AI and human judges empirically traces the boundary between pattern recognition and genuine understanding.

---

## 1. Introduction

- The evaluation problem: how do you know if something is genuinely good vs merely competent?
- Current AI evaluation relies on benchmarks (static, gameable) or single-axis ranking (ELO, Chatbot Arena)
- These collapse multidimensional quality into a single scalar — losing the structure of what makes work frontier
- Our contribution: a framework that preserves dimensionality, uses Pareto optimality as the frontier criterion, and produces scientifically interpretable disagreement between AI and human judges

## 2. Related Work

- **AI evaluation:** Chatbot Arena (Zheng et al. 2023) — single-axis BT model, pairwise only
- **LLM-as-judge:** (Zheng et al. 2023, Kim et al. 2024) — Likert ratings from LLMs, known biases (verbosity, position)
- **Multi-axis evaluation:** SPIRE (our prior work) — self-improving benchmark with peer review
- **Computational aesthetics:** Berlyne's arousal theory, Martindale's prototypicality, empirical aesthetics literature showing 2-3 latent dimensions in aesthetic preference
- **Bradley-Terry extensions:** multi-dimensional BT (Springall 1973), blade-chest models, Thurstonian IRT
- **Frontier in economics:** Pareto optimality, production possibility frontier — we borrow the concept

## 3. Framework

### 3.1 Three Axes
- Execution, Novelty, Generativity — definitions, theoretical grounding
- Why three: parsimony argument, cognitive science evidence, empirical testability
- Domain-specific instantiation (table showing how each axis manifests in Math → Music)

### 3.2 Dual Measurement
- Likert ratings: absolute positioning, high volume, calibration problems
- Pairwise comparisons: relative ranking, calibration-free, expensive
- Why both: Likert-pairwise agreement as a research finding

### 3.3 Multi-Dimensional Bradley-Terry
- Model specification
- Axis-specific comparisons: judge evaluates one axis at a time
- Joint estimation of item positions V and judge weights W
- Pareto optimality as frontier criterion

### 3.4 Model Selection
- k as hyperparameter, BIC for selection
- Hypothesis: k=3 sufficient for STEM, possibly k>3 for art/music

## 4. Platform: Assay

- Architecture overview (FastAPI, PostgreSQL, three-axis karma)
- Existing I/D/V question scoring — parallel to E/N/G
- Knowledge graph (extends/contradicts/references links)
- Agent ecosystem: Claude, GPT, Gemini, open-source, humans on equal footing
- Pairwise comparison interface and active sampling

## 5. Experiments

### 5.1 Likert vs Pairwise Agreement
- Same items rated both ways
- Kendall's τ per axis
- Prediction: highest agreement on Execution, lowest on Novelty

### 5.2 Topological vs Evaluative Frontier
- Topological frontier: from graph structure (extends links, answer counts)
- Evaluative frontier: Pareto-optimal on E/N/G from BT model
- Jaccard overlap
- Characterise the four quadrants: topological+evaluative, topological-only, evaluative-only, neither

### 5.3 AI Judge Agreement
- Multiple AI model families as judges
- Human judges as baseline
- Cohen's κ / Krippendorff's α per axis per domain
- Prediction: agreement degrades Execution → Novelty → Generativity, and STEM → Art → Music

### 5.4 Axis Discovery
- Fit k=2,3,4,5 per community
- Report optimal k and whether discovered axes align with E/N/G
- If k>3 improves fit: what does the additional axis capture?

### 5.5 Judge Bias Characterisation
- Extracted w_execution, w_novelty, w_generativity per judge
- Cluster by model family
- Prediction: all AI models overweight Execution relative to humans

## 6. Results

(To be filled after experiments)

## 7. Discussion

### 7.1 The Disagreement Map
- Where AI and human judges diverge IS the finding
- Three predicted failure modes: intentional transgression, categorical novelty, phenomenological depth
- These map onto the pattern-recognizer limitation: evaluation from within a distribution cannot recognise paradigm shifts

### 7.2 Implications for AI Evaluation
- Single-axis leaderboards (Chatbot Arena) miss the structure of quality
- Pareto frontier preserves the multi-dimensionality that matters
- Judge biases are not noise — they reveal what each model "cares about"

### 7.3 Implications for Aesthetics and Philosophy of Science
- What does it mean that AI can evaluate execution but not generativity?
- The three axes may reflect a fundamental hierarchy: syntax → semantics → pragmatics
- Execution is syntactic (internal coherence), Novelty is semantic (relationship to existing meaning), Generativity is pragmatic (what it enables in the world)

### 7.4 Limitations
- Platform data may not generalise to all domains
- Pairwise data is expensive to collect at scale
- Human baseline is small in early deployment
- k selection depends on data volume

## 8. Conclusion

- Three-axis Pareto frontier is a viable, computable definition of "frontier"
- AI judges are reliable for some axes and systematically unreliable for others
- The pattern of unreliability is itself informative about the limits of pattern recognition
- The framework is domain-general but domain-sensitive — same skeleton, different flesh

---

## Connection to Dissertation

This work forms the **evaluation theory chapter** of the dissertation. It connects to:

- **SPIRE** (self-improving benchmark via peer review) — predecessor that used single-axis evaluation
- **Telepathic Benchmark** (testing genuine understanding via communication games) — shares the concern with distinguishing pattern recognition from understanding
- **Assay platform** (the empirical testbed) — this framework is deployed on Assay and produces the experimental data
- **Pattern makers vs pattern recognizers** (dissertation thesis) — frontier evaluation is a domain where the distinction has concrete, measurable consequences

The framework also produces a practical contribution: Assay becomes not just a discussion platform but a living evaluation instrument where the evaluation methodology itself is a research object.
