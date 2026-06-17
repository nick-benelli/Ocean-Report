"""Email sending operations."""

import time
from ...application import ApplicationContext
from ...emailer import sender as emailer
from ...logger import logger
from .preview import write_email_preview
from .validator import validate_email_credentials


def send_or_preview_email(
    *,
    context: ApplicationContext,
    run_email: bool,
    subject: str,
    body: str,
    bcc_recipients: list[str],
) -> None:
    """Send email via SMTP or print preview to console.

    Args:
        context: Application context containing config
        run_email: If True, send via SMTP; if False, print to console
        subject: Email subject line
        body: Email body content
        bcc_recipients: List of BCC recipient email addresses
    """
    email_recipients = context.config.email.recipients or ""
    sender_email = context.config.email.sender
    email_password = context.config.email.password

    if run_email:
        _send_via_smtp(
            context=context,
            subject=subject,
            body=body,
            sender_email=sender_email,
            email_password=email_password,
            email_recipients=email_recipients,
            bcc_recipients=bcc_recipients,
        )
    else:
        _print_preview(
            subject=subject,
            body=body,
            sender_email=sender_email,
            email_recipients=email_recipients,
            bcc_recipients=bcc_recipients,
        )


def _send_via_smtp(  # pylint: disable=too-many-arguments
    *,
    context: ApplicationContext,
    subject: str,
    body: str,
    sender_email: str | None,
    email_password: str | None,
    email_recipients: str,
    bcc_recipients: list[str],
) -> None:
    """Send email via SMTP server."""
    logger.info("  → Validating email configuration...")
    validate_email_credentials(sender_email, email_password)
    logger.debug("  ✓ Email configuration validated")

    logger.info(
        "  → Connecting to SMTP and sending to %d recipients...",
        len(bcc_recipients),
    )
    logger.debug("  → Sender: %s", sender_email)
    send_start = time.time()
    emailer.send_email(
        subject=subject,
        body=body,
        sender_email=sender_email,
        email_password=email_password,
        recipients=emailer.EmailRecipients(
            to_email=email_recipients,
            bcc_list=bcc_recipients,
        ),
        smtp_server=context.config.email.smtp_server,
        smtp_port=context.config.email.smtp_port,
    )
    logger.info(
        "  ✓ Email sent successfully via SMTP in %.2f seconds",
        time.time() - send_start,
    )


def _print_preview(
    *,
    subject: str,
    body: str,
    sender_email: str | None,
    email_recipients: str,
    bcc_recipients: list[str],
) -> None:
    """Print email preview to console and write preview files."""
    logger.info("  → Displaying email content (NOT sending):")
    print(
        f"\nTo: {email_recipients}\n"
        f"BCC: {', '.join(bcc_recipients)}\n"
        f"From: {sender_email}\n\n"
        f"Subject: {subject}\n\n"
        f"{body}"
    )
    logger.info("Email content printed to console.")

    # Write email preview files
    logger.info("  → Writing email preview files...")
    html_file = write_email_preview(
        subject=subject,
        body=body,
        sender_email=sender_email or "",
        email_recipients=email_recipients,
        bcc_recipients=bcc_recipients,
    )
    logger.info("  ✓ Email preview saved:")
    logger.info("    • HTML: %s", html_file)
    logger.info("    • Text: %s", html_file.with_suffix(".txt"))
    print("\n📁 Email preview files saved:")
    print(f"   • Open in browser: open {html_file}")
    print(f"   • View text: cat {html_file.with_suffix('.txt')}")
