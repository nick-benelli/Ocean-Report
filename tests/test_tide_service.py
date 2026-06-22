"""Tests for tide service layer."""

from unittest.mock import Mock, patch
import pytest

from ocean_report.api_client.client import ApiClient
from ocean_report.api_client.exceptions import ApiClientError
from ocean_report.application.context import ApplicationContext
from ocean_report.config.schemas import AppConfig
from ocean_report.models.noaa.tides import NoaaTideParams, NoaaTidePredictionRecord
from ocean_report.services.tide_service import fetch_tide_data


def test_fetch_tide_data_success():
    """Test successful tide data fetch."""
    # Setup
    config = AppConfig()
    mock_client = Mock(spec=ApiClient)
    context = ApplicationContext(config=config, client=mock_client)
    
    params = NoaaTideParams(
        station="8534720",
        begin_date="20250704",
        end_date="20250704",
    )
    
    # Mock the endpoint response
    with patch("ocean_report.services.tide_service.NoaaTidesEndpoint") as MockEndpoint:
        mock_endpoint = MockEndpoint.return_value
        mock_predictions = [
            NoaaTidePredictionRecord(
                timestamp="2025-07-04 06:00",
                height_feet=4.5,
                event_type="H"
            ),
            NoaaTidePredictionRecord(
                timestamp="2025-07-04 12:30",
                height_feet=0.8,
                event_type="L"
            ),
        ]
        
        mock_response = Mock()
        mock_response.predictions = mock_predictions
        mock_endpoint.fetch.return_value = mock_response
        
        # Execute
        result = fetch_tide_data(context=context, params=params)
        
        # Verify
        assert len(result) == 2
        assert result[0].height_feet == 4.5
        assert result[0].event_type == "H"
        assert result[1].height_feet == 0.8
        assert result[1].event_type == "L"
        
        MockEndpoint.assert_called_once_with(mock_client)
        mock_endpoint.fetch.assert_called_once_with(params)


def test_fetch_tide_data_api_error():
    """Test tide data fetch when API fails."""
    config = AppConfig()
    mock_client = Mock(spec=ApiClient)
    context = ApplicationContext(config=config, client=mock_client)
    
    params = NoaaTideParams(
        station="8534720",
        begin_date="20250704",
        end_date="20250704",
    )
    
    with patch("ocean_report.services.tide_service.NoaaTidesEndpoint") as MockEndpoint:
        mock_endpoint = MockEndpoint.return_value
        mock_endpoint.fetch.side_effect = ApiClientError("Network error")
        
        with pytest.raises(ApiClientError, match="Network error"):
            fetch_tide_data(context=context, params=params)


def test_fetch_tide_data_empty_response():
    """Test tide data fetch with empty response."""
    config = AppConfig()
    mock_client = Mock(spec=ApiClient)
    context = ApplicationContext(config=config, client=mock_client)
    
    params = NoaaTideParams(
        station="8534720",
        begin_date="20250704",
        end_date="20250704",
    )
    
    with patch("ocean_report.services.tide_service.NoaaTidesEndpoint") as MockEndpoint:
        mock_endpoint = MockEndpoint.return_value
        mock_response = Mock()
        mock_response.predictions = []
        mock_endpoint.fetch.return_value = mock_response
        
        result = fetch_tide_data(context=context, params=params)
        
        assert result == []
