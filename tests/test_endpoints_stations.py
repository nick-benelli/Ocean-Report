from unittest.mock import Mock

from ocean_report.endpoints.noaa.stations import NoaaStationsEndpoint
from ocean_report.models.noaa.stations import (
    NoaaStationsParams,
    NoaaStationsResponse,
)


def test_noaa_stations_endpoint_wired_to_models() -> None:
    """Verify stations endpoint correctly consumes model layer."""
    mock_client = Mock()
    mock_client.get_json.return_value = {
        "stations": [
            {"id": "8534720", "name": "Atlantic City", "latitude": 39.355, "longitude": -74.417},
            {"id": "8545530", "name": "Cape May", "latitude": 38.969, "longitude": -74.961},
        ]
    }

    endpoint = NoaaStationsEndpoint(mock_client)
    params = NoaaStationsParams()

    response = endpoint.get(params)

    assert isinstance(response, NoaaStationsResponse)
    assert len(response.stations) == 2
    assert response.stations[0].station_id == "8534720"
    assert response.stations[0].name == "Atlantic City"
    assert response.stations[0].latitude == 39.355

    mock_client.get_json.assert_called_once_with(
        "https://api.tidesandcurrents.noaa.gov/api/prod/stations",
        params={"format": "json"},
        headers=None,
    )
