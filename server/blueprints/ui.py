from __future__ import annotations

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from ..services.movements import MovementService
from ..services.directory import NameDirectory


ui_bp = Blueprint("ui", __name__)


@ui_bp.app_context_processor
def inject_areas() -> dict[str, object]:
    return {"areas": current_app.config.get("AREAS", [])}


@ui_bp.route("/healthz")
def healthcheck() -> tuple[str, int]:
    return "ok", 200


@ui_bp.route("/")
def index():
    area = request.args.get("area")
    key = request.args.get("key")
    valid_areas = current_app.config.get("AREAS", [])
    required_key = current_app.config.get("ACCESS_KEY", "woodleigh")

    # Check if key is provided and valid
    if key and key == required_key:
        session["access_key"] = key
    elif "access_key" not in session:
        flash("Access denied. Invalid or missing access key.", "error")
        return render_template("area-select.html", show_access_denied=True)

    # Handle area selection
    if area and area in valid_areas:
        session["area"] = area
        return redirect(url_for("ui.signin"))

    # If area is already in session, check if it's still valid and go to signin
    if "area" in session:
        if session["area"] in valid_areas:
            return redirect(url_for("ui.signin"))
        else:
            # Area in session is no longer valid, clear it
            session.pop("area", None)
            flash("Your selected area is no longer available. Please select a new area.", "warning")

    if area and area not in valid_areas:
        # Invalid area
        flash(f"Invalid area '{area}'. Please select a valid area.", "error")

    # Show area selection page
    return render_template("area-select.html")


@ui_bp.route("/signin", methods=["GET", "POST"])
def signin():
    # Check access key
    if "access_key" not in session:
        return redirect(url_for("ui.index"))

    # Check area selection
    if "area" not in session:
        return redirect(url_for("ui.index"))

    directory: NameDirectory = current_app.extensions["name_directory"]

    if request.method == "POST":
        direction = (request.form.get("direction") or "in").strip().lower()
        if direction not in {"in", "out"}:
            direction = "in"
        entry = (request.form.get("entry") or "").strip()
        if not entry:
            flash("Please enter your name.", "error")
            return redirect(url_for("ui.signin"))

        lowered = entry.lower()
        if directory.has_name(entry):
            person_name = entry
        else:
            person_name = None

        if person_name:
            movements: MovementService = current_app.extensions["movement_service"]
            current_app.logger.info(f"Recording event: {person_name} {direction} at {session['area']}")
            movements.record_event(
                name=person_name,
                area=session["area"],
                direction=direction,
                raw_input=entry,
            )
            verb = "out" if direction == "out" else "in"
            flash(f"Signed {verb}: {person_name} at {session['area']}", "success")
            return redirect(url_for("ui.signin"))

        flash("This name could not be matched. Try entering your name again.", "error")
        return redirect(url_for("ui.signin"))

    return render_template(
        "signin.html",
        names=directory.names,
    )
