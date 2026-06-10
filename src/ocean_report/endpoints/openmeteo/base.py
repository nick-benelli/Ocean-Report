"""Open-Meteo endpoint base abstractions."""

from __future__ import annotations

from ..base import BaseEndpoint


class OpenMeteoEndpoint(BaseEndpoint):
    """Base endpoint for Open-Meteo APIs."""

    BASE_URL = "https://api.open-meteo.com"
