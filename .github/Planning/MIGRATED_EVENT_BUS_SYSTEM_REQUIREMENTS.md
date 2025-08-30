# Event Bus System Requirements

## Overview

This document details the specific requirements for the Event Bus System in the VPA (Virtual Personal Assistant) project. The Event Bus is a central architectural component that enables async event-driven communication between all system components with strict performance targets.

## 1. Core Requirements

### 1.1 Functional Requirements

| Feature | Requirement |
|---------|-------------|
| **Event Publication** | Async-first with both sync and async interfaces |
| **Event Subscription** | Support for both sync and async event handlers |
| **Event Types** | Strongly-typed events with validation |
| **Filtering** | Support for event filtering and pattern matching |
| **Performance** | <10ms event dispatch target for 95% of events |
| **Error Handling** | Isolated error boundaries for event handlers |
| **Monitoring** | Built-in performance monitoring and metrics |
| **Ordering** | Optional strict ordering guarantees when needed |
| **Middleware** | Support for middleware in the event processing pipeline |
| **Event History** | Optional event history tracking for debugging |

### 1.2 Non-Functional Requirements

| Feature | Requirement |
|---------|-------------|
| **Throughput** | At least 1000 events/second on standard hardware |
| **Memory Footprint** | <20MB memory overhead |
| **CPU Usage** | <5% CPU overhead at full event load |
| **Startup Time** | <50ms initialization time |
| **Error Rate** | <0.01% event delivery failure rate |
| **Thread Safety** | Thread-safe implementation for all operations |

## 2. Event Bus Implementation

### 2.1 Core Event Bus Class

