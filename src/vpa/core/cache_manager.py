"""
VPA Cache Manager - Performance Enhancement
Implements intelligent caching for frequent operations
"""

import time
import json
import hashlib
from typing import Any, Optional, Dict
from functools import wraps, lru_cache
from pathlib import Path

class VPACacheManager:
    """
    Intelligent cache manager for VPA performance optimization
    
    Features:
    - Configuration caching with change detection
    - Event handler caching
    - Plugin metadata caching
    - LLM response caching
    """
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self._memory_cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, float] = {}
        
    def cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def cached_config_load(self, config_path: str) -> Dict[str, Any]:
        """Cache configuration loading with file change detection"""
        config_file = Path(config_path)
        
        if not config_file.exists():
            return {}
        
        file_mtime = config_file.stat().st_mtime
        cache_key = f"config_{config_path}_{file_mtime}"
        
        if cache_key in self._memory_cache:
            return self._memory_cache[cache_key]
        
        # Load and cache configuration
        with open(config_file, 'r') as f:
            if config_path.endswith('.json'):
                config_data = json.load(f)
            else:  # YAML
                import yaml
                config_data = yaml.safe_load(f)
        
        self._memory_cache[cache_key] = config_data
        self._cache_timestamps[cache_key] = time.time()
        
        return config_data
    
    @lru_cache(maxsize=500)
    def cached_plugin_metadata(self, plugin_path: str) -> Dict[str, Any]:
        """Cache plugin metadata for faster loading"""
        plugin_file = Path(plugin_path)
        
        if not plugin_file.exists():
            return {}
        
        # Extract plugin metadata (simplified)
        metadata = {
            'name': plugin_file.stem,
            'path': str(plugin_file),
            'size': plugin_file.stat().st_size,
            'modified': plugin_file.stat().st_mtime
        }
        
        return metadata
    
    def cache_decorator(self, ttl: int = 300):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = f"{func.__name__}_{self.cache_key(*args, **kwargs)}"
                
                # Check if cached and not expired
                if (cache_key in self._memory_cache and 
                    cache_key in self._cache_timestamps and
                    time.time() - self._cache_timestamps[cache_key] < ttl):
                    return self._memory_cache[cache_key]
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self._memory_cache[cache_key] = result
                self._cache_timestamps[cache_key] = time.time()
                
                return result
            return wrapper
        return decorator
    
    def clear_expired_cache(self, max_age: int = 3600):
        """Clear expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self._cache_timestamps.items()
            if current_time - timestamp > max_age
        ]
        
        for key in expired_keys:
            self._memory_cache.pop(key, None)
            self._cache_timestamps.pop(key, None)
        
        return len(expired_keys)

# Global cache manager instance
cache_manager = VPACacheManager()
