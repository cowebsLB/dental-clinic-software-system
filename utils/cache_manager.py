"""In-memory query caching."""

import time
import hashlib
import json
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

logger = None  # Will be initialized if logging is needed


class CacheManager:
    """Manages in-memory query cache."""
    
    def __init__(self, default_ttl: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def _make_key(self, query: str, params: Optional[Dict] = None) -> str:
        """Generate cache key from query and parameters."""
        key_data = query
        if params:
            key_data += json.dumps(params, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, query: str, params: Optional[Dict] = None) -> Optional[Any]:
        """Get cached result."""
        key = self._make_key(query, params)
        
        if key in self.cache:
            entry = self.cache[key]
            if entry['expires_at'] > time.time():
                return entry['data']
            else:
                # Expired, remove it
                del self.cache[key]
        
        return None
    
    def set(self, query: str, data: Any, ttl: Optional[int] = None, params: Optional[Dict] = None):
        """Cache a result."""
        key = self._make_key(query, params)
        ttl = ttl or self.default_ttl
        
        self.cache[key] = {
            'data': data,
            'expires_at': time.time() + ttl,
            'created_at': time.time()
        }
    
    def invalidate(self, pattern: Optional[str] = None):
        """Invalidate cache entries."""
        if pattern:
            # Invalidate entries matching pattern
            keys_to_remove = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self.cache[key]
        else:
            # Clear all cache
            self.cache.clear()
    
    def clear_expired(self):
        """Remove expired entries."""
        now = time.time()
        expired_keys = [k for k, v in self.cache.items() if v['expires_at'] <= now]
        for key in expired_keys:
            del self.cache[key]


# Global instance
cache_manager = CacheManager()

