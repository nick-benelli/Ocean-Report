# API Client Component

**Purpose**: Reusable HTTP transport layer that handles all outbound API requests with retry logic, SSL error recovery, and timeout management.

**Location**: `src/ocean_report/api_client/`

---

## Overview

The API Client is the **foundation** of all external integrations. It provides a single, consistent way to make HTTP requests without duplicating retry logic, error handling, or SSL configuration across the codebase.

### Key Principle

**The API Client knows nothing about NOAA, Open-Meteo, or any specific API.** It only knows how to:
- Make HTTP GET requests
- Retry on failures
- Handle SSL certificate errors
- Apply timeouts
- Parse JSON responses

This separation makes it reusable for any external API and easy to test in isolation.

---

## What Problem Does It Solve?

### Before (Without API Client)

Every module that made HTTP requests had to handle:
```python
# Tide module
response = requests.get(url, timeout=10)
if response.status_code == 500:
    # Retry? How many times? With what backoff?
    ...

# Water temp module  
response = requests.get(url, timeout=10)
if response.status_code == 500:
    # Same retry logic duplicated here
    ...
```

**Problems**:
- Retry logic duplicated everywhere
- Inconsistent timeout handling
- SSL errors handled differently in each module
- Hard to test (each module creates its own requests)

### After (With API Client)

```python
# Tide module
client = ApiClient()
data = client.get_json(url, params={"station": "8534720"})

# Water temp module
client = ApiClient()  
data = client.get_json(url, params={"station": "8534720"})
```

**Benefits**:
- Retry logic centralized
- Consistent error handling
- Easy to mock for tests
- Configuration-driven behavior

---

## Architecture

### File Structure

```
api_client/
├── __init__.py           # Public exports
├── client.py             # Main ApiClient class
├── exceptions.py         # Custom exception hierarchy
├── factory.py            # Helper for creating clients from config
└── utils.py              # Legacy safe_get() wrapper (deprecated)
```

### Class Hierarchy

```
ApiClient (client.py)
    ├─> Uses requests.Session
    ├─> Raises ApiClientError (and subclasses)
    └─> Configured by AppConfig

Exceptions (exceptions.py):
    ApiClientError (base)
    ├── ApiConnectionError
    ├── ApiResponseError  
    └── ApiSslError
```

---

## Core Components

### 1. ApiClient (`client.py`)

**What It Does**: Executes HTTP GET requests with production-ready resilience.

**Key Features**:

#### Automatic Retries
```python
client = ApiClient(
    max_retries=3,           # Try up to 3 times
    backoff_seconds=0.8      # Exponential backoff between retries
)
```

The client automatically retries on:
- HTTP 429 (Too Many Requests)
- HTTP 500-504 (Server errors)
- Connection errors
- Read timeouts

#### SSL Error Recovery
```python
client = ApiClient(
    verify_ssl=True,
    retry_insecure_on_ssl_error=True  # Fallback to unverified on SSL errors
)
```

If an SSL certificate error occurs and `retry_insecure_on_ssl_error=True`, the client will:
1. Log the SSL error
2. Retry the same request with `verify=False`
3. Return the response if successful

#### Timeout Management
```python
client = ApiClient(timeout=10.0)  # 10 second timeout for all requests
```

#### Context Manager Support
```python
with ApiClient() as client:
    data = client.get_json(url)
# Session automatically closed
```

---

### 2. Public Methods

#### `get(url, params, headers) → requests.Response`

**Purpose**: Execute a GET request and return the raw response.

**Example**:
```python
response = client.get(
    "https://api.example.com/data",
    params={"station": "8534720"},
    headers={"User-Agent": "OceanReport/1.0"}
)
print(response.status_code)  # 200
```

**Error Handling**: Raises `ApiClientError` subclasses on failure:
- `ApiConnectionError`: Network issues, DNS failures
- `ApiResponseError`: HTTP 4xx/5xx errors
- `ApiSslError`: SSL certificate verification failures

**Important**: Unlike the old code, `get()` **never returns None**. It always returns a response or raises an exception.

---

#### `get_json(url, params, headers) → dict | list`

**Purpose**: Execute a GET request and parse the JSON response.

**Example**:
```python
data = client.get_json(
    "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter",
    params={
        "station": "8534720",
        "product": "water_temperature",
        "format": "json"
    }
)
print(data["data"][0])  # First temperature record
```

**What It Does Internally**:
1. Calls `get()` to fetch the response
2. Checks `response.status_code` (raises on 4xx/5xx)
3. Parses JSON with `response.json()`
4. Returns the parsed data

**Error Cases**:
- Network error → `ApiConnectionError`
- HTTP 404 → `ApiResponseError`
- Invalid JSON → `ApiResponseError`

---

### 3. Exceptions (`exceptions.py`)

**Why Custom Exceptions?**

Standard library exceptions like `requests.RequestException` are too broad. Our custom hierarchy lets callers handle specific failure modes:

