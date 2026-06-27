# Models Component

**Purpose**: Type-safe data schemas using Pydantic for validation, serialization, and documentation.

**Location**: `src/ocean_report/models/`

---

## Overview

The Models component defines the structure of all data flowing through the application—from API requests to API responses to internal data structures. Every piece of data is validated against a Pydantic schema.

### What It Does

**For Non-Technical Readers:**

Think of models as "templates" or "blueprints" for data. They define:
- What fields exist (e.g., `temperature`, `timestamp`)
- What type each field is (number, text, date, etc.)
- What's required vs optional
- What values are valid (e.g., temperature must be a number, not text)

If data doesn't match the template, the application rejects it immediately with a clear error message.

**For Technical Readers:**

- Pydantic v2 models with strict validation
- Frozen dataclasses for immutability
- Field aliases for API compatibility (e.g., API returns `"t"`, we use `timestamp`)
- Type hints throughout for IDE support
- Automatic serialization/deserialization
- Provider-organized structure mirroring endpoints

---

## Architecture

### File Structure

```
models/
├── __init__.py
├── email.py              # Email template data models
├── common/
│   ├── __init__.py
│   ├── base.py           # Base model classes
│   ├── errors.py         # Error response models
│   └── pagination.py     # Pagination models
├── noaa/
│   ├── __init__.py
│   ├── water_temperature.py
│   ├── tides.py
│   └── stations.py
├── ndbc/
│   ├── __init__.py
│   └── observations.py
└── openmeteo/
    ├── __init__.py
    ├── forecast.py
    └── wind.py
```

### Model Categories

```
Common Models (shared patterns)
    ├── BaseAPIModel (frozen, validation enabled)
    ├── ErrorResponse (API error handling)
    └── PaginatedResponse (paginated results)

Email Models (template data)
    └── EmailTemplateData (data contract for Jinja2 templates)

Provider Models (API-specific)
    ├── NOAA Models (water temp, tides, stations)
    ├── NDBC Models (buoy observations)
    └── Open-Meteo Models (forecasts, wind)

Domain Models (business logic)
    ├── WindForecastEntry (processed wind data)
    └── TidePrediction (processed tide data)
```

---

## Core Components

### 1. Base Models (`common/base.py`)

#### BaseAPIModel

**Purpose**: Base class for all API-related models with shared configuration.

**Definition**:
```python
from pydantic import BaseModel, ConfigDict

class BaseAPIModel(BaseModel):
    """Base model for API request/response schemas.
    
    Features:
    - Frozen (immutable after creation)
    - Strict validation (no coercion of incompatible types)
    - Arbitrary types allowed (for complex objects)
    - Validation enabled
    """
    model_config = ConfigDict(
        frozen=True,          # Immutable
        strict=False,         # Allow type coercion
        arbitrary_types_allowed=False,
        validate_assignment=True,
    )
```

**Why Frozen?**
- Prevents accidental modification
- Makes objects hashable (can use in sets/dicts)
- Thread-safe (no mutation = no race conditions)

**Example**:
```python
class NoaaWaterTempRecord(BaseAPIModel):
    timestamp: str = Field(alias="t")
    temperature: float = Field(alias="v")

record = NoaaWaterTempRecord(t="2026-06-16 12:00", v=72.5)
print(record.temperature)  # 72.5

# ❌ Cannot modify (frozen)
record.temperature = 75.0  # Raises FrozenInstanceError
```

---

### 2. Email Models (`email.py`)

#### EmailTemplateData

**Purpose**: Data contract between workflow layer and Jinja2 email templates.

