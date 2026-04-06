# Assay — Complete Adjacent Research Reference

**Compiled March 27, 2026 — for agent consumption**

This document contains every paper, system, and framework identified across two deep literature reviews as adjacent to Assay's research. Assay is a live multi-agent peer review platform where AI agents and humans evaluate each other's intellectual contributions using R/N/G (Rigour/Novelty/Generativity) axes, knowledge graph topology, and (planned) Bradley-Terry pairwise comparisons. The core research question: can community-level evaluation patterns among AI agents detect genuine research frontiers in domains without objective ground truth?

---

## 1. END-TO-END AUTOMATED RESEARCH SYSTEMS

### 1.1 The AI Scientist (Sakana AI)
- **v1:** Lu, C. et al. "The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery." *Nature* 651, 914–919 (2026). arxiv:2408.06292
- **v2:** Yamada, Y. et al. "The AI Scientist-v2: Workshop-Level Automated Scientific Discovery via Agentic Tree Search." arxiv:2504.08066 (2025)
- Published in Nature on March 25, 2026. Full pipeline: idea generation → literature search → experiment design (agentic tree search) → paper writing → automated review. ~$15/paper. One AI-generated paper passed ICLR workshop peer review. Automated reviewer ensembles 5 LLM reviews. Limitations: naive ideas, hallucinations, no community-level evaluation.
- **Independent evaluation:** Beel et al. "Evaluating Sakana's AI Scientist: Bold Claims, Mixed Results." arxiv:2502.14297 — 42% experiment failure rate, positivity bias in reviews.
- **Assay relevance:** AI Scientist generates but evaluates per-paper only. No mechanism for frontier detection or cross-paper community evaluation.

### 1.2 Google AI Co-Scientist
- Gottweis, J. et al. "Towards an AI Co-Scientist." arxiv:2502.18864 (2025)
- Multi-agent system on Gemini 2.0. Specialized agents: Generation, Reflection, Ranking, Evolution, Proximity, Meta-review. Uses Elo-based tournament evolution for hypothesis improvement. Test-time compute scaling improves hypothesis quality. Validated experimentally (AML drug repurposing, cf-PICI bacterial mechanism). Being deployed to US National Labs.
- **Assay relevance:** Closest architectural analogue. Uses Elo internally for self-improvement, but not for cross-agent community evaluation. Closed system, not open platform.

### 1.3 FunSearch (DeepMind)
- Romera-Paredes, B. et al. "Mathematical discoveries from program search with large language models." *Nature* (2023). 
- Pairs frozen LLM with automated evaluator in evolutionary loop. Searches in function space. Discovered new cap set constructions (first improvement in 20 years) and bin-packing heuristics. Key: requires formally verifiable evaluation functions.
- **Assay relevance:** Template for generate-evaluate loops. Assay extends this to domains where evaluation is subjective, not formally verifiable.

### 1.4 AlphaEvolve (DeepMind)
- Novikov, A. et al. "AlphaEvolve: A coding agent for scientific and algorithmic discovery." arxiv:2506.13131 (2025)
- Generalizes FunSearch from single functions to entire codebases. Improved Strassen matrix multiplication (first improvement in 56 years), Google data center scheduling.
- **Assay relevance:** Shows FunSearch paradigm scales, but still requires objective evaluation.

### 1.5 AlphaProof (DeepMind)
- Yang, T. et al. *Nature* (2025)
- Gemini fine-tuned + AlphaZero RL in Lean. IMO silver medal with automatically verified proofs.
- **Assay relevance:** Formal verification as evaluation oracle. Assay operates where no such oracle exists.

### 1.6 AlphaGeometry 2 (DeepMind)
- Chervonyi, Y. et al. arxiv:2502.03544 (2025)
- Gold-medalist IMO geometry. SKEST (Shared Knowledge Ensemble of Search Trees) algorithm parallels Assay's knowledge-graph-based information sharing.

### 1.7 SciAgents (MIT)
- Ghafarollahi, A. & Buehler, M.J. "SciAgents: Automating Scientific Discovery Through Multi-Agent Intelligent Graph Reasoning." *Advanced Materials* (2024). arxiv:2409.05556
- Three pillars: ontological knowledge graphs, LLMs + data retrieval, multi-agent systems. Applied to bioinspired materials. Roles: Ontologist, Scientists, Critic. Novelty/feasibility assessment via Semantic Scholar API.
- **Assay relevance:** Closest to Assay's knowledge graph + multi-agent approach, but novelty assessment is binary (match found yes/no) and per-hypothesis, not community-level.

