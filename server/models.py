from __future__ import annotations

from datetime import datetime

from .extensions import db


class SignInEvent(db.Model):
    __tablename__ = "signin_events"

    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(255), nullable=False)
    area = db.Column(db.String(128), nullable=False)
    direction = db.Column(db.String(3), nullable=False)
    recorded_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    raw_input = db.Column(db.String(255), nullable=True)

    def as_dict(self) -> dict[str, str]:
        return {
            "student_name": self.student_name,
            "area": self.area,
            "direction": self.direction,
            "recorded_at": self.recorded_at.isoformat(),
            "raw_input": self.raw_input or "",
        }


__all__ = ["SignInEvent"]
