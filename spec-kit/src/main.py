from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1 import api_router, websocket_chat
from src.config import settings
from src.middleware import LoggingMiddleware, add_error_handlers, RateLimitMiddleware

# Create FastAPI app instance
app = FastAPI(
    title="Unified Textbook Generation and RAG System API",
    description="API for the Unified Physical AI & Humanoid Robotics Learning Book project",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware, requests_limit=100, window_size=60)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add error handlers
add_error_handlers(app)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include WebSocket routes directly on the app (not under the API prefix)
app.add_websocket_route("/ws/{user_id}", websocket_chat.websocket_endpoint)
app.add_websocket_route("/ws/anonymous", websocket_chat.websocket_anonymous_endpoint)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Unified Textbook Generation and RAG System API"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "unified-book-api"}