from __future__ import annotations

import threading
import time
import uuid
from datetime import datetime

from src.audio.audio_capture import AudioCapture
from src.audio.vad import VADSegmenter
from src.core.event_bus import EventBus
from src.core.metrics import MetricsCollector
from src.export.exporters import ExportService
from src.session.session_types import SessionState
from src.transcription.engine import DummyTranscriptionEngine, TranscriptionEngine


class SessionController:
    def __init__(
        self,
        event_bus: EventBus,
        metrics: MetricsCollector,
        audio_capture: AudioCapture,
        vad: VADSegmenter,
        transcription_engine: TranscriptionEngine | None = None,
        export_service: ExportService | None = None,
        output_formats: list[str] | None = None,
    ) -> None:
        self.event_bus = event_bus
        self.metrics = metrics
        self.audio_capture = audio_capture
        self.vad = vad
        self.engine = transcription_engine or DummyTranscriptionEngine()
        self.export_service = export_service or ExportService()
        self.output_formats = output_formats or ["txt", "json", "srt"]
        self.state = SessionState(session_id="")
        self._thread: threading.Thread | None = None
        self._stop_requested = threading.Event()

    def start(self) -> str:
        if self.state.status == "running":
            return self.state.session_id

        self.state = SessionState(session_id=uuid.uuid4().hex, status="running", started_at=datetime.utcnow())
        self._stop_requested.clear()
        self.audio_capture.start()
        self.metrics.mark_state("running")
        self.event_bus.publish("session.started", {"session_id": self.state.session_id})

        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self.state.session_id

    def stop(self) -> list[str]:
        if self.state.status != "running":
            return []

        self._stop_requested.set()
        self.audio_capture.stop()
        if self._thread:
            self._thread.join(timeout=2)

        self.state.status = "stopped"
        self.state.stopped_at = datetime.utcnow()
        self.metrics.mark_state("stopped")

        paths = self.export_service.export(
            session_id=self.state.session_id,
            segments=self.state.segments,
            formats=self.output_formats,
        )
        self.event_bus.publish("session.stopped", {"session_id": self.state.session_id, "files": [str(p) for p in paths]})
        return [str(p) for p in paths]

    def _run(self) -> None:
        try:
            for chunk in self.audio_capture.stream():
                if self._stop_requested.is_set():
                    break
                if not self.vad.is_speech(chunk.samples):
                    time.sleep(0.05)
                    continue
                seg = self.engine.transcribe(chunk.samples, chunk.sample_rate)
                if seg is None:
                    continue
                self.state.segments.append(seg)
                self.metrics.add_segment()
                self.event_bus.publish("transcript.segment", {"text": seg.text})
                time.sleep(0.1)
        except Exception as exc:
            self.metrics.add_error()
            self.event_bus.publish("transcription.error", {"error": str(exc)})
