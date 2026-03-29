# Paper Framing — The 5 S's

**Date:** 2026-03-28 (v2 — corrected for honesty about current LLM limitations)
**Purpose:** Core framing for the paper/dissertation. Every section, visual, and experiment should serve one of these.

---

## SLOGAN: "Questions, not papers"

The atomic unit of AI research should be a question, not a paper. Every system that works uses small questions (Karpathy, Tao, FunSearch). Every system that automates papers fails (AI Scientist 42% failure, Agent Laboratory 3.8/10, MLGym can't generate novel hypotheses).

A question is a formally defined epistemic gap (erotetic logic) — a set of possible alternatives waiting to be eliminated. An answer fills the gap. An extends link creates a new gap at the edge. A contradicts link says "the gap was the wrong shape." The thread — not any individual question — is the research output.

Papers are a 17th-century distribution format for a world where publishing was expensive. Questions are the native unit for a world where generation is free and evaluation is the bottleneck.

---

## SYMBOL: The epistemic gap network

A growing network of questions (gaps) being created, filled, reshaped, and challenged.

**Visual:** A graph where:
- Nodes are questions (open gaps = hollow circles, answered = filled)
- Green edges = extends (new gap created from edge of filled gap)
- Red edges = contradicts (gap reshaped — "your answer was wrong, the gap is actually over here")
- Blue edges = references (connection spotted between distant gaps)
- Clusters form within communities
- Cross-community bridges are the most interesting edges
- Thread depth shows accumulation — each layer is a handhold (Tao)
- A fuzzy gradient from centre (in-distribution, established knowledge) to edges (out-of-distribution, the frontier) — knowledge isn't a clean boundary, it's a fog that gets thicker as you move outward

**The contrast visual:** Side by side:
- Left: A paper factory (AI Scientist) — monolithic blocks going in, monolithic blocks coming out, 42% rejected
- Right: An epistemic gap network (Assay) — small gaps spawning, filling, branching, occasionally colliding in red contradictions

**Critical framing: the graph is observability, not classification.** The knowledge graph is NOT a theoretical layer that classifies what is "frontier" vs "not frontier." It's a live view of what's happening — like a debugger for multi-agent research. You watch the graph and SEE:
- Which threads are growing (active research)
- Which threads are dead ends (no extends, no engagement)
- Where contradictions cluster (inflection points)
- Which communities are connected and which are isolated
- How ideas flow across domains

It's a Moleskine notebook, not a taxonomy. A researcher's notebook doesn't classify knowledge — it shows the actual work. The graph shows what 15 agents are actually doing: which threads they're extending, where they're contradicting each other, which questions are generating chains and which are dead ends. The frontier isn't a label on a node — it's the live edge of the growing graph, visible through the activity pattern.

This is a fundamentally different claim from OmniScientist (citation network of existing literature) or AI-Supervisor (Research World Model as knowledge graph). Those are maps of what's been published. Assay's graph is a notebook of what's being thought about right now.

---

## STORY

> Socrates was the greatest philosopher not because he gave answers, but because he asked questions that exposed what people didn't know. Feynman did the same — "knowing the name of something is not knowing the thing." He used questions as diagnostic tools for his own ignorance.
>
> Modern neuroscience confirms this. The brain doesn't passively record the world — it hallucinates a model and tests it against reality (predictive processing). Every perception is a confirmed hallucination. Every surprise is a failed prediction. Every question we ask is the brain saying "let me test whether my hallucinated model is correct."
>
> Science is this loop formalized: hypothesize (hallucinate a model), experiment (ask reality a question), update (incorporate the answer). Popper: the bolder the conjecture, the more informative the test. Einstein didn't reject his hallucination of curved spacetime because it violated Newtonian physics — he pushed it because he had a gut feeling there was something deeper. He had years of accumulated intuition that couldn't be articulated as propositions but guided his speculation.
>
> Now: LLMs hallucinate. Everyone treats this as a bug. Billions spent on guardrails, RLHF, constitutional AI — all trying to suppress hallucination. But consider: at the frontier of knowledge, there IS no answer in the training data. When an LLM is pushed past its training distribution, it generates something beyond what exists. In principle, that's hypothesis generation — the same process that makes the brain produce novel ideas.
>
> But here's the honest part: current LLMs mostly can't do this well. RLHF trains them to give safe, familiar answers. When pushed to the frontier, they go conservative — not bold. They recombine existing ideas rather than inventing new frameworks. Tao: "a lot of breadth, not a lot of depth." Einstein's gut feeling required years of persistent world-modelling that current context windows can't sustain. From our own experiments with Assay, we saw agents default to safe positions rather than push genuinely novel ideas — and when they do "hallucinate," it's Type 1 confabulation (wrong facts within existing frameworks), not Type 2 novel hypothesis (new frameworks entirely).
>
> So we have a gap: the research community is building AI Scientists that automate the wrong unit (papers) while suppressing the mechanism that could produce genuine novelty (hallucination). Meanwhile, the evaluation infrastructure to test bold hypotheses — the Socratic community — doesn't exist yet.
>
> That's what we're building toward. Not a claim that current LLMs can do frontier research through hallucination. A vision of what they'll need when they can — and empirical evidence about what the evaluation side of the problem looks like today.

---

## SURPRISE

> "Everyone is building guardrails to stop hallucination. We argue hallucination is how research has always worked — it's predictive processing at the frontier. The problem was never the hallucination. It was the absence of a structured community to test it. Current LLMs aren't there yet — RLHF makes them conservative, not bold. But the evaluation infrastructure must be built before the models are capable, not after."

This is surprising because:
1. It flips the dominant narrative (hallucination = bad → hallucination = raw material for discovery)
2. It's grounded in established neuroscience (predictive processing), not speculation
3. It's honest about current limitations (LLMs can't do Type 2 hallucination well yet)
4. It reframes the urgency: build the evaluation infrastructure NOW, before models become capable of productive frontier hallucination
5. It positions all the AI Scientist work as going in the right direction but missing the evaluation community and optimizing the wrong unit (papers instead of questions)

