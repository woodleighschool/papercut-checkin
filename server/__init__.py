from __future__ import annotations

import logging
import os
from typing import Optional

from flask import Flask

from .blueprints.reports import reports_bp
from .blueprints.ui import ui_bp
from .config import BaseConfig, load_config
from .extensions import db
from .services.movements import MovementService
from .services.directory import NameDirectory

from .services.reports import ReportService
from .vite import vite_asset, vite_styles


def create_app(config: Optional[str | type[BaseConfig] | BaseConfig] = None) -> Flask:
    app = Flask(
        __name__,
        static_folder="../static",
        template_folder="../templates",
    )

    cfg = load_config(config)
    app.config.from_object(cfg)

    os.makedirs(app.instance_path, exist_ok=True)
    data_dir = app.config.get("DATA_DIR")
    if data_dir:
        os.makedirs(data_dir, exist_ok=True)

    _configure_logging(app)
    _register_extensions(app)
    _register_services(app)
    _register_blueprints(app)
    _register_template_helpers(app)
    _register_cli(app)

    with app.app_context():
        db.create_all()

    return app


def _configure_logging(app: Flask) -> None:
    level_name = app.config.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(level=level)
    app.logger.setLevel(level)


def _register_extensions(app: Flask) -> None:
    db.init_app(app)


def _register_services(app: Flask) -> None:
    directory = NameDirectory(
        names_file_path=app.config.get("NAMES_FILE_PATH"),
        names_list=app.config.get("NAMES_LIST", []),
    )
    app.extensions["name_directory"] = directory

    attendance_service = MovementService(db.session)
    app.extensions["movement_service"] = attendance_service

    report_service = ReportService(
        movement_service=attendance_service,
        areas=app.config.get("AREAS", []),
    )
    app.extensions["report_service"] = report_service


def _register_blueprints(app: Flask) -> None:
    app.register_blueprint(ui_bp)
    app.register_blueprint(reports_bp, url_prefix="/reports")


def _register_template_helpers(app: Flask) -> None:
    @app.context_processor
    def _inject_vite_helpers() -> dict[str, object]:
        return {"vite_asset": vite_asset, "vite_styles": vite_styles}


def _register_cli(app: Flask) -> None:
    from datetime import date

    @app.cli.command("reload-directory")
    def reload_directory() -> None:
        directory: NameDirectory = app.extensions["name_directory"]
        directory.reload()
        app.logger.info("Name directory reloaded")


__all__ = ["create_app"]
