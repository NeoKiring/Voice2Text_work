from __future__ import annotations

from src.audio.audio_capture import AudioCapture
from src.audio.vad import VADSegmenter
from src.core.config_manager import ConfigManager
from src.core.event_bus import EventBus
from src.core.logger import configure_logger
from src.core.metrics import MetricsCollector
from src.export.exporters import ExportService
from src.session.session_controller import SessionController
from src.ui.app import Voice2TextApp


def build_app() -> Voice2TextApp:
    configure_logger()

    config = ConfigManager().load()
    event_bus = EventBus()
    metrics = MetricsCollector()

    controller = SessionController(
        event_bus=event_bus,
        metrics=metrics,
        audio_capture=AudioCapture(),
        vad=VADSegmenter(threshold=config.vad_threshold),
        export_service=ExportService(output_dir=config.output_dir),
        output_formats=config.output_formats,
    )

    return Voice2TextApp(controller=controller)


def main() -> None:
    app = build_app()
    app.mainloop()


if __name__ == "__main__":
    main()
