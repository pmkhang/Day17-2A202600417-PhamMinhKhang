import json
import os
from typing import Any
from src.memory.long_term import LongTermMemory


class RedisLongTermMemory:
    """Long-term profile memory backed by Redis.
    Falls back to JSON-based LongTermMemory if Redis is unavailable.
    """

    def __init__(self, prefix: str = "profile"):
        self.prefix = prefix
        self._redis = None
        self._fallback = LongTermMemory()

        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            try:
                import redis
                self._redis = redis.from_url(redis_url, decode_responses=True)
                self._redis.ping()
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning("Redis unavailable, using JSON fallback: %s", e)
                self._redis = None

    def _key(self, k: str) -> str:
        return f"{self.prefix}:{k}"

    def save(self, key: str, value: Any) -> None:
        if self._redis:
            self._redis.set(self._key(key), json.dumps(value, ensure_ascii=False))
        else:
            self._fallback.save(key, value)

    def retrieve(self, key: str) -> Any:
        if self._redis:
            raw = self._redis.get(self._key(key))
            return json.loads(raw) if raw else None
        return self._fallback.retrieve(key)

    def all(self) -> dict:
        if self._redis:
            keys = self._redis.keys(f"{self.prefix}:*")
            return {
                k.removeprefix(f"{self.prefix}:"): json.loads(self._redis.get(k))  # type: ignore
                for k in keys
            }
        return self._fallback.all()
