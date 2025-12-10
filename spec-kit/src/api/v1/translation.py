from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from src.db.database import get_db
from src.services.translation_service import TranslationService
from src.utils.auth import get_current_user_id_from_token

router = APIRouter()


@router.post("/translate")
def translate_text(
    text: str,
    target_language: str,
    source_language: str = "en",
    use_cache: bool = True,
    user_id: str = Depends(get_current_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Translate text to the target language.

    Args:
        text: Text to translate
        target_language: Target language code (e.g., 'ur', 'es', 'fr')
        source_language: Source language code (default 'en')
        use_cache: Whether to use cached translations (default True)
        user_id: Current user ID (from auth)
        db: Database session
    """
    if not text or not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text to translate cannot be empty"
        )

    if not target_language or not target_language.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target language cannot be empty"
        )

    try:
        # Initialize translation service and translate
        translation_service = TranslationService()
        translated_text = translation_service.translate_text_with_db(
            db, text, target_language, source_language, use_cache
        )

        return {
            "original_text": text,
            "translated_text": translated_text,
            "source_language": source_language,
            "target_language": target_language,
            "translation_cached": not use_cache  # Simplified logic for demo
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )


@router.post("/translate-large")
def translate_large_text(
    text: str,
    target_language: str,
    source_language: str = "en",
    chunk_size: int = 1000,
    overlap: int = 100,
    user_id: str = Depends(get_current_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Translate large text by breaking it into chunks.

    Args:
        text: Large text to translate
        target_language: Target language code
        source_language: Source language code (default 'en')
        chunk_size: Size of text chunks (default 1000)
        overlap: Overlap between chunks (default 100)
        user_id: Current user ID (from auth)
        db: Database session
    """
    if not text or not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text to translate cannot be empty"
        )

    if not target_language or not target_language.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target language cannot be empty"
        )

    try:
        # Initialize translation service and translate large text
        translation_service = TranslationService()
        translated_text = translation_service.translate_large_text(
            db, text, target_language, source_language, chunk_size, overlap
        )

        return {
            "original_text": text,
            "translated_text": translated_text,
            "source_language": source_language,
            "target_language": target_language,
            "chunk_size": chunk_size,
            "overlap": overlap
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )


@router.get("/cache/stats")
def get_cache_stats(
    user_id: str = Depends(get_current_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Get translation cache statistics.

    Args:
        user_id: Current user ID (from auth)
        db: Database session
    """
    try:
        translation_service = TranslationService()
        stats = translation_service.get_cache_stats(db)

        return {
            "cache_stats": stats,
            "message": "Cache statistics retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache stats: {str(e)}"
        )


@router.post("/cache/clear")
def clear_cache(
    hours_old: int = 720,  # Default to 30 days
    target_language: Optional[str] = None,
    source_language: Optional[str] = None,
    clear_all: bool = False,
    user_id: str = Depends(get_current_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Clear cache entries based on various criteria.

    Args:
        hours_old: Entries older than this many hours will be cleared (default 720 = 30 days)
        target_language: Specific target language to clear (optional)
        source_language: Specific source language to clear (optional)
        clear_all: If True, clear all cache entries regardless of age (default False)
        user_id: Current user ID (from auth)
        db: Database session
    """
    try:
        translation_service = TranslationService()

        if clear_all:
            # Clear all cache entries
            cleared_count = translation_service.clear_all_cache(db)
            message = f"All cache cleared successfully. {cleared_count} entries removed."
        elif target_language or source_language:
            # Clear by language
            cleared_count = translation_service.clear_cache_by_language(
                db, target_language, source_language
            )
            lang_desc = f"target={target_language}" if target_language else ""
            if source_language:
                lang_desc += f"{' and ' if lang_desc else ''}source={source_language}"
            message = f"Cache cleared for {lang_desc}. {cleared_count} entries removed."
        else:
            # Clear expired entries
            cleared_count = translation_service.clear_expired_cache(db, hours_old)
            message = f"Expired cache cleared successfully. {cleared_count} entries removed."

        return {
            "cleared_entries": cleared_count,
            "message": message
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )


@router.get("/cache/size-stats")
def get_cache_size_stats(
    user_id: str = Depends(get_current_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Get cache size statistics by language.

    Args:
        user_id: Current user ID (from auth)
        db: Database session
    """
    try:
        translation_service = TranslationService()
        stats = translation_service.get_cache_size_by_language(db)

        return {
            "cache_size_stats": stats,
            "message": "Cache size statistics retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache size stats: {str(e)}"
        )


@router.get("/cache/usage-stats")
def get_cache_usage_stats(
    days_old: int = 30,
    user_id: str = Depends(get_current_user_id_from_token),
    db: Session = Depends(get_db)
):
    """
    Get cache usage statistics.

    Args:
        days_old: Consider entries from last N days (default 30)
        user_id: Current user ID (from auth)
        db: Database session
    """
    try:
        translation_service = TranslationService()
        stats = translation_service.get_cache_usage_stats(db, days_old)

        return {
            "cache_usage_stats": stats,
            "message": "Cache usage statistics retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cache usage stats: {str(e)}"
        )


@router.get("/supported-languages")
def get_supported_languages():
    """
    Get list of supported languages for translation.
    """
    # In a real implementation, this would come from the translation service
    supported_languages = [
        {"code": "ur", "name": "Urdu"},
        {"code": "es", "name": "Spanish"},
        {"code": "fr", "name": "French"},
        {"code": "de", "name": "German"},
        {"code": "it", "name": "Italian"},
        {"code": "pt", "name": "Portuguese"},
        {"code": "ru", "name": "Russian"},
        {"code": "zh", "name": "Chinese"},
        {"code": "ja", "name": "Japanese"},
        {"code": "ko", "name": "Korean"},
        {"code": "ar", "name": "Arabic"},
    ]

    return {
        "supported_languages": supported_languages,
        "default_source_language": "en"
    }