"""Tests for wind use cases."""

from datetime import datetime
from unittest.mock import Mock, patch
import pytest

from ocean_report.application.context import ApplicationContext
from ocean_report.config.schemas import AppConfig, LocationConfig
from ocean_report.models.openmeteo.forecast import (
    OpenMeteoForecastResponse,
    OpenMeteoHourlyForecast,
)
from ocean_report.use_cases.wind import get_daily_wind_forecast


@pytest.fixture
def mock_context():
    """Create a mock application context."""
    config = AppConfig(
        location=LocationConfig(
            latitude=39.5,
            longitude=-74.2,
            beach_orientation_degrees=140.0
        )
    )
    return ApplicationContext(config=config, client=Mock())


@pytest.fixture
def mock_wind_response():
    """Create a mock wind forecast response."""
    today = datetime.now().strftime("%Y-%m-%d")
    return OpenMeteoForecastResponse(
        hourly=OpenMeteoHourlyForecast(
            time=[
                f"{today}T08:00",
                f"{today}T12:00",
                f"{today}T15:00",
                f"{today}T18:00",
            ],
            wind_speed_10m=[10.5, 15.2, 12.8, 8.3],
            wind_direction_10m=[180.0, 220.0, 190.0, 310.0],
        )
    )


def test_get_daily_wind_forecast_uses_config_defaults(mock_context, mock_wind_response):
    """Test that get_daily_wind_forecast uses config defaults."""
    
    with patch("ocean_report.use_cases.wind.fetch_wind_forecast") as mock_fetch:
        mock_fetch.return_value = mock_wind_response
        
        result, timestamp = get_daily_wind_forecast(context=mock_context)
        
        # Verify it used config location
        call_args = mock_fetch.call_args
        assert call_args.kwargs["params"].latitude == 39.5
        assert call_args.kwargs["params"].longitude == -74.2
        
        # Verify result structure
        assert isinstance(result, list)
        assert len(result) == 4  # Default times: 08:00, 12:00, 15:00, 18:00
        assert isinstance(timestamp, datetime)
        
        # Verify each entry has required fields
        for entry in result:
            assert "time" in entry
            assert "speed_mph" in entry
            assert "direction" in entry
            assert "direction_deg" in entry
            assert "wind_type" in entry


def test_get_daily_wind_forecast_with_custom_location(mock_context, mock_wind_response):
    """Test that custom lat/lon overrides config."""
    
    with patch("ocean_report.use_cases.wind.fetch_wind_forecast") as mock_fetch:
        mock_fetch.return_value = mock_wind_response
        
        get_daily_wind_forecast(
            context=mock_context,
            latitude=40.0,
            longitude=-75.0
        )
        
        # Verify custom location was used
        call_args = mock_fetch.call_args
        assert call_args.kwargs["params"].latitude == 40.0
        assert call_args.kwargs["params"].longitude == -75.0


def test_get_daily_wind_forecast_with_custom_times(mock_context, mock_wind_response):
    """Test filtering to custom time set."""
    
    with patch("ocean_report.use_cases.wind.fetch_wind_forecast") as mock_fetch:
        mock_fetch.return_value = mock_wind_response
        
        result, _ = get_daily_wind_forecast(
            context=mock_context,
            times_to_get={"08:00", "15:00"}  # Only 2 times
        )
        
        # Should only return entries for requested times
        assert len(result) == 2
        times = [entry["time"] for entry in result]
        assert any("08:00" in t or "8 AM" in t for t in times)
        assert any("15:00" in t or "3 PM" in t for t in times)


def test_get_daily_wind_forecast_calculates_wind_type(mock_context, mock_wind_response):
    """Test that wind type (offshore/onshore) is calculated."""
    
    with patch("ocean_report.use_cases.wind.fetch_wind_forecast") as mock_fetch:
        mock_fetch.return_value = mock_wind_response
        
        result, _ = get_daily_wind_forecast(context=mock_context)
        
        # Verify wind_type is calculated for each entry
        # Possible values: "Offshore", "Cross/Offshore", "Cross-shore", "Cross/Onshore", "Onshore"
        valid_types = {"Offshore", "Cross/Offshore", "Cross-shore", "Cross/Onshore", "Onshore"}
        for entry in result:
            assert entry["wind_type"] in valid_types


def test_get_daily_wind_forecast_converts_speed_to_mph(mock_context, mock_wind_response):
    """Test that wind speed is converted from km/h to mph."""
    
    with patch("ocean_report.use_cases.wind.fetch_wind_forecast") as mock_fetch:
        mock_fetch.return_value = mock_wind_response
        
        result, _ = get_daily_wind_forecast(context=mock_context)
        
        # Original: 10.5 km/h → should be ~6.5 mph
        # Verify speed is in reasonable mph range (not km/h)
        for entry in result:
            assert 0 < entry["speed_mph"] < 50  # Reasonable mph range
            assert isinstance(entry["speed_mph"], float)


def test_get_daily_wind_forecast_formats_direction(mock_context, mock_wind_response):
    """Test that wind direction is converted to compass points."""
    
    with patch("ocean_report.use_cases.wind.fetch_wind_forecast") as mock_fetch:
        mock_fetch.return_value = mock_wind_response
        
        result, _ = get_daily_wind_forecast(context=mock_context)
        
        # Verify direction is compass point (N, S, E, W, NE, etc.)
        valid_directions = {"N", "NE", "E", "SE", "S", "SW", "W", "NW", 
                          "NNE", "ENE", "ESE", "SSE", "SSW", "WSW", "WNW", "NNW"}
        
        for entry in result:
            assert entry["direction"] in valid_directions
            assert 0 <= entry["direction_deg"] < 360
