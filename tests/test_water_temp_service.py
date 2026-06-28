"""Tests for water temperature service layer."""

from unittest.mock import Mock, patch
import pytest

from ocean_report.api_client.client import ApiClient
from ocean_report.api_client.exceptions import ApiClientError
from ocean_report.application.context import ApplicationContext
from ocean_report.config.schemas import AppConfig
from ocean_report.models.noaa.water_temperature import (
    NoaaWaterTempParams,
    NoaaWaterTemperatureRecord,
)
from ocean_report.services.water_temp_service import fetch_water_temp


def test_fetch_water_temp_success():
    """Test successful water temperature fetch."""
    config = AppConfig()
    mock_client = Mock(spec=ApiClient)
    context = ApplicationContext(config=config, client=mock_client)

    params = NoaaWaterTempParams(station="8534720")

    with patch(
        "ocean_report.services.water_temp_service.WaterTemperatureEndpoint"
    ) as MockEndpoint:
        mock_endpoint = MockEndpoint.return_value
        mock_record = NoaaWaterTemperatureRecord(
            timestamp="2025-07-04 15:00", temperature=73.5
        )

        mock_response = Mock()
        mock_response.data = [mock_record]
        mock_endpoint.fetch.return_value = mock_response

        result = fetch_water_temp(context=context, params=params)

        assert result is not None
        assert result.temperature == 73.5
        assert result.timestamp == "2025-07-04 15:00"

        MockEndpoint.assert_called_once_with(mock_client)
        mock_endpoint.fetch.assert_called_once_with(params)


def test_fetch_water_temp_no_data():
    """Test water temperature fetch with no data."""
    config = AppConfig()
    mock_client = Mock(spec=ApiClient)
    context = ApplicationContext(config=config, client=mock_client)

    params = NoaaWaterTempParams(station="8534720")

    with patch(
        "ocean_report.services.water_temp_service.WaterTemperatureEndpoint"
    ) as MockEndpoint:
        mock_endpoint = MockEndpoint.return_value
        mock_response = Mock()
        mock_response.data = []
        mock_endpoint.fetch.return_value = mock_response

        result = fetch_water_temp(context=context, params=params)

        assert result is None


def test_fetch_water_temp_api_error():
    """Test water temperature fetch when API fails."""
    config = AppConfig()
    mock_client = Mock(spec=ApiClient)
    context = ApplicationContext(config=config, client=mock_client)

    params = NoaaWaterTempParams(station="8534720")

    with patch(
        "ocean_report.services.water_temp_service.WaterTemperatureEndpoint"
    ) as MockEndpoint:
        mock_endpoint = MockEndpoint.return_value
        mock_endpoint.fetch.side_effect = ApiClientError("Connection failed")

        with pytest.raises(ApiClientError, match="Connection failed"):
            fetch_water_temp(context=context, params=params)