```python
import asyncio
import inspect
import time
import uuid
import weakref
from typing import Any, Callable, Dict, List, Optional, Set, TypeVar, Union, Generic, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor

from vpa.core.performance import PerformanceMonitor

# Type definitions
T = TypeVar('T')
EventHandler = Callable[[Dict[str, Any]], None]
AsyncEventHandler = Callable[[Dict[str, Any]], asyncio.coroutine]
EventFilter = Callable[[str, Dict[str, Any]], bool]
EventMiddleware = Callable[[str, Dict[str, Any], Callable], Any]

logger = logging.getLogger(__name__)

class EventBus:
    """Central event bus for async communication between components.
    
    The EventBus provides a pub-sub mechanism for event-driven architecture,
    supporting both synchronous and asynchronous event handlers with error isolation.
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[Tuple[Callable, bool, Optional[EventFilter]]]] = {}
        self._middleware: List[EventMiddleware] = []
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="event_bus_")
        self._history_enabled = False
        self._history: List[Dict[str, Any]] = []
        self._history_limit = 100
        self._performance = PerformanceMonitor("event_bus")
        
    @PerformanceMonitor.track_execution_time("event_bus.emit")
    def emit(self, event_name: str, event_data: Dict[str, Any] = None) -> None:
        """Emit an event synchronously.
        
        Args:
            event_name: Name of the event
            event_data: Data associated with the event
        """
        if event_data is None:
            event_data = {}
            
        # Record event history if enabled
        if self._history_enabled:
            self._add_to_history(event_name, event_data)
            
        # Apply middleware
        processed_event_data = self._apply_middleware(event_name, event_data)
        
        # Get subscribers for this event
        subscribers = self._get_subscribers(event_name)
        
        # Call handlers
        for handler, is_async, event_filter in subscribers:
            # Skip if filter doesn't match
            if event_filter and not event_filter(event_name, processed_event_data):
                continue
                
            try:
                if is_async:
                    # For async handlers, schedule them on the event loop
                    asyncio.create_task(self._call_async_handler(handler, processed_event_data))
                else:
                    # For sync handlers, call them directly
                    handler(processed_event_data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_name}: {e}")
                
    @PerformanceMonitor.track_execution_time("event_bus.emit_async")
    async def emit_async(self, event_name: str, event_data: Dict[str, Any] = None) -> None:
        """Emit an event asynchronously.
        
        Args:
            event_name: Name of the event
            event_data: Data associated with the event
        """
        if event_data is None:
            event_data = {}
            
        # Record event history if enabled
        if self._history_enabled:
            self._add_to_history(event_name, event_data)
            
        # Apply middleware
        processed_event_data = self._apply_middleware(event_name, event_data)
        
        # Get subscribers for this event
        subscribers = self._get_subscribers(event_name)
        
        # Call handlers asynchronously
        handler_tasks = []
        for handler, is_async, event_filter in subscribers:
            # Skip if filter doesn't match
            if event_filter and not event_filter(event_name, processed_event_data):
                continue
                
            if is_async:
                # For async handlers, create a task
                handler_tasks.append(self._call_async_handler(handler, processed_event_data))
            else:
                # For sync handlers, run in thread pool
                handler_tasks.append(self._run_sync_handler_in_executor(handler, processed_event_data))
                
        # Wait for all handlers to complete
        if handler_tasks:
            await asyncio.gather(*handler_tasks, return_exceptions=True)
            
    def subscribe(self, 
                event_name: str, 
                handler: Union[EventHandler, AsyncEventHandler], 
                async_callback: bool = False,
                event_filter: Optional[EventFilter] = None) -> Callable:
        """Subscribe to an event.
        
        Args:
            event_name: Name of the event
            handler: Function to call when the event is emitted
            async_callback: Whether the handler is asynchronous
            event_filter: Optional filter function to determine if handler should be called
            
        Returns:
            Unsubscribe function
        """
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
            
        self._subscribers[event_name].append((handler, async_callback, event_filter))
        
        # Return an unsubscribe function
        def unsubscribe():
            if event_name in self._subscribers:
                self._subscribers[event_name] = [
                    (h, a, f) for h, a, f in self._subscribers[event_name] 
                    if h is not handler
                ]
                if not self._subscribers[event_name]:
                    del self._subscribers[event_name]
                    
        return unsubscribe
        
    def add_middleware(self, middleware: EventMiddleware) -> Callable:
        """Add middleware to the event processing pipeline.
        
        Args:
            middleware: Middleware function
            
        Returns:
            Remove middleware function
        """
        self._middleware.append(middleware)
        
        # Return a remove function
        def remove_middleware():
            if middleware in self._middleware:
                self._middleware.remove(middleware)
                
        return remove_middleware
        
    def enable_history(self, enabled: bool = True, limit: int = 100) -> None:
        """Enable or disable event history.
        
        Args:
            enabled: Whether to enable event history
            limit: Maximum number of events to keep
        """
        self._history_enabled = enabled
        self._history_limit = limit
        
        if not enabled:
            self._history = []
            
    def get_history(self) -> List[Dict[str, Any]]:
        """Get event history.
        
        Returns:
            List of events
        """
        return self._history.copy()
        
    def get_subscriber_count(self, event_name: Optional[str] = None) -> int:
        """Get the number of subscribers for an event.
        
        Args:
            event_name: Name of the event, or None for all events
            
        Returns:
            Number of subscribers
        """
        if event_name is None:
            # Sum all subscribers
            return sum(len(subscribers) for subscribers in self._subscribers.values())
        elif event_name in self._subscribers:
            return len(self._subscribers[event_name])
        else:
            return 0
            
    def clear_all_subscriptions(self) -> None:
        """Clear all subscriptions."""
        self._subscribers = {}
        
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics.
        
        Returns:
            Dictionary of metrics
        """
        return self._performance.get_metrics()
        
    def cleanup(self) -> None:
        """Clean up resources."""
        self._executor.shutdown(wait=False)
        self._subscribers = {}
        self._middleware = []
        self._history = []
        
    def _get_subscribers(self, event_name: str) -> List[Tuple[Callable, bool, Optional[EventFilter]]]:
        """Get subscribers for an event.
        
        Args:
            event_name: Name of the event
            
        Returns:
            List of subscribers
        """
        # Exact matches
        subscribers = self._subscribers.get(event_name, []).copy()
        
        # Wildcard matches (e.g. "namespace.*")
        for pattern, handlers in self._subscribers.items():
            if '*' in pattern:
                # Convert pattern to regex
                regex_pattern = pattern.replace('.', '\\.').replace('*', '.*')
                if re.match(f"^{regex_pattern}$", event_name):
                    subscribers.extend(handlers)
                    
        return subscribers
        
    def _add_to_history(self, event_name: str, event_data: Dict[str, Any]) -> None:
        """Add an event to history.
        
        Args:
            event_name: Name of the event
            event_data: Data associated with the event
        """
        self._history.append({
            "event_name": event_name,
            "event_data": event_data.copy(),
            "timestamp": time.time(),
            "id": str(uuid.uuid4())
        })
        
        # Trim history if needed
        if len(self._history) > self._history_limit:
            self._history = self._history[-self._history_limit:]
            
    def _apply_middleware(self, event_name: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply middleware to event data.
        
        Args:
            event_name: Name of the event
            event_data: Data associated with the event
            
        Returns:
            Processed event data
        """
        processed_data = event_data
        
        for middleware in self._middleware:
            try:
                # Apply middleware
                processed_data = middleware(event_name, processed_data, lambda d: d)
            except Exception as e:
                logger.error(f"Error in event middleware for {event_name}: {e}")
                
        return processed_data
        
    async def _call_async_handler(self, handler: AsyncEventHandler, event_data: Dict[str, Any]) -> None:
        """Call an async handler.
        
        Args:
            handler: Async handler function
            event_data: Event data
        """
        try:
            await handler(event_data)
        except Exception as e:
            logger.error(f"Error in async event handler: {e}")
            
    async def _run_sync_handler_in_executor(self, handler: EventHandler, event_data: Dict[str, Any]) -> None:
        """Run a sync handler in the executor.
        
        Args:
            handler: Sync handler function
            event_data: Event data
        """
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(self._executor, handler, event_data)
        except Exception as e:
            logger.error(f"Error in sync event handler: {e}")
```

