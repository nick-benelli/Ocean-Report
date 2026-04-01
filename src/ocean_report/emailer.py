"""Email sending module for ocean report."""

import smtplib
from email.mime.text import MIMEText
from typing import List, Optional

from .config import config

# Email configuration constants
SMTP_SERVER = config["email"].get("smtp_server")
SMTP_PORT = config["email"].get("smtp_port")


def send_email(
    subject: str = "🌊 Daily Water Report",
    body: str = "Here is the daily water report.",
    sender_email: str = "from-person@example.com",
    recipient_email: str = "example-recipient@gmail.com",
    bcc_list: Optional[List[str]] = None,
    email_password: Optional[str] = None,
) -> None:
    """Send email using SMTP."""
    if bcc_list is None:
        bcc_list = []

    if email_password is None:
        raise ValueError("Email password must be provided.")

    if recipient_email == "example-recipient@gmail.com" or recipient_email is None:
        recipient_email = ""

    if bcc_list == []:
        bcc_list = [""]

    # Construct the email message
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Bcc"] = ", ".join(bcc_list)  # ✅ Use commas per RFC 5322

    # Connect to the SMTP server and send the email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()  # Upgrade the connection to secure
        server.login(sender_email, email_password)
        server.send_message(msg)  # Send the message

    # Optionally, log or print success message
    print("Email sent successfully.")
