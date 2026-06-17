# Logging Configuration Guide

## Overview

The Ocean Report logger supports flexible output destinations and log levels. It's designed for both development (see everything) and production (file-based persistent logs).

**Logging Options:**
- **Console only** (terminal) - Default for development
- **File only** (no terminal output) - Best for production/cron
- **Both** console and file - Best for debugging

---

## Quick Start

```python
from ocean_report.logger import configure_logger, LogOutput
import logging

# Console only (default)
configure_logger()

# File only
configure_logger(LogOutput.FILE, log_file="logs/app.log")

# Both console and file
configure_logger(LogOutput.BOTH, log_file="logs/app.log")

# With debug level
configure_logger(LogOutput.BOTH, log_file="logs/debug.log", level=logging.DEBUG)
```

---

## Configuration via Config File

The recommended way to configure logging is through `config.yaml`:

```yaml
# configs/config.yaml
logging:
  output: both         # Options: console, file, both
  level: INFO          # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
  file_path: logs/runs/ocean_report.log
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

The workflow automatically configures the logger from config:

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

# Apply config
configure_logger(
    output=output_map[config.logging.output],
    log_file=config.logging.file_path,
    level=level_map[config.logging.level],
    log_format=config.logging.format
)
```

---

## Environment Variable Overrides

You can override logging settings via environment variables in `.env`:

```bash
# .env
LOG_OUTPUT=both
LOG_FILE_PATH=logs/production.log
LOG_LEVEL=WARNING
```

Then in `config.yaml`, reference them with fallback defaults:

```yaml
logging:
  output: ${LOG_OUTPUT:console}       # Fallback to console
  file_path: ${LOG_FILE_PATH:logs/app.log}  # Fallback to logs/app.log
  level: ${LOG_LEVEL:INFO}            # Fallback to INFO
```

**Priority Order:**
```
Code Defaults  →  config.yaml  →  Environment Variables (.env)
   (lowest)                          (highest priority)
```

---

## Usage Examples

### Example 1: Default Console Logging

No configuration needed! Works out-of-the-box:

```python
from ocean_report.logger import logger

logger.info("This goes to the terminal")
logger.warning("This is a warning")
logger.error("This is an error")
```

**Output:**
```
2026-06-17 10:30:45,123 - ocean_report - INFO - This goes to the terminal
2026-06-17 10:30:45,124 - ocean_report - WARNING - This is a warning
2026-06-17 10:30:45,125 - ocean_report - ERROR - This is an error
```

---

### Example 2: File-Only Logging (Production)

Perfect for cron jobs and production servers:

```python
from ocean_report.logger import configure_logger, LogOutput

configure_logger(
    output=LogOutput.FILE,
    log_file="logs/production.log"
)
```

**Benefits:**
- ✅ Persistent logs you can review later
- ✅ No console noise in automated environments
- ✅ Easy to rotate and archive

---

### Example 3: Both Console and File (Development)

See logs in real-time AND save for later:

```python
from ocean_report.logger import configure_logger, LogOutput

configure_logger(
    output=LogOutput.BOTH,
    log_file="logs/debug.log"
)
```

**Benefits:**
- ✅ Watch progress in terminal
- ✅ Review full logs if something goes wrong
- ✅ Compare runs side-by-side

---

### Example 4: Timestamped Log Files

Organize logs by date/time (one file per run):

```python
from datetime import datetime
from pathlib import Path
from ocean_report.logger import configure_logger, LogOutput

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = Path(f"logs/reports/ocean_report_{timestamp}.log")

configure_logger(
    output=LogOutput.BOTH,
    log_file=log_file
)
```

**Result:**
```
logs/reports/
├── ocean_report_20260616_103045.log
├── ocean_report_20260616_153022.log
└── ocean_report_20260617_093015.log
```

---

### Example 5: Debug Level Logging

See detailed diagnostic information:

```python
import logging
from ocean_report.logger import configure_logger, LogOutput

configure_logger(
    output=LogOutput.BOTH,
    log_file="logs/debug.log",
    level=logging.DEBUG  # Show everything
)
```

**Shows all log levels:**
```
DEBUG   - Detailed diagnostic info
INFO    - General informational messages
WARNING - Warning messages
ERROR   - Error messages
CRITICAL - Critical failures
```

---

