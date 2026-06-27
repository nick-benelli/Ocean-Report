"""Performance tests for critical paths.

Tests that verify key operations complete within acceptable time limits.
Run with: pytest tests/test_performance.py -m performance
"""

import pytest
import time
from datetime import datetime
from unittest.mock import Mock, patch

from ocean_report.application.context import ApplicationContext
from ocean_report.config.schemas import AppConfig
from ocean_report.workflows.data.fetcher import fetch_raw_data
from ocean_report.workflows.data.formatter import format_report_data
from ocean_report.workflows.models import FetchParams, RawReportData
from ocean_report.models.noaa.tides import NoaaTidePredictionRecord


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


@pytest.fixture
def large_tide_dataset():
    """Create a large tide dataset for performance testing."""
    return [
        NoaaTidePredictionRecord(
            timestamp=f"2025-07-04 {hour:02d}:{minute:02d}",
            height_feet=3.0 + (hour % 6),
            event_type="H" if hour % 2 == 0 else "L"
        )
        for hour in range(24)
        for minute in range(0, 60, 15)  # Every 15 minutes
    ]


@pytest.mark.performance
def test_fetch_raw_data_performance(mock_context, fetch_params):
    """Test that fetch_raw_data completes in acceptable time."""
    
    with patch("ocean_report.workflows.data.fetcher.tides_use_case.get_daytime_tides_for_date") as mock_tides, \
         patch("ocean_report.workflows.data.fetcher.water_temp_use_case.get_latest_water_temp") as mock_temp, \
         patch("ocean_report.workflows.data.fetcher.wind_use_case.get_daily_wind_forecast") as mock_wind:
        
        mock_tides.return_value = ([], datetime.now())
        mock_temp.return_value = (73.5, datetime.now(), None)
        mock_wind.return_value = ([], datetime.now())
        
        start_time = time.time()
        fetch_raw_data(context=mock_context, params=fetch_params)
        elapsed = time.time() - start_time
        
        # Should complete in under 100ms (mocked)
        assert elapsed < 0.1, f"fetch_raw_data took {elapsed*1000:.2f}ms (expected <100ms)"


@pytest.mark.performance
def test_format_report_data_performance_large_dataset(large_tide_dataset):
    """Test formatting performance with large tide dataset."""
    
    raw_data = RawReportData(
        tides=large_tide_dataset,  # 96 tide records
        tide_timestamp=datetime.now(),
        water_temp=73.5,
        water_temp_timestamp=datetime.now(),
        water_temp_data_time="2025-07-04 14:00",
        wind_forecast=[{"time": f"{h} AM", "speed_mph": 10.0} for h in range(8, 16)],
        wind_timestamp=datetime.now(),
    )
    
    with patch("ocean_report.emailer.template_helpers.format_tide_info") as mock_tide, \
         patch("ocean_report.emailer.template_helpers.format_water_temp_value") as mock_temp, \
         patch("ocean_report.emailer.template_helpers.format_wind_info") as mock_wind:
        
        mock_tide.return_value = "Tide text"
        mock_temp.return_value = "Water temp text"
        mock_wind.return_value = "Wind text"
        
        start_time = time.time()
        format_report_data(raw_data)
        elapsed = time.time() - start_time
        
        # Should handle large dataset quickly
        assert elapsed < 0.05, f"format_report_data took {elapsed*1000:.2f}ms with large dataset"


@pytest.mark.performance
def test_tide_formatting_performance(large_tide_dataset):
    """Test tide formatting performance with many events."""
    from ocean_report.emailer.template_helpers import format_tide_info
    
    start_time = time.time()
    result = format_tide_info(large_tide_dataset)
    elapsed = time.time() - start_time
    
    # Should format 96 tide events quickly
    assert elapsed < 0.1, f"format_tide_info took {elapsed*1000:.2f}ms for 96 events"
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.performance
def test_wind_classification_performance():
    """Test wind type classification performance."""
    from ocean_report.utils.wind_utils import classify_wind_relative_to_beach
    
    test_angles = list(range(0, 360, 5))  # 72 test cases
    beach_facing = 140.0
    
    start_time = time.time()
    results = [classify_wind_relative_to_beach(angle, beach_facing) for angle in test_angles]
    elapsed = time.time() - start_time
    
    # Should classify 72 wind directions quickly
    assert elapsed < 0.01, f"classify_wind_relative_to_beach took {elapsed*1000:.2f}ms for 72 classifications"
    assert len(results) == 72
    assert all(r in ["Onshore", "Offshore", "Cross-shore", "Cross/Onshore", "Cross/Offshore"] for r in results)


