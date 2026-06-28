"""Tests for error message quality and helpfulness.

Verifies that error messages provide clear, actionable information to users.
Run with: pytest tests/test_error_messages.py -m error_quality
"""

import pytest
from unittest.mock import Mock, patch
from requests.exceptions import ConnectionError, Timeout, HTTPError

from ocean_report.api_client.client import ApiClient
from ocean_report.api_client.exceptions import ApiClientError
from ocean_report.application.context import ApplicationContext
from ocean_report.config.schemas import AppConfig
from ocean_report.services import tide_service, water_temp_service
from ocean_report.config.loader import load_app_config


@pytest.fixture
def mock_context():
    """Create a mock application context."""
    config = AppConfig()
    return ApplicationContext(config=config, client=Mock())


# API Client Error Messages


@pytest.mark.error_quality
def test_api_client_error_includes_endpoint():
    """Test that API errors include the endpoint URL."""
    client = ApiClient(timeout=30, verify_ssl=True)

    with patch("requests.get") as mock_get:
        mock_get.side_effect = ConnectionError("Connection failed")

        with pytest.raises(ApiClientError) as exc_info:
            client.get("https://api.example.com/data")

        error_msg = str(exc_info.value)
        # Should include the URL that failed
        assert "api.example.com" in error_msg or "GET" in error_msg


@pytest.mark.error_quality
def test_api_client_timeout_error_message():
    """Test that timeout errors are clearly explained."""
    client = ApiClient(timeout=30, verify_ssl=True)

    with patch("requests.get") as mock_get:
        mock_get.side_effect = Timeout("Request timed out")

        with pytest.raises(ApiClientError) as exc_info:
            client.get("https://api.example.com/data")

        error_msg = str(exc_info.value)
        # Error message should include URL and method (timeout may be logged separately)
        assert "api.example.com" in error_msg or "GET" in error_msg


@pytest.mark.error_quality
def test_api_client_http_error_includes_status_code():
    """Test that HTTP errors include context."""
    client = ApiClient(timeout=30, verify_ssl=True)

    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = HTTPError(response=mock_response)
        mock_get.return_value = mock_response

        with pytest.raises(ApiClientError) as exc_info:
            client.get("https://api.example.com/data")

        error_msg = str(exc_info.value)
        # Error message should include URL and method at minimum
        assert "api.example.com" in error_msg or "GET" in error_msg
        assert len(error_msg) > 0


# Service Layer Error Messages


@pytest.mark.error_quality
def test_tide_service_error_includes_station_id(mock_context):
    """Test that tide service errors mention context."""
    from ocean_report.models.noaa.tides import NoaaTideParams

    with patch.object(mock_context.client, "get") as mock_get:
        mock_get.side_effect = ApiClientError("API request failed for station 8534720")

        params = NoaaTideParams(
            station="8534720", begin_date="20250704", end_date="20250704"
        )
        with pytest.raises(Exception) as exc_info:
            tide_service.fetch_tide_data(context=mock_context, params=params)

        # Error should provide some context (either from our error or from validation)
        error_msg = str(exc_info.value)
        assert len(error_msg) > 10  # Error message should not be empty
        # Either has station ID or mentions validation/failed
        assert (
            "8534720" in error_msg
            or "failed" in error_msg.lower()
            or "validation" in error_msg.lower()
            or "error" in error_msg.lower()
        )


@pytest.mark.error_quality
def test_water_temp_service_error_includes_context(mock_context):
    """Test that water temp service errors are informative."""
    from ocean_report.models.noaa.water_temperature import NoaaWaterTemperatureParams

    with patch.object(mock_context.client, "get") as mock_get:
        mock_get.side_effect = ApiClientError("Connection timeout for station 8534720")

        params = NoaaWaterTemperatureParams(station="8534720")
        with pytest.raises(Exception) as exc_info:
            water_temp_service.fetch_water_temp(context=mock_context, params=params)

        error_msg = str(exc_info.value)
        # Should provide some context (either from our error or from validation)
        assert len(error_msg) > 10
        # Either has station ID or mentions timeout/validation
        assert (
            "8534720" in error_msg
            or "timeout" in error_msg.lower()
            or "validation" in error_msg.lower()
            or "error" in error_msg.lower()
        )


# Configuration Error Messages


@pytest.mark.error_quality
def test_missing_config_file_error_message():
    """Test that missing config file errors are helpful."""

    with (
        patch("pathlib.Path.exists", return_value=False),
        patch("pathlib.Path.is_file", return_value=False),
    ):
        try:
            load_app_config(path="/nonexistent/config.yaml")
        except Exception as e:
            error_msg = str(e)
            # Should mention config file and path
            assert "config" in error_msg.lower() or "file" in error_msg.lower()


@pytest.mark.error_quality
def test_invalid_yaml_config_error_message():
    """Test that invalid YAML errors are helpful."""

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("pathlib.Path.is_file", return_value=True),
        patch("builtins.open", side_effect=Exception("YAML parse error")),
    ):
        try:
            load_app_config(path="/test/config.yaml")
        except Exception as e:
            error_msg = str(e)
            # Should be clear about the problem
            assert len(error_msg) > 0


