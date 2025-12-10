from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from src.utils.auth import decode_access_token, get_current_user_id


class AuthMiddleware:
    """
    Authentication middleware to protect API routes.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)

        # Skip auth for public routes
        path = request.url.path
        public_routes = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/"
        ]

        # Check if the path starts with any public route
        is_public = any(path.startswith(route) for route in public_routes)

        if not is_public and path.startswith("/api/v1/"):
            # Extract token from Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                response = JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Not authenticated"}
                )
                return await response(scope, receive, send)

            token = auth_header[7:]  # Remove "Bearer " prefix
            payload = decode_access_token(token)

            if payload is None:
                response = JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Could not validate credentials"}
                )
                return await response(scope, receive, send)

        return await self.app(scope, receive, send)


def get_current_user_from_request(request: Request) -> str:
    """
    Extract user ID from request headers.

    Args:
        request: FastAPI request object

    Returns:
        User ID string
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    token = auth_header[7:]  # Remove "Bearer " prefix
    user_id = get_current_user_id(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

    return user_id