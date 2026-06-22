# Logger Component

**Purpose**: Centralized logging configuration with flexible output options (console, file, or both).

**Location**: `src/ocean_report/logger.py`

---

## Overview

The Logger component provides a single, shared logger instance used throughout the application. It supports flexible output configuration, making it easy to log to the console during development and to files in production.

### What It Does

**For Non-Technical Readers:**

Logging is like keeping a diary of what the application does. It records:
- When the application starts
- What data it fetches
- If anything goes wrong
- How long operations take

The Logger component lets you choose where this diary is written:
- Screen (console) - good for watching the app in real-time
- File - good for reviewing what happened later
- Both - good for production (watch live + keep records)

**For Technical Readers:**

- Singleton logger instance (`logger = logging.getLogger("ocean_report")`)
- Configurable output: console, file, or both
- Configurable log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Custom format strings
- Automatic log directory creation
- Handler deduplication (prevents duplicate log messages)
- UTF-8 encoding for emoji support

---

## Architecture

### File Structure

```
src/ocean_report/
└── logger.py        # Complete logger implementation (single file)
```

### Core Components

```
configure_logger()  ← Configuration function
    ↓
logger              ← Module-level logger instance
    ↓
Used everywhere     ← All modules import and use
```

---

## Core Components

### 1. Logger Instance

**Module-Level Singleton**:
```python
import logging

logger = logging.getLogger("ocean_report")
```

**Why Module-Level?**
- Shared across entire application
- Consistent logging namespace
- Easy to import: `from ocean_report.logger import logger`

---

### 2. LogOutput Enum

**Purpose**: Define where logs should be written.

```python
from enum import Enum

class LogOutput(Enum):
    CONSOLE = "console"  # Print to terminal only
    FILE = "file"        # Write to file only
    BOTH = "both"        # Both terminal and file
```

**Usage**:
```python
from ocean_report.logger import LogOutput, configure_logger

configure_logger(output=LogOutput.CONSOLE)  # Console only
configure_logger(output=LogOutput.FILE, log_file="app.log")  # File only
configure_logger(output=LogOutput.BOTH, log_file="app.log")  # Both
```

---

### 3. Configure Logger Function

#### `configure_logger(output, log_file, level, log_format) → logging.Logger`

**Purpose**: Configure the shared logger with output destinations and formatting.

**Signature**:
```python
def configure_logger(
    output: LogOutput = LogOutput.CONSOLE,
    log_file: Optional[str | Path] = None,
    level: int = logging.INFO,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
) -> logging.Logger:
```

**Parameters**:
- `output`: Where to send logs (CONSOLE, FILE, or BOTH)
- `log_file`: Path to log file (required if output is FILE or BOTH)
- `level`: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_format`: Format string for log messages

**Returns**: Configured logger instance

**Example**:
```python
from ocean_report.logger import logger, configure_logger, LogOutput
import logging

# Console only (default)
configure_logger()
logger.info("This goes to console")

# File only
configure_logger(
    output=LogOutput.FILE,
    log_file="logs/app.log",
    level=logging.DEBUG
)
logger.debug("This goes to file")

# Both console and file
configure_logger(
    output=LogOutput.BOTH,
    log_file="logs/app.log",
    level=logging.INFO
)
logger.info("This goes to both console and file")
```

---

### 4. Log Levels

**Available Levels** (from least to most severe):

```python
import logging

logger.debug("Detailed debugging information")      # DEBUG (10)
logger.info("General informational messages")       # INFO (20)
logger.warning("Warning messages")                  # WARNING (30)
logger.error("Error messages")                      # ERROR (40)
logger.critical("Critical error messages")          # CRITICAL (50)
```

**When to Use Each Level**:

- **DEBUG**: Detailed diagnostic information, useful during development
  ```python
  logger.debug("Using station_id from config: %s", station_id)
  logger.debug("Raw API response: %s", response_data)
  ```

- **INFO**: General informational messages about normal operation
  ```python
  logger.info("Starting Ocean Report workflow...")
  logger.info("Fetching water temperature for station: %s", station_id)
  logger.info("Email sent successfully to %d recipients", len(recipients))
  ```

- **WARNING**: Potentially problematic situations that don't prevent execution
  ```python
  logger.warning("No water temperature data available for station: %s", station_id)
  logger.warning("SSL verification failed, retrying without verification")
  ```

- **ERROR**: Error events that might still allow the application to continue
  ```python
  logger.error("Failed to fetch water temperature: %s", error)
  logger.error("Email sending failed: %s", error)
  ```

- **CRITICAL**: Very severe errors that may cause the application to terminate
  ```python
  logger.critical("Configuration file not found: %s", config_path)
  logger.critical("Database connection failed, cannot proceed")
  ```

---

## Configuration

### Via Config File

Logger behavior is controlled by `config.yaml`:

```yaml
logging:
  output: both         # Options: console, file, both
  level: INFO          # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
  file_path: logs/runs/ocean_report.log
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

