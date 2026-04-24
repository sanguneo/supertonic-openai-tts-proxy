# Supertonic OpenAI TTS Proxy

> OpenAI-compatible local TTS proxy for [supertone-inc/supertonic](https://github.com/supertone-inc/supertonic).  
> Hermes core를 수정하지 않고, Supertonic TTS를 OpenAI `/v1/audio/speech` 규격처럼 사용할 수 있게 감싸는 로컬 프록시입니다.

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-OpenAI_compatible-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img alt="Supertonic" src="https://img.shields.io/badge/Supertonic-TTS-7C3AED?style=for-the-badge" />
  <img alt="Hermes" src="https://img.shields.io/badge/Hermes-ready-111827?style=for-the-badge" />
</p>

---

## What is this?

`supertonic-openai-tts-proxy`는 공식 Supertonic 프로젝트인
[`https://github.com/supertone-inc/supertonic`](https://github.com/supertone-inc/supertonic)를 백엔드 합성 엔진으로 사용하고,
외부에는 OpenAI TTS 호환 API처럼 보이게 만드는 작은 FastAPI 서버입니다.

즉, 클라이언트는 아래처럼 OpenAI 스타일로 호출합니다.

```http
POST http://127.0.0.1:8789/v1/audio/speech
```

내부에서는 Supertonic으로 음성을 합성하고, 요청한 포맷에 맞춰 오디오를 반환합니다.

---

## Why?

Hermes Agent는 이미 `tts.provider: openai` 경로와 `base_url` override를 지원합니다.
그래서 Hermes core를 건드리지 않고도, 로컬 Supertonic 서버를 OpenAI 호환 TTS API로 맞추면 그대로 연결할 수 있습니다.

```text
Hermes / client
      │
      │ OpenAI-compatible request
      ▼
/v1/audio/speech
      │
      │ proxy adapter
      ▼
Supertonic
      │
      │ synthesized audio
      ▼
mp3 / opus / wav
```

---

## Features

- OpenAI-compatible `POST /v1/audio/speech`
- Supertonic 기반 로컬 TTS 합성
- `mp3`, `opus`, `wav` 응답 지원
- 긴 텍스트 chunking 처리
- Supertonic quality/steps 제어 (`total_steps`)
- Hermes 설정 자동 적용 스크립트
- WSL user systemd 서비스 스크립트
- 브라우저 테스트용 Playground 내장
- pytest 기반 API contract 테스트

---

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Local TTS playground |
| `GET` | `/health` | Health check |
| `GET` | `/v1/models` | OpenAI-style model list |
| `POST` | `/v1/audio/speech` | OpenAI-compatible TTS endpoint |

### Request example

```json
{
  "model": "supertonic-2",
  "voice": "F1",
  "input": "안녕하세요. Supertonic TTS 테스트입니다.",
  "response_format": "mp3",
  "speed": 1.3,
  "total_steps": 3
}
```

### Supported response formats

| `response_format` | Content-Type | Notes |
|---|---|---|
| `mp3` | `audio/mpeg` | 일반 재생/다운로드용 |
| `opus` | `audio/ogg` | Telegram voice bubble에 적합 |
| `wav` | `audio/wav` | 원본/디버깅용 |

---

## Quick start

### 1. Install

```bash
uv sync
```

### 2. Run dev server

```bash
./scripts/run-dev.sh
```

Default server:

```text
http://127.0.0.1:8789
```

### 3. Open playground

```text
http://127.0.0.1:8789/
```

Playground에서 텍스트, voice, format, speed, quality steps를 바로 테스트할 수 있습니다.

### 4. Smoke test

```bash
./scripts/smoke-test.sh
```

---

## Run as user service

WSL user systemd 기준입니다. `sudo` 없이 사용자 서비스로 등록합니다.

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

---

## Hermes integration

### Option A. Helper script

가장 간단한 방식입니다. 기존 Hermes 설정을 백업한 뒤 Supertonic proxy로 TTS 설정을 맞춥니다.

```bash
./scripts/setup-hermes-config.sh
```

스크립트가 적용하는 기본값:

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

`.env`에는 dummy key를 넣습니다. 로컬 프록시라 실제 OpenAI key는 필요 없습니다.

```bash
VOICE_TOOLS_OPENAI_KEY=dummy
```

적용 후 gateway를 쓰고 있다면 재시작합니다.

```bash
hermes gateway restart
```

### Option B. Manual config

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

---

## Quality / steps

Supertonic quality 설정은 OpenAI 호환 요청의 확장 필드 `total_steps`로 넘깁니다.

| Quality | `total_steps` | Use case |
|---|---:|---|
| Low | `3` | 빠른 응답, 기본값 |
| Normal | `6` | 균형 |
| High | `10` | 더 좋은 품질, 느릴 수 있음 |

현재 기본값:

```text
lang=ko
voice=F1
total_steps=3
speed=1.3
```

---

## Project layout

```text
.
├── frontend/
│   └── index.html              # tiny browser playground
├── scripts/
│   ├── install-user-service.sh
│   ├── run-dev.sh
│   ├── service-status.sh
│   ├── setup-hermes-config.sh
│   ├── smoke-test.sh
│   └── uninstall-user-service.sh
├── src/supertonic_openai_tts_proxy/
│   ├── audio.py                # audio conversion / content-type mapping
│   ├── main.py                 # FastAPI app and endpoints
│   ├── schemas.py              # request schema / defaults
│   └── synth.py                # Supertonic adapter and chunking
└── tests/
    ├── test_api_contract.py
    ├── test_audio.py
    └── test_schemas.py
```

---

## Development

Run tests:

```bash
uv run pytest -q
```

Check service:

```bash
curl http://127.0.0.1:8789/health
```

Generate audio directly:

```bash
curl -X POST http://127.0.0.1:8789/v1/audio/speech \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "supertonic-2",
    "voice": "F1",
    "input": "안녕하세요. 테스트입니다.",
    "response_format": "opus",
    "speed": 1.3,
    "total_steps": 3
  }' \
  --output test.ogg
```

---

## Notes

- 첫 요청은 Supertonic asset download/load 때문에 느릴 수 있습니다.
- Non-WAV format 변환에는 `ffmpeg`가 필요합니다.
- `opus`는 `audio/ogg`로 반환하며 Telegram voice message에 적합합니다.
- Hermes CLI/gateway는 기존 config/env를 들고 있을 수 있으니 설정 변경 후 새 프로세스나 gateway restart로 확인합니다.
- Hermes streaming voice mode는 별도 경로를 쓸 수 있습니다.

---

## Credits

- TTS engine: [supertone-inc/supertonic](https://github.com/supertone-inc/supertonic)
- API compatibility target: OpenAI-style `/v1/audio/speech`
- Integration target: Hermes Agent TTS provider path
