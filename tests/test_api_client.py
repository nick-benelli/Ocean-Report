from unittest.mock import Mock, patch

import pytest
import requests

from ocean_report.api_client.context import ApiContext
from ocean_report.api_client.client import (
    ApiClient,
    ApiConnectionError,
    ApiResponseError,
    ApiSslError,
)
from ocean_report.api_client.factory import (
    get_api_client,
    get_api_client_from_config,
    get_api_context,
)
from ocean_report.config.schemas import AppConfig


def test_api_client_uses_timeout_and_ssl_settings():
    with patch("requests.sessions.Session.get") as mock_get:
        response = Mock()
        mock_get.return_value = response

        client = ApiClient(timeout=3.5, verify_ssl=False)
        result = client.get("https://example.com/data", params={"a": 1})

        assert result is response
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert args[0] == "https://example.com/data"
        assert kwargs["params"] == {"a": 1}
        assert kwargs["timeout"] == 3.5
        assert kwargs["verify"] is False


def test_api_client_retries_without_ssl_on_ssl_error():
    with patch("requests.sessions.Session.get") as mock_get:
        first_exc = requests.exceptions.SSLError("bad cert")
        success_response = Mock()
        mock_get.side_effect = [first_exc, success_response]

        client = ApiClient(timeout=10, verify_ssl=True, retry_insecure_on_ssl_error=True)
        result = client.get("https://example.com/data")

        assert result is success_response
        assert mock_get.call_count == 2
        _, first_kwargs = mock_get.call_args_list[0]
        _, second_kwargs = mock_get.call_args_list[1]
        assert first_kwargs["verify"] is not False
        assert second_kwargs["verify"] is False


def test_api_client_raises_connection_error_when_retry_fails():
    with patch("requests.sessions.Session.get") as mock_get:
        mock_get.side_effect = [
            requests.exceptions.SSLError("bad cert"),
            requests.exceptions.RequestException("network down"),
        ]

        client = ApiClient(timeout=10, verify_ssl=True, retry_insecure_on_ssl_error=True)
        with pytest.raises(ApiConnectionError):
            client.get("https://example.com/data")


def test_api_client_raises_ssl_error_when_ssl_retry_disabled():
    with patch("requests.sessions.Session.get") as mock_get:
        mock_get.side_effect = requests.exceptions.SSLError("bad cert")

        client = ApiClient(timeout=10, verify_ssl=True, retry_insecure_on_ssl_error=False)
        with pytest.raises(ApiSslError):
            client.get("https://example.com/data")


def test_api_client_raises_response_error_for_http_status_failure():
    with patch("requests.sessions.Session.get") as mock_get:
        response = Mock()
        response.status_code = 503
        response.raise_for_status.side_effect = requests.HTTPError("service unavailable")
        mock_get.return_value = response

        client = ApiClient(timeout=10, verify_ssl=True)
        with pytest.raises(ApiResponseError):
            client.get("https://example.com/data")


def test_api_client_closes_session_on_context_exit():
    session = Mock()
    with ApiClient(session=session) as client:
        assert client.session is session

    session.close.assert_called_once()


def test_api_client_mounts_retry_adapter_from_init_settings():
    client = ApiClient(max_retries=5, backoff_seconds=0.25)

    https_retry = client.session.adapters["https://"].max_retries
    http_retry = client.session.adapters["http://"].max_retries

    assert https_retry.total == 5
    assert https_retry.backoff_factor == 0.25
    assert http_retry.total == 5
    assert http_retry.backoff_factor == 0.25


def test_get_api_client_from_config_uses_passed_settings():
    settings = AppConfig.model_validate(
        {
            "api": {
                "timeout_seconds": 7.5,
                "verify_ssl": False,
                "retry_insecure_on_ssl_error": False,
                "max_retries": 5,
                "backoff_seconds": 0.25,
            }
        }
    )

    client = get_api_client_from_config(settings)

    assert client.timeout == 7.5
    assert client.verify_ssl is False
    assert client.retry_insecure_on_ssl_error is False
    assert client.max_retries == 5
    assert client.backoff_seconds == 0.25


def test_get_api_client_alias_uses_factory():
    settings = AppConfig.model_validate(
        {
            "api": {
                "timeout_seconds": 3,
                "verify_ssl": True,
                "retry_insecure_on_ssl_error": True,
            }
        }
    )

    with patch("ocean_report.api_client.context.get_settings", return_value=settings):
        client = get_api_client()

    assert client.timeout == 3
    assert client.verify_ssl is True
    assert client.retry_insecure_on_ssl_error is True


def test_get_api_context_from_config_uses_passed_settings():
    settings = AppConfig.model_validate(
        {
            "api": {
                "timeout_seconds": 4.5,
                "verify_ssl": True,
                "retry_insecure_on_ssl_error": False,
                "max_retries": 2,
                "backoff_seconds": 0.1,
            }
        }
    )

    context = get_api_context(settings)

    assert isinstance(context, ApiContext)
    assert context.config is settings
    assert context.client.timeout == 4.5
    assert context.client.verify_ssl is True
    assert context.client.retry_insecure_on_ssl_error is False


def test_api_context_resolve_returns_same_context_instance():
    settings = AppConfig.model_validate({"api": {"timeout_seconds": 2.0}})
    existing = ApiContext.from_config(settings)

    resolved = ApiContext.resolve(context=existing)

    assert resolved is existing


def test_api_context_resolve_from_config_builds_client():
    settings = AppConfig.model_validate(
        {
            "api": {
                "timeout_seconds": 8.0,
                "verify_ssl": False,
                "retry_insecure_on_ssl_error": False,
            }
        }
    )

    resolved = ApiContext.resolve(config=settings)

    assert resolved.config is settings
    assert resolved.client.timeout == 8.0
    assert resolved.client.verify_ssl is False
    assert resolved.client.retry_insecure_on_ssl_error is False


def test_api_context_resolve_from_config_path_loads_settings():
    settings = AppConfig.model_validate({"api": {"timeout_seconds": 9.0}})

    with patch("ocean_report.api_client.context.get_settings", return_value=settings):
        resolved = ApiContext.resolve(config_path="/tmp/test-config.yaml")

    assert resolved.config is settings
    assert resolved.client.timeout == 9.0


def test_api_context_resolve_rejects_client_without_config_source():
    custom_client = ApiClient(timeout=12.0)

    with pytest.raises(ValueError, match="client requires config or config_path"):
        ApiContext.resolve(client=custom_client)
