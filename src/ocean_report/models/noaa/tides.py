"""Typed NOAA tide request and response schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ..common.base import ApiSchema


class NoaaTideParams(ApiSchema):
    """Query parameters for NOAA tide predictions."""

    begin_date: str = Field(min_length=8, max_length=8)
    end_date: str = Field(min_length=8, max_length=8)
    station: str = Field(min_length=7, max_length=7)
    product: Literal["predictions"] = "predictions"
    application: str = "ocean-report"
    datum: str = "MLLW"
    time_zone: Literal["lst_ldt", "gmt"] = "lst_ldt"
    units: Literal["english", "metric"] = "english"
    interval: Literal["hilo", "h"] = "hilo"
    format: Literal["json"] = "json"

    def to_query_params(self) -> dict[str, str]:
        """Serialize this request into NOAA query params."""
        payload = self.model_dump(by_alias=True, exclude_none=True)
        return {key: str(value) for key, value in payload.items()}


class NoaaTidePredictionRecord(ApiSchema):
    """One NOAA tide prediction data point."""

    timestamp: str = Field(alias="t")
    height_feet: float = Field(alias="v")
    event_type: str = Field(alias="type")


class NoaaTideResponse(ApiSchema):
    """Top-level NOAA tide response body."""

    predictions: list[NoaaTidePredictionRecord] = Field(default_factory=list)
