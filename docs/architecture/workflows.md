# Workflows Component

**Purpose**: Top-level orchestration that coordinates use cases, data formatting, and email delivery to execute the complete ocean report workflow.

**Location**: `src/ocean_report/workflows/`

---

## Overview

The Workflows component is the **conductor** of the application. It sits at the highest level, orchestrating all other components to execute end-to-end business workflows. Think of it as the "main" function that ties everything together.

### What It Does

**For Non-Technical Readers:**

The Workflow is like a recipe that says:
1. Load configuration
2. Fetch water temperature
3. Fetch tide predictions
4. Fetch wind forecast
5. Format everything into an email
6. Send the email (or just preview it)

It's the step-by-step instructions for the entire process.

**For Technical Readers:**

- Entry point for application execution
- Creates ApplicationContext
- Coordinates multiple use cases
- Handles data aggregation and formatting
- Manages email recipient selection
- Controls email delivery or preview
- Centralized logging and error handling
- Captures timing metrics

---

## Architecture

### File Structure

```
workflows/
├── __init__.py
├── report_runner.py     # Main workflow: fetch data + send email
├── models.py            # Workflow-specific models
├── data/
│   ├── __init__.py
│   ├── fetcher.py       # Data fetching orchestration
│   └── formatter.py     # Data formatting to EmailTemplateData
└── email/
    ├── __init__.py
    ├── preview.py       # Email preview (console + file output)
    ├── recipients.py    # Recipient list management
    ├── sender.py        # Email sending orchestration
    ├── subject.py       # Email subject formatting
    └── validator.py     # Email credential validation
```

### Layer Position

```
Entry Points (scripts)
    ↓
Workflows Layer  ← YOU ARE HERE (top of the stack)
    ↓
Use Cases Layer (business logic)
    ↓
Services Layer (data fetching)
    ↓
Endpoints Layer (API calls)
    ↓
API Client Layer (HTTP transport)
```

---

## Core Components

### 1. Report Runner (`report_runner.py`)

**Purpose**: Main orchestration function that executes the complete ocean report workflow.

#### `run_report(cfg_path, run_email, test) → None`

**What It Does**:
1. **Initialize**: Load config, setup logging
2. **Get Recipients**: Fetch email recipient list
3. **Fetch Data**: Call use cases for water temp, tides, wind
4. **Format Data**: Convert to email sections
5. **Generate Email**: Build complete email body
6. **Deliver/Preview**: Send email or print to console

**Signature**:
```python
def run_report(
    *,
    cfg_path: Union[str, Path] = None,  # Optional custom config path
    run_email: bool = True,              # True = send, False = preview
    test: bool = False                   # True = use test recipients
) -> None:
```

**Example Usage**:
```python
from ocean_report.workflows.report_runner import run_report

# Production: send email to real recipients
run_report(run_email=True, test=False)

# Testing: preview in console
run_report(run_email=False, test=True)

# Custom config
run_report(cfg_path="config/prod.yaml", run_email=True, test=False)
```

**Complete Flow**:
```python
def run_report(...):
    # === STEP 1: Initialization ===
    logger.info("Starting Ocean Report Email Process...")
    context = create_application_context(config_path=cfg_path)
    configure_logger_from_settings(context.config)
    
    # === STEP 2: Get Recipients ===
    logger.info("Fetching email recipients...")
    bcc_recipients = get_bcc_recipients(
        test=test,
        use_url=context.config.email.use_recipient_url,
        fallback_recipients=context.config.email.recipients or ""
    )
    
    # === STEP 3: Fetch Data ===
    logger.info("Fetching weather data from APIs...")
    fetch_params = FetchParams(
        station_id=context.config.noaa.station_id,
        date_str=datetime.now().strftime("%Y%m%d"),
        latitude=context.config.location.latitude,
        longitude=context.config.location.longitude,
        beach_facing_deg=context.config.location.beach_orientation_degrees,
        forecast_times={"08:00", "12:00", "15:00", "18:00"}
    )
    raw_data = fetch_raw_data(context, fetch_params)
    
    # === STEP 4: Format Data ===
    logger.info("Formatting data to EmailTemplateData...")
    email_data = format_report_data(raw_data)
    
    # === STEP 5: Render Email ===
    logger.info("Rendering email from template...")
    email_body = render_email_template(
        data=email_data,
        template_path=context.config.reporting.template_path
    )
    email_subject = format_email_subject(
        subject_name=context.config.reporting.subject,
        today=date.today(),
        test=test
    )
    
    # === STEP 6: Deliver or Preview ===
    logger.info("Sending email..." if run_email else "Displaying email...")
    send_or_preview_email(
        context=context,
        run_email=run_email,
        subject=email_subject,
        body=email_body,
        bcc_recipients=bcc_recipients
    )
    
    logger.info("Ocean Report workflow completed successfully!")
```

