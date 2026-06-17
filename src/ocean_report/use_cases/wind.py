"""Wind use cases - orchestration layer for wind forecast workflows."""

from datetime import datetime
from typing import Any, Dict, List, Set, Tuple

from ..application.factory import ApplicationContext
from ..logger import logger
from ..models.openmeteo.forecast import OpenMeteoForecastParams
from ..services.wind_service import fetch_wind_forecast
from ..utils.wind_utils import (
    classify_wind_relative_to_beach,
    deg_to_16_point_direction,
    kmh_to_mph,
)


def get_daily_wind_forecast(
    *,
    context: ApplicationContext,
    latitude: float | None = None,
    longitude: float | None = None,
    beach_facing_deg: float | None = None,
    times_to_get: Set[str] | None = None,
) -> Tuple[List[Dict[str, Any]], datetime]:
    """
    Get daily wind forecast for specified times.

    This is the main orchestration function for wind workflows. It:
    1. Resolves defaults (lat/lon/beach_facing from config)
    2. Fetches raw wind forecast from Open-Meteo
    3. Filters to specified times and current date
    4. Transforms each entry with wind calculations
    5. Returns list of normalized wind entries

    Args:
        context (ApplicationContext): The application context containing
            configuration and API client.
        latitude (float | None): Location latitude. If None, uses config value.
        longitude (float | None): Location longitude. If None, uses config value.
        beach_facing_deg (float | None): Beach orientation in degrees.
            If None, uses config value.
        times_to_get (Set[str] | None): Set of times in "HH:MM" format to filter
            (e.g., {"08:00", "12:00"}).
            If None, defaults to {"08:00", "12:00", "15:00", "18:00"}.

    Returns:
        Tuple[List[Dict[str, Any]], datetime]:
            - List of wind forecast entries for the specified times today
            - Timestamp when data was retrieved

    Raises:
        ApiClientError: If the Open-Meteo API request fails.
    """
    # Resolve defaults at the orchestration layer
    if times_to_get is None:
        times_to_get = {"08:00", "12:00", "15:00", "18:00"}
        logger.debug("Using default times: %s", times_to_get)

    if latitude is None:
        latitude = context.config.location.latitude
        logger.debug("Using latitude from config: %.4f", latitude)

    if longitude is None:
        longitude = context.config.location.longitude
        logger.debug("Using longitude from config: %.4f", longitude)

    if beach_facing_deg is None:
        beach_facing_deg = context.config.location.beach_orientation_degrees
        logger.debug("Using beach orientation from config: %.1f°", beach_facing_deg)

    # Build request parameters
    params = OpenMeteoForecastParams(
        latitude=latitude,
        longitude=longitude,
        hourly="wind_speed_10m,wind_direction_10m",
        timezone="America/New_York",
    )

    # Capture retrieval timestamp
    retrieval_time = datetime.now()

    # Fetch raw wind forecast data (service layer - API only)
    logger.info("Fetching wind forecast for lat: %.4f, lon: %.4f", latitude, longitude)
    forecast_response = fetch_wind_forecast(context=context, params=params)

    # Apply business logic: filter by time and current date, then transform
    selected_forecasts = []
    current_date = datetime.now().date()

    for timestamp, speed_kmh, direction_deg in zip(
        forecast_response.hourly.time,
        forecast_response.hourly.wind_speed_10m,
        forecast_response.hourly.wind_direction_10m,
    ):
        forecast_time = datetime.fromisoformat(timestamp)

        # Filter: only specified times and current date
        if (
            forecast_time.strftime("%H:%M") in times_to_get
            and forecast_time.date() == current_date
        ):
            wind_entry = _build_wind_entry(
                timestamp=timestamp,
                speed_kmh=speed_kmh,
                direction_deg=direction_deg,
                beach_facing_deg=beach_facing_deg,
            )
            selected_forecasts.append(wind_entry)

    logger.info(
        "Filtered wind forecast to %d entries for today at specified times",
        len(selected_forecasts),
    )

    return selected_forecasts, retrieval_time


def _build_wind_entry(
    timestamp: str,
    speed_kmh: float,
    direction_deg: float,
    beach_facing_deg: float,
) -> Dict[str, Any]:
    """
    Build a normalized wind forecast entry with all derived fields.

    Args:
        timestamp (str): ISO format timestamp.
        speed_kmh (float): Wind speed in km/h.
        direction_deg (float): Wind direction in degrees.
        beach_facing_deg (float): Beach orientation in degrees.

    Returns:
        Dict[str, Any]: Normalized wind entry with time, speeds, directions, and classification.
    """
    forecast_time = datetime.fromisoformat(timestamp)
    return {
        "time": forecast_time.strftime("%-I %p"),
        "speed_kmh": speed_kmh,
        "direction_deg": direction_deg,
        "speed_mph": kmh_to_mph(speed_kmh),
        "direction": deg_to_16_point_direction(direction_deg),
        "wind_type": classify_wind_relative_to_beach(
            direction_deg, beach_facing_deg=beach_facing_deg
        ),
    }


__all__ = ["get_daily_wind_forecast"]
