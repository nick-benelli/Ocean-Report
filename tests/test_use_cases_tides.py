"""Tests for tide use cases."""

from datetime import datetime
from unittest.mock import Mock, patch
import pytest

from ocean_report.application.context import ApplicationContext
from ocean_report.config.schemas import AppConfig, NoaaConfig
from ocean_report.models.noaa.tides import NoaaTidePredictionRecord
from ocean_report.use_cases.tides import get_daytime_tides_for_date


@pytest.fixture
def mock_context():
    """Create a mock application context."""
    config = AppConfig(noaa=NoaaConfig(station_id="8534720", buoy_id="44091"))
    return ApplicationContext(config=config, client=Mock())


def test_get_daytime_tides_uses_config_defaults(mock_context):
    """Test that get_daytime_tides_for_date uses config defaults when not provided."""

    mock_tides = [
        NoaaTidePredictionRecord(
            timestamp="2025-07-04 08:00", height_feet=4.2, event_type="H"
        ),
        NoaaTidePredictionRecord(
            timestamp="2025-07-04 14:30", height_feet=0.5, event_type="L"
        ),
    ]

    with (
        patch("ocean_report.use_cases.tides.fetch_tide_data") as mock_fetch,
        patch("ocean_report.use_cases.tides.filter_daytime_tides") as mock_filter,
    ):
        mock_fetch.return_value = mock_tides
        mock_filter.return_value = mock_tides

        result, timestamp = get_daytime_tides_for_date(context=mock_context)

        # Verify it used config station_id
        call_args = mock_fetch.call_args
        assert call_args.kwargs["context"] is mock_context
        assert call_args.kwargs["params"].station == "8534720"

        # Verify it used today's date
        today_yyyymmdd = datetime.now().strftime("%Y%m%d")
        assert call_args.kwargs["params"].begin_date == today_yyyymmdd
        assert call_args.kwargs["params"].end_date == today_yyyymmdd

        # Verify filtering was applied
        mock_filter.assert_called_once_with(mock_tides)

        # Verify result
        assert result == mock_tides
        assert isinstance(timestamp, datetime)


def test_get_daytime_tides_with_custom_station(mock_context):
    """Test that custom station_id overrides config."""

    with (
        patch("ocean_report.use_cases.tides.fetch_tide_data") as mock_fetch,
        patch("ocean_report.use_cases.tides.filter_daytime_tides") as mock_filter,
    ):
        mock_fetch.return_value = []
        mock_filter.return_value = []

        get_daytime_tides_for_date(context=mock_context, station_id="9999999")

        # Verify custom station was used
        call_args = mock_fetch.call_args
        assert call_args.kwargs["params"].station == "9999999"


def test_get_daytime_tides_with_custom_date(mock_context):
    """Test that custom date overrides today's date."""

    with (
        patch("ocean_report.use_cases.tides.fetch_tide_data") as mock_fetch,
        patch("ocean_report.use_cases.tides.filter_daytime_tides") as mock_filter,
    ):
        mock_fetch.return_value = []
        mock_filter.return_value = []

        get_daytime_tides_for_date(context=mock_context, date="20250815")

        # Verify custom date was used
        call_args = mock_fetch.call_args
        assert call_args.kwargs["params"].begin_date == "20250815"
        assert call_args.kwargs["params"].end_date == "20250815"


def test_get_daytime_tides_returns_empty_list_when_no_data(mock_context):
    """Test handling of empty tide data."""

    with (
        patch("ocean_report.use_cases.tides.fetch_tide_data") as mock_fetch,
        patch("ocean_report.use_cases.tides.filter_daytime_tides") as mock_filter,
    ):
        mock_fetch.return_value = []
        mock_filter.return_value = []

        result = get_daytime_tides_for_date(context=mock_context)

        # When no data, function returns just empty list (not tuple)
        assert result == []


def test_get_daytime_tides_filters_nighttime(mock_context):
    """Test that nighttime tides are filtered out."""

    all_tides = [
        NoaaTidePredictionRecord(
            timestamp="2025-07-04 02:00",  # Nighttime
            height_feet=3.5,
            event_type="H",
        ),
        NoaaTidePredictionRecord(
            timestamp="2025-07-04 08:00",  # Daytime
            height_feet=4.2,
            event_type="H",
        ),
        NoaaTidePredictionRecord(
            timestamp="2025-07-04 22:00",  # Nighttime
            height_feet=0.3,
            event_type="L",
        ),
    ]

    daytime_only = [all_tides[1]]  # Only the 08:00 tide

    with (
        patch("ocean_report.use_cases.tides.fetch_tide_data") as mock_fetch,
        patch("ocean_report.use_cases.tides.filter_daytime_tides") as mock_filter,
    ):
        mock_fetch.return_value = all_tides
        mock_filter.return_value = daytime_only

        result, _ = get_daytime_tides_for_date(context=mock_context)

        assert len(result) == 1
        assert result[0].timestamp == "2025-07-04 08:00"
