"""Main entry point for ocean report."""

from datetime import date, datetime

from .api_client.endpoints import tide, water_temp, wind

from . import email_formatter as formatter
from . import emailer
from .address_fetcher import get_recipients
from .config import get_settings
from .logger import logger

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

    print(f"Today is {date.today().strftime('%A, %B %d, %Y')}")
    logger.info("Today is %s", date.today().strftime("%A, %B %d, %Y"))

    settings = get_settings()

    # --- Email Settings ---
    email_sender = settings.email.sender or "sender@example.com"
    email_password = settings.email.password or "password1234"
    email_recipients = settings.email.recipients or ""

    # --- Recipients (BCC) ---
    bcc_recipients = [
        email.strip()
        for email in (
            get_recipients(test_recips=test)
            if USE_RECIP_URL
            else (settings.email.recipients or "")
        ).split(",")
        if email.strip()
    ]

    # --- Location/Station Settings ---
    station_id = settings.noaa.station_id

    # --- Date ---
    today_str = datetime.now().strftime("%Y%m%d")
    today_date_str = datetime.today().strftime("%Y-%m-%d")

    # --- Fetch Data ---
    # Tide data
    logger.info("Adding tide data...")
    tide_text = formatter.format_tide_for_email(
        tide.filter_daytime_tides(
            tide.fetch_tide_data(station_id=station_id, date=today_str)
        )
    )

    # Water temperature data
    logger.info("Adding water temp data...")
    h20_temp_str = formatter.format_water_temp(
        water_temp.fetch_water_temp(station_id=station_id)
    )

    # Wind data
    logger.info("Adding wind data...")
    wind_text = formatter.format_wind_forecast_email(
        wind.get_daily_wind_data(
            latitude=settings.location.latitude,
            longitude=settings.location.longitude,
            beach_facing_deg=settings.location.beach_orientation_degrees,
            times_to_get={"08:00", "12:00", "15:00", "18:00"},
        )
    )

    # --- Format Email ---
    logger.info("Constructing email...")
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
            email_password=email_password,
            recipients=emailer.EmailRecipients(
                to_email=email_recipients,
                bcc_list=bcc_recipients,
            ),
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
