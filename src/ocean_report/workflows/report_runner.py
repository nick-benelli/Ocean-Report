"""Main entry point for ocean report."""

import logging
import time
from datetime import date, datetime
from pathlib import Path
from typing import Union

from ..application import create_application_context
from ..emailer import email_formatter as formatter
from ..logger import logger, configure_logger, LogOutput
from .data import fetch_raw_data, format_report_data
from .email import get_bcc_recipients, send_or_preview_email
from .models import FetchParams


def run_report(  # pylint: disable=too-many-locals,too-many-statements
    *, cfg_path: Union[str, Path] = None, run_email: bool = True, test: bool = False
) -> None:
    """
    Fetch tide, water temperature, and wind data, format it, and send or print an email report.

    Args:
        cfg_path: Path to configuration file. If None, uses default config.
        run_email: If True, send the email. If False, print the email content.
        test: If True, use test email settings.
    """
    workflow_start_time = time.time()
    logger.info("=" * 80)
    logger.info("Starting Ocean Report Email Process...")
    logger.info("Today is %s", date.today().strftime("%A, %B %d, %Y"))
    logger.info(
        "Run mode: %s | Send email: %s", "TEST" if test else "PRODUCTION", run_email
    )
    logger.info("=" * 80)

    # Load configuration
    logger.info("[STEP 1/5] Loading configuration...")
    step_start = time.time()
    context = create_application_context(config_path=cfg_path)
    settings = context.config

    # Configure logger from config
    log_output_map = {
        "console": LogOutput.CONSOLE,
        "file": LogOutput.FILE,
        "both": LogOutput.BOTH,
    }
    log_level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    output = log_output_map.get(settings.logging.output.lower(), LogOutput.CONSOLE)
    level = log_level_map.get(settings.logging.level.upper(), logging.INFO)

    if output in (LogOutput.FILE, LogOutput.BOTH):
        configure_logger(
            output=output,
            log_file=settings.logging.file_path,
            level=level,
            log_format=settings.logging.format,
        )
    else:
        configure_logger(
            output=output,
            level=level,
            log_format=settings.logging.format,
        )

    logger.info("Configuration loaded in %.2f seconds", time.time() - step_start)

    # Get email recipients
    logger.info("[STEP 2/5] Fetching email recipients...")
    step_start = time.time()
    bcc_recipients = get_bcc_recipients(
        test=test,
        use_url=settings.email.use_recipient_url,
        fallback_recipients=settings.email.recipients or "",
    )
    logger.info(
        "Recipients fetched in %.2f seconds (found %d recipients)",
        time.time() - step_start,
        len(bcc_recipients),
    )

    station_id = settings.noaa.station_id
    today_yyyymmdd = datetime.now().strftime("%Y%m%d")
    today_display = datetime.today().strftime("%Y-%m-%d")

    # Fetch all report data
    logger.info("[STEP 3/5] Fetching weather data from APIs...")
    step_start = time.time()
    try:
        fetch_params = FetchParams(
            station_id=station_id,
            date_str=today_yyyymmdd,
            latitude=settings.location.latitude,
            longitude=settings.location.longitude,
            beach_facing_deg=settings.location.beach_orientation_degrees,
            forecast_times={"08:00", "12:00", "15:00", "18:00"},
        )
        raw_data = fetch_raw_data(context, fetch_params)
        formatted_data = format_report_data(raw_data)
        logger.info(
            "All data fetched successfully in %.2f seconds", time.time() - step_start
        )
    except Exception as e:
        logger.error(
            "Failed to fetch report data after %.2f seconds: %s",
            time.time() - step_start,
            e,
            exc_info=True,
        )
        raise

    # Format email
    logger.info("[STEP 4/5] Formatting email content...")
    step_start = time.time()
    email_body = formatter.generate_email_body(
        sections=[
            formatted_data.water_temp_text,
            formatted_data.tide_text,
            formatted_data.wind_text,
        ],
        retrieval_timestamps=formatted_data.retrieval_timestamps,
    )
    logger.info(
        "Email formatted in %.2f seconds (body length: %d chars)",
        time.time() - step_start,
        len(email_body),
    )

    email_subject = f"🌊 LBI Daily Water Report: {today_display}"
    if test:
        email_subject = f"TEST: {email_subject}"

    # Send or display email
    logger.info("[STEP 5/5] %s email...", "Sending" if run_email else "Displaying")
    step_start = time.time()
    try:
        send_or_preview_email(
            context=context,
            run_email=run_email,
            subject=email_subject,
            body=email_body,
            bcc_recipients=bcc_recipients,
        )
        logger.info(
            "%s completed in %.2f seconds",
            "Email sent" if run_email else "Email displayed",
            time.time() - step_start,
        )
    except Exception as e:
        logger.error(
            "Failed to %s email after %.2f seconds: %s",
            "send" if run_email else "display",
            time.time() - step_start,
            e,
            exc_info=True,
        )
        raise

    # Final summary
    total_time = time.time() - workflow_start_time
    logger.info("=" * 80)
    logger.info("Ocean Report workflow completed successfully!")
    logger.info(
        "Total execution time: %.2f seconds (%.1f minutes)", total_time, total_time / 60
    )
    logger.info("=" * 80)