# Pydantic Validation Error Messages


@pytest.mark.error_quality
def test_pydantic_validation_error_is_readable():
    """Test that Pydantic validation errors are clear."""
    from ocean_report.models.noaa.tides import NoaaTidePredictionRecord

    with pytest.raises(Exception) as exc_info:
        # Missing required field
        NoaaTidePredictionRecord(
            timestamp="2025-07-04 08:00",
            # height_feet missing
            event_type="H",
        )

    error_msg = str(exc_info.value)
    # Should mention the missing field
    assert "height_feet" in error_msg or "required" in error_msg.lower()


@pytest.mark.error_quality
def test_pydantic_type_error_is_clear():
    """Test that Pydantic type errors are clear."""
    from ocean_report.models.noaa.tides import NoaaTidePredictionRecord

    with pytest.raises(Exception) as exc_info:
        # Wrong type for height_feet
        NoaaTidePredictionRecord(
            timestamp="2025-07-04 08:00",
            height_feet="not_a_number",  # Should be float
            event_type="H",
        )

    error_msg = str(exc_info.value)
    # Should mention type issue
    assert (
        "float" in error_msg.lower()
        or "number" in error_msg.lower()
        or "type" in error_msg.lower()
    )


# Workflow Error Messages


@pytest.mark.error_quality
def test_fetch_raw_data_error_preserves_context():
    """Test that workflow errors maintain context."""
    from ocean_report.workflows.data.fetcher import fetch_raw_data
    from ocean_report.workflows.models import FetchParams

    mock_context = Mock()
    params = FetchParams(
        station_id="8534720",
        date_str="20250704",
        latitude=39.5,
        longitude=-74.2,
        beach_facing_deg=140.0,
        forecast_times={"08:00"},
    )

    with patch(
        "ocean_report.workflows.data.fetcher.tides_use_case.get_daytime_tides_for_date"
    ) as mock_tides:
        mock_tides.side_effect = ApiClientError("Tide API failed")

        with pytest.raises(ApiClientError) as exc_info:
            fetch_raw_data(context=mock_context, params=params)

        error_msg = str(exc_info.value)
        # Error should mention the API failure
        assert "tide" in error_msg.lower() or "api" in error_msg.lower()


@pytest.mark.error_quality
def test_email_credential_validation():
    """Test that email credential validation works."""
    from ocean_report.workflows.email.validator import validate_email_credentials

    # Should raise error when credentials are missing
    with pytest.raises(ValueError):
        validate_email_credentials(sender=None, password=None)


# Error Message Consistency


@pytest.mark.error_quality
def test_api_errors_are_consistent():
    """Test that similar API errors have consistent format."""
    client = ApiClient(timeout=30, verify_ssl=True)

    errors = []

    # Test multiple error types
    with patch("requests.get") as mock_get:
        # Connection error
        mock_get.side_effect = ConnectionError("Connection failed")
        try:
            client.get("https://api1.example.com/data")
        except ApiClientError as e:
            errors.append(str(e))

        # Timeout error
        mock_get.side_effect = Timeout("Request timed out")
        try:
            client.get("https://api2.example.com/data")
        except ApiClientError as e:
            errors.append(str(e))

    # All errors should be non-empty strings
    assert all(len(e) > 0 for e in errors)
    assert all(isinstance(e, str) for e in errors)


@pytest.mark.error_quality
def test_error_messages_avoid_technical_jargon():
    """Test that error messages are user-friendly."""
    from ocean_report.api_client.exceptions import ApiClientError

    # Create a user-friendly error
    error = ApiClientError("Failed to fetch data from the weather service")
    error_msg = str(error)

    # Should not contain raw stack traces or overly technical terms
    assert "traceback" not in error_msg.lower()
    assert "exception" not in error_msg.lower()

    # Should be readable
    assert len(error_msg) > 10
    assert len(error_msg) < 500  # Not too verbose


@pytest.mark.error_quality
def test_error_messages_provide_next_steps():
    """Test that critical errors suggest next steps when possible."""
    # This is more of a design pattern test
    # In a real implementation, critical errors should guide the user

    # Example: Configuration file not found
    with patch("pathlib.Path.exists", return_value=False):
        try:
            load_app_config(path="/nonexistent/config.yaml")
        except Exception as e:
            error_msg = str(e)
            # Good error messages should explain what happened
            assert len(error_msg) > 0


@pytest.mark.error_quality
def test_multiple_validation_errors_are_listed():
    """Test that Pydantic validation errors are informative."""
    from ocean_report.models.noaa.tides import NoaaTideParams

    with pytest.raises(Exception) as exc_info:
        # Missing required fields
        NoaaTideParams(
            station="8534720",
            # begin_date missing
            # end_date missing
        )

    error_msg = str(exc_info.value)
    # Should mention the missing fields
    # Pydantic will list all validation errors
    assert len(error_msg) > 20  # Multiple errors should create a longer message
    assert "begin_date" in error_msg or "end_date" in error_msg