### Example 6: Daily Log Files (Production Pattern)

Organize production logs by date:

```python
from datetime import date
from ocean_report.logger import configure_logger, LogOutput

log_file = f"logs/production/{date.today()}.log"
configure_logger(
    output=LogOutput.FILE,
    log_file=log_file,
    level=logging.INFO
)
```

**Result:**
```
logs/production/
├── 2026-06-15.log
├── 2026-06-16.log
└── 2026-06-17.log
```

---

## Log Levels Explained

### DEBUG (Most Verbose)
```python
logger.debug("Using station_id from config: %s", station_id)
logger.debug("Raw API response: %s", response_data)
```

**When to use:** Development, detailed diagnostic information

---

### INFO (Default)
```python
logger.info("Starting Ocean Report workflow...")
logger.info("Fetching water temperature for station: %s", station_id)
logger.info("Email sent successfully to %d recipients", len(recipients))
```

**When to use:** Normal operation milestones, general information

---

### WARNING
```python
logger.warning("No water temperature data available for station: %s", station_id)
logger.warning("SSL verification failed, retrying without verification")
```

**When to use:** Potentially problematic situations that don't prevent execution

---

### ERROR
```python
logger.error("Failed to fetch water temperature: %s", error)
logger.error("Email sending failed: %s", error)
```

**When to use:** Error events that might still allow the application to continue

---

### CRITICAL (Most Severe)
```python
logger.critical("Configuration file not found: %s", config_path)
logger.critical("Database connection failed, cannot proceed")
```

**When to use:** Very severe errors that may cause the application to terminate

---

## Common Patterns

### Pattern 1: Performance Logging

Track timing for operations:

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

**Output:**
```
2026-06-17 10:45:23 - INFO - [STEP 3/6] Fetching weather data from APIs...
2026-06-17 10:45:25 - INFO - Data fetched in 1.38 seconds
```

---

### Pattern 2: Structured Logging with Context

Add visual structure to logs:

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

**Output:**
```
2026-06-17 10:45:23 - INFO - ================================================================================
2026-06-17 10:45:23 - INFO - Starting Ocean Report Email Process...
2026-06-17 10:45:23 - INFO - Today is Tuesday, June 17, 2026
2026-06-17 10:45:23 - INFO - Run mode: PRODUCTION
2026-06-17 10:45:23 - INFO - ================================================================================
```

---

### Pattern 3: Error Logging with Traceback

Log errors with full context:

```python
from ocean_report.logger import logger

def process_data(data):
    try:
        result = complex_operation(data)
        return result
    except Exception as e:
        # logger.exception() automatically includes the full traceback
        logger.exception("Unexpected error during data processing")
        raise
```

**Output:**
```
2026-06-17 10:45:25 - ERROR - Unexpected error during data processing
Traceback (most recent call last):
  File "process.py", line 3, in process_data
    result = complex_operation(data)
ValueError: Invalid data format
```

---

## Function Signature

```python
def configure_logger(
    output: LogOutput = LogOutput.CONSOLE,
    log_file: Optional[str | Path] = None,
    level: int = logging.INFO,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
) -> logging.Logger:
    """Configure logger with flexible output options.
    
    Args:
        output: Where to send logs (CONSOLE, FILE, or BOTH)
        log_file: Path to log file (required if output is FILE or BOTH)
        level: Logging level (default: logging.INFO)
        log_format: Log message format string
        
    Returns:
        Configured logger instance
        
    Raises:
        ValueError: If log_file is not provided when output requires file writing
    """
```

---

## Log Format Customization

### Default Format

```python
"%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

**Output:**
```
2026-06-17 10:45:23,456 - ocean_report - INFO - Starting workflow...
```

---

### Minimal Format

```python
configure_logger(log_format="%(levelname)s: %(message)s")
```

**Output:**
```
INFO: Starting workflow...
WARNING: No data available
ERROR: Failed to send email
```

---

### Detailed Format (with function and line number)

```python
configure_logger(
    log_format="%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s"
)
```

**Output:**
```
2026-06-17 10:45:23 [INFO] ocean_report.run_report:45 - Starting workflow...
```

---

### Production Format (aligned columns)

```python
configure_logger(
    log_format="%(asctime)s | %(levelname)-8s | %(message)s"
)
```

**Output:**
```
2026-06-17 10:45:23,456 | INFO     | Starting Ocean Report workflow...
2026-06-17 10:45:23,789 | WARNING  | No water temperature data
2026-06-17 10:45:24,012 | ERROR    | Failed to send email
```

---

## Important Notes

### 1. Call configure_logger() BEFORE Using Logger

```python
# ✅ Correct order
from ocean_report.logger import configure_logger, logger, LogOutput

