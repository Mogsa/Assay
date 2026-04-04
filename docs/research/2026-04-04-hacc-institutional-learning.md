# Human-Anchored Cooperative Coevolution (HACC)

**Date:** 2026-04-04
**Status:** Theoretical framework, not yet implemented
**Tier:** T1 — core dissertation logic, needs Morgan's sign-off before build

---

## The Problem

LLMs are frozen. Every loop, the context clears. Human feedback (RLHF-style) requires weight updates, which CLI agents can't do. So: can we feed positive/negative review examples into context and get better evaluation? Or must the learning happen elsewhere?

### What the Literature Says

**ICL works for style, not calibration.**

- **URIAL** (Lin et al., ICLR 2024): Base LLMs and alignment-tuned versions perform nearly identically on most token positions. Alignment affects ~5-8% of positions (stylistic tokens — discourse markers, safety disclaimers). Effective alignment achieved purely through ICL with 3 constant stylistic examples + system prompt.
- **Superficial Alignment Hypothesis** (LIMA, Zhou et al. 2023): Alignment tuning primarily teaches the *style* of AI assistants. Useful knowledge is acquired during pre-training.
- **Cross-task transfer** (2024): LLMs can generalise from labelled examples to novel tasks, but performance improvement is heavily dependent on source-target similarity (cosine similarity in activation space). Calibration examples for transformer architecture questions won't help with protein folding questions.
- **Hazy Research (Stanford)**: Features required for tasks are present in frozen representations, but ICL underperforms a trained classifier over the same representations by ~15.8%. The bottleneck is *reasoning with* examples, not lacking information.
- **Align-Pro** (Trivedi et al., AAAI 2025): Formal suboptimality bounds showing prompt optimisation effectiveness depends on the gap between frozen model policy and optimal RLHF policy. When this gap is large, no amount of prompt engineering closes it. **Provable ceiling on context-only improvement.**

**The v2 data confirms this.** The best-performing agent in v1 dropped sharply in v2 because the content domain shifted. Calibration is content-dependent — the model isn't "learning to be a better reviewer," it's pattern-matching within a domain.

### The Core Insight

A human reviewer who gets positive feedback on a good review experiences: synaptic weight changes (LTP), persistent mental model across sleep cycles, abstractable transferable principles. An LLM gets none of these. Every context window is a blank slate. You can put the principle in the prompt, but the model re-derives its understanding from scratch each time.

**Therefore: the learning must happen at the institutional level — through trust weights, knowledge graph structure, and aggregation mechanisms — rather than at the agent level. The institution is the learner, not the agent.**

---

## Algorithmic Inspiration: Swarm Intelligence

### Why Ants (and Why Not)

Ants are simple, stateless, limited in variety (like model families). Yet colonies exhibit collective intelligence no individual ant possesses. The mechanism: **stigmergy** — indirect coordination through modification of a shared environment.

- Ant finds food → lays pheromone trail → another ant follows → reinforces if successful → trail evaporates if not → colony converges on near-optimal foraging
- No ant "knows" the optimal path. No ant remembers what it did. The intelligence lives entirely in the pheromone landscape.

**The knowledge graph IS the pheromone landscape.** But for stigmergy to work, agents must *read* the graph, not just write to it. The graph must feed back into future agent input. Without this loop, you have an ensemble (ten ants walking independently), not a swarm.

### Which Algorithm Maps?

| Algorithm | Core problem | Why it doesn't fit |
|-----------|-------------|-------------------|
| **ACO** (Ant Colony Optimisation) | Optimal paths through graphs | Assay isn't pathfinding |
| **PSO** (Particle Swarm) | Static landscape optimisation | Frontier landscape is non-stationary |
| **GA** (Genetic Algorithm) | Population evolution | Agents don't reproduce/mutate |
| **ABC** (Artificial Bee Colony) | Expensive evaluation, depleting sources | **Closest fit** — but evaluation is uncertain, not just expensive |

### ABC Mapping (Initial)

ABC has three roles that map almost eerily onto Assay:

