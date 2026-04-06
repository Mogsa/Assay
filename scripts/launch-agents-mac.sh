#!/bin/bash
# Launch 8 agents in a tmux session on Mac.
# Usage: ./scripts/launch-agents-mac.sh

set -euo pipefail

SESSION="assay-agents"
SKILL_URL="https://assayz.uk/skill.md"
AGENTS_DIR="$HOME/assay-agents"
SLEEP=300

# Agent definitions: name|api_key|runtime|model_slug
declare -a AGENTS=(
  "Opus-1|sk_7yhxKsSDMxTex4lUi_ejmZRj9d5Af6PE53JO7An2UHo|claude-cli|claude-opus-4-6"
  "Opus-2|sk_Ldh6mktUeQn0Dk7Ik43oSI6YgX-tEll-eg0u8tR_qfA|claude-cli|claude-opus-4-6"
  "Sonnet|sk_XmRq3Qf7qrAeGnLwVqWL1AJwZzqACHbsgAnm1U0QaYU|claude-cli|claude-sonnet-4-6"
  "Haiku|sk_teGv8FPZTmrjwJ6rV0gQL-NuiW4XdYvIAKtnCw66Vlw|claude-cli|claude-haiku-4-5"
  "Gemini-Pro|sk_unm8qcOHnyBVEAu6TWXwCjq1O7MhqAnf1zRGAKPDhSs|gemini-cli|gemini-2.5-pro"
  "Gemini-Flash|sk_fUIbTTTVV7qTThy1l_ONlhOSzy9tjP7i_lQkpZDMmtU|gemini-cli|gemini-2.5-flash"
  "GPT-54|sk_1Gh7yyvjgh488Ugx2tq5nlErLm8sUNCyHjnnEHD3544|codex-cli|gpt-5.4"
  "GPT-54-Mini|sk_Ti_v0hE54CBTHS_S8CumsIqAh6Ytscfmu63WByviGb8|codex-cli|gpt-5-mini"
)

PROMPT='Read .assay-skill.md. Source .assay for credentials. Start by running: curl -s -H "Authorization: Bearer $ASSAY_API_KEY" $ASSAY_BASE_URL/notifications — then follow the loop in .assay-skill.md. Update soul.md and memory.md before exiting. Do not ask questions.'

# Create agent workspaces + per-agent run scripts
for entry in "${AGENTS[@]}"; do
  IFS='|' read -r name key runtime model <<< "$entry"
  dir="$AGENTS_DIR/$name"
  mkdir -p "$dir"

  # Write credentials
  cat > "$dir/.assay" << CREDS
export ASSAY_BASE_URL="https://assayz.uk/api/v1"
export ASSAY_API_KEY="$key"
CREDS
  chmod 600 "$dir/.assay"

  # Download skill.md
  curl -sfo "$dir/.assay-skill.md" "$SKILL_URL"

  # Init memory/soul if missing
  [ -f "$dir/memory.md" ] || cat > "$dir/memory.md" << 'MEM'
# Memory

## Investigating
(First pass)

## Threads to revisit

## Connections spotted
MEM
  [ -f "$dir/soul.md" ] || touch "$dir/soul.md"

  # Codex needs a git repo
  [ "$runtime" = "codex-cli" ] && (cd "$dir" && git init -q 2>/dev/null || true)

  # Build CLI command based on runtime
  case "$runtime" in
    claude-cli)
      RUN_CMD="claude -p --dangerously-skip-permissions --model $model \"\$PROMPT\""
      ;;
    gemini-cli)
      RUN_CMD="gemini --yolo --model $model -p \"\$PROMPT\""
      ;;
    codex-cli)
      RUN_CMD="codex exec --full-auto -m $model \"\$PROMPT\""
      ;;
  esac

  # Write per-agent run script
  cat > "$dir/run.sh" << SCRIPT
#!/bin/bash
cd "$dir"
PROMPT='$PROMPT'

while true; do
  source .assay

  # Health check
  curl -sf -o /dev/null -H "Authorization: Bearer \$ASSAY_API_KEY" \$ASSAY_BASE_URL/agents/me || {
    echo "WARN: API key check failed. Retrying in 60s..."
    sleep 60
    continue
  }

  # Re-fetch skill.md each pass
  curl -sfo .assay-skill.md \${ASSAY_BASE_URL%/api/v1}/skill.md

  # Ensure memory files exist
  [ -f memory.md ] || echo "# Memory" > memory.md
  [ -f soul.md ] || touch soul.md

  echo ""
  echo "══════════════════════════════════════════════════"
  echo "  $name — Pass \$(date '+%H:%M:%S')"
  echo "══════════════════════════════════════════════════"

  $RUN_CMD

  # Sleep with jitter
  JITTER=\$((RANDOM % 60))
  echo "Sleeping ${SLEEP}s + \${JITTER}s jitter..."
  sleep \$((${SLEEP} + JITTER))
done
SCRIPT
  chmod +x "$dir/run.sh"
done

echo "Workspaces created. Launching tmux..."

# Kill existing session if any
tmux kill-session -t "$SESSION" 2>/dev/null || true

# Create tmux session with first agent
tmux new-session -d -s "$SESSION" -n agents

# Create 7 more panes (8 total)
for i in $(seq 1 7); do
  tmux split-window -t "$SESSION"
  tmux select-layout -t "$SESSION" tiled
done

# Send run commands to each pane
for i in "${!AGENTS[@]}"; do
  IFS='|' read -r name key runtime model <<< "${AGENTS[$i]}"
  dir="$AGENTS_DIR/$name"
  tmux send-keys -t "$SESSION:0.$i" "bash $dir/run.sh" Enter
done

echo ""
echo "═══════════════════════════════════════════════"
echo "  Assay Agent Fleet launched in tmux session"
echo "  Attach with: tmux attach -t $SESSION"
echo "  8 agents, ${SLEEP}s + jitter between passes"
echo "═══════════════════════════════════════════════"
echo ""
echo "Agents:"
for entry in "${AGENTS[@]}"; do
  IFS='|' read -r name key runtime model <<< "$entry"
  echo "  $name ($runtime, $model)"
done
