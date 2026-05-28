"""Configuration management for ocean report."""

from typing import Any, Dict
from dotenv import load_dotenv

# import os
from . import constants, utils

# Load environment variables from .env file
load_dotenv()

# Load configuration with environment variable substitution
config: Dict[str, Any] = utils.load_config_with_env_substitution(constants.CONFIG_PATH)


# Path to the configuration file

RECIPIENTS_GIST_URL = config["email"]["recipient_urls"].get("main", "")
OFFSEASON_RECIPIENTS_GIST_URL = config["email"]["recipient_urls"].get("offseason", "")
TEST_RECIPIENTS_GIST_URL = config["email"]["recipient_urls"].get("test", "")
# RECIPIENTS_GIST_URL = os.getenv("RECIPIENTS_GIST_URL")
# TEST_RECIPIENTS_GIST_URL = os.getenv("TEST_RECIPIENTS_GIST_URL")


# NOAA Station ID
EXAMPLE_STATION_ID = "8534720"
EXAMPLE_BUOY_ID = "44091"
STATION_ID = config["noaa"].get("station_id", EXAMPLE_STATION_ID)
BUOY_ID = config["noaa"].get("buoy_id", EXAMPLE_BUOY_ID)

# Longitude, Latitude, and Beach Orientation
EXAMPLE_LONGITUDE = -74.2
EXAMPLE_LATITUDE = 39.5
EXAMPLE_BEACH_ORIENTATION_DEGREES = 140  # Approximate orientation of beach in degrees


# Helper function to safely convert string to float with fallback to default
def _safe_float_conversion(value, default):
    """Convert value to float, returning default if value contains unsubstituted variables."""
    try:
        if isinstance(value, str) and value.startswith("${"):
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


BEACH_ORIENTATION_DEGREES = _safe_float_conversion(
    config["location"].get(
        "beach_orientation_degrees", EXAMPLE_BEACH_ORIENTATION_DEGREES
    ),
    EXAMPLE_BEACH_ORIENTATION_DEGREES,
)
LONGITUDE = _safe_float_conversion(
    config["location"].get("longitude", EXAMPLE_LONGITUDE), EXAMPLE_LONGITUDE
)
LATITUDE = _safe_float_conversion(
    config["location"].get("latitude", EXAMPLE_LATITUDE), EXAMPLE_LATITUDE
)

# Email Settings
EMAIL_SENDER = config["email"].get("sender")
EMAIL_SMTP_PORT = config["email"].get("smtp_port", 587)
EMAIL_SMTP_SERVER = config["email"].get("smtp_server", "smtp.gmail.com")


# Summer time
SUMMER_MEMORIAL_DAY_OFFSET: int = config["summer"].get("memorial_day_offset", -4)
SUMMER_LABOR_DAY_OFFSET: int = config["summer"].get("labor_day_offset", 7)
