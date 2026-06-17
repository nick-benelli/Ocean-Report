"""Data fetching operations for ocean report."""

import time
from ...application import ApplicationContext
from ...logger import logger
from ...use_cases import tides as tides_use_case
from ...use_cases import water_temperature as water_temp_use_case
from ...use_cases import wind as wind_use_case
from ..models import FetchParams, RawReportData


def fetch_raw_data(context: ApplicationContext, params: FetchParams) -> RawReportData:
    """Fetch raw data from all APIs without any formatting.

    Pure data fetching layer - no formatting, just retrieval.

    Args:
        context: Application context
        params: Fetch parameters

    Returns:
        RawReportData with all fetched information

    Raises:
        ApiClientError: If any critical API call fails
    """
    # Fetch tide data
    logger.info("  → Fetching tide data from NOAA...")
    fetch_start = time.time()
    daytime_tides, tide_timestamp = tides_use_case.get_daytime_tides_for_date(
        context=context,
        station_id=params.station_id,
        date=params.date_str,
    )
    logger.info(
        "  ✓ Tide data fetched in %.2f seconds (%d events)",
        time.time() - fetch_start,
        len(daytime_tides),
    )

    # Fetch water temperature
    logger.info("  → Fetching water temperature from NOAA...")
    fetch_start = time.time()
    water_temp, water_temp_timestamp, water_temp_data_time = (
        water_temp_use_case.get_latest_water_temp(
            context=context,
            station_id=params.station_id,
        )
    )
    logger.info(
        "  ✓ Water temperature fetched in %.2f seconds (%.1f°F)",
        time.time() - fetch_start,
        water_temp if water_temp else 0.0,
    )

    # Fetch wind forecast with graceful error handling
    logger.info("  → Fetching wind forecast from Open-Meteo...")
    fetch_start = time.time()
    try:
        wind_forecast, wind_timestamp = wind_use_case.get_daily_wind_forecast(
            context=context,
            latitude=params.latitude,
            longitude=params.longitude,
            beach_facing_deg=params.beach_facing_deg,
            times_to_get=params.forecast_times,
        )
        logger.info(
            "  ✓ Wind forecast fetched in %.2f seconds (%d time slots)",
            time.time() - fetch_start,
            len(wind_forecast),
        )
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.warning(
            "  ⚠ Wind forecast unavailable after %.2f seconds: %s",
            time.time() - fetch_start,
            str(exc),
        )
        logger.debug("Wind API error details:", exc_info=True)
        # Provide fallback
        wind_forecast = []
        wind_timestamp = None
        logger.info("  → Continuing with report despite wind data failure")

    return RawReportData(
        tides=daytime_tides,
        tide_timestamp=tide_timestamp,
        water_temp=water_temp,
        water_temp_timestamp=water_temp_timestamp,
        water_temp_data_time=water_temp_data_time,
        wind_forecast=wind_forecast,
        wind_timestamp=wind_timestamp,
    )
