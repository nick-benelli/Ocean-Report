# Endpoints Component

**Purpose**: API-specific implementations that know how to call external weather APIs (NOAA, NDBC, Open-Meteo).

**Location**: `src/ocean_report/endpoints/`

---

## Overview

The Endpoints component sits between the generic API Client and your business logic. Each endpoint knows:
- The base URL for a specific API
- How to construct request parameters
- How to validate and parse responses into typed models

### Key Principle

**Endpoints contain API-specific knowledge, but NOT business logic.**

- ✅ **Good**: "NOAA water temperature endpoint lives at `/datagetter` with specific query params"
- ❌ **Bad**: "Use station 8534720 by default"  ← That's business logic (belongs in use cases)

---

## Architecture

### File Structure

```
endpoints/
├── __init__.py
├── base.py              # BaseEndpoint - shared abstractions
├── noaa/
│   ├── __init__.py
│   ├── base.py          # NoaaEndpoint - NOAA-specific base
│   ├── water_temperature.py
│   ├── tides.py
│   └── stations.py
├── ndbc/
│   ├── __init__.py
│   ├── base.py          # NdbcEndpoint - NDBC-specific base
│   └── observations.py
└── openmeteo/
    ├── __init__.py
    ├── base.py          # OpenMeteoEndpoint - OpenMeteo-specific base
    └── forecast.py
```

### Class Hierarchy

```
BaseEndpoint (base.py)
    ├── NoaaEndpoint (noaa/base.py)
    │   ├── WaterTemperatureEndpoint
    │   ├── TidesEndpoint
    │   └── StationsEndpoint
    │
    ├── NdbcEndpoint (ndbc/base.py)
    │   └── ObservationsEndpoint
    │
    └── OpenMeteoEndpoint (openmeteo/base.py)
        └── ForecastEndpoint
```

---

## Core Components

### 1. BaseEndpoint (`base.py`)

**Purpose**: Reusable base class for all API endpoints.

**Key Features**:
- URL building from base + path
- Parameter serialization (Pydantic models → query params)
- Generic `get_response()` and `get_json()` methods

**Definition**:
```python
class BaseEndpoint:
    BASE_URL: str = ""  # Override in subclass
    
    def __init__(self, client: ApiClient, *, base_url: str | None = None):
        self.client = client
        self.base_url = base_url or self.BASE_URL
    
    def build_url(self, path: str = "") -> str:
        """Build absolute URL from base + path."""
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
    
    @staticmethod
    def serialize_params(params: BaseModel | Mapping | None):
        """Convert Pydantic model to query params dict."""
        if isinstance(params, BaseModel):
            return params.model_dump(by_alias=True, exclude_none=True)
        return params
    
    def get_json(self, path: str, *, params=None, headers=None):
        """Execute GET request and return JSON."""
        return self.client.get_json(
            self.build_url(path),
            params=self.serialize_params(params),
            headers=headers
        )
```

**Usage**:
```python
endpoint = WaterTemperatureEndpoint(client)
data = endpoint.get_json(
    "/datagetter",
    params=NoaaWaterTempParams(station="8534720")
)
```

---

### 2. NOAA Endpoints (`noaa/`)

#### NoaaEndpoint (Base)

```python
class NoaaEndpoint(BaseEndpoint):
    """Base for all NOAA API endpoints."""
    BASE_URL = "https://api.tidesandcurrents.noaa.gov/api/prod"
```

**All NOAA endpoints inherit from this to share the base URL.**

---

#### WaterTemperatureEndpoint

**Purpose**: Fetch water temperature observations from NOAA.

**API URL**: `https://api.tidesandcurrents.noaa.gov/api/prod/datagetter`

**Implementation**:
```python
class WaterTemperatureEndpoint(NoaaEndpoint):
    PATH = "/datagetter"
    
    def fetch(
        self,
        params: NoaaWaterTempParams,
    ) -> NoaaWaterTempResponse:
        """Fetch water temperature data."""
        data = self.get_json(self.PATH, params=params)
        return NoaaWaterTempResponse.model_validate(data)
```

**Example Usage**:
```python
from ocean_report.endpoints.noaa.water_temperature import WaterTemperatureEndpoint
from ocean_report.models.noaa.water_temperature import NoaaWaterTempParams

endpoint = WaterTemperatureEndpoint(client)

params = NoaaWaterTempParams(
    station="8534720",
    date="latest",
    product="water_temperature",
    format="json",
    time_zone="gmt",
    units="english",
    application="ocean-report"
)

response = endpoint.fetch(params)
print(response.data[0].temperature)  # 72.5
```

**Key Methods**:
- `fetch(params)` - Returns validated `NoaaWaterTempResponse`

---

#### TidesEndpoint

**Purpose**: Fetch tide predictions from NOAA.

**API URL**: `https://api.tidesandcurrents.noaa.gov/api/prod/datagetter`

**Implementation**:
```python
class TidesEndpoint(NoaaEndpoint):
    PATH = "/datagetter"
    
    def fetch(
        self,
        params: NoaaTidesParams,
    ) -> NoaaTidePredictionResponse:
        """Fetch tide prediction data."""
        data = self.get_json(self.PATH, params=params)
        return NoaaTidePredictionResponse.model_validate(data)
```

