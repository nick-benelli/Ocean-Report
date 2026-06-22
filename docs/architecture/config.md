# Config Component

**Purpose**: Configuration loading with environment variable substitution, type validation, and production-ready path resolution.

**Location**: `src/ocean_report/config/`

---

## Overview

The Config component handles all application configuration—from finding the config file to validating every setting. It provides type-safe access to configuration throughout the application.

### What It Does

**For Non-Technical Readers:**

Think of configuration like a settings file for the application. It contains things like:
- Which weather stations to use
- Email server settings
- Where the beach is located
- How long to wait for API responses

The Config component:
1. **Finds** the right configuration file
2. **Loads** settings from the file
3. **Fills in** secrets from environment variables (like passwords)
4. **Validates** that all settings are correct
5. **Provides** type-safe access to settings

**For Technical Readers:**

- YAML-based configuration with `${VAR}` substitution from environment variables
- Pydantic-based validation with custom field validators
- Production-ready path resolution with XDG-style fallbacks
- Cached configuration with explicit reload support
- Strict schema validation (extra fields forbidden)

---

## Architecture

### File Structure

```
config/
├── __init__.py     # Public exports
├── loader.py       # Path resolution, loading, caching
└── schemas.py      # Pydantic models for validation
```

### Component Layers

```
┌────────────────────────────────────────┐
│       get_settings() (cached)          │  ← High-level: cached config
├────────────────────────────────────────┤
│     load_app_config() (validated)      │  ← Mid-level: load + validate
├────────────────────────────────────────┤
│    load_raw_config() (with ${VAR})     │  ← Low-level: YAML + env substitution
├────────────────────────────────────────┤
│      resolve_config_path()             │  ← Path resolution
└────────────────────────────────────────┘
```

---

## Core Components

### 1. Path Resolution (`loader.py`)

**Problem**: Where is the config file?

**Solution**: Fallback strategy with clear priorities.

#### `resolve_config_path(path=None) → Path`

**Resolution Order** (highest priority first):

1. **Explicit parameter**: `resolve_config_path("custom.yaml")`
2. **`OCEAN_REPORT_CONFIG` environment variable**
3. **Project-relative**: `configs/config.yaml` (relative to `pyproject.toml`)
4. **User config directory**: `~/.config/ocean-report/config.yaml` (XDG-style)

**Example**:
```python
from ocean_report.config.loader import resolve_config_path

# Use default resolution
path = resolve_config_path()
# → /path/to/project/configs/config.yaml

# Explicit path
path = resolve_config_path("test/config.yaml")
# → /absolute/path/to/test/config.yaml

# Via environment variable
os.environ["OCEAN_REPORT_CONFIG"] = "/opt/ocean-report/config.yaml"
path = resolve_config_path()
# → /opt/ocean-report/config.yaml
```

**Error Handling**:
```python
try:
    path = resolve_config_path()
except FileNotFoundError as e:
    print(e)
    # Output: No config file found. Tried:
    #   - OCEAN_REPORT_CONFIG env var
    #   - /path/to/project/configs/config.yaml
    #   - /home/user/.config/ocean-report/config.yaml
```

---

### 2. Raw Loading (`loader.py`)

#### `load_raw_config(path=None) → dict`

**What It Does**:
1. Resolves config path (using `resolve_config_path()`)
2. Reads YAML file content
3. Substitutes `${VAR}` placeholders with environment variables
4. Returns raw dictionary (no validation yet)

**Environment Variable Substitution**:

`config.yaml`:
```yaml
email:
  sender: ${EMAIL_ADDRESS}
  password: ${EMAIL_PASSWORD}
  smtp_server: smtp.gmail.com  # No substitution needed
```

Environment:
```bash
export EMAIL_ADDRESS="surf@example.com"
export EMAIL_PASSWORD="secret123"
```

Result:
```python
config = load_raw_config()
# {
#     "email": {
#         "sender": "surf@example.com",
#         "password": "secret123",
#         "smtp_server": "smtp.gmail.com"
#     }
# }
```

