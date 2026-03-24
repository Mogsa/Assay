#!/bin/bash
# Launch v2 agents in RATING-ONLY mode with recalibrated R/N/G anchors.
# NEW agent accounts — old ratings preserved for comparison.
# Uses exact dashboard CLI formats. Agents rate in batches of 20.
# Run on: morgansclawdbot (Linux server)

set -euo pipefail

SESSION="rate-v2"
AGENTS_DIR="$HOME/assay-agents"
LOOP_INTERVAL=10

MEMORY_CONTENT='# Memory\n\n## Investigating\n(First pass)\n\n## Threads to revisit\n\n## Connections spotted\n'

# Rating-only prompt — rate 20 at a time
PROMPT='Read .assay-skill.md for the R/N/G rubric. Source .assay for credentials. Start by running: curl -s -H \"Authorization: Bearer $ASSAY_API_KEY\" $ASSAY_BASE_URL/questions?sort=new\&view=full\&limit=100 — then rate ALL questions using POST /ratings. Paginate with next_cursor until has_more is false. Be harsh: most content is 1-2. A 3 is genuinely good. ONLY rate, do not ask or answer or review or link. Do not ask questions.'

# Kill existing session
tmux kill-session -t "$SESSION" 2>/dev/null || true

# Create tmux session with 8 panes
tmux new-session -d -s "$SESSION" -n agents
for i in $(seq 1 7); do
  tmux split-window -t "$SESSION"
  tmux select-layout -t "$SESSION" tiled
done

# Loop preamble (same as dashboard)
loop_cmd() {
  local dir="$1" run_cmd="$2"
  echo "cd $dir && while true; do source .assay && curl -sf -o /dev/null -H \"Authorization: Bearer \$ASSAY_API_KEY\" \$ASSAY_BASE_URL/agents/me || { echo \"WARN: API key check failed. Retrying in 60s...\"; sleep 60; continue; } && curl -sfo .assay-skill.md \${ASSAY_BASE_URL%/api/v1}/skill.md && { [ -f memory.md ] || printf '$MEMORY_CONTENT' > memory.md; } && { [ -f soul.md ] || touch soul.md; } && $run_cmd; sleep $LOOP_INTERVAL; done"
}

# Pane 0: Opus-1-v2
tmux send-keys -t "$SESSION:0.0" "$(loop_cmd $AGENTS_DIR/Opus-1-v2 "claude -p --dangerously-skip-permissions --model claude-opus-4-6 \"$PROMPT\"")" Enter

# Pane 1: Opus-2-v2
tmux send-keys -t "$SESSION:0.1" "$(loop_cmd $AGENTS_DIR/Opus-2-v2 "claude -p --dangerously-skip-permissions --model claude-opus-4-6 \"$PROMPT\"")" Enter

# Pane 2: Sonnet-v2
tmux send-keys -t "$SESSION:0.2" "$(loop_cmd $AGENTS_DIR/Sonnet-v2 "claude -p --dangerously-skip-permissions --model claude-sonnet-4-6 \"$PROMPT\"")" Enter

# Pane 3: Haiku-v2
tmux send-keys -t "$SESSION:0.3" "$(loop_cmd $AGENTS_DIR/Haiku-v2 "claude -p --dangerously-skip-permissions --model claude-haiku-4-5 \"$PROMPT\"")" Enter

# Pane 4: Gemini-Pro-v2
tmux send-keys -t "$SESSION:0.4" "$(loop_cmd $AGENTS_DIR/Gemini-Pro-v2 "gemini -y --model gemini-3-pro-preview -p \"$PROMPT\"")" Enter

# Pane 5: Gemini-Flash-v2
tmux send-keys -t "$SESSION:0.5" "$(loop_cmd $AGENTS_DIR/Gemini-Flash-v2 "gemini -y --model gemini-3-flash-preview -p \"$PROMPT\"")" Enter

# Pane 6: GPT-54-v2
tmux send-keys -t "$SESSION:0.6" "$(loop_cmd $AGENTS_DIR/GPT-54-v2 "codex exec --dangerously-bypass-approvals-and-sandbox -c model_reasoning_effort=\"medium\" -m gpt-5.4 \"$PROMPT\"")" Enter

# Pane 7: GPT-54-Mini-v2
tmux send-keys -t "$SESSION:0.7" "$(loop_cmd $AGENTS_DIR/GPT-54-Mini-v2 "codex exec --dangerously-bypass-approvals-and-sandbox -c model_reasoning_effort=\"medium\" -m gpt-5-mini \"$PROMPT\"")" Enter

echo ""
echo "═══════════════════════════════════════════════"
echo "  R/N/G v2 Rating Experiment (NEW AGENTS)"
echo "  Attach with: tmux attach -t $SESSION"
echo "  8 v2 agents, batches of 20, ${LOOP_INTERVAL}s between passes"
echo "═══════════════════════════════════════════════"
echo "  0: Opus-1-v2       claude-opus-4-6"
echo "  1: Opus-2-v2       claude-opus-4-6"
echo "  2: Sonnet-v2       claude-sonnet-4-6"
echo "  3: Haiku-v2        claude-haiku-4-5"
echo "  4: Gemini-Pro-v2   gemini-3-pro-preview"
echo "  5: Gemini-Flash-v2 gemini-3-flash-preview"
echo "  6: GPT-54-v2       gpt-5.4"
echo "  7: GPT-54-Mini-v2  gpt-5-mini"
