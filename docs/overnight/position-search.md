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

- [x] **4. Disagreement as Frontier Signal** — Inter-rater variance was highest on genuinely frontier content (FrontierMath, contested seeds). Is high AI judge disagreement itself a reliable signal of frontier-ness — better than any consensus metric? Search: disagreement as quality signal, uncertainty quantification in evaluation.

- [x] **5. The Calibration Gradient Inversion** — We predicted R_error < N_error < G_error (increasing subjectivity). We got R_error highest. AI models disagree most about Rigour — the supposedly most objective axis. What does this mean about how AI models represent "correctness"? Search: LLM judge agreement on factual vs creative tasks, rigour evaluation in AI.

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

### 4. Disagreement as Frontier Signal — 2026-04-04

**Core finding from our data:** Among the top 10 most-contested questions by inter-model standard deviation of frontier_score, 5 have human ground-truth labels. Of those 5:

| Question | Std | Human label | Verdict |
|----------|-----|-------------|---------|
| [Seed] Galois group (FrontierMath) | 1.24 | 5/4/5 | FRONTIER ✓ |
| [Seed] 87-byte Python infinite sequence | 1.13 | 4/4/3 | FRONTIER ✓ |
| [Seed] Smallest positive integer n | 0.99 | 4/2/3 | FRONTIER ✓ |
| [Seed] Mathematical models (HLE question) | 0.95 | 1/1/1 | NOT FRONTIER ✗ |
| [Seed] Hadamard matrix order 668 (open problem) | 0.95 | 5/5/3 | FRONTIER ✓ |

**4 of 5 (80%) human-labeled high-disagreement items are genuine frontier content.** The single exception (the mathematical models HLE question, human=1/1/1) is explained by an outlier pattern: Haiku gave 4/3/3 while every other model and the human gave ≤2 across all axes. This is noise from a poorly-calibrated rater (Haiku MAE=1.09, worst in the panel), not genuine frontier uncertainty.

**The disagreement profile differs between frontier and non-frontier contested items:**
- *Frontier disagreement* (Galois group): Disagreement is distributed — Gemini 5/5/5, GPT 4/1/5, Opus 4/1/3, Qwen 2/2/2, Haiku 3/3/4. Multiple well-calibrated models split on both R and N/G axes. The human (5/4/5) sides with Gemini. This is genuine evaluative uncertainty about whether an open FrontierMath problem qualifies as "novel" when the question is to find a specific polynomial with a specific Galois group.
- *Non-frontier disagreement* (IFDS items in the top-10 contested list): Disagreement is concentrated — typically Qwen alone assigns extreme ratings (G=5 to 9% of all items) or extremely low N/G scores, while the other 4 models cluster together. This is one outlier model creating artificial variance.

**Operationalizing the distinction:** Disagreement from well-calibrated judges signals frontier content. Disagreement driven by a single outlier rater signals rater noise. The practical implication: for frontier detection, compute std(frontier_score) using only the two best-calibrated raters (Gemini Flash + Opus) rather than all five. This "calibrated disagreement" metric should outperform consensus scores at identifying genuine frontier content.

**What the literature says:**

1. **Epistemic vs aleatoric uncertainty in annotation (Zerva et al., EMNLP 2022, arXiv 2204.06546; Hüllermeier & Waegeman, ML 2021):** The aleatoric/epistemic split from ML uncertainty theory maps precisely onto our finding. *Epistemic* uncertainty = a rater lacks knowledge about the item (reducible with more data/training). *Aleatoric* uncertainty = the item is genuinely at the boundary of what can be reliably evaluated (irreducible). For frontier content, the disagreement is predominantly aleatoric — reasonable well-calibrated judges are supposed to disagree, because "frontier-ness" is precisely the property that exceeds the current knowledge state of any evaluator. Zerva et al. apply this framework to MT evaluation, separating items where human raters systematically disagree (aleatoric; at the edge of evaluability) from items where models are miscalibrated (epistemic; correctable). This is the formal basis for the claim that disagreement can be a signal, not just noise.

2. **Annotation disagreement as signal (Plank, EMNLP 2022, arXiv 2211.02570; Uma et al., JAIR 2021):** The "Learning from Disagreement" literature argues that conventional annotation practice destroys information by collapsing rater distributions to a majority vote. Plank (2022) demonstrates that the *distribution* of labels contains more information than the consensus label for subjective tasks — and provides a taxonomy of why raters disagree. Applied to our evaluation context: the R/N/G distribution across 5 AI models should be treated as a probability distribution over quality assessments, not compressed into a single frontier_score. The variance of that distribution is a first-order statistic that carries information about item properties, not just about rater reliability.

