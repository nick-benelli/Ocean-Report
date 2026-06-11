"""Tide data fetching module for ocean report."""

from datetime import datetime, time
from typing import List

from ..api_client.exceptions import ApiClientError
from ..application.factory import ApplicationContext
from ..endpoints.noaa.tides import NoaaTidesEndpoint
from ..logger import logger
from ..models.noaa.tides import NoaaTideParams, NoaaTidePredictionRecord


def fetch_tide_data(
    *,
    context: ApplicationContext,
    params: NoaaTideParams,
) -> List[NoaaTidePredictionRecord]:
    """
    Fetch tide prediction data from the NOAA API.

    This is a thin service layer function that only handles API calls.
    No defaults, no business logic, no error suppression.

    Args:
        context (ApplicationContext): The application context containing the API client.
        params (NoaaTideParams): Fully constructed NOAA tide query parameters.

    Returns:
        List[NoaaTidePredictionRecord]: A list of validated tide predictions with
            timestamp, height_feet, and event_type attributes.

    Raises:
        ApiClientError: If the NOAA API request fails.
    """
    endpoint = NoaaTidesEndpoint(context.client)

    try:
        response = endpoint.fetch(params)
        logger.info(
            "Tide data fetched successfully for station %s. Found %d predictions.",
            params.station,
            len(response.predictions),
        )
        return response.predictions

    except ApiClientError as e:
        logger.error("Failed to fetch tide data from NOAA API: %s", e)
        raise


def filter_daytime_tides(
    tides: List[NoaaTidePredictionRecord],
    start_time: time = time(6, 0),
    end_time: time = time(20, 30),
) -> List[NoaaTidePredictionRecord]:
    """
    Filter tide events to only include those occurring during daytime hours.

    This is a pure business logic function with no API dependencies.

    Args:
        tides (List[NoaaTidePredictionRecord]): List of tide predictions.
        start_time (time): Start of the daytime window (default: 6:00 AM).
        end_time (time): End of the daytime window (default: 8:30 PM).

    Returns:
        List[NoaaTidePredictionRecord]: Filtered list of tide predictions within daytime hours.
    """
    filtered = []
    for tide in tides:
        # Parse timestamp once per tide
        tide_time = datetime.strptime(tide.timestamp, "%Y-%m-%d %H:%M").time()
        if start_time <= tide_time <= end_time:
            filtered.append(tide)

    logger.debug(
        "Filtered %d tides to %d daytime tides (between %s and %s)",
        len(tides),
        len(filtered),
        start_time,
        end_time,
    )

    return filtered
