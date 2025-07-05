# src/lbi_surf/main.py
import os
from datetime import datetime
from dotenv import load_dotenv
from . import constants, tide, water_temp, emailer, wind, email_formatter as formatter
import logging


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def main(run_email: bool = True):
    load_dotenv()

    # Env Variables
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")
    BCC_RECIPIENTS_RAW = os.getenv("BCC_RECIPIENTS", "")
    BCC_RECIPIENTS = [
        email.strip() for email in BCC_RECIPIENTS_RAW.split(",") if email.strip()
    ]

    # Date
    today = datetime.now().strftime("%Y%m%d")
    today_date_str = datetime.today().strftime("%Y-%m-%d")

    # Get tides
    logger.info("Fetching tide data...")
    tides = tide.fetch_tide_data(date=today)
    daytime_tides = tide.filter_daytime_tides(tides)
    tide_text = formatter.format_tide_for_email(daytime_tides)

    # Get water temperature
    logger.info("Fetching water temp data...")
    h20_temp = water_temp.fetch_water_temp(station_id=constants.STATION_ID)
    h20_temp_str = formatter.format_water_temp(h20_temp)

    # Get wind data
    logger.info("Fetching wind data...")
    wind_data = wind.get_daily_wind_data(
        latitude=constants.LATITUDE,
        longitude=constants.LONGITUDE,
        times_to_get={"08:00", "12:00", "15:00", "18:00"},
    )
    wind_text = formatter.format_wind_forecast_email(wind_data)

    # Send email
    logger.info("Generating email body...")
    email_body = formatter.generate_email_body(
        sections=[h20_temp_str, tide_text, wind_text]
    )

    email_subject = f"🌊 Daily Water Report: {today_date_str}"
    logger.info("Sending email...")
    if run_email:
        emailer.send_email(
            subject=email_subject,
            body=email_body,
            sender_email=EMAIL_SENDER,
            recipient_email=EMAIL_RECIPIENT,
            bcc_list=BCC_RECIPIENTS,
            email_password=EMAIL_PASSWORD,
        )

        print("Email sent successfully!")
    else:
        print("Email sending is disabled.")
        print(
            (f"\nTo: {EMAIL_RECIPIENT}\n"),
            (f"From: {EMAIL_SENDER}\nBCC: {BCC_RECIPIENTS}"),
            (f"{email_subject}\n\n{email_body}"),
        )

    return None


if __name__ == "__main__":
    main()
