from __future__ import annotations

from datetime import date
from typing import List, Sequence

from .movements import MovementService, MovementSummary


class ReportService:
    """Generates movement summaries."""

    def __init__(
        self,
        *,
        movement_service: MovementService,
        areas: Sequence[str] | None = None,
    ) -> None:
        self.movement_service = movement_service
        self.areas = list(areas or [])

    def grouped_summary(self, target_date: date) -> List[MovementSummary]:
        summaries = self.movement_service.grouped_events(target_date)
        by_area = {summary.area: summary for summary in summaries}
        ordered: List[MovementSummary] = []
        seen = set()
        for area in self.areas:
            if area in by_area:
                ordered.append(by_area[area])
                seen.add(area)
            else:
                ordered.append(MovementSummary(area=area, events=[]))
        for area, summary in sorted(by_area.items()):
            if area not in seen:
                ordered.append(summary)
        return ordered

    def summary_as_dict(self, target_date: date) -> List[dict]:
        return [summary.as_dict() for summary in self.grouped_summary(target_date)]


__all__ = ["ReportService"]
