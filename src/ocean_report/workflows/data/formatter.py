"""Data formatting operations for ocean report."""

from ...emailer import email_formatter as formatter
from ..models import RawReportData, FormattedReportData


def format_report_data(raw_data: RawReportData) -> FormattedReportData:
    """Format raw data into email-ready text sections.

    Pure formatting layer - takes raw data, returns formatted text.

    Args:
        raw_data: Raw data from APIs

    Returns:
        FormattedReportData with text sections ready for email
    """
    tide_text = formatter.format_tide_for_email(raw_data.tides)
    water_temp_text = formatter.format_water_temp(raw_data.water_temp)
    wind_text = formatter.format_wind_forecast_email(raw_data.wind_forecast)

    retrieval_timestamps = {
        "tides": raw_data.tide_timestamp,
        "water_temp": raw_data.water_temp_timestamp,
        "water_temp_data_time": raw_data.water_temp_data_time,
        "wind": raw_data.wind_timestamp,
    }

    return FormattedReportData(
        tide_text=tide_text,
        water_temp_text=water_temp_text,
        wind_text=wind_text,
        retrieval_timestamps=retrieval_timestamps,
    )
