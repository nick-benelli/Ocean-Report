# Demo Scripts

This folder contains demonstration scripts that show how to use various features of the Ocean Report package.

## Available Demos

### `demo_logger.py`
Interactive demo showing how to control logging via environment variables.

**What it demonstrates:**
- Console-only logging (default)
- File-only logging
- Both console and file logging
- Debug level logging
- Timestamped log files

**How to run:**
```bash
python scripts/demos/demo_logger.py
```

The demo will:
1. Set environment variables (`LOG_OUTPUT`, `LOG_FILE_PATH`, `LOG_LEVEL`)
2. Run the actual report with those settings
3. Show you where logs are written
4. Pause between demos so you can observe the behavior

**What you'll learn:**
- How to control logging without modifying code
- The recommended way to configure logging in production (via `.env` file)
- How to organize log files by timestamp or run

## Using Logging in Production

After running the demo, add these to your `.env` file:

```bash
LOG_OUTPUT=both              # Options: console, file, both
LOG_FILE_PATH=logs/ocean_report.log
LOG_LEVEL=INFO               # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

Then just run your normal script:
```bash
python scripts/run_report.py
```

The logging will automatically be configured from your environment variables!
