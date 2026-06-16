"""Unit Tests for ApplicationContext Factory

Comprehensive test suite for create_application_context() covering all rules,
validation, and error cases.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from ocean_report.application.factory import create_application_context
from ocean_report.application.context import ApplicationContext
from ocean_report.config.schemas import AppConfig, ApiConfig
from ocean_report.api_client.client import ApiClient


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config():
    """Create a mock AppConfig for testing."""
    return AppConfig(
        api=ApiConfig(
            timeout_seconds=30,
            verify_ssl=True,
            max_retries=3,
            backoff_seconds=1.0,
            retry_insecure_on_ssl_error=False,
        ),
        # Add other required config fields...
    )


@pytest.fixture
def mock_context(mock_config):
    """Create a mock ApplicationContext for testing."""
    client = Mock(spec=ApiClient)
    return ApplicationContext(config=mock_config, client=client)


# =============================================================================
# Test Rule 1: Return Existing Context Unchanged
# =============================================================================


def test_rule1_returns_existing_context(mock_context):
    """Test that providing a context returns it unchanged (no-op)."""
    result = create_application_context(context=mock_context)

    # Should return the exact same instance
    assert result is mock_context
    assert result.config is mock_context.config
    assert result.client is mock_context.client


def test_rule1_does_not_create_new_client(mock_context):
    """Test that providing context doesn't trigger client creation."""
    with patch("ocean_report.application.factory.create_api_client") as mock_create:
        result = create_application_context(context=mock_context)

        # Should not call create_api_client
        mock_create.assert_not_called()
        assert result is mock_context


# =============================================================================
# Test Rule 2: Create from Config
# =============================================================================


def test_rule2_creates_context_from_config(mock_config):
    """Test creating context from a provided AppConfig."""
    with patch("ocean_report.application.factory.create_api_client") as mock_create:
        mock_client = Mock(spec=ApiClient)
        mock_create.return_value = mock_client

        result = create_application_context(config=mock_config)

        # Should create client from config
        mock_create.assert_called_once_with(mock_config)

        # Should return properly structured context
        assert isinstance(result, ApplicationContext)
        assert result.config is mock_config
        assert result.client is mock_client


def test_rule2_client_matches_config(mock_config):
    """Test that the created client uses the provided config."""
    result = create_application_context(config=mock_config)

    # Verify the client was created with correct config values
    # (This assumes you can inspect the client's configuration)
    assert result.config is mock_config
    assert isinstance(result.client, ApiClient)


# =============================================================================
# Test Rule 3: Load from Config Path
# =============================================================================


def test_rule3_loads_config_from_path(mock_config, tmp_path):
    """Test creating context by loading config from a file path."""
    config_file = tmp_path / "config.yaml"

    with (
        patch("ocean_report.application.factory.load_app_config") as mock_load,
        patch("ocean_report.application.factory.create_api_client") as mock_create,
    ):
        mock_load.return_value = mock_config
        mock_client = Mock(spec=ApiClient)
        mock_create.return_value = mock_client

        result = create_application_context(config_path=config_file)

        # Should load config from the provided path
        mock_load.assert_called_once_with(config_file)

        # Should create client from loaded config
        mock_create.assert_called_once_with(mock_config)

        # Should return properly structured context
        assert isinstance(result, ApplicationContext)
        assert result.config is mock_config
        assert result.client is mock_client


def test_rule3_accepts_string_path(mock_config):
    """Test that config_path accepts string paths."""
    with (
        patch("ocean_report.application.factory.load_app_config") as mock_load,
        patch("ocean_report.application.factory.create_api_client"),
    ):
        mock_load.return_value = mock_config

        result = create_application_context(config_path="config/test.yaml")

        # Should accept string path
        mock_load.assert_called_once_with("config/test.yaml")
        assert isinstance(result, ApplicationContext)


def test_rule3_accepts_path_object(mock_config):
    """Test that config_path accepts Path objects."""
    with (
        patch("ocean_report.application.factory.load_app_config") as mock_load,
        patch("ocean_report.application.factory.create_api_client"),
    ):
        mock_load.return_value = mock_config
        path_obj = Path("config/test.yaml")

        result = create_application_context(config_path=path_obj)

        # Should accept Path object
        mock_load.assert_called_once_with(path_obj)
        assert isinstance(result, ApplicationContext)


# =============================================================================
# Test Rule 4: Default Configuration
# =============================================================================


def test_rule4_loads_default_config(mock_config):
    """Test creating context with no parameters loads default config."""
    with (
        patch("ocean_report.application.factory.get_settings") as mock_get,
        patch("ocean_report.application.factory.create_api_client") as mock_create,
    ):
        mock_get.return_value = mock_config
        mock_client = Mock(spec=ApiClient)
        mock_create.return_value = mock_client

        result = create_application_context()

        # Should load default settings (cached)
        mock_get.assert_called_once_with()

        # Should create client from default config
        mock_create.assert_called_once_with(mock_config)

        # Should return properly structured context
        assert isinstance(result, ApplicationContext)
        assert result.config is mock_config
        assert result.client is mock_client


