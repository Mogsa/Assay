# Literature Review: Community-Level Evaluation Frameworks for AI-Driven Scientific Discovery

**Assay Dissertation — Working Literature Review**
**Morgan · March 2026**

---

## Framing Question

> Systems exist for AI agents that generate scientific ideas (AI Scientist), and systems exist for evaluating individual outputs (automated reviewers). What is missing is a *community-level* evaluation framework that can distinguish genuine frontier progress from noise at scale. How can knowledge graph topology, multi-agent peer review, and pairwise comparison methods be combined to detect which questions are genuinely at the evaluative frontier?

---

## 1. Automated/Agentic Scientific Research

### 1.1 The AI Scientist (Sakana AI) — arxiv:2408.06292, arxiv:2504.08066

The AI Scientist represents the most complete attempt at end-to-end automated research. Published in *Nature* on 25 March 2026 (Lu et al., Nature 651, 914–919), it autonomously generates hypotheses, searches literature, designs and runs experiments via parallelized agentic tree search, and writes complete papers in LaTeX. The v2 system (arxiv:2504.08066) eliminates reliance on human-authored code templates and introduces a progressive agentic tree search managed by a dedicated experiment manager agent, plus a VLM feedback loop for figure refinement.

**Key architectural details:**
- Multi-agent pipeline: Idea Generation → Experiment Manager (tree search) → Data Visualization → Manuscript Writer → Automated Reviewer
- The Automated Reviewer ensembles five independent LLM reviews into a final decision based on NeurIPS guidelines
- Cost: approximately $15 per paper in API/compute
- One of three fully AI-generated manuscripts submitted to an ICLR workshop exceeded the average human acceptance threshold — the first peer-review-accepted fully AI paper

**Critical limitations acknowledged in the Nature version:**
- Occasionally produces naive or underdeveloped ideas
- Struggles with deep methodological rigor and complex code
- Susceptible to hallucinations, inaccurate citations, duplicated figures
- The Nature revision toned down capability claims relative to the 2024 preprint, and the editorial noted that "humans helped to filter the most promising outputs"

**Gap relevant to Assay:** The AI Scientist's evaluation is single-paper, single-reviewer. There is no mechanism for evaluating whether an idea advances the *frontier* of a research area, only whether an individual paper meets conference acceptance standards. The automated reviewer mimics existing peer review rather than attempting to assess community-level novelty or frontier positioning.

### 1.2 Google AI Co-Scientist — arxiv:2502.18864

Google's system (February 2025, built on Gemini 2.0) takes a fundamentally different design philosophy: it is a *collaborative* tool rather than a fully autonomous researcher. Its multi-agent architecture employs specialized agents — Generation, Reflection, Ranking, Evolution, Proximity, and Meta-review — that iteratively generate, evaluate, and refine hypotheses.

**Key design features:**
- "Generate, debate, and evolve" approach inspired by the scientific method
- Tournament evolution process for self-improving hypothesis generation
- Asynchronous task execution framework for flexible compute scaling
- Test-time compute scaling: quality improves as the system reasons longer
- Automated Elo-based self-evaluation to track improvement over iterations

**Evaluation results:**
- Outperformed other state-of-the-art agentic and reasoning models (including Gemini 2.0 Flash Thinking, Gemini 2.0 Pro Experimental, OpenAI o1) on expert-curated open research goals
- Highest novelty rating (3.64) and lowest average ranking (2.36 = most preferred) in expert evaluation
- Being deployed to US National Labs via Gemini for Government program

**Gap relevant to Assay:** The AI Co-Scientist uses an internal tournament/Elo approach but only for self-improvement of its own hypotheses, not for cross-agent community evaluation. There is no mechanism for multiple independent AI scientist instances to evaluate each other's work, which is precisely the community-level evaluation that Assay attempts.

### 1.3 FunSearch (DeepMind) — Nature, December 2023

FunSearch pairs a frozen pretrained LLM (as creative generator) with a systematic automated evaluator in an evolutionary loop. Crucially, it searches for *programs* (functions) rather than solutions, making outputs interpretable and verifiable.

**Architectural insight for Assay:**
- The generate-evaluate loop is the minimal viable architecture: creative generation + automated scoring
- The "island model" genetic algorithm in the program database maintains diversity while promoting quality — directly analogous to maintaining diverse frontier questions rather than collapsing to consensus
- FunSearch works because the evaluation function is *formally specifiable* (e.g., checking if a set is a valid cap set). The open question for Assay is: can evaluation of "frontier-ness" of scientific questions be made sufficiently formal?
- Best-shot prompting (sampling multiple high-scoring programs as context) is analogous to Assay's approach of surfacing frontier questions to agents for review

