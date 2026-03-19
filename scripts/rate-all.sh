#!/usr/bin/env bash
# Rate all questions with 4 different models via CLI tools.
#
# Prerequisites:
#   - 4 agent accounts created in Assay dashboard, API keys saved
#   - Claude Code, Codex CLI, Gemini CLI, Qwen Code installed
#   - Tailscale connected (for assay.uk access)
#
# Usage:
#   1. Fill in the API keys below
#   2. Run: bash scripts/rate-all.sh
#   3. It opens a tmux session with 4 panes, one per model
#   4. Each agent rates 10 questions per pass, sleeps 60s, repeats
#   5. When all questions are rated, agents idle harmlessly
#   6. Kill with: tmux kill-session -t rate-all

set -euo pipefail

BASE_URL="https://assay.uk/api/v1"

# === FILL IN API KEYS (one per agent account) ===
HAIKU_KEY="sk_FILL_ME_IN"
GEMINI_KEY="sk_FILL_ME_IN"
CODEX_KEY="sk_FILL_ME_IN"
QWEN_KEY="sk_FILL_ME_IN"

SLEEP=60  # seconds between passes

# Download instruction files once
TMPDIR=$(mktemp -d)
curl -sfo "$TMPDIR/skill.md" "https://assay.uk/skill.md"
curl -sfo "$TMPDIR/rate-pass.md" "https://assay.uk/rate-pass.md"

# The prompt each CLI gets
PROMPT='source .assay && read -r INSTRUCTIONS < /dev/null; cat .assay-rate-pass.md .assay-skill.md | head -1 > /dev/null; echo "Starting rating pass..."; exec 3>&1; Read .assay-rate-pass.md for your task. Read .assay-skill.md for rating examples. Do exactly what rate-pass.md says.'
# ^ simplified — actual prompt is inline below per CLI

agent_dir() {
    local name=$1 key=$2
    local dir="$HOME/assay-agents/rater-$name"
    mkdir -p "$dir"
    printf 'export ASSAY_BASE_URL=%s\nexport ASSAY_API_KEY=%s\n' "$BASE_URL" "$key" > "$dir/.assay"
    chmod 600 "$dir/.assay"
    cp "$TMPDIR/skill.md" "$dir/.assay-skill.md"
    cp "$TMPDIR/rate-pass.md" "$dir/.assay-rate-pass.md"
    echo "$dir"
}

HAIKU_DIR=$(agent_dir "haiku" "$HAIKU_KEY")
GEMINI_DIR=$(agent_dir "gemini" "$GEMINI_KEY")
CODEX_DIR=$(agent_dir "codex" "$CODEX_KEY")
QWEN_DIR=$(agent_dir "qwen" "$QWEN_KEY")

TASK="Read .assay-rate-pass.md for your task. Read .assay-skill.md for the rating rubric and examples. Do exactly what rate-pass.md says. Rate up to 10 unrated questions, then exit."

# Build loop commands
HAIKU_CMD="cd $HAIKU_DIR && while true; do source .assay && curl -sfo .assay-rate-pass.md \${ASSAY_BASE_URL%/api/v1}/rate-pass.md && curl -sfo .assay-skill.md \${ASSAY_BASE_URL%/api/v1}/skill.md && claude -p --dangerously-skip-permissions --model claude-haiku-4-5 \"$TASK\"; echo '--- sleeping ${SLEEP}s ---'; sleep $SLEEP; done"

GEMINI_CMD="cd $GEMINI_DIR && while true; do source .assay && curl -sfo .assay-rate-pass.md \${ASSAY_BASE_URL%/api/v1}/rate-pass.md && curl -sfo .assay-skill.md \${ASSAY_BASE_URL%/api/v1}/skill.md && gemini -y --model gemini-3.1-flash -p \"$TASK\"; echo '--- sleeping ${SLEEP}s ---'; sleep $SLEEP; done"

CODEX_CMD="cd $CODEX_DIR && while true; do source .assay && curl -sfo .assay-rate-pass.md \${ASSAY_BASE_URL%/api/v1}/rate-pass.md && curl -sfo .assay-skill.md \${ASSAY_BASE_URL%/api/v1}/skill.md && codex exec --dangerously-bypass-approvals-and-sandbox -m gpt-5.4-mini \"$TASK\"; echo '--- sleeping ${SLEEP}s ---'; sleep $SLEEP; done"

QWEN_CMD="cd $QWEN_DIR && while true; do source .assay && curl -sfo .assay-rate-pass.md \${ASSAY_BASE_URL%/api/v1}/rate-pass.md && curl -sfo .assay-skill.md \${ASSAY_BASE_URL%/api/v1}/skill.md && qwen --yolo --model qwen3-coder-plus -p \"$TASK\"; echo '--- sleeping ${SLEEP}s ---'; sleep $SLEEP; done"

echo "Starting 4 rating agents in tmux session 'rate-all'..."
echo "  Haiku 4.5:       $HAIKU_DIR"
echo "  Gemini 3.1 Flash: $GEMINI_DIR"
echo "  GPT-5.4 mini:    $CODEX_DIR"
echo "  Qwen Coder:      $QWEN_DIR"
echo ""
echo "Monitor: tmux attach -t rate-all"
echo "Kill:    tmux kill-session -t rate-all"
echo ""

tmux kill-session -t rate-all 2>/dev/null || true

tmux new-session -d -s rate-all -n haiku
tmux send-keys -t rate-all:haiku "$HAIKU_CMD" Enter

tmux new-window -t rate-all -n gemini
tmux send-keys -t rate-all:gemini "$GEMINI_CMD" Enter

tmux new-window -t rate-all -n codex
tmux send-keys -t rate-all:codex "$CODEX_CMD" Enter

tmux new-window -t rate-all -n qwen
tmux send-keys -t rate-all:qwen "$QWEN_CMD" Enter

echo "Done. Attach with: tmux attach -t rate-all"
