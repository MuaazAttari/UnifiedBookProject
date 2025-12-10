"""
Logging configuration for the Unified Physical AI & Humanoid Robotics Learning Book project.
This module provides centralized logging configuration across all components.
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


def get_logger(name: str, log_level: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Name of the logger (typically __name__ of the module)
        log_level: Optional log level override (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)

    # Set log level
    level = log_level or os.getenv('LOG_LEVEL', 'INFO').upper()
    logger.setLevel(getattr(logging, level))

    # Prevent adding handlers multiple times
    if logger.handlers:
        return logger

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # File handler for detailed logs
    log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(detailed_formatter)
    file_handler.setLevel(logging.DEBUG)  # File gets all logs

    # Console handler for important logs
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(simple_formatter)
    console_handler.setLevel(getattr(logging, level))

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def setup_logging():
    """
    Setup logging configuration for the entire application.
    This should be called once at application startup.
    """
    # Set up root logger
    root_logger = get_logger("root")
    root_logger.setLevel(logging.INFO)

    # Log application startup
    root_logger.info("Logging system initialized")
    root_logger.info(f"Log level set to: {os.getenv('LOG_LEVEL', 'INFO')}")


def get_error_logger() -> logging.Logger:
    """
    Get a special logger for errors and exceptions.

    Returns:
        Logger configured for error logging
    """
    return get_logger("error", log_level="ERROR")


def get_audit_logger() -> logging.Logger:
    """
    Get a special logger for audit trails.

    Returns:
        Logger configured for audit logging
    """
    audit_logger = get_logger("audit")
    audit_logger.setLevel(logging.INFO)
    return audit_logger


def log_api_call(
    logger: logging.Logger,
    endpoint: str,
    method: str,
    user_id: Optional[str] = None,
    status_code: Optional[int] = None,
    response_time: Optional[float] = None
):
    """
    Log API calls for monitoring and analytics.

    Args:
        logger: Logger instance to use
        endpoint: API endpoint that was called
        method: HTTP method (GET, POST, etc.)
        user_id: Optional user ID making the request
        status_code: HTTP status code of response
        response_time: Time taken to process the request in seconds
    """
    log_msg = f"API Call: {method} {endpoint}"
    if user_id:
        log_msg += f" by user {user_id}"
    if status_code:
        log_msg += f" - Status: {status_code}"
    if response_time:
        log_msg += f" - Response time: {response_time:.3f}s"

    logger.info(log_msg)


def log_performance_metric(
    logger: logging.Logger,
    metric_name: str,
    value: float,
    unit: str = "",
    context: Optional[dict] = None
):
    """
    Log performance metrics.

    Args:
        logger: Logger instance to use
        metric_name: Name of the metric being logged
        value: Value of the metric
        unit: Unit of measurement (optional)
        context: Additional context information (optional)
    """
    log_msg = f"Performance Metric: {metric_name} = {value}"
    if unit:
        log_msg += f" {unit}"

    if context:
        log_msg += f" | Context: {context}"

    logger.info(log_msg)


def log_security_event(
    logger: logging.Logger,
    event_type: str,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[dict] = None
):
    """
    Log security-related events.

    Args:
        logger: Logger instance to use
        event_type: Type of security event
        user_id: User ID involved in the event
        ip_address: IP address of the request
        details: Additional details about the event
    """
    log_msg = f"SECURITY EVENT: {event_type}"
    if user_id:
        log_msg += f" - User: {user_id}"
    if ip_address:
        log_msg += f" - IP: {ip_address}"

    logger.warning(log_msg)

    if details:
        logger.warning(f"Event details: {details}")


def log_user_action(
    logger: logging.Logger,
    action: str,
    user_id: str,
    resource: Optional[str] = None,
    metadata: Optional[dict] = None
):
    """
    Log user actions for audit trails.

    Args:
        logger: Logger instance to use
        action: Action performed by the user
        user_id: ID of the user performing the action
        resource: Resource affected by the action
        metadata: Additional metadata about the action
    """
    log_msg = f"USER ACTION: {action} by user {user_id}"
    if resource:
        log_msg += f" on resource {resource}"

    logger.info(log_msg)

    if metadata:
        logger.info(f"Action metadata: {metadata}")


def configure_structured_logging():
    """
    Configure structured logging with JSON format for better log analysis.
    """
    import json
    import logging.handlers

    class JSONFormatter(logging.Formatter):
        """Custom formatter to output logs in JSON format."""

        def format(self, record):
            log_entry = {
                'timestamp': datetime.utcfromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
            }

            # Add exception info if present
            if record.exc_info:
                log_entry['exception'] = self.formatException(record.exc_info)

            # Add any extra fields
            for key, value in record.__dict__.items():
                if key not in [
                    'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                    'filename', 'module', 'lineno', 'funcName', 'created',
                    'msecs', 'relativeCreated', 'thread', 'threadName',
                    'processName', 'process', 'getMessage', 'exc_info',
                    'exc_text', 'stack_info'
                ]:
                    log_entry[key] = value

            return json.dumps(log_entry)

    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Get root logger
    root_logger = logging.getLogger()

    # Clear existing handlers
    root_logger.handlers.clear()

    # Create JSON file handler
    json_log_file = log_dir / f"structured_{datetime.now().strftime('%Y%m%d')}.log"
    json_handler = logging.FileHandler(json_log_file, encoding='utf-8')
    json_handler.setFormatter(JSONFormatter())
    json_handler.setLevel(logging.DEBUG)

    # Create console handler with simple format
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)

    # Add handlers to root logger
    root_logger.addHandler(json_handler)
    root_logger.addHandler(console_handler)

    # Set root logger level
    root_logger.setLevel(logging.DEBUG)

    # Log configuration
    root_logger.info("Structured logging configured")


# Initialize logging system
setup_logging()

# Example usage:
if __name__ == "__main__":
    # Test the logging system
    app_logger = get_logger(__name__)
    app_logger.info("Testing application logger")

    error_logger = get_error_logger()
    error_logger.error("Testing error logger")

    audit_logger = get_audit_logger()
    audit_logger.info("Testing audit logger")

    # Test API call logging
    log_api_call(
        app_logger,
        "/api/v1/chat",
        "POST",
        user_id="test_user_123",
        status_code=200,
        response_time=0.15
    )

    # Test performance metric logging
    log_performance_metric(
        app_logger,
        "response_time",
        150.5,
        "milliseconds",
        {"endpoint": "/api/v1/chat", "method": "POST"}
    )