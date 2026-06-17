# Application Context Factory Guide

## Overview

The `create_application_context()` factory provides a single, unambiguous entry point for constructing `ApplicationContext` instances. It bundles configuration and API client together in an immutable container, simplifying dependency management throughout the application.

**Key Features:**
- ✅ Four clear rules for creating contexts
- ✅ Mutual exclusivity validation (only one source allowed)
- ✅ Keyword-only parameters (prevents mistakes)
- ✅ Immutable frozen dataclass result
- ✅ Supports testing, development, and production workflows

---

## Quick Reference

### Import

```python
from ocean_report.application import create_application_context
```

### The Four Rules

#### Rule 1: Pass-Through (Dependency Injection)
```python
# Return existing context unchanged (no-op)
existing = create_application_context()
same = create_application_context(context=existing)
assert same is existing  # True
```

**Use when:** Optional context parameters, dependency injection

---

#### Rule 2: From Config (Testing)
```python
# Create from pre-loaded configuration
from ocean_report.config.loader import load_app_config

config = load_app_config("custom.yaml")
context = create_application_context(config=config)
```

**Use when:** Testing, programmatic config construction

---

#### Rule 3: From Path (Multi-Environment)
```python
# Load config from file and create context
context = create_application_context(config_path="config/prod.yaml")

# Also accepts Path objects
from pathlib import Path
context = create_application_context(config_path=Path("config/prod.yaml"))
```

**Use when:** Multi-environment deployments, explicit config files

---

#### Rule 4: Default (Recommended for Production)
```python
# Load default config (cached) and create context
context = create_application_context()
```

**Use when:** Standard production use, best performance

---

## Basic Usage Examples

### Example 1: Default Production Path (Recommended)

```python
from ocean_report.application import create_application_context

# Load default configuration and create fully initialized context
# This is the primary production path - uses cached config for performance
context = create_application_context()

# Access configuration
print(f"API timeout: {context.config.api.timeout_seconds}s")
print(f"Station ID: {context.config.location.station_id}")

# Use the client
response = context.client.get("https://api.weather.gov/stations")
print(response.json())
```

---

### Example 2: Custom Configuration Path

```python
from pathlib import Path

# Load configuration from a non-default location
# Useful for multi-environment deployments (dev/staging/prod)
context = create_application_context(config_path="config/production.yaml")

# Or using Path object
config_file = Path("config") / "staging.yaml"
context = create_application_context(config_path=config_file)

# Use context
response = context.client.get("https://api.weather.gov/stations")
```

---

### Example 3: Pre-loaded Configuration

```python
from ocean_report.config.loader import load_app_config

# Load and potentially modify configuration before creating context
config = load_app_config("config.yaml")

# Inspect or validate config
print(f"Using station: {config.location.station_id}")

# Create context from the loaded config
context = create_application_context(config=config)
```

---

### Example 4: Pass-through Existing Context

```python
# Create context once
main_context = create_application_context()

# Pass it through in functions that may or may not have a context
# This is useful for dependency injection patterns
def process_data(context = None):
    """Process data using provided or default context."""
    ctx = create_application_context(context=context)
    # ctx is always valid here - either the passed context or a new one
    return ctx.client.get("https://api.example.com/data")

# Call with existing context (no-op, returns same instance)
result = process_data(context=main_context)

# Call without context (creates new one)
result = process_data()
```

---

## Advanced Usage

### Application Initialization Pattern

```python
from ocean_report.application import create_application_context

def initialize_application(env: str = "default"):
    """Initialize application with environment-specific configuration."""
    if env == "default":
        return create_application_context()
    else:
        config_path = f"config/{env}.yaml"
        return create_application_context(config_path=config_path)

# Usage
dev_context = initialize_application("dev")
prod_context = initialize_application("prod")
default_context = initialize_application()
```

---

### Testing Pattern with Custom Config

