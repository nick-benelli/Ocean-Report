"""Tide data fetching module for ocean report."""

from datetime import datetime, time
from typing import Any, Dict, List

import requests

from .config import get_settings
from .logger import logger


def fetch_tide_data(
    station_id: str | None = None, date: str | None = None
) -> List[Dict[str, str]]:
    """
    Fetch tide prediction data from the NOAA API for a given station and date.

    Args:
        station_id (str): NOAA station ID. Defaults to STATION_ID from constants.
        date (str, optional): Date for predictions in YYYYMMDD format. Defaults to today.

    Returns:
        List[Dict[str, str]]: A list of tide predictions, each containing time
            ('t'), value ('v'), and type ('type').
    """
    if station_id is None:
        station_id = get_settings().noaa.station_id

    if date is None:
        date = datetime.now().strftime("%Y%m%d")

    params = {
        "product": "predictions",
        "application": "chatgpt-tide-app",
        "begin_date": date,
        "end_date": date,
        "datum": "MLLW",
        "station": station_id,
        "time_zone": "lst_ldt",
        "units": "english",
        "interval": "hilo",
        "format": "json",
    }

    try:
        logger.info(
            "Fetching tide data for station: %s on date: %s...", station_id, date
        )
        response = requests.get(
            "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter",
            params=params,
            timeout=10,
        )
        logger.info("\tTide data response status code: %s", response.status_code)
        response.raise_for_status()
        data = response.json()
        logger.info("...Tide data fetched successfully.")
        predictions = data.get("predictions", [])

        if not predictions:
            logger.error("No predictions found in tide data response.")
            return []

        return predictions

    except requests.RequestException as e:
        logger.error("Failed to fetch tide data: %s", e)
        return []


def filter_daytime_tides(
    tides: List[Dict[str, Any]], start_hour: float = 6, end_hour: float = 20.5
) -> List[Dict[str, str]]:
    """
    Filters tide events to only include those occurring between start_hour and end_hour.

    Args:
        tides (List[Dict[str, Any]]): List of tide predictions with keys {"t": timestamp, ...}.
        start_hour (float): Start of the daytime window in 24-hour format (default: 7).
        end_hour (float): End of the daytime window in 24-hour format (default: 19).

    Returns:
        List[Dict[str, str]]: Filtered list of tide predictions within daytime hours.
    """

    def hour_to_time(hour_float: float) -> time:
        """Convert a float hour (e.g. 19.5) to a datetime.time object."""
        h = int(hour_float)
        m = int((hour_float - h) * 60)
        return time(h, m)

    start = hour_to_time(start_hour)
    end = hour_to_time(end_hour)

    filtered = []
    for tide in tides:
        tide_time = datetime.strptime(tide["t"], "%Y-%m-%d %H:%M").time()
        if start <= tide_time <= end:
            filtered.append(tide)

    return filtered
