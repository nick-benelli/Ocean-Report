"""NOAA tides endpoint scaffolding."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .base import NoaaEndpoint


class NoaaTideParams(BaseModel):
    """Typed query parameters for NOAA tide predictions."""

    model_config = ConfigDict(extra="forbid")

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


class NoaaTidesEndpoint(NoaaEndpoint):
    """Scaffolded NOAA tides endpoint."""

    PATH = "datagetter"

    def get_raw(self, params: NoaaTideParams) -> object:
        """Return raw JSON payload for tide prediction requests."""

        return self.get_json(self.PATH, params=params)
