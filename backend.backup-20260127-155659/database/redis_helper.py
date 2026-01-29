"""Redis connection helper for SusBonk bot infrastructure."""
import redis.asyncio as redis
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

class RedisHelper:
    """Redis connection and utility helper."""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.redis_url = os.getenv("REDIS_URL")
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", "6379"))
        self.password = os.getenv("REDIS_PASSWORD") or None
        self.db = int(os.getenv("REDIS_DB", "0"))
    
    async def connect(self) -> redis.Redis:
        """Create Redis connection."""
        if not self.redis:
            if self.redis_url:
                # Use REDIS_URL if provided
                self.redis = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
            else:
                # Fall back to individual parameters
                self.redis = redis.Redis(
                    host=self.host,
                    port=self.port,
                    password=self.password,
                    db=self.db,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
        return self.redis
    
    async def health_check(self) -> bool:
        """Check Redis connection health."""
        try:
            client = await self.connect()
            await client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False
    
    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.aclose()
            self.redis = None

# Global Redis helper instance
redis_helper = RedisHelper()

async def get_redis() -> redis.Redis:
    """Dependency to get Redis connection."""
    return await redis_helper.connect()
