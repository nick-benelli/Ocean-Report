# src/lbi_surf/main.py
from datetime import datetime
from dotenv import load_dotenv
from . import tide, water_temp, emailer, wind, email_formatter as formatter
from .config import config, LONGITUDE, LATITUDE
from .logger import logger
from .address_fetcher import get_recipients


def main(run_email: bool = True, test: bool = False) -> None:
    """
    Main function to fetch tide, water temperature, and wind data,
    format it, and send an email report.
    Args:
        run_email (bool): If True, send the email. If False, just print the email content.
        test (bool): If True, use test email settings.
    """
    load_dotenv()

    # Env Variables
    # Email Settings
    EMAIL_SENDER = config["email"].get("sender", "sender@example.com")
    EMAIL_PASSWORD = config["email"].get("password", "password1234")
    EMAIL_RECIPIENTS = config["email"].get("recipients", "")
    BCC_RECIPIENTS_RAW = get_recipients(test_recips=test)

    # Location Settings
    # LONGITUDE = config["location"].get("longitude")
    # LATITUDE = config["location"].get("latitude")
    STATION_ID = config["noaa"]["station_id"]

    # NOTE: This is an unnecessary step because it is already formated
    BCC_RECIPIENTS = [
        email.strip() for email in BCC_RECIPIENTS_RAW.split(",") if email.strip()
    ]

    # Date
    today = datetime.now().strftime("%Y%m%d")
    today_date_str = datetime.today().strftime("%Y-%m-%d")

    # Get tides
    logger.info("Fetching tide data...")
    tides = tide.fetch_tide_data(station_id=STATION_ID, date=today)
    daytime_tides = tide.filter_daytime_tides(tides)
    tide_text = formatter.format_tide_for_email(daytime_tides)

    # Get water temperature
    logger.info("Fetching water temp data...")
    h20_temp = water_temp.fetch_water_temp(station_id=STATION_ID)
    h20_temp_str = formatter.format_water_temp(h20_temp)

    # Get wind data
    logger.info("Fetching wind data...")
    wind_data = wind.get_daily_wind_data(
        latitude=LATITUDE,
        longitude=LONGITUDE,
        times_to_get={"08:00", "12:00", "15:00", "18:00"},
    )
    wind_text = formatter.format_wind_forecast_email(wind_data)

    # Send email
    logger.info("Generating email body...")
    email_body = formatter.generate_email_body(
        sections=[h20_temp_str, tide_text, wind_text]
    )

    email_subject = f"🌊 Daily Water Report: {today_date_str}"
    if test:
        email_subject = f"TEST: {email_subject}"
    logger.info("Sending email...")
    if run_email:
        emailer.send_email(
            subject=email_subject,
            body=email_body,
            sender_email=EMAIL_SENDER,
            recipient_email=EMAIL_RECIPIENTS,
            bcc_list=BCC_RECIPIENTS,
            email_password=EMAIL_PASSWORD,
        )

        print("Email sent!")
    else:
        print("Email sending is disabled.")
        print(
            (f"\nTo: {EMAIL_RECIPIENTS}\n"),
            (f"BCC: {', '.join(BCC_RECIPIENTS)}\n"),
            (f"From: {EMAIL_SENDER}\n\n\n"),
            (f"{email_subject}\n\n{email_body}"),
        )

    return None


if __name__ == "__main__":
    main()
