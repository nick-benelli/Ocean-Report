# Application Component

**Purpose**: Dependency injection container that bundles configuration and the API client for easy passing throughout the application.

**Location**: `src/ocean_report/application/`

---

## Overview

The Application component solves a simple but important problem: **how do we share configuration and the API client across many functions without passing them separately everywhere?**

### The Problem It Solves

Imagine you have 10 functions that need both `config` and `client`:

```python
# Without ApplicationContext ❌
def fetch_water_temp(config, client, station_id):
    ...

def fetch_tides(config, client, station_id):
    ...

def fetch_wind(config, client, lat, lon):
    ...

# Every function needs both parameters!
water_temp = fetch_water_temp(config, client, "8534720")
tides = fetch_tides(config, client, "8534720")
wind = fetch_wind(config, client, 39.58, -74.22)
```

With `ApplicationContext`:

```python
# With ApplicationContext ✅
def fetch_water_temp(context, station_id):
    # Access config: context.config
    # Access client: context.client
    ...

context = create_application_context()
water_temp = fetch_water_temp(context, "8534720")
tides = fetch_tides(context, "8534720")
wind = fetch_wind(context, 39.58, -74.22)
```

**Benefits**:
- Fewer function parameters
- Clear dependency ownership
- Easier to extend (add logging, metrics, etc. to context later)
- Consistent API across all functions

---

## Architecture

### File Structure

```
application/
├── __init__.py        # Public exports
├── context.py         # ApplicationContext class
└── factory.py         # Factory for creating contexts
```

### Component Diagram

```
┌─────────────────────────────────────────┐
│         create_application_context()    │  ← Factory function
│                                         │
│  Input: config_path, config, or context│
│  Output: ApplicationContext             │
└────────────────┬────────────────────────┘
                 │
                 ↓
         ┌───────────────────┐
         │ApplicationContext │
         ├───────────────────┤
         │ + config          │  ← AppConfig instance
         │ + client          │  ← ApiClient instance
         └───────────────────┘
```

---

## Core Components

### 1. ApplicationContext (`context.py`)

**What It Is**: A simple container that holds `config` and `client`.

**Definition**:
```python
from dataclasses import dataclass
from ..api_client.client import ApiClient
from ..config.schemas import AppConfig

@dataclass(frozen=True)
class ApplicationContext:
    """Immutable container for application dependencies.
    
    This context holds everything needed to execute application workflows:
    - Configuration (settings, API keys, station IDs, etc.)
    - API client (HTTP transport with retry logic)
    
    Being frozen (immutable) prevents accidental modification during
    the workflow execution.
    """
    config: AppConfig
    client: ApiClient
```

**Key Characteristics**:
- **Immutable** (`frozen=True`): Once created, cannot be modified
- **Type-Safe**: Both attributes have type hints
- **Simple**: No methods, just data

**Usage**:
```python
context = create_application_context()

# Access configuration
station_id = context.config.noaa.station_id
email_host = context.config.email.host

# Access client
data = context.client.get_json(url, params=params)
```

---

### 2. Factory Function (`factory.py`)

**What It Does**: Creates `ApplicationContext` instances from different sources.

**Signature**:
```python
def create_application_context(
    *,
    context: ApplicationContext | None = None,
    config: AppConfig | None = None,
    config_path: str | Path | None = None,
) -> ApplicationContext:
    """Create or return an ApplicationContext instance."""
```

**Four Use Cases**:

#### Use Case 1: Default Production Context

```python
# No parameters → uses default config path
context = create_application_context()
```

**What Happens**:
1. Looks for config in default locations (see [Config](./config.md))
2. Loads and validates configuration
3. Creates API client from config
4. Returns new ApplicationContext

**When to Use**: Normal production execution

---

#### Use Case 2: Custom Config Path

```python
# Specify config file location
context = create_application_context(config_path="config/test.yaml")
```

