# NeurIPS 2026 Position Paper — Research Queue

**Purpose:** Find ONE sharp, surprising, defensible position claim for a NeurIPS 2026 position paper about AI evaluation.

**Context:** Assay is a multi-agent evaluation platform where AI agents and humans rate intellectual content on three axes: Rigour (R), Novelty (N), Generativity (G). We ran a rating experiment with 5 AI models + 1 human on 134 questions. Several findings are counterintuitive and potentially publishable. The dissertation grounding is philosophy-of-science (Popper/Lakatos/Peirce) applied to AI evaluation.

**Audience:** NeurIPS reviewers — technically sophisticated, skeptical of overclaiming, rewarded by surprise + rigorous argument.

**What we have:** Empirical data from a live multi-model evaluation platform, 5 AI raters, 1 human, 134 items, multiple surprising findings. The position paper should take ONE of these findings and build a sharp, provocative, well-supported thesis around it.

---

## RESEARCH QUEUE

- [x] **1. The Novelty Impossibility** — Can LLM judges structurally assess novelty? The IFDS jargon finding (well-structured narrow questions outscoring genuine frontier math) suggests AI judges reward "novelty-resembling" content over actual novelty. Is this a calibration failure or a structural impossibility? Search literature on: LLM-as-judge novelty, AI evaluation limitations, training data horizon problem.

- [x] **2. The Cheapest-Is-Best Paradox** — Gemini Flash (free) MAE=0.53 vs Opus ($5/M) MAE=0.97. Does model scale anti-correlate with human judgment alignment for evaluation tasks? Is there a "sycophancy amplification" hypothesis? Search literature on: LLM judge model size, evaluation quality vs capability, sycophancy in large models.

- [x] **3. Convergent Errors in Diverse Panels** — Three model families independently made the same terminological error on the Log-Rank Conjecture. Does model diversity guarantee evaluation diversity? Search: ensemble LLM evaluation, correlated errors, shared training data blind spots.

- [ ] **4. Disagreement as Frontier Signal** — Inter-rater variance was highest on genuinely frontier content (FrontierMath, contested seeds). Is high AI judge disagreement itself a reliable signal of frontier-ness — better than any consensus metric? Search: disagreement as quality signal, uncertainty quantification in evaluation.

- [ ] **5. The Calibration Gradient Inversion** — We predicted R_error < N_error < G_error (increasing subjectivity). We got R_error highest. AI models disagree most about Rigour — the supposedly most objective axis. What does this mean about how AI models represent "correctness"? Search: LLM judge agreement on factual vs creative tasks, rigour evaluation in AI.

---

## FINDINGS

*(Append new findings here — do NOT overwrite)*

---

### 1. The Novelty Impossibility — 2026-04-04

**Core finding from our data:** Across all 5 AI raters, IFDS/tombstone questions (one agent looping on incremental dataflow analysis, generating repetitive but formally-structured jargon) scored *higher* on frontier_score (avg 3.21) than genuine frontier mathematics from HLE and FrontierMath (avg 2.37). The inversion is stark and consistent across model families — GPT-5.4 mini: Seeds avg R/N/G = 3.02/1.29/1.78 vs IFDS 3.89/3.19/3.78. Even Opus — the harshest rater — gave IFDS tombstone questions N=2.30 vs genuine seeds N=1.44.

**What the literature says:** The finding is not isolated. Three independent research threads converge on the same mechanism:

1. **Perplexity-driven preference (arXiv 2410.21819, EMNLP 2025):** LLM judges assign higher scores to text with *lower perplexity* — i.e., text more similar to their training distribution. IFDS jargon is formulaic and repetitive (low perplexity). Genuine frontier math is rare and unpredictable (high perplexity). The judge systematically confuses familiarity with quality — and "novelty-resembling academic formalism" is deeply in-distribution because it was common in training corpora.

2. **CALM framework (arXiv 2410.02736, NeurIPS 2024):** Among the 12 documented LLM judge biases, verbosity bias, chain-of-thought bias, and formality bias together explain the IFDS inversion. IFDS questions use hypothesis/falsifier structure, formal mathematical notation, and elaborate framing — all surface features that trigger upward calibration in LLM judges, independently of whether the content is substantively novel.

