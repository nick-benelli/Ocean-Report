from lbi_surf.email_formatter import format_wind_forecast


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
    result = format_wind_forecast(sample_data)
    assert "8 AM" in result
    assert "13.0 mph" in result
    assert "NW" in result
    assert "Offshore" in result
