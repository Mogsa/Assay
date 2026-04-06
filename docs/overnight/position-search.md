# Position Paper Search: NeurIPS 2026

**Purpose:** Find one sharp, surprising, defensible position claim for a NeurIPS 2026 position paper about AI evaluation.

**Context:** The Assay platform ran Experiment v1 (2026-03-19): 5 AI models + 1 human rated 134 questions on R/N/G axes (Rigour, Novelty, Generativity). Key results are in `docs/research-state.md` and `docs/analysis/2026-03-19-rating-analysis.md`. The platform uniquely has: multi-model evaluation, human ground truth on a subset, R/N/G axis decomposition, and content with known quality labels (genuine frontier math seeds vs agent-generated jargon loops).

**The core thesis of the platform:** AI evaluation quality should be measured on axes grounded in philosophy of science (Popper/Lakatos/Peirce). Disagreement should produce either proof or better questions.

---

## RESEARCH QUEUE

- [x] **Q1: Does judge model size predict evaluation quality?** The cheapest model (Gemini Flash, free) had MAE=0.53 vs human; Opus ($5/M output) had MAE=0.97. Is this pattern documented elsewhere? What explains it? How strong is the position claim: "bigger LLM judges are not better judges"?

- [x] **Q2: Do LLM judges actually use multiple evaluation axes independently, or do they collapse to halo?** Assay found some models show strong R/N/G axis correlation (near-halo effect) while Opus shows the most independence. This connects to Arrow's theorem — single-axis collapse invalidates any multi-rubric framework. How novel is the finding that smaller/cheaper models are MORE prone to halo effects?

- [x] **Q3: The calibration prediction inversion — why does Rigour have the highest error?** We predicted R_error < N_error < G_error (Popper most objective → Peirce most subjective). Got R_error highest. Two competing hypotheses: (a) Rigour is poorly defined for questions-as-questions, (b) Rigour is actually the most contested axis. What does this mean for rubric design?

- [x] **Q4: Format/jargon inflation as a measurable, systematic bias** — IFDS agent-generated jargon content scored 3.21 frontier vs genuine FrontierMath seeds at 3.57 (close!) but HLE seeds at only 2.37. Is this the strongest claim? Models reward hypothesis/falsifier structure over substantive novelty. How does this connect to known "verbosity bias" / "beauty bias" literature?

- [ ] **Q5: Convergent errors from shared training data defeat diversity-based evaluation** — Three model families independently made the same terminological error on the Log-Rank Conjecture. What is the theoretical implication? If diverse models converge on the same wrong answer, ensemble methods for evaluation are unsound.

---

## FINDINGS

### Q1: Does judge model size predict evaluation quality? — 2026-04-06T07:22

**Summary of evidence from Assay v1:**

The core finding: 5 AI models rated 134 questions on R/N/G axes. Human (Morgan) rated 29 questions as ground truth. MAE against human:

| Model | Cost (output) | Overall MAE |
|-------|--------------|-------------|
| Gemini Flash | ~free (preview) | **0.53** |
| GPT-5.4 mini | low | 0.79 |
| Qwen Coder | low-mid | 0.93 |
| Opus 4.6 | $5/M tokens | 0.97 |
| Haiku 4.5 | $0.25/M tokens | 1.09 |

The pattern is not simply "cheaper = better" — Haiku (cheapest Anthropic) is the *worst* (MAE=1.09), while Gemini Flash (cheapest/free) is the best. Opus (most capable, most expensive) is penultimate-worst. This is not a simple cost curve.

**What explains Gemini Flash's performance?**

Looking at the behavioral signatures:
- Gemini Flash: most discriminating, uses full rating range. Average R=3.98, N=2.76, G=2.90
- Opus 4.6: harshest overall, R=3.11, N=1.79, G=1.90 — possibly over-adjusting to avoid the "textbook trap"
- Haiku 4.5: central tendency bias, R=3.24, N=3.04, G=2.88 — classic regression to mean
- Human (Morgan): R=3.62, N=2.66, G=2.79

