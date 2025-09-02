import os
from dotenv import find_dotenv

PROJECT_DIR = os.path.dirname(find_dotenv("pyproject.toml")) or os.getcwd()
CONFIG_PATH = os.path.join(PROJECT_DIR, "config.yaml")

