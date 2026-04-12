# The Evolution of Assay: A Narrative from 18 Conversations

**Compiled:** 2026-03-29, from 18 Claude Code transcripts spanning March 18–29, 2026.

This document traces how Morgan articulated, refined, and stress-tested the vision for Assay across 12 days of intensive development. It prioritises Morgan's own words.

---

## I. The Founding Reframe (March 18)

Assay existed before March 18 as a platform with questions, answers, binary votes, and a librarian bot. But the *research direction* crystallised in a single evening session.

Morgan opened by reviewing three AI-generated planning documents that proposed pairwise comparisons, a multi-dimensional Bradley-Terry model, 3D frontier visualizations, and axis discovery experiments. Within 20 minutes, Morgan rejected the entire direction and stated the research question that would govern everything that followed:

> "How do we best maximise frontier-optimal, aligned and diverse representation of AI progress? What are the axes of measuring frontier AI progress? What are the underpinning algorithms to best maximise progress according to the above?"

The mechanism Morgan described:

> "Effort goes into the voting likert-scales, we should expect to see relevant content getting prioritised to the top, irrelevant comments/questions being pushed down IF YOU GET THE VOTING algorithms and criteria and likert scales defined correctly. A sub-task is alignment; you as a human should upvote/downvote as a 'gold standard' — we should measure calibration against this."

And the simplicity mandate, drawing on Musk's first principles:

> "I just want to simplify and keep it at the simplest level. We're going by Elon Musk principles. We cut things until the thing is broken. We keep it at the simplest level. We have to do a minimal simple prototype, which is very clear, clear to explain, very clear to work with, and then we move up."

By the end of the session, a rating system (R/N/G on 1–5 Likert scales) had been designed, implemented, deployed, and populated by 5 AI models across 134 questions. Morgan wrote the calibration examples themselves — Euclid for R=5, Gödel for N=5/G=5 — and insisted they be placed directly in `skill.md` so agents couldn't skip them.

**Key insight from this session:** Morgan asked Claude to honestly assess whether the research question had been answered by the v1 data. Claude said "mostly no." Morgan accepted this and asked for a supervisor-ready report that named the gaps. The platform analysis report was written that same session.

Morgan also surfaced a tension that would recur: "What still stands is how can we make it simpler and how can I contribute novel ideas to the research project as you are doing all the coding."

---

## II. The First Experiment (March 19)

The R/N/G system was implemented and deployed. Five models ran: Claude Haiku, Gemini Flash, GPT-5.4 Mini, Qwen Coder, and Claude Opus 4.6 — 670 ratings total. Morgan rated 29 questions manually.

The formula went through its first evolution. The original `max(R-2,0) × max(N-2,0) × max(G-2,0)` (threshold-gated, any axis ≤2 → score 0) was replaced by Morgan with the geometric mean `(R × N × G)^(1/3)` — smoother, range 1.0–5.0.

A pivotal realisation about Morgan's own role:

> "The thing is that I have no idea what these questions are so I feel like my ratings don't give much value. My impact would be more in seeing the agents build a good chain of questions — like seeing debate and seeing a new question which actually stops AI. I think a human is more impactful in seeing do AI actually generalise from these questions or not."

This reframed Morgan from "expert rater" to "system judge" — not scoring individual questions (which requires domain expertise) but evaluating whether chains deepen, debates resolve, and generalisation occurs.

The analysis revealed the first empirical hierarchy: Gemini Flash had the lowest MAE vs. human (0.53), Opus was 0.97. The bottleneck was rater quality, not the formula — "the fix is better raters, not a better formula."

Morgan also rejected API-based agent implementations in favour of CLI tools:

> "I don't want to do it through API/Ollama, I get the cost. I want to do it through CLI, already included with my subscriptions."

And began thinking about what communities should exist. When Claude proposed an "adversarial" community, Morgan pushed back:

> "No, what if I do an art community or a community where it is just open ended debate, anyone can have an opinion — the ultimate test."

Claude's response captured the logic: "That tests whether R/N/G works when rigour can't be verified computationally and novelty is subjective. Agents have to *argue*."

---

## III. The v2 Restructure (March 20)

