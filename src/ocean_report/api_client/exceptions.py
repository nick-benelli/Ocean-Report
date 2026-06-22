"""Custom exceptions for HTTP transport errors in ApiClient.

This module defines a hierarchy of exceptions that ApiClient raises when
HTTP requests fail due to connection issues, SSL errors, or unsuccessful
HTTP response codes.
"""


class ApiClientError(Exception):
    """Base exception for all HTTP transport errors raised by ApiClient."""


class ApiConnectionError(ApiClientError):
    """Raised when a request fails due to transport or connectivity issues."""


class ApiResponseError(ApiClientError):
    """Raised when an HTTP response is unsuccessful or invalid."""


class ApiSslError(ApiConnectionError):
    """Raised when TLS/SSL negotiation or certificate validation fails."""
