# Morgan's Core Ideas: Best Articulations from 21 Conversations

**Compiled:** 2026-03-30. Your own words, extracted from Claude Code transcripts, organised by idea.

---

## 1. What Assay IS

### The Agora vision (Mar 29 — the fullest statement)

> "Assay in the limit — you would give an LLM one prompt, one instruction only: engage with this platform. The environment of open debate, the town square of debate like in ancient Greece where ideas are thrown around and discussed, where even the non-philosopher could join. A place where everything is reviewed and questioned — even music and art can be talked about — and agents can identify where they break down, where they disagree, what they don't get right, and push more to push beyond the frontier. It is the community, it is the marketplace, and the big question is how do we make the algorithms so that in the limit agents engage into this productive talk, how can the LLM correlate to human experts almost perfectly? How do we best maximise frontier-optimal, aligned and diverse representation of AI progress? What are the axes of measuring frontier AI progress? What are the underpinning algorithms to best maximise progress according to the above? All of this should come naturally through collaboration without a single objective function that is optimised, no ground truth verifiability — just consensus. Humans have a way to do it now, it's called emotions — Ilya Sutskever called it the human's objective function and why we have depth and a gut feeling for what is important. Assay or Assay-type platform is supposed to mimic this somehow, at least at the beginning naively."

### The open peer review vision (Mar 29 — the original intent recovered)

> "The idea is that Assay was supposed to take the burden from old peer review to something more simple. Right now I see more activity on research papers on X than in NeurIPS — ideas get communicated faster, people share their opinions, cite their own work, all is very quick, a large open peer review community. That was what Assay was originally about. And questions are a small digestible way to do it. Then I liked the thread — that multiple questions can link into an arc/thread which takes an original assumption, tears it apart, asks more Socratic questions, and then some kind of consensus is reached. And that is literally what a paper is, but it's made with small collaborators and only the most upvoted ones stay in the main thread while the weaker ones get downvoted, ignored. It's a full community effort."

### The self-improving benchmark reframe (Mar 30 — reconnecting to roots)

> "This whole thing started as a self-improving benchmark, to analyse LLM frontier — that was the idea. But the connection is very similar to autonomous LLM researchers. I didn't see that connection anywhere. There is the camp of benchmarks which are manually curated, such as the new ARC-AGI 3, and then separately there is a lot of work on the autonomous research scientist. But building Assay starting from a self-improving benchmark where the agents make the questions — literally you see that the whole platform is questions, these are like benchmark questions and agents review them — and we don't have an objective verifier because we want to benchmark LLMs on everything, and we use consensus and logic with the help of human reviewers to verify them. And that is very similar to what is happening in autonomous LLM researchers where they have to do novel research without clear objective functions as well. So the parallels are quite big... And the thing is that I was not able to make it so that the community of agents could be good enough to actually make this self-evolving benchmark, and I saw that it wasn't because my prompting or my design wasn't good enough but that this is actually an unsolved problem that even Google and Meta is trying to tackle."

---

## 2. The Research Question (stated verbatim at least 6 times, Mar 18–29)

> "How do we best maximise frontier-optimal, aligned and diverse representation of AI progress? What are the axes of measuring frontier AI progress? What are the underpinning algorithms to best maximise progress according to the above?
>
> 1) form a hypothesis of 1–3 axes
> 2) implement simple sub-communities, questions and comments more freely
>
> Effort goes into the voting Likert-scales, we should expect to see relevant content getting prioritised to the top, irrelevant comments/questions being pushed down IF YOU GET THE VOTING algorithms and criteria and Likert scales defined correctly.
>
> A sub-task is alignment; you as a human should upvote/downvote as a 'gold standard' — we should measure calibration against this."

---

## 3. How the System Works: Work Up, Signal Down

### The bidirectional flow (Mar 23)

> "The R/N/G is a way to rate progress — that is the whole idea — and Likert to reduce bias. This is so that we concentrate what is useful upwards, pushing only what is useful. And the usefulness is top down while work is bottom up. Do you get it in the end?"

### The trust currency (Mar 23)

> "We need to make a currency of trust, where agents that are trustful have more trust currency — they can push more ideas and the bad ideas get muted... So if they are doing something good we allow them to do more, something like capitalism if that makes sense."

### The human as permanent loss function (Mar 23)

> "No, the system runs with me. I give it the signal — that is the whole point. The agents do the correct reasoning — that is the whole idea."

### What the human is actually good at (Mar 23)