---

### 2. Data Fetcher (`data/fetcher.py`)

**Purpose**: Coordinate data fetching from multiple use cases.

#### `fetch_raw_data(context, fetch_params) → RawReportData`

**What It Does**: Calls all use cases in sequence and returns aggregated data.

**Example**:
```python
from ocean_report.workflows.data.fetcher import fetch_raw_data

fetch_params = FetchParams(
    station_id="8534720",
    date_str="20260616",
    latitude=39.58,
    longitude=-74.22,
    beach_direction=140
)

data = fetch_raw_data(context, fetch_params)

# Access fetched data
print(data.water_temp)      # 72.5
print(data.tides)           # [{"time": "7:32 AM", ...}, ...]
print(data.wind_entries)    # [WindForecastEntry(...), ...]
```

**Structure**:
```python
@dataclass
class RawReportData:
    water_temp: float | None
    water_temp_time: datetime
    water_temp_data_time: str | None
    tides: list[dict]
    wind_entries: list[WindForecastEntry]
```

---

### 3. Data Formatter (`data/formatter.py`)

**Purpose**: Convert raw data into EmailTemplateData for template rendering.

#### `format_report_data(raw_data) → EmailTemplateData`

**What It Does**: Transforms raw data into structured EmailTemplateData model.

**Example**:
```python
from ocean_report.workflows.data.formatter import format_report_data

email_data = format_report_data(raw_data)

# Returns EmailTemplateData with formatted fields:
# EmailTemplateData(
#     long_date="Monday, June 16, 2026",
#     water_temp="72.5 °F",
#     tide_info="⬇️ Low Tide at 8:23 AM — 0.3 ft\n...",
#     wind_info="•  8 AM:  4.8 mph ESE (108.0°) → Cross/Onshore\n...",
#     station_name="Atlantic City Station 8534720",
#     station_city="Atlantic City",
#     wind_provider="Open-Meteo",
#     date_retrieved="Jun 16 at 6:45 AM",
#     water_temp_measured_at_date="Jun 16 at 6:30 AM"
# )
```

---

### 4. Email Recipient Manager (`email/recipients.py`)

**Purpose**: Determine which recipient list to use.

#### `get_bcc_recipients(test, use_url, fallback_recipients) → list[str]`

**What It Does**: Selects appropriate recipient list based on mode and configuration.

**Logic**:
```python
def get_bcc_recipients(test, use_url, fallback_recipients):
    if use_url:
        # Fetch from URL (uses seasonal or test URLs)
        recipients_str = get_email_recipients(test_recips=test)
    else:
        # Use fallback from config
        recipients_str = fallback_recipients or ""
    
    # Parse and return as list
    return [email.strip() for email in recipients_str.split(",") if email.strip()]
```

---

### 5. Email Sender (`email/sender.py`)

**Purpose**: Orchestrate email sending with proper error handling.

#### `send_or_preview_email(context, run_email, subject, body, bcc_recipients)`

**What It Does**: Either sends email or prints preview based on mode.

