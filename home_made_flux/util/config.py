import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_PATH = Path("config.json")


@dataclass
class AppConfig:
    location_mode: str = "auto"  # "auto" or "manual"
    manual_location: str = ""
    night_light_strength: int = 50
    transition_minutes: int = 10
    schedule_interval_minutes: int = 5
    dry_run: bool = True
    start_at_login: bool = False
    manual_override: bool | None = None  # None means follow schedule


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> AppConfig:
    config_path = Path(path)
    if not config_path.exists():
        return AppConfig()
    try:
        with config_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        return AppConfig(**raw)
    except (json.JSONDecodeError, TypeError, OSError):
        return AppConfig()


def save_config(config: AppConfig, path: str | Path = DEFAULT_CONFIG_PATH) -> None:
    config_path = Path(path)
    try:
        with config_path.open("w", encoding="utf-8") as f:
            json.dump(asdict(config), f, indent=2)
    except OSError:
        # Best-effort persistence; logging handled by caller.
        return


def update_config(config: AppConfig, updates: dict[str, Any]) -> AppConfig:
    data = asdict(config)
    data.update(updates)
    return AppConfig(**data)
