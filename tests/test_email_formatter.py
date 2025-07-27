from ocean_report.email_formatter import format_wind_forecast_email


def test_format_wind_forecast_output():
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


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
