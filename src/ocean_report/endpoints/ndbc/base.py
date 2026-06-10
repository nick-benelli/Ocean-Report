"""NDBC endpoint base abstractions."""

from __future__ import annotations

from ..base import BaseEndpoint


class NdbcEndpoint(BaseEndpoint):
    """Base endpoint for NOAA NDBC APIs."""

    BASE_URL = "https://www.ndbc.noaa.gov"