**Example Usage**:
```python
from ocean_report.endpoints.noaa.tides import TidesEndpoint
from ocean_report.models.noaa.tides import NoaaTidesParams

endpoint = TidesEndpoint(client)

params = NoaaTidesParams(
    station="8534720",
    begin_date="20260616",
    end_date="20260617",
    product="predictions",
    datum="MLLW",
    interval="hilo",  # High/low tides only
    format="json",
    time_zone="lst_ldt",
    units="english"
)

response = endpoint.fetch(params)
for tide in response.predictions:
    print(f"{tide.type} tide at {tide.timestamp}: {tide.value} ft")
```

---

#### StationsEndpoint

**Purpose**: Fetch metadata about NOAA stations.

**API URL**: `https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations`

**Implementation**:
```python
class StationsEndpoint(BaseEndpoint):
    BASE_URL = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi"
    
    def fetch(
        self,
        station_id: str,
    ) -> NoaaStationResponse:
        """Fetch station metadata."""
        path = f"/stations/{station_id}.json"
        data = self.get_json(path)
        return NoaaStationResponse.model_validate(data)
```

---

### 3. NDBC Endpoints (`ndbc/`)

#### ObservationsEndpoint

**Purpose**: Fetch observations from NDBC buoys (National Data Buoy Center).

**API URL**: `https://www.ndbc.noaa.gov/data/realtime2/`

**Implementation**:
```python
class ObservationsEndpoint(NdbcEndpoint):
    def fetch_latest_observation(
        self,
        buoy_id: str,
    ) -> NdbcObservation:
        """Fetch latest observation from a buoy."""
        # NDBC uses text files, not JSON
        path = f"/{buoy_id}.txt"
        response = self.get_response(path)
        
        # Parse text file into observation
        lines = response.text.split("\n")
        # ... parsing logic ...
        
        return NdbcObservation.model_validate(parsed_data)
```

---

### 4. Open-Meteo Endpoints (`openmeteo/`)

#### ForecastEndpoint

**Purpose**: Fetch hourly weather forecasts from Open-Meteo.

**API URL**: `https://api.open-meteo.com/v1/forecast`

**Implementation**:
```python
class ForecastEndpoint(OpenMeteoEndpoint):
    PATH = "/forecast"
    
    def fetch(
        self,
        params: OpenMeteoForecastParams,
    ) -> OpenMeteoForecastResponse:
        """Fetch hourly forecast data."""
        data = self.get_json(self.PATH, params=params)
        return OpenMeteoForecastResponse.model_validate(data)
```

**Example Usage**:
```python
from ocean_report.endpoints.openmeteo.forecast import ForecastEndpoint
from ocean_report.models.openmeteo.forecast import OpenMeteoForecastParams

endpoint = ForecastEndpoint(client)

params = OpenMeteoForecastParams(
    latitude=39.58,
    longitude=-74.22,
    hourly=["wind_speed_10m", "wind_direction_10m"],
    wind_speed_unit="mph",
    timezone="America/New_York"
)

response = endpoint.fetch(params)
for hour in response.hourly:
    print(f"{hour.time}: {hour.wind_speed_10m} mph from {hour.wind_direction_10m}°")
```

---

## Design Patterns

### Pattern 1: Typed Request/Response

Every endpoint uses Pydantic models for both input (params) and output (response):

```python
class WaterTemperatureEndpoint:
    def fetch(
        self,
        params: NoaaWaterTempParams,  # ← Typed input
    ) -> NoaaWaterTempResponse:        # ← Typed output
        data = self.get_json(self.PATH, params=params)
        return NoaaWaterTempResponse.model_validate(data)
```