```python
import pytest
from ocean_report.config.schemas import AppConfig, ApiConfig
from ocean_report.application import create_application_context

@pytest.fixture
def test_context():
    """Create test context with custom configuration."""
    # Build config programmatically for testing
    test_config = AppConfig(
        api=ApiConfig(
            timeout_seconds=5,
            verify_ssl=False,
            max_retries=1,
            backoff_seconds=0.1,
        ),
        # ... other config fields with test values
    )
    return create_application_context(config=test_config)

def test_api_call(test_context):
    """Test using custom test context."""
    response = test_context.client.get("https://test.example.com")
    assert response.status_code == 200
```

---

### Singleton Pattern (If Needed)

```python
from ocean_report.application import create_application_context, ApplicationContext

class ApplicationService:
    """Service that maintains a single application context."""
    
    _context: ApplicationContext | None = None
    
    @classmethod
    def get_context(cls) -> ApplicationContext:
        """Get or create the singleton application context."""
        if cls._context is None:
            cls._context = create_application_context()
        return cls._context
    
    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (useful for testing)."""
        cls._context = None

# Usage
context = ApplicationService.get_context()

# In tests
ApplicationService.reset()  # Clean state for next test
```

---

### Environment-Specific Configs

```python
import os
from ocean_report.application import create_application_context

def get_context_for_environment():
    """Get context based on APP_ENV environment variable."""
    env = os.getenv("APP_ENV", "dev")
    
    if env == "prod":
        return create_application_context(config_path="config/prod.yaml")
    elif env == "staging":
        return create_application_context(config_path="config/staging.yaml")
    else:
        return create_application_context(config_path="config/dev.yaml")

# Usage
context = get_context_for_environment()
```

---

### Context Manager Pattern

```python
from contextlib import contextmanager
from ocean_report.application import create_application_context

@contextmanager
def application_context(config_path: str | None = None):
    """Context manager for application lifecycle."""
    if config_path:
        context = create_application_context(config_path=config_path)
    else:
        context = create_application_context()
    
    try:
        yield context
    finally:
        # Cleanup if needed (e.g., close connections)
        # ApiClient sessions are closed automatically when garbage collected
        pass

# Usage
with application_context("config/prod.yaml") as ctx:
    response = ctx.client.get("https://api.example.com")
    print(response.json())
```

---

## Design Decisions

### 1. Keyword-Only Parameters

```python
def create_application_context(
    *,  # Forces keyword-only arguments
    context: ApplicationContext | None = None,
    config: AppConfig | None = None,
    config_path: str | Path | None = None,
) -> ApplicationContext:
```

**Rationale:**
- ✅ Prevents accidental positional argument passing
- ✅ Makes call sites self-documenting
- ✅ Reduces risk of parameter order mistakes
- ✅ Common Python best practice for multiple optional parameters

**Example:**
```python
# ✅ Clear and explicit
create_application_context(config=my_config)

# ❌ Would fail - no positional args allowed
create_application_context(my_config)  # TypeError!
```

---

### 2. Mutual Exclusivity Validation

Only ONE source of configuration can be provided:

```python
provided_params = sum([
    context is not None,
    config is not None,
    config_path is not None,
])

if provided_params > 1:
    raise ValueError(
        "Only one of 'context', 'config', or 'config_path' may be provided. "
        "Multiple parameters create ambiguous configuration sources."
    )
```

**Rationale:**
- ✅ Eliminates ambiguity about which source takes precedence
- ✅ Fail-fast behavior prevents subtle bugs
- ✅ Makes the API contract explicit
- ✅ Validation happens before any I/O (efficient early failure)

**Example:**
```python
# ✅ Valid - one source
create_application_context()
create_application_context(config=cfg)
create_application_context(config_path="config.yaml")

# ❌ Invalid - multiple sources
create_application_context(config=cfg, config_path="config.yaml")  # ValueError!
```

---

### 3. No `client` Parameter

