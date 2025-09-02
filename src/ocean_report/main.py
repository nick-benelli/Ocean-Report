# src/ocean_report/main.py
from datetime import datetime
from dotenv import load_dotenv

from . import tide, water_temp, emailer, wind, email_formatter as formatter
from .config import config, LONGITUDE, LATITUDE, BEACH_ORIENTATION_DEGREES
from .logger import logger
from .address_fetcher import get_recipients

# Whether to use the recipients URL for email or environment variable
USE_RECIP_URL = True


def run_report(run_email: bool = True, test: bool = False) -> None:
    """
    Fetch tide, water temperature, and wind data, format it, and send or print an email report.

    Args:
        run_email (bool): If True, send the email. If False, print the email content.
        test (bool): If True, use test email settings.
    """
    print("Initiating Ocean Report Email Process...")
    logger.info("Starting Ocean Report Email Process...")

    # Load environment variables
    load_dotenv()

    # --- Email Settings ---
    email_sender = config["email"].get("sender", "sender@example.com")
    email_password = config["email"].get("password", "password1234")
    email_recipients = config["email"].get("recipients", "")

    # --- Recipients (BCC) ---
    if USE_RECIP_URL:
        bcc_recipients_raw = get_recipients(test_recips=test)
    else:
        bcc_recipients_raw = config["email"].get("recipients", "")
    bcc_recipients = [
        email.strip() for email in bcc_recipients_raw.split(",") if email.strip()
    ]

    # --- Location/Station Settings ---
    station_id = config["noaa"]["station_id"]

    # --- Date ---
    today_str = datetime.now().strftime("%Y%m%d")
    today_date_str = datetime.today().strftime("%Y-%m-%d")

    # --- Fetch Data ---
    # Tide data
    logger.info("Fetching tide data...")
    tides = tide.fetch_tide_data(station_id=station_id, date=today_str)
    daytime_tides = tide.filter_daytime_tides(tides)
    tide_text = formatter.format_tide_for_email(daytime_tides)

    # Water temperature data
    logger.info("Fetching water temp data...")
    h20_temp = water_temp.fetch_water_temp(station_id=station_id)
    h20_temp_str = formatter.format_water_temp(h20_temp)

    # Wind data
    logger.info("Fetching wind data...")
    wind_data = wind.get_daily_wind_data(
        latitude=LATITUDE,
        longitude=LONGITUDE,
        beach_facing_deg=BEACH_ORIENTATION_DEGREES,
        times_to_get={"08:00", "12:00", "15:00", "18:00"},
    )
    wind_text = formatter.format_wind_forecast_email(wind_data)

    # --- Format Email ---
    logger.info("Generating email body...")
    email_body = formatter.generate_email_body(
        sections=[h20_temp_str, tide_text, wind_text]
    )

    email_subject = f"🌊 LBI Daily Water Report: {today_date_str}"
    if test:
        email_subject = f"TEST: {email_subject}"

    # --- Send or Print Email ---
    logger.info("Sending email..." if run_email else "Email sending is disabled.")
    if run_email:
        emailer.send_email(
            subject=email_subject,
            body=email_body,
            sender_email=email_sender,
            recipient_email=email_recipients,
            bcc_list=bcc_recipients,
            email_password=email_password,
        )
        logger.info("Email sent successfully.")
        print("Email sent!")
    else:
        print("Email sending is disabled.")
        logger.info("Email sending is disabled. Printing email content instead.")
        print(
            f"\nTo: {email_recipients}\n",
            f"BCC: {', '.join(bcc_recipients)}\n",
            f"From: {email_sender}\n\n\n",
            f"{email_subject}\n\n{email_body}",
        )
        logger.info("Email content printed to console.")

    return None