### 2.2 TypedEventBus Extension

```python
class TypedEventBus(Generic[T]):
    """Type-safe wrapper for EventBus.
    
    Provides a strongly-typed interface for a specific event type.
    """
    
    def __init__(self, event_bus: EventBus, event_name: str):
        self._event_bus = event_bus
        self._event_name = event_name
        
    def emit(self, event_data: T) -> None:
        """Emit an event synchronously.
        
        Args:
            event_data: Data associated with the event
        """
        self._event_bus.emit(self._event_name, event_data)
        
    async def emit_async(self, event_data: T) -> None:
        """Emit an event asynchronously.
        
        Args:
            event_data: Data associated with the event
        """
        await self._event_bus.emit_async(self._event_name, event_data)
        
    def subscribe(self, 
                handler: Callable[[T], None], 
                async_callback: bool = False,
                event_filter: Optional[Callable[[str, T], bool]] = None) -> Callable:
        """Subscribe to the event.
        
        Args:
            handler: Function to call when the event is emitted
            async_callback: Whether the handler is asynchronous
            event_filter: Optional filter function
            
        Returns:
            Unsubscribe function
        """
        return self._event_bus.subscribe(
            self._event_name,
            handler,
            async_callback,
            event_filter
        )
```

### 2.3 EventBusRegistry

```python
class EventBusRegistry:
    """Registry for named event buses.
    
    Provides a way to get typed event buses for specific events.
    """
    
    def __init__(self, event_bus: EventBus):
        self._event_bus = event_bus
        self._typed_buses: Dict[str, TypedEventBus] = {}
        
    def get_typed_bus(self, event_name: str) -> TypedEventBus:
        """Get a typed event bus for an event.
        
        Args:
            event_name: Name of the event
            
        Returns:
            Typed event bus
        """
        if event_name not in self._typed_buses:
            self._typed_buses[event_name] = TypedEventBus(self._event_bus, event_name)
            
        return self._typed_buses[event_name]
```

### 2.4 EventDecorators

```python
def event_handler(event_name: str, async_handler: bool = False, event_filter: Optional[EventFilter] = None):
    """Decorator to mark a method as an event handler.
    
    Args:
        event_name: Name of the event
        async_handler: Whether the handler is asynchronous
        event_filter: Optional filter function
    """
    def decorator(func):
        # Store event handler metadata on the function
        func._event_handler = {
            "event_name": event_name,
            "async_handler": async_handler,
            "event_filter": event_filter
        }
        return func
        
    return decorator
```

### 2.5 AutoSubscriber Utility