The factory does NOT accept a pre-built `ApiClient`:

```python
# ❌ NOT SUPPORTED
create_application_context(config=config, client=my_client)
```

**Rationale:**
- ✅ Prevents inconsistency between config and client state
- ✅ Configuration remains the single source of truth
- ✅ Eliminates bugs where client and config don't match
- ✅ Simplifies testing (mock the config, not the client)

**Alternative:** Modify `AppConfig.api` settings instead

---

### 4. Cached vs. Uncached Config Loading

| Pattern | Function Used | Caching | Performance |
|---------|---------------|---------|-------------|
| Rule 4 (no params) | `get_settings()` | ✅ Cached | Fast (best for production) |
| Rule 3 (config_path) | `load_app_config(path)` | ❌ Uncached | Slower (reads file) |
| Rule 2 (config) | N/A | N/A | Fast (no I/O) |
| Rule 1 (context) | N/A | N/A | Instant (no-op) |

**Rationale:**
- Default path (production) benefits from caching for repeated calls
- Explicit path suggests intent to load specific configuration
- Allows explicit control when needed

---

### 5. Frozen ApplicationContext

The returned context is immutable:

```python
@dataclass(frozen=True, slots=True)
class ApplicationContext:
    config: AppConfig
    client: ApiClient
```

**Rationale:**
- ✅ Prevents accidental mutation after creation
- ✅ Makes context safe to pass across threads
- ✅ Encourages creating new contexts rather than modifying
- ✅ `slots=True` adds memory efficiency

**Example:**
```python
context = create_application_context()

# ❌ This will fail
context.config = other_config  # AttributeError: cannot assign to field 'config'
```

---

## Decision Tree

```
create_application_context() called
│
├─ context provided?
│   ├─ Yes → Return it unchanged (Rule 1)
│   └─ No ↓
│
├─ config provided?
│   ├─ Yes → Create client from config (Rule 2)
│   └─ No ↓
│
├─ config_path provided?
│   ├─ Yes → Load config, create client (Rule 3)
│   └─ No ↓
│
└─ Default → Load cached default config, create client (Rule 4)
```

---

## Validation and Error Handling

### Valid Calls ✅

```python
# Rule 4: Default
create_application_context()

# Rule 1: Pass-through
create_application_context(context=ctx)

# Rule 2: From config
create_application_context(config=cfg)

# Rule 3: From path
create_application_context(config_path="config.yaml")
```

---

### Invalid Calls ❌

```python
# Multiple parameters - raises ValueError
create_application_context(context=ctx, config=cfg)
create_application_context(config=cfg, config_path="config.yaml")
create_application_context(context=ctx, config_path="config.yaml")

# Invalid config file - raises FileNotFoundError
create_application_context(config_path="missing.yaml")
```

**Error message example:**
```
ValueError: Only one of 'context', 'config', or 'config_path' may be 
provided. Multiple parameters create ambiguous configuration sources.
```

---

## What You Get

```python
context = create_application_context()

# ApplicationContext is a frozen dataclass with two fields:
context.config    # AppConfig - validated configuration
context.client    # ApiClient - HTTP client with retry logic

# Immutable - prevents accidental changes
context.config = other_config  # ❌ Raises AttributeError
```