```python
try:
    data = client.get_json(url)
except ApiSslError:
    logger.error("SSL certificate problem - check server certificate")
except ApiConnectionError:
    logger.error("Network connectivity issue - check internet connection")
except ApiResponseError as e:
    logger.error(f"API returned error: {e.status_code}")
```

#### Exception Hierarchy

```
ApiClientError (base)
├── ApiConnectionError      # Network/connectivity issues
├── ApiResponseError        # HTTP 4xx/5xx responses
└── ApiSslError             # SSL certificate failures
```

**ApiClientError** (base):
- Attributes: `url`, `original_error`
- Use: Catch all API-related errors

**ApiConnectionError**:
- Raised for: DNS failures, connection timeouts, refused connections
- Example: `Connection refused`, `Name or service not known`

**ApiResponseError**:
- Attributes: `status_code`, `response_text`
- Raised for: HTTP errors (4xx, 5xx)
- Example: `404 Not Found`, `500 Internal Server Error`

**ApiSslError**:
- Raised for: SSL certificate verification failures
- Example: `[SSL: CERTIFICATE_VERIFY_FAILED]`

---

### 4. Factory (`factory.py`)

**Purpose**: Create `ApiClient` instances from configuration.

**Why?** So you don't have to manually extract config values every time.

**Example**:
```python
from ocean_report.api_client.factory import create_api_client
from ocean_report.config.loader import get_settings

config = get_settings()
client = create_api_client(config)
# Client is pre-configured with timeout, SSL settings, retry logic
```

**What It Does**:
```python
def create_api_client(config: AppConfig) -> ApiClient:
    return ApiClient(
        timeout=config.api.timeout,
        verify_ssl=config.api.verify_ssl,
        retry_insecure_on_ssl_error=config.api.retry_insecure_on_ssl_error,
        max_retries=config.api.max_retries,
        backoff_seconds=config.api.backoff_factor,
    )
```

---

## Configuration

API Client behavior is controlled by the `api:` section in `config.yaml`:

```yaml
api:
  timeout: 10.0                        # Request timeout in seconds
  verify_ssl: true                     # Verify SSL certificates
  retry_insecure_on_ssl_error: true    # Fallback to unverified on SSL errors
  max_retries: 3                       # Number of retry attempts
  backoff_factor: 0.8                  # Exponential backoff multiplier
```

**Schema** (`config/schemas.py`):
```python
class ApiConfig(BaseModel):
    timeout: float = 10.0
    verify_ssl: bool = True
    retry_insecure_on_ssl_error: bool = True
    max_retries: int = 3
    backoff_factor: float = 0.8
```

---

## Usage Patterns

### Pattern 1: Direct Usage (Not Recommended)

```python
from ocean_report.api_client import ApiClient

client = ApiClient(timeout=5.0)
data = client.get_json("https://api.example.com/data")
```

**Problem**: Hardcoded configuration makes testing difficult.

---

### Pattern 2: Configuration-Driven (Recommended)

```python
from ocean_report.application import create_application_context

context = create_application_context()
data = context.client.get_json("https://api.example.com/data")
```

**Benefits**:
- Configuration comes from `config.yaml`
- Easy to override in tests
- Consistent across the application

---

### Pattern 3: Testing with Mocks

```python
from unittest.mock import Mock
from ocean_report.api_client import ApiClient

def test_endpoint():
    mock_client = Mock(spec=ApiClient)
    mock_client.get_json.return_value = {"data": [{"v": 72.5}]}
    
    endpoint = WaterTemperatureEndpoint(mock_client)
    response = endpoint.fetch(params)
    
    assert response.data[0].temperature == 72.5
```

---

## Error Handling Strategy

### Fail Fast with Clear Errors

The API Client **does not suppress errors**. If an API call fails, it raises an exception immediately. This is intentional:

**Why Not Return `None`?**

Old code used to do this:
```python
try:
    response = requests.get(url)
    return response.json()
except Exception:
    return None  # ❌ Silent failure
```

**Problem**: Callers couldn't tell the difference between:
- "API returned empty data" (valid)
- "Network failed" (error)
- "Invalid JSON" (error)

**New Approach**:
```python
try:
    return client.get_json(url)
except ApiClientError as e:
    logger.error(f"API call failed: {e}")
    raise  # ✅ Explicit failure
```

Now the caller must decide: retry, use fallback data, or fail the workflow.

---

### Retry Strategy

**What Gets Retried?**
- Connection errors (DNS, refused connection)
- Read timeouts
- HTTP 429, 500, 502, 503, 504

**What Doesn't Get Retried?**
- HTTP 4xx errors (except 429)
- JSON parsing errors
- SSL errors (unless `retry_insecure_on_ssl_error=True`)

**Backoff Calculation**:
```
delay = backoff_factor * (2 ^ retry_number)

With backoff_factor=0.8:
- First retry:  0.8 * 2^0 = 0.8 seconds
- Second retry: 0.8 * 2^1 = 1.6 seconds
- Third retry:  0.8 * 2^2 = 3.2 seconds
```

---

## Design Decisions

### Why Not Use `httpx` or `aiohttp`?

