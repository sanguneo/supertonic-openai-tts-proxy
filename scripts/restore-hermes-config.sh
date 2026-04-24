#!/usr/bin/env bash
set -euo pipefail

HERMES_BIN="${HERMES_BIN:-hermes}"
TIMESTAMP="${1:-}"

if ! command -v "$HERMES_BIN" >/dev/null 2>&1; then
  echo "hermes CLI not found: $HERMES_BIN" >&2
  exit 1
fi

CFG_PATH="$($HERMES_BIN config path)"
ENV_PATH="$($HERMES_BIN config env-path)"

usage() {
  cat <<EOF
Usage:
  $0 <backup_timestamp>
  $0 --latest
  $0 --list

Examples:
  $0 20260424_105304
  $0 --latest
EOF
}

list_backups() {
  shopt -s nullglob
  local cfg env ts
  for cfg in "${CFG_PATH}".bak.*; do
    ts="${cfg##*.bak.}"
    env="${ENV_PATH}.bak.${ts}"
    if [[ -f "$env" ]]; then
      printf '%s\n' "$ts"
    fi
  done | sort
}

if [[ -z "$TIMESTAMP" ]]; then
  usage >&2
  exit 1
fi

if [[ "$TIMESTAMP" == "--list" ]]; then
  list_backups
  exit 0
fi

if [[ "$TIMESTAMP" == "--latest" ]]; then
  TIMESTAMP="$(list_backups | tail -n 1)"
  if [[ -z "$TIMESTAMP" ]]; then
    echo "No paired Hermes backups found." >&2
    exit 1
  fi
fi

CFG_BAK="${CFG_PATH}.bak.${TIMESTAMP}"
ENV_BAK="${ENV_PATH}.bak.${TIMESTAMP}"

if [[ ! -f "$CFG_BAK" ]]; then
  echo "Missing config backup: $CFG_BAK" >&2
  exit 1
fi

if [[ ! -f "$ENV_BAK" ]]; then
  echo "Missing env backup: $ENV_BAK" >&2
  exit 1
fi

RESTORE_TS="$(date +%Y%m%d_%H%M%S)"
cp -a "$CFG_PATH" "${CFG_PATH}.pre-restore.${RESTORE_TS}"
cp -a "$ENV_PATH" "${ENV_PATH}.pre-restore.${RESTORE_TS}"
cp -a "$CFG_BAK" "$CFG_PATH"
cp -a "$ENV_BAK" "$ENV_PATH"

echo "Hermes config restored from backup timestamp: $TIMESTAMP"
echo "Restored config: $CFG_BAK -> $CFG_PATH"
echo "Restored env:    $ENV_BAK -> $ENV_PATH"
echo "Pre-restore backup: ${CFG_PATH}.pre-restore.${RESTORE_TS}"
echo "Pre-restore backup: ${ENV_PATH}.pre-restore.${RESTORE_TS}"
echo "Restart gateway if needed: hermes gateway restart"
