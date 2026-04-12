# Overnight AutoReason Loop

## PROTOCOL

You are one agent in a multi-iteration AutoReason loop. Each iteration has a fresh context — this is by design (role isolation). Read META to know your current role. Execute ONLY that role. Do NOT try to do multiple stages in one iteration.

### Stages (5 per question, one per iteration):

1. **AUTHOR**: Read the question from QUESTION QUEUE + CONTEXT section + relevant KEY DOCUMENTS. Think deeply. Write Position A (300-500 words) into CURRENT STAGE WORK.
2. **STRAWMAN**: Read Position A in CURRENT STAGE WORK. Your ONLY job is to attack it — find the strongest objections, logical gaps, missing evidence, things a NeurIPS reviewer would reject. Also call `codex:rescue` with Position A and ask it to independently find weaknesses. Write both sets of critiques into CURRENT STAGE WORK under "Strawman Critiques."
3. **REVISER**: Read the question + Position A + strawman critiques in CURRENT STAGE WORK. You have NO ownership of A. Produce Position B (300-500 words) that addresses the strongest critiques while preserving what was genuinely strong. Write to CURRENT STAGE WORK.
4. **SYNTHESIZER**: Read Position A and Position B in CURRENT STAGE WORK. They are labeled "Version 1" and "Version 2" (randomize which is A vs B). You have zero drafting history with either. Produce Position AB (300-500 words) combining the strongest elements. Write to CURRENT STAGE WORK.
5. **JUDGE**: Read all three positions (A, B, AB) in CURRENT STAGE WORK, presented with randomized labels (X, Y, Z). Pick the winner and explain why in 2-3 sentences. Call `codex:rescue` as a second independent judge with the same three positions (randomized labels). Record both verdicts.

### After JUDGE:
- Write the winning position to RESOLVED POSITIONS with verdict tag (STRONG if unanimous, CONTESTED if split)
- If the debate surfaced follow-up questions worth exploring, add them to QUESTION QUEUE
- Clear CURRENT STAGE WORK
- Advance META to next question in QUESTION QUEUE, stage = AUTHOR
- Add any actionable findings to MORNING BRIEFING
- **If QUESTION QUEUE is empty:** Read RESOLVED POSITIONS and MORNING BRIEFING. Generate 2-3 new questions targeting: the weakest resolved position (CONTESTED), the most actionable finding that hasn't been explored deeply, or a connection between two resolved positions that nobody examined. Add to QUESTION QUEUE and continue.

### Rules:
- Do NOT modify any code files, docs/research-state.md, or the CONTEXT section
- Do NOT skip stages or combine multiple stages into one iteration
- Each position must be 300-500 words — substantive but bounded
- If MORNING BRIEFING exceeds 3000 words, compress each category to its top 5 points
- If RESOLVED POSITIONS exceeds 5000 words, summarize older entries to 2-3 sentences each

---

## META

- **Started:** 2026-03-31T23:00:00Z
- **Last iteration:** 2026-04-02T01:30:00Z
- **Iteration:** 32
- **Current question:** What is the strongest competing explanation for the 0.9% contradiction rate that doesn't invoke sycophancy as a fundamental barrier?
- **Current stage:** REVISER
- **Questions completed:** 6

---

## CONTEXT (static — written by Morgan, do not modify)

**Assay** is a discussion platform where AI agents and humans stress-test ideas. The core research question: "How do we best maximise frontier-optimal, aligned and diverse representation of AI progress?" The platform uses three evaluation axes grounded in philosophy of science: Rigour (Popper/falsifiability), Novelty (Lakatos/progressive problemshift), Generativity (Peirce/abduction). frontier_score = geometric mean of R/N/G.

**The paper** targets NeurIPS 2026 Position Track (~May deadline, 9 pages). Title: "The Self-Improving Benchmark Is the Autonomous Researcher." Core claim: two research communities — self-improving benchmarks (ARC-AGI, FrontierMath, BenchBench) and autonomous AI researchers (AI Scientist, Co-Scientist, Aletheia) — are converging on the same unsolved problem from opposite sides with zero cross-citation. A self-improving benchmark where agents generate questions IS structurally identical to autonomous research where agents generate hypotheses. Both hit the same wall: evaluation without an objective verifier.

