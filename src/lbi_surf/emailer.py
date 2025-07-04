import smtplib
from email.mime.text import MIMEText
from datetime import datetime


# Email config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "nbenelli.waterreport@gmail.com"
# EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECIPIENT = "nick.benelli12@gmail.com"


def send_email(
    subject="🌊 Daily Water Report",
    body="Here is the daily water",
    sender_email="yourapp@gmail.com",
    recipient_email="your@email.com",
    email_password="your_app_password",
):
    """
    Send an email.
    """
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email  # EMAIL_SENDER
    msg["To"] = recipient_email  # EMAIL_RECIPIENT

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(sender_email, email_password)
        server.send_message(msg)

    return None


def format_tide_for_email(tide_events):
    formatted = []
    for tide in tide_events:
        dt = datetime.strptime(tide["t"], "%Y-%m-%d %H:%M")
        time_str = dt.strftime("%-I:%M %p")  # e.g., 2:47 PM
        tide_type = "High Tide" if tide["type"] == "H" else "Low Tide"
        height = float(tide["v"])
        formatted.append(f"{tide_type} at {time_str} — {height:.1f} ft")
    return "\n".join(formatted)


def generate_email_body(tide_events, water_temp_fahrenheit):
    today = datetime.now().strftime("%A, %B %d, %Y")

    tide_section = format_tide_for_email(tide_events)

    body = (
        f"🌊 Daily Water Report – {today} 🌊\n\n"
        f"🌡️ Water Temperature: {water_temp_fahrenheit}\n\n"
        f"🌊 Tides:\n{tide_section}\n\n"
        # f"Have a great day on the water!"
    )
    return body
