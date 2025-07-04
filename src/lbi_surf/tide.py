import requests
import logging
from datetime import datetime, time
from .constants import STATION_ID
from typing import List, Dict, Any

# NOAA API endpoints
TIDE_URL_EXAMPLE = (
    f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?"
    f"product=predictions&application=chatgpt-tide-app&begin_date=latest&"
    f"end_date=latest&datum=MLLW&station={STATION_ID}&time_zone=lst_ldt&"
    f"units=english&interval=hilo&format=json"
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def fetch_tide_data(
    station_id: str = "8534720", date: str = None
) -> List[Dict[str, str]]:
    """
    Fetch tide data from NOAA API.
    Parameters:
    - station_id: NOAA Station ID
    - date: Date for tide predictions (YYYYMMDD)
    Returns:
    - List of tide predictions
    """
    # Set default date to today
    if date is None:
        date = datetime.now().strftime("%Y%m%d")

    # Construct the API URL
    base_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"

    # Set up query parameters
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

    # Make the API request
    response = requests.get(base_url, params=params)
    # Raise an error for HTTP errors
    response.raise_for_status()
    # Check if the response contains data
    data = response.json()
    if "predictions" not in data:
        logger.error("No predictions found in tide data.")
        return []

    return data["predictions"]


def filter_daytime_tides(
    tides: List[Dict[str, Any]], start_hour: float = 7, end_hour: float = 19
) -> List[Dict[str, str]]:
    """
    Return only tides that occur between start_hour and end_hour (24-hour format).
    Parameters:
    - tides: List of tide predictions
    - start_hour: Start hour (24-hour format)
    - end_hour: End hour (24-hour format)
    Returns:
    - List of daytime tide predictions
    """
    result = []
    for tide in tides:
        tide_time = datetime.strptime(tide["t"], "%Y-%m-%d %H:%M")
        if time(start_hour) <= tide_time.time() <= time(end_hour):
            result.append(tide)
    return result
