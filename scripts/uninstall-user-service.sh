#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="${SERVICE_NAME:-supertonic-openai-tts-proxy.service}"
SERVICE_PATH="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user/$SERVICE_NAME"

systemctl --user disable --now "$SERVICE_NAME" 2>/dev/null || true
rm -f "$SERVICE_PATH"
systemctl --user daemon-reload

printf 'Uninstalled %s\n' "$SERVICE_NAME"