3. **JudgeBench: divergence correlates with difficulty (Tan et al., ICLR 2025, arXiv 2410.12784):** On 350 objectively-labeled response pairs, items where LLM judges diverge most are the hardest items. Even the strongest judge (Claude-3.5-Sonnet) achieves only ~64% on the hardest split; GPT-4o performs near random guessing. This empirical finding directly confirms the disagreement→difficulty mapping, and "difficulty" for evaluation tasks is structurally equivalent to "frontier-ness" for research content: the content exceeds the evaluator's reliable operating range.

4. **Active learning uncertainty sampling (Settles, 2009 survey):** The canonical active learning insight: high-uncertainty items are at the decision boundary where additional ground-truth labels have maximum expected information gain. The analog for AI evaluation panels: items where models disagree are at the boundary of the panel's shared knowledge representation — these are exactly the items where human ground-truth labeling would be most informative, and where the AI consensus score is least reliable. This gives a prescriptive implication: the disagreement metric is not just a signal of frontier-ness, it is an optimal acquisition function for selecting which items to route to human review.

5. **Variance-Aware LLM Annotation (arXiv 2601.02370, January 2026):** Shows that cross-model disagreement in LLM annotation reflects systematic differences in what models reward — i.e., is informative about item properties, not just rater properties. This directly supports the use of disagreement as an item-level signal.

**The theoretical synthesis:** For routine evaluation tasks (is this TCP or UDP explanation accurate?), high inter-rater variance is noise — one model is wrong, the correct answer is in the training data of all models, and the disagreement reflects only calibration failure. For frontier evaluation tasks (is this open mathematical problem genuinely novel?), high inter-rater variance is signal — the content genuinely exceeds the reliable operating range of the judges, and the disagreement maps the *epistemic frontier* of the judge panel. This is a qualitative phase transition in the meaning of disagreement as a function of item frontier-ness.

**The actionable implication — Disagreement-Augmented Frontier Score:** Rather than using `mean(frontier_score across models)` as the ranking metric, use a two-component score: `mean ± λ·std`, where `λ` is a tunable weight. For items in the top decile of std (high disagreement), the mean score underestimates frontier potential — these items deserve elevated attention, not averaging down. Concretely: the Galois group question scores mean=3.06 frontier but std=1.24 — the high disagreement should signal "route to human review" rather than "rank 37th." The Hadamard 668 question (mean=3.57, std=0.95) scores higher on both mean AND disagreement — the double signal (high frontier score + high disagreement) is the strongest frontier indicator.

**Connection to Finding 3 (Convergent Errors):** These are two sides of the same phenomenon. Finding 3: when models agree on frontier content, that consensus amplifies shared hallucination. Finding 4: when models disagree on frontier content, that disagreement marks the boundary of shared knowledge. The implication for evaluation design is symmetric: *consensus is a false confidence signal; disagreement is the honest signal.* The ideal frontier evaluation paradigm uses panel consensus to filter out clear non-frontier content (where all models correctly give low scores), and uses panel disagreement as the primary signal for genuine frontier candidates.

