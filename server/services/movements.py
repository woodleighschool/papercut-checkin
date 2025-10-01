from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Dict, List, Sequence

from sqlalchemy.orm import Session

from ..models import SignInEvent


@dataclass
class MovementSummary:
    area: str
    events: Sequence[SignInEvent]

    def as_dict(self) -> Dict[str, object]:
        return {
            "area": self.area,
            "events": [event.as_dict() for event in self.events],
        }


class MovementService:
    """Handles persistence and retrieval of sign-in events."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def record_event(
        self,
        *,
        name: str,
        area: str,
        direction: str,
        raw_input: str | None = None,
        recorded_at: datetime | None = None,
    ) -> SignInEvent:
        event = SignInEvent(
            name=name,
            area=area,
            direction=direction.upper(),
            recorded_at=recorded_at or datetime.now(),
            raw_input=raw_input,
        )
        self._session.add(event)
        self._session.commit()
        return event

    def events_for_date(self, target_date: date) -> List[SignInEvent]:
        start = datetime.combine(target_date, datetime.min.time())
        end = start + timedelta(days=1)
        return (
            SignInEvent.query
            .filter(SignInEvent.recorded_at >= start)
            .filter(SignInEvent.recorded_at < end)
            .order_by(SignInEvent.area.asc(), SignInEvent.recorded_at.asc())
            .all()
        )

    def grouped_events(self, target_date: date) -> List[MovementSummary]:
        events = self.events_for_date(target_date)
        grouped: Dict[str, List[SignInEvent]] = {}
        for event in events:
            grouped.setdefault(event.area, []).append(event)
        return [
            MovementSummary(area=area, events=grouped[area])
            for area in sorted(grouped.keys())
        ]


__all__ = ["MovementService", "MovementSummary"]
