from typing import Literal

from pydantic import BaseModel, Field, field_validator


TResponseFormat = Literal["mp3", "opus", "wav"]


class SpeechRequest(BaseModel):
    model: str = "supertonic-3"
    input: str = Field(min_length=1)
    voice: str = "F1"
    response_format: TResponseFormat = "mp3"
    speed: float = 1.3
    lang: str = "ko"
    total_steps: int = 6

    @field_validator("input")
    @classmethod
    def validate_input(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("input must not be empty")
        return value.strip()

    @field_validator("speed")
    @classmethod
    def validate_speed(cls, value: float) -> float:
        return max(0.25, min(4.0, float(value)))

    @field_validator("total_steps")
    @classmethod
    def validate_total_steps(cls, value: int) -> int:
        return max(1, min(20, int(value)))
