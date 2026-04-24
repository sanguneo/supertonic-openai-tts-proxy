#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8789}"

exec uv run uvicorn supertonic_openai_tts_proxy.main:app --host "$HOST" --port "$PORT"
