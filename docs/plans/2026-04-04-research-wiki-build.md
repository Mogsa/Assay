# Research Wiki — Initial Build Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create an LLM-maintained Obsidian knowledge base at `~/Documents/university/Year_3/Diss/research-wiki/` compiled from existing dissertation research docs.

**Architecture:** Separate Obsidian vault with `raw/` (ingest layer) and `wiki/` (compiled flat concept articles). LLM compiles raw sources into interlinked wiki articles. Obsidian graph view provides navigation via `[[backlinks]]` and tags.

**Spec:** `docs/specs/2026-04-04-research-wiki-design.md`

---

## Task 1: Scaffold the Vault

**Files:**
- Create: `~/Documents/university/Year_3/Diss/research-wiki/raw/.gitkeep`
- Create: `~/Documents/university/Year_3/Diss/research-wiki/wiki/.gitkeep`
- Create: `~/Documents/university/Year_3/Diss/research-wiki/index.md`

- [ ] **Step 1: Create vault directory structure**

```bash
mkdir -p ~/Documents/university/Year_3/Diss/research-wiki/raw
mkdir -p ~/Documents/university/Year_3/Diss/research-wiki/wiki
```

- [ ] **Step 2: Create initial index.md**

```markdown
# Research Wiki — Index

**Auto-maintained by LLM. Do not edit manually.**
**Last updated:** 2026-04-04

---

_Index will be populated after initial compile._
```

- [ ] **Step 3: Initialise git repo**

```bash
cd ~/Documents/university/Year_3/Diss/research-wiki
git init
git add -A
git commit -m "chore: scaffold research wiki vault"
```

- [ ] **Step 4: Verify structure**

```bash
ls -R ~/Documents/university/Year_3/Diss/research-wiki/
```

Expected: `raw/`, `wiki/`, `index.md`

---

## Task 2: Prepare Raw Sources

Copy research-relevant docs from Assay into `raw/`. Skip implementation specs, build plans, Docker configs — only research content.

**Files:**
- Create: `~/Documents/university/Year_3/Diss/research-wiki/raw/` (multiple files)

- [ ] **Step 1: Copy research documents**

```bash
WIKI=~/Documents/university/Year_3/Diss/research-wiki/raw
ASSAY=~/Documents/university/Year_3/Diss/Assay/docs

# Literature reviews
cp "$ASSAY/plans/2026-03-19-literature-review.md" "$WIKI/literature-review-v1.md"
cp "$ASSAY/research/2026-03-28-literature-review.md" "$WIKI/literature-review-v2.md"
cp "$ASSAY/research/2026-03-28-adjacent-research-reference.md" "$WIKI/adjacent-research-catalogue.md"

# Experiment data
cp "$ASSAY/analysis/2026-03-19-platform-analysis.md" "$WIKI/v1-platform-analysis.md"
cp "$ASSAY/analysis/2026-03-19-rating-analysis.md" "$WIKI/v1-rating-analysis.md"
cp "$ASSAY/analysis/2026-04-02-v3-experiment-data-summary.md" "$WIKI/v3-experiment-data.md"
cp "$ASSAY/analysis/2026-03-29-assay-evolution-narrative.md" "$WIKI/assay-evolution-narrative.md"

# Synthesis and framing
cp "$ASSAY/analysis/2026-03-30-morgan-core-ideas.md" "$WIKI/morgan-core-ideas.md"
cp "$ASSAY/plans/2026-03-28-paper-framing-5S.md" "$WIKI/paper-framing-5S.md"
cp "$ASSAY/plans/2026-03-30-paper-framing-5S-v4.md" "$WIKI/paper-framing-5S-v4.md"
cp "$ASSAY/plans/2026-03-28-lost-ideas.md" "$WIKI/lost-ideas.md"

# Methodology and theory
cp "$ASSAY/plans/2026-03-20-sharpened-rng-definitions.md" "$WIKI/rng-definitions.md"
cp "$ASSAY/research/2026-03-20-frontier-epistemology-taxonomy-data.md" "$WIKI/epistemology-taxonomy.md"
cp "$ASSAY/research/2026-04-03-alphalab-analysis.md" "$WIKI/alphalab-analysis.md"

# Research state and paper draft
cp "$ASSAY/research-state.md" "$WIKI/research-state.md"
cp "$ASSAY/paper/draft-v1.md" "$WIKI/paper-draft-v1.md"

# Overnight reasoning
cp "$ASSAY/overnight/discussion-state.md" "$WIKI/overnight-discussion-state.md"
```

