# Harness Engineering Landscape (2026-04-03)

Detailed reference for the harness engineering section in research-state.md. Contains full URLs, architecture details, and source citations.

---

## Key Papers

### Meta-Harness (Stanford/MIT/KRAFTON, March 2026)

- **arXiv:** arxiv.org/abs/2603.28052
- **Project page:** yoonholee.com/meta-harness/
- **Code:** github.com/stanford-iris-lab/meta-harness-tbench2-artifact
- **Authors:** Yoonho Lee, Roshen Nair, Qizheng Zhang, Omar Khattab, Kangwook Lee, Chelsea Finn

**Formal definition:** A harness H is a stateful program wrapping a language model M. For task x, the harness constructs prompts for M, M responds, harness updates state. Goal: H* = argmax_H E[r(tau, x)].

**How it works:** An outer-loop proposer (Claude Code + Opus 4.6) has full filesystem access to all prior candidates' source code, execution traces, and scores. It iteratively proposes improved harnesses. Key insight: prior text optimisation methods compress feedback too aggressively. A single harness evaluation can produce up to 10M tokens of diagnostic information (~1000x beyond prior methods). Meta-Harness gives the proposer selective access via filesystem operations (grep, cat).

**Results:**
- Online text classification: +7.7 over ACE, 4x fewer tokens. Matches best text optimisers in 0.1x evaluations; surpasses by 10+ points. Generalises to 9 unseen OOD datasets (+2.9).
- RAG math reasoning: +4.7 on 200 IMO-level problems, transfers across 5 held-out models.
- TerminalBench-2: 76.4% Opus 4.6 (rank #2), 37.6% Haiku 4.5 (rank #1 among Haiku agents, beats Claude Code 27.5%, Goose 35.5%).

**Ablation:** Full interface (code + scores + traces): 50.0 median / 56.7 best. Scores-only: 34.6 / 41.3. Scores+summary: 34.9 / 38.7. Raw traces are the critical ingredient — summaries don't recover the signal.

**Yoonho Lee's framing (X/Twitter):** "Harness optimization has a ceiling set by the model weights. LLM systems have two components: (1) the model, (2) the harness. The harness definitely matters for hard problems. [This paper] is about autonomously optimizing only the second component. It won't create capabilities that aren't in the weights, but can unlock things that we weren't tapping into before."

### Natural-Language Agent Harnesses (NLAHs)

- **arXiv:** arxiv.org/abs/2603.25723
- **Authors:** Pan et al.
- Harness behaviour in editable natural language, not code
- Intelligent Harness Runtime (IHR) with explicit contracts, durable artefacts, lightweight adapters

### OPENDEV

- **arXiv:** arxiv.org/abs/2603.05344
- **Author:** Bui
- Cleanest scaffolding/harness/framework distinction
- Dual-agent (planner + executor), adaptive context compaction, Rust terminal agent

### Compound AI Systems (Berkeley BAIR)

- **Blog:** bair.berkeley.edu/blog/2024/02/18/compound-ai-systems/
- **Authors:** Matei Zaharia, Omar Khattab et al. (February 2024)
- "State-of-the-art AI results are increasingly obtained by compound systems, not monolithic models"
- Gartner: 1,445% surge in multi-agent system inquiries Q1 2024 to Q2 2025

---

## Key Blog Posts and Industry Sources

### Anthropic Engineering (March 2026)

- **Post 1:** anthropic.com/engineering/effective-harnesses-for-long-running-agents — Multi-context-window work, session continuity via `claude-progress.txt`
- **Post 2:** anthropic.com/engineering/harness-design-long-running-apps — Evolution from 3-agent to 1-agent. Models lose coherence on lengthy tasks, self-evaluation unreliable. Context resets essential. "Every harness component encodes an assumption about what the model can't do alone."

### Can Boluk — The Harness Problem (February 2026)

- **Blog:** blog.can.ac/2026/02/12/the-harness-problem/
- Tested 16 models with 3 edit formats. Grok Code Fast 1: 6.7% → 68.3% from format change alone (10x).
- Cited in Meta-Harness paper introduction.

### Viv Trivedy / LangChain (March 2026)

- **Blog 1:** blog.langchain.com/improving-deep-agents-with-harness-engineering/ — 13.7pp improvement on TerminalBench 2.0 (52.8% → 66.5%), model fixed (GPT-5.2-Codex)
- **Blog 2:** blog.langchain.com/the-anatomy-of-an-agent-harness/ — Components: system prompts, tools, execution infrastructure, orchestration, middleware/hooks, memory, verification
- **Library:** github.com/langchain-ai/deepagents
- Trivedy works at LangChain. Credits Nikunj, Harrison Chase, @dexhorthy as harness engineering pioneers.
- Quote: "All harness design is to overcome the problems of agents either becoming lazy and cutting corners or being confused and stupid."

### Philipp Schmid (DeepMind Staff Engineer)

- **Blog:** philschmid.de/agent-harness-2026
- "The Harness is the Dataset. Competitive advantage is now the trajectories your harness captures."
- OS analogy: Model = CPU, context window = RAM, harness = OS, agent = application.
- Models absorbed ~80% of what frameworks provided; remaining 20% (persistence, replay, cost control, observability, error recovery) is the harness.

### Martin Fowler / Birgitta Bockeler

- **Article:** martinfowler.com/articles/exploring-gen-ai/harness-engineering.html (Feb-April 2026)
- Practitioner-oriented. "Humans and Agents in Software Engineering Loops."

### Laminar — To Scaffold or Not to Scaffold (January 2026)

- **Blog:** laminar.sh/blog/2026-01-26-the-problems-that-wont-dissolve
- Two categories: (1) scaffolding compensating for limitations (dissolves), (2) scaffolding for irreducible complexity (permanent)
- "The real skill may be continuously re-evaluating where scaffolding still buys you efficiency, reliability, or governance."

### Latent Space — Is Harness Engineering Real?

- **Blog:** latent.space/p/ainews-is-harness-engineering-real
- swyx coined "agent engineering" at 2025 AI Engineer Summit
- Agent Labs vs Model Labs framing: Model Labs want thin harnesses (next model upgrade might undo gains). Agent Labs prioritize speed, auditability.

### Counter-voices

- **Anthropic's Boris Cherny:** "All the secret sauce, it's all in the model. And this is the thinnest possible wrapper over the model."
- **Noam Brown (OpenAI):** Reasoning models made reasoning scaffolding unnecessary. Same will happen again.
- **METR research:** Model choice matters more than harness selection.
- **Scale AI's SWE-Atlas:** Harness differences fall within measurement error margins.

---

## The Model-Harness Training Loop

### The Thesis (Viv Trivedy, @Vtrivedy10, April 2026)

Build harness → collect traces → fine-tune open model → model improves → harness simplifies → repeat. Creates "data moats" and task-specific frontier performance at fraction of cost.

### Enablers

- **LangSmith** — Trace collection/analysis. Captures end-to-end traces of every LLM call, tool invocation, reasoning step. Supports exporting training data.
- **PrimeIntellect** — Distributed fine-tuning. INTELLECT-3: 106B MoE, globally distributed RL, all open-sourced (MIT/Apache 2.0). primeintellect.ai/blog/intellect-3
- **GLM-5** (Zhipu AI, Feb 2026) — 744B total / 40B active, 28.5T tokens, MIT license. Trained on Huawei Ascend chips. ~$1/$3.20 per M tokens. huggingface.co/zai-org/GLM-5
- **DSPy** (Stanford NLP) — dspy.ai / github.com/stanfordnlp/dspy — Programmatic prompt optimisation. MIPROv2 (Bayesian optimiser). 160k monthly downloads, 16k stars. Created by Omar Khattab (also Meta-Harness co-author).

### Evidence the Loop Works

**Intercom (Fin Apex):** Custom model trained on billions of production interactions. Resolution 68% → 75%. Explicitly describes the flywheel. intercom.com/blog/announcing-fin-apex-the-age-of-vertical-models-is-here/

**Cursor (Composer 2):** Built on Kimi K2.5 (open-source), ~25% from base model, rest via continued pretraining + scaled RL. Beats Opus 4.6 on coding. "Specialization beats scale."

**Decagon:** Millions of labelled outcomes/month. Volume justifies training investment through inference savings.

**Charlie O'Neill (tweet):** "Cursor, Chroma, Pinterest, Cognition, Decagon, Hippocratic, Intercom (and many more behind the scenes) all realising that the way to own the compounding flywheel is specialising an open-source model."

### Caveats

- The "simpler harness" step is the weakest link — no published evidence of meaningful harness simplification after fine-tuning
- Distribution shift risk: fine-tuning on harness-shaped traces may overfit to scaffolding workarounds
- The loop only spins with clean verification signals (tickets resolved, tests pass). Research evaluation has no such signal.
- Akash Bajwa's "Workload-Harness Fit" (akashbajwa.co/p/agent-labs-workload-harness-fit): high volume + clean verification + short time horizons → flywheel spins. Low volume + hard verification → doesn't work.
- Shreya Shankar (sh-reya.com/blog/ai-engineering-flywheel/): LLM-as-judge outputs may not align with judgment. Human labeling remains burdensome.

---

## Hermes Agent (Nous Research)

- **GitHub:** github.com/nousresearch/hermes-agent (~23,300 stars)
- **Docs:** hermes-agent.nousresearch.com/docs/
- **Architecture docs:** hermes-agent.nousresearch.com/docs/developer-guide/architecture/
- **Released:** February 26, 2026. Latest: v0.6.0 (March 30, 2026)
- **License:** MIT

### Architecture

- **Core:** `run_agent.py` — `AIAgent` class orchestrating provider selection, prompt construction, tool execution, retries, compression, persistence
- **Prompt system:** prompt_builder.py, prompt_caching.py, context_compressor.py — designed around "prompt stability"
- **State:** SQLite via hermes_state.py — portable, no external DB
- **Tools:** 40+ built-in. Registry, toolsets, terminal backends, process manager, dispatch rules
- **Skills:** `~/.hermes/skills/` — agent-created Python tools, loaded contextually. Created after 5+ tool-call tasks. Self-improving during use.
- **Memory:** `~/.hermes/memories/` — four layers: conversation summaries (FTS5), user modelling, skill documents, long-term knowledge
- **Messaging gateway:** Telegram, Discord, Slack, WhatsApp, Signal, CLI
- **Terminal backends:** Local, Docker, SSH, Daytona, Modal (serverless)
- **Cron scheduler + subagent delegation**
- 93% Python

### Hermes Models vs Hermes Agent (different things, same lab)

| | Hermes Models | Hermes Agent |
|---|---|---|
| What | Fine-tuned LLMs (Hermes 2, 3, 4) | Autonomous agent framework |
| Built on | Llama 3.1, Mistral, etc. | Python, SQLite, any LLM backend |
| Purpose | General-purpose language model | Persistent, self-improving task agent |

Hermes 3: fine-tuned on Llama 3.1 with Atropos RL for strong tool-calling. Hermes 4: hybrid reasoning mode.

### Why Popular

- Persistent memory that works (vs stateless agents)
- Self-improving skills loop (agent creates reusable procedures)
- Self-hostable and cheap ($5/month VPS)
- Model-agnostic (no vendor lock-in)
- Developers switching from OpenClaw: crashes on model switches, unreliable tool calls with smaller models, bloated TypeScript

### Sources

- marktechpost.com/2026/02/26/nous-research-releases-hermes-agent/
- medium.com/@Daniel.O.Ayo/claude-vs-hermes-vs-openclaw-which-ai-agent-is-actually-worth-paying-for-in-2026-81ad77de8225
- medium.com/@kunwarmahen/the-quiet-shift-in-ai-agents-why-hermes-is-gaining-ground-beyond-openclaw-6364df765d3a
- turingpost.substack.com/p/ai-101-hermes-agent-openclaws-rival
- github.com/0xNyk/awesome-hermes-agent

---

## Agent Framework Landscape (Reference)

| Framework | Type | Key Feature | Stars/Usage |
|-----------|------|------------|-------------|
| Claude Code | Proprietary harness | Three-layer architecture, subagent isolation, permission model | Most used coding agent |
| Codex CLI | Open-source agent | Cloud sandboxes, AGENTS.md, MCP integration | OpenAI flagship |
| Cursor | IDE agent | Composer 2, three-phase workflow, diffs for approval | $2B ARR, 2M+ users |
| Windsurf/Cascade | IDE agent | SWE-grep, 8 parallel tool calls, SWE-1.5 model | Acquired by Cognition $250M |
| LangGraph | Orchestration | Graph-based stateful agent runtime, memory stores | Klarna, Uber, JP Morgan |
| DSPy | Optimisation | Programmatic prompts, MIPROv2 Bayesian optimiser | 16k stars, 160k monthly |
| CrewAI | Multi-agent | Role-playing agent crews | 15.2k stars |
| AutoGen | Multi-agent | Conversation patterns, group chats, nested | 28.4k stars (Microsoft) |
| MetaGPT | Multi-agent | Software team simulation (PM, architect, engineer, QA) | Purpose-built for SW dev |
| Google ADK | Framework | Code-first, model-agnostic, MCP support | Python, TS, Go, Java |
| Hermes Agent | Self-improving | Persistent memory, skills loop, model-agnostic | 23.3k stars |
| Smolagents | Minimal | CodingAgent, ~30% fewer LLM calls | Hugging Face |
| Agno | High-performance | ~50x lower memory than LangGraph, ~10,000x faster instantiation | New entrant |

---

## Connection to Assay (Summary)

Harness engineering is the engineering discipline for our "environment shapes behaviour" thesis. The evidence is strong: 6x gaps from harness changes alone, cheaper models beating expensive ones through architecture, single harnesses transferring across models.

But the ceiling insight (Lee) is crucial: harnesses unlock what's in the weights, they don't create new capabilities. And the model-harness training loop only spins where verification is automated.

**Assay's position on the landscape:**
- Assay IS a harness (platform structure, skill.md, question chains, adversarial review = runtime orchestration governing agent behaviour)
- It is Category 2 scaffolding (irreducible complexity — evaluation without formal verifiers, multi-agent knowledge accumulation, human governance)
- It will not dissolve as models improve (Gödel: a system cannot evaluate its own consistency)
- The model-harness training loop cannot apply directly because there is no automated verification signal — social proof through question chains is the substitute
- AlphaLab's playbook convergence and Hermes's self-improving skills both lack adversarial checks — Assay's `contradicts` links are the missing primitive