**Example**:
```python
from ocean_report.workflows.email.sender import send_or_preview_email

send_or_preview_email(
    context=context,
    run_email=True,
    subject="Daily Water Report",
    body="Email content here...",
    bcc_recipients=["user1@example.com", "user2@example.com"]
)
```

---

### 6. Email Subject Formatter (`email/subject.py`)

**Purpose**: Format email subject line with date and optional test prefix. The base subject text is provided from configuration.

#### `format_email_subject(subject_name, today, test=False) → str`

**Parameters**:
- `subject_name`: Base subject text from `config.reporting.subject`
- `today`: Date to append to subject
- `test`: Whether to add "TEST:" prefix

**Example**:
```python
from ocean_report.workflows.email.subject import format_email_subject
from datetime import date

# Production
subject = format_email_subject(
    subject_name="🌊 LBI Daily Water Report",
    today=date.today(),
    test=False
)
# "🌊 LBI Daily Water Report: 2026-06-16"

# Test mode
subject = format_email_subject(
    subject_name="🌊 LBI Daily Water Report",
    today=date.today(),
    test=True
)
# "TEST: 🌊 LBI Daily Water Report: 2026-06-16"
```

---

### 7. Email Preview (`email/preview.py`)

**Purpose**: Write email preview to console and HTML/text files for testing.

#### `write_email_preview(subject, body, sender_email, email_recipients, bcc_recipients) → Path`

**What It Does**: Writes email preview to both console and files in `logs/email-previews/`.

**Creates**:
- Plain text file: `email_preview_YYYYMMDD_HHMMSS.txt`
- HTML file: `email_preview_YYYYMMDD_HHMMSS.html` (formatted for browser viewing)

**Example**:
```python
from ocean_report.workflows.email.preview import write_email_preview

html_path = write_email_preview(
    subject="Daily Water Report",
    body="Email content...",
    sender_email="surf@example.com",
    email_recipients="",
    bcc_recipients=["user1@example.com", "user2@example.com"]
)

print(f"Preview saved to: {html_path}")
# Opens in browser for easy review
```

---

### 8. Email Validator (`email/validator.py`)

**Purpose**: Validate email credentials before sending.

#### `validate_email_credentials(sender, password) → None`

**What It Does**: Ensures required email credentials are configured.

**Example**:
```python
from ocean_report.workflows.email.validator import validate_email_credentials

# Raises ValueError if missing
validate_email_credentials(
    sender="surf@example.com",
    password="app_password_123"
)
```

---

## Workflow Models (`models.py`)

### FetchParams

**Purpose**: Bundle all parameters needed for data fetching.

```python
@dataclass
class FetchParams:
    station_id: str
    date_str: str              # YYYYMMDD format
    latitude: float
    longitude: float
    beach_facing_deg: float    # Beach orientation in degrees
    forecast_times: set[str]   # Times to fetch (e.g., {"08:00", "12:00"})
```

### RawReportData

**Purpose**: Container for all fetched data before formatting.

```python
@dataclass
class RawReportData:
    tides: list                      # List of NoaaTidePredictionRecord
    tide_timestamp: datetime
    water_temp: float | None
    water_temp_timestamp: datetime
    water_temp_data_time: str | None # Sensor measurement time
    wind_forecast: list              # List of WindForecastEntry dicts
    wind_timestamp: datetime | None
```

---

## Design Principles

### Principle 1: Top-Level Orchestration Only

**Workflows don't implement business logic - they coordinate.**

```python
# ✅ Good - workflow coordinates
def run_report(context, ...):
    # Coordinate use cases
    water_temp, _, _ = get_latest_water_temp(context)  # ← Use case handles logic
    tides = get_tides_for_date(context, date_str)       # ← Use case handles logic
    
    # Coordinate formatting
    sections = format_report_data(...)
    
    # Coordinate sending
    send_or_preview_email(...)

# ❌ Bad - workflow implementing business logic
def run_report(context, ...):
    # ❌ Workflow shouldn't filter tides
    all_tides = fetch_tides(context, ...)
    daytime_tides = [t for t in all_tides if is_daytime(t)]  # ❌ Business logic!
```

