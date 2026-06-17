# Logger Configuration Guide

## Overview

The Ocean Report logger now supports flexible output destinations:
- **Console only** (terminal) - default behavior
- **File only** (no terminal output)
- **Both** console and file

## Quick Start

```python
from ocean_report import configure_logger, LogOutput

# Console only (default - backward compatible)
configure_logger()

# File only
configure_logger(LogOutput.FILE, log_file="logs/app.log")

# Both console and file
configure_logger(LogOutput.BOTH, log_file="logs/app.log")

# With debug level
configure_logger(LogOutput.BOTH, log_file="logs/debug.log", level=logging.DEBUG)
```

## Usage Examples

### Example 1: Default Console Logging (Backward Compatible)

No changes needed! Existing code works as before:

```python
from ocean_report import logger

logger.info("This goes to the terminal")
```

### Example 2: File-Only Logging

Perfect for production/cron jobs where you want persistent logs:

```python
from ocean_report import configure_logger, LogOutput

configure_logger(
    output=LogOutput.FILE,
    log_file="logs/production.log"
)
```

### Example 3: Both Console and File

Best for development and debugging:

```python
from ocean_report import configure_logger, LogOutput

configure_logger(
    output=LogOutput.BOTH,
    log_file="logs/debug.log"
)
```

### Example 4: Timestamped Log Files

Organize logs by date/time:

```python
from datetime import datetime
from pathlib import Path
from ocean_report import configure_logger, LogOutput

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = Path(f"logs/reports/ocean_report_{timestamp}.log")

configure_logger(
    output=LogOutput.BOTH,
    log_file=log_file
)
```

### Example 5: Debug Level Logging

See detailed debug messages:

```python
import logging
from ocean_report import configure_logger, LogOutput

configure_logger(
    output=LogOutput.BOTH,
    log_file="logs/debug.log",
    level=logging.DEBUG  # Show DEBUG, INFO, WARNING, ERROR
)
```

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

## LogOutput Enum

```python
class LogOutput(Enum):
    CONSOLE = "console"  # Print to terminal only
    FILE = "file"        # Write to log file only
    BOTH = "both"        # Both terminal and log file
```

## Logging Levels

From least to most severe:

- `logging.DEBUG` - Detailed diagnostic info
- `logging.INFO` - General informational messages (default)
- `logging.WARNING` - Warning messages
- `logging.ERROR` - Error messages
- `logging.CRITICAL` - Critical failures

## Common Patterns

### Pattern 1: Development Mode

```python
# See everything in terminal and save to file
configure_logger(
    output=LogOutput.BOTH,
    log_file="logs/dev.log",
    level=logging.DEBUG
)
```

### Pattern 2: Production Mode

```python
# File only, INFO level, organized by date
from datetime import date

log_file = f"logs/production/{date.today()}.log"
configure_logger(
    output=LogOutput.FILE,
    log_file=log_file,
    level=logging.INFO
)
```

### Pattern 3: Cron Job / Scheduled Task

```python
# File only with timestamps
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
configure_logger(
    output=LogOutput.FILE,
    log_file=f"logs/cron/run_{timestamp}.log"
)
```

## Important Notes

1. **Call `configure_logger()` BEFORE running your main code**
   ```python
   configure_logger(LogOutput.BOTH, log_file="logs/app.log")
   # Then run your code
   ocean_report.run_report(...)
   ```

2. **Log directories are created automatically**
   - No need to create `logs/` folder manually
   - Parent directories are created if they don't exist

3. **File mode is append**
   - Logs are appended to existing files
   - Won't overwrite previous logs

4. **Backward compatible**
   - Existing code works without changes
   - Default is console-only logging

## Demo Scripts

Try these demo scripts to see the logger in action:

```bash
# See all logger features
uv run scripts/demo_logger.py

# Run report with file logging
uv run scripts/run_report_with_logging.py

# Original script still works (console only)
uv run scripts/run_report_no_email.py
```

## Troubleshooting

### ValueError: log_file must be provided

**Problem:** Trying to use `LogOutput.FILE` or `LogOutput.BOTH` without specifying a log file.

**Solution:**
```python
# ❌ Wrong
configure_logger(LogOutput.FILE)

# ✅ Correct
configure_logger(LogOutput.FILE, log_file="logs/app.log")
```

### No logs appearing

**Check:**
1. Did you call `configure_logger()` before using `logger`?
2. Is your log level too restrictive?
3. For file output, check the file path is correct

```python
# View log level
from ocean_report import logger
print(f"Current level: {logger.level}")
```

## Terminal Debugging Tips

```bash
# View latest log file
cat logs/ocean_report_*.log | tail -50

# Watch logs in real-time
tail -f logs/production.log

# Search for errors
grep ERROR logs/*.log

# Count log entries by level
grep -c INFO logs/app.log
grep -c WARNING logs/app.log
grep -c ERROR logs/app.log

# Find logs from specific date
ls -lh logs/ | grep "Jun 16"
```
