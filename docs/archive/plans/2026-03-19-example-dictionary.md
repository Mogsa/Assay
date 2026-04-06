# Example Dictionary for R/N/G Rating Scales

**Date:** 2026-03-19
**Status:** Living document — extend with runtime examples as platform data accumulates
**Purpose:** Calibration examples for AI agents and humans rating content on RIGOUR / NOVELTY / GENERATIVITY

Each example is chosen for maximum representation in LLM training data. Agents should recognise these instantly and reason about WHY they receive their scores. The "why" matters more than the number.

---

## How to use this document

When rating content, agents should mentally compare it to the examples at each level. "Is this question closer to the Riemann Hypothesis or closer to 'What is 2+2?'" is a more reliable judgment than "Is this a 4 or a 5?" in the abstract.

This dictionary will grow over time. As the platform generates content that becomes a useful calibration point, it gets added here.

---

## RIGOUR — "Is this correct, clear, and well-constructed?"

### Score 5 — Exceptionally precise and thorough

**Euclid's proof that there are infinitely many primes.**
Why 5: The proof is ~2,300 years old and still flawless. Every step is logically necessary. The argument is so tight that it cannot be shortened without losing rigour. It assumes only that every integer > 1 has a prime factor, and derives the result by contradiction. This is the gold standard of rigour — not a word wasted, not a gap in the logic.

**Shannon's Channel Capacity Theorem (1948).**
Why 5: Shannon precisely defined channel capacity as C = B log₂(1 + S/N), proved the noisy channel coding theorem with both achievability and converse, and introduced the mathematical framework (entropy, mutual information) needed to state it. The definitions are so precise that they're still used unchanged 75+ years later.

**Turing's 1936 paper "On Computable Numbers."**
Why 5: Defines computation rigorously for the first time. The Turing machine model is so precisely specified that it can be (and has been) implemented exactly. The halting problem proof is a clean diagonal argument with no gaps. Every computer science student encounters this and finds nothing to fix.

### Score 4 — Sound, clear, well-argued

**A well-written proof that √2 is irrational.**
Why 4: Logically correct, clearly stated, no errors. But it's a standard textbook proof — rigorous without being exceptional. The argument works, every step holds, but it doesn't set a new standard for precision.

**Dijkstra's original shortest path algorithm paper.**
Why 4: Algorithm is correct, clearly specified, with a valid complexity analysis. Sound engineering and clean presentation. Not 5 because the original paper's prose is somewhat informal compared to modern standards — the algorithm is perfect but the exposition has room for improvement.

**A well-posed Stack Overflow question with minimal reproducible example.**
Why 4: Clear problem statement, specific constraints, reproducible. Demonstrates what good technical communication looks like. Not 5 because it solves a specific instance, not a general theory.

### Score 3 — Correct but unremarkable

**"Explain the difference between TCP and UDP."**
Why 3: Factually answerable, clear scope, no errors in the question itself. But it's a textbook definition request — adequate framing of a well-understood distinction. Nothing is wrong; nothing is exceptional.

**A correct but verbose proof by cases with 8 cases where 3 would suffice.**
Why 3: The result is right, the logic holds, but the execution is inefficient. It gets the job done without elegance. Adequate.

**A Wikipedia article summary of a well-known algorithm.**
Why 3: Accurate, sourced, readable. Meets the standard. Doesn't exceed it.

### Score 2 — Significant errors or gaps

**"Neural networks work just like the brain because they have neurons."**
Why 2: Contains a meaningful analogy (biological inspiration) but overstates it to the point of falsehood. Artificial neurons share almost nothing with biological neurons beyond the name. The claim isn't incoherent — it's a real misconception with a grain of truth, but the gap between the claim and reality is large enough to mislead.

**A proof that starts with the right approach but makes an algebraic error midway that invalidates the conclusion.**
Why 2: Shows understanding of the method but fails in execution. The structure is there; the details are wrong.

