from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


def _parse_area_list(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.replace(",", ";").split(";") if item.strip()]


def _to_bool(value: Optional[str]) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_float(value: Optional[str]) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


@dataclass
class BaseConfig:
    """Default application configuration."""

    SECRET_KEY: str = os.getenv("FLASK_SECRET", "change-me")
    SERVER_NAME: Optional[str] = os.getenv("SERVER_NAME")

    DATA_DIR: str = os.getenv("DATA_DIR", "/config")

    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{Path(os.getenv('DATA_DIR', '/config')).joinpath('checkins.sqlite').as_posix()}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    STUDENT_CSV_PATH: str = os.getenv("STUDENT_CSV_PATH", "students.csv")
    DIRECTORY_NAME_COLUMN: str = os.getenv("DIRECTORY_NAME_COLUMN", "Full Name")
    DIRECTORY_CARD_COLUMNS: List[str] = field(
        default_factory=lambda: [item.strip() for item in os.getenv(
            "DIRECTORY_CARD_COLUMNS",
            "Primary Card Number,Secondary Card Number",
        ).split(",") if item.strip()]
    )

    AREAS: List[str] = field(
        default_factory=lambda: _parse_area_list(
            os.getenv("CHECKIN_AREAS")
        )
    )

    REPORT_ACCESS_TOKEN: Optional[str] = os.getenv("REPORT_ACCESS_TOKEN")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


def load_config(config: Optional[str | type[BaseConfig]]) -> BaseConfig:
    if config is None:
        return BaseConfig()
    if isinstance(config, str):
        module_name, _, class_name = config.rpartition(":")
        if not module_name:
            module_name = __name__
        module = __import__(module_name, fromlist=[class_name])
        config_class = getattr(module, class_name)
        return config_class()
    if isinstance(config, type):
        return config()
    return config


__all__ = ["BaseConfig", "load_config"]
