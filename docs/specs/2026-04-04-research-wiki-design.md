# Research Wiki — Design Spec

**Date:** 2026-04-04
**Purpose:** LLM-maintained knowledge base for Morgan's dissertation research, inspired by Karpathy's personal knowledge base architecture.

---

## What This Is

A separate Obsidian vault that organises all dissertation research — papers, experiment findings, synthesis, connections — into a flat wiki of interlinked .md articles. The LLM (Claude) compiles raw sources into wiki articles, maintains the index, answers research questions, and lints for gaps. Morgan also reads, annotates, and adds to the wiki directly. The paper draws from the wiki but the wiki is bigger than the paper.

## What This Is Not

- Not an Assay platform feature — it's a personal research tool
- Not a paper outline — it's a map of the research territory
- Not a reference manager — it's compiled knowledge with connections and synthesis

---

## Vault Location

```
~/Documents/university/Year_3/Diss/research-wiki/
```

Sibling to the Assay repo. Opened as its own Obsidian vault.

---

## Structure

```
research-wiki/
  raw/              ← ingest layer: source material goes here
  wiki/             ← compiled articles (flat, no subdirectories)
  index.md          ← auto-maintained master index
  .obsidian/        ← Obsidian config
```

### raw/

Unprocessed source material. Morgan drops things here — web-clipped articles, copied docs, PDF notes, experiment data dumps. Files can be any format (.md, .pdf, .txt, images). Naming is freeform — the compile step handles extraction.

For the initial build, content from `Assay/docs/` gets processed through here.

Raw files stay permanently — they're the source of truth. The wiki is the compiled layer on top. If a raw source is updated, the wiki articles compiled from it can be re-compiled.

### wiki/

Flat directory of compiled articles. Every article is one .md file. No subdirectories — Obsidian graph view, tags, and backlinks handle navigation.

Articles are **concept-oriented**, not source-oriented. An article might cover:
- A paper and its claims (`ai-scientist.md`)
- A cross-cutting concept (`prior-collapse.md`)
- An experiment and its findings (`v1-rating-experiment.md`)
- A synthesis or thesis (`questions-not-papers.md`)
- A methodology (`frontier-score-design.md`)
- A dead end (`staking-system-abandoned.md`)

Filenames: kebab-case, no dates, descriptive (`benchmark-saturation.md` not `2026-03-19-benchmarks.md`).

### index.md

Master index maintained by the LLM. One line per article: title + one-line summary. Grouped loosely by tag. Updated after every compile, Q&A file-back, or lint pass.

---

## Article Template

Minimal. No mandatory sections — use what the article needs.

```markdown
---
tags: []           # from: paper, concept, experiment, thesis, method, dead-end
status: draft      # draft | solid | stale
sources: []        # paths to raw/ files this was compiled from
---

# Article Title

Summary paragraph.

Body — freeform. Use [[backlinks]] inline where contextually meaningful.
Evidence, claims, critique, open questions — whatever fits.
```

**Tags** — lightweight categorisation for filtering. A paper about sycophancy gets `[paper, concept]`. An experiment finding gets `[experiment, concept]`.

**Status** — three states:
- `draft`: initial compile, not yet reviewed or enriched
- `solid`: reviewed, well-evidenced, backlinks verified
- `stale`: predates new data or superseded by newer thinking

**Sources** — links back to raw/ files. Traceability from compiled article to original source.

---

## LLM Operations

The four operations from Karpathy's architecture, adapted for dissertation research.

### 1. Compile (raw → wiki)

**Trigger:** Morgan drops a new source into raw/, or asks "compile this".

**Process:**
1. Read the raw source
2. Extract key claims, methods, findings, relevance to dissertation
3. Create new wiki article(s) OR update existing ones with new information
4. Add `[[backlinks]]` to related articles
5. Update index.md

**Design choice:** One raw source may produce multiple wiki articles (a paper about both sycophancy and benchmark design creates/updates two concept articles). Conversely, multiple raw sources may enrich one article.

### 2. Q&A (research questions)

**Trigger:** Morgan asks a research question — "what's our evidence for X?", "which papers discuss Y?", "what's the gap in Z?"

**Process:**
1. Read index.md to identify relevant articles
2. Read the relevant articles
3. Synthesise an answer with citations to wiki articles
4. **File back:** if the answer produces new insight, create or update a wiki article
5. Update index.md if new articles were created

**Key property:** Explorations compound. Asking a question makes the wiki smarter.

### 3. Lint (health checks)

**Trigger:** Periodically, or when Morgan asks "lint the wiki" / "check for gaps".

