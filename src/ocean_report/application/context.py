
from dataclasses import dataclass
from ..config.loader import AppConfig
from ..api_client.client import ApiClient


@dataclass(frozen=True, slots=True)
class ApplicationContext:
    """
    Shared application dependencies.

    Contains application configuration and infrastructure
    services that are reused throughout the project.
    """
    config: AppConfig
    client: ApiClient