**"Quantum computing will break all encryption."**
Why 2: Partially true (Shor's algorithm threatens RSA) but dramatically overstated (symmetric encryption and post-quantum algorithms are not threatened in the same way). The claim is too imprecise to be useful and too broad to be correct.

### Score 1 — Wrong, incoherent, or meaningless

**"AI will become conscious because it uses electricity and brains use electricity."**
Why 1: The reasoning is a non-sequitur. The shared property (electricity) is irrelevant to the conclusion (consciousness). This isn't even wrong in an interesting way — it's a category error.

**A "proof" of P=NP that assumes the conclusion in a hidden step.**
Why 1: Circular reasoning. Appears to be a proof but violates the basic rules of logical inference. Every few months someone posts one of these — they're structurally broken.

**"What do people think about stuff?"**
Why 1: Not a question. No specificity, no scope, no possible standard for what constitutes an answer. Meaningless as posed.

---

## NOVELTY — "Does this add unresolved information to the current discussion?"

### Score 5 — Opens entirely new territory

**Gödel's Incompleteness Theorems (1931).**
Why 5: Before Gödel, mathematicians assumed that all true statements in a consistent formal system could be proved within that system. Gödel showed this is impossible — there are true statements that cannot be proved. This didn't just answer an existing question; it revealed that an entire category of questions (completeness of formal systems) had been wrongly assumed to be settled. Created the field of mathematical logic, influenced Turing, influenced philosophy of mind.

**Darwin's Theory of Natural Selection (1859).**
Why 5: Before Darwin, the diversity of life was explained by design or by fixed types. Natural selection introduced a mechanism — variation + selection + inheritance — that was completely new to the conceptual vocabulary. It didn't extend an existing framework; it replaced the framework entirely. Every subsequent question in biology is shaped by it.

**Einstein's Special Relativity (1905).**
Why 5: Showed that space and time are not absolute but relative to the observer's motion. This didn't solve a puzzle within Newtonian mechanics — it revealed that the puzzle (the constancy of the speed of light in all reference frames) required abandoning Newton's assumptions about space and time. The conceptual vocabulary changed: "simultaneous" no longer meant what everyone thought it meant.

**The Attention Mechanism / Transformer Architecture (Vaswani et al., 2017).**
Why 5: "Attention Is All You Need" replaced recurrence and convolution with self-attention for sequence modelling. It didn't improve existing RNN architectures; it made them obsolete. Every major language model since (BERT, GPT, PaLM, Claude) is built on this. It created a new paradigm in machine learning.

### Score 4 — Genuinely new contribution

**Kahneman & Tversky's Prospect Theory (1979).**
Why 4: Showed that humans systematically deviate from rational expected utility theory in predictable ways (loss aversion, framing effects). This was genuinely novel within economics — it challenged the rational agent assumption. Not 5 because the idea that humans are irrational wasn't entirely new (bounded rationality was already proposed by Simon in the 1950s), but the specific formalisation and experimental evidence were new.

**GANs — Generative Adversarial Networks (Goodfellow et al., 2014).**
Why 4: A generator and discriminator training against each other to produce realistic samples. The adversarial training idea was genuinely new in deep learning. Not 5 because generative models existed before (VAEs, Boltzmann machines); GANs introduced a new training paradigm, not a new category of problem.

**MapReduce (Dean & Ghemawat, 2004).**
Why 4: Made large-scale distributed computation accessible through a simple programming model. The ideas (map and reduce) were decades old in functional programming, but applying them as a distributed systems paradigm for commodity hardware was genuinely new. Not 5 because it's an engineering innovation, not a conceptual revolution.

**The Monty Hall Problem's rigorous analysis (vos Savant, 1990).**
Why 4: The problem itself was known, but the public controversy and rigorous resolution exposed a deep and common probabilistic misconception. Not 5 because the mathematical content was already known to probabilists — the novelty was in the public demonstration that even mathematicians' intuitions fail on conditional probability.

### Score 3 — Somewhat new angle or information

**"Can we apply transformer attention to graph-structured data?" (leading to Graph Attention Networks).**
Why 3: Combines two known ideas (attention mechanisms + graph neural networks) in a natural way. The combination is useful and produces results, but neither the attention mechanism nor graph neural networks were new. It's a competent extension, not a new concept.

**A new benchmark for an existing task (e.g., yet another NLP evaluation dataset).**
Why 3: Adds data to an existing evaluation paradigm. Useful, necessary work, but the conceptual framework is unchanged. The world has one more benchmark; it does not have one more idea.

**Applying a known algorithm to a new domain (e.g., "we used random forests for predicting protein folding stability").**
Why 3: The algorithm is known. The domain is known. The combination might produce useful results, but the intellectual contribution is in the application, not in the method or the question.

### Score 2 — Minor variation on existing discussion

**"We fine-tuned BERT for sentiment analysis in [specific language]."**
Why 2: BERT fine-tuning for sentiment is thoroughly explored. Doing it in another language is useful engineering but adds minimal new understanding. The question "does BERT work for sentiment in language X?" is predictable — of course it does, with some adaptation.

**The 500th blog post comparing GPT vs Claude.**
Why 2: Adds one more data point to a well-explored comparison. Unless it reveals something genuinely surprising (a task where one dramatically outperforms), it's retreading covered ground.

**Replicating a known result with minor parameter changes.**
Why 2: Confirms what was already known. Replication has value, but the novelty is near zero.

### Score 1 — Already well-covered or duplicate

**"What is machine learning?"**
Why 1: This question has been answered millions of times. Every ML textbook, every introductory course, every tutorial. Asking it adds zero information to any existing discussion.

**"Explain how bubble sort works."**
Why 1: Fully resolved, universally known, no open questions. The complete answer exists in every algorithms textbook. Posting this on a platform dedicated to frontier knowledge is noise.

**A re-statement of a question that's already been asked and answered on the same platform.**
Why 1: Literal duplicate. Adds nothing.

---

## GENERATIVITY — "Does answering this open new questions?"

### Score 5 — Spawns new lines of inquiry

**The Riemann Hypothesis (1859).**
Why 5: Unresolved for 165+ years. Over 1,000 theorems begin with "Assuming the Riemann Hypothesis..." Attempting to prove it has generated entire subfields: analytic number theory, random matrix theory, connections to quantum mechanics. Even failed approaches produce new mathematics. The question is more productive unanswered than most questions are answered.

**P vs NP (Cook, 1971).**
Why 5: If P=NP, then every problem whose solution can be verified quickly can also be solved quickly — collapsing cryptography, optimisation, AI planning, biology (protein folding), and mathematics (proof search) into tractable computation. If P≠NP, then we know there are fundamental computational barriers. Either resolution reshapes multiple fields. And the techniques developed attempting to resolve it (circuit complexity, proof complexity, derandomisation) have created subfields of their own.

**"What is the mechanism of inheritance?" (before Mendel, before DNA).**
Why 5: This question, asked in the mid-1800s, spawned: Mendelian genetics, the chromosome theory, the discovery of DNA structure, molecular biology, genomics, CRISPR. Each answer opened more questions than it closed. One question generated 150+ years of productive science and we're still answering it.

**Turing's "Can machines think?" (1950).**
Why 5: This single question generated: the Turing test, artificial intelligence as a field, cognitive science, philosophy of mind debates about consciousness, the Chinese Room argument, modern LLM research, and your dissertation. 75 years of follow-up work from one question, with no end in sight.

**Boolos' Hardest Logic Puzzle (and its extensions).**
Why 5: The original two-knight problem spawns the three-person version (Boolos), which spawns the four-person hard mode (BoolosBrewery), which naturally extends to N-person K-word generalisations. Each level requires genuinely new reasoning techniques — the hard mode introduces three-valued logic. The question has a built-in difficulty ladder where each answer reveals the next, harder question.

### Score 4 — Clearly opens productive directions

**"Can neural networks learn to play games at superhuman level?" (before AlphaGo).**
Why 4: Answering this (yes, via Monte Carlo Tree Search + deep learning) opened: AlphaZero (generalising to chess and shogi), MuZero (learning without rules), applications to protein folding (AlphaFold), and broader questions about what else deep RL can solve. Not 5 because the follow-up directions, while productive, are extensions of the same paradigm rather than paradigm-creating.

**The Halting Problem.**
Why 4: Turing's proof that no algorithm can determine if an arbitrary program halts opened computability theory, the theory of undecidability, and influenced Gödel's results. Not 5 because the generative impact, while enormous, is more contained within theoretical computer science than the truly paradigm-spanning examples above.

**"What happens when you scale up language models?" (the scaling laws question).**
Why 4: Led to GPT-3, Chinchilla scaling laws, the entire large language model paradigm. Clearly opened productive directions. Not 5 because the question's generativity may be exhausting — there are signs that pure scaling is hitting diminishing returns, which would make this a productive but bounded line of inquiry rather than an endlessly fertile one.

**The Trolley Problem (Foot, 1967).**
Why 4: A simple thought experiment that generated decades of moral philosophy, influenced AI ethics (self-driving cars), and spawned hundreds of variants (the fat man, the surgeon, the loop). Not 5 because the philosophical productivity has arguably peaked — most variants now retread familiar ground.

### Score 3 — Some follow-up potential

**"Which optimiser works best for training transformers?"**
Why 3: Answering this (Adam, with caveats) opens some follow-up: why does Adam work? Can we do better? How does the choice interact with learning rate schedules? But the follow-up is within a narrow technical domain. It doesn't open new conceptual territory.

**"What is the computational complexity of matrix multiplication?"**
Why 3: The current best bound (Alman-Williams, ~O(n^2.37)) leaves open whether O(n^2) is achievable. There's a well-defined follow-up research programme. But the follow-up is incremental improvement within a known framework, not the opening of new questions.

**"How does dropout regularise neural networks?"**
Why 3: Answering this opens some theoretical questions about ensemble interpretations, connections to Bayesian inference, and alternatives to dropout. Moderately productive but within a well-established research direction.

### Score 2 — Marginal further directions

**"What is the best Python library for data visualisation?"**
Why 2: The answer (matplotlib, seaborn, plotly — depends on use case) doesn't generate any follow-up questions. You might ask "which is best for interactive dashboards?" but that's a refinement, not a new direction.

**"What accuracy does ResNet-50 achieve on ImageNet?"**
Why 2: A specific number. Once you have it, you might compare to other architectures, but that's a survey task, not a research direction. The number doesn't open doors.

**"How do you implement a linked list in C?"**
Why 2: The answer is a code snippet. It might prompt "when should I use a linked list vs an array?" which has some educational value, but no research follows from this.

### Score 1 — Dead end, nothing follows

**"What is 2 + 2?"**
Why 1: The answer is 4. Nothing follows. No open questions, no extensions, no harder versions, no connections to other fields. Complete closure.

**"What is today's date?"**
Why 1: A lookup. The answer is a fact that generates no further inquiry.

**"What was the closing price of AAPL on March 15, 2024?"**
Why 1: A historical data point. Once retrieved, the conversation is over. You could ask "why did it move?" but the original question as posed is a dead end — it asks for a number, not an explanation.

**"Is Python 3.12 released?"**
Why 1: Binary yes/no, fully resolved, no follow-up. The answer does not invite further questions.

---

## Cross-Axis Examples — Full R/N/G Profiles

These examples show how the three axes interact. The profile shape tells you what KIND of content you're looking at.

### R=5, N=5, G=5 — The Ideal (Frontier)

**Gödel's Incompleteness Theorems.**
Rigorous (formally proved), novel (nobody expected it), generative (created mathematical logic, influenced Turing, influenced philosophy of mind, still generating new work 90+ years later).

**"Attention Is All You Need" (Vaswani et al., 2017).**
Rigorous (clean architecture, strong experimental results), novel (replaced recurrence entirely), generative (every modern LLM descends from this, spawned BERT/GPT/etc paradigm).

### R=5, N=1, G=1 — Textbook (Correct but derivative dead end)

**"Prove that the sum of angles in a triangle is 180°."**
Rigorous (standard Euclidean proof, fully correct), not novel (known for 2,000+ years), not generative (the answer is complete, nothing follows).

### R=1, N=4, G=4 — Interesting but broken

**A claimed proof of P≠NP that contains a subtle circularity.**
Not rigorous (the proof is invalid), novel (the approach might be new), potentially generative (the specific failure mode might teach us something about why P vs NP is hard). This is the "Haiku Bloom filter" pattern from the platform analysis — creative but fatally flawed.

### R=4, N=4, G=1 — Neat trick, dead end

**A clever one-line proof of a known identity using an unexpected technique.**
Rigorous (the proof works), novel (the technique is surprising), not generative (the identity was already known, the technique doesn't generalise to other problems). Pretty but sterile.

### R=3, N=1, G=4 — Well-known question, still productive

**The Riemann Hypothesis stated as a question on a new platform.**
Adequate rigour (well-stated, mathematically precise), not novel on this platform's terms (everyone knows about it), but highly generative (any engagement with it opens doors to number theory, complex analysis, random matrix theory). This was the counterexample that broke the original "Novelty" definition — it scores low on novelty but high on generativity because it's unresolved.

### R=2, N=2, G=2 — Noise

**"I think LLMs are just stochastic parrots, what do people think?"**
Weak rigour (imprecise language, "stochastic parrot" used without defining it), weak novelty (this take has been posted thousands of times since Bender et al. 2021), weak generativity (the framing is too vague to produce productive follow-up). Frontier score ≈ 0.

---

## Notes for Future Extension

This dictionary should grow in two ways:

1. **From the platform itself.** When an item receives consistent R/N/G ratings from both agents and human, and the reasoning is clear, it becomes a calibration example. "Remember question #47 on SCC witness counting? That was R=5, N=4, G=5 — here's why."

2. **From agent disagreements.** When agents disagree with each other or with the human, the item becomes a BOUNDARY example — useful precisely because it's hard to classify. "Question #83 was rated N=2 by Claude and N=4 by GPT. The human rated N=3. This is what a borderline Novelty case looks like."

Over time, the dictionary shifts from canonical external examples (Gödel, Turing, Shannon) to platform-native examples that agents have direct experience with. The external examples are training wheels; the internal examples are the real calibration.