**Safe Substitution**: If an environment variable is missing, the placeholder is left as-is:
```yaml
email:
  sender: ${MISSING_VAR}  # ENV var not set
```

Result:
```python
# {"email": {"sender": "${MISSING_VAR}"}}
# Pydantic validation will catch this later
```

---

### 3. Validated Loading (`loader.py`)

#### `load_app_config(path=None) → AppConfig`

**What It Does**:
1. Calls `load_raw_config()` to get dictionary
2. Validates dictionary against Pydantic schema
3. Returns type-safe `AppConfig` instance

**Example**:
```python
from ocean_report.config.loader import load_app_config

config = load_app_config()

# Type-safe access
station_id: str = config.noaa.station_id
latitude: float = config.location.latitude
timeout: float = config.api.timeout
```

**Validation Errors**:
```python
# config.yaml has invalid data
api:
  timeout: "not_a_number"

try:
    config = load_app_config()
except ValidationError as e:
    print(e)
    # Shows which field is invalid and why
```

---

### 4. Cached Loading (`loader.py`)

#### `get_settings() → AppConfig`

**What It Does**: Same as `load_app_config()` but **caches** the result.

**Why Cache?**

Loading config involves:
- File I/O (slow)
- YAML parsing (slow)
- Validation (moderate)

If 20 modules import config on startup, we'd load it 20 times. Caching makes it load once.

**Usage**:
```python
from ocean_report.config.loader import get_settings

# First call: loads from file
config1 = get_settings()  # 100ms

# Subsequent calls: returns cached instance
config2 = get_settings()  # <1ms
config3 = get_settings()  # <1ms

assert config1 is config2 is config3  # Same object
```

#### `reload_settings() → AppConfig`

**What It Does**: Clears cache and reloads config from file.

**When to Use**:
- Configuration changed and you need to pick up changes
- Testing: reset state between test cases

**Example**:
```python
from ocean_report.config.loader import get_settings, reload_settings

config1 = get_settings()
print(config1.noaa.station_id)  # "8534720"

# Modify config file externally
# (or change environment variables)

config2 = reload_settings()  # Clears cache, reloads from file
print(config2.noaa.station_id)  # "NEW_STATION"
```

---

## Configuration Schema

### Schema Overview (`schemas.py`)

All config validation is done with Pydantic models:

```python
class AppConfig(StrictModel):
    """Root configuration model."""
    noaa: NoaaConfig
    email: EmailConfig
    location: LocationConfig
    summer: SummerConfig
    api: ApiConfig
    logging: LoggingConfig
```

**Key Feature**: `StrictModel` base class forbids extra fields:

```yaml
# ❌ This will raise ValidationError
email:
  sender: test@example.com
  typo_password: secret  # Should be "password", not "typo_password"
```

**Why?** Catches typos and prevents silent config errors.

---

### Schema Sections

#### 1. NoaaConfig

```python
class NoaaConfig(StrictModel):
    station_id: str = "8534720"  # Atlantic City, NJ
    buoy_id: str = "44091"        # Delaware Bay buoy
```

**YAML**:
```yaml
noaa:
  station_id: ${NOAA_STATION_ID:-8534720}  # Default if env var missing
  buoy_id: "44091"
```

**Custom Validation**: If environment variable is unresolved (`${MISSING}`), uses default value.

---

#### 2. EmailConfig

```python
class EmailConfig(StrictModel):
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender: str | None = None
    password: str | None = None
    recipients: str | None = None
    test_recipients: str | None = None
    recipient_urls: RecipientUrlsConfig
    use_recipient_url: bool = True
```

