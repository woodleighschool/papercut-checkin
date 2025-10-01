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
    valid_areas = current_app.config.get("AREAS", [])

    if area and area in valid_areas:
        session["area"] = area
        return redirect(url_for("ui.signin"))

    if not area:
        # No area set, show selection page
        return render_template("area-select.html")
    else:
        # Invalid area
        flash(f"Invalid area '{area}'. Please select a valid area.", "error")
        return render_template("area-select.html")


@ui_bp.route("/signin", methods=["GET", "POST"])
def signin():
    if "area" not in session:
        return redirect(url_for("ui.index"))

    directory: NameDirectory = current_app.extensions["name_directory"]

    if request.method == "POST":
        direction = request.form.get("direction", "in")
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