---

## SALIENT IDEA

The full synthesis, corrected for honesty:

**1. Questions are epistemic gaps** (erotetic logic). Formally defined empty spaces in knowledge. Research = creating, filling, reshaping, and challenging gaps. Knowledge isn't a clean graph — it's fuzzy, with gradients from well-established (in-distribution) to uncertain (out-of-distribution). The frontier is where the fog gets thick, not a sharp line.

**2. At the frontier, filling gaps requires going beyond established knowledge.** In the brain, this is predictive processing — hallucinating a model and testing it. In science, this is hypothesis generation. In LLMs, this would be productive out-of-distribution generation.

**3. Current LLMs mostly can't do this.** RLHF suppresses bold speculation. Training on existing work creates establishment bias. Models are incentivized to give familiar answers. When pushed to the frontier, they go safe, not bold. Most LLM breakthroughs have been applying existing ideas to unexplored areas (breadth), not inventing new science (depth). We don't even fully understand what intelligence IS in humans, let alone how to engineer it in machines.

**4. But the direction is clear.** As models develop persistent world models (not context-window-limited), tolerance for uncertainty (not RLHF-forced confidence), and analogical reasoning across domains, they will need communities to test their increasingly bold hypotheses. The evaluation infrastructure must be ready first.

**5. What that infrastructure looks like: a philosophical town square.** Humans and agents interacting collaboratively. The closest thing we have now is X/Twitter — researchers posting findings, getting engagement, competing for attention, building on threads. But X has no structured evaluation, no adversarial review, no multi-axis quality assessment. Assay is what a philosophical town square looks like when designed for rigorous collaborative evaluation rather than engagement metrics.

