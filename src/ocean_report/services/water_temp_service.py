"""Water temperature data fetching module for ocean report."""

import time

from pydantic import ValidationError

from ..api_client.exceptions import ApiClientError
from ..application.factory import ApplicationContext
from ..endpoints.noaa.water_temperature import WaterTemperatureEndpoint
from ..logger import logger
from ..models.noaa.water_temperature import (
    NoaaWaterTemperatureRecord,
    NoaaWaterTempParams,
)


def fetch_water_temp(
    *,
    context: ApplicationContext,
    params: NoaaWaterTempParams,
) -> NoaaWaterTemperatureRecord | None:
    """
    Fetch water temperature data from the NOAA API.

    This is a thin service layer function that only handles API calls.
    Returns None if the API is unavailable or returns unexpected data.

    Args:
        context (ApplicationContext): The application context containing the API client.
        params (NoaaWaterTempParams): Fully constructed NOAA water temperature query parameters.

    Returns:
        Optional[NoaaWaterTemperatureRecord]: The latest water temperature record,
            or None if no data or API is unavailable.
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
            logger.warning("No water temperature data returned for station %s", params.station)
            return None

        return response.data[0]  # Return the latest record

    except ValidationError as e:
        # NOAA API is returning unexpected data format
        logger.warning(
            "NOAA Water Temperature API returned unexpected data format (API may be down): %s. "
            "Continuing report without water temperature.",
            str(e).split("\n")[0],  # First line of validation error
        )
        return None

    except ApiClientError as e:
        logger.error(
            "Failed to connect to NOAA Water Temperature API: %s. Continuing report without water temperature.",
            e,
        )
        return None


def add_unit_of_measure(temp: float) -> str:
    """
    Format the water temperature value as a string with the Fahrenheit symbol.

    Args:
        temp (float): Temperature value in Fahrenheit.

    Returns:
        str: Formatted temperature string.
    """
    return f"{temp:.1f} °F"
