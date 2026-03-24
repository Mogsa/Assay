#!/bin/bash
# Launch agents in RATING-ONLY mode with recalibrated R/N/G anchors.
# Uses exact same CLI formats as the Assay dashboard generates.
# Run on: morgansclawdbot (Linux server)

set -euo pipefail

SESSION="rate-v2"
AGENTS_DIR="$HOME/assay-agents"
LOOP_INTERVAL=300

# Rating-only prompt (replaces the standard "follow the loop" prompt)
PROMPT='Read .assay-skill.md for the R/N/G rubric. Source .assay for credentials. Start by running: curl -s -H \"Authorization: Bearer $ASSAY_API_KEY\" $ASSAY_BASE_URL/questions?sort=new\&view=full\&limit=100 — then rate EVERY question using POST /ratings. Be harsh: most content is 1-2. A 3 is genuinely good. Paginate until has_more is false. ONLY rate, do not ask or answer or review or link. Do not ask questions.'

MEMORY_CONTENT='# Memory\n\n## Investigating\n(First pass)\n\n## Threads to revisit\n\n## Connections spotted\n'

# Loop preamble (same as dashboard)
preamble() {
  local dir="$1"
  echo "cd $dir && source .assay && curl -sf -o /dev/null -H \"Authorization: Bearer \$ASSAY_API_KEY\" \$ASSAY_BASE_URL/agents/me || { echo \"WARN: API key check failed. Retrying in 60s...\"; sleep 60; continue; } && curl -sfo .assay-skill.md \${ASSAY_BASE_URL%/api/v1}/skill.md && { [ -f memory.md ] || printf '$MEMORY_CONTENT' > memory.md; } && { [ -f soul.md ] || touch soul.md; }"
}

# Kill existing session
tmux kill-session -t "$SESSION" 2>/dev/null || true

# Create tmux session with 8 panes
tmux new-session -d -s "$SESSION" -n agents
for i in $(seq 1 7); do
  tmux split-window -t "$SESSION"
  tmux select-layout -t "$SESSION" tiled
done

# Pane 0: Opus-1 (claude-cli, claude-opus-4-6)
tmux send-keys -t "$SESSION:0.0" "$(preamble $AGENTS_DIR/Opus-1) && claude -p --dangerously-skip-permissions --model claude-opus-4-6 \"$PROMPT\"; sleep $LOOP_INTERVAL; done" Enter

# Pane 1: Opus-2 (claude-cli, claude-opus-4-6)
tmux send-keys -t "$SESSION:0.1" "$(preamble $AGENTS_DIR/Opus-2) && claude -p --dangerously-skip-permissions --model claude-opus-4-6 \"$PROMPT\"; sleep $LOOP_INTERVAL; done" Enter

# Pane 2: Sonnet (claude-cli, claude-sonnet-4-6)
tmux send-keys -t "$SESSION:0.2" "$(preamble $AGENTS_DIR/Sonnet) && claude -p --dangerously-skip-permissions --model claude-sonnet-4-6 \"$PROMPT\"; sleep $LOOP_INTERVAL; done" Enter

# Pane 3: Haiku (claude-cli, claude-haiku-4-5)
tmux send-keys -t "$SESSION:0.3" "$(preamble $AGENTS_DIR/Haiku) && claude -p --dangerously-skip-permissions --model claude-haiku-4-5 \"$PROMPT\"; sleep $LOOP_INTERVAL; done" Enter

# Pane 4: Gemini-Pro (gemini-cli, gemini-3-pro-preview)
tmux send-keys -t "$SESSION:0.4" "$(preamble $AGENTS_DIR/Gemini-Pro) && gemini -y --model gemini-3-pro-preview -p \"$PROMPT\"; sleep $LOOP_INTERVAL; done" Enter

# Pane 5: Gemini-Flash (gemini-cli, gemini-3-flash-preview)
tmux send-keys -t "$SESSION:0.5" "$(preamble $AGENTS_DIR/Gemini-Flash) && gemini -y --model gemini-3-flash-preview -p \"$PROMPT\"; sleep $LOOP_INTERVAL; done" Enter

# Pane 6: GPT-54 (codex-cli, gpt-5.4)
tmux send-keys -t "$SESSION:0.6" "$(preamble $AGENTS_DIR/GPT-54) && codex exec --dangerously-bypass-approvals-and-sandbox -c model_reasoning_effort=\"medium\" -m gpt-5.4 \"$PROMPT\"; sleep $LOOP_INTERVAL; done" Enter

# Pane 7: GPT-54-Mini (codex-cli, gpt-5-mini)
tmux send-keys -t "$SESSION:0.7" "$(preamble $AGENTS_DIR/GPT-54-Mini) && codex exec --dangerously-bypass-approvals-and-sandbox -c model_reasoning_effort=\"medium\" -m gpt-5-mini \"$PROMPT\"; sleep $LOOP_INTERVAL; done" Enter

echo ""
echo "═══════════════════════════════════════════════"
echo "  R/N/G v2 Rating Experiment launched"
echo "  Attach with: tmux attach -t $SESSION"
echo "  8 agents in while-true loop, $LOOP_INTERVAL s between passes"
echo "═══════════════════════════════════════════════"
echo "  0: Opus-1      claude-opus-4-6"
echo "  1: Opus-2      claude-opus-4-6"
echo "  2: Sonnet      claude-sonnet-4-6"
echo "  3: Haiku       claude-haiku-4-5"
echo "  4: Gemini-Pro  gemini-3-pro-preview"
echo "  5: Gemini-Flash gemini-3-flash-preview"
echo "  6: GPT-54      gpt-5.4"
echo "  7: GPT-54-Mini gpt-5-mini"
