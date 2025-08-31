import logging
import sys
from logging.handlers import RotatingFileHandler

# Log format
LOG_FORMAT = "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"

# Configure root logger
logging.basicConfig(
    level=logging.INFO,  # Default level
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),  # Console output
        RotatingFileHandler("backend.log", maxBytes=5_000_000, backupCount=5),  # File rotation
    ],
)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given module.
    Example: logger = get_logger(__name__)
    """
    return logging.getLogger(name)
