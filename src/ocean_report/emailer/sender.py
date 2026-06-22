"""Email sending module for ocean report."""

import smtplib
import time
from dataclasses import dataclass, field
from email.mime.text import MIMEText
from typing import List, Optional

from ..logger import logger
# from ..application.context import ApplicationContext

# from .config import get_settings


@dataclass(frozen=True)
class EmailRecipients:
    """Container for primary and BCC recipients."""

    to_email: str = ""
    bcc_list: List[str] = field(default_factory=list)


def send_email(  # pylint: disable=too-many-arguments,too-many-locals,too-many-statements
    *,
    subject: str = "🌊 Daily Water Report",
    body: str = "Here is the daily water report.",
    sender_email: str = "from-person@example.com",
    email_password: Optional[str] = None,
    recipients: Optional[EmailRecipients] = None,
    smtp_server: Optional[str] = None,
    smtp_port: Optional[int] = None,
) -> None:
    """Send email using SMTP."""
    operation_start = time.time()

    if email_password is None:
        raise ValueError("Email password must be provided.")

    # smtp_server = context.config.email.smtp_server
    # smtp_port = context.config.email.smtp_port

    to_email = "" if recipients is None else recipients.to_email
    bcc_list = [] if recipients is None else recipients.bcc_list

    if to_email == "example-recipient@gmail.com" or to_email is None:
        to_email = ""

    if not bcc_list:
        bcc_list = [""]

    logger.debug("    → Preparing email message...")
    logger.debug("    → From: %s", sender_email)
    logger.debug("    → To: %s", to_email if to_email else "(none)")
    logger.debug("    → BCC: %d recipients", len(bcc_list))
    logger.debug("    → Subject: %s", subject)

    # Construct the email message
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Bcc"] = ", ".join(bcc_list)  # ✅ Use commas per RFC 5322

    logger.debug(
        "    ✓ Email message constructed in %.3f seconds", time.time() - operation_start
    )

    # Connect to the SMTP server and send the email
    logger.info("    → Connecting to SMTP server: %s:%s", smtp_server, smtp_port)
    smtp_start = time.time()

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            connect_time = time.time() - smtp_start
            logger.debug(
                "    ✓ SMTP connection established in %.2f seconds", connect_time
            )

            logger.debug("    → Starting TLS upgrade...")
            tls_start = time.time()
            server.starttls()  # Upgrade the connection to secure
            logger.debug(
                "    ✓ TLS upgrade completed in %.2f seconds", time.time() - tls_start
            )

            logger.debug("    → Authenticating with SMTP server...")
            auth_start = time.time()
            server.login(sender_email, email_password)
            logger.debug(
                "    ✓ SMTP authentication succeeded in %.2f seconds",
                time.time() - auth_start,
            )

            logger.debug("    → Sending email message...")
            send_start = time.time()
            server.send_message(msg)  # Send the message
            logger.debug(
                "    ✓ Email message sent in %.2f seconds", time.time() - send_start
            )

        total_smtp_time = time.time() - smtp_start
        total_operation_time = time.time() - operation_start

        logger.info("    ✓ Email sent successfully!")
        logger.info("    ✓ SMTP operations took %.2f seconds total", total_smtp_time)
        logger.info(
            "    ✓ Complete email operation took %.2f seconds", total_operation_time
        )

    except smtplib.SMTPException as e:
        logger.error(
            "    ✗ SMTP error after %.2f seconds: %s", time.time() - smtp_start, e
        )
        raise
    except Exception as e:
        logger.error(
            "    ✗ Unexpected error during email send after %.2f seconds: %s",
            time.time() - smtp_start,
            e,
        )
        raise