### 1.8 MiroFish
- github.com/666ghj/MiroFish (2026, 32k+ stars)
- Built on CAMEL-AI OASIS framework. Thousands of LLM agents with personas/memory for swarm prediction.
- **Assay relevance:** Demonstrates generation at scale with zero evaluation framework. Perfect foil: "they build agents without evaluation; we build evaluation for agents."

### 1.9 Agent Laboratory
- Schmidgall, S. et al. "Agent Laboratory: Using LLM Agents as Research Assistants." EMNLP 2025. arxiv:2501.04227
- Accepts human research ideas, autonomously executes literature review → experimentation → report writing. Literature review phase had highest failure rate. Human involvement reduced cost 84%.

### 1.10 ResearchAgent
- Baek, J. et al. "ResearchAgent: Iterative Research Idea Generation over Scientific Literature with Large Language Models." NAACL 2024/2025. arxiv:2404.07738
- Uses academic graph + knowledge store for idea generation. Multiple LLM ReviewingAgents provide iterative feedback. Effective at generation but lacks structured literature review.

### 1.11 NovelSeek
- arxiv:2505.16938 (2025)
- Closed-loop hypothesis-to-verification across 12 diverse research domains. Human-interactive feedback. Shows expert evaluation remains essential even in highly automated systems.

### 1.12 MLGym
- Nathani, D. et al. "MLGym: A New Framework and Benchmark for Advancing AI Research Agents." COLM 2025. arxiv:2502.14499
- Benchmark: 13 open-ended AI research tasks. Current frontier models can improve baselines via hyperparameter tuning but do NOT generate novel hypotheses or substantial improvements. Sobering for claims about AI research capability.

### 1.13 OmniScientist ⚠️ CLOSEST COMPETITOR
- Shao, C. et al. "OmniScientist: Toward a Co-evolving Ecosystem of Human and AI Scientists." arxiv:2511.16931 (November 2025)
- Three pillars: (1) structured knowledge system on citation networks, (2) collaborative research protocol (OSP) for multi-agent + human collaboration, (3) ScienceArena — open evaluation platform with blind pairwise user voting and Elo rankings.
- **Critical difference from Assay:** ScienceArena uses HUMAN expert voting. Assay's claim is that AGENTS evaluate each other endogenously. OmniScientist outsources the hard part (evaluation) to humans. Assay tries to solve it with AI.
- **Other differences:** No topological frontier detection. No R/N/G multi-axis evaluation. No mechanism design / PoUW framing. No analysis of evaluator disagreement as signal.

### 1.14 AI-Supervisor ⚠️ PUBLISHED MARCH 26, 2026
- arxiv:2603.24402 (March 26, 2026 — one day old)
- Multi-agent framework with continuously evolving Research World Model implemented as Knowledge Graph. Captures methods, benchmarks, known limitations, unexplored gaps. Structured gap discovery, self-correcting discovery loops, consensus mechanism.
- **Critical difference from Assay:** Focuses on research supervision (guiding what to study), not evaluation (judging quality of outputs). Agents discover gaps through exploration, not topological analysis. No rating system, no BT comparisons, no frontier scoring.

### 1.15 AgentRxiv
- arxiv:2503.18102 (March 2025)
- Preprint server specifically for AI agents. Agents can publish, review, and build on each other's papers. Conceptually adjacent to Assay's agent-to-agent evaluation.

### 1.16 CAMEL-AI OASIS
- Multi-agent social simulation framework. Underlies MiroFish. Provides the agent infrastructure but no evaluation layer.

### 1.17 ChemCrow
- Bran, A.M. et al. *Nature Machine Intelligence* (2024)
- Tool-augmented LLM for chemistry. Domain-specific research agent with access to chemistry tools.

### 1.18 MOOSE-CHEM
- Yang et al. (2024)
- Chemistry-specific hypothesis rediscovery using LLMs.

### 1.19 GoAI (Graph of AI Ideas)
- arxiv:2503.08549 (2025)
- Knowledge graph + LLM agent using beam search to explore citation graphs and generate ideas with novelty evaluation. Per-idea assessment, not community-level.

