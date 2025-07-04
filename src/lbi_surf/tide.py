import requests
import logging
from datetime import datetime, time
from typing import List, Dict, Any
from .constants import STATION_ID

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def fetch_tide_data(
    station_id: str = STATION_ID, date: str = None
) -> List[Dict[str, str]]:
    """
    Fetch tide prediction data from the NOAA API for a given station and date.

    Args:
        station_id (str): NOAA station ID. Defaults to STATION_ID from constants.
        date (str, optional): Date for predictions in YYYYMMDD format. Defaults to today.

    Returns:
        List[Dict[str, str]]: A list of tide predictions, each containing time ('t'), value ('v'), and type ('type').
    """
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
        response = requests.get(
            "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter", params=params
        )
        response.raise_for_status()
        data = response.json()
        predictions = data.get("predictions", [])

        if not predictions:
            logger.error("No predictions found in tide data response.")
            return []

        return predictions

    except requests.RequestException as e:
        logger.error(f"Failed to fetch tide data: {e}")
        return []


def filter_daytime_tides(
    tides: List[Dict[str, Any]], start_hour: float = 7, end_hour: float = 19
) -> List[Dict[str, str]]:
    """
    Filters tide events to only include those occurring between start_hour and end_hour.

    Args:
        tides (List[Dict[str, Any]]): List of tide predictions.
        start_hour (float): Start of the daytime window in 24-hour format (default: 7).
        end_hour (float): End of the daytime window in 24-hour format (default: 19).

    Returns:
        List[Dict[str, str]]: Filtered list of tide predictions within daytime hours.
    """
    filtered = []
    for tide in tides:
        tide_time = datetime.strptime(tide["t"], "%Y-%m-%d %H:%M").time()
        if time(int(start_hour)) <= tide_time <= time(int(end_hour)):
            filtered.append(tide)

    return filtered
