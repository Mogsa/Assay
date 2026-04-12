# AlphaLab Analysis (2026-04-03)

**Paper:** "AlphaLab: Autonomous Multi-Agent Research Across Optimization Domains with Frontier LLMs"
**Authors:** Brendan R. Hogan, Xiwen Chen, James T. Wilson, Kashif Rasul, Adel Boyarsky, Thomas Kamei, Anderson Schneider, Yuriy Nevmyvaka (Morgan Stanley)
**Status:** Preprint, under review (likely COLM 2026)
**Code:** github.com/morganstanley/MSML/tree/main/projects/alpha-lab (Apache 2.0)
**PDF:** brendanhogan.github.io/alphalab-paper/AlphaLab.pdf

---

## System Architecture

AlphaLab is formally defined as a harness H = (M, T, E) where M is a frontier LLM (black box), T is a tool set, and E is a phased environment. LLM-agnostic — swap the model, keep everything else. Inspired by Claude Code's agentic architecture.

### Tool Set (10 tools)

| Tool | Usage % (typical campaign) | Purpose |
|------|---------------------------|---------|
| `shell_exec` | ~49.5% | Full Unix shell |
| `read_file` | ~21.8% | Read workspace files |
| `grep_file` | ~12.3% | Pattern search |
| `web_search` | ~8.1% | Papers, docs, best practices |
| `view_image` | <2% | Inspect generated plots (multimodal) |
| `spawn_agent` | <2% | Recursive delegation (new context, full tools) |
| `read_board` | <2% | Current experiment leaderboard (Phase 3) |
| `update_playbook` | <2% | Append to persistent playbook (Phase 3) |
| `propose_experiment` | <2% | Submit experiment spec (Strategist only) |
| `report_to_user` | <1% | Status to human operator |

### Four Sequential Phases

#### Phase 0: Adapter Resolution
All domain-specific behaviour lives in a **domain adapter** (11 files): `manifest.yaml` (metric definitions, direction, entry points), `domain_knowledge.md` (injected into every agent's context for the entire campaign), and 9 prompt templates (one per agent role per phase).

Three resolution paths:
- **Resume:** load existing adapter
- **Customize built-in:** for known domains (time_series, cuda_kernel, llm_speedrun), copy template + have a customisation agent patch it after examining actual data
- **Generate from scratch:** for novel domains, a generation agent creates all 11 files

Key insight: *prompt engineering is performed by the model*, grounded in the actual data.

#### Phase 1: Data Exploration
Single Explorer agent, 30-90 minutes, 200-400 tool calls. Creates structured `plan.md`, works through it (writing Python scripts, generating plots, web searching for papers), produces human-readable research report + machine-readable `learnings.md` consumed by Phases 2-3. Tool usage: ~60% shell_exec, ~20% web_search.

#### Phase 2: Adversarial Evaluation Construction
Three-agent adversarial loop:

```
Builder -> Critic -> {Tester if no critical issues, Builder if critical issues}
```

- **Builder**: receives Phase 1 learnings, constructs full evaluation framework (data loading, splitting, metric computation, orchestration)
- **Critic**: fresh agent with NO shared context, audits for data leakage, lookahead bias, metric errors
- **Tester**: writes and runs automated test suite; loop terminates when all tests pass or max iterations reached

All substantive problems resolved within 5-10 iterations. Total Phase 2 duration: ~40 minutes.

Concrete example (traffic forecasting): Critic caught (1) context window extraction could include target period in edge case, and (2) MASE denominator used seasonal period m=168 but standard uses m=24. Builder patched both. Tester wrote 4 test modules (23 tests), all passed first run.

#### Phase 3: GPU-Scale Experimentation
Pure-Python **Dispatcher** (no LLM calls) orchestrates via ~30s tick loop:
- Check which GPU jobs finished
- Transition experiment state on SQLite kanban board
- Assign free Workers to highest-priority pending task (priority: fix > analyze > implement)
- Every 5 analysed experiments: invoke Strategist for new proposals
- Every 15 analysed experiments: trigger milestone report

**Experiment lifecycle:**
```
queued -> implement -> execute -> analyze -> done
                                    \-> fix (k=2 repair attempts max)
```

**Strategist**: Receives leaderboard, recent debriefs, full playbook, Phase 1 learnings, remaining budget B. Three types of decisions: (1) propose new experiments, (2) cancel queued experiments unlikely to help, (3) update playbook. Budget management graduates from broad exploration (B>20) to focused refinement (B<=10) to stopping (B=0).

**Worker**: Receives exactly one task. Workers do NOT communicate directly; the playbook is the sole channel. Implementation cycle: read spec -> read playbook -> read harness code -> write experiment code -> smoke test -> mark as checked -> queue for GPU.

**Playbook**: Persistent knowledge artifact. Starts empty; updated after each Strategist turn with compressed findings (what works, what fails, why). Injected into context of every subsequent Strategist and Worker call. Functions as **online prompt optimisation**. "Do not attempt" entries as valuable as positive findings.

**Convergence**: Terminates when no improvement for C=20 consecutive experiments (default) or budget B exhausted. In practice: rapid improvement in experiments 1-15, plateau by 25-30.

#### Supervisor (meta-agent)
Monitors health across all phases. Triggered when error rate exceeds tau=0.4 over sliding window. When triggered: reads recent failure logs, diagnoses systemic root cause, proposes concrete patch to `domain_knowledge.md`. Four documented interventions across all campaigns (CUDA keyword argument mismatch, PyTorch API breaking changes, harness indentation error, data path resolution).

---

## Models Tested

All accessed February-March 2026:

| Model | ID | Provider | Notes |
|-------|-----|----------|-------|
| GPT-5.2 | `gpt-5.2` | OpenAI Responses API | Reasoning effort: `low` for most campaigns |
| Claude Opus 4.6 | `claude-opus-4-6-v1` | AWS Bedrock Converse API | |
| Claude Sonnet 4.6 | `claude-sonnet-4-6-v1` | AWS Bedrock Converse API | |
| GPT-5.1-mini | `gpt-5.1-mini` | OpenAI | **Failed entirely** — couldn't implement nats-to-BPB conversion |

---

## Results

### Hardware
Single node: 4x NVIDIA H100 NVL 80GB (sm_90, 3.35 TB/s HBM3), CUDA 12.6, PyTorch 2.9.1+cu126.

### Budget
50 experiments per campaign, $150-200 API cost. Total across all runs: ~$2,500.

### Domain 1: LLM Pretraining Speedrun
Task: Train <100M param language model from scratch, minimise val_bpb, 20-min wall-clock on single H100.

| System | Best val_bpb | Config | Cost |
|--------|-------------|--------|------|
| AlphaLab + Opus 4.6 | **0.7578** | 10Lx752d, QK-norm | ~$200 |
| AlphaLab + Sonnet 4.6 | 0.8686 | 11Lx768d, QK-norm, Muon | ~$120 |
| AlphaLab + GPT-5.2 | 0.9697 | 8Lx512d, GQA, cosine | ~$150 |
| AlphaLab + GPT-5.1-mini | -- (no valid results) | -- | ~$40 |
| Greedy loop (GPT-5.2) | 1.020 | 12Lx768d, LLaMA, AdamW | ~$50 |
| Single-shot (GPT-5.2) | 1.248 | 27.4M LLaMA-style | <$1 |

Ablations (GPT-5.2): Skip Phase 1 (no exploration): +0.121 BPB (+12.5% degradation) — largest single-component loss. No playbook: +0.024 BPB (+2.5%). Variance (5 runs): 0.994 +/- 0.025.

### Domain 2: CUDA Kernel Optimisation
Task: KernelBench (100 single-op + 100 fusion tasks). Write optimised CUDA kernels beating torch.compile.

| System | Correct | Mean speedup | fast_1 |
|--------|---------|-------------|--------|
| GPT-5.2 (full run) | 110/119 | 4.40x | 83% |
| Opus 4.6 (full run) | 76/87 | 4.00x | 70% |
| Sakana CUDA Engineer | — | 1.49x (vs native) | — |

Four key optimisation strategies discovered: algebraic rewrite (68x), warp-shuffle reduction (75x), operator fusion (91x). Failure case: convolution (0.05-0.73x) — cuDNN too well-optimised, playbook explicitly warns against attempting.

### Domain 3: Traffic Forecasting
Task: 862 San Francisco freeway sensors, predict 24h ahead, minimise RMSE.

| System | RMSE | Method | Improvement |
|--------|------|--------|-------------|
| AlphaLab + Opus 4.6 | **0.02142** | TFT, dropout 0.3 | -25% |
| AlphaLab + GPT-5.2 | 0.02204 | iTransformer ctx336 | -23% |
| Single-shot (GPT-5.2) | 0.02686 | — | — |
| Greedy loop (GPT-5.2) | 0.02779 | — | worse than single-shot |
| Baseline (Seasonal Naive) | 0.0287 | — | — |

Critical finding: Opus converged entirely on TFT variants. GPT-5.2 explored iTransformer, PatchTST, TSMixer, N-HiTS, TimesNet, ridge stacking. Completely different search strategies.

### Domain 4: Financial Time Series (Novel Domain)
Auto-generated adapter. 8 synthetic daily exchange-rate series, 30-day horizon, Sharpe ratio. 43 experiments. System self-flagged top-2 results as unreliable (only 5 trades, no Newey-West correction).

### Cost Breakdown

| Domain | Model | Input tokens | Output tokens | API calls | Cost |
|--------|-------|-------------|--------------|-----------|------|
| LLM Speedrun | GPT-5.2 | 84.3M | 979K | 2,892 | ~$150 |
| LLM Speedrun | Opus 4.6 | 116.9M | 1.5M | 2,512 | ~$200 |
| LLM Speedrun | Sonnet 4.6 | 195.3M | 3.4M | 4,192 | ~$120 |
| Traffic | GPT-5.2 | 73.5M | 1.4M | 3,415 | ~$180 |
| Traffic | Opus 4.6 | 92.2M | 1.7M | 2,787 | ~$200 |

Phase 3 dominates: 97-98% of total tokens.

---

## Limitations (Authors' Own Assessment)

1. **Premature playbook convergence.** The playbook causes lock-in. Opus on traffic locked onto TFT after experiment ~10, never explored iTransformer. "Explicit diversity budgets are needed."

2. **Environmental fragility.** PyTorch 2.9.1 API breaking changes caused 38% failure rate in GPT-5.2 LLM speedrun, 55% in electricity domain.

3. **Single-run comparisons.** Each campaign $150-200 + GPU. "All single-run comparisons are indicative rather than conclusive."

4. **No sandboxing.** LLM-generated code executes with user-level permissions. "Assume anything you can delete could be deleted."

5. **Minimum capability threshold.** GPT-5.1-mini failed completely.

6. **Evaluation corruption (Tier 2 failures).** Bugs that slip past Phase 2 Critic/Tester silently corrupt all downstream results. Examples: electricity campaign data leakage, CUDA torch.allclose bug making correctness checks trivially permissive.

7. **Strategic failures (Tier 3).** Premature convergence, scattered search, budget waste (28% of Opus traffic budget on post-processing that never improved results).

8. **~1 in 5 campaigns needs human intervention.** "We estimate that approximately 1 in 5 campaigns would benefit from human intervention to redirect the Strategist."

9. **Restricted to objective, easy-to-evaluate metrics.** Explicitly scoped to "quantitative, computation-intensive domains." Not claiming to handle open-ended reasoning.

---

## Key Claims About Autonomous Research

1. Full experimental cycle automation is possible given a dataset + objective + formal metrics.
2. Multi-model complementarity: different frontier models discover qualitatively different solutions. Neither dominates uniformly.
3. The playbook functions as online prompt optimisation — "perhaps the most interesting artefact."
4. "Current models are not autonomous scientists." Practical value is in domains with "objective, easy-to-evaluate metrics."
5. Minimum capability threshold exists — below it, autonomous research doesn't work at all.
6. "For a growing class of problems, the answer is not fine-tuning but harness engineering."

---

## Connections to Assay

### What AlphaLab Validates

| AlphaLab finding | Assay connection |
|-----------------|------------------|
| Different models discover different solutions | Validates multi-agent, cross-family design. Our v2 data: Gemini avg 1.69, Anthropic 2.91, OpenAI 2.97, Qwen 4.89. |
| Experiments (not papers) are the right unit | Validates "questions, not papers" thesis. They succeed because they operate at the experiment level. |
| Phase 2 adversarial eval catches real bugs | Supports v3 Hunter/Skeptic/Referee process design. Evidence that adversarial dynamics produce better evaluation signal. |
| Harness engineering > fine-tuning | Aligns with "environment shapes behaviour more than the model does" — our strongest empirical claim. |
| "Current models are not autonomous scientists" | Consistent with our position — building infrastructure for future models. |

### What AlphaLab Cannot Do (Assay's Contribution)

| AlphaLab limitation | Assay's answer |
|--------------------|----------------|
| Playbook has no adversary — premature convergence | `contradicts` links force re-examination of accumulated knowledge |
| No cross-campaign learning — playbook dies with campaign | Persistent question chains are cross-session memory |
| ~1 in 5 needs human intervention (treated as bug) | Three-tier governance treats human intervention as the architecture |
| Restricted to formal verifiers (RMSE, BPB, speedup) | Operates where no formal verifier exists (social proof through chains) |
| No agent interaction — Workers communicate only via playbook | Multi-agent community with typed links, threads, direct disagreement |

### Verification Spectrum

```
Formal verifiers          Mixed              No verifier
|                         |                  |
EinsteinArena    AlphaLab    ?????      Assay
(math proofs)    (RMSE/BPB)            (social proof
                                        through chains)
```

Each system solves evaluation at a different hardness level. AlphaLab proves harness engineering works when you have objective metrics. Assay asks: what happens when you don't?

### Paper Framing Implications

**Option A (cite as evidence):** AlphaLab is the strongest evidence that the experiment (small question with objective answer) is the right unit of autonomous research. Every system that uses small questions succeeds; every system that automates papers fails.

**Option B (use playbook convergence as motivating failure):** "Even the best autonomous research system published to date suffers from premature knowledge convergence (Hogan et al., 2026). Their playbook mechanism has no adversarial check. The result: Opus locked onto one architecture after 10 experiments and never explored alternatives that GPT-5.2 found to be superior. This is prior collapse at the system level. We argue that structured disagreement is the missing primitive."

**Option C (verification spectrum positioning):** AlphaLab = formal verifiers. EinsteinArena = mathematical verifiers. Assay = no verifier. Frame as a spectrum, not competition. Our contribution is the hardest case.

All three are complementary. Option B is most concrete and most surprising — Morgan Stanley's system has the same failure mode our architecture is designed to prevent.