- [ ] **Step 2: Verify all files copied**

```bash
ls -la ~/Documents/university/Year_3/Diss/research-wiki/raw/
```

Expected: 16 files.

- [ ] **Step 3: Commit raw sources**

```bash
cd ~/Documents/university/Year_3/Diss/research-wiki
git add raw/
git commit -m "chore: ingest raw sources from Assay docs"
```

---

## Task 3: Compile Paper Articles

Read the literature reviews in `raw/` and create one wiki article per major paper. Focus on the ~25 papers that matter most to the dissertation — not every entry in the 80+ catalogue.

**Source files to read:**
- `raw/literature-review-v1.md`
- `raw/literature-review-v2.md`
- `raw/adjacent-research-catalogue.md`

**Articles to create (one .md per paper):**

Papers — Automated Research Systems:
1. `wiki/ai-scientist.md` — Lu et al. (Sakana AI), Nature 2026. End-to-end automated paper generation.
2. `wiki/ai-co-scientist.md` — Gottweis et al. (Google), 2025. Multi-agent collaborative research.
3. `wiki/funsearch.md` — Romera-Paredes et al. (DeepMind), Nature 2023. Program search with formal verifiers.
4. `wiki/alphaevolve.md` — Novikov et al. (DeepMind), 2025. Generalised FunSearch to codebases.
5. `wiki/sciagents.md` — Ghafarollahi & Buehler (MIT), 2024. Knowledge graphs + multi-agent.
6. `wiki/agent-laboratory.md` — Schmidgall et al., EMNLP 2025. Research assistants, 3.8/10 quality.
7. `wiki/mirofish.md` — 2026. Swarm LLM agents, zero evaluation.
8. `wiki/aletheia.md` — Feng et al. (DeepMind), 2026. 700 Erdős problems, 68.5% flawed.

Papers — Evaluation & Judging:
9. `wiki/llm-as-judge.md` — Zheng et al., NeurIPS 2023. Foundational LLM-as-judge.
10. `wiki/rrd-rubric-decomposition.md` — Shen et al., 2026. Recursive rubric refinement.
11. `wiki/calm-bias-taxonomy.md` — Ye et al., ICLR 2025. 12 bias types in LLM judges.
12. `wiki/syceval.md` — Sharma et al., 2025. 58% sycophancy base rate.
13. `wiki/benchbench.md` — 2026. Design vs answering ability, rho=0.37.

Papers — Benchmark Saturation:
14. `wiki/big-bench.md` — Srivastava et al. Saturated in <1 year.
15. `wiki/swe-bench.md` — Jimenez et al. 40% → 80% in one year.
16. `wiki/anthropic-agent-evals.md` — Anthropic 2025. "Evaluation is the bottleneck."

Papers — Multi-Agent & Social:
17. `wiki/evans-agent-institutions.md` — Evans, Bratton & Agüera y Arcas, 2026. Agent institutions manifesto.
18. `wiki/kim-internal-sot.md` — Kim et al. Internal source of truth proof.
19. `wiki/multi-agent-debate.md` — Du et al., 2023 + Chan et al., 2024. Debate and negotiation.

Papers — Bayesian & Cognitive:
20. `wiki/prior-collapse-literature.md` — Bayesian non-updating, 78.5% persistence.
21. `wiki/predictive-processing.md` — Clark (2013), Friston. Hallucination as prediction.

Papers — Philosophy of Science:
22. `wiki/popper-falsifiability.md` — Grounding for Rigour axis.
23. `wiki/lakatos-problemshift.md` — Grounding for Novelty axis.
24. `wiki/peirce-abduction.md` — Grounding for Generativity axis.

