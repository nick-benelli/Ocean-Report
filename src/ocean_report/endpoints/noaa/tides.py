"""NOAA tides endpoint."""

from __future__ import annotations

from ...models.noaa.tides import (
    NoaaTideParams,
    NoaaTidePredictionRecord,
    NoaaTideResponse,
)
from .base import NoaaEndpoint


class NoaaTidesEndpoint(NoaaEndpoint):
    """NOAA endpoint wrapper for tide prediction retrieval."""

    PATH = "datagetter"

    def fetch(self, params: NoaaTideParams) -> NoaaTideResponse:
        """Retrieve and validate tide prediction data."""

        payload = self.get_json(self.PATH, params=params.to_query_params())
        return self.parse_model(NoaaTideResponse, payload)

    get = fetch


__all__ = [
    "NoaaTideParams",
    "NoaaTidePredictionRecord",
    "NoaaTideResponse",
    "NoaaTidesEndpoint",
]
