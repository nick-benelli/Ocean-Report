"""Integration test for Open-Meteo endpoints and models."""

from unittest.mock import Mock

from ocean_report.endpoints.openmeteo import OpenMeteoForecastEndpoint
from ocean_report.models.openmeteo import (
    OpenMeteoForecastParams,
    OpenMeteoForecastResponse,
)


def test_openmeteo_forecast_endpoint_wired() -> None:
    mock_client = Mock()
    mock_client.get_json.return_value = {
        "hourly": {
            "time": ["2025-07-04T15:00", "2025-07-04T16:00"],
            "wind_speed_10m": [8.5, 9.2],
            "wind_direction_10m": [180.0, 185.0],
        }
    }

    endpoint = OpenMeteoForecastEndpoint(mock_client)
    params = OpenMeteoForecastParams(latitude=40.7128, longitude=-74.0060)

    response = endpoint.get(params)

    assert isinstance(response, OpenMeteoForecastResponse)
    assert len(response.hourly.time) == 2
    assert response.hourly.wind_speed_10m == [8.5, 9.2]
    assert response.hourly.wind_direction_10m == [180.0, 185.0]
