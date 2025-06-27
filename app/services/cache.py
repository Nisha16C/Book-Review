import redis
import json
import logging
from typing import Optional, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST if hasattr(settings, 'REDIS_HOST') else 'localhost',
                port=settings.REDIS_PORT if hasattr(settings, 'REDIS_PORT') else 6379,
                password=settings.REDIS_PASSWORD if hasattr(settings, 'REDIS_PASSWORD') else None,
                db=settings.REDIS_DB if hasattr(settings, 'REDIS_DB') else 0,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        if not self.redis_client:
            logger.warning("Redis client not available, returning None")
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                logger.info(f"Cache hit for key: {key}")
                return json.loads(value)
            logger.info(f"Cache miss for key: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, expire: int = 300) -> bool:
        if not self.redis_client:
            logger.warning("Redis client not available, skipping cache set")
            return False
        
        try:
            serialized_value = json.dumps(value, default=str)
            self.redis_client.setex(key, expire, serialized_value)
            logger.info(f"Cache set successful for key: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        if not self.redis_client:
            logger.warning("Redis client not available, skipping cache delete")
            return False
        
        try:
            self.redis_client.delete(key)
            logger.info(f"Cache delete successful for key: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def is_available(self) -> bool:
        return self.redis_client is not None

cache_service = CacheService()