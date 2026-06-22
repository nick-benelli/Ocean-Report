"""NOAA endpoint base abstractions."""

from __future__ import annotations

from ..base import BaseEndpoint


class NoaaEndpoint(BaseEndpoint):
    """Base endpoint for NOAA Tides & Currents APIs."""

    BASE_URL = "https://api.tidesandcurrents.noaa.gov/api/prod"