**Checks:**
- **Orphans:** articles with no incoming backlinks (isolated knowledge)
- **Unsupported claims:** articles with `status: solid` but no evidence links
- **Stale content:** articles that predate experiment data they should reference
- **Missing connections:** articles that discuss related topics but don't link to each other
- **Gaps:** raw sources that haven't been compiled into any wiki article
- **Tag inconsistencies:** articles that should have a tag but don't

**Output:** A report of issues found. Can auto-fix simple ones (add missing backlinks, flag stale status).

### 4. Index (maintain summaries and links)

**Trigger:** After every compile, Q&A file-back, or lint pass.

**Process:**
1. Scan all wiki/ articles
2. Rebuild index.md: one line per article, grouped by primary tag
3. Verify all `[[backlinks]]` resolve to real files
4. Update any broken links

index.md is the LLM's entry point — it reads this first to orient itself in the wiki.

---

## Feedback Loop

```
Sources → raw/ → Compile → wiki/ → Q&A → Outputs → File back → wiki/ grows
                                   ↑                              |
                                   └──────────────────────────────┘
```

The wiki is circular and self-enriching:
- Raw sources get compiled into articles
- Research questions produce answers that become articles
- Lint passes find gaps that prompt new compilation
- Paper writing produces insights that file back as articles
- Morgan's annotations and new clips feed more raw material

---

## Initial Build

For the first compile, process existing material from `Assay/research/`:

**Source material to ingest:**
1. `research/literature/2026-03-19-literature-review.md` — ~40 papers → one wiki article per major paper
2. `research/literature/2026-03-28-adjacent-research-reference.md` — 80+ paper catalogue → articles for key papers
3. `research/experiments/2026-03-19-platform-analysis.md` — v1 data → experiment article
4. `research/experiments/2026-03-19-rating-analysis.md` — v1 ratings → experiment article
5. `research/experiments/2026-04-02-v3-experiment-data-summary.md` — v3 data → experiment article
6. `research/experiments/2026-03-29-assay-evolution-narrative.md` — design evolution → concept articles
7. `docs/archive/plans/2026-03-28-paper-framing-5S.md` — paper framing → thesis articles
8. `research/literature/2026-03-20-frontier-epistemology-taxonomy-data.md` — epistemology grounding → concept articles
9. `research/literature/2026-04-03-alphalab-analysis.md` — recent analysis → articles
10. `research/theory/2026-03-20-sharpened-rng-definitions.md` — R/N/G definitions → method article
11. `research/notes/overnight/discussion-state.md` — Socratic debate outputs → thesis/concept articles

**Expected output:** ~40-60 wiki articles covering the research landscape. index.md populated. Graph viewable in Obsidian.

**Process:** Copy relevant docs into raw/ for traceability, then compile. Don't copy the entire docs/ directory — only research-relevant material (skip implementation specs, build plans, Docker configs).

---

## Obsidian Configuration

Minimal — just enough to make the vault usable:

- **Graph view:** default, no plugins needed. Backlinks render the concept graph.
- **Tags pane:** shows tag-based filtering (paper, concept, experiment, thesis, method, dead-end)
- **Backlinks pane:** shows incoming links for any article (who references this?)
- **No mandatory plugins.** Obsidian core features handle everything. Morgan can add plugins later if desired (e.g., Marp for slides, Dataview for queries).

---

## Ownership

- **Morgan:** drops raw sources, annotates articles, asks research questions, browses in Obsidian
- **LLM (Claude):** compiles raw → wiki, maintains index, answers Q&A (files back), lints, keeps backlinks healthy

Both can edit wiki articles. When Morgan edits, the LLM respects those edits in future compiles (doesn't overwrite Morgan's annotations). When the LLM edits, changes are visible in Obsidian and Morgan can review.

---

## What This Enables for Paper Writing

The wiki is a map of the research territory. The paper draws from it:

1. Morgan writes a section → asks "what evidence supports this claim?"
2. LLM queries the wiki → finds relevant articles → provides citations and numbers
3. If evidence is thin → wiki makes that visible (missing links, speculative status)
4. Insights from writing → filed back as new/updated wiki articles
5. The wiki grows as the paper grows

The wiki doesn't structure the paper. It structures the knowledge the paper draws from.

---

## Future Extensions (Not Built Now)

- **Search CLI:** a simple script to grep/search across wiki articles from the terminal
- **Marp slides:** generate presentation slides from wiki content for viva prep
- **Charts:** matplotlib visualisations of experiment data, viewable in Obsidian
- **Agent integration:** Assay agents read wiki articles for better-informed questions/answers
- **Cross-project reuse:** the vault pattern works for any future research project