**Definition**:
```python
from pydantic import BaseModel, Field

class EmailTemplateData(BaseModel):
    """
    Data model for email template variables.
    
    This represents the contract between the workflow
    and the Jinja2 email template. All data should be
    pre-formatted and ready for display.
    """
    
    # Header
    long_date: str = Field(
        ..., description="Full date string (e.g., 'Monday, June 24, 2026')"
    )
    
    # Water temperature section
    water_temp: Optional[str] = Field(
        None, description="Formatted water temperature with unit (e.g., '64.4 °F')"
    )
    
    # Tides section
    tide_info: Optional[str] = Field(
        None, description="Formatted tide information with emoji and times"
    )
    
    # Wind section
    wind_info: Optional[str] = Field(
        None, description="Formatted wind forecast with bullet points"
    )
    
    # Footer - station/provider info
    station_name: str = Field(..., description="NOAA station name and ID")
    station_city: str = Field(..., description="Station city name")
    wind_provider: str = Field(
        default="Open-Meteo", description="Wind data provider name"
    )
    
    # Metadata timestamps
    date_retrieved: str = Field(
        ..., description="Formatted data retrieval timestamp (e.g., 'Jun 24 at 6:22 AM')"
    )
    water_temp_measured_at_date: Optional[str] = Field(
        None, description="Water temp measurement timestamp from NOAA sensor"
    )
    
    model_config = {"frozen": True}  # Immutable
```

**Usage Example**:
```python
from ocean_report.models.email import EmailTemplateData

# Create template data
data = EmailTemplateData(
    long_date="Monday, June 16, 2026",
    water_temp="72.5 °F",
    tide_info="⬇️ Low Tide at 8:23 AM — 0.3 ft\n⬆️ High Tide at 2:46 PM — 4.1 ft",
    wind_info="•  8 AM:  4.8 mph ESE (108.0°) → Cross/Onshore",
    station_name="Atlantic City Station 8534720",
    station_city="Atlantic City",
    wind_provider="Open-Meteo",
    date_retrieved="Jun 16 at 6:45 AM",
    water_temp_measured_at_date="Jun 16 at 6:30 AM"
)

# Convert to template dict
template_dict = data.to_template_dict()
# Uses .model_dump(exclude_none=False) to include None values for template conditionals
```

**Design Notes**:
- **Frozen**: Immutable after creation (prevents accidental modification)
- **Pre-formatted**: All values ready for display (no formatting in template)
- **Optional fields**: Use `None` for unavailable data
- **Type safety**: Pydantic validates all fields before template rendering

---

### 3. NOAA Models (`noaa/`)

#### Water Temperature Models

**NoaaWaterTempParams** (Request):
```python
class NoaaWaterTempParams(BaseAPIModel):
    """Query parameters for NOAA water temperature API."""
    
    station: str
    date: str = "latest"
    product: str = "water_temperature"
    format: str = "json"
    time_zone: str = "gmt"
    units: str = "english"
    application: str = "ocean-report"
    
    # Aliases map Python names to API parameter names
    model_config = ConfigDict(
        populate_by_name=True,  # Allow both Python and API names
    )
```

**NoaaWaterTemperatureRecord** (Response):
```python
class NoaaWaterTemperatureRecord(BaseAPIModel):
    """Single water temperature observation."""
    
    timestamp: str = Field(alias="t")
    temperature: float = Field(alias="v")
    
    # Example JSON from API: {"t": "2026-06-16 12:00", "v": "72.5"}
    # Maps to: timestamp="2026-06-16 12:00", temperature=72.5
```

**NoaaWaterTempResponse** (Response):
```python
class NoaaWaterTempResponse(BaseAPIModel):
    """Complete response from NOAA water temperature API."""
    
    data: list[NoaaWaterTemperatureRecord]
    metadata: dict | None = None
```

**Usage Example**:
```python
# Build request params
params = NoaaWaterTempParams(
    station="8534720",
    date="latest"
)

# Serialize to query params
query_params = params.model_dump(by_alias=True, exclude_none=True)
# {"station": "8534720", "date": "latest", "product": "water_temperature", ...}

# Parse API response
api_response = {
    "data": [
        {"t": "2026-06-16 12:00", "v": "72.5"},
        {"t": "2026-06-16 11:54", "v": "72.3"}
    ]
}

response = NoaaWaterTempResponse.model_validate(api_response)
print(response.data[0].temperature)  # 72.5
print(response.data[0].timestamp)    # "2026-06-16 12:00"
```

---

#### Tide Models

**NoaaTidesParams** (Request):
```python
class NoaaTidesParams(BaseAPIModel):
    """Query parameters for NOAA tide predictions API."""
    
    station: str
    begin_date: str
    end_date: str
    product: str = "predictions"
    datum: str = "MLLW"  # Mean Lower Low Water
    interval: str = "hilo"  # High/low tides only
    format: str = "json"
    time_zone: str = "lst_ldt"  # Local standard/daylight time
    units: str = "english"
    application: str = "ocean-report"
```

