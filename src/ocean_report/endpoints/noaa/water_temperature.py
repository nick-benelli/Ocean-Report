"""NOAA water temperature endpoint."""

from __future__ import annotations

from ...models.noaa.water_temperature import (
    NoaaWaterTempParams,
    NoaaWaterTemperatureDatum,
    NoaaWaterTemperatureParams,
    NoaaWaterTemperatureRecord,
    NoaaWaterTemperatureResponse,
)
from .base import NoaaEndpoint


class WaterTemperatureEndpoint(NoaaEndpoint):
    """NOAA endpoint wrapper for water temperature retrieval."""

    PATH = "datagetter"

    def fetch(self, params: NoaaWaterTempParams) -> NoaaWaterTemperatureResponse:
        """Retrieve and validate water temperature data."""

        payload = self.get_json(self.PATH, params=params.to_query_params())
        return self.parse_model(NoaaWaterTemperatureResponse, payload)

    get = fetch


__all__ = [
    "NoaaWaterTempParams",
    "NoaaWaterTemperatureDatum",
    "NoaaWaterTemperatureParams",
    "NoaaWaterTemperatureRecord",
    "NoaaWaterTemperatureResponse",
    "WaterTemperatureEndpoint",
]
