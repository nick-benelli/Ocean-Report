"""Utility functions for ocean report."""


from collections.abc import Mapping

import requests
from ..api_client.factory import create_api_client
from ..api_client.exceptions import ApiClientError

from ..logger import logger


def safe_get(
    url: str,
    *,
    params: Mapping[str, object] | None = None,
    headers: Mapping[str, str] | None = None,
    timeout: float | tuple[float, float] | None = None,
    verify: bool | str | None = None,
    allow_redirects: bool = True,
) -> requests.Response | None:
    """
    Perform a GET request using the shared API client configuration.
    """
    try:
        return create_api_client().get(
            url,
            params=params,
            headers=headers,
            timeout=timeout,
            verify=verify,
            allow_redirects=allow_redirects,
        )
    except ApiClientError as exc:
        logger.error("Request failed for URL: %s", url)
        logger.debug("Request failure details for %s: %s", url, exc)
        return None


