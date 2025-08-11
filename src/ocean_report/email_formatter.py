# ocean_report/email_formatter.py
from datetime import datetime
from typing import List, Dict, Any


def generate_email_body(sections: List[str]) -> str:
    """
    Generates the full email body including water temperature, tides, and optional wind data.

    Args:
        sections (List[str]): Sections to add to emails. Example: ['🌡️ Water Temperature: 72.5°F', '🌊 Tides:\n...']

    Returns:
        str: Full formatted email body.
    """
    today = datetime.now().strftime("%A, %B %d, %Y")
    headings = [f"Daily Water Report – {today} \n\n"]
    trailer = [
        "--------",
        "\nTide & water temp from NOAA (Atlantic City Station 8534720) | Wind by Open-Meteo",
    ]
    body_list = headings + sections + trailer
    return "".join(body_list)


# NOTE ---- Water Temperature ----
def format_water_temp(water_temperature: float) -> str:
    """
    Formats the water temperature for email display.

    Args:
        water_temperature (float): Water temperature in Fahrenheit.

    Returns:
        str: Formatted water temperature string.
    """
    return f"🌡️ Water Temperature: {water_temperature:.1f} °F\n\n"


# NOTE ---- Tide ----
def format_tide_for_email(tide_events: List[Dict[str, Any]]) -> str:
    """
    Converts a list of tide event dictionaries into a formatted string for email display.

    Args:
        tide_events (List[Dict[str, Any]]): List of tide events with keys 't', 'type', and 'v'.

    Returns:
        str: Formatted string of tide events.
    """
    formatted = []
    for tide in tide_events:
        dt = datetime.strptime(tide["t"], "%Y-%m-%d %H:%M")
        time_str = dt.strftime("%-I:%M %p")  # Format time as '2:47 PM'
        tide_type = "High Tide" if tide["type"] == "H" else "Low Tide"
        height = float(tide["v"])
        formatted.append(f"{tide_type} at {time_str} — {height:.1f} ft")

    tide_text = "\n".join(formatted)
    return f"🌊 Tides:\n{tide_text}\n\n"


# NOTE ---- Wind Forecast ----
def convert_wind_data_to_text(wind_data: List[Dict[str, Any]]) -> str:
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


def format_wind_forecast_email(wind_data: List[Dict[str, Any]]) -> str:
    """
    Formats wind forecast data as plain text for email.

    Args:
        wind_data (List[Dict[str, Any]]): Wind forecast with keys 'time', 'speed_mph', 'direction', 'direction_deg', and 'wind_type'.

    Returns:
        str: Plain text wind forecast section.
    """
    lines = [
        "🌬️ Wind Forecast:",
        "Key times for your beach today:",
    ]

    for entry in wind_data:
        time_str = entry["time"].rjust(5)  # e.g., '8 AM ' or '12 PM'
        speed_str = f"{entry['speed_mph']:.1f}".rjust(
            4
        )  # right-align speeds like '13.0' or ' 4.0'
        direction = entry["direction"].ljust(3)  # 'NW ', 'ENE', etc.
        deg = f"({entry['direction_deg']}°)".rjust(6)  # Align degrees with parentheses
        wind_type = entry["wind_type"]

        line = f"- {time_str}: {speed_str} mph {direction} {deg} → {wind_type}"
        lines.append(line)

    return "\n".join(lines) + "\n\n"


def format_wind_forecast_html(wind_data: List[Dict[str, Any]]) -> str:
    """
    Formats wind forecast data as HTML for email clients.

    Args:
        wind_data (List[Dict[str, Any]]): Wind forecast with keys 'time', 'speed_mph', 'direction', 'direction_deg', and 'wind_type'.

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
