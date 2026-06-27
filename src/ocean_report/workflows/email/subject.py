"""Format the email subject line for the ocean report."""

from datetime import date


def format_email_subject(today: date, test: bool = False) -> str:
    """Format the email subject line."""
    subject = f"🌊 LBI Daily Water Report: {today.strftime('%Y-%m-%d')}"
    if test:
        subject = f"TEST: {subject}"
    return subject
