from dataclasses import dataclass

from .client import ApiClient
from ..config.schemas import AppConfig


@dataclass(slots=True)
class ApiContext:
    config: AppConfig
    client: ApiClient

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
