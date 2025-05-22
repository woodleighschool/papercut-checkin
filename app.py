import csv
import os
from flask import Flask, render_template, request, flash
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT   = int(os.getenv("SMTP_PORT", 25))
EMAIL_FROM  = os.getenv("EMAIL_FROM")
EMAIL_TO    = os.getenv("EMAIL_TO")

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
            cid = row.get(col, "").strip()
            if cid:
                CARD_TO_NAME[cid] = name

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "change-me")

def send_notification(name: str):
    ts = datetime.now().strftime("%H:%M:%S %d-%m-%Y")
    body = f"{name} checked in at learning enhancement at {ts}."
    msg = MIMEText(body)
    msg["Subject"] = f"Learning Enhancement Check-In: {name}"
    msg["From"]    = EMAIL_FROM
    msg["To"]      = EMAIL_TO
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as s:
        s.send_message(msg)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        entry = request.form.get("entry", "").strip()
        if not entry:
            flash("Please scan card or enter a name", "error")
            return render_template("index.html", names=sorted(NAMES), cards=list(CARD_TO_NAME))
        # card?
        if entry in CARD_TO_NAME:
            name = CARD_TO_NAME[entry]
        # name?
        elif entry in NAMES:
            name = entry
        else:
            flash("Entry not recognized", "error")
            return render_template("index.html", names=sorted(NAMES), cards=list(CARD_TO_NAME))

        #send_notification(name)
        flash(f"Checked in: {name}", "success")
        # fall through to re-render the empty form

    return render_template("index.html", names=sorted(NAMES), cards=list(CARD_TO_NAME))
