from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Union
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomException(Exception):
    """Custom application exception"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions
    """
    logger.error(f"HTTPException: {exc.status_code} - {exc.detail} - URL: {request.url}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "HTTPException",
                "message": exc.detail,
                "status_code": exc.status_code
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors
    """
    logger.error(f"Validation error: {exc} - URL: {request.url}")

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "type": "ValidationError",
                "message": "Input validation failed",
                "details": exc.errors(),
                "status_code": 422
            }
        }
    )

async def custom_exception_handler(request: Request, exc: CustomException):
    """
    Handle custom application exceptions
    """
    logger.error(f"CustomException: {exc.status_code} - {exc.message} - URL: {request.url}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "type": "CustomException",
                "message": exc.message,
                "status_code": exc.status_code
            }
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle general/unexpected exceptions
    """
    logger.error(f"General exception: {str(exc)} - URL: {request.url}")
    logger.error(traceback.format_exc())

    # Log the full traceback in development
    if request.app.debug:
        logger.error(traceback.format_exc())

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "InternalServerError",
                "message": "An internal server error occurred",
                "status_code": 500
            }
        }
    )

def add_error_handlers(app: FastAPI):
    """
    Add error handlers to the FastAPI application
    """
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(CustomException, custom_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    return app