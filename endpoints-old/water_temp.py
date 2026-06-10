

from dataclasses import dataclass
from typing import Optional
import requests
from ..client import ApiClient, ApiClientError
from ...logger import logger



@dataclass(frozen=True, slots=True)
class NoaaWaterTempParams:
    """Typed query params for NOAA water temperature data."""

    station: str
    product: str = "water_temperature"
    application: str = "chatgpt-tide-app"
    date: str = "latest"
    units: str = "english"
    time_zone: str = "lst_ldt"
    format: str = "json"

    def to_query_params(self) -> dict[str, str]:
        return {
            "product": self.product,
            "application": self.application,
            "station": self.station,
            "date": self.date,
            "units": self.units,
            "time_zone": self.time_zone,
            "format": self.format,
        }

def get_noaa_water_temp(
        client : ApiClient, station_id: str) -> Optional[float]:
    """
    Fetch the latest water temperature in Fahrenheit from NOAA API.

    Args:
        client (ApiClient): The API client to use for making requests.
        station_id (str): NOAA Station ID.

    Returns:
        Optional[float]: Latest recorded water temperature in Fahrenheit, or None if fetch fails.
    """
    base_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"

    params = NoaaWaterTempParams(station=station_id).to_query_params()


    try:
        logger.info("Fetching water temperature for station: %s...", station_id)
        response = client.get(base_url, params=params)
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