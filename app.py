from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
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


def send_notification(name, location):
    ts = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
    body = f"{name} checked in at {location} at {ts}."
    msg = MIMEText(body)
    msg["Subject"] = f"{location} Check-In: {name}"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
        s.send_message(msg)


@app.route("/", methods=["GET", "POST"])
def select_area():
    if request.method == "POST":
        area = request.form.get("area")
        if not area:
            flash("Please select an area.", "error")
            return redirect(url_for("select_area"))
        session["area"] = area
        return redirect(url_for("checkin"))
    return render_template("select_area.html")


@app.route("/checkin", methods=["GET", "POST"])
def checkin():
    if "area" not in session:
        return redirect(url_for("select_area"))

    if request.method == "POST":
        entry = request.form.get("entry", "").strip()
        lowered = entry.lower()
        if not entry:
            flash("Please scan card or enter your name", "error")
            return redirect(url_for("checkin"))
        elif lowered in CARD_TO_NAME:
            session["name"] = CARD_TO_NAME[lowered]
            return redirect(url_for("confirm"))
        elif entry in NAMES:
            session["name"] = entry
            return redirect(url_for("confirm"))
        else:
            flash("This card or name could not be matched. Try manually entering your name below.", "error")
            return redirect(url_for("checkin"))

    return render_template("checkin.html", names=sorted(NAMES), cards=list(CARD_TO_NAME))


@app.route("/confirm", methods=["GET", "POST"])
def confirm():
    name = session.get("name")
    area = session.get("area")
    if not name or not area:
        return redirect(url_for("select_area"))

    if request.method == "POST":
        action = request.form.get("action")
        if action == "confirm":
            send_notification(name, area)
            flash(f"Checked in: {name} at {area}", "success")
            session.clear()
            return redirect(url_for("select_area"))
        elif action == "cancel":
            return redirect(url_for("checkin"))

    return render_template("confirm.html", name=name, area=area)
