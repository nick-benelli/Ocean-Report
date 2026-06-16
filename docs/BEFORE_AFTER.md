# Config Loader: Before & After

## The Transformation

### Before
❌ **350+ lines** of over-engineered code  
❌ Extensive docstrings for "library-like" API  
❌ Legacy aliases for backward compatibility  
❌ Module-level side effects (`load_dotenv()` at import)  
❌ Took several minutes to understand  

### After
✅ **80 lines** of focused, clean code  
✅ Concise docstrings for application code  
✅ No aliases - one clear way per operation  
✅ No import-time side effects  
✅ Understandable in 30 seconds  

---

## Side-by-Side Comparison

### Module Size
```
Before: 350+ lines  →  After: 80 lines  (77% reduction)
```

### Docstring Example

**Before:**
```python
def load_config(path: str | Path | None = None) -> AppConfig:
    """Load and validate configuration from disk (uncached).
    
    This function always reads from disk, performs environment variable
    substitution, and validates the configuration against the AppConfig schema.
    Changes to the config file or environment variables will be reflected on
    each call.
    
    For cached access (recommended in production), use get_settings() instead.
    
    Args:
        path: Path to the configuration file.
    
    Returns:
        Validated AppConfig instance.
    
    Raises:
        FileNotFoundError: If the config file doesn't exist.
        yaml.YAMLError: If the YAML is malformed.
        pydantic.ValidationError: If the configuration doesn't match the schema.
    
    Examples:
        >>> config = load_config()
        >>> config.email.smtp_server
        'smtp.gmail.com'
        >>> config.noaa.station_id
        '8534720'
    """
```

**After:**
```python
def load_app_config(path: str | Path | None = None) -> AppConfig:
    """Load and validate config from disk (uncached)."""
```

### Side Effects

**Before:**
```python
# At module level - runs on import
load_dotenv()

def load_config_with_env_substitution(...):
    # Already loaded above
    ...
```

**After:**
```python
# No module-level side effects

def load_raw_config(...):
    load_dotenv()  # Only when actually needed
    ...
```

### API Surface

**Before:**
```python
__all__ = [
    # Primary API
    "get_settings",
    "load_config",
    "load_raw_config",
    "clear_config_cache",
    "reload_config",
    "resolve_config_path",
    "get_config_dict",
    # Legacy aliases (backward compatibility)
    "get_config",
    "get_cached_settings",
    "load_settings",
    "load_config_with_env_substitution",
    "get_config_path",
    "reload_settings",
]
# 13 functions (6 are duplicates)
```

**After:**
```python
__all__ = [
    "get_settings",
    "load_app_config",
    "load_raw_config",
    "clear_config_cache",
    "reload_config",
    "resolve_config_path",
    "get_config_dict",
]
# 7 functions (all unique)
```

---

## What We Kept

✅ **Clear separation of concerns**
```
resolve_config_path() → load_raw_config() → load_app_config() → get_settings()
```

✅ **Modern pathlib usage**
```python
Path(path).expanduser().resolve()  # vs os.path.abspath(os.path.expanduser(str(path)))
```

✅ **Type safety**
```python
def get_settings(path: str | Path | None = None) -> AppConfig:
```

✅ **Simple caching**
```python
@lru_cache(maxsize=None)
def _cached_load(resolved_path: Path) -> AppConfig:
```

---

## What We Removed

❌ **200+ lines of docstring prose**  
❌ **6 legacy alias functions**  
❌ **Section header comments**  
❌ **Excessive examples in docstrings**  
❌ **Over-documentation**  

---

## The Result

### loader.py: 80 lines
```python
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
```

---

## Grade Progression

| Aspect | Original | First Refactor | Final |
|--------|----------|----------------|-------|
| **Architecture** | B+ | A- | **A** |
| **Simplicity** | B | C+ | **A** |
| **Maintainability** | B+ | B | **A** |
| **Clarity** | B | B+ | **A** |
| **Lines of Code** | ~80 | 350+ | **80** |

---

**Final verdict:** Clean, focused, production-ready configuration loading. Easy to understand, easy to test, easy to maintain. 🎯
