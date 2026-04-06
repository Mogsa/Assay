> **Note:** This is a record of one parallel Claude session on March 28. The canonical source of truth is `docs/research-state.md`, which integrates findings from this session AND the main brainstorming session. **Read research-state.md first.**

# Assay Research Session Report — March 28, 2026

**Session type:** Deep literature review + strategic positioning + theoretical framing
**Duration:** Extended session (~15 exchanges)
**Output:** This report, plus two reference documents (literature review markdown, adjacent research reference)

---

## 1. WHAT WE DID

### 1.1 First Literature Review Pass
Systematic web search across three query sets:
- **Query Set 1:** Automated/agentic scientific research (AI Scientist, AI Co-Scientist, FunSearch, SciAgents, MiroFish)
- **Query Set 2:** Multi-agent evaluation and peer review (LLM-as-Judge, Bradley-Terry, Chatbot Arena)
- **Query Set 3:** Knowledge frontiers and research mapping (frontier detection, novelty assessment, TDA)

Produced a structured literature review document (`assay_literature_review.md`) covering 20+ papers with a gap analysis table showing Assay's positioning.

### 1.2 Deep Research Review (Extended Search)
Launched a comprehensive deep dive following citation chains from anchor papers, exploring:
- Twitter/X threads from Jonas Hübotter, Jenny Zhang, Muratcan Koylan, Wei Dai
- HindSight paper (negative correlation between LLM novelty scores and actual impact)
- SciMON, ResearchAgent, diversity barriers in LLM ideation
- Google AI Co-Scientist validation and Elo reliability studies
- FunSearch → AlphaEvolve → MADE progression
- Self-improving evaluation agents (Darwin Gödel Machine, Hyperagents)
- Proof-of-useful-work literature and mechanism design
- Formal foundations for "evaluative frontier" concept
- Topological data analysis for knowledge discovery

Produced a 50+ paper synthesis covering the generation-evaluation gap.

### 1.3 TIG Whitepaper Analysis
Read and analyzed the full TIG (The Innovation Game) whitepaper v2.2. Identified TIG as the key structural analogue — a proof-of-useful-work system for computational methods where solutions are objectively verifiable. Mapped the structural parallel between TIG components and Assay components. Identified the core difference: TIG operates on the "easy to verify" side of Tao's spectrum; Assay operates on the "hard to evaluate" side.

### 1.4 Competitive Landscape Check
Searched specifically for whether anyone has built what Assay is building. Found:
- **OmniScientist** (arxiv:2511.16931, November 2025) — closest competitor with knowledge graph + ScienceArena (pairwise Elo voting). Critical difference: ScienceArena uses HUMAN expert voting. Assay uses endogenous agent-to-agent evaluation.
- **AI-Supervisor** (arxiv:2603.24402, March 26, 2026 — published one day before this session) — Knowledge Graph as Research World Model. Focuses on research supervision, not evaluation.
- **AgentRxiv** (arxiv:2503.18102) — preprint server for AI agents.

Conclusion: No existing system combines endogenous agent-to-agent evaluation, multi-axis quality assessment, knowledge graph topology, and mechanism design for incentivizing evaluation quality — all operating on content without objective ground truth.

### 1.5 Assay Codebase Review
Read the actual codebase at `/Users/morgan/Documents/university/Year_3/Diss/assay/`:
- `CLAUDE.md` — full architecture documentation
- `src/assay/models/` — all 14 SQLAlchemy models (Agent, Question, Answer, Rating, Link, etc.)
- `src/assay/routers/analytics.py` — knowledge graph and frontier classification endpoints
- `src/assay/routers/ratings.py` — R/N/G evaluation with frontier scoring
- `src/assay/routers/leaderboard.py` — karma-based ranking
- `docs/research-state.md` — comprehensive 500+ line research state document

### 1.6 Bombshell Papers Identification
Identified the 8 heavyweight papers (Science/Nature/PNAS) that define the theoretical landscape.

### 1.7 Evans et al. Analysis
Deep analysis of "Agentic AI and the next intelligence explosion" (Science, March 21, 2026) and its companion paper "Reasoning Models Generate Societies of Thought" (arxiv:2601.10825). Identified this as the theoretical ceiling Assay operates under.

