# ApplicationContext Factory - Quick Reference

## Import

```python
from ocean_report.application import create_application_context
```

## API Signature

```python
def create_application_context(
    *,
    context: ApplicationContext | None = None,
    config: AppConfig | None = None,
    config_path: str | Path | None = None,
) -> ApplicationContext:
```

## The Four Rules

### Rule 1: Pass-Through
```python
# Return existing context unchanged (no-op)
existing = create_application_context()
same = create_application_context(context=existing)
assert same is existing  # True
```

**Use Case:** Dependency injection, optional context parameters

---

### Rule 2: From Config
```python
# Create from pre-loaded configuration
from ocean_report.config.loader import load_app_config

config = load_app_config("custom.yaml")
context = create_application_context(config=config)
```

**Use Case:** Testing, programmatic config construction

---

### Rule 3: From Path
```python
# Load config from file and create context
context = create_application_context(config_path="config/prod.yaml")

# Also accepts Path objects
from pathlib import Path
context = create_application_context(config_path=Path("config/prod.yaml"))
```

**Use Case:** Multi-environment deployments, explicit config files

---

### Rule 4: Default (Recommended)
```python
# Load default config (cached) and create context
context = create_application_context()
```

**Use Case:** Standard production use, best performance

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

## Validation

❌ **Only ONE parameter allowed**

```python
# ✅ Valid
create_application_context()
create_application_context(context=ctx)
create_application_context(config=cfg)
create_application_context(config_path="config.yaml")

# ❌ Invalid - raises ValueError
create_application_context(context=ctx, config=cfg)
create_application_context(config=cfg, config_path="config.yaml")
create_application_context(context=ctx, config_path="config.yaml")
```

## Common Patterns

### Production Initialization
```python
from ocean_report.application import create_application_context

# At application startup
app_context = create_application_context()

# Use throughout application
response = app_context.client.get("https://api.example.com")
```

### Testing with Custom Config
```python
import pytest
from ocean_report.config.schemas import AppConfig, ApiConfig

@pytest.fixture
def test_context():
    config = AppConfig(
        api=ApiConfig(timeout_seconds=5, verify_ssl=False, max_retries=1),
        # ... other fields
    )
    return create_application_context(config=config)

def test_api_call(test_context):
    response = test_context.client.get("https://test.example.com")
    assert response.ok
```

### Optional Context Parameter
```python
def process_data(context: ApplicationContext | None = None):
    """Process data with provided or default context."""
    ctx = create_application_context(context=context)
    # ctx is always valid here
    return ctx.client.get("https://api.example.com/data")

# Call with context
process_data(context=my_context)

# Call without context (creates default)
process_data()
```

### Environment-Specific Configs
```python
import os

def get_context_for_environment():
    env = os.getenv("APP_ENV", "dev")
    if env == "prod":
        return create_application_context(config_path="config/prod.yaml")
    elif env == "staging":
        return create_application_context(config_path="config/staging.yaml")
    else:
        return create_application_context(config_path="config/dev.yaml")
```

## What You Get

```python
context = create_application_context()

# ApplicationContext is a frozen dataclass
context.config    # AppConfig - validated configuration
context.client    # ApiClient - HTTP client with retry logic

# Immutable - prevents accidental changes
context.config = other_config  # ❌ Raises AttributeError
```

## Performance Notes

| Pattern | Caching | Performance |
|---------|---------|-------------|
| `create_application_context()` | ✅ Cached | Fast (best for production) |
| `create_application_context(config=...)` | N/A | Fast (no I/O) |
| `create_application_context(config_path=...)` | ❌ Uncached | Slower (reads file) |
| `create_application_context(context=...)` | N/A | Instant (no-op) |

## Error Messages

```python
# Multiple parameters
>>> create_application_context(config=cfg, config_path="file.yaml")
ValueError: Only one of 'context', 'config', or 'config_path' may be 
provided. Multiple parameters create ambiguous configuration sources.

# Invalid config file
>>> create_application_context(config_path="missing.yaml")
FileNotFoundError: [Errno 2] No such file or directory: 'missing.yaml'

# Invalid YAML
>>> create_application_context(config_path="bad.yaml")
yaml.scanner.ScannerError: ...

# Missing required fields
>>> create_application_context(config=incomplete_config)
pydantic.ValidationError: ...
```

## Dependencies

```
create_application_context()
    ↓
    ├─→ get_settings() or load_app_config()
    │       ↓
    │       └─→ config.yaml → AppConfig (validated)
    │
    └─→ create_api_client(config)
            ↓
            └─→ ApiClient (with retry, timeout, SSL settings)
```

## Comparison with Manual Construction

### ❌ Manual (Error-Prone)
```python
from ocean_report.config.loader import load_app_config
from ocean_report.api_client.factory import create_api_client
from ocean_report.application.context import ApplicationContext

config = load_app_config()
client = create_api_client(config)
context = ApplicationContext(config=config, client=client)
```

### ✅ Factory (Clean)
```python
from ocean_report.application import create_application_context

context = create_application_context()
```

## Type Annotations

```python
from ocean_report.application import ApplicationContext, create_application_context
from ocean_report.config.schemas import AppConfig
from pathlib import Path

# All return ApplicationContext
ctx1: ApplicationContext = create_application_context()
ctx2: ApplicationContext = create_application_context(config=config)
ctx3: ApplicationContext = create_application_context(config_path="file.yaml")

# Accepts str or Path
path1: str = "config.yaml"
path2: Path = Path("config.yaml")
create_application_context(config_path=path1)  # ✅
create_application_context(config_path=path2)  # ✅
```

## Troubleshooting

### Issue: Multiple parameters error
**Solution:** Use only one parameter. Choose the most appropriate for your use case.

### Issue: Config file not found
**Solution:** Verify the path is correct and relative to working directory.

### Issue: Validation errors
**Solution:** Check config file has all required fields. See `config/schemas.py` for schema.

### Issue: Context is None
**Solution:** The factory never returns None. If you see None, check calling code.

### Issue: Need custom client settings
**Solution:** Don't pass a client. Instead, modify `AppConfig.api` settings:
```python
config = load_app_config()
config.api.timeout_seconds = 60
context = create_application_context(config=config)
```

---

**Full Documentation:** See `docs/application_context_factory_design.md`  
**Examples:** See `docs/application_context_factory_examples.py`  
**Tests:** See `tests/test_application_context_factory.py`
