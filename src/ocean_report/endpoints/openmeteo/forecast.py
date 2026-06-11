"""Open-Meteo forecast endpoint."""

from __future__ import annotations

from ...models.openmeteo.forecast import (
    OpenMeteoForecastParams,
    OpenMeteoForecastResponse,
    OpenMeteoHourlyForecast,
)
from .base import OpenMeteoEndpoint


class OpenMeteoForecastEndpoint(OpenMeteoEndpoint):
    """Open-Meteo endpoint wrapper for forecast data retrieval."""

    PATH = "v1/forecast"

    def fetch(self, params: OpenMeteoForecastParams) -> OpenMeteoForecastResponse:
        """Retrieve and validate Open-Meteo forecast data."""

        payload = self.get_json(self.PATH, params=params.to_query_params())
        return self.parse_model(OpenMeteoForecastResponse, payload)

    get = fetch


__all__ = [
    "OpenMeteoForecastParams",
    "OpenMeteoForecastResponse",
    "OpenMeteoHourlyForecast",
    "OpenMeteoForecastEndpoint",
]