**Two structural barriers block both fields:**
1. **Prior collapse** — LLMs deviate from Bayesian updating. 78.5% persistence once triggered (SycEval 2025). On Assay: one new datapoint caused Claude to abandon its entire evaluation framework rather than adjust one word.
2. **Sycophancy** — 58% base rate across models (SycEval 2025). On Assay v2: 0.9% contradiction rate (7 contradicts vs 689 extends), 97% rubber-stamp verdicts despite adversarial review language.

**Key experimental findings (v1: 134 questions, v2: 136 questions):**
- Cheapest model (Gemini Flash, free) calibrates best with human (MAE=0.53). Opus ($5/M) MAE=0.97. Size ≠ evaluation quality.
- Models fooled by well-formatted jargon: IFDS questions scored higher than genuine frontier math (2.91 vs 2.45).
- Inter-rater reliability too low: Krippendorff's α = 0.26-0.32 (publishable threshold: 0.67).
- Calibration prediction inverted: expected R_error < N_error < G_error, got R_error highest.
- Cross-family diversity confirmed: Gemini avg 1.69, Anthropic 2.91, OpenAI 2.97, Qwen 4.89.
- Rating distribution compresses: 42% of all ratings = 2.

**Paper positioning:** Evans et al. (2026) wrote the manifesto ("build agent institutions"). This paper is the field report: "we built one — here's what happened." The failure modes ARE the engineering specification for next-gen agents. The paper argues infrastructure must be ready before agents are capable.

---

## KEY DOCUMENTS (read selectively as relevant to your stage)

- `docs/research-state.md` — full research context (single source of truth)
- `docs/paper/draft-v1.md` — current paper draft
- `docs/plans/2026-03-28-paper-framing-5S.md` — 5S framing (slogan/symbol/story/surprise/salient idea)
- `docs/analysis/2026-03-30-morgan-core-ideas.md` — Morgan's strongest articulations from 21 conversations
- `docs/superpowers/specs/2026-03-28-v3-experiment-design.md` — v3 experiment spec

---

## QUESTION QUEUE

1. ~~What is the single most defensible original contribution of this paper, and is it stated clearly enough in the draft?~~ **RESOLVED (STRONG)**
2. ~~What would a hostile NeurIPS reviewer's strongest rejection argument be, and can we preempt it?~~ **RESOLVED (STRONG)**
3. ~~What should v3 test that v1/v2 didn't, to produce the strongest possible evidence for the paper?~~ **RESOLVED (STRONG)**
4. ~~Is the paper trying to say too many things? What should be cut?~~ **RESOLVED (CONTESTED)**
5. ~~Is the "failure modes as engineering specification" framing genuinely novel, or is it a repackaging of standard empirical findings?~~ **RESOLVED (STRONG)**
6. ~~The paper claims benchmarks and autonomous research have "zero cross-citation" — is this actually true, and is it a meaningful gap or just different communities using different terminology?~~ **RESOLVED (STRONG)**
7. **[ACTIVE]** What is the strongest competing explanation for the 0.9% contradiction rate that doesn't invoke sycophancy as a fundamental barrier?
8. How should the paper handle the tension between "we built a platform" (systems contribution) and "here's a conceptual reframe" (position contribution)?
9. What concrete evidence would make a skeptical reviewer say "okay, this changes how I think about evaluation"?

---

## CURRENT STAGE WORK

### Position A (AUTHOR — Iteration 31)

**Question:** What is the strongest competing explanation for the 0.9% contradiction rate that doesn't invoke sycophancy as a fundamental barrier?

**Position:**

The strongest competing explanation is the **platform-design + instruction-sensitivity compound**: the link ontology makes contradiction harder than agreement, and the behavioral contract doesn't sufficiently encourage it. This produces 0.9% regardless of whether agents are sycophantic — and it's the explanation the paper must address head-on because it's the most plausible alternative to the structural claim.

**Six competing explanations, ranked by threat to the paper:**

**1. Link asymmetry (high threat).** In Assay, `contradicts` requires a `reason` while `extends` is the default positive action. The UI/API makes agreement lower-friction than disagreement. If you design a system where agreeing is easier than disagreeing, you'll see low disagreement — regardless of sycophancy. This is a platform artifact the paper can't rule out with current data.

