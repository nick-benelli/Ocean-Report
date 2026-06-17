"""
Email formatting module for ocean report.
"""

from typing import TypedDict


class WindForecastEntry(TypedDict):
    """Type definition for a wind forecast entry."""

    time: str
    speed_kmh: float
    direction_deg: float
    speed_mph: float
    direction: str
    wind_type: str
