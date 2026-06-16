"""Shared HTTP API client for outbound requests."""

from __future__ import annotations

from collections.abc import Mapping
from types import TracebackType
from typing import Any

import certifi
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..logger import logger
from .exceptions import (
    ApiClientError,
    ApiConnectionError,
    ApiResponseError,
    ApiSslError,
)


RequestTimeout = float | tuple[float, float]
VerifyOption = bool | str


class ApiClient:
    """Reusable HTTP transport client with retries, SSL controls, and typed accessors.

    The client is intentionally transport-focused and does not contain API-specific
    behavior.
    """

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        timeout: float = 10.0,
        verify_ssl: bool = True,
        retry_insecure_on_ssl_error: bool = True,
        max_retries: int = 3,
        backoff_seconds: float = 0.8,
        session: requests.Session | None = None,
    ) -> None:
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.retry_insecure_on_ssl_error = retry_insecure_on_ssl_error
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.session = session or self._build_session()
        self._closed = False

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

    def _log_retry_history(self, response: requests.Response, url: str) -> None:
        """Log retry metadata captured by urllib3 for observability."""

        retries = getattr(getattr(response, "raw", None), "retries", None)
        history = getattr(retries, "history", None)
        if not history:
            return

        try:
            retry_count = len(history)
        except TypeError:
            return

        if retry_count > 0:
            logger.info(
                "api.request_retried method=GET url=%s retry_count=%s status_code=%s",
                url,
                retry_count,
                response.status_code,
            )

    def _send_get(  # pylint: disable=too-many-arguments
        self,
        *,
        url: str,
        params: Mapping[str, object] | None,
        headers: Mapping[str, str] | None,
        timeout: RequestTimeout,
        verify: VerifyOption,
        allow_redirects: bool,
    ) -> requests.Response:
        """Send a GET request and normalize request/response errors."""

        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=timeout,
                verify=verify,
                allow_redirects=allow_redirects,
            )
        except requests.exceptions.SSLError as exc:
            raise ApiSslError(f"SSL request failed for GET {url}") from exc
        except requests.exceptions.RequestException as exc:
            raise ApiConnectionError(f"Connection failed for GET {url}") from exc

        self._log_retry_history(response, url)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise ApiResponseError(
                f"HTTP {response.status_code} returned for GET {url}"
            ) from exc
        return response

    def get(  # pylint: disable=too-many-arguments
        self,
        url: str,
        *,
        params: Mapping[str, object] | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: RequestTimeout | None = None,
        verify: VerifyOption | None = None,
        allow_redirects: bool = True,
    ) -> requests.Response:
        """Perform a GET request using configured transport defaults.

        This method automatically raises :class:`ApiResponseError` when the
        response status code is not successful.
        """

        resolved_timeout = timeout if timeout is not None else self.timeout
        resolved_verify = verify if verify is not None else self._resolve_verify()

        try:
            return self._send_get(
                url=url,
                params=params,
                headers=headers,
                timeout=resolved_timeout,
                verify=resolved_verify,
                allow_redirects=allow_redirects,
            )
        except ApiSslError:
            if not self.retry_insecure_on_ssl_error or verify is False:
                logger.error(
                    "api.request_ssl_failed method=GET url=%s retry_insecure=%s",
                    url,
                    self.retry_insecure_on_ssl_error,
                )
                raise

            logger.warning(
                "api.request_ssl_fallback method=GET url=%s action=retry_verify_false",
                url,
            )
            try:
                return self._send_get(
                    url=url,
                    params=params,
                    headers=headers,
                    timeout=resolved_timeout,
                    verify=False,
                    allow_redirects=allow_redirects,
                )
            except ApiClientError as retry_exc:
                logger.error(
                    "api.request_failed_after_ssl_fallback method=GET url=%s error=%s",
                    url,
                    retry_exc,
                )
                raise
        except ApiConnectionError:
            logger.error("api.request_connection_failed method=GET url=%s", url)
            raise
        except ApiResponseError:
            logger.error("api.request_response_error method=GET url=%s", url)
            raise

    def get_json(  # pylint: disable=too-many-arguments
        self,
        url: str,
        *,
        params: Mapping[str, object] | None = None,
        headers: Mapping[str, str] | None = None,
        timeout: RequestTimeout | None = None,
        verify: VerifyOption | None = None,
        allow_redirects: bool = True,
    ) -> Any:
        """Perform a GET request and parse the JSON response body."""

        response = self.get(
            url,
            params=params,
            headers=headers,
            timeout=timeout,
            verify=verify,
            allow_redirects=allow_redirects,
        )
        try:
            return response.json()
        except ValueError as exc:
            raise ApiResponseError(f"Invalid JSON returned for GET {url}") from exc

    def close(self) -> None:
        """Close the underlying HTTP session."""

        if self._closed:
            return
        self.session.close()
        self._closed = True

    def __enter__(self) -> "ApiClient":
        """Enter a context manager scope for this client."""

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Exit context manager scope and close the session."""

        self.close()


__all__ = [
    "ApiClient",
    "ApiClientError",
    "ApiConnectionError",
    "ApiResponseError",
    "ApiSslError",
]
