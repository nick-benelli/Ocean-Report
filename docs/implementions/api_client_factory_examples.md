# ApiClient Factory - Usage Examples

## Overview

The `create_api_client` factory function provides a clean, dependency-injected way to construct `ApiClient` instances from validated configuration.

## Basic Usage

### Standard Usage with Config File

```python
from ocean_report.config.loader import load_config
from ocean_report.api_client.factory import create_api_client

# Load configuration from YAML
config = load_config("config.yaml")

# Create client with config settings
client = create_api_client(config)

# Use the client
response = client.get("https://api.weather.gov/stations")
print(response.json())
```

### Direct Configuration Construction

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

## Advanced Usage

### Custom Session Injection

Useful for testing or when you need to share a session pool:

```python
import requests
from ocean_report.api_client.factory import create_api_client
from ocean_report.config.loader import load_config

# Create custom session with additional configuration
session = requests.Session()
session.headers.update({"User-Agent": "OceanReport/1.0"})

# Inject session into client
config = load_config("config.yaml")
client = create_api_client(config, session=session)
```

### Testing with Mock Session

```python
from unittest.mock import Mock, MagicMock
import pytest
from ocean_report.api_client.factory import create_api_client
from ocean_report.config.schemas import AppConfig

def test_api_interaction():
    """Test API interactions with a mocked session."""
    # Create mock session
    mock_session = Mock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}
    mock_session.get.return_value = mock_response
    
    # Create client with mock
    config = AppConfig()
    client = create_api_client(config, session=mock_session)
    
    # Test behavior
    response = client.get("https://api.example.com/test")
    assert response.status_code == 200
    assert response.json() == {"data": "test"}
```

### Environment-Specific Clients

```python
from ocean_report.config.loader import load_config
from ocean_report.api_client.factory import create_api_client

def create_production_client():
    """Create client optimized for production."""
    config = load_config("config.production.yaml")
    return create_api_client(config)

def create_development_client():
    """Create client for development with relaxed SSL."""
    config = load_config("config.development.yaml")
    # config.yaml might have verify_ssl: false for local testing
    return create_api_client(config)

def create_test_client():
    """Create client with shorter timeouts for testing."""
    config = load_config("config.test.yaml")
    # config.yaml might have timeout_seconds: 5.0 for faster tests
    return create_api_client(config)
```

### Multiple Clients for Different Services

```python
from ocean_report.config.loader import load_config
from ocean_report.api_client.factory import create_api_client

# Load base configuration
config = load_config("config.yaml")

# Create multiple independent clients
noaa_client = create_api_client(config)
ndbc_client = create_api_client(config)
weather_client = create_api_client(config)

# Each client has its own session and can be used independently
noaa_data = noaa_client.get("https://api.weather.gov/stations")
ndbc_data = ndbc_client.get("https://www.ndbc.noaa.gov/data")
weather_data = weather_client.get("https://api.open-meteo.com/v1/forecast")
```

### Context Manager Usage

```python
from ocean_report.config.loader import load_config
from ocean_report.api_client.factory import create_api_client

def fetch_ocean_data():
    """Fetch data with automatic resource cleanup."""
    config = load_config("config.yaml")
    
    with create_api_client(config) as client:
        response = client.get("https://api.weather.gov/stations/8534720")
        return response.json()
    # Session is automatically closed when exiting the context
```

### Configuration Override Pattern

```python
from ocean_report.config.schemas import AppConfig, ApiConfig
from ocean_report.api_client.factory import create_api_client

def create_client_with_overrides(base_config: AppConfig, **overrides) -> ApiClient:
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
base_config = load_config("config.yaml")

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

## Integration with Application Context

```python
from dataclasses import dataclass
from ocean_report.config.loader import load_config
from ocean_report.api_client.factory import create_api_client
from ocean_report.api_client.client import ApiClient

@dataclass
class AppContext:
    """Application-wide shared resources."""
    config: AppConfig
    api_client: ApiClient
    
    @classmethod
    def from_config_file(cls, config_path: str) -> "AppContext":
        """Create application context from config file."""
        config = load_config(config_path)
        api_client = create_api_client(config)
        return cls(config=config, api_client=api_client)
    
    def __enter__(self) -> "AppContext":
        return self
    
    def __exit__(self, *args) -> None:
        self.api_client.close()

# Usage
with AppContext.from_config_file("config.yaml") as app:
    response = app.api_client.get("https://api.example.com/data")
    # Process response...
# Resources cleaned up automatically
```

## Configuration Examples

### Minimal config.yaml

```yaml
api:
  verify_ssl: true
  timeout_seconds: 10.0
  retry_insecure_on_ssl_error: true
  max_retries: 3
  backoff_seconds: 0.8
```

### Production config.yaml

```yaml
api:
  verify_ssl: true
  timeout_seconds: 30.0
  retry_insecure_on_ssl_error: false
  max_retries: 5
  backoff_seconds: 1.0
```

### Development config.yaml

```yaml
api:
  verify_ssl: false  # For local testing with self-signed certs
  timeout_seconds: 60.0  # Longer timeout for debugging
  retry_insecure_on_ssl_error: true
  max_retries: 2
  backoff_seconds: 0.5
```

### CI/Test config.yaml

```yaml
api:
  verify_ssl: true
  timeout_seconds: 5.0  # Fast failure for tests
  retry_insecure_on_ssl_error: false
  max_retries: 1  # No retries in tests
  backoff_seconds: 0.1
```
