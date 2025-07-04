# src/lbi_surf/main.py
import os
from datetime import datetime
from dotenv import load_dotenv
from . import constants, tide, water_temp, emailer
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    load_dotenv()

    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")

    # email_password = os.getenv("EMAIL_PASSWORD")
    today = datetime.now().strftime("%Y%m%d")
    today_date_str = datetime.today().strftime("%Y-%m-%d")

    # Get tides
    logger.info("Fetching tide data...")
    tides = tide.fetch_tide_data(date=today)
    daytime_tides = tide.filter_daytime_tides(tides)

    # Get water temperature
    logger.info("Fetching water temp data...")
    h20_temp = water_temp.fetch_water_temp(station_id=constants.STATION_ID)
    h20_temp_str = water_temp.format_water_temp(h20_temp)

    # Send email
    logger.info("Generating email body...")
    email_body = emailer.generate_email_body(daytime_tides, h20_temp_str)
    logger.info("Sending email...")
    emailer.send_email(
        subject=f"🌊 Daily Water Report: {today_date_str}",
        body=email_body,
        sender_email=EMAIL_SENDER,
        recipient_email=EMAIL_RECIPIENT,
        email_password=EMAIL_PASSWORD,
    )

    print("Email sent successfully!")

    return None


if __name__ == "__main__":
    main()
