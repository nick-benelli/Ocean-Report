# Use Cases Component

**Purpose**: Business logic orchestration that resolves defaults, implements domain rules, and coordinates service calls.

**Location**: `src/ocean_report/use_cases/`

---

## Overview

Use Cases are the **brain** of the application. They understand the business domain and make decisions about how to fetch and process data. While Services are "dumb fetchers," Use Cases are "smart coordinators."

### Key Principle

**Use Cases implement business logic and coordinate services.**

- ✅ **Use Cases DO**: Resolve defaults, implement business rules, coordinate multiple services, format for use
- ❌ **Use Cases DON'T**: Make HTTP requests, know about SMTP, handle retries

---

## Architecture

### File Structure

```
use_cases/
├── __init__.py
├── water_temperature.py
├── tides.py
├── wind.py
└── email.py
```

### Layer Position

```
Workflows Layer (orchestrates use cases)
    ↓
Use Cases Layer  ← YOU ARE HERE
    ↓
Services Layer (dumb data fetchers)
    ↓
Endpoints Layer (API-specific implementations)
```

---

## Core Components

### 1. Water Temperature Use Case (`water_temperature.py`)

#### `get_latest_water_temp(context, station_id=None) → Tuple[float | None, datetime, str | None]`

**What It Does**:
1. **Resolves defaults**: If station_id not provided, uses config
2. **Builds params**: Creates NoaaWaterTempParams
3. **Calls service**: fetch_water_temp()
4. **Extracts value**: Gets temperature from record
5. **Returns**: (temperature, retrieval_time, data_timestamp)

**Example**:
```python
from ocean_report.use_cases.water_temperature import get_latest_water_temp

# Use configured station (business logic: default resolution)
temp, retrieval_time, data_time = get_latest_water_temp(context)
print(f"Water temp: {temp}°F (retrieved at {retrieval_time})")

# Override with specific station
temp, retrieval_time, data_time = get_latest_water_temp(
    context,
    station_id="8557380"  # Different station
)
```

**Business Logic**:
- ✅ Resolves station_id from config if not provided
- ✅ Captures retrieval timestamp
- ✅ Extracts temperature value from complex response

---

#### `format_water_temp_with_unit(temp) → str`

**What It Does**: Formats temperature with unit symbol.

**Example**:
```python
formatted = format_water_temp_with_unit(72.5)
# "72.5 °F"
```

---

### 2. Tides Use Case (`tides.py`)

#### `get_tides_for_date(context, date_str, station_id=None) → list[dict]`

**What It Does**:
1. **Resolves defaults**: Station from config if not provided
2. **Builds date range**: Single day → begin_date + end_date
3. **Calls service**: fetch_tides()
4. **Filters data**: Only daytime tides (6 AM - 8 PM)
5. **Transforms**: Converts records to simple dicts

**Example**:
```python
from ocean_report.use_cases.tides import get_tides_for_date

# Get today's tides (daytime only)
tides = get_tides_for_date(context, date_str="20260616")

for tide in tides:
    print(f"{tide['type']} tide at {tide['time']}: {tide['height']} ft")
```

**Business Logic**:
- ✅ Filters to daytime hours only (6 AM - 8 PM)
- ✅ Resolves station from config
- ✅ Converts date format (YYYYMMDD → NOAA format)
- ✅ Transforms complex records into simple dicts

---

#### `filter_daytime_tides(tides) → list`

**What It Does**: Filters tide predictions to daytime hours.