---

### Principle 2: Clear Step Progression

**Workflow should read like a recipe with clear steps.**

```python
def run_report(...):
    # Step 1
    logger.info("[STEP 1/6] Loading configuration...")
    context = create_application_context(...)
    
    # Step 2
    logger.info("[STEP 2/6] Fetching email recipients...")
    recipients = get_bcc_recipients(...)
    
    # Step 3
    logger.info("[STEP 3/6] Fetching weather data...")
    data = fetch_raw_data(...)
    
    # And so on...
```

**Benefits**:
- Easy to follow execution flow
- Clear progress indicators in logs
- Easy to debug (know which step failed)

---

### Principle 3: Centralized Error Handling

**Workflow handles top-level errors and decides recovery strategy.**

```python
def run_report(...):
    try:
        # Execute workflow steps
        ...
        
    except ApiClientError as e:
        logger.error(f"API error during report generation: {e}")
        # Decide: retry, send partial report, or fail completely
        
    except Exception as e:
        logger.exception("Unexpected error in workflow")
        raise
```

---

### Principle 4: Performance Monitoring

**Track timing for each major step.**

```python
def run_report(...):
    workflow_start = time.time()
    
    logger.info("[STEP 3/6] Fetching weather data...")
    step_start = time.time()
    data = fetch_raw_data(...)
    logger.info(f"Data fetched in {time.time() - step_start:.2f} seconds")
    
    # ...
    
    logger.info(f"Total workflow time: {time.time() - workflow_start:.2f} seconds")
```

---

## Usage Patterns

### Pattern 1: Production Execution

```python
from ocean_report.workflows.report_runner import run_report

# Send real email to production recipients
run_report(
    run_email=True,   # Send email
    test=False        # Production recipients
)
```

---

### Pattern 2: Testing/Development

```python
# Preview email without sending
run_report(
    run_email=False,  # Preview only
    test=True         # Test recipients
)
```

---

### Pattern 3: Custom Configuration

```python
# Use different config file
run_report(
    cfg_path="config/staging.yaml",
    run_email=True,
    test=False
)
```

---

### Pattern 4: Scheduled Execution (GitHub Actions)

```yaml
# .github/workflows/daily-report.yml
name: Daily Water Report
on:
  schedule:
    - cron: '45 10 * * *'  # 6:45 AM ET (10:45 UTC)

jobs:
  send-report:
    runs-on: ubuntu-latest
    steps:
      - name: Run report
        run: python scripts/run_report.py
        env:
          RUN_EMAIL: "true"
          TEST: "false"
```

---

## Testing Guidelines

### Unit Tests: Workflow Logic

```python
from unittest.mock import patch, Mock
from ocean_report.models.email import EmailTemplateData

@patch('ocean_report.workflows.report_runner.fetch_raw_data')
@patch('ocean_report.workflows.report_runner.format_report_data')
@patch('ocean_report.workflows.report_runner.render_email_template')
@patch('ocean_report.workflows.report_runner.send_or_preview_email')
def test_run_report_preview_mode(mock_send, mock_render, mock_format, mock_fetch):
    # Mock data fetching
    mock_fetch.return_value = Mock()  # RawReportData
    
    # Mock formatting
    mock_format.return_value = EmailTemplateData(
        long_date="Monday, June 16, 2026",
        water_temp="72.5 °F",
        tide_info="Tide data",
        wind_info="Wind data",
        station_name="Test Station",
        station_city="Test City",
        wind_provider="Test Provider",
        date_retrieved="Jun 16 at 6:45 AM",
        water_temp_measured_at_date=None
    )
    
    # Mock template rendering
    mock_render.return_value = "Email body content"
    
    # Run in preview mode
    run_report(run_email=False, test=True)
    
    # Verify calls
    mock_fetch.assert_called_once()
    mock_format.assert_called_once()
    mock_render.assert_called_once()
    mock_send.assert_called_once_with(
        context=Any,
        run_email=False,
        subject=Any,
        body="Email body content",
        bcc_recipients=Any
    )
```

