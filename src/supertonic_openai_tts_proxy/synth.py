import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Iterable

import soundfile as sf

from .schemas import SpeechRequest

# Supertonic 3 model directory (downloaded from Hugging Face)
V3_MODEL_DIR = os.path.expanduser("~/.cache/supertonic3")


def split_text(text: str, max_chars: int = 260) -> list[str]:
    text = text.replace("\\n", "\n").strip()
    if len(text) <= max_chars:
        return [text]

    parts = [p.strip() for p in re.split(r"(?<=[.!?。！？.])\\s+|\\n+", text) if p.strip()]
    chunks: list[str] = []
    current = ""
    for part in parts:
        if not current:
            current = part
            continue
        if len(current) + 1 + len(part) <= max_chars:
            current = f"{current} {part}"
        else:
            chunks.append(current)
            current = part
    if current:
        chunks.append(current)

    normalized: list[str] = []
    for chunk in chunks:
        if len(chunk) <= max_chars:
            normalized.append(chunk)
        else:
            normalized.extend(chunk[i : i + max_chars] for i in range(0, len(chunk), max_chars))
    return normalized


@lru_cache(maxsize=1)
def get_tts():
    from supertonic import TTS

    return TTS(auto_download=False, model_dir=V3_MODEL_DIR, model="supertonic-2")


def _synthesize_chunk(tts, text: str, req: SpeechRequest):
    style = tts.get_voice_style(voice_name=req.voice)
    wav, _duration = tts.synthesize(
        text,
        voice_style=style,
        lang=req.lang,
        speed=req.speed,
        total_steps=req.total_steps,
    )
    return wav


def synthesize_to_wav(req: SpeechRequest, work_dir: Path) -> Path:
    work_dir.mkdir(parents=True, exist_ok=True)
    output_path = work_dir / "speech.wav"
    chunks = split_text(req.input)
    tts = get_tts()

    if len(chunks) == 1:
        wav = _synthesize_chunk(tts, chunks[0], req)
        tts.save_audio(wav, str(output_path))
        return output_path

    arrays = []
    sample_rate = None
    silence = None
    for chunk in chunks:
        wav = _synthesize_chunk(tts, chunk, req)
        chunk_path = work_dir / f"chunk_{len(arrays)}.wav"
        tts.save_audio(wav, str(chunk_path))
        audio, sr = sf.read(str(chunk_path), dtype="float32")
        if sample_rate is None:
            sample_rate = sr
            import numpy as np

            silence = np.zeros(int(sr * 0.25), dtype="float32")
        arrays.append(audio)
        if silence is not None:
            arrays.append(silence)

    import numpy as np

    combined = np.concatenate(arrays) if arrays else np.array([], dtype="float32")
    sf.write(str(output_path), combined, sample_rate or 24000)
    return output_path
