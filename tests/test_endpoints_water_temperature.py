from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from ocean_report.models.noaa.water_temperature import (
    NoaaWaterTemperatureParams,
    NoaaWaterTemperatureResponse,
)
from ocean_report.endpoints.noaa.water_temperature import (
    WaterTemperatureEndpoint,
)


def test_water_temperature_endpoint_uses_injected_client() -> None:
    mock_client = Mock()
    mock_client.get_json.return_value = {
        "data": [
            {"t": "2026-06-10 12:00", "v": "74.2"},
            {"t": "2026-06-10 13:00", "v": "74.6"},
        ]
    }

    endpoint = WaterTemperatureEndpoint(mock_client)
    params = NoaaWaterTemperatureParams(station="8534720")

    response = endpoint.get(params)

    assert isinstance(response, NoaaWaterTemperatureResponse)
    assert response.data[0].temperature == 74.2
    assert response.data[0].timestamp == "2026-06-10 12:00"
    mock_client.get_json.assert_called_once_with(
        "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter",
        params={
            "station": "8534720",
            "product": "water_temperature",
            "application": "ocean-report",
            "date": "latest",
            "units": "english",
            "time_zone": "lst_ldt",
            "format": "json",
        },
        headers=None,
    )


def test_noaa_water_temp_params_station_validation() -> None:
    with pytest.raises(ValidationError):
        NoaaWaterTemperatureParams(station="123")
