# Services Component

**Purpose**: Pure data fetching functions that call API endpoints and return validated data—no business logic, no defaults.

**Location**: `src/ocean_report/services/`

---

## Overview

The Services layer sits between Use Cases (business logic) and Endpoints (API calls). Services are **thin** - they only handle API communication and return data. All decision-making happens in the Use Cases layer.

### Key Principle

**Services are dumb data fetchers. They don't think, they just fetch.**

- ✅ **Services DO**: Call endpoints, handle API errors, return validated data
- ❌ **Services DON'T**: Choose defaults, implement business rules, format for display

---

## Architecture

### File Structure

```
services/
├── __init__.py
├── water_temp_service.py
├── tide_service.py
└── wind_service.py
```

### Layer Position

```
Use Cases Layer
    ↓ (calls with defaults resolved)
Services Layer  ← YOU ARE HERE
    ↓ (calls with fully specified params)
Endpoints Layer
    ↓ (makes HTTP request)
API Client Layer
```

---

## Core Components

### 1. Water Temperature Service (`water_temp_service.py`)

**Purpose**: Fetch water temperature data from NOAA.

#### `fetch_water_temp(context, params) → NoaaWaterTemperatureRecord | None`

**What It Does**:
1. Creates WaterTemperatureEndpoint
2. Calls endpoint.fetch(params)
3. Returns latest record or None

**Example**:
```python
from ocean_report.services.water_temp_service import fetch_water_temp
from ocean_report.models.noaa.water_temperature import NoaaWaterTempParams

params = NoaaWaterTempParams(
    station="8534720",
    date="latest"
)

record = fetch_water_temp(context=context, params=params)

if record:
    print(f"Temperature: {record.temperature}°F at {record.timestamp}")
else:
    print("No data available")
```

**Important**: This function does NOT decide which station to use or what date to fetch. The caller (Use Case) provides fully-constructed params.

**Error Handling**: Raises `ApiClientError` if API call fails.

---

#### `add_unit_of_measure(temp) → str`

**What It Does**: Formats temperature value with unit symbol.

**Example**:
```python
formatted = add_unit_of_measure(72.5)
# "72.5 °F"
```

---

### 2. Tide Service (`tide_service.py`)

**Purpose**: Fetch tide predictions from NOAA.

#### `fetch_tides(context, params) → list[NoaaTidePredictionRecord]`

**What It Does**:
1. Creates TidesEndpoint
2. Calls endpoint.fetch(params)
3. Returns list of tide predictions

**Example**:
```python
from ocean_report.services.tide_service import fetch_tides
from ocean_report.models.noaa.tides import NoaaTidesParams

params = NoaaTidesParams(
    station="8534720",
    begin_date="20260616",
    end_date="20260617",
    interval="hilo"
)

tides = fetch_tides(context=context, params=params)

for tide in tides:
    print(f"{tide.type} tide at {tide.timestamp}: {tide.height_ft} ft")
```

**Important**: Service doesn't filter tides (e.g., daytime only). That's business logic—belongs in Use Cases.

---

### 3. Wind Service (`wind_service.py`)

**Purpose**: Fetch wind forecast data from Open-Meteo.

#### `fetch_wind_forecast(context, params) → OpenMeteoForecastResponse`

**What It Does**:
1. Creates ForecastEndpoint
2. Calls endpoint.fetch(params)
3. Returns complete forecast response

**Example**:
```python
from ocean_report.services.wind_service import fetch_wind_forecast
from ocean_report.models.openmeteo.forecast import OpenMeteoForecastParams

params = OpenMeteoForecastParams(
    latitude=39.58,
    longitude=-74.22,
    hourly=["wind_speed_10m", "wind_direction_10m"],
    wind_speed_unit="mph"
)

forecast = fetch_wind_forecast(context=context, params=params)

for i, time in enumerate(forecast.hourly.time):
    speed = forecast.hourly.wind_speed_10m[i]
    direction = forecast.hourly.wind_direction_10m[i]
    print(f"{time}: {speed} mph from {direction}°")
```

**Important**: Service returns raw forecast data. Processing (converting to human-readable times, classifying wind type) happens in Use Cases or Utils.

---

## Design Principles

### Principle 1: No Defaults

**❌ Bad** (Service chooses defaults):
```python
def fetch_water_temp(context, station_id=None):
    # ❌ Service chooses default station
    if station_id is None:
        station_id = "8534720"  # Business logic in service!
    
    params = NoaaWaterTempParams(station=station_id, date="latest")
    ...
```

