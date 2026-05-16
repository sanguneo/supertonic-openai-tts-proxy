import shutil
import tempfile
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from starlette.background import BackgroundTask

from .audio import convert_audio
from .schemas import SpeechRequest
from .synth import synthesize_to_wav

app = FastAPI(title="Supertonic OpenAI TTS Proxy", version="0.1.0")
ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTEND_PATH = ROOT_DIR / "frontend" / "index.html"


@lru_cache(maxsize=1)
def _load_frontend_html() -> str:
    return FRONTEND_PATH.read_text(encoding="utf-8")


@app.get("/")
def index() -> HTMLResponse:
    return HTMLResponse(_load_frontend_html())


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/models")
def models() -> dict[str, object]:
    return {
        "object": "list",
        "data": [
            {
                "id": "supertonic-3",
                "object": "model",
                "owned_by": "local",
            }
        ],
    }


@app.post("/v1/audio/speech")
def audio_speech(req: SpeechRequest):
    work_dir = Path(tempfile.mkdtemp(prefix="supertonic-tts-"))
    try:
        wav_path = synthesize_to_wav(req, work_dir)
        converted = convert_audio(wav_path, req.response_format, work_dir)
        return FileResponse(
            converted.path,
            media_type=converted.media_type,
            filename=converted.path.name,
            background=BackgroundTask(shutil.rmtree, work_dir, ignore_errors=True),
        )
    except ValueError as exc:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def run() -> None:
    import uvicorn

    uvicorn.run("supertonic_openai_tts_proxy.main:app", host="127.0.0.1", port=8789)