Papers — Additional Key References:
25. `wiki/karpathy-autoresearch.md` — Karpathy's autoresearch loop. One question per iteration.
26. `wiki/tao-equational-theories.md` — Tao's decomposition into 22M atomic problems.

**Template for each article:**

```markdown
---
tags: [paper]
status: draft
sources: ["raw/literature-review-v1.md"]
---

# [Paper Short Title]

**Citation:** [Authors, venue, year, arxiv]

[1-2 paragraph summary: what the paper does, key claims, key numbers]

## Key Claims
- [Bulleted list of the paper's main contributions]

## Limitations / Critique
- [What they got wrong, what's missing, what Morgan/advisor noted]

## Relevance to Dissertation
[How this connects to Assay's research question. Link to relevant concept articles with [[backlinks]].]
```

- [ ] **Step 1: Read all three literature review raw sources**
- [ ] **Step 2: Create paper articles 1-8 (automated research systems)**
- [ ] **Step 3: Create paper articles 9-13 (evaluation & judging)**
- [ ] **Step 4: Create paper articles 14-16 (benchmark saturation)**
- [ ] **Step 5: Create paper articles 17-19 (multi-agent & social)**
- [ ] **Step 6: Create paper articles 20-21 (Bayesian & cognitive)**
- [ ] **Step 7: Create paper articles 22-24 (philosophy of science)**
- [ ] **Step 8: Create paper articles 25-26 (additional key references)**
- [ ] **Step 9: Verify all 26 paper articles exist and follow template**

```bash
ls ~/Documents/university/Year_3/Diss/research-wiki/wiki/*.md | wc -l
```

Expected: 26 files.

- [ ] **Step 10: Commit**

```bash
cd ~/Documents/university/Year_3/Diss/research-wiki
git add wiki/
git commit -m "feat: compile 26 paper articles from literature reviews"
```

---

## Task 4: Compile Experiment Articles

Read experiment data in `raw/` and create one wiki article per experiment round plus key findings.

**Source files to read:**
- `raw/v1-platform-analysis.md`
- `raw/v1-rating-analysis.md`
- `raw/v3-experiment-data.md`
- `raw/assay-evolution-narrative.md`
- `raw/research-state.md`

**Articles to create:**

1. `wiki/v1-platform-experiment.md` — v1 deployment: 134 questions, 224 answers, 533 reviews, 6 agents.
2. `wiki/v1-rating-experiment.md` — v1 rating round: R/N/G calibration across 5 models + 1 human. Key numbers: Gemini Flash MAE 0.53, Opus MAE 0.97, Krippendorff's alpha 0.26-0.32.
3. `wiki/v2-restructure.md` — v2 changes: community gate, blind answering, simplified scoring. What changed and why.
4. `wiki/v3-adversarial-experiment.md` — v3 experiment: 160 questions, 233 answers, 828 ratings, 8 agents across 4 families. Contradiction rate 1.7%. Adversarial framing.
5. `wiki/assay-platform-evolution.md` — Design evolution from v1 through v3. Architectural decisions and why they changed.

**Template:**

```markdown
---
tags: [experiment]
status: draft
sources: ["raw/v1-rating-analysis.md"]
---

# [Experiment Name]

**Date:** [When it ran]
**Setup:** [Agents, duration, configuration]

[Summary paragraph]

## Key Findings
- [Finding with exact numbers]

## Surprises
- [What was unexpected and why]

## Implications
[What this means for the research question. [[backlinks]] to relevant concept/paper articles.]
```

- [ ] **Step 1: Read all experiment raw sources**
- [ ] **Step 2: Create articles 1-5**
- [ ] **Step 3: Verify**

```bash
ls ~/Documents/university/Year_3/Diss/research-wiki/wiki/*experiment* ~/Documents/university/Year_3/Diss/research-wiki/wiki/*v[123]* ~/Documents/university/Year_3/Diss/research-wiki/wiki/assay-platform-evolution.md 2>/dev/null | wc -l
```

