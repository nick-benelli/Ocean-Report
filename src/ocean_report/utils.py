import os
import yaml
import requests
from typing import Optional
import certifi
from datetime import date, timedelta
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
        

# ---- Get Dates ----
def get_memorial_day(year: int) -> date:
    """
    Return the date of Memorial Day (last Monday of May) for a given year.

    Args:
        year (int): The year to calculate Memorial Day for.

    Returns:
        date: The date of Memorial Day in that year.
    """
    # May 31st of that year
    may_last = date(year, 5, 31)
    # Go backwards until Monday
    days_back_to_monday = (may_last.weekday() - 0) % 7
    return may_last - timedelta(days=days_back_to_monday)


def get_labor_day(year: int) -> date:
    """
    Return the date of Labor Day (first Monday of September) for a given year.

    Args:
        year (int): The year to calculate Labor Day for.

    Returns:
        date: The date of Labor Day in that year.
    """
    # September 1st of that year
    sept_first = date(year, 9, 1)
    # weekday() → Monday=0 ... Sunday=6
    days_until_monday = (0 - sept_first.weekday()) % 7
    return sept_first + timedelta(days=days_until_monday)


def determine_is_summer(today: date | None = None, memorial_day_offset: int = -4, labor_day_offset: int = 7) -> bool:
    """
    Determine if a given date is in 'summer' season:
    - Starts 4 days before Memorial Day. The default is -4.
    - Ends 7 days after Labor Day. The default is 7.
    """
    if today is None:
        today = date.today()
    
    year = today.year
    memorial_day = get_memorial_day(year) + timedelta(days=memorial_day_offset)
    labor_day = get_labor_day(year) + timedelta(days=labor_day_offset)

    return memorial_day <= today <= labor_day

