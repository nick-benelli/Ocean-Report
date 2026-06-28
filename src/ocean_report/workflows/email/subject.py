"""Format the email subject line for the ocean report."""

from datetime import date
from ...emailer.template_helpers import format_short_date


def format_email_subject(
    subject_name: str, today: date = None, test: bool = False
) -> str:
    """
    Format the email subject line.

    Args:
        subject_name: The main subject of the email (e.g., "Ocean Report")
        today: The date to include in the subject line (defaults to current date)
        test: If True, prepend "TEST: " to the subject line
    Returns:
        Formatted email subject line (e.g., "Ocean Report • Jun 24, 2026")

    """
    subject = f"{subject_name} • {format_short_date(today)}"
    if test:
        subject = f"TEST: {subject}"
    return subject
