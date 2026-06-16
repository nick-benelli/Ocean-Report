import datetime as dt
from ocean_report.emailer.address_fetcher import (
    fetch_recipients_from_gist,
    parse_recipients,
)
from ..application.context import ApplicationContext
from ..application.factory import create_application_context
from ..logger import logger
from ..utils import determine_is_summer


def get_email_recipients(
    *,
    context: ApplicationContext | None = None,
    test_recips: bool = False,
    verbose: bool = False,
) -> str:
    """
    Fetches and cleans a list of email recipients from the configured Gist.

    Args:
        verbose (bool): Whether to print parsed output for debugging.

    Returns:
        str: Cleaned, comma-separated string of email addresses.
    """

    if context is None:
        logger.warning("No application context provided, using default settings.")
        # context = create_application_context() --- IGNORE ---
        context = create_application_context()

    settings = context.config

    # settings = get_settings()
    is_summer = determine_is_summer(
        today=dt.date.today(),
        memorial_day_offset=settings.summer.memorial_day_offset,
        labor_day_offset=settings.summer.labor_day_offset,
    )

    if is_summer:
        logger.info("It's summer!")
    else:
        logger.info("It's winter!")

    if test_recips:
        logger.info("Using test recipients.")
        url = settings.email.recipient_urls.test
    else:
        if is_summer:
            logger.info("Using regular recipients URL.")
            url = settings.email.recipient_urls.main
        else:
            logger.info("Using offseason recipients URL.")
            url = settings.email.recipient_urls.offseason

    raw_text = fetch_recipients_from_gist(url=url)
    return parse_recipients(raw_text, verbose=verbose)
