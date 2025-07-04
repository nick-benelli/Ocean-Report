import requests
from datetime import datetime
import json
import pytz
from typing import Set, List, Dict, Any
from .constants import (
    LONGITUDE as LONG,
    LATITUDE as LAT,
)


def get_wind_data_for_email(
    latitude: float = LAT,
    longitude: float = LONG,
    times_to_get: Set[str] = {"08:00", "12:00", "15:00", "18:00"},
) -> str:
    wind_data = get_daily_wind_data(
        latitude=latitude,
        longitude=longitude,
        times_to_get=times_to_get,
    )

    for entry in wind_data:
        deg = entry["direction_deg"]
        entry["speed_mph"] = kmh_to_mph(entry["speed_kmh"])
        entry["direction"] = deg_to_16_point_direction(deg)
        entry["wind_type"] = classify_wind_relative_to_beach(deg)

    email_text = format_wind_forecast_email(wind_data)

    return email_text


def get_daily_wind_data(
    latitude: float = LAT,
    longitude: float = LONG,
    times_to_get: Set[str] = {"08:00", "12:00", "15:00", "18:00"},
):
    base_url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "wind_speed_10m,wind_direction_10m",
        # "daily": "wind_speed_10m_max,wind_direction_10m_dominant",
        "timezone": "America/New_York",
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()
    print(json.dumps(data, indent=4))

    selected = []

    for t, speed, direction in zip(
        data["hourly"]["time"],
        data["hourly"]["wind_speed_10m"],
        data["hourly"]["wind_direction_10m"],
    ):
        dt = datetime.fromisoformat(t)
        if dt.strftime("%H:%M") in times_to_get and dt.date() == datetime.now().date():
            selected.append(
                {
                    "time": dt.strftime("%-I %p"),  # e.g., "8 AM"
                    "speed_kmh": speed,
                    "direction_deg": direction,
                }
            )

    for entry in selected:
        deg = entry["direction_deg"]
        entry["speed_mph"] = kmh_to_mph(entry["speed_kmh"])
        entry["direction"] = deg_to_16_point_direction(deg)
        entry["wind_type"] = classify_wind_relative_to_beach(deg)

    return selected


def get_wind_data(latitude=LAT, longitude=LONG, hours=24, days=3):
    # url = (
    #     "https://marine-api.open-meteo.com/v1/marine?"
    #     "latitude=39.565&longitude=-74.240&hourly=wind_speed_10m,wind_direction_10m&"
    #     "daily=wind_speed_10m_max,wind_direction_10m_dominant&timezone=auto"
    # )
    base_url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "wind_speed_10m,wind_direction_10m",
        # "daily": "wind_speed_10m_max,wind_direction_10m_dominant",
        "timezone": "America/New_York",
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()

    print(json.dumps(data, indent=4))

    # Convert strings to datetime
    hourly_times = [datetime.fromisoformat(t) for t in data["hourly"]["time"]]

    # Match the nearest time to now
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    try:
        hour_idx = hourly_times.index(now)
    except ValueError:
        raise RuntimeError(f"Current hour {now.isoformat()} not found in hourly times")

    current_wind_speed = data["hourly"]["wind_speed_10m"][hour_idx]
    current_wind_dir = data["hourly"]["wind_direction_10m"][hour_idx]

    # Get current hour index
    current_hour = datetime.now().strftime("%Y-%m-%dT%H:00")
    hour_idx = data["hourly"]["time"].index(current_hour)

    current_wind_speed = data["hourly"]["wind_speed_10m"][hour_idx]
    current_wind_dir = data["hourly"]["wind_direction_10m"][hour_idx]

    # Next 24 hours
    next_24 = {
        "wind_speeds": data["hourly"]["wind_speed_10m"][hour_idx : hour_idx + 24],
        "wind_dirs": data["hourly"]["wind_direction_10m"][hour_idx : hour_idx + 24],
        "times": data["hourly"]["time"][hour_idx : hour_idx + 24],
    }

    # # Next 3 days
    # next_3_days = list(
    #     zip(
    #         data["daily"]["time"][:3],
    #         data["daily"]["wind_speed_10m_max"][:3],
    #         data["daily"]["wind_direction_10m_dominant"][:3],
    #     )
    # )

    return {
        "current": {"speed": current_wind_speed, "dir": current_wind_dir},
        "next_24": next_24,
        # "next_3_days": next_3_days,
    }


def kmh_to_mph(kmh: float) -> float:
    return round(kmh * 0.621371, 1)


def deg_to_16_point_direction(deg):
    """
    Convert degrees to compass rose directions
    """
    directions = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]
    ix = round(deg / 22.5) % 16
    return directions[ix]


def classify_wind_relative_to_beach(wind_deg, beach_facing_deg=140):
    # Normalize the angle difference between 0–180
    diff = abs(wind_deg - beach_facing_deg) % 360
    if diff > 180:
        diff = 360 - diff

    if diff <= 22.5:
        return "Onshore"
    elif diff <= 67.5:
        return "Onshore/Cross-shore"
    elif diff <= 112.5:
        return "Cross-shore"
    elif diff <= 157.5:
        return "Cross-shore/Offshore"
    else:
        return "Offshore"


def convert_data_to_text(wind_data: List[Dict[str, Any]]) -> str:
    text = ""
    for entry in wind_data:
        text += f"Time: {entry['time']}\n"
        text += f"Wind Speed: {entry['speed_mph']} mph\n"
        text += f"Wind Direction: {entry['direction']}\n"
        text += f"Wind Type: {entry['wind_type']}\n"
        text += "\n"

    text += "\n"
    return text


def format_wind_forecast_email(wind_data: List[Dict[str, Any]]) -> str:
    lines = []
    lines.append("**Wind Forecast for Today** 🌬️\n")
    lines.append(
        "Here’s the wind forecast near your beach (facing 140°) for key times today:\n"
    )

    for entry in wind_data:
        # line = f"- **{entry['time']}** – {entry['speed_mph']} mph ({entry['speed_kmh']} km/h) from **{entry['direction']} ({entry['direction_deg']}°)** → **{entry['wind_type']}**"
        line = f"- **{entry['time']}** – {entry['speed_mph']} mph from **{entry['direction']} ({entry['direction_deg']}°)** → **{entry['wind_type']}**"
        lines.append(line)

    lines.append(
        "\nAll winds are **onshore**, which may create choppier ocean conditions and less ideal surf."
    )

    text = "\n".join(lines)
    return text