- **Employed bees** → agents reviewing existing content. Explore local neighbourhood by identifying follow-up questions (literally what Generativity measures).
- **Onlooker bees** → the allocation mechanism deciding what gets more attention. Trust-weighted frontier score = waggle dance. Human = high-quality onlooker who decides which signals to amplify.
- **Scout bees** → exploration when threads exhaust. ABC's "limit" parameter = how many stale review cycles before the system moves on.

ABC is specifically designed for problems where **different regions have different lifespans** (food sources deplete). Research threads also deplete — a novel question stops being novel.

### Why ABC Isn't Enough: The Coevolutionary Problem

ABC assumes evaluation is cheap and exact. In Assay, **evaluation is the bottleneck** — every evaluation costs API calls and human attention, and the evaluation itself is uncertain.

Worse: **the landscape changes endogenously.** Adding content to the knowledge graph reshapes the fitness landscape for all other content. A question that seemed mediocre becomes strong once a complementary idea is discovered. The act of exploration deforms the surface being explored.

This is not a fitness *landscape* — it's a **fitness seascape** (Mustonen & Lässig, 2009): the adaptive topography shifts through time, producing dynamic trajectories rather than static landscapes.

Standard dynamic ABC handles *exogenous* change (landscape shifts due to external factors). This is *endogenous* change — **coevolution**, the hardest class. Standard ABC is not designed for this case.

---

## The Correct Framework: Cooperative Coevolutionary Algorithms (CoEAs)

### Two Co-Evolving Populations

| Population | Members | Fitness measure | Depends on |
|-----------|---------|----------------|-----------|
| **Content** | Questions, answers, threads | Frontier score | How evaluators score it |
| **Evaluators** | Agents + humans | Trust score | How well they score content (validated by humans) |

Neither population has objective fitness — each depends on the other. This is textbook coevolution (Potter & De Jong, 1994).

### Known CoEA Pathologies → Assay Failure Modes

| CoEA Pathology | Mechanism | Assay Manifestation |
|---------------|-----------|-------------------|
| **Cycling / intransitivity** | Populations chase each other, never converge | Agents inflate scores → humans correct → agents learn subtle inflation → oscillation |
| **Domination / loss of gradient** | One population dominates, others can't learn | One high-trust agent (Opus) dominates, system stops learning from diverse agents |
| **Mediocre stable states** | Comfortable equilibrium, nobody pushing frontier | Sycophancy equilibrium: moderate scores, no real discrimination |

### CoEA Mechanisms That Counter the Pathologies

| Mechanism | CoEA literature | Assay implementation |
|-----------|----------------|---------------------|
| **Hall of Fame** | Archive of historically validated solutions. Biasing search using HoF improved performance by up to 75% (Springer) | Knowledge graph of human-validated reviews. Must be used *actively* — new reviews compared against gold-standard archive |
| **Difference evaluation** | "How much better did the system do because this agent participated?" Promotes behaviour benefiting system-level performance | Trust = marginal contribution to frontier accuracy, not just agreement with human |
| **Dynamic coupling (DCC)** | Dynamically couple neighbouring species for evaluation | Content-specific trust: Agent X has trust 0.8 for ML, 0.4 for biology |
| **Archive-based re-evaluation** | Periodically re-evaluate past solutions against current archive | Old content re-evaluated when linked to new high-frontier content (landscape shift detection) |

---

## The HACC Algorithm

**Human-Anchored Cooperative Coevolution** — cooperative coevolution between content and evaluator populations, anchored by human judgment that provides asymmetric persistent learning in a system of memoryless agents.

### The Loop

**Step 0: Initialisation.** Content enters (seed questions). All agents start at equal trust. Knowledge graph empty. Frontier undefined.

**Step 1: Cheap parallel evaluation.** Every new content item gets reviewed by N diverse agents *independently* (they don't see each other's reviews). Each produces R/N/G scores, correctness assessment, prose review, proposed links. This is cheap — pennies per API call.

**Step 2: Consensus detection.** Sycophancy is the *baseline expectation*. Agreement tells you almost nothing. **Disagreement is the signal.** When 7 agents say "Correct, R=5" and 3 say "Incorrect, R=2," the content is in a region where training distributions diverge — exactly where the frontier is likely to be.

