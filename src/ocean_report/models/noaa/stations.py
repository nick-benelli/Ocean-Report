"""Typed NOAA station schemas."""

from __future__ import annotations

from pydantic import Field

from ..common.base import ApiSchema


class NoaaStationsParams(ApiSchema):
    """Query parameters for NOAA stations requests."""

    format: str = "json"

    def to_query_params(self) -> dict[str, str]:
        """Serialize params to NOAA query string shape."""

        payload = self.model_dump(by_alias=True, exclude_none=True)
        return {key: str(value) for key, value in payload.items()}


class NoaaStation(ApiSchema):
    """NOAA station metadata."""

    station_id: str = Field(alias="id")
    name: str
    latitude: float | None = None
    longitude: float | None = None


class NoaaStationsResponse(ApiSchema):
    """Top-level NOAA stations response body."""

    stations: list[NoaaStation] = Field(default_factory=list)


# Backward-compatible alias for earlier naming.
NoaaStations = NoaaStationsParams
