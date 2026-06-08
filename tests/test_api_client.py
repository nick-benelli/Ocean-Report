from unittest.mock import Mock, patch

import requests

from ocean_report.api_client.client import ApiClient
from ocean_report.api_client.factory import get_api_client, get_api_client_from_config
from ocean_report.config.schemas import AppConfig


def test_api_client_uses_timeout_and_ssl_settings():
    with patch("requests.get") as mock_get:
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
    with patch("requests.get") as mock_get:
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


def test_api_client_returns_none_when_retry_fails():
    with patch("requests.get") as mock_get:
        mock_get.side_effect = [
            requests.exceptions.SSLError("bad cert"),
            requests.exceptions.RequestException("network down"),
        ]

        client = ApiClient(timeout=10, verify_ssl=True, retry_insecure_on_ssl_error=True)
        assert client.get("https://example.com/data") is None


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

    with patch("ocean_report.api_client.factory.get_settings", return_value=settings):
        client = get_api_client()

    assert client.timeout == 3
    assert client.verify_ssl is True
    assert client.retry_insecure_on_ssl_error is True