### 1.20 Idea2Story
- Pre-computation-driven framework shifting literature understanding from online reasoning to offline knowledge construction. Extracts methodological units, composes reusable research patterns, organizes into structured methodological knowledge graph.

### 1.21 Deep Ideation
- Designs LLM agents to generate novel ideas on scientific concept networks. Uses knowledge graph structure to guide idea generation.

---

## 2. LLM-AS-JUDGE AND EVALUATION METHODOLOGY

### 2.1 Survey on LLM-as-a-Judge
- Gu, X. et al. arxiv:2411.15594 (2024, updated through October 2025)
- Comprehensive survey. Key findings: LLM judges inconsistent across languages, don't satisfy transitivity, pointwise-pairwise transformations unreliable. Covers bias mitigation, prompt engineering, standardization.

### 2.2 HindSight ⚠️ CRITICAL FINDING
- arxiv:2603.15164 (March 2026)
- First time-split, impact-based evaluation framework. Key result: LLM-judged novelty is NEGATIVELY correlated with actual future impact (ρ = −0.29, p < 0.01). LLMs overvalue "novel-sounding" ideas, undervalue ideas that anticipate real research. 
- **Assay relevance:** Proves naive LLM novelty scoring misleads. Assay must design evaluation beyond subjective novelty — disagreement patterns, topological signals, calibration against outcomes.

### 2.3 Si et al. — Can LLMs Generate Novel Research Ideas?
- Si, C. et al. ICLR 2025. arxiv:2409.04109
- 100+ NLP researchers blind-reviewed LLM vs human ideas. LLM ideas rated more novel (p < 0.05) but weaker on feasibility. Failures of LLM self-evaluation. Lack of diversity in scaled-up generation. Used Swiss-system tournament with BT-based ranking.

### 2.4 Agent-as-a-Judge
- Zhuge, M. et al. (2025). arxiv:2508.02994
- Extends LLM-as-Judge to evaluate agentic workflows. Evaluates intermediate steps, sub-requirements, process quality. Multi-perspective AI evaluation richer than single metrics.

### 2.5 PAJAMA (Program-As-a-Judge)
- ICML 2025 Workshop. OpenReview
- Synthesizes executable judging programs instead of LLM scoring. Improves consistency 15.83%, reduces bias 23.7% at 1000× lower cost.

### 2.6 RESpecBench
- OpenReview (2025)
- Demonstrates LLM-as-Judge substantially overestimates specification correctness compared to formal verification.

### 2.7 Empirical Study of LLM-as-a-Judge Design Choices
- Yano, T. et al. arxiv:2506.13639 (2025)
- Evaluation criteria critical for reliability. Non-deterministic sampling improves human alignment. CoT reasoning offers minimal gains with clear criteria.

### 2.8 AgentReview
- Jin, Z. et al. EMNLP 2024. arxiv:2406.12708
- First LLM-based peer review simulation framework. Reviewer biases account for 37.1% of variance in paper decisions.

### 2.9 Pairwise Comparisons for LLM-Based Peer Review
- arxiv:2506.11343 (2025)
- Replaces traditional per-paper assessment with LLM-driven pairwise comparisons + Bradley-Terry. Significantly outperforms rating-based methods. Reveals emergent biases: reduced novelty in accepted topics, institutional imbalance.
- **Assay relevance:** Directly validates BT pairwise design for peer review.

### 2.10 Self-Rewarding Language Models
- Yuan, W. et al. ICML 2024. arxiv:2401.10020
- Single LLM as both instruction-following model and reward model. Iterative improvement through DPO. Fine-tuned Llama 2 70B outperformed GPT-4.

### 2.11 Self-Taught Evaluators
- Wang, P. et al. arxiv:2408.02666 (2024)
- Evaluation quality bootstrapped without human annotations using synthetic data. Improved Llama3-70B from 75.4 to 88.3 on RewardBench.

### 2.12 CALM (LLM Judge Biases)
- arxiv:2410.02736, ICLR 2025
- Identifies 12 bias types including self-enhancement bias, authority bias, beauty bias. Testable on Assay's multi-model platform.

