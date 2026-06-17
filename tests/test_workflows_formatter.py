"""Tests for workflow data formatter."""

from datetime import datetime
from unittest.mock import patch
import pytest

from ocean_report.workflows.models import RawReportData, FormattedReportData
from ocean_report.workflows.data.formatter import format_report_data
from ocean_report.models.noaa.tides import NoaaTidePredictionRecord


@pytest.fixture
def raw_report_data():
    """Create sample raw report data."""
    return RawReportData(
        tides=[
            NoaaTidePredictionRecord(
                timestamp="2025-07-04 08:00",
                height_feet=4.2,
                event_type="H"
            ),
            NoaaTidePredictionRecord(
                timestamp="2025-07-04 14:30",
                height_feet=0.5,
                event_type="L"
            ),
        ],
        tide_timestamp=datetime(2025, 7, 4, 6, 0, 0),
        water_temp=73.5,
        water_temp_timestamp=datetime(2025, 7, 4, 6, 0, 0),
        water_temp_data_time="2025-07-04 14:00",
        wind_forecast=[
            {"time": "8 AM", "speed_mph": 10.5, "direction": "NW", "wind_type": "Offshore"},
            {"time": "12 PM", "speed_mph": 12.3, "direction": "W", "wind_type": "Cross-shore"},
        ],
        wind_timestamp=datetime(2025, 7, 4, 6, 0, 0),
    )


def test_format_report_data_returns_formatted_data_model(raw_report_data):
    """Test that format_report_data returns FormattedReportData."""
    
    with patch("ocean_report.workflows.data.formatter.formatter.format_tide_for_email") as mock_tide, \
         patch("ocean_report.workflows.data.formatter.formatter.format_water_temp") as mock_temp, \
         patch("ocean_report.workflows.data.formatter.formatter.format_wind_forecast_email") as mock_wind:
        
        mock_tide.return_value = "Tide text"
        mock_temp.return_value = "Water temp text"
        mock_wind.return_value = "Wind text"
        
        result = format_report_data(raw_report_data)
        
        assert isinstance(result, FormattedReportData)
        assert result.tide_text == "Tide text"
        assert result.water_temp_text == "Water temp text"
        assert result.wind_text == "Wind text"


def test_format_report_data_calls_formatters_with_raw_data(raw_report_data):
    """Test that formatters are called with correct raw data."""
    
    with patch("ocean_report.workflows.data.formatter.formatter.format_tide_for_email") as mock_tide, \
         patch("ocean_report.workflows.data.formatter.formatter.format_water_temp") as mock_temp, \
         patch("ocean_report.workflows.data.formatter.formatter.format_wind_forecast_email") as mock_wind:
        
        mock_tide.return_value = "Tide text"
        mock_temp.return_value = "Water temp text"
        mock_wind.return_value = "Wind text"
        
        format_report_data(raw_report_data)
        
        # Verify formatters were called with raw data
        mock_tide.assert_called_once_with(raw_report_data.tides)
        mock_temp.assert_called_once_with(raw_report_data.water_temp)
        mock_wind.assert_called_once_with(raw_report_data.wind_forecast)


def test_format_report_data_includes_retrieval_timestamps(raw_report_data):
    """Test that retrieval timestamps are preserved."""
    
    with patch("ocean_report.workflows.data.formatter.formatter.format_tide_for_email") as mock_tide, \
         patch("ocean_report.workflows.data.formatter.formatter.format_water_temp") as mock_temp, \
         patch("ocean_report.workflows.data.formatter.formatter.format_wind_forecast_email") as mock_wind:
        
        mock_tide.return_value = "Tide text"
        mock_temp.return_value = "Water temp text"
        mock_wind.return_value = "Wind text"
        
        result = format_report_data(raw_report_data)
        
        # Verify timestamps are included
        assert "tides" in result.retrieval_timestamps
        assert "water_temp" in result.retrieval_timestamps
        assert "water_temp_data_time" in result.retrieval_timestamps
        assert "wind" in result.retrieval_timestamps
        
        assert result.retrieval_timestamps["tides"] == raw_report_data.tide_timestamp
        assert result.retrieval_timestamps["water_temp"] == raw_report_data.water_temp_timestamp
        assert result.retrieval_timestamps["water_temp_data_time"] == raw_report_data.water_temp_data_time
        assert result.retrieval_timestamps["wind"] == raw_report_data.wind_timestamp


def test_format_report_data_handles_none_water_temp():
    """Test formatting when water temperature is None."""
    
    raw_data = RawReportData(
        tides=[],
        tide_timestamp=datetime.now(),
        water_temp=None,  # No water temp
        water_temp_timestamp=datetime.now(),
        water_temp_data_time=None,
        wind_forecast=[],
        wind_timestamp=datetime.now(),
    )
    
    with patch("ocean_report.workflows.data.formatter.formatter.format_tide_for_email") as mock_tide, \
         patch("ocean_report.workflows.data.formatter.formatter.format_water_temp") as mock_temp, \
         patch("ocean_report.workflows.data.formatter.formatter.format_wind_forecast_email") as mock_wind:
        
        mock_tide.return_value = "No tides"
        mock_temp.return_value = "Water temp unavailable"
        mock_wind.return_value = "No wind"
        
        result = format_report_data(raw_data)
        
        # Should still format successfully
        mock_temp.assert_called_once_with(None)
        assert result.water_temp_text == "Water temp unavailable"


def test_format_report_data_handles_empty_lists():
    """Test formatting when data lists are empty."""
    
    raw_data = RawReportData(
        tides=[],  # No tides
        tide_timestamp=datetime.now(),
        water_temp=73.5,
        water_temp_timestamp=datetime.now(),
        water_temp_data_time="2025-07-04 14:00",
        wind_forecast=[],  # No wind data
        wind_timestamp=None,
    )
    
    with patch("ocean_report.workflows.data.formatter.formatter.format_tide_for_email") as mock_tide, \
         patch("ocean_report.workflows.data.formatter.formatter.format_water_temp") as mock_temp, \
         patch("ocean_report.workflows.data.formatter.formatter.format_wind_forecast_email") as mock_wind:
        
        mock_tide.return_value = "No tide events today"
        mock_temp.return_value = "73.5°F"
        mock_wind.return_value = "Wind data unavailable"
        
        result = format_report_data(raw_data)
        
        # Should handle empty lists gracefully
        mock_tide.assert_called_once_with([])
        mock_wind.assert_called_once_with([])
        assert isinstance(result, FormattedReportData)
