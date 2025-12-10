from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .v1 import textbook_generation, content_management, user_preferences, auth
from ..config.settings import settings
from ..middleware.error_handler import add_error_handlers
from ..utils.logging_config import get_logger

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Get logger
logger = get_logger(__name__)

# Add rate limiting to the app
app = FastAPI(
    title="Textbook Generation API",
    description="API for generating textbooks using AI",
    version="1.0.0",
    debug=settings.debug
)

# Add the rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure allowed origins based on environment
if settings.is_production:
    # In production, specify exact origins
    allowed_origins = [
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ]
else:
    # In local/staging, allow local development origins
    allowed_origins = settings.allowed_origins.split(",")

app = FastAPI(
    title="Textbook Generation API",
    description="API for generating textbooks using AI",
    version="1.0.0",
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Only allow credentials with specific origins in production
    allow_origin_regex=None if settings.is_production else None,
)

# Include API routes
app.include_router(textbook_generation.router, prefix="/api/v1", tags=["textbook-generation"])
app.include_router(content_management.router, prefix="/api/v1", tags=["content-management"])
app.include_router(user_preferences.router, prefix="/api/v1", tags=["user-preferences"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])

# Add error handlers
app = add_error_handlers(app)

@app.get("/")
def read_root():
    return {"message": "Textbook Generation API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}