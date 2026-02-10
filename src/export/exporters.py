from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from src.transcription.engine import TranscriptSegment


class ExportService:
    def __init__(self, output_dir: str = "outputs") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(self, session_id: str, segments: list[TranscriptSegment], formats: list[str]) -> list[Path]:
        paths: list[Path] = []
        if "txt" in formats:
            paths.append(self._export_txt(session_id, segments))
        if "json" in formats:
            paths.append(self._export_json(session_id, segments))
        if "srt" in formats:
            paths.append(self._export_srt(session_id, segments))
        return paths

    def _export_txt(self, session_id: str, segments: list[TranscriptSegment]) -> Path:
        path = self.output_dir / f"{session_id}.txt"
        with path.open("w", encoding="utf-8") as f:
            for seg in segments:
                f.write(seg.text + "\n")
        return path

    def _export_json(self, session_id: str, segments: list[TranscriptSegment]) -> Path:
        path = self.output_dir / f"{session_id}.json"
        payload = {
            "schema_version": 1,
            "segments": [
                {**asdict(seg), "created_at": seg.created_at.isoformat()} for seg in segments
            ],
        }
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return path

    def _export_srt(self, session_id: str, segments: list[TranscriptSegment]) -> Path:
        path = self.output_dir / f"{session_id}.srt"
        with path.open("w", encoding="utf-8") as f:
            for i, seg in enumerate(segments, start=1):
                f.write(f"{i}\n")
                f.write(f"{self._fmt(seg.start_sec)} --> {self._fmt(seg.end_sec)}\n")
                f.write(seg.text + "\n\n")
        return path

    @staticmethod
    def _fmt(sec: float) -> str:
        total_ms = int(sec * 1000)
        s = (total_ms // 1000) % 60
        m = (total_ms // 60000) % 60
        h = total_ms // 3600000
        ms = total_ms % 1000
        return f"{h:02}:{m:02}:{s:02},{ms:03}"