**✅ Good** (Use Case chooses defaults):
```python
# Service (no defaults)
def fetch_water_temp(context, params):
    endpoint = WaterTemperatureEndpoint(context.client)
    response = endpoint.fetch(params)
    return response.data[0] if response.data else None

# Use Case (handles defaults)
def get_latest_water_temp(context, station_id=None):
    # ✅ Use case chooses default
    if station_id is None:
        station_id = context.config.noaa.station_id
    
    params = NoaaWaterTempParams(station=station_id, date="latest")
    return fetch_water_temp(context, params)
```

---

### Principle 2: No Business Logic

**❌ Bad** (Service filters data):
```python
def fetch_tides(context, params):
    endpoint = TidesEndpoint(context.client)
    response = endpoint.fetch(params)
    
    # ❌ Filtering is business logic!
    daytime_tides = [t for t in response.predictions if is_daytime(t.timestamp)]
    return daytime_tides
```

**✅ Good** (Service returns all data):
```python
def fetch_tides(context, params):
    endpoint = TidesEndpoint(context.client)
    response = endpoint.fetch(params)
    return response.predictions  # Return all, let Use Case filter
```

---

### Principle 3: No Formatting

**❌ Bad** (Service formats for display):
```python
def fetch_water_temp(context, params):
    endpoint = WaterTemperatureEndpoint(context.client)
    response = endpoint.fetch(params)
    
    # ❌ Formatting is presentation logic!
    temp = response.data[0].temperature
    return f"Water Temperature: {temp}°F"
```

**✅ Good** (Service returns raw data):
```python
def fetch_water_temp(context, params):
    endpoint = WaterTemperatureEndpoint(context.client)
    response = endpoint.fetch(params)
    return response.data[0] if response.data else None
```

---

### Principle 4: Explicit Parameters

**❌ Bad** (Too many implicit choices):
```python
def fetch_water_temp(context):
    # ❌ Too much hidden logic
    station = context.config.noaa.station_id
    date = "latest"
    params = NoaaWaterTempParams(station=station, date=date)
    ...
```

**✅ Good** (Caller provides params):
```python
def fetch_water_temp(context, params):
    # ✅ Caller decides what to fetch
    endpoint = WaterTemperatureEndpoint(context.client)
    return endpoint.fetch(params)
```

---

## Error Handling Strategy

### Services Raise Exceptions (Don't Suppress)

**Pattern**: Services let exceptions propagate to Use Cases.

```python
def fetch_water_temp(context, params):
    endpoint = WaterTemperatureEndpoint(context.client)
    
    # No try/except - let errors propagate
    response = endpoint.fetch(params)
    
    return response.data[0] if response.data else None
```

**Why?**
- Use Cases decide how to handle errors (retry, fallback, fail)
- Services shouldn't make error recovery decisions
- Explicit error handling at Use Case layer

**Use Case decides**:
```python
def get_latest_water_temp(context, station_id=None):
    try:
        params = NoaaWaterTempParams(...)
        return fetch_water_temp(context, params)
    except ApiClientError as e:
        logger.error(f"Failed to fetch water temp: {e}")
        return None  # Or retry, or raise, or use cached data
```

---

## Usage Patterns

### Pattern 1: Simple Fetch

```python
from ocean_report.services.water_temp_service import fetch_water_temp

params = NoaaWaterTempParams(station="8534720", date="latest")
record = fetch_water_temp(context, params)

if record:
    print(f"{record.temperature}°F")
```

---

### Pattern 2: Batch Fetching

```python
# Fetch multiple stations
stations = ["8534720", "8557380", "8518750"]

temperatures = {}
for station in stations:
    params = NoaaWaterTempParams(station=station, date="latest")
    record = fetch_water_temp(context, params)
    if record:
        temperatures[station] = record.temperature
```

---

### Pattern 3: With Error Handling

```python
try:
    params = NoaaWaterTempParams(station="8534720", date="latest")
    record = fetch_water_temp(context, params)
except ApiClientError as e:
    logger.error(f"API error: {e}")
    record = None
```

---

## Testing Guidelines

### Unit Tests: Mock Endpoint

```python
from unittest.mock import Mock, patch

def test_fetch_water_temp():
    # Mock context
    context = Mock()
    context.client = Mock()
    
    # Mock endpoint
    with patch('ocean_report.services.water_temp_service.WaterTemperatureEndpoint') as MockEndpoint:
        mock_endpoint = Mock()
        MockEndpoint.return_value = mock_endpoint
        
        # Mock response
        mock_response = NoaaWaterTempResponse(
            data=[NoaaWaterTemperatureRecord(t="2026-06-16 12:00", v=72.5)]
        )
        mock_endpoint.fetch.return_value = mock_response
        
        # Call service
        params = NoaaWaterTempParams(station="8534720")
        record = fetch_water_temp(context, params)
        
        # Verify
        assert record.temperature == 72.5
        mock_endpoint.fetch.assert_called_once_with(params)
```