**Loading and Applying**:
```python
from ocean_report.config.loader import get_settings
from ocean_report.logger import configure_logger, LogOutput
import logging

config = get_settings()

# Map config strings to enums
output_map = {
    "console": LogOutput.CONSOLE,
    "file": LogOutput.FILE,
    "both": LogOutput.BOTH,
}

level_map = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# Configure from config
configure_logger(
    output=output_map[config.logging.output],
    log_file=config.logging.file_path,
    level=level_map[config.logging.level],
    log_format=config.logging.format
)
```

---

### Programmatic Configuration

```python
from ocean_report.logger import configure_logger, LogOutput
import logging

# Development: console with DEBUG
configure_logger(
    output=LogOutput.CONSOLE,
    level=logging.DEBUG
)

# Production: file only with INFO
configure_logger(
    output=LogOutput.FILE,
    log_file="logs/production.log",
    level=logging.INFO
)

# Production with monitoring: both with WARNING
configure_logger(
    output=LogOutput.BOTH,
    log_file="logs/production.log",
    level=logging.WARNING  # Only warnings and errors
)
```

---

## Usage Patterns

### Pattern 1: Simple Import and Use

```python
from ocean_report.logger import logger

def fetch_water_temp(context, params):
    logger.info("Fetching water temperature for station: %s", params.station)
    
    try:
        response = endpoint.fetch(params)
        logger.debug("API response: %s", response)
        return response
    except ApiClientError as e:
        logger.error("Failed to fetch water temperature: %s", e)
        raise
```

---

### Pattern 2: Structured Logging with Context

```python
from ocean_report.logger import logger

def run_report(context):
    logger.info("=" * 80)
    logger.info("Starting Ocean Report Email Process...")
    logger.info("Today is %s", date.today().strftime("%A, %B %d, %Y"))
    logger.info("Run mode: %s", "TEST" if test else "PRODUCTION")
    logger.info("=" * 80)
    
    # ... workflow steps ...
    
    logger.info("Ocean Report workflow completed successfully!")
```

---

### Pattern 3: Performance Logging

```python
import time
from ocean_report.logger import logger

def fetch_all_data(context):
    start_time = time.time()
    logger.info("[STEP 3/6] Fetching weather data from APIs...")
    
    # Fetch data
    water_temp = get_latest_water_temp(context)
    tides = get_tides_for_date(context, date_str)
    wind = get_hourly_wind_forecast(context, date_str)
    
    duration = time.time() - start_time
    logger.info("Data fetched in %.2f seconds", duration)
```

---

### Pattern 4: Error Logging with Traceback

```python
from ocean_report.logger import logger

def process_data(data):
    try:
        # Process data
        result = complex_operation(data)
        return result
    except Exception as e:
        # Log with full traceback
        logger.exception("Unexpected error during data processing")
        raise
```

**Note**: `logger.exception()` automatically includes the full traceback.

---

## Log Format Customization

### Default Format

```python
"%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

**Output Example**:
```
2026-06-16 10:45:23,456 - ocean_report - INFO - Starting Ocean Report workflow...
```

### Custom Formats

#### Minimal Format
```python
configure_logger(
    log_format="%(levelname)s: %(message)s"
)
# Output: INFO: Starting Ocean Report workflow...
```

#### Detailed Format with Function Name
```python
configure_logger(
    log_format="%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s"
)
# Output: 2026-06-16 10:45:23 [INFO] ocean_report.run_report:45 - Starting workflow...
```

#### Production Format with Timestamp
```python
configure_logger(
    log_format="%(asctime)s | %(levelname)-8s | %(message)s",
)
# Output: 2026-06-16 10:45:23,456 | INFO     | Starting Ocean Report workflow...
```

---

## File Logging

### Automatic Directory Creation

The logger automatically creates log directories if they don't exist:

```python
configure_logger(
    output=LogOutput.FILE,
    log_file="logs/runs/2026/june/report.log"  # Creates all directories
)
```

**Implementation**:
```python
log_path = Path(log_file)
log_path.parent.mkdir(parents=True, exist_ok=True)  # Create directories
```

---

### Append Mode

Log files are opened in append mode by default:

```python
file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
```

**Benefits**:
- Previous logs preserved
- Can track history across multiple runs
- Easy to review daily logs

---

### UTF-8 Encoding

Handlers use UTF-8 encoding to support emoji and international characters:

```python
file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
```

**Why?**
- Emoji in log messages: `logger.info("✓ Email sent successfully!")`
- International characters: `logger.info("Température: 22°C")`

---

## Handler Management

### Deduplication

The logger clears existing handlers before configuration to prevent duplicates:

```python
def configure_logger(...):
    # Clear existing handlers
    logger.handlers.clear()
    
    # Add new handlers
    if output in (LogOutput.CONSOLE, LogOutput.BOTH):
        console_handler = logging.StreamHandler()
        logger.addHandler(console_handler)
    
    if output in (LogOutput.FILE, LogOutput.BOTH):
        file_handler = logging.FileHandler(log_file)
        logger.addHandler(file_handler)
