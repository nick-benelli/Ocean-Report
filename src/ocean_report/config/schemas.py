"""Pydantic models for the application config."""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

_ENV_PLACEHOLDER_PATTERN = re.compile(r"^\$\{[^}]+\}$")


def _is_unresolved_env_placeholder(value: Any) -> bool:
    return isinstance(value, str) and bool(_ENV_PLACEHOLDER_PATTERN.fullmatch(value))


class StrictModel(BaseModel):
    """Base model that rejects unknown config keys."""

    model_config = ConfigDict(extra="forbid")


class NoaaConfig(StrictModel):
    """NOAA station configuration."""

    station_id: str = "8534720"
    buoy_id: str = "44091"

    @field_validator("station_id", "buoy_id", mode="before")
    @classmethod
    def apply_default_station_values(cls, value: Any, info: Any) -> str:
        defaults = {
            "station_id": "8534720",
            "buoy_id": "44091",
        }
        if value is None or _is_unresolved_env_placeholder(value):
            return defaults[info.field_name]
        return str(value)


class RecipientUrlsConfig(StrictModel):
    """Remote recipient list sources."""

    main: str = ""
    test: str = ""
    offseason: str = ""

    @field_validator("main", "test", "offseason", mode="before")
    @classmethod
    def normalize_urls(cls, value: Any) -> str:
        if value is None or _is_unresolved_env_placeholder(value):
            return ""
        return str(value)


class EmailConfig(StrictModel):
    """SMTP and recipient configuration."""

    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender: str | None = None
    password: str | None = None
    recipients: str | None = None
    test_recipients: str | None = None
    recipient_urls: RecipientUrlsConfig = Field(default_factory=RecipientUrlsConfig)

    @field_validator("smtp_server", mode="before")
    @classmethod
    def normalize_smtp_server(cls, value: Any) -> str:
        if value is None or _is_unresolved_env_placeholder(value):
            return "smtp.gmail.com"
        return str(value)

    @field_validator("smtp_port", mode="before")
    @classmethod
    def normalize_smtp_port(cls, value: Any) -> int:
        if value is None or _is_unresolved_env_placeholder(value):
            return 587
        return int(value)

    @field_validator(
        "sender",
        "password",
        "recipients",
        "test_recipients",
        mode="before",
    )
    @classmethod
    def normalize_optional_strings(cls, value: Any) -> str | None:
        if value is None or _is_unresolved_env_placeholder(value):
            return None
        return str(value)


class LocationConfig(StrictModel):
    """Beach location and orientation settings."""

    longitude: float = -74.2
    latitude: float = 39.5
    beach_orientation_degrees: float = 140

    @field_validator("longitude", "latitude", "beach_orientation_degrees", mode="before")
    @classmethod
    def normalize_float_defaults(cls, value: Any, info: Any) -> float:
        defaults = {
            "longitude": -74.2,
            "latitude": 39.5,
            "beach_orientation_degrees": 140,
        }
        if value is None or _is_unresolved_env_placeholder(value):
            return defaults[info.field_name]
        return float(value)


class SummerConfig(StrictModel):
    """Season boundary offsets."""

    memorial_day_offset: int = -4
    labor_day_offset: int = 7

    @field_validator("memorial_day_offset", "labor_day_offset", mode="before")
    @classmethod
    def normalize_int_defaults(cls, value: Any, info: Any) -> int:
        defaults = {
            "memorial_day_offset": -4,
            "labor_day_offset": 7,
        }
        if value is None or _is_unresolved_env_placeholder(value):
            return defaults[info.field_name]
        return int(value)


class OceanReportConfig(StrictModel):
    """Validated config root model."""

    noaa: NoaaConfig = Field(default_factory=NoaaConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)
    location: LocationConfig = Field(default_factory=LocationConfig)
    summer: SummerConfig = Field(default_factory=SummerConfig)