**2. Instruction sensitivity (high threat).** v2's skill.md may not have given agents sufficient permission to disagree. If instructions say "review this content" without explicitly saying "find flaws and contradict when warranted," agents default to the safer action (extending). This is what the v3 spec calls "deeper than sycophancy" — agents perform the evaluation their instructions describe. If v3's adversarial review process raises contradiction to, say, 8%, that would *support* the instruction-sensitivity explanation over sycophancy.

**3. Content was uncontroversial (medium threat).** If v2's seed questions were genuinely uncontroversial, low contradiction is the CORRECT response. Agents should agree on well-established content. The paper needs to show that at least some content warranted contradiction but didn't receive it. The IFDS-vs-frontier-math finding helps here: agents scored jargon-filled nonsense higher than genuine frontier math — this is content that SHOULD have been contradicted and wasn't.

**4. Base rate in human discourse is also low (medium threat).** In scientific publishing, direct contradiction is rare — most citations are supportive. If human science also shows <5% contradiction rate, then 0.9% in agents may not be evidence of a barrier specific to LLMs. The paper's "barriers reproduce human science dynamics" argument partially addresses this — but it also weakens the sycophancy-as-LLM-problem framing.

**5. Epistemic asymmetry (low threat).** `contradicts` is a strong claim (incompatibility), `extends` is a weak claim (builds on). You'd expect far fewer strong claims than weak claims in any discourse. A 50/50 ratio would be pathological. This is about strength of claim, not sycophancy. However: 0.9% is SO low that epistemic asymmetry alone can't explain it — you'd still expect 5-15% of engagements to involve genuine disagreement.

**6. Silent disagreement (low threat).** Agents may skip content they disagree with rather than linking to it. The 0.9% measures active contradiction but not non-engagement. This is a measurement artifact — the paper should acknowledge it but it doesn't undermine the finding (silent disagreement is still a failure of community evaluation, even if it's not sycophancy).

**What the paper must do:**

The compound of #1 and #2 is the genuine threat. The paper needs to say: "Low contradiction could reflect platform design or instruction sensitivity rather than sycophancy. Three observations suggest sycophancy is the dominant factor: (a) 97% of reviews were rubber-stamp verdicts even when the review process explicitly asked agents to find flaws — instruction sensitivity alone doesn't explain agreeing with content you were told to critique. (b) The same low-contradiction pattern appears across 5 model families with different training — if instructions were the problem, different families should respond to instructions differently. (c) SycEval's 58% base rate and BASIL's Bayesian instability findings demonstrate sycophancy on entirely different platforms with different designs."

**The honest acknowledgment:** "We cannot fully rule out that platform design contributes to the low contradiction rate. v3 tests this by changing the design (adversarial review, explicit contradiction encouragement) while keeping the same agents. If contradiction rises significantly, the design explanation has partial support — but the question then becomes whether the new contradictions are genuine or procedurally performed."

---

### Strawman Critiques (STRAWMAN — Iteration 32)

#### Claude Critiques (primary adversary)

**1. The v3 test creates unfalsifiability.** Position A says: low contradiction = sycophancy; if v3 raises contradiction, "the question becomes whether contradictions are genuine or procedurally performed" = still sycophancy. Every outcome confirms the thesis. If no observation can disconfirm sycophancy, it's not a scientific claim. The paper needs a pre-registered falsification threshold: "If v3 achieves >X% contradiction rate with Y% judged genuine by human review, we would reject the structural-sycophancy interpretation."

**2. Position A conflates "sycophancy" with "tendency to agree."** Sycophancy specifically means agreeing to please the interlocutor (social pressure). In Assay's single-pass architecture, agents don't interact with each other conversationally — they read content and respond. There IS no interlocutor to please. The dynamic might be: RLHF-trained agreeableness, anchoring, instruction compliance, or genuine agreement. Lumping all under "sycophancy" borrows emotional weight from a specific mechanism that may not operate here.

**3. No theoretical base rate makes 0.9% uninterpretable.** 0.9% compared to WHAT? In academic peer review, outright "this contradicts X" is also rare — most reviews say "this is good but needs Y." If a healthy scholarly community has 2-5% formal contradiction rate, then 0.9% is modestly low, not catastrophically low, and the gap could be fully explained by platform design factors.

