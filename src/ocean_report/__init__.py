"""Ocean Report package initialization."""

from . import config  # noqa: F401
from . import emailer  # noqa: F401
from .services import tide_service  # noqa: F401
from .services import water_temp_service  # noqa: F401
from .workflows.report_runner import run_report  # noqa: F401


def hello() -> None:
    """Print hello message."""
    print("Hello from ocean-report!")


__all__ = [
    "hello",
    "run_report",
    "config",
    "emailer",
    "tide_service",
    "water_temp_service",
]
