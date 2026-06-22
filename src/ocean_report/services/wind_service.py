"""Wind forecast data fetching module for ocean report."""

import time
from ..api_client.exceptions import ApiClientError
from ..application.factory import ApplicationContext
from ..endpoints.openmeteo.forecast import OpenMeteoForecastEndpoint
from ..logger import logger
from ..models.openmeteo.forecast import (
    OpenMeteoForecastParams,
    OpenMeteoForecastResponse,
)


def fetch_wind_forecast(
    *,
    context: ApplicationContext,
    params: OpenMeteoForecastParams,
) -> OpenMeteoForecastResponse:
    """
    Fetch wind forecast data from the Open-Meteo API.

    This is a thin service layer function that only handles API calls.
    No defaults, no business logic, no error suppression.

    Args:
        context (ApplicationContext): The application context containing the API client.
        params (OpenMeteoForecastParams): Fully constructed Open-Meteo forecast query parameters.

    Returns:
        OpenMeteoForecastResponse: Wind forecast response with hourly data.

    Raises:
        ApiClientError: If the Open-Meteo API request fails.
    """
    endpoint = OpenMeteoForecastEndpoint(context.client)

    try:
        logger.debug(
            "    → Making Open-Meteo API request for wind forecast (lat: %.4f, lon: %.4f)",
            params.latitude,
            params.longitude,
        )
        api_start = time.time()
        response = endpoint.fetch(params)
        api_duration = time.time() - api_start

        logger.info(
            "    ✓ Open-Meteo Wind Forecast API responded in %.2f seconds. "
            "Found %d hourly records.",
            api_duration,
            len(response.hourly.time),
        )
        return response

    except ApiClientError as e:
        logger.error("Failed to fetch wind forecast from Open-Meteo API: %s", e)
        raise
