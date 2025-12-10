import hashlib
import time
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta

from src.models.translation_cache import TranslationCache
from src.utils.text_utils import chunk_text  # Assuming we have a text utility


class TranslationService:
    """Service class for translation functionality with caching."""

    def __init__(self):
        # In a real implementation, this would initialize the Google Cloud Translation client
        # self.client = translate.TranslationServiceClient()
        pass

    @staticmethod
    def get_cached_translation(db: Session, text: str, target_language: str, source_language: str = "en") -> Optional[str]:
        """
        Get cached translation if available.

        Args:
            db: Database session
            text: Text to translate
            target_language: Target language code (e.g., 'ur', 'es', 'fr')
            source_language: Source language code (default 'en')

        Returns:
            Cached translation or None if not found
        """
        # Create a hash of the source text for lookup
        text_hash = hashlib.sha256(f"{text}_{source_language}_{target_language}".encode()).hexdigest()

        cached = db.query(TranslationCache).filter(
            TranslationCache.source_text_hash == text_hash,
            TranslationCache.target_language == target_language,
            TranslationCache.source_language == source_language
        ).first()

        if cached:
            # Update last accessed time
            cached.last_accessed = datetime.now()
            db.commit()
            return cached.translated_text

        return None

    @staticmethod
    def cache_translation(db: Session, text: str, translated_text: str, target_language: str, source_language: str = "en"):
        """
        Cache a translation.

        Args:
            db: Database session
            text: Original text
            translated_text: Translated text
            target_language: Target language code
            source_language: Source language code
        """
        text_hash = hashlib.sha256(f"{text}_{source_language}_{target_language}".encode()).hexdigest()

        # Check if already exists
        existing = db.query(TranslationCache).filter(
            TranslationCache.source_text_hash == text_hash
        ).first()

        if existing:
            # Update existing cache entry
            existing.translated_text = translated_text
            existing.updated_at = datetime.now()
            existing.last_accessed = datetime.now()
        else:
            # Create new cache entry
            cache_entry = TranslationCache(
                source_text_hash=text_hash,
                source_text=text,
                target_language=target_language,
                translated_text=translated_text,
                source_language=source_language
            )
            db.add(cache_entry)

        db.commit()

    def translate_text(self, text: str, target_language: str, source_language: str = "en", use_cache: bool = True) -> str:
        """
        Translate text with caching support.

        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code
            use_cache: Whether to use cached translations

        Returns:
            Translated text
        """
        # For now, implementing a mock translation service
        # In a real implementation, this would call the Google Cloud Translation API
        if use_cache and hasattr(self, '_db_session'):
            cached = self.get_cached_translation(self._db_session, text, target_language, source_language)
            if cached:
                return cached

        # Mock translation - in real implementation, use Google Cloud Translation API
        translated_text = self._mock_translate(text, target_language)

        if use_cache and hasattr(self, '_db_session'):
            self.cache_translation(self._db_session, text, translated_text, target_language, source_language)

        return translated_text

    def translate_text_with_db(self, db: Session, text: str, target_language: str, source_language: str = "en", use_cache: bool = True) -> str:
        """
        Translate text with database session for caching.

        Args:
            db: Database session
            text: Text to translate
            target_language: Target language code
            source_language: Source language code
            use_cache: Whether to use cached translations

        Returns:
            Translated text
        """
        if use_cache:
            cached = TranslationService.get_cached_translation(db, text, target_language, source_language)
            if cached:
                return cached

        # Mock translation - in real implementation, use Google Cloud Translation API
        translated_text = self._mock_translate(text, target_language)

        if use_cache:
            TranslationService.cache_translation(db, text, translated_text, target_language, source_language)

        return translated_text

    def _mock_translate(self, text: str, target_language: str) -> str:
        """
        Mock translation function for demonstration purposes.
        In a real implementation, this would call the Google Cloud Translation API.

        Args:
            text: Text to translate
            target_language: Target language code

        Returns:
            Translated text (mocked)

        Raises:
            Exception: If translation fails
        """
        # Validate inputs
        if not text or not text.strip():
            raise ValueError("Text to translate cannot be empty")

        if not target_language or not target_language.strip():
            raise ValueError("Target language cannot be empty")

        # This is a mock implementation - in real system, integrate with Google Cloud Translation API
        try:
            if target_language.lower() == 'ur':  # Urdu
                # For demonstration, we'll return a placeholder
                return f"[URDU TRANSLATION] {text} [TRANSLATED TO URDU]"
            elif target_language.lower() == 'es':  # Spanish
                return f"[SPANISH TRANSLATION] {text} [TRADUCIDO AL ESPAÑOL]"
            elif target_language.lower() == 'fr':  # French
                return f"[FRENCH TRANSLATION] {text} [TRADUIT EN FRANÇAIS]"
            else:
                # Default to English with identifier
                return f"[{target_language.upper()} TRANSLATION] {text} [TRANSLATED TO {target_language.upper()}]"
        except Exception as e:
            raise Exception(f"Translation service error: {str(e)}")

    def translate_text_with_db(self, db: Session, text: str, target_language: str, source_language: str = "en", use_cache: bool = True) -> str:
        """
        Translate text with database session for caching.

        Args:
            db: Database session
            text: Text to translate
            target_language: Target language code
            source_language: Source language code
            use_cache: Whether to use cached translations

        Returns:
            Translated text

        Raises:
            Exception: If translation fails
        """
        # Validate inputs
        if not text or not text.strip():
            raise ValueError("Text to translate cannot be empty")

        if not target_language or not target_language.strip():
            raise ValueError("Target language cannot be empty")

        if use_cache:
            cached = TranslationService.get_cached_translation(db, text, target_language, source_language)
            if cached:
                return cached

        try:
            # Mock translation - in real implementation, use Google Cloud Translation API
            translated_text = self._mock_translate(text, target_language)

            if use_cache:
                TranslationService.cache_translation(db, text, translated_text, target_language, source_language)

            return translated_text
        except Exception as e:
            # Log the error for debugging
            print(f"Translation error: {str(e)}")
            # Re-raise the exception to be handled by the caller
            raise

    def translate_large_text(self, db: Session, text: str, target_language: str, source_language: str = "en",
                           chunk_size: int = 1000, overlap: int = 100) -> str:
        """
        Translate large text by breaking it into chunks.

        Args:
            db: Database session
            text: Large text to translate
            target_language: Target language code
            source_language: Source language code
            chunk_size: Size of text chunks
            overlap: Overlap between chunks to maintain context

        Returns:
            Translated text
        """
        # Split text into chunks
        chunks = chunk_text(text, chunk_size, overlap)
        translated_chunks = []

        for chunk in chunks:
            translated_chunk = self.translate_text_with_db(db, chunk, target_language, source_language)
            translated_chunks.append(translated_chunk)

        # Combine translated chunks
        # Note: In a real implementation, we'd need to handle the overlap properly
        result = " ".join(translated_chunks)

        # Remove overlap artifacts if any
        result = result.replace(f" [TRANSLATED TO {target_language.upper()}] [TRANSLATED TO {target_language.upper()}] ",
                               f" [TRANSLATED TO {target_language.upper()}] ")

        return result

    def clear_expired_cache(self, db: Session, hours_old: int = 24 * 30):  # 30 days default
        """
        Clear expired cache entries.

        Args:
            db: Database session
            hours_old: Entries older than this many hours will be cleared
        """
        cutoff_time = datetime.now() - timedelta(hours=hours_old)

        expired_entries = db.query(TranslationCache).filter(
            TranslationCache.updated_at < cutoff_time
        ).delete()

        db.commit()
        return expired_entries

    def clear_cache_by_language(self, db: Session, target_language: str = None, source_language: str = None):
        """
        Clear cache entries by language.

        Args:
            db: Database session
            target_language: Target language to clear (optional)
            source_language: Source language to clear (optional)

        Returns:
            Number of entries deleted
        """
        query = db.query(TranslationCache)

        if target_language:
            query = query.filter(TranslationCache.target_language == target_language)
        if source_language:
            query = query.filter(TranslationCache.source_language == source_language)

        deleted_count = query.delete()
        db.commit()
        return deleted_count

    def clear_all_cache(self, db: Session):
        """
        Clear all cache entries.

        Args:
            db: Database session

        Returns:
            Number of entries deleted
        """
        deleted_count = db.query(TranslationCache).delete()
        db.commit()
        return deleted_count

    def get_cache_size_by_language(self, db: Session) -> dict:
        """
        Get cache size statistics by language.

        Args:
            db: Database session

        Returns:
            Dictionary with cache size by language combination
        """
        from sqlalchemy import func

        # Get count by target language
        target_lang_stats = db.query(
            TranslationCache.target_language,
            func.count(TranslationCache.id).label('count')
        ).group_by(TranslationCache.target_language).all()

        # Get count by source/target language combination
        lang_combo_stats = db.query(
            TranslationCache.source_language,
            TranslationCache.target_language,
            func.count(TranslationCache.id).label('count')
        ).group_by(
            TranslationCache.source_language,
            TranslationCache.target_language
        ).all()

        return {
            "by_target_language": {lang: count for lang, count in target_lang_stats},
            "by_language_combo": {(src, tgt): count for src, tgt, count in lang_combo_stats}
        }

    def get_cache_usage_stats(self, db: Session, days_old: int = 30):
        """
        Get cache usage statistics.

        Args:
            db: Database session
            days_old: Consider entries from last N days

        Returns:
            Dictionary with cache usage statistics
        """
        from sqlalchemy import func

        cutoff_time = datetime.now() - timedelta(days=days_old)

        # Total entries
        total_entries = db.query(TranslationCache).count()

        # Recent entries
        recent_entries = db.query(TranslationCache).filter(
            TranslationCache.created_at >= cutoff_time
        ).count()

        # Most accessed entries (based on last_accessed)
        recent_accessed_entries = db.query(TranslationCache).filter(
            TranslationCache.last_accessed >= cutoff_time
        ).count()

        # Average time since last access
        avg_time_since_access = db.query(
            func.avg(func.julianday(datetime.now()) - func.julianday(TranslationCache.last_accessed))
        ).scalar()

        return {
            "total_entries": total_entries,
            "recent_entries": recent_entries,
            "recently_accessed_entries": recent_accessed_entries,
            "average_days_since_access": avg_time_since_access,
            "coverage_period": f"Last {days_old} days"
        }

    def get_cache_stats(self, db: Session) -> dict:
        """
        Get cache statistics.

        Args:
            db: Database session

        Returns:
            Dictionary with cache statistics
        """
        total_entries = db.query(TranslationCache).count()

        # Get stats by language
        from sqlalchemy import func
        language_stats = db.query(
            TranslationCache.target_language,
            func.count(TranslationCache.id).label('count')
        ).group_by(TranslationCache.target_language).all()

        return {
            "total_entries": total_entries,
            "by_language": {lang: count for lang, count in language_stats},
            "last_updated": datetime.now()
        }