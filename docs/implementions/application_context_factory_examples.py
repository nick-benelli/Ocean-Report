"""Usage Examples for ApplicationContext Factory

This document demonstrates all supported use cases for create_application_context().
"""

# =============================================================================
# Example 1: Default Production Path (Recommended)
# =============================================================================

from ocean_report.application.factory import create_application_context

# Load default configuration and create fully initialized context
# This is the primary production path - uses cached config for performance
context = create_application_context()

# Access configuration
print(f"API timeout: {context.config.api.timeout_seconds}s")

# Use the client
response = context.client.get("https://api.example.com/data")


# =============================================================================
# Example 2: Custom Configuration Path
# =============================================================================

# Load configuration from a non-default location
# Useful for multi-environment deployments (dev/staging/prod)
context = create_application_context(config_path="config/production.yaml")

# Or using Path object
from pathlib import Path

config_file = Path("config") / "staging.yaml"
context = create_application_context(config_path=config_file)


# =============================================================================
# Example 3: Pre-loaded Configuration
# =============================================================================

from ocean_report.config.loader import load_app_config

# Load and potentially modify configuration before creating context
config = load_app_config("config.yaml")

# Create context from the loaded config
context = create_application_context(config=config)


# =============================================================================
# Example 4: Pass-through Existing Context
# =============================================================================

# Create context once
main_context = create_application_context()


# Pass it through in functions that may or may not have a context
# This is useful for dependency injection patterns
def process_data(context: ApplicationContext | None = None):
    """Process data using provided or default context."""
    ctx = create_application_context(context=context)
    # Use ctx...


# Call with existing context (no-op, returns same instance)
process_data(context=main_context)

# Call without context (creates new one)
process_data()


# =============================================================================
# Example 5: Application Initialization Pattern
# =============================================================================


def initialize_application(env: str = "default"):
    """Initialize application with environment-specific configuration."""
    if env == "default":
        return create_application_context()
    else:
        config_path = f"config/{env}.yaml"
        return create_application_context(config_path=config_path)


# Usage
dev_context = initialize_application("dev")
prod_context = initialize_application("prod")
default_context = initialize_application()


# =============================================================================
# Example 6: Testing Pattern with Custom Config
# =============================================================================

import pytest
from ocean_report.config.schemas import AppConfig, ApiConfig


@pytest.fixture
def test_context():
    """Create test context with custom configuration."""
    # Build config programmatically for testing
    test_config = AppConfig(
        api=ApiConfig(
            timeout_seconds=5,
            verify_ssl=False,
            max_retries=1,
            backoff_seconds=0.1,
        ),
        # ... other config fields
    )
    return create_application_context(config=test_config)


def test_api_call(test_context):
    """Test using custom test context."""
    response = test_context.client.get("https://test.example.com")
    assert response.status_code == 200


# =============================================================================
# Example 7: Singleton Pattern (if needed)
# =============================================================================


class ApplicationService:
    """Service that maintains a single application context."""

    _context: ApplicationContext | None = None

    @classmethod
    def get_context(cls) -> ApplicationContext:
        """Get or create the singleton application context."""
        if cls._context is None:
            cls._context = create_application_context()
        return cls._context

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (useful for testing)."""
        cls._context = None


# Usage
context = ApplicationService.get_context()


# =============================================================================
# Example 8: Error Handling - Multiple Parameters
# =============================================================================

from ocean_report.config.loader import get_settings

try:
    # This will raise ValueError - can't provide both config and config_path
    config = get_settings()
    context = create_application_context(
        config=config,
        config_path="other.yaml",  # ERROR: ambiguous source
    )
except ValueError as e:
    print(f"Expected error: {e}")
    # Output: Only one of 'context', 'config', or 'config_path' may be provided...


# =============================================================================
# Example 9: Dependency Injection with FastAPI
# =============================================================================

from fastapi import FastAPI, Depends

# Create app-level context once at startup
app = FastAPI()
app_context = create_application_context()


def get_context() -> ApplicationContext:
    """Dependency that provides the application context."""
    return app_context


@app.get("/data")
async def fetch_data(context: ApplicationContext = Depends(get_context)):
    """Endpoint that uses injected context."""
    response = context.client.get("https://api.example.com/data")
    return response.json()


# =============================================================================
# Example 10: Context Manager Pattern (if needed)
# =============================================================================

from contextlib import contextmanager


@contextmanager
def application_context(config_path: str | None = None):
    """Context manager for application lifecycle."""
    if config_path:
        context = create_application_context(config_path=config_path)
    else:
        context = create_application_context()

    try:
        yield context
    finally:
        # Cleanup if needed (e.g., close connections)
        pass


# Usage
with application_context("config/prod.yaml") as ctx:
    response = ctx.client.get("https://api.example.com")
    print(response.json())