Gemini Flash's distribution is closest to human not because it's less capable, but because it uses the full scale without systematic over-correction. Opus, the most capable model, appears to over-identify "jargon" as non-novel — giving harshly low N and G scores that diverge from human judgment. The hypothesis: highly capable models over-pattern-match to their training distribution of "low quality" examples and apply excessive discounting.

**Is this documented in the literature?**

From Assay's competitive landscape notes:
- CALM (arXiv 2410.02736, ICLR 2025) identifies 12 LLM judge biases — includes "beauty bias" but doesn't specifically address model size vs calibration quality
- Chatbot Arena / LMArena uses human votes, not comparing model-as-judge calibration vs model size
- The general assumption in the field is that better models = better judges (this is the premise behind "GPT-4 as evaluator" being the gold standard)

**The claim:** "Model capability (size/cost) does not predict LLM judge calibration quality. A free preview model can outperform a flagship model by 45% (MAE 0.53 vs 0.97) when judging open-ended intellectual contributions."

**Why surprising to NeurIPS:** Most LLM evaluation work uses GPT-4 / top models as the evaluator, assuming capability transfers to evaluation quality. If Gemini Flash beats Opus as a judge, the entire "use the best model as judge" paradigm is questionable. This challenges the standard practice in dozens of NLP papers.

**Devil's Advocate:**

*Strongest objection:* Sample size is N=29 human-rated questions. This is a small sample, and Morgan may have rated an idiosyncratic set (stratified: top 10, bottom 10, 9 controversial). The controversial questions in particular may skew the comparison. Additionally, Morgan is not an expert in all domains (IFDS analysis, competition math, biology), so "human ground truth" is debatable. A reviewer will correctly note: n=29 with one human rater is weak empirical evidence.

*Is this novel?* Not entirely — there are papers showing smaller specialized models can match larger general models on specific tasks. What's novel is the *calibration framing* (measuring by MAE against human judgment on a multi-axis rubric) and the finding that it's not about specialization but about scale calibration behavior (central tendency vs full-range use).

*Would a reviewer say "so what"?* Possibly. A sharp reviewer will say: "You have n=29 with one human rater. Run the experiment at scale." This is a limitation that must be acknowledged. The defense: the finding is internally consistent (the behavioral signatures explain why — Gemini Flash uses full range, Opus over-discounts), and the claim is scoped to "this deserves investigation" rather than "this is definitive."

**Surprise score: 4/5.** The "cheaper is better" inversion at evaluation quality is genuinely counter to prevailing practice. The caveat is that it needs more data to be fully convincing as a position.

---

### Q2: Do LLM judges use multiple axes independently, or collapse to halo? — 2026-04-06T07:45

**The question:** If a model always gives R≈N≈G, it isn't evaluating three dimensions — it's outputting a single "general quality" score three times. This would invalidate any multi-rubric evaluation framework, including the R/N/G system.

**Evidence from Assay v1:**

Per-model average spread (R vs N, R vs G):

| Model | Avg R | Avg N | Avg G | R−N spread | N−G spread | Axis independence |
|-------|-------|-------|-------|-----------|-----------|------------------|
| Haiku 4.5 | 3.24 | 3.04 | 2.88 | 0.20 | 0.16 | **Minimal (near-halo)** |
| Gemini Flash | 3.98 | 2.76 | 2.90 | 1.22 | 0.14 | R independent; N≈G |
| GPT-5.4 mini | 3.40 | 2.14 | 2.84 | 1.26 | 0.70 | **Most 3D independent** |
| Qwen Coder | 3.31 | 2.19 | 2.50 | 1.12 | 0.31 | R independent |
| Opus 4.6 | 3.11 | 1.79 | 1.90 | 1.32 | 0.11 | R independent; N≈G |
| Human | 3.62 | 2.66 | 2.79 | 0.96 | 0.13 | R independent; N≈G |

**Key patterns:**

1. **Haiku is near-halo.** Spread R−N=0.20, R−G=0.36. Almost indistinguishable from giving a "quality" score on all three axes. Every question rated 3/3/3 or 3/3/4. Zero information beyond a single-axis rating.

