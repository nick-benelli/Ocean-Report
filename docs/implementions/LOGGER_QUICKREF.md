# Quick Reference: Logger Configuration

## Three Ways to Configure Logging

### 1️⃣ Do Nothing (Default)
```bash
uv run scripts/run_report_no_email.py
```
**Result:** Console-only logging at INFO level

---

### 2️⃣ Configure in config.yaml (Recommended)
```yaml
# configs/config.yaml
logging:
  output: both  # console, file, or both
  file_path: logs/ocean_report.log
  level: INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

**Use when:** You want documented, version-controlled settings

---

### 3️⃣ Override with Environment Variables (Flexible)
```bash
# .env
LOG_OUTPUT=file
LOG_FILE_PATH=logs/custom.log
LOG_LEVEL=DEBUG
```

**Use when:** Different settings per environment (dev/prod)

---

## Priority Order (Low → High)
```
Code Defaults → config.yaml → Environment Variables
```

---

## Common Patterns

### Development (Verbose)
```yaml
# config.yaml
logging:
  output: both
  level: DEBUG
```

### Production (File Only)
```bash
# .env
LOG_OUTPUT=file
LOG_FILE_PATH=/var/log/ocean-report.log
LOG_LEVEL=WARNING
```

### Quick Debug
```bash
LOG_LEVEL=DEBUG uv run scripts/run_report_no_email.py
```

---

## Files Modified
- ✅ `configs/config.yaml` - Added logging section
- ✅ `.env.template` - Added LOG_* variables
- ✅ `src/ocean_report/config/schemas.py` - Added LoggingConfig
- ✅ `src/ocean_report/workflows/report_runner.py` - Auto-configures logger

---

## Read More
- [LOGGER_ARCHITECTURE.md](LOGGER_ARCHITECTURE.md) - Why we built it this way
- [LOGGER_GUIDE.md](LOGGER_GUIDE.md) - Full API documentation
