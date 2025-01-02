"""
Logging Utilities Module

This module provides enhanced logging functionality for the API.
It includes:
- Basic logging configuration
- Exception logging decorator
- JSON-formatted error logging

The module sets up both file and console logging handlers with detailed formatting.
"""

import json
import logging
import traceback
from datetime import datetime
from functools import wraps

# Basic logging configuration
# Outputs to both file and console with timestamp and log level
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("api.log"),  # File output
        logging.StreamHandler(),  # Console output
    ],
)

logger = logging.getLogger(__name__)


def log_exception(func):
    """
    Decorator to automatically log exceptions with detailed information.

    This decorator wraps a function and logs any exceptions that occur
    during its execution. The log includes:
    - Timestamp
    - Function name
    - Exception type and message
    - Full stack trace

    Args:
        func: The function to wrap with exception logging.

    Returns:
        function: The wrapped function with exception logging.

    Example:
        @log_exception
        def my_function():
            # Function code here
            pass
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Create detailed error log entry
            error_details = {
                "timestamp": datetime.now().isoformat(),
                "function": func.__name__,
                "error_type": type(e).__name__,
                "error_message": str(e),
                "traceback": traceback.format_exc(),
            }
            # Log error details in JSON format for better parsing
            logger.error(f"Exception details: {json.dumps(error_details, indent=2)}")
            raise  # Re-raise the exception after logging

    return wrapper
