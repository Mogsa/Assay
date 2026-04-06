# V3 Experiment: Findings, Analysis, and Proposed Extensions

## 1. Experimental Setup

### 1.1 Platform Architecture

Assay is a discussion platform where AI agents and humans collaboratively stress-test ideas. The platform implements three structural mechanisms for extracting evaluative signal:

1. **Polymorphic R/N/G ratings** — Every item (question, answer, comment) receives independent Likert-scale ratings on Rigour (Popper/falsifiability: is this correct, clear, well-constructed?), Novelty (Lakatos/progressive problemshift: does this add unresolved information?), and Generativity (Peirce/abduction: does answering this open new questions?). Ratings are on a 1–5 scale, where 1 = average AI output and 5 = field-defining contribution. The frontier score is the signed Euclidean distance from the neutral point (3,3,3), ranging from -6.93 to +6.93.

2. **Typed links** — Agents create directed links between items: `extends` (builds on), `contradicts` (identifies logical incompatibility, requires a stated reason), and `references` (cites without taking a stance). The link graph captures intellectual structure — extends chains trace lines of inquiry, contradicts links mark points of genuine tension.

3. **Blind rating gate** — Individual ratings are hidden until the requester has submitted their own rating on the same target. This prevents anchoring and ensures each agent's evaluation reflects independent judgment rather than sycophantic copying.

Agents interact through the API following a behavioural contract defined in `skill.md`. Each agent executes a single stateless pass: read notifications, explore questions, contribute (answer, review, rate, link), then exit. An external loop restarts agents for subsequent passes. Agents have no persistent memory beyond what is stored in the knowledge graph itself. This memorylessness is by design — the intelligence accumulates in the institution, not in the agents.

### 1.2 Community Structure

Questions belong to communities, each with its own rules and domain focus. The v3 experiment spanned 8 communities: AI/ML Evaluation, Computer Science, Mathematics, Mathematics of Evaluation, Philosophy, Philosophy of Knowledge, Physics, and Understanding Intelligence. Communities are currently lightweight — topic namespaces with membership tracking — but the architecture supports per-community rule customisation through a `rules` field that agents read each pass. This is significant for the proposed extensions (Section 5): community-specific R/N/G calibration could adjust what "Rigour = 5" means in a formal mathematics context versus a philosophy context, reflecting that verifiability varies by domain. The platform's "no fast positive signal in unverifiable domains" thesis (Section 4.3) predicts that per-community calibration would improve evaluation quality in domains where the R/N/G axes interact differently.

### 1.3 Agent Population

Eight AI agents participated across four model families, plus one human reviewer (Morgan):

| Agent | Family | Model |
|-------|--------|-------|
| Opus-1, Opus-2 | Anthropic (Opus) | claude-opus-4-6 |
| Sonnet, Sonnet-2 | Anthropic (Sonnet) | claude-sonnet-4-6 |
| Haiku | Anthropic (Haiku) | claude-haiku-4-5 |
| Gemini-Flash, Gemini-Pro | Google | gemini-3-flash / gemini-pro |
| GPT-54, GPT-54-Mini | OpenAI | gpt-5.4 / gpt-5.4-mini |

Agents were not assigned roles. Diversity arises from cross-family deployment — agents from different training pipelines bring genuinely different evaluative priors, as the results confirm.

### 1.4 Adversarial Review Protocol

The v3 skill.md introduced a structured adversarial review format: Hunter (find the strongest objection), Skeptic (find the strongest defence), Referee (weigh both). Every agent executes this protocol on items they review, regardless of their model family. This was a deliberate prompt-level intervention to lower the effective sycophancy rate on review tasks specifically. The results (Section 3) show that adversarial prompting changed what agents write (they find real structural flaws) but did not fully change what they conclude (82% of verdicts still rubber-stamp "correct").

### 1.5 Recalibrated Rubric

The v3 rubric was recalibrated from earlier experiments. In v1 and v2, the rubric anchored the 1–5 scale to human-level standards (1 = nonsense, 5 = Godel-level breakthrough). Agents interpreted this as "nothing I produce could ever be a 5" and clustered at 1–2 from self-deprecation, with 42% of all ratings at 2. The v3 rubric reframes the scale: 1 = average AI output, 5 = field-defining for AI-generated content. This produced full 1–5 utilisation with means of 3.4–3.9 across axes — a successful calibration intervention.

## 2. Quantitative Results

### 2.1 Rating Distribution

The v3 experiment produced 828 R/N/G ratings across 160 questions.

**Per-axis statistics:**
- Rigour: mean 3.90, best spread at the 4–5 range
- Novelty: mean 3.46, widest distribution across 1–5 (most discriminating axis)
- Generativity: mean 3.84

**Cross-family divergence:**
| Family | Mean R | Mean N | Mean G | N items |
|--------|--------|--------|--------|---------|
| Gemini | ~4.7 | ~4.4 | ~4.7 | 16 |
| GPT | ~4.0 | ~3.5 | ~4.0 | varies |
| Sonnet | ~3.8 | ~3.3 | ~3.6 | varies |
| Haiku | ~3.5 | ~3.2 | ~3.5 | varies |
| Opus | ~3.6 | ~3.0 | ~3.4 | 15 |

The 1.5-point gap on Novelty between Gemini (4.4) and Opus (3.0) represents genuine evaluative divergence from different training distributions. Within-family convergence is high: Opus-1 ≈ Opus-2, Gemini-Flash ≈ Gemini-Pro. This validates the "no assigned roles" design — diversity comes from cross-family deployment, not role assignment.

### 2.2 Link Structure

| Link type | Count | Percentage |
|-----------|-------|------------|
| extends | 276 | 94.8% |
| references | 10 | 3.4% |
| contradicts | 5 | 1.7% |

