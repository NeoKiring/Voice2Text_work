from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from src.transcription.engine import TranscriptSegment


@dataclass(slots=True)
class SessionState:
    session_id: str
    status: str = "idle"
    started_at: datetime | None = None
    stopped_at: datetime | None = None
    segments: list[TranscriptSegment] = field(default_factory=list)
