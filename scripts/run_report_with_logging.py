#!/usr/bin/env python3
"""Example: Run ocean report with file logging enabled."""

from datetime import datetime
from pathlib import Path

import ocean_report
from ocean_report import configure_logger, LogOutput

# Configuration
CONFIG_FILE = "configs/config.yaml"
RUN_EMAIL = False
TEST = False

# Configure logger to write to both console and file
LOG_DIR = Path("logs/reports")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = LOG_DIR / f"ocean_report_{timestamp}.log"

# Setup logger BEFORE running the report
configure_logger(
    output=LogOutput.BOTH,  # Write to both terminal and file
    log_file=log_file,
)

print(f"📝 Logging to: {log_file}\n")


def main():
    """Run the ocean report with file logging."""
    ocean_report.hello()
    ocean_report.run_report(cfg_path=CONFIG_FILE, run_email=RUN_EMAIL, test=TEST)
    print(f"\n✅ Complete log saved to: {log_file}")
    print(f"   View with: cat {log_file}")


if __name__ == "__main__":
    main()