@pytest.mark.performance
def test_email_body_generation_performance():
    """Test full email template rendering performance."""
    from ocean_report.emailer.template_renderer import render_email_template
    from ocean_report.models.email import EmailTemplateData
    
    # Create realistic template data
    template_data = EmailTemplateData(
        long_date="Monday, July 4, 2025",
        water_temp="73.5 °F",
        tide_info="High: 4.2 ft at 08:30 AM, Low: 0.5 ft at 14:45 PM",
        wind_info="8 AM: 10.5 mph NW (Offshore)\n12 PM: 12.0 mph NW (Offshore)",
        station_name="Test Station",
        station_city="Test City",
        wind_provider="Open-Meteo",
        date_retrieved="Jul 4 at 6:00 AM",
        water_temp_measured_at_date="14:00"
    )
    
    start_time = time.time()
    result = render_email_template(template_data)
    elapsed = time.time() - start_time
    
    # Should render template quickly
    assert elapsed < 0.01, f"render_email_template took {elapsed*1000:.2f}ms"
    assert isinstance(result, str)
    assert len(result) > 100


@pytest.mark.performance
def test_config_loading_performance():
    """Test configuration loading performance."""
    from ocean_report.config.loader import load_app_config
    
    start_time = time.time()
    config = load_app_config()
    elapsed = time.time() - start_time
    
    # Config loading should be fast
    assert elapsed < 0.1, f"load_config took {elapsed*1000:.2f}ms"
    assert config is not None


@pytest.mark.performance
def test_application_context_creation_performance():
    """Test application context creation performance."""
    from ocean_report.application.factory import create_application_context
    
    start_time = time.time()
    context = create_application_context()
    elapsed = time.time() - start_time
    
    # Context creation should be fast
    assert elapsed < 0.2, f"create_application_context took {elapsed*1000:.2f}ms"
    assert context is not None


@pytest.mark.performance
def test_pydantic_model_validation_performance():
    """Test Pydantic model validation performance."""
    from ocean_report.models.noaa.tides import NoaaTidePredictionRecord
    
    # Create 1000 tide records
    tide_data = [
        {
            "timestamp": f"2025-07-04 {hour:02d}:{minute:02d}",
            "height_feet": 3.0,
            "event_type": "H"
        }
        for hour in range(24)
        for minute in range(0, 60, 2)  # 720 records
    ]
    
    start_time = time.time()
    records = [NoaaTidePredictionRecord(**data) for data in tide_data[:100]]
    elapsed = time.time() - start_time
    
    # Should validate 100 records quickly
    assert elapsed < 0.05, f"Pydantic validation took {elapsed*1000:.2f}ms for 100 records"
    assert len(records) == 100


@pytest.mark.performance
@pytest.mark.benchmark
def test_full_report_workflow_performance_benchmark(mock_context, fetch_params):
    """Benchmark full report workflow (fetch + format)."""
    
    with patch("ocean_report.workflows.data.fetcher.tides_use_case.get_daytime_tides_for_date") as mock_tides, \
         patch("ocean_report.workflows.data.fetcher.water_temp_use_case.get_latest_water_temp") as mock_temp, \
         patch("ocean_report.workflows.data.fetcher.wind_use_case.get_daily_wind_forecast") as mock_wind, \
         patch("ocean_report.emailer.template_helpers.format_tide_info") as mock_fmt_tide, \
         patch("ocean_report.emailer.template_helpers.format_water_temp_value") as mock_fmt_temp, \
         patch("ocean_report.emailer.template_helpers.format_wind_info") as mock_fmt_wind:
        
        mock_tides.return_value = ([], datetime.now())
        mock_temp.return_value = (73.5, datetime.now(), None)
        mock_wind.return_value = ([], datetime.now())
        mock_fmt_tide.return_value = "Tide text"
        mock_fmt_temp.return_value = "Temp text"
        mock_fmt_wind.return_value = "Wind text"
        
        start_time = time.time()
        raw_data = fetch_raw_data(context=mock_context, params=fetch_params)
        formatted_data = format_report_data(raw_data)
        elapsed = time.time() - start_time
        
        # Full workflow should be fast
        assert elapsed < 0.15, f"Full workflow took {elapsed*1000:.2f}ms (expected <150ms)"
        assert formatted_data is not None
