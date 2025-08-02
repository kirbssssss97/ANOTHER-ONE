from flask import Flask, request, render_template, redirect, url_for, session
from werkzeug.utils import secure_filename
import os, json, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

VIN_HISTORY_FILE = "vin_history.json"
vin_history = {}
if os.path.exists(VIN_HISTORY_FILE):
    with open(VIN_HISTORY_FILE, "r") as f:
        vin_history = json.load(f)

ADMIN_USER = "admin@gatewayleasing.com"
ADMIN_PASS = "password123"

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def save_vin_history():
    with open(VIN_HISTORY_FILE, "w") as f:
        json.dump(vin_history, f, indent=2)

def send_email_copy(to_email, vin, kms):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = f"Appraisal Submitted: {vin}"
    body = f"Thank you for submitting the appraisal for VIN {vin}.\nKMs: {kms}\nWe'll get you a value shortly."
    msg.attach(MIMEText(body, "plain"))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("Email error:", e)

@app.route("/", methods=["GET"])
def dealer_page():
    return render_template("dealer.html")

@app.route("/submit", methods=["POST"])
def submit():
    vin = request.form.get("vin")
    kms = request.form.get("kms")
    email = request.form.get("email")
    send_copy = request.form.get("send_copy")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if vin not in vin_history:
        vin_history[vin] = []
    vin_history[vin].append({"kms": kms, "date": now, "email": email})
    save_vin_history()

    photos = request.files.getlist("photos")
    for idx, photo in enumerate(photos[:12]):
        filename = secure_filename(f"{vin}_{now}_{idx}_{photo.filename}")
        photo.save(os.path.join(UPLOAD_FOLDER, filename))

    if send_copy and email:
        send_email_copy(email, vin, kms)

    return render_template("thankyou.html")

@app.route("/admin", methods=["GET"])
def admin():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("admin.html", vin_history=vin_history)

@app.route("/login", methods=["GET","POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_USER and password == ADMIN_PASS:
            session["logged_in"] = True
            return redirect(url_for("admin"))
        else:
            error = "Invalid username or password"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81)