**Business Rule**: Only show tides between 6 AM and 8 PM (people don't care about 2 AM tides).

**Example**:
```python
all_tides = [
    {"time": "03:15 AM", ...},  # ❌ Filtered out (too early)
    {"time": "09:30 AM", ...},  # ✅ Kept
    {"time": "03:45 PM", ...},  # ✅ Kept
    {"time": "10:22 PM", ...},  # ❌ Filtered out (too late)
]

daytime = filter_daytime_tides(all_tides)
# Returns only 9:30 AM and 3:45 PM tides
```

---

### 3. Wind Use Case (`wind.py`)

#### `get_hourly_wind_forecast(context, date_str, latitude=None, longitude=None, beach_direction=None) → list[WindForecastEntry]`

**What It Does**:
1. **Resolves defaults**: Lat/lon/beach_direction from config if not provided
2. **Calls service**: fetch_wind_forecast()
3. **Processes data**: Extracts specific hours (8 AM, 12 PM, 4 PM, 8 PM)
4. **Classifies wind**: Offshore/Onshore/Cross-shore based on beach orientation
5. **Transforms**: Creates WindForecastEntry objects

**Example**:
```python
from ocean_report.use_cases.wind import get_hourly_wind_forecast

# Use configured location and beach orientation
wind_entries = get_hourly_wind_forecast(context, date_str="20260616")

for entry in wind_entries:
    print(f"{entry.time}: {entry.speed_mph} mph {entry.direction} ({entry.wind_type})")

# Output:
# 8 AM: 12 mph NW (Offshore) ⬇️
# 12 PM: 10 mph W (Cross-shore) ↔️
# 4 PM: 8 mph SW (Onshore) ⬆️
```

**Business Logic**:
- ✅ Extracts specific report times (8 AM, 12 PM, 4 PM, 8 PM)
- ✅ Converts 24-hour time to 12-hour format ("14:00" → "2 PM")
- ✅ Converts degrees to compass directions (315° → "NW")
- ✅ Classifies wind relative to beach orientation
- ✅ Resolves lat/lon/orientation from config

---

#### `classify_wind_type(wind_direction, beach_direction) → str`

**What It Does**: Determines if wind is offshore, onshore, or cross-shore.

**Business Rule**: 
- **Offshore**: Wind blows from land to sea (good for surfing)
- **Onshore**: Wind blows from sea to land (choppy conditions)
- **Cross-shore**: Wind blows parallel to beach

**Example**:
```python
# Beach faces southeast (140°)
beach_direction = 140

# Wind from northwest (315°)
wind_type = classify_wind_type(wind_direction=315, beach_direction=140)
# "Offshore" (good conditions!)

# Wind from southeast (140°)
wind_type = classify_wind_type(wind_direction=140, beach_direction=140)
# "Onshore" (choppy)
```

---

### 4. Email Use Case (`email.py`)

**Purpose**: Coordinate email-specific workflows (not currently used in simplified architecture).

---

## Design Principles

### Principle 1: Resolve Defaults Here

**Pattern**: Use Cases provide optional parameters with None defaults, then resolve from config.

```python
def get_latest_water_temp(
    context: ApplicationContext,
    station_id: str | None = None,  # ← Optional parameter
) -> Tuple[float | None, datetime, str | None]:
    # ✅ Resolve default from config
    if station_id is None:
        station_id = context.config.noaa.station_id
        logger.debug("Using station_id from config: %s", station_id)
    
    # Now call service with resolved value
    params = NoaaWaterTempParams(station=station_id, date="latest")
    return fetch_water_temp(context, params)
```

**Why Here?**
- Use Cases understand business context
- Keeps services simple and reusable
- Makes defaults explicit and testable

---

### Principle 2: Implement Business Rules Here

**Pattern**: Use Cases contain domain-specific logic.

```python
def filter_daytime_tides(tides):
    """Filter to tides between 6 AM and 8 PM.
    
    Business rule: Users only care about tides during beach hours.
    """
    daytime_tides = []
    for tide in tides:
        hour = extract_hour_from_time(tide["time"])
        if 6 <= hour <= 20:  # ✅ Business rule
            daytime_tides.append(tide)
    return daytime_tides
```

---

### Principle 3: Coordinate Multiple Services

**Pattern**: Use Cases can call multiple services to build complete workflows.

```python
def get_complete_beach_report(context, date_str):
    """Fetch all data needed for beach report.
    
    Orchestrates multiple service calls.
    """
    # Call multiple services
    water_temp, _, _ = get_latest_water_temp(context)
    tides = get_tides_for_date(context, date_str)
    wind = get_hourly_wind_forecast(context, date_str)
    
    # Combine into report
    return {
        "water_temp": water_temp,
        "tides": tides,
        "wind": wind,
    }
```

---

### Principle 4: Transform Data for Consumers

**Pattern**: Use Cases convert service responses into consumer-friendly formats.

```python
def get_hourly_wind_forecast(context, date_str, ...):
    # Service returns complex nested response
    forecast = fetch_wind_forecast(context, params)
    
    # ✅ Transform into simple list of WindForecastEntry objects
    entries = []
    for i, time_str in enumerate(forecast.hourly.time):
        if time_str in target_times:
            entry = WindForecastEntry(
                time=format_hour(time_str),  # "14:00" → "2 PM"
                speed_mph=forecast.hourly.wind_speed_10m[i],
                direction=degrees_to_compass(forecast.hourly.wind_direction_10m[i]),
                wind_type=classify_wind_type(...),
                direction_degrees=forecast.hourly.wind_direction_10m[i]
            )
            entries.append(entry)
    
    return entries  # Clean, simple list
```

---

## Error Handling Strategy

### Use Cases Decide How to Handle Errors

**Pattern**: Use Cases catch service errors and decide recovery strategy.

```python
def get_latest_water_temp(context, station_id=None):
    try:
        # Call service
        params = NoaaWaterTempParams(...)
        record = fetch_water_temp(context, params)
        
        if record is None:
            logger.warning("No water temperature data available")
            return None, datetime.now(), None
        
        return record.temperature, datetime.now(), record.timestamp
        
    except ApiClientError as e:
        # ✅ Use case decides: log and return None (graceful degradation)
        logger.error(f"Failed to fetch water temperature: {e}")
        return None, datetime.now(), None
```

**Options**:
1. **Return None** (graceful degradation)
2. **Retry** with exponential backoff
3. **Use cached data** from previous fetch
4. **Raise** to workflow layer (fail entire report)

---

## Usage Patterns

### Pattern 1: Simple Use Case Call

```python
from ocean_report.use_cases.water_temperature import get_latest_water_temp

context = create_application_context()

# Use defaults from config
temp, retrieval_time, data_time = get_latest_water_temp(context)

if temp:
    print(f"Water temperature: {temp}°F")
else:
    print("Water temperature unavailable")
```

---

### Pattern 2: Override Defaults

```python
# Override with specific station
temp, _, _ = get_latest_water_temp(context, station_id="8557380")

# Override location for wind
wind = get_hourly_wind_forecast(
    context,
    date_str="20260616",
    latitude=40.7,  # NYC instead of configured location
    longitude=-74.0,
    beach_direction=90  # East-facing
)
```

---

### Pattern 3: Workflow Orchestration

```python
def generate_daily_report(context):
    """Orchestrate all use cases to generate report."""
    date_str = datetime.now().strftime("%Y%m%d")
    
    # Call use cases to fetch data
    water_temp, _, _ = get_latest_water_temp(context)
    tides = get_tides_for_date(context, date_str)
    wind = get_hourly_wind_forecast(context, date_str)
    
    # Format data into EmailTemplateData model
    template_data = format_report_data(raw_data)
    
    # Render email using Jinja2 template
    body = render_email_template(template_data)
    send_email(..., body=body)
```

---

## Testing Guidelines

### Unit Tests: Business Logic

```python
def test_filter_daytime_tides():
    tides = [
        {"time": "03:15 AM"},  # Too early
        {"time": "09:30 AM"},  # Good
        {"time": "03:45 PM"},  # Good
        {"time": "10:22 PM"},  # Too late
    ]
    
    daytime = filter_daytime_tides(tides)
    
    assert len(daytime) == 2
    assert daytime[0]["time"] == "09:30 AM"
    assert daytime[1]["time"] == "03:45 PM"

def test_classify_wind_offshore():
    # Beach faces SE (140°), wind from NW (315°)
    wind_type = classify_wind_type(315, 140)
    assert wind_type == "Offshore"
```

---

### Integration Tests: With Mocked Services

```python
from unittest.mock import patch, Mock

@patch('ocean_report.use_cases.water_temperature.fetch_water_temp')
def test_get_latest_water_temp_with_default(mock_fetch):
    # Mock service return
    mock_record = Mock()
    mock_record.temperature = 72.5
    mock_record.timestamp = "2026-06-16 12:00"
    mock_fetch.return_value = mock_record
    
    # Mock context
    context = Mock()
    context.config.noaa.station_id = "8534720"
    
    # Call use case (no station_id provided)
    temp, _, data_time = get_latest_water_temp(context)
    
    # Verify default was used
    assert temp == 72.5
    mock_fetch.assert_called_once()
    call_args = mock_fetch.call_args
    assert call_args[1]["params"].station == "8534720"  # Used default
```

---

### End-to-End Tests: Real Services

```python
@pytest.mark.integration
def test_get_latest_water_temp_real():
    context = create_application_context()
    
    temp, retrieval_time, data_time = get_latest_water_temp(context)
    
    assert temp is not None
    assert isinstance(temp, float)
    assert 30 <= temp <= 90  # Reasonable range
    assert retrieval_time <= datetime.now()
```

---

## When to Add a New Use Case

**Add a new use case when**:
- You need to implement a new business workflow
- You need to coordinate multiple services
- You need to apply business rules to data

**Example**: Adding a use case for surf conditions:

```python
# use_cases/surf_conditions.py

def get_surf_conditions(context, date_str):
    """Determine surf conditions based on wind, waves, tides.
    
    Business logic: Combine multiple data sources to rate surf conditions.
    """
    # Fetch data from services
    wind = get_hourly_wind_forecast(context, date_str)
    tides = get_tides_for_date(context, date_str)
    # waves = get_wave_forecast(context, date_str)  # Future
    
    # Apply business rules
    conditions = []
    for hour in [8, 12, 16, 20]:
        wind_entry = find_wind_for_hour(wind, hour)
        tide_state = find_tide_state(tides, hour)
        
        rating = rate_surf_conditions(
            wind_type=wind_entry.wind_type,
            wind_speed=wind_entry.speed_mph,
            tide_state=tide_state,
        )
        
        conditions.append({
            "hour": hour,
            "rating": rating,  # "Excellent", "Good", "Fair", "Poor"
            "explanation": explain_rating(...)
        })
    
    return conditions
```

---

## Common Pitfalls

### Pitfall 1: Business Logic in Services

```python
# ❌ Wrong (in service)
def fetch_tides(context, params):
    endpoint = TidesEndpoint(context.client)
    response = endpoint.fetch(params)
    # ❌ Filtering is business logic!
    return [t for t in response.predictions if 6 <= get_hour(t.timestamp) <= 20]

# ✅ Right (in use case)
def get_tides_for_date(context, date_str):
    params = NoaaTidesParams(...)
    all_tides = fetch_tides(context, params)  # Service returns all
    return filter_daytime_tides(all_tides)  # Use case filters
```

---

### Pitfall 2: Hardcoded Values Instead of Config

```python
# ❌ Wrong
def get_latest_water_temp(context):
    station_id = "8534720"  # ❌ Hardcoded
    ...

# ✅ Right
def get_latest_water_temp(context, station_id=None):
    if station_id is None:
        station_id = context.config.noaa.station_id  # ✅ From config
    ...
```

---

### Pitfall 3: Tight Coupling to Presentation

```python
# ❌ Wrong (use case returns formatted string)
def get_latest_water_temp(context):
    ...
    return f"Water Temperature: {temp}°F"  # ❌ Presentation logic

# ✅ Right (use case returns data)
def get_latest_water_temp(context):
    ...
    return temp, retrieval_time, data_time  # ✅ Raw data
    
# Formatting happens in Emailer layer
formatted = format_water_temp(temp)  # ✅ Separate concern
```

---

## Design Decisions

### Decision: Optional Parameters with None Defaults

**Chose**: `param: str | None = None`, resolve from config inside function

**Reasoning**:
- **Convenient**: `get_latest_water_temp(context)` uses defaults
- **Flexible**: `get_latest_water_temp(context, station_id="...")` overrides
- **Testable**: Easy to inject test values
- **Explicit**: Clear what can be customized

---

### Decision: Return Tuples for Multiple Values

**Chose**: `(temp, retrieval_time, data_time)` instead of dict

**Reasoning**:
- **Type Hints**: `Tuple[float | None, datetime, str | None]`
- **Unpacking**: `temp, _, _ = get_latest_water_temp(context)`
- **Simple**: No need for complex return objects for 2-3 values

---

### Decision: Use Cases Don't Know About HTTP/SMTP

**Chose**: Use Cases call services, not endpoints or API client

**Reasoning**:
- **Abstraction**: Use Cases shouldn't know about HTTP verbs, retries, SMTP
- **Testability**: Easy to mock services
- **Separation**: Integration concerns live in lower layers

---

## Related Components

- **[Services](./services.md)**: Called by use cases to fetch data
- **[Workflows](./workflows.md)**: Orchestrates multiple use cases
- **[Models](./models.md)**: Use cases work with typed models
- **[Utils](./utils.md)**: Use cases use utility functions for calculations

---

## Summary

**Key Takeaways**:

1. **Business Logic Lives Here**: Use cases implement domain rules
2. **Resolve Defaults**: From config, not hardcoded
3. **Coordinate Services**: Orchestrate multiple service calls
4. **Transform Data**: Convert service responses for consumers
5. **Handle Errors Gracefully**: Decide recovery strategies

**When to Use**:
- You need to implement business logic
- You need to coordinate multiple services
- You need to resolve configuration defaults
- You need to transform data for specific consumers

**When Not to Use**:
- For making HTTP requests (use Services)
- For formatting emails (use Emailer)
- For mathematical calculations (use Utils)
- For top-level orchestration (use Workflows)

---

**Next**: See [Workflows](./workflows.md) to understand how use cases are orchestrated at the application level.