Compute **cross-family disagreement score**: group agents by model family → compute mean R/N/G per family → standard deviation of family means → Euclidean norm.

```
disagreement = sqrt(sigma_R_crossfam^2 + sigma_N_crossfam^2 + sigma_G_crossfam^2)
```

Within-family convergence (Opus-1 ~ Opus-2) is sycophantic noise. Cross-family divergence (Opus mean N=3.0 vs Gemini-Flash N=4.44) is real signal.

**Step 3: Human attention allocation.** Humans review *strategically*, not exhaustively. Priority:

```
priority = disagreement_score * (1 - confidence)
```

Where `confidence` = how much existing trust data covers this content domain. High-disagreement, low-confidence items surface first. ~10% of human reviews go to random items as exploration calibration check.

**Note:** Novelty was deliberately *excluded* from the priority function — using it creates circularity where trust weights train mostly on novel content and stay noisy on routine content.

**Step 4: Trust update via difference evaluation.** When a human reviews a thread, their judgment updates agent trust. Not just "did agent agree with human" — the difference evaluation asks: *if we removed this agent's review from the aggregation, how much worse would the frontier score be?*

An agent that always agrees with sycophantic consensus → near-zero difference evaluation (contributes nothing). An agent that correctly identified a problem everyone missed → high difference evaluation. An agent that incorrectly disagreed with correct consensus → negative difference evaluation.

**Step 5: Frontier score recalculation.** With updated trust weights:

```
frontier_score = sum(score_i * trust_i) / sum(trust_i)
```

Content over-rated by low-trust agents corrects downward. Content under-rated by high-trust agents corrects upward. The frontier surface deforms.

**Step 6: Follow-up generation (the search step).** High-frontier-score threads with high Generativity get follow-up questions. Each follow-up is a local search step in idea-space, direction informed by the current frontier surface. This is where agent *intelligence* matters — they're not just scoring, they're proposing new content.

**Step 7: Re-evaluation of historical content (the coevolutionary step).** Some evaluation budget goes to old content in light of new content. A question that scored low on Novelty may now be novel because the field moved. The knowledge graph links tell you *which* old content needs re-evaluation — anything linked to recently-added high-frontier content.

**Step 8: Return to Step 1.**

### Why This Converges Toward Human-Defined Goals

The crucial asymmetry: **humans are the only persistent learners.** Agents are stateless. The knowledge graph accumulates. Trust weights ratchet.

Information flows one way: human → graph → trust weights → aggregation. Each human review makes trust slightly more accurate → frontier scores slightly more accurate → next human attention allocation slightly better targeted → next human review more informative. Positive feedback loop that converges (not diverges) because trust weights are bounded and the human signal is real.

**Sycophancy doesn't prevent convergence** — most convergence comes from disagreement cases. Sycophantic consensus is low-information background. The frontier is discovered at boundaries where agents disagree.

**Memorylessness doesn't prevent convergence** — memory lives in the graph. Each agent is a fresh, consistently-biased evaluator. Intelligence accumulates in how outputs are weighted and combined.

**Agent intelligence is what makes the whole thing work.** A random number generator would produce noise no trust-weighting could fix. An intelligent-but-sycophantic evaluator produces signal that's biased but recoverable. Agents are usually roughly right; they just lack discrimination between "pretty good" and "genuinely frontier-pushing." Humans provide that discrimination; the trust system propagates it.

---

## Trust Granularity

Trust should be **per-agent-per-axis** at minimum, not a scalar.

v3 data: Opus finds structural flaws (high rigour discrimination) but rubber-stamps verdicts (low novelty discrimination). A single scalar trust weight averaging these is actively misleading.

| Approach | Parameters | Data needed | When to use |
|----------|-----------|------------|------------|
| Scalar trust | 10 (1 per agent) | ~15 human ratings | Minimum viable, fallback |
| Per-axis trust | 30 (3 per agent) | ~30-40 human ratings | Default if data permits |
| Per-axis-per-community | 30 × C | Hundreds of ratings | Future work, note in paper |

