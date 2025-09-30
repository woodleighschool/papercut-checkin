from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from flask import current_app, url_for


def _load_manifest() -> Dict[str, dict]:
    static_folder = Path(current_app.static_folder or "static")
    manifest_path = static_folder / "dist" / ".vite" / "manifest.json"
    cache_key = "_vite_manifest_cache"
    mtime_key = "_vite_manifest_mtime"

    try:
        stat = manifest_path.stat()
    except FileNotFoundError:
        current_app.logger.warning("Vite manifest not found at %s", manifest_path)
        current_app.config[cache_key] = {}
        current_app.config[mtime_key] = None
        return {}

    cached_manifest = current_app.config.get(cache_key)
    cached_mtime = current_app.config.get(mtime_key)
    if cached_manifest is not None and cached_mtime == stat.st_mtime:
        return cached_manifest

    with manifest_path.open(encoding="utf-8") as handle:
        manifest = json.load(handle)

    current_app.config[cache_key] = manifest
    current_app.config[mtime_key] = stat.st_mtime
    return manifest


def vite_asset(entry: str) -> str:
    manifest = _load_manifest()
    entry_data = manifest.get(entry)
    file_path = None
    if isinstance(entry_data, dict):
        file_path = entry_data.get("file")
    elif isinstance(entry_data, str):
        file_path = entry_data

    if not file_path:
        current_app.logger.warning("Entry '%s' not found in Vite manifest", entry)
        return url_for("static", filename=f"dist/{entry}")

    return url_for("static", filename=f"dist/{file_path}")


def vite_styles(entry: str) -> List[str]:
    manifest = _load_manifest()
    entry_data = manifest.get(entry)
    css_files: List[str] = []
    if isinstance(entry_data, dict):
        css_files = entry_data.get("css", [])
    return [url_for("static", filename=f"dist/{path}") for path in css_files]


__all__ = ["vite_asset", "vite_styles"]