```python
class AutoSubscriber:
    """Utility to automatically subscribe methods marked with @event_handler.
    
    Usage:
    ```
    class MyComponent:
        def __init__(self, event_bus):
            self.event_bus = event_bus
            self._unsubscribers = AutoSubscriber.subscribe_all(self, event_bus)
            
        @event_handler("user_input", async_handler=True)
        async def on_user_input(self, event_data):
            # Handle user input
            pass
            
        def cleanup(self):
            # Unsubscribe all event handlers
            for unsubscribe in self._unsubscribers:
                unsubscribe()
    ```
    """
    
    @staticmethod
    def subscribe_all(instance: Any, event_bus: EventBus) -> List[Callable]:
        """Subscribe all methods marked with @event_handler.
        
        Args:
            instance: Instance to subscribe
            event_bus: Event bus
            
        Returns:
            List of unsubscribe functions
        """
        unsubscribers = []
        
        for name, method in inspect.getmembers(instance, inspect.ismethod):
            if hasattr(method, '_event_handler'):
                metadata = method._event_handler
                
                # Subscribe the method
                unsubscribe = event_bus.subscribe(
                    metadata["event_name"],
                    method,
                    metadata["async_handler"],
                    metadata["event_filter"]
                )
                
                unsubscribers.append(unsubscribe)
                
        return unsubscribers
```

## 3. Standard Events

### 3.1 Core System Events

| Event Name | Description | Data Structure |
|------------|-------------|----------------|
| `system.startup` | Emitted when the system starts up | `{"startup_time": float}` |
| `system.shutdown` | Emitted when the system is shutting down | `{"shutdown_reason": str}` |
| `system.error` | Emitted when a system error occurs | `{"error": str, "context": dict, "severity": str}` |
| `system.status_change` | Emitted when system status changes | `{"new_status": str, "old_status": str}` |

### 3.2 User Interaction Events

| Event Name | Description | Data Structure |
|------------|-------------|----------------|
| `user.input` | Emitted when user input is received | `{"input": str, "input_type": str, "timestamp": float}` |
| `user.input.processed` | Emitted when user input has been processed | `{"input": str, "result": dict, "duration_ms": float}` |
| `user.command` | Emitted when a user command is detected | `{"command": str, "args": list, "raw_input": str}` |
| `user.notification` | Emitted when a notification should be shown to the user | `{"title": str, "message": str, "level": str, "actions": list}` |

### 3.3 Voice System Events

| Event Name | Description | Data Structure |
|------------|-------------|----------------|
| `voice.synthesis.start` | Emitted when voice synthesis starts | `{"text": str, "voice_id": str, "request_id": str}` |
| `voice.synthesis.complete` | Emitted when voice synthesis completes | `{"text": str, "voice_id": str, "duration_ms": float, "audio_data": bytes, "request_id": str}` |
| `voice.synthesis.error` | Emitted when voice synthesis fails | `{"text": str, "voice_id": str, "error": str, "request_id": str}` |
| `voice.recognition.start` | Emitted when voice recognition starts | `{"request_id": str}` |
| `voice.recognition.result` | Emitted when voice recognition completes | `{"text": str, "confidence": float, "duration_ms": float, "request_id": str}` |

### 3.4 Plugin Events

| Event Name | Description | Data Structure |
|------------|-------------|----------------|
| `plugin.loaded` | Emitted when a plugin is loaded | `{"plugin_id": str, "name": str, "version": str}` |
| `plugin.enabled` | Emitted when a plugin is enabled | `{"plugin_id": str, "name": str}` |
| `plugin.disabled` | Emitted when a plugin is disabled | `{"plugin_id": str, "name": str}` |
| `plugin.error` | Emitted when a plugin error occurs | `{"plugin_id": str, "name": str, "error": str}` |
| `plugin.action` | Emitted when a plugin performs an action | `{"plugin_id": str, "name": str, "action": str, "data": dict}` |

### 3.5 LLM Events

| Event Name | Description | Data Structure |
|------------|-------------|----------------|
| `llm.request` | Emitted when an LLM request is made | `{"prompt": str, "system_message": str, "temperature": float, "request_id": str}` |
| `llm.response` | Emitted when an LLM response is received | `{"response": str, "model": str, "tokens": int, "duration_ms": float, "request_id": str}` |
| `llm.error` | Emitted when an LLM request fails | `{"error": str, "request_id": str}` |
| `llm.status_change` | Emitted when LLM status changes | `{"status": str, "model": str}` |

## 4. Event Bus Usage Patterns

### 4.1 Basic Usage

```python
from vpa.core.events import event_bus

# Subscribe to an event
unsubscribe = event_bus.subscribe(
    "user.input",
    lambda event: print(f"User input: {event['input']}"),
    async_callback=False
)

# Emit an event
event_bus.emit("user.input", {"input": "Hello world", "input_type": "text", "timestamp": time.time()})

# Unsubscribe when no longer needed
unsubscribe()
```

