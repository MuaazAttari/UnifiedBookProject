"""
Caching utilities for the Unified Physical AI & Humanoid Robotics Learning Book project.
This module provides caching strategies for performance optimization.
"""

import asyncio
import json
import time
import hashlib
from typing import Any, Optional, Dict, Callable, Awaitable
from functools import wraps
from datetime import datetime, timedelta
import redis
import pickle


class CacheManager:
    """Manages caching with multiple backends and strategies."""

    def __init__(self, cache_backend: str = "memory", redis_url: str = None):
        """
        Initialize the cache manager.

        Args:
            cache_backend: Cache backend to use ('memory', 'redis', or 'hybrid')
            redis_url: Redis connection URL (required if using Redis)
        """
        self.cache_backend = cache_backend
        self.redis_client = None

        if cache_backend in ["redis", "hybrid"] and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
            except Exception as e:
                print(f"Failed to connect to Redis: {e}")
                if cache_backend == "redis":
                    raise

        # In-memory cache (LRU-like)
        self.memory_cache = {}
        self.cache_access_times = {}
        self.max_memory_items = 1000  # Maximum items in memory cache

    def _generate_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate a unique cache key based on function and parameters."""
        key_data = {
            "func": func_name,
            "args": args,
            "kwargs": {k: v for k, v in sorted(kwargs.items())}  # Sort for consistency
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()

    def _get_cache_value(self, key: str) -> Optional[Any]:
        """Get value from cache (memory or Redis)."""
        if self.cache_backend in ["redis", "hybrid"] and self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return pickle.loads(value)
            except:
                pass  # Fall back to memory cache

        if self.cache_backend in ["memory", "hybrid"]:
            if key in self.memory_cache:
                # Update access time for LRU
                self.cache_access_times[key] = time.time()
                return self.memory_cache[key]

        return None

    def _set_cache_value(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache (memory or Redis)."""
        if self.cache_backend in ["redis", "hybrid"] and self.redis_client:
            try:
                self.redis_client.setex(key, ttl, pickle.dumps(value))
                return
            except:
                pass  # Fall back to memory cache

        if self.cache_backend in ["memory", "hybrid"]:
            # Implement simple LRU by removing oldest items when needed
            if len(self.memory_cache) >= self.max_memory_items:
                # Remove least recently used item
                oldest_key = min(self.cache_access_times.keys(),
                               key=lambda k: self.cache_access_times[k])
                del self.memory_cache[oldest_key]
                del self.cache_access_times[oldest_key]

            self.memory_cache[key] = value
            self.cache_access_times[key] = time.time()

    def _delete_cache_key(self, key: str):
        """Delete a key from cache."""
        if self.cache_backend in ["redis", "hybrid"] and self.redis_client:
            try:
                self.redis_client.delete(key)
            except:
                pass

        if self.cache_backend in ["memory", "hybrid"]:
            if key in self.memory_cache:
                del self.memory_cache[key]
                del self.cache_access_times[key]

    def cache(self, ttl: int = 3600, key_prefix: str = "cache"):
        """
        Decorator to cache function results.

        Args:
            ttl: Time to live in seconds
            key_prefix: Prefix for cache keys
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                key = f"{key_prefix}:{func.__name__}:{self._generate_key(func.__name__, args, kwargs)}"

                # Try to get from cache
                cached_result = self._get_cache_value(key)
                if cached_result is not None:
                    return cached_result

                # Execute function and cache result
                result = await func(*args, **kwargs)
                self._set_cache_value(key, result, ttl)
                return result

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                key = f"{key_prefix}:{func.__name__}:{self._generate_key(func.__name__, args, kwargs)}"

                # Try to get from cache
                cached_result = self._get_cache_value(key)
                if cached_result is not None:
                    return cached_result

                # Execute function and cache result
                result = func(*args, **kwargs)
                self._set_cache_value(key, result, ttl)
                return result

            # Return appropriate wrapper based on function type
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    def cache_method(self, ttl: int = 3600, key_prefix: str = "method_cache"):
        """
        Decorator to cache method results based on instance and parameters.

        Args:
            ttl: Time to live in seconds
            key_prefix: Prefix for cache keys
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(self, *args, **kwargs):
                instance_id = id(self)
                key = f"{key_prefix}:{instance_id}:{func.__name__}:{self._generate_key(func.__name__, args, kwargs)}"

                # Try to get from cache
                cached_result = self._get_cache_value(key)
                if cached_result is not None:
                    return cached_result

                # Execute method and cache result
                result = await func(self, *args, **kwargs)
                self._set_cache_value(key, result, ttl)
                return result

            @wraps(func)
            def sync_wrapper(self, *args, **kwargs):
                instance_id = id(self)
                key = f"{key_prefix}:{instance_id}:{func.__name__}:{self._generate_key(func.__name__, args, kwargs)}"

                # Try to get from cache
                cached_result = self._get_cache_value(key)
                if cached_result is not None:
                    return cached_result

                # Execute method and cache result
                result = func(self, *args, **kwargs)
                self._set_cache_value(key, result, ttl)
                return result

            # Return appropriate wrapper based on function type
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator

    def invalidate(self, pattern: str = "*"):
        """
        Invalidate cache entries matching a pattern.

        Args:
            pattern: Pattern to match cache keys (Redis pattern)
        """
        if self.cache_backend in ["redis", "hybrid"] and self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            except:
                pass

        if self.cache_backend in ["memory", "hybrid"]:
            # For memory cache, we'll clear all items (since we don't have pattern matching)
            if pattern == "*":
                self.memory_cache.clear()
                self.cache_access_times.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "backend": self.cache_backend,
            "memory_cache_size": len(self.memory_cache),
            "max_memory_items": self.max_memory_items
        }

        if self.cache_backend in ["redis", "hybrid"] and self.redis_client:
            try:
                redis_info = self.redis_client.info()
                stats["redis_connected"] = True
                stats["redis_used_memory"] = redis_info.get("used_memory_human", "N/A")
                stats["redis_connected_clients"] = redis_info.get("connected_clients", 0)
            except:
                stats["redis_connected"] = False

        return stats

    def clear_all(self):
        """Clear all cache entries."""
        if self.cache_backend in ["redis", "hybrid"] and self.redis_client:
            try:
                self.redis_client.flushdb()
            except:
                pass

        if self.cache_backend in ["memory", "hybrid"]:
            self.memory_cache.clear()
            self.cache_access_times.clear()


