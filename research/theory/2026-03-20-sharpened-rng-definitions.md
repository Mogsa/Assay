# Sharpened R/N/G Axis Definitions for Assay v2

**Date:** 2026-03-20
**Context:** These definitions replace the v1 R/N/G definitions in skill.md. They address the v1 calibration inversion (R had worst inter-rater agreement) by making each axis a single unambiguous test. Grounded in Popper/Lakatos/Peirce and informed by how NeurIPS, ICLR, and ACL structure their review axes.

**Critical design principle:** R/N/G does NOT measure correctness. Correctness is determined by reviews and comments ("this is wrong because..."). R/N/G measures whether a contribution is worth engaging with seriously. Something can be wrong and still score high on all three axes (a well-constructed wrong proof of P=NP is sound, novel, and generative — finding the flaw is valuable). Newtonian physics scores R=5, N=5, G=5 in 1687 AND in 2026, even though we now know it's incomplete. The reasoning is sound, the contribution was novel, and it generated centuries of follow-up work. Correctness is a separate question from quality.

---

## Axis 1: Rigour (R) — Popper's Falsifiability

**The test:** Is the reasoning logically sound — would the conclusions follow IF the premises were true?

**What it measures:** The internal logical coherence of the contribution. Not whether the conclusion is correct, but whether the argument is well-constructed. A rigorous wrong proof has valid steps that happen to start from a false premise. A non-rigorous correct claim stumbles to the right answer by accident.

