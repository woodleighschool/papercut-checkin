from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


def _parse_list(raw: Optional[str]) -> List[str]:
    """Parse a comma or newline separated list"""
    if not raw:
        return []
    # Handle both comma and newline separation
    items = []
    for item in raw.replace("\n", ",").split(","):
        clean_item = item.strip()
        if clean_item:
            items.append(clean_item)
    return items


@dataclass
class BaseConfig:
    """Default application configuration."""

    SECRET_KEY: str = os.getenv("FLASK_SECRET", "change-me")
    SERVER_NAME: Optional[str] = os.getenv("SERVER_NAME")

    DATA_DIR: str = os.getenv("DATA_DIR", "/config")

    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{Path(os.getenv('DATA_DIR', '/config')).joinpath('signin.sqlite').as_posix()}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Names can be provided via file path or environment variable
    NAMES_FILE_PATH: Optional[str] = os.getenv("NAMES_FILE_PATH")
    NAMES_LIST: List[str] = field(
        default_factory=lambda: _parse_list(os.getenv("NAMES_LIST"))
    )

    AREAS: List[str] = field(
        default_factory=lambda: _parse_list(os.getenv("SIGNIN_AREAS"))
    )

    # Authentication for reports access
    REPORT_USERNAME: Optional[str] = os.getenv("REPORT_USERNAME")
    REPORT_PASSWORD: Optional[str] = os.getenv("REPORT_PASSWORD")
    ACCESS_KEY: str = os.getenv("ACCESS_KEY")

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
