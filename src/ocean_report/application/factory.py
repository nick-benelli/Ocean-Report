"""Factory for creating ApplicationContext instances.

This module provides the single entry point for constructing ApplicationContext
with validated configuration. The factory ensures configuration consistency by
always creating the ApiClient from AppConfig, never accepting pre-built clients.

The factory supports four clear use cases:
1. Return an existing context unchanged (no-op for dependency injection)
2. Create context from a pre-loaded AppConfig instance
3. Create context by loading config from a specified path
4. Create context using default configuration (primary production path)
"""

from __future__ import annotations

from pathlib import Path

from .context import ApplicationContext
from ..api_client.factory import create_api_client
from ..config.loader import get_settings, load_app_config
from ..config.schemas import AppConfig


def create_application_context(
    *,
    context: ApplicationContext | None = None,
    config: AppConfig | None = None,
    config_path: str | Path | None = None,
) -> ApplicationContext:
    """Create or return an ApplicationContext instance.

    This factory is the single entry point for constructing ApplicationContext.
    It enforces mutual exclusivity between parameters to prevent ambiguous
    configuration sources and always creates the ApiClient from configuration
    to maintain consistency.

    Args:
        context: Existing ApplicationContext to return unchanged. Use this for
            dependency injection scenarios where you want to pass through an
            already-constructed context. This is a no-op that returns the
            provided context as-is.
        config: Pre-loaded and validated AppConfig instance. Use this when you've
            already loaded or constructed configuration and want to create a new
            context from it. The factory will create an ApiClient from this config.
        config_path: Path to a YAML configuration file. Use this to load config
            from a non-default location. The factory will load, validate, and
            create both ApiClient and ApplicationContext from this file.

    Returns:
        ApplicationContext: Fully initialized context with config and client.
            If `context` was provided, returns it unchanged. Otherwise, returns
            a new ApplicationContext with a freshly-created ApiClient.

    Raises:
        ValueError: If more than one parameter is provided. Only one source of
            configuration is allowed to prevent ambiguous behavior.

    Examples:
        Create context with default configuration (primary production use):
        >>> context = create_application_context()

        Create context from pre-loaded config:
        >>> config = load_app_config("custom.yaml")
        >>> context = create_application_context(config=config)

        Create context from config file path:
        >>> context = create_application_context(
        ...     config_path="config/prod.yaml"
        ... )

        Pass through existing context (dependency injection):
        >>> existing = create_application_context()
        >>> same = create_application_context(context=existing)
        >>> assert same is existing

    Design Notes:
        - The factory does NOT accept a `client` parameter. ApiClient must always
          be created from AppConfig to ensure configuration consistency.
        - Parameter validation happens before any I/O operations to fail fast.
        - The default case (no parameters) loads cached configuration via
          get_settings() for optimal performance in production.
    """
    # Validate mutual exclusivity - only one parameter may be provided
    provided_params = sum([
        context is not None,
        config is not None,
        config_path is not None,
    ])

    if provided_params > 1:
        raise ValueError(
            "Only one of 'context', 'config', or 'config_path' may be provided. "
            "Multiple parameters create ambiguous configuration sources."
        )

    # Rule 1: Return existing context unchanged (no-op)
    if context is not None:
        return context

    # Rule 2: Create from provided config
    if config is not None:
        client = create_api_client(config)
        return ApplicationContext(config=config, client=client)

    # Rule 3: Load config from specified path
    if config_path is not None:
        config = load_app_config(config_path)
        client = create_api_client(config)
        return ApplicationContext(config=config, client=client)

    # Rule 4: Default production path - load cached default config
    config = get_settings()
    client = create_api_client(config)
    return ApplicationContext(config=config, client=client)


__all__ = [
    "create_application_context",
]
