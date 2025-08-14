"""
VPA EventBus - Performance Optimized Version
Implements lazy loading and caching for improved startup performance
"""

import threading
import logging
from typing import Dict, List, Callable, Any, Optional
from functools import lru_cache

class EventBusOptimized:
    """
    Optimized EventBus with performance enhancements:
    - Lazy initialization of thread locks
    - LRU cache for event handler lookups
    - Reduced memory footprint for subscriptions
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._lock: Optional[threading.RLock] = None
        self._initialized = False
        self.logger = logging.getLogger(__name__)
        
    @property
    def lock(self):
        """Lazy initialization of thread lock"""
        if self._lock is None:
            self._lock = threading.RLock()
        return self._lock
    
    def initialize(self):
        """Lightweight initialization"""
        if not self._initialized:
            self._initialized = True
            self.logger.info("EventBus initialized with performance optimizations")
    
    @lru_cache(maxsize=1000)
    def _get_handlers_cached(self, event_name: str) -> tuple:
        """Cached handler lookup for frequently accessed events"""
        return tuple(self._subscribers.get(event_name, []))
    
    def subscribe(self, event_name: str, handler: Callable):
        """Subscribe to event with optimized storage"""
        with self.lock:
            if event_name not in self._subscribers:
                self._subscribers[event_name] = []
            self._subscribers[event_name].append(handler)
            # Clear cache for this event
            self._get_handlers_cached.cache_clear()
    
    def emit(self, event_name: str, data: Any = None):
        """Emit event with cached handler lookup"""
        handlers = self._get_handlers_cached(event_name)
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                self.logger.error(f"Event handler error: {e}")
