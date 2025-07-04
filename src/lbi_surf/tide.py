import requests
from datetime import datetime, time
from .constants import STATION_ID

# NOAA API endpoints
TIDE_URL = (
    f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?"
    f"product=predictions&application=chatgpt-tide-app&begin_date=latest&"
    f"end_date=latest&datum=MLLW&station={STATION_ID}&time_zone=lst_ldt&"
    f"units=english&interval=hilo&format=json"
)


def fetch_tide_data(station_id: str = "8534720", date: str = None):
    """
    Fetch tide data from NOAA API.
    Parameters:
    - station_id: NOAA Station ID
    - date: Date for tide predictions (YYYYMMDD)
    Returns:
    - List of tide predictions
    """
    if date is None:
        date = datetime.now().strftime("%Y%m%d")

    # tide_url = (
    #     f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?"
    #     f"product=predictions&application=chatgpt-tide-app&begin_date={today}&"
    #     f"end_date={today}&datum=MLLW&station={STATION_ID}&time_zone=lst_ldt&"
    #     f"units=english&interval=hilo&format=json"
    # )
    base_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"

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

    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()

    return data["predictions"]


def filter_daytime_tides(tides, start_hour: float = 7, end_hour: float = 19):
    """Return only tides that occur between start_hour and end_hour (24-hour format)."""
    result = []
    for tide in tides:
        tide_time = datetime.strptime(tide["t"], "%Y-%m-%d %H:%M")
        if time(start_hour) <= tide_time.time() <= time(end_hour):
            result.append(tide)
    return result
