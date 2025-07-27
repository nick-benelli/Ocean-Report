# src/lbi_surf/logger.py
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
# Create a logger instance
logger = logging.getLogger(__name__)
