from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from flask import (
    Blueprint,
    abort,
    current_app,
    jsonify,
    render_template,
    request,
)

from ..services.reports import ReportService


reports_bp = Blueprint("reports", __name__)


@reports_bp.before_request
def require_token() -> Optional[str]:
    token = current_app.config.get("REPORT_ACCESS_TOKEN")
    if not token:
        return None
    provided = _extract_token(request)
    if provided != token:
        abort(401)
    return None


@reports_bp.route("/daily", methods=["GET"])
def daily_report():
    target_date = _parse_date(request.args.get("date")) or date.today()
    report_service: ReportService = current_app.extensions["report_service"]
    summaries = report_service.grouped_summary(target_date)
    token = _extract_token(request)

    if request.args.get("format") == "json" or request.accept_mimetypes.best == "application/json":
        return jsonify({
            "date": target_date.isoformat(),
            "areas": [summary.as_dict() for summary in summaries],
        })

    return render_template(
        "reports/daily.html",
        target_date=target_date,
        summaries=summaries,
        auth_token=token,
    )


def _extract_token(req) -> Optional[str]:
    auth_header = req.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header.split(" ", 1)[1].strip()
    return req.args.get("token") or req.form.get("token")


def _parse_date(raw: Optional[str]) -> Optional[date]:
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return None


__all__ = ["reports_bp"]
