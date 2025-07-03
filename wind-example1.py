import requests
from datetime import datetime

def get_wind_data():
    url = (
        "https://marine-api.open-meteo.com/v1/marine?"
        "latitude=39.565&longitude=-74.240&hourly=wind_speed_10m,wind_direction_10m&"
        "daily=wind_speed_10m_max,wind_direction_10m_dominant&timezone=auto"
    )
    response = requests.get(url)
    data = response.json()

    # Get current hour index
    current_hour = datetime.now().strftime("%Y-%m-%dT%H:00")
    hour_idx = data["hourly"]["time"].index(current_hour)

    current_wind_speed = data["hourly"]["wind_speed_10m"][hour_idx]
    current_wind_dir = data["hourly"]["wind_direction_10m"][hour_idx]

    # Next 24 hours
    next_24 = {
        "wind_speeds": data["hourly"]["wind_speed_10m"][hour_idx:hour_idx+24],
        "wind_dirs": data["hourly"]["wind_direction_10m"][hour_idx:hour_idx+24],
        "times": data["hourly"]["time"][hour_idx:hour_idx+24],
    }

    # Next 3 days
    next_3_days = list(zip(
        data["daily"]["time"][:3],
        data["daily"]["wind_speed_10m_max"][:3],
        data["daily"]["wind_direction_10m_dominant"][:3],
    ))

    return {
        "current": {"speed": current_wind_speed, "dir": current_wind_dir},
        "next_24": next_24,
        "next_3_days": next_3_days
    }
  
