# API Client Factory Guide

## Overview

The `create_api_client` factory provides a clean, dependency-injected way to construct `ApiClient` instances from validated configuration. It follows the factory pattern to encapsulate client construction logic and ensure consistent configuration across the application.

**Key Features:**
- ✅ Pure function (no side effects)
- ✅ Explicit dependency injection
- ✅ Type-safe configuration mapping
- ✅ Optional session injection for testing
- ✅ Comprehensive type hints

---

## Quick Start

```python
from ocean_report.config.loader import load_app_config
from ocean_report.api_client.factory import create_api_client

# Load configuration from YAML
config = load_app_config("config.yaml")

# Create client with config settings
client = create_api_client(config)

# Use the client
response = client.get("https://api.weather.gov/stations")
print(response.json())
```

---

## Basic Usage

### Standard Usage with Config File

```python
from ocean_report.config.loader import load_app_config
from ocean_report.api_client.factory import create_api_client

# Load and validate configuration
config = load_app_config("config.yaml")

# Create client with all settings from config
client = create_api_client(config)

# Make API requests
response = client.get("https://api.weather.gov/stations/8534720")
print(response.json())
```

**Config file example:**
```yaml
# config.yaml
api:
  timeout_seconds: 30.0
  verify_ssl: true
  retry_insecure_on_ssl_error: true
  max_retries: 5
  backoff_seconds: 1.0
```

---

### Direct Configuration Construction

For programmatic configuration (useful in tests):

```python
from ocean_report.config.schemas import AppConfig, ApiConfig
from ocean_report.api_client.factory import create_api_client

# Create config programmatically
api_config = ApiConfig(
    timeout_seconds=30.0,
    verify_ssl=True,
    retry_insecure_on_ssl_error=True,
    max_retries=5,
    backoff_seconds=1.0,
)
app_config = AppConfig(api=api_config)

# Create client
client = create_api_client(app_config)
```

---

## Advanced Usage

### Custom Session Injection

Inject a custom `requests.Session` for testing or advanced use cases:

```python
import requests
from ocean_report.api_client.factory import create_api_client
from ocean_report.config.loader import load_app_config

# Create custom session with additional configuration
session = requests.Session()
session.headers.update({
    "User-Agent": "OceanReport/1.0",
    "Accept": "application/json"
})

# Inject session into client
config = load_app_config("config.yaml")
client = create_api_client(config, session=session)
```

**Use cases for custom sessions:**
- Adding custom headers
- Setting up authentication
- Connection pooling
- Testing with mocked sessions

---

### Testing with Mock Session

```python
from unittest.mock import Mock, MagicMock
import pytest
from ocean_report.api_client.factory import create_api_client
from ocean_report.config.schemas import AppConfig, ApiConfig

def test_api_interaction():
    """Test API interactions with a mocked session."""
    # Create mock session
    mock_session = Mock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_session.get.return_value = mock_response
    
    # Create minimal config for testing
    config = AppConfig(
        api=ApiConfig(
            timeout_seconds=5,
            verify_ssl=False,
            max_retries=1
        )
    )
    
    # Create client with mock
    client = create_api_client(config, session=mock_session)
    
    # Test behavior
    response = client.get("https://api.example.com/test")
    assert response.status_code == 200
    assert response.json() == {"data": "test"}
    
    # Verify session was called correctly
    mock_session.get.assert_called_once()
```

---

### Environment-Specific Clients

```python
from ocean_report.config.loader import load_app_config
from ocean_report.api_client.factory import create_api_client

def create_production_client():
    """Create client optimized for production."""
    config = load_app_config("config/production.yaml")
    return create_api_client(config)

def create_development_client():
    """Create client for development with relaxed SSL."""
    config = load_app_config("config/development.yaml")
    # development.yaml might have verify_ssl: false
    return create_api_client(config)

def create_test_client():
    """Create client with shorter timeouts for testing."""
    config = load_app_config("config/test.yaml")
    # test.yaml might have timeout_seconds: 5.0
    return create_api_client(config)

# Usage
if os.getenv("ENV") == "production":
    client = create_production_client()
elif os.getenv("ENV") == "development":
    client = create_development_client()
else:
    client = create_test_client()
```

---

### Multiple Clients for Different Services

```python
from ocean_report.config.loader import load_app_config
from ocean_report.api_client.factory import create_api_client

# Load base configuration
config = load_app_config("config.yaml")

# Create multiple independent clients
noaa_client = create_api_client(config)
ndbc_client = create_api_client(config)
weather_client = create_api_client(config)

# Each client has its own session and can be used independently
noaa_data = noaa_client.get("https://api.weather.gov/stations")
ndbc_data = ndbc_client.get("https://www.ndbc.noaa.gov/data")
weather_data = weather_client.get("https://api.open-meteo.com/v1/forecast")
```

**Why multiple clients?**
- Independent retry state
- Separate connection pools
- Isolated error handling
- Different rate limiting

