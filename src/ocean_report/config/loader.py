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
from dotenv import load_dotenv, find_dotenv

from .schemas import AppConfig


def _get_default_config_path() -> Path:
    """Find config path with production-ready fallback strategy.

    Resolution order:
    1. OCEAN_REPORT_CONFIG environment variable
    2. configs/config.yaml relative to project root (pyproject.toml location)
    3. ~/.config/ocean-report/config.yaml (user config directory)

    Returns:
        Resolved config path

    Raises:
        FileNotFoundError: If no config file found in any location
    """
    # Load .env file first so OCEAN_REPORT_CONFIG is available
    load_dotenv()

    # 1. Check environment variable (highest priority)
    env_config = os.getenv("OCEAN_REPORT_CONFIG")
    if env_config:
        path = Path(env_config).expanduser().resolve()
        if path.exists():
            return path
        raise FileNotFoundError(
            f"Config path from OCEAN_REPORT_CONFIG not found: {path}"
        )

    # 2. Check project-relative path (works for repo checkouts, GitHub Actions)
    pyproject_path = find_dotenv("pyproject.toml")
    if pyproject_path:
        project_config = Path(pyproject_path).parent / "configs" / "config.yaml"
        if project_config.exists():
            return project_config

    # 3. Check user config directory (XDG-style for installed packages)
    user_config = Path.home() / ".config" / "ocean-report" / "config.yaml"
    if user_config.exists():
        return user_config

    # 4. Nothing found - provide helpful error
    project_str = (
        str(project_config)
        if pyproject_path
        else "configs/config.yaml (no pyproject.toml found)"
    )
    raise FileNotFoundError(
        f"No config file found. Tried:\n"
        f"  - OCEAN_REPORT_CONFIG env var\n"
        f"  - {project_str}\n"
        f"  - {user_config}\n"
        f"Set OCEAN_REPORT_CONFIG=/path/to/config.yaml or place config "
        f"in one of the above locations."
    )


def resolve_config_path(path: str | Path | None = None) -> Path:
    """Resolve config path to absolute Path.

    Args:
        path: Optional explicit config path. If None, uses default resolution.

    Returns:
        Resolved absolute Path to config file
    """
    if path is not None:
        return Path(path).expanduser().resolve()
    return _get_default_config_path()


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
