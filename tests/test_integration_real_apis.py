"""Integration tests with real external APIs.

These tests make actual HTTP calls to NOAA and OpenMeteo APIs.
Run with: pytest tests/test_integration_real_apis.py -m integration
Skip with: pytest tests/ -m "not integration"
"""

import pytest
from datetime import datetime, timedelta

from ocean_report.application.factory import create_application_context
from ocean_report.services import tide_service, water_temp_service, wind_service
from ocean_report.models.noaa.tides import NoaaTideParams
from ocean_report.models.noaa.water_temperature import NoaaWaterTemperatureParams
from ocean_report.models.openmeteo.forecast import OpenMeteoForecastParams
from ocean_report.use_cases.tides import get_daytime_tides_for_date
from ocean_report.use_cases.water_temperature import get_latest_water_temp
from ocean_report.use_cases.wind import get_daily_wind_forecast
from ocean_report.workflows.report_runner import run_report


@pytest.fixture
def context():
    """Create application context with default config."""
    return create_application_context()


@pytest.fixture
def atlantic_city_station():
    """Atlantic City station ID."""
    return "8534720"


@pytest.fixture
def recent_date():
    """Get a recent date for testing (yesterday to avoid no-data issues)."""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y%m%d")


# Service Layer Integration Tests


@pytest.mark.integration
def test_tide_service_fetch_real_data(context, atlantic_city_station, recent_date):
    """Test tide service with real NOAA API."""
    params = NoaaTideParams(
        station=atlantic_city_station,
        begin_date=recent_date,
        end_date=recent_date
    )
    
    result = tide_service.fetch_tide_data(
        context=context,
        params=params,
    )
    
    # Verify we got valid tide data
    assert result is not None
    assert len(result) > 0
    
    # Check structure of first tide event
    first_tide = result[0]
    assert hasattr(first_tide, "timestamp")
    assert hasattr(first_tide, "height_feet")
    assert hasattr(first_tide, "event_type")
    assert first_tide.event_type in ["H", "L"]


@pytest.mark.integration
def test_water_temp_service_fetch_real_data(context, atlantic_city_station):
    """Test water temperature service with real NOAA API."""
    params = NoaaWaterTemperatureParams(station=atlantic_city_station)
    
    result = water_temp_service.fetch_water_temp(context=context, params=params)
    
    # Verify response (may be None if no recent data)
    if result is not None:
        water_temp, data_time = result
        assert isinstance(water_temp, float)
        assert water_temp > 0  # Reasonable temp (above freezing)
        assert water_temp < 100  # Reasonable temp (below boiling)
        if data_time:
            assert isinstance(data_time, str)


@pytest.mark.integration
def test_wind_service_fetch_real_data(context):
    """Test wind service with real OpenMeteo API."""
    # Long Beach Island coordinates
    params = OpenMeteoForecastParams(
        latitude=39.6437,
        longitude=-74.1975,
    )
    
    result = wind_service.fetch_wind_forecast(
        context=context,
        params=params,
    )
    
    # Verify we got wind data
    assert result is not None
    assert hasattr(result, "hourly")
    assert result.hourly is not None


# Use Case Layer Integration Tests


@pytest.mark.integration
def test_tides_use_case_real_api(context, atlantic_city_station, recent_date):
    """Test tides use case with real API (including daytime filtering)."""
    tides, timestamp = get_daytime_tides_for_date(
        context=context,
        station_id=atlantic_city_station,
        date=recent_date,
    )
    
    # Should get some tide events (daytime filtered)
    assert isinstance(tides, list)
    assert isinstance(timestamp, datetime)
    
    # If we have tides, verify structure
    if len(tides) > 0:
        assert all(hasattr(t, "event_type") for t in tides)


@pytest.mark.integration
def test_water_temp_use_case_real_api(context, atlantic_city_station):
    """Test water temperature use case with real API."""
    water_temp, timestamp, data_time = get_latest_water_temp(
        context=context,
        station_id=atlantic_city_station,
    )
    
    # Timestamp should always be present
    assert isinstance(timestamp, datetime)
    
    # Water temp may be None if no recent data
    if water_temp is not None:
        assert isinstance(water_temp, float)
        assert 32 < water_temp < 90  # Reasonable ocean temp range


@pytest.mark.integration
def test_wind_use_case_real_api(context):
    """Test wind use case with real API."""
    wind_forecast, timestamp = get_daily_wind_forecast(
        context=context,
        latitude=39.6437,
        longitude=-74.1975,
        beach_facing_deg=140.0,
        times_to_get={"08:00", "12:00", "15:00"},
    )
    
    assert isinstance(wind_forecast, list)
    assert isinstance(timestamp, datetime)
    assert len(wind_forecast) > 0
    
    # Verify wind type classification
    for forecast in wind_forecast:
        assert forecast["wind_type"] in [
            "Onshore",
            "Offshore",
            "Cross-shore",
            "Cross/Onshore",
            "Cross/Offshore",
        ]


# End-to-End Integration Test


@pytest.mark.integration
def test_run_report_full_integration_preview_mode(context):
    """Test complete run_report workflow with real APIs in preview mode."""
    result = run_report(
        run_email=False,  # Preview only
        test=False,
    )
    
    # Should complete successfully
    assert result is not None
    
    # In preview mode, run_report prints to console and doesn't return structured data
    # Just verify it completes without error


@pytest.mark.integration
def test_api_error_handling_invalid_station():
    """Test error handling with invalid station ID."""
    context = create_application_context()
    params = NoaaTideParams(
        station="invalid",  # Too short, will fail validation
        begin_date="20250704",
        end_date="20250704"
    )
    
    # This should raise a validation error
    with pytest.raises(Exception):
        tide_service.fetch_tide_data(
            context=context,
            params=params,
        )


@pytest.mark.integration
def test_api_response_time_tide_service(context, atlantic_city_station, recent_date):
    """Test that tide API responds in reasonable time."""
    import time
    
    params = NoaaTideParams(
        station=atlantic_city_station,
        begin_date=recent_date,
        end_date=recent_date
    )
    
    start_time = time.time()
    tide_service.fetch_tide_data(
        context=context,
        params=params,
    )
    elapsed_time = time.time() - start_time
    
    # Should complete in under 5 seconds
    assert elapsed_time < 5.0, f"Tide API took {elapsed_time:.2f}s (too slow)"


@pytest.mark.integration
def test_api_response_time_wind_service(context):
    """Test that wind API responds in reasonable time."""
    import time
    
    params = OpenMeteoForecastParams(
        latitude=39.6437,
        longitude=-74.1975,
    )
    
    start_time = time.time()
    wind_service.fetch_wind_forecast(
        context=context,
        params=params,
    )
    elapsed_time = time.time() - start_time
    
    # Should complete in under 5 seconds
    assert elapsed_time < 5.0, f"Wind API took {elapsed_time:.2f}s (too slow)"
