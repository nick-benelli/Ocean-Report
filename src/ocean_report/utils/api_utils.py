"""Utility functions for ocean report."""


from typing import Optional

import requests
from ..api_client import get_api_client
from ..logger import logger


def safe_get(url: str, **kwargs) -> Optional[requests.Response]:
    """
    Perform a GET request using the shared API client configuration.
    """
    response = get_api_client().get(url, **kwargs)
    if response is None:
        logger.error("Request failed for URL: %s", url)
    return response


