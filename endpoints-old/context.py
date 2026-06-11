from __future__ import annotations

from dataclasses import dataclass
from os import PathLike

from .client import ApiClient
from ..config import get_settings
from ..config.schemas import AppConfig


@dataclass(slots=True)
class ApiContext:
    config: AppConfig
    client: ApiClient

    @classmethod
    def resolve(
        cls,
        context: "ApiContext" | None = None,
        config: AppConfig | None = None,
        config_path: str | PathLike[str] | None = None,
        client: ApiClient | None = None,
    ) -> "ApiContext":
        """Resolve any supported input into a fully built ApiContext.

        Rules:
        - If context is provided, return it as-is.
        - Else if config is provided, build context from config.
        - Else if config_path is provided, load config from path and build context.
        - Else load default settings and build context.
        - A client without config/config_path is rejected because it can produce
          a context that does not match intended config.
        """

        if context is not None:
            return context

        if client is not None and config is None and config_path is None:
            raise ValueError(
                "client requires config or config_path so ApiContext remains config-driven"
            )

        if config is not None:
            return cls.from_config(config=config, client=client)

        if config_path is not None:
            return cls.from_config_path(config_path=config_path, client=client)

        return cls.from_settings(client=client)

    @classmethod
    def from_config(cls, config: AppConfig, client: ApiClient | None = None) -> "ApiContext":
        # Keep one place that translates config -> client settings.
        resolved_client = client or ApiClient(
            timeout=config.api.timeout_seconds,
            verify_ssl=config.api.verify_ssl,
            retry_insecure_on_ssl_error=config.api.retry_insecure_on_ssl_error,
            max_retries=config.api.max_retries,
            backoff_seconds=config.api.backoff_seconds,
        )
        return cls(config=config, client=resolved_client)

    @classmethod
    def from_settings(
        cls,
        settings: AppConfig | None = None,
        client: ApiClient | None = None,
    ) -> "ApiContext":
        """Build context from provided settings or the default configured settings."""

        resolved_settings = settings or get_settings()
        return cls.from_config(config=resolved_settings, client=client)

    @classmethod
    def from_config_path(
        cls,
        config_path: str | PathLike[str],
        client: ApiClient | None = None,
    ) -> "ApiContext":
        """Build context from a specific config file path."""

        return cls.from_settings(settings=get_settings(config_path), client=client)


__all__ = ["ApiContext"]
