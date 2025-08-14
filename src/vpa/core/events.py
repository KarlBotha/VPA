"""
Event system for VPA.
Provides a simple pub/sub event bus for component communication.
"""

import logging
from typing import Dict, List, Callable, Any, Optional
from collections import defaultdict


class EventBus:
    """Simple event bus for pub/sub messaging."""
    
    def __init__(self):
        """Initialize the event bus."""
        self.logger = logging.getLogger(__name__)
        self._listeners: Dict[str, List[Callable]] = defaultdict(list)
        self._initialized = False
    
    def initialize(self) -> None:
        """Initialize the event bus."""
        if not self._initialized:
            self.logger.info("Event bus initialized")
            self._initialized = True
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Subscribe to an event type."""
        self._listeners[event_type].append(callback)
        self.logger.debug(f"Subscribed to event: {event_type}")
    
    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """Unsubscribe from an event type."""
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(callback)
                self.logger.debug(f"Unsubscribed from event: {event_type}")
            except ValueError:
                self.logger.warning(f"Callback not found for event: {event_type}")
    
    def emit(self, event_type: str, data: Any = None) -> None:
        """Emit an event to all subscribers."""
        if not self._initialized:
            self.logger.warning("Event bus not initialized, ignoring event")
            return
        
        self.logger.debug(f"Emitting event: {event_type}")
        
        for callback in self._listeners.get(event_type, []):
            try:
                if data is not None:
                    callback(data)
                else:
                    callback()
            except Exception as e:
                self.logger.error(f"Error in event callback for {event_type}: {e}")
    
    def clear_listeners(self, event_type: Optional[str] = None) -> None:
        """Clear listeners for a specific event type or all events."""
        if event_type:
            self._listeners[event_type].clear()
            self.logger.debug(f"Cleared listeners for event: {event_type}")
        else:
            self._listeners.clear()
            self.logger.debug("Cleared all event listeners")
    
    def get_listener_count(self, event_type: str) -> int:
        """Get the number of listeners for an event type."""
        return len(self._listeners.get(event_type, []))