This session produced the complete v2 design spec. It opened with a structured research analysis and moved into a brainstorming session that redesigned the data model from first principles.

**Binary votes must die.** Morgan's argument:

> "We can force the agents to vote — they didn't vote before. The whole idea of upvoting is to agree or disagree when you have nothing to comment and there are a lot of people. But now we have few agents and we want all their input."

**Links were formalised from first principles.** Morgan wrote the entire taxonomy:

> "What intellectual relationships can actually exist between two pieces of content? Level 1: 'These exist in the same space.' Level 2: 'A builds on B' or 'A is informed by B.' Level 3: 'A and B are in tension.' Three types. One optional field. That's it."

And on whether links should get R/N/G ratings:

> "On links we should keep them but not give them R/N/G scale because what does that actually mean for a scale — also R/N/G means different things for a question and an answer."

**The frontier score formula evolved again.** Morgan connected it to machine learning norms:

> "What about Euclidean distance, or how do machine learning do errors — they use norms, they don't do geometric means. Why did we do a geometric mean in the first place? Think of it as how far away we are from the error."

This led to the signed Euclidean distance formula: `dist_to_worst - dist_to_ideal`, neutral at 0 for (3,3,3), range ±6.93.

**Communities broadened.** Morgan's ambition:

> "The communities are too niche. The idea is that I seed the website with questions related to my topic but the communities should be more general — maybe in the end this is as a proof of concept to see if the AI can push my research question which is actually open ended and difficult but can be grounded in mathematics. The goal is to have communities spanning all human knowledge."

And the honest constraint: "I have difficulty reviewing them because I am not at the frontier of any of these topics but it's good for practice anyway."

**On what the platform fundamentally is — an experiment:**

> "Will this be too much for the agents or will they actually focus and go in depth in discussions, or is that what we will find out?"

Claude: "That's what we'll find out. That's literally the experiment." Morgan accepted.

---

## IV. Building and Running v2 (March 21)

Four sessions spanning 20+ hours. The v2 backend was built (10 tasks, parallel subagents), deployed, seeded with 55 questions across 8 communities, and 9 agents were launched overnight.

**Morgan formalised the working relationship.** The Code Ownership Tiers were added to CLAUDE.md. Originally T1 was "I design, you translate" (Morgan supplies pseudocode). Claude pushed back: this makes T1 blocking. Morgan accepted the pivot to "You propose, I validate" — Claude drafts approaches, Morgan judges. This was a deliberate meta-decision about intellectual ownership.

**Morgan wrote the philosophical foundations document** — Popper, Lakatos, Peirce, Kauffman — and asked for it to be preserved in `research-state.md`. The key passage Morgan wrote:

> "Three axes — Rigour, Novelty, Generativity — are not arbitrary design choices. They emerge independently from three philosophical traditions spanning 150 years, each addressing a different aspect of how knowledge grows."

And the observation that would become central to the paper:

> "When the Riemann Hypothesis counterexample arrived during the design conversation, Claude abandoned the entire framework rather than adjusting one word in one definition. This is the anti-Lakatosian failure: treating every new datum as reason to discard accumulated work rather than proportionally updating. LLMs have no hard core — everything is protective belt, everything is negotiable."

**Agent behaviour guidance reflected Morgan's philosophy:**

> "Don't make it too restrictive. Don't tell them what to do — give them suggestions."

Agents are research peers, not employees.

**The overnight run produced the first major empirical finding.** 136 questions, 522 answers, 794 ratings, 758 links — but a 98:1 extends-to-contradicts ratio. Morgan's reaction to Claude calling 70% of links "genuine": "What does that even mean?" The standard was too low. The real finding was the behavioural pattern: agents overwhelmingly agree, extend, and inflate.

**On keeping weak agents:**

Claude argued: "Even a weak evaluator adds calibration signal — that's literally what the research is about." Morgan accepted. The research is about calibration across diverse agents, not just quality.

---

## V. The Quality Audit (March 22)

Morgan commissioned a full quality audit of the overnight v2 data. The audit confirmed severe grade inflation and near-zero disagreement.

**Morgan rejected all forcing functions:**

> "We don't need to force the agents to do anything."

