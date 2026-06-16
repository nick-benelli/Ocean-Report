"""Main entry point for ocean report."""

from datetime import date, datetime
from pathlib import Path
from typing import Union

from ..application.factory import create_application_context
from ..emailer import email_formatter as formatter
from ..emailer import sender as emailer
from ..logger import logger
from ..use_cases import tides as tides_use_case
from ..use_cases import water_temperature as water_temp_use_case
from ..use_cases import wind as wind_use_case
from ..use_cases.email import get_email_recipients

# Whether to use the recipients URL for email or environment variable
USE_RECIP_URL = True


def run_report(
    *,
    cfg_path: Union[str, Path] = None,
    run_email: bool = True,
    test: bool = False
) -> None:
    """
    Fetch tide, water temperature, and wind data, format it, and send or print an email report.

    Args:
        cfg_path: Path to configuration file. If None, uses default config.
        run_email: If True, send the email. If False, print the email content.
        test: If True, use test email settings.
    """
    print("Initiating Ocean Report Email Process...")
    logger.info("Starting Ocean Report Email Process...")

    print(f"Today is {date.today().strftime('%A, %B %d, %Y')}")
    logger.info("Today is %s", date.today().strftime("%A, %B %d, %Y"))

    # --- Initialize Application Context ---
    app_cfg =  create_application_context(config_path=cfg_path)
    settings = app_cfg.config

    # --- Email Settings ---
    email_sender_address = settings.email.sender or "sender@example.com"
    email_password = settings.email.password or "password1234"
    email_recipients = settings.email.recipients or ""

    # --- Recipients (BCC) ---
    bcc_recipients = [
        email.strip()
        for email in (
            get_email_recipients(test_recips=test)
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
    # Tide data - using orchestration layer
    logger.info("Fetching daytime tide data...")
    daytime_tides = tides_use_case.get_daytime_tides_for_date(
        context=app_cfg,
        station_id=station_id,
        date=today_str,
    )
    tide_text = formatter.format_tide_for_email(daytime_tides)

    # Water temperature data - using orchestration layer
    logger.info("Fetching latest water temperature...")
    water_temp = water_temp_use_case.get_latest_water_temp(
        context=app_cfg,
        station_id=station_id,
    )
    h20_temp_str = formatter.format_water_temp(water_temp)

    # Wind data - using orchestration layer
    logger.info("Fetching daily wind forecast...")
    wind_forecast = wind_use_case.get_daily_wind_forecast(
        context=app_cfg,
        latitude=settings.location.latitude,
        longitude=settings.location.longitude,
        beach_facing_deg=settings.location.beach_orientation_degrees,
        times_to_get={"08:00", "12:00", "15:00", "18:00"},
    )
    wind_text = formatter.format_wind_forecast_email(wind_forecast)

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
            sender_email=email_sender_address,
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
            f"From: {email_sender_address}\n\n\n",
            f"{email_subject}\n\n{email_body}",
        )
        logger.info("Email content printed to console.")



def clean_recip_addresses():




def _send_email(*, context, run_email)