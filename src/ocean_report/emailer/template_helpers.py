"""Helper functions to prepare data for email templates.

These functions format data for use with Jinja2 templates.
Unlike email_formatter.py which includes section headers and emoji,
these return just the formatted values that templates can compose.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from ..models.noaa.tides import NoaaTidePredictionRecord
from ..models.openmeteo.wind import WindForecastEntry


def format_water_temp_value(water_temperature: Optional[float]) -> Optional[str]:
    """
    Format water temperature value for template.

    Args:
        water_temperature: Water temperature in Fahrenheit, or None if unavailable.

    Returns:
        Formatted temperature string (e.g., "64.4 °F") or None if unavailable.
    """
    unavailable_text = "Unavailable ⚠️"

    try:
        if water_temperature is None or not isinstance(water_temperature, (int, float)):
            return unavailable_text

        # Handle NaN or infinite values
        if abs(water_temperature) == float("inf"):
            return unavailable_text

        return f"{water_temperature:.1f} °F"

    except (TypeError, ValueError):
        return unavailable_text


def format_tide_info(tide_events: list[NoaaTidePredictionRecord]) -> Optional[str]:
    """
    Format tide events as multi-line string for template.

    Args:
        tide_events: List of NoaaTidePredictionRecord objects

    Returns:
        Formatted tide information (without section header) or None if empty.
        Example: "⬇️ Low Tide at 8:23 AM — 0.3 ft\\n⬆️ High Tide at 2:46 PM — 4.1 ft"
    """
    unavailable_text = "Tide data unavailable ⚠️"

    if not tide_events:
        return unavailable_text

    formatted = []
    for tide in tide_events:
        dt = datetime.strptime(tide.timestamp, "%Y-%m-%d %H:%M")
        time_str = dt.strftime("%-I:%M %p")
        tide_type = "⬆️ High Tide" if tide.event_type == "H" else "⬇️ Low Tide"
        height = float(tide.height_feet)
        formatted.append(f"• {tide_type} at {time_str} — {height:.1f} ft")

    return "\n".join(formatted)


def format_wind_info(wind_data: list[WindForecastEntry]) -> Optional[str]:
    """
    Format wind forecast as multi-line string for template.

    Args:
        wind_data: List of wind forecast entries with time, speed, direction

    Returns:
        Formatted wind forecast (without section header) or None if empty.
        Example: "•  8 AM:  4.8 mph ESE (108.0°) → Cross/Onshore\\n..."
    """

    unavailable_text = "Wind data unavailable ⚠️"

    if not wind_data:
        return unavailable_text

    lines = []
    for entry in wind_data:
        try:
            time_str = entry["time"].rjust(5)
            speed_str = f"{entry['speed_mph']:.1f}".rjust(4)
            direction = entry["direction"].ljust(3)
            deg = f"({entry['direction_deg']:>5.1f}°)"
            wind_type = entry["wind_type"]

            line = f"• {time_str}: {speed_str} mph {direction} {deg} → {wind_type}"
            lines.append(line)
        except (KeyError, TypeError, ValueError):
            continue

    return "\n".join(lines) if lines else unavailable_text


def format_retrieval_timestamp(retrieval_time: Optional[datetime]) -> str:
    """
    Format data retrieval timestamp for template.

    Args:
        retrieval_time: DateTime of data retrieval (any timezone)

    Returns:
        Formatted timestamp string (e.g., "Jun 24 at 6:22 AM")
    """
    if not retrieval_time:
        return "Unknown"

    # Convert to Eastern Time
    eastern = ZoneInfo("America/New_York")
    if retrieval_time.tzinfo is None:
        # Naive datetime - assume UTC
        retrieval_time = retrieval_time.replace(tzinfo=timezone.utc)

    retrieval_time_et = retrieval_time.astimezone(eastern)
    return retrieval_time_et.strftime("%b %-d at %-I:%M %p")


def format_long_date(date: Optional[datetime] = None) -> str:
    """
    Format date as long format for email header.

    Args:
        date: Date to format. If None, uses current date.

    Returns:
        Formatted date string (e.g., "Monday, June 24, 2026")
    """
    if date is None:
        date = datetime.now()

    return date.strftime("%A, %B %d, %Y")


__all__ = [
    "format_water_temp_value",
    "format_tide_info",
    "format_wind_info",
    "format_retrieval_timestamp",
    "format_long_date",
]