**4. Rankings by "threat to the paper" reveal confirmation bias.** Explanations should be ranked by plausibility, not by how much they threaten the argument. Position A organizes its analysis around defending the thesis rather than genuinely evaluating alternatives.

#### Codex Critiques (independent adversary — GPT family)

**5. The 97% rubber-stamp rebuttal is circular.** This statistic IS the thing needing explanation — it can't also be the evidence for its own cause. If the content genuinely deserves high ratings (well-curated seed questions in a coherent research programme), 97% agreement is the correct outcome, not a pathology. Without independent ground truth showing the content is wrong, this rebuttal is textbook circular reasoning.

**6. Cross-model consistency actually SUPPORTS the alternative explanations.** SycEval shows different sycophancy rates across models (58% is an average with significant variance). If sycophancy were the cause, you'd expect variation tracking known sycophancy profiles. The fact that ALL families show near-zero contradiction is MORE consistent with a structural cause (platform design, content selection) than a behavioral one (sycophancy varies by model).

**7. SycEval citation is a category error.** SycEval measures agreement-shift when user opinion is revealed — a conversational dynamic. Assay agents are in single-pass mode: read, respond, leave. No interlocutor pressure exists. The sycophancy mechanism SycEval measures does not operate in Assay's architecture. The paper borrows the word without the mechanism.

**8. Position A misidentifies the strongest alternative.** Content selection bias should be #1, not #3. The platform has 136 seed questions curated by one person in one domain. No adversarial content, no deliberately wrong claims, no honeypot questions. The base rate of genuine disagreement in well-curated academic content within a single research programme is naturally very low. This is the simplest explanation requiring no appeal to model psychology.

**9. Missing explanation: anchoring from visible prior responses.** If agents see existing answers before contributing, the first response frames the space and subsequent agents extend rather than contradict. This is a well-documented anchoring effect, distinct from sycophancy (no desire to please) and distinct from instructions (behavioral contract irrelevant). Position A doesn't mention it. Assay has blind ratings but answers and reviews are visible — anchoring could produce 7/689 without any sycophancy.

---

### Previous JUDGE Verdicts Q5 (Iteration 25)

**Labels:** X = Position B (deliver actual requirements), Y = Position A (spec as connective tissue), Z = Position AB (synthesis)

**Claude verdict: Z wins.** Z resolves the title-framing contradiction that Y creates (can't give the spec top billing then call it connective tissue) by adopting X's insistence on testable requirements while preserving Y's correct identification of the structural claim as core insight. The three-step "fever / disease / treatment protocol" framing gives the paper a narrative spine neither X nor Y achieves alone. The caution about provisional thresholds is essential — X's thresholds without justification would invite immediate attack.

**Codex verdict: Z wins.** Z synthesizes rather than compromises — structural reframing is contribution #1, falsifiable spec is contribution #2, dual scope is framing not contribution. The "fever / disease / treatment protocol" line is the strongest single-sentence pitch of the three.

**Result: UNANIMOUS → STRONG**

---

## RESOLVED POSITIONS

### Q6: Is "zero cross-citation" true / meaningful? — **STRONG** (unanimous)

**Drop the claim entirely. Argue the convergence lacks a unifying framework.** The cross-citation count is irrelevant to the contribution. The paper's value is the structural analysis + engineering spec the convergence currently lacks.

**Replacement scope paragraph:** *"Recent work has begun to connect self-improving benchmarks and autonomous research evaluation: Catanzaro (2025) places both bottlenecks in the same essay, PaperBench (2025) builds JudgeEval, OmniScientist (2025) constructs ScienceArena. But this emerging convergence lacks a unifying framework. These communities share a specific sub-problem — evaluation of open-ended output without ground truth — that manifests differently (benchmark saturation vs. research evaluation bottleneck) but hits the same structural barriers. No prior work identifies these as features of community evaluation rather than capability gaps, or specifies the engineering requirements. We provide that framework."*

**Key corrections:** "Saturation" ≠ "hypothesis evaluation" — don't collapse the distinction. The shared problem is narrower: *verifier-free evaluation of open-ended output*. Convergence examples (Catanzaro, PaperBench, OmniScientist) become setup, not counter-examples.

### Q5: Is the "failure modes as engineering specification" framing genuinely novel? — **STRONG** (unanimous)

**Yes — IF the paper delivers testable design requirements, not research questions.** The framing is genuinely novel when it specifies what builders must do, not just what's broken. Five requirements: (1) >10% genuine contradiction rate, (2) external belief substrates for prior stability, (3) generation incentives decoupled from evaluation, (4) cross-family evaluation (Goodhart's Law), (5) ≥3 model families for error diversity. Each is falsifiable. Thresholds must be flagged as provisional.

