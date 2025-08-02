
from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime
import os, json
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

VIN_HISTORY_FILE = "vin_history.json"
vin_history = {}
if os.path.exists(VIN_HISTORY_FILE):
    with open(VIN_HISTORY_FILE, "r") as f:
        vin_history = json.load(f)

def save_vin_history():
    with open(VIN_HISTORY_FILE, "w") as f:
        json.dump(vin_history, f, indent=2)

@app.route("/", methods=["GET","POST"])
def dealer():
    if request.method == "POST":
        vin = request.form.get("vin")
        distance = request.form.get("distance")
        email = request.form.get("user_email")
        phone = request.form.get("user_phone")

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if vin not in vin_history:
            vin_history[vin] = []
        vin_history[vin].append({
            "email": email,
            "phone": phone,
            "date": now,
            "distance": distance
        })
        save_vin_history()

        photos = request.files.getlist("photos")
        for idx, photo in enumerate(photos[:12]):
            filename = secure_filename(f"{vin}_{now}_{idx}_{photo.filename}")
            photo.save(os.path.join(UPLOAD_FOLDER, filename))

        return render_template("thank_you.html")
    return render_template("dealer.html")

@app.route("/submissions")
def submissions():
    return render_template("submissions.html", vin_history=vin_history)

@app.route("/admin")
def admin():
    return "<h1>Admin Dashboard Coming Soon</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
