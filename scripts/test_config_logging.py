#!/usr/bin/env python3
"""Test script: Run report with logging configured via config.yaml."""

import ocean_report

# Configuration - Using config file with logging settings
CONFIG_FILE = "configs/config_with_logging.yaml"
RUN_EMAIL = False
TEST = False


def main():
    """Run the ocean report with config-based logging."""
    print("=" * 70)
    print("Testing Config-Based Logger Configuration")
    print("=" * 70)
    print("\nThis config file specifies:")
    print("  - output: both (console + file)")
    print("  - file_path: logs/test_config_logging.log")
    print("  - level: INFO")
    print("\n" + "=" * 70 + "\n")

    ocean_report.hello()
    ocean_report.run_report(cfg_path=CONFIG_FILE, run_email=RUN_EMAIL, test=TEST)

    print("\n" + "=" * 70)
    print("✅ Check the log file at: logs/test_config_logging.log")
    print("   View with: cat logs/test_config_logging.log")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
