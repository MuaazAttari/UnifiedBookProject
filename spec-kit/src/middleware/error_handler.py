"""
Comprehensive error handling middleware for the Unified Physical AI & Humanoid Robotics Learning Book project.
This module provides centralized error handling across all components.
"""

import logging
import traceback
from typing import Callable, Awaitable, Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware


# Import the logger after creating the logging_config.py file
from src.utils.logging_config import get_logger


logger = get_logger(__name__)


class ComprehensiveErrorHandler:
    """Centralized error handler for the application."""

    @staticmethod
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        """Handle request validation errors."""
        logger.warning(f"Validation error for {request.url.path}: {exc.errors()}")

        error_details = []
        for error in exc.errors():
            error_details.append({
                "loc": error["loc"],
                "type": error["type"],
                "msg": error["msg"],
                "input": error.get("input", "N/A")
            })

        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation Error",
                "details": error_details,
                "message": "Request validation failed. Please check input parameters."
            }
        )

    @staticmethod
    async def handle_http_exception(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions."""
        logger.info(f"HTTP {exc.status_code} error for {request.url.path}: {exc.detail}")

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": f"HTTP {exc.status_code}",
                "details": str(exc.detail),
                "path": str(request.url.path)
            }
        )

    @staticmethod
    async def handle_general_exception(request: Request, exc: Exception):
        """Handle general exceptions."""
        error_id = __import__('uuid').uuid4().hex[:8]
        logger.error(f"Error ID {error_id} - Path: {request.url.path}, Error: {str(exc)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        # Don't expose internal error details in production
        error_message = "An internal server error occurred. Please try again later."

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "error_id": error_id,
                "message": error_message,
                "path": str(request.url.path)
            }
        )


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive request logging."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[any]]):
        """Process request and log details."""
        import time
        start_time = time.time()

        # Log request
        logger.info(f"Request: {request.method} {request.url.path} - Headers: {dict(request.headers)}")

        try:
            response = await call_next(request)
        except Exception as e:
            # Handle exception with our error handler
            if isinstance(e, RequestValidationError):
                return await ComprehensiveErrorHandler.handle_validation_error(request, e)
            elif isinstance(e, StarletteHTTPException):
                return await ComprehensiveErrorHandler.handle_http_exception(request, e)
            else:
                return await ComprehensiveErrorHandler.handle_general_exception(request, e)

        # Calculate response time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        # Log response
        logger.info(f"Response: {response.status_code} for {request.method} {request.url.path} - Process time: {process_time:.3f}s")

        return response


def add_error_handlers(app: FastAPI):
    """Add comprehensive exception handlers to the FastAPI application."""
    app.add_exception_handler(RequestValidationError, ComprehensiveErrorHandler.handle_validation_error)
    app.add_exception_handler(StarletteHTTPException, ComprehensiveErrorHandler.handle_http_exception)

    # Handle general exceptions
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return await ComprehensiveErrorHandler.handle_general_exception(request, exc)


def setup_error_monitoring():
    """Setup comprehensive error monitoring and logging."""
    # Create logs directory if it doesn't exist
    import os
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger.info("Error monitoring and logging configured")


# Additional utility functions for error handling in services
def handle_service_error(service_name: str, operation: str, error: Exception, user_friendly_msg: str = None):
    """Generic error handler for service operations."""
    error_id = __import__('uuid').uuid4().hex[:8]
    logger.error(f"Service Error ID {error_id} - {service_name}.{operation}: {str(error)}")
    logger.error(f"Traceback: {traceback.format_exc()}")

    user_message = user_friendly_msg or "An error occurred while processing your request."

    return {
        "error": True,
        "error_id": error_id,
        "message": user_message,
        "service": service_name,
        "operation": operation
    }


def validate_and_handle_input_errors(input_data: dict, required_fields: list = None, field_validations: dict = None):
    """Validate input data and handle validation errors."""
    if required_fields:
        missing_fields = [field for field in required_fields if field not in input_data or input_data[field] is None]
        if missing_fields:
            return {
                "error": True,
                "message": f"Missing required fields: {', '.join(missing_fields)}",
                "missing_fields": missing_fields
            }

    if field_validations:
        validation_errors = []
        for field, validation_func in field_validations.items():
            if field in input_data:
                try:
                    is_valid, error_msg = validation_func(input_data[field])
                    if not is_valid:
                        validation_errors.append({"field": field, "error": error_msg})
                except Exception as e:
                    validation_errors.append({"field": field, "error": f"Validation error: {str(e)}"})

        if validation_errors:
            return {
                "error": True,
                "message": "Input validation failed",
                "validation_errors": validation_errors
            }

    return {"error": False, "data": input_data}


def safe_execute(func, *args, **kwargs):
    """Safely execute a function and handle any exceptions."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_id = __import__('uuid').uuid4().hex[:8]
        logger.error(f"Safe execution error ID {error_id}: {str(e)}")
        logger.error(f"Function: {func.__name__ if hasattr(func, '__name__') else 'unknown'}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        return {
            "error": True,
            "error_id": error_id,
            "message": "An error occurred during execution",
            "function": getattr(func, '__name__', 'unknown')
        }


# Custom exceptions for specific use cases
class DatabaseConnectionError(Exception):
    """Raised when database connection fails."""
    pass


class ExternalServiceError(Exception):
    """Raised when external service calls fail."""
    pass


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class AuthorizationError(Exception):
    """Raised when authorization fails."""
    pass


class RateLimitError(Exception):
    """Raised when rate limit is exceeded."""
    pass


def create_error_response(status_code: int, message: str, error_code: str = None, details: dict = None):
    """Create a standardized error response."""
    response = {
        "success": False,
        "error": True,
        "message": message,
        "status_code": status_code
    }

    if error_code:
        response["error_code"] = error_code

    if details:
        response["details"] = details

    return JSONResponse(status_code=status_code, content=response)


__all__ = [
    "ComprehensiveErrorHandler",
    "LoggingMiddleware",
    "add_error_handlers",
    "setup_error_monitoring",
    "handle_service_error",
    "validate_and_handle_input_errors",
    "safe_execute",
    "DatabaseConnectionError",
    "ExternalServiceError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "RateLimitError",
    "create_error_response"
]