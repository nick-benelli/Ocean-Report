import pytest
from unittest.mock import patch
from ocean_report import address_fetcher


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
    url = "https://example.com/gist.txt"
    with patch("requests.get") as mock_get:
        mock_response = mock_get.return_value
        mock_response.raise_for_status.return_value = None
        mock_response.text = "test@example.com\nfoo@bar.com"
        result = address_fetcher.fetch_recipients_from_gist(url)
        assert result == "test@example.com\nfoo@bar.com"
        mock_get.assert_called_once_with(url)


def test_fetch_recipients_from_gist_no_url():
    with pytest.raises(ValueError):
        address_fetcher.fetch_recipients_from_gist(None)


def test_get_recipients_integration(monkeypatch):
    # Patch the RECIPIENTS_GIST_URL and requests.get
    monkeypatch.setattr(
        address_fetcher, "RECIPIENTS_GIST_URL", "https://example.com/gist.txt"
    )
    with patch("requests.get") as mock_get:
        mock_response = mock_get.return_value
        mock_response.raise_for_status.return_value = None
        mock_response.text = "A@EXAMPLE.COM, b@example.com\nc@example.com"
        result = address_fetcher.get_recipients()
        assert result == "a@example.com,b@example.com,c@example.com"



def test_get_recipients_offseason(monkeypatch):
    # Patch to simulate January (offseason)
    class FakeDateTime:
        @classmethod
        def now(cls):
            return type("dt", (), {"month": 1})()

    monkeypatch.setattr("datetime.datetime", FakeDateTime)
    monkeypatch.setattr(address_fetcher, "OFFSEASON_RECIPIENTS_GIST_URL", "https://example.com/offseason.txt")
    with patch("requests.get") as mock_get:
        mock_response = mock_get.return_value
        mock_response.raise_for_status.return_value = None
        mock_response.text = "off1@example.com, off2@example.com"
        result = address_fetcher.get_recipients()
        assert result == "off1@example.com,off2@example.com"
        mock_get.assert_called_once_with("https://example.com/offseason.txt")


def test_get_recipients_summer(monkeypatch):
    # Patch to simulate July (summer)
    class FakeDateTime:
        @classmethod
        def now(cls):
            return type("dt", (), {"month": 7})()

    monkeypatch.setattr("datetime.datetime", FakeDateTime)
    monkeypatch.setattr(address_fetcher, "RECIPIENTS_GIST_URL", "https://example.com/summer.txt")
    with patch("requests.get") as mock_get:
        mock_response = mock_get.return_value
        mock_response.raise_for_status.return_value = None
        mock_response.text = "sum1@example.com, sum2@example.com"
        result = address_fetcher.get_recipients()
        assert result == "sum1@example.com,sum2@example.com"
        mock_get.assert_called_once_with("https://example.com/summer.txt")


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
