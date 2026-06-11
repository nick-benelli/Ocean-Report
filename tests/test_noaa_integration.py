"""Integration test for all NOAA endpoints and models."""
from unittest.mock import Mock

from ocean_report.endpoints.noaa import (
    NoaaTidesEndpoint,
    NoaaStationsEndpoint,
    WaterTemperatureEndpoint,
)
from ocean_report.models.noaa import (
    NoaaTideParams,
    NoaaTideResponse,
    NoaaStationsParams,
    NoaaStationsResponse,
    NoaaWaterTemperatureParams,
    NoaaWaterTemperatureResponse,
)


def test_tides_endpoint_wired() -> None:
    mock_client = Mock()
    mock_client.get_json.return_value = {
        "predictions": [
            {"t": "2025-07-04 15:00", "v": "2.5", "type": "H"},
        ]
    }

    endpoint = NoaaTidesEndpoint(mock_client)
    params = NoaaTideParams(begin_date="20250704", end_date="20250704", station="8534720")

    response = endpoint.get(params)

    assert isinstance(response, NoaaTideResponse)
    assert len(response.predictions) == 1
    assert response.predictions[0].height_feet == 2.5


def test_stations_endpoint_wired() -> None:
    mock_client = Mock()
    mock_client.get_json.return_value = {
        "stations": [{"id": "8534720", "name": "Atlantic City"}]
    }

    endpoint = NoaaStationsEndpoint(mock_client)
    params = NoaaStationsParams()

    response = endpoint.get(params)

    assert isinstance(response, NoaaStationsResponse)
    assert response.stations[0].station_id == "8534720"


def test_water_temperature_endpoint_wired() -> None:
    mock_client = Mock()
    mock_client.get_json.return_value = {
        "data": [{"t": "2025-07-04 15:00", "v": "73.2"}]
    }

    endpoint = WaterTemperatureEndpoint(mock_client)
    params = NoaaWaterTemperatureParams(station="8534720")

    response = endpoint.get(params)

    assert isinstance(response, NoaaWaterTemperatureResponse)
    assert response.data[0].temperature == 73.2
