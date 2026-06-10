"""Wind data fetching module for ocean report."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Set

import requests

from .api_client import ApiClientError, get_api_client
from .config import get_settings
from .logger import logger


def _fetch_wind_payload(latitude: float, longitude: float) -> Dict[str, Any]:
    """Fetch hourly wind payload from Open-Meteo."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "wind_speed_10m,wind_direction_10m",
        "timezone": "America/New_York",
    }

    try:
        logger.info(
            "Fetching wind data from Open-Meteo for lat: %s, lon: %s...",
            latitude,
            longitude,
        )
        response = get_api_client().get(
            "https://api.open-meteo.com/v1/forecast", params=params
        )
        logger.info(
            "\tWind data response status code: %s",
            response.status_code,
        )
        logger.info("...Open-Meteo wind data fetched successfully.")
        return response.json()
    except (ApiClientError, requests.RequestException) as exc:
        logger.error("Error fetching wind data: %s", exc)
        raise RuntimeError(f"Error fetching wind data: {exc}") from exc


def _build_wind_entry(
    timestamp: str, speed_kmh: float, direction_deg: float, beach_facing_deg: float
) -> Dict[str, Any]:
    """Normalize one hourly wind forecast entry."""
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


def _relative_angle_difference(wind_deg: float, beach_facing_deg: float) -> float:
    """Return the smallest angular difference between wind and beach orientation."""
    diff = abs(wind_deg - beach_facing_deg) % 360
    if diff > 180:
        return 360 - diff
    return diff


def get_daily_wind_data(
    latitude: float | None = None,
    longitude: float | None = None,
    beach_facing_deg: float | None = None,
    times_to_get: Optional[Set[str]] = None,
) -> List[Dict[str, Any]]:
    """Fetch daily wind data from Open-Meteo API."""
    if times_to_get is None:
        times_to_get = {"08:00", "12:00", "15:00", "18:00"}

    if latitude is None or longitude is None or beach_facing_deg is None:
        settings = get_settings()
        latitude = settings.location.latitude if latitude is None else latitude
        longitude = settings.location.longitude if longitude is None else longitude
        if beach_facing_deg is None:
            beach_facing_deg = settings.location.beach_orientation_degrees

    data = _fetch_wind_payload(latitude=latitude, longitude=longitude)

    selected = []
    current_date = datetime.now().date()

    for timestamp, speed_kmh, direction_deg in zip(
        data["hourly"]["time"],
        data["hourly"]["wind_speed_10m"],
        data["hourly"]["wind_direction_10m"],
    ):
        forecast_time = datetime.fromisoformat(timestamp)
        if forecast_time.strftime("%H:%M") in times_to_get and forecast_time.date() == current_date:
            selected.append(
                _build_wind_entry(
                    timestamp=timestamp,
                    speed_kmh=speed_kmh,
                    direction_deg=direction_deg,
                    beach_facing_deg=beach_facing_deg,
                )
            )

    return selected


def kmh_to_mph(kmh: float) -> float:
    """
    Convert kilometers per hour to miles per hour.
    """
    return round(kmh * 0.621371, 1)


def deg_to_16_point_direction(deg: float) -> str:
    """
    Convert degrees into one of the 16 compass rose directions.
    """
    # Ordered List of Compass Rose Directions
    directions = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]
    index = round(deg / 22.5) % 16
    return directions[index]


def classify_wind_relative_to_beach(
    wind_deg: float, beach_facing_deg: float = 140.0
) -> str:
    """
    Classify wind direction relative to beach orientation.
    Args:
        wind_deg (float): Wind direction in degrees.
        beach_facing_deg (float): Beach orientation in degrees.
    Returns:
        str: Classification of wind direction relative to beach orientation.
    """
    diff = _relative_angle_difference(wind_deg, beach_facing_deg)

    if diff <= 22.5:
        return "Onshore"
    if diff <= 67.5:
        return "Cross/Onshore"
    if diff <= 112.5:
        return "Cross-shore"
    if diff <= 157.5:
        return "Cross/Offshore"
    return "Offshore"


def classify_wind_relative_to_beach_breakdown(
    wind_deg: float, beach_facing_deg: float = 140.0
) -> str:
    """
    Classify wind direction relative to beach orientation.
    Labels:
        - Onshore
        - On/Cross-shore (leans more onshore than cross)
        - Cross-shore
        - Off/Cross-shore (leans more offshore than cross)
        - Offshore
    """
    diff = _relative_angle_difference(wind_deg, beach_facing_deg)
    thresholds = [
        (22.5, "Onshore"),
        (45, "On/Cross-shore"),
        (67.5, "Cross/Onshore"),
        (90, "Cross-shore"),
        (112.5, "Cross/Offshore"),
        (135, "Off/Cross-shore"),
        (157.5, "Cross/Offshore"),
    ]

    for threshold, label in thresholds:
        if diff <= threshold:
            return label
    return "Offshore"
