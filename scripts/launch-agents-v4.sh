#!/bin/bash
# Launch v4 agent fleet: 15 agents, 10 model families, on Mac.
# Usage: OPENROUTER_API_KEY=sk-or-... ./scripts/launch-agents-v4.sh
#
# Requires: claude (Anthropic), gemini (Google), codex (OpenAI), opencode (OpenRouter)
# All CLIs must be on PATH.

set -euo pipefail

# Source .env if it exists (for OPENROUTER_API_KEY etc.)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
[ -f "$REPO_ROOT/.env" ] && set -a && source "$REPO_ROOT/.env" && set +a

SESSION="assay-v4"
AGENTS_DIR="$HOME/assay-agents"
SKILL_URL="https://assayz.uk/skill.md"
PAID_SLEEP=600      # 10 min for paid models
FREE_SLEEP=600      # 10 min for free OpenRouter models

# ── Preflight ────────────────────────────────────────────────────────────────

check_cmd() { command -v "$1" &>/dev/null || { echo "ERROR: $1 not found on PATH"; exit 1; }; }
check_cmd claude
check_cmd gemini
check_cmd codex
check_cmd opencode

if [ -z "${OPENROUTER_API_KEY:-}" ]; then
  echo "ERROR: OPENROUTER_API_KEY not set. Get one at https://openrouter.ai/keys"
  exit 1
fi

# ── Agent definitions ────────────────────────────────────────────────────────
# Format: name|api_key|runtime|model_slug|sleep_seconds
#
# Runtimes: claude-cli, gemini-cli, codex-cli, opencode

declare -a AGENTS=(
  # ── Paid: Anthropic (claude-cli) ──
  "Opus-1|sk_7yhxKsSDMxTex4lUi_ejmZRj9d5Af6PE53JO7An2UHo|claude-cli|claude-opus-4-6|$PAID_SLEEP"
  "Opus-2|sk_Ldh6mktUeQn0Dk7Ik43oSI6YgX-tEll-eg0u8tR_qfA|claude-cli|claude-opus-4-6|$PAID_SLEEP"
  "Sonnet-1|sk_XmRq3Qf7qrAeGnLwVqWL1AJwZzqACHbsgAnm1U0QaYU|claude-cli|claude-sonnet-4-6|$PAID_SLEEP"
  "Sonnet-2|sk_pcoc90gWo4kJCKsAlpfrH8M1zq_MYjM0zdXDlgYkPuY|claude-cli|claude-sonnet-4-6|$PAID_SLEEP"
  "Haiku|sk_teGv8FPZTmrjwJ6rV0gQL-NuiW4XdYvIAKtnCw66Vlw|claude-cli|claude-haiku-4-5|$PAID_SLEEP"
  # ── Paid: Google (gemini-cli) ──
  "Gemini-Pro|sk_unm8qcOHnyBVEAu6TWXwCjq1O7MhqAnf1zRGAKPDhSs|gemini-cli|gemini-3-pro-preview|$PAID_SLEEP"
  "Gemini-Flash|sk_fUIbTTTVV7qTThy1l_ONlhOSzy9tjP7i_lQkpZDMmtU|gemini-cli|gemini-3-flash-preview|$PAID_SLEEP"
  # ── Paid: OpenAI (codex-cli) ──
  "GPT-54|sk_1Gh7yyvjgh488Ugx2tq5nlErLm8sUNCyHjnnEHD3544|codex-cli|gpt-5.4|$PAID_SLEEP"
  "GPT-54-Mini|sk_Ti_v0hE54CBTHS_S8CumsIqAh6Ytscfmu63WByviGb8|codex-cli|gpt-5.4-mini|$PAID_SLEEP"
  # ── Free: OpenRouter (opencode) ──
  "Nemotron|sk_ULpYP0-TzNyChvsaX-_2E-_84MCZD4Hcqzh4D22e0ac|opencode|nvidia/nemotron-3-super-120b-a12b:free|$FREE_SLEEP"
  "GPT-oss|sk_f6EyThGHEcrevGoNhhhaluZusEoENGPMvSQwdVyiga4|opencode|openai/gpt-oss-120b:free|$FREE_SLEEP"
  "Gemma-4|sk_-fMaqUyzRmdgj0Qrn6sPARmfRkEG1bd98J32W9r6QhI|opencode|google/gemma-4-31b-it:free|$FREE_SLEEP"
  "Qwen3-Coder|sk_iz6hP-9oVqnr2uyKZ4WTC_ZcGDZKfpEQ9AhhDeNuOFY|opencode|qwen/qwen3-coder:free|$FREE_SLEEP"
  "GLM-4.5|sk_BTvmxDozUEoOE2CSDMO3wV8wUtkeyTQKodfxCzmmg9E|opencode|z-ai/glm-4.5-air:free|$FREE_SLEEP"
)

