#!/usr/bin/env bash
set -euo pipefail

HERMES_BIN="${HERMES_BIN:-hermes}"
PROXY_URL="${PROXY_URL:-http://127.0.0.1:8789/v1}"
MODEL_NAME="${MODEL_NAME:-supertonic-2}"
VOICE_NAME="${VOICE_NAME:-F1}"
SPEED="${SPEED:-1.3}"
MAX_TEXT_LENGTH="${MAX_TEXT_LENGTH:-2000}"

if ! command -v "$HERMES_BIN" >/dev/null 2>&1; then
  echo "hermes CLI not found: $HERMES_BIN" >&2
  exit 1
fi

CFG_PATH="$($HERMES_BIN config path)"
ENV_PATH="$($HERMES_BIN config env-path)"
TS="$(date +%Y%m%d_%H%M%S)"
CFG_BAK="${CFG_PATH}.bak.${TS}"
ENV_BAK="${ENV_PATH}.bak.${TS}"

mkdir -p "$(dirname "$CFG_PATH")" "$(dirname "$ENV_PATH")"
touch "$CFG_PATH" "$ENV_PATH"
cp -a "$CFG_PATH" "$CFG_BAK"
cp -a "$ENV_PATH" "$ENV_BAK"

$HERMES_BIN config set tts.provider openai
$HERMES_BIN config set tts.openai.base_url "$PROXY_URL"
$HERMES_BIN config set tts.openai.model "$MODEL_NAME"
$HERMES_BIN config set tts.openai.voice "$VOICE_NAME"
$HERMES_BIN config set tts.openai.speed "$SPEED"
$HERMES_BIN config set tts.openai.max_text_length "$MAX_TEXT_LENGTH"

if grep -q '^VOICE_TOOLS_OPENAI_KEY=' "$ENV_PATH"; then
  perl -0pi -e 's/^VOICE_TOOLS_OPENAI_KEY=.*/VOICE_TOOLS_OPENAI_KEY=dummy/m' "$ENV_PATH"
else
  printf '\nVOICE_TOOLS_OPENAI_KEY=dummy\n' >> "$ENV_PATH"
fi

echo "Hermes config updated."
echo "Backup: $CFG_BAK"
echo "Backup: $ENV_BAK"
echo "Restore command: ./scripts/restore-hermes-config.sh $TS"
echo "Restart gateway if needed: hermes gateway restart"
echo "Verify: hermes doctor && hermes gateway status"