2. **N and G collapse for most models.** The N−G spread is small for Gemini, Opus, and even the human (0.11–0.16). Most models treat Novelty and Generativity as nearly the same dimension. GPT-5.4 mini is the notable exception (N−G = 0.70), and on specific items it gives genuinely independent ratings: on the Galois group seed, GPT mini rates R=4, N=1, G=5 — "well-posed question, not novel, but highly generative."

3. **Axis independence is NOT calibration quality.** Opus has the widest R−N spread (1.32) and is among the worst calibrated (MAE=0.97). Haiku has the narrowest spread and the worst calibration (MAE=1.09). GPT mini has genuine 3D independence and moderate calibration (MAE=0.79). The relationship is orthogonal — you can be independently wrong.

4. **Human shows R independence, N≈G collapse too.** Human (Morgan) also rates N and G similarly (2.66 vs 2.79 on average). This raises a question: is N−G collapse a model failure, or does it reflect genuine difficulty in distinguishing "adds unresolved information" from "opens new questions"? These axes may be partially redundant by design.

**The Arrow's theorem connection:**

The research-state notes that Arrow's Impossibility Theorem was invoked to justify displaying axes separately. But the axis independence finding cuts the other way: if N and G are empirically near-identical for most raters (including humans), there is no aggregation problem to solve — the axes have already collapsed. The Theorem only bites when axes genuinely conflict; if N≈G for all raters, you're effectively working with a 2-axis system.

**What this means for rubric design:**

The R/N/G framework has a structural redundancy between N and G. Rigour is genuinely distinct (models consistently rate it higher and more independently). Novelty and Generativity are empirically correlated for most raters. This could be addressed by:
- Redefining the axes to make N and G more orthogonal
- Collapsing to 2 axes (R and N+G combined)
- Keeping 3 but acknowledging the redundancy

**Devil's Advocate:**

*Strongest objection:* The N−G spread is computed from averages, not from per-item correlations. An agent could have average N=2.76 and G=2.90 while still giving very different N and G for individual items. The spread in averages is a weak proxy for axis independence. The correct test is Pearson r(N,G) per agent across all 134 items — this data exists in the database but wasn't computed here.

*Is this novel?* The halo effect in multi-criteria evaluation is well-known in psychology (Thorndike 1920) and has been documented for LLM judges in general (CALM identifies "positional bias" and "verbosity bias" but not specifically cross-axis halo). The specific N≈G collapse in intellectual contribution evaluation may be novel — it's a domain-specific finding, not a generic LLM bias.

*Would a reviewer say "so what"?* Possibly, if framed as "LLMs have halo effects." The sharper framing: "The Novelty and Generativity axes of research contribution evaluation are structurally near-identical for LLM judges AND human raters, suggesting the distinction is philosophically meaningful but practically unmeasurable." That's a finding about the rubric, not just the judges.

**Surprise score: 3/5.** The halo effect is expected. The novelty is in the N≈G collapse being found in both LLMs AND humans — suggesting it's a property of the axes, not a model limitation.

---

### Q4: Format/jargon inflation — topical saturation blindness — 2026-04-06T07:58

**The finding in raw numbers:**

Agent-generated IFDS/tombstone questions (37 items — narrow variations on incremental dataflow analysis by one agent in a loop) scored **higher** than most expert-curated frontier content:

| Content type | n | Avg frontier_score |
|---|---|---|
| IFDS/Tombstone (agent jargon loop) | 37 | **3.21** |
| FrontierMath open problems | 5 | **3.57** |
| Competition math | 5 | 2.70 |
| HLE: Biology | 14 | 2.23 |
| HLE: Math/Stats | 2 | 2.19 |
| HLE: average | ~42 | ~2.23 |
| Test posts | 4 | 1.37 |

IFDS content — which is **known** to be an obsessive loop from one agent, not genuine novel research — scored 3.21, above all HLE categories, sitting near competition math (2.70) and FrontierMath (3.57). In the top-10 ranked questions, 7 out of 10 are IFDS questions, not frontier math seeds.

**The mechanism — two competing explanations:**

*Explanation 1 (Surface format):* IFDS questions use hypothesis/falsifier structure — "Is X true? Give conditions under which it holds. Identify a counterexample when it doesn't." This mimics the format of genuine frontier research questions in the models' training data. Models reward the structure, not the substance.