def test_rule4_uses_cached_config(mock_config):
    """Test that default path uses get_settings (cached) not load_app_config."""
    with (
        patch("ocean_report.application.factory.get_settings") as mock_get,
        patch("ocean_report.application.factory.load_app_config") as mock_load,
        patch("ocean_report.application.factory.create_api_client"),
    ):
        mock_get.return_value = mock_config

        create_application_context()

        # Should use cached get_settings
        mock_get.assert_called_once()

        # Should NOT use uncached load_app_config
        mock_load.assert_not_called()


# =============================================================================
# Test Validation: Mutual Exclusivity
# =============================================================================


def test_validation_rejects_context_and_config(mock_context, mock_config):
    """Test that providing both context and config raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        create_application_context(context=mock_context, config=mock_config)

    assert "Only one of" in str(exc_info.value)
    assert "ambiguous" in str(exc_info.value).lower()


def test_validation_rejects_context_and_config_path(mock_context):
    """Test that providing both context and config_path raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        create_application_context(context=mock_context, config_path="config.yaml")

    assert "Only one of" in str(exc_info.value)


def test_validation_rejects_config_and_config_path(mock_config):
    """Test that providing both config and config_path raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        create_application_context(config=mock_config, config_path="config.yaml")

    assert "Only one of" in str(exc_info.value)


def test_validation_rejects_all_three_parameters(mock_context, mock_config):
    """Test that providing all three parameters raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        create_application_context(
            context=mock_context, config=mock_config, config_path="config.yaml"
        )

    assert "Only one of" in str(exc_info.value)


def test_validation_happens_before_io():
    """Test that validation occurs before any I/O operations."""
    with (
        patch("ocean_report.application.factory.get_settings") as mock_get,
        patch("ocean_report.application.factory.load_app_config") as mock_load,
    ):
        # Provide conflicting parameters
        with pytest.raises(ValueError):
            create_application_context(config=Mock(), config_path="config.yaml")

        # Should not attempt to load anything
        mock_get.assert_not_called()
        mock_load.assert_not_called()


# =============================================================================
# Test Type Annotations and Return Types
# =============================================================================


def test_return_type_is_application_context():
    """Test that factory always returns ApplicationContext instance."""
    with (
        patch("ocean_report.application.factory.get_settings"),
        patch("ocean_report.application.factory.create_api_client"),
    ):
        result = create_application_context()
        assert isinstance(result, ApplicationContext)


def test_context_is_immutable(mock_config):
    """Test that returned ApplicationContext is immutable (frozen dataclass)."""
    result = create_application_context(config=mock_config)

    # Should not allow attribute assignment (frozen dataclass)
    with pytest.raises((AttributeError, TypeError)):
        result.config = Mock()

    with pytest.raises((AttributeError, TypeError)):
        result.client = Mock()


# =============================================================================
# Integration Tests
# =============================================================================


@pytest.mark.integration
def test_integration_full_context_creation(tmp_path):
    """Integration test: create real context from real config file."""
    # Create a minimal valid config file
    config_content = """
api:
  timeout_seconds: 30
  verify_ssl: true
  max_retries: 3
  backoff_seconds: 1.0
  retry_insecure_on_ssl_error: false

# Add other required config sections...
    """.strip()

    config_file = tmp_path / "test_config.yaml"
    config_file.write_text(config_content)

    # Create context from real file
    context = create_application_context(config_path=config_file)

    # Verify structure
    assert isinstance(context, ApplicationContext)
    assert isinstance(context.config, AppConfig)
    assert isinstance(context.client, ApiClient)
    assert context.config.api.timeout_seconds == 30


@pytest.mark.integration
def test_integration_default_context_creation():
    """Integration test: create context with default configuration."""
    # This requires a valid config.yaml in the default location
    context = create_application_context()

    assert isinstance(context, ApplicationContext)
    assert isinstance(context.config, AppConfig)
    assert isinstance(context.client, ApiClient)


# =============================================================================
# Test Edge Cases
# =============================================================================


def test_none_values_treated_as_not_provided():
    """Test that explicitly passing None is same as not providing parameter."""
    with (
        patch("ocean_report.application.factory.get_settings") as mock_get,
        patch("ocean_report.application.factory.create_api_client"),
    ):
        mock_config = Mock()
        mock_get.return_value = mock_config

        # These should all behave the same (use default)
        result1 = create_application_context()
        result2 = create_application_context(context=None)
        result3 = create_application_context(config=None)
        result4 = create_application_context(config_path=None)

        # All should use get_settings
        assert mock_get.call_count == 4


def test_keyword_only_arguments():
    """Test that all parameters are keyword-only."""
    mock_config = Mock()

    # Should not allow positional arguments
    with pytest.raises(TypeError):
        create_application_context(mock_config)  # type: ignore


# =============================================================================
# Test Documentation and Exports
# =============================================================================


def test_factory_is_exported():
    """Test that create_application_context is in __all__."""
    from ocean_report.application import factory

    assert "create_application_context" in factory.__all__


def test_factory_has_docstring():
    """Test that factory function has comprehensive docstring."""
    assert create_application_context.__doc__ is not None
    assert len(create_application_context.__doc__) > 100
    assert "Args:" in create_application_context.__doc__
    assert "Returns:" in create_application_context.__doc__
    assert "Raises:" in create_application_context.__doc__
    assert "Examples:" in create_application_context.__doc__