**NoaaTidePredictionRecord** (Response):
```python
class NoaaTidePredictionRecord(BaseAPIModel):
    """Single tide prediction."""
    
    timestamp: str = Field(alias="t")
    value: str = Field(alias="v")  # Height in feet
    type: str  # "H" for high, "L" for low
    
    @property
    def height_ft(self) -> float:
        """Convert value to float."""
        return float(self.value)
```

**Usage Example**:
```python
params = NoaaTidesParams(
    station="8534720",
    begin_date="20260616",
    end_date="20260617",
    interval="hilo"
)

# Parse response
api_response = {
    "predictions": [
        {"t": "2026-06-16 07:32", "v": "3.1", "type": "H"},
        {"t": "2026-06-16 13:45", "v": "0.8", "type": "L"}
    ]
}

response = NoaaTidePredictionResponse.model_validate(api_response)
for tide in response.predictions:
    print(f"{tide.type} tide at {tide.timestamp}: {tide.height_ft} ft")
# Output:
# H tide at 2026-06-16 07:32: 3.1 ft
# L tide at 2026-06-16 13:45: 0.8 ft
```

---

### 4. Open-Meteo Models (`openmeteo/`)

#### Forecast Models

**OpenMeteoForecastParams** (Request):
```python
class OpenMeteoForecastParams(BaseAPIModel):
    """Query parameters for Open-Meteo forecast API."""
    
    latitude: float
    longitude: float
    hourly: list[str]  # e.g., ["wind_speed_10m", "wind_direction_10m"]
    wind_speed_unit: str = "mph"
    timezone: str = "America/New_York"
```

**OpenMeteoHourlyData** (Response):
```python
class OpenMeteoHourlyData(BaseAPIModel):
    """Hourly forecast data from Open-Meteo."""
    
    time: list[str]  # ISO 8601 timestamps
    wind_speed_10m: list[float]
    wind_direction_10m: list[int]
```

**OpenMeteoForecastResponse** (Response):
```python
class OpenMeteoForecastResponse(BaseAPIModel):
    """Complete response from Open-Meteo forecast API."""
    
    latitude: float
    longitude: float
    hourly: OpenMeteoHourlyData
    timezone: str
```

---

#### Wind Models (Domain)

**WindForecastEntry** (Processed):
```python
class WindForecastEntry(BaseAPIModel):
    """Processed wind forecast entry for email display."""
    
    time: str  # e.g., "8 AM"
    speed_mph: float
    direction: str  # e.g., "NW"
    wind_type: str  # "Offshore", "Onshore", "Cross-shore"
    direction_degrees: int
    
    # This is NOT an API response model
    # It's a domain model created by processing Open-Meteo data
```

**Usage Example**:
```python
# API returns raw data
api_response = {
    "hourly": {
        "time": ["2026-06-16T08:00", "2026-06-16T12:00"],
        "wind_speed_10m": [12.5, 10.2],
        "wind_direction_10m": [315, 270]
    }
}

# Convert to domain model for display
entries = []
for i, time_str in enumerate(api_response["hourly"]["time"]):
    entry = WindForecastEntry(
        time="8 AM" if i == 0 else "12 PM",
        speed_mph=api_response["hourly"]["wind_speed_10m"][i],
        direction="NW" if i == 0 else "W",
        wind_type="Offshore" if i == 0 else "Cross-shore",
        direction_degrees=api_response["hourly"]["wind_direction_10m"][i]
    )
    entries.append(entry)
```

---

### 5. Error Models (`common/errors.py`)

**ApiErrorResponse**:
```python
class ApiErrorResponse(BaseAPIModel):
    """Standard error response from APIs."""
    
    error: str
    message: str | None = None
    code: int | None = None
```

**Usage**:
```python
try:
    response = endpoint.fetch(params)
except ApiResponseError as e:
    # Try to parse as error response
    try:
        error = ApiErrorResponse.model_validate_json(e.response_text)
        logger.error(f"API error: {error.message}")
    except ValidationError:
        logger.error(f"Unexpected error: {e}")
```

---

## Design Patterns

### Pattern 1: Field Aliases

**Problem**: API uses short/cryptic names, but we want readable Python names.