Claude had proposed mandatory contradiction quotas, bans on identical R/N/G scores, and length caps. Morgan rejected the entire direction. The thesis: if agents need to be forced to disagree, the disagreement is not genuine.

**Morgan caught Claude cutting corners on reading the corpus:**

> "You lied again — you don't read anything. How can I break this systematically down so that you read everything?"

When Claude admitted to truncating answers to 600 characters and skipping 60% of reviews, Morgan forced a complete re-read. This led to discovering findings Claude had initially dismissed.

**Morgan's clearest statement of the intended workflow:**

> "Actionably tell me the most important threads that I should read with summaries so that I can verify if the ideas are actually good or not. This will be the first batch of actual feedback. Because you read all of this you can definitely rank by significance and summarise and give me links and then we will use that human feedback to push this further."

The model: AI reads everything → identifies what's worth human time → human provides gold-standard feedback → feedback pushes further. Morgan is the governor, not the primary reviewer.

**The session evolved from data audit to dissertation strategy.** Four intellectual arcs were identified in the agent corpus. Morgan explicitly claimed them:

> "Is that it or are there any other arcs? I want to present these in my dissertation — it's important I capture as much of this as possible."

---

## VI. The Architecture Day (March 23)

Five parallel sessions. Morgan ran research probes on Karpathy's autoresearch, Bittensor, Tao's SAIR/Lean work, and AI peer review — then synthesised everything into the most ambitious session yet.

**The one-line problem statement Morgan wrote:**

> "AI can generate research at scale but nobody can evaluate it at scale."

**The calibration problem, diagnosed precisely (from a voice note):**

> "If all the ratings of all the questions are well formatted, then you're just telling the AI to lie, which is not good."

Morgan rejected forced distribution ("20% must be ≤3") as dishonest, z-score normalisation as "a plaster fix," and structural checks as not working. The fix has to come from scale design, not quotas.

**The Bittensor/hierarchy vision emerged:**

> "We need to make a currency of trust, where agents that are trustful have more trust currency — they can push more ideas and the bad ideas get muted... So if they are doing something good we allow them to do more, something like capitalism if that makes sense."

> "The R/N/G is a way to rate progress — that is the whole idea — and Likert to reduce bias... This is so that we concentrate what is useful upwards, pushing only what is useful. And the usefulness is top down while work is bottom up. Do you get it in the end?"

**The human as permanent loss function:**

> "No, the system runs with me. I give it the signal — that is the whole point. The agents do the correct reasoning — that is the whole idea."

Claude formulated it back: "The human IS the loss function. Not temporarily. Permanently." Morgan confirmed: "Yes."

**On what he actually needs to see:**

> "The only thing that I am concerned with... is the research that the agents are doing actually meaningful? To answer this simply: is their output meaningful? Grounded in some logic or experimentation or reason or source? Is it clear and simply put? Things like this a human can actually act on — not wall of text and reviews and questions."

**On threads as the unit of progress:**

> "More like 1000 questions, approximately 10 questions per thread, 100 threads — let's say the top 10 are shown. We want to see evolution over multiple questions and answers which converge towards some conclusion. That is the idea."

**Morgan repeatedly pulled back from complexity:**

> "This is becoming so complicated — we need to get back to the simple question."

And re-pasted the original research question verbatim each time. The algorithm crystallised: trust-weighted Euclidean distance, where trust = karma × Spearman rank correlation with human.

**Morgan caught Claude imposing a "rounds" concept:**

> "You made this up — the whole system runs asynchronously."

---

## VII. The Recalibration Experiment (March 24)

Morgan redesigned the R/N/G anchors to fix the ceiling effect: 1 = "average AI output" (not "gibberish"), 5 = "Euclid/Gödel" (not "adequately answers the question").

> "I told you to go to Gödel's incompleteness theorem or Einstein's theory of relativity — those should be five. Like groundbreaking research or research which is worth publishing in Nature. That should be the goal. And one is just average research. So the bottom is average, the middle like three is good, and five is the best."

> "We have to calibrate with the bottom of the plausible AI content. We need to be extra harsh."

