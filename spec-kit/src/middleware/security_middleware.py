import time
from collections import defaultdict
from typing import Dict
from datetime import datetime, timedelta

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, requests_limit: int = 100, window_size: int = 60):
        super().__init__(app)
        self.requests_limit = requests_limit
        self.window_size = window_size  # in seconds
        self.requests: Dict[str, list] = defaultdict(list)

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host

        # Clean old requests
        now = datetime.utcnow()
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < timedelta(seconds=self.window_size)
        ]

        # Check if limit exceeded
        if len(self.requests[client_ip]) >= self.requests_limit:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )

        # Add current request
        self.requests[client_ip].append(now)

        response = await call_next(request)
        return response


# Add to __init__.py in middleware
__all__ = ["RateLimitMiddleware"]