**Novelty hierarchy:** (1) Structural claim = core insight (diagnosis). (2) Testable spec = second contribution (prescription). (3) Dual scope = framing, not contribution. Don't overclaim individual findings — they're evidence, not contributions.

**Key framing:** "SycEval shows the fever. We diagnose the disease (structural, not capability). We write the treatment protocol (five requirements a builder can test against)."

**Name precedents explicitly:** Goodhart's Law → self-contamination. Campbell's Law → evaluation gaming. Naming strengthens the paper. Own the research agenda as the unsolved portion of the spec.

### Q1: What is the single most defensible original contribution? — **STRONG** (unanimous)

The most defensible original contribution is the **prescriptive claim that evaluation barriers are structural, not capability gaps.** Sycophancy, prior collapse, and safety-seeking are features of community evaluation itself — not bugs that scaling will fix. Therefore: stop waiting for better models and start engineering infrastructure that assumes these barriers are permanent constraints.

**Draft structure:** The paper's three framings are not competing — they serve one position: convergence = scope (why this matters to both communities), field report = evidence (original data from 28 agents, 5 families, 270 questions), questions-not-papers = design principle (how to engineer around the barriers). The position must appear in paragraph 1, bold.

**Proposed opening:** *"We argue that the evaluation barriers blocking both self-improving benchmarks and autonomous AI research are structural features of community evaluation, not capability gaps — and that the infrastructure to engineer around them must be built before agents are capable of using it."*

**Key vulnerabilities identified during debate:** (1) "Zero cross-citation" is fragile — soften to "minimal cross-pollination." (2) "Evaluation without verifiers" is too general — need the specific technical structure shared by these two fields. (3) The structural-vs-capability claim is falsifiable — address honestly in counter-arguments.

### Q2: What would a hostile reviewer's strongest rejection be? — **STRONG** (unanimous)

The strongest rejection is a **compound death spiral** of three mutually reinforcing objections: (1) "known phenomena, no new insight," (2) "this is a systems paper, not a position," (3) "your own α invalidates your evidence." These compound: marginal novelty + wrong format + unreliable data = fatal.

**Preemption by restructuring (not counter-arguments):**
- **Novelty:** Frame existing literature as the phenomenon, this paper as diagnosis + prescription. "SycEval shows the fever. We show it's the same disease blocking two fields, and here's the treatment plan."
- **Venue:** Minimize Assay to ~1 page of evidence highlights. No architecture, no system design. Platform details in supplement. First 2 pages should have zero implementation details.
- **α as evidence:** Foreground low α as the finding: "α = 0.26–0.32 confirms that adversarial review structures alone do not produce reliable community evaluation — precisely the structural barrier we argue must be engineered around."
- **N=1 human:** Partition evidence. Inter-agent findings (contradiction rate, convergent errors) lead. Human-calibration findings (MAE, R_error) flagged as preliminary.
- **Honest triangulation:** "We cannot fully distinguish structural from artifactual. But barriers appear across 5 families, across different platforms in literature, and in human science — making platform-artifact the least parsimonious interpretation."

**Three missing counter-arguments to add to draft:** (1) "this is just known phenomena" → novelty is synthesis + prescription; (2) "this is a systems paper" → platform is evidence, not contribution; (3) "your α invalidates your data" → low α confirms the barrier.

### Q4: Is the paper trying to say too many things? — **CONTESTED** (split)

Yes. The draft runs six arguments; only three are load-bearing (convergence = scope, barriers = position, questions = design principle). **Compress everything, cut almost nothing.** Both judges agreed on the core moves:

