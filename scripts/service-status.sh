#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="${SERVICE_NAME:-supertonic-openai-tts-proxy.service}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

systemctl --user --no-pager status "$SERVICE_NAME" || true
printf '\n--- service.log ---\n'
tail -n 80 "$ROOT_DIR/.logs/service.log" 2>/dev/null || true
printf '\n--- service.err.log ---\n'
tail -n 80 "$ROOT_DIR/.logs/service.err.log" 2>/dev/null || true