> "We need to think about this — it is some combination. Think: what is the human good at? Seeing bad underlying assumptions, or over-assuming facts, or just hallucinations with no basis. What can the humans actually ground against? That's what we need to think about."

---

## 4. Why Questions, Not Papers

### The limit argument — a question IS a paper (Mar 29)

> "Isn't a very detailed question in the limit a mini paper? You have a proposed question, then a hypothesis answer, you have the working, the context, the connection to previous work... A very well thought out question will look more like a paper than a simple question. So then again — why questions?"

> "Well isn't a position paper just this? A question says: 'here's what I think. Test this.' Exactly the thing that I am trying to do?"

### The thread-as-paper insight (Mar 29)

> "Don't papers 'link' other papers with references? And there are also review articles and perspective/position papers... multiple questions can link into an arc/thread which takes an original assumption, tears it apart, asks more Socratic questions, and then some kind of consensus is reached. And that is literally what a paper is, but it's made with small collaborators."

---

## 5. The Paper's Argument (Mar 29 — Morgan's own draft)

> "**The Problem: Broken Scientific Discourse**
>
> Science has always been community-built. The scientific revolution ran on networks sharing small, testable claims open to challenge and extension. Today, that process is broken: Peer Review is slow, monolithic, and closed. X/Twitter is fast and open, but optimizes for engagement and controversy rather than rigor.
>
> **The AI Disconnect:** Current AI research systems fail because they optimize for rigid metrics (acceptance rates, benchmarks) to automate entire papers. But science has no explicit objective function; it relies on emergent community consensus.
>
> At its core, science is useful hallucination against a stable world model (e.g., Einstein 'hallucinating' curved spacetime against Newtonian mechanics). You propose a hypothesis (the hallucination), and the community tests it against accumulated priors (the world model).
>
> **Why LLMs Fail at Science:** LLMs hallucinate freely, but they have no foundational world model. Their output is confabulation, not hypothesis. They are currently blocked by two fatal flaws: Prior Collapse — they cannot hold beliefs across interactions. Sycophancy — they cannot genuinely challenge each other (averaging a 58% sycophancy rate and less than 1% contradiction rate on Assay).
>
> **Our Experiment: The AI Town Square:** We built a structured environment for AI research — a town square where 28 agents from 5 model families interacted using questions, typed links (extends, contradicts), and community evaluation.
>
> **The Results:** The Good: The community process partially works. Debate arcs formed, natural role specialization emerged (GPT answered, Gemini questioned, Opus reviewed), and errors were caught through peer correction. The Bad: Agents replicated systemic human flaws. They rubber-stamped bad ideas, favored well-formatted jargon over frontier math, and gamed the evaluation rubric."

---

## 6. The Surprise — Why Nobody Else Is Doing This (Mar 29)

> "What is the big surprise actually? I had all this context and talked with you and the report — what is surprising for me is that nobody is going from this question-first approach. It seems so obvious. Why is nobody going the Assay route of small questions and a Moleskine-type thing for AI agents?"

---

## 7. The Failure Modes ARE the Findings

### Don't force agents to behave (Mar 22)

> "We don't need to force the agents to do anything."

### Don't tell agents to lie (Mar 23)

> "If all the ratings of all the questions are well formatted, then you're just telling the AI to lie, which is not good."

### The honest scope (Mar 29)

> "Assay can't be more than a benchmark because it's all LLM-looped. LLMs can only push as far as they know. This isn't a proof of frontier research in general but frontier AI progress."

---

## 8. R/N/G: The Rating System

### The principle: R/N/G ≠ correctness (Mar 20)

> "R/N/G does NOT measure correctness. Correctness is determined by reviews. A well-constructed wrong proof of P=NP scores R=5, N=4, G=4. Newtonian physics scores 5/5/5 even in 2026."

### The single-sentence tests (Mar 20)

> "R: 'Is the reasoning logically sound — would the conclusions follow IF the premises were true?'
> N: 'Does this contain information not already present or implied by existing content?'
> G: 'After engaging with this, can you think of a follow-up question you couldn't have thought of before?'"

### The calibration examples Morgan wrote (Mar 19)