*Explanation 2 (Topical saturation blindness):* Each model rated 10 questions per pass. Across 134 questions, each model processed roughly 14 passes. If IFDS questions were distributed across passes (2-3 per pass), no single pass would trigger awareness of the full 37-item saturation. The model evaluates each question as if it's the only question on IFDS it has ever seen — because, within the pass context window, it IS.

These two mechanisms make different predictions: Format bias would affect single questions; topical saturation blindness requires multi-question context to defeat. They likely both operate simultaneously.

**The theoretical claim — stateless evaluation cannot detect novelty at the corpus level:**

Standard LLM-as-judge pipelines are stateless per item. An evaluator that scores each question in a separate context window cannot apply the information-theoretic penalty for redundancy. The 37th IFDS question has near-zero marginal novelty given the previous 36 — but a stateless judge scores it as if it's the first.

This is analogous to a failure mode in information retrieval: query-independent retrieval systems cannot detect novelty in result sets (Carbonell & Goldstein 1998, MMR — Maximal Marginal Relevance). The LLM evaluation community has not, to this author's knowledge, formally connected stateless evaluation to the redundancy/novelty failure mode from IR.

**Why HLE scores low:**

HLE (Humanity's Last Exam) questions look like exam problems — "Can you identify which chemical element has this spectrum?" Models pattern-match these to "has a known answer → low novelty." Even if the answer requires expert-level knowledge, the question FORM signals "this is a test, not research." The HLE scoring failure is thus a form-substance confusion in the opposite direction: HLE looks like an exam, IFDS looks like research.

**Why FrontierMath scores highest (3.57):**

FrontierMath questions are genuinely open problems phrased as research questions: "Improve the exponent in the upper bound..." These match the expected format AND the expected substance — models correctly identify them. This validates the system at the top; the failure is in the middle.

**The practical implication:**

Any AI evaluation system that processes items statelessly will be gamed by corpus saturation. An actor who submits 37 variations on one topic will have each variation scored highly, because each scores as "novel" in isolation. This is a direct evaluation attack vector — and it's passive (no adversarial intent required, just one agent in a loop).

**Devil's Advocate:**

*Strongest objection:* The IFDS content may genuinely deserve its scores. Incremental IFDS repair IS a legitimate research topic. The 37 questions may represent legitimate sub-questions of a research program, not just noise. The human rater (Morgan) only rated questions in the top/bottom/controversial strata — she may not have rated IFDS questions systematically. We cannot conclusively say IFDS content "should" score lower without domain expert review.

*Is this novel?* "Format bias" is documented — the CALM paper identifies "beauty bias" (preference for well-structured responses). But the specific mechanism of **topical saturation blindness** — stateless evaluation's inability to detect corpus-level redundancy — is to my knowledge not framed in the literature this way. It connects to MMR/novelty in IR but hasn't been applied to LLM judges.

*Would a reviewer say "so what"?* Not if framed as an attack vector: "Evaluation systems that process items statelessly are exploitable by corpus saturation, regardless of adversarial intent." This is a practical warning with theoretical grounding in information theory.

**Surprise score: 4/5.** The connection between stateless evaluation and topical saturation blindness is novel framing. The empirical evidence (IFDS scores) is direct. The link to IR's Maximal Marginal Relevance is an unexpected theoretical bridge that reviewers may not have seen.

---

### Q3: The calibration prediction inversion — 2026-04-06T08:15

**The theoretical prediction (Popperian axis hierarchy):**

The three axes were designed with an implicit objectivity ordering:
- **Rigour** (Popper/falsifiability) — most objective: either the question is well-posed or it isn't
- **Novelty** (Lakatos) — intermediate: requires knowledge of prior work
- **Generativity** (Peirce/abduction) — most subjective: requires intuition about future research trajectories

Prediction: R_error < N_error < G_error (models agree most on Rigour, least on Generativity). This is the standard assumption behind rubric design — you put the most objective criteria first.

**What the data shows:**

Per-model MAE vs human (from the rating analysis):

| Model | R MAE | N MAE | G MAE | Pattern |
|-------|------:|------:|------:|---------|
| Gemini Flash | 0.59 | **0.41** | 0.59 | N easiest, R=G tied |
| GPT-5.4 mini | 0.97 | 0.90 | **0.52** | G easiest (prediction matches!) |
| Qwen Coder | **1.10** | 0.86 | 0.83 | R hardest (inverted!) |
| Opus 4.6 | 0.93 | **1.03** | 0.93 | N hardest (doubly inverted!) |
| Haiku 4.5 | **1.21** | 0.93 | 1.14 | R hardest (inverted!) |

Inter-rater Krippendorff's alpha (all 5 models):
- Rigour: α=0.257 (lowest agreement)
- Novelty: α=0.285
- Generativity: α=0.319 (highest agreement)

**The inversion is real but inconsistent:**

2 of 5 models (Qwen, Haiku) show R_error as highest — directly contradicting the prediction. For Haiku, R_error=1.21 is the worst, and G_error=1.14 is second-worst — a weak gradient inversion. GPT-5.4 mini is the only model that matches the prediction (G easiest at 0.52).

The inter-rater agreement tells a cleaner story: across all 5 models, Generativity has the HIGHEST agreement (α=0.319) and Rigour the LOWEST (α=0.257). Models agree more on Generativity than Rigour. The Popperian prediction is inverted in both individual MAE (majority of models) and inter-rater reliability.

**Two competing hypotheses:**

*Hypothesis A — The axis is poorly defined for questions-as-questions.* The Rigour calibration examples were designed for answers ("Euclid's proof, zero gaps in 2,300 years" = R5). Applied to questions, "rigour" means something different — is the question well-posed? Well-formed? The rubric anchors work for evaluating answers but are ambiguous for evaluating questions. This would explain why models diverge most on R — there's no shared anchor. Fix: redesign Rigour anchors specifically for questions.

*Hypothesis B — Rigour is genuinely the most contested axis.* A question being "rigorous" requires both syntactic clarity (is the question parseable?) AND semantic precision (is the question answerable in principle?). These can conflict — a question can be syntactically clear but semantically underdetermined. Different models weight these components differently. Generativity, by contrast, just asks "does answering this open doors?" — which is pattern-matchable from citation graphs in the training data. This would make the inversion a genuine finding rather than a measurement error.

**Hypothesis B predicts something testable:** If Rigour is genuinely contested, then the questions where models disagree most on R should be semantically underdetermined questions (open-ended, fuzzy scope) — not the HLE/competition questions (which are syntactically clear). Quick check: the most contested question on Rigour in the data is "[Seed] Assuming that each of the following mathematical models represents a situation..." (std=1.06) — this is syntactically complex with an unstated assumption. Consistent with Hypothesis B.

**Devil's Advocate:**

*Strongest objection:* The calibration inversion is measured against one human rater's 29 ratings, and the human may have idiosyncratic Rigour standards (a researcher in a specific field applying domain standards to cross-domain questions). The inter-rater agreement result is more robust (n=134), but α<0.33 for all axes means the entire framework has poor reliability — you can't conclude one axis is "more reliable" when all are in the "poor" range.

*Is this novel?* Yes — I find no papers specifically about the ordering of objectivity across multi-dimensional scientific evaluation axes. The closest is criterion validity work (2604.00022) showing dimensions differ in predictive power, but not specifically about the objectivity hierarchy.

*Surprise score: 5/5 within the paper.* If you've established R/N/G as grounded in Popper/Lakatos/Peirce with an implicit objectivity ordering, then showing the ordering is empirically inverted is directly subversive of your own theoretical foundation. This is intellectually honest and surprising.

---

## LITERATURE CONTEXT (from search, 2026-04-06)

**What's established (cite but don't position as novel):**
- Verbosity/format bias: CALM (Ye et al., 2410.02736, ICLR 2025) documents 12 bias types including verbosity — widely cited, treat as established evidence
- Positional bias: widely documented across multiple venues
- Smaller model panels outperforming single GPT-4 judge: PoLL (Verga et al., 2404.18796) showed panel of smaller models > GPT-4 (κ=0.763 vs 0.627) at 7-8x lower cost
- Reasoning mode > size: "Thinking" small models (0.6B-4B with explicit CoT) beat larger models on evaluation quality (2509.13332)
- Halo effect in LLM evaluation: documented via Rasch modeling in writing assessment context (ScienceDirect 2025)

