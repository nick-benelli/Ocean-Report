"""Address fetcher module for ocean report."""


import json
from ..api_client.client import ApiClient
from ..logger import logger

def fetch_recipients_from_gist(
    *,
    client: ApiClient,
    url: str,
) -> str:
    """
    Fetches the raw email recipient list from a public Gist URL.

    Args:
        client: HTTP client for making the request.
        url: URL to the Gist raw text file.

    Returns:
        str: Raw string content of the Gist.

    Raises:
        ValueError: If the URL is empty.
        ApiClientError: If the request fails (connection, SSL, or HTTP error).
    """
    if not url:
        raise ValueError("Gist URL is not set.")

    logger.info("Fetching recipients from Gist: %s", url)
    response = client.get(url)
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
