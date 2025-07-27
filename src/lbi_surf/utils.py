import os
import yaml
from dotenv import load_dotenv
from string import Template
from .constants import CONFIG_PATH


def load_config_with_env_substitution(path: str = CONFIG_PATH) -> dict:
    """Load YAML config and substitute environment variables."""
    # Load .env file into environment
    load_dotenv()

    with open(path) as f:
        content = f.read()

    # Replace ${VAR_NAME} with environment variable values
    template = Template(content)
    substituted = template.substitute(os.environ)

    return yaml.safe_load(substituted)
