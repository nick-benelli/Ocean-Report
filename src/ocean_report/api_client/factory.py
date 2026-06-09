"""Factories for building API clients from app config."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..config import get_settings
from .client import ApiClient

if TYPE_CHECKING:
    from ..config.schemas import AppConfig




def get_api_client_from_config(settings: AppConfig | None = None) -> ApiClient:
    """Build an API client from config settings.

    If settings are not passed, this function loads validated settings via get_settings().
    """

    resolved_settings = settings or get_settings()
    api_config = resolved_settings.api
    return ApiClient(
        timeout=api_config.timeout_seconds,
        verify_ssl=api_config.verify_ssl,
        retry_insecure_on_ssl_error=api_config.retry_insecure_on_ssl_error,
        max_retries=api_config.max_retries,
        backoff_seconds=api_config.backoff_seconds,
    )


def get_api_client_from_config_path(config_path: str) -> ApiClient:
    """Build an API client from a specific config path."""

    settings = get_settings(config_path)
    return get_api_client_from_config(settings)


def get_api_client() -> ApiClient:
    """Backward-compatible alias for the config-backed API client factory."""

    return get_api_client_from_config()


__all__ = [
    "get_api_client",
    "get_api_client_from_config",
    "get_api_client_from_config_path",
]
