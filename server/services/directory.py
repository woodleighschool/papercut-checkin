from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set


class StudentDirectory:
    """Caches student information."""

    def __init__(self, csv_path: str, card_columns: Iterable[str], name_column: str) -> None:
        self.csv_path = Path(csv_path)
        self.card_columns = [col.strip() for col in card_columns if col.strip()]
        self.name_column = name_column
        self._card_to_name: Dict[str, str] = {}
        self._names: Set[str] = set()
        self.reload()

    def reload(self) -> None:
        self._card_to_name.clear()
        self._names.clear()
        if not self.csv_path.exists():
            logging.getLogger(__name__).warning("Student CSV not found at %s; directory will be empty", self.csv_path)
            return

        with self.csv_path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                raw_name = (row.get(self.name_column) or "").strip()
                if not raw_name:
                    continue
                name = self._normalize_name(raw_name)
                self._names.add(name)
                for column in self.card_columns:
                    card_value = (row.get(column) or "").strip().lower()
                    if card_value:
                        self._card_to_name[card_value] = name

    def find_by_card(self, card_value: str) -> Optional[str]:
        return self._card_to_name.get(card_value.lower())

    def has_name(self, name: str) -> bool:
        return name in self._names

    @property
    def names(self) -> List[str]:
        return sorted(self._names)

    @property
    def cards(self) -> List[str]:
        return sorted(self._card_to_name.keys())

    @staticmethod
    def _normalize_name(raw_name: str) -> str:
        if "," in raw_name:
            last, first = [part.strip() for part in raw_name.split(",", 1)]
            return f"{first} {last}".strip()
        return raw_name.strip()


__all__ = ["StudentDirectory"]