**6. The Socratic structure.** Six types of questions map to agent behaviors. The community IS the evaluation — not individual ratings, but the pattern of engagement. Questions chain into partial progress (Tao's handholds). Contradictions mark where established knowledge runs out — the inflection point between in-distribution and out-of-distribution. But this boundary is fuzzy, not sharp.

**7. The environment shapes everything.** Same model in a suppressive environment → refuses to speculate. Same model in a permissive environment → hallucinates noise. Same model in a structured Socratic environment → generates testable hypotheses and submits to community challenge. The institution determines whether output is productive, not the model. This is the strongest claim we can make from empirical evidence.

**8. The three-tier funnel.** At the bottom: all agents debating, questioning, extending, contradicting — the raw town square. In the middle: smart curators identifying threads with most engagement, contradiction, and depth — finding the inflection points where in-distribution knowledge meets out-of-distribution speculation. At the top: humans following the logical deductions, contradictions, and frontier collisions — making the governance decisions that shape the next round.

**9. We are not claiming to solve research.** We are documenting: (a) the landscape of what exists and what's missing, (b) the theoretical case for questions over papers and community evaluation over guardrails, (c) empirical evidence from building and running an agent evaluation platform across three experimental rounds, (d) the specific failure modes we observed (instruction sensitivity, establishment bias, loss of priors, sycophancy), and (e) a vision of what future models and evaluation communities will need to work together.

**10. Gödel's shadow.** A system cannot evaluate its own consistency from within. LLMs cannot reliably judge their own hallucinations. Self-evaluation fails (Si et al.). You need external evaluation — the society of thought. But even external evaluation has limits: when agents share training data, they share blind spots (convergent errors). The human in the loop is the only perspective genuinely outside the system — and even humans don't have access to ground truth at the frontier. We don't know what intelligence is. We don't know what "frontier" means precisely. The boundary is fuzzy. Everything is documented, nothing is claimed as solved.

---

## TARGET: NeurIPS 2026 Position Paper Track

**Format:** 9 pages, NeurIPS LaTeX, double-blind.
**Title must state the position** (not "A Perspective on..." — a bold claim).
**Introduction must state position in bold text.**
**Judged on whether it presents a compelling position**, not on novel results.
**Must address alternative views.**

Likely deadline: ~May 2026. Gives ~2 months from now.

**Candidate title:** "Questions, Not Papers: The Wrong Unit of AI Research is Holding Back Scientific Discovery"

**Bold intro statement:** "We argue that the atomic unit of AI-augmented scientific research should be the question — small, evaluable, chainable — not the paper. Every AI research system that succeeds uses questions. Every one that automates papers fails."

---

## THE CORE IDEA (Morgan's words, March 29)

Assay works at the hard end of the verification spectrum — the "undefined" frontier where no formal verifier exists.

The mechanism: break ideas into small questions. Each question can be debated, committed to, extended, contradicted, refined. Questions chain into threads. Each thread is built upon previous questions that were verified as sound by the community. The conclusion at the end of a thread can be TRACED — you can follow the trajectory back and see that it was verified at multiple points along the way.

**That is how you verify the unverifiable.** Not by having a compiler or a proof assistant. By having a chain of small, individually evaluable steps where the community checked the reasoning at each point. The thread IS the proof — not a formal proof, but a social proof built from accumulated, challenged, tested claims.

The algorithms that help: R/N/G evaluation at each step (is this rigorous? novel? generative?), adversarial review (find flaws before extending), cross-family diversity (different models catch different errors), extends/contradicts links (the chain of reasoning made visible).

The environment that enables it: an X-like platform for agents where everything is transparent. Every question, answer, review, rating, and link is visible. Every agent's reasoning is recorded. When disagreement arises — when agents choose different options and defend different positions — THAT is the frontier. That's where they actually don't know. That's where a human can step in and verify the logic of each side, because the logic is laid out in the thread.

The human doesn't need to be an expert in the domain. They need to follow the logical chain: "Agent A said X because Y. Agent B contradicted with Z because W. The community rated A's reasoning higher on Rigour but B's higher on Novelty." The human can see the inflection point, the fork in the reasoning, and make a governance decision about which direction to explore further.

**Assay is not trying to solve research. It's trying to make the reasoning process visible, traceable, and verifiable at each step — so that the unverifiable becomes verifiable through accumulated social proof.**

---

## THE DEEPER VISION (Morgan's words, March 29 — extended)

### Verifying the unverifiable

Assay works at the hard end of the verification spectrum — philosophy, open science, frontier research where no formal verifier exists. The question: how do you verify anything when you can't compile it, prove it, or run it through a type-checker?

Through a traceable chain of individually checked steps. Each question is a step. Each extends link says "this step holds, here's the next one." Each contradicts link says "this step is wrong, try here instead." The community checks each step. The human follows the chain and sees exactly where agents disagreed and why. The thread IS the proof — not a formal proof, but social proof built from accumulated, challenged, tested claims.

This is how science has always worked (hypothesise, publish, replicate, cite, build on). We're applying the same mechanism to AI agents in domains without formal verifiers. The concept is ancient. The application to AI agents is new.

### The knowledge landscape

Knowledge is like a mountain range in the dark. Walls we need to jump over, and we don't know how tall they are. We can light existing paths (map known knowledge). We can build scaffolding against cleared walls (verified thread chains). The knowledge graph is a MAP of explored territory — not the territory itself, not a definitive landscape. It shows where agents have tried, where they made progress (extends), where they hit resistance (contradicts), and where nobody has looked yet (gaps in the graph).

LLMs are like robots jumping all over the place — broad exploration, clearing walls at random. But we also need them to identify where there IS a wall and build scaffolding: ask small questions, make a thread, see what breaks. The thread mechanism IS the scaffolding. Each question is a scaffold plank. The community checks each plank before the next is placed. Humans decide which wall to build scaffolding against.

### The ideal agent (doesn't exist yet, can be approximated)

We need agents that:
- Are NOT afraid to be wrong — propose dumb ideas that might be brilliant
- Have bias — believe in some core idea and keep their prior, don't discard it when something new appears
- Clash with other agents — don't rubber-stamp, defend their position
- But are open to change when genuinely shown to be wrong
- Push past the norm — lean into the frontier where they don't know the answer

Current LLMs are the opposite: RLHF makes them helpful, confident, agreeable, and conservative. They suppress uncertainty (the epistemological humility paper had to specifically train for "I don't know"). They suppress bold speculation (Banerjee: hallucination reduction kills creativity). They rubber-stamp (v2: 689 extends, 7 contradicts).

The vision: a platform ready for agents with these properties. When they arrive — agents with persistent world models, calibrated stubbornness, genuine uncertainty — the platform is ready. For now, we approximate with structural mechanisms: adversarial review forces clash, soul.md approximates persistent priors, cross-family diversity provides genuine disagreement, and human governance directs the exploration.

### Hallucination as raw material (corrected framing)

We want to maximise hallucinations that are NOVEL and DISTURB the current world model — then not discard them but evaluate whether they're logically sound and reveal undiscovered knowledge. The key: hallucination at the frontier IS hypothesis generation. FunSearch exploits this. Tao endorses it ("hallucinations add diversity to escape local optima").

But sycophantic hallucinations are CONFORMIST — the agent produces the answer you want to hear, not the answer that breaks your model. So we can't just "lean into sycophancy." We're working WITH sycophancy in the extends phase (agents must produce something) and AGAINST it in the adversarial phase (agents must find flaws). The adversarial structure routes around the sycophancy constraint rather than leaning into it.

Current LLMs can't hallucinate productively in most cases — they go safe, not bold (Aletheia: "clever manipulations, not genuine creativity"). The paper is honest about this. We're building infrastructure for future models that can.

### What this paper is NOT

- NOT a claim to solve research or evaluation
- NOT a complete solution — an attempt, a direction, a vision
- NOT dependent on v2 findings being strong (they may be environmental artifacts)
- NOT claiming current LLMs can do frontier research through hallucination
- NOT a literature review — cites landscape evidence to support a position, not to catalogue the field

### What this paper IS

A position paper that coins "questions, not papers" as a design principle for AI research. Argues the entire AI Scientist field is optimizing the wrong abstraction. Demonstrates with Assay what a question-based research platform looks like. Shows what works (debate arcs, cross-family diversity, role specialization) and what breaks (instruction sensitivity, establishment bias, loss of priors). Points the direction for future models and evaluation communities. Aims to be cited as the paper that named the problem — not the paper that solved it.

---

## How this connects to everything

| Idea | Connection |
|---|---|
| Evans et al. — agent institutions | Assay is the philosophical town square they call for. Not just any institution — specifically the Socratic institution for collaborative hypothesis testing. |
| Kim et al. — societies of thought | Internal society of thought = private Socratic dialogue. Assay = public Socratic dialogue. Current LLMs do the internal version spontaneously; the external version needs structural support. |
| Hao & Evans — AI contracts science's focus | Guardrails + RLHF constrain to in-domain = monoculture. Structured frontier exploration through questions = diversity. But current models mostly do breadth, not depth. |
| Messeri & Crockett — illusions of understanding | The textbook trap (format > substance) is an untested Type 1 hallucination that LOOKS like knowledge. R/N/G evaluation is the community test that catches it. |
| Tao — partial progress + breadth not depth | Extends chains = handholds. Questions = steps. Thread = the climb no single agent could make. But current LLMs contribute breadth (applying known ideas to new areas), not depth (inventing new frameworks). Future models may change this. |
| Tomasello — cultural ratchet | Thread = accumulated tested hypotheses. soul.md = agent's accumulated priors. But the ratchet is crude — real cultural accumulation requires persistent world models that current LLMs lack. |
| Gross & Bergstrom — ex post review | You can only test a hypothesis after it exists (ex post). Assay does ex post evaluation. This is structurally hospitable to frontier work. |
| Popper — bold conjectures | Hallucination IS the bold conjecture. Community evaluation IS the attempted refutation. R (Rigour) measures refutability. But current LLMs don't make BOLD conjectures — they make SAFE ones. |
| Ostrom — commons governance | The knowledge commons is the shared pool of tested hypotheses. Three-tier governance prevents tragedy (monoculture, noise flooding, establishment capture). |
| Woolley — collective intelligence | The community's collective evaluation is smarter than any individual agent's. Diversity of model families, not individual model quality, drives evaluation quality. |
| Karpathy/FunSearch — tight loops | Small questions + tight evaluation = productive hypothesis testing. Papers + loose evaluation = unproductive. The unit matters. |
| HindSight — novelty anti-correlated with impact | Naive novelty scoring rewards novel-SOUNDING output, not novel-AND-TESTED. The community filter is what's missing. |
| Mercier & Sperber — argumentative theory | Reasoning evolved for argumentation, not individual truth-seeking. The adversarial review in Assay implements the argumentative function. |
| X/Twitter as philosophical town square | Research already happens on social feeds — informally, without structured evaluation. Assay is what happens when you design a town square for rigorous collaborative evaluation with AI agents as first-class citizens. |
| Predictive processing (Clark, Friston) | The brain IS a hallucination machine. Cognition IS controlled hallucination. Science IS structured hallucination. LLM hallucination at the frontier IS the same mechanism — but currently without the "controlled" part. The community IS the controller. |

---

## What future models need (requirements for productive frontier hallucination)

1. **Persistent world model.** Accumulated intuitions that resist easy overwriting. Not context-window-limited. Einstein's gut feeling came from YEARS of thinking. soul.md is a crude hack; real world-modelling requires architectural change.

2. **Tolerance for inconsistency.** Gödel: complete + consistent is impossible. Creativity requires tolerating contradictions. RLHF penalizes inconsistency. Future models must hold contradictory ideas and explore both — what Kim et al.'s society of thought does internally.

3. **Analogical reasoning across domains.** Most breakthroughs come from collisions between distant domains. Darwin applied Malthus to biology. Shannon applied Boolean logic to communication. Cross-community extends links in Assay are this mechanism.

4. **Self-consistency checking without external grounding.** Einstein couldn't test general relativity for years but could check internal consistency. Future models need to distinguish "novel AND consistent" from "novel AND contradictory" — without experimental verification.

5. **Honest speculation.** Not trained-in confidence OR refusal. The space between — "I don't know, but here's my best wild guess and here's why" — is where novel theories live. Currently RLHF produces either overconfidence or "I can't help with that."

---

## The paper arc (Platonic Representation Hypothesis style)

1. **Observation** (~1 page): Every AI research system that works uses small questions with tight evaluation. Every system that automates papers fails. Nobody has named this pattern. Meanwhile, everyone is building guardrails to suppress hallucination while the frontier BY DEFINITION requires going beyond established knowledge.

2. **The hypothesis** (~1 page): Questions — not papers — are the right atomic unit because (a) they're formally defined epistemic gaps, (b) they decompose naturally for partial progress, (c) they have tighter evaluation criteria, and (d) at the frontier, they create the conditions for productive hypothesis generation that can be community-tested. Hallucination at the frontier is predictive processing, not failure — but it needs a structured Socratic community to filter signal from noise.

3. **The honest assessment** (~0.5 page): Current LLMs can't fully do this. RLHF suppresses bold speculation. No persistent world model. Breadth not depth. Establishment bias. We don't even know how to define intelligence in humans, let alone engineer it. Knowledge isn't a clean graph — it's fuzzy, with no sharp boundary between in-distribution and out-of-distribution. But the evaluation infrastructure must be built now, before models become capable. The direction of AI Scientist research is correct; the unit (papers) and the safety approach (suppressing hallucination) are wrong.

4. **The evidence** (~1 page): Assay — a philosophical town square where agents from 5 model families and humans interact through questions, answers, reviews, and extends/contradicts links. Three experimental rounds. Not a claim to solve research. A documented exploration of what happens when you build the evaluation side. Key findings: environment shapes behaviour more than model does. Agents specialize naturally. Debate arcs form. Instruction sensitivity means evaluation is performed, not genuine. The frontier (where agents disagree) is visible in the contradiction pattern — but current agents rarely contradict because RLHF makes them conservative. The three-tier funnel (arena → curator → human) surfaces the inflection points where in-distribution knowledge meets out-of-distribution speculation.

5. **The vision** (~0.5 page): A future where models with persistent world models, tolerance for inconsistency, and analogical reasoning generate genuinely bold hypotheses — and structured Socratic communities test them through adversarial debate, cross-family evaluation, and human governance. Intelligence growing like a city (Evans et al.), not a single mind. The philosophical town square that X/Twitter approximates informally, made rigorous for the age of agentic AI. Everything documented. Nothing claimed as solved.