---

### Integration Tests: Real API

```python
@pytest.mark.integration
def test_fetch_water_temp_real_api():
    context = create_application_context()
    
    params = NoaaWaterTempParams(
        station="8534720",
        date="latest"
    )
    
    record = fetch_water_temp(context, params)
    
    assert record is not None
    assert isinstance(record.temperature, float)
    assert 30 <= record.temperature <= 90  # Reasonable range
```

---

## When to Add a New Service

**Add a new service when**:
- You need to fetch data from a new endpoint
- You need to orchestrate multiple endpoint calls
- You need to transform raw API responses into domain objects

**Example**: Adding a service for wind forecasts:

```python
# services/wind_service.py

def fetch_wind_forecast(context, params):
    """Fetch wind forecast from Open-Meteo."""
    endpoint = ForecastEndpoint(context.client)
    response = endpoint.fetch(params)
    return response

def process_hourly_wind(forecast_response, target_hours):
    """Extract specific hours from forecast.
    
    Note: This might be borderline business logic.
    Consider moving to Use Cases if it gets complex.
    """
    # Simple extraction/filtering is OK in services
    # Complex business rules belong in Use Cases
    ...
```

---

## Common Pitfalls

### Pitfall 1: Service Choosing Defaults

```python
# ❌ Wrong
def fetch_water_temp(context):
    station = context.config.noaa.station_id  # Service accessing config
    params = NoaaWaterTempParams(station=station, date="latest")
    ...

# ✅ Right
def fetch_water_temp(context, params):
    # Params provided by caller
    ...
```

---

### Pitfall 2: Service Implementing Business Rules

```python
# ❌ Wrong
def fetch_tides(context, params):
    endpoint = TidesEndpoint(context.client)
    response = endpoint.fetch(params)
    
    # Business rule: only show high tides above 3ft
    return [t for t in response.predictions if t.type == "H" and t.height_ft > 3.0]

# ✅ Right
def fetch_tides(context, params):
    endpoint = TidesEndpoint(context.client)
    response = endpoint.fetch(params)
    return response.predictions  # Return all, let Use Case decide
```

---

### Pitfall 3: Service Handling Errors Silently

```python
# ❌ Wrong
def fetch_water_temp(context, params):
    try:
        endpoint = WaterTemperatureEndpoint(context.client)
        return endpoint.fetch(params)
    except ApiClientError:
        return None  # ❌ Silent failure!

# ✅ Right
def fetch_water_temp(context, params):
    endpoint = WaterTemperatureEndpoint(context.client)
    return endpoint.fetch(params)  # Let error propagate
```

---

## Design Decisions

### Decision: Thin Services, Not Fat

**Chose**: Keep services as thin wrappers around endpoints

**Reasoning**:
- **Simplicity**: Easy to understand what service does
- **Testability**: Less logic = easier to test
- **Flexibility**: Business logic changes more than API calls
- **Single Responsibility**: Services only handle API communication

---

### Decision: Services Don't Access Config Directly

**Chose**: Services receive everything via parameters

**Reasoning**:
- **Explicit**: Clear what service needs
- **Testable**: Easy to pass test params
- **Reusable**: Same service works with different configs
- **Separation**: Config decisions belong in Use Cases

---

## Related Components

- **[Use Cases](./use_cases.md)**: Calls services with resolved defaults and business logic
- **[Endpoints](./endpoints.md)**: Called by services to make API requests
- **[Models](./models.md)**: Services receive and return typed models
- **[API Client](./api_client.md)**: Used by endpoints (via context)

---

## Summary

**Key Takeaways**:

1. **Thin Layer**: Services are simple wrappers around endpoints
2. **No Defaults**: Callers provide fully-constructed parameters
3. **No Business Logic**: Services don't make decisions
4. **No Formatting**: Services return raw data
5. **Explicit Errors**: Let exceptions propagate to Use Cases

**When to Use**:
- You need to call an API endpoint
- You need consistent error handling for an endpoint
- You need to transform raw API response into domain object

**When Not to Use**:
- For choosing default values (use Use Cases)
- For implementing business rules (use Use Cases)
- For formatting data (use Emailer or Utils)

---

**Next**: See [Use Cases](./use_cases.md) to understand how services are orchestrated with business logic.
