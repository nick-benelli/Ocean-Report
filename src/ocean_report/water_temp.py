"""Water temperature data fetching module for ocean report."""

from typing import Optional

import requests

from .api_client import ApiClientError, get_api_client
from .config import get_settings
from .logger import logger


def fetch_water_temp(station_id: str | None = None) -> Optional[float]:
    """
    Fetch the latest water temperature in Fahrenheit from NOAA API.

    Args:
        station_id (str): NOAA Station ID. Defaults to STATION_ID.

    Returns:
        Optional[float]: Latest recorded water temperature in Fahrenheit, or None if fetch fails.
    """
    if station_id is None:
        station_id = get_settings().noaa.station_id

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
        logger.info("Fetching water temperature for station: %s...", station_id)
        response = get_api_client().get(base_url, params=params)
        logger.info(
            "\tWater temperature response status code: %s", response.status_code
        )
        data = response.json()

        if "data" not in data or not data["data"]:
            logger.error(
                "\tNo water temperature data returned for station: %s", station_id
            )
            return None

        logger.info("...Water temperature fetched successfully.")
        return float(data["data"][0]["v"])

    except (ApiClientError, requests.RequestException, KeyError, IndexError, ValueError) as e:
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
