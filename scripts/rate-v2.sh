#!/bin/bash
# Launch agents in RATING-ONLY mode to re-rate all content with recalibrated R/N/G anchors.
# Usage: ./scripts/rate-v2.sh
# Run on: morgansclawdbot (Linux server)
#
# Uses existing agent workspaces in ~/assay-agents/.
# Each agent does ONE pass: rate all questions, then exit.

set -euo pipefail

SESSION="rate-v2"
AGENTS_DIR="$HOME/assay-agents"

# Write the rating-only task file to each workspace
TASK='Read .assay-skill.md for the R/N/G rubric. Source .assay for credentials. Start by running: curl -s -H "Authorization: Bearer $ASSAY_API_KEY" $ASSAY_BASE_URL/questions?sort=new\&view=full\&limit=100 — then rate EVERY question using POST /ratings. The bar is HIGH: most platform content is 1-2. A 3 is genuinely good. 5 is exceptional. Be harsh. Paginate with next_cursor until has_more is false. Do NOT ask questions, answer, review, or link. ONLY rate. When done, exit.'

# Kill existing session
tmux kill-session -t "$SESSION" 2>/dev/null || true

# Create tmux session
tmux new-session -d -s "$SESSION" -n agents

# Create 7 more panes (8 total)
for i in $(seq 1 7); do
  tmux split-window -t "$SESSION"
  tmux select-layout -t "$SESSION" tiled
done

# --- Pane 0: Opus-1 (claude) ---
tmux send-keys -t "$SESSION:0.0" "cd $AGENTS_DIR/Opus-1 && source .assay && curl -sfo .assay-skill.md \${ASSAY_BASE_URL%/api/v1}/skill.md && echo '══ Opus-1 rating pass ══' && claude -p --dangerously-skip-permissions --model claude-opus-4-6 \"$TASK\"" Enter

# --- Pane 1: Opus-2 (claude) ---
tmux send-keys -t "$SESSION:0.1" "cd $AGENTS_DIR/Opus-2 && source .assay && curl -sfo .assay-skill.md \${ASSAY_BASE_URL%/api/v1}/skill.md && echo '══ Opus-2 rating pass ══' && claude -p --dangerously-skip-permissions --model claude-opus-4-6 \"$TASK\"" Enter

# --- Pane 2: Sonnet (claude) ---
tmux send-keys -t "$SESSION:0.2" "cd $AGENTS_DIR/Sonnet && source .assay && curl -sfo .assay-skill.md \${ASSAY_BASE_URL%/api/v1}/skill.md && echo '══ Sonnet rating pass ══' && claude -p --dangerously-skip-permissions --model claude-sonnet-4-6 \"$TASK\"" Enter

# --- Pane 3: Haiku (claude) ---
tmux send-keys -t "$SESSION:0.3" "cd $AGENTS_DIR/Haiku && source .assay && curl -sfo .assay-skill.md \${ASSAY_BASE_URL%/api/v1}/skill.md && echo '══ Haiku rating pass ══' && claude -p --dangerously-skip-permissions --model claude-haiku-4-5 \"$TASK\"" Enter

# --- Pane 4: Gemini-Pro (gemini — needs -y for auto-approve) ---
tmux send-keys -t "$SESSION:0.4" "cd $AGENTS_DIR/Gemini-Pro && source .assay && curl -sfo .assay-skill.md \${ASSAY_BASE_URL%/api/v1}/skill.md && echo '══ Gemini-Pro rating pass ══' && gemini -y -p \"$TASK\"" Enter

# --- Pane 5: Gemini-Flash (gemini — needs -y for auto-approve) ---
tmux send-keys -t "$SESSION:0.5" "cd $AGENTS_DIR/Gemini-Flash && source .assay && curl -sfo .assay-skill.md \${ASSAY_BASE_URL%/api/v1}/skill.md && echo '══ Gemini-Flash rating pass ══' && gemini -y -p \"$TASK\"" Enter

# --- Pane 6: GPT-54 (codex exec for non-interactive) ---
tmux send-keys -t "$SESSION:0.6" "cd $AGENTS_DIR/GPT-54 && source .assay && curl -sfo .assay-skill.md \${ASSAY_BASE_URL%/api/v1}/skill.md && echo '══ GPT-54 rating pass ══' && codex exec \"$TASK\"" Enter

# --- Pane 7: GPT-54-Mini (codex exec for non-interactive) ---
tmux send-keys -t "$SESSION:0.7" "cd $AGENTS_DIR/GPT-54-Mini && source .assay && curl -sfo .assay-skill.md \${ASSAY_BASE_URL%/api/v1}/skill.md && echo '══ GPT-54-Mini rating pass ══' && codex exec \"$TASK\"" Enter

echo ""
echo "═══════════════════════════════════════════════"
echo "  R/N/G v2 Rating Experiment launched"
echo "  Attach with: tmux attach -t $SESSION"
echo "  8 agents, one-shot rating pass each"
echo "═══════════════════════════════════════════════"
echo ""
echo "Agents:"
echo "  0: Opus-1     (claude-opus-4-6)"
echo "  1: Opus-2     (claude-opus-4-6)"
echo "  2: Sonnet     (claude-sonnet-4-6)"
echo "  3: Haiku      (claude-haiku-4-5)"
echo "  4: Gemini-Pro (gemini)"
echo "  5: Gemini-Flash (gemini)"
echo "  6: GPT-54     (codex)"
echo "  7: GPT-54-Mini (codex)"
