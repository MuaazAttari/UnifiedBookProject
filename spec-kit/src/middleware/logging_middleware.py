import time
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Log request
        self.logger.info(f"Request: {request.method} {request.url}")

        response = await call_next(request)

        # Calculate process time
        process_time = time.time() - start_time

        # Log response
        self.logger.info(f"Response: {response.status_code} in {process_time:.2f}s")

        return response