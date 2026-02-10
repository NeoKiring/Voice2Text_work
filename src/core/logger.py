from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

import structlog


def configure_logger(log_dir: str = "logs") -> None:
    path = Path(log_dir)
    path.mkdir(parents=True, exist_ok=True)

    handler = RotatingFileHandler(path / "app.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[handler, logging.StreamHandler()],
    )

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
