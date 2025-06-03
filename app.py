import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Configurable areas for check-in/out
AREAS = ["Learning Enhancement", "Wellbeing", "Reception"]

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
app.secret_key = os.getenv("FLASK_SECRET", "change-me")

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 25))
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")

# Load CSV into mappings
CARD_TO_NAME = {}
NAMES = set()
with open("students.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        raw = row["Full Name"].strip()
        if "," in raw:
            last, first = [p.strip() for p in raw.split(",", 1)]
            name = f"{first} {last}"
        else:
            name = raw
        NAMES.add(name)
        for col in ("Primary Card Number", "Secondary Card Number"):
            cid = row.get(col, "").strip().lower()  # <-- normalize here
            if cid:
                CARD_TO_NAME[cid] = name


def send_notification(name, location, direction="in"):
    ts = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
    verb = "checked out" if direction == "out" else "checked in"
    body = f"{name} {verb} at {location} at {ts}."
    msg = MIMEText(body)
    action_label = "Check-Out" if direction == "out" else "Check-In"
    msg["Subject"] = f"{location} {action_label}: {name}"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    app.logger.debug("Sending notification email: Subject=%s, Body=%s", msg["Subject"], body)
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
        s.send_message(msg)


@app.route("/", methods=["GET", "POST"])
def select_area():
    if request.method == "POST":
        area = request.form.get("area")
        if not area:
            app.logger.warning("Select area POST with no area")
            flash("Please select an area.", "error")
            return redirect(url_for("select_area"))
        app.logger.info("Area selected: %s", area)
        session["area"] = area
        return redirect(url_for("checkin"))
    app.logger.debug("Rendering select_area page")
    return render_template("select_area.html", areas=AREAS)


@app.route("/area")
def set_area():
    area = request.args.get("area")
    raw = request.query_string.decode('utf-8')
    if not area and raw:
        area = raw.lstrip('=')
    if area in AREAS:
        app.logger.info("Area set via URI: %s", area)
        session["area"] = area
        return redirect(url_for("checkin"))
    app.logger.warning("Invalid area via URI: %s", area)
    flash(f"Invalid area: {area}", "error")
    return redirect(url_for("select_area"))


@app.route("/checkin", methods=["GET", "POST"])
def checkin():
    if "area" not in session:
        app.logger.warning("Accessed /checkin without area in session, redirecting")
        return redirect(url_for("select_area"))

    if request.method == "POST":
        direction = request.form.get("direction", "in")
        entry = request.form.get("entry", "").strip()
        lowered = entry.lower()
        if not entry:
            app.logger.warning("Empty checkin entry submitted for area: %s", session.get("area"))
            flash("Please scan card or enter your name", "error")
            return redirect(url_for("checkin"))
        elif lowered in CARD_TO_NAME:
            name = CARD_TO_NAME[lowered]
            app.logger.info("Card matched: %s -> %s, direction: %s, area: %s", entry, name, direction, session.get("area"))
            session["name"] = name
            session["direction"] = direction
            return redirect(url_for("confirm"))
        elif entry in NAMES:
            app.logger.info("Name matched: %s, direction: %s, area: %s", entry, direction, session.get("area"))
            session["name"] = entry
            session["direction"] = direction
            return redirect(url_for("confirm"))
        else:
            app.logger.warning("No match for entry: %s, area: %s", entry, session.get("area"))
            flash("This card or name could not be matched. Try manually entering your name below.", "error")
            return redirect(url_for("checkin"))

    app.logger.debug("Rendering checkin page for area: %s", session.get("area"))
    return render_template(
        "checkin.html",
        names=sorted(NAMES),
        cards=list(CARD_TO_NAME),
    )


@app.route("/confirm", methods=["GET", "POST"])
def confirm():
    name = session.get("name")
    area = session.get("area")
    direction = session.get("direction", "in")
    if not name or not area:
        app.logger.warning("Confirm accessed without name/area, redirecting")
        return redirect(url_for("select_area"))

    if request.method == "POST":
        action = request.form.get("action")
        if action == "confirm":
            try:
                send_notification(name, area, direction)
                verb = "out" if direction == "out" else "in"
                app.logger.info("Notification sent: %s %s at %s", name, verb, area)
                flash(f"Checked {verb}: {name} at {area}", "success")
            except Exception as e:
                app.logger.error("Failed to send notification for %s at %s: %s", name, area, e)
                flash("Login failed: notification could not be sent", "error")
            finally:
                session.clear()
            return redirect(url_for("select_area"))
        elif action == "cancel":
            app.logger.info("Confirmation cancelled by user: %s at %s", name, area)
            return redirect(url_for("checkin"))

    app.logger.debug("Rendering confirm page for %s at %s, direction: %s", name, area, direction)
    return render_template(
        "confirm.html",
        name=name,
        area=area,
        direction=direction,
    )