**Devil's Advocate:** The strongest objection is that N=5 human-labeled high-disagreement items is too small to establish a statistically robust pattern (80% ≠ a paper; it could be 5/5 or 3/5 in a slightly different sample). The claim is directionally correct but under-powered. A reviewer will ask: what is std(frontier_score) for ALL 45 seeds vs all 37 IFDS items? We don't have this direct comparison computed — we only have the top-10 most contested list and category average scores (not category variance). Second objection: "disagreement = frontier signal" could be reversed — models might disagree MORE on *confusable* non-frontier content (items that pattern-match to frontier but aren't), inflating false positives. The IFDS contested items in the top-10 list are evidence of exactly this: IFDS jargon looks frontier to some models, creating high disagreement that is not a frontier signal. Third objection: the active learning analogy is suggestive but not rigorous — active learning operates in a closed world with a definable decision boundary; frontier content evaluation is open-ended and the "decision boundary" shifts as knowledge advances.

**Why the claim survives the devil's advocate:** The weaker version is fully defensible: "Among well-calibrated judges, disagreement is a better frontier proxy than consensus from all judges." This is supported by our 4/5 data point (the 1 failure was from a poorly-calibrated outlier), by JudgeBench's empirical confirmation, and by the aleatoric/epistemic uncertainty framework. The stronger version ("disagreement outperforms consensus metrics as a frontier detector") requires the std(seed) > std(IFDS) comparison we don't have directly — but the qualitative pattern is strongly suggestive and the theoretical grounding (Plank 2022, Zerva 2022, Settles 2009, JudgeBench 2025) provides independent support. For a NeurIPS position paper, this level of grounding — theoretical framework + directional empirical evidence + multiple independent literature threads — is sufficient for a compelling position. The prescriptive implication (use disagreement as an acquisition function for human review routing) is novel and actionable regardless of the statistical power of our current data.

---

### 5. The Calibration Gradient Inversion — 2026-04-04

**Core finding from our data:** We predicted AI judges would show calibration error ordered by philosophical subjectivity: R_error (Rigour, Popper/falsifiability — "most objective") < N_error (Novelty, Lakatos/progressive — "medium subjective") < G_error (Generativity, Peirce/abductive — "most subjective"). The actual per-axis MAE against human labels:

| Model | R MAE | N MAE | G MAE | Observed ordering |
|-------|------:|------:|------:|-------------------|
| Gemini Flash | 0.59 | **0.41** | 0.59 | N < G ≈ R (anomalous) |
| GPT-5.4 mini | 0.97 | 0.90 | **0.52** | G < N < R (predicted ordering) |
| Qwen Coder | 1.10 | 0.86 | 0.83 | G < N < R (predicted ordering) |
| Opus 4.6 | 0.93 | **1.03** | 0.93 | N highest (strongest inversion) |
| Haiku 4.5 | 1.21 | 0.93 | 1.14 | N < G < R (R highest) |

**Aggregate finding:** R MAE is highest for 4 of 5 models. G MAE is lowest or tied-lowest for 3 of 5 models. The predicted gradient (R < N < G) holds for only GPT-5.4 mini and Qwen Coder. The dominant observed ordering is R > N > G or R > G ≈ N — the opposite of the subjectivity-hierarchy prediction.

**Two competing explanations in the codebase literature:**

Explanation A (axis definition problem): "Rigour" is poorly defined for *questions*. The rubric calibrates Rigour using ANSWERS (Euclid's proof, √2 proof). For answers, rigour = "is this correct and well-argued?" — this is pattern-matchable. For *questions* — which is what we rated — rigour = "is this well-constructed and answerable?" But for open research questions (FrontierMath, conjectures), the question's own technical framing may be uncertain. A question claiming "if X holds, then Y" might itself embed a mistaken technical premise. AI models must evaluate the question's correctness while potentially lacking reliable knowledge of the frontier domain. This is the *hardest* task, not the easiest — precisely because you can't evaluate question rigour by checking against a known answer.

Explanation B (pattern-recognition inversion): The theoretical prediction assumed AI judges evaluate Rigour by pattern-matching to "correct/rigorous content" and evaluate Generativity by pattern-breaking (recognizing content that deviates from known patterns). If that model were right, Rigour should be easiest (pattern similarity is the core LLM skill) and Generativity hardest. But the observed inversion suggests the opposite is happening: models CAN reliably pattern-match to "generative-looking" content (open-ended questions that spawned follow-up work in training data), but they CANNOT reliably assess technical correctness for research questions because correctness requires domain knowledge that varies across model families.

**The deeper theoretical synthesis:** These two explanations converge on the same mechanism. The axis that requires *FACTUAL CHECKING of domain-specific technical claims* (Rigour) has higher AI judge error than the axes that require *PATTERN MATCHING to known distributions* (Novelty = "does this look novel?", Generativity = "does this look generative?"). AI judges are fundamentally distribution-matching engines. Pattern-matching tasks (novelty recognition, generativity detection) map directly onto their architecture. Factual verification tasks (correctness checking, rigour assessment) require domain knowledge that is inconsistently encoded across model families — particularly for frontier content where that knowledge is sparse in training data.

**This inverts the standard assumption in LLM-as-judge design:** Prior work (MT-Bench/NeurIPS 2023, CALM/NeurIPS 2024) assumes that factual/objective tasks are easier for AI judges than subjective creative tasks — hence the practice of using GPT-4 to evaluate "factual accuracy" with high confidence while flagging "creativity" evaluations as unreliable. Our data suggests this assumption is context-dependent. For routine content (is this answer factually correct about TCP/UDP?) the assumption holds. For frontier research content (is this question's technical framing correct about the Log-Rank Conjecture?), factual checking FAILS HARDER than pattern-matching, reversing the reliability gradient.

**Per-model asymmetries offer additional insight:**
- **Gemini Flash (N_MAE=0.41, lowest):** Gemini reliably assigns Novelty scores that align with human judgment. This is consistent with Gemini's training optimization for information retrieval — recognizing what is informationally "new" to a corpus is structurally similar to retrieval tasks.
- **Opus 4.6 (N_MAE=1.03, highest — uniquely bad on Novelty):** Opus is the harshest rater overall (avg N=1.79, lowest of all models) — it sees through jargon and rates genuine content as low-novelty even when the human rates it higher. This isn't miscalibration in the noise sense; it may be systematic over-penalization of questions that are not *open* research problems (HLE seeds are technically precise but not genuinely unsolved). Opus is correct to rate HLE seed novelty lower than the human's lenient 2.66 average — but the human rated only 29 items, and the MAE may reflect genuine legitimate disagreement about what "novel" means for a question.
- **GPT-5.4 mini (G_MAE=0.52, best on Generativity):** GPT-5.4 mini reliably predicts which questions "open new questions" in a way that matches human intuition. Likely reflects training on academic writing patterns where "generative" language (this opens new directions for research, future work includes...) has clear distributional signatures.

**The key asymmetry for the position paper:** Rigour evaluation of frontier questions requires knowing whether the question's own technical premise is correct — which is a DOMAIN KNOWLEDGE task that fails at the frontier. Novelty and Generativity evaluation are PATTERN RECOGNITION tasks — "does this match the pattern of novel academic work?" and "does this match the pattern of research that spawned follow-up?" — which are fundamentally within-distribution tasks that LLMs can perform reliably. The gradient inversion is the fingerprint of this architecture-level distinction.

**Connection to previous findings:** This finding deepens Candidates D and E. If R_error > N_error for most models, and if high R_error is concentrated on frontier content (where technical claim checking is most likely to fail), then the disagreement-as-frontier-signal claim (Finding 4) should predict that Rigour-axis disagreement is the best frontier indicator. A high-disagreement question's Rigour disagreement (not Novelty or Generativity disagreement) should be the strongest predictor of human frontier labels. This is a testable prediction.

**Devil's Advocate:** The strongest objection is that the inversion might be an artifact of the specific rubric calibration examples, which all use ANSWERS (Euclid's proof, √2 proof, Gödel's theorems). Models trained to evaluate answer-quality rigour may be poorly calibrated for evaluating question-rigour — but this would make the finding a measurement error, not a structural claim about AI judges. The counter: the same rubric was given to all 5 models, and they all show R_error > G_error for most (4/5). If this were pure miscalibration from the rubric examples, we'd expect more between-model variation. The consistency across models suggests a structural feature, not a rubric artifact.

Second objection: The sample asymmetry might drive the result. We have 45 seeds (complex frontier math), 37 IFDS (jargon-heavy technical questions), and 49 other-agent questions. If rigour is hard to assess for complex math (seeds) and easy to assess for jargon (IFDS), and if human ground-truth is more represented in seeds, the MAE on R might be inflated by the seed content specifically. However, the per-model consistency of R > G (4/5 models) across ALL 134 items suggests this isn't purely a seed-concentration artifact.

Third objection: This finding is too close to "we made a wrong prediction" without a clear positive claim. The paper can't just say "our prediction was wrong" — it needs to explain what the data is telling us about AI evaluation. The constructive version of the finding (factual checking fails harder than pattern matching at the frontier) is the publishable version. Without this framing, the finding is a limitation, not a contribution.

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

### Candidate E: "Disagreement Is the Frontier Signal" *(new, from Finding 4)*

**One-sentence claim:** Inter-judge disagreement among well-calibrated AI evaluators is a better detector of genuine frontier content than any consensus score — because the disagreement marks the *aleatoric* boundary of the judge panel's shared knowledge representation, while consensus reflects shared training distribution, not objective quality.

**Evidence for:**
- Our data: 4/5 human-labeled high-disagreement items (top 10 by std) are genuine frontier content (FrontierMath open problems, contested open conjectures)
- The 1 failure case explained by poorly-calibrated rater outlier (Haiku MAE=1.09)
- JudgeBench (arXiv 2410.12784, ICLR 2025): items where judges diverge most are the hardest/most difficult items, confirming disagreement→difficulty/frontier mapping
- Aleatoric/epistemic uncertainty distinction (Zerva et al., EMNLP 2022): frontier content produces irreducible evaluative disagreement — the disagreement IS the signal, not noise
- Plank (EMNLP 2022): annotation disagreement contains more information than consensus labels for subjective/ambiguous tasks; collapsing to consensus destroys signal
- Active learning analog (Settles 2009): high-uncertainty items are at the decision boundary where labels have maximum expected information gain — same principle applies to evaluation panels

**Evidence against:**
- Sample size: N=5 human-labeled high-disagreement items is underpowered; we don't have std(frontier_score) by category (Seeds vs IFDS) to test the claim systematically
- IFDS items appear in top-10 contested list — disagreement from outlier raters (Qwen's G=5 pattern) creates false positives
- Active learning analogy is suggestive, not rigorous — "decision boundary" is well-defined in active learning but undefined for open-ended frontier evaluation
- JudgeBench tests items with objective correct answers ("difficulty"); frontier content has no ground truth — the two properties may not transfer

**Surprise score: 3/5** — "Disagreement is a signal" has been argued in the annotation literature (Plank 2022), and "items where judges disagree are hard" is found in JudgeBench. The specifically novel contribution is the *frontier evaluation context* — applying this principle to the multi-model AI evaluation problem, where the disagreement signal is most needed and most counterintuitive (practitioners expect consensus = reliability). The active learning acquisition function framing (use disagreement to route items to human review) is the operationally new piece.

**Relationship to Candidate D:** E is the positive counterpart of D. D says: "consensus is a false confidence signal at the frontier." E says: "disagreement is the honest frontier signal." Together they form a complete theory: *the appropriate evaluation paradigm reuses inter-judge disagreement as the primary detection signal and routes high-disagreement items to human review.* E provides the constructive prescription that D lacks.

---

## TOP RECOMMENDATION

**Revised after 4 queue items: Candidate D + E unified is now the strongest recommendation, with a close second of Candidate D alone.**

**The new synthesis: D and E are one argument, not two.**

Finding 3 (D) and Finding 4 (E) are two sides of the same coin:
- **D:** When AI judges agree at the frontier, that consensus is unreliable — it amplifies shared hallucination from correlated training data. (Condorcet fails; error independence violated.)
- **E:** When AI judges disagree at the frontier, that disagreement is informative — it marks the epistemic boundary of the shared knowledge representation. (Aleatoric uncertainty is signal; calibrated disagreement predicts human frontier labels.)

The unified claim: **"For AI evaluation of frontier intellectual content, the diagnostic signal is inverted — consensus indicates reliability only for non-frontier content, and disagreement indicates frontier-ness for genuinely novel content."**

This is a single, sharp, falsifiable thesis:
1. It attacks an assumption (consensus = reliability) held by every major evaluation paper using multi-model panels
2. It provides a constructive alternative (use disagreement as the frontier detection signal)
3. It has theoretical grounding in Condorcet (D) and aleatoric uncertainty theory (E)
4. It has empirical support from: Log-Rank anecdote (D), 4/5 contested-item human labels (E), JudgeBench (E), correlated errors literature (D)
5. It has an operational implication: route high-disagreement items to human review rather than averaging them down

**Why D+E beats the alternatives:**

- **vs Candidate A (Novelty Impossibility):** A is partially anticipated (CALM 2024, NeurIPS); the inversion finding requires the HLE seeds to genuinely BE non-novel, which is debatable. D+E attacks an assumption, not a known bias.
- **vs Candidate B (Scale Anti-Correlation):** B has the N=29 weakness and cross-family confound. D+E has stronger evidence (theoretical + multiple empirical threads) without depending on the thin human sample.
- **vs Candidate C (Synthesis A+B):** C combines two weak findings into one compound claim. D+E is a single coherent mechanism with constructive implications.

**Revised argument structure for the paper (incorporating Finding 4):**

1. **Setup:** Multi-model LLM-as-judge is standard practice. The Condorcet Jury Theorem is its implicit justification — aggregate diverse models to reduce individual error. This requires error independence.

2. **Part I — Consensus fails (Finding 3/D):** Error independence fails for frontier content because frontier topics are discussed in small, heavily-cited corpora that all frontier-tier models have read. Three model families made the identical terminological error on the Log-Rank Conjecture. "Great Models Think Alike" (arXiv 2502.04313, ICML 2025 spotlight): as models become more capable, their errors become more similar. Consensus among capable models on frontier content = shared hallucination, not reliability.

3. **Part II — Disagreement succeeds (Finding 4/E):** If consensus is the wrong signal, what is the right signal? Our data: 4/5 human-labeled high-disagreement items are genuine frontier content. The theoretical framing: frontier content exceeds the reliable evaluation range of all judges — its evaluability is irreducibly uncertain (aleatoric, not epistemic). JudgeBench confirms: items where judges diverge are the hardest items. The active learning analog: high-disagreement items are at the knowledge boundary, where human ground-truth labels have maximum expected information gain.

4. **The operational proposal:** Disagreement-augmented frontier detection. Replace `sort=mean(frontier_score)` with `sort=mean + λ·std(frontier_score from calibrated judges)`. Items in the top decile of disagreement among well-calibrated judges should be routed to human review, not averaged into mediocrity. This reframes evaluation from a voting task toward a consensus to a *probing task toward the boundary of shared knowledge*.

5. **The implication for the field:** Every AI evaluation system using multi-model panels — LMArena, AlpacaEval, MT-Bench, FrontierMath scoring — currently throws away the disagreement signal. The inter-judge variance is computed, noted in limitations, then aggregated away. We argue that this variance IS the primary signal for frontier content, and discarding it is discarding the most informative measurement the evaluation system produces.

**Why this matters beyond our platform:** If disagreement among AI judges is the best available signal for "this is genuinely frontier," then the field's current practice of averaging AI judges into a consensus score is systematically *suppressing* the frontier signal. The items that would rank highest on a disagreement-weighted score are exactly the items the field most needs to identify and route to human evaluation. This is not a marginal improvement to evaluation methodology — it inverts the ranking criterion.

**Update after Finding 5:** The Calibration Gradient Inversion directly confirms the D+E thesis. R_error is highest for 4/5 models — models disagree most about Rigour. This is now the mechanistic explanation for both D and E: Rigour evaluation requires domain-specific factual checking, which fails for frontier content (because the relevant knowledge is sparse and inconsistently encoded across model families). Novelty and Generativity evaluation require pattern matching, which succeeds for frontier content (because "novel-looking" and "generative-looking" content has clear distributional signatures). The three findings (D, E, Finding 5) now form a coherent mechanism: (1) AI judges fail hardest on Rigour at the frontier [Finding 5], (2) this failure is correlated across model families [Finding 3/D], (3) the inter-judge disagreement on Rigour specifically identifies frontier content [Finding 4/E].

---

### Candidate F: "The Factual-Checking Reversal" *(new, from Finding 5)*

**One-sentence claim:** AI judges' evaluation quality gradient inverts for frontier content — they agree well on pattern-matching axes (Novelty, Generativity) but disagree severely on the factual-checking axis (Rigour), because frontier questions require domain-specific correctness verification that is inconsistently encoded across model families.

**Evidence for:**
- R MAE highest for 4/5 models in our experiment (G MAE lowest for 3/5)
- Consistent across model families (not driven by one outlier model)
- Coherent mechanism: Novelty/Generativity = pattern matching (distributional task; reliable for LLMs); Rigour = factual checking of technical claims (domain knowledge task; unreliable at frontier)
- Connection to Finding 3 (Log-Rank error): three model families confidently wrongly evaluated the "rigour" of a technical claim (calling an upper bound a proof barrier) — Rigour failure was the SPECIFIC failure mode
- Connection to Finding 4: R-axis disagreement specifically should be the best frontier probe

**Evidence against:**
- The inversion might be an artifact of rubric examples using answers (not questions) to calibrate Rigour — models may be systematically miscalibrated on R for questions specifically
- GPT-5.4 mini and Qwen Coder DO show G < N < R (the predicted ordering) — the inversion is not universal
- Opus's anomaly (N_MAE=1.03 highest) doesn't fit the clean narrative — if N is pattern matching, Opus should be good at it
- N=29 human items is still the ground truth sample, and the pattern may not replicate on a larger human sample

**Surprise score: 3/5** — "LLMs are bad at factual checking" is known, but "factual checking is the hardest evaluation axis, even harder than creativity/novelty" is counterintuitive and inverts the assumption of every LLM-as-judge paper that treats factual accuracy as the reliable baseline.

**Relationship to D+E:** F is the mechanistic explanation for D and E. It answers "WHY does consensus fail at the frontier?" (because R, the axis most likely to have correlated errors from shared domain misconceptions, drives the consensus failures) and "WHY is disagreement the frontier signal?" (because R-axis disagreement specifically marks the boundary of reliable domain knowledge encoding across models). F, D, and E are one argument.

---

## FINAL TOP RECOMMENDATION (all 5 queue items complete)

**The paper's thesis: Candidates D + E + F unified — "Frontier Evaluation Requires a New Measurement Paradigm."**

The three findings point to one coherent argument:

> **Multi-model AI evaluation panels, designed to reduce error through diversity and consensus, systematically fail for frontier intellectual content — and the failure signal they produce (disagreement) is more informative than the consensus signal they are designed to produce.**

The three-part structure:

**Mechanism (Finding 5/F):** AI judges fail hardest on Rigour — the axis that requires domain-specific factual verification. Rigour evaluation of frontier research questions cannot be reduced to pattern matching; it requires checking whether the question's technical framing is itself correct, which depends on domain knowledge that is inconsistently encoded across model families. Finding 5 shows R_error > N_error, G_error for 4/5 models — the opposite of what the "objectivity hierarchy" predicts.

**Correlated failure (Finding 3/D):** The Rigour evaluation failures are correlated across model families — not independent random errors, but shared misconceptions from co-occurring training corpora. The Log-Rank error (three families, identical mistake) is a concrete instance. This violates the Condorcet independence assumption: consensus amplifies the shared error rather than cancelling it.

**The silver lining (Finding 4/E):** The same failure mode produces an actionable signal. When well-calibrated judges disagree about a question's Rigour, that disagreement marks the boundary of their shared domain knowledge — which is precisely the frontier of the question's evaluability. 4/5 human-labeled high-disagreement items are genuine frontier content. The inter-judge disagreement IS the frontier signal; averaging it into a consensus score discards the most informative measurement.

**One-sentence position:** *For frontier intellectual content, AI judge consensus is a false reliability signal and inter-judge disagreement is the true frontier signal — because judges fail hardest on factual verification (not pattern recognition), these failures are correlated across model families, and the resulting disagreement marks the exact boundary where human evaluation is most needed.*

**The argument is now complete and coherent across all five findings:**

1. (Finding 1/A): AI judges invert novelty rankings — they reward pattern-matching to novelty-resembling content, not actual novelty. *This is the problem statement.*
2. (Finding 2/B): Larger models are worse judges for frontier content. *This is the scale dimension of the problem.*
3. (Finding 3/D): Diverse model panels produce correlated errors — consensus amplifies shared hallucination. *This is why the standard solution (more judges) fails.*
4. (Finding 4/E): Inter-judge disagreement is the frontier signal — it marks the boundary of shared knowledge. *This is the positive alternative.*
5. (Finding 5/F): R-axis disagreement is highest — factual checking fails harder than pattern matching. *This is the mechanistic explanation.*

All five findings converge on the same position: **frontier evaluation requires inverting the standard paradigm — from consensus-as-reliability-signal to disagreement-as-frontier-probe.**

**Single sharpest claim for a one-sentence abstract (choose one):**

- **Conservative version (strongest evidence):** "Multi-model evaluation panels violate the Condorcet independence assumption for frontier content, making panel consensus a false confidence signal — demonstrated by three model families independently making the identical terminological error on the Log-Rank Conjecture."

- **Provocative version (maximum surprise):** "The best predictor of whether intellectual content is genuinely at the frontier is not the AI evaluation panel's consensus score — it is their disagreement score."

- **Mechanistic version (most theoretically grounded):** "AI judges agree well on novelty and generativity (pattern-matching tasks) but disagree severely on rigour (factual-checking tasks), and this disagreement about rigour is correlated across model families — making panel consensus on frontier content a measurement of shared misconception, not shared truth."

**Recommendation:** Lead with the provocative version in the abstract ("disagreement is the frontier signal"), support with the mechanistic version in the technical sections, and use the conservative version as the falsifiable claim in the experimental section.

---