---

### Unit Tests: Data Formatter

```python
from ocean_report.workflows.data.formatter import format_report_data
from ocean_report.workflows.models import RawReportData

def test_format_report_data():
    """Test data formatting to EmailTemplateData."""
    raw_data = RawReportData(
        tides=[...],
        tide_timestamp=datetime.now(),
        water_temp=72.5,
        water_temp_timestamp=datetime.now(),
        water_temp_data_time="2026-06-16 12:00",
        wind_forecast=[...],
        wind_timestamp=datetime.now()
    )
    
    email_data = format_report_data(raw_data)
    
    assert isinstance(email_data, EmailTemplateData)
    assert "72.5" in email_data.water_temp
    assert email_data.long_date is not None
```

---

### Integration Tests: Full Workflow

```python
@pytest.mark.integration
def test_run_report_end_to_end():
    """Test complete workflow with real APIs but preview mode."""
    
    # Run with real API calls but don't send email
    run_report(
        run_email=False,  # Preview only
        test=True
    )
    
    # If we get here without exceptions, workflow succeeded
    assert True
```

---

## Common Issues

### Issue: Workflow Fails Midway

**Symptom**: Some data fetched, then workflow crashes

**Cause**: Unhandled exception from use case

**Solution**: Add try/except for graceful degradation:
```python
try:
    water_temp, _, _ = get_latest_water_temp(context)
except ApiClientError:
    logger.warning("Water temp fetch failed, continuing with None")
    water_temp = None  # Continue with partial data
```

---

### Issue: Logs Not Showing

**Symptom**: No log output during execution

**Cause**: Logger not configured

**Solution**: Workflow configures logger early:
```python
def run_report(...):
    # Configure logger FIRST
    configure_logger(
        output=LogOutput.BOTH,
        log_file="logs/report.log",
        level=logging.INFO
    )
    
    # Now logging works
    logger.info("Starting workflow...")
```

---

## Design Decisions

### Decision: Single Orchestration Function

**Chose**: One `run_report()` function instead of multiple entry points

**Reasoning**:
- **Simplicity**: One place to understand complete flow
- **Maintainability**: Changes to workflow in one location
- **Debuggability**: Easy to trace execution
- **Consistency**: All executions follow same path

---

### Decision: Separate Data Fetching and Formatting

**Chose**: `fetcher.py` (fetch) + `formatter.py` (format) instead of combined

**Reasoning**:
- **Testability**: Can test fetching without formatting
- **Reusability**: Formatting can be reused for different outputs (email, web, PDF)
- **Separation of Concerns**: Fetching ≠ formatting

---

### Decision: Explicit Step Logging

**Chose**: Log each major step with step numbers

**Reasoning**:
- **Progress Visibility**: Know where execution is
- **Debugging**: Identify which step failed
- **Monitoring**: Track step durations
- **User Experience**: Clear progress indicators

---

## Related Components

- **[Use Cases](./use_cases.md)**: Orchestrated by workflows
- **[Emailer](./emailer.md)**: Called by workflows for formatting and sending
- **[Application](./application.md)**: Workflows create ApplicationContext
- **[Config](./config.md)**: Workflows load configuration
- **[Logger](./logger.md)**: Workflows configure logging

---

## Summary

**Key Takeaways**:

1. **Top-Level Orchestration**: Coordinates all other components
2. **Clear Step Progression**: Reads like a recipe
3. **Centralized Error Handling**: Decides recovery strategies
4. **Performance Monitoring**: Tracks timing for each step
5. **Flexible Execution**: Supports preview, test, and production modes

**When to Use**:
- You need to execute the complete report workflow
- You need to coordinate multiple use cases
- You need top-level error handling and logging

**When Not to Use**:
- For individual data fetching (use Use Cases)
- For business logic (use Use Cases)
- For API calls (use Services)

---

**Next**: See [Logger](./logger.md) to understand how logging is configured and used throughout the application.
