"""Data models for workflow orchestration."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class FetchParams:
    """Parameters for fetching report data."""

    station_id: str
    date_str: str
    latitude: float
    longitude: float
    beach_facing_deg: float
    forecast_times: set[str]


@dataclass
class RawReportData:
    """Raw data fetched from APIs before formatting."""

    tides: list
    tide_timestamp: datetime
    water_temp: float | None
    water_temp_timestamp: datetime
    water_temp_data_time: str | None
    wind_forecast: list
    wind_timestamp: datetime | None
