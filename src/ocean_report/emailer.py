"""Email sending module for ocean report."""

import smtplib
from dataclasses import dataclass, field
from email.mime.text import MIMEText
from typing import List, Optional

from .config import get_settings


@dataclass(frozen=True)
class EmailRecipients:
    """Container for primary and BCC recipients."""

    to_email: str = ""
    bcc_list: List[str] = field(default_factory=list)


def send_email(
    subject: str = "🌊 Daily Water Report",
    body: str = "Here is the daily water report.",
    sender_email: str = "from-person@example.com",
    email_password: Optional[str] = None,
    recipients: Optional[EmailRecipients] = None,
) -> None:
    """Send email using SMTP."""
    if email_password is None:
        raise ValueError("Email password must be provided.")

    settings = get_settings()
    smtp_server = settings.email.smtp_server
    smtp_port = settings.email.smtp_port

    to_email = "" if recipients is None else recipients.to_email
    bcc_list = [] if recipients is None else recipients.bcc_list

    if to_email == "example-recipient@gmail.com" or to_email is None:
        to_email = ""

    if not bcc_list:
        bcc_list = [""]

    # Construct the email message
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Bcc"] = ", ".join(bcc_list)  # ✅ Use commas per RFC 5322

    # Connect to the SMTP server and send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Upgrade the connection to secure
        server.login(sender_email, email_password)
        server.send_message(msg)  # Send the message

    # Optionally, log or print success message
    print("Email sent successfully.")
