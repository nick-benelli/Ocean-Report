"""Factory for creating configured ApiClient instances.

This module provides a clean factory function that constructs ApiClient instances
from validated configuration objects. The factory promotes dependency injection
by accepting AppConfig rather than loading configuration itself.
"""

from __future__ import annotations

import requests

from .client import ApiClient
from ..config.schemas import AppConfig


def create_api_client(
    config: AppConfig,
    session: requests.Session | None = None,
) -> ApiClient:
    """Create a fully configured ApiClient from validated application config.

    This factory extracts HTTP client settings from AppConfig.api and constructs
    an ApiClient with proper timeout, SSL verification, retry behavior, and
    backoff configuration.

    The factory is pure and stateless - it does not load configuration from disk
    or maintain any global state. All behavior is controlled by the provided config.

    Args:
        config: Validated application configuration containing API client settings.
        session: Optional pre-configured requests.Session. If None, the ApiClient
            will create its own session with retry adapters. Useful for testing
            or when sharing a session pool across multiple clients.

    Returns:
        Configured ApiClient ready for making HTTP requests.

    Example:
        >>> from ocean_report.config.loader import load_config
        >>> config = load_config("config.yaml")
        >>> client = create_api_client(config)
        >>> response = client.get("https://api.example.com/data")
    """
    return ApiClient(
        timeout=config.api.timeout_seconds,
        verify_ssl=config.api.verify_ssl,
        retry_insecure_on_ssl_error=config.api.retry_insecure_on_ssl_error,
        max_retries=config.api.max_retries,
        backoff_seconds=config.api.backoff_seconds,
        session=session,
    )
