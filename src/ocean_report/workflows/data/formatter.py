"""Data formatting operations for ocean report."""

from ...config import get_settings
from ...emailer import template_helpers
from ...models.email import EmailTemplateData
from ..models import RawReportData


def format_report_data(raw_data: RawReportData) -> EmailTemplateData:
    """Format raw data into email template data.

    Pure formatting layer - takes raw data, returns EmailTemplateData
    ready for template rendering.

    Args:
        raw_data: Raw data from APIs

    Returns:
        EmailTemplateData ready for template rendering
    """
    # Get config for station/provider info
    config = get_settings()

    # Format all data sections
    water_temp_str = template_helpers.format_water_temp_value(raw_data.water_temp)
    tide_str = template_helpers.format_tide_info(raw_data.tides)
    wind_str = template_helpers.format_wind_info(raw_data.wind_forecast)

    # Format timestamps
    retrieval_time = raw_data.water_temp_timestamp or raw_data.tide_timestamp
    date_retrieved = template_helpers.format_retrieval_timestamp(retrieval_time)

    # Build and return EmailTemplateData
    return EmailTemplateData(
        long_date=template_helpers.format_long_date(),
        water_temp=water_temp_str,
        tide_info=tide_str,
        wind_info=wind_str,
        station_name=config.reporting.station_name,
        station_city=config.reporting.station_city,
        wind_provider=config.reporting.wind_provider,
        date_retrieved=date_retrieved,
        water_temp_measured_at_date=raw_data.water_temp_data_time,
    )
