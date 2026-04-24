from fastapi.testclient import TestClient

from supertonic_openai_tts_proxy.main import app


client = TestClient(app)


def test_frontend_page_contains_playground_form():
    res = client.get("/")

    assert res.status_code == 200
    html = res.text
    assert "Supertonic TTS Playground" in html
    assert 'id="tts-form"' in html
    assert 'id="tts-input"' in html
    assert 'id="tts-response-format"' in html
    assert 'id="tts-result"' in html
    assert "/v1/audio/speech" in html


def test_health():
    res = client.get("/health")

    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_models_endpoint():
    res = client.get("/v1/models")

    assert res.status_code == 200
    data = res.json()["data"]
    assert data[0]["id"] == "supertonic-2"


def test_audio_speech_returns_binary(monkeypatch, tmp_path):
    wav_path = tmp_path / "fake.wav"
    wav_path.write_bytes(b"RIFFfake")

    def fake_synthesize_to_wav(req, work_dir):
        return wav_path

    def fake_convert_audio(source_path, response_format, work_dir):
        class Result:
            path = wav_path
            media_type = "audio/wav"
        return Result()

    monkeypatch.setattr("supertonic_openai_tts_proxy.main.synthesize_to_wav", fake_synthesize_to_wav)
    monkeypatch.setattr("supertonic_openai_tts_proxy.main.convert_audio", fake_convert_audio)

    res = client.post(
        "/v1/audio/speech",
        headers={"Authorization": "Bearer dummy"},
        json={
            "model": "supertonic-2",
            "voice": "F1",
            "input": "안녕하세요. 테스트입니다.",
            "response_format": "wav",
            "speed": 1.3,
        },
    )

    assert res.status_code == 200
    assert res.headers["content-type"].startswith("audio/wav")
    assert res.content == b"RIFFfake"


def test_audio_speech_rejects_empty_input():
    res = client.post("/v1/audio/speech", json={"input": ""})

    assert res.status_code == 422
