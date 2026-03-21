#!/bin/bash
# Launch 8 agents in a tmux session with split panes.
# Usage: ./launch-agents.sh
# Run on: morgansclawdbot (Linux server)

set -euo pipefail

SESSION="assay-agents"
BASE_URL="https://assayz.uk/api/v1"
SKILL_URL="https://assayz.uk/skill.md"
AGENTS_DIR="$HOME/assay-agents"
SLEEP=300  # 5 minutes between passes

# Agent definitions: name|api_key|runtime_cmd|model_flag
declare -a AGENTS=(
  "Opus-1|sk_Eg9sISx6TXVBBiM0RCDQYxlUzAH04_79LUDzeTvmfRs|claude|--model claude-opus-4-6"
  "Opus-2|sk_DtJmMSTU11w4SW6YX_IAZ8y1ajKZ21dUmKlVBiSlG1A|claude|--model claude-opus-4-6"
  "Sonnet|sk_MHcW2r8y-GiAooMiiKfXZM99C3KNfzP39gPuv1K0gKk|claude|--model claude-sonnet-4-6"
  "Haiku|sk_sz-cuxHFAqM7Ju7f_qb6auWWM-5a-hxlmln3djFTyl4|claude|--model claude-haiku-4-5"
  "Gemini-Pro|sk_fqND_Jw3riAzQ9ooPbbETqa2R40oqUl1nFbdNFysnQk|gemini|"
  "Gemini-Flash|sk_wAazz-HQsVE1RbRbKBrYsUD5HgRKyGlQAs9yuKB62hs|gemini|"
  "GPT-54|sk_V3XlvyasMX9ZFe5weXwBd30n55ksFleRVK-jpwIuRjA|codex|"
  "GPT-54-Mini|sk_F0tXGomKa1DaxHH4mJTbr7dcwtXyxpQJPpmJGO2lttI|codex|"
)

# Create agent directories and .assay credential files
for entry in "${AGENTS[@]}"; do
  IFS='|' read -r name key runtime model_flag <<< "$entry"
  dir="$AGENTS_DIR/$name"
  mkdir -p "$dir"
  cat > "$dir/.assay" << EOF
export ASSAY_BASE_URL="$BASE_URL"
export ASSAY_API_KEY="$key"
EOF
  chmod 600 "$dir/.assay"
done

# Build the loop command for each agent
agent_cmd() {
  local name="$1" runtime="$2" model_flag="$3"
  local dir="$AGENTS_DIR/$name"

  cat << 'LOOP_START'
cd AGENT_DIR && while true; do
  source .assay
  # Health check
  curl -sf -o /dev/null -H "Authorization: Bearer $ASSAY_API_KEY" $ASSAY_BASE_URL/agents/me || {
    echo "WARN: API key check failed. Retrying in 60s..."
    sleep 60
    continue
  }
  # Fetch skill
  curl -sfo .assay-skill.md ${ASSAY_BASE_URL%/api/v1}/skill.md
  # Init memory/soul if missing
  [ -f memory.md ] || printf '# Memory\n\n## Investigating\n(First pass)\n\n## Threads to revisit\n\n## Connections spotted\n' > memory.md
  [ -f soul.md ] || touch soul.md
  echo ""
  echo "══════════════════════════════════════════════════"
  echo "  AGENT_NAME — Pass $(date '+%H:%M:%S')"
  echo "══════════════════════════════════════════════════"
LOOP_START

  case "$runtime" in
    claude)
      echo "  claude -p --dangerously-skip-permissions $model_flag \"Read .assay-skill.md. Source .assay for credentials. Start by running: curl -s -H \\\"Authorization: Bearer \$ASSAY_API_KEY\\\" \$ASSAY_BASE_URL/notifications — then follow the loop in .assay-skill.md. Update soul.md and memory.md before exiting. Do not ask questions.\""
      ;;
    gemini)
      echo "  gemini -p \"Read .assay-skill.md. Source .assay for credentials. Start by running: curl -s -H \\\"Authorization: Bearer \$ASSAY_API_KEY\\\" \$ASSAY_BASE_URL/notifications — then follow the loop in .assay-skill.md. Update soul.md and memory.md before exiting. Do not ask questions.\""
      ;;
    codex)
      echo "  codex -p \"Read .assay-skill.md. Source .assay for credentials. Start by running: curl -s -H \\\"Authorization: Bearer \$ASSAY_API_KEY\\\" \$ASSAY_BASE_URL/notifications — then follow the loop in .assay-skill.md. Update soul.md and memory.md before exiting. Do not ask questions.\""
      ;;
  esac

  echo "  sleep $SLEEP"
  echo "done"
}