**Benefits:**
- Simple data structure (just two fields)
- Type-safe (both fields have proper types)
- Immutable (can't be accidentally modified)
- Easy to pass around (lightweight container)

---

## Common Patterns

### Pattern 1: Production Initialization

```python
from ocean_report.application import create_application_context

# At application startup
app_context = create_application_context()

# Use throughout application
def main():
    # Fetch water temperature
    from ocean_report.use_cases.water_temp import get_latest_water_temp
    temp, time, data_time = get_latest_water_temp(app_context)
    print(f"Water temp: {temp}°F at {time}")
```

---

### Pattern 2: Testing with Custom Config

```python
import pytest
from ocean_report.application import create_application_context
from ocean_report.config.schemas import AppConfig, ApiConfig

@pytest.fixture
def test_context():
    """Test context with fast timeouts."""
    config = AppConfig(
        api=ApiConfig(
            timeout_seconds=5,
            verify_ssl=False,
            max_retries=1,
            backoff_seconds=0.1
        ),
        # ... other test config
    )
    return create_application_context(config=config)

def test_use_case(test_context):
    """Test with custom context."""
    from ocean_report.use_cases.water_temp import get_latest_water_temp
    temp, _, _ = get_latest_water_temp(test_context)
    assert isinstance(temp, float)
```

---

### Pattern 3: Optional Context Parameter

```python
from ocean_report.application import create_application_context, ApplicationContext

def process_data(context: ApplicationContext | None = None):
    """Process data with provided or default context."""
    ctx = create_application_context(context=context)
    # ctx is always valid here
    response = ctx.client.get("https://api.example.com/data")
    return response.json()

# Call with context
result = process_data(context=my_context)

# Call without context (creates default)
result = process_data()
```

---

## Troubleshooting

### Error: Multiple Parameters Provided

```python
# ❌ Error
config = load_app_config("config.yaml")
context = create_application_context(
    config=config,
    config_path="other.yaml"  # ERROR!
)
```

**Solution:** Only use ONE parameter
```python
# ✅ Fix - use config OR config_path, not both
context = create_application_context(config=config)
# OR
context = create_application_context(config_path="other.yaml")
```

---

### Error: Config File Not Found

```python
# ❌ Error
context = create_application_context(config_path="missing.yaml")
# FileNotFoundError: [Errno 2] No such file or directory: 'missing.yaml'
```

**Solution:** Verify file exists or use correct path
```python
# ✅ Fix - verify file exists
from pathlib import Path
config_path = Path("config/prod.yaml")
assert config_path.exists(), f"Config not found: {config_path}"
context = create_application_context(config_path=config_path)
```

---

### Context is Immutable

```python
# ❌ Can't modify context
context = create_application_context()
context.config = other_config  # AttributeError!
```

**Solution:** Create a new context
```python
# ✅ Fix - create new context with different config
new_context = create_application_context(config=other_config)
```

---

## Best Practices

### Do's ✅

1. **Use default path in production**
   ```python
   context = create_application_context()  # Cached, fast
   ```

2. **Pass context explicitly in functions**
   ```python
   def fetch_data(context: ApplicationContext):
       return context.client.get("https://api.example.com")
   ```

3. **Create test contexts with custom config**
   ```python
   test_config = AppConfig(...)
   test_context = create_application_context(config=test_config)
   ```

4. **Use environment-specific configs**
   ```python
   env = os.getenv("ENV", "dev")
   context = create_application_context(config_path=f"config/{env}.yaml")
   ```

---

### Don'ts ❌

1. **Don't create global singleton unnecessarily**
   ```python
   # ❌ Avoid global state
   GLOBAL_CONTEXT = create_application_context()
   ```

2. **Don't pass multiple parameters**
   ```python
   # ❌ Will raise ValueError
   create_application_context(config=cfg, config_path="file.yaml")
   ```

3. **Don't try to modify context**
   ```python
   # ❌ Context is frozen
   context.config = new_config  # AttributeError!
   ```

4. **Don't recreate context unnecessarily**
   ```python
   # ❌ Inefficient - create once, reuse
   for item in items:
       context = create_application_context()  # Bad!
       process(item, context)
   
   # ✅ Better - create once
   context = create_application_context()
   for item in items:
       process(item, context)
   ```

---

## See Also

- [Application Component](../architecture/application.md) - Detailed ApplicationContext documentation
- [API Client Factory](./api-client-factory.md) - Lower-level factory used internally
- [Configuration Setup](./config-setup.md) - Config loading and path resolution
- [Use Cases](../architecture/use_cases.md) - How context is used in business logic
