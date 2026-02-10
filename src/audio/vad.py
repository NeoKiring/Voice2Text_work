from __future__ import annotations


class VADSegmenter:
    def __init__(self, threshold: float = 0.5) -> None:
        self.threshold = threshold

    def is_speech(self, samples: list[float]) -> bool:
        if not samples:
            return False
        energy = sum(abs(v) for v in samples) / len(samples)
        return energy >= self.threshold
