"""Tide use cases - orchestration layer for tide-related workflows."""

from datetime import datetime
from typing import List

from ..application.factory import ApplicationContext
from ..logger import logger
from ..models.noaa.tides import NoaaTideParams, NoaaTidePredictionRecord
from ..services.tide_service import fetch_tide_data, filter_daytime_tides


def get_daytime_tides_for_date(
    *,
    context: ApplicationContext,
    station_id: str | None = None,
    date: str | None = None,
) -> List[NoaaTidePredictionRecord]:
    """
    Get filtered daytime tide predictions for a specific date.

    This is the main orchestration function for tide workflows. It:
    1. Resolves defaults (today's date, configured station)
    2. Fetches raw tide data from NOAA
    3. Filters to daytime hours only
    4. Returns the final filtered list

    Args:
        context (ApplicationContext): The application context containing configuration and API client.
        station_id (str | None): NOAA station ID. If None, uses station from config.
        date (str | None): Date for predictions in YYYYMMDD format. If None, uses today.

    Returns:
        List[NoaaTidePredictionRecord]: Filtered list of daytime tide predictions.

    Raises:
        ApiClientError: If the NOAA API request fails.
    """
    # Resolve defaults at the orchestration layer
    if station_id is None:
        station_id = context.config.noaa.station_id
        logger.debug("Using station_id from config: %s", station_id)

    if date is None:
        date = datetime.now().strftime("%Y%m%d")
        logger.debug("Using today's date: %s", date)

    # Build request parameters
    params = NoaaTideParams(
        begin_date=date,
        end_date=date,
        station=station_id,
    )

    # Fetch raw tide data (service layer - API only)
    logger.info("Fetching tide data for station: %s on date: %s", station_id, date)
    raw_tides = fetch_tide_data(context=context, params=params)

    if not raw_tides:
        logger.warning("No tide predictions returned for station %s on %s", station_id, date)
        return []

    logger.info("Fetched %d tide predictions", len(raw_tides))

    # Apply business logic: filter to daytime hours
    daytime_tides = filter_daytime_tides(raw_tides)
    logger.info("Filtered to %d daytime tide predictions", len(daytime_tides))

    return daytime_tides


__all__ = ["get_daytime_tides_for_date"]
