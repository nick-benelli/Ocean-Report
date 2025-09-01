import requests
import json
from typing import Optional
import datetime as dt
from .utils import safe_get
from .config import (
    RECIPIENTS_GIST_URL,
    TEST_RECIPIENTS_GIST_URL,
    OFFSEASON_RECIPIENTS_GIST_URL,
)


def get_recipients(verbose: bool = False, test_recips: bool = False) -> str:
    """
    Fetches and cleans a list of email recipients from the configured Gist.

    Args:
        verbose (bool): Whether to print parsed output for debugging.

    Returns:
        str: Cleaned, comma-separated string of email addresses.
    """
    current_month = dt.datetime.now().month
    is_summer = current_month >= 6 and current_month <= 9

    if is_summer:
        print("It's summer!")
    else:
        print("It's winter!")

    if test_recips:
        print("Using test recipients.")
        url = TEST_RECIPIENTS_GIST_URL
    else:
        if is_summer:
            print("Using regular recipients URL.")
            url = RECIPIENTS_GIST_URL
        else:
            print("Using offseason recipients URL.")
            url = OFFSEASON_RECIPIENTS_GIST_URL

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
