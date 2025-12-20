from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime


router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint to verify the service is running"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "RAG Chatbot API",
        "version": "1.0.0"
    }