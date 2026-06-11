"""Typed NDBC observation request and response schemas."""

from __future__ import annotations

from pydantic import Field

from ..common.base import ApiSchema


class NdbcObservationsParams(ApiSchema):
    """Query parameters for NDBC observations requests."""

    station_id: str = Field(min_length=4, max_length=5)
    format: str = "json"

    def to_query_params(self) -> dict[str, str]:
        """Serialize params to NDBC query string shape."""

        payload = self.model_dump(by_alias=True, exclude_none=True)
        return {key: str(value) for key, value in payload.items()}


class NdbcObservation(ApiSchema):
    """One normalized NDBC observation record."""

    station_id: str = Field(alias="station")
    timestamp: str
    wind_speed_knots: float | None = Field(default=None, alias="wind_spd")
    water_temperature_c: float | None = Field(default=None, alias="water_temp")


class NdbcObservationsResponse(ApiSchema):
    """Top-level NDBC observations response body."""

    observations: list[NdbcObservation] = Field(default_factory=list)