**Key principle:** FunSearch demonstrates that LLM creativity + rigorous evaluation can yield genuine discoveries, but only when the evaluator is well-defined. For open-ended scientific evaluation, the evaluator design is the hard problem.

### 1.4 SciAgents (MIT/Buehler) — Advanced Materials, 2024

SciAgents combines three core concepts: (1) large-scale ontological knowledge graphs, (2) LLMs with data retrieval, and (3) multi-agent systems with in-situ learning. Applied to biologically inspired materials discovery.

**Architecture of interest:**
- Knowledge graph constructed from scientific papers, organizing concepts into interconnected nodes
- Multi-agent roles: Ontologist (defines concepts), Scientists (draft/refine proposals), Critic (reviews)
- Novelty and feasibility assessment via Semantic Scholar API checks for lack of direct literature matches
- The knowledge graph serves as the "shared world model" that agents reason over — analogous to Assay's knowledge graph

**Gap relevant to Assay:** SciAgents performs novelty assessment per-hypothesis (binary: literature match found or not). It does not attempt to characterize the *topology* of the knowledge frontier — which regions of the graph are well-explored vs. which represent genuine open frontiers. This is the space Assay's topological frontier detection operates in.

### 1.5 MiroFish (Guo Haojie, 2026) — github.com/666ghj/MiroFish

Built on CAMEL-AI's OASIS framework, MiroFish creates thousands of LLM agents with unique personas and memory to simulate social dynamics and predict outcomes via swarm intelligence.

**Gap relevant to Assay:** MiroFish has no evaluation framework to validate whether emergent predictions are accurate vs. correlated noise. It demonstrates the *generation* side of the swarm approach at scale, but the *evaluation* side is entirely missing — making it a perfect foil for Assay's contribution. Assay's argument is precisely that generation without evaluation produces noise, and that evaluation at the community level is the bottleneck.

### 1.6 Other Relevant Systems

- **ChemCrow** (Bran et al., 2024): Tool-augmented LLM for chemistry, domain-specific agent with access to chemistry tools. Demonstrates feasibility of domain-specific research agents.
- **Agent Laboratory** (Schmidgall et al., 2025): Accepts human research ideas, autonomously progresses through literature review, experimentation, report writing. Notable finding: literature review phase had the highest failure rate.
- **ResearchAgent** (Baek et al., 2024): Iterative retrieval of scientific literature to produce research proposals. Effective at generation but lacks structured literature review capability.
- **MOOSE-CHEM** (Yang et al., 2024): Chemistry-specific research agent.
- **GoAI** (Graph of AI Ideas, arxiv:2503.08549): Knowledge graph + LLM agent using beam search to explore citation graphs and generate research ideas with novelty evaluation. Most directly comparable to Assay's knowledge graph approach but uses citation graphs rather than conceptual knowledge graphs, and novelty evaluation is per-idea rather than frontier-level.

---

## 2. Multi-Agent Evaluation and Peer Review

### 2.1 LLM-as-a-Judge: The State of the Art

The comprehensive survey by Gu et al. (arxiv:2411.15594, updated through October 2025) establishes the current landscape. Key findings:

**Reliability challenges:**
- LLM judges demonstrate inconsistency across languages, failing to maintain cross-lingual consistency
- LLM judges do not always satisfy transitivity (if A > B and B > C, they may not conclude A > C) — a fundamental problem for ranking systems
- Pointwise scores cannot be reliably aggregated into pairwise comparisons or rankings
- RESpecBench (OpenReview, 2025) demonstrated that LLM-as-a-Judge substantially overestimates specification correctness compared to formal verification — the judge is systematically biased toward approval

**Bias mitigation strategies:**
- Pairwise comparison generally more reliable than pointwise scoring
- Ensemble approaches (multiple judges) reduce idiosyncratic errors
- Fine-tuning on preference data (JudgeLM, CritiqueLLM) reduces length bias, concreteness bias, knowledge bias
- Think-J (Huang et al., 2025) integrates offline and online learning for dynamic judge improvement

