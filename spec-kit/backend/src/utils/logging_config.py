import logging
import logging.handlers
import os
from typing import Optional
from ..config.settings import settings

def setup_logging():
    """
    Set up logging configuration for the application.
    """
    # Create a custom logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Create formatters and add it to handlers
    formatter = logging.Formatter(settings.log_format)

    # Create console handler and set level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.log_level.upper()))
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)

    # Add file handler if log_file is specified
    if settings.log_file:
        # Ensure the log directory exists
        log_dir = os.path.dirname(settings.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Create file handler for rotating logs
        file_handler = logging.handlers.RotatingFileHandler(
            settings.log_file,
            maxBytes=settings.log_file_max_size,
            backupCount=settings.log_file_backup_count
        )
        file_handler.setLevel(getattr(logging, settings.log_level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent duplicate logs from propagating to root logger
    logger.propagate = False

    # Set specific log levels for third-party libraries to avoid too much noise
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    """
    return logging.getLogger(name)


# Initialize logging when module is imported
setup_logging()