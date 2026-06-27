"""Tests for workflow data formatter."""

from datetime import datetime
from unittest.mock import patch
import pytest

from ocean_report.workflows.models import RawReportData
from ocean_report.models.email import EmailTemplateData
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
            {"time": "8 AM", "speed_mph": 10.5, "direction": "NW", "direction_deg": 315, "wind_type": "Offshore"},
            {"time": "12 PM", "speed_mph": 12.3, "direction": "W", "direction_deg": 270, "wind_type": "Cross-shore"},
        ],
        wind_timestamp=datetime(2025, 7, 4, 6, 0, 0),
    )


def test_format_report_data_returns_formatted_data_model(raw_report_data):
    """Test that format_report_data returns EmailTemplateData."""
    
    result = format_report_data(raw_report_data)
    
    assert isinstance(result, EmailTemplateData)
    assert result.water_temp is not None
    assert result.tide_info is not None
    assert result.wind_info is not None
    assert result.long_date is not None
    assert result.station_name is not None
    assert result.date_retrieved is not None


def test_format_report_data_calls_formatters_with_raw_data(raw_report_data):
    """Test that formatters are called with correct raw data."""
    
    with patch("ocean_report.emailer.template_helpers.format_tide_info") as mock_tide, \
         patch("ocean_report.emailer.template_helpers.format_water_temp_value") as mock_temp, \
         patch("ocean_report.emailer.template_helpers.format_wind_info") as mock_wind:
        
        mock_tide.return_value = "Tide text"
        mock_temp.return_value = "Water temp text"
        mock_wind.return_value = "Wind text"
        
        format_report_data(raw_report_data)
        
        # Verify formatters were called with raw data
        mock_tide.assert_called_once_with(raw_report_data.tides)
        mock_temp.assert_called_once_with(raw_report_data.water_temp)
        mock_wind.assert_called_once_with(raw_report_data.wind_forecast)


def test_format_report_data_includes_retrieval_timestamps(raw_report_data):
    """Test that retrieval timestamps are formatted and included."""
    
    result = format_report_data(raw_report_data)
    
    # Verify formatted timestamp is present
    assert result.date_retrieved is not None
    assert isinstance(result.date_retrieved, str)
    
    # Verify water temp data time is preserved
    assert result.water_temp_measured_at_date == raw_report_data.water_temp_data_time


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
    
    result = format_report_data(raw_data)
    
    # Should still format successfully
    assert isinstance(result, EmailTemplateData)
    # Water temp should show unavailable message
    assert result.water_temp is not None
    assert isinstance(result.water_temp, str)


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
    
    result = format_report_data(raw_data)
    
    # Should handle empty lists gracefully
    assert isinstance(result, EmailTemplateData)
    assert result.tide_info is not None
    assert result.wind_info is not None