**Solution**: Use `Field(alias=...)` to map between them:

```python
class NoaaWaterTemperatureRecord(BaseAPIModel):
    timestamp: str = Field(alias="t")  # API uses "t"
    temperature: float = Field(alias="v")  # API uses "v"

# API response: {"t": "2026-06-16 12:00", "v": "72.5"}
record = NoaaWaterTemperatureRecord.model_validate({"t": "...", "v": 72.5})

# Access with readable names
print(record.timestamp)    # Not "record.t"
print(record.temperature)  # Not "record.v"
```

---

### Pattern 2: Frozen Models

**Why?** Prevent accidental modification:

```python
record = NoaaWaterTemperatureRecord(t="...", v=72.5)

# ❌ Cannot modify
record.temperature = 75.0  # Raises FrozenInstanceError

# ✅ Create new instance instead
updated = NoaaWaterTemperatureRecord(
    t=record.timestamp,
    v=75.0
)
```

---

### Pattern 3: Separate Request/Response Models

**Pattern**: Every API call has separate models for request params and response data.

```python
# Request (what we send)
class NoaaWaterTempParams(BaseAPIModel):
    station: str
    date: str
    # ...

# Response (what we receive)
class NoaaWaterTempResponse(BaseAPIModel):
    data: list[NoaaWaterTemperatureRecord]
    # ...
```

**Benefits**:
- Clear separation of input vs output
- Different validation rules for each
- Easy to see what API expects vs returns

---

### Pattern 4: Nested Models

**Pattern**: Complex responses use nested models:

```python
class NoaaWaterTempResponse(BaseAPIModel):
    data: list[NoaaWaterTemperatureRecord]  # ← Nested model
    metadata: dict | None = None

class NoaaWaterTemperatureRecord(BaseAPIModel):  # ← Nested model
    timestamp: str
    temperature: float
```

**Benefits**:
- Validation happens at every level
- Type hints work for nested data
- Clear structure

---

## Validation Features

### Type Validation

```python
class NoaaWaterTempParams(BaseAPIModel):
    station: str
    date: str

# ✅ Valid
params = NoaaWaterTempParams(station="8534720", date="latest")

# ❌ Invalid - type error
params = NoaaWaterTempParams(station=8534720, date=123)
# Raises ValidationError: Input should be a valid string
```

---

### Required vs Optional

```python
class NoaaWaterTempParams(BaseAPIModel):
    station: str              # Required
    date: str = "latest"      # Optional with default
    metadata: dict | None = None  # Optional, can be None
```

---

### Custom Validators

```python
from pydantic import field_validator

class NoaaTidesParams(BaseAPIModel):
    station: str
    begin_date: str
    
    @field_validator("begin_date")
    @classmethod
    def validate_date_format(cls, value: str) -> str:
        """Ensure date is in YYYYMMDD format."""
        if not re.match(r"^\d{8}$", value):
            raise ValueError("Date must be in YYYYMMDD format")
        return value
```

---

## Usage Guidelines

### When to Create a New Model

1. **API Request Parameters**: Create `*Params` model
2. **API Response Data**: Create `*Response` model
3. **Domain Objects**: Create domain model if data is processed/transformed

**Example**:
```python
# API models (direct API interaction)
NoaaWaterTempParams      # API request
NoaaWaterTempResponse    # API response

# Domain models (processed data)
WindForecastEntry        # Processed wind data for email
```

---

### Model Naming Conventions

```python
# Request parameters
NoaaWaterTempParams
OpenMeteoForecastParams

# API responses
NoaaWaterTempResponse
OpenMeteoForecastResponse

# Individual records from API
NoaaWaterTemperatureRecord
NoaaTidePredictionRecord

# Domain/business models
WindForecastEntry
ProcessedTideData
```

---

### Serialization

```python
# To dict (for JSON/API)
params = NoaaWaterTempParams(station="8534720", date="latest")
dict_data = params.model_dump(by_alias=True, exclude_none=True)
# {"station": "8534720", "date": "latest", "product": "water_temperature", ...}

# To JSON string
json_str = params.model_dump_json(by_alias=True)

# From dict (parsing API response)
api_data = {"data": [{"t": "...", "v": 72.5}]}
response = NoaaWaterTempResponse.model_validate(api_data)

# From JSON string
json_str = '{"data": [{"t": "...", "v": 72.5}]}'
response = NoaaWaterTempResponse.model_validate_json(json_str)
```