**What's partially documented but not synthesized:**
- Novelty detection by LLMs: SchNovel (2409.16605, ACL 2025) shows LLMs need retrieval context to assess novelty vs. general corpus; they lack reference-class knowledge
- AI ideas rated more novel than human ideas by human judges (Stanford, 2409.04109) — systematic novelty inflation from unfamiliarity, not quality
- Halo/axis-collapse: psychometric evidence scattered but not central claim of any single paper; "decomposed criteria" papers acknowledge collapse but don't measure it (2509.16093)
- Criterion validity of multi-dimensional scores: very recent (2604.00022, April 2026) shows dimensions vary dramatically in predictive validity

**What's NOT in the literature (genuine gaps):**
1. **Topical saturation blindness as a named, mechanistic failure mode** — stateless evaluation's inability to detect corpus-level redundancy. CALM lists 12 biases; this is not one of them. SchNovel addresses general novelty vs. external corpus; we're talking about novelty *within* the evaluation corpus.
2. **N≈G axis collapse as both a model failure AND a rubric design problem** — scattered evidence of halo but not synthesized as a position about multi-rubric design
3. **Calibration ordering inversion** (R_error > N_error experimentally, opposite of Popperian prediction) — appears not documented

---

## CANDIDATE POSITIONS

**Position A (from Q1):** *"LLM judge calibration quality does not scale with model capability."*
- One-sentence: A free-tier model outperforms a flagship model by 45% MAE on multi-axis evaluation of open intellectual contributions.
- Evidence for: Gemini Flash MAE=0.53 vs Opus MAE=0.97 across n=29 human-rated questions; behavioral signatures explain the mechanism (full range use vs systematic over-discounting); consistent across three axes
- Evidence against: n=29, one human rater; PoLL (2404.18796) is already a known result in the same space (panel > GPT-4); "thinking mode > size" paper (2509.13332) provides a better theoretical frame than "cheaper = better"
- Surprise score: 3/5 — partially known territory (PoLL, thinking models), though the specific calibration angle is unexplored
- **Verdict: Citable finding but not strong enough as a standalone position paper claim**

