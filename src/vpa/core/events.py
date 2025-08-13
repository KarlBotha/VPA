"""
VPA Core Events System
Event Bus Performance Optimization with async handling and memory-efficient callbacks.
Target: <10ms event dispatch time with performance monitoring.
"""

import asyncio
import time
import psutil
import logging
from typing import Dict, Any, List, Callable, Optional, Union
from functools import wraps
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor


class PerformanceMonitor:
    """Performance monitoring utility with <10ms tracking precision."""
    
    @staticmethod
    def track_execution_time(func_name: str):
        """Decorator for tracking function execution time with <10ms precision."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration_ms = (time.perf_counter() - start_time) * 1000
                    if duration_ms > 10:  # Only log operations >10ms
                        logging.info(f"Performance: {func_name} took {duration_ms:.2f}ms")
            return wrapper
        return decorator
    
    @staticmethod
    def monitor_memory_usage() -> Dict[str, float]:
        """Monitor real-time memory usage."""
        process = psutil.Process()
        return {
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "memory_percent": process.memory_percent(),
            "cpu_percent": process.cpu_percent()
        }


@dataclass
class Event:
    """Event data structure for the VPA event system."""
    name: str
    data: Dict[str, Any]
    timestamp: float
    priority: int = 0
    source: Optional[str] = None


class EventBus:
    """
    High-performance async event bus with memory-efficient callback management.
    Supports event-driven communication patterns with zero direct coupling.
    """
    
    def __init__(self, max_workers: int = 4):
        self.logger = logging.getLogger(__name__)
        self._callbacks: Dict[str, List[Callable]] = {}
        self._async_callbacks: Dict[str, List[Callable]] = {}
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._event_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self._metrics = {
            "events_dispatched": 0,
            "total_dispatch_time": 0.0,
            "average_dispatch_time": 0.0
        }
        
    @PerformanceMonitor.track_execution_time("event_subscription")
    def subscribe(self, event_name: str, callback: Callable, async_callback: bool = False) -> None:
        """Subscribe to an event with memory-efficient callback storage."""
        if async_callback:
            if event_name not in self._async_callbacks:
                self._async_callbacks[event_name] = []
            self._async_callbacks[event_name].append(callback)
        else:
            if event_name not in self._callbacks:
                self._callbacks[event_name] = []
            self._callbacks[event_name].append(callback)
        
        self.logger.debug(f"Subscribed to event: {event_name}")
    
    def unsubscribe(self, event_name: str, callback: Callable) -> None:
        """Unsubscribe from an event to prevent memory leaks."""
        # Remove from sync callbacks
        if event_name in self._callbacks and callback in self._callbacks[event_name]:
            self._callbacks[event_name].remove(callback)
            if not self._callbacks[event_name]:
                del self._callbacks[event_name]
        
        # Remove from async callbacks
        if event_name in self._async_callbacks and callback in self._async_callbacks[event_name]:
            self._async_callbacks[event_name].remove(callback)
            if not self._async_callbacks[event_name]:
                del self._async_callbacks[event_name]
    
    @PerformanceMonitor.track_execution_time("event_dispatch")
    async def dispatch(self, event: Event) -> None:
        """Dispatch event to all subscribers with performance tracking."""
        start_time = time.perf_counter()
        
        try:
            # Dispatch to sync callbacks
            await self._dispatch_sync_callbacks(event)
            
            # Dispatch to async callbacks
            await self._dispatch_async_callbacks(event)
            
            # Update performance metrics
            dispatch_time = time.perf_counter() - start_time
            self._update_metrics(dispatch_time)
            
        except Exception as e:
            self.logger.error(f"Error dispatching event {event.name}: {e}")
            raise
    
    async def _dispatch_sync_callbacks(self, event: Event) -> None:
        """Dispatch event to synchronous callbacks using thread pool."""
        if event.name not in self._callbacks:
            return
        
        # Check if thread pool executor is still available
        if self._executor._shutdown:
            # Fallback to direct execution if executor is shutdown
            for callback in self._callbacks[event.name]:
                try:
                    callback(event)
                except Exception as e:
                    self.logger.error(f"Sync callback error: {e}")
            return
        
        # Execute sync callbacks in thread pool to avoid blocking
        tasks = []
        for callback in self._callbacks[event.name]:
            task = asyncio.get_event_loop().run_in_executor(
                self._executor, callback, event
            )
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _dispatch_async_callbacks(self, event: Event) -> None:
        """Dispatch event to asynchronous callbacks."""
        if event.name not in self._async_callbacks:
            return
        
        tasks = []
        for callback in self._async_callbacks[event.name]:
            if asyncio.iscoroutinefunction(callback):
                tasks.append(callback(event))
            else:
                # Wrap non-async callbacks
                tasks.append(asyncio.create_task(self._wrap_sync_callback(callback, event)))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _wrap_sync_callback(self, callback: Callable, event: Event) -> None:
        """Wrap synchronous callback to run in thread pool."""
        await asyncio.get_event_loop().run_in_executor(
            self._executor, callback, event
        )
    
    def _update_metrics(self, dispatch_time: float) -> None:
        """Update performance metrics."""
        self._metrics["events_dispatched"] += 1
        self._metrics["total_dispatch_time"] += dispatch_time
        self._metrics["average_dispatch_time"] = (
            self._metrics["total_dispatch_time"] / self._metrics["events_dispatched"]
        )
    
    def emit(self, event_name: str, data: Dict[str, Any] = None, 
             priority: int = 0, source: str = None) -> None:
        """Emit an event synchronously."""
        event = Event(
            name=event_name,
            data=data or {},
            timestamp=time.time(),
            priority=priority,
            source=source
        )
        
        # Try to schedule async dispatch if event loop is running
        try:
            asyncio.create_task(self.dispatch(event))
        except RuntimeError:
            # No event loop running - emit without async processing
            self.logger.debug(f"No event loop for async dispatch of {event_name} - using sync callbacks only")
            # Process sync callbacks immediately in current thread
            if event_name in self._callbacks:
                for callback in self._callbacks[event_name]:
                    try:
                        callback(event)
                    except Exception as e:
                        self.logger.error(f"Callback error for {event_name}: {e}")
    
    async def emit_async(self, event_name: str, data: Dict[str, Any] = None,
                        priority: int = 0, source: str = None) -> None:
        """Emit an event asynchronously."""
        event = Event(
            name=event_name,
            data=data or {},
            timestamp=time.time(),
            priority=priority,
            source=source
        )
        
        await self.dispatch(event)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for monitoring."""
        memory_info = PerformanceMonitor.monitor_memory_usage()
        return {
            **self._metrics,
            "memory_usage_mb": memory_info["memory_mb"],
            "memory_percent": memory_info["memory_percent"],
            "callback_count": sum(len(callbacks) for callbacks in self._callbacks.values()),
            "async_callback_count": sum(len(callbacks) for callbacks in self._async_callbacks.values())
        }
    
    def cleanup(self) -> None:
        """Clean up resources to prevent memory leaks."""
        self._callbacks.clear()
        self._async_callbacks.clear()
        self._executor.shutdown(wait=True)
        self.logger.info("EventBus cleanup completed")


# Global event bus instance for application-wide use
event_bus = EventBus()