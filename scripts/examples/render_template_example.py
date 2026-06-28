"""
Example script demonstrating how to use the new template rendering system.

This shows the end-to-end flow from creating EmailTemplateData to rendering.
"""

from ocean_report.config import get_settings
from ocean_report.emailer.template_renderer import render_email_template
from ocean_report.models.email import EmailTemplateData


def example_render_email():
    """Example: Create template data and render email."""

    # Load config to get station info
    config = get_settings()

    # Create the template data model
    email_data = EmailTemplateData(
        # Header
        long_date="Monday, June 24, 2026",
        # Water temperature
        water_temp="64.4 °F",
        # Tides
        tide_info=("⬇️ Low Tide at 8:23 AM — 0.3 ft\n⬆️ High Tide at 2:46 PM — 4.1 ft"),
        # Wind forecast
        wind_info=(
            "•  8 AM:  4.8 mph ESE (108.0°) → Cross/Onshore\n"
            "• 12 PM:  8.9 mph SE  (128.0°) → Onshore\n"
            "•  3 PM: 11.1 mph SSE (151.0°) → Onshore\n"
            "•  6 PM:  8.9 mph S   (172.0°) → Cross/Onshore"
        ),
        # Footer metadata
        station_name=config.reporting.station_name,
        station_city=config.reporting.station_city,
        wind_provider=config.reporting.wind_provider,
        date_retrieved="Jun 24 at 6:22 AM",
        water_temp_measured_at_date="2026-06-24 10:12",
    )

    # Render the template
    email_body = render_email_template(email_data)

    print("=" * 60)
    print("RENDERED EMAIL BODY:")
    print("=" * 60)
    print(email_body)
    print("=" * 60)

    return email_body


def example_with_missing_data():
    """Example: Handle missing data gracefully."""

    config = get_settings()

    # Create template data with some missing values
    email_data = EmailTemplateData(
        long_date="Monday, June 24, 2026",
        water_temp=None,  # Missing!
        tide_info="⬇️ Low Tide at 8:23 AM — 0.3 ft",
        wind_info=None,  # Missing!
        station_name=config.reporting.station_name,
        station_city=config.reporting.station_city,
        wind_provider=config.reporting.wind_provider,
        date_retrieved="Jun 24 at 6:22 AM",
        water_temp_measured_at_date=None,
    )

    # Template will show "Temporarily unavailable" for missing sections
    email_body = render_email_template(email_data)

    print("\nEmail with missing data:")
    print(email_body)


if __name__ == "__main__":
    # Run examples
    example_render_email()
    print("\n")
    example_with_missing_data()
