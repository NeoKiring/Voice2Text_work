from __future__ import annotations

import time

from src.audio.audio_capture import AudioCapture
from src.audio.vad import VADSegmenter
from src.core.event_bus import EventBus
from src.core.metrics import MetricsCollector
from src.export.exporters import ExportService
from src.session.session_controller import SessionController


class DummySpeechCapture(AudioCapture):
    def stream(self):
        while self._running:
            yield type("Chunk", (), {"samples": [1.0] * 1600, "sample_rate": 16000})
            time.sleep(0.01)


class CrashEngine:
    def transcribe(self, samples, sample_rate):
        raise RuntimeError("boom")


def test_session_start_stop_exports_respects_output_formats(tmp_path):
    controller = SessionController(
        event_bus=EventBus(),
        metrics=MetricsCollector(),
        audio_capture=DummySpeechCapture(),
        vad=VADSegmenter(threshold=0.1),
        export_service=ExportService(output_dir=str(tmp_path)),
        output_formats=["txt", "json"],
    )

    session_id = controller.start()
    assert session_id
    time.sleep(0.2)

    files = controller.stop()

    assert len(files) == 2
    assert any(path.endswith(".txt") for path in files)
    assert any(path.endswith(".json") for path in files)
    assert controller.state.status == "stopped"
    assert controller.metrics.processed_segments >= 1


def test_session_emits_error_event_on_transcription_failure():
    bus = EventBus()
    errors: list[str] = []
    bus.subscribe("transcription.error", lambda event: errors.append(event.payload["error"]))

    controller = SessionController(
        event_bus=bus,
        metrics=MetricsCollector(),
        audio_capture=DummySpeechCapture(),
        vad=VADSegmenter(threshold=0.1),
        transcription_engine=CrashEngine(),
    )

    controller.start()
    time.sleep(0.1)
    controller.stop()

    assert controller.metrics.errors >= 1
    assert errors
