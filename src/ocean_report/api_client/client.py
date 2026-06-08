"""Shared HTTP API client for outbound requests."""

from __future__ import annotations

import certifi
import requests

from ..logger import logger


class ApiClient:
    """Simple client wrapper that standardizes timeout and SSL behavior."""

    def __init__(
        self,
        timeout: float = 10.0,
        verify_ssl: bool = True,
        retry_insecure_on_ssl_error: bool = True,
        max_retries: int = 3,
        backoff_seconds: float = 0.8,
    ) -> None:
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.retry_insecure_on_ssl_error = retry_insecure_on_ssl_error
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

    def _resolve_verify(self) -> str | bool:
        return certifi.where() if self.verify_ssl else False

    def get(self, url: str, **kwargs) -> requests.Response | None:
        """Perform a GET with configured defaults and optional SSL fallback."""

        timeout = kwargs.pop("timeout", self.timeout)
        verify = kwargs.pop("verify", self._resolve_verify())

        try:
            return requests.get(url, timeout=timeout, verify=verify, **kwargs)
        except requests.exceptions.SSLError as exc:
            if not self.retry_insecure_on_ssl_error:
                raise

            logger.warning(
                "SSL verification failed (%s). Retrying with verify=False.",
                exc,
            )
            try:
                return requests.get(url, timeout=timeout, verify=False, **kwargs)
            except requests.exceptions.RequestException as retry_exc:
                logger.error("Request failed even with verify=False: %s", retry_exc)
                return None


__all__ = ["ApiClient"]
