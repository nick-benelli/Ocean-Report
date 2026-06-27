"""Tests for wind service layer."""

from unittest.mock import Mock, patch
import pytest

from ocean_report.api_client.client import ApiClient
from ocean_report.api_client.exceptions import ApiClientError
from ocean_report.application.context import ApplicationContext
from ocean_report.config.schemas import AppConfig
from ocean_report.models.openmeteo.forecast import (
    OpenMeteoForecastParams,
    OpenMeteoForecastResponse,
    OpenMeteoHourlyForecast,
)
from ocean_report.services.wind_service import fetch_wind_forecast


def test_fetch_wind_forecast_success():
    """Test successful wind forecast fetch."""
    config = AppConfig()
    mock_client = Mock(spec=ApiClient)
    context = ApplicationContext(config=config, client=mock_client)

    params = OpenMeteoForecastParams(latitude=39.5, longitude=-74.2)

    with patch(
        "ocean_report.services.wind_service.OpenMeteoForecastEndpoint"
    ) as MockEndpoint:
        mock_endpoint = MockEndpoint.return_value

        mock_hourly = OpenMeteoHourlyForecast(
            time=["2025-07-04T08:00", "2025-07-04T12:00"],
            wind_speed_10m=[8.5, 12.3],
            wind_direction_10m=[180.0, 220.0],
        )

        mock_response = OpenMeteoForecastResponse(hourly=mock_hourly)
        mock_endpoint.fetch.return_value = mock_response

        result = fetch_wind_forecast(context=context, params=params)

        assert result is not None
        assert len(result.hourly.time) == 2
        assert result.hourly.wind_speed_10m == [8.5, 12.3]
        assert result.hourly.wind_direction_10m == [180.0, 220.0]

        MockEndpoint.assert_called_once_with(mock_client)
        mock_endpoint.fetch.assert_called_once_with(params)


def test_fetch_wind_forecast_api_error():
    """Test wind forecast fetch when API fails."""
    config = AppConfig()
    mock_client = Mock(spec=ApiClient)
    context = ApplicationContext(config=config, client=mock_client)

    params = OpenMeteoForecastParams(latitude=39.5, longitude=-74.2)

    with patch(
        "ocean_report.services.wind_service.OpenMeteoForecastEndpoint"
    ) as MockEndpoint:
        mock_endpoint = MockEndpoint.return_value
        mock_endpoint.fetch.side_effect = ApiClientError("API unavailable")

        with pytest.raises(ApiClientError, match="API unavailable"):
            fetch_wind_forecast(context=context, params=params)