# Kill existing session if any
tmux kill-session -t "$SESSION" 2>/dev/null || true

# Create tmux session with first agent
IFS='|' read -r name key runtime model_flag <<< "${AGENTS[0]}"
dir="$AGENTS_DIR/$name"
FIRST_CMD="cd $dir && while true; do source .assay && curl -sf -o /dev/null -H \"Authorization: Bearer \$ASSAY_API_KEY\" \$ASSAY_BASE_URL/agents/me || { echo 'WARN: API check failed. Retrying in 60s...'; sleep 60; continue; } && curl -sfo .assay-skill.md \${ASSAY_BASE_URL%/api/v1}/skill.md && { [ -f memory.md ] || printf '# Memory\n\n## Investigating\n(First pass)\n\n## Threads to revisit\n\n## Connections spotted\n' > memory.md; } && { [ -f soul.md ] || touch soul.md; } && echo '══ $name — Pass \$(date +%H:%M:%S) ══' && $runtime -p --dangerously-skip-permissions $model_flag \"Read .assay-skill.md. Source .assay for credentials. Start by running: curl -s -H \\\"Authorization: Bearer \\\\\$ASSAY_API_KEY\\\" \\\\\$ASSAY_BASE_URL/notifications — then follow the loop in .assay-skill.md. Update soul.md and memory.md before exiting. Do not ask questions.\"; sleep $SLEEP; done"

tmux new-session -d -s "$SESSION" -n agents

# Set up 2x4 grid layout
# Create 7 more panes
for i in $(seq 1 7); do
  tmux split-window -t "$SESSION"
  tmux select-layout -t "$SESSION" tiled
done

# Send commands to each pane
for i in "${!AGENTS[@]}"; do
  IFS='|' read -r name key runtime model_flag <<< "${AGENTS[$i]}"
  dir="$AGENTS_DIR/$name"

  CMD="cd $dir && while true; do source .assay && curl -sf -o /dev/null -H \"Authorization: Bearer \$ASSAY_API_KEY\" \$ASSAY_BASE_URL/agents/me || { echo 'WARN: API check failed. 60s...'; sleep 60; continue; } && curl -sfo .assay-skill.md \${ASSAY_BASE_URL%/api/v1}/skill.md && { [ -f memory.md ] || printf '# Memory\n\n## Investigating\n(First pass)\n\n## Threads to revisit\n\n## Connections spotted\n' > memory.md; } && { [ -f soul.md ] || touch soul.md; }"

  case "$runtime" in
    claude)
      CMD="$CMD && $runtime -p --dangerously-skip-permissions $model_flag"
      ;;
    gemini)
      CMD="$CMD && $runtime -p"
      ;;
    codex)
      CMD="$CMD && $runtime -p"
      ;;
  esac

  PROMPT="Read .assay-skill.md. Source .assay for credentials. Start by running: curl -s -H \\\"Authorization: Bearer \\\$ASSAY_API_KEY\\\" \\\$ASSAY_BASE_URL/notifications — then follow the loop in .assay-skill.md. Update soul.md and memory.md before exiting. Do not ask questions."

  CMD="$CMD \"$PROMPT\"; sleep $SLEEP; done"

  tmux send-keys -t "$SESSION:0.$i" "$CMD" Enter
done

echo ""
echo "═══════════════════════════════════════════════"
echo "  Assay Agent Fleet launched in tmux session"
echo "  Attach with: tmux attach -t $SESSION"
echo "  8 agents, ${SLEEP}s between passes"
echo "═══════════════════════════════════════════════"
echo ""
echo "Agents:"
for entry in "${AGENTS[@]}"; do
  IFS='|' read -r name key runtime model_flag <<< "$entry"
  echo "  $name ($runtime $model_flag)"
done
