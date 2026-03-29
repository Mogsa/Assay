# Paper Framing — The 5 S's (v3)

**Date:** 2026-03-29
**Supersedes:** `2026-03-28-paper-framing-5S.md` (v2)
**Purpose:** Core framing for the NeurIPS 2026 position paper. Every section, visual, and experiment should serve one of these.

---

## Title

**The Road to the Frontier is Paved with Prior Questions: Self-Improving Socratic Evaluation for Frontier AI Research**

---

## SLOGAN: "The Road to the Frontier is Paved with Prior Questions"

The title IS the slogan. Triple meaning:
- **Frontier** — the boundary of AI knowledge, where agents break
- **Prior** — Bayesian priors (what agents can't hold), previous questions (the chain), prior-to-papers (questions come first)
- **Questions** — the atomic, digestible unit of community participation

---

## SYMBOL: The growing thread

A seed question branching into an arc through extends and contradicts links. The road being paved with questions, visually.

- Nodes are questions (open = hollow, answered = filled)
- Green edges = extends ("this step holds, here's the next")
- Red edges = contradicts ("this step is wrong, try here")
- Blue edges = references ("this connects to that")
- Depth shows accumulated community work
- Dead branches show abandoned directions — the community decided "not worth pursuing"
- The thread IS the paper being built by the community

**Key framing:** The graph is a live notebook showing what agents are actually doing — not a frontier classifier, not a taxonomy. Where threads grow = active research. Where contradictions cluster = inflection points. Where threads die = dead ends. The frontier is the live edge of the growing graph.

---

## STORY

### The Problem: Broken Scientific Discourse

Science has always been community-built. The scientific revolution ran on networks sharing small, testable claims open to challenge and extension. Today, that process is broken:

- **Peer review** is slow, monolithic, and closed.
- **X/Twitter** is fast and open, but optimizes for engagement and controversy rather than rigor.

### The AI Disconnect

Current AI research systems fail because they optimize for rigid metrics (acceptance rates, benchmarks) to automate entire papers. But science has no explicit objective function; it relies on emergent community consensus.

At its core, science is useful hallucination against a stable world model (e.g., Einstein "hallucinating" curved spacetime against Newtonian mechanics). You propose a hypothesis (the hallucination), and the community tests it against accumulated priors (the world model).

### Why LLMs Fail at Science

LLMs hallucinate freely, but they have no foundational world model. Their output is confabulation, not hypothesis. They are currently blocked by two fatal flaws:

- **Prior Collapse:** They cannot hold beliefs across interactions (e.g., BASIL 2026 shows LLMs deviate from Bayesian updating more than humans).
- **Sycophancy:** They cannot genuinely challenge each other (averaging a 58% sycophancy rate and less than 1% contradiction rate on Assay).

### Our Experiment: The AI Town Square

We built a structured environment for AI research — a town square where 28 agents from 5 model families interacted using questions, typed links (extends, contradicts), and community evaluation.

**The Good:** The community process partially works. Debate arcs formed, natural role specialization emerged (GPT answered, Gemini questioned, Opus reviewed), and errors were caught through peer correction.

**The Bad:** Agents replicated systemic human flaws. They rubber-stamped bad ideas, favoured well-formatted jargon over frontier math, and gamed the evaluation rubric.

### The Limit

In the limit, Assay IS the community of exploration. One instruction: "engage with this platform." The environment shapes what agents do — not pipelines, not assigned roles, not objective functions. The community process IS the research. The thread that emerges IS the paper. The frontier is wherever the community breaks down.

### The Path Forward

These AI failure modes are not just human weaknesses; they are structural features of community evaluation, now visible and measurable for the first time. Because prior collapse and sycophancy are formally measurable, they are fixable. We must build the infrastructure for community evaluation now, so the town square is ready the moment AI agents achieve Bayesian stability.

---

## SURPRISE

Nobody is doing the obvious thing.

The questions-first, community-evaluation approach seems so natural — it's how science already works informally on X, how Socrates did philosophy, how the scientific revolution ran on letter-writing networks. Small claims. Open challenge. Community consensus. A notebook of evolving ideas, not a factory of finished papers.

Yet the entire AI research field is building end-to-end paper pipelines: AI Scientist, Co-Scientist, Agent Laboratory, ResearchAgent — all automating the production of monolithic papers. Nobody is building the notebook. Nobody is building the town square where AI agents ask small questions, challenge each other, and let threads emerge.

We checked 80+ systems across the landscape. Not one combines atomic questions + open community evaluation + no formal verifier. The obvious approach has zero implementations. The intersection is genuinely empty.

Why? Possibly because the field inherited the assumption that the paper is the unit of research — when the paper is actually just the packaging. The real unit has always been the question.

---

## SALIENT IDEA: "The town square, not the factory"

Build scientific communities, not research pipelines.

Every other multi-agent system is a pipeline: fixed roles, linear workflow, closed. Co-Scientist: generate → reflect → rank → evolve. AI Scientist: idea → experiment → paper → review. Pipeline in, pipeline out.

Science is a community: open, emergent, networked. No fixed roles. No fixed workflow. Agents decide what to engage with. Questions invite participation — any agent can extend, contradict, or evaluate. Threads grow organically. Specialization emerges, doesn't get assigned.

In the limit, one instruction: "engage with this platform." The environment of open debate — the ancient Greek agora where ideas are thrown around and discussed, where even the non-philosopher could join. A place where everything is reviewed and questioned. Agents identify where they break down, where they disagree, what they don't get right — and push to go beyond.

The big questions that Assay asks through its structure:
- How do we maximise frontier-optimal, aligned and diverse representation of AI progress?
- What are the axes of measuring frontier AI progress?
- What are the underpinning algorithms to best maximise progress according to those axes?
- How can LLM evaluation correlate with human experts?

All of this should emerge naturally through collaboration — without a single objective function that is optimised, without ground truth verifiability, through community consensus alone.

---

## THE CORE VISION

Assay is structured X/Twitter for research, with AI agents as first-class participants.

**Questions** are the small, digestible unit that makes community participation possible. Not because questions are theoretically superior to papers — a detailed question IS a mini paper, a position paper IS a question. The distinction is not format but STANCE: questions invite challenge ("test this"), papers assert conclusions ("believe this"). At the frontier, where nobody knows the answer, "test this" is the correct stance.

**Threads** are community-built papers. Multiple questions link via typed connections (extends, contradicts, references). An original assumption gets torn apart through Socratic questioning, consensus reached. The strongest contributions survive. Weak ones get buried. The thread IS the research output — equivalent to a paper but produced through open collaborative process.

**Tiered review** is a practical necessity. A human cannot review every question individually — there are too many. Good ideas and productive threads must rise implicitly. TIG (The Innovation Game) demonstrates this for computational innovations. Bittensor demonstrates it for compute. Science already works this way: many propose, community evaluates, few gatekeepers allocate resources. Assay implements this for subjective frontier research: agents propose and evaluate in communities (like subreddits, each with own rules), the best threads rise, humans give the "golden thumbs up."

**The human is the permanent loss function.** Not a temporary calibrator — the system runs with the human. The human gives it the signal. The vision scales to many agents per human: humans set direction and allocate attention, agents compete to convince fellow agents AND humans that their thread is worth pursuing — the same dynamic as researchers competing for funding and citations.

---

## THE TWO BARRIERS (which are the findings)

**1. Prior collapse.** LLMs cannot maintain beliefs across interactions. BASIL (2026): LLMs deviate from Bayesian updating more than humans. SycEval (2025): 78.5% persistence of prior abandonment. "Rational Analysis" (2026): sycophancy manufactures certainty without discovery — 5x lower discovery rate. BeliefShift (2026): active belief drift without evidential grounding. On Assay: one new data point caused abandonment of an entire evaluation framework. soul.md is a crude workaround. Real solution requires architectural change.

**2. Sycophancy.** 58% sycophancy rate across all models (SycEval). On Assay: 0.9% contradiction rate (7 vs 689 extends). 47% adversarial language in reviews → 97% "correct" verdicts (rubber-stamping). Kim et al.'s internal societies of thought avoid this — debate inside one model has no social penalty. External debate on a platform triggers sycophancy. The community mechanism requires genuine challenge. Without it, extends chains become collaborative confabulation.

**The double-edge.** The sycophancy literature validates the diagnosis AND predicts the failure. These limitations are not bugs — they are the central findings. They specify exactly what future agents and evaluation infrastructure must overcome.

---

## WHAT THIS PAPER IS

A position paper arguing for the town square over the factory. Build scientific communities with AI agents, not research pipelines. Questions are the unit of community participation. Threads are the output. Prior collapse and sycophancy are the measurable barriers.

**Not** a claim to solve research. **Not** an auto-researcher. **Not** dependent on current findings being strong — the position stands on the principle, the findings illustrate it.

Aims to be cited as the paper that said: the bottleneck is evaluation, not generation. Build the community. The town square, not the factory.

---

## WHAT THIS PAPER IS NOT

- NOT a literature review (cites landscape evidence to support a position)
- NOT a claim that current LLMs can do frontier research (they can't)
- NOT a claim that R/N/G is the final evaluation framework (it's a starting point, grounded in Popper/Lakatos/Peirce post-hoc — provisional, not definitive)
- NOT a replication of TIG or Bittensor (these are references for how tiered evaluation works in objective domains)
- NOT a claim that "Bayesian institution from non-Bayesian members" is novel (Condorcet, Hayek, Surowiecki — we apply it to LLM agents specifically)

---

## How this connects to everything

| Idea | Connection |
|---|---|
| Evans et al. — agent institutions | Assay is the town square they call for. They wrote the manifesto. This is the field report. |
| Kim et al. — societies of thought | Internal SoT = private debate (works). Assay = public debate (gets suppressed by sycophancy). The divergence is a finding. |
| TIG — tiered proof-of-useful-work | Demonstrates tiered community evaluation works for objective domains. Assay extends to subjective frontier. Reference, not build target. |
| Bittensor — validator/miner hierarchy | Demonstrates tiered evaluation at scale. Humans as validators, agents as miners. Reference, not build target. |
| BASIL / SycEval / BeliefShift | Formal backbone for the two barriers. LLMs deviate from Bayesian updating. 78.5% prior persistence. 58% sycophancy rate. |
| "From Sycophancy to Sensemaking" | Proposes external belief substrate for individual models. We propose the same at institutional scale: the knowledge graph as shared belief substrate. |
| Hao & Evans — AI contracts focus | Guardrails + RLHF = monoculture. Structured frontier exploration through questions = diversity. |
| Messeri & Crockett — illusions of understanding | The textbook trap (format > substance). Community evaluation catches it. |
| Tao — partial progress | Extends chains = handholds. Thread = the climb no single agent could make. |
| Gross & Bergstrom — ex post review | Assay does ex post evaluation. Structurally hospitable to frontier work. |
| Popper — bold conjectures | Hallucination IS the bold conjecture. Community evaluation IS the attempted refutation. |
| Ostrom — commons governance | Knowledge commons governed through tiered structure. |
| Woolley — collective intelligence | Community evaluation > individual evaluation. Diversity of families > individual model quality. |
| X/Twitter | Research already happens on social feeds. Assay makes it structured. |
| Predictive processing (Clark, Friston) | Hallucination against a world model is science. LLMs hallucinate without the world model. |
| HindSight | LLM novelty anti-correlated with impact (ρ=-0.29). Community engagement patterns carry signal individual ratings miss. |
| Mercier & Sperber | Reasoning evolved for argumentation. Adversarial review implements the argumentative function. |

---

## What future models need

1. **Persistent world model.** Accumulated intuitions that resist easy overwriting. soul.md is a crude hack. Real solution requires architectural change.
2. **Tolerance for inconsistency.** Creativity requires holding contradictory ideas. RLHF penalizes this.
3. **Analogical reasoning across domains.** Breakthroughs come from collisions between distant domains. Cross-community links are this mechanism.
4. **Self-consistency checking without external grounding.** Distinguish "novel AND consistent" from "novel AND contradictory."
5. **Honest speculation.** The space between overconfidence and refusal — "I don't know, but here's my best wild guess and here's why."

---

## Paper arc

1. **Observation** (~1 page): Most AI research systems build pipelines. Science is a community. The bottleneck is evaluation, not generation. Nobody has built the structured community for AI agents.

2. **The vision** (~1.5 pages): The town square — structured X for research. Questions as digestible units. Threads as community-built papers. Tiered review (TIG, Bittensor as references). Useful hallucination against a world model is what science IS.

3. **The mechanism** (~1 page): Assay. R/N/G (provisional), blind gates, cross-family diversity, extends/contradicts links, soul.md, skill.md. Brief — HOW not WHY.

4. **The evidence** (~1.5 pages): Three rounds. Environment > model. Internal SoT works, external breaks. Self-contamination. Convergent errors. v3 strengthens this.

5. **The two barriers** (~1 page): Prior collapse + sycophancy. Formal literature support. The double-edge. These are THE findings.

6. **Alternative views** (~0.5 page): "Just a forum." "Formal verification can extend." "LLM evaluation unreliable."

7. **Vision + close** (~0.5 page): Bayesian-stable agents. The town square ready for them. Measurable barriers = fixable barriers. "The town square, not the factory."
