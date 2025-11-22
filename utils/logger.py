"""
Logging configuration for the application.
"""
import logging
import json
import sys
from datetime import datetime
from typing import Optional

from config import settings


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logger(name: str = "nanonets-vl", level: str = None) -> logging.Logger:
    """
    Set up and configure a logger.

    Args:
        name: Logger name.
        level: Log level (DEBUG, INFO, WARNING, ERROR).

    Returns:
        Configured logger.
    """
    logger = logging.getLogger(name)

    # Set level
    log_level = getattr(logging, (level or settings.logging.level).upper())
    logger.setLevel(log_level)

    # Clear existing handlers
    logger.handlers.clear()

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    # Set formatter based on config
    if settings.logging.format == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Add file handler if configured
    if settings.logging.file_path:
        file_handler = logging.FileHandler(settings.logging.file_path)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Global logger instance
logger = setup_logger()


if __name__ == "__main__":
    print("=" * 60)
    print("LOGGER MODULE TEST")
    print("=" * 60)

    test_logger = setup_logger("test", "DEBUG")

    test_logger.debug("Debug message")
    test_logger.info("Info message")
    test_logger.warning("Warning message")
    test_logger.error("Error message")

    print("\n  ✓ Logger tests passed")

    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
