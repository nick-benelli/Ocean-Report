"""NDBC observations endpoint."""

from __future__ import annotations

from ...models.ndbc.observations import (
    NdbcObservation,
    NdbcObservationsParams,
    NdbcObservationsResponse,
)
from .base import NdbcEndpoint


class NdbcObservationsEndpoint(NdbcEndpoint):
    """NDBC endpoint wrapper for observation data retrieval."""

    PATH = "data/realtime2"

    def fetch(self, params: NdbcObservationsParams) -> NdbcObservationsResponse:
        """Retrieve and validate NDBC observation data."""

        payload = self.get_json(self.PATH, params=params.to_query_params())
        return self.parse_model(NdbcObservationsResponse, payload)

    get = fetch


__all__ = [
    "NdbcObservation",
    "NdbcObservationsParams",
    "NdbcObservationsResponse",
    "NdbcObservationsEndpoint",
]
