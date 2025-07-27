from dotenv import load_dotenv
import os
from . import constants, utils

# Load environment variables from .env file
load_dotenv()

# Load configuration with environment variable substitution
config = utils.load_config_with_env_substitution(constants.CONFIG_PATH)


# Path to the configuration file
RECIPIENTS_GIST_URL = os.getenv("RECIP_GIST_URL")
TEST_RECIPIENTS_GIST_URL = os.getenv("RECIP_GIST_TEST_URL")


# NOAA Station ID
EXAMPLE_STATION_ID = "8534720"
EXAMPLE_BUOY_ID = "44091"
STATION_ID = config["noaa"].get("station_id", EXAMPLE_STATION_ID)
BUOY_ID = config["noaa"].get("buoy_id", EXAMPLE_BUOY_ID)

# Longitude and Latitude
EXAMPLE_LONGITUDE = -74.2
EXAMPLE_LATITUDE = 39.5
LONGITUDE = float(config["location"].get("longitude", EXAMPLE_LONGITUDE))
LATITUDE = float(config["location"].get("latitude", EXAMPLE_LATITUDE))

# Email Settings
EMAIL_SENDER = config["email"].get("sender")
EMAIL_SMTP_PORT = config["email"].get("smtp_port", 587)
EMAIL_SMTP_SERVER = config["email"].get("smtp_server", "smtp.gmail.com")