**Benefits**:
- Type safety (IDE autocomplete, type checking)
- Validation (bad data rejected immediately)
- Documentation (types show what's expected)

---

### Pattern 2: Separation of Concerns

**Endpoints DO**:
- Know API URLs and paths
- Know query parameter names
- Parse and validate responses
- Handle API-specific quirks

**Endpoints DON'T**:
- Choose default values (use cases do that)
- Implement retry logic (API client does that)
- Format data for display (emailer does that)
- Contain business rules (use cases do that)

**Example**:
```python
# ✅ Good: Endpoint just knows how to call the API
class WaterTemperatureEndpoint:
    def fetch(self, params: NoaaWaterTempParams):
        return self.get_json(self.PATH, params=params)

# ❌ Bad: Endpoint has business logic
class WaterTemperatureEndpoint:
    def fetch(self):
        # ❌ Hardcoded station ID (business logic)
        params = NoaaWaterTempParams(station="8534720")
        return self.get_json(self.PATH, params=params)
```

---

### Pattern 3: Provider-Specific Base Classes

Instead of every endpoint inheriting from `BaseEndpoint`, we have provider-specific bases:

```
BaseEndpoint
    ↓
NoaaEndpoint (adds NOAA base URL)
    ↓
WaterTemperatureEndpoint (adds /datagetter path)
```

**Benefits**:
- Shared base URL across all NOAA endpoints
- Provider-specific helpers (e.g., NOAA date formatting)
- Easy to add new endpoints from same provider

---

## Configuration

Endpoints don't have their own configuration. They receive an `ApiClient` which is already configured:

```python
from ocean_report.application import create_application_context

context = create_application_context()
# context.client already has timeout, SSL, retry settings

endpoint = WaterTemperatureEndpoint(context.client)
# Endpoint inherits all API client configuration
```

---

## Usage Guidelines

### When Creating a New Endpoint

1. **Identify the Provider**: NOAA, NDBC, Open-Meteo, or new?
2. **Create Request Model**: Define `Params` class in `models/provider_name/`
3. **Create Response Model**: Define `Response` class in `models/provider_name/`
4. **Create Endpoint Class**:
   ```python
   class MyNewEndpoint(ProviderEndpoint):
       PATH = "/api/path"
       
       def fetch(self, params: MyParams) -> MyResponse:
           data = self.get_json(self.PATH, params=params)
           return MyResponse.model_validate(data)
   ```
5. **Add Unit Tests**: Test request building and response parsing

---

### Testing Endpoints

#### Unit Tests (Mocked API)

```python
from unittest.mock import Mock

def test_water_temp_endpoint():
    # Mock API client
    mock_client = Mock()
    mock_client.get_json.return_value = {
        "data": [{"t": "2026-06-16 12:00", "v": "72.5"}]
    }
    
    # Create endpoint with mock
    endpoint = WaterTemperatureEndpoint(mock_client)
    
    # Call endpoint
    params = NoaaWaterTempParams(station="8534720")
    response = endpoint.fetch(params)
    
    # Verify
    assert len(response.data) == 1
    assert response.data[0].temperature == 72.5
    
    # Verify API client was called correctly
    mock_client.get_json.assert_called_once_with(
        "/datagetter",
        params={"station": "8534720", ...},
        headers=None
    )
```

---

#### Integration Tests (Real API)

```python
@pytest.mark.integration
def test_water_temp_endpoint_real_api():
    client = ApiClient(timeout=5.0)
    endpoint = WaterTemperatureEndpoint(client)
    
    params = NoaaWaterTempParams(
        station="8534720",
        date="latest",
        product="water_temperature",
        format="json"
    )
    
    response = endpoint.fetch(params)
    
    # Verify we got real data
    assert len(response.data) > 0
    assert 30 <= response.data[0].temperature <= 90  # Reasonable range
```

---

## Common Issues

### Issue: API Returns Different Schema Than Expected

**Symptom**: `ValidationError: Field required` or `Extra inputs are not permitted`

**Cause**: API response doesn't match Pydantic model

**Solution**:
1. Print raw response: `print(client.get_json(url, params))`
2. Compare to model definition
3. Update model to match actual API response

---

### Issue: Query Parameters Not Sent Correctly

**Symptom**: API returns error or unexpected results

**Cause**: Parameter serialization issue

**Debug**:
```python
params = NoaaWaterTempParams(station="8534720")
serialized = params.model_dump(by_alias=True, exclude_none=True)
print(serialized)  # See what's actually sent to API
```

---

## Design Decisions

### Decision: Typed Params Instead of Kwargs

**Considered**:
```python
# Option 1: Kwargs
endpoint.fetch(station="8534720", date="latest", product="water_temperature")

# Option 2: Typed params
params = NoaaWaterTempParams(station="8534720", date="latest")
endpoint.fetch(params)
```

**Chose**: Typed params

**Reasoning**:
- Type safety (IDE knows what parameters are valid)
- Validation (Pydantic catches invalid values)
- Reusability (params can be constructed separately and reused)
- Documentation (params class documents all options)

---

### Decision: Provider-Specific Subdirectories

**Chose**: Group by provider (`noaa/`, `ndbc/`, `openmeteo/`)

**Reasoning**:
- Clear organization (easy to find NOAA vs Open-Meteo endpoints)
- Shared base classes per provider
- Easy to add new providers
- Mirrors model structure (`models/noaa/`, etc.)

---

## Related Components

- **[API Client](./api_client.md)**: Provides HTTP transport for endpoints
- **[Models](./models.md)**: Defines request and response schemas
- **[Services](./services.md)**: Calls endpoints to fetch data
- **[Use Cases](./use_cases.md)**: Orchestrates endpoint calls with business logic

---

## Summary

**Key Takeaways**:

1. **API-Specific Logic**: Endpoints know how to call specific APIs
2. **No Business Logic**: Endpoints don't choose defaults or implement rules
3. **Typed Everything**: Pydantic models for requests and responses
4. **Provider Hierarchy**: Base classes per provider (NOAA, NDBC, Open-Meteo)
5. **Easy to Extend**: Adding new endpoints follows clear patterns

**When to Add an Endpoint**:
- You need to call a new external API
- You need to call a new path on an existing API
- You need different request/response models

**When Not to Use**:
- For internal function calls (not APIs)
- For business logic (that belongs in use cases)
- For data transformation (that belongs in services or use cases)

---

**Next**: See [Models](./models.md) to understand the request and response schemas used by endpoints.
