#!/usr/bin/env python3
"""Demo script showing logger configurations via environment variables.

This demonstrates how to control logging by setting environment variables
BEFORE running the report. This is the recommended production approach.
"""

import os
from datetime import datetime

import ocean_report


def demo_console_only():
    """Demo 1: Console output only (default)."""
    print("\n" + "=" * 70)
    print("DEMO 1: Console Only (Default)")
    print("=" * 70)
    print("Setting: LOG_OUTPUT=console")
    print("=" * 70)

    # Set environment variables for this run
    os.environ["LOG_OUTPUT"] = "console"
    os.environ["LOG_LEVEL"] = "INFO"

    # Run a quick report
    ocean_report.run_report(run_email=False, test=True)


def demo_file_only():
    """Demo 2: File output only."""
    print("\n" + "=" * 70)
    print("DEMO 2: File Only")
    print("=" * 70)
    print("Setting: LOG_OUTPUT=file")
    print("         LOG_FILE_PATH=logs/demos/demo_file_only.log")
    print("=" * 70)

    # Set environment variables for this run
    os.environ["LOG_OUTPUT"] = "file"
    os.environ["LOG_FILE_PATH"] = "logs/demos/demo_file_only.log"
    os.environ["LOG_LEVEL"] = "INFO"

    print("\n⚠️  You won't see log output in terminal...")
    ocean_report.run_report(run_email=False, test=True)

    print(f"\n✅ Check the log file: {os.environ['LOG_FILE_PATH']}")
    print(f"   View with: cat {os.environ['LOG_FILE_PATH']}")


def demo_both_outputs():
    """Demo 3: Both console and file output."""
    print("\n" + "=" * 70)
    print("DEMO 3: Both Console and File")
    print("=" * 70)
    print("Setting: LOG_OUTPUT=both")
    print("         LOG_FILE_PATH=logs/demos/demo_both.log")
    print("=" * 70)

    # Set environment variables for this run
    os.environ["LOG_OUTPUT"] = "both"
    os.environ["LOG_FILE_PATH"] = "logs/demos/demo_both.log"
    os.environ["LOG_LEVEL"] = "INFO"

    ocean_report.run_report(run_email=False, test=True)

    print(f"\n✅ Also logged to: {os.environ['LOG_FILE_PATH']}")


def demo_debug_level():
    """Demo 4: Debug level logging."""
    print("\n" + "=" * 70)
    print("DEMO 4: Debug Level with Both Outputs")
    print("=" * 70)
    print("Setting: LOG_OUTPUT=both")
    print("         LOG_LEVEL=DEBUG")
    print("         LOG_FILE_PATH=logs/demos/demo_debug.log")
    print("=" * 70)

    # Set environment variables for this run
    os.environ["LOG_OUTPUT"] = "both"
    os.environ["LOG_FILE_PATH"] = "logs/demos/demo_debug.log"
    os.environ["LOG_LEVEL"] = "DEBUG"

    ocean_report.run_report(run_email=False, test=True)

    print(f"\n✅ Detailed debug logs in: {os.environ['LOG_FILE_PATH']}")


def demo_timestamped_logs():
    """Demo 5: Organizing logs by timestamp."""
    print("\n" + "=" * 70)
    print("DEMO 5: Timestamped Log Files")
    print("=" * 70)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"logs/demos/runs/ocean_report_{timestamp}.log"

    print(f"Setting: LOG_OUTPUT=both")
    print(f"         LOG_FILE_PATH={log_file}")
    print("=" * 70)

    # Set environment variables for this run
    os.environ["LOG_OUTPUT"] = "both"
    os.environ["LOG_FILE_PATH"] = log_file
    os.environ["LOG_LEVEL"] = "INFO"

    ocean_report.run_report(run_email=False, test=True)

    print(f"\n✅ Timestamped log created: {log_file}")


def main():
    """Run all logger demos using environment variables."""
    print("\n" + "=" * 70)
    print("OCEAN REPORT LOGGING DEMOS - Environment Variable Control")
    print("=" * 70)
    print("\nThis demo shows how to control logging via environment variables:")
    print("  • LOG_OUTPUT: console, file, or both")
    print("  • LOG_FILE_PATH: where to write log files")
    print("  • LOG_LEVEL: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    print("\nThese can be set in:")
    print("  1. .env file (recommended)")
    print("  2. Shell environment (export LOG_OUTPUT=both)")
    print("  3. Programmatically (os.environ['LOG_OUTPUT'] = 'both')")
    print("=" * 70)

    input("\nPress Enter to start demos...")

    # Run demos
    demo_console_only()
    input("\n\nPress Enter for next demo...")

    demo_file_only()
    input("\n\nPress Enter for next demo...")

    demo_both_outputs()
    input("\n\nPress Enter for next demo...")

    demo_debug_level()
    input("\n\nPress Enter for next demo...")

    demo_timestamped_logs()

    # Summary
    print("\n" + "=" * 70)
    print("DEMOS COMPLETE!")
    print("=" * 70)
    print("\n📁 Check the logs/demos/ directory for generated files")
    print("\n💡 To use in production, add to your .env file:")
    print("   LOG_OUTPUT=both")
    print("   LOG_FILE_PATH=logs/ocean_report.log")
    print("   LOG_LEVEL=INFO")
    print("\n   Then just run: python scripts/run_report.py")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