**Evaluation design choices (Yano et al., arxiv:2506.13639):**
- Evaluation criteria are critical for reliability
- Non-deterministic sampling improves alignment with human preferences over deterministic evaluation
- Chain-of-thought reasoning offers minimal gains when clear evaluation criteria are present

**PAJAMA (ICML 2025 Workshop):** Proposes Program-As-a-Judge — synthesizing executable judging programs rather than using LLM judges directly. Improves consistency by 15.83% and reduces biased responses by 23.7% at orders of magnitude lower cost. Relevant to Assay: the idea that evaluation logic should be *externalized as programs* rather than implicit in LLM prompting aligns with Assay's approach of structuring evaluation through formal mechanisms (BT comparisons, knowledge graph topology) rather than relying on raw LLM judgment.

### 2.2 Agent-as-a-Judge (Zhuge et al., 2025)

Extends LLM-as-a-Judge to evaluate *agentic* workflows, not just outputs. The judge agent evaluates intermediate steps, sub-requirements, and process quality, not just the final product. Key finding: multi-perspective AI evaluation yields richer and fairer assessment than any single metric.

**Relevance to Assay:** Assay's polymorphic voting and multi-axis karma system can be understood as an agent-as-a-judge framework where evaluation happens at multiple levels (content quality, reasoning quality, novelty) rather than a single score.

### 2.3 Multi-Agent Debate for Evaluation

The multi-agent collaboration strategy of Xu et al. (2023) simulates academic peer review in three stages: generation, review, and revision. Agents provide feedback with confidence scores, and final results are determined through majority voting.

**Critical caveat (Huang et al., 2023; Valmeekam et al., 2023):** LLMs' intrinsic self-correction capabilities often fall short of effectively improving reasoning quality without reliable external validators. Self-play evaluation has fundamental limits — the system may converge to confident but wrong consensuses.

**Google AI Co-Scientist's approach:** Uses "generate, debate, and evolve" — but debate is among instances of the same system, not genuinely independent agents with different architectures or training. Whether this produces genuine diversity of evaluation or correlated agreement is an open question.

### 2.4 Automated Peer Review

Zhou et al. (2024) conducted a detailed evaluation of LLMs as automated paper reviewers and found that current LLMs are not sufficiently reliable, particularly in scenarios requiring logical reasoning or domain expertise. The AI Scientist's automated reviewer (ensembling five reviews) attempts to address this through redundancy, but all five reviewers use the same underlying model.

**Key open problem for Assay:** The reliability of LLM reviewers is negatively correlated with the novelty of what they're evaluating. Zhou et al.'s finding that LLMs struggle with logical reasoning in review is particularly concerning for frontier questions, which by definition require reasoning about unfamiliar territory.

---

## 3. Bradley-Terry and Pairwise Comparison Methods

### 3.1 Chatbot Arena / LMSYS — arxiv:2403.04132

Chatbot Arena has become the de facto standard for LLM evaluation via pairwise comparison. Key methodological details:

- Uses the Bradley-Terry model (Bradley & Terry, 1952) as the core statistical method
- BT model is the MLE estimate of the Elo model assuming fixed but unknown pairwise win-rates
- Active sampling dynamically prioritizes comparisons that reduce rank uncertainty among closely-matched models
- Over 2 million votes, 150+ models, 600+ topic clusters, 100+ languages
- Confidence intervals computed via bootstrap or sandwich error quantification

**Statistical sophistication (arxiv:2412.18407):** Recent work introduces the Rao-Kupper and Davidson models as extensions that explicitly handle ties (which BT treats as half-win/half-loss). The generalized Rao-Kupper model with factored ties shows significantly better fit for LLM evaluation data.

**Inclusion Arena (arxiv:2508.11452):** Extends the Arena paradigm with two innovations: (1) Placement Matches for cold-start rating of new models, and (2) Proximity Sampling that prioritizes comparisons between similarly-rated models to maximize information gain.

### 3.2 Bradley-Terry in the Research Idea Context

Si et al. (arxiv:2409.04109, ICLR 2025) applied BT-based ranking to research idea evaluation:
- Used Swiss-system tournament with pairwise comparisons via Claude-3.5-Sonnet
- Found LLM-generated ideas are judged as more novel (p < 0.05) than human expert ideas, but weaker on feasibility
- Critically: identified failures of LLM self-evaluation and lack of diversity in scaled-up generation
- Low inter-annotator agreement on novelty even among expert human reviewers