**Decision**: Stick with `requests` + `urllib3`

**Reasoning**:
- `requests` is stable, battle-tested, and well-documented
- Our use case is synchronous (no need for async)
- The application runs once per day (not a high-throughput service)
- Switching to async would require rewriting the entire codebase

**Future**: If we need concurrent API calls, consider `httpx` with async/await.

---

### Why Separate `get()` and `get_json()`?

**Decision**: Two methods instead of one with a `parse_json` flag

**Reasoning**:
- Clear intent: `get_json()` means "I expect JSON"
- Type safety: `get_json()` always returns `dict | list`
- Less error-prone: No need to remember to pass `parse_json=True`

**Alternative Considered**:
```python
client.get(url, parse_json=True)  # ❌ Easy to forget
```

---

### Why Context Manager Support?

**Decision**: Allow `with ApiClient() as client:`

**Reasoning**:
- Ensures `session.close()` is called automatically
- Follows Python best practices for resource management
- Prevents connection pool leaks

**Example**:
```python
with ApiClient() as client:
    data1 = client.get_json(url1)
    data2 = client.get_json(url2)
# Session closed automatically here
```

---

## Testing Guidelines

### Unit Tests

**What to Test**:
- Retry logic (mock `requests.Session`)
- SSL fallback behavior
- Exception raising on HTTP errors
- JSON parsing errors

**Example**:
```python
def test_get_json_retries_on_500():
    session = Mock()
    session.get.side_effect = [
        Mock(status_code=500),  # First attempt fails
        Mock(status_code=200, json=lambda: {"data": []})  # Retry succeeds
    ]
    
    client = ApiClient(session=session, max_retries=2)
    data = client.get_json("http://example.com/api")
    
    assert session.get.call_count == 2
    assert data == {"data": []}
```

---

### Integration Tests

**What to Test**:
- Real API calls (marked with `@pytest.mark.integration`)
- SSL certificate handling with real HTTPS endpoints
- Timeout behavior with slow endpoints

**Example**:
```python
@pytest.mark.integration
def test_real_noaa_request():
    client = ApiClient(timeout=5.0)
    data = client.get_json(
        "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter",
        params={"station": "8534720", "product": "water_temperature", "format": "json"}
    )
    assert "data" in data
```

---

## Common Issues and Solutions

### Issue: SSL Certificate Errors in Production

**Symptom**: `ApiSslError: [SSL: CERTIFICATE_VERIFY_FAILED]`

**Cause**: The server's SSL certificate can't be verified (expired, self-signed, or intermediate cert missing)

**Solution**:
1. **Best**: Fix the server's SSL certificate
2. **Acceptable**: Set `retry_insecure_on_ssl_error: true` in config
3. **Last Resort**: Set `verify_ssl: false` (not recommended for production)

---

### Issue: Timeouts in GitHub Actions

**Symptom**: Tests pass locally but timeout in CI

**Cause**: Network conditions differ between local and CI environments

**Solution**: Increase timeout in config for CI:
```yaml
api:
  timeout: 30.0  # Higher timeout for CI environments
```

---

### Issue: Too Many Retries

**Symptom**: Slow execution when APIs are down

**Cause**: Default `max_retries=3` with exponential backoff can take ~6 seconds per failed request

**Solution**: Reduce retries for non-critical data:
```python
client = ApiClient(max_retries=1, backoff_seconds=0.3)
```

---

## Migration Notes

### From Old `safe_get()` to New `ApiClient`

**Old Code**:
```python
from ocean_report.api_client.utils import safe_get

response = safe_get(url, params=params)
if response is None:
    return None
return response.json()
```

**New Code**:
```python
from ocean_report.api_client import ApiClient

client = ApiClient()
try:
    return client.get_json(url, params=params)
except ApiClientError as e:
    logger.error(f"API request failed: {e}")
    return None  # Or raise, depending on your needs
```

**Why?**
- `safe_get()` is deprecated (kept for backward compatibility)
- New approach makes error handling explicit
- Easier to test and reason about

---

## Related Components

- **[Endpoints](./endpoints.md)**: Uses ApiClient to call specific APIs
- **[Application](./application.md)**: Creates and manages ApiClient instances
- **[Config](./config.md)**: Provides ApiClient configuration settings

---

## Summary

**Key Takeaways**:

1. **Single Responsibility**: ApiClient only handles HTTP transport
2. **No API-Specific Logic**: Works with any external API
3. **Fail Fast**: Raises exceptions instead of returning `None`
4. **Configuration-Driven**: Behavior controlled by `config.yaml`
5. **Test-Friendly**: Easy to mock and inject for testing

**When to Use**:
- You need to make HTTP requests to external APIs
- You want automatic retries and timeout handling
- You need consistent error handling

**When Not to Use**:
- For internal function calls (not HTTP)
- For complex request signing (OAuth, etc.) - extend with a subclass instead
- For file uploads or POST requests (currently only supports GET)

---

**Next**: See [Endpoints](./endpoints.md) to learn how API-specific logic is built on top of this client.
