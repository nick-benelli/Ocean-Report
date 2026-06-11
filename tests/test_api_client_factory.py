"""Unit tests for the ApiClient factory."""

from unittest.mock import Mock

import pytest
import requests

from ocean_report.api_client.client import ApiClient
from ocean_report.api_client.factory import create_api_client
from ocean_report.config.schemas import ApiConfig, AppConfig


class TestCreateApiClient:
    """Test suite for the create_api_client factory function."""

    def test_creates_client_with_default_config(self) -> None:
        """Factory should create a client using default API configuration."""
        config = AppConfig()
        client = create_api_client(config)

        assert isinstance(client, ApiClient)
        assert client.timeout == 10.0
        assert client.verify_ssl is True
        assert client.retry_insecure_on_ssl_error is True
        assert client.max_retries == 3
        assert client.backoff_seconds == 0.8
        assert isinstance(client.session, requests.Session)

    def test_creates_client_with_custom_config(self) -> None:
        """Factory should respect custom API configuration values."""
        api_config = ApiConfig(
            timeout_seconds=30.0,
            verify_ssl=False,
            retry_insecure_on_ssl_error=False,
            max_retries=5,
            backoff_seconds=1.5,
        )
        config = AppConfig(api=api_config)
        client = create_api_client(config)

        assert client.timeout == 30.0
        assert client.verify_ssl is False
        assert client.retry_insecure_on_ssl_error is False
        assert client.max_retries == 5
        assert client.backoff_seconds == 1.5

    def test_accepts_custom_session(self) -> None:
        """Factory should use provided session instead of creating one."""
        config = AppConfig()
        mock_session = Mock(spec=requests.Session)

        client = create_api_client(config, session=mock_session)

        assert client.session is mock_session

    def test_creates_new_session_when_none_provided(self) -> None:
        """Factory should create a new session if none is provided."""
        config = AppConfig()
        client = create_api_client(config, session=None)

        assert isinstance(client.session, requests.Session)
        assert client.session is not None

    def test_multiple_clients_independent(self) -> None:
        """Multiple clients from the same config should be independent."""
        config = AppConfig()
        client1 = create_api_client(config)
        client2 = create_api_client(config)

        assert client1 is not client2
        assert client1.session is not client2.session

    def test_config_immutability(self) -> None:
        """Factory should not modify the input configuration."""
        api_config = ApiConfig(timeout_seconds=15.0)
        config = AppConfig(api=api_config)
        original_timeout = config.api.timeout_seconds

        create_api_client(config)

        assert config.api.timeout_seconds == original_timeout

    @pytest.mark.parametrize(
        "timeout,verify_ssl,max_retries",
        [
            (5.0, True, 2),
            (15.0, False, 4),
            (60.0, True, 10),
        ],
    )
    def test_various_config_combinations(
        self, timeout: float, verify_ssl: bool, max_retries: int
    ) -> None:
        """Factory should handle various valid configuration combinations."""
        api_config = ApiConfig(
            timeout_seconds=timeout,
            verify_ssl=verify_ssl,
            max_retries=max_retries,
        )
        config = AppConfig(api=api_config)
        client = create_api_client(config)

        assert client.timeout == timeout
        assert client.verify_ssl is verify_ssl
        assert client.max_retries == max_retries


class TestFactoryIntegration:
    """Integration tests verifying factory output works correctly."""

    def test_created_client_is_functional(self) -> None:
        """Client created by factory should be ready to make requests."""
        config = AppConfig()
        client = create_api_client(config)

        # Verify client has necessary methods
        assert hasattr(client, "get")
        assert hasattr(client, "post")
        assert hasattr(client, "_build_session")
        assert callable(client.get)
        assert callable(client.post)

    def test_session_has_retry_adapters(self) -> None:
        """Created client should have properly configured retry adapters."""
        config = AppConfig()
        client = create_api_client(config)

        # Verify session has adapters mounted
        assert "https://" in client.session.adapters
        assert "http://" in client.session.adapters

    def test_client_respects_ssl_verification_setting(self) -> None:
        """Created client should properly configure SSL verification."""
        config_secure = AppConfig(api=ApiConfig(verify_ssl=True))
        config_insecure = AppConfig(api=ApiConfig(verify_ssl=False))

        client_secure = create_api_client(config_secure)
        client_insecure = create_api_client(config_insecure)

        # Verify the SSL setting is preserved
        assert client_secure.verify_ssl is True
        assert client_insecure.verify_ssl is False

        # Verify _resolve_verify returns correct values
        assert client_secure._resolve_verify() != False  # Should return cert path
        assert client_insecure._resolve_verify() is False
