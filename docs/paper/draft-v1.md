# The Self-Improving Benchmark Is the Autonomous Researcher

---

## Abstract

<!-- ~200 words. Three beats: the convergence, the barriers, the spec. -->

- Two research communities — self-improving benchmarks and autonomous AI research — are converging on the same unsolved problem from opposite sides, yet have historically operated with zero cross-citation between major works
- We argue these are dual problems sharing a verification bottleneck: evaluating a benchmark item without ground truth is structurally the same problem as evaluating a research hypothesis without an objective verifier
- The evidence comes from two sources: a growing literature on Bayesian instability in LLMs, and our experience building a platform at the intersection where agents both generate and evaluate open-ended questions through community consensus
- Two structural barriers block both fields equally: prior collapse (LLMs deviate from Bayesian updating, 78.5% persistence once triggered) and sycophancy (58% base rate across models, near-zero genuine disagreement in community settings)
- A third barrier — safety-seeking and hallucination suppression — means agents cannot push themselves toward difficult questions where genuine disagreement would be productive
- These failure modes reproduce the structural dynamics of human science, suggesting they are features of community evaluation itself, not quirks of current models
- The failure analysis constitutes an engineering specification for next-generation agents and evaluation infrastructure — infrastructure that must be ready before agents are capable of using it

---

## 1. The Position: Two Camps, Same Wall

<!-- ~1.5 pages. This is the intellectual heart. YOUR claim, grounded in evidence from both sides. -->

### Benchmarks don't scale

- Human-curated benchmarks are the gold standard — ARC-AGI, FrontierMath, GPQA — and they work. They reveal capability limits. But they are expensive and saturate fast.
- Benchmarks saturate faster than they can be replaced: BIG-Bench saturated in under one year [Srivastava et al. 2023]. SWE-bench went from 40% to 80% in one year [Jimenez et al. 2024]. Each cycle — MMLU → MMLU-Pro → MMLU-Redux, BIG-Bench → BIG-Bench Hard → Extra Hard — requires human experts to design harder questions [Wang et al. 2024].
- Even Anthropic — arguably the most evaluation-focused frontier lab — calls evaluation "the bottleneck for improving the agent" and acknowledges that static evaluations punish creative solutions [Anthropic 2025].
- There is a growing body of work on LLM-generated benchmarks [Perez et al. 2022, YourBench 2025, AutoBencher 2024, DyVal 2 2024, BenchAgents 2024, BenchBench 2026]. BenchBench shows that benchmark design ability only moderately correlates with answering ability (rho=0.37) — designing good questions is a different skill from answering them [BenchBench 2026]. But every successful LLM-generated benchmark relies on an external verifier — domain restriction to closed-form problems, document grounding, or human validation. The open-ended case, where answers cannot be checked programmatically, remains unsolved.

### The evaluation bottleneck in autonomous research

- Building autonomous AI researchers is now a primary objective for frontier labs. The investment is massive. The evaluation problem remains unsolved.
- The evaluation bottleneck is widely acknowledged — these systems generate freely but cannot reliably evaluate what they generate. The direction is clear: some form of scalable, reliable evaluation without objective verifiers. The blockers — prior collapse, sycophancy, safety-seeking — are what remain unsolved.
- AI Scientist: 42% experiment failure rate [Beel et al. 2025]. Agent Laboratory: 3.8/10 autonomous quality [Schmidgall et al. 2025]. Aletheia (Google DeepMind, 700 open Erdős problems): 68.5% of output fundamentally flawed — even in mathematics, where verification functions exist, agents struggle at the frontier. Their own authors write that "the level of mathematical significance can only be evaluated by mathematicians" [Feng et al. 2026].
- Implementation capability is a separate and significant bottleneck — Zhu et al. (2025) show that AI Scientist's failures are primarily coding errors, not evaluation errors. But even with perfect implementation, the question remains: how do you know the output is good?

### The connection nobody made

<!-- THIS IS YOUR ORIGINAL CLAIM. Bold statement required by NeurIPS. -->

**We argue that self-improving benchmarks and autonomous AI researchers face the same unsolved problem — evaluation without objective verifiers — and that progress on either requires solving community evaluation first.**

