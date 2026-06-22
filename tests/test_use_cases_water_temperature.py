"""Tests for water temperature use cases."""

from datetime import datetime
from unittest.mock import Mock, patch
import pytest

from ocean_report.application.context import ApplicationContext
from ocean_report.config.schemas import AppConfig, NoaaConfig
from ocean_report.models.noaa.water_temperature import NoaaWaterTemperatureRecord
from ocean_report.use_cases.water_temperature import get_latest_water_temp


@pytest.fixture
def mock_context():
    """Create a mock application context."""
    config = AppConfig(
        noaa=NoaaConfig(station_id="8534720", buoy_id="44091")
    )
    return ApplicationContext(config=config, client=Mock())


def test_get_latest_water_temp_uses_config_default(mock_context):
    """Test that get_latest_water_temp uses config station_id by default."""
    
    mock_record = NoaaWaterTemperatureRecord(
        timestamp="2025-07-04 15:30",
        temperature=73.5
    )
    
    with patch("ocean_report.use_cases.water_temperature.fetch_water_temp") as mock_fetch:
        mock_fetch.return_value = mock_record
        
        temp, timestamp, data_time = get_latest_water_temp(context=mock_context)
        
        # Verify it used config station_id
        call_args = mock_fetch.call_args
        assert call_args.kwargs["context"] is mock_context
        assert call_args.kwargs["params"].station == "8534720"
        
        # Verify result
        assert temp == 73.5
        assert isinstance(timestamp, datetime)
        assert data_time == "2025-07-04 15:30"


def test_get_latest_water_temp_with_custom_station(mock_context):
    """Test that custom station_id overrides config."""
    
    mock_record = NoaaWaterTemperatureRecord(
        timestamp="2025-07-04 15:30",
        temperature=72.0
    )
    
    with patch("ocean_report.use_cases.water_temperature.fetch_water_temp") as mock_fetch:
        mock_fetch.return_value = mock_record
        
        temp, timestamp, data_time = get_latest_water_temp(
            context=mock_context,
            station_id="9999999"
        )
        
        # Verify custom station was used
        call_args = mock_fetch.call_args
        assert call_args.kwargs["params"].station == "9999999"
        assert temp == 72.0


def test_get_latest_water_temp_handles_no_data(mock_context):
    """Test handling when no water temperature data is available."""
    
    with patch("ocean_report.use_cases.water_temperature.fetch_water_temp") as mock_fetch:
        mock_fetch.return_value = None
        
        temp, timestamp, data_time = get_latest_water_temp(context=mock_context)
        
        assert temp is None
        assert isinstance(timestamp, datetime)
        assert data_time is None


def test_get_latest_water_temp_always_requests_latest(mock_context):
    """Test that date parameter is always 'latest'."""
    
    mock_record = NoaaWaterTemperatureRecord(
        timestamp="2025-07-04 15:30",
        temperature=74.0
    )
    
    with patch("ocean_report.use_cases.water_temperature.fetch_water_temp") as mock_fetch:
        mock_fetch.return_value = mock_record
        
        get_latest_water_temp(context=mock_context)
        
        # Verify 'latest' was used in params
        call_args = mock_fetch.call_args
        assert call_args.kwargs["params"].date == "latest"
