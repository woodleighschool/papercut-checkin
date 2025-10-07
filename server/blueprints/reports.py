from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from ..services.reports import ReportService


reports_bp = Blueprint("reports", __name__)


@reports_bp.before_request
def require_authentication() -> Optional[str]:
    # Check if user is authenticated for reports
    if "reports_authenticated" not in session:
        # Allow any request to the login route (both GET and POST)
        if request.endpoint == "reports.login":
            return None  # Allow login page access
        # Otherwise redirect to login
        return redirect(url_for("reports.login"))
    
    return None


@reports_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        required_username = current_app.config.get("REPORT_USERNAME")
        required_password = current_app.config.get("REPORT_PASSWORD")
        
        if not required_username or not required_password:
            flash("Reports access is not configured. Please contact the administrator.", "error")
            return render_template("reports-login.html")
        
        if username == required_username and password == required_password:
            session["reports_authenticated"] = True
            # Redirect to the originally requested page or reports
            next_page = request.args.get("next") or url_for("reports.reports")
            return redirect(next_page)
        else:
            flash("Invalid username or password.", "error")
    
    return render_template("reports-login.html")


@reports_bp.route("/", methods=["GET"])
def reports():
    target_date = _parse_date(request.args.get("date")) or date.today()
    report_service: ReportService = current_app.extensions["report_service"]
    summaries = report_service.grouped_summary(target_date)
    
    # Debug: Check if we have any summaries
    current_app.logger.info(f"Reports for {target_date}: Found {len(summaries)} area summaries")
    for summary in summaries:
        current_app.logger.info(f"Area {summary.area}: {len(summary.events)} events")

    if request.args.get("format") == "json" or request.accept_mimetypes.best == "application/json":
        return jsonify({
            "date": target_date.isoformat(),
            "areas": [summary.as_dict() for summary in summaries],
        })

    return render_template(
        "reports.html",
        target_date=target_date,
        summaries=summaries,
    )


@reports_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("reports_authenticated", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("reports.login"))


def _parse_date(raw: Optional[str]) -> Optional[date]:
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return None


__all__ = ["reports_bp"]