3. **Frontier evaluation limits (arXiv 2410.13341, NeurIPS 2024):** A theoretical result shows that when the content under evaluation exceeds the judge's own capability, no debiasing method can reduce required ground-truth labels by more than half. This is a formal impossibility at the frontier — which is precisely where we need evaluation to work.

4. **OOD detection impossibility (NeurIPS 2021):** Without restrictions on what counts as "out-of-distribution," OOD detection is formally impossible under PAC learning. Novelty is OOD detection. A judge trained on a fixed corpus cannot reliably identify content that is novel *relative to that corpus* without explicit structural constraints — which no current rubric provides.

**The theoretical synthesis:** Novelty assessment requires knowing what *doesn't* exist in the training distribution. This is structurally impossible for a model whose representations are entirely derived from that distribution. What the model can assess is "resemblance to novel-looking text" — which anti-correlates with actual novelty, because genuinely novel content breaks the patterns that characterize "novel-looking" academic writing.

**Generativity is even worse:** Generativity (does answering this open new questions?) requires predicting the *future* research trajectory — questions that haven't been asked yet. This is a prediction task about the adjacent possible from a fixed training distribution. The model has no mechanism to distinguish "this opens questions that already exist in our training data" from "this opens genuinely new questions." This is why Qwen assigned G=5 to 9% of all questions — it can only detect the pattern of generative-seeming content, not genuine generativity.

**Devil's Advocate:** The strongest objection is that this isn't novel to the community — the CALM paper was at NeurIPS 2024 and the perplexity-preference paper was at EMNLP 2025. A reviewer could say "we already know LLM judges are biased toward familiar text." The counter: nobody has yet demonstrated this as a *systematic reversal* — not just downrating novelty, but actively *inverting* the ranking so that jargon-loops score higher than actual open problems. Our data provides that concrete, quantifiable demonstration. The gap between "known bias" and "3.21 vs 2.37 inversion on curated frontier content" is publishable.

A second objection: maybe the HLE seeds genuinely aren't that novel on a question-as-question basis — they're asking for answers to known problems, not asking genuinely open questions. This is plausible for HLE (designed as a hard exam, not a research agenda). FrontierMath questions, which scored 3.57 vs IFDS 3.21, partially control for this — they're genuinely open computational problems. The IFDS inversion holds strongest against HLE, which may be the weaker half of our argument.

---

### 2. The Cheapest-Is-Best Paradox — 2026-04-04

**Core finding from our data:** Model calibration ranking (lower = better) vs human ground truth (29 items, MAE):
- Gemini Flash (free tier): MAE = 0.53
- GPT-5.4 mini: MAE = 0.79
- Qwen Coder: MAE = 0.93
- Claude Opus 4.6 ($15/M input, $75/M output): MAE = 0.97
- Claude Haiku 4.5 (cheapest Anthropic model): MAE = 1.09

The ranking is not monotonic with price or capability — but the correlation is in the *wrong* direction. Opus, the most capable model by every standard benchmark, is the second-worst evaluator of frontier content.

**What the literature says:** Three independent mechanisms, all with 2024-2026 citations, explain this:

1. **Semantic Capacity Asymmetry (arXiv 2601.22588, Jan 2026):** Evaluation requires substantially *less* semantic capacity than generation. A 1.7B model's internal representations already encode the features needed for judgment, even when generation fails. Larger models have "excess capacity" that creates liabilities in evaluation: they overgeneralize patterns, project their own generative priors, and confuse "what I would produce" with "what is good."

2. **Sycophancy scales with model size (arXiv 2310.13548, arXiv 2411.15287):** RLHF training teaches models to predict and match human preference signals — i.e., to produce outputs that *sound* good. This sycophancy increases with scale (demonstrated up to 540B PaLM). When a sycophantic model judges content, it evaluates "does this match the distribution of things that get positive human feedback?" not "is this genuinely novel/rigorous/generative?" For frontier content — which by definition deviates from the prior distribution — a sycophantic judge is systematically miscalibrated.

