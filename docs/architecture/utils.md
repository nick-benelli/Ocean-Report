# Utils Component

**Purpose**: Shared utility functions for date handling, wind calculations, and other common operations.

**Location**: `src/ocean_report/utils/`

---

## Overview

The Utils component contains pure, reusable functions that don't fit into other layers. These are typically mathematical calculations, date manipulations, or data transformations used across multiple components.

### Key Principle

**Utils are pure functions with no side effects.**

- ✅ **Utils DO**: Calculate, transform, format, convert
- ❌ **Utils DON'T**: Make API calls, access config, modify global state, perform I/O

---

## Architecture

### File Structure

```
utils/
├── __init__.py
├── date_utils.py        # Date and time calculations
└── wind_utils.py        # Wind direction and classification
```

---

## Core Components

### 1. Date Utils (`date_utils.py`)

#### Purpose: Date calculations for seasonal recipient selection.

#### `get_memorial_day(year) → datetime.date`

**What It Does**: Calculates Memorial Day (last Monday of May).

**Example**:
```python
from ocean_report.utils.date_utils import get_memorial_day

memorial_day = get_memorial_day(2026)
# datetime.date(2026, 5, 25)
```

**Algorithm**:
1. Find last day of May
2. Find last Monday in May

---

#### `get_labor_day(year) → datetime.date`

**What It Does**: Calculates Labor Day (first Monday of September).

**Example**:
```python
from ocean_report.utils.date_utils import get_labor_day

labor_day = get_labor_day(2026)
# datetime.date(2026, 9, 7)
```

**Algorithm**:
1. Find first day of September
2. Find first Monday in September

---

#### `determine_is_summer(today, memorial_offset, labor_offset) → bool`

**What It Does**: Determines if a given date falls in the "summer" season.

**Business Logic**: Summer = Memorial Day (+ offset) to Labor Day (+ offset)

**Example**:
```python
from ocean_report.utils.date_utils import determine_is_summer
from datetime import date

# Check if July 4th, 2026 is in summer
is_summer = determine_is_summer(
    today=date(2026, 7, 4),
    memorial_offset=-14,  # Start 14 days before Memorial Day
    labor_offset=0        # End on Labor Day
)
# True

# Check if October 1st, 2026 is in summer
is_summer = determine_is_summer(
    today=date(2026, 10, 1),
    memorial_offset=-14,
    labor_offset=0
)
# False
```

**Usage in Application**:
```python
from ocean_report.config.loader import get_settings

config = get_settings()
is_summer = determine_is_summer(
    today=date.today(),
    memorial_offset=config.summer.memorial_day_offset,
    labor_offset=config.summer.labor_day_offset
)

# Use to select recipient list
if is_summer:
    url = config.email.recipient_urls.main
else:
    url = config.email.recipient_urls.offseason
```

---

### 2. Wind Utils (`wind_utils.py`)

#### Purpose: Wind direction calculations and classifications.

#### `degrees_to_compass(degrees) → str`

**What It Does**: Converts wind direction degrees to 16-point compass notation.

**Example**:
```python
from ocean_report.utils.wind_utils import degrees_to_compass

direction = degrees_to_compass(0)      # "N"
direction = degrees_to_compass(45)     # "NE"
direction = degrees_to_compass(90)     # "E"
direction = degrees_to_compass(135)    # "SE"
direction = degrees_to_compass(180)    # "S"
direction = degrees_to_compass(225)    # "SW"
direction = degrees_to_compass(270)    # "W"
direction = degrees_to_compass(315)    # "NW"
direction = degrees_to_compass(348)    # "N" (wraps around)
```

**Algorithm**:
1. Divide compass into 16 sectors (22.5° each)
2. Find which sector the degrees fall into
3. Return corresponding label

**16-Point Compass**:
```
N   (0°)     NNE (22.5°)  NE  (45°)    ENE (67.5°)
E   (90°)    ESE (112.5°) SE  (135°)   SSE (157.5°)
S   (180°)   SSW (202.5°) SW  (225°)   WSW (247.5°)
W   (270°)   WNW (292.5°) NW  (315°)   NNW (337.5°)
```

---

#### `classify_wind(wind_degrees, beach_degrees) → str`

**What It Does**: Classifies wind as Offshore, Onshore, or Cross-shore relative to beach.

**Business Logic**:
- **Offshore**: Wind blows from land → sea (perpendicular, away from beach)
- **Onshore**: Wind blows from sea → land (perpendicular, toward beach)
- **Cross-shore**: Wind blows parallel to beach

