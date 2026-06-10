"""Shared HTTP API client for outbound requests."""

from __future__ import annotations

import certifi
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
        self.session = self._build_session()

    def _build_session(self) -> requests.Session:
        """Create a shared session with retry behavior from config."""

        retry = Retry(
            total=self.max_retries,
            connect=self.max_retries,
            read=self.max_retries,
            status=self.max_retries,
            backoff_factor=self.backoff_seconds,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)

        session = requests.Session()
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def _resolve_verify(self) -> str | bool:
        return certifi.where() if self.verify_ssl else False

    def get(self, url: str, **kwargs) -> requests.Response | None:
        """Perform a GET with configured defaults and optional SSL fallback."""

        timeout = kwargs.pop("timeout", self.timeout)
        verify = kwargs.pop("verify", self._resolve_verify())

        try:
            return self.session.get(url, timeout=timeout, verify=verify, **kwargs)
        except requests.exceptions.SSLError as exc:
            if not self.retry_insecure_on_ssl_error:
                raise

            logger.warning(
                "SSL verification failed (%s). Retrying with verify=False.",
                exc,
            )
            try:
                return self.session.get(url, timeout=timeout, verify=False, **kwargs)
            except requests.exceptions.RequestException as retry_exc:
                logger.error("Request failed even with verify=False: %s", retry_exc)
                return None
        except requests.exceptions.RequestException as exc:
            logger.error("Request failed: %s", exc)
            return None


__all__ = ["ApiClient"]
