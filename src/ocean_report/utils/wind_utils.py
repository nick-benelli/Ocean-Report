"""Wind calculation and conversion utilities."""


def kmh_to_mph(kmh: float) -> float:
    """
    Convert kilometers per hour to miles per hour.

    Args:
        kmh (float): Speed in kilometers per hour.

    Returns:
        float: Speed in miles per hour, rounded to 1 decimal place.
    """
    return round(kmh * 0.621371, 1)


def deg_to_16_point_direction(deg: float) -> str:
    """
    Convert degrees into one of the 16 compass rose directions.

    Args:
        deg (float): Direction in degrees (0-360).

    Returns:
        str: Compass direction (e.g., "N", "NE", "ENE", etc.).
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
    index = round(deg / 22.5) % 16
    return directions[index]


def relative_angle_difference(wind_deg: float, beach_facing_deg: float) -> float:
    """
    Return the smallest angular difference between wind and beach orientation.

    Args:
        wind_deg (float): Wind direction in degrees.
        beach_facing_deg (float): Beach orientation in degrees.

    Returns:
        float: Smallest angular difference (0-180 degrees).
    """
    diff = abs(wind_deg - beach_facing_deg) % 360
    if diff > 180:
        return 360 - diff
    return diff


def classify_wind_relative_to_beach(
    wind_deg: float,
    beach_facing_deg: float = 140.0,
) -> str:
    """
    Classify wind direction relative to beach orientation.

    Args:
        wind_deg (float): Wind direction in degrees.
        beach_facing_deg (float): Beach orientation in degrees (default: 140.0).

    Returns:
        str: Classification of wind (e.g., "Onshore", "Cross-shore", "Offshore").
    """
    diff = relative_angle_difference(wind_deg, beach_facing_deg)

    if diff <= 22.5:
        return "Onshore"
    if diff <= 67.5:
        return "Cross/Onshore"
    if diff <= 112.5:
        return "Cross-shore"
    if diff <= 157.5:
        return "Cross/Offshore"
    return "Offshore"


def classify_wind_relative_to_beach_breakdown(
    wind_deg: float,
    beach_facing_deg: float = 140.0,
) -> str:
    """
    Classify wind direction relative to beach orientation with detailed breakdown.

    Labels:
        - Onshore
        - On/Cross-shore (leans more onshore than cross)
        - Cross-shore
        - Off/Cross-shore (leans more offshore than cross)
        - Offshore

    Args:
        wind_deg (float): Wind direction in degrees.
        beach_facing_deg (float): Beach orientation in degrees (default: 140.0).

    Returns:
        str: Detailed classification of wind direction.
    """
    diff = relative_angle_difference(wind_deg, beach_facing_deg)
    thresholds = [
        (22.5, "Onshore"),
        (45, "On/Cross-shore"),
        (67.5, "Cross/Onshore"),
        (90, "Cross-shore"),
        (112.5, "Cross/Offshore"),
        (135, "Off/Cross-shore"),
        (157.5, "Cross/Offshore"),
    ]

    for threshold, label in thresholds:
        if diff <= threshold:
            return label
    return "Offshore"