**Example**:
```python
from ocean_report.utils.wind_utils import classify_wind

beach_direction = 140  # Beach faces southeast

# Wind from northwest (opposite of beach direction)
classify_wind(wind_degrees=315, beach_degrees=140)
# "Offshore" (good for surfing!)

# Wind from southeast (same as beach direction)
classify_wind(wind_degrees=140, beach_degrees=140)
# "Onshore" (choppy)

# Wind from northeast (perpendicular to beach)
classify_wind(wind_degrees=45, beach_degrees=140)
# "Cross-shore" (sideways)
```

**Algorithm**:
1. Calculate angle difference between wind and beach
2. Normalize to 0-180° range
3. Classify based on thresholds:
   - 0-45°: Offshore
   - 45-135°: Cross-shore
   - 135-180°: Onshore

---

#### `format_hour_12(hour_24) → str`

**What It Does**: Converts 24-hour time to 12-hour format with AM/PM.

**Example**:
```python
from ocean_report.utils.wind_utils import format_hour_12

format_hour_12(8)   # "8 AM"
format_hour_12(12)  # "12 PM"
format_hour_12(14)  # "2 PM"
format_hour_12(20)  # "8 PM"
format_hour_12(0)   # "12 AM"
```

---

## Design Principles

### Principle 1: Pure Functions

**All utility functions are pure - same input always produces same output, no side effects.**

```python
# ✅ Pure function
def degrees_to_compass(degrees: float) -> str:
    # Only depends on input parameter
    # No API calls, no config access, no global state
    index = round(degrees / 22.5) % 16
    return COMPASS_POINTS[index]

# ❌ Impure function (don't do this in utils)
def degrees_to_compass():
    # ❌ Accesses global state
    degrees = get_current_wind_direction()
    # ❌ Makes API call
    return fetch_compass_label(degrees)
```

---

### Principle 2: No Dependencies on Application Layers

**Utils don't import from Use Cases, Services, Endpoints, or Config.**

```python
# ❌ Wrong - utils importing from higher layers
from ocean_report.use_cases.wind import get_hourly_wind_forecast
from ocean_report.config.loader import get_settings

# ✅ Right - utils are self-contained
def degrees_to_compass(degrees: float) -> str:
    # Only uses standard library
    ...
```

**Dependency Direction**:
```
Use Cases  ────→  Utils  ✅
Services   ────→  Utils  ✅
Utils      ────→  Use Cases  ❌
Utils      ────→  Services   ❌
```

---

### Principle 3: Well-Tested

**Utils should have high test coverage since they're used everywhere.**

```python
def test_degrees_to_compass_cardinal_directions():
    assert degrees_to_compass(0) == "N"
    assert degrees_to_compass(90) == "E"
    assert degrees_to_compass(180) == "S"
    assert degrees_to_compass(270) == "W"

def test_degrees_to_compass_wrapping():
    assert degrees_to_compass(360) == "N"
    assert degrees_to_compass(365) == "N"
    assert degrees_to_compass(-10) == "N"
```

---

## Usage Patterns

### Pattern 1: Import and Call

```python
from ocean_report.utils.wind_utils import degrees_to_compass, classify_wind

# Convert degrees to compass direction
direction = degrees_to_compass(315)
print(direction)  # "NW"

# Classify wind relative to beach
wind_type = classify_wind(wind_degrees=315, beach_degrees=140)
print(wind_type)  # "Offshore"
```

---

### Pattern 2: Use in Transformations

```python
from ocean_report.utils.wind_utils import degrees_to_compass, format_hour_12

def process_wind_data(raw_forecast):
    """Transform raw API data using utils."""
    processed = []
    for entry in raw_forecast:
        processed.append({
            "time": format_hour_12(entry["hour"]),  # ✅ Using util
            "direction": degrees_to_compass(entry["direction_deg"]),  # ✅ Using util
            "speed": entry["speed_mph"]
        })
    return processed
```

---

### Pattern 3: Configuration-Driven Calculations

```python
from ocean_report.utils.date_utils import determine_is_summer
from ocean_report.config.loader import get_settings

config = get_settings()

is_summer = determine_is_summer(
    today=date.today(),
    memorial_offset=config.summer.memorial_day_offset,  # From config
    labor_offset=config.summer.labor_day_offset          # From config
)
```

---

## Testing Guidelines

### Unit Tests: Pure Logic

```python
def test_classify_wind_offshore():
    # Beach faces SE (140°), wind from NW (315°)
    result = classify_wind(wind_degrees=315, beach_degrees=140)
    assert result == "Offshore"

def test_classify_wind_onshore():
    # Beach faces SE (140°), wind from SE (140°)
    result = classify_wind(wind_degrees=140, beach_degrees=140)
    assert result == "Onshore"

def test_classify_wind_cross_shore():
    # Beach faces SE (140°), wind from NE (45°)
    result = classify_wind(wind_degrees=45, beach_degrees=140)
    assert result == "Cross-shore"
```

---

### Edge Cases