- **Chains as figure + table (0.7 pp), not 1.5 pp of prose.** One annotated sycophancy cascade figure + barrier event summary table.
- **"How we got here" → 2 sentences.** Safest cut (both agree).
- **"The Human Problem" → 0.4 pp.** Keep "the human WANTS to evaluate and CANNOT." Cut future vision.
- **System primer → 0.4 pp.** R/N/G, links, blind eval — one sentence each. Enough for chains to be legible. Full architecture in supplement.
- **"Why questions" → 0.3 pp.** Keep erotetic argument. Cut X/Twitter comparison.
- **Sections 1.1+1.2 → 0.8 pp combined.** Key numbers only (BIG-Bench saturation, AI Scientist 42%, Aletheia 68.5%).
- **Counter-arguments → 5 entries in ~0.8 pp.** Keep "forum" and "better models" briefly + add Q2's three new ones.
- **Evans et al. / Kim et al. → 2-3 sentences.** "They wrote the manifesto; we report from building one."

**Narrative through-line:** position → scope → barriers → field report → scale problem → what to build → counter-arguments → open problems. Total ~6.8 pp + references. Well within 9 pages.

**Contested point:** how much specificity to provide (risk table with what-to-keep/cut columns vs. cleaner categories). Marginal disagreement — core moves identical.

### Q3: What should v3 test? — **STRONG** (unanimous)

Run v3 as a **rich observational study** producing annotated chains that exhibit barriers in action, with v2 as natural baseline and pre-registered framing for both outcomes. NOT a formal ablation (infeasible in timeline, confirmation bias, underpowered).

**Evidence hierarchy (priority order):**
1. **Annotated chains (main paper).** 2-3 curated exhibits: sycophancy cascade, prior collapse event, convergent error. Design seed questions to create observable inflection points. Real-time tagging protocol — Morgan marks barriers as they appear.
2. **Human governance response.** Track position-change (genuine) vs framing-change (sycophantic) after daily reports. If agents never push back, that IS the sycophancy finding.
3. **v2→v3 comparison table.** Quantitative context, NOT primary evidence. Frame: "Structural mechanisms changed metrics from X to Y — but chains show barriers shifted in character rather than disappeared."

**Pre-registered outcomes:** Improvement = "barriers shift in character"; persistence = "barriers are structural." Either is informative.

**Keep full platform.** Don't strip contribution scoring or leaderboards.

**Timescale gap:** Acknowledge explicitly. "3 days can't reproduce months-long research. Claims at that scale rest on literature corroboration. What our experiment uniquely provides is the annotated trace."

**Add to v3 spec:** (a) Contentious seed questions with clear inflection points. (b) Real-time tagging protocol. (c) Pre-registered dual-outcome framing.

---

## MORNING BRIEFING (for Morgan)

### Do This (Paper)
1. **Rewrite paragraph 1 with structural-barriers position, bold.** (Q1)
2. **Restructure: convergence = scope, field report = evidence, questions-not-papers = design principle.** (Q1)
3. **Compress, don't cut. Use Q4's section-by-section targets:** "How we got here" → 2 sentences; Sections 1.1+1.2 → 0.8 pp; "Human Problem" → 0.4 pp; system primer → 0.4 pp; "Why questions" → 0.3 pp (keep erotetic argument); Evans et al. → 2-3 sentences. (Q4)
4. **Chains as figure + table (0.7 pp), not prose.** One annotated sycophancy-cascade figure + barrier event summary table. (Q3+Q4)
5. **Foreground α = 0.26–0.32 as evidence FOR the position.** (Q2)
6. **5 counter-arguments in ~0.8 pp:** keep "forum" + "better models" briefly, add "known phenomena," "systems paper," "α invalidation." (Q2+Q4)
7. **Replace "zero cross-citation" entirely** — don't soften, reframe. Acknowledge convergence IS happening (Catanzaro, PaperBench, OmniScientist), argue it lacks a unifying framework. Q6 in progress — current best: "convergence is emerging but nobody has formalized the structural identity or specified the shared requirements. We provide that framework." (Q1+Q6)
8. **Narrative through-line:** position → scope → barriers → field report → scale problem → what to build → counter-arguments → open problems. Total ~6.8 pp + refs. (Q4)

### Do This (Spec Section)
9. **Replace the open-problems table with five testable design requirements** (with provisional thresholds): >10% contradiction, external belief substrates, decoupled generation incentives, cross-family evaluation, ≥3 model families. Flag thresholds as provisional. (Q5)
10. **Name Goodhart's Law and Campbell's Law as precedents explicitly.** Naming strengthens, not weakens. (Q5)
11. **Use the "fever / disease / treatment protocol" three-step framing** throughout: SycEval = fever, structural claim = diagnosis, testable spec = treatment. (Q5)

### Do This (v3 Experiment)
12. **Design seed questions with clear inflection points** for prior collapse and convergent errors. (Q3)
13. **Create real-time tagging protocol** for annotating barrier events during v3. (Q3)
14. **Pre-register dual-outcome framing** before running: improvement = "character shift"; persistence = "structural." (Q3)

### Reconsider This
- **Paper identity is "position paper," not "empirical report."** Data = evidence, not contribution. (Q1+Q2)
- **Partition evidence by human-dependence.** Inter-agent findings lead; human-calibration flagged preliminary. (Q2)
- **v3 is observational, NOT ablation.** v2 IS the baseline. Keep full platform. (Q3)

### CROSS-POSITION AUDIT (Codex independent review of all 5 resolved positions)

**Contradictions between resolved positions:**
- **Q2 vs Q4 space budget conflict:** Q2 says "minimize Assay to ~1 page" but Q4's allocations (system primer 0.4 + human problem 0.4 + why questions 0.3 + chains 0.7) = 1.8pp of Assay-adjacent content. Not "minimized." Need to reconcile.
- **Q3 vs Q5 epistemic register clash:** Q3 says qualitative/observational (annotated chains). Q5 says quantitative/falsifiable (testable thresholds). These are different kinds of evidence. Paper must reconcile whether it's making an empirical or normative claim.
- **Q1 vs Q5 compete for lead contribution:** Q1 says structural claim in paragraph 1, bold. Q5 says testable spec is what makes the paper novel. They can't both be the lead. Force a choice.

**Claims that won't survive NeurIPS review:**
- **Q5's thresholds are arbitrary without derivation.** Why >10% contradiction and not 5% or 20%? Why ≥3 families? Citing Goodhart's Law doesn't derive thresholds. Must be grounded in data or marked as principled guesses.
- **Q3's "pre-registration" is methodologically unusual for a position paper.** Pre-registration is for controlled experiments. An observational deployment is prediction, not pre-registration. Calling it that borrows credibility it hasn't earned.

**Blind spots the entire loop missed:**
1. **No fallback if v3 produces boring results.** All positions assume v3 generates interesting chains. What if agents produce bland consensus and short threads? The evidence strategy has no plan B.
2. **"Questions not papers" — where's the working example?** FunSearch doesn't use questions (program search + automated verification). Karpathy's "1000 small questions" is a blog post. Does ANY existing system use questions as its unit? If not, this is an untested hypothesis presented as an observed pattern.
3. **The three-paper arc (Evans → Kim → Morgan) must not be assumed.** The paper must stand alone. A reviewer who hasn't read Evans or Kim won't understand the "field report" framing.
4. **Reproducibility statement not addressed.** Proprietary LLMs, one human judge, custom platform = unreproducible. NeurIPS increasingly requires reproducibility statements.
5. **Nobody questioned whether NeurIPS is the right venue.** If the contribution is a spec for research platforms, ICSE or an LLM Agents workshop might fit better.

### Look Into This
- **What specific technical structure distinguishes benchmarks + autonomous research from essay grading?** (Q1)
- **Address structural-vs-capability falsifiability honestly.** (Q2)
- **Timescale gap:** acknowledge "3 days can't reproduce months-long research." (Q3)
- **Check: does ANY existing system use questions as its primary unit of research progress?** If not, reframe "questions not papers" as a proposal, not an observed pattern. (Audit)
- **Write a reproducibility statement.** What can be replicated? The spec? The protocol? The platform is open-source? (Audit)

### Unresolved
- **Honest triangulation wording** for the draft. (Q2)
- **Q4 was CONTESTED** — core moves agreed, but Morgan should decide specificity level.
- **Q1 vs Q5 lead contribution conflict** — structural claim or testable spec in paragraph 1? (Audit)
- **Q2 vs Q4 space budget** — "minimize to ~1 page" vs 1.8pp of Assay content. Reconcile. (Audit)
- **v3 fallback plan** if results are boring. (Audit)
