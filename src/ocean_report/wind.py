"""Wind data fetching module for ocean report."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

import requests

from .config import LATITUDE as LAT
from .config import LONGITUDE as LONG
from .logger import logger
from .utils import safe_get


def get_daily_wind_data(
    latitude: float = LAT,
    longitude: float = LONG,
    beach_facing_deg: float = 140.0,
    times_to_get: Optional[Set[str]] = None,
) -> List[Dict[str, Any]]:
    """Fetch daily wind data from Open-Meteo API."""
    if times_to_get is None:
        times_to_get = {"08:00", "12:00", "15:00", "18:00"}

    verbose = False
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "wind_speed_10m,wind_direction_10m",
        "timezone": "America/New_York",
    }

    try:
        # response = requests.get(
        #     "https://api.open-meteo.com/v1/forecast",
        #     params=params,
        #     verify=certifi.where()
        # )
        logger.info(
            "Fetching wind data from Open-Meteo for lat: %s, lon: %s...",
            latitude,
            longitude,
        )
        response = safe_get("https://api.open-meteo.com/v1/forecast", params=params)
        logger.info(
            "\tWind data response status code: %s",
            response.status_code if response else "No Response",
        )
        if response is None:
            raise RuntimeError(
                "Failed to fetch wind data from Open-Meteo after SSL retries"
            )
        response.raise_for_status()
        logger.info("...Open-Meteo wind data fetched successfully.")
        data = response.json()
        if verbose:
            print(json.dumps(data, indent=2))
    except requests.RequestException as e:
        logger.error("Error fetching wind data: %s", e)
        raise RuntimeError(f"Error fetching wind data: {e}") from e

    selected = []
    current_date = datetime.now().date()

    for t, speed, direction in zip(
        data["hourly"]["time"],
        data["hourly"]["wind_speed_10m"],
        data["hourly"]["wind_direction_10m"],
    ):
        dt = datetime.fromisoformat(t)
        if dt.strftime("%H:%M") in times_to_get and dt.date() == current_date:
            deg = direction
            selected.append(
                {
                    "time": dt.strftime("%-I %p"),
                    "speed_kmh": speed,
                    "direction_deg": deg,
                    "speed_mph": kmh_to_mph(speed),
                    "direction": deg_to_16_point_direction(deg),
                    "wind_type": classify_wind_relative_to_beach(
                        deg, beach_facing_deg=beach_facing_deg
                    ),
                }
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
    # Difference between wind and beach orientation (absolute value)
    diff = abs(wind_deg - beach_facing_deg) % 360
    # Adjust difference to be within 180 degrees
    if diff > 180:
        diff = 360 - diff

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
    # Difference between wind and beach orientation
    diff = abs(wind_deg - beach_facing_deg) % 360
    if diff > 180:
        diff = 360 - diff

    if diff <= 22.5:
        return "Onshore"
    if diff <= 45:
        return "On/Cross-shore"  # closer to onshore
    if diff <= 67.5:
        return "Cross/Onshore"  # closer to cross-shore
    if diff <= 90:
        return "Cross-shore"
    if diff <= 112.5:
        return "Cross/Offshore"  # closer to cross-shore
    if diff <= 135:
        return "Off/Cross-shore"  # closer to offshore
    if diff <= 157.5:
        return "Cross/Offshore"  # leaning offshore but still cross-influenced
    return "Offshore"