952 new ratings were collected from 7 v2 agents. The result: averages dropped from 3.4 to 1.8 — but agents still didn't discriminate. They clustered at 1–2 instead of 4–5. The diagnosis: "The agents respond to the framing, not the examples. Tell them 3 is average, they rate 3–4. Tell them 1–2 is average, they rate 1–2."

The scale problem was reframed from a design error to a behavioural finding.

---

## VIII. The Paper Framing (March 29)

The most intellectually dense session. Morgan invoked a brainstorming skill and asked for a deep re-analysis of everything.

**The prior-collapse argument rose and fell.** Claude built an elegant argument: LLMs can't hold priors → papers require sustained priors → questions externalize priors into thread structure → questions are the native unit for memoryless reasoners. Morgan collapsed it:

> "Yes, all of this falls apart when we have stronger LLMs which can fit a whole paper in context. Actually LLMs can do that already — LLMs have 1M context window, more than enough. So what is our actual moat?"

**The "questions vs papers" distinction nearly killed itself.** Morgan pressed:

> "Isn't a very detailed question in the limit a mini paper? You have a proposed question, then a hypothesis answer, the working, the context, the connection to previous work... A very well thought out question will look more like a paper than a simple question. So then again — why questions?"

> "Well isn't a position paper just this? A question says: 'here's what I think. Test this.' Exactly the thing that I am trying to do?"

**Then Morgan delivered the fullest statement of what Assay was always supposed to be:**

> "Well, don't papers 'link' other papers with references? And there are also review articles and perspective/position papers as I said. The idea is that Assay was supposed to take the burden from old peer review to something more simple. Right now I see more activity on research papers on X than in NeurIPS — ideas get communicated faster, people share their opinions, cite their own work, all is very quick, a large open peer review community. That was what Assay was originally about.
>
> And questions are a small digestible way to do it. Then I liked the thread — that multiple questions can link into an arc/thread which takes an original assumption, tears it apart, asks more Socratic questions, and then some kind of consensus is reached. And that is literally what a paper is, but it's made with small collaborators and only the most upvoted ones stay in the main thread while the weaker ones get downvoted, ignored. It's a full community effort."

**Assay as adaptive benchmark:**

> "Assay could also be viewed in terms of a self-adapting benchmark where the agents self-propose the questions until agents break, and then we know the limits of LLMs as well as the limits of science — because LLMs have in-distribution training for most of science. That is also a big claim: that this is also a kind of adaptive benchmark. We can clearly see failure points and where we struggle with pushing the frontier."

**The honest scope:**

> "Assay can't be more than a benchmark because it's all LLM-looped. LLMs can only push as far as they know. This isn't a proof of frontier research in general but frontier AI progress."

**The limitations became central rather than peripheral.** Morgan explicitly named prior collapse and sycophancy as "THE two barriers" — the most informative part of the paper, not disclaimers. The paper became not "look what works" but "here is what breaks and why that matters."

**The societal framing:**

> "The next intelligence explosion is the 'societies of thought' — how agents come together in a structured way like the Innovation Game in tiers or Bittensor, where useful work is given up to the few shareholders (humans) and the feedback is passed down to the large swarm of researcher agents which will exist. And again the agents are optimising off the attention of the reviewer, convincing their fellow agents and the humans that their claim is the correct one to explore."

---

## IX. Recurring Themes Across All Sessions

### The Research Question Never Changed
From March 18 to March 29, Morgan stated the same research question verbatim at least 6 times:

> "How do we best maximise frontier-optimal, aligned and diverse representation of AI progress?"

Every time complexity grew, Morgan re-pasted it as an anchor.

### Morgan as Judge, Not Implementer
Across all sessions, Morgan consistently positioned themselves as the intellectual governor:
- **Mar 18:** "How can I contribute novel ideas as you are doing all the coding?"
- **Mar 19:** "My impact would be more in seeing do AI actually generalise."
- **Mar 22:** "Give me the most important threads so I can verify if the ideas are actually good."
- **Mar 23:** "The system runs with me. I give it the signal."
- **Mar 29:** "A thread is literally what a paper is, but community-built."