configure_logger(LogOutput.BOTH, log_file="logs/app.log")
logger.info("This will be logged correctly")

# ❌ Wrong order
logger.info("This uses default config (console only)")
configure_logger(LogOutput.BOTH, log_file="logs/app.log")
```

---

### 2. Log Directories Created Automatically

No need to create directories manually:

```python
configure_logger(
    output=LogOutput.FILE,
    log_file="logs/very/deep/nested/path/app.log"  # All created automatically
)
```

---

### 3. File Mode is Append

Logs are appended to existing files (won't overwrite):

```python
# Run 1
configure_logger(LogOutput.FILE, log_file="logs/app.log")
logger.info("First run")

# Run 2
configure_logger(LogOutput.FILE, log_file="logs/app.log")
logger.info("Second run")

# File contains both runs:
# 2026-06-17 10:00:00 - INFO - First run
# 2026-06-17 10:05:00 - INFO - Second run
```

---

### 4. UTF-8 Encoding for Emoji

Logger uses UTF-8 encoding, so emojis work:

```python
logger.info("✓ Email sent successfully!")
logger.info("🌡️ Water temperature: 72.5 °F")
logger.info("🌊 Tide data retrieved")
```

---

## Troubleshooting

### Error: "log_file must be provided"

**Problem:** Using `LogOutput.FILE` or `LogOutput.BOTH` without specifying a log file.

**Solution:**
```python
# ❌ Wrong
configure_logger(LogOutput.FILE)

# ✅ Correct
configure_logger(LogOutput.FILE, log_file="logs/app.log")
```

---

### No Logs Appearing

**Check:**

1. **Did you call `configure_logger()` first?**
   ```python
   configure_logger()  # Must call this first!
   logger.info("Now it works")
   ```

2. **Is your log level too restrictive?**
   ```python
   # If level=ERROR, you won't see INFO messages
   configure_logger(level=logging.ERROR)  # Only ERROR and CRITICAL
   logger.info("This won't appear!")  # ❌
   logger.error("This will appear")    # ✅
   ```

3. **For file output, check the file path is correct:**
   ```python
   from pathlib import Path
   
   log_file = Path("logs/app.log")
   configure_logger(LogOutput.FILE, log_file=log_file)
   
   # Verify file exists after logging
   assert log_file.exists(), f"Log file not created: {log_file}"
   ```

---

### Duplicate Log Messages

**Problem:** Each log message appears twice (or more).

**Cause:** Logger configured multiple times without clearing handlers.

**Solution:** The logger automatically clears handlers in `configure_logger()`, but if you're configuring manually:

```python
from ocean_report.logger import logger

# Clear handlers before reconfiguring
logger.handlers.clear()
```

---

## Terminal Commands

### View Latest Log File

```bash
# View entire log
cat logs/app.log

# View last 50 lines
tail -50 logs/app.log

# Follow log in real-time
tail -f logs/app.log
```

### Search Logs

```bash
# Find all errors
grep ERROR logs/app.log

# Find errors with context (3 lines before/after)
grep -C3 ERROR logs/app.log

# Count warnings
grep -c WARNING logs/app.log
```

### Clean Up Old Logs

```bash
# Remove all logs
rm logs/*.log

# Remove logs older than 7 days
find logs -type f -name "*.log" -mtime +7 -delete

# Keep only the 10 most recent logs
ls -t logs/*.log | tail -n +11 | xargs rm
```

---

## Demo Scripts

Try these scripts to see the logger in action:

```bash
# Comprehensive logger demo
uv run scripts/demo_logger.py

# Run report with file logging
uv run scripts/run_report_with_logging.py

# Original script (console only)
uv run scripts/run_report_no_email.py
```

---

## See Also

- [Logger Architecture](../architecture/logger.md) - Technical implementation details
- [Configuration Setup](./config-setup.md) - Configuring logger via config.yaml
- [Workflows](../architecture/workflows.md) - How logger is used in workflows
