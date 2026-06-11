"""Water temperature use cases - orchestration layer for water temperature workflows."""

from typing import Optional

from ..application.factory import ApplicationContext
from ..logger import logger
from ..models.noaa.water_temperature import NoaaWaterTempParams
from ..services.water_temp_service import fetch_water_temp


def get_latest_water_temp(
    *,
    context: ApplicationContext,
    station_id: str | None = None,
) -> Optional[float]:
    """
    Get the latest water temperature for a station.

    This is the main orchestration function for water temperature workflows. It:
    1. Resolves defaults (configured station)
    2. Fetches latest water temperature from NOAA
    3. Extracts and returns the temperature value

    Args:
        context (ApplicationContext): The application context containing configuration and API client.
        station_id (str | None): NOAA station ID. If None, uses station from config.

    Returns:
        Optional[float]: Latest water temperature in Fahrenheit, or None if no data available.

    Raises:
        ApiClientError: If the NOAA API request fails.
    """
    # Resolve defaults at the orchestration layer
    if station_id is None:
        station_id = context.config.noaa.station_id
        logger.debug("Using station_id from config: %s", station_id)

    # Build request parameters
    params = NoaaWaterTempParams(
        station=station_id,
        date="latest",  # Always fetch latest for water temp
    )

    # Fetch latest water temperature data (service layer - API only)
    logger.info("Fetching latest water temperature for station: %s", station_id)
    water_temp_record = fetch_water_temp(context=context, params=params)

    if water_temp_record is None:
        logger.warning("No water temperature data returned for station %s", station_id)
        return None

    temperature = water_temp_record.temperature
    logger.info("Latest water temperature: %.1f°F", temperature)

    return temperature


def format_water_temp_with_unit(temp: float) -> str:
    """
    Format the water temperature value as a string with the Fahrenheit symbol.

    Args:
        temp (float): Temperature value in Fahrenheit.

    Returns:
        str: Formatted temperature string (e.g., "72.5 °F").
    """
    return f"{temp:.1f} °F"


__all__ = ["get_latest_water_temp", "format_water_temp_with_unit"]