**What Happens**:
1. Loads config from specified path
2. Creates API client from that config
3. Returns new ApplicationContext

**When to Use**: Testing, multiple environments, CI/CD

---

#### Use Case 3: Pre-Loaded Config

```python
# Load config separately, then create context
config = load_app_config("config.yaml")
context = create_application_context(config=config)
```

**What Happens**:
1. Uses the provided config (doesn't load from file)
2. Creates API client from that config
3. Returns new ApplicationContext

**When to Use**: When you need to modify config programmatically before creating context

---

#### Use Case 4: Pass-Through (Dependency Injection)

```python
# Return existing context unchanged
existing_context = create_application_context()
same_context = create_application_context(context=existing_context)

assert same_context is existing_context  # True - same object
```

**What Happens**:
1. Returns the provided context as-is (no-op)

**When to Use**: Dependency injection patterns where you want to accept either a context or build one if missing:

```python
def my_function(context: ApplicationContext | None = None):
    # Accept existing context or create new one
    ctx = create_application_context(context=context)
    ...
```

---

## Design Principles

### Principle 1: Mutual Exclusivity

**Rule**: You can only provide ONE of `context`, `config`, or `config_path`.

**Why?**

Multiple sources create ambiguity:
```python
# ❌ What should this do?
context = create_application_context(
    config=my_config,
    config_path="other_config.yaml"  # Which one wins?
)
```

**Enforcement**:
```python
provided_params = sum([
    context is not None,
    config is not None,
    config_path is not None,
])

if provided_params > 1:
    raise ValueError("Only one parameter may be provided")
```

---

### Principle 2: ApiClient Always From Config

**Rule**: The factory NEVER accepts a pre-built `ApiClient`.

**Why?**

Configuration and client must stay synchronized:

```python
# ❌ Config says timeout=10, but client has timeout=5
config = load_app_config()  # timeout: 10
client = ApiClient(timeout=5)  # Different!

context = ApplicationContext(config=config, client=client)
# Now config and client are inconsistent
```

**Instead**:
```python
# ✅ Client always created from config
config = load_app_config()  # timeout: 10
client = create_api_client(config)  # Uses config.api.timeout = 10

context = ApplicationContext(config=config, client=client)
# Config and client are guaranteed consistent
```

---

### Principle 3: Immutability

**Rule**: `ApplicationContext` is frozen (immutable).

**Why?**

Prevents accidental modification during workflow execution:

```python
context = create_application_context()

# ❌ Cannot modify
context.config = new_config  # Raises AttributeError
context.client = new_client  # Raises AttributeError

# ✅ Create new context instead
new_context = create_application_context(config=new_config)
```

**Benefits**:
- Thread-safe (no shared mutable state)
- Predictable behavior (context never changes mid-execution)
- Easier to reason about (no hidden mutations)

---

## Usage Patterns

### Pattern 1: Simple Script

```python
from ocean_report.application import create_application_context
from ocean_report.use_cases.water_temperature import get_latest_water_temp

# Create context once at the start
context = create_application_context()

# Pass to functions that need it
temp, timestamp, data_time = get_latest_water_temp(context=context)
print(f"Water temperature: {temp}°F")
```

---

### Pattern 2: Testing with Custom Config

```python
import pytest
from ocean_report.application import create_application_context
from ocean_report.config.loader import load_app_config

@pytest.fixture
def test_context():
    # Load test-specific config
    config = load_app_config("tests/fixtures/test_config.yaml")
    return create_application_context(config=config)

def test_water_temp_fetch(test_context):
    temp, _, _ = get_latest_water_temp(context=test_context)
    assert temp is not None
```

---

### Pattern 3: Dependency Injection

```python
def fetch_report_data(
    context: ApplicationContext | None = None,
    station_id: str | None = None,
):
    """Fetch report data. Accept context or create one if missing."""
    
    # Create context only if not provided
    ctx = create_application_context(context=context)
    
    # Use defaults from context config if parameters not provided
    if station_id is None:
        station_id = ctx.config.noaa.station_id
    
    # Now proceed with fetching...
    water_temp = fetch_water_temp(ctx, station_id)
    ...
```

**Benefits**:
- Caller can provide context (testing, custom config)
- OR let function create default context (convenience)
- Function works in both scenarios

---

### Pattern 4: Multiple Environments

```python
import os
from ocean_report.application import create_application_context

# Select config based on environment
env = os.getenv("ENV", "production")
config_paths = {
    "production": "config/prod.yaml",
    "staging": "config/staging.yaml",
    "development": "config/dev.yaml",
}

context = create_application_context(config_path=config_paths[env])
```

---

## Configuration Structure

The `ApplicationContext.config` contains all application settings. See [Config Component](./config.md) for full details.

**Quick Reference**:

```python
context = create_application_context()

# NOAA settings
context.config.noaa.station_id       # "8534720"
context.config.noaa.buoy_id          # "44009"

# Email settings
context.config.email.host            # "smtp.gmail.com"
context.config.email.port            # 587
context.config.email.address         # "sender@example.com"
context.config.email.password        # From environment variable

# Location settings
context.config.location.latitude     # 39.58
context.config.location.longitude    # -74.22
context.config.location.beach_direction  # 140

# API client settings
context.config.api.timeout           # 10.0
context.config.api.verify_ssl        # True
context.config.api.max_retries       # 3
```

---

## Testing Guidelines

### Unit Tests: Factory Logic

Test that the factory creates contexts correctly:

```python
def test_create_default_context():
    context = create_application_context()
    
    assert context.config is not None
    assert context.client is not None
    assert isinstance(context.config, AppConfig)
    assert isinstance(context.client, ApiClient)

def test_create_from_config_path():
    context = create_application_context(config_path="tests/fixtures/test.yaml")
    
    assert context.config.noaa.station_id == "TEST_STATION"

def test_mutual_exclusivity():
    with pytest.raises(ValueError, match="Only one parameter"):
        create_application_context(
            config=AppConfig(...),
            config_path="config.yaml"
        )
```

---

### Integration Tests: End-to-End

Test that context works in real workflows:

```python
@pytest.mark.integration
def test_context_in_workflow():
    context = create_application_context()
    
    # Use context in real use case
    temp, _, _ = get_latest_water_temp(context=context)
    
    # Verify we got real data
    assert temp is not None
    assert isinstance(temp, float)
    assert 30 <= temp <= 90  # Reasonable temperature range
```

---

## Common Questions

### Q: Why not just use a global config object?

**A**: Global state makes testing difficult:

```python
# ❌ With global config
import ocean_report
ocean_report.CONFIG = load_config("config.yaml")  # Modifies global state

# Now every test must reset global state
def test_something():
    ocean_report.CONFIG = load_config("test_config.yaml")
    # Test...
    # Cleanup required!
```

**With ApplicationContext**:
```python
# ✅ With context
def test_something():
    context = create_application_context(config_path="test_config.yaml")
    # No global state modified
    # No cleanup required
```

---

### Q: Why not pass config and client separately?

**A**: It reduces boilerplate:

```python
# ❌ Separate parameters
def fetch_water_temp(config, client, station_id):
    ...

def fetch_tides(config, client, station_id):
    ...

def run_report(config, client):
    water = fetch_water_temp(config, client, config.noaa.station_id)
    tides = fetch_tides(config, client, config.noaa.station_id)
    # config and client passed everywhere
```

```python
# ✅ With context
def fetch_water_temp(context, station_id):
    ...

def fetch_tides(context, station_id):
    ...

def run_report(context):
    water = fetch_water_temp(context, context.config.noaa.station_id)
    tides = fetch_tides(context, context.config.noaa.station_id)
    # Single parameter
```

---

### Q: Can I add more things to ApplicationContext?

**A**: Yes, but be thoughtful:

```python
# ✅ Good additions: widely-used dependencies
@dataclass(frozen=True)
class ApplicationContext:
    config: AppConfig
    client: ApiClient
    logger: logging.Logger  # Used by many components
    metrics: MetricsCollector  # Used by many components

# ❌ Bad additions: workflow-specific data
@dataclass(frozen=True)
class ApplicationContext:
    config: AppConfig
    client: ApiClient
    water_temp: float  # ❌ This is workflow data, not a dependency!
    tides: list        # ❌ This is workflow data, not a dependency!
```

**Guideline**: Only add things that are:
- Created once at startup
- Used by multiple components
- Stateless or immutable
- Infrastructure/dependency, not domain data

---

### Q: Why frozen=True?

**A**: Immutability prevents bugs:

```python
context = create_application_context()

def bad_function(ctx):
    # ❌ If not frozen, this would modify shared state
    ctx.config = some_other_config
    # Now all code using this context is broken!

bad_function(context)
# Without frozen=True, context is now corrupted
```

With `frozen=True`, the assignment raises `AttributeError` immediately.

---

## Design Decisions

### Decision: Use Dataclass Instead of Dict

**Considered**:
```python
# Option 1: Dict
context = {"config": config, "client": client}

# Option 2: Dataclass
context = ApplicationContext(config=config, client=client)
```

**Chose**: Dataclass

**Reasoning**:
- **Type safety**: `context.config` vs `context["config"]` (typo-proof)
- **IDE support**: Autocomplete, type checking
- **Explicit**: Clear what's in the context
- **Immutable**: `frozen=True` prevents modifications

---

### Decision: Factory Function Instead of Constructor

**Considered**:
```python
# Option 1: Direct construction
context = ApplicationContext(
    config=load_app_config(),
    client=create_api_client(...)
)

# Option 2: Factory function
context = create_application_context()
```

**Chose**: Factory function

**Reasoning**:
- **Convenience**: Handles common cases automatically
- **Consistent**: Always creates client from config correctly
- **Flexible**: Supports multiple use cases with one interface
- **Validation**: Enforces mutual exclusivity rules

---

## Error Handling

### ValueError: Only one parameter may be provided

**Cause**: Multiple conflicting parameters:
```python
create_application_context(
    config=my_config,
    config_path="config.yaml"
)
```

**Fix**: Provide only one:
```python
create_application_context(config=my_config)
# OR
create_application_context(config_path="config.yaml")
```

---

### FileNotFoundError: No config file found

**Cause**: Factory can't find config in default locations

**Fix**: Either:
1. Set `OCEAN_REPORT_CONFIG` environment variable
2. Provide explicit path: `create_application_context(config_path="...")`
3. Put config in one of the default locations

See [Config Component](./config.md) for details on config path resolution.

---

## Related Components

- **[Config](./config.md)**: Provides the `AppConfig` held in context
- **[API Client](./api_client.md)**: Provides the `ApiClient` held in context
- **[Use Cases](./use_cases.md)**: Consumes context to orchestrate workflows
- **[Services](./services.md)**: Consumes context to fetch data
- **[Workflows](./workflows.md)**: Creates context at application entry point

---

## Summary

**Key Takeaways**:

1. **Dependency Injection**: ApplicationContext bundles config and client
2. **Single Responsibility**: Only holds dependencies, no business logic
3. **Immutable**: `frozen=True` prevents accidental modification
4. **Factory Pattern**: `create_application_context()` handles creation logic
5. **Type-Safe**: Full type hints for IDE support

**When to Use**:
- At application entry point (create once, pass everywhere)
- In tests (create with custom config)
- In any function that needs config or API client

**When Not to Use**:
- For workflow-specific data (use function parameters or return values)
- For mutable state (context should be immutable)

---

**Next**: See [Config Component](./config.md) to understand how configuration is loaded and validated.
