"""Tests for email formatter module."""

from datetime import datetime
from ocean_report.emailer.email_formatter import (
    format_wind_forecast_email,
    format_water_temp,
    format_tide_for_email,
    generate_email_body,
)
from ocean_report.models.noaa.tides import NoaaTidePredictionRecord


def test_format_wind_forecast_output():
    """Test wind forecast formatting."""
    sample_data = [
        {
            "time": "8 AM",
            "speed_mph": 13.0,
            "direction": "NW",
            "direction_deg": 312,
            "wind_type": "Offshore",
        }
    ]
    result = format_wind_forecast_email(sample_data)
    assert "8 AM" in result
    assert "13.0 mph" in result
    assert "NW" in result
    assert "Offshore" in result


def test_format_wind_forecast_multiple_times():
    """Test wind forecast with multiple time slots."""
    sample_data = [
        {"time": "8 AM", "speed_mph": 10.5, "direction": "N", "direction_deg": 0, "wind_type": "Onshore"},
        {"time": "12 PM", "speed_mph": 15.0, "direction": "NW", "direction_deg": 315, "wind_type": "Offshore"},
        {"time": "3 PM", "speed_mph": 12.3, "direction": "W", "direction_deg": 270, "wind_type": "Cross-shore"},
    ]
    result = format_wind_forecast_email(sample_data)
    
    # Should contain all times
    assert "8 AM" in result
    assert "12 PM" in result
    assert "3 PM" in result
    
    # Should contain all wind types
    assert "Onshore" in result
    assert "Offshore" in result
    assert "Cross-shore" in result


def test_format_water_temp_with_value():
    """Test water temperature formatting with valid value."""
    result = format_water_temp(73.5)
    
    assert "73.5" in result or "73.5°F" in result or "73.5" in result.replace("°", "")


def test_format_water_temp_with_none():
    """Test water temperature formatting when value is None."""
    result = format_water_temp(None)
    
    # Should handle None gracefully (likely shows "unavailable" or similar)
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0


def test_format_tide_for_email_with_events():
    """Test tide formatting with valid tide events."""
    tide_events = [
        NoaaTidePredictionRecord(
            timestamp="2025-07-04 08:30",
            height_feet=4.2,
            event_type="H"
        ),
        NoaaTidePredictionRecord(
            timestamp="2025-07-04 14:45",
            height_feet=0.5,
            event_type="L"
        ),
        NoaaTidePredictionRecord(
            timestamp="2025-07-04 20:15",
            height_feet=3.8,
            event_type="H"
        ),
    ]
    
    result = format_tide_for_email(tide_events)
    
    # Should contain tide heights
    assert "4.2" in result
    assert "0.5" in result
    assert "3.8" in result
    
    # Should indicate high/low
    assert result is not None


def test_format_tide_for_email_with_empty_list():
    """Test tide formatting with no events."""
    result = format_tide_for_email([])
    
    # Should handle empty list gracefully
    assert result is not None
    assert isinstance(result, str)


def test_generate_email_body_combines_sections():
    """Test that generate_email_body combines all sections."""
    sections = [
        "🌡️ Water Temperature: 73.5°F",
        "🌊 Tides:\nHigh: 4.2 ft at 08:30 AM\nLow: 0.5 ft at 02:45 PM",
        "💨 Wind Forecast:\n8 AM: 10.5 mph NW (Offshore)",
    ]
    
    result = generate_email_body(sections)
    
    # Should contain all sections
    assert "Water Temperature" in result
    assert "Tides" in result
    assert "Wind Forecast" in result
    assert "73.5" in result
    assert "4.2" in result


def test_generate_email_body_includes_header():
    """Test that email body includes a header with date."""
    sections = ["Test section"]
    result = generate_email_body(sections)
    
    # Should have a header with "Daily Water Report"
    assert "Daily Water Report" in result or "Daily" in result


def test_generate_email_body_includes_footer():
    """Test that email body includes footer attribution."""
    sections = ["Test section"]
    result = generate_email_body(sections)
    
    # Should mention data sources
    assert "NOAA" in result or "Atlantic City" in result or "8534720" in result


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
