from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess


@dataclass(frozen=True)
class ConvertedAudio:
    path: Path
    media_type: str


def content_type_for_format(response_format: str) -> str:
    mapping = {
        "mp3": "audio/mpeg",
        "opus": "audio/ogg",
        "aac": "audio/aac",
        "flac": "audio/flac",
        "wav": "audio/wav",
        "pcm": "application/octet-stream",
    }
    return mapping[response_format]


def _extension_for_format(response_format: str) -> str:
    return "ogg" if response_format == "opus" else response_format


def _codec_args(response_format: str) -> list[str]:
    if response_format == "mp3":
        return ["-codec:a", "libmp3lame", "-b:a", "128k"]
    if response_format == "opus":
        return ["-codec:a", "libopus", "-ac", "1", "-b:a", "64k", "-vbr", "off"]
    if response_format == "aac":
        return ["-codec:a", "aac", "-b:a", "128k"]
    if response_format == "flac":
        return ["-codec:a", "flac"]
    if response_format == "pcm":
        return ["-f", "s16le", "-acodec", "pcm_s16le", "-ac", "1", "-ar", "24000"]
    raise ValueError(f"Unsupported response_format: {response_format}")


def convert_audio(source_wav: Path, response_format: str, work_dir: Path) -> ConvertedAudio:
    source_wav = Path(source_wav)
    work_dir.mkdir(parents=True, exist_ok=True)
    media_type = content_type_for_format(response_format)

    if response_format == "wav":
        target = work_dir / "speech.wav"
        if source_wav.resolve() != target.resolve():
            shutil.copyfile(source_wav, target)
        return ConvertedAudio(path=target, media_type=media_type)

    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg is required for non-wav response formats")

    target = work_dir / f"speech.{_extension_for_format(response_format)}"
    command = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(source_wav)]
    command.extend(_codec_args(response_format))
    command.append(str(target))

    completed = subprocess.run(command, capture_output=True, text=True, timeout=60)
    if completed.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {completed.stderr.strip()}")
    if not target.exists() or target.stat().st_size == 0:
        raise RuntimeError("ffmpeg produced empty output")

    return ConvertedAudio(path=target, media_type=media_type)
