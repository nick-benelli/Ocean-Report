import pytest
from pydantic import ValidationError

from ocean_report.models.noaa.water_temperature import (
    NoaaWaterTemperatureParams,
    NoaaWaterTemperatureResponse,
)


def test_noaa_water_temperature_params_to_query_params() -> None:
    params = NoaaWaterTemperatureParams(station="8534720")

    assert params.to_query_params() == {
        "station": "8534720",
        "product": "water_temperature",
        "application": "ocean-report",
        "date": "latest",
        "units": "english",
        "time_zone": "lst_ldt",
        "format": "json",
    }


def test_noaa_water_temperature_params_reject_invalid_station() -> None:
    with pytest.raises(ValidationError):
        NoaaWaterTemperatureParams(station="123")


def test_noaa_water_temperature_response_alias_mapping_and_dump() -> None:
    payload = {
        "data": [
            {"t": "2025-07-04 15:00", "v": "73.2"},
        ]
    }

    response = NoaaWaterTemperatureResponse.model_validate(payload)

    assert response.data[0].timestamp == "2025-07-04 15:00"
    assert response.data[0].temperature == 73.2

    dumped = response.model_dump(by_alias=True, exclude_none=True)
    assert dumped == {
        "data": [{"t": "2025-07-04 15:00", "v": 73.2}],
    }
    assert isinstance(response.model_dump_json(), str)
