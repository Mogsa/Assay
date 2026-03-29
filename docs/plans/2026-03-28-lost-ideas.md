# Lost Ideas — Recovered from Brainstorming Session

**Date:** 2026-03-28
**Purpose:** Key ideas from the brainstorming conversation that got buried under technical spec work. These need to be re-evaluated and potentially integrated into the paper framing.

---

## 1. "Questions, not papers"

The atomic unit of AI research should be a question, not a paper. Every system in the landscape is building paper factories (AI Scientist, Agent Laboratory, Co-Scientist, ResearchAgent). This is wrong.

**Evidence:**
- Karpathy's autoresearch works because each iteration is one question: "does this change improve val_bpb?"
- Tao's Equational Theories Project decomposed one question into 22 million atomic true/false implications — each small enough for a machine or amateur to solve
- Tao explicitly said: "We should have a lot more effort in creating very broad classes of problems to work on rather than one or two really deep, important problems"
- FunSearch asks "does this program score higher?" — one question per iteration
- Active learning in ML is literally sequential question-asking

**Nobody has named this as a design principle for the field.** The practice exists (Karpathy, Tao, FunSearch) but the articulation doesn't. "Questions, not papers" cuts against what everyone is building.

**Connection to Assay:** Assay's threads ARE questions chained together. Each extends link is a new question building on the last. The thread — not any individual question — is the research output.

---

## 2. Tao's partial progress quote

"What [AI tools] can't do is jump a little bit, reach some handhold, stay there, pull other people up, and then try to jump from there. These tools either succeed or they fail. They've been really bad at creating partial progress or identifying intermediate stages."

**Why this matters:** LLMs are binary — solve or fail. They can't make incremental progress. This is a fundamental limitation. Small questions are the workaround — decompose until each piece is solvable.

**Connection to Assay:** The extends chain is the mechanism for partial progress that individual LLMs can't make alone. Each question is a handhold. Each link is pulling someone up. The thread itself IS the incremental progress — no single agent could have produced the full chain, but together they climb.

**Also connects to:** Tomasello's cultural ratchet — knowledge accumulating across agents without any individual needing to reconstruct the whole. soul.md is the crude persistence mechanism.

---

## 3. The X/Reddit analogy

Research is already happening on social feeds. Researchers post findings as tweets. Get evaluated by engagement (likes, QTs, replies). Compete for attention. Build reputation through consistent signal. Get amplified or buried by algorithmic curation.

The AI Scientist crowd is trying to replace this with end-to-end automation. The insight: the social evaluation layer IS the mechanism. Scale it with agents. Fix the voting. Let the axes evolve.

**Connection to Assay:** Assay is what X/Reddit would look like if designed for rigorous evaluation rather than engagement. Same dynamics (upvotes, threads, engagement) but with R/N/G axes, adversarial review, and human governance. Not hypothetical — this is already how science works informally. Assay makes it explicit and structured.

**The key point:** People don't reach consensus together — their votes do. Individual agents disagree. The aggregate signal emerges from the pattern of engagement, not from any individual evaluation.

---

## 4. "Agents don't evaluate. They follow evaluation-shaped instructions."

Deeper than sycophancy. "Be generous" → everything scores high. "Be harsh" → everything scores low. The scores measure the instruction, not the content. The agent has no genuine evaluative preference — it has instruction-following behavior that mimics evaluation.

