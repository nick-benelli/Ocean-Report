"""Email template data models."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class EmailTemplateData(BaseModel):
    """
    Data model for email template variables.

    This represents the contract between the workflow
    and the Jinja2 email template. All data should be
    pre-formatted and ready for display.
    """

    # Header
    long_date: str = Field(
        ..., description="Full date string (e.g., 'Monday, June 24, 2026')"
    )

    # Water temperature section
    water_temp: Optional[str] = Field(
        None, description="Formatted water temperature with unit (e.g., '64.4 °F')"
    )

    # Tides section
    tide_info: Optional[str] = Field(
        None, description="Formatted tide information with emoji and times"
    )

    # Wind section
    wind_info: Optional[str] = Field(
        None, description="Formatted wind forecast with bullet points"
    )

    # Footer - station/provider info
    station_name: str = Field(..., description="NOAA station name and ID")
    station_city: str = Field(..., description="Station city name")
    wind_provider: str = Field(
        default="Open-Meteo", description="Wind data provider name"
    )

    # Metadata timestamps
    date_retrieved: str = Field(
        ..., description="Formatted data retrieval timestamp (e.g., 'Jun 24 at 6:22 AM')"
    )
    water_temp_measured_at_date: Optional[str] = Field(
        None, description="Water temp measurement timestamp from NOAA sensor"
    )

    model_config = {"frozen": True}  # Immutable

    def to_template_dict(self) -> dict:
        """
        Convert to dict for Jinja2 template rendering.

        Returns:
            Dictionary with all fields, including None values for template conditionals.
        """
        return self.model_dump(exclude_none=False)


__all__ = ["EmailTemplateData"]