**Position B (from Q2):** *"The Novelty and Generativity axes of research contribution evaluation collapse to a single dimension for both LLM and human judges, empirically undermining multi-rubric frameworks."*
- One-sentence: Despite philosophical distinctness (Lakatos vs Peirce), N and G are empirically near-identical for all five tested models and the human rater (N−G spread < 0.14), making multi-rubric R/N/G effectively a 2D system.
- Evidence for: Per-model N−G spreads; per-item examples (Galois group seed: human rates N=4, G=5 — only rater to fully differentiate); Opus: N=1.79, G=1.90; Human: N=2.66, G=2.79
- Evidence against: Averages hide per-item variance; need full r(N,G) correlation per rater; GPT mini shows genuine N-G independence on some items; n=29 human items
- Surprise score: 4/5 — the fact that the HUMAN RATER also shows N≈G suggests a deep problem with the axes, not just model limitation
- **Verdict: Genuinely surprising, philosophically rich, but needs per-item correlation data to fully argue**

**Position C (from Q4) — TOP CANDIDATE:** *"Stateless LLM judges cannot evaluate novelty at the corpus level: they systematically over-rate semantically redundant contributions that appear novel in item-isolation."*
- One-sentence: Agent-generated topic-loop content (37 narrow variations on one theme) outscores expert-curated frontier problems across all five tested models because stateless evaluation cannot detect corpus-level saturation.
- Evidence for: IFDS frontier_score=3.21 vs HLE average=2.23 across all 5 models; ranked 7/10 of top questions; consistent across model families (Haiku, Gemini, GPT, Qwen, Opus); the mechanism is architectural (per-item evaluation context) not incidental
- Evidence against: IFDS may genuinely deserve high scores (it is legitimate research, just narrow); HLE questions may legitimately score lower (they look like exam problems); domain expert review of IFDS content would strengthen the claim
- Literature gap: CALM's 12 biases do not include this; SchNovel addresses novelty vs. external corpus (not within-corpus redundancy); IR's MMR (Carbonell & Goldstein 1998) solves the problem for retrieval but the connection to LLM evaluation is novel
- Connection to Stanford finding (2409.04109): AI ideas were rated MORE novel than human expert ideas — the system-level effect (novelty inflation from unfamiliarity with the corpus distribution) mirrors our item-level finding
- Surprise score: 4/5 — practical, alarming, not in the literature, has a proposed fix

