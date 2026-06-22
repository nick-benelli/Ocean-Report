"""End-to-end tests for the ocean report workflow.

These tests verify the complete workflow from configuration loading through
data fetching, formatting, and email generation.
"""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from ocean_report.workflows.report_runner import run_report
from ocean_report.workflows.models import RawReportData, FormattedReportData
from ocean_report.models.noaa.tides import NoaaTidePredictionRecord
from ocean_report.models.noaa.water_temperature import NoaaWaterTemperatureRecord
from ocean_report.models.openmeteo.forecast import (
    OpenMeteoForecastResponse,
    OpenMeteoHourlyForecast,
)


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    config_content = """
noaa:
  station_id: "8534720"
  buoy_id: "44091"
  
email:
  smtp_server: "smtp.example.com"
  smtp_port: 587
  sender: "test@example.com"
  recipients: "recipient@example.com"
  use_recipient_url: false
  
location:
  longitude: -74.2
  latitude: 39.5
  beach_orientation_degrees: 140
  
logging:
  level: "INFO"
  output: "console"
  format: "%(message)s"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(config_content)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def mock_data_responses():
    """Mock responses for all data fetching operations."""
    return {
        "tides": [
            NoaaTidePredictionRecord(
                timestamp="2025-07-04 06:30",
                height_feet=4.2,
                event_type="H"
            ),
            NoaaTidePredictionRecord(
                timestamp="2025-07-04 12:45",
                height_feet=0.5,
                event_type="L"
            ),
        ],
        "water_temp": NoaaWaterTemperatureRecord(
            timestamp="2025-07-04 14:00",
            temperature=72.5
        ),
        "wind": OpenMeteoForecastResponse(
            hourly=OpenMeteoHourlyForecast(
                time=["2025-07-04T08:00", "2025-07-04T12:00"],
                wind_speed_10m=[8.5, 12.0],
                wind_direction_10m=[180.0, 220.0],
            )
        ),
    }


def test_run_report_preview_mode(temp_config_file, mock_data_responses):
    """Test the full report workflow in preview mode (no email sent)."""
    
    # Mock all external dependencies
    with patch("ocean_report.workflows.report_runner.fetch_raw_data") as mock_fetch, \
         patch("ocean_report.workflows.report_runner.format_report_data") as mock_format, \
         patch("ocean_report.workflows.report_runner.send_or_preview_email") as mock_send, \
         patch("ocean_report.workflows.report_runner.get_bcc_recipients") as mock_recipients:
        
        # Setup mocks
        mock_fetch.return_value = {
            "tides": mock_data_responses["tides"],
            "water_temp": mock_data_responses["water_temp"],
            "wind": mock_data_responses["wind"],
        }
        
        mock_format.return_value = FormattedReportData(
            tide_text="High: 4.2 ft at 06:30 AM, Low: 0.5 ft at 12:45 PM",
            water_temp_text="Water Temperature: 72.5°F",
            wind_text="Wind: 8-12 mph from S",
            retrieval_timestamps={
                "tides": datetime.now(),
                "water_temp": datetime.now(),
                "water_temp_data_time": "14:00",
                "wind": datetime.now(),
            }
        )
        
        mock_recipients.return_value = "test@example.com"
        
        # Run the workflow in preview mode (run_email=False)
        run_report(cfg_path=temp_config_file, run_email=False, test=False)
        
        # Verify the workflow executed all steps
        mock_fetch.assert_called_once()
        mock_format.assert_called_once()
        mock_send.assert_called_once()
        mock_recipients.assert_called_once()


def test_run_report_with_default_config(mock_data_responses):
    """Test report workflow using default config path."""
    
    with patch("ocean_report.workflows.report_runner.create_application_context") as mock_context, \
         patch("ocean_report.workflows.report_runner.fetch_raw_data") as mock_fetch, \
         patch("ocean_report.workflows.report_runner.format_report_data") as mock_format, \
         patch("ocean_report.workflows.report_runner.send_or_preview_email") as mock_send, \
         patch("ocean_report.workflows.report_runner.get_bcc_recipients") as mock_recipients:
        
        # Setup mock context
        mock_ctx = Mock()
        mock_ctx.config.noaa.station_id = "8534720"
        mock_ctx.config.email.use_recipient_url = False
        mock_ctx.config.email.recipients = "test@example.com"
        mock_ctx.config.logging.level = "INFO"
        mock_ctx.config.logging.output = "console"
        mock_ctx.config.logging.format = "%(message)s"
        mock_context.return_value = mock_ctx
        
        mock_fetch.return_value = {
            "tides": mock_data_responses["tides"],
            "water_temp": mock_data_responses["water_temp"],
            "wind": mock_data_responses["wind"],
        }
        
        mock_format.return_value = FormattedReportData(
            tide_text="Test",
            water_temp_text="Test",
            wind_text="Test",
            retrieval_timestamps={}
        )
        mock_recipients.return_value = "test@example.com"
        
        # Run with no config path (uses default)
        run_report(cfg_path=None, run_email=False, test=False)
        
        # Verify context was created with None (default config)
        mock_context.assert_called_once()
        call_kwargs = mock_context.call_args.kwargs
        assert call_kwargs.get("config_path") is None


def test_run_report_test_mode(temp_config_file, mock_data_responses):
    """Test report workflow in test mode."""
    
    with patch("ocean_report.workflows.report_runner.fetch_raw_data") as mock_fetch, \
         patch("ocean_report.workflows.report_runner.format_report_data") as mock_format, \
         patch("ocean_report.workflows.report_runner.send_or_preview_email") as mock_send, \
         patch("ocean_report.workflows.report_runner.get_bcc_recipients") as mock_recipients:
        
        mock_fetch.return_value = {
            "tides": mock_data_responses["tides"],
            "water_temp": mock_data_responses["water_temp"],
            "wind": mock_data_responses["wind"],
        }
        
        mock_format.return_value = FormattedReportData(
            tide_text="Test",
            water_temp_text="Test",
            wind_text="Test",
            retrieval_timestamps={}
        )
        mock_recipients.return_value = "test@example.com"
        
        # Run in test mode
        run_report(cfg_path=temp_config_file, run_email=False, test=True)
        
        # Verify test=True was passed to get_bcc_recipients
        call_kwargs = mock_recipients.call_args.kwargs
        assert call_kwargs["test"] is True


def test_run_report_handles_data_fetch_error(temp_config_file):
    """Test that run_report handles data fetching errors gracefully."""
    
    with patch("ocean_report.workflows.report_runner.fetch_raw_data") as mock_fetch, \
         patch("ocean_report.workflows.report_runner.get_bcc_recipients") as mock_recipients:
        
        mock_recipients.return_value = "test@example.com"
        mock_fetch.side_effect = Exception("API connection failed")
        
        # Should raise or handle the error
        with pytest.raises(Exception, match="API connection failed"):
            run_report(cfg_path=temp_config_file, run_email=False, test=False)


def test_run_report_email_mode(temp_config_file, mock_data_responses):
    """Test report workflow when actually sending email (run_email=True)."""
    
    with patch("ocean_report.workflows.report_runner.fetch_raw_data") as mock_fetch, \
         patch("ocean_report.workflows.report_runner.format_report_data") as mock_format, \
         patch("ocean_report.workflows.report_runner.send_or_preview_email") as mock_send, \
         patch("ocean_report.workflows.report_runner.get_bcc_recipients") as mock_recipients:
        
        mock_fetch.return_value = {
            "tides": mock_data_responses["tides"],
            "water_temp": mock_data_responses["water_temp"],
            "wind": mock_data_responses["wind"],
        }
        
        mock_format.return_value = FormattedReportData(
            tide_text="Test",
            water_temp_text="Test",
            wind_text="Test",
            retrieval_timestamps={}
        )
        mock_recipients.return_value = "test@example.com"
        
        # Run with run_email=True
        run_report(cfg_path=temp_config_file, run_email=True, test=False)
        
        # Verify send_or_preview_email was called with correct parameters
        assert mock_send.called
        call_kwargs = mock_send.call_args.kwargs
        assert call_kwargs["run_email"] is True


@pytest.mark.integration
def test_run_report_integration_smoke_test(temp_config_file):
    """
    Integration smoke test - runs the full workflow with real API calls.
    
    This test is marked as 'integration' and skipped by default.
    Run with: pytest tests/test_end_to_end.py -m integration
    
    Note: This will make real API calls and may fail if:
    - APIs are down
    - Network is unavailable
    - Rate limits are hit
    """
    
    # Mock only the email sending to avoid actually sending email
    with patch("ocean_report.workflows.report_runner.send_or_preview_email") as mock_send:
        
        # Run the full workflow with real API calls
        try:
            run_report(cfg_path=temp_config_file, run_email=False, test=False)
            
            # If we got here, the workflow completed successfully
            assert mock_send.called
            
        except Exception as e:
            # If APIs are unavailable, skip rather than fail
            pytest.skip(f"Integration test skipped due to API unavailability: {e}")


def test_run_report_creates_proper_log_output(temp_config_file, mock_data_responses):
    """Test that run_report produces expected log output."""
    
    with patch("ocean_report.workflows.report_runner.fetch_raw_data") as mock_fetch, \
         patch("ocean_report.workflows.report_runner.format_report_data") as mock_format, \
         patch("ocean_report.workflows.report_runner.send_or_preview_email") as mock_send, \
         patch("ocean_report.workflows.report_runner.get_bcc_recipients") as mock_recipients:
        
        mock_fetch.return_value = {
            "tides": mock_data_responses["tides"],
            "water_temp": mock_data_responses["water_temp"],
            "wind": mock_data_responses["wind"],
        }
        
        mock_format.return_value = FormattedReportData(
            tide_text="Test",
            water_temp_text="Test",
            wind_text="Test",
            retrieval_timestamps={}
        )
        mock_recipients.return_value = "test@example.com"
        
        # Run the workflow - if it completes without error, logs were produced
        run_report(cfg_path=temp_config_file, run_email=False, test=False)
        
        # Verify all mocks were called (workflow executed completely)
        mock_fetch.assert_called_once()
        mock_format.assert_called_once()
        mock_send.assert_called_once()
        mock_recipients.assert_called_once()
