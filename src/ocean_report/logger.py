"""Logging configuration for ocean report."""

import logging
from enum import Enum
from pathlib import Path
from typing import Optional


class LogOutput(Enum):
    """Logging output destination options."""

    CONSOLE = "console"  # Print to terminal only
    FILE = "file"  # Write to log file only
    BOTH = "both"  # Both terminal and log file


# Create the base logger
logger = logging.getLogger("ocean_report")


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

    Examples:
        >>> # Console only (default)
        >>> configure_logger()

        >>> # File only
        >>> configure_logger(LogOutput.FILE, log_file="ocean_report.log")

        >>> # Both console and file
        >>> configure_logger(LogOutput.BOTH, log_file="logs/report.log")

        >>> # With custom level
        >>> configure_logger(LogOutput.BOTH, log_file="debug.log", level=logging.DEBUG)
    """
    # Validate file path if needed
    if output in (LogOutput.FILE, LogOutput.BOTH) and not log_file:
        raise ValueError(f"log_file must be provided when output is {output.value}")

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()
    logger.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(log_format)

    # Add console handler
    if output in (LogOutput.CONSOLE, LogOutput.BOTH):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler
    if output in (LogOutput.FILE, LogOutput.BOTH):
        log_path = Path(log_file)
        # Create parent directories if they don't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to avoid duplicate logs
    logger.propagate = False

    return logger


# Initialize with default console logging for backward compatibility
if not logger.handlers:
    configure_logger()