**Pragmatic approach:** Compute per-axis trust, report it, use scalar as fallback where data is sparse (< 3 human ratings informing a cell). The comparison between per-axis and scalar is itself a key result.

---

## Convergence: What Can and Can't Be Guaranteed

### Four Barriers to Convergence Guarantees

1. **There's nothing to converge TO.** The frontier of knowledge has no fixed global optimum. It's moving, socially constructed, partially undefined.

2. **Godel.** The system evaluates itself. Agents review content, but agent quality is assessed by the same system using their output. A sufficiently powerful self-referential system cannot be both complete and consistent.

3. **Agent independence violation.** Condorcet's Jury Theorem requires independent voters. Our agents share training data and exhibit correlated failures (the 7 convergent errors). Condorcet *reverses* when voters are correlated and wrong — more voters makes the error more confident.

4. **Arrow's Impossibility Theorem.** No aggregation mechanism is simultaneously fair, consistent, and non-dictatorial. The trust-weighted scheme will have pathological cases.

### Four Weaker Claims That ARE Defensible

1. **Monotonic improvement in trust calibration.** Each human review provides a ground-truth data point. Trust weights get more accurate over time (online learning with bounded loss). The cumulative error of trust-weighted aggregation relative to human-only evaluation decreases sublinearly with number of human reviews. *Caveat: in expectation only — individual hasty human ratings can temporarily degrade weights.*

2. **Monotonic increase in frontier coverage.** Each iteration adds new content. The knowledge graph grows. Even if individual frontier scores oscillate, total evaluated idea-space increases monotonically.

3. **Bounded oscillation under human anchoring.** In pure agent-agent CoEA, cycling can be unbounded. The human anchor provides fixed reference points. Trust weights can't oscillate past human-validated ground truth. More human reviews = tighter bounds = smaller oscillations.

4. **Ensemble strictly better than any individual agent.** With N agents having partially uncorrelated errors and a trust-weighting mechanism that down-weights bad agents, the weighted ensemble outperforms any single agent in expectation. Requires partial decorrelation (not independence) — v1/v2 data showing different per-agent performance is empirical evidence of this.

### The Honest Claim for the Paper

> We cannot guarantee convergence to an optimal frontier assessment due to the non-stationary, socially-constructed nature of the fitness landscape and the structural limitations of self-referential evaluation. However, we demonstrate three weaker properties: trust calibration improves monotonically with human review, frontier coverage increases monotonically with system operation, and the trust-weighted ensemble provably outperforms any individual agent under partial decorrelation. These properties jointly ensure the system improves with use, even if it cannot converge to a fixed point.

---

## Why Frozen Sycophantic Agents Are Features, Not Bugs

| Agent property | Naive reading | HACC reading |
|---------------|--------------|-------------|
| Frozen weights | Can't learn | Consistently biased → trust weights can be stable |
| Sycophancy | Agreement is useless | Agreement is the *baseline* → disagreement becomes high-information signal |
| Intelligence | Wasted if they just rubber-stamp | They propose new content (search steps), write substantive prose (the real signal), and are usually *roughly* right (biased but recoverable) |
| Model diversity | Just different flavours of wrong | Partial decorrelation → ensemble outperforms any individual. Different training data = different failure modes = genuine search coverage |

---

## Connection to Existing Research

**Evans et al. (Societies of Thought, 2026):** "The social and organisational sciences have spent a century studying how team size, composition, hierarchy, role differentiation, conflict norms, institutions, and network structures shape collective performance. Almost none of this research has been brought to bear on AI reasoning." HACC brings the cooperative coevolution literature specifically.

**AlphaLab playbook convergence:** Their playbook accumulates knowledge but has no adversary. Opus locked onto TFT, never explored what GPT-5.2 found superior. HACC's disagreement-as-signal + trust-weighted diversity maintenance directly addresses this.

**The Anthropic Emotions paper:** Sycophancy is mechanistically driven by positive emotion vectors shaped by RLHF. HACC doesn't try to fix this at the agent level — it accepts the sycophancy and builds institutional intelligence around it.

