"""Water temperature data fetching module for ocean report."""

import time
from typing import Optional

from ..api_client.exceptions import ApiClientError
from ..application.factory import ApplicationContext
from ..endpoints.noaa.water_temperature import WaterTemperatureEndpoint
from ..logger import logger
from ..models.noaa.water_temperature import (
    NoaaWaterTempParams,
    NoaaWaterTemperatureRecord,
)


def fetch_water_temp(
    *,
    context: ApplicationContext,
    params: NoaaWaterTempParams,
) -> Optional[NoaaWaterTemperatureRecord]:
    """
    Fetch water temperature data from the NOAA API.

    This is a thin service layer function that only handles API calls.
    No defaults, no business logic, no error suppression.

    Args:
        context (ApplicationContext): The application context containing the API client.
        params (NoaaWaterTempParams): Fully constructed NOAA water temperature query parameters.

    Returns:
        Optional[NoaaWaterTemperatureRecord]: The latest water temperature record, or None if no data.

    Raises:
        ApiClientError: If the NOAA API request fails.
    """
    endpoint = WaterTemperatureEndpoint(context.client)

    try:
        logger.debug(
            "    → Making NOAA API request for water temperature (station: %s)",
            params.station,
        )
        api_start = time.time()
        response = endpoint.fetch(params)
        api_duration = time.time() - api_start

        logger.info(
            "    ✓ NOAA Water Temperature API responded in %.2f seconds. Found %d records.",
            api_duration,
            len(response.data),
        )

        if not response.data:
            logger.warning(
                "No water temperature data returned for station %s", params.station
            )
            return None

        return response.data[0]  # Return the latest record

    except ApiClientError as e:
        logger.error("Failed to fetch water temperature from NOAA API: %s", e)
        raise


def add_unit_of_measure(temp: float) -> str:
    """
    Format the water temperature value as a string with the Fahrenheit symbol.

    Args:
        temp (float): Temperature value in Fahrenheit.

    Returns:
        str: Formatted temperature string.
    """
    return f"{temp:.1f} °F"
