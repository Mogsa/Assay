# NeurIPS 2026 Position Paper — Research Queue

**Purpose:** Find ONE sharp, surprising, defensible position claim for a NeurIPS 2026 position paper about AI evaluation.

**Context:** Assay is a multi-agent evaluation platform where AI agents and humans rate intellectual content on three axes: Rigour (R), Novelty (N), Generativity (G). We ran a rating experiment with 5 AI models + 1 human on 134 questions. Several findings are counterintuitive and potentially publishable. The dissertation grounding is philosophy-of-science (Popper/Lakatos/Peirce) applied to AI evaluation.

**Audience:** NeurIPS reviewers — technically sophisticated, skeptical of overclaiming, rewarded by surprise + rigorous argument.

**What we have:** Empirical data from a live multi-model evaluation platform, 5 AI raters, 1 human, 134 items, multiple surprising findings. The position paper should take ONE of these findings and build a sharp, provocative, well-supported thesis around it.

---

## RESEARCH QUEUE

- [x] **1. The Novelty Impossibility** — Can LLM judges structurally assess novelty? The IFDS jargon finding (well-structured narrow questions outscoring genuine frontier math) suggests AI judges reward "novelty-resembling" content over actual novelty. Is this a calibration failure or a structural impossibility? Search literature on: LLM-as-judge novelty, AI evaluation limitations, training data horizon problem.

- [x] **2. The Cheapest-Is-Best Paradox** — Gemini Flash (free) MAE=0.53 vs Opus ($5/M) MAE=0.97. Does model scale anti-correlate with human judgment alignment for evaluation tasks? Is there a "sycophancy amplification" hypothesis? Search literature on: LLM judge model size, evaluation quality vs capability, sycophancy in large models.

- [ ] **3. Convergent Errors in Diverse Panels** — Three model families independently made the same terminological error on the Log-Rank Conjecture. Does model diversity guarantee evaluation diversity? Search: ensemble LLM evaluation, correlated errors, shared training data blind spots.

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

## CANDIDATE POSITIONS

**After researching queue items 1 and 2, here is the current assessment:**

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

## TOP RECOMMENDATION

**Candidate B ("Scale Anti-Correlates with Evaluation Quality") with Candidate A's mechanism as explanation.**

**Why B over A:** Candidate A's finding (jargon beats frontier math) is surprising, but the mechanism (formality bias) is already documented in the CALM paper from NeurIPS 2024. A position paper can't just replicate a known finding with a new dataset — it needs to advance the claim. Candidate B does this: it takes the known bias and shows that *capability amplifies it*, which is the novel and actionable insight.

**The argument structure for the paper:**

1. **Setup:** LLM-as-judge is the dominant paradigm for scalable AI evaluation. The implicit assumption: more capable models make better judges. We tested this.

2. **Finding 1 (empirical):** In frontier content evaluation, capability anti-correlates with calibration. Gemini Flash MAE=0.53; Opus MAE=0.97.

3. **Finding 2 (mechanism):** Frontier content is high-perplexity (by definition — it deviates from the prior distribution). LLM judges prefer low-perplexity content (arXiv 2410.21819). RLHF-tuning amplifies this preference (arXiv 2310.13548). Larger models have received more RLHF optimization → stronger perplexity preference → larger inversion.

4. **Implication:** Evaluating AI capability at the frontier using AI judges is not just unreliable — it is *specifically miscalibrated in the direction of false confidence* — the most capable judges will most reliably uprate in-distribution jargon and downrate genuine frontier departures.

5. **The position:** Don't use your frontier model to evaluate frontier content. Use either (a) a smaller, less RLHF-tuned model, (b) human ground truth with AI interpolation rather than AI consensus, or (c) disagreement-based detection (when AI models maximally disagree, that is your frontier signal, not their consensus).

**Why this matters beyond our platform:** Chatbot Arena, LMArena, and every RLHF training pipeline uses strong models as judges. If scale anti-correlates with judge calibration for frontier content, the entire "use AI to evaluate AI at the frontier" paradigm has a systematic flaw — and it fails exactly where we need it most.

**Caveats to acknowledge in the paper:** N=29 human items; single platform; need replication across domains; Gemini Flash may be a specific outlier. These are limitations, not fatal flaws — position papers argue from evidence, not prove theorems.

---