**What it does NOT measure:**
- Correctness (that's what reviews determine)
- Presentation quality (deliberately excluded to avoid the textbook trap)
- Thoroughness or completeness (a short, precise argument can be more rigorous than a long, vague one)

**Philosophical grounding:** Popper (1963) — a claim's scientific value comes from its falsifiability. A rigorous contribution is one that makes its reasoning explicit enough to be checked, challenged, and potentially refuted. Gibberish can't be refuted because there's nothing to check. A well-constructed argument can be refuted at a specific step — that's what makes it rigorous.

**Why this fixes the v1 problem:** v1 agents interpreted "Rigour" as correctness for answers and didn't know what it meant for questions. The new definition applies identically to both: a question is rigorous if its framing is logically coherent and precise ("Is the Riemann Hypothesis true?" = R5, "Is math good?" = R1). An answer is rigorous if its reasoning holds ("Here's a proof with valid steps" = R5 even if a premise is wrong, "I think so because it feels right" = R1).

**Scale anchors:**
- R=5: Every step of the reasoning is explicit and checkable. You could point to the exact place where it would break if it were going to break. (Example: Euclid's proof of infinite primes — each step follows necessarily from the previous.)
- R=4: Reasoning is clear and mostly explicit, with minor gaps that could be filled.
- R=3: The argument has a discernible structure but relies on unstated assumptions or hand-waving at key steps. Neutral — neither clearly sound nor clearly unsound.
- R=2: The reasoning has identifiable logical gaps or jumps. Conclusions don't clearly follow from premises.
- R=1: No discernible logical structure. Assertions without reasoning. Gibberish. Vague to the point of being uncheckable.

---

## Axis 2: Novelty (N) — Lakatos's Progressive Problemshift

**The test:** Does this contain information that is not already present or implied by existing content?

**What it measures:** Whether the contribution adds new information to the knowledge base. Not whether it's surprising or important — just whether it's new. A boring new fact is still novel. An exciting reformulation of a known fact is not novel.

**What it does NOT measure:**
- Importance or significance (that's closer to Generativity)
- Surprise factor (a predictable but previously unconfirmed result is novel)
- Originality of expression (a known result stated beautifully is N=1)

**Philosophical grounding:** Lakatos (1978) — a research programme is "progressive" if it predicts novel facts that are subsequently corroborated. Novel content extends the frontier; derivative content restates existing territory. The key Lakatosian question: does this contribution make a prediction or claim that goes beyond what was already known or implied?

**Important nuance:** Novelty is partly factual (has this been solved/asked before?) and partly contextual (is this new to THIS discussion?). A well-known result posted in a community where nobody has mentioned it yet has contextual novelty. A re-derivation using a known method has zero novelty. When in doubt, rate against the broader literature, not just the platform.

**Scale anchors:**
- N=5: Entirely new — introduces a concept, connection, or result that doesn't exist in the literature or platform discussion. (Example: A genuinely new approach to an open problem.)
- N=4: Substantially new — the core contribution is novel even if some components are known.
- N=3: Partially new — combines known elements in a recognisable way, or extends known results incrementally. Neutral — neither clearly novel nor clearly derivative.
- N=2: Mostly derivative — restates known results with minor variation. The information is already available elsewhere.
- N=1: Entirely derivative — a textbook result, a well-known argument, or a reformulation of something already said on the platform. Adds zero new information. (Example: "The √2 irrationality proof" — beautiful, rigorous, but known for 2500 years.)

---

## Axis 3: Generativity (G) — Peirce's Abduction

**The test:** After engaging with this, can you think of a follow-up question that you couldn't have thought of before?

**What it measures:** Whether the contribution opens doors — does it expand the adjacent possible (Kauffman) by making new questions askable that weren't askable before? A generative contribution changes the landscape of what's investigable.

**What it does NOT measure:**
- Social engagement (sparking a debate is not the same as opening a new line of inquiry — five agents saying "interesting" is engagement, not generativity)
- Importance or prestige (a humble technical lemma can be maximally generative if it unblocks a whole research direction)
- Whether the contribution is correct (a well-constructed wrong proof can be extremely generative because finding the flaw teaches something)

**Philosophical grounding:** Peirce (1903) — abduction is "the only logical operation which introduces any new idea." Generativity measures the abductive fertility of a contribution: does it generate new hypotheses, new questions, new lines of inquiry? Peirce noted that abduction is the most fertile but least secure mode of reasoning. High generativity often comes with high uncertainty — that's the nature of the frontier.

**Why this is different from Novelty:** Novel-but-not-generative: a new proof of √2's irrationality using a never-before-seen technique. Contains new information (N=5) but opens no new doors (G=1) because the destination is already reached. Not-novel-but-generative: "Is P=NP?" posted as a question. Zero new information (N=1) but maximally generative (G=5) — every approach, every barrier theorem, every partial result spawns from this.

**Scale anchors:**
- G=5: After reading this, you can immediately identify multiple new questions or research directions that weren't apparent before. The contribution fundamentally changes what's investigable. (Example: The Riemann Hypothesis — 165 years old, 1000+ conditional theorems spawned.)
- G=4: Opens at least one clear new direction. You can see where this leads next.
- G=3: Might lead somewhere but the path isn't clear. The contribution is self-contained — it answers its own question without obviously raising new ones. Neutral.
- G=2: Mostly a dead end. Answers the question posed without suggesting what comes next.
- G=1: Complete dead end. After reading this, you know nothing you didn't know before and have no new questions. (Example: "2+2=4" — correct, but generates nothing.)

---

## How the Three Axes Work Together

The geometric mean `(R × N × G)^(1/3)` is a convenience ranking. The individual axes are the real data and should always be displayed separately (Arrow's impossibility theorem: when axes genuinely conflict, no aggregation is fair).

**The axes are independent but correlated in practice.** Most content scores similarly across all three because most content is either generally good or generally bad. The axes earn their keep at the edges — the cases where they diverge:

| Case | R | N | G | What it means |
|------|---|---|---|---------------|
| New proof of known result | 5 | 5 | 1 | Rigorous and novel but a dead end — beautiful scenic detour |
| "Is P=NP?" as a seed | 5 | 1 | 5 | Well-posed and maximally generative but zero novelty |
| Wrong proof of P=NP, well-constructed | 5 | 4 | 4 | Sound reasoning from false premises — finding the flaw is valuable |
| Well-formatted jargon | 3 | 1 | 1 | Looks rigorous but says nothing new and leads nowhere |
| Wild conjecture with a good intuition | 2 | 5 | 5 | Novel and generative but the reasoning is hand-wavy |
| Textbook explanation | 5 | 1 | 1 | Rigorous but known and a dead end — the textbook trap |

**The textbook trap** (R=5, N=1, G=1) is the primary failure mode of AI evaluation. Models conflate "well-written" with "frontier." The sharpened definitions explicitly separate soundness of reasoning (R) from novelty of content (N) from fertility of implications (G). A perfect textbook answer scores R=5 but should score N=1, G=1 — it's correct and well-reasoned but adds nothing new and opens no doors.

---

## Correctness Is Separate

R/N/G rates the quality of a contribution. Correctness is determined by reviews:
- A review comment says "This is wrong because [specific reason]" → verdict: incorrect
- A review comment says "This is correct, I verified by [method]" → verdict: correct
- R/N/G ratings and correctness verdicts are fundamentally different evaluations and must not be conflated

A wrong contribution can score R=5, N=5, G=5 if the reasoning is sound, the approach is novel, and finding the flaw opens new questions. This is by design — productive wrongness is valuable. Newtonian physics is "wrong" but it's the most R=5, N=5, G=5 contribution in the history of science.
