"""Ocean Report package initialization."""

from . import config
from .logger import configure_logger, logger, LogOutput
from .services import tide_service
from .services import water_temp_service
from .workflows.report_runner import run_report


def hello() -> None:
    """Print hello message."""
    print("Hello from ocean-report!")


__all__ = [
    "hello",
    "run_report",
    "config",
    "logger",
    "configure_logger",
    "LogOutput",
    "tide_service",
    "water_temp_service",
]
