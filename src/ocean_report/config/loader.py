"""Configuration loading and validation for ocean report.

Provides a clean separation between path resolution, raw config loading,
validation, and caching. Uses pathlib for modern path handling.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from string import Template
from typing import Any

import yaml
from dotenv import load_dotenv

from .. import constants
from .schemas import AppConfig


def resolve_config_path(path: str | Path | None = None) -> Path:
    """Resolve config path to absolute Path, defaulting to project config."""
    candidate = path if path is not None else constants.CONFIG_PATH
    return Path(candidate).expanduser().resolve()


def load_raw_config(path: str | Path | None = None) -> dict[str, Any]:
    """Load YAML config with ${VAR} substitution from environment."""
    load_dotenv()

    config_path = resolve_config_path(path)
    content = config_path.read_text(encoding="utf-8")
    substituted = Template(content).safe_substitute(os.environ)
    return yaml.safe_load(substituted) or {}


def load_app_config(path: str | Path | None = None) -> AppConfig:
    """Load and validate config from disk (uncached)."""
    raw_config = load_raw_config(path)
    return AppConfig.model_validate(raw_config)


def get_settings(path: str | Path | None = None) -> AppConfig:
    """Return cached validated application settings."""
    resolved = resolve_config_path(path)
    return _cached_load(resolved)


def get_config_dict(path: str | Path | None = None) -> dict[str, Any]:
    """Get cached config as a dictionary."""
    return get_settings(path).model_dump(exclude_none=True)


def clear_config_cache() -> None:
    """Clear the cache, forcing next get_settings() to reload from disk."""
    _cached_load.cache_clear()


def reload_config(path: str | Path | None = None) -> AppConfig:
    """Clear cache and reload config from disk."""
    clear_config_cache()
    return get_settings(path)


@lru_cache(maxsize=None)
def _cached_load(resolved_path: Path) -> AppConfig:
    """Internal cached loader."""
    return load_app_config(resolved_path)


__all__ = [
    "get_settings",
    "load_app_config",
    "load_raw_config",
    "clear_config_cache",
    "reload_config",
    "resolve_config_path",
    "get_config_dict",
]
