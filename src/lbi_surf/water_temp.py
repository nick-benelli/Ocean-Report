import requests
from .constants import STATION_ID

TEMP_URL = (
    f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?"
    f"product=water_temperature&application=chatgpt-tide-app&station={STATION_ID}&"
    f"date=latest&units=english&time_zone=lst_ldt&format=json"
)


def fetch_water_temp(station_id: str = "8534720"):
    """
    Fetch water temperature data from NOAA API.
    Parameters:
    - station_id: NOAA Station ID
    Returns:
    - Water temperature in Fahrenheit
    """

    # response = requests.get(TEMP_URL)
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

    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()
    return float(data["data"][0]["v"])


def format_water_temp(temp: float) -> str:
    """Format the water temperature string."""
    return str(temp) + " °F"