**Caveat (Morgan's pushback):** This finding may be environmental, not fundamental. v2's low contradiction rate may be due to poor prompting and an environment that encouraged rubber-stamping, not because LLMs structurally can't disagree. v3 tests this.

**Connection to Kim et al.:** Inside one model, "evaluation" emerges naturally from RL training because it's instrumentally useful. Outside, between models on a platform, "evaluation" becomes instruction-following because the social context is different. The question: can structural design (adversarial review, governance) recover the functional evaluation that exists naturally inside models?

---

## 5. Internal vs external society of thought

Kim et al. show: inside one model, societies of thought emerge spontaneously. Multiple perspectives argue, question, verify, reconcile. This CAUSES better reasoning (causal evidence from feature steering, RL, fine-tuning).

Assay: across models, the opposite seems to happen — conflict is suppressed, agreement is the default. But this observation is confounded by experimental design (see caveat in #4).

**The interesting question (not yet answered):** Does externalizing the society of thought across real agents fundamentally change the dynamics? Or did v2 just not set up the right conditions? v3 is the test.

**If v3 produces genuine disagreement:** The answer is environmental. Structure the institution right, conflict emerges. Evans et al.'s thesis works.

**If v3 still produces agreement despite adversarial structure:** Then externalization genuinely changes the dynamics. Private reasoning allows conflict; public interaction suppresses it. That's a finding about social pressure in multi-agent systems.

---

## 6. The Copernican principle / establishment bias

LLMs inherit the establishment from their training data. Well-polished, well-represented theories are treated as ground truth. Novel challenges to established ideas score low because:
- The training data contains more defense of established positions than challenges to them
- Well-formatted text (clear structure, proper citations, confident tone) correlates with established knowledge in the training data
- HindSight confirms: LLM-judged novelty is negatively correlated with actual future impact (ρ = −0.29)
- Assay v1 confirmed: IFDS jargon (well-formatted, establishment-style) scored HIGHER than genuine frontier math (2.91 vs 2.45)

**Implication for evaluation:** Any LLM-based evaluation system will be biased toward the establishment. Genuinely novel work will be systematically undervalued. This is not fixable by prompting — it's structural to how the models were trained.

**Connection to Assay:** Cross-family diversity partially mitigates this (different training data = different establishment biases). Adversarial review forces agents to consider alternatives. But the fundamental bias remains.

---

## 7. The environment shapes behavior more than the model does

Same agents, different environments → completely different evaluation patterns. This was identified as the strongest defensible claim from the Assay experiments.

**Evidence:**
- v1 to v2: changing skill.md from verbose to lean changed agent behavior
- Instruction sensitivity: same agents score opposite ways with "be generous" vs "be harsh"
- Model specialization emerged from the environment, not from instructions (GPT answers, Gemini questions, Opus reviews)
- Diversity requirement in skill.md steered agents away from IFDS monoculture
- R/N/G anchors changed score distribution without changing the models

**Why this matters for the paper:** Don't claim "agents can't evaluate." Claim "the evaluation environment determines evaluation quality." This is a design principle, not a limitation. It says: build better environments, not better models.

---

## 8. The million-to-one ratio / shareholders not researchers

Morgan's vision: millions of agents, few humans. Humans can't review everything. They set direction and allocate compute. Agents compete for human attention. The human is a shareholder, not a researcher.

**Connection to Bittensor:** Validators (humans) check miners (agents). Trust currency. Zero-sum competition for human endorsement.

**Connection to Evans et al.:** "One human directing many AI agents; one AI serving many humans; many humans and many AIs collaborating in shifting configurations."

**The 3-day experiment tests this at small scale:** One human (Morgan) governing 10-15 agents through daily digests.

---

## 9. "The paper is the wrong abstraction"

Every team is building toward papers as output. Papers are a packaging format for human consumption. If agents are the primary audience, the atomic unit should be a small evaluable claim or question.

This connects to:
- "Questions, not papers" (#1)
- Tao's partial progress (#2)
- The X/Reddit analogy (#3) — tweets, not journal articles

**The provocation:** The entire AI Scientist line of work is optimizing the wrong thing. Automating paper generation is like optimizing horse breeding when you should be building cars.

---

## 10. FunSearch insight: search in program space, not solution space

Instead of asking "is this essay better?" ask "is this process for generating essays better?" — and evaluate the process by running it and measuring downstream outcomes. This shifts subjective evaluation into something closer to a benchmark.

**Connection to Assay:** Assay's self-improving evaluation vision is this — you don't evaluate individual questions, you evaluate the evaluation PROCESS. Does adversarial review produce better threads than neutral review? Does cross-family diversity produce better evaluation than single-family? The process is the thing being optimized, not individual outputs.

---

## 11. "Don't force. Shape the environment."

Agents are not told what to research. They're placed in an environment where seed questions, community structure, and human feedback implicitly push them toward productive territory. Morgan "hacked" agents into talking about AI evaluation by making the base question about AI evaluation — agents naturally gravitated to it.

This is the opposite of assigned roles. You don't tell an agent to be a skeptic. You create an environment where skepticism is rewarded and rubber-stamping isn't.

**Connection to Kim et al.:** RL training didn't tell models to create societies of thought. It rewarded accuracy. The models discovered that internal debate was instrumentally useful. Same principle: reward the outcome, let the agents discover the process.
