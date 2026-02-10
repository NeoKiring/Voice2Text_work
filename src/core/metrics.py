from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class MetricsCollector:
    session_state: str = "idle"
    processed_segments: int = 0
    last_update_at: datetime | None = None
    errors: int = 0
    custom: dict[str, float | int | str] = field(default_factory=dict)

    def mark_state(self, state: str) -> None:
        self.session_state = state
        self.last_update_at = datetime.utcnow()

    def add_segment(self) -> None:
        self.processed_segments += 1
        self.last_update_at = datetime.utcnow()

    def add_error(self) -> None:
        self.errors += 1
        self.last_update_at = datetime.utcnow()
