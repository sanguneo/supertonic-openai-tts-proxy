import wave
from pathlib import Path

from supertonic_openai_tts_proxy.audio import content_type_for_format, convert_audio


def _write_dummy_wav(path: Path) -> None:
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(b"\x00\x00" * 2400)


def test_content_type_for_supported_formats():
    assert content_type_for_format("mp3") == "audio/mpeg"
    assert content_type_for_format("opus") == "audio/ogg"
    assert content_type_for_format("wav") == "audio/wav"


def test_convert_audio_returns_wav_without_ffmpeg(tmp_path):
    source = tmp_path / "source.wav"
    _write_dummy_wav(source)

    result = convert_audio(source, "wav", tmp_path)

    assert result.path.exists()
    assert result.media_type == "audio/wav"
    assert result.path.suffix == ".wav"


def test_convert_audio_to_mp3(tmp_path):
    source = tmp_path / "source.wav"
    _write_dummy_wav(source)

    result = convert_audio(source, "mp3", tmp_path)

    assert result.path.exists()
    assert result.path.stat().st_size > 0
    assert result.media_type == "audio/mpeg"
    assert result.path.suffix == ".mp3"


def test_convert_audio_to_opus(tmp_path):
    source = tmp_path / "source.wav"
    _write_dummy_wav(source)

    result = convert_audio(source, "opus", tmp_path)

    assert result.path.exists()
    assert result.path.stat().st_size > 0
    assert result.media_type == "audio/ogg"
    assert result.path.suffix == ".ogg"
