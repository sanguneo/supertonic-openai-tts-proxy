#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8789/v1}"
OUT="${OUT:-/tmp/supertonic-openai-tts-proxy-smoke.mp3}"
TEXT="${1:-안녕하세요. 슈퍼토닉 오픈에이아이 호환 프록시 테스트입니다.}"

curl -sS "$BASE_URL/audio/speech" \
  -H 'Authorization: Bearer dummy' \
  -H 'Content-Type: application/json' \
  -d "$(python3 -c 'import json,sys; print(json.dumps({"model":"supertonic-2","voice":"F1","input":sys.argv[1],"response_format":"mp3","speed":1.3}, ensure_ascii=False))' "$TEXT")" \
  --output "$OUT"

ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 "$OUT"
echo "$OUT"
