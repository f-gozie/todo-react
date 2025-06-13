from __future__ import annotations

import os
from redis.asyncio import Redis

__all__ = ["redis_client"]

REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

redis_client: Redis = Redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True) 