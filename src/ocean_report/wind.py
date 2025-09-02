# src/ocean_report/wind.py
import requests
from datetime import datetime
import json
import certifi
from typing import Set, List, Dict, Any, Optional
from .config import LONGITUDE as LONG, LATITUDE as LAT
from .logger import logger


def get_daily_wind_data(
    latitude: float = LAT,
    longitude: float = LONG,
    beach_facing_deg: float = 140.0,
    times_to_get: Set[str] = {"08:00", "12:00", "15:00", "18:00"},
) -> List[Dict[str, Any]]:
    """
    Retrieve hourly wind data and filter it for the specified times today.
    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        beach_facing_deg (float): Orientation of the beach in degrees.
        times_to_get (Set[str]): Set of times to filter the wind data.
    Returns:
        List[Dict[str, Any]]: List of dictionaries containing wind data for the specified times.
    Raises:
        RuntimeError: If there is an error fetching the wind data.
    """
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
        response = safe_get(
            "https://api.open-meteo.com/v1/forecast", params=params, timeout=10
        )
        response.raise_for_status()
        if response is None:
            return None
        data = response.json()
        if verbose:
            print(json.dumps(data, indent=2))
    except requests.RequestException as e:
        raise RuntimeError(f"Error fetching wind data: {e}")

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
    elif diff <= 67.5:
        return "Cross/Onshore"
    elif diff <= 112.5:
        return "Cross-shore"
    elif diff <= 157.5:
        return "Cross/Offshore"
    else:
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
    elif diff <= 45:
        return "On/Cross-shore"  # closer to onshore
    elif diff <= 67.5:
        return "Cross/Onshore"  # closer to cross-shore
    elif diff <= 90:
        return "Cross-shore"
    elif diff <= 112.5:
        return "Cross/Offshore"  # closer to cross-shore
    elif diff <= 135:
        return "Off/Cross-shore"  # closer to offshore
    elif diff <= 157.5:
        return "Cross/Offshore"  # leaning offshore but still cross-influenced
    else:
        return "Offshore"


def safe_get(url: str, **kwargs) -> Optional[requests.Response]:
    """
    Try to GET with certifi verification first.
    If SSL fails, retry with verify=False.
    """
    try:
        return requests.get(url, verify=certifi.where(), **kwargs)
    except requests.exceptions.SSLError as e:
        logger.warning("SSL verification failed (%s). Retrying with verify=False.", e)
        try:
            return requests.get(url, verify=False, **kwargs)
        except requests.exceptions.RequestException as e2:
            logger.error("Request failed even with verify=False: %s", e2)
            return None