### 4.2 Async Usage

```python
from vpa.core.events import event_bus

# Subscribe to an event with async handler
unsubscribe = event_bus.subscribe(
    "user.command",
    process_user_command,
    async_callback=True
)

# Define async handler
async def process_user_command(event):
    command = event["command"]
    args = event["args"]
    
    # Process command asynchronously
    result = await process_command(command, args)
    
    # Emit result
    await event_bus.emit_async("user.command.result", {
        "command": command,
        "result": result
    })
    
# Emit an event asynchronously
await event_bus.emit_async("user.command", {
    "command": "weather",
    "args": ["New York"],
    "raw_input": "what's the weather in New York?"
})
```

### 4.3 Component Integration

```python
from vpa.core.events import event_bus, event_handler, AutoSubscriber

class WeatherPlugin:
    def __init__(self):
        # Auto-subscribe all event handlers in this class
        self._unsubscribers = AutoSubscriber.subscribe_all(self, event_bus)
        
    @event_handler("user.command", async_handler=True)
    async def handle_command(self, event):
        if event["command"] == "weather":
            location = event["args"][0] if event["args"] else "current location"
            
            # Process weather request
            weather_data = await self.get_weather(location)
            
            # Emit response
            await event_bus.emit_async("user.notification", {
                "title": f"Weather for {location}",
                "message": f"Temperature: {weather_data['temperature']}°C, {weather_data['condition']}",
                "level": "info"
            })
            
    async def get_weather(self, location):
        # Implementation of weather API call
        pass
        
    def cleanup(self):
        # Unsubscribe all event handlers when component is destroyed
        for unsubscribe in self._unsubscribers:
            unsubscribe()
```

### 4.4 Performance Monitoring

```python
from vpa.core.events import event_bus

# Add middleware for performance monitoring
def performance_middleware(event_name, event_data, next_func):
    start_time = time.time()
    
    # Process event
    result = next_func(event_data)
    
    # Record performance
    duration_ms = (time.time() - start_time) * 1000
    if duration_ms > 10:  # More than 10ms
        logger.warning(f"Slow event processing: {event_name} took {duration_ms:.2f}ms")
        
    return result
    
# Add middleware to event bus
remove_middleware = event_bus.add_middleware(performance_middleware)

# Get performance metrics
metrics = event_bus.get_performance_metrics()
print(f"Average event processing time: {metrics['avg_time_ms']:.2f}ms")
print(f"Events processed: {metrics['count']}")
```

### 4.5 Error Handling

```python
from vpa.core.events import event_bus

# Add middleware for error handling
def error_handling_middleware(event_name, event_data, next_func):
    try:
        # Process event
        return next_func(event_data)
    except Exception as e:
        # Log error
        logger.error(f"Error processing event {event_name}: {e}")
        
        # Emit error event
        event_bus.emit("system.error", {
            "error": str(e),
            "context": {
                "event_name": event_name,
                "event_data": event_data
            },
            "severity": "error"
        })
        
        # Return original data
        return event_data
    
# Add middleware to event bus
event_bus.add_middleware(error_handling_middleware)
```

## 5. Testing and Verification

### 5.1 Unit Testing

```python
import pytest
from vpa.core.events import EventBus

@pytest.fixture
def event_bus():
    bus = EventBus()
    yield bus
    bus.cleanup()

def test_event_subscription(event_bus):
    received_events = []
    
    # Subscribe to event
    event_bus.subscribe("test.event", lambda e: received_events.append(e))
    
    # Emit event
    event_data = {"data": "value"}
    event_bus.emit("test.event", event_data)
    
    # Check that event was received
    assert len(received_events) == 1
    assert received_events[0]["data"] == "value"
    
@pytest.mark.asyncio
async def test_async_event(event_bus):
    received_events = []
    
    # Subscribe to event with async handler
    async def async_handler(event):
        received_events.append(event)
        
    event_bus.subscribe("test.async", async_handler, async_callback=True)
    
    # Emit event
    event_data = {"data": "async_value"}
    await event_bus.emit_async("test.async", event_data)
    
    # Wait for async handlers to complete
    await asyncio.sleep(0.1)
    
    # Check that event was received
    assert len(received_events) == 1
    assert received_events[0]["data"] == "async_value"
```