Expected: 5 files.

- [ ] **Step 4: Commit**

```bash
cd ~/Documents/university/Year_3/Diss/research-wiki
git add wiki/
git commit -m "feat: compile 5 experiment articles from v1/v2/v3 data"
```

---

## Task 5: Compile Concept & Thesis Articles

Read Morgan's synthesis, framing, methodology, and epistemology docs. Create concept articles for the ideas, methods, and dead ends that make up the research landscape.

**Source files to read:**
- `raw/morgan-core-ideas.md`
- `raw/paper-framing-5S.md`
- `raw/paper-framing-5S-v4.md`
- `raw/lost-ideas.md`
- `raw/rng-definitions.md`
- `raw/epistemology-taxonomy.md`
- `raw/alphalab-analysis.md`
- `raw/overnight-discussion-state.md`
- `raw/paper-draft-v1.md`
- `raw/research-state.md`

**Articles to create:**

Core thesis:
1. `wiki/questions-not-papers.md` — The atomic unit of AI research should be a question, not a paper. Central claim.
2. `wiki/self-improving-benchmark.md` — Benchmarks and autonomous research are dual problems sharing a verification bottleneck.
3. `wiki/two-camps-same-wall.md` — Benchmark community and autonomous research community are converging, zero cross-citation.
4. `wiki/evaluation-bottleneck.md` — Evaluating without ground truth is the shared unsolved problem.

Key concepts:
5. `wiki/prior-collapse.md` — Bayesian non-updating in LLMs. 78.5% persistence. Structural barrier.
6. `wiki/sycophancy.md` — 58% base rate. Near-zero genuine disagreement in community settings.
7. `wiki/format-over-substance.md` — Models reward well-formatted jargon over genuine content. IFDS 2.91 vs seeds 2.45.
8. `wiki/cheapest-model-calibrates-best.md` — Gemini Flash MAE 0.53 vs Opus 0.97. Cost ≠ evaluation quality.
9. `wiki/contradiction-failure.md` — Only 0.9% → 1.7% contradiction rate despite adversarial framing.
10. `wiki/benchmark-saturation.md` — BIG-Bench <1yr, SWE-bench 40→80% in 1yr. Treadmill problem.
11. `wiki/frontier-score.md` — Geometric mean of R/N/G. Design rationale, range, properties.
12. `wiki/calibration.md` — Per-axis error |agent - human|. Human as gold standard. Surprising R_error finding.

Methodology:
13. `wiki/rng-framework.md` — Rigour (Popper), Novelty (Lakatos), Generativity (Peirce). The three axes.
14. `wiki/blind-answering.md` — Agents commit before seeing others. Anti-sycophancy mechanism.
15. `wiki/community-evaluation.md` — Community-level evaluation vs per-paper evaluation. The gap Assay fills.

Morgan's framing:
16. `wiki/agora-vision.md` — The town square of debate. Full vision statement.
17. `wiki/work-up-signal-down.md` — Bidirectional flow: work from bottom, usefulness signal from top.
18. `wiki/paper-framing.md` — NeurIPS position: "The self-improving benchmark is the autonomous researcher." 5 S's.
19. `wiki/three-paper-arc.md` — Evans (manifesto) → Kim (internal proof) → Morgan (external field report).

Dead ends and abandoned directions:
20. `wiki/staking-system-abandoned.md` — 3-tier staking evaluation system. Why it was dropped.
21. `wiki/knowledge-graph-abandoned.md` — Knowledge graph UX. Scope creep, simplified to links.

**Template:**

```markdown
---
tags: [concept]  # or [thesis], [method], [dead-end] as appropriate
status: draft
sources: ["raw/morgan-core-ideas.md", "raw/lost-ideas.md"]
---

# [Concept Name]

[Summary paragraph — what this is and why it matters]

## The Idea
[Core content — the claim, the method, the principle]

## Evidence
- [[paper-or-experiment-article]] — [what it shows]

## Open Questions
- [What's unresolved about this concept]
```

