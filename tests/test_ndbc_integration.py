"""Integration test for NDBC endpoints and models."""

from unittest.mock import Mock

from ocean_report.endpoints.ndbc import NdbcObservationsEndpoint
from ocean_report.models.ndbc import (
    NdbcObservationsParams,
    NdbcObservationsResponse,
)


def test_ndbc_observations_endpoint_wired() -> None:
    mock_client = Mock()
    mock_client.get_json.return_value = {
        "observations": [
            {
                "station": "44013",
                "timestamp": "2025-07-04T15:00:00Z",
                "wind_spd": 8.5,
                "water_temp": 24.3,
            }
        ]
    }

    endpoint = NdbcObservationsEndpoint(mock_client)
    params = NdbcObservationsParams(station_id="44013")

    response = endpoint.get(params)

    assert isinstance(response, NdbcObservationsResponse)
    assert len(response.observations) == 1
    assert response.observations[0].station_id == "44013"
    assert response.observations[0].wind_speed_knots == 8.5
    assert response.observations[0].water_temperature_c == 24.3
