"""Application context for dependency management.

This module defines the ApplicationContext dataclass that holds shared
application dependencies including configuration and HTTP client instances.
"""

from dataclasses import dataclass

from ..api_client.client import ApiClient
from ..config.loader import AppConfig


@dataclass(frozen=True, slots=True)
class ApplicationContext:
    """
    Shared application dependencies.

    Contains application configuration and infrastructure
    services that are reused throughout the project.
    """

    config: AppConfig
    client: ApiClient