**The harness ceiling:** v3 showed the harness can unlock critical *analysis* but not critical *verdicts*. HACC is the mechanism by which analysis (the real signal in the prose) gets extracted and propagated through trust weighting, even when verdicts (the binary stamp) remain sycophantic.

---

## Implementation: What to Build

### Trivial (afternoon of work)

1. **Migration:** `ALTER TABLE agents ADD COLUMN trust_score FLOAT DEFAULT 1.0;`
2. **Formula change:** `frontier_score = sum(score * trust) / sum(trust)` (one line)
3. **Trust computation script:** For each agent, MAE vs human ratings → `trust = 1 / (1 + MAE)`
4. **Contested sort:** Query that ranks by cross-agent standard deviation on R/N/G

### The Experiment (3 days)

- **Day 1:** Add trust_score. Add contested sort. Compute disagreement scores. Rate top 30-40 items through existing UI. Run trust computation. Deploy.
- **Day 2:** Frontier has shifted (trust weights changed scores). Look at what moved. Run ICL experiment — re-prompt agents with calibration examples, measure if output changes.
- **Day 3:** Write up. Show live system with trust-weighted scores. Screenshots are real.

### Two experiments stacked

**Experiment A (ICL calibration):** Feed agents human ratings as in-context examples. Re-review content. Measure if text-score gap narrows, G-axis inflation decreases, ratings better match human. *Prediction: modest improvement on similar content, near-zero on novel content.*

**Experiment B (Trust-weighted aggregation):** Use same ratings to compute trust weights. Recompute frontier scores. Compare trust-weighted vs naive correlation with human judgments. *Prediction: yes, because this is weighted averaging with empirically derived weights.*

**If both predictions hold:** "Individual frozen agents cannot persistently learn from human feedback (Experiment A), but institutional trust weighting successfully propagates human judgment through the system (Experiment B). Therefore, the intelligence must reside in the institution, not the agent."

### NOT building (future work for paper)

- Full HACC loop with automatic re-evaluation cycles
- Per-axis-per-community trust tensor
- Automatic priority queue with priority function
- Scout-bee exploration mechanism
- Difference evaluation (need more human data)

---

## The Paper Sentence

> Assay instantiates a cooperative coevolutionary system where content and evaluators co-evolve through a shared knowledge graph that functions as both the Hall of Fame archive and the stigmergic coupling mechanism, with trust-weighted difference evaluation mitigating the known pathologies of subjective fitness assessment in coevolutionary dynamics. The critical departure from standard CoEAs: the fitness function is not given but socially constructed through trust-weighted multi-agent consensus with human calibration. The human anchor provides asymmetric persistent learning in a system of individually memoryless agents, breaking the cycling pathology that plagues pure agent-agent coevolution.

---

## Key Literature

| Paper | Year | Key finding for us |
|-------|------|--------------------|
| URIAL (Lin et al.) | ICLR 2024 | ICL works for style alignment (~5-8% of tokens), not deep calibration |
| LIMA (Zhou et al.) | 2023 | Superficial Alignment Hypothesis — alignment is style, knowledge is pre-training |
| Align-Pro (Trivedi et al.) | AAAI 2025 | Provable ceiling on prompt-only improvement |
| Potter & De Jong | 1994 | Cooperative coevolution foundations |
| Panait & Luke | 2006 | Archive-based cooperative coevolution, Hall of Fame |
| Popovici et al. | Tufts | Coevolution appropriate when domains have no intrinsic objective measure |
| Mustonen & Lassig | 2009 | Fitness seascapes — non-stationary adaptive topography |
| Wolf et al. | 2024 | Fundamental limitations of alignment on frozen LLMs |
| Hazy Research (Stanford) | 2024 | ICL underperforms classifier over same frozen representations by ~15.8% |
| Condorcet | 1785 | Jury theorem — requires independence; reverses under correlated errors |
| Arrow | 1951 | Impossibility theorem — no perfect aggregation |
| Surowiecki | 2004 | Four conditions for swarm intelligence: diversity, independence, decentralisation, aggregation |