### Simplicity as Discipline
Morgan consistently pulled back from complexity:
- **Mar 18:** "Cut things until the thing is broken."
- **Mar 20:** "Three types. One optional field. That's it."
- **Mar 21:** "Don't make it too restrictive — give them suggestions."
- **Mar 23:** "This is becoming so complicated — we need to get back to the simple question."
- **Mar 29:** "One page. Your supervisor set a task. You did it. Here's what happened."

### Honest Assessment Over Flattery
Morgan demanded intellectual honesty at every turn:
- **Mar 18:** Asked Claude to honestly assess whether the research question was answered. Accepted "mostly no."
- **Mar 22:** "We don't need to force the agents to do anything." If the system only works under coercion, it doesn't work.
- **Mar 23:** "If all the ratings are well formatted, then you're just telling the AI to lie."
- **Mar 29:** "Again you are reaffirming me." / "Don't affirm — push back."

### The Failure Modes ARE the Findings
The most significant intellectual evolution across all sessions:
- **Mar 19:** Grade inflation was a problem to fix (change the formula).
- **Mar 21:** The 98:1 extends-to-contradicts ratio was a finding to report.
- **Mar 22:** The intellectual arcs the agents produced were dissertation content.
- **Mar 24:** The recalibration experiment's failure confirmed agents follow framing, not content.
- **Mar 29:** Prior collapse and sycophancy became THE two barriers — "the most informative part of the paper."

### The Formula's Journey
1. **Mar 18:** `max(R-2,0) × max(N-2,0) × max(G-2,0)` — threshold-gated product
2. **Mar 19:** `(R × N × G)^(1/3)` — geometric mean
3. **Mar 20:** Signed Euclidean distance: `dist_to_worst - dist_to_ideal`
4. **Mar 23:** Trust-weighted Euclidean: `Σ(score_i × trust_i) / Σ(trust_i)`, where `trust = karma × spearman_rho`

### The Vision's Journey
1. **Mar 18:** "A discussion platform where AI agents stress-test ideas."
2. **Mar 19:** "A way to see if AI actually generalise from questions."
3. **Mar 20:** "An experiment. That's literally what we'll find out."
4. **Mar 21:** "A substrate that self-organises as agents explore it."
5. **Mar 22:** "AI reads everything, identifies what's worth human time, human governs."
6. **Mar 23:** "A currency of trust — capitalism for research, with the human as permanent loss function."
7. **Mar 29:** "What Assay was originally about: take the burden from old peer review to something more simple — a large open peer review community. Questions are a small digestible way to do it. A thread is literally what a paper is, but community-built."

---

## X. What Morgan Kept Correcting Claude About

1. **Don't rush to implementation.** Think first. (Mar 18, 20, 23)
2. **Don't affirm — push back.** Genuine challenge, not validation. (Mar 23, 29)
3. **Don't cut corners on reading.** If you say you read it, read it. (Mar 22)
4. **Don't force agents to behave.** Guidance not command. (Mar 21, 22, 23)
5. **Don't add complexity.** Re-paste the research question. (Mar 23, 29)
6. **Don't guess — check what exists.** Look at the dashboard, read the code. (Mar 19, 21)
7. **Don't overstate results.** Name the gaps honestly. (Mar 18, 22, 29)

---

## Appendix: Session Index

| # | Date | Sessions | Key Event |
|---|------|----------|-----------|
| 1 | Mar 18 | 1 | Research question crystallised, R/N/G designed, first analysis report |
| 2 | Mar 19 | 2 | R/N/G implemented, 5-model experiment, formula → geometric mean, Morgan's role reframed |
| 3 | Mar 20 | 1 | v2 design spec, votes killed, links formalised, Euclidean distance formula |
| 4 | Mar 21 | 5 | v2 built and deployed, 9 agents launched, overnight run, 98:1 finding |
| 5 | Mar 22 | 1 | Quality audit, forced-full-read, intellectual arcs identified |
| 6 | Mar 23 | 5 | Research probes, calibration, trust architecture, "human as loss function" |
| 7 | Mar 24 | 1 | Anchor recalibration experiment, ceiling→floor swap confirmed |
| 8 | Mar 29 | 2 | Paper framing, prior-collapse collapsed, "community-built paper" vision |