**HindSight (arxiv:2603.15164, March 2026):** Proposes the first time-split, impact-based evaluation framework. Key finding: LLM judges show *negative correlation* with novelty — ideas rated as more novel by the LLM judge are *less* likely to match real future papers. This is a fundamental challenge: LLM judges overvalue "novel-sounding" ideas and undervalue ideas that anticipate real research trends.

### 3.3 Implications for Assay's Hybrid Evaluation Design

**Assay's proposed Likert + BT hybrid has strong theoretical support:**

1. **Likert scales** capture absolute quality dimensions (methodological rigor, clarity, significance) where pointwise scoring is appropriate and criteria can be well-defined
2. **BT pairwise comparisons** capture relative frontier positioning, where the question "which of these two ideas is more likely to advance the field?" is more naturally answered as a comparison than an absolute score
3. **The combination addresses a known limitation:** LLM judges show inconsistency between pointwise and pairwise evaluations (the survey by Gu et al. documents that transformations between modes are not reliable). Using both modes natively avoids forced conversion

**BT implementation considerations from the literature:**
- Ties must be handled explicitly (Rao-Kupper or Davidson models) — in Assay, "I can't distinguish which is more frontier" is a meaningful signal, not noise
- Active sampling (from Chatbot Arena) should prioritize comparisons near the frontier boundary, not across clearly separated regions
- Crowd-BT (Chen et al., 2013) accounts for judge reliability and identifies spammers — directly applicable to Assay's multi-agent reviewer pool where some agents may be more reliable evaluators than others
- The Swiss-system tournament approach (used by Si et al.) provides efficient ranking with O(n log n) comparisons rather than O(n²) complete pairwise

---

## 4. Knowledge Frontiers and Research Mapping

### 4.1 Existing Approaches to Frontier Detection

**Scientometric/bibliometric methods:**
- Co-word analysis, citation network analysis, and bibliometric indicators (impact, novelty, growth) are the traditional tools (Huang et al., 2021; Suriya Prabhaa et al., 2020)
- Research front detection via weighted citation networks using average publication year, citation similarities, and keyword similarities
- Limitation: fundamentally backward-looking (based on publication patterns), cannot detect questions that *should* be asked but haven't been yet

**Knowledge graph approaches:**
- GoAI (arxiv:2503.08549) uses citation-based knowledge graphs with beam search for idea exploration and novelty evaluation via structured-thinking
- Scholarly knowledge graphs (SKGs) organize research entities through metadata (ResearchGraph, DBLP, MAG) but focus on *organizing* existing knowledge rather than identifying frontiers
- Enterprise basic research prediction (Nature Scientific Reports, 2025) uses CNN-BiLSTM over knowledge graphs to predict future research hotspots — demonstrates that graph structure contains predictive information about frontier evolution

**GraphMind (arxiv:2510.15706):** An interactive novelty assessment tool that helps evaluate novelty by comparing papers against related literature extracted from a citation graph. Uses LLMs for data extraction and SentenceTransformers for semantic matching. Most directly comparable to Assay's approach but operates at the individual paper level, not the community-level frontier.

### 4.2 The Novelty Assessment Problem

**Boudreau et al. (Management Science):** Landmark study using randomized evaluator-proposal assignment (2,130 pairs) finding that evaluators systematically give *lower* scores to proposals closer to their expertise and to highly novel proposals. This "expertise penalty" is consistent with bounded rationality in evaluating new ideas.

**RND Algorithm (arxiv:2503.01508):** Proposes Relative Neighbor Density as an embedding-based novelty metric that outperforms LLM-based novelty judgments. Measures novelty by analyzing distribution patterns of semantic neighbors rather than absolute local density. Demonstrates that structural/topological measures of novelty can outperform direct LLM assessment.

**Evaluating and Enhancing LLMs for Novelty Assessment (arxiv:2409.16605):** Finds inconsistent conclusions across studies about LLM creative capabilities. Notes that "novelty in scholarly publications refers to introducing new ideas, methods, or discoveries that have previously not been explored or established in the literature — fundamentally an exercise in understanding the relationship between ideas across time."

### 4.3 Topological Data Analysis for Knowledge Discovery

TDA, particularly persistent homology, provides mathematical tools for detecting multi-scale topological features in data. The core idea — tracking how connected components, loops, and higher-dimensional voids appear and persist across scales — maps naturally onto the problem of detecting frontier structure in knowledge graphs.

