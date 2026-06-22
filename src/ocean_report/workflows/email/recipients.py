"""Email recipient management."""

import time
from ...logger import logger
from ...use_cases.email import get_email_recipients


def get_bcc_recipients(
    *, test: bool, use_url: bool, fallback_recipients: str
) -> list[str]:
    """Get and parse BCC recipient list from URL or config.

    Args:
        test: Whether to use test recipients
        use_url: If True, fetch from URL; if False, use fallback
        fallback_recipients: Comma-separated fallback recipient string

    Returns:
        List of cleaned email addresses
    """
    if use_url:
        logger.debug("  → Fetching recipients from URL (test=%s)", test)
        fetch_start = time.time()
        recipients_str = get_email_recipients(test_recips=test)
        logger.debug(
            "  ✓ Recipients fetched from URL in %.2f seconds",
            time.time() - fetch_start,
        )
    else:
        logger.debug("  → Using fallback recipients from config")
        recipients_str = fallback_recipients or ""

    return [email.strip() for email in recipients_str.split(",") if email.strip()]
