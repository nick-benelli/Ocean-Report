"""Endpoint layer exports."""

from .base import BaseEndpoint
from .ndbc import NdbcEndpoint, NdbcObservationsEndpoint
from .noaa import (
    NoaaEndpoint,
    NoaaStationsEndpoint,
    NoaaTidesEndpoint,
    WaterTemperatureEndpoint,
)
from .openmeteo import OpenMeteoEndpoint, OpenMeteoForecastEndpoint
from ..models.ndbc import (
    NdbcObservation,
    NdbcObservationsParams,
    NdbcObservationsResponse,
)
from ..models.noaa import (
    NoaaStation,
    NoaaStationsParams,
    NoaaStationsResponse,
    NoaaTideParams,
    NoaaTidePredictionRecord,
    NoaaTideResponse,
    NoaaWaterTempParams,
    NoaaWaterTemperatureDatum,
    NoaaWaterTemperatureParams,
    NoaaWaterTemperatureRecord,
    NoaaWaterTemperatureResponse,
)
from ..models.openmeteo import (
    OpenMeteoForecastParams,
    OpenMeteoForecastResponse,
    OpenMeteoHourlyForecast,
)

__all__ = [
    "BaseEndpoint",
    "NdbcEndpoint",
    "NdbcObservation",
    "NdbcObservationsEndpoint",
    "NdbcObservationsParams",
    "NdbcObservationsResponse",
    "NoaaEndpoint",
    "NoaaStation",
    "NoaaStationsEndpoint",
    "NoaaStationsParams",
    "NoaaStationsResponse",
    "NoaaTideParams",
    "NoaaTidePredictionRecord",
    "NoaaTideResponse",
    "NoaaTidesEndpoint",
    "NoaaWaterTempParams",
    "NoaaWaterTemperatureDatum",
    "NoaaWaterTemperatureParams",
    "NoaaWaterTemperatureRecord",
    "NoaaWaterTemperatureResponse",
    "OpenMeteoEndpoint",
    "OpenMeteoForecastEndpoint",
    "OpenMeteoForecastParams",
    "OpenMeteoForecastResponse",
    "OpenMeteoHourlyForecast",
    "WaterTemperatureEndpoint",
]
