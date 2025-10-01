from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional, Set


class NameDirectory:
    """Caches name information."""

    def __init__(
        self,
        names_file_path: Optional[str] = None,
        names_list: Optional[List[str]] = None,
    ) -> None:
        self.names_file_path = Path(names_file_path) if names_file_path else None
        self.names_list = names_list or []
        self._names: Set[str] = set()
        self.reload()

    def reload(self) -> None:
        self._names.clear()

        # Load from names from environment
        for name in self.names_list:
            normalized = self._normalize_name(name)
            if normalized:
                self._names.add(normalized)

        # Load from names from file
        if self.names_file_path and self.names_file_path.exists():
            self._load_names_file()

    def _load_names_file(self) -> None:
        """Load names from file"""
        try:
            with self.names_file_path.open(encoding="utf-8-sig") as handle:
                content = handle.read()
                # Handle comma and newline separation
                for line in content.replace(",", "\n").split("\n"):
                    name = line.strip()
                    if name:
                        normalized = self._normalize_name(name)
                        if normalized:
                            self._names.add(normalized)
        except Exception as e:
            logging.getLogger(__name__).warning("Failed to load names file %s: %s", self.names_file_path, e)

    def has_name(self, name: str) -> bool:
        return name in self._names

    @property
    def names(self) -> List[str]:
        return sorted(self._names)

    @staticmethod
    def _normalize_name(raw_name: str) -> str:
        if "," in raw_name:
            last, first = [part.strip() for part in raw_name.split(",", 1)]
            return f"{first} {last}".strip()
        return raw_name.strip()


__all__ = ["NameDirectory"]
