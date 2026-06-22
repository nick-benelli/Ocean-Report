"""NOAA stations endpoint."""

from __future__ import annotations

from ...models.noaa.stations import (
    NoaaStation,
    NoaaStationsParams,
    NoaaStationsResponse,
)
from .base import NoaaEndpoint


class NoaaStationsEndpoint(NoaaEndpoint):
    """NOAA endpoint wrapper for station metadata retrieval."""

    PATH = "stations"

    def fetch(self, params: NoaaStationsParams | None = None) -> NoaaStationsResponse:
        """Retrieve and validate station metadata."""

        query_params = params.to_query_params() if params else None
        payload = self.get_json(self.PATH, params=query_params)
        return self.parse_model(NoaaStationsResponse, payload)

    get = fetch


__all__ = [
    "NoaaStation",
    "NoaaStationsParams",
    "NoaaStationsResponse",
    "NoaaStationsEndpoint",
]
