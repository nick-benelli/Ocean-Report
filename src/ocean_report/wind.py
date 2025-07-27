# src/ocean_report/wind.py
import requests
from datetime import datetime
import json
from typing import Set, List, Dict, Any
from .config import LONGITUDE as LONG, LATITUDE as LAT


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
        response = requests.get("https://api.open-meteo.com/v1/forecast", params=params)
        response.raise_for_status()
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
    """
    diff = abs(wind_deg - beach_facing_deg) % 360
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