### 5.2 Performance Testing

```python
import time
import pytest
from vpa.core.events import EventBus

@pytest.fixture
def event_bus():
    bus = EventBus()
    yield bus
    bus.cleanup()

def test_event_performance(event_bus):
    # Subscribe to event
    event_bus.subscribe("test.performance", lambda e: None)
    
    # Emit events and measure time
    count = 1000
    start_time = time.time()
    
    for i in range(count):
        event_bus.emit("test.performance", {"index": i})
        
    duration = time.time() - start_time
    events_per_second = count / duration
    
    # Check performance
    assert events_per_second >= 1000, f"Event throughput too low: {events_per_second:.2f} events/second"
    
    # Check metrics
    metrics = event_bus.get_performance_metrics()
    assert metrics["count"] >= count
    assert metrics["avg_time_ms"] < 1.0  # Less than 1ms per event
```

## 6. Integration with Core Components

### 6.1 Application Manager Integration

```python
from vpa.core.events import event_bus
from vpa.core.app import AppManager

class AppManager:
    """Application lifecycle management."""
    
    def __init__(self):
        self.state = "initializing"
        
        # Subscribe to system events
        self._unsubscribe_shutdown = event_bus.subscribe(
            "system.shutdown",
            self._handle_shutdown
        )
        
    async def start(self):
        """Start the application."""
        try:
            # Initialize components
            await self._initialize_components()
            
            # Update state
            self.state = "running"
            
            # Emit startup complete
            await event_bus.emit_async("system.startup", {
                "startup_time": time.time()
            })
            
            return True
        except Exception as e:
            logger.error(f"Error starting application: {e}")
            self.state = "error"
            
            # Emit error
            await event_bus.emit_async("system.error", {
                "error": str(e),
                "context": {"component": "AppManager"},
                "severity": "critical"
            })
            
            return False
            
    async def shutdown(self):
        """Shutdown the application."""
        # Update state
        self.state = "shutting_down"
        
        # Emit shutdown event
        await event_bus.emit_async("system.shutdown", {
            "shutdown_reason": "user_request"
        })
        
        # Clean up
        self._unsubscribe_shutdown()
        await self._cleanup_components()
        
        # Update state
        self.state = "shutdown"
        
    def _handle_shutdown(self, event):
        """Handle shutdown event."""
        if self.state == "running":
            # Schedule shutdown
            asyncio.create_task(self.shutdown())
```

### 6.2 Plugin Manager Integration

```python
from vpa.core.events import event_bus
from vpa.core.plugins import PluginManager

class PluginManager:
    """Plugin management system."""
    
    def __init__(self):
        self._plugins = {}
        self._enabled_plugins = set()
        
    async def load_plugins(self):
        """Load all available plugins."""
        # Discover plugins
        plugins = self._discover_plugins()
        
        # Load each plugin
        for plugin_info in plugins:
            await self._load_plugin(plugin_info)
            
    async def _load_plugin(self, plugin_info):
        """Load a single plugin."""
        try:
            # Load plugin module
            plugin = self._instantiate_plugin(plugin_info)
            
            # Store plugin
            plugin_id = plugin_info["id"]
            self._plugins[plugin_id] = plugin
            
            # Emit plugin loaded event
            await event_bus.emit_async("plugin.loaded", {
                "plugin_id": plugin_id,
                "name": plugin_info["name"],
                "version": plugin_info["version"]
            })
            
            # Enable plugin if it should be enabled by default
            if plugin_info.get("enabled_by_default", False):
                await self.enable_plugin(plugin_id)
                
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_info['id']}: {e}")
            
            # Emit plugin error event
            await event_bus.emit_async("plugin.error", {
                "plugin_id": plugin_info["id"],
                "name": plugin_info["name"],
                "error": f"Failed to load: {str(e)}"
            })
            
    async def enable_plugin(self, plugin_id):
        """Enable a plugin."""
        if plugin_id not in self._plugins:
            logger.error(f"Cannot enable plugin {plugin_id}: not loaded")
            return False
            
        if plugin_id in self._enabled_plugins:
            # Already enabled
            return True
            
        try:
            plugin = self._plugins[plugin_id]
            
            # Enable plugin
            await plugin.enable()
            self._enabled_plugins.add(plugin_id)
            
            # Emit plugin enabled event
            await event_bus.emit_async("plugin.enabled", {
                "plugin_id": plugin_id,
                "name": plugin.name
            })
            
            return True
        except Exception as e:
            logger.error(f"Error enabling plugin {plugin_id}: {e}")
            
            # Emit plugin error event
            await event_bus.emit_async("plugin.error", {
                "plugin_id": plugin_id,
                "name": self._plugins[plugin_id].name,
                "error": f"Failed to enable: {str(e)}"
            })
            
            return False
```