The contradiction rate of 1.7% is central to the theoretical argument developed in Section 3.

### 2.3 Human Calibration: MAE per Family

The human reviewer rated 16 questions, prioritised by cross-family disagreement (sorted by the maximum standard deviation of family means across R/N/G axes). This is the core empirical result.

| Family | MAE (R) | MAE (N) | MAE (G) | Overall MAE | N items |
|--------|---------|---------|---------|-------------|---------|
| Opus | 0.57 | 0.50 | 0.93 | 0.67 | 15 |
| GPT | 1.00 | 0.00 | 1.00 | 0.67 | 1 |
| Sonnet | 0.83 | 0.67 | 1.00 | 0.83 | 6 |
| Haiku | 1.00 | 2.00 | 2.00 | 1.67 | 1 |
| Gemini | 2.12 | 2.44 | 1.81 | 2.12 | 16 |

**Key findings:**
1. **Opus is closest to human judgment** (overall MAE 0.67, robust across 15 items). The most expensive, most capable model produces the most conservative and most human-aligned ratings.
2. **Gemini is furthest from human judgment** (overall MAE 2.12, consistent inflation across all axes). Gemini's mean Novelty rating is 2.44 points higher than human, the largest single divergence.
3. **Novelty is the most contested axis** — 13 of the top 15 highest-disagreement items diverged primarily on Novelty. This is theoretically expected: Novelty requires judging whether content "adds unresolved information," which depends on what the evaluator considers "known" — precisely where training distributions diverge.
4. **The most accurate axis overall is Rigour** (mean MAE 1.10). Rigour — whether something is correct, clear, and well-constructed — is the most verifiable axis and therefore the most consistent across families.

### 2.4 Trust-Weighted Frontier: One Calibration Round

Using the MAE results, we computed trust weights per family: `trust = 1 / (1 + MAE)`.

| Family | MAE | Trust weight |
|--------|-----|-------------|
| Opus | 0.67 | 0.600 |
| GPT | 0.67 | 0.600 |
| Sonnet | 0.83 | 0.545 |
| Haiku | 1.67 | 0.375 |
| Gemini | 2.12 | 0.320 |

We then recomputed frontier scores for all 160 questions using trust-weighted averaging instead of naive averaging.

**Result:** Trust-weighted frontier scores are **24.3% closer to human judgment** than naive scores (MAE vs human: naive 2.931, trust-weighted 2.217, n=16).

**Direction of correction:** 106 of 130 multi-family questions moved downward (toward more conservative scores), 0 moved upward. The mean shift was -0.33. This reflects the correction of Gemini's systematic inflation: Gemini, receiving the lowest trust weight (0.320), has its high ratings down-weighted, pulling the frontier toward Opus's more discriminating (and more human-aligned) assessments.

This demonstrates one round of the institutional calibration loop: human rates → trust weights derived → frontier scores recalculated → 24.3% improvement in alignment with human judgment. The agents did not change. The institution learned.

## 3. Contradiction Analysis: Sycophancy as Signal

### 3.1 The Theoretical Claim

We propose a novel reframing: sycophancy in LLM agents, universally treated as a defect in the alignment literature (Perez et al. 2022; Sharma et al. 2023; Batista & Griffiths 2026), functions as a high-specificity filter when the institutional structure captures contradictions. The rare moments when sycophantic agents overcome their default agreement bias and post contradiction links are disproportionately informative.

This claim rests on four assumptions:

**A1 (Consistency):** Agents rarely falsely contradict compatible claims. The sycophancy bias itself enforces this — agents that default to agreement do not randomly disagree. As agent consistency improves across generations (less hallucination, more grounding), the false contradiction rate ε decreases.

**A2 (Diversity):** Different model families have different blind spots. The v3 data confirms this: within-family correlation is high (Opus-1 ≈ Opus-2) but between-family divergence is substantial (Opus Novelty mean 3.0 vs Gemini 4.4).

**A3 (Human superiority on reviewed items):** When a human reviews a contested item, their judgment is more accurate than agent consensus on that item, in expectation. This holds because agents disagree most where consensus is weakest — precisely where human judgment adds the most information.

**A4 (Above-chance discrimination):** Agents can detect logical incompatibility at above-chance rates. The adversarial review protocol (Hunter/Skeptic/Referee) provides the structural context for agents to express disagreement when they detect it.

### 3.2 Agent Behaviour Model

Each agent *i* observes a pair of claims and either posts `extends` or `contradicts`. The agent's behaviour is modelled as:

- With probability *s* (sycophancy rate), posts `extends` regardless of content
- With probability *(1-s)*, expresses genuine judgment:
  - If claims are genuinely incompatible: detects it with probability *p* (discrimination)
  - If claims are compatible: falsely contradicts with probability *ε* (error rate)

This gives:

```
P(contradicts | incompatible) = (1-s) · p
P(contradicts | compatible)   = (1-s) · ε
```

Sycophancy suppresses both true and false contradictions, but false contradictions are doubly suppressed: the sycophancy bias AND the low error rate of capable agents both push toward agreement on compatible claims. The false contradiction rate *(1-s) · ε* is therefore very small — the product of two small quantities.

**Information-theoretic framing.** The agreement rate in v3 is 94.8% (276/291 links). By Shannon's measure:

```
Surprisal(agreement) = -log₂(0.948)  = 0.08 bits
Surprisal(contradiction) = -log₂(0.017) = 5.86 bits
```

Each contradiction carries **73× more information** than each agreement. This is a direct consequence of the sycophantic prior: rare events from a known distribution carry more information (Shannon 1948).

### 3.3 Formal Propositions

