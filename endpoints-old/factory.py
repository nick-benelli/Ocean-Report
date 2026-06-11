"""Factories for building API contexts and clients from app config."""

from __future__ import annotations

from os import PathLike
from typing import TYPE_CHECKING

from .context import ApiContext

if TYPE_CHECKING:
    from .client import ApiClient
    from ..config.schemas import AppConfig


def get_api_context(settings: AppConfig | None = None) -> ApiContext:
    """Build an API context from config settings.

    If settings are not passed, this function loads default validated settings.
    """

    return ApiContext.resolve(config=settings)


def get_api_context_from_config_path(config_path: str | PathLike[str]) -> ApiContext:
    """Build an API context from a specific config path."""

    return ApiContext.resolve(config_path=config_path)


def get_api_client_from_config(settings: AppConfig | None = None) -> ApiClient:
    """Build an API client from config settings.

    If settings are not passed, this function loads default validated settings.
    """

    return get_api_context(settings).client


def get_api_client_from_config_path(config_path: str | PathLike[str]) -> ApiClient:
    """Build an API client from a specific config path."""

    return get_api_context_from_config_path(config_path).client


def get_api_client() -> ApiClient:
    """Backward-compatible alias for the config-backed API client factory."""

    return get_api_context().client


__all__ = [
    "get_api_context",
    "get_api_context_from_config_path",
    "get_api_client",
    "get_api_client_from_config",
    "get_api_client_from_config_path",
]