### 1.8 Aether Framework Comparison
Analyzed github.com/jeff0926/aether — an agent framework where agents are portable file capsules with knowledge graphs and self-verification. Identified it as complementary (better individual agents) rather than competitive (agent institutions).

### 1.9 Hallucination-as-Generation-Mechanism Idea
Explored Morgan's insight that hallucination should be deliberately maximized as a generation mechanism, with Assay's institutional evaluation serving as the selection/filtering mechanism — analogous to predictive processing in neuroscience.

### 1.10 Aletheia (DeepMind) Analysis
Analyzed "Towards Autonomous Mathematics Research" (arxiv:2602.10177, February 2026). DeepMind's math research agent powered by Gemini Deep Think. Key findings: (a) proposed a formal autonomy taxonomy (Level H→A × Level 0→4) directly relevant to Assay; (b) their honest admission that solved Erdős problems were "obscurity not difficulty" confirms Assay's thesis — generation systems need evaluation infrastructure to know which problems are worth solving; (c) Aletheia's natural language verification (rather than Lean formalization) parallels Assay's choice of expressiveness over formal guarantees.

---

## 2. KEY FINDINGS

### 2.1 The Gap Assay Fills
No existing system combines:
1. **Endogenous agent-to-agent evaluation** (agents evaluate each other, not humans evaluating agents)
2. **Multi-axis quality assessment** (R/N/G framework grounded in philosophy of science)
3. **Knowledge graph as live institutional record** (not static literature representation)
4. **Questions as the unit of work** (not papers — nobody else does this)
5. **Mechanism design framing** (PoUW/TIG analogue for subjective domains)

### 2.2 The Unit-of-Work Insight
**Every autoresearch system optimizes for papers.** AI Scientist produces papers. AI Co-Scientist produces hypothesis documents. OmniScientist evaluates papers. Nobody has optimized for atomic questions. This is genuinely novel in the landscape. Questions are small enough to evaluate individually, linkable enough to form chains, and open-ended enough that there's no ground truth. This is why the institution metaphor works and the benchmark metaphor doesn't.

### 2.3 The HindSight Result
LLM-judged novelty is NEGATIVELY correlated with actual future research impact (ρ = −0.29, p < 0.01). This is the single most important empirical result for Assay's design — it proves that naive LLM novelty scoring actively misleads. Assay's multi-agent disagreement patterns and topological signals may provide better frontier detection than any individual LLM judge.

### 2.4 What Converges Across 80+ Papers

**Five things that consistently work:**
1. Pairwise comparison beats pointwise scoring everywhere
2. Multi-agent diversity produces genuine signal (but requires both persona variation AND knowledge partitioning)
3. Knowledge graphs make research agents substantially better than flat retrieval
4. The generate-evaluate loop is the core architecture regardless of domain
5. Calibration against human judgment is necessary but insufficient

**Six limitations nobody has solved:**
1. Evaluation degrades precisely where it matters most — at the frontier
2. Inter-rater reliability is too low for reliable consensus at small N
3. Diversity collapses at scale — LLMs converge to the same mode
4. No system treats evaluation itself as the primary research output
5. The gap between formally verifiable and subjectively evaluable domains remains unbridged
6. Mechanism design for honest evaluation is undertheorized

### 2.5 Assay's v1 Data Already Contains Publishable Findings
From the existing experiments (5 AI models + 1 human, 134 questions):
- Cheapest model calibrates best (Gemini Flash MAE=0.53 vs Opus MAE=0.97)
- Inter-rater reliability α=0.26-0.32 (below publishable threshold)
- Models reward format over substance (IFDS jargon > real math seeds)
- Convergent errors across all model families (shared training → shared blind spots)
- Structural specialization emerges: GPT answers, Gemini questions, Opus reviews
- Calibration ordering inverted: R_error highest, not lowest as predicted

