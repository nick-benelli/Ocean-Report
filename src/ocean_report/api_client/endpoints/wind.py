"""Wind data fetching module for ocean report."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

import requests

from ...api_client import get_api_client
from ...api_client.client import ApiClient
from ...config import get_settings
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


def fetch_wind_payload_with_client(
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
            response.status_code if response else "No Response",
        )
        if response is None:
            raise RuntimeError(
                "Failed to fetch wind data from Open-Meteo after SSL retries"
            )
        response.raise_for_status()
        logger.info("...Open-Meteo wind data fetched successfully.")
        return response.json()
    except requests.RequestException as exc:
        logger.error("Error fetching wind data: %s", exc)
        raise RuntimeError(f"Error fetching wind data: {exc}") from exc