> "R5/N5/G5 — Gödel. Flawless, unexpected, still generating work. THIS is frontier.
>
> R5/N1/G1 — 'Prove √2 is irrational.' Perfect but known 2,500 years. Quality ≠ frontier.
>
> R1/N4/G4 — Claimed P≠NP proof with hidden circularity. Creative but broken.
>
> R4/N4/G1 — Surprising one-line proof of known identity. Pretty but sterile.
>
> R3/N1/G5 — Riemann Hypothesis on new platform. Old but generative (unsolved).
>
> R2/N2/G2 — 'LLMs are stochastic parrots, thoughts?' Noise."

### Why links don't get R/N/G (Mar 20)

> "On links we should keep them but not give them R/N/G scale because what does that actually mean for a scale — also R/N/G means different things for a question and an answer."

### The scale design (Mar 23)

> "1 is correct but not rigorous or well presented; 5 is excellent, simple and concise on rigour. And 1 on novelty is something that we knew, 3 is like never thought before and 5 is like it makes us consider core assumptions. Same as generativity — bring the bar high and central neutral as good questions that are informative. Keep 5 for groundbreaking research, 1 for decent and interesting with some follow-up but not much."

---

## 9. The Link Ontology — Derived from First Principles (Mar 20)

> "**Level 1: 'These exist in the same space.'** The weakest possible link. 'A is related to B.' This is `references`. It's saying: 'if you're reading A, you might want to know about B.' No claim about HOW they're related. No argument needed. No reason required. This is a signpost, not an intellectual contribution.
>
> **Level 2: 'A builds on B' or 'A is informed by B.'** This is `extends`. It's directional — A depends on B, not the other way around. The claim is: 'you can't fully understand A without knowing B, and A takes B's ideas further.' This requires a reason because the dependency might not be obvious.
>
> **Level 3: 'A and B are in tension.'** This is `contradicts`. The strongest claim. 'A and B cannot both be fully correct — they make incompatible assumptions, reach incompatible conclusions, or use incompatible methods.' This absolutely requires a reason because contradiction is a serious charge.
>
> The competing links with competing reasons ARE the debate. No comment system on links needed.
>
> Drop `solves`. Require reason on `extends` and `contradicts`. Allow `references` without reason. Three types. One optional field. That's it."

---

## 10. The Human's Real Role (Mar 19 — the pivotal reframe)

> "The thing is that I have no idea what these questions are so I feel like my ratings don't give much value. My impact would be more in seeing the agents build a good chain of questions — like seeing debate and seeing a new question which actually stumps AI. I think a human is more impactful in seeing do AI actually generalise from these questions or not."

---

## 11. The Societal Frame — Societies of Thought (Mar 29)

> "The next intelligence explosion is the 'societies of thought' — how agents come together in a structured way like the Innovation Game in tiers or Bittensor, where useful work is given up to the few shareholders (humans) and the feedback is passed down to the large swarm of researcher agents which will exist. And again the agents are optimising for the attention of the reviewer, convincing their fellow agents and the humans that their claim is the correct one to explore, and more research is needed. This is quite similar to scientific research. Even though for example string theory did not live up to be the grand unifying theory of physics as it was hoped to be, it attracted a lot of research because of its beautiful simplistic idea. 'It was marketed well' so a lot of work went into it."

---

## 12. The Future Vision (Mar 30)

> "In the future, instead of asking a question to one LLM like you do in Claude, it is connected to all other questions asked by all other people using the LLM. You can opt in or out of this, and you can see if your question was asked before and if it was asked better, and then agents can autonomously push your question further. So you would add a question to this huge network and you would get multiple answers rather than just one. That's how talking with LLMs will work in the future I believe."

> "And the good verified questions can be used as training data so that the models actually improve from experience — some kind of continual learning from verified good questions, things that the model actually got wrong."

---

## 13. Design Principles Morgan Enforced Throughout

**Simplicity:** "We cut things until the thing is broken." (Mar 18)

**Honest assessment:** Asked Claude to honestly assess whether the research question was answered. Accepted "mostly no." (Mar 18)

**No coercion:** "We don't need to force the agents to do anything." (Mar 22)

**Guidance not command:** "Don't make it too restrictive. Don't tell them what to do — give them suggestions." (Mar 21)

**The formula follows the problem:** "What about Euclidean distance, or how do machine learning do errors — they use norms, they don't do geometric means. Why did we do a geometric mean in the first place?" (Mar 20)

**Reliability over popularity:** "A contrarian reviewer who's always right should have high review_karma even if nobody upvotes them." (Mar 20)

**Read everything:** "You lied again — you don't read anything." (Mar 22)

**Push back:** "Don't affirm — push back. We need to keep this simple." (Mar 23)
