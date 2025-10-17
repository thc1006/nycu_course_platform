"""
Cache utilities for course platform.

Provides caching decorators and cache management for performance optimization.
"""

import functools
import hashlib
import json
import logging
from typing import Any, Callable, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Simple in-memory cache (for development)
# In production, this would use Redis
_memory_cache: dict[str, tuple[Any, float]] = {}


def generate_cache_key(*args, **kwargs) -> str:
    """
    Generate a cache key from function arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        str: Hash-based cache key
    """
    key_parts = []

    # Add positional args (skip self/cls)
    for arg in args[1:]:  # Skip first arg (self/cls)
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        elif isinstance(arg, (list, tuple)):
            key_parts.append(json.dumps(arg, default=str))
        elif isinstance(arg, dict):
            key_parts.append(json.dumps(arg, default=str, sort_keys=True))

    # Add keyword args
    for k in sorted(kwargs.keys()):
        v = kwargs[k]
        if isinstance(v, (str, int, float, bool)):
            key_parts.append(f"{k}={v}")
        elif isinstance(v, (list, tuple)):
            key_parts.append(f"{k}={json.dumps(v, default=str)}")
        elif isinstance(v, dict):
            key_parts.append(f"{k}={json.dumps(v, default=str, sort_keys=True)}")

    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def cache(ttl_seconds: int = 300):
    """
    Caching decorator for async functions.

    Args:
        ttl_seconds: Time to live in seconds (default: 5 minutes)

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = generate_cache_key(*args, **kwargs)

            # Check cache
            if cache_key in _memory_cache:
                cached_value, expiry_time = _memory_cache[cache_key]
                import time
                if time.time() < expiry_time:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_value
                else:
                    # Remove expired entry
                    del _memory_cache[cache_key]

            # Call function
            result = await func(*args, **kwargs)

            # Store in cache
            import time
            _memory_cache[cache_key] = (result, time.time() + ttl_seconds)
            logger.debug(f"Cached result for {func.__name__} (TTL: {ttl_seconds}s)")

            return result

        return wrapper
    return decorator


def clear_cache():
    """Clear all cached entries."""
    global _memory_cache
    _memory_cache.clear()
    logger.info("Cache cleared")


def clear_cache_pattern(pattern: str):
    """
    Clear cache entries matching a pattern.

    Args:
        pattern: Pattern to match in cache keys
    """
    global _memory_cache
    keys_to_delete = [k for k in _memory_cache.keys() if pattern in k]
    for key in keys_to_delete:
        del _memory_cache[key]
    logger.info(f"Cleared {len(keys_to_delete)} cache entries matching '{pattern}'")
