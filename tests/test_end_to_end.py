"""End-to-end tests for the ocean report workflow.

These tests verify the complete workflow from configuration loading through
data fetching, formatting, and email generation.
"""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

from ocean_report.workflows.report_runner import run_report
from ocean_report.workflows.models import RawReportData
from ocean_report.models.email import EmailTemplateData
from ocean_report.models.noaa.tides import NoaaTidePredictionRecord


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

reporting:
  station_name: "Test Station"
  station_city: "Test City"
  wind_provider: "Open-Meteo"
  template_path: null
  
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
    }


def test_run_report_preview_mode(temp_config_file, mock_data_responses):
    """Test the full report workflow in preview mode (no email sent)."""
    
    # Mock all external dependencies
    with patch("ocean_report.workflows.report_runner.fetch_raw_data") as mock_fetch, \
         patch("ocean_report.workflows.report_runner.format_report_data") as mock_format, \
         patch("ocean_report.workflows.report_runner.send_or_preview_email") as mock_send, \
         patch("ocean_report.workflows.report_runner.get_bcc_recipients") as mock_recipients, \
         patch("ocean_report.workflows.report_runner.render_email_template") as mock_render:
        
        # Setup mocks
        mock_fetch.return_value = RawReportData(
            tides=mock_data_responses["tides"],
            tide_timestamp=datetime.now(),
            water_temp=72.5,
            water_temp_timestamp=datetime.now(),
            water_temp_data_time="14:00",
            wind_forecast=[],
            wind_timestamp=datetime.now(),
        )
        
        mock_format.return_value = EmailTemplateData(
            long_date="Monday, July 4, 2025",
            water_temp="72.5 °F",
            tide_info="High: 4.2 ft at 06:30 AM, Low: 0.5 ft at 12:45 PM",
            wind_info="Wind: 8-12 mph from S",
            station_name="Test Station",
            station_city="Test City",
            wind_provider="Open-Meteo",
            date_retrieved="Jul 4 at 6:00 AM",
            water_temp_measured_at_date="14:00"
        )
        
        mock_render.return_value = "Email body content"
        mock_recipients.return_value = ["test@example.com"]
        
        # Run the workflow in preview mode (run_email=False)
        run_report(cfg_path=temp_config_file, run_email=False, test=False)
        
        # Verify the workflow executed all steps
        mock_fetch.assert_called_once()
        mock_format.assert_called_once()
        mock_render.assert_called_once()
        mock_send.assert_called_once()
        mock_recipients.assert_called_once()


def test_run_report_with_default_config(mock_data_responses):
    """Test report workflow using default config path."""
    
    with patch("ocean_report.workflows.report_runner.create_application_context") as mock_context, \
         patch("ocean_report.workflows.report_runner.fetch_raw_data") as mock_fetch, \
         patch("ocean_report.workflows.report_runner.format_report_data") as mock_format, \
         patch("ocean_report.workflows.report_runner.send_or_preview_email") as mock_send, \
         patch("ocean_report.workflows.report_runner.get_bcc_recipients") as mock_recipients, \
         patch("ocean_report.workflows.report_runner.render_email_template") as mock_render:
        
        # Setup mock context
        mock_ctx = Mock()
        mock_ctx.config.noaa.station_id = "8534720"
        mock_ctx.config.email.use_recipient_url = False
        mock_ctx.config.email.recipients = "test@example.com"
        mock_ctx.config.logging.level = "INFO"
        mock_ctx.config.logging.output = "console"
        mock_ctx.config.logging.format = "%(message)s"
        mock_ctx.config.location.latitude = 39.5
        mock_ctx.config.location.longitude = -74.2
        mock_ctx.config.location.beach_orientation_degrees = 140
        mock_ctx.config.reporting.template_path = None
        mock_context.return_value = mock_ctx
        
        mock_fetch.return_value = RawReportData(
            tides=mock_data_responses["tides"],
            tide_timestamp=datetime.now(),
            water_temp=72.5,
            water_temp_timestamp=datetime.now(),
            water_temp_data_time="14:00",
            wind_forecast=[],
            wind_timestamp=datetime.now(),
        )
        
        mock_format.return_value = EmailTemplateData(
            long_date="Test",
            water_temp="Test",
            tide_info="Test",
            wind_info="Test",
            station_name="Test",
            station_city="Test",
            wind_provider="Test",
            date_retrieved="Test",
            water_temp_measured_at_date=None
        )
        mock_render.return_value = "Email body"
        mock_recipients.return_value = ["test@example.com"]
        
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
         patch("ocean_report.workflows.report_runner.get_bcc_recipients") as mock_recipients, \
         patch("ocean_report.workflows.report_runner.render_email_template") as mock_render:
        
        mock_fetch.return_value = RawReportData(
            tides=mock_data_responses["tides"],
            tide_timestamp=datetime.now(),
            water_temp=72.5,
            water_temp_timestamp=datetime.now(),
            water_temp_data_time="14:00",
            wind_forecast=[],
            wind_timestamp=datetime.now(),
        )
        
        mock_format.return_value = EmailTemplateData(
            long_date="Test",
            water_temp="Test",
            tide_info="Test",
            wind_info="Test",
            station_name="Test",
            station_city="Test",
            wind_provider="Test",
            date_retrieved="Test",
            water_temp_measured_at_date=None
        )
        mock_render.return_value = "Email body"
        mock_recipients.return_value = ["test@example.com"]
        
        # Run in test mode
        run_report(cfg_path=temp_config_file, run_email=False, test=True)
        
        # Verify test=True was passed to get_bcc_recipients
        call_kwargs = mock_recipients.call_args.kwargs
        assert call_kwargs["test"] is True
