# supertonic-openai-tts-proxy

Supertonic TTS 공식 `serve` 명령어 앞단에서 ffmpeg 변환을 추가하는 프록시.

Telegram 음성메시지(OGG Opus)나 MP3/AAC 포맷을 지원하기 위해 만들어졌다.

## 배경

이전에는 [Supertonic](https://supertone-inc.github.io/supertonic-py/) TTS 엔진을 직접 FastAPI로 감싸는 커스텀 프록시를 운영했다.
하지만 Supertonic v1.3.1부터 공식 `serve` CLI가 OpenAI 호환 `/v1/audio/speech` 엔드포인트를 내장하면서,
굳이 직접 TTS 엔진을 다룰 필요가 없어졌다.

**변경 이유:**

| 이전 | 이후 |
|---|---|
| 직접 supertonic.TTS 호출 | 공식 `supertonic serve` 호출 |
| 유지보수 필요 | 유지보수 0 (Supertone이 관리) |
| /v1/audio/speech 만 지원 | /v1/health, /v1/tts, /v1/styles, /v1/tts/batch, /docs 등 모두 지원 |
| mp3/opus 지원 (ffmpeg) | wav/flac/ogg 기본 + mp3/opus/aac는 프록시에서 변환 |

공식 serve가 지원하지 않는 포맷(mp3, opus, aac)만 이 프록시가 ffmpeg로 변환해준다. 
나머지 요청은 전부 공식 serve로 그대로 통과시킨다.

## 구조

```
supertonic serve (:8788)   ← 공식 serve (내부)
    ↕
supertonic-proxy (:8789)   ← ffmpeg 변환 프록시 (외부)
    ↕
Hermes / OpenAI 클라이언트
```

## 설치 & 실행

```bash
# 1. supertonic serve 설치 (별도 프로젝트)
pip install 'supertonic[serve]>=1.3.1'
supertonic serve --port 8788 --log-level warning

# 2. 프록시 설치
uv sync
uv run uvicorn supertonic_proxy.main:app --host 127.0.0.1 --port 8789
```

## systemd (user service)

```ini
# ~/.config/systemd/user/supertonic-serve.service
ExecStart=/path/to/.venv/bin/supertonic serve --port 8788 --log-level warning

# ~/.config/systemd/user/supertonic-proxy.service
ExecStart=/path/to/.venv/bin/uvicorn supertonic_proxy.main:app --host 127.0.0.1 --port 8789
```

## 엔드포인트

프록시를 통해 모든 엔드포인트 사용 가능:

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/v1/health` | 상태 확인 |
| GET | `/v1/styles` | 음성 목록 |
| POST | `/v1/tts` | 네이티브 합성 |
| POST | `/v1/audio/speech` | **OpenAI 호환** (opus/mp3/aac 변환 지원) |
| POST | `/v1/tts/batch` | 배치 합성 |
| GET | `/docs` | Swagger UI |

## 지원 포맷

| 포맷 | 코덱 | 비고 |
|---|---|---|
| `wav` | PCM | 기본 |
| `flac` | FLAC | |
| `ogg` | Vorbis | 공식 serve 네이티브 |
| `mp3` | MP3 LAME | **프록시 변환** |
| `opus` | Opus | **프록시 변환** — Telegram 음성메시지 |
| `aac` | AAC | **프록시 변환** |
