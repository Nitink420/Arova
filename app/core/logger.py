# app/core/logger.py
"""
AROVA Centralized Logging

Provides a single, configured logger for the entire application.
Replaces all scattered print() calls with structured, leveled logging.

Usage:
    from app.core.logger import get_logger
    logger = get_logger(__name__)
    logger.info("Model loaded successfully")
    logger.warning("Voice engine unavailable, disabling TTS")
    logger.error("Failed to generate PDF report", exc_info=True)
"""

import sys
import logging
from app.core.config import Config


# Module-level flag to prevent duplicate handler setup across imports
_logging_configured = False


def setup_logging() -> None:
    """
    Configure the root AROVA logger with console output.

    Called once at application startup. Subsequent calls are no-ops.
    Log level is read from Config().LOG_LEVEL.
    """
    global _logging_configured
    if _logging_configured:
        return
    _logging_configured = True

    config = Config()

    # Resolve log level from config string
    level = getattr(logging, config.LOG_LEVEL, logging.INFO)

    # Configure the root arova logger
    root_logger = logging.getLogger("arova")
    root_logger.setLevel(level)

    # Prevent duplicate handlers if called multiple times
    if root_logger.handlers:
        return

    # Console handler with UTF-8 support
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Format: [LEVEL] module_name — message
    formatter = logging.Formatter(
        fmt="[%(levelname)s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a child logger under the 'arova' namespace.

    Args:
        name: Module name (typically __name__).

    Returns:
        A configured logging.Logger instance.

    Example:
        logger = get_logger(__name__)
        logger.info("Service initialized")
    """
    # Ensure logging is configured
    setup_logging()

    # Strip common prefixes for cleaner log output
    clean_name = name
    for prefix in ("app.services.", "app.core.", "app.utils.", "app."):
        if clean_name.startswith(prefix):
            clean_name = clean_name[len(prefix):]
            break

    return logging.getLogger(f"arova.{clean_name}")
