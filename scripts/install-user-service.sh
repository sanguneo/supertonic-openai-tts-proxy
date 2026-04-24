#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="${SERVICE_NAME:-supertonic-openai-tts-proxy.service}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
USER_SYSTEMD_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
SERVICE_PATH="$USER_SYSTEMD_DIR/$SERVICE_NAME"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8789}"

mkdir -p "$USER_SYSTEMD_DIR"
mkdir -p "$ROOT_DIR/.cache" "$ROOT_DIR/.logs"

cat > "$SERVICE_PATH" <<EOF
[Unit]
Description=Supertonic OpenAI-compatible TTS proxy
After=network.target

[Service]
Type=simple
WorkingDirectory=$ROOT_DIR
Environment=HOST=$HOST
Environment=PORT=$PORT
Environment=UV_LINK_MODE=copy
Environment=HF_HOME=$ROOT_DIR/.cache/huggingface
Environment=TRANSFORMERS_CACHE=$ROOT_DIR/.cache/huggingface
ExecStart=$ROOT_DIR/.venv/bin/uvicorn supertonic_openai_tts_proxy.main:app --host $HOST --port $PORT
Restart=on-failure
RestartSec=5
StandardOutput=append:$ROOT_DIR/.logs/service.log
StandardError=append:$ROOT_DIR/.logs/service.err.log

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable "$SERVICE_NAME"
systemctl --user restart "$SERVICE_NAME"

printf 'Installed and started %s\n' "$SERVICE_NAME"
printf 'Service file: %s\n' "$SERVICE_PATH"
printf 'Health: http://%s:%s/health\n' "$HOST" "$PORT"
