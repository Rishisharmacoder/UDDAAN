"""Redis Hot Cache with automatic in-memory fallback for offline resilience."""
import os
import json
from typing import Optional, Dict, Any, List
from loguru import logger

try:
    import redis
except ImportError:
    redis = None


class RedisCache:
    """Hot cache layer serving sub-millisecond lookups for dashboard & APIs."""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = None
        self._memory_cache: Dict[str, str] = {}

        if redis:
            try:
                self.client = redis.Redis.from_url(self.redis_url, decode_responses=True, socket_timeout=1.5)
                self.client.ping()
                logger.info(f"[REDIS CACHE] Connected successfully to {self.redis_url}")
            except Exception as e:
                logger.warning(f"[REDIS CACHE] Redis unavailable ({e}). Using in-memory fallback.")
                self.client = None

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> None:
        val_str = json.dumps(value) if not isinstance(value, str) else value
        if self.client:
            try:
                self.client.set(key, val_str, ex=ex)
                return
            except Exception as e:
                logger.debug(f"[REDIS CACHE] Set failed, using memory fallback: {e}")

        self._memory_cache[key] = val_str

    def get(self, key: str) -> Optional[Any]:
        val_str = None
        if self.client:
            try:
                val_str = self.client.get(key)
            except Exception:
                val_str = None

        if val_str is None:
            val_str = self._memory_cache.get(key)

        if val_str:
            try:
                return json.loads(val_str)
            except Exception:
                return val_str
        return None

    def set_latest_index(self, frequency: str, data: Dict[str, Any]) -> None:
        self.set(f"apix:index:{frequency}", data, ex=7200)

    def get_latest_index(self, frequency: str) -> Optional[Dict[str, Any]]:
        return self.get(f"apix:index:{frequency}")

    def set_active_datasource(self, source_info: Dict[str, Any]) -> None:
        self.set("apix:datasource:active", source_info, ex=3600)

    def get_active_datasource(self) -> Optional[Dict[str, Any]]:
        return self.get("apix:datasource:active")
