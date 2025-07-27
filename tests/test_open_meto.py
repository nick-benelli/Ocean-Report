import requests
from datetime import datetime
import pytest

from lbi_surf.wind import get_daily_wind_data


@pytest.fixture
def mock_open_meteo(monkeypatch):
    today = datetime.now().date()
    times = [
        datetime.combine(today, datetime.strptime(h, "%H:%M").time()).isoformat()
        for h in ["08:00", "12:00", "15:00", "18:00", "21:00"]
    ]
    mock_response = {
        "hourly": {
            "time": times,
            "wind_speed_10m": [10.0, 12.5, 8.0, 15.0, 5.0],
            "wind_direction_10m": [90, 120, 180, 270, 45],
        }
    }

    def mock_get(*args, **kwargs):
        class MockResponse:
            def json(self):
                return mock_response

            def raise_for_status(self):
                pass

        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)


def test_get_daily_wind_data_returns_expected_times(mock_open_meteo):
    result = get_daily_wind_data()
    assert isinstance(result, list)
    # Should only include times in times_to_get (not 21:00)
    assert len(result) == 4
    times = [entry["time"] for entry in result]
    assert set(times) == {"8 AM", "12 PM", "3 PM", "6 PM"}


def test_get_daily_wind_data_fields(mock_open_meteo):
    result = get_daily_wind_data()
    for entry in result:
        assert "speed_kmh" in entry
        assert "direction_deg" in entry
        assert "speed_mph" in entry
        assert "direction" in entry
        assert "wind_type" in entry


def test_get_daily_wind_data_empty(monkeypatch):
    # Simulate empty API response
    def mock_get(*args, **kwargs):
        class MockResponse:
            def json(self):
                return {
                    "hourly": {
                        "time": [],
                        "wind_speed_10m": [],
                        "wind_direction_10m": [],
                    }
                }

            def raise_for_status(self):
                pass

        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    result = get_daily_wind_data()
    assert result == []


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