---

### Configuration Override Pattern

```python
from ocean_report.config.schemas import AppConfig, ApiConfig
from ocean_report.api_client.factory import create_api_client
from ocean_report.config.loader import load_app_config

def create_client_with_overrides(base_config: AppConfig, **overrides):
    """Create client with specific config overrides."""
    # Extract current API config
    api_dict = base_config.api.model_dump()
    
    # Apply overrides
    api_dict.update(overrides)
    
    # Create new config with overrides
    new_api_config = ApiConfig(**api_dict)
    new_app_config = base_config.model_copy(update={"api": new_api_config})
    
    return create_api_client(new_app_config)

# Usage
base_config = load_app_config("config.yaml")

# Create client with extended timeout for slow endpoints
slow_client = create_client_with_overrides(
    base_config,
    timeout_seconds=60.0,
    max_retries=5
)

# Create client with SSL verification disabled for local testing
local_client = create_client_with_overrides(
    base_config,
    verify_ssl=False
)
```

---

## Design Principles

### 1. Pure Factory Function (No Side Effects)

**Decision:** The factory is a pure function that doesn't load configuration or maintain state.

**Rationale:**
- ✅ **Testability:** Easy to test - no mocking of file I/O required
- ✅ **Predictability:** Same input always produces equivalent output
- ✅ **Composability:** Can be used in any context without hidden dependencies
- ✅ **Thread-safety:** No shared mutable state means no concurrency issues

**Alternative rejected:**
```python
# ❌ Singleton pattern with internal config loading
def create_api_client() -> ApiClient:
    config = load_config("config.yaml")  # Hidden file I/O
    return ApiClient(...)
```

