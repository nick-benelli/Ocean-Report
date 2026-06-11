"""Application context and factory for Ocean Report.

This module provides the core application context and factory for constructing
fully initialized ApplicationContext instances with validated configuration.
"""

from .context import ApplicationContext
from .factory import create_application_context

__all__ = [
    "ApplicationContext",
    "create_application_context",
]
