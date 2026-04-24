# supertonic-openai-tts-proxy

OpenAI-compatible local TTS proxy backed by Supertonic.

Hermes core 수정 없이 Hermes `tts.provider: openai` 경로를 그대로 재사용하기 위한 로컬 서버입니다.

## Endpoint

- `GET /health`
- `GET /v1/models`
- `POST /v1/audio/speech`

`POST /v1/audio/speech` accepts OpenAI-like body:

```json
{
  "model": "supertonic-2",
  "voice": "F1",
  "input": "안녕하세요.",
  "response_format": "mp3",
  "speed": 1.3,
  "total_steps": 3
}
```

Supported `response_format`:

- `mp3` -> `audio/mpeg`
- `opus` -> `audio/ogg`
- `wav` -> `audio/wav`

## Install

```bash
uv sync
```

## Run

```bash
./scripts/run-dev.sh
```

Default server:

```text
http://127.0.0.1:8789
```

Open browser:
- `http://127.0.0.1:8789/`

The page includes a tiny TTS playground for quick local testing.

## Smoke test

```bash
./scripts/smoke-test.sh
```

## Install as user service

No sudo required. WSL user systemd is supported.

```bash
./scripts/install-user-service.sh
./scripts/service-status.sh
```

Uninstall:

```bash
./scripts/uninstall-user-service.sh
```

Logs:

```text
.logs/service.log
.logs/service.err.log
```

## Hermes config

`~/.hermes/config.yaml`:

```yaml
tts:
  provider: openai
  openai:
    base_url: http://127.0.0.1:8789/v1
    model: supertonic-2
    voice: F1
    speed: 1.3
    max_text_length: 2000
```

`~/.hermes/.env`:

```bash
VOICE_TOOLS_OPENAI_KEY=dummy
```

Or run the helper script:

```bash
./scripts/setup-hermes-config.sh
```

## Notes

- First request may download/load Supertonic assets and can be slow.
- Korean default: `lang=ko`, `voice=F1`, `total_steps=3`.
- Long text is split into chunks before synthesis.
- Non-WAV formats require `ffmpeg`.
- Hermes streaming voice mode is separate and may still use ElevenLabs internals.
