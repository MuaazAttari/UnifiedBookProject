from fastapi import APIRouter

from src.api.v1 import configuration, chapters, chat, auth, translation, personalization

api_router = APIRouter()

# Include all API routes
api_router.include_router(configuration.router, prefix="/configuration", tags=["configuration"])
api_router.include_router(chapters.router, prefix="/chapters", tags=["chapters"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(translation.router, prefix="/translation", tags=["translation"])
api_router.include_router(personalization.router, prefix="/personalization", tags=["personalization"])