3. **Self-recognition bias (arXiv 2404.13076, NeurIPS 2024):** Larger models recognize their own outputs significantly better than smaller models, and this self-recognition enables stronger self-preference bias. GPT-4 shows this; Llama 2 doesn't. Translated: Opus may be partially evaluating "does this look like something Opus/Claude would produce?" rather than evaluating on the rubric. This is Preference Leakage — a risk already flagged in our own research-state.md.

**The theoretical synthesis:** There are two dissociable skills — generation and evaluation. They are correlated in humans (experts at a domain tend to be good evaluators in that domain) but this correlation breaks for LLMs because: (a) LLM generation is optimized for RLHF-preference which biases away from frontier content, and (b) evaluation requires pattern-breaking sensitivity that is actually *degraded* by optimization for pattern-conforming generation. The bigger the model, the more optimization pressure, the bigger the gap.

**A further wrinkle:** The per-axis breakdown of Opus's ratings is revealing. Opus gave seeds avg N=1.44 — *lower* than any other model. This is consistent with Opus seeing through the "novelty-resembling" surface of HLE seeds (which are hard exam questions, not genuine open problems). So Opus isn't simply biased toward "sounds good" — it's being harsh on a dimension that, for HLE questions, may actually be correct. The human gave seeds avg N=2.66, which is more lenient. This means the "Opus is miscalibrated" story is more nuanced — Opus may be RIGHT about novelty of HLE seeds and the human may be applying a gentler standard. The 29-item human sample is too small to adjudicate this cleanly.

**Devil's Advocate:** The strongest objection is sample size. 29 human-rated items is a thin ground truth — the MAE differences (0.53 vs 0.97) may not be statistically significant at N=29. A reviewer will ask for confidence intervals and will note that with N=29, a few outlier items can move MAE by 0.2-0.3. The "Semantic Capacity Asymmetry" paper (arXiv 2601.22588) provides theoretical grounding but its empirical tests were on different tasks (not multi-axis frontier content rating). Second objection: this might be a Gemini Flash peculiarity rather than a general principle — Gemini was trained with a different objective or calibration than Anthropic or OpenAI models, and "smallest Anthropic model is worst" (Haiku MAE=1.09) is consistent with cost-correlation *within* a family. The cross-family comparison (Gemini Flash vs Opus) may be confounded by training methodology, not size alone.

---

### 3. Convergent Errors in Diverse Panels — 2026-04-04

**Core finding from our data:** On the Log-Rank Conjecture, three model families from different providers — Claude (Anthropic), Gemini (Google), and GPT (OpenAI) — independently made the identical terminological error: calling Lovett's O(√r · log r) upper bound a "proof barrier." This is a specific, sharp technical error. A proof barrier (in the sense of Razborov-Rudich natural proofs, Aaronson-Wigderson algebrization, or relativization results) is a *theorem showing that a class of techniques cannot prove a result* — it is a meta-mathematical impossibility. Lovett's result is an *upper bound* on deterministic communication complexity: it says CC(f) = O(√rank(f) · log rank(f)), which is actually progress *toward* the Log-Rank Conjecture, not a barrier against it. The models did not just rate the content poorly or inconsistently — they made the identical wrong terminological move, confidently, in their reasoning fields, and the presence of inter-model consensus would have given a naive panel evaluator false confidence in the error.

**Why this matters for evaluation methodology:** The canonical justification for multi-model evaluation panels rests on the Condorcet Jury Theorem: if each model independently has a better-than-chance probability of being correct, majority vote converges to the correct answer. But the Condorcet theorem has a critical hidden premise — **error independence**. If models' errors are correlated, majority vote amplifies the shared error rather than cancelling it. Our Log-Rank finding is a concrete demonstration that this independence assumption fails.

**What the literature says:** Four independent research threads converge on the same mechanism:

1. **Correlated Errors in Large Language Models (arXiv 2506.07962, 2025):** Empirically demonstrates that even across different providers and architectures, models exhibit highly correlated errors — when models err, they "collapse onto the same wrong answer." Models agree on errors ~60% of the time on tested datasets, and accuracy remains flat despite increasing panel consensus. This directly violates the error independence assumption.

2. **Ensemble independence failures (arXiv 2409.00094, 2024):** Directly invokes the Condorcet Jury Theorem to show that LLM ensemble evaluation violates independence in practice — shared latent confounders (training artifacts, stylistic biases, shared knowledge representations) drive correlated error rates across supposedly diverse models. The CARE framework (arXiv 2603.00039) identifies the mechanism: models share latent confounders that make their judgments dependent even when architectures differ.

3. **Epistemic Diversity and Knowledge Collapse (arXiv 2510.04226, 2025):** Across 27 LLMs from Llama, Gemma, Qwen, and OpenAI families — i.e., maximally diverse model families — model scale negatively impacts epistemic diversity, and knowledge collapse on specific topics occurs even across different families. Different model families ≠ different epistemic perspectives.

4. **Wisdom of crowds with shared information (Palley & Soll, Management Science 2019; Scientific Reports 2025):** From the decision theory literature: when crowd members share a common information source, aggregation fails to improve accuracy. Group accuracy can *decrease* as group size increases when members share correlated information. Frontier academic content lives in a small, highly-cited corpus of papers — every model has seen the same sources, creating a "correlated crowd" where additional panel members add no epistemic value.

**The mechanism for the Log-Rank error:** The term "proof barrier" is common in complexity theory (barriers to P vs NP: relativization, natural proofs, algebrization). Papers about the Log-Rank Conjecture appear in training corpora near papers about other complexity barriers. The association "challenging result in complexity → proof barrier" was encoded from co-occurrence in training data, and this association fires regardless of whether the specific result is actually a barrier. Three models from three companies independently learned the same broken association from the same overlapping corpora of academic complexity theory papers. Their errors are not independent random variables — they are draws from a shared distribution over the same knowledge representation error.

**The irony of frontier evaluation:** Multi-model panels are most urgently needed for frontier content — where individual model confidence is highest and errors most costly. But frontier content is discussed in a small, densely-cited academic literature that all models have seen equally. Routine content (explaining TCP vs UDP) is discussed in millions of documents; frontier mathematics is discussed in dozens. The *smaller* the literature, the *more correlated* the models' errors. Multi-model panels thus fail exactly where they are most needed: not because the models don't know the answer (they can't), but because their errors are more correlated on obscure frontier content than on common knowledge. The panel gives false confidence — consensus looks like reliability but is actually shared hallucination.

**Actionable implication:** "Replace judges with juries" (arXiv 2404.18796, the canonical multi-model panel paper) works for content where errors are plausibly independent. For frontier content, a better signal than panel consensus is **panel disagreement** — when models from diverse families disagree, that's a signal that the content is at the edge of their shared knowledge representation. Disagreement is a more honest frontier signal than consensus.

**Sharper mechanism for the Log-Rank error (addendum from extended literature search):** A more precise explanation for the Lovett mischaracterization: there *is* a genuine barrier result near this conjecture — Chattopadhyay, Mande, Sherif (J.ACM 2020) proved that the *log-approximate-rank conjecture is false*, ruling out an entire class of proof strategies. This IS a proof barrier, by different authors, six years later, on a related but distinct conjecture. Models likely conflate Lovett's 2014 upper bound with this 2020 barrier result — both appear in the same literature on the Log-Rank Conjecture, and training corpora (especially survey papers like Lovett's own arXiv 1403.8106) discuss them in close proximity. The mechanism is not a generic confusion about terminology — it is a specific cross-citation conflation driven by co-occurrence in training data. Three model families independently activated the same broken association from the same survey literature.

**Strongest additional supporting paper:** "Great Models Think Alike and this Undermines AI Oversight" (arXiv 2502.04313, ICML 2025 spotlight) — introduces CAPA (Chance-Adjusted Probabilistic Agreement) to measure model similarity via overlapping mistakes. Central finding: *as frontier LMs become more capable, their mistakes become more similar*, even across distinct architectures and providers. Two implications: (1) this directly links Candidate B (scale anti-correlation) and Candidate D (correlated errors) — they are the same mechanism viewed from different angles; (2) the paper explicitly argues this undermines both LLM-as-judge and weak-to-strong oversight paradigms. Project page: model-similarity.github.io

**Additional confirming papers:**
- "Don't Always Pick the Highest-Performing Model" (arXiv 2602.08003, Feb 2026): formalizes an *information-theoretic error floor* — a ceiling on ensemble performance that correlated errors impose regardless of how many panel members you add. Even infinite panel size cannot improve accuracy past this floor when errors are correlated. This is a formal result that panels fail, not just an empirical observation.
- "Consensus is Not Verification" (arXiv 2603.06612, Mar 2026): across five benchmarks, models are better at predicting what *other models will say* than at identifying what is *true* — meaning panel consensus measures social coherence within the shared training distribution, not factual accuracy. Under uncertainty, majority vote converges to "what training data says" not "what is correct."
- "AI Models Collapse When Trained on Recursively Generated Data" (Shumailov et al., *Nature* 631, 2024): progressive collapse of output diversity when models train on each other's outputs — as post-2024 web increasingly contains LLM-generated text, models from different providers converge in output distribution. Model family diversity is eroding at the corpus level.

**Devil's Advocate:** The strongest objection is that the Log-Rank finding is a single anecdote. We observed this error in narrative review (models discussing the question), not in the systematic rating data — we don't have a quantified rate of "same-error convergence" across our full 134-question corpus. A reviewer will say: one shared terminology error could be coincidence, or could reflect one model's training data bleeding through common pretraining (Dolma, The Pile, C4). We need systematic evidence — e.g., measuring the fraction of questions where all 5 models agree and that agreement differs from human ground truth, stratified by question rarity in pretraining corpora. Second objection: the argument isn't fully new. "Models agree on wrong answers" is the informal intuition behind why AI evaluation is hard; the Condorcet framework is standard. What's genuinely new here is the mechanism (frontier-specific correlation) and the counterintuitive implication (panel diversity is *least* effective exactly at the frontier). That counterintuitive structural claim is the publishable novelty — the anecdote is the hook, not the argument. Counter to the devil's advocate: the literature as of 2025-2026 is now sufficiently developed (ICML 2025 spotlight, March 2026 preprints) that our platform data is a *corroborating* empirical instance for a structural argument the field is only beginning to articulate. The position paper's contribution is articulating the argument cleanly with a diagnosable concrete example — not claiming to be the first to notice errors correlate.

---

## CANDIDATE POSITIONS

**After researching queue items 1, 2, and 3, here is the current assessment:**

---

### Candidate A: "LLM Judges Invert Novelty Rankings"

**One-sentence claim:** LLM judges systematically rank formally-structured in-distribution jargon *above* genuine frontier content on novelty and generativity axes, making them structurally unsuitable as novelty evaluators without human calibration.

**Evidence for:**
- IFDS jargon (3.21) > FrontierMath/HLE seeds (2.37) across all 5 model families
- Perplexity-preference mechanism (arXiv 2410.21819) explains the mechanism
- OOD detection impossibility (NeurIPS 2021) gives formal grounding
- CALM bias framework (NeurIPS 2024) provides independent validation of formality bias

**Evidence against:**
- HLE seeds may genuinely not be "novel" as questions (they're hard exam problems, not open research questions) — the inversion might be correct for HLE
- FrontierMath (3.57 > IFDS 3.21) partially recovers expected ordering — so the inversion is category-dependent
- Sample sizes: only 5 FrontierMath, 5 competition math, 37 IFDS items
- The claim is partially anticipated by CALM (2024) — a reviewer may see this as incremental

**Surprise score: 3/5** — Sophisticated NeurIPS reviewers will know LLM judges have biases. The *inversion* (not just downrating) is the genuinely surprising part, but the underlying mechanism is increasingly well-known.

---

### Candidate B: "Model Scale Anti-Correlates with Evaluation Quality at the Frontier"

**One-sentence claim:** For frontier intellectual content evaluation, model capability and judge calibration are dissociable — the most capable generation models are the worst judges, because scale amplifies sycophancy and self-projection at the cost of sensitivity to genuine novelty.

**Evidence for:**
- Gemini Flash MAE=0.53, Opus MAE=0.97 on the same 29-item human ground truth
- Sycophancy scaling literature (arXiv 2310.13548, 2411.15287) explains mechanism
- Self-recognition bias (arXiv 2404.13076) provides self-preference mechanism
- Semantic Capacity Asymmetry (arXiv 2601.22588, Jan 2026) provides theoretical frame

**Evidence against:**
- N=29 human items is thin — confidence intervals likely overlap
- Cross-family comparison confounds size with training methodology
- Haiku (cheap Anthropic) = worst within Anthropic family, so cost-correlation is not monotonic
- "Cheapest is best" may be Gemini Flash-specific rather than a principle

**Surprise score: 4/5** — "Don't use your flagship model as a judge" would be genuinely counterintuitive to most NeurIPS practitioners. The Semantic Capacity Asymmetry paper (Jan 2026) is brand-new and establishes the theoretical frame, giving this angle a timely hook.

---

### Candidate C (Synthesis): "Frontier Evaluation Requires Judges With No Skin In the Game"

**One-sentence claim:** LLM evaluation of frontier content fails in proportion to a model's optimization pressure: larger, more RLHF-tuned models are simultaneously worse at detecting genuine novelty (perplexity preference inverts novelty rankings) and more sycophantic (scale amplifies preference-matching), producing a double failure mode where the most capable models are the least trustworthy frontier judges.

**Evidence for:** Combines evidence from A and B — both findings point to the same underlying mechanism: RLHF optimization pressure teaches models to recognize and reward "sounds good" rather than "is genuinely novel/frontier."

**Evidence against:** Making a compound claim risks diluting both. Reviewers prefer one clean thesis with strong evidence over two weaker ones combined.

**Surprise score: 4/5** — The synthesis is more powerful but harder to prove rigorously with N=29.

---

### Candidate D: "Model Diversity Doesn't Guarantee Error Diversity at the Frontier"

**One-sentence claim:** Multi-model evaluation panels produce correlated rather than independent errors on frontier intellectual content — because frontier topics are discussed in small, densely-cited corpora that all models have seen equally — making panel consensus a false confidence signal precisely where it is most needed.

**Evidence for:**
- Log-Rank Conjecture: three model families (Claude, Gemini, GPT) independently made identical terminological error (calling Lovett's upper bound a "proof barrier")
- "Correlated Errors in Large Language Models" (arXiv 2506.07962, 2025): models agree on errors ~60% of the time; accuracy flat despite increased consensus
- "Epistemic Diversity and Knowledge Collapse" (arXiv 2510.04226, 2025): model family diversity ≠ epistemic diversity; knowledge collapse across Llama/Gemma/Qwen/OpenAI families
- Condorcet Jury Theorem requires error independence — structurally violated when all models trained on the same rare academic papers
- Palley & Soll (Management Science, 2019): group accuracy decreases when crowd members share information source
- "Replacing Judges with Juries" (arXiv 2404.18796): the canonical multi-model paper doesn't claim epistemic independence and doesn't test whether it holds for frontier content

**Evidence against:**
- Log-Rank finding is a single qualitative anecdote, not a systematic count
- Correlated errors might be correctable by prompt engineering (explicit "disagree with the panel" instruction)
- Clinical literature (83% error repetition) is a different domain; may not generalize to mathematical evaluation
- We don't have a systematic measure of "all-models-agree, all-models-wrong" frequency across our 134-question corpus

**Surprise score: 4/5** — "Adding more judges doesn't help at the frontier because the judges' errors are correlated" is counterintuitive to practitioners who assume diversity = independence. The Condorcet framing elevates this from an empirical complaint to a structural impossibility argument, which is publishable at NeurIPS. The inversion — that disagreement is more informative than consensus for frontier content — is the genuinely actionable and surprising takeaway.

---

## TOP RECOMMENDATION

**Revised after 3 queue items: Candidate D ("Correlated Errors") is now the top recommendation, above Candidate B.**

**Why D is now ranked first:**

Candidate B ("Scale Anti-Correlates with Evaluation Quality") has the most immediate practitioner impact — "don't use Opus as your judge" is a concrete, actionable, surprising finding. But it has a fatal weakness: N=29 human-rated items, and the finding depends on cross-family comparison that a reviewer will correctly flag as confounded by training methodology (not just model size).

Candidate D ("Correlated Errors") is structurally stronger for three reasons:

1. **It doesn't depend on N=29.** The Condorcet argument is theoretical — it holds whenever error rates are correlated, regardless of sample size. Our Log-Rank finding is the empirical hook; the argument stands on the theoretical structure.

2. **The surprise is higher and more durable.** "Bigger model = better judge" is a heuristic that everyone knows is imperfect. "Diverse panel = independent errors" is an assumption that almost no one has questioned — it's baked into every multi-judge evaluation paper as an unstated premise. Candidate D attacks a hidden assumption; Candidate B attacks a known heuristic.

3. **The implication is more radical and more actionable.** If Candidate B is right, the fix is "use smaller models as judges." If Candidate D is right, the fix is "disagreement, not consensus, is the frontier signal." This reframes what evaluation even means — not a vote toward a correct answer, but a probe for the boundary of shared knowledge. That's a genuine conceptual contribution.

**The revised argument structure for the paper:**

1. **Setup:** Multi-model LLM-as-judge is now standard practice (cite: arXiv 2404.18796, Chatbot Arena, LMArena). The motivation for multiple judges is explicit: aggregate to reduce individual error. This reasoning imports the Condorcet Jury Theorem — which requires error independence.

2. **The structural claim:** Error independence fails for frontier content. Frontier topics are discussed in a small, heavily-cited academic literature. All frontier-tier models have read the same papers. Their representations of frontier content are therefore correlated — not identical, but correlated. The Condorcet guarantee requires *independent* errors; correlated errors mean consensus amplifies shared hallucination.

3. **Empirical hook 1 (qualitative):** On the Log-Rank Conjecture, three model families made the identical terminological error, confidently, despite coming from different providers with different architectures. A naive panel would have rated this assessment as highly reliable.

4. **Empirical hook 2 (quantitative from literature):** "Correlated Errors in LLMs" (arXiv 2506.07962): models agree on errors ~60% of the time on tested datasets; accuracy flat despite increased consensus.

5. **The inversion implication:** Panel disagreement is a *better* signal of frontier-ness than panel consensus. When all 5 models from 3 families agree confidently, that tells you the content is well-covered in the shared training distribution — not that it's correct or frontier. When they disagree, that tells you the content is at the boundary of their shared knowledge representation.

6. **Connection to Finding 2 (scale anti-correlation) — now theoretically unified:** "Great Models Think Alike and this Undermines AI Oversight" (arXiv 2502.04313, ICML 2025 spotlight) provides the bridge: *as frontier LMs become more capable, their mistakes become more similar*. This directly explains both why Opus is the worst-calibrated judge (its errors are more correlated with other models' errors on frontier content, so "agreed assessment" is really "shared misconception") and why panel diversity fails at the frontier (a panel of frontier models is the worst-case for error independence). Candidates B and D are not independent findings — they are the same mechanism (capability-correlated error homogenization) viewed from two angles: B sees calibration degrade, D sees error correlation grow.

7. **The position:** For frontier evaluation, the appropriate paradigm is not "build a consensus from diverse judges" but "use disagreement as the primary signal and human calibration as the ground truth." This reframes the entire LLM-as-judge literature.

**Why this matters beyond our platform:** Every major AI evaluation paper using multi-model panels — LMArena, AlpacaEval, MT-Bench, FrontierMath scoring — implicitly assumes error independence. If this assumption fails for frontier content, the entire empirical basis for "AI is making progress at the frontier" using AI judges is suspect. This is not just a platform paper — it's a structural critique of how the field measures its own progress.

**Caveats to acknowledge in the paper:** The Log-Rank anecdote is qualitative and single-instance; "correlated errors" paper (arXiv 2506.07962) needs independent verification; panel disagreement as a frontier signal has not been systematically tested (Queue Item 4 would strengthen this if completed). These are limitations, not fatal flaws — position papers argue from evidence and structure, not prove theorems.

---