```

**Why?**
- Calling `configure_logger()` multiple times won't create duplicate log messages
- Safe to reconfigure logger at runtime

---

### Prevent Propagation

Logger propagation is disabled to avoid duplicate logs:

```python
logger.propagate = False
```

**Why?**
- Without this, logs would appear twice (from our handlers + from root logger)
- Gives us full control over log output

---

## Testing Guidelines

### Unit Tests: Logger Configuration

```python
import logging
from ocean_report.logger import configure_logger, LogOutput

def test_configure_logger_console():
    logger = configure_logger(output=LogOutput.CONSOLE, level=logging.INFO)
    
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.StreamHandler)

def test_configure_logger_file(tmp_path):
    log_file = tmp_path / "test.log"
    
    logger = configure_logger(
        output=LogOutput.FILE,
        log_file=str(log_file),
        level=logging.DEBUG
    )
    
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.FileHandler)
    assert log_file.exists()
```

---

### Integration Tests: Log Output

```python
def test_logger_writes_to_file(tmp_path):
    log_file = tmp_path / "test.log"
    
    configure_logger(output=LogOutput.FILE, log_file=str(log_file))
    
    logger.info("Test message")
    
    # Read log file
    content = log_file.read_text()
    assert "Test message" in content
    assert "INFO" in content
```

---

### Capturing Logs in Tests

```python
import logging

def test_function_logs_correctly(caplog):
    with caplog.at_level(logging.INFO):
        some_function_that_logs()
    
    assert "Expected log message" in caplog.text
```

---

## Common Issues

### Issue: Duplicate Log Messages

**Symptom**: Each log message appears twice

**Cause**: Logger configured multiple times without clearing handlers

**Solution**: Logger automatically clears handlers in `configure_logger()`. If you're configuring manually, clear first:
```python
logger.handlers.clear()
```

---

### Issue: Logs Not Appearing in File

**Symptom**: Console logs work, but file is empty

**Cause**: 
1. Log level too high (e.g., level=ERROR but you're logging INFO)
2. File path invalid
3. Permissions issue

**Solution**:
```python
# Check log level
configure_logger(output=LogOutput.FILE, log_file="app.log", level=logging.DEBUG)

# Verify file is created
logger.info("Test message")
assert Path("app.log").exists()
```

---

### Issue: Unicode Errors

**Symptom**: `UnicodeEncodeError` when logging emoji

**Cause**: Handler not using UTF-8 encoding

**Solution**: `configure_logger()` automatically uses UTF-8. If configuring manually:
```python
handler = logging.FileHandler(log_file, encoding="utf-8")
```

---

## Design Decisions

### Decision: Module-Level Logger Instance

**Chose**: Single `logger` instance at module level

**Reasoning**:
- **Consistency**: All modules use same logger
- **Namespace**: All logs under "ocean_report" namespace
- **Simplicity**: No need to pass logger instances around
- **Standard Practice**: Common pattern in Python applications

---

### Decision: Enum for Output Options

**Chose**: `LogOutput` enum instead of strings

**Reasoning**:
- **Type Safety**: IDE autocomplete, type checking
- **Clear Options**: Easy to see valid values
- **Validation**: Can't pass invalid output option

---

### Decision: Separate Configuration Function

**Chose**: `configure_logger()` function instead of at import time

**Reasoning**:
- **Flexibility**: Can reconfigure at runtime
- **Testing**: Easy to configure differently for tests
- **Control**: Application decides when/how to configure

---

### Decision: Handler Deduplication

**Chose**: Clear handlers before adding new ones

**Reasoning**:
- **Safe Reconfiguration**: Can call `configure_logger()` multiple times
- **No Duplicates**: Prevents duplicate log messages
- **Clean State**: Each configuration starts fresh

---

## Related Components

- **[Config](./config.md)**: Provides logging configuration settings
- **[Workflows](./workflows.md)**: Configures logger at workflow startup
- **All Components**: Import and use logger for diagnostics

---

## Summary

**Key Takeaways**:

1. **Single Shared Instance**: One logger for entire application
2. **Flexible Output**: Console, file, or both
3. **Configurable Levels**: DEBUG through CRITICAL
4. **UTF-8 Support**: Handles emoji and international characters
5. **Handler Management**: Automatic deduplication

**When to Use**:
- Everywhere in the application for diagnostics
- At workflow startup for configuration
- In error handling for debugging
- For performance monitoring

**Best Practices**:
- Use INFO for normal operation milestones
- Use DEBUG for detailed diagnostics (development)
- Use WARNING for recoverable issues
- Use ERROR for failures
- Include context: `logger.info("Fetching data for station: %s", station_id)`
- Use `logger.exception()` in except blocks for full tracebacks

---

**Architecture Documentation Complete**: You now have comprehensive documentation for every component in the Ocean Report application!