# Specific cache instances for different use cases
class TranslationCacheManager(CacheManager):
    """Cache manager specifically for translation services."""

    def __init__(self, cache_backend: str = "memory", redis_url: str = None):
        super().__init__(cache_backend, redis_url)

    @CacheManager.cache(ttl=86400, key_prefix="translation")  # 24 hours
    async def get_translation(self, source_text: str, target_language: str, source_language: str = "en") -> str:
        """Cached translation lookup."""
        # This would normally call the translation service
        # For now, return a mock translation
        return f"[TRANSLATED] {source_text} to {target_language}"

    @CacheManager.cache(ttl=3600, key_prefix="translation_metadata")  # 1 hour
    async def get_translation_metadata(self, source_text: str, target_language: str) -> Dict[str, Any]:
        """Cached translation metadata."""
        return {
            "source_text_hash": hashlib.sha256(f"{source_text}_{target_language}".encode()).hexdigest(),
            "cached_at": datetime.now().isoformat(),
            "target_language": target_language
        }


class EmbeddingCacheManager(CacheManager):
    """Cache manager specifically for embedding services."""

    def __init__(self, cache_backend: str = "memory", redis_url: str = None):
        super().__init__(cache_backend, redis_url)

    @CacheManager.cache(ttl=7200, key_prefix="embedding")  # 2 hours
    async def get_embedding(self, text: str, model: str = "text-embedding-ada-002") -> list:
        """Cached embedding lookup."""
        # This would normally call the embedding service
        # For now, return a mock embedding
        return [0.1] * 1536  # Mock embedding vector

    @CacheManager.cache(ttl=1800, key_prefix="embedding_metadata")  # 30 minutes
    async def get_embedding_metadata(self, text: str) -> Dict[str, Any]:
        """Cached embedding metadata."""
        return {
            "text_hash": hashlib.sha256(text.encode()).hexdigest(),
            "cached_at": datetime.now().isoformat(),
            "model": "text-embedding-ada-002"
        }


class ChapterCacheManager(CacheManager):
    """Cache manager specifically for chapter content."""

    def __init__(self, cache_backend: str = "memory", redis_url: str = None):
        super().__init__(cache_backend, redis_url)

    @CacheManager.cache(ttl=1800, key_prefix="chapter")  # 30 minutes
    async def get_chapter_content(self, chapter_id: int) -> str:
        """Cached chapter content lookup."""
        # This would normally fetch from database
        # For now, return mock content
        return f"Content for chapter {chapter_id}"

    @CacheManager.cache(ttl=300, key_prefix="chapter_metadata")  # 5 minutes
    async def get_chapter_metadata(self, chapter_id: int) -> Dict[str, Any]:
        """Cached chapter metadata."""
        return {
            "chapter_id": chapter_id,
            "cached_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat()
        }


# Global cache managers
translation_cache = TranslationCacheManager()
embedding_cache = EmbeddingCacheManager()
chapter_cache = ChapterCacheManager()


def setup_caching(redis_url: str = None) -> Dict[str, CacheManager]:
    """
    Setup caching system with multiple cache managers.

    Args:
        redis_url: Redis connection URL (optional)

    Returns:
        Dictionary of cache managers
    """
    cache_config = {
        "translation": TranslationCacheManager(redis_url=redis_url),
        "embedding": EmbeddingCacheManager(redis_url=redis_url),
        "chapter": ChapterCacheManager(redis_url=redis_url),
        "general": CacheManager(redis_url=redis_url)
    }

    return cache_config


def get_cache_stats() -> Dict[str, Any]:
    """Get statistics for all cache managers."""
    return {
        "translation_cache": translation_cache.get_stats(),
        "embedding_cache": embedding_cache.get_stats(),
        "chapter_cache": chapter_cache.get_stats(),
        "general_cache": CacheManager().get_stats()
    }


# Example usage in services
def example_usage():
    """Example of how to use caching in services."""

    # Example with translation service
    async def translate_text_with_cache(text: str, target_lang: str):
        cache_manager = TranslationCacheManager()
        cached_result = await cache_manager.get_translation(text, target_lang)
        return cached_result

    # Example with embedding service
    async def get_embedding_with_cache(text: str):
        cache_manager = EmbeddingCacheManager()
        cached_result = await cache_manager.get_embedding(text)
        return cached_result

    # Example with chapter service
    async def get_chapter_with_cache(chapter_id: int):
        cache_manager = ChapterCacheManager()
        cached_result = await cache_manager.get_chapter_content(chapter_id)
        return cached_result

    return {
        "translate_text_with_cache": translate_text_with_cache,
        "get_embedding_with_cache": get_embedding_with_cache,
        "get_chapter_with_cache": get_chapter_with_cache
    }


__all__ = [
    "CacheManager",
    "TranslationCacheManager",
    "EmbeddingCacheManager",
    "ChapterCacheManager",
    "translation_cache",
    "embedding_cache",
    "chapter_cache",
    "setup_caching",
    "get_cache_stats",
    "example_usage"
]