from __future__ import annotations

import json
from pathlib import Path

from src.core.config_manager import ConfigManager


def test_migrate_v1_to_v2(tmp_path: Path) -> None:
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text(
        json.dumps(
            {
                "config_version": 1,
                "language": "ja",
                "model_name": "tiny",
                "output_format": "txt",
                "output_dir": "outputs",
                "vad_threshold": 0.2,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    cfg = ConfigManager(str(cfg_path)).load()

    assert cfg.config_version == 2
    assert "txt" in cfg.output_formats
    assert "json" in cfg.output_formats