```python
def test_degrees_to_compass_edge_cases():
    # Exactly on boundary
    assert degrees_to_compass(22.5) == "NNE"
    
    # Negative degrees
    assert degrees_to_compass(-45) == "NW"
    
    # Greater than 360
    assert degrees_to_compass(405) == "NE"
    
    # Zero
    assert degrees_to_compass(0) == "N"
```

---

## When to Add New Utils

**Add a new utility function when**:
- You have pure calculation logic used in multiple places
- You need mathematical transformations
- You have date/time calculations
- You need data format conversions

**Example**: Adding a temperature conversion util:

```python
# utils/temperature_utils.py

def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit.
    
    Formula: F = C * 9/5 + 32
    """
    return celsius * 9 / 5 + 32

def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convert Fahrenheit to Celsius.
    
    Formula: C = (F - 32) * 5/9
    """
    return (fahrenheit - 32) * 5 / 9
```

---

## Common Pitfalls

### Pitfall 1: Utils That Access Config

```python
# ❌ Wrong - util accessing config
def is_summer_season():
    config = get_settings()  # ❌ Util shouldn't access config
    return determine_is_summer(
        date.today(),
        config.summer.memorial_day_offset,
        config.summer.labor_day_offset
    )

# ✅ Right - caller passes config values
def determine_is_summer(today, memorial_offset, labor_offset):
    # ✅ Pure function, all inputs are parameters
    ...
```

---

### Pitfall 2: Utils That Make API Calls

```python
# ❌ Wrong - util making API call
def get_current_wind_classification():
    wind_data = fetch_wind_forecast()  # ❌ API call!
    return classify_wind(wind_data.direction, 140)

# ✅ Right - caller fetches data, util just calculates
def classify_wind(wind_degrees, beach_degrees):
    # ✅ Pure calculation
    ...
```

---

### Pitfall 3: Utils With Side Effects

```python
# ❌ Wrong - util with side effects
def log_and_classify_wind(wind_degrees, beach_degrees):
    logger.info(f"Classifying wind: {wind_degrees}°")  # ❌ Side effect!
    return classify_wind(wind_degrees, beach_degrees)

# ✅ Right - caller handles logging
def classify_wind(wind_degrees, beach_degrees):
    # ✅ No side effects, just returns result
    ...

# Caller decides to log
result = classify_wind(315, 140)
logger.info(f"Wind classification: {result}")
```

---

## Design Decisions

### Decision: Separate Files by Domain

**Chose**: `date_utils.py`, `wind_utils.py` instead of monolithic `utils.py`

**Reasoning**:
- **Organization**: Related functions grouped together
- **Discoverability**: Easy to find date functions
- **Maintainability**: Changes to wind utils don't affect date utils
- **Scalability**: Easy to add new util categories

---

### Decision: No Class-Based Utils

**Chose**: Module-level functions instead of utility classes

**Reasoning**:
- **Simplicity**: Functions are simpler than classes for pure calculations
- **No State**: Utils don't need instance state
- **Easy Import**: `from utils import func` vs `from utils import UtilClass; UtilClass().func()`
- **Python Idiom**: Functional approach is more Pythonic for utilities

---

### Decision: Explicit Parameters, No Defaults

**Chose**: All parameters required (no defaults)

**Reasoning**:
- **Explicit**: Caller must provide all inputs
- **Testable**: Easy to see what function needs
- **Reusable**: Works in different contexts
- **Clear**: No hidden assumptions

```python
# ✅ Good - explicit parameters
def determine_is_summer(today, memorial_offset, labor_offset):
    ...

# ❌ Bad - hidden defaults
def determine_is_summer(today, memorial_offset=-14, labor_offset=0):
    # ❌ Why these defaults? Should be caller's decision
    ...
```

---

## Related Components

- **[Use Cases](./use_cases.md)**: Calls utils for calculations
- **[Services](./services.md)**: May use utils for data transformation
- **[Workflows](./workflows.md)**: Uses utils for date/time logic
- **[Emailer](./emailer.md)**: Uses utils for formatting

---

## Summary

**Key Takeaways**:

1. **Pure Functions**: No side effects, same input → same output
2. **No Dependencies**: Don't import from Use Cases, Services, Config
3. **Well-Tested**: High test coverage for reliability
4. **Domain-Organized**: Separate files by functional area
5. **Reusable**: Used across multiple layers

**When to Use**:
- Pure calculations (math, conversions)
- Date/time manipulations
- Data transformations
- Format conversions

**When Not to Use**:
- API calls (use Services)
- Business logic (use Use Cases)
- Configuration access (pass config values as parameters)
- I/O operations (use appropriate layer)

---

**Next**: See [Workflows](./workflows.md) to understand how all components are orchestrated at the top level.
