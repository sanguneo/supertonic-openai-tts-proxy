"""Thin proxy for supertonic serve with ffmpeg audio conversion.

Proxies all requests to the official supertonic serve on BACKEND_URL,
but intercepts /v1/audio/speech to convert WAV output to opus/mp3/aac
via ffmpeg — formats the official serve doesn't natively support.
"""

import subprocess
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

BACKEND_URL = "http://127.0.0.1:8788"

# ffmpeg: (ext, media_type, codec_args)
FFMPEG_MAP: dict[str, tuple[str, str, list[str]]] = {
    "mp3":  ("mp3", "audio/mpeg",   ["-codec:a", "libmp3lame", "-b:a", "128k"]),
    "opus": ("ogg", "audio/ogg",    ["-codec:a", "libopus", "-ac", "1", "-b:a", "64k", "-vbr", "off"]),
    "aac":  ("aac", "audio/aac",    ["-codec:a", "aac", "-b:a", "128k"]),
    "wav":  ("wav", "audio/wav",    []),
    "flac": ("flac", "audio/flac",  ["-codec:a", "flac"]),
    "ogg":  ("ogg", "audio/ogg",    ["-codec:a", "libvorbis", "-b:a", "64k"]),
}

SUPPORTED = frozenset(FFMPEG_MAP.keys())

client: httpx.AsyncClient | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    client = httpx.AsyncClient(base_url=BACKEND_URL, timeout=120)
    yield
    await client.aclose()


app = FastAPI(
    title="Supertonic TTS Proxy",
    version="0.1.0",
    lifespan=lifespan,
)


def _convert(wav_bytes: bytes, fmt: str) -> tuple[bytes, str]:
    ext, media_type, codec_args = FFMPEG_MAP[fmt]
    if fmt == "wav":
        return wav_bytes, media_type

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(wav_bytes)
        in_path = f.name

    out_path = in_path + f".{ext}"
    try:
        r = subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", in_path, *codec_args, out_path],
            capture_output=True, text=True, timeout=120,
        )
        if r.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {r.stderr.strip()}")
        data = Path(out_path).read_bytes()
    finally:
        Path(in_path).unlink(missing_ok=True)
        Path(out_path).unlink(missing_ok=True)

    return data, media_type


def _error(status: int, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": {"message": detail, "type": "invalid_request_error"}},
    )


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str):
    global client
    if client is None:
        return _error(503, "proxy not ready")

    # ── Intercept /v1/audio/speech ──
    if path == "v1/audio/speech" and request.method == "POST":
        body = await request.json()
        fmt = (body.get("response_format") or "mp3").lower()

        if fmt not in SUPPORTED:
            return _error(400, f"unsupported format: {fmt}")

        if fmt in ("wav", "flac", "ogg"):
            # Forward as-is (native formats)
            resp = await client.post(f"/v1/audio/speech", json=body)
            return Response(content=resp.content, media_type=resp.headers.get("content-type", ""))

        # Request WAV from backend, then convert
        body_wav = {**body, "response_format": "wav"}
        resp = await client.post("/v1/audio/speech", json=body_wav)
        if resp.status_code != 200:
            return _error(resp.status_code, "backend synthesis failed")

        try:
            converted, media_type = _convert(resp.content, fmt)
            return Response(content=converted, media_type=media_type)
        except RuntimeError as e:
            return _error(500, str(e))

    # ── Forward everything else ──
    target_path = f"/{path}"
    if request.query_params:
        target_path += f"?{request.query_params}"

    body_bytes = await request.body()
    resp = await client.request(
        method=request.method,
        url=target_path,
        content=body_bytes,
        headers={k: v for k, v in request.headers.items() if k.lower() not in ("host", "content-length")},
    )

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=resp.headers.get("content-type"),
    )
