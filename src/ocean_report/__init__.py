"""Ocean Report package initialization."""

from . import config_loader  # noqa: F401
from . import emailer  # noqa: F401
from . import tide  # noqa: F401
from . import water_temp  # noqa: F401
from .main import run_report  # noqa: F401


def hello() -> None:
    """Print hello message."""
    print("Hello from ocean-report!")


__all__ = [
    "hello",
    "run_report",
    "config_loader",
    "emailer",
    "tide",
    "water_temp",
]
