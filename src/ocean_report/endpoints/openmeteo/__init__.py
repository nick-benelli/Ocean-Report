"""Open-Meteo endpoint exports."""

from .base import OpenMeteoEndpoint
from .forecast import OpenMeteoForecastEndpoint

__all__ = ["OpenMeteoEndpoint", "OpenMeteoForecastEndpoint"]
