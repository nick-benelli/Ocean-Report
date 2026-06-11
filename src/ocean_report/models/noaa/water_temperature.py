"""Typed NOAA water temperature request and response schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ..common.base import ApiSchema


class NoaaWaterTemperatureParams(ApiSchema):
    """Query parameters for NOAA water temperature requests."""

    station: str = Field(min_length=7, max_length=7)
    product: Literal["water_temperature"] = "water_temperature"
    application: str = "ocean-report"
    date: str = "latest"
    units: Literal["english", "metric"] = "english"
    time_zone: Literal["lst_ldt", "gmt"] = "lst_ldt"
    format: Literal["json"] = "json"

    def to_query_params(self) -> dict[str, str]:
        """Serialize this request into NOAA query params."""

        payload = self.model_dump(by_alias=True, exclude_none=True)
        return {key: str(value) for key, value in payload.items()}


class NoaaWaterTemperatureRecord(ApiSchema):
    """One NOAA water temperature data point."""

    timestamp: str = Field(alias="t")
    temperature: float = Field(alias="v")


class NoaaWaterTemperatureResponse(ApiSchema):
    """Top-level NOAA water temperature response body."""

    data: list[NoaaWaterTemperatureRecord] = Field(default_factory=list)


# Backward-compatible aliases for earlier naming.
NoaaWaterTempParams = NoaaWaterTemperatureParams
NoaaWaterTemperatureDatum = NoaaWaterTemperatureRecord