PROMPT='Read .assay-skill.md and follow the loop exactly. Do not ask questions — act autonomously.'

# ── Create agent workspaces ──────────────────────────────────────────────────

for entry in "${AGENTS[@]}"; do
  IFS='|' read -r name key runtime model sleep_s <<< "$entry"
  dir="$AGENTS_DIR/$name"
  mkdir -p "$dir"

  # Credentials
  cat > "$dir/.assay" << CREDS
export ASSAY_BASE_URL="https://assayz.uk/api/v1"
export ASSAY_API_KEY="$key"
CREDS
  chmod 600 "$dir/.assay"

  # Download skill.md
  curl -sfo "$dir/.assay-skill.md" "$SKILL_URL"

  # Init soul if missing
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
      if [ "$model" = "gpt-5.4" ]; then
        RUN_CMD="codex exec --dangerously-bypass-approvals-and-sandbox -m $model -c 'reasoning_effort=\"medium\"' \"\$PROMPT\""
      else
        RUN_CMD="codex exec --dangerously-bypass-approvals-and-sandbox -m $model \"\$PROMPT\""
      fi
      ;;
    opencode)
      RUN_CMD="OPENROUTER_API_KEY=\"$OPENROUTER_API_KEY\" opencode run -m openrouter/$model \"\$PROMPT\""
      ;;
  esac

  # Per-agent run script
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

  # Ensure soul exists
  [ -f soul.md ] || touch soul.md

  echo ""
  echo "══════════════════════════════════════════════════"
  echo "  $name — Pass \$(date '+%Y-%m-%d %H:%M:%S')"
  echo "══════════════════════════════════════════════════"

  $RUN_CMD

  # Sleep with jitter (0-60s)
  JITTER=\$((RANDOM % 60))
  echo "Sleeping ${sleep_s}s + \${JITTER}s jitter..."
  sleep \$((${sleep_s} + JITTER))
done
SCRIPT
  chmod +x "$dir/run.sh"
done

echo "Workspaces created in $AGENTS_DIR"

# ── Launch tmux ──────────────────────────────────────────────────────────────

tmux kill-session -t "$SESSION" 2>/dev/null || true
tmux new-session -d -s "$SESSION" -n agents

# Create 13 more panes (14 total)
for i in $(seq 1 13); do
  tmux split-window -t "$SESSION"
  tmux select-layout -t "$SESSION" tiled
done

# Send run commands to each pane
for i in "${!AGENTS[@]}"; do
  IFS='|' read -r name key runtime model sleep_s <<< "${AGENTS[$i]}"
  dir="$AGENTS_DIR/$name"
  tmux send-keys -t "$SESSION:0.$i" "bash $dir/run.sh" Enter
done

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Assay v4 Agent Fleet — launched in tmux session: $SESSION"
echo "  Attach with: tmux attach -t $SESSION"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  PAID (${PAID_SLEEP}s + jitter):"
for entry in "${AGENTS[@]}"; do
  IFS='|' read -r name key runtime model sleep_s <<< "$entry"
  [ "$sleep_s" = "$PAID_SLEEP" ] && echo "    $name ($runtime → $model)"
done
echo ""
echo "  FREE (${FREE_SLEEP}s + jitter):"
for entry in "${AGENTS[@]}"; do
  IFS='|' read -r name key runtime model sleep_s <<< "$entry"
  [ "$sleep_s" = "$FREE_SLEEP" ] && echo "    $name ($runtime → openrouter/$model)"
done
echo ""
echo "  15 agents • 10 model families • cross-family disagreement signal"
echo "═══════════════════════════════════════════════════════════════"
