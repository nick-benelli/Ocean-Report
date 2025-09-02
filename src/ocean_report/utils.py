import os
import yaml
import requests
from typing import Optional
import certifi
from dotenv import load_dotenv
from string import Template
from .constants import CONFIG_PATH
from .logger import logger


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


def safe_get(url: str, **kwargs) -> Optional[requests.Response]:
    """
    Try to GET with certifi verification first.
    If SSL fails, retry with verify=False.
    """
    try:
        return requests.get(url, verify=certifi.where(), **kwargs)
    except requests.exceptions.SSLError as e:
        logger.warning("SSL verification failed (%s). Retrying with verify=False.", e)
        try:
            return requests.get(url, verify=False, **kwargs)
        except requests.exceptions.RequestException as e2:
            logger.error("Request failed even with verify=False: %s", e2)
            return None