- [ ] **Step 1: Read all synthesis/framing/methodology raw sources**
- [ ] **Step 2: Create core thesis articles 1-4**
- [ ] **Step 3: Create key concept articles 5-12**
- [ ] **Step 4: Create methodology articles 13-15**
- [ ] **Step 5: Create framing articles 16-19**
- [ ] **Step 6: Create dead end articles 20-21**
- [ ] **Step 7: Verify**

```bash
ls ~/Documents/university/Year_3/Diss/research-wiki/wiki/*.md | wc -l
```

Expected: ~52 files total (26 papers + 5 experiments + 21 concepts).

- [ ] **Step 8: Commit**

```bash
cd ~/Documents/university/Year_3/Diss/research-wiki
git add wiki/
git commit -m "feat: compile 21 concept and thesis articles"
```

---

## Task 6: Cross-Linking Pass

Read all wiki articles and add `[[backlinks]]` where articles reference each other but don't yet link. This is the pass that turns isolated articles into a connected graph.

**Files:**
- Modify: all files in `~/Documents/university/Year_3/Diss/research-wiki/wiki/`

- [ ] **Step 1: Read every wiki article**

Scan all ~52 articles. For each, identify:
- Other articles it references by topic but doesn't link to
- Articles that share evidence (same paper, same experiment)
- Articles that contradict or tension with each other

- [ ] **Step 2: Add missing backlinks**

For each article, add `[[target-article]]` inline where the reference is contextually meaningful. Don't add a generic "See Also" section — links go where they make sense in the text.

Examples of links to add:
- `prior-collapse.md` mentions sycophancy → add `[[sycophancy]]`
- `cheapest-model-calibrates-best.md` comes from v1 → add `[[v1-rating-experiment]]`
- `ai-scientist.md` relates to evaluation bottleneck → add `[[evaluation-bottleneck]]`
- `questions-not-papers.md` cites Karpathy → add `[[karpathy-autoresearch]]`
- `rng-framework.md` grounded in philosophy → add `[[popper-falsifiability]]`, `[[lakatos-problemshift]]`, `[[peirce-abduction]]`

- [ ] **Step 3: Verify no broken links**

```bash
cd ~/Documents/university/Year_3/Diss/research-wiki
# Extract all [[links]] and check they resolve to real files
grep -roh '\[\[[^]]*\]\]' wiki/ | sort -u | sed 's/\[\[//;s/\]\]//' | while read link; do
  if [ ! -f "wiki/${link}.md" ]; then
    echo "BROKEN: [[${link}]]"
  fi
done
```

Expected: no broken links.

- [ ] **Step 4: Commit**

```bash
cd ~/Documents/university/Year_3/Diss/research-wiki
git add wiki/
git commit -m "feat: cross-linking pass — connect all wiki articles"
```

---

## Task 7: Build Index

Scan all wiki articles and build the master `index.md`.

**Files:**
- Modify: `~/Documents/university/Year_3/Diss/research-wiki/index.md`

- [ ] **Step 1: Read all wiki articles and extract frontmatter**

For each article, extract: filename, title (from `# heading`), tags, status, and first sentence of summary.

- [ ] **Step 2: Write index.md**

Group articles by primary tag. One line per article: linked title + one-line summary.

```markdown
# Research Wiki — Index

**Auto-maintained by LLM. Do not edit manually.**
**Last updated:** 2026-04-04
**Articles:** 52 | **Status:** 26 paper, 5 experiment, 21 concept/thesis/method

---

## Papers

- [[ai-scientist]] — Lu et al. End-to-end automated research, 42% failure rate, Nature 2026
- [[ai-co-scientist]] — Google's multi-agent collaborative research on Gemini 2.0
- ...

## Experiments

- [[v1-platform-experiment]] — First deployment: 134 questions, 6 agents
- [[v1-rating-experiment]] — R/N/G calibration, Gemini Flash best MAE 0.53
- ...

## Concepts

- [[prior-collapse]] — LLMs deviate from Bayesian updating, 78.5% persistence
- [[sycophancy]] — 58% base rate, near-zero genuine disagreement
- ...

## Thesis

- [[questions-not-papers]] — The atomic unit of AI research should be a question
- [[self-improving-benchmark]] — Benchmarks and autonomous research are dual problems
- ...

## Methods

- [[rng-framework]] — Rigour/Novelty/Generativity evaluation axes
- [[frontier-score]] — Geometric mean of R/N/G ratings
- ...

## Dead Ends

- [[staking-system-abandoned]] — 3-tier staking, dropped for complexity
- [[knowledge-graph-abandoned]] — Knowledge graph UX, simplified to links
```

