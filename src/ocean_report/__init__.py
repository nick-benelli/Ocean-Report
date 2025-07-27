# def main() -> None:
#     print("Hello from lbi-surf!")
def hello() -> None:
    print("Hello from ocean-report!")


from . import config, emailer as emailer, tide, water_temp  # noqa: E402, F401
from .main import main  # noqa: E402, F401

__all__ = [
    "hello",
    "main",
    "config",
    "emailer",
    "tide",
    "water_temp",
]
