"""Main entry point for ocean report."""

import logging
import time
from datetime import date, datetime
from pathlib import Path
from typing import Union

from ..application import create_application_context, ApplicationContext
from ..emailer import email_formatter as formatter
from ..emailer import sender as emailer
from ..logger import logger, configure_logger, LogOutput
from ..use_cases import tides as tides_use_case
from ..use_cases import water_temperature as water_temp_use_case
from ..use_cases import wind as wind_use_case
from ..use_cases.email import get_email_recipients


def _write_email_preview(
    subject: str,
    body: str,
    sender_email: str,
    email_recipients: str,
    bcc_recipients: list[str],
) -> Path:
    """Write email preview to files for review.
    
    Creates both HTML and plain text versions in logs/email-previews/
    with timestamped filenames.
    
    Args:
        subject: Email subject line
        body: Email body content
        sender_email: Sender email address
        email_recipients: To: recipients
        bcc_recipients: BCC recipients list
        
    Returns:
        Path to the HTML preview file
    """
    # Create preview directory
    preview_dir = Path("logs/email-previews")
    preview_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = f"email_preview_{timestamp}"
    
    # Prepare email header info
    header_text = (
        f"To: {email_recipients}\n"
        f"BCC: {', '.join(bcc_recipients)}\n"
        f"From: {sender_email}\n\n"
        f"Subject: {subject}\n\n"
    )
    
    # Write plain text version (exact copy of what would be sent)
    txt_file = preview_dir / f"{base_filename}.txt"
    txt_file.write_text(header_text + body, encoding="utf-8")
    
    # Write HTML version (formatted for browser viewing)
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .email-container {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        .email-header {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            font-size: 0.9em;
            color: #666;
        }}
        .email-header div {{
            margin: 5px 0;
        }}
        .email-header strong {{
            color: #333;
        }}
        .email-subject {{
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 20px;
            color: #1a1a1a;
        }}
        .email-body {{
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            line-height: 1.6;
            color: #333;
        }}
        .preview-notice {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 12px;
            margin-bottom: 20px;
            border-radius: 4px;
        }}
        .preview-notice strong {{
            color: #856404;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="preview-notice">
            <strong>📧 Email Preview</strong> — This is how your email will appear to recipients
        </div>
        
        <div class="email-header">
            <div><strong>To:</strong> {email_recipients if email_recipients else "(none)"}</div>
            <div><strong>BCC:</strong> {', '.join(bcc_recipients)}</div>
            <div><strong>From:</strong> {sender_email}</div>
            <div><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        </div>
        
        <div class="email-subject">{subject}</div>
        
        <div class="email-body">{body}</div>
    </div>
</body>
</html>"""
    
    html_file = preview_dir / f"{base_filename}.html"
    html_file.write_text(html_content, encoding="utf-8")
    
    return html_file


def run_report(
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
    bcc_recipients = _get_bcc_recipients(
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
        tide_text, water_temp_text, wind_text, retrieval_times = _fetch_report_data(
            context=context,
            station_id=station_id,
            date_str=today_yyyymmdd,
            latitude=settings.location.latitude,
            longitude=settings.location.longitude,
            beach_facing_deg=settings.location.beach_orientation_degrees,
            forecast_times={"08:00", "12:00", "15:00", "18:00"},
        )
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
        sections=[water_temp_text, tide_text, wind_text],
        retrieval_timestamps=retrieval_times,
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
        _send_email(
            context=context,
            run_email=run_email,
            email_subject=email_subject,
            email_body=email_body,
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


# Helper Functions


def _fetch_report_data(
    *,
    context: ApplicationContext,
    station_id: str,
    date_str: str,
    latitude: float,
    longitude: float,
    beach_facing_deg: float,
    forecast_times: set[str],
) -> tuple[str, str, str, dict]:
    """Fetch and format all report data sections.

    Args:
        context: Application context
        station_id: NOAA station ID
        date_str: Date string in YYYYMMDD format
        latitude: Location latitude
        longitude: Location longitude
        beach_facing_deg: Beach orientation in degrees
        forecast_times: Set of times to fetch wind forecasts for (e.g., {"08:00", "12:00"})

    Returns:
        Tuple of (tide_text, water_temp_text, wind_text, retrieval_timestamps)
    """
    logger.info("  → Fetching tide data from NOAA...")
    fetch_start = time.time()
    daytime_tides, tide_retrieval_time = tides_use_case.get_daytime_tides_for_date(
        context=context,
        station_id=station_id,
        date=date_str,
    )
    tide_text = formatter.format_tide_for_email(daytime_tides)
    logger.info(
        "  ✓ Tide data fetched in %.2f seconds (%d events)",
        time.time() - fetch_start,
        len(daytime_tides),
    )

    logger.info("  → Fetching water temperature from NOAA...")
    fetch_start = time.time()
    water_temp, water_temp_retrieval_time, water_temp_data_time = (
        water_temp_use_case.get_latest_water_temp(
            context=context,
            station_id=station_id,
        )
    )
    water_temp_text = formatter.format_water_temp(water_temp)
    logger.info(
        "  ✓ Water temperature fetched in %.2f seconds (%.1f°F)",
        time.time() - fetch_start,
        water_temp if water_temp else 0.0,
    )

    logger.info("  → Fetching wind forecast from Open-Meteo...")
    fetch_start = time.time()
    wind_forecast, wind_retrieval_time = wind_use_case.get_daily_wind_forecast(
        context=context,
        latitude=latitude,
        longitude=longitude,
        beach_facing_deg=beach_facing_deg,
        times_to_get=forecast_times,
    )
    wind_text = formatter.format_wind_forecast_email(wind_forecast)
    logger.info(
        "  ✓ Wind forecast fetched in %.2f seconds (%d time slots)",
        time.time() - fetch_start,
        len(wind_forecast),
    )

    # Collect all retrieval timestamps
    retrieval_times = {
        "tides": tide_retrieval_time,
        "water_temp": water_temp_retrieval_time,
        "water_temp_data_time": water_temp_data_time,
        "wind": wind_retrieval_time,
    }

    return tide_text, water_temp_text, wind_text, retrieval_times


def _validate_email_config(sender: str | None, password: str | None) -> None:
    """Validate that required email credentials are configured.

    Args:
        sender: Email sender address
        password: Email password

    Raises:
        ValueError: If required credentials are missing
    """
    if not sender:
        raise ValueError(
            "Email sender address is not configured. "
            "Set EMAIL_SENDER environment variable or email.sender in config."
        )
    if not password:
        raise ValueError(
            "Email password is not configured. "
            "Set EMAIL_PASSWORD environment variable or email.password in config."
        )


def _get_bcc_recipients(
    *, test: bool, use_url: bool, fallback_recipients: str
) -> list[str]:
    """Get and parse BCC recipient list from URL or config.

    Args:
        test: Whether to use test recipients
        use_url: If True, fetch from URL; if False, use fallback
        fallback_recipients: Comma-separated fallback recipient string

    Returns:
        List of cleaned email addresses
    """
    if use_url:
        logger.debug("  → Fetching recipients from URL (test=%s)", test)
        fetch_start = time.time()
        recipients_str = get_email_recipients(test_recips=test)
        logger.debug(
            "  ✓ Recipients fetched from URL in %.2f seconds", time.time() - fetch_start
        )
    else:
        logger.debug("  → Using fallback recipients from config")
        recipients_str = fallback_recipients or ""

    return [email.strip() for email in recipients_str.split(",") if email.strip()]


def _send_email(
    *,
    context: ApplicationContext,
    run_email: bool,
    email_subject: str,
    email_body: str,
    bcc_recipients: list[str],
) -> None:
    """Send or print email report.

    Args:
        context: Application context containing config
        run_email: If True, send via SMTP; if False, print to console
        email_subject: Email subject line
        email_body: Email body content
        bcc_recipients: List of BCC recipient email addresses
    """
    email_recipients = context.config.email.recipients or ""
    sender_email = context.config.email.sender
    email_password = context.config.email.password

    if run_email:
        logger.info("  → Validating email configuration...")
        _validate_email_config(sender_email, email_password)
        logger.debug("  ✓ Email configuration validated")

        logger.info(
            "  → Connecting to SMTP and sending to %d recipients...",
            len(bcc_recipients),
        )
        logger.debug("  → Sender: %s", sender_email)
        send_start = time.time()
        emailer.send_email(
            subject=email_subject,
            body=email_body,
            sender_email=sender_email,
            email_password=email_password,
            recipients=emailer.EmailRecipients(
                to_email=email_recipients,
                bcc_list=bcc_recipients,
            ),
            smtp_server=context.config.email.smtp_server,
            smtp_port=context.config.email.smtp_port,
        )
        logger.info(
            "  ✓ Email sent successfully via SMTP in %.2f seconds",
            time.time() - send_start,
        )
    else:
        logger.info("  → Displaying email content (NOT sending):")
        print(
            f"\nTo: {email_recipients}\n"
            f"BCC: {', '.join(bcc_recipients)}\n"
            f"From: {sender_email}\n\n"
            f"Subject: {email_subject}\n\n"
            f"{email_body}"
        )
        logger.info("Email content printed to console.")
        
        # Write email preview files
        logger.info("  → Writing email preview files...")
        html_file = _write_email_preview(
            subject=email_subject,
            body=email_body,
            sender_email=sender_email,
            email_recipients=email_recipients,
            bcc_recipients=bcc_recipients,
        )
        logger.info(f"  ✓ Email preview saved:")
        logger.info(f"    • HTML: {html_file}")
        logger.info(f"    • Text: {html_file.with_suffix('.txt')}")
        print(f"\n📁 Email preview files saved:")
        print(f"   • Open in browser: open {html_file}")
        print(f"   • View text: cat {html_file.with_suffix('.txt')}")
