from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

CURRENT_CONFIG_VERSION = 2


@dataclass(slots=True)
class AppConfig:
    config_version: int = CURRENT_CONFIG_VERSION
    language: str = "ja"
    model_name: str = "tiny"
    output_dir: str = "outputs"
    output_formats: list[str] = None  # type: ignore[assignment]
    vad_threshold: float = 0.5

    def __post_init__(self) -> None:
        if self.output_formats is None:
            self.output_formats = ["txt", "json", "srt"]


class ConfigManager:
    def __init__(self, path: str = "config.json") -> None:
        self.path = Path(path)

    def load(self) -> AppConfig:
        if not self.path.exists():
            config = AppConfig()
            self.save(config)
            return config

        with self.path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        migrated = self._migrate(data)
        config = AppConfig(**migrated)
        self.save(config)
        return config

    def save(self, config: AppConfig) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(asdict(config), f, ensure_ascii=False, indent=2)

    def _migrate(self, data: dict[str, Any]) -> dict[str, Any]:
        version = int(data.get("config_version", 1))
        migrated = dict(data)

        if version < 2:
            output_format = migrated.pop("output_format", "txt")
            migrated["output_formats"] = [output_format, "json"] if output_format != "json" else ["json"]
            migrated["config_version"] = 2

        if "output_formats" not in migrated:
            migrated["output_formats"] = ["txt", "json", "srt"]

        migrated["config_version"] = CURRENT_CONFIG_VERSION
        return migrated