**Why rejected:**
- Hard to test (requires filesystem mocking)
- Inflexible (can't use programmatically created configs)
- Violates separation of concerns

---

### 2. Dependency Injection Over Service Locator

**Decision:** Configuration is passed explicitly as a parameter.

**Rationale:**
- ✅ **Explicit dependencies:** Clear what the factory needs
- ✅ **Multiple configurations:** Easy to create clients with different configs
- ✅ **No hidden coupling:** No dependency on global state
- ✅ **Better for testing:** Can pass test configs without touching global state

**Alternative rejected:**
```python
# ❌ Global configuration registry
def create_api_client() -> ApiClient:
    config = ConfigRegistry.get_global_config()
    return ApiClient(...)
```

**Why rejected:**
- Hard to test (requires registry setup/teardown)
- Single configuration limits flexibility
- Hidden dependency on global state

---

### 3. Optional Session Injection

**Decision:** Allow passing a custom `requests.Session` but create one by default.

**Rationale:**
- ✅ **Default simplicity:** Most callers don't need custom sessions
- ✅ **Testing flexibility:** Can inject mock sessions for unit tests
- ✅ **Session pooling:** Advanced users can share sessions across clients
- ✅ **Custom configuration:** Allows pre-configured sessions with headers, auth, etc.

**Signature:**
```python
def create_api_client(
    config: AppConfig,
    session: requests.Session | None = None,
) -> ApiClient:
```

**Use cases:**
- `None` (default): ApiClient creates its own session
- Mock session: Unit testing without HTTP calls
- Shared session: Connection pooling across multiple clients
- Custom session: Pre-configured with auth tokens, headers, etc.

---

### 4. Configuration Mapping (Not Passthrough)

**Decision:** Explicitly map each config field to ApiClient parameters.

**Current implementation:**
```python
return ApiClient(
    timeout=config.api.timeout_seconds,
    verify_ssl=config.api.verify_ssl,
    retry_insecure_on_ssl_error=config.api.retry_insecure_on_ssl_error,
    max_retries=config.api.max_retries,
    backoff_seconds=config.api.backoff_seconds,
    session=session,
)
```

**Rationale:**
- ✅ **Clarity:** Easy to see exactly what's being configured
- ✅ **Type safety:** IDE and type checkers can verify all mappings
- ✅ **Maintainability:** Changes to config schema are obvious
- ✅ **Documentation:** Self-documenting - shows all supported parameters

**Alternative rejected:**
```python
# ❌ Dictionary unpacking
return ApiClient(**config.api.model_dump(), session=session)
```

**Why rejected:**
- Fragile - breaks if config field names differ from constructor params
- Type-unsafe - no compile-time checking
- Hard to debug - unclear what values are being passed

---

## Function Signature

```python
def create_api_client(
    config: AppConfig,
    session: requests.Session | None = None,
) -> ApiClient:
    """Create an ApiClient instance from configuration.
    
    Args:
        config: Validated application configuration
        session: Optional requests.Session instance (creates one if None)
        
    Returns:
        Configured ApiClient instance
        
    Example:
        >>> config = load_app_config("config.yaml")
        >>> client = create_api_client(config)
        >>> response = client.get("https://api.example.com")
    """
```

---

## Architecture

### Component Flow

```
┌─────────────────┐
│  config.yaml    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ConfigLoader    │  ← Handles I/O and parsing
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Pydantic Schema │  ← Validates configuration
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ create_api_     │  ← Extracts and maps config
│ client()        │     values to client params
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ApiClient       │  ← Makes HTTP requests
└─────────────────┘
```

### Separation of Concerns

Each layer has a single responsibility:

1. **Config Loader** - Reads YAML, substitutes env vars
2. **Pydantic Schema** - Validates structure and types
3. **Factory** - Maps config to client parameters
4. **ApiClient** - Handles HTTP communication and retries

---

## Best Practices

### Do's ✅

**1. Always load config first**
```python
config = load_app_config("config.yaml")  # Validates
client = create_api_client(config)       # Uses validated config
```

**2. Use factory consistently**
```python
# ✅ Always use the factory
client = create_api_client(config)
```

**3. Inject sessions for testing**
```python
mock_session = Mock(spec=requests.Session)
client = create_api_client(config, session=mock_session)
```

**4. Create multiple clients when needed**
```python
noaa_client = create_api_client(config)
ndbc_client = create_api_client(config)
# Independent clients, no shared state
```

---

### Don'ts ❌

**1. Don't bypass the factory**
```python
# ❌ Don't do this in application code
client = ApiClient(timeout=10.0, verify_ssl=True, ...)
```
**Why:** Loses configuration management benefits

**2. Don't modify config after loading**
```python
# ❌ Don't mutate config
config = load_app_config("config.yaml")
config.api.timeout_seconds = 20.0  # Pydantic models are frozen
```
**Why:** Config should be immutable; create new config instead

**3. Don't create global singletons**
```python
# ❌ Avoid global state
GLOBAL_CLIENT = create_api_client(config)
```
**Why:** Makes testing harder, couples code to global state

**4. Don't mix factory and direct construction**
```python
# ❌ Inconsistent
client1 = create_api_client(config)        # Via factory
client2 = ApiClient(timeout=10.0, ...)     # Direct construction
```
**Why:** Choose one pattern and stick with it

---

## Testing Patterns

### Unit Test with Mock Session

```python
import pytest
from unittest.mock import Mock
from ocean_report.api_client.factory import create_api_client
from ocean_report.config.schemas import AppConfig, ApiConfig

@pytest.fixture
def mock_session():
    """Mock session that returns test data."""
    session = Mock()
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"test": "data"}
    session.get.return_value = response
    return session

@pytest.fixture
def test_config():
    """Test configuration."""
    return AppConfig(
        api=ApiConfig(
            timeout_seconds=5,
            verify_ssl=False,
            max_retries=1,
            backoff_seconds=0.1
        )
    )

def test_client_makes_request(mock_session, test_config):
    """Test that client makes requests correctly."""
    client = create_api_client(test_config, session=mock_session)
    
    response = client.get("https://api.example.com/test")
    
    assert response.status_code == 200
    assert response.json() == {"test": "data"}
    mock_session.get.assert_called_once()
```

---

### Integration Test with Real Config

```python
import pytest
from ocean_report.api_client.factory import create_api_client
from ocean_report.config.loader import load_app_config

@pytest.mark.integration
def test_client_with_real_config():
    """Test client creation with real configuration."""
    config = load_app_config("config/test.yaml")
    client = create_api_client(config)
    
    # Verify client is configured correctly
    assert client.timeout == config.api.timeout_seconds
    assert client.verify_ssl == config.api.verify_ssl
```

---

## Common Pitfalls

### Pitfall 1: Creating Client Before Loading Config

```python
# ❌ Wrong order
client = create_api_client(None)  # TypeError!

# ✅ Correct order
config = load_app_config("config.yaml")
client = create_api_client(config)
```

---

### Pitfall 2: Reusing Session Across Thread Boundaries

```python
# ❌ Dangerous - sessions aren't thread-safe
session = requests.Session()
client1 = create_api_client(config, session=session)
client2 = create_api_client(config, session=session)

# ✅ Safe - separate sessions per client
client1 = create_api_client(config)  # Creates own session
client2 = create_api_client(config)  # Creates own session
```

---

### Pitfall 3: Forgetting to Handle ApiClient Exceptions

```python
# ❌ No error handling
client = create_api_client(config)
response = client.get("https://api.example.com")  # May raise!

# ✅ With error handling
from ocean_report.api_client.exceptions import ApiClientError

client = create_api_client(config)
try:
    response = client.get("https://api.example.com")
except ApiClientError as e:
    logger.error(f"API request failed: {e}")
    # Handle error appropriately
```

---

## See Also

- [API Client Component](../architecture/api_client.md) - Detailed ApiClient documentation
- [Configuration Setup](./config-setup.md) - Config loading and path resolution
- [Application Context Factory](./application-context-factory.md) - Higher-level factory that uses this one
