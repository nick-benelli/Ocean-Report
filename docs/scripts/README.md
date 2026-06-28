# Scripts Documentation

This directory contains executable scripts for running Ocean Report in different modes and testing various configurations.

---

## Quick Reference

| Script | Purpose | Common Use |
|--------|---------|------------|
| [`run_report.py`](#run_reportpy) | Production email runner | `uv run scripts/run_report.py` |
| [`run_report_no_email.py`](#run_report_no_emailpy) | Preview mode with HTML/text output | `uv run scripts/run_report_no_email.py --html` |
| [`run_report_with_logging.py`](#run_report_with_loggingpy) | Example: programmatic logging setup | `uv run scripts/run_report_with_logging.py` |
| [`demo_logger.py`](#demo_loggerpy) | Logger configuration examples | `uv run scripts/demo_logger.py` |
| [`test_config_logging.py`](#test_config_loggingpy) | Test config-based logging | `uv run scripts/test_config_logging.py` |

---

## Production Scripts

### `run_report.py`

**Purpose**: Main production script for sending Ocean Report emails.

**Behavior**:
- Sends actual emails to recipients (when `RUN_EMAIL=true`)
- Controlled via environment variables
- Uses default configuration from `configs/config.yaml`

**Usage**:

```bash
# Send email in production
RUN_EMAIL=true uv run scripts/run_report.py

# Preview only (no email sent)
uv run scripts/run_report.py

# Test mode (uses test recipients)
TEST=true RUN_EMAIL=true uv run scripts/run_report.py
```

**Environment Variables**:

| Variable | Default | Values | Description |
|----------|---------|--------|-------------|
| `RUN_EMAIL` | `False` | `true`, `false` | Actually send email via SMTP |
| `TEST` | `False` | `true`, `false` | Use test recipients instead of production list |

**When to use**:
- ✅ Production deployments (cron jobs, scheduled tasks)
- ✅ Automated workflows (CI/CD, GitHub Actions)
- ✅ Environment-based configuration
- ❌ Local development/testing (use `run_report_no_email.py` instead)

---

### `run_report_no_email.py`

**Purpose**: Preview email content without sending. Generates HTML and text previews.

**Behavior**:
- Never sends email
- Saves previews to `logs/email-previews/`
- Can open HTML in browser
- Can display text in terminal

**Usage**:

```bash
# Generate preview (saved to logs/email-previews/)
uv run scripts/run_report_no_email.py

# Open HTML preview in browser
uv run scripts/run_report_no_email.py --html

# Display text preview in terminal
uv run scripts/run_report_no_email.py --text

# Both previews
uv run scripts/run_report_no_email.py --html --text

# Short flags work too
uv run scripts/run_report_no_email.py -H -T

# Use test mode
uv run scripts/run_report_no_email.py --test

# Combine everything
uv run scripts/run_report_no_email.py -H -T --test
```

**Command-Line Options**:

| Flag | Short | Description |
|------|-------|-------------|
| `--html` | `-H` | Open latest HTML preview in browser |
| `--text` | `-T` | Display latest text preview in terminal |
| `--test` | `-t` | Use test mode configuration |

**Output Files**:

```
logs/email-previews/
├── email_preview_20260626_143015.html  # Browser-friendly HTML
└── email_preview_20260626_143015.txt   # Plain text (exact email content)
```

**When to use**:
- ✅ Local development
- ✅ Testing email formatting changes
- ✅ Verifying data before sending
- ✅ Debugging email templates

**See also**: [Email Preview Guide](../guides/email-preview.md) for detailed preview documentation

---

## Logging Examples

### `run_report_with_logging.py`

**Purpose**: Example of programmatic logging configuration with file output.

**Behavior**:
- Demonstrates how to configure logging via code
- Writes logs to both console and file
- Creates timestamped log files in `logs/reports/`

**Usage**:

```bash
uv run scripts/run_report_with_logging.py
```

**Output**:

```
logs/reports/
└── ocean_report_20260626_143015.log  # Complete execution log
```

**What it demonstrates**:
- How to use `configure_logger()` function
- Setting up `LogOutput.BOTH` (console + file)
- Creating timestamped log files
- Running report with custom logging

**Key code pattern**:

```python
from ocean_report import configure_logger, LogOutput
from datetime import datetime
from pathlib import Path

# Setup logger BEFORE running report
LOG_DIR = Path("logs/reports")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = LOG_DIR / f"ocean_report_{timestamp}.log"

configure_logger(
    output=LogOutput.BOTH,  # Console + file
    log_file=log_file,
)

# Now run the report
ocean_report.run_report(run_email=False)
```

**When to use**:
- ✅ Learning how to configure logging programmatically
- ✅ Creating custom logging setups
- ✅ Generating audit logs for production runs

**See also**: [Logging Guide](../guides/logging.md) for complete logging documentation

---

### `demo_logger.py`

**Purpose**: Interactive demonstration of all logger configuration options.

**Behavior**:
- Runs 4 different logging demos
- Shows console-only, file-only, both, and custom format examples
- Creates example log files in `logs/`

**Usage**:

```bash
uv run scripts/demo_logger.py
```

**Demos included**:

1. **Console Only** - Default behavior, logs to terminal
2. **File Only** - Silent terminal, logs to file only
3. **Both** - Logs to both console and file
4. **Custom Format** - Example of custom log formatting

**Output**:

```
logs/
├── ocean_report_file_only.log
├── ocean_report_both.log
└── ocean_report_custom_format.log
```

**What it demonstrates**:
- `LogOutput.CONSOLE` - Terminal only
- `LogOutput.FILE` - File only
- `LogOutput.BOTH` - Terminal + file
- Custom log formats
- Different log levels (INFO, WARNING, ERROR)

**When to use**:
- ✅ Learning logger configuration options
- ✅ Testing different logging setups
- ✅ Understanding log output formats

---

### `test_config_logging.py`

**Purpose**: Test configuration-based logging (via `config.yaml`).

**Behavior**:
- Uses `configs/config_with_logging.yaml`
- Demonstrates config file logging setup
- Tests that config-based logging works correctly

**Usage**:

```bash
uv run scripts/test_config_logging.py
```

**Config file used**: `configs/config_with_logging.yaml`

```yaml
logging:
  output: both          # console + file
  file_path: logs/test_config_logging.log
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

**Output**:

```
logs/
└── test_config_logging.log
```

**What it demonstrates**:
- How logging configuration in YAML files works
- Config-based vs programmatic logging setup
- Verifying logger behaves as configured

**When to use**:
- ✅ Testing config file logging settings
- ✅ Verifying logging configuration changes
- ✅ Learning config-based logging patterns

---

## Common Workflows

### Daily Development Routine

```bash
# 1. Make code changes
vim src/ocean_report/emailer/template_renderer.py

# 2. Preview changes
uv run scripts/run_report_no_email.py --html --text

# 3. Review HTML in browser (opens automatically)
# 4. Check text output in terminal (displays automatically)

# 5. If satisfied, test with real recipient list
TEST=true uv run scripts/run_report.py
```

### Testing Email Template Changes

```bash
# Run preview multiple times to compare
uv run scripts/run_report_no_email.py --html

# Make changes...

uv run scripts/run_report_no_email.py --html

# Compare the two latest previews
diff $(ls -t logs/email-previews/*.txt | sed -n '2p') \
     $(ls -t logs/email-previews/*.txt | sed -n '1p')
```

### Debugging Production Issues

```bash
# Run with full logging to file
uv run scripts/run_report_with_logging.py

# Check the log for errors
cat logs/reports/ocean_report_*.log | grep ERROR

# Or use test_config_logging.py for config-based logging
uv run scripts/test_config_logging.py
cat logs/test_config_logging.log
```

### Scheduled Production Run (Cron)

```bash
# Add to crontab:
0 6 * * * cd /path/to/Ocean-Report && RUN_EMAIL=true uv run scripts/run_report.py

# With logging:
0 6 * * * cd /path/to/Ocean-Report && RUN_EMAIL=true uv run scripts/run_report_with_logging.py
```

---

## Script Dependencies

All scripts require:
- ✅ Ocean Report package installed (`uv sync`)
- ✅ Valid `config.yaml` file
- ✅ Python 3.12+

Additional requirements by script:

| Script | Requires | Optional |
|--------|----------|----------|
| `run_report.py` | SMTP credentials (if `RUN_EMAIL=true`) | - |
| `run_report_no_email.py` | Preview helper scripts (`help/bin/`) | Browser for HTML preview |
| `run_report_with_logging.py` | Writable `logs/reports/` directory | - |
| `demo_logger.py` | Writable `logs/` directory | - |
| `test_config_logging.py` | `configs/config_with_logging.yaml` | - |

---

## Troubleshooting

### Preview scripts don't open HTML/text

**Problem**: `--html` or `--text` flags don't work

**Solution**: Check that helper scripts exist:

```bash
ls -l help/bin/preview-email.sh
ls -l help/bin/preview-email-txt.sh
```

If missing, the preview files are still created in `logs/email-previews/` - you can open them manually.

### Email not sending

**Problem**: `RUN_EMAIL=true` but no email sent

**Checklist**:
1. ✅ SMTP credentials configured in `config.yaml`
2. ✅ Recipient list configured or URL accessible
3. ✅ Check for errors in terminal output
4. ✅ Try with `TEST=true` to use test recipients

### Log files not created

**Problem**: Logging scripts don't create log files

**Solution**:

```bash
# Create logs directory
mkdir -p logs/reports

# Verify permissions
chmod 755 logs
chmod 755 logs/reports
```

### Import errors

**Problem**: `ModuleNotFoundError: No module named 'ocean_report'`

**Solution**:

```bash
# Install package in development mode
uv sync

# Or if using different Python environment
uv pip install -e .
```

---

## See Also

- [Email Preview Guide](../guides/email-preview.md) - Detailed preview workflow documentation
- [Logging Guide](../guides/logging.md) - Complete logging configuration guide
- [Config Setup](../guides/config-setup.md) - Configuration file documentation
- [Workflows](../architecture/workflows.md) - How `run_report()` works internally
