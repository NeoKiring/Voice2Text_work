from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(slots=True)
class AudioChunk:
    samples: list[float]
    sample_rate: int


class AudioCapture:
    def __init__(self, sample_rate: int = 16000, chunk_size: int = 1600) -> None:
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self._running = False

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def stream(self) -> Iterable[AudioChunk]:
        while self._running:
            yield AudioChunk(samples=[0.0] * self.chunk_size, sample_rate=self.sample_rate)
