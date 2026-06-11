"""Wind data fetching service for ocean report."""

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
        response = endpoint.fetch(params)
        logger.info(
            "Wind forecast data fetched successfully for lat: %.4f, lon: %.4f. Found %d hourly records.",
            params.latitude,
            params.longitude,
            len(response.hourly.time),
        )
        return response

    except ApiClientError as e:
        logger.error("Failed to fetch wind forecast from Open-Meteo API: %s", e)
        raise