### 6.3 LLM Integration

```python
from vpa.core.events import event_bus
from vpa.core.llm import LLMManager

class LLMManager:
    """LLM integration manager."""
    
    def __init__(self):
        self._active_model = None
        self._models = {}
        
        # Subscribe to LLM request events
        self._unsubscribe_llm = event_bus.subscribe(
            "llm.request",
            self._handle_llm_request,
            async_callback=True
        )
        
    async def initialize(self):
        """Initialize LLM integration."""
        # Discover available models
        models = self._discover_models()
        
        # Initialize each model
        for model_id, model_info in models.items():
            try:
                adapter = self._create_adapter(model_info)
                self._models[model_id] = {
                    "info": model_info,
                    "adapter": adapter
                }
            except Exception as e:
                logger.error(f"Error initializing LLM model {model_id}: {e}")
                
        # Set active model
        if self._models:
            default_model = next(iter(self._models.keys()))
            await self.set_active_model(default_model)
            
    async def set_active_model(self, model_id):
        """Set the active LLM model."""
        if model_id not in self._models:
            logger.error(f"Cannot set active model {model_id}: not available")
            return False
            
        # Update active model
        self._active_model = model_id
        
        # Emit status change event
        await event_bus.emit_async("llm.status_change", {
            "status": "active",
            "model": model_id
        })
        
        return True
        
    async def _handle_llm_request(self, event):
        """Handle LLM request event."""
        if not self._active_model:
            await event_bus.emit_async("llm.error", {
                "error": "No active LLM model",
                "request_id": event["request_id"]
            })
            return
            
        try:
            # Get active model
            model_data = self._models[self._active_model]
            adapter = model_data["adapter"]
            
            # Process request
            start_time = time.time()
            response = await adapter.process_prompt(
                event["prompt"],
                event.get("system_message", ""),
                event.get("temperature", 0.7)
            )
            duration_ms = (time.time() - start_time) * 1000
            
            # Emit response event
            await event_bus.emit_async("llm.response", {
                "response": response["text"],
                "model": self._active_model,
                "tokens": response["tokens"],
                "duration_ms": duration_ms,
                "request_id": event["request_id"]
            })
        except Exception as e:
            logger.error(f"Error processing LLM request: {e}")
            
            # Emit error event
            await event_bus.emit_async("llm.error", {
                "error": str(e),
                "request_id": event["request_id"]
            })
```

## 7. Security Considerations

### 7.1 Event Data Security

1. **Sensitive Data**
   - Never include sensitive data (passwords, API keys) in event payloads
   - Use references or tokens instead of actual sensitive values
   - Implement event data filtering middleware for sensitive fields

2. **Event Access Control**
   - Consider implementing permission checking for certain events
   - Use event namespaces to organize and control event access

### 7.2 Error Handling Security

1. **Error Isolation**
   - Ensure errors in one event handler don't affect others
   - Implement proper error boundaries
   - Log errors appropriately without exposing sensitive information

2. **Graceful Degradation**
   - System should continue operating if event handlers fail
   - Implement fallback mechanisms for critical functionality

### 7.3 Resource Protection

1. **Resource Limits**
   - Implement limits on event queue size
   - Throttle event emission if needed
   - Monitor and alert on abnormal event patterns

2. **Memory Management**
   - Implement proper cleanup of event subscriptions
   - Use weak references where appropriate to avoid memory leaks
   - Perform periodic garbage collection

## Conclusion

This document provides detailed requirements and implementation guidance for the Event Bus System in the VPA project. The Event Bus is a central architectural component that enables async event-driven communication between all system components with strict performance targets. Implementation follows the architectural principles defined in the project planning documents and ensures a robust foundation for the event-driven architecture of the VPA system.

---

*Event Bus System Requirements completed on August 27, 2025*