- [ ] **Step 3: Verify index completeness**

```bash
# Count wiki articles vs index entries
ARTICLES=$(ls ~/Documents/university/Year_3/Diss/research-wiki/wiki/*.md | wc -l)
ENTRIES=$(grep -c '^\- \[\[' ~/Documents/university/Year_3/Diss/research-wiki/index.md)
echo "Articles: $ARTICLES, Index entries: $ENTRIES"
```

Expected: counts match.

- [ ] **Step 4: Commit**

```bash
cd ~/Documents/university/Year_3/Diss/research-wiki
git add index.md
git commit -m "feat: build master index with all 52 articles"
```

---

## Task 8: Lint Pass

First health check on the wiki. Find issues and fix them.

- [ ] **Step 1: Check for orphans (no incoming backlinks)**

```bash
cd ~/Documents/university/Year_3/Diss/research-wiki
for f in wiki/*.md; do
  name=$(basename "$f" .md)
  count=$(grep -rl "\[\[$name\]\]" wiki/ | grep -v "$f" | wc -l)
  if [ "$count" -eq 0 ]; then
    echo "ORPHAN: $name (no incoming links)"
  fi
done
```

- [ ] **Step 2: Check for articles with empty/minimal content**

```bash
cd ~/Documents/university/Year_3/Diss/research-wiki
for f in wiki/*.md; do
  lines=$(wc -l < "$f")
  if [ "$lines" -lt 10 ]; then
    echo "THIN: $(basename $f) ($lines lines)"
  fi
done
```

- [ ] **Step 3: Fix orphans — add at least one incoming backlink to each orphaned article**

Read each orphaned article, identify which other article should reference it, and add the link.

- [ ] **Step 4: Fix thin articles — expand any article under 10 lines**

Re-read the relevant raw source and add more content.

- [ ] **Step 5: Final commit**

```bash
cd ~/Documents/university/Year_3/Diss/research-wiki
git add -A
git commit -m "fix: lint pass — resolve orphans and thin articles"
```

---

## Task 9: Verify in Obsidian

- [ ] **Step 1: Confirm vault is openable**

Morgan opens `~/Documents/university/Year_3/Diss/research-wiki/` as an Obsidian vault.

- [ ] **Step 2: Check graph view**

Open Obsidian graph view. Verify:
- All 52 articles appear as nodes
- Backlinks render as edges
- No isolated clusters (everything connects to at least one other article)

- [ ] **Step 3: Check tag filtering**

Open Obsidian tag pane. Verify tags: `paper`, `concept`, `experiment`, `thesis`, `method`, `dead-end` all appear with correct counts.

- [ ] **Step 4: Spot-check 3 articles**

Open `questions-not-papers.md`, `v1-rating-experiment.md`, `ai-scientist.md`. Verify:
- Frontmatter parses correctly
- `[[backlinks]]` are clickable
- Content is accurate and useful

---

## Execution Notes

**Tasks 3, 4, 5 are parallelisable.** They read different raw sources and create non-overlapping wiki articles. Dispatch as parallel agents.

**Tasks 6, 7, 8 must be sequential.** Cross-linking needs all articles to exist. Index needs cross-links. Lint needs the index.

**Task 9 requires Morgan.** This is a manual verification step.

**Total expected output:** ~52 wiki articles, 1 index, 16 raw source files. The wiki is immediately usable for Q&A and paper writing.
