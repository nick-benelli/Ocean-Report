#!/usr/bin/env python3
"""Demo script showing different logger configurations."""

import logging
from pathlib import Path

from ocean_report import configure_logger, logger, LogOutput


def demo_console_only():
    """Demo: Console output only (default behavior)."""
    print("\n" + "=" * 60)
    print("DEMO 1: Console Only (Default)")
    print("=" * 60)

    configure_logger(output=LogOutput.CONSOLE, level=logging.INFO)

    logger.info("This appears in the terminal")
    logger.warning("This is a warning in the terminal")
    logger.error("This is an error in the terminal")


def demo_file_only():
    """Demo: File output only."""
    print("\n" + "=" * 60)
    print("DEMO 2: File Only")
    print("=" * 60)

    log_file = Path("logs/ocean_report_file_only.log")
    configure_logger(output=LogOutput.FILE, log_file=log_file, level=logging.INFO)

    logger.info("This message goes to file only")
    logger.warning("You won't see this in terminal!")
    logger.error("Check the log file to see these messages")

    print(f"✓ Logs written to: {log_file.absolute()}")
    print(f"  View with: cat {log_file}")


def demo_both_outputs():
    """Demo: Both console and file output."""
    print("\n" + "=" * 60)
    print("DEMO 3: Both Console and File")
    print("=" * 60)

    log_file = Path("logs/ocean_report_both.log")
    configure_logger(output=LogOutput.BOTH, log_file=log_file, level=logging.INFO)

    logger.info("This appears in BOTH terminal and file")
    logger.warning("Warning logged to both destinations")
    logger.error("Error logged everywhere")

    print(f"\n✓ Logs also written to: {log_file.absolute()}")


def demo_debug_level():
    """Demo: Debug level logging to file."""
    print("\n" + "=" * 60)
    print("DEMO 4: Debug Level with Both Outputs")
    print("=" * 60)

    log_file = Path("logs/ocean_report_debug.log")
    configure_logger(output=LogOutput.BOTH, log_file=log_file, level=logging.DEBUG)

    logger.debug("This is a debug message (normally hidden)")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    print(f"\n✓ Debug logs written to: {log_file.absolute()}")


def demo_organize_by_date():
    """Demo: Organizing logs by date."""
    print("\n" + "=" * 60)
    print("DEMO 5: Organized Log Files")
    print("=" * 60)

    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = Path(f"logs/runs/ocean_report_{timestamp}.log")

    configure_logger(output=LogOutput.BOTH, log_file=log_file, level=logging.INFO)

    logger.info(f"Log file created at {timestamp}")
    logger.info("This helps organize logs by run time")

    print(f"\n✓ Timestamped log: {log_file.absolute()}")


def main():
    """Run all logger demos."""
    print("\n" + "=" * 60)
    print("OCEAN REPORT LOGGER CONFIGURATION DEMOS")
    print("=" * 60)

    # Run demos
    demo_console_only()
    demo_file_only()
    demo_both_outputs()
    demo_debug_level()
    demo_organize_by_date()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("\n3 Output Modes:")
    print("  • LogOutput.CONSOLE - Terminal only (default)")
    print("  • LogOutput.FILE    - File only")
    print("  • LogOutput.BOTH    - Terminal + File")
    print("\nUsage in your code:")
    print("  from ocean_report import configure_logger, LogOutput")
    print('  configure_logger(LogOutput.BOTH, log_file="logs/app.log")')
    print("\nCheck the logs/ directory for generated files!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