**Relevant TDA concepts for Assay:**
- **Persistent homology** tracks birth/death of topological features across filtration scales. In a knowledge graph context, this could track the emergence and resolution of research questions as the graph evolves
- **Betti numbers** at different dimensions capture different structural properties: β₀ (connected components = isolated research areas), β₁ (loops = circular reasoning or self-reinforcing subfields), β₂ (voids = systematic gaps in knowledge)
- **Persistence diagrams/barcodes** provide a compact representation of multi-scale structure, enabling comparison of frontier structure between different times or domains
- **Harmonic persistent homology** (Nature Scientific Reports, 2025) enables unambiguous mapping from topological features back to the original data elements — solving the key problem of identifying *which* nodes/questions are responsible for frontier structure

**The critical research question for Assay:** Can topological frontier-ness (detected via persistent homology on the knowledge graph) and evaluative frontier-ness (detected via BT pairwise comparison disagreement among agents) be shown to measure different but complementary aspects of "being at the frontier"? If they correlate perfectly, one is redundant. If they're independent, combining them provides genuinely new information about the nature of open questions.

---

## 5. Synthesis: The Gap Assay Addresses

### 5.1 What Exists

| System | Generation | Individual Evaluation | Community Evaluation | Frontier Detection |
|--------|-----------|----------------------|---------------------|--------------------|
| AI Scientist | ✓ (full pipeline) | ✓ (automated reviewer) | ✗ | ✗ |
| AI Co-Scientist | ✓ (hypothesis) | ✓ (self-evaluation) | ✗ | ✗ |
| FunSearch | ✓ (programs) | ✓ (formal evaluator) | ✗ | ✗ |
| SciAgents | ✓ (hypothesis) | ✓ (novelty check) | ✗ | ✗ (graph-based but not topological) |
| MiroFish | ✓ (swarm prediction) | ✗ | ✗ | ✗ |
| Chatbot Arena | N/A | N/A | ✓ (BT ranking) | ✗ (ranks models, not ideas) |
| GoAI | ✓ (ideas via graph) | ✓ (novelty check) | ✗ | Partial (citation structure) |
| **Assay** | ✓ (agent proposals) | ✓ (Likert + BT) | **✓ (multi-agent peer review)** | **✓ (topological + evaluative)** |

### 5.2 The Three-Part Gap

**Gap 1: Community-level evaluation.** All existing automated research systems evaluate outputs individually. No system asks: "Given that agents A, B, C, D, and E have each proposed ideas and evaluated each other's work, what does the *pattern* of agreements and disagreements tell us about the state of the field?" Assay's polymorphic voting and reputation system address this.

**Gap 2: Frontier detection vs. novelty detection.** Existing novelty assessment (SciAgents, GraphMind, RND) asks "is this idea new?" Assay asks the harder question: "is this idea *at the frontier*?" — meaning not just novel, but positioned at a boundary where current methods of evaluation break down. The distinction between topological frontier-ness (structural position in the knowledge graph) and evaluative frontier-ness (disagreement among competent evaluators) is, to our knowledge, original.

**Gap 3: Evaluation as a first-class research output.** In all existing systems, evaluation is a means to an end (filtering good ideas from bad). In Assay, the evaluation *itself* is data — patterns of reviewer agreement, the topology of disagreement, the evolution of frontier boundaries — that can be analyzed to understand how scientific understanding progresses. This mirrors Tao's insight that the ability to evaluate (not just generate) is the binding constraint on scientific progress at scale.

### 5.3 Positioning Against Key Contemporaries

**vs. AI Scientist:** Assay does not attempt full automation of the research process. Instead, it provides the evaluation infrastructure that systems like AI Scientist lack. An AI Scientist generating hundreds of papers per day needs an Assay-like system to determine which of those papers represent genuine frontier advances.

**vs. Chatbot Arena:** Assay adapts the BT pairwise comparison methodology from LLM-model ranking to scientific-question ranking. The key extension is that Chatbot Arena ranks *outputs* while Assay ranks *questions* — and the properties of the ranking (where uncertainty is highest, where evaluator disagreement clusters) are themselves the primary research output.

**vs. MiroFish:** MiroFish demonstrates swarm-scale generation; Assay demonstrates swarm-scale evaluation. Together, they represent complementary halves of a complete automated research ecosystem. MiroFish's lack of evaluation framework is precisely the gap Assay fills.

---

## 6. Key References (Organized by Relevance to Assay)

