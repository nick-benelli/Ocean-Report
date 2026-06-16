class ApiClientError(Exception):
    """Base exception for all HTTP transport errors raised by ApiClient."""


class ApiConnectionError(ApiClientError):
    """Raised when a request fails due to transport or connectivity issues."""


class ApiResponseError(ApiClientError):
    """Raised when an HTTP response is unsuccessful or invalid."""


class ApiSslError(ApiConnectionError):
    """Raised when TLS/SSL negotiation or certificate validation fails."""
