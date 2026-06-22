"""Tests for workflow data fetcher."""

from datetime import datetime
from unittest.mock import Mock, patch
import pytest

from ocean_report.application.context import ApplicationContext
from ocean_report.config.schemas import AppConfig
from ocean_report.workflows.models import FetchParams, RawReportData
from ocean_report.workflows.data.fetcher import fetch_raw_data
from ocean_report.models.noaa.tides import NoaaTidePredictionRecord
from ocean_report.api_client.exceptions import ApiClientError


@pytest.fixture
def mock_context():
    """Create a mock application context."""
    config = AppConfig()
    return ApplicationContext(config=config, client=Mock())


@pytest.fixture
def fetch_params():
    """Create fetch parameters."""
    return FetchParams(
        station_id="8534720",
        date_str="20250704",
        latitude=39.5,
        longitude=-74.2,
        beach_facing_deg=140.0,
        forecast_times={"08:00", "12:00", "15:00"},
    )


def test_fetch_raw_data_success(mock_context, fetch_params):
    """Test successful data fetching from all APIs."""
    
    mock_tides = [
        NoaaTidePredictionRecord(
            timestamp="2025-07-04 08:00",
            height_feet=4.2,
            event_type="H"
        )
    ]
    
    with patch("ocean_report.workflows.data.fetcher.tides_use_case.get_daytime_tides_for_date") as mock_tides_uc, \
         patch("ocean_report.workflows.data.fetcher.water_temp_use_case.get_latest_water_temp") as mock_temp_uc, \
         patch("ocean_report.workflows.data.fetcher.wind_use_case.get_daily_wind_forecast") as mock_wind_uc:
        
        # Setup mocks
        mock_tides_uc.return_value = (mock_tides, datetime.now())
        mock_temp_uc.return_value = (73.5, datetime.now(), "2025-07-04 14:00")
        mock_wind_uc.return_value = ([{"time": "8 AM", "speed_mph": 10.5}], datetime.now())
        
        result = fetch_raw_data(context=mock_context, params=fetch_params)
        
        # Verify result structure
        assert isinstance(result, RawReportData)
        assert result.tides == mock_tides
        assert result.water_temp == 73.5
        assert result.water_temp_data_time == "2025-07-04 14:00"
        assert len(result.wind_forecast) == 1
        assert isinstance(result.tide_timestamp, datetime)
        assert isinstance(result.water_temp_timestamp, datetime)


def test_fetch_raw_data_calls_use_cases_with_params(mock_context, fetch_params):
    """Test that fetch_raw_data passes correct parameters to use cases."""
    
    with patch("ocean_report.workflows.data.fetcher.tides_use_case.get_daytime_tides_for_date") as mock_tides_uc, \
         patch("ocean_report.workflows.data.fetcher.water_temp_use_case.get_latest_water_temp") as mock_temp_uc, \
         patch("ocean_report.workflows.data.fetcher.wind_use_case.get_daily_wind_forecast") as mock_wind_uc:
        
        mock_tides_uc.return_value = ([], datetime.now())
        mock_temp_uc.return_value = (None, datetime.now(), None)
        mock_wind_uc.return_value = ([], datetime.now())
        
        fetch_raw_data(context=mock_context, params=fetch_params)
        
        # Verify tide use case was called with correct params
        mock_tides_uc.assert_called_once_with(
            context=mock_context,
            station_id="8534720",
            date="20250704",
        )
        
        # Verify water temp use case was called with correct params
        mock_temp_uc.assert_called_once_with(
            context=mock_context,
            station_id="8534720",
        )
        
        # Verify wind use case was called with correct params
        mock_wind_uc.assert_called_once_with(
            context=mock_context,
            latitude=39.5,
            longitude=-74.2,
            beach_facing_deg=140.0,
            times_to_get={"08:00", "12:00", "15:00"},
        )


def test_fetch_raw_data_handles_wind_api_failure_gracefully(mock_context, fetch_params):
    """Test that wind API failure doesn't crash entire fetch."""
    
    with patch("ocean_report.workflows.data.fetcher.tides_use_case.get_daytime_tides_for_date") as mock_tides_uc, \
         patch("ocean_report.workflows.data.fetcher.water_temp_use_case.get_latest_water_temp") as mock_temp_uc, \
         patch("ocean_report.workflows.data.fetcher.wind_use_case.get_daily_wind_forecast") as mock_wind_uc:
        
        mock_tides_uc.return_value = ([], datetime.now())
        mock_temp_uc.return_value = (73.5, datetime.now(), None)
        mock_wind_uc.side_effect = ApiClientError("Wind API unavailable")
        
        # Should not raise, should provide fallback
        result = fetch_raw_data(context=mock_context, params=fetch_params)
        
        # Wind forecast should be empty list (fallback)
        assert result.wind_forecast == []
        assert result.wind_timestamp is None
        # Other data should still be present
        assert result.water_temp == 73.5


def test_fetch_raw_data_propagates_tide_api_failure(mock_context, fetch_params):
    """Test that tide API failure propagates (critical data)."""
    
    with patch("ocean_report.workflows.data.fetcher.tides_use_case.get_daytime_tides_for_date") as mock_tides_uc:
        mock_tides_uc.side_effect = ApiClientError("Tide API unavailable")
        
        # Tide failure should propagate (not caught)
        with pytest.raises(ApiClientError, match="Tide API unavailable"):
            fetch_raw_data(context=mock_context, params=fetch_params)


def test_fetch_raw_data_handles_no_water_temp_data(mock_context, fetch_params):
    """Test handling when water temperature is unavailable."""
    
    with patch("ocean_report.workflows.data.fetcher.tides_use_case.get_daytime_tides_for_date") as mock_tides_uc, \
         patch("ocean_report.workflows.data.fetcher.water_temp_use_case.get_latest_water_temp") as mock_temp_uc, \
         patch("ocean_report.workflows.data.fetcher.wind_use_case.get_daily_wind_forecast") as mock_wind_uc:
        
        mock_tides_uc.return_value = ([], datetime.now())
        mock_temp_uc.return_value = (None, datetime.now(), None)  # No water temp available
        mock_wind_uc.return_value = ([], datetime.now())
        
        result = fetch_raw_data(context=mock_context, params=fetch_params)
        
        # Should handle None water temp gracefully
        assert result.water_temp is None
        assert result.water_temp_data_time is None
        assert isinstance(result, RawReportData)
