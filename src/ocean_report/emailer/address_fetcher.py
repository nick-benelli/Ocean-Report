"""Address fetcher module for ocean report."""

import datetime as dt
import json
from typing import Optional

import requests

from ..config import get_settings
from ..logger import logger
from ..utils import determine_is_summer, safe_get


def get_recipients(verbose: bool = False, test_recips: bool = False) -> str:
    """
    Fetches and cleans a list of email recipients from the configured Gist.

    Args:
        verbose (bool): Whether to print parsed output for debugging.

    Returns:
        str: Cleaned, comma-separated string of email addresses.
    """
    settings = get_settings()
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


def fetch_recipients_from_gist(url: Optional[str] = None) -> str:
    """
    Fetches the raw email recipient list from a public Gist URL.

    Args:
        url (str): URL to the Gist raw text file.

    Returns:
        str: Raw string content of the Gist.

    Raises:
        ValueError: If the URL is not provided.
        requests.HTTPError: If the request fails.
    """

    if not url:
        raise ValueError("Gist URL is not set.")

    # response = requests.get(url)
    response = safe_get(url)
    if response is None:
        raise requests.HTTPError("Failed to retrieve Gist")
    return response.text


def parse_recipients(text: str, verbose: bool = False) -> str:
    """
    Cleans and parses the raw text into a comma-separated string of email addresses.

    Args:
        text (str): Raw text input.
        verbose (bool): Whether to print parsed output for debugging.

    Returns:
        str: Comma-separated list of cleaned email addresses.
    """
    # Replace commas with newlines, split lines, strip whitespace, and lowercase
    cleaned = [
        line.strip().lower()
        for line in text.replace(",", "\n").splitlines()
        if line.strip()
    ]

    if verbose:
        print(json.dumps(cleaned, indent=2))

    return ",".join(cleaned)
