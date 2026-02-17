"""
缓存工具
"""

import hashlib
import json
from functools import wraps
from typing import Optional, Any, Callable
from datetime import datetime, timedelta
import time


class CacheStore:
    """简单的内存缓存存储"""
    
    def __init__(self):
        self._cache: dict = {}
        self._timestamps: dict = {}
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key not in self._cache:
            return None
        
        timestamp = self._timestamps.get(key, 0)
        if time.time() - timestamp > 3600:
            del self._cache[key]
            del self._timestamps[key]
            return None
        
        return self._cache[key]
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """设置缓存"""
        self._cache[key] = value
        self._timestamps[key] = time.time()
    
    def delete(self, key: str) -> None:
        """删除缓存"""
        if key in self._cache:
            del self._cache[key]
        if key in self._timestamps:
            del self._timestamps[key]
    
    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        self._timestamps.clear()
    
    def cleanup(self) -> None:
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self._timestamps.items()
            if current_time - timestamp > 3600
        ]
        for key in expired_keys:
            self.delete(key)


cache_store = CacheStore()


def generate_cache_key(*args, **kwargs) -> str:
    """生成缓存键"""
    key_data = {
        "args": args,
        "kwargs": sorted(kwargs.items())
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_str.encode()).hexdigest()


def cached(ttl: int = 3600, key_prefix: str = ""):
    """
    缓存装饰器
    
    Args:
        ttl: 缓存时间（秒），默认1小时
        key_prefix: 缓存键前缀
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}{generate_cache_key(*args, **kwargs)}"
            
            cached_result = cache_store.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = await func(*args, **kwargs)
            cache_store.set(cache_key, result, ttl)
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}{generate_cache_key(*args, **kwargs)}"
            
            cached_result = cache_store.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            result = func(*args, **kwargs)
            cache_store.set(cache_key, result, ttl)
            return result
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def clear_cache(pattern: str = "") -> None:
    """
    清除缓存
    
    Args:
        pattern: 缓存键模式，如果为空则清除所有缓存
    """
    if not pattern:
        cache_store.clear()
    else:
        keys_to_delete = [
            key for key in cache_store._cache.keys()
            if key.startswith(pattern)
        ]
        for key in keys_to_delete:
            cache_store.delete(key)


def get_cache_stats() -> dict:
    """获取缓存统计信息"""
    return {
        "total_keys": len(cache_store._cache),
        "keys": list(cache_store._cache.keys())
    }