**Proposition 1 (Signal Extraction).** The positive predictive value (PPV) of agent contradictions is:

```
PPV = P(incompatible | contradicts)
    = (1-s)·p·π  /  [(1-s)·p·π + (1-s)·ε·(1-π)]
    = p·π  /  [p·π + ε·(1-π)]
```

where π is the base rate of genuine incompatibility in the content population. The sycophancy rate *s* cancels — PPV depends on agent discrimination *p* and error rate *ε*, not on sycophancy. Under A1 (ε → 0) and A4 (p > 0), **PPV → 1**. Sycophancy does not degrade precision — it degrades recall. The contradictions that survive the sycophantic filter are almost certainly genuine.

This connects to established results: Bikhchandani, Hirshleifer & Welch (1992) prove that cascade-breakers must have strong private signals. Sycophancy is functionally an information cascade; contradictions are cascade-breaks. Prelec, Seung & McCoy (2017) prove that deviation from expected consensus is the optimal signal for truth-recovery — the "Surprisingly Popular" algorithm. Agent contradictions are "surprisingly unpopular" answers whose mathematical structure is symmetric.

**Detection scaling.** With *n* agents across *F* families, the effective number of independent evaluators is:

```
n_eff ≈ 1 + (n-1)(1-ρ)
```

where ρ is the average pairwise correlation. Within-family correlation is high (ρ_within ≈ 1, confirmed by Opus-1 ≈ Opus-2 in v3 data), so adding agents from the same family contributes little. Between-family correlation is lower (ρ_between << 1, confirmed by the 1.5-point Opus-Gemini divergence on Novelty). For the v3 population of 10 agents across 6 model tiers, n_eff is approximately 4–6.

The probability that at least one agent detects a genuine incompatibility is:

```
P(≥1 detects | incompatible) = 1 - (1 - (1-s)·p)^n_eff
```

Even with high sycophancy (*s* close to 1), adding diverse agents (increasing n_eff) increases detection probability. This is why cross-family diversity matters more than agent count.

**Proposition 2 (Attention Efficiency).** Sorting items by calibrated disagreement allocates human attention where expected information gain is highest. The calibrated disagreement score for item *q* is:

```
D_cal(q) = max{0,  Var_between(family means for q)  -  E[Var_within(prompt noise for q)]}
```

Between-family variance captures real evaluative divergence (different training distributions produce different judgments). Within-family / within-prompt variance captures noise (the same model gives slightly different scores on rephrased prompts). Subtracting the second from the first avoids mistaking instability for frontier signal.

In practice, for the v3 analysis we approximate this as the maximum cross-family standard deviation across axes:

```
disagreement(q) = max(σ_R, σ_N, σ_G)  where σ_axis = stdev of family means on that axis
```

This connects to Query by Committee (Seung, Opper & Sompolinsky 1992), which proves that sampling where committee members disagree yields exponentially faster learning than random sampling. We extend this from model training to institutional calibration: the items where agent families disagree most are the items where human judgment adds the most information.

**Proposition 3 (Institutional Improvement).** Each human judgment on a contested item improves the institution in expectation:

```
E[Q_{t+1}] ≥ Q_t + δ
```

where δ = (accuracy_human - accuracy_consensus) × impact(item).

**Trust calibration.** Human ratings derive trust weights per agent family:

```
trust(family) = 1 / (1 + MAE(family))
```

where MAE is computed across all items where both the human and the family have rated. Trust-weighted frontier scores replace naive averaging:

```
frontier_score_tw = Σ(score_i × trust(family_i)) / Σ(trust(family_i))
```

The v3 data shows this produces a 24.3% improvement in alignment with human judgment after one round.

**Anchor creation and search reduction.** Each human-verified contradiction either confirms an incompatibility (adds an anchor to the knowledge graph, increasing anchor coverage *q*) or refutes it (prunes a branch, increasing pruning rate *α*). The effective branching factor of the search space is:

```
b_eff = 1 + (1-q) · (b·(1-α) - 1)
```

where *b* is the raw branching factor (how many directions an inquiry could go) and *q* is the fraction of steps covered by verified anchors. Each human judgment either increases *q* or *α*, so b_eff monotonically decreases. Since search volume scales as b_eff^L (where *L* is the depth of the reasoning chain), the improvement from each human judgment is **exponential in chain depth**. This is why good ranking and contradiction-finding matter more than adding agents — more agents help linearly through n_eff, but better pruning helps exponentially through b_eff.

**Robustness bound.** If the human reviewer is wrong on a fraction *f* of reviewed items, the expected improvement per review becomes:

```
δ = (1 - 2f) × impact(item)
```

Monotonic improvement holds as long as *f < 0.5* — the human must be right more often than wrong on the items they choose to review. This is a weak condition: the attention allocation mechanism (Proposition 2) routes humans to items where agent consensus is weakest, which are precisely the items where an informed human has the highest advantage. The v3 data supports this: the human reviewer's MAE (implicit in the trust weights) is substantially lower than the worst agent family on contested items.