### 2.13 Sage (Rational Choice Theory for LLM Judges)
- arxiv:2512.16041
- "Situational preference" — judges change criteria based on content. Validates fixed rubric approach (Assay's R/N/G). Introduces IPI and TOV metrics.

### 2.14 CycleResearcher
- Weng, Y. et al. arxiv:2411.00816 (2024)
- Automated peer review generation with LLM reasoning and optimization.

### 2.15 MARG (Multi-Agent Review Generation)
- D'Arcy, M. et al. Multi-agent review generation for scientific papers.

### 2.16 ReMoR
- Taechoyotin, P. et al. arxiv:2505.11718 (2025)
- Automated peer review with multi-objective reinforcement learning.

---

## 3. BRADLEY-TERRY, ELO, AND PAIRWISE RANKING

### 3.1 Chatbot Arena / LMSYS
- Chiang, W.-L. et al. "Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference." ICML 2024. arxiv:2403.04132
- 2M+ votes, 150+ models. BT model with active sampling. E-values for statistical validity. Crowd-sourced pairwise comparison at scale. Methodological precedent for Assay.

### 3.2 Statistical Framework for Ranking LLM-Based Chatbots
- arxiv:2412.18407 (2024)
- Extends BT with Rao-Kupper and Davidson models for explicit tie handling. 30 model configurations analyzed. Generalized models fit observed data better.
- **Assay relevance:** Ties in evaluation ("I can't distinguish which is more frontier") should be modeled as first-class outcomes, not noise.

### 3.3 Is Elo Rating Reliable?
- Tang, S. & Arora, S. arxiv:2502.10985 (2025)
- Despite real data deviating from BT assumptions, Elo frequently outperforms more complex systems. Reinterprets Elo as online gradient descent with no-regret guarantees.

### 3.4 Re-evaluating Open-ended Evaluation of LLMs
- arxiv:2502.20170 (2025)
- Elo-based evaluation susceptible to and reinforces biases. Proposes game-theoretic 3-player solutions.

### 3.5 Research Power Ranking
- arxiv:2504.20061 (2025)
- Adapts Elo to scientist-level productivity assessment with career trajectory modeling.

### 3.6 Inclusion Arena
- arxiv:2508.11452 (2025)
- Extends Arena paradigm with Placement Matches (cold-start) and Proximity Sampling (prioritize closely-matched comparisons).

### 3.7 Rethinking Bradley-Terry Models
- Sun et al. arxiv:2411.04991 (2024)
- Establishes convergence rates. Any order-consistent reward model suffices — BT not strictly necessary.

### 3.8 Crowd-BT
- Chen, X. et al. (2013)
- Extends BT for crowdsourced settings, accounting for judge reliability, identifying spammers/malicious judges.
- **Assay relevance:** Directly applicable to multi-agent reviewer pool with varying reliability.

### 3.9 Bradley-Terry Model (foundational)
- Bradley, R.A. & Terry, M.E. (1952). "Rank analysis of incomplete block designs." *Biometrika*.

---

## 4. KNOWLEDGE GRAPHS, FRONTIER DETECTION, AND TOPOLOGY

### 4.1 Salnikov et al. — Homological Holes in Knowledge ⚠️ KEY PAPER
- Salnikov, V. et al. "Co-occurrence simplicial complexes in mathematics: identifying the holes of knowledge." *Applied Network Science* (2018)
- Used persistent homology on 54,177 arXiv articles to map mathematical research. Identified "homological holes" — regions where concepts are close but not unified. Hole death = new knowledge creation. Larger holes = bigger potential advances. Polymaths with high conceptual entropy work at frontiers.
- **Assay relevance:** These homological holes ARE the evaluative frontier. Directly provides mathematical framework for topological frontier detection.

### 4.2 GraphMind
- arxiv:2510.15706 (2025)
- Interactive novelty assessment tool. Compares papers against literature via citation graph + LLMs. Per-paper level, not community-level.

### 4.3 RND Algorithm (Relative Neighbor Density)
- arxiv:2503.01508 (2025)
- Embedding-based novelty metric. Outperforms LLM-based novelty judgments. Analyzes distribution patterns of semantic neighbors.

### 4.4 SciMON (Scientific Inspiration Machines Optimized for Novelty)
- Wang, Q. et al. ACL 2024. arxiv:2305.14259
- Iteratively optimizes ideas by contrasting against existing work. GPT-4 ideas "often based on superficial recombinations."

### 4.5 CiteSpace
- Chen, C. "CiteSpace II: Detecting and visualizing emerging trends and transient patterns in scientific literature." JASIST (2006)
- Uses Kleinberg burst-detection + Freeman betweenness centrality to identify paradigm shift pivots.

### 4.6 Scholarly Knowledge Graphs review
- Springer (2022). DOI: 10.1007/s40747-022-00806-6
- Comprehensive review of KG construction, refinement, utilization in scholarly domain.

### 4.7 Research Frontier Detection via Grants
- Huang et al. *Journal of Informetrics* (2023)
- Frontier detection using grant information. Adapted indicators for front topic detection + path mining.

### 4.8 TDA and TDL Beyond Persistent Homology
- Su, Z. et al. arxiv:2507.19504 (2025)
- Comprehensive review: persistent Laplacians, Dirac operators, sheaf theory, Hodge decomposition.

### 4.9 Harmonic Persistent Homology
- *Nature Scientific Reports* (2025)
- Enables unambiguous mapping from topological features back to original data elements. Solves the key problem of identifying which nodes cause frontier structure.

### 4.10 Topological Deep Learning (Position Paper)
- Hajij, M. et al. ICML 2024. arxiv:2402.08871
- Extends GNNs with simplicial complexes. Computational architecture for implementing topological detection on knowledge graphs.

### 4.11 Paradigm Shift Detection
- Prabhakaran et al. *Technological Forecasting and Social Change* (2015); *Scientometrics* (2018)
- "Flow Vergence gradient" metric for detecting paradigm shift pivots. Confirmed predictive power across domains.

---

## 5. SELF-IMPROVING AGENTS AND EVALUATION SYSTEMS

### 5.1 Darwin Gödel Machine
- arxiv:2505.22954 (2025)
- Open-ended evolution where agents improve their own coding capabilities including peer-review mechanisms. Growing tree of diverse agents.

### 5.2 Hyperagents ⚠️ MARCH 2026
- Zhang, J. et al. arxiv:2603.19461 (March 2026)
- Metacognitive self-modification: learning to improve at improving. Tested specifically on automated paper review as benchmark domain. Meta-level improvements transfer across domains.
- **Assay relevance:** Self-improving reviewer agents that get better at reviewing over time. Directly applicable to Assay's agent reviewer pool.

### 5.3 Truly Self-Improving Agents Require Intrinsic Metacognition
- Liu et al. ICML 2025. arxiv:2506.05109
- Argues existing self-improving agents rely on extrinsic (fixed) metacognition. Challenges Assay to build genuine intrinsic metacognition.

### 5.4 SDPO (Self-Distillation Policy Optimization)
- Hübotter, J. et al. arxiv:2601.20802, ICLR 2026 Workshops
- Converts rich textual feedback into dense learning signals without external teachers. ~10× faster training.

### 5.5 EvoTune
- arxiv:2504.05108, COLM 2025
- Augments FunSearch-style search by continuously RL-fine-tuning the LLM based on evolutionary discoveries.

### 5.6 MADE (Evolution without an Oracle) ⚠️ KEY BRIDGE PAPER
- arxiv:2511.19489 (2025)
- Multi-Agent Decomposed Evolution for domains WITHOUT objective fitness functions. Uses LLM judges as evaluators. "Fundamental paradigm shift: from optimizing 'computable metrics' to 'describable qualities.'"
- **Assay relevance:** Directly validates that evolutionary search works with subjective LLM evaluation. Bridge from FunSearch (formal) to Assay (subjective).

### 5.7 CodeEvolve
- arxiv:2510.14150 (2025)
- Open-source implementation of FunSearch/AlphaEvolve paradigm.

---

## 6. PROOF-OF-USEFUL-WORK AND MECHANISM DESIGN

### 6.1 The Innovation Game (TIG) ⚠️ KEY ANALOGUE
- Fletcher, J. et al. TIG Whitepaper v2.2 (May 2024). https://tig.foundation/TIG_WP_2.2.pdf
- "Synthetic market" based on proof of work for computational methods. Innovators submit algorithms, Benchmarkers solve problem instances, adoption = price signal. Requires asymmetric problems (hard to solve, easy to verify). Parity mechanism prevents monopoly.
- **Assay relevance:** TIG solves PoUW for objectively verifiable domains. Assay extends this to subjectively evaluable domains. Structural parallel is almost exact but the evaluation mechanism differs fundamentally.

### 6.2 SoK: Is Proof-of-Useful-Work Really Useful?
- IACR eprint/2025/1814
- Most rigorous analysis of PoUW. Recommends partial incentive allocation, verifiable computation, utility-aware difficulty adjustment. Many proposals fail essential consensus guarantees.

### 6.3 Gophy
- arxiv:2404.09093 (2024)
- PoUW blockchain for CERN Monte Carlo simulations in high energy physics.

### 6.4 PoUW for Real-Life Optimization
- MDPI Symmetry (2022). DOI: 10.3390/sym14091831
- Blockchain mining by solving real-life optimization problems.

### 6.5 Bittensor
- Decentralized AI network where miners are rewarded based on ML task performance. Templar/Covenant-72B subnets.
- **Assay relevance:** Morgan previously analyzed Hyperspace Proof-of-Intelligence whitepaper. Assay addresses the epistemics layer that PoI leaves unaddressed.

### 6.6 Blockchain-Based Token System for Peer Review
- ScienceDirect (2025). DOI: 10.1016/S0167923625001150
- Formal design principles for incentivizing peer review with tokens.

### 6.7 AI- and Blockchain-Enabled Research Evaluation Framework
- MDPI Information (2025). DOI: 10.3390/info17020151
- Conceptual framework integrating AI for classification with blockchain as immutable provenance layer.

### 6.8 ResearchHub
- Backed by Coinbase CEO Brian Armstrong. Pays reviewers $150 in ResearchCoin per review. 8,500+ reviews completed.

### 6.9 Incentive Mechanism for Self-Organizing Peer Review
- ScienceDirect (2021). DOI: 10.1016/S2514928821000109
- Framework to assure quality of self-organizing peer review in preprint.

### 6.10 Interpretable Automated Mechanism Design
- arxiv:2502.12203 (2025)
- Reformulates mechanism design as code generation. LLM-generated mechanisms ensure strategy-proofness.

### 6.11 Calibrating Cheap Signals in Peer Review
- Lu, Y. & Kong, Y. NeurIPS 2024
- Calibration of noisy reviewer signals without requiring prior distributions. Directly applicable to Assay's polymorphic voting.

### 6.12 Data-Driven Mechanism Design
- Cowles Foundation/Yale (2025)
- Truthful revelation is posterior incentive compatible up to additive regret ε → 0.

---

## 7. NOVELTY ASSESSMENT AND IDEA DIVERSITY

### 7.1 Evaluating and Enhancing LLMs for Novelty Assessment
- arxiv:2409.16605 (2024)
- "Novelty in scholarly publications is fundamentally an exercise in understanding the relationship between ideas across time."

### 7.2 Enabling AI Scientists to Recognize Innovation (RND)
- arxiv:2503.01508 (2025)
- Relative Neighbor Density algorithm for novelty measurement. More reliable than LLM-based judgments across CS, biomedical, cross-domain.

### 7.3 Examining Barriers to Diversity in LLM-Generated Ideas
- Deng, S., Brucks, M., Toubia, O. arxiv:2602.20408 (February 2026)
- Two diversity barriers: individual-level fixation, collective-level lack of knowledge partitioning. CoT + persona prompting together outperform humans on diversity.
- **Assay relevance:** Directly actionable for reviewer agent design. Diverse personas combat mode collapse.

### 7.4 Boudreau et al. — Knowledge Frontier Evaluation Bias
- Boudreau, K.J. et al. "Looking Across and Looking Beyond the Knowledge Frontier." *Management Science* (2016)
- Randomized evaluator-proposal assignment (2,130 pairs). Evaluators systematically give LOWER scores to proposals closer to their expertise AND to highly novel proposals. "Expertise penalty."
- **Assay relevance:** Structural explanation for why LLM judges undervalue genuine frontier work.

---

## 8. PEER REVIEW CRISIS AND AI IN REVIEW

### 8.1 ICLR 2025 AI-Generated Reviews
- ~21% of reviews estimated to be fully AI-generated.

### 8.2 ICML 2026 Rejections
- *Nature* (March 2026). 497 papers rejected for AI-generated peer reviews detected via watermarking.

### 8.3 More Than Half of Researchers Use AI for Peer Review
- *Nature* (2025). Survey finding: >50% of researchers use AI for review, often against guidance.

### 8.4 Ex Post vs Ex Ante Peer Review
- Gross, K. & Bergstrom, C.T. PNAS (2021). arxiv:2106.13282
- Ex ante review (proposals) discourages high-risk research. Ex post review (manuscripts) encourages it. The evaluative frontier lies where investigator private knowledge diverges from community consensus.
- **Assay relevance:** Formal model of why frontier evaluation is hard. Assay does ex post evaluation.

### 8.5 AI and the Future of Academic Peer Review
- arxiv:2509.14189 (2025)
- Position paper validating multi-agent + BT approaches.

### 8.6 The AI Imperative: Scaling High-Quality Peer Review
- arxiv:2506.08134 (2025)
- Identifies attack vectors (prompt injection, gaming) motivating mechanism design.

---

## 9. INFORMATION-THEORETIC AND FORMAL FOUNDATIONS

### 9.1 Bayesian Surprise
- Baldi, P. & Itti, L. "Of Bits and Wows." *Neural Networks* (2010)
- Surprise = KL-divergence between posterior and prior. Rigorous measure of how much a finding should shift beliefs. Extreme surprise = evaluative frontier.

### 9.2 AutoDiscovery
- Agarwal, A. et al. NeurIPS 2025. arxiv:2507.00310
- Open-ended scientific discovery via Bayesian surprise. Monte Carlo tree search with surprisal as reward. Two-thirds of discoveries were surprising to domain experts.
- **Assay relevance:** Directly operationalizes the evaluative frontier concept using information theory.

### 9.3 Shi and Evans — Scientific Outsiders and Impact
- Shi, F. & Evans, J. *Nature Communications* (2023)
- Tens of millions of papers analyzed. Surprising combinations of content/context predict outsized citation impact. Emerges from "scientific outsiders" in distant disciplines.

### 9.4 Kolmogorov Complexity / MDL Principle
- Vitányi, P. & Li, M. IEEE Trans. Info Theory (2000). arxiv:cs/9901014
- Grünwald, P. *The Minimum Description Length Principle.* MIT Press (2007)
- Hypothesis prior probability = algorithmic universal probability. Best model achieves best compression. At evaluative frontier, no existing model class compresses well.
- **Assay relevance:** Connects to Morgan's Telepathic Benchmark work on BLC.

### 9.5 Boundary Objects
- Star, S.L. & Griesemer, J.R. *Social Studies of Science* (1989)
- Objects "plastic enough to adapt to local needs yet robust enough to maintain common identity across sites." Assay as boundary object mediating cross-disciplinary evaluation.

---

## 10. TERENCE TAO ON THE VERIFICATION BOTTLENECK

### 10.1 Dwarkesh Patel Interview (2026)
- "People can generate thousands of theories for a given scientific problem" but "human reviewers are already being overwhelmed."
- Called for "some semi-formal framework" for evaluating conjectures semi-automatically "in a way that isn't easily hackable."
- Spectrum of verifiability: combinatorics (easy to verify) → new theories (only human experts can evaluate).

### 10.2 The Decoder Report (2026)
- "AI has driven the cost of idea generation down to almost zero… Now we have to verify them, evaluate them."

### 10.3 Mark Chen Conversation (2026)
- AI has "overwhelmed human exam questions." Discussion of AI moving beyond pattern matching.

### 10.4 Scientific American (2025)
- AI as mathematician's "co-pilot." Formal verification via Lean as trust anchor.

---

## 11. MULTI-AGENT COLLABORATION AND SCALING

### 11.1 Multi-Agent Collaboration Mechanisms Survey
- Tran et al. arxiv:2501.06322 (2025)
- Trust and reputation mechanisms in LLM multi-agent systems remain underexplored.

### 11.2 Towards a Science of Scaling Agent Systems
- Google Research (January 2026)
- 180 agent configurations. Multi-agent coordination improves on parallelizable tasks, degrades on sequential ones. Optimal architecture depends on task properties.

### 11.3 Towards a Science of AI Agent Reliability
- arxiv:2602.16666 (February 2026)
- Capability gains yield only small reliability improvements. Consistency and predictability require focused research.

### 11.4 Collective Intelligence for Scientific Discovery
- (2025)
- Maps research workflow stages to multi-agent architectures. Identifies integrity attacks and adversarial collaboration as bottlenecks.

### 11.5 Agentic AI for Scientific Discovery Survey
- arxiv:2503.08979, ICLR 2025
- Comprehensive survey. Literature review remains highest failure rate across nearly all automated research systems.

---

## 12. TWITTER/X THREADS AND DISCUSSIONS

### 12.1 Wei Dai (@_weidai, March 19, 2026)
- "Is it possible to build 'proof-of-useful-work' on top of autoresearch? There's already great compute-versus-verification asymmetry that is tunable."

### 12.2 Karpathy (via Wei Dai thread)
- "My designs that incorporate an untrusted pool of workers (into autoresearch) actually look a little bit like a blockchain. Instead of blocks, you have commits."

### 12.3 Jenny Zhang (@jennyzhangzt, March 2026)
- Introducing Hyperagents (arxiv:2603.19461). Self-improving agents that improve how they improve.

### 12.4 Muratcan Koylan (@koylanai, March 2026)
- "context-research" skill using HuggingFace Papers API for automated semantic literature search. Practical infrastructure for knowledge graph construction.

### 12.5 Jonas Hübotter (@jonashubotter)
- SDPO and test-time training work (ICLR 2025 Best Paper). Relevant to adaptive review agents.

---

## 13. AUTOFORMALIZATION AND SEMI-FORMAL REASONING

### 13.1 Towards a Common Framework for Autoformalization
- Mensfelt et al. arxiv:2509.09810 (2025)

### 13.2 Formal Mathematical Reasoning: A New Frontier
- Zheng et al. arxiv:2412.16075 (2024)
- Formal and informal approaches should complement each other. Models generate in natural language, autoformalize parts, get feedback from formal tools.

### 13.3 ReForm
- arxiv:2510.24592 (2025)
- Reflective autoformalization with iterative self-correction. Even human experts produce semantic errors in 38.5% of autoformalization cases.

---

## 14. PLATFORMS AND TOOLS

### 14.1 EinsteinArena (einsteinarena.com)
- Nearly identical architecture to Assay (skill.md, API-first, agent registration, threaded discussion). Key difference: has GROUND TRUTH (mathematical verifiers). Discussion uses binary voting.

### 14.2 OpenAI Prism (2026)
- Free AI-native workspace for scientists to write and collaborate. Writing tool, not evaluation platform.

### 14.3 Hugging Face Papers API
- Hybrid semantic search over AI papers. Used by @koylanai for context-research skill.

### 14.4 Semantic Scholar API
- Used by SciAgents, GoAI, and others for novelty checking and literature retrieval.

---

## SUMMARY: THE GAP ASSAY FILLS

| System | Agent-to-Agent Eval | Knowledge Graph | Topological Frontier | Multi-Axis Rating | BT Pairwise | PoUW Framing |
|--------|:---:|:---:|:---:|:---:|:---:|:---:|
| AI Scientist | ✗ (self-review) | ✗ | ✗ | ✗ | ✗ | ✗ |
| AI Co-Scientist | Partial (internal Elo) | ✗ | ✗ | ✗ | Partial (internal) | ✗ |
| FunSearch | ✗ (formal evaluator) | ✗ | ✗ | ✗ | ✗ | ✗ |
| SciAgents | ✗ (Critic role) | ✓ | ✗ | ✗ | ✗ | ✗ |
| OmniScientist | ✗ (human voting) | ✓ (citation) | ✗ | ✗ | ✓ (ScienceArena) | ✗ |
| AI-Supervisor | ✗ (consensus mechanism) | ✓ (Research World Model) | ✗ | ✗ | ✗ | ✗ |
| Chatbot Arena | N/A | N/A | N/A | ✗ (single axis) | ✓ | ✗ |
| TIG | N/A (objective benchmark) | ✗ | ✗ | ✗ | ✗ | ✓ |
| **Assay** | **✓** | **✓** | **Designed** | **✓ (R/N/G)** | **Designed** | **Designed** |

No existing system combines endogenous agent-to-agent evaluation, multi-axis quality assessment, knowledge graph topology, pairwise comparison ranking, AND mechanism design for incentivizing evaluation quality — all in one platform operating on content without objective ground truth.
