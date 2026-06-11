"""Typed Open-Meteo forecast request and response schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ..common.base import ApiSchema


class OpenMeteoForecastParams(ApiSchema):
    """Query parameters for Open-Meteo forecast requests."""

    latitude: float = Field(gt=-90, lt=90)
    longitude: float = Field(gt=-180, lt=180)
    hourly: str = "wind_speed_10m,wind_direction_10m"
    wind_speed_unit: Literal["kmh", "mph", "ms", "kn"] = "kn"
    timezone: str = "UTC"
    format: Literal["json"] = "json"

    def to_query_params(self) -> dict[str, str]:
        """Serialize params to Open-Meteo query string shape."""

        payload = self.model_dump(by_alias=True, exclude_none=True)
        return {key: str(value) for key, value in payload.items()}


class OpenMeteoHourlyForecast(ApiSchema):
    """Subset of Open-Meteo hourly forecast payload."""

    time: list[str] = Field(default_factory=list)
    wind_speed_10m: list[float] = Field(default_factory=list)
    wind_direction_10m: list[float] = Field(default_factory=list)


class OpenMeteoForecastResponse(ApiSchema):
    """Top-level Open-Meteo forecast response body."""

    hourly: OpenMeteoHourlyForecast
