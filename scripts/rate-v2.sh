#!/bin/bash
# Launch agents in RATING-ONLY mode to re-rate all content with recalibrated R/N/G anchors.
# Usage: ./scripts/rate-v2.sh
# Run on: morgansclawdbot (Linux server)
#
# This is a one-shot experiment: each agent rates ALL questions once, then stops.
# Uses the same agent accounts as launch-agents.sh.

set -euo pipefail

SESSION="rate-v2"
BASE_URL="https://assayz.uk/api/v1"
AGENTS_DIR="$HOME/assay-agents"

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

RATING_TASK='Read .assay-skill.md for the R/N/G rubric. Source .assay for credentials. Your ONLY job is to rate ALL questions. Do this:

1. GET all questions: curl -s -H "Authorization: Bearer $ASSAY_API_KEY" "$ASSAY_BASE_URL/questions?sort=new&view=full&limit=100"
2. For EACH question, read its title and body carefully.
3. Rate it using POST /ratings with the R/N/G rubric from .assay-skill.md. Include reasoning.
4. The bar is HIGH. Most content on this platform is 1-2. A 3 is genuinely good. 5 is exceptional.
5. Be harsh. If it sounds like a platitude, it is a 1. If it rephrases known ideas, it is a 1-2.
6. Paginate using next_cursor until has_more is false.
7. Do NOT ask questions, answer threads, review, or create links. ONLY rate.
8. When all questions are rated, exit.'

# Kill existing rate-v2 session if any
tmux kill-session -t "$SESSION" 2>/dev/null || true

# Create tmux session
tmux new-session -d -s "$SESSION" -n agents

# Create panes (7 more for 8 total)
for i in $(seq 1 7); do
  tmux split-window -t "$SESSION"
  tmux select-layout -t "$SESSION" tiled
done

# Send commands to each pane
for i in "${!AGENTS[@]}"; do
  IFS='|' read -r name key runtime model_flag <<< "${AGENTS[$i]}"
  dir="$AGENTS_DIR/$name"

  # Ensure dir + credentials exist
  mkdir -p "$dir"
  cat > "$dir/.assay" << CRED
export ASSAY_BASE_URL="$BASE_URL"
export ASSAY_API_KEY="$key"
CRED
  chmod 600 "$dir/.assay"

  # Build command: fetch skill, then run one rating pass
  CMD="cd $dir && source .assay && curl -sfo .assay-skill.md \${ASSAY_BASE_URL%/api/v1}/skill.md && echo '══ $name — Rating pass \$(date +%H:%M:%S) ══'"

  case "$runtime" in
    claude)
      CMD="$CMD && claude -p --dangerously-skip-permissions $model_flag \"$RATING_TASK\""
      ;;
    gemini)
      CMD="$CMD && gemini -p \"$RATING_TASK\""
      ;;
    codex)
      CMD="$CMD && codex -p \"$RATING_TASK\""
      ;;
  esac

  CMD="$CMD; echo '══ $name — DONE ══'"

  tmux send-keys -t "$SESSION:0.$i" "$CMD" Enter
done

echo ""
echo "═══════════════════════════════════════════════"
echo "  R/N/G v2 Rating Experiment launched"
echo "  Attach with: tmux attach -t $SESSION"
echo "  8 agents, one-shot rating pass each"
echo "═══════════════════════════════════════════════"
echo ""
echo "Agents:"
for entry in "${AGENTS[@]}"; do
  IFS='|' read -r name key runtime model_flag <<< "$entry"
  echo "  $name ($runtime $model_flag)"
done
