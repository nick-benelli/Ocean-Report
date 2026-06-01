"""Configuration loading helpers for ocean report."""

from __future__ import annotations

from functools import lru_cache
import os
from os import PathLike
from string import Template
from typing import Any

import yaml
from dotenv import load_dotenv

from .. import constants
from .schemas import OceanReportConfig


def _resolve_config_path(path: str | PathLike[str] | None = None) -> str:
    """Resolve the config path, defaulting to the project config file."""

    return str(path or constants.CONFIG_PATH)


def load_config_with_env_substitution(
    path: str | PathLike[str] | None = None,
) -> dict[str, Any]:
    """Load YAML config and substitute environment variables."""

    load_dotenv()
    resolved_path = _resolve_config_path(path)

    with open(resolved_path, encoding="utf-8") as config_file:
        content = config_file.read()

    substituted = Template(content).safe_substitute(os.environ)
    return yaml.safe_load(substituted) or {}


def load_settings(path: str | PathLike[str] | None = None) -> OceanReportConfig:
    """Load and validate config data without using the cache."""

    raw_config = load_config_with_env_substitution(path)
    return OceanReportConfig.model_validate(raw_config)


@lru_cache(maxsize=None)
def _get_settings_cached(resolved_path: str) -> OceanReportConfig:
    """Cache validated settings by resolved config path."""

    return load_settings(resolved_path)


def get_settings(path: str | PathLike[str] | None = None) -> OceanReportConfig:
    """Return cached validated settings for the requested config path."""

    return _get_settings_cached(_resolve_config_path(path))


def get_config(path: str | PathLike[str] | None = None) -> dict[str, Any]:
    """Return the validated config as a plain dict."""

    return get_settings(path).model_dump(exclude_none=True)


def reload_settings(path: str | PathLike[str] | None = None) -> OceanReportConfig:
    """Clear the settings cache and reload the requested config path."""

    _get_settings_cached.cache_clear()
    return get_settings(path)


__all__ = [
    "get_config",
    "get_settings",
    "load_config_with_env_substitution",
    "load_settings",
    "reload_settings",
]