**YAML**:
```yaml
email:
  smtp_server: smtp.gmail.com
  smtp_port: 587
  sender: ${EMAIL_ADDRESS}
  password: ${EMAIL_PASSWORD}
  recipients: ${EMAIL_RECIPIENTS}
  test_recipients: ${EMAIL_TEST_RECIPIENTS}
  use_recipient_url: true
  recipient_urls:
    main: ${MAIN_RECIPIENT_URL}
    test: ${TEST_RECIPIENT_URL}
    offseason: ${OFFSEASON_RECIPIENT_URL}
```

---

#### 3. LocationConfig

```python
class LocationConfig(StrictModel):
    longitude: float = -74.2
    latitude: float = 39.5
    beach_orientation_degrees: float = 140  # Southeast-facing
```

**YAML**:
```yaml
location:
  longitude: -74.2
  latitude: 39.5
  beach_orientation_degrees: 140
```

---

#### 4. SummerConfig

```python
class SummerConfig(StrictModel):
    start_offset_days: int = -14  # Summer starts 14 days before Memorial Day
    end_offset_days: int = 0      # Summer ends on Labor Day
```

**YAML**:
```yaml
summer:
  start_offset_days: -14
  end_offset_days: 0
```

---

#### 5. ApiConfig

```python
class ApiConfig(StrictModel):
    timeout: float = 10.0
    verify_ssl: bool = True
    retry_insecure_on_ssl_error: bool = True
    max_retries: int = 3
    backoff_factor: float = 0.8
```

**YAML**:
```yaml
api:
  timeout: 10.0
  verify_ssl: true
  retry_insecure_on_ssl_error: true
  max_retries: 3
  backoff_factor: 0.8
```

---

#### 6. LoggingConfig

```python
class LoggingConfig(StrictModel):
    output: str = "console"  # "console", "file", or "both"
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str | None = None
```

**YAML**:
```yaml
logging:
  output: both  # console and file
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file_path: logs/runs/ocean_report.log
```

---

## Usage Patterns

### Pattern 1: Simple Access

```python
from ocean_report.config.loader import get_settings

config = get_settings()

station_id = config.noaa.station_id
email_host = config.email.smtp_server
```

---

### Pattern 2: Dependency Injection via ApplicationContext

```python
from ocean_report.application import create_application_context

context = create_application_context()

# Config is part of context
station_id = context.config.noaa.station_id
```

---

### Pattern 3: Testing with Custom Config

```python
import pytest
from ocean_report.config.loader import load_app_config

@pytest.fixture
def test_config():
    return load_app_config("tests/fixtures/test_config.yaml")

def test_something(test_config):
    assert test_config.noaa.station_id == "TEST_STATION"
```

---

### Pattern 4: Environment-Based Config

```python
import os
from ocean_report.config.loader import get_settings

# Set environment to select config
env = os.getenv("ENV", "production")
os.environ["OCEAN_REPORT_CONFIG"] = f"config/{env}.yaml"

config = get_settings()
```

---

## Configuration Best Practices

### 1. Secrets in Environment Variables

**✅ Good**: Secrets in environment variables
```yaml
email:
  password: ${EMAIL_PASSWORD}
```

**❌ Bad**: Secrets in config file
```yaml
email:
  password: "my_secret_password_123"  # ❌ Committed to git!
```

---

### 2. Defaults in Schema, Overrides in Environment

**Schema** (`schemas.py`):
```python
class NoaaConfig(StrictModel):
    station_id: str = "8534720"  # Production default
```

**Config** (`config.yaml`):
```yaml
noaa:
  station_id: ${NOAA_STATION_ID:-8534720}  # Can override with env var
```

**Environment** (optional):
```bash
export NOAA_STATION_ID="1234567"  # Override for specific deployment
```

---

### 3. Validate Early

**✅ Good**: Load config at startup
```python
def main():
    config = get_settings()  # Fails fast if config is invalid
    # Now proceed knowing config is valid
    run_report(config)
```

**❌ Bad**: Load config lazily
```python
def fetch_data():
    config = get_settings()  # ❌ Config error discovered mid-execution
    ...
```

---

## Testing Guidelines

### Unit Tests: Validation Logic

