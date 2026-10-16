import json
import logging
from typing import Any, Optional
import redis
from backend.app.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self._memory_cache = {}
        self._redis_client = None
        try:
            client = redis.from_url(settings.REDIS_URL, socket_timeout=1)
            client.ping()
            self._redis_client = client
            logger.info("Connected to Redis cache at %s", settings.REDIS_URL)
        except Exception:
            logger.info("Redis not available. Using local in-memory caching fallback.")

    def get(self, key: str) -> Optional[Any]:
        if self._redis_client:
            try:
                val = self._redis_client.get(key)
                if val:
                    return json.loads(val.decode("utf-8"))
            except Exception as e:
                logger.warning("Redis get error for %s: %s", key, e)
        return self._memory_cache.get(key)

    def set(self, key: str, value: Any, ttl: int = settings.CACHE_EXPIRATION_SECONDS) -> None:
        if self._redis_client:
            try:
                self._redis_client.setex(key, ttl, json.dumps(value))
                return
            except Exception as e:
                logger.warning("Redis set error for %s: %s", key, e)
        self._memory_cache[key] = value

    def invalidate(self, key_prefix: str) -> None:
        if self._redis_client:
            try:
                keys = self._redis_client.keys(f"{key_prefix}*")
                if keys:
                    self._redis_client.delete(*keys)
            except Exception as e:
                logger.warning("Redis invalidate error: %s", e)
        # Clear matching from memory
        keys_to_del = [k for k in self._memory_cache.keys() if k.startswith(key_prefix)]
        for k in keys_to_del:
            self._memory_cache.pop(k, None)

cache_service = CacheService()
