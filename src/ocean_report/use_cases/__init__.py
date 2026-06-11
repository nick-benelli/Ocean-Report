"""Use cases (application orchestration layer) for ocean report."""

from . import tides
from . import water_temperature
from . import wind

__all__ = ["tides", "water_temperature", "wind"]