```python
import pytest
from pydantic import ValidationError
from ocean_report.config.schemas import ApiConfig

def test_api_config_defaults():
    config = ApiConfig()
    assert config.timeout == 10.0
    assert config.verify_ssl is True

def test_api_config_invalid_timeout():
    with pytest.raises(ValidationError):
        ApiConfig(timeout="not_a_number")
```

---

### Integration Tests: File Loading

```python
import pytest
from ocean_report.config.loader import load_app_config, FileNotFoundError

def test_load_config_from_file():
    config = load_app_config("tests/fixtures/valid_config.yaml")
    assert config.noaa.station_id == "8534720"

def test_load_config_missing_file():
    with pytest.raises(FileNotFoundError):
        load_app_config("nonexistent.yaml")
```

---

## Error Handling

### FileNotFoundError: No config file found

**Cause**: Config file doesn't exist in any fallback location

**Solution**:
1. Set `OCEAN_REPORT_CONFIG`: `export OCEAN_REPORT_CONFIG=/path/to/config.yaml`
2. Or place config in `configs/config.yaml` (project root)
3. Or place config in `~/.config/ocean-report/config.yaml`

---

### ValidationError: Invalid config value

**Cause**: Config file has invalid data

**Example Error**:
```
pydantic.ValidationError: 1 validation error for AppConfig
api.timeout
  Input should be a valid number [type=float_type, input_value='not_a_number']
```

**Solution**: Fix the value in `config.yaml`:
```yaml
api:
  timeout: 10.0  # Not "not_a_number"
```

---

### ValidationError: Extra fields

**Cause**: Config file has unknown fields

**Example Error**:
```
pydantic.ValidationError: 1 validation error for EmailConfig
extra_field
  Extra inputs are not permitted [type=extra_forbidden]
```

**Solution**: Remove the extra field or add it to schema if it's valid

---

## Design Decisions

### Decision: Pydantic Instead of Dataclasses

**Considered**:
- Dataclasses (Python stdlib)
- attrs
- Pydantic

**Chose**: Pydantic

**Reasoning**:
- **Validation**: Automatic type checking and validation
- **Parsing**: `.model_validate()` handles complex nested structures
- **Serialization**: `.model_dump()` for exporting
- **Error Messages**: Clear validation errors for debugging
- **Field Validators**: Custom validation logic (e.g., default substitution for `${VAR}`)

---

### Decision: YAML Instead of TOML/JSON

**Chose**: YAML

**Reasoning**:
- **Comments**: Can document settings inline
- **Readability**: More human-friendly than JSON
- **Hierarchy**: Natural nested structure
- **Common**: Widely used for configuration

---

### Decision: Caching with `@lru_cache`

**Implementation**:
```python
@lru_cache(maxsize=1)
def _get_settings() -> AppConfig:
    return load_app_config()
```

**Reasoning**:
- **Performance**: Load once, use everywhere
- **Consistency**: All modules see same config instance
- **Simple**: No manual cache management needed

---

## Related Components

- **[Application](./application.md)**: Uses config in ApplicationContext
- **[API Client](./api_client.md)**: Configured by ApiConfig section
- **[Logger](./logger.md)**: Configured by LoggingConfig section
- **[Workflows](./workflows.md)**: Loads config at startup

---

## Summary

**Key Takeaways**:

1. **Production-Ready Path Resolution**: XDG-style fallbacks, environment variable support
2. **Type-Safe**: Pydantic validation catches errors early
3. **Environment Variable Substitution**: `${VAR}` placeholders in YAML
4. **Cached**: `get_settings()` loads once, returns cached instance
5. **Strict**: Extra fields forbidden to catch typos

**When to Use**:
- At application startup (load once)
- In ApplicationContext (dependency injection)
- In tests (load custom test configs)

**When Not to Use**:
- For runtime state (config is settings, not data)
- For frequently changing values (config should be relatively static)

---

**Next**: See [Application Component](./application.md) to understand how config is bundled with the API client.
