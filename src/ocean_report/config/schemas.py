"""Pydantic models for the application config."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

_ENV_PLACEHOLDER_PATTERN = re.compile(r"^\$\{[^}]+\}$")


def _is_unresolved_env_placeholder(value: Any) -> bool:
    return isinstance(value, str) and bool(_ENV_PLACEHOLDER_PATTERN.fullmatch(value))


def _field_default(model_cls: type[BaseModel], field_name: str) -> Any:
    """Return a model field default in a type-checker-friendly way."""

    return model_cls.__pydantic_fields__[field_name].default


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
        """
        If the value is None or an unresolved env placeholder, return the default.
        This allows users to set env vars to empty or leave them unset to use defaults.
        """
        if value is None or _is_unresolved_env_placeholder(value):
            return _field_default(cls, info.field_name)
        return str(value)


class RecipientUrlsConfig(StrictModel):
    """Remote recipient list sources."""

    main: str = ""
    test: str = ""
    offseason: str = ""

    @field_validator("main", "test", "offseason", mode="before")
    @classmethod
    def normalize_urls(cls, value: Any) -> str:
        """
        If the value is None or an unresolved env placeholder, return an empty string.
        This allows users to set env vars to empty or leave them unset to disable URL sources.
        """
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
    use_recipient_url: bool = True

    @field_validator("smtp_server", mode="before")
    @classmethod
    def normalize_smtp_server(cls, value: Any) -> str:
        """
        If the value is None or an unresolved env placeholder, return the default.
        This allows users to set env vars to empty or leave them unset to use defaults.
        """
        if value is None or _is_unresolved_env_placeholder(value):
            return _field_default(cls, "smtp_server")
        return str(value)

    @field_validator("smtp_port", mode="before")
    @classmethod
    def normalize_smtp_port(cls, value: Any) -> int:
        """
        If the value is None or an unresolved env placeholder, return the default.
        This allows users to set env vars to empty or leave them unset to use defaults.
        """
        if value is None or _is_unresolved_env_placeholder(value):
            return _field_default(cls, "smtp_port")
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
        """
        If the value is None or an unresolved env placeholder, return None.
        This allows users to set env vars to empty or leave them unset to disable optional strings.
        """
        if value is None or _is_unresolved_env_placeholder(value):
            return None
        return str(value)

    @field_validator("use_recipient_url", mode="before")
    @classmethod
    def normalize_use_recipient_url(cls, value: Any) -> bool:
        """
        If the value is None or an unresolved env placeholder, return the default.
        This allows users to set env vars to empty or leave them unset to use defaults.
        """
        if value is None or _is_unresolved_env_placeholder(value):
            return _field_default(cls, "use_recipient_url")
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1", "yes", "on"}:
                return True
            if normalized in {"false", "0", "no", "off"}:
                return False
        return bool(value)


class LocationConfig(StrictModel):
    """Beach location and orientation settings."""

    longitude: float = -74.2
    latitude: float = 39.5
    beach_orientation_degrees: float = 140

    @field_validator(
        "longitude", "latitude", "beach_orientation_degrees", mode="before"
    )
    @classmethod
    def normalize_float_defaults(cls, value: Any, info: Any) -> float:
        """
        If the value is None or an unresolved env placeholder, return the default.
        This allows users to set env vars to empty or leave them unset to use defaults.
        """
        if value is None or _is_unresolved_env_placeholder(value):
            return _field_default(cls, info.field_name)
        return float(value)


class SummerConfig(StrictModel):
    """Season boundary offsets."""

    memorial_day_offset: int = -4
    labor_day_offset: int = 7

    @field_validator("memorial_day_offset", "labor_day_offset", mode="before")
    @classmethod
    def normalize_int_defaults(cls, value: Any, info: Any) -> int:
        """
        If the value is None or an unresolved env placeholder, return the default.
        This allows users to set env vars to empty or leave them unset to use defaults.
        """
        if value is None or _is_unresolved_env_placeholder(value):
            return _field_default(cls, info.field_name)
        return int(value)


class LoggingConfig(StrictModel):
    """Logging configuration."""

    output: str = "console"  # Options: console, file, both
    file_path: str = "logs/ocean_report.log"
    level: str = "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @field_validator("output", mode="before")
    @classmethod
    def normalize_output(cls, value: Any) -> str:
        """Normalize logging output option."""
        if value is None or _is_unresolved_env_placeholder(value):
            return _field_default(cls, "output")
        output = str(value).lower()
        if output not in {"console", "file", "both"}:
            raise ValueError(
                f"logging.output must be 'console', 'file', or 'both', got: {output}"
            )
        return output

    @field_validator("file_path", mode="before")
    @classmethod
    def normalize_file_path(cls, value: Any) -> str:
        """Normalize log file path."""
        if value is None or _is_unresolved_env_placeholder(value):
            return _field_default(cls, "file_path")
        return str(value)

    @field_validator("level", mode="before")
    @classmethod
    def normalize_level(cls, value: Any) -> str:
        """Normalize logging level."""
        if value is None or _is_unresolved_env_placeholder(value):
            return _field_default(cls, "level")
        level = str(value).upper()
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if level not in valid_levels:
            raise ValueError(
                f"logging.level must be one of {valid_levels}, got: {level}"
            )
        return level

    @field_validator("format", mode="before")
    @classmethod
    def normalize_format(cls, value: Any) -> str:
        """Normalize log format string."""
        if value is None or _is_unresolved_env_placeholder(value):
            return _field_default(cls, "format")
        return str(value)


class ApiConfig(StrictModel):
    """HTTP client behavior configuration."""

    verify_ssl: bool = True
    timeout_seconds: float = 10.0
    retry_insecure_on_ssl_error: bool = True
    max_retries: int = 3
    backoff_seconds: float = 0.8

    @field_validator("verify_ssl", "retry_insecure_on_ssl_error", mode="before")
    @classmethod
    def normalize_bool_defaults(cls, value: Any, info: Any) -> bool:
        """
        If the value is None or an unresolved env placeholder, return the default.
        This allows users to set env vars to empty or leave them unset to use defaults.
        """
        if value is None or _is_unresolved_env_placeholder(value):
            return _field_default(cls, info.field_name)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1", "yes", "on"}:
                return True
            if normalized in {"false", "0", "no", "off"}:
                return False
        return bool(value)

    @field_validator("timeout_seconds", mode="before")
    @classmethod
    def normalize_timeout(cls, value: Any) -> float:
        """
        If the value is None or an unresolved env placeholder, return the default.
        This allows users to set env vars to empty or leave them unset to use defaults.
        """
        if value is None or _is_unresolved_env_placeholder(value):
            return _field_default(cls, "timeout_seconds")
        timeout = float(value)
        if timeout <= 0:
            raise ValueError("api.timeout_seconds must be greater than zero")
        return timeout

    @field_validator("max_retries", mode="before")
    @classmethod
    def normalize_max_retries(cls, value: Any) -> int:
        """
        If the value is None or an unresolved env placeholder, return the default.
        This allows users to set env vars to empty or leave them unset to use defaults.
        """
        if value is None or _is_unresolved_env_placeholder(value):
            return _field_default(cls, "max_retries")
        retries = int(value)
        if retries < 0:
            raise ValueError("api.max_retries must be greater than or equal to zero")
        return retries

    @field_validator("backoff_seconds", mode="before")
    @classmethod
    def normalize_backoff_seconds(cls, value: Any) -> float:
        """
        If the value is None or an unresolved env placeholder, return the default.
        This allows users to set env vars to empty or leave them unset to use defaults.
        """
        if value is None or _is_unresolved_env_placeholder(value):
            return _field_default(cls, "backoff_seconds")
        backoff = float(value)
        if backoff < 0:
            raise ValueError(
                "api.backoff_seconds must be greater than or equal to zero"
            )
        return backoff


class ReportingConfig(StrictModel):
    """Report content configuration."""

    template_path: str = "templates/ocean-report-email-v2.j2"
    station_name: str = "NOAA Atlantic City (8534720)"
    station_city: str = "Atlantic City, NJ"
    wind_provider: str = "Open-Meteo"

    @field_validator(
        "template_path", "station_name", "station_city", "wind_provider", mode="before"
    )
    @classmethod
    def normalize_string_defaults(cls, value: Any, info: Any) -> str:
        """
        If the value is None or an unresolved env placeholder, return the default.
        This allows users to set env vars to empty or leave them unset to use defaults.
        """
        if value is None or _is_unresolved_env_placeholder(value):
            return _field_default(cls, info.field_name)
        return str(value)

    def resolve_template_path(self, project_root: Path) -> Path:
        """
        Resolve template_path relative to project root.

        Args:
            project_root: Root directory of the project (typically where pyproject.toml lives)

        Returns:
            Absolute path to the template file
        """
        path = Path(self.template_path)
        if path.is_absolute():
            return path
        return (project_root / path).resolve()


class AppConfig(StrictModel):
    """Validated config root model."""

    noaa: NoaaConfig = Field(default_factory=NoaaConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)
    location: LocationConfig = Field(default_factory=LocationConfig)
    summer: SummerConfig = Field(default_factory=SummerConfig)
    api: ApiConfig = Field(default_factory=ApiConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    reporting: ReportingConfig = Field(default_factory=ReportingConfig)
