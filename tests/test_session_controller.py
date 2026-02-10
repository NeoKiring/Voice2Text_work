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


def test_session_start_stop_exports(tmp_path):
    controller = SessionController(
        event_bus=EventBus(),
        metrics=MetricsCollector(),
        audio_capture=DummySpeechCapture(),
        vad=VADSegmenter(threshold=0.1),
        export_service=ExportService(output_dir=str(tmp_path)),
    )

    session_id = controller.start()
    assert session_id
    time.sleep(0.2)

    files = controller.stop()

    assert len(files) == 3
    assert controller.state.status == "stopped"
    assert controller.metrics.processed_segments >= 1