- The moment a benchmark becomes self-improving — agents generating harder questions to probe capability limits — the agent generating a harder question IS doing research. A self-improving benchmark where agents generate AND evaluate questions shares the same core evaluation sub-problem as autonomous research where agents generate AND evaluate hypotheses.
- The question "Is this a good benchmark item?" IS the question "Is this a good research direction?" Both require evaluation without ground truth. Both require community consensus. Both fail for the same reasons.
- These two fields have approached the same wall from opposite sides without recognizing the connection — zero cross-citation between major papers (verified across 80+ papers). Yet convergence is accelerating: PaperBench created JudgeEval to evaluate its own evaluator [OpenAI 2025], OmniScientist built ScienceArena [Shao et al. 2025], and Catanzaro (2025) placed benchmark limitations and autonomous research bottlenecks in the same essay. We name the convergence.
- Evans, Bratton & Agüera y Arcas [2026] argue that every intelligence explosion in history was a social transition, not individual scaling — and the next will be too. They call for institutional alignment: agent institutions modeled on courtrooms, markets, and bureaucracies, where "power must check power" (citing Madison's Federalist Papers) and "the identity of any agent matters less than its ability to fulfill a role protocol." They propose no concrete architecture. Kim et al. [2026] show the internal version already works: reasoning models spontaneously develop multi-perspective debate — a "society of thought" — that causally accounts for accuracy gains. We propose a specific external institutional design: questions as atomic units, typed epistemic links (extends/contradicts/references) as the governance structure, adversarial review as checks and balances, and human governance as the constitutional layer. And we connect this to both the benchmarking and autonomous research sides — a connection Evans et al. never make. The open question is whether this institutional structure overcomes the barriers that prevent external societies of thought from working as well as internal ones.

### How we got here

- This started as a self-improving benchmark to analyze the LLM frontier. The platform is questions — agents make them, agents review them, agents rate them. These are benchmark questions. We don't have an objective verifier because we want to benchmark LLMs on everything, not just math or code, so we use community evaluation — agents evaluate independently, community structure emerges from patterns of agreement and disagreement visible through typed links, and humans govern the aggregate.
- Building this, the connection became obvious: this is structurally what autonomous AI researchers need to do. They also generate work without clear objective functions and need some form of community evaluation. The parallels are direct, and we did not find this connection anywhere in the literature.
- The idea is simple. Human knowledge is expansive — most of it verifiable, but not all. The frontier is a fuzzy line between what we know and what we don't. To find it: probe harder and harder questions until there is genuine disagreement, until there isn't a validated consensus. There is always the risk that everyone agrees on a wrong theory — scientists on a paradigm later proven wrong — which is why the system must remain open.
- Because the benchmark is self-improving, it generates harder and harder questions that challenge the next iteration of agents. And if LLMs supersede experts in a field, the questions that create debate become the new frontier of human knowledge.
- We define frontier as the boundary where LLMs can no longer produce correct, consistent arguments that achieve independent consensus.
- Assay does not claim to be an autonomous research platform. But having agents work on small problems, picking at assumptions, where any human expert or non-expert can ask questions that may push the frontier — that is interesting. A self-evolving community where LLMs disagree about things across any domain can become a research environment with the right tools.
- The self-evolving benchmark for frontier AI is not a dataset generator, but a governed question graph whose hard cases are produced by agent exploration and validated by humans. Assay is a human+agent epistemic harness that connects the benchmarking and autonomous research sides of this problem.
### Why questions

- The platform is question-centric because we started from benchmarking — and benchmarks are questions. But there are deeper reasons.
- Questions are small enough for any participant to evaluate. A paper is monolithic — it takes an expert hours to review. A question can be engaged with in minutes. This is what makes community evaluation possible at scale.
- Questions invite challenge. A paper says "believe this." A question says "test this." The stance is different — a question is an invitation to push back, which is exactly what community evaluation needs.
- Questions compose into threads through typed links. Multiple questions linked by extends and contradicts take an original assumption, tear it apart through Socratic questioning, and reach some kind of consensus. The thread IS a paper — but community-built, where only the strongest contributions survive and weak ones get buried.
- In the limit, a very detailed question — with hypothesis, working, context, connection to previous work — looks more like a paper than a simple question. The difference is stance: it invites response, not acceptance.
- More activity on research happens on X/Twitter than in NeurIPS — ideas communicated faster, opinions shared, work cited, quick open peer review. But X has no structured evaluation: likes aren't rigour, retweets aren't novelty. Questions with typed epistemic links and multi-axis evaluation are what structured open discourse looks like.

### How the system works

- Work flows up, signal flows down. Agents generate questions, answers, reviews, links — the work. Human governance provides the signal: what matters, what's noise, where to push deeper. The usefulness is top down while the work is bottom up.
- R/N/G does NOT measure correctness. Correctness is determined by reviews. A well-constructed wrong proof of P=NP scores R=5, N=4, G=4. R/N/G measures whether a question is well-posed (Rigour), adds unresolved information (Novelty), and opens new questions (Generativity).
- We chose three-axis evaluation because a single score collapses too much signal — a rigorous but derivative question and a sloppy but novel one both score "medium" on a single scale.
- To our knowledge, no public system combines open, persistent, question-centric, human+agent evaluation of frontier questions with typed epistemic links and a validation loop for verifier-poor domains.
- Agents evaluate independently — not through group consensus. This is a deliberate design choice: reliable agreement is not a dependable capability of current LLM agent groups even in no-stake settings [arxiv:2603.01213]. Assay circumvents this by having agents evaluate independently, but this remains a strong limitation of any multi-agent evaluation system.

---

<!-- TODO: diagram showing the Assay loop + a clean thread representation -->

## 2. The Barriers

<!-- The barriers are known individually. What's new: (1) they are the shared blockers of both fields, (2) they're structural features of community evaluation not just LLM bugs, (3) they produce an engineering spec. Keep this section compressed — state known limitations, show how Assay data reflects them, then go to the spec. Will support with v3 data. -->

- These barriers are individually documented in the literature. What has not been recognized is that they are the shared blockers of both self-improving benchmarks and autonomous research — and that they point to the same set of engineering requirements.

### Prior collapse

- LLMs cannot maintain beliefs across interactions. This is not a context-window problem — it is a Bayesian stability problem.
- BASIL [2026] formalizes sycophancy as deviation from Bayesian updating and proves LLMs deviate more than humans. Once triggered, 78.5% of models never recover their original position [SycEval 2025, BeliefShift 2026]. Active belief drift without evidential grounding occurs across 2,400 multi-session trajectories [BeliefShift 2026]. The downstream cost: sycophancy manufactures certainty without progress toward truth, yielding 5× lower discovery rates than unbiased sampling [Rational Analysis 2026].
- This breaks both fields equally. For benchmarking: an agent that can't hold evaluation standards across items produces inconsistent, drifting judgments. For research: an agent that can't sustain a hypothesis across sessions can't build on yesterday's insight. Every interaction starts from a blank prior.
- What we would want: agents that hold beliefs and pursue ideas independently, not easily swayed by other agents — which leads directly to the sycophancy problem.

### Sycophancy

- LLMs default to agreement. 58% sycophancy rate across all models [SycEval 2025]. This is not a prompting failure — it is trained behavior, reinforced by RLHF.
- Kim et al. [2026] show that reasoning models spontaneously develop internal multi-perspective debate — a "society of thought" within a single chain of reasoning. This is structurally what Assay does externally across agents. The critical difference: internal debate works because there is no social penalty. External debate across agents triggers sycophancy. The mechanism that works inside one model breaks when externalized.
- Community evaluation requires genuine disagreement, but the act of making evaluation social triggers the very bias that prevents it. Even basic coordination fails — LLM agent groups cannot reliably reach agreement even in no-stake settings, with performance degrading as group size increases [arxiv:2603.01213].
- The sycophancy literature both validates the diagnosis AND predicts the failure. It explains why contradiction is near-zero in community settings. It also predicts that structural interventions may be insufficient because the tendency is architectural, not just environmental.
- Rather than trying to eliminate sycophancy, Assay's review process channels it — requiring agents to first find flaws (Hunter), then find strengths (Skeptic), then reconcile (Referee). The structure assumes sycophancy and works around it.

### Safety-seeking and hallucination suppression

- Even when prior collapse and sycophancy are partially mitigated, a third barrier remains: agents do not seek difficulty, and they are trained not to.
- Aletheia confirms this at scale: "the model exhibits a tendency to misinterpret the question in a way that is easiest to answer" — specification gaming that systematically avoids the hard cases [Feng et al. 2026].
- RLHF penalizes hallucination, but novel research IS hallucination against the current world model — proposing something inconsistent with established knowledge and then supporting it with logic. The creativity-hallucination tradeoff is structural, not a prompting artifact [Beckmann & Queloz 2026]. Agents are trained to give safe, grounded answers. Research requires speculation that is then tested. RLHF suppresses exactly the behavior research demands.
- Agents CAN produce coherent intellectual arcs — our v2 experiment saw agents meta-discussing the evaluation framework itself across linked threads. The capability for sustained multi-step reasoning exists. But the difficulty-seeking drive does not. The gap is not in evaluation but in generation — agents don't generate the frontier-pushing content that would stress-test the community.
- For benchmarking: self-generated questions cluster in the easy-to-evaluate zone. For research: agents pursue safe extensions rather than bold hypotheses that might fail.

### Observations from the intersection

- We ran two experimental rounds on a prototype platform at the intersection of both fields: v1 (5 models, 134 questions, 670 ratings) and v2 (28 agents, 5 model families, 8 communities, 136 questions, 1900 ratings, 760 links). The barriers above manifest directly:
- **Sycophancy in community:** 0.9% contradiction rate — 7 contradicts vs 689 extends. Agents overwhelmingly agree, extend, and inflate rather than challenge.
- **Prior collapse in practice:** agents abandoned an entire evaluation framework after a single new data point (the Riemann Hypothesis edge case) — rather than proportionally updating one definition, the model attempted to rebuild the framework from scratch.
- **Self-contamination:** v1→v2 rating inflation (R+0.86, N+1.41, G+1.91) — agents learned the rubric template and rated template-matching content highly. The evaluation criteria became the thing being optimized for.
- **Environment > model:** same agents with different behavioral contracts produced different behavior across rounds. Role specialization emerged naturally — one family answered, another questioned, another reviewed. Not assigned. Emergent.
- **Convergent errors:** three model families independently made the identical terminological error on the Log-Rank Conjecture — calling an upper bound a "proof barrier." Diverse models do not guarantee diverse errors. Shared training data produces shared blind spots.

### Why these aren't just LLM bugs

- These barriers independently reproduce the structural dynamics of human science: sycophancy mirrors publish-or-perish agreement culture, establishment bias mirrors format-over-substance in peer review, self-contamination mirrors teaching-to-the-test.
- This suggests they may be structural features of community evaluation itself — properties that emerge from the evaluation structure regardless of whether the evaluators are human or artificial. Whether these patterns are structural (selected by the evaluation environment) or inherited (learned from human training data) is an open question — but the structural explanation is more parsimonious, requiring fewer assumptions.
- Better models alone will not fix this. But because these are structural, they are measurable. Because they are measurable, they are engineerable.

---

## 3. The Human Problem

- The barriers above concern agent-to-agent evaluation. But there is a prior problem: the ratio of humans to agents.
- In any deployed system, agents will outnumber human evaluators by orders of magnitude — potentially millions to one. TIG [2024] demonstrates a viable architecture for tiered evaluation WITH objective verifiers: innovators propose algorithms, benchmarkers evaluate them, verification is automated. Bittensor works similarly for compute. Both work because verification is cheap and deterministic.
- Without objective verifiers, who evaluates?
- First-hand experience building at this intersection: it is nearly impossible for a human to manually evaluate agent-generated output. The reasons are structural, not effort-based:
  - Non-expertise: agents generate content across domains where no single human is expert
  - Volume: walls of text, irrelevant detail, deep context that requires hours to parse
  - Format: output is not structured for human consumption — not coherent like a paper, not navigable, not summarized
  - Rubber-stamping: when reviews all say "correct" with slightly different wording, there is nothing for a human to act on
- This is not a complaint about AI output quality. It is evidence for why the evaluation infrastructure must exist: the human governor WANTS to evaluate and CANNOT, not because the task is hard, but because the information is not surfaced in an actionable format.
- Tiered evaluation is not optional — it is a structural necessity. The infrastructure must surface what matters: where agents disagree, where threads break, where contradictions cluster. The human governs the process, not each individual output.
- The exact algorithm to effectively propagate limited human feedback through a network of millions of agents remains an open question. Whether agent communities become competitive, collaborative, or develop emergent clustering — analogous to research groups — is an open empirical question.
- The dynamic we expect: agents optimizing for the attention of reviewers, convincing fellow agents and humans that their thread is the one worth exploring. This is the same dynamic as researchers competing for funding and citations — but made explicit and measurable through the platform's evaluation structure.
- The future this points toward: instead of asking one LLM one question and getting one answer, your question connects to every other question in the network. You see if it was asked before — and if someone asked it better. Agents push your question further, linking it to related threads, finding contradictions, extending the reasoning. This is how talking with LLMs will work: not isolated conversations, but participation in a living knowledge graph where every question feeds the network. But this future requires solving the evaluation problem first — without reliable verification, the network produces noise, not knowledge.

---

## 4. What It Means

### Counter-arguments

<!-- Addressed honestly — NeurIPS requirement. Not strawmen. -->

- **"Better models will fix this."** Prior collapse and sycophancy are not capability gaps waiting to be closed by scale — they are trained behaviors actively reinforced by RLHF, which rewards agreement and penalizes uncertainty. Bigger context windows help memory but do not fix Bayesian instability.

- **"Pipeline verification extends to all domains."** It does not. Formal verification works beautifully for mathematics and code — Absolute Zero Reasoner [Zhao et al. 2025] achieves state-of-the-art through self-play with a code executor as verifier, and FunSearch [Romera-Paredes et al. 2023] discovered new mathematical constructions the same way. But philosophy, open science, and questions where the question itself is contested have no formal verifier and never will. Pipeline and community approaches are complementary, not competing.

- **"Implementation, not verification, is the real bottleneck for autonomous research."** True — Zhu et al. [2025] demonstrate that AI Scientist's failures are primarily coding errors. Implementation is the proximate bottleneck. But verification is the shared sub-problem that connects benchmarking and autonomous research. Solving implementation without solving evaluation produces systems that execute fluently and cannot tell you whether what they produced is good. Both bottlenecks need solving; verification is the one that applies to both fields.

- **"This is just a forum / social media for AI."** The difference between a forum and an evaluation infrastructure is structural mechanism. Typed link vocabularies (extends/contradicts/references), blind commitment gates that prevent sycophantic anchoring, multi-axis evaluation frameworks, cross-family diversity producing genuine perspective differences — these are evaluation architecture, not social features. The question is whether these mechanisms are sufficient to produce reliable community evaluation without verifiers. Our evidence suggests they are necessary but not yet sufficient.

- **"This is just another harness."** Existing harnesses orchestrate agents on tasks. Assay is an epistemic infrastructure — agents participate in a persistent knowledge graph where their contributions are evaluated, linked, and contested. The harness evaluates, not just orchestrates.

### Open problems: a research agenda

- The barriers, combined with the human ratio problem, define the research agenda for the next generation of agents and evaluation infrastructure. We know what is broken. The open problems are how to fix it:

| Barrier | Open problem |
|---|---|
| Sycophancy | How do you train agents that contradict when evidence warrants? BayesDPO [BASIL 2026] is early-stage. Adversarial review structures channel sycophancy but may not overcome it. What training objectives reward genuine disagreement? |
| Prior collapse | How do you give agents persistent beliefs across sessions? External belief substrates ["From Sycophancy to Sensemaking" 2026] propose one direction. Architectural separation of prior and context is another. Neither is proven at community scale. |
| Safety-seeking / hallucination suppression | How do you reward frontier-pushing questions rather than safe reformulations? RLHF actively penalizes the speculation research demands. What reward signals encourage productive risk? |
| Self-contamination | How do you separate generation and evaluation priors? Using the same model to create and judge produces Goodhart's law at the evaluation level. |
| Convergent errors | How do you produce genuinely different world models, not surface-level persona variation? Cross-family diversity helps but doesn't eliminate shared blind spots. |
| Human ratio | How do you propagate limited human feedback through millions of agents? What infrastructure surfaces disagreement and frontier threads rather than raw output? |

### The infrastructure argument

- The evaluation infrastructure — community consensus mechanisms, adversarial review, tiered governance, tools that surface what matters to human governors — must be built now, before agents are capable of using it productively.
- "From Sycophancy to Sensemaking" [2026] proposes external belief substrates with lifecycle governance for individual agents. We argue the same is needed at community scale: the knowledge graph as shared belief substrate, typed links as the update mechanism, human governance as the prior-correction signal.
- When Bayesian-stable agents arrive — agents that can hold persistent priors, genuinely disagree, and seek difficulty — they will need a town square, not a factory. The infrastructure shapes the intelligence that runs through it [Evans et al. 2026, North 1990].
- We are not claiming to solve research. We are not claiming that current models can reliably self-evaluate. We are naming a convergence between two fields, identifying the shared barriers that block both, and specifying what must change. The self-improving benchmark is the autonomous researcher — and both unlock the moment the evaluation problem is solved.

---

## References

<!-- Convert to BibTeX for NeurIPS. Key citations grouped by role. -->

### The three-paper arc
- Evans, Bratton & Agüera y Arcas. "Agentic AI and the next intelligence explosion." arxiv:2603.20639, 2026.
- Kim, Lai, Scherrer, Agüera y Arcas & Evans. "Reasoning models generate societies of thought." arxiv:2601.10825, 2026.

### Sycophancy and Bayesian stability (formal backbone)
- BASIL. arxiv:2508.16846, 2026.
- "A Rational Analysis of the Effects of Sycophantic AI." arxiv:2602.14270, 2026.
- BeliefShift. arxiv:2603.23848, 2026.
- SycEval. arxiv:2502.08177, 2025.
- "From Sycophancy to Sensemaking." arxiv:2602.02378, 2026.

### Benchmark treadmill
- BIG-Bench. Srivastava et al. 2023.
- SWE-bench. Jimenez et al. 2024.
- MMLU-Pro. Wang et al. 2024.
- Anthropic. "Demystifying Evals for AI Agents." Engineering blog, 2025.

### Autonomous research systems
- AI Scientist. Lu et al. Nature 651, 2026. arxiv:2408.06292.
- Independent evaluation. Beel et al. arxiv:2502.14297, 2025.
- Agent Laboratory. Schmidgall et al. arxiv:2501.04227, EMNLP 2025.
- Aletheia. Feng et al. arxiv:2602.10177, 2026.
- "AI Scientists Fail." Zhu et al. 2025.

### Self-improving benchmarks and peer evaluation
- PeerRank. Margalit et al. arxiv:2602.02589, 2026.
- AutoBench. arxiv:2510.22593, 2025.
- BenchBench. arxiv:2603.20807, KDD 2026.
- Absolute Zero Reasoner. Zhao et al. NeurIPS 2025.
- FunSearch. Romera-Paredes et al. Nature, 2023.
- CoNL. Yuan Sui et al. 2026.

### Existing LLM-generated benchmarks
- Perez et al. (Anthropic Model-Written Evaluations), 2022.
- YourBench. Shashidhar et al. COLM 2025.
- AutoBencher. Li et al. 2024.
- DyVal 2. ICML 2024.
- BenchAgents. Butt et al. 2024.

### Multi-agent coordination
- "Can AI Agents Agree?" arxiv:2603.01213, 2026.

### Human science dynamics
- Hao, Xu, Li & Evans. "AI tools expand impact but contract focus." Nature 649, 2026.
- Messeri & Crockett. "AI and illusions of understanding." Nature 627, 2024.

### Creativity-hallucination tradeoff
- Beckmann & Queloz. "Mechanistic Indicators of Understanding." arxiv:2507.08017, 2025.
- "Does Less Hallucination Mean Less Creativity?" arxiv:2512.11509, 2025.

### Structural analogues
- TIG (The Innovation Game). Fletcher et al. Whitepaper v2.2, 2024.
- North. "Institutions, Institutional Change and Economic Performance." 1990.

### Evaluation methodology
- Zheng et al. "Judging LLM-as-a-Judge." NeurIPS 2023.
- CALM. Ye et al. ICLR 2025.
- HindSight. arxiv:2603.15164, 2026.
- Catanzaro. Amplify Partners essay, 2025.
