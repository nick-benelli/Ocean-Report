import requests
from lbi_surf.water_temp import fetch_water_temp
from lbi_surf.tide import fetch_tide_data


def test_fetch_noaa_data(monkeypatch):
    def mock_get(*args, **kwargs):
        class MockResponse:
            def json(self):
                # Match the structure expected by fetch_water_temp
                return {"data": [{"v": 74.2}]}

            def raise_for_status(self):
                pass  # Pretend the response was OK

        return MockResponse()

    print("\nTesting connection to NOAA API for water temperature via monkeypatch...")
    print("Testing function `fetch_water_temp`...")
    monkeypatch.setattr(requests, "get", mock_get)
    data = fetch_water_temp()
    assert data == 74.2  # fetch_water_temp returns a float


def test_fetch_noaa_data_live():
    """Test live connection to NOAA API and check that a number is returned."""
    print("\nTesting live connection to NOAA API for water temperature...")
    print("Testing function `fetch_water_temp`...")
    temp = fetch_water_temp()
    assert temp is not None, "No temperature returned from NOAA API"
    assert isinstance(temp, float), "Temperature is not a float"


def test_fetch_tide_data(monkeypatch):
    """Test fetch_tide_data returns correct structure from mocked NOAA API."""
    print("\nTesting connection to NOAA API for tide data via monkeypatch...")
    print("Testing function `fetch_tide_data`...")
    mock_response = {
        "predictions": [
            {"t": "2024-07-01 01:00", "v": "3.2", "type": "H"},
            {"t": "2024-07-01 07:00", "v": "0.5", "type": "L"},
        ]
    }

    def mock_get(*args, **kwargs):
        class MockResponse:
            def json(self):
                return mock_response

            def raise_for_status(self):
                pass

        return MockResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    result = fetch_tide_data(station_id="1234567", date="20240701")
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["t"] == "2024-07-01 01:00"
    assert result[0]["v"] == "3.2"
    assert result[0]["type"] == "H"
    assert result[1]["type"] == "L"


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