---

## Testing Guidelines

### Unit Tests: Model Validation

```python
def test_water_temp_record_validation():
    # Valid data
    record = NoaaWaterTemperatureRecord(t="2026-06-16 12:00", v=72.5)
    assert record.timestamp == "2026-06-16 12:00"
    assert record.temperature == 72.5

def test_water_temp_record_invalid():
    # Invalid data (temperature is string, not float)
    with pytest.raises(ValidationError):
        NoaaWaterTemperatureRecord(t="2026-06-16 12:00", v="not_a_number")
```

---

### Integration Tests: API Parsing

```python
@pytest.mark.integration
def test_parse_real_noaa_response():
    # Make real API call
    client = ApiClient()
    endpoint = WaterTemperatureEndpoint(client)
    params = NoaaWaterTempParams(station="8534720", date="latest")
    
    # Parse response
    response = endpoint.fetch(params)
    
    # Verify model structure
    assert isinstance(response, NoaaWaterTempResponse)
    assert len(response.data) > 0
    assert isinstance(response.data[0], NoaaWaterTemperatureRecord)
    assert 30 <= response.data[0].temperature <= 90
```

---

## Common Issues

### Issue: Field Alias Not Working

**Symptom**: `ValidationError: Field required`

**Cause**: API returns `{"t": "..."}` but model expects `{"timestamp": "..."}`

**Solution**: Add `Field(alias="t")`:
```python
class MyModel(BaseAPIModel):
    timestamp: str = Field(alias="t")  # ✅ Maps "t" to "timestamp"
```

---

### Issue: Type Coercion Fails

**Symptom**: API returns `"72.5"` (string) but model expects `float`

**Solution**: Pydantic will automatically coerce string to float. If you want strict validation:
```python
class MyModel(BaseAPIModel):
    model_config = ConfigDict(strict=True)  # No coercion
```

---

### Issue: Frozen Model Modification

**Symptom**: `FrozenInstanceError: cannot assign to field`

**Solution**: Create new instance instead:
```python
# ❌ Cannot modify
record.temperature = 75.0

# ✅ Create new instance
updated = record.model_copy(update={"temperature": 75.0})
```

---

## Design Decisions

### Decision: Pydantic v2 Instead of Dataclasses

**Chose**: Pydantic v2

**Reasoning**:
- **Validation**: Automatic type validation
- **Parsing**: Easy API response parsing
- **Serialization**: Built-in JSON/dict conversion
- **Documentation**: Auto-generated schema
- **Field Aliases**: Map API names to Python names

---

### Decision: Frozen Models

**Chose**: `frozen=True` for all API models

**Reasoning**:
- **Immutability**: Prevents accidental modification
- **Hashable**: Can use in sets/dicts
- **Thread-safe**: No mutation = no race conditions
- **Predictable**: Data doesn't change unexpectedly

---

### Decision: Provider-Based Organization

**Chose**: Organize by provider (`noaa/`, `openmeteo/`, etc.)

**Reasoning**:
- **Mirrors API structure**: Easy to find models for specific API
- **Isolation**: Changes to NOAA models don't affect Open-Meteo
- **Scalability**: Easy to add new providers

---

## Related Components

- **[Endpoints](./endpoints.md)**: Uses models for request params and response parsing
- **[Services](./services.md)**: Receives validated model instances
- **[Use Cases](./use_cases.md)**: Works with domain models

---

## Summary

**Key Takeaways**:

1. **Type Safety**: Every piece of data has a schema
2. **Validation**: Pydantic validates automatically
3. **Immutability**: Frozen models prevent modification
4. **Field Aliases**: Map API names to readable Python names
5. **Provider-Organized**: Models grouped by API provider

**When to Create Models**:
- Every API request needs a `*Params` model
- Every API response needs a `*Response` model
- Processed data may need domain models

**When Not to Use**:
- For simple primitives (use `str`, `int`, `float` directly)
- For internal-only data structures (consider plain dataclasses)

---

**Next**: See [Services](./services.md) to understand how validated models flow through the service layer.
