from supertonic_openai_tts_proxy.schemas import SpeechRequest


def test_speech_request_defaults():
    req = SpeechRequest(input="안녕하세요")

    assert req.model == "supertonic-2"
    assert req.voice == "F1"
    assert req.response_format == "mp3"
    assert req.speed == 1.3
    assert req.lang == "ko"
    assert req.total_steps == 3


def test_speech_request_accepts_custom_total_steps():
    req = SpeechRequest(input="hello", total_steps=10)

    assert req.total_steps == 10


def test_speech_request_rejects_empty_input():
    try:
        SpeechRequest(input="   ")
    except ValueError as exc:
        assert "input" in str(exc).lower()
    else:
        raise AssertionError("empty input should fail")


def test_speech_request_rejects_unknown_format():
    try:
        SpeechRequest(input="hello", response_format="flac")
    except ValueError as exc:
        assert "response_format" in str(exc).lower()
    else:
        raise AssertionError("unknown response_format should fail")