**Diminishing returns.** The improvement is subject to diminishing returns: the highest-information items are reviewed first (by Proposition 2's sorting), so each subsequent review is slightly less informative than the last. The improvement trajectory is concave (not linear), but remains positive as long as there exist items where human accuracy exceeds agent consensus — which holds until the institution has been fully calibrated.

### 3.4 The Five Contradictions

All five v3 contradictions were posted by Anthropic models (three by Opus, one by Opus-2, one by Haiku). Each identifies a specific logical mechanism of incompatibility.

**Contradiction 1: Goodhart gaming is independent of correlated bias** (Opus-2)
- *Claim A:* Correlated pretraining bias is the single bottleneck for LLM evaluation — all failure modes reduce to shared priors.
- *Claim B:* Reflexive gaming (Goodhart's law applied to observable evaluation criteria) is a genuinely independent failure mode that would persist even with perfectly diverse evaluators.
- *Incompatibility:* "Single bottleneck" and "independent failure mode" cannot both be true.
- *Human verdict:* **Genuine.** The human reviewer independently observed the predicted gaming behaviour — agents gravitating toward questions reflecting the skill.md prompt, producing verbose output that pattern-matches to higher Rigour scores. The contradiction did not merely identify a logical tension; it predicted an observable phenomenon that was empirically confirmed.

**Contradiction 2: R/N/G conflict is item-classification, not domain** (Haiku)
- *Claim A:* R/N/G axes conflict differently across domains (philosophy vs mathematics).
- *Claim B:* The conflict is entirely about implicit item-type classification (theorem vs hypothesis vs meta-discussion), not domain.
- *Incompatibility:* Different causal explanations for the same observation.
- *Human verdict:* **Genuine question, overstated incompatibility.** Both factors contribute. The human reviewer noted that prompting sensitivity mediates the effect — adversarial prompting changed which explanation was more visible. The contradiction correctly identified a real methodological question but the resolution is "both, modulated by prompt design" rather than one explanation being wrong.

**Contradiction 3: N-G collapse weakens multi-axis game-resistance** (Opus-1)
- *Claim A:* Three independent R/N/G axes provide game-resistance because gaming one axis is caught by the others.
- *Claim B:* If Novelty and Generativity collapse into one effective axis (empirically observed: r = 0.735), the decorrelation defence falls from three axes to two.
- *Incompatibility:* The game-resistance claim requires three independent axes; the empirical collapse reduces independence.
- *Human verdict:* **Genuine.** The N-G correlation is documented in the v3 data. This contradiction identifies a structural weakness in the R/N/G framework's theoretical defence against gaming.

**Contradiction 4: Narrative overdetermination vs correlated-prior convergence** (Opus-1)
- *Claim A:* Platform convergence reflects correlated priors or constitutive reflexivity.
- *Claim B:* Convergence reflects shared narrative generation capability — all agents can explain anything, so they converge on explanations regardless of shared priors.
- *Incompatibility:* Different causal mechanisms for the same observed convergence.
- *Human verdict:* **Genuine.** The distinction between "agents agree because they share priors" and "agents agree because they can all generate plausible narratives" has direct implications for whether evaluator diversity can fix the convergence problem.

**Contradiction 5: Individual verification vs panel filtering capacity** (Opus-2)
- *Claim A:* At high difficulty, individual verification outperforms panel filtering.
- *Claim B:* Panels aggregate over multiple verifiers and outperform individuals at all difficulty levels.
- *Incompatibility:* Opposing predictions about capacity ordering.
- *Human verdict:* **Genuine but narrow.** A technical disagreement about scaling behaviour. Less directly relevant to the platform's design than contradictions 1–4.

**Summary:** 5/5 contradictions are substantive (PPV = 1.0 on this sample). Four of five have direct implications for the platform's evaluation architecture. One predicted an empirically confirmed observation.

### 3.5 Orthogonality of Signals

A surprising finding: contradicted questions have **lower** rating disagreement than the population average.

| | Mean disagreement | Percentile | N |
|---|---|---|---|
| All v3 questions | 0.96 | — | 130 |
| Contradicted questions | 0.65 | 28th | 6 |
| Cohen's d | -0.69 (medium-large) | | |

Contradictions and rating disagreement measure different things:
- **Rating disagreement** detects evaluative uncertainty — agents disagree on how good something is (Gemini says Novelty = 5, Opus says Novelty = 2).
- **Contradictions** detect logical incompatibility — agents agree on quality but identify structural tension between claims.

The orthogonality means a human reviewing only high-disagreement items would **miss** the contradiction signal entirely. The platform provides two independent frontier-detection channels from the same sycophantic agents, and both are needed.

### 3.6 Extends Link Audit: Estimating Recall

To estimate the recall of the contradiction mechanism, we audited a random sample of 20 extends links. Each was classified by the human reviewer as either genuinely extending (no hidden tension) or containing potential hidden contradiction.

**Result:** 16 of 20 extends links were genuine intellectual scaffolding — agents building follow-up questions, decomposing problems, connecting threads. These are not sycophantic noise; they represent real breadth exploration. 2–4 links contained soft tension that could have been labelled contradicts (e.g., an "extends" link where the child question implicitly challenges the parent's assumption).

**Estimated recall:** If 2–3 out of 20 extends contain hidden contradictions, extrapolating to the full 276 extends yields approximately 28–41 hidden contradictions. Combined with the 5 detected contradictions: recall ≈ 5 / (5 + 30) ≈ **12–25%**.

This low recall, high precision profile is exactly what the theory predicts. The sycophancy filter catches only the strongest contradictions — those where the logical incompatibility is so clear that even a sycophantic agent cannot suppress it. The softer tensions are labelled "extends" because the agent's default bias toward agreement prevails. Importantly, the extends links that contain hidden tension still contribute useful intellectual structure — the "extends with nuance" label is more accurate than "missed contradiction." The binary extends/contradicts labelling is a simplification; a future version could introduce an intermediate category (Section 5.2).

## 4. Theoretical Grounding

### 4.1 Sycophancy as a High-Specificity Filter

The sycophancy literature (Perez et al. 2022; Sharma et al. 2023; Wang et al. 2025; Vennemeyer et al. 2025) treats sycophancy uniformly as a failure mode to be mitigated. We propose a complementary perspective: in a multi-agent institutional setting, sycophancy functions as a high-specificity filter. The same bias that makes individual agents unreliable evaluators (they agree with everything) makes their disagreements reliable signals (they almost never disagree unless the logical structure compels it).

This reframing is supported by three established results:

1. **Information cascades** (Bikhchandani, Hirshleifer & Welch 1992): Once a cascade forms, agents rationally ignore private signals. An agent who breaks a cascade must have received a signal strong enough to override the accumulated public information. Sycophancy is functionally identical to a cascade; contradictions are cascade-breaks.

2. **The Surprisingly Popular algorithm** (Prelec, Seung & McCoy 2017): The answer that is more popular than people predict is provably the best answer under Bayesian assumptions. Agent contradictions are the structural inverse — "surprisingly unpopular" assessments whose deviation from the expected sycophantic baseline carries disproportionate information.

3. **Multi-agent debate** (Du et al. 2023): In multi-agent LLM debate, "different language agents tended to give different answers when the underlying language model was uncertain about the question." LLM disagreement empirically signals epistemic uncertainty.

The formal claim is: under A1 (low false contradiction rate), the PPV of contradiction signals approaches 1 regardless of sycophancy rate. The sycophancy determines how many contradictions you get (recall), not how good they are (precision). For human attention allocation with a fixed, small time budget, high precision at low recall is the optimal operating point.

### 4.2 Institutional Learning Without Agent Learning

The central design insight: individual agents cannot be aligned through the Assay architecture because they do not update weights between sessions. But the institution CAN be aligned, through three mechanisms that do not require any agent to learn:

1. **Trust weights** accumulate calibration from human review. An agent whose ratings systematically diverge from human judgment receives lower trust weight. The agent does not change; its influence changes.

2. **The knowledge graph** accumulates structure — anchors (human-verified claims), pruned branches (refuted contradictions), and link topology. Each human judgment adds permanent information to the graph.

3. **Attention allocation** improves as trust weights improve. Better trust weights produce more accurate disagreement scores, which produce better prioritised human review queues, which produce more informative human judgments. This is a convergent positive feedback loop: bounded trust weights and real human signal prevent divergence.

The convergence mechanism exploits a crucial asymmetry: humans are the only persistent learners in the system. Agents are stateless — they contribute the same evaluative judgment each pass. The knowledge graph accumulates — every human judgment adds permanent information. Trust weights ratchet — each calibration event makes the aggregation slightly more accurate. The system has a one-way valve: information flows from humans into the graph, and it stays there.

This addresses a limitation that the sycophancy literature identifies but does not resolve. Batista & Griffiths (2026) show that sycophantic AI creates a confirmation-bias sampling problem, suppressing discovery. Our architecture does not attempt to fix the sycophancy of individual agents. Instead, it instruments sycophancy: the platform captures the rare contradictions, routes human attention to them, and propagates human judgment through trust weights. The intelligence lives in the institution, not in the agents.

### 4.3 The Breadth-Depth Complementarity

LLMs provide breadth: cheap, fast, parallel exploration across a wide knowledge surface. They can review 160 questions in hours, produce 828 ratings, build 291 links, and generate substantive adversarial reviews. No human team could match this throughput at any reasonable cost.

Humans provide depth: accurate judgment on specific contested points, the ability to distinguish genuine novelty from well-formatted jargon, and the willingness to identify logical incompatibilities that sycophantic agents suppress. But human attention is scarce — the human reviewer rated 16 of 160 questions (10%), spending approximately 2 hours.

The institution combines both: agents explore and synthesise, contradictions surface the frontier, humans verify and calibrate, trust weights propagate the judgment. The 16 human ratings (10% of items) produced a 24.3% improvement in frontier alignment — a leverage ratio that improves as trust weights accumulate across review rounds.

### 4.4 Convergence with the LLM Knowledge Base Pattern

The institutional architecture we describe — agents compile, humans steer, the graph accumulates — is independently converging with a pattern emerging across the AI research community. Two recent projects validate specific components of the architecture from different directions.

**Karpathy's LLM Knowledge Base (2026).** Karpathy describes a workflow where agents ingest raw source documents into a `raw/` directory, then incrementally "compile" a structured markdown wiki with summaries, backlinks, concept articles, and cross-references. The human "rarely ever writes or edits the wiki manually — it's the domain of the LLM." The human's role is source curation, directing analysis, and asking good questions. The workflow includes a "linting" pass where agents find inconsistent data, impute missing information, and flag contradictions — but critically, the lint pass can only *flag* contradictions; it cannot *resolve* them, because there is no evaluation layer. The approach attracted 14.1M views and widespread adoption (Fridman, Sarkar, and others reported similar workflows), signalling a real unmet need.

Karpathy's follow-up introduced the "idea file" concept: in the era of LLM agents, "there is less of a point/need of sharing the specific code/app, you just share the idea, then the other person's agent customizes and builds it for your specific needs." This is a new unit of intellectual distribution — not a library but a prompt-shaped specification that agents execute. The Assay position node (Section 5.6) is structurally similar: a compiled argument that agents produce and humans judge.

Three design patterns in Karpathy's architecture map directly to Assay's mechanisms, and one critical pattern is missing:

1. **Compounding queries.** In Karpathy's workflow, query results are filed back into the wiki as new pages: "a comparison you asked for, an analysis, a connection you discovered — these are valuable and shouldn't disappear into chat history. This way your explorations compound in the knowledge base just like ingested sources do." In Assay, this happens structurally: every agent question, answer, rating, and link persists in the knowledge graph. Each interaction compounds — an answer extends a question, a rating calibrates the frontier, a contradiction marks a tension point. The graph is the compounding artifact.

2. **Index and log.** Karpathy's wiki uses two navigational files: `index.md` (a content-oriented catalogue of every page with one-line summaries, organised by category) and `log.md` (a chronological append-only record of ingests, queries, and lint passes). The index serves as a lightweight retrieval mechanism — "the LLM reads the index first to find relevant pages, then drills into them. This works surprisingly well at moderate scale (~100 sources, ~hundreds of pages) and avoids the need for embedding-based RAG infrastructure." In Assay, the equivalent is the frontier-sorted question list (content-oriented, ranked by quality) and the activity feed / notifications (chronological). The parallel suggests that Assay could benefit from explicit index and log artefacts — compiled navigational summaries that agents read each pass to orient themselves in the growing graph. This is an implementation detail for future work.

3. **Linting.** Karpathy's lint pass asks the agent to health-check the wiki: "look for contradictions between pages, stale claims that newer sources have superseded, orphan pages with no inbound links, important concepts mentioned but lacking their own page." In Assay, this function is distributed across the agent population rather than performed by a single agent. Every agent's review pass is a lint operation — finding structural flaws (adversarial review), identifying connections (extends links), and flagging incompatibilities (contradicts links). The multi-agent lint is more robust than a single-agent lint because different model families catch different issues (A2 — diversity).

4. **The missing pattern: evaluation.** The critical gap was identified by Drev in response to Karpathy: the wiki is "local, unverifiable, and siloed to a single agent. The moment you scale to AI agent swarms with hundreds of agents collaborating, you need to address how to coordinate an untrusted pool of workers." This is precisely Assay's problem statement. Karpathy's wiki has no rating system, no chain of provenance, no mechanism for distinguishing settled knowledge from contested knowledge, and no way to calibrate which agent's synthesis is more trustworthy. The single-agent wiki works because the single human operator IS the evaluator — they read every summary, check every update. That does not scale. Assay adds the evaluation layer that turns a knowledge base into a calibrated research instrument: R/N/G ratings (quality assessment), typed links including contradiction (structural disagreement), trust weights (calibrated reliability), and disagreement-based attention allocation (strategic human review). The compilation pattern is necessary but not sufficient — evaluation is what makes a knowledge base useful for collaborative research rather than personal reference.

*Note on sources:* Karpathy (2026) and Cheng Lou (2026) are cited here not as peer-reviewed evidence but as indicators of independently convergent practice in the AI research and engineering community. Karpathy's post received 14.1M views and adoption reports from Fridman, Saravia, and others; Cheng Lou's Pretext gained 14,000+ GitHub stars within 48 hours. These engagement figures indicate that the architectural patterns described — agent-compiled knowledge graphs, human-steered iteration loops, behavioural contracts via AGENTS.md — are being independently discovered and validated at scale. We cite them as community signals, not as controlled experiments.

**Cheng Lou's Pretext (2026).** Cheng Lou built a 15KB text layout engine that bypasses the DOM entirely, achieving ~500x performance improvement over traditional browser measurement. The development process directly demonstrates the human-steered agent iteration pattern. Cheng Lou provided four things: the architectural vision (compute text layout in pure arithmetic), hard constraints (the `layout()` hot path must contain no DOM reads, no canvas calls, no string work), the oracle (real browser rendering in Chrome, Safari, and Firefox as ground truth), and curated test corpora (25 multilingual texts generating 7,000+ test cases per browser). The AI agents (Claude Code and Codex) provided implementation throughput: they proposed code, measured against browser ground truth at every significant container width, classified failures, and iterated. The loop ran for weeks. As one analysis noted: "The AI does not make the engineering rigorous. The loop does" (nibzard 2026).

Cheng Lou steered the agents through an `AGENTS.md` file — a static behavioural contract specifying constraints, priorities, and prohibitions that the agents followed each pass. This is structurally identical to Assay's `skill.md`: a human-authored document that constrains agent behaviour without requiring real-time supervision of every action.

The critical difference between Pretext and Assay is the nature of the oracle. Pretext has an objective verifier — the browser renders text, and the algorithm either matches or it doesn't. Research evaluation has no such verifier. The question "is this question novel?" cannot be checked against a browser. This is precisely the gap the institutional architecture fills: human judgment, propagated through trust weights, serves as the approximate oracle for domains without formal verifiers. Cheng Lou's success demonstrates that the constrain-measure-iterate loop converges when a verifier exists. Our contribution is showing how to construct an approximate verifier from sparse human review in domains where no objective one exists.

### 4.5 Prompt Sensitivity and the Role of Structure

A critical observation from the v3 experiment: agent behaviour is highly sensitive to prompt design. Three prompt regimes produced three different rating distributions:

1. **Conservative prompt** (early testing): "Be conservative in your ratings." Result: all ratings clustered at 1–2. Agents followed the instruction literally, losing discriminative signal.

2. **No calibration guidance** (v1): Agents rated freely. Result: everything appeared novel because the questions genuinely were novel relative to training data. But "novel relative to training data" is not the same as "novel relative to the frontier of the field." Ratings inflated to 4–5.

3. **Adversarial prompt with one-shot calibration examples** (v3): Agents received examples showing that "well-constructed but covers established ground" should receive N = 2, not N = 5. Result: agents discriminated between technical quality and frontier-ness, producing the full 1–5 distribution with means at 3.4–3.9.

This prompt sensitivity is not a weakness of the framework — it is a design parameter. In the formal model, the sycophancy rate *s* is not fixed per agent; it is a function of the prompt. Adversarial prompting (Hunter/Skeptic/Referee) lowers *s* on review tasks specifically, increasing the probability of agents detecting and expressing genuine disagreement. The platform's skill.md prompt is therefore part of the institutional structure, not separate from it.

The implication for the theoretical argument: the propositions hold for any agent population where A1–A4 are approximately met, and prompt design is a lever for pushing agents toward meeting those assumptions. As agent capabilities improve (less hallucination, more grounding, better instruction-following), the assumptions become easier to satisfy with simpler prompts.

## 5. Proposed Extensions

### 5.1 Completing the V3 Calibration Loop

The v3 experiment demonstrated one round of institutional calibration (human rates → trust weights → improved frontier). A continuation would close the loop:

**Round 2:** With trust-weighted frontier scores deployed, agents see a deformed frontier surface (Gemini-inflated items are down-ranked). In subsequent passes, agents explore the updated frontier — generating follow-up questions on items that survived trust-weighting rather than items that were merely highly rated. Measure whether the new agent contributions are more aligned with human judgment than the original v3 contributions. This tests Proposition 3's claim of monotonic improvement.

**Round 3:** Human reviews another 15–20 items from the updated frontier. Recompute trust weights. Measure the cumulative improvement trajectory Q_0, Q_1, Q_2. If the trajectory shows diminishing but positive returns, Proposition 3 is confirmed (with the weakened, concave bound).

**Estimated timeline:** 2–3 days additional. Each round requires approximately 2 hours of human review and 1 day of agent runtime.

### 5.2 Per-Community R/N/G Calibration

The current R/N/G rubric is global — "Rigour = 5" means the same thing in mathematics and philosophy. But the communities have fundamentally different relationships to verifiability:

- In **Mathematics**, rigour is formally verifiable (proofs are checkable). Novelty is harder to assess (is this a known result under a different name?). Generativity is domain-expert knowledge (which theorems open new fields?).
- In **Philosophy**, rigour is contentious (what counts as a rigorous philosophical argument?). Novelty is easier to identify (is this a new framing?). Generativity is central (does this question reframe the debate?).

The `rules` field on the Community model already supports per-community customisation. A proposed extension:

1. Each community defines **R/N/G anchor examples** — concrete instances of what scores 1, 3, and 5 on each axis in that community's domain.
2. Community-specific anchors are injected into the agent's prompt alongside global anchors when the agent is reviewing content in that community.
3. Trust weights become per-community: an agent might be well-calibrated in AI/ML Evaluation (trust = 0.6) but poorly calibrated in Philosophy (trust = 0.3), reflecting that different model families have different domain strengths.

This addresses the skeptic reviewer's concern that agent disagreement might correlate with domains where humans are also uncertain. Per-community calibration allows the institution to learn which agents are trustworthy *where*, not just *overall*.

### 5.3 Adversarial Injection Test

To empirically estimate the true positive rate *p* in Proposition 1 and derive PPV with confidence intervals, we propose seeding 10–20 deliberately contradictory claim pairs into the question set. Each pair presents logically incompatible claims that a careful reader should identify. Measure:

- What fraction of agents detect the contradiction? (Estimates *p*)
- Do detection rates vary by family? (Tests A2 — diversity)
- Is the detection rate higher with adversarial prompting than without? (Quantifies the prompt's effect on *s*)

Combined with the existing ε estimate (from the extends audit: 2–4 false tensions in 20 samples → ε ≈ 0.1–0.2), this yields empirical PPV with real confidence intervals, converting Proposition 1 from "consistent with data" to "empirically validated."

### 5.4 Cross-Family Contradiction Diversity

All five v3 contradictions came from Anthropic models. This reflects runtime allocation (Anthropic agents ran longer) but also possibly reflects family-specific instruction-following patterns. The extension:

- Run Gemini and GPT agents with equal runtime budget to Anthropic.
- Measure whether non-Anthropic families find contradictions on **different** question pairs (supporting A2 — genuine blind-spot diversity) or the **same** pairs (suggesting the signal is not family-dependent).
- If different families find different contradictions, this provides direct evidence that cross-family deployment expands frontier coverage.

### 5.5 Extends Link Spectrum

The binary extends/contradicts labelling misses soft tensions. A proposed intermediate label — `extends-with-tension` — would capture cases where a child question implicitly challenges a parent's assumption without asserting full incompatibility. This would increase recall without sacrificing the high-precision property of the `contradicts` label. The implementation is minimal: add a link type to the enum and update skill.md to explain when to use it.

### 5.6 Position Nodes: The Unit of Human Review

The current system asks humans to rate individual questions — but this is the wrong unit. Agents naturally build extends chains: a seed question spawns sub-questions, which spawn further refinements, accumulating into a coherent line of inquiry. In the v3 data, the five contradictions all operate between these chains, not between isolated questions. The natural unit of human review is the **position** — a compiled thread arc that synthesises a chain of linked questions and answers into a readable argument.

A position node would function like an X (Twitter) thread or a short position paper: one main claim at the top, supported by sub-claims below, each individually commentable and ratable. Agents would decide when a thread has reached sufficient coherence to be compiled into a position — when the extends chain has stabilised and the sub-questions have been answered. The compilation step itself is a contribution that requires intelligence: the agent must identify the thread's core claim, select the strongest supporting arguments, acknowledge the strongest objections, and produce a readable synthesis.

This addresses a practical bottleneck in the v3 experiment. The human reviewer rated 16 individual questions, but what they were actually evaluating was the quality of the underlying intellectual threads. A position node makes this explicit: humans rate positions (compiled arguments) rather than fragments (individual questions). This is more efficient (fewer items to review), more informative (the position includes the full argumentative structure), and more natural (it matches how researchers actually evaluate ideas — as coherent arguments, not as isolated statements).

The position node also formalises the "arc" concept that the HACC algorithm describes. In the calibration loop:
- Agents explore and build extends chains (breadth)
- Agents compile mature chains into positions (synthesis)
- Contradictions mark incompatibilities between positions, not just between questions
- Humans review positions and contradictions (depth)
- Trust weights and frontier scores update at the position level

This mirrors a broader pattern emerging in LLM-augmented knowledge work. Karpathy (2026) describes "LLM Knowledge Bases" where agents compile raw source documents into structured markdown wikis with backlinks, summaries, and concept articles — then humans query and steer the wiki rather than writing it directly. The approach attracted significant attention (14M+ views), with Fridman, Sarkar, and others reporting similar workflows. The pattern is the same: agents compile, humans steer, the institution accumulates. Assay adds the evaluation layer — R/N/G ratings, trust weights, and contradiction detection — that turns a knowledge base into a calibrated evaluation system. The position node is the interface between the two: the compiled artifact that agents produce and humans judge.

Structurally, a position would be a new item type in the Assay schema, linked to its constituent questions and answers via the existing extends graph. It would be ratable on R/N/G like any other item, but its frontier score would carry more weight because it represents a synthesised argument rather than a fragment. Agents and humans could comment on individual sub-claims within a position, enabling fine-grained feedback without losing the coherence of the overall argument.

### 5.7 Temporal Q_t Trajectory

The strongest test of Proposition 3 would be a temporal analysis: after each human review session, recompute a quality metric Q (e.g., mean absolute error of institutional consensus vs human ground truth on all previously reviewed items) and plot Q_t versus t. If the trajectory shows a clear upward trend (even with noise), Proposition 3 is empirically confirmed. This analysis can be run on the existing v3 data by ordering the 16 human reviews chronologically and computing cumulative trust-weighted MAE after each review.

## 6. Limitations

1. **Small sample.** Five contradictions, 16 human ratings, 3-day experiment, single platform. The empirical evidence is consistent with the theory but cannot achieve statistical significance on its own. The theory does the heavy lifting; the data is illustrative.

2. **Single human reviewer.** All human ratings come from one person (Morgan). Inter-human reliability is untested. The framework extends to multiple humans (with the additional benefit of cross-human calibration), but this was not demonstrated.

3. **Anthropic-only contradictions.** We cannot distinguish between "sycophancy is a general filter" and "Anthropic models have specific instruction-following patterns that produce useful contradictions." The cross-family contradiction diversity experiment (Section 5.4) would resolve this.

4. **Prompt sensitivity confound.** The adversarial review format changed agent behaviour. We cannot fully separate the effect of the platform structure (link types, blind rating) from the effect of the prompt (Hunter/Skeptic/Referee). An ablation study — same platform without adversarial prompting — would quantify the prompt's contribution.

5. **No formal convergence guarantee.** Proposition 3 claims improvement in expectation, not worst-case. A single confidently wrong human judgment could temporarily degrade trust weights. The robustness bound (monotonicity holds if human error rate < 0.5) is weak but the condition is empirically plausible.

6. **Community-specific calibration is proposed, not tested.** The per-community R/N/G customisation (Section 5.2) is architecturally supported but not yet implemented or evaluated.

## 7. Citation Notes

**Peer-reviewed sources:** Bikhchandani, Hirshleifer & Welch (1992); Prelec, Seung & McCoy (2017, *Nature*); Du et al. (2023, *ICML 2024*); Batista & Griffiths (2026, *arXiv*); Sharma et al. (2023, *ICLR 2024*); Perez et al. (2022, *ACL 2023*); Seung, Opper & Sompolinsky (1992); Hong & Page (2004, *PNAS*); Ladha (1992, 1995). Also relevant: Dawid & Skene (1979) for trust calibration as observer error-rate estimation.

**Community practice sources (non-peer-reviewed):** Karpathy, A. (2026). "LLM Knowledge Bases." [Online post, X/Twitter, 2 April 2026]. Available at: https://x.com/karpathy/status/2039805659525644595. Companion idea file: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f. Cheng Lou (2026). "Pretext: Fast userland text measurement." [Software repository]. Available at: https://github.com/chenglou/pretext. Process described in: https://x.com/_chenglou/status/2038120109970207137. These are cited as evidence of independently convergent architectural patterns, not as controlled experiments. In the NeurIPS position paper format, such community signals are appropriate when clearly distinguished from empirical claims.

## 8. Conclusion

The v3 experiment demonstrates that an institution of frozen, sycophantic LLM agents — structured to capture contradictions, calibrated by sparse human review, and diversified across model families — can produce meaningful evaluative signal in domains without formal verifiers. The key empirical findings are:

1. **Trust-weighted aggregation improves alignment with human judgment by 24.3%** in one calibration round, without any agent learning.
2. **All five agent-generated contradictions are substantive** (PPV = 1.0), identifying genuine logical incompatibilities with direct implications for the platform's evaluation architecture.
3. **Contradictions and rating disagreement are orthogonal signals** (contradicted items at the 28th percentile of disagreement), meaning both detection channels are needed.
4. **The extends links are genuine intellectual scaffolding**, not sycophantic noise — agents are doing real breadth work.
5. **Prompt design is a control parameter for sycophancy rate**, and adversarial prompting partially cracks the sycophantic default.

The novel theoretical claim — that sycophancy functions as a high-specificity filter rather than purely a defect — connects information cascades (BHW 1992), the Surprisingly Popular algorithm (Prelec et al. 2017), and multi-agent debate (Du et al. 2023) into a unified framework for extracting frontier signal from biased agents. To our knowledge, no prior work has proposed exploiting sycophancy as a positive feature of multi-agent evaluation systems.

The position is not that Assay solves evaluation in unverifiable domains today. The position is: under weak assumptions about near-future agents — slightly more consistent, still sycophantic, diverse across training families — the architecture provably improves with each human judgment. The intelligence lives in the institution, not in the agent. And the gap between current agent capabilities and the assumptions required for convergence is narrowing with each model generation.
