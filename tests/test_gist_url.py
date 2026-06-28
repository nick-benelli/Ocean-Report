import pytest
from unittest.mock import patch
from ocean_report.emailer import address_fetcher
from ocean_report.config.schemas import AppConfig


def _build_settings(
    *,
    main_url: str = "",
    offseason_url: str = "",
    test_url: str = "",
    memorial_day_offset: int = -4,
    labor_day_offset: int = 7,
) -> AppConfig:
    return AppConfig.model_validate(
        {
            "email": {
                "recipient_urls": {
                    "main": main_url,
                    "offseason": offseason_url,
                    "test": test_url,
                }
            },
            "summer": {
                "memorial_day_offset": memorial_day_offset,
                "labor_day_offset": labor_day_offset,
            },
        }
    )


def test_parse_recipients_basic():
    raw = "A@EXAMPLE.COM, b@example.com\nc@example.com\n  D@EXAMPLE.com  "
    expected = "a@example.com,b@example.com,c@example.com,d@example.com"
    result = address_fetcher.parse_recipients(raw)
    assert result == expected


def test_parse_recipients_verbose(capsys):
    raw = "A@EXAMPLE.COM, b@example.com"
    address_fetcher.parse_recipients(raw, verbose=True)
    captured = capsys.readouterr()
    assert "a@example.com" in captured.out


def test_fetch_recipients_from_gist_success():
    """Test successful fetching from gist URL using mock client."""
    url = "https://example.com/gist.txt"

    from unittest.mock import Mock

    mock_response = Mock()
    mock_response.text = "test@example.com\nfoo@bar.com"

    mock_client = Mock()
    mock_client.get.return_value = mock_response

    result = address_fetcher.fetch_recipients_from_gist(client=mock_client, url=url)

    assert result == "test@example.com\nfoo@bar.com"
    assert "test@example.com" in result
    assert "foo@bar.com" in result
    mock_client.get.assert_called_once_with(url)


def test_fetch_recipients_from_gist_no_url():
    from unittest.mock import Mock

    mock_client = Mock()
    with pytest.raises(ValueError):
        address_fetcher.fetch_recipients_from_gist(client=mock_client, url="")


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