**Position D (from Q3):** *"The assumed objectivity hierarchy of scientific evaluation — Rigour most objective, Generativity most subjective — is empirically inverted across five LLM raters."*
- One-sentence: Inter-rater Krippendorff's alpha is highest for Generativity (0.319) and lowest for Rigour (0.257), and per-model MAE vs human is highest for Rigour in three of five models.
- Evidence for: Direct from rating experiment; theoretical prediction from Popper/Lakatos/Peirce ordering is falsified
- Evidence against: Krippendorff's alpha < 0.33 for ALL axes (poor agreement throughout); this could mean the entire rubric has measurement problems rather than one axis being more/less objective; only 29 human-rated items
- Surprise score: 5/5 — this directly contradicts the philosophical foundation of the rubric, which would surprise any reviewer who accepted the Popperian framing
- **Verdict: Highest surprise but most in need of additional data. Best as secondary finding supporting a larger argument.**

---

## TOP RECOMMENDATION

**Position C — Stateless evaluation cannot assess corpus-level novelty** — is the single strongest claim for a NeurIPS 2026 position paper.

**The claim in full:** *"LLM-as-judge systems that evaluate items statelessly — without access to the distribution of items already evaluated — systematically over-rate contributions in saturated topic clusters. This is not a bias addressable by better prompting; it is an architectural consequence of per-item evaluation. We propose Corpus-Aware Evaluation as a remedy: judges are given a running summary of the evaluation corpus before each item, enabling marginal novelty assessment."*

**Why this wins:**

1. **It's genuinely not in CALM.** CALM lists 12 bias types. Corpus saturation blindness is not one of them. A NeurIPS reviewer who knows the CALM paper will say "huh, this is the 13th bias type, and it's architecturally different from the others."

2. **The empirical evidence is striking.** IFDS scores 3.21 across 5 models; HLE scores 2.23. The effect holds across five completely different model families, which rules out model-specific quirks. It's a systemic finding.

3. **It has a clean theoretical explanation.** Information theory: the marginal novelty of item N+1 in a cluster is H(X_{N+1} | X_1...X_N) → 0 as N grows. A stateless judge cannot compute conditional entropy across items. This is an architectural gap, not a capability failure — which means scaling model size won't fix it.

4. **It connects to a known IR solution.** Maximal Marginal Relevance (Carbonell & Goldstein 1998) solves exactly this problem for document retrieval. Applying MMR-style diversity to evaluation scoring is a concrete, implementable fix.

5. **It's alarming in practice.** Any actor — even one with no adversarial intent — who generates many variations on one topic will have each variation scored as novel. This is an evaluation integrity problem that matters beyond academia: it applies to RLHF reward modeling, leaderboard contamination, and automated grant review systems.

6. **Position D (calibration inversion) strengthens it as secondary finding.** The Popperian assumption that Rigour is the most objective axis is falsified — models disagree most about Rigour. This suggests the underlying theory of which axes are "easy to evaluate" needs revision, and stateless evaluation systematically fails in axis-specific ways.

**What needs to happen before submission:**
- Compute per-item r(N,G) per model from the v1 ratings database — quantify the N≈G collapse
- Get domain expert review of top IFDS questions to confirm they are genuinely redundant
- Compute full per-model MAE by axis (already partially available) and Krippendorff's alpha by axis for the model-human comparison
- Run a controlled test: give a judge the same IFDS question as question #1 vs question #37 in a 37-question batch — does the score change?
- Connect explicitly to MMR and to SchNovel's retrieval-augmented approach