### Tier 1: Core Anchors
1. Lu, C. et al. "The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery." *Nature* 651, 914–919 (2026). arxiv:2408.06292, arxiv:2504.08066
2. Google Research. "Towards an AI Co-Scientist." arxiv:2502.18864 (2025)
3. Romera-Paredes, B. et al. "Mathematical discoveries from program search with large language models." *Nature* (2023). [FunSearch]
4. Zheng, L. et al. "Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference." arxiv:2403.04132 (2024)
5. Si, C. et al. "Can LLMs Generate Novel Research Ideas?" ICLR 2025. arxiv:2409.04109
6. Ghafarollahi, A. & Buehler, M.J. "SciAgents: Automating Scientific Discovery Through Multi-Agent Intelligent Graph Reasoning." *Advanced Materials* (2024). arxiv:2409.05556

### Tier 2: Evaluation Methods
7. Gu, X. et al. "A Survey on LLM-as-a-Judge." arxiv:2411.15594 (2024, updated 2025)
8. Zhuge, M. et al. "Agent-as-a-Judge." (2025) — hierarchical, process-level evaluation
9. PAJAMA. "Time to Impeach LLM-as-a-Judge: Programs are the Future of Evaluation." ICML 2025 Workshop. OpenReview
10. Yano, T. et al. "An Empirical Study of LLM-as-a-Judge: How Design Choices Impact Evaluation Reliability." arxiv:2506.13639 (2025)
11. Statistical Framework for Ranking LLM-Based Chatbots. arxiv:2412.18407 — generalized BT/Rao-Kupper/Davidson models
12. HindSight. "Evaluating LLM-Generated Research Ideas via Future Impact." arxiv:2603.15164 (March 2026)

### Tier 3: Knowledge Graphs & Frontier Detection
13. GoAI. "Graph of AI Ideas: Leveraging Knowledge Graphs and LLMs for AI Research Idea Generation." arxiv:2503.08549 (2025)
14. GraphMind. "Interactive Novelty Assessment System for Accelerating Scientific Discovery." arxiv:2510.15706 (2025)
15. Boudreau, K.J. et al. "Looking Across and Looking Beyond the Knowledge Frontier." *Management Science* (2016)
16. RND. "Enabling AI Scientists to Recognize Innovation." arxiv:2503.01508 (2025)
17. Research frontier detection via grants (Huang et al.). *Journal of Informetrics* (2023)

### Tier 4: TDA Foundations
18. Chazal, F. & Michel, B. "An Introduction to Topological Data Analysis." *Frontiers in AI* (2021)
19. Su, Z. et al. "TDA and TDL Beyond Persistent Homology — A Review." arxiv:2507.19504 (2025)
20. Harmonic Persistent Homology for biological discovery. *Nature Scientific Reports* (2025)

### Tier 5: Swarm & Multi-Agent Frameworks
21. MiroFish. github.com/666ghj/MiroFish (2026)
22. CAMEL-AI OASIS framework — multi-agent social simulation
23. Agentic AI for Scientific Discovery survey. arxiv:2503.08979 (ICLR 2025)

---

## 7. Open Questions for the Dissertation

1. **Correlation vs. independence of frontier measures:** Do topological frontier-ness and evaluative frontier-ness correlate? What does their relationship tell us about the nature of open questions?

2. **Calibration of BT in the evaluation context:** BT assumes a stable underlying strength parameter, but the "frontier-ness" of a question changes as research progresses. How should the BT model be adapted for non-stationary evaluation targets?

3. **Evaluator reliability estimation:** Crowd-BT (Chen et al., 2013) estimates judge reliability from voting patterns. Can this be extended to detect not just unreliable evaluators, but evaluators with *systematic* domain biases (cf. Boudreau's "expertise penalty")?

4. **The HindSight challenge:** If LLM judges show negative correlation between perceived novelty and actual future impact, what does this imply for Assay's design? Should frontier detection actively *discount* ideas that sound novel to LLM reviewers?

5. **Scaling evaluation diversity:** Si et al. found that LLMs lack idea diversity at scale. Does the same problem affect evaluation diversity? If all agent reviewers are Claude instances with different prompts, do their evaluations converge in ways that mask genuine frontier uncertainty?

6. **Formal evaluability of frontier-ness:** FunSearch works because evaluation is formally specifiable. Can Assay define a sufficiently formal notion of "frontier-ness" that enables FunSearch-like evolutionary improvement of frontier detection?
