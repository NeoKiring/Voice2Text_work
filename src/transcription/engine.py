from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(slots=True)
class TranscriptSegment:
    text: str
    start_sec: float
    end_sec: float
    created_at: datetime


class TranscriptionEngine(Protocol):
    def transcribe(self, samples: list[float], sample_rate: int) -> TranscriptSegment | None:
        ...


class DummyTranscriptionEngine:
    def transcribe(self, samples: list[float], sample_rate: int) -> TranscriptSegment | None:
        if not samples:
            return None
        return TranscriptSegment(
            text="[sample] 音声を受信しました",
            start_sec=0.0,
            end_sec=float(len(samples) / sample_rate),
            created_at=datetime.utcnow(),
        )
