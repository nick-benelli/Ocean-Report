import requests
from typing import Optional
from .config import STATION_ID
from .logger import logger


def fetch_water_temp(station_id: str = STATION_ID) -> Optional[float]:
    """
    Fetch the latest water temperature in Fahrenheit from NOAA API.

    Args:
        station_id (str): NOAA Station ID. Defaults to STATION_ID.

    Returns:
        Optional[float]: Latest recorded water temperature in Fahrenheit, or None if fetch fails.
    """
    base_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"

    params = {
        "product": "water_temperature",
        "application": "chatgpt-tide-app",
        "station": station_id,
        "date": "latest",
        "units": "english",
        "time_zone": "lst_ldt",
        "format": "json",
    }

    try:
        logger.log("Fetching water temperature for station %s", station_id)
        response = requests.get(base_url, params=params, timeout=10)
        logger.log("Water temperature response status code: ", response.status_code)
        response.raise_for_status()
        data = response.json()

        if "data" not in data or not data["data"]:
            logger.error("No water temperature data returned for station %s", station_id)
            return None

        return float(data["data"][0]["v"])

    except (requests.RequestException, KeyError, IndexError, ValueError) as e:
        logger.error("Failed to fetch water temp: %s", e)
        return None


def add_unit_of_measure(temp: float) -> str:
    """
    Format the water temperature value as a string with the Fahrenheit symbol.

    Args:
        temp (float): Temperature value in Fahrenheit.

    Returns:
        str: Formatted temperature string.
    """
    return f"{temp:.1f} °F"
