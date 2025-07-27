import smtplib
from email.mime.text import MIMEText
from email.message import EmailMessage
from typing import Optional, List
from .config import config

# Email configuration constants
SMTP_SERVER = config["email"].get("smtp_server")
SMTP_PORT = config["email"].get("smtp_port")


def send_email(
    subject: str = "🌊 Daily Water Report",
    body: str = "Here is the daily water report.",
    sender_email: str = "from-person@example.com",
    recipient_email: str = "example-recipient@gmail.com",
    bcc_list: List[str] = [],
    email_password: Optional[str] = None,
) -> None:
    """
    Sends an email with the provided subject and body using SMTP.

    Args:
        subject (str): Subject of the email.
        body (str): Body content of the email.
        sender_email (str): Sender's email address.
        recipient_email (str): Recipient's email address.
        email_password (str): Password or app-specific password for the sender's email.

    Returns:
        None
    """
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
    return None
