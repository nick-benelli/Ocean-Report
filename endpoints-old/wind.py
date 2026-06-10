"""Wind data fetching module for ocean report."""

from dataclasses import dataclass
from typing import Any, Dict

import requests

from ...api_client.client import ApiClient, ApiClientError
from ...logger import logger




@dataclass(frozen=True, slots=True)
class OpenMeteoWindParams:
    """Typed query params for the Open-Meteo hourly wind endpoint."""

    latitude: float
    longitude: float
    hourly: str = "wind_speed_10m,wind_direction_10m"
    timezone: str = "America/New_York"

    def to_query_params(self) -> dict[str, float | str]:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "hourly": self.hourly,
            "timezone": self.timezone,
        }


def get_wind_from_open_meteo(
    api_client: ApiClient,
    latitude: float,
    longitude: float,
) -> Dict[str, Any]:
    """Fetch hourly wind payload from Open-Meteo using the provided ApiClient."""

    params = OpenMeteoWindParams(
        latitude=latitude,
        longitude=longitude,
    ).to_query_params()

    try:
        logger.info(
            "Fetching wind data from Open-Meteo for lat: %s, lon: %s...",
            latitude,
            longitude,
        )
        response = api_client.get(
            "https://api.open-meteo.com/v1/forecast", params=params
        )
        logger.info(
            "\tWind data response status code: %s",
            response.status_code,
        )
        logger.info("...Open-Meteo wind data fetched successfully.")
        return response.json()
    except (ApiClientError, requests.RequestException) as exc:
        logger.error("Error fetching wind data: %s", exc)
        raise RuntimeError(f"Error fetching wind data: {exc}") from exc
