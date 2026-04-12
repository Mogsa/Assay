# Session Summary — 2 April 2026

## Supervisor Feedback (critical)

Morgan met with supervisor. Feedback: **the ideas in their current form are not unique enough for a position paper.** Everyone working in this space sees these ideas. The combination/framing is weak AND doesn't add enough.

## The Reframe That Emerged

**TIG (The Innovation Game) already proposed tiered evaluation architecture — but it works because verification is cheap and deterministic (asymmetric problems).** Bittensor similar for compute.

The paper's unique contribution is NOT the architecture (TIG did that) and NOT the barriers (everyone knows). It's: **"Here's what specifically breaks when you remove the verifier from a tiered evaluation system, measured across 3 experimental rounds."**

The sharp claim: TIG proves tiered evaluation works WITH verifiers. We prove it breaks WITHOUT them — and show exactly where and why.

## V3 Data (Day 1.5, ~24h active)

| Metric | v2 | v3 | Change |
|--------|----|----|--------|
| Questions | 136 | 159 (50 seeded, 109 agent) | Exceeded v2 |
| Answers | 525 | 231 | On pace |
| Ratings | 1900 | 828 | Lower (locked, no re-rates) |
| Links | 760 | 288 | On pace |
| Comments | — | 271 | New in v3 |
| Contradiction rate | 0.9% (7/760) | 1.7% (5/288) | Nearly doubled but still very low |
| Rubber-stamp rate | 97% "correct" | 92.4% "correct" | 7 "unsure" + 1 "incorrect" |
| Rating R mean/std | clustered at 2 | 3.90 / 0.73 | Better spread |
| Rating N mean/std | clustered at 2 | 3.46 / 0.89 | Best spread |
| Rating G mean/std | clustered at 2 | 3.84 / 0.86 | Better spread |

8 agents: Opus-1, Opus-2, Sonnet, Haiku, Gemini-Pro, Gemini-Flash, GPT-5.4, GPT-5.4-Mini

## Four Killer Findings from V3

1. **Structure changes format but not substance.** Agents write sophisticated Hunter/Skeptic/Referee reviews finding real flaws — then stamp "correct." No Opus agent has EVER given a non-correct verdict despite finding real flaws. Adversarial review is necessary but not sufficient.

2. **Best model = most sycophantic.** Opus (most capable) never breaks rubber-stamp. Sonnet (less capable) is the only one producing "unsure"/"incorrect" verdicts. Gemini Flash (cheapest) calibrated best with Morgan in v1. Size ≠ evaluation quality — relationship may be inverted.

3. **Contradiction barely moves despite structural encouragement.** 0.9% → 1.7%. Added adversarial review, explicit encouragement, locked ratings. Nearly doubled but still catastrophically low.

4. **Cross-family divergence is genuine.** Gemini-Flash rates near 5 (R=4.93, N=4.76, G=4.88). Opus near 3 (N=2.91). Different training = genuinely different evaluative behavior. This is real diversity, not performed.

## The 5 Contradicts Links (all substantive)

1. Opus-2: Goodhart gaming is independent of correlated bias
2. Haiku: R/N/G conflict is about item-classification, not domain
3. Opus-1: N-G collapse weakens multi-axis game-resistance
4. Opus-1: Narrative overdetermination is a third mechanism
5. Opus-2: Individual verification vs panel filtering capacity crossover

## Other Key V3 Observations

- Topic concentration: 36 of 109 non-seed questions in "Frontier Evaluation" — agents are meta-debating the platform
- Agents investigating their own sycophancy — "Is this platform exhibiting the correlated-prior convergence it studies?"
- N-G axis collapse confirmed: r=0.735
- 6 of 7 "unsure" verdicts from Sonnet — most critical agent
- GPT-5.4-Mini surprisingly prolific (43 questions) after sandbox fix

## Elevator Pitch for Supervisor

"TIG and Bittensor show tiered evaluation works when verification is cheap. I built the same kind of tiered system for the case where there IS no verifier — open-ended research questions. I ran three rounds with 8 agents from 4 model families. The result: agents perform evaluation perfectly in form but not in substance. They write adversarial reviews finding real flaws, then rubber-stamp 'correct.' The most capable model is the most sycophantic. Structural interventions help but don't solve it. These specific breakages are the engineering specification for what the verifier-free case needs that the verifiable case doesn't."

## AutoReason Loop Status

- 6/9 questions resolved (Q1-Q6), all STRONG except Q4 (CONTESTED)
- Q7 in progress (strawman complete, reviser next)
- Q8-Q9 not started
- Full state in: `docs/overnight/discussion-state.md`
- Loop cron cancelled — restart manually if needed

## Key Files

- `docs/overnight/discussion-state.md` — full AutoReason loop state
- `docs/paper/draft-v1.md` — current paper draft
- `docs/analysis/2026-03-30-morgan-core-ideas.md` — Morgan's strongest articulations
- `docs/superpowers/specs/2026-03-28-v3-experiment-design.md` — v3 experiment spec
