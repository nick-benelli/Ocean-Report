"""Email formatting module for ocean report."""

from datetime import datetime
from typing import Dict, List, Optional, TypedDict

from ..logger import logger
from ..models.noaa.tides import NoaaTidePredictionRecord


class WindForecastEntry(TypedDict):
    """Type definition for a wind forecast entry."""

    time: str
    speed_kmh: float
    direction_deg: float
    speed_mph: float
    direction: str
    wind_type: str


def generate_email_body(
    sections: List[str], retrieval_timestamps: Optional[Dict[str, datetime]] = None
) -> str:
    """
    Generate the full email body including water temperature, tides, and wind data.

    Args:
        sections (List[str]): Sections to add to emails. Example:
            ['🌡️ Water Temperature: 72.5°F', '🌊 Tides:\n...']
        retrieval_timestamps (Optional[Dict[str, datetime]]):
            Dictionary containing retrieval timestamps for each data source.
            Keys: 'water_temp', 'tides', 'wind', 'water_temp_data_time'

    Returns:
        str: Full formatted email body.
    """
    logger.info("Generating email body...")
    today = datetime.now().strftime("%A, %B %d, %Y")
    headings = [f"Daily Water Report – {today} \n\n"]

    # Add data retrieval timestamp section if provided
    timestamp_section = []
    if retrieval_timestamps:
        timestamp_section.append(format_retrieval_timestamps(retrieval_timestamps))

    trailer = [
        "--------",
        "\nTide & water temp from NOAA (Atlantic City Station 8534720) | Wind by Open-Meteo\n",
    ]
    body_list = headings + sections + trailer + timestamp_section
    return "".join(body_list)


def format_retrieval_timestamps(timestamps: Dict[str, datetime]) -> str:
    """
    Format data retrieval timestamps for email display.

    Args:
        timestamps (Dict[str, datetime]): Dictionary with keys 'water_temp', 'tides', 'wind'
            and optionally 'water_temp_data_time' for the NOAA measurement timestamp

    Returns:
        str: Formatted timestamp section
    """
    # Since all data is typically retrieved at the same time, just show one timestamp
    retrieval_time = None
    if "water_temp" in timestamps:
        retrieval_time = timestamps["water_temp"]
    elif "tides" in timestamps:
        retrieval_time = timestamps["tides"]
    elif "wind" in timestamps:
        retrieval_time = timestamps["wind"]
    
    if not retrieval_time:
        return ""
    
    lines = ["\n📊 Data Retrieved: "]
    lines.append(retrieval_time.strftime("%b %-d at %-I:%M %p"))
    
    # Add the actual water temp measurement time if different from retrieval time
    if "water_temp_data_time" in timestamps and timestamps["water_temp_data_time"]:
        data_time_str = timestamps["water_temp_data_time"]
        lines.append(f"\n  Water temp measured at {data_time_str}")
    
    lines.append("\n")
    return "".join(lines)


# NOTE ---- Water Temperature ----
def format_water_temp(water_temperature: Optional[float]) -> str:
    """
    Format the water temperature for email display.

    Args:
        water_temperature (Optional[float]): Water temperature in Fahrenheit,
            or None if unavailable.

    Returns:
        str: Formatted water temperature string.
    """
    try:
        if water_temperature is None or not isinstance(water_temperature, (int, float)):
            return "🌡️ Water Temperature: unavailable\n\n"

        # Handle NaN or infinite values
        if water_temperature is None or abs(water_temperature) == float("inf"):
            return "🌡️ Water Temperature: unavailable\n\n"

        return f"🌡️ Water Temperature: {water_temperature:.1f} °F\n\n"

    except (TypeError, ValueError):
        return "🌡️ Water Temperature: unavailable\n\n"


# NOTE ---- Tide ----
def format_tide_for_email(tide_events: List[NoaaTidePredictionRecord]) -> str:
    """
    Converts a list of tide event objects into a formatted string for email display.

    Args:
        tide_events: List of NoaaTidePredictionRecord objects with timestamp, event_type, and height_feet.

    Returns:
        str: Formatted string of tide events.
    """
    formatted = []
    for tide in tide_events:
        dt = datetime.strptime(tide.timestamp, "%Y-%m-%d %H:%M")
        time_str = dt.strftime("%-I:%M %p")  # Format time as '2:47 PM'
        tide_type = "⬆️ High Tide" if tide.event_type == "H" else "⬇️ Low Tide"
        height = float(tide.height_feet)
        formatted.append(f"{tide_type} at {time_str} — {height:.1f} ft")

    tide_text = "\n".join(formatted)
    return f"🌊 Tides:\n{tide_text}\n\n"


# NOTE ---- Wind Forecast ----
def convert_wind_data_to_text(wind_data: List[WindForecastEntry]) -> str:
    """
    Convert structured wind data into formatted text.
    """
    lines = []
    for entry in wind_data:
        lines.append(f"Time: {entry['time']}")
        lines.append(f"Wind Speed: {entry['speed_mph']} mph")
        lines.append(f"Wind Direction: {entry['direction']}")
        lines.append(f"Wind Type: {entry['wind_type']}\n")
    return "\n".join(lines) + "\n"


def format_wind_forecast_email(wind_data: List[WindForecastEntry]) -> str:
    """
    Format wind forecast data as plain text for email.

    Args:
        wind_data (List[WindForecastEntry]): Wind forecast with keys 'time',
            'speed_mph', 'direction', 'direction_deg', and 'wind_type'.

    Returns:
        str: Plain text wind forecast section.
    """
    lines = [
        "🌬️ Wind Forecast:",
        "Key times for your beach today:",
    ]

    for entry in wind_data:
        try:
            time_str = entry["time"].rjust(5)  # e.g., '8 AM ' or '12 PM'
            speed_str = f"{entry['speed_mph']:.1f}".rjust(
                4
            )  # right-align speeds like '13.0' or ' 4.0'
            direction = entry["direction"].ljust(3)  # 'NW ', 'ENE', etc.
            deg = f"({entry['direction_deg']}°)".rjust(
                6
            )  # Align degrees with parentheses
            wind_type = entry["wind_type"]

            line = f"• {time_str}: {speed_str} mph {direction} {deg} → {wind_type}"
            lines.append(line)
        except (KeyError, TypeError, ValueError):
            continue

    if len(lines) < 3:
        return "🌬️ Wind Forecast: unavailable\n\n"

    return "\n".join(lines) + "\n\n"


def format_wind_forecast_html(wind_data: List[WindForecastEntry]) -> str:
    """
    Format wind forecast data as HTML for email clients.

    Args:
        wind_data (List[WindForecastEntry]): Wind forecast with keys 'time', 'speed_mph',
            'direction', 'direction_deg', and 'wind_type'.

    Returns:
        str: HTML string of wind forecast.
    """
    lines = [
        "<h2>Wind Forecast for Today 🌬️</h2>",
        "<p>Here’s the wind forecast near your beach (facing 140°) for key times today:</p>",
        "<ul>",
    ]

    for entry in wind_data:
        line = (
            f"<li><strong>{entry['time']}</strong> – {entry['speed_mph']} mph from "
            f"<strong>{entry['direction']} ({entry['direction_deg']}°)</strong> → "
            f"<strong>{entry['wind_type']}</strong></li>"
        )
        lines.append(line)

    lines.append("</ul>")
    return "\n".join(lines)
