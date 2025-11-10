# src/ocean_report/logger.py
import logging

# Configure logging for Lambda
logger = logging.getLogger(__name__)
if not logger.handlers:  # Avoid duplicate handlers in Lambda
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger.setLevel(logging.INFO)
