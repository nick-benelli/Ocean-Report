"""
Helper functions to prepare data for email templates if
switched to HTML templates.
"""

from typing import List
from ..models.openmeteo.wind import WindForecastEntry


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
