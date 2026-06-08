"""Configuration loading helpers for ocean report."""

from __future__ import annotations

import os
from functools import lru_cache
from os import PathLike
from string import Template
from typing import Any

import yaml
from dotenv import load_dotenv

from .. import constants
from .schemas import AppConfig


def get_config_path(path: str | PathLike[str] | None = None) -> str:
    """Return the absolute config path, defaulting to the project config file."""

    candidate = str(path or constants.CONFIG_PATH)
    return os.path.abspath(os.path.expanduser(candidate))


def load_config_with_env_substitution(
    path: str | PathLike[str] | None = None,
) -> dict[str, Any]:
    """Read YAML config and apply ${VAR} substitutions from environment variables."""

    load_dotenv()
    resolved_path = get_config_path(path)

    with open(resolved_path, encoding="utf-8") as config_file:
        content = config_file.read()

    substituted = Template(content).safe_substitute(os.environ)
    return yaml.safe_load(substituted) or {}


def load_settings(path: str | PathLike[str] | None = None) -> AppConfig:
    """Load and validate settings directly from disk (no cache)."""

    raw_config = load_config_with_env_substitution(path)
    return AppConfig.model_validate(raw_config)


def get_settings(path: str | PathLike[str] | None = None) -> AppConfig:
    """Return cached validated settings for the requested config path."""

    resolved_path = get_config_path(path)
    return _load_settings_cached(resolved_path)


def get_config(path: str | PathLike[str] | None = None) -> dict[str, Any]:
    """Return validated settings as a plain dictionary."""

    return get_settings(path).model_dump(exclude_none=True)


def reload_settings(path: str | PathLike[str] | None = None) -> AppConfig:
    """Clear the settings cache and reload validated settings from disk."""

    _load_settings_cached.cache_clear()
    return get_settings(path)


@lru_cache(maxsize=None)
def _load_settings_cached(resolved_path: str) -> AppConfig:
    """Load and cache validated settings by resolved config path."""

    return load_settings(resolved_path)



__all__ = [
    "get_config_path",
    "get_config",
    "get_settings",
    "load_config_with_env_substitution",
    "load_settings",
    "reload_settings",
]