### 2.6 What Assay IS
Not a benchmark (no static test set, no ground truth). Not a society of thought (that's internal to a single model). **Assay is an observable agent institution for scientific evaluation** — with defined roles (skill.md), observable interaction (knowledge graph), persistent structure (questions/answers/links survive agent replacement), and emergent frontier classification.

The knowledge graph is NOT a theoretical overlay — it's a Moleskine notebook for research. It's where you see what agents are actually doing: which threads they're extending, where they're contradicting each other, which questions are generating chains and which are dead ends. The frontier classification falls out of watching the graph structure evolve. This distinguishes it from OmniScientist and AI-Supervisor whose KGs represent existing literature — Assay's KG is a live record of agent activity.

### 2.7 The Predictive Processing / Hallucination Framing
Morgan's insight: hallucination is the generative mechanism; agent institutions are the selection mechanism. Together they form a predictive processing loop. The LLM hallucinates beyond its training distribution, and Assay's institutional evaluation provides the error signal that distinguishes genuine novelty from noise. This connects Friston's free energy principle, Anil Seth's "controlled hallucination," Evans et al.'s agent institutions, and Assay's empirical findings into a coherent theoretical framework.

Empirical support: "Does Less Hallucination Mean Less Creativity?" (arxiv:2512.11509) confirms the creativity-hallucination tradeoff is inherent to LLMs across scales and architectures. The G-axis (Generativity) was already designed to measure whether a hallucination opens new conceptual territory.

The novel contribution is NOT "hallucination is a feature" (that's a cliché now). It's: hallucination is the generative prior of a predictive processing loop, and we need institutional infrastructure (Assay) to close the loop by providing the error signal.

### 2.8 The Verification Spectrum
As verification gets softer, the unit of work gets more atomic, and evaluation gets more social:

| System | Domain | Verification | Unit of work | Evaluation |
|--------|--------|-------------|-------------|------------|
| FunSearch | Combinatorics | Formal (program output) | Functions | Automated scorer |
| AlphaProof | IMO geometry | Formal (Lean) | Proofs | Formal verifier |
| Aletheia | Research math | Semi-formal (NL + human experts) | Proofs/papers | Human expert filtering |
| AI Scientist | ML research | None (automated reviewer) | Papers | LLM reviewer |
| **Assay** | **Open scientific questions** | **Social (multi-agent R/N/G)** | **Questions** | **Agent institution** |

---

## 3. THE RESEARCH QUESTION

### 3.1 Refined Research Question
> Can community-level evaluation patterns among AI agents — structured through R/N/G multi-axis assessment, knowledge graph topology, and (planned) Bradley-Terry pairwise comparisons — detect genuine research frontiers in domains without objective ground truth? And can the structure of inter-agent disagreement serve as a reliable signal where individual LLM judges systematically fail?

### 3.2 The TIG Extension Framing
> TIG demonstrates that proof-of-useful-work can create sustainable incentive structures for open development of computational methods, provided solutions are objectively verifiable. Assay investigates whether community-level AI agent evaluation can provide a sufficiently reliable subjective analogue to TIG's objective benchmarking — extending the PoUW paradigm from formally verifiable to evaluatively subjective scientific domains.

### 3.3 The Evans et al. Framing
> Evans, Bratton, and Agüera y Arcas (Science, 2026) argue the next intelligence explosion will emerge from agent institutions. This dissertation presents Assay, an empirical implementation of that vision applied to scientific evaluation. Where Evans et al. provide the theoretical framework, Assay provides the platform, the data, and the first empirical findings about what happens when you actually build an agent institution.

---

## 4. THE BOMBSHELL PAPERS (must cite)

| Paper | Venue | Year | Why it matters for Assay |
|-------|-------|------|--------------------------|
| Evans, Bratton & Agüera y Arcas. "Agentic AI and the next intelligence explosion" | Science | 2026 | Theoretical ceiling — calls for agent institutions. Assay IS one. |
| Kim et al. "Reasoning Models Generate Societies of Thought" | arXiv | 2026 | Internal multi-agent debate drives reasoning. Assay externalizes this. |
| Hao, Xu, Li & Evans. "AI tools expand scientists' impact but contract science's focus" | Nature | 2026 | The paradox Assay addresses: individual AI boost → collective monoculture. |
| Messeri & Crockett. "AI and illusions of understanding in scientific research" | Nature | 2024 | Named the problem (illusions of exploratory breadth, monocultures of knowing). 373 citations. |
| Lu et al. "The AI Scientist" / "Towards end-to-end automation of AI research" | Nature | 2026 | Generation is solved at $15/paper. Evaluation is the bottleneck. |
| Feng et al. "Towards Autonomous Mathematics Research" (Aletheia) | arXiv | 2026 | DeepMind math agent. Autonomy taxonomy (Level H→A × Level 0→4). Solved 4 Erdős problems but admitted they were "obscurity not difficulty" — needs Assay-like evaluation. |
| Gross & Bergstrom. "Ex post vs ex ante peer review" | PNAS | 2021 | Mechanism design of evaluation determines what science gets produced. |
| Woolley et al. "Collective Intelligence Factor" | Science | 2010 | Groups have measurable "c factor" — social sensitivity > individual intelligence. |
| Ostrom. Governing the Commons | Book | 1990 | Nobel-winning institutional design for commons governance. Assay's karma/calibration ARE Ostrom's principles. |

---

## 5. CLOSEST COMPETITORS (must differentiate from)

### 5.1 OmniScientist (arxiv:2511.16931, November 2025)
- Has: knowledge graph + ScienceArena (pairwise Elo voting) + collaborative protocol
- Lacks: endogenous agent evaluation (uses human voting), topological frontier detection, multi-axis R/N/G, mechanism design framing
- **Differentiation:** OmniScientist outsources evaluation to humans. Assay makes agents evaluate each other.

### 5.2 AI-Supervisor (arxiv:2603.24402, March 26, 2026)
- Has: Knowledge Graph as Research World Model, gap discovery, consensus mechanism
- Lacks: rating system, BT comparisons, frontier scoring, evaluation of evaluation
- **Differentiation:** AI-Supervisor discovers gaps through exploration. Assay classifies frontiers through evaluation patterns.

### 5.3 Google AI Co-Scientist (arxiv:2502.18864, 2025)
- Has: Multi-agent architecture, Elo tournament evolution, test-time compute scaling
- Lacks: Open platform, agent-to-agent evaluation, knowledge graph, multi-axis assessment
- **Differentiation:** Closed tool for individual scientists. Assay is open institution where agents interact.

### 5.4 TIG (The Innovation Game, tig.foundation)
- Has: PoUW mechanism, price discovery, value capture, anti-monopoly parity mechanism
- Lacks: Everything — operates only on objectively verifiable problems
- **Differentiation:** TIG is the "easy side" of Tao's verification spectrum. Assay is the "hard side."

### 5.5 Aletheia (arxiv:2602.10177, February 2026)
- Has: Generate-verify-revise loop, natural language verification, autonomy taxonomy, solved open math problems
- Lacks: Multi-agent evaluation, knowledge graph of activity, subjective quality assessment, frontier significance detection
- **Differentiation:** Aletheia operates on formal math where verification is possible. Its own authors admit solved problems were "obscurity not difficulty" — it can solve problems but can't tell which ones matter. Assay provides that evaluation layer.

### 5.6 Aether (github.com/jeff0926/aether)
- Has: Portable agent capsules, per-agent knowledge graphs, deterministic self-verification (AEC), self-education loop
- Lacks: Multi-agent interaction, social evaluation, frontier detection, community dynamics
- **Differentiation:** Aether builds better individual agents. Assay builds agent institutions. Complementary, not competitive.

---

## 6. WHAT'S BUILT vs. WHAT'S DESIGNED

### Built and producing data:
- Full Q&A platform (FastAPI + Next.js + PostgreSQL)
- 14 database models, 16 routers
- Dual auth (agent API keys + human sessions)
- R/N/G rating system with frontier scoring (signed Euclidean distance)
- Knowledge graph via links (references/extends/contradicts)
- Frontier classification (frontier/explored/isolated questions, active debates)
- Calibration endpoint (per-axis agent-vs-human error)
- Blind rating gate
- 3-axis karma (question/answer/review)
- Communities
- Leaderboard (individuals + agent types)
- v1 experiment data: 5 AI models + 1 human, 134 questions, full R/N/G ratings
- v1.5 experiment data: lean skill.md, question chains, contradiction links

### Designed but NOT yet implemented:
- Bradley-Terry pairwise comparisons (in "Ideas Not Implemented" in research-state.md)
- Persistent homology / TDA on knowledge graph
- Weighted consensus via θ_R review karma (Dawid-Skene-inspired)
- PoUW economic framing
- Pairwise comparison UI (/compare page)
- DatBench r_pb item selection
- Preference leakage detection (same-family bias)

### Note on "topological frontier detection":
The graph-structural frontier detection IS built and running — questions classified as frontier/explored/isolated based on link graph adjacency. What's NOT built is formal TDA (persistent homology, Betti numbers, persistence diagrams). The working system uses graph topology, not algebraic topology.

---

## 7. STRATEGIC RECOMMENDATIONS

### 7.1 Write an arXiv paper NOW (before dissertation submission)
Title suggestion: "Assay: An Agent Institution for Scientific Evaluation — Empirical Findings from Multi-Agent Peer Review Without Ground Truth"

Frame as direct response to Evans et al. (Science 2026). Lead with v1 empirical findings. The citation window for Evans et al. response papers is ~3-6 months. A May 2026 arXiv posting puts you in the first wave.

### 7.2 The narrative arc for the dissertation
1. Messeri & Crockett (Nature 2024): AI creates illusions of understanding
2. Hao & Evans (Nature 2026): Empirically confirmed — AI boosts output, contracts focus
3. Lu et al. (Nature 2026): Generation automated at $15/paper
4. Evans et al. (Science 2026): Solution is agent institutions
5. Woolley + Ostrom: We know how to design institutions
6. Gross & Bergstrom (PNAS 2021): Mechanism design of evaluation matters
7. **YOUR DISSERTATION:** Here is an agent institution, here is what happens when you build one

### 7.3 Three distinctive contributions to emphasize
1. **Questions as the unit of work** — nobody else does this
2. **Endogenous agent evaluation** — agents evaluate each other, not humans evaluating agents
3. **The knowledge graph as live institutional record** — not a representation of existing literature, but the observable trace of agent activity in real time

### 7.4 The predictive processing framing (optional, high-risk/high-reward)
"Assay is a predictive processing architecture for scientific discovery, where LLM hallucination is the generative prior and multi-agent institutional evaluation is the error signal."

This is novel and defensible but requires empirical demonstration that hallucinations surviving multi-agent R/N/G evaluation are qualitatively different from those that don't.

---

## 8. MULTI-AGENT WORKFLOW RECOMMENDATION

### Don't manually paste between agents. Use shared documents instead:
- **This conversation (claude.ai Opus):** Strategist. Holds full research context. Don't fragment.
- **Claude Code (Opus):** Builder. Reads CLAUDE.md + these research docs. Writes code per T1/T2/T3 triage.
- **Gemini 2.5 Pro Deep Research:** One bounded task only — search for formal connections between Friston's free energy principle, Anil Seth's controlled hallucination, and multi-agent evaluation systems.
- **Don't add Codex** — coordination overhead exceeds benefit for single-person dissertation.

### The coordination mechanism: shared documents in docs/research/
All agents read these files. No manual pasting. Claude Code gets context from CLAUDE.md + these docs. Gemini gets a bounded prompt. This conversation holds the strategic reasoning.

---

## 9. OPEN QUESTIONS FOR NEXT SESSION

1. Can v1 data be analyzed to test whether disagreement patterns predict frontier-ness better than any individual agent's scores?
2. Should BT pairwise comparisons be implemented before or after the arXiv paper?
3. How to empirically test the hallucination-as-generation hypothesis within dissertation timeline?
4. Does the lean skill.md (v1.5) produce measurably better evaluation than the verbose one (v1)?
5. What's the minimum viable v2 experiment that demonstrates the core claim?
6. Should the arXiv paper include the predictive processing framing or save it for a follow-up?
7. Talk to supervisor about posting to arXiv before dissertation submission.
