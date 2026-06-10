"""NOAA water temperature endpoint and typed models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .base import NoaaEndpoint


class NoaaWaterTempParams(BaseModel):
    """Query parameters for NOAA water temperature requests."""

    model_config = ConfigDict(extra="forbid")

    station: str = Field(min_length=7, max_length=7)
    product: Literal["water_temperature"] = "water_temperature"
    application: str = "ocean-report"
    date: str = "latest"
    units: Literal["english", "metric"] = "english"
    time_zone: Literal["lst_ldt", "gmt"] = "lst_ldt"
    format: Literal["json"] = "json"

    def to_query_params(self) -> dict[str, str]:
        """Serialize params to NOAA query string shape."""

        payload = self.model_dump(by_alias=True, exclude_none=True)
        return {key: str(value) for key, value in payload.items()}


class NoaaWaterTemperatureDatum(BaseModel):
    """One water temperature record returned by NOAA."""

    timestamp: str = Field(alias="t")
    temperature: float = Field(alias="v")


class NoaaWaterTemperatureResponse(BaseModel):
    """Typed NOAA water temperature response payload."""

    data: list[NoaaWaterTemperatureDatum] = Field(default_factory=list)


class WaterTemperatureEndpoint(NoaaEndpoint):
    """NOAA endpoint wrapper for water temperature retrieval."""

    PATH = "datagetter"

    def fetch(self, params: NoaaWaterTempParams) -> NoaaWaterTemperatureResponse:
        """Retrieve and validate water temperature data."""

        payload = self.get_json(self.PATH, params=params.to_query_params())
        return self.parse_model(NoaaWaterTemperatureResponse, payload)

    get = fetch
