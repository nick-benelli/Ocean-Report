
from dataclasses import dataclass
from datetime import datetime

import requests
from typing import Dict, List

from ...api_client import ApiClientError, get_api_client
from ...api_client.client import ApiClient
from ...config import get_settings
from ...logger import logger


@dataclass(frozen=True, slots=True)
class NoaaTideParams:
    """Typed query params for NOAA tide predictions."""

    begin_date: str
    end_date: str
    station: str
    product: str = "predictions"
    application: str = "chatgpt-tide-app"
    datum: str = "MLLW"
    time_zone: str = "lst_ldt"
    units: str = "english"
    interval: str = "hilo"
    format: str = "json"

    def to_query_params(self) -> dict[str, str]:
        return {
            "product": self.product,
            "application": self.application,
            "begin_date": self.begin_date,
            "end_date": self.end_date,
            "datum": self.datum,
            "station": self.station,
            "time_zone": self.time_zone,
            "units": self.units,
            "interval": self.interval,
            "format": self.format,
        }


def get_noaa_tide_data(
    station_id: str | None = None,
    date: str | None = None,
    api_client: ApiClient | None = None,
) -> List[Dict[str, str]]:
    """
    Fetch tide prediction data from the NOAA API for a given station and date.

    Args:
        station_id (str): NOAA station ID. Defaults to STATION_ID from constants.
        date (str, optional): Date for predictions in YYYYMMDD format. Defaults to today.
        api_client (ApiClient, optional): Shared API client to use for the request.
            If omitted, uses get_api_client() with configured defaults.

    Returns:
        List[Dict[str, str]]: A list of tide predictions, each containing time
            ('t'), value ('v'), and type ('type').
    """
    if station_id is None:
        station_id = get_settings().noaa.station_id

    if date is None:
        date = datetime.now().strftime("%Y%m%d")

    resolved_client = api_client or get_api_client()

    params = NoaaTideParams(
        begin_date=date,
        end_date=date,
        station=station_id,
    ).to_query_params()

    try:
        logger.info(
            "Fetching tide data for station: %s on date: %s...", station_id, date
        )
        response = resolved_client.get(
            "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter",
            params=params,
        )
        logger.info("\tTide data response status code: %s", response.status_code)
        data = response.json()
        logger.info("...Tide data fetched successfully.")
        predictions = data.get("predictions", [])

        if not predictions:
            logger.error("No predictions found in tide data response.")
            return []

        return predictions

    except (ApiClientError, requests.RequestException) as e:
        logger.error("Failed to fetch tide data: %s", e)
        return []