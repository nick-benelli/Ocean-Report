# def main() -> None:
#     print("Hello from lbi-surf!")
def hello() -> None:
    print("Hello from lbi-surf!")


from . import emailer as emailer, constants, tide, water_temp  # noqa: E402, F401

from .main import main  # noqa: E402, F401
