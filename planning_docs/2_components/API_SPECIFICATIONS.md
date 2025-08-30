# API Specifications

## Overview

This document outlines the API specifications for the Virtual Personal Assistant (VPA) system. It details both internal APIs for component communication and external APIs for integration with other systems. The API design follows RESTful principles, uses consistent patterns, and ensures type safety and validation throughout.

## API Design Principles

1. **Consistency**: Uniform patterns for endpoints, request/response formats, and error handling
2. **Versioning**: All APIs are versioned to ensure backward compatibility
3. **Security**: Authentication and authorization are enforced where appropriate
4. **Documentation**: All endpoints are fully documented with OpenAPI specifications
5. **Testability**: APIs are designed to be easily testable with clear inputs and outputs

## Internal API Components

### 1. Event Bus API

The Event Bus provides a central messaging system for communication between components.

#### Event Format

```typescript
interface EventData {
  [key: string]: any;
}

interface Event {
  type: string;
  data: EventData;
  timestamp: number;
  id: string;
}
```

#### Event Bus Methods

```python
# src/vpa/core/events.py
from typing import Any, Callable, Dict, List, Optional, Union, Awaitable
import asyncio
import uuid
import time
import logging

logger = logging.getLogger(__name__)

EventCallback = Callable[[Dict[str, Any]], None]
AsyncEventCallback = Callable[[Dict[str, Any]], Awaitable[None]]

class EventBus:
    """Event bus for application-wide event communication."""
    
    def __init__(self):
        """Initialize the event bus."""
        self._subscribers = {}
        self._async_subscribers = {}
        
    def subscribe(
        self, 
        event_type: str, 
        callback: Union[EventCallback, AsyncEventCallback],
        async_callback: bool = False
    ) -> None:
        """Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event is emitted
            async_callback: Whether the callback is asynchronous
        """
        if async_callback:
            if event_type not in self._async_subscribers:
                self._async_subscribers[event_type] = []
                
            self._async_subscribers[event_type].append(callback)
            logger.debug(f"Subscribed async callback to {event_type}")
        else:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
                
            self._subscribers[event_type].append(callback)
            logger.debug(f"Subscribed callback to {event_type}")
            
    def unsubscribe(
        self, 
        event_type: str, 
        callback: Union[EventCallback, AsyncEventCallback]
    ) -> bool:
        """Unsubscribe from an event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Function to unsubscribe
            
        Returns:
            True if unsubscribed, False if not found
        """
        # Try sync callbacks first
        if event_type in self._subscribers:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
                logger.debug(f"Unsubscribed callback from {event_type}")
                return True
                
        # Try async callbacks
        if event_type in self._async_subscribers:
            if callback in self._async_subscribers[event_type]:
                self._async_subscribers[event_type].remove(callback)
                logger.debug(f"Unsubscribed async callback from {event_type}")
                return True
                
        return False
        
    def emit(self, event_type: str, data: Dict[str, Any] = None) -> str:
        """Emit an event.
        
        Args:
            event_type: Type of event to emit
            data: Event data
            
        Returns:
            Event ID
        """
        data = data or {}
        event_id = str(uuid.uuid4())
        
        # Call synchronous subscribers
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in event callback: {e}")
                    
        # Schedule asynchronous subscribers
        if event_type in self._async_subscribers:
            for callback in self._async_subscribers[event_type]:
                asyncio.create_task(self._call_async_callback(callback, data))
                
        logger.debug(f"Emitted event {event_type} with ID {event_id}")
        return event_id
        
    async def emit_async(self, event_type: str, data: Dict[str, Any] = None) -> str:
        """Emit an event and wait for async subscribers to complete.
        
        Args:
            event_type: Type of event to emit
            data: Event data
            
        Returns:
            Event ID
        """
        data = data or {}
        event_id = str(uuid.uuid4())
        
        # Call synchronous subscribers
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in event callback: {e}")
                    
        # Call asynchronous subscribers and wait for them
        if event_type in self._async_subscribers:
            tasks = []
            
            for callback in self._async_subscribers[event_type]:
                tasks.append(self._call_async_callback(callback, data))
                
            if tasks:
                await asyncio.gather(*tasks)
                
        logger.debug(f"Emitted async event {event_type} with ID {event_id}")
        return event_id
        
    async def _call_async_callback(
        self,
        callback: AsyncEventCallback,
        data: Dict[str, Any]
    ) -> None:
        """Call an async callback with error handling.
        
        Args:
            callback: Async callback to call
            data: Event data
        """
        try:
            await callback(data)
        except Exception as e:
            logger.error(f"Error in async event callback: {e}")

# Global event bus instance
event_bus = EventBus()
```

#### Example Usage

```python
# Subscribe to an event
def on_message_received(data):
    message = data.get("message")
    print(f"Received message: {message}")
    
event_bus.subscribe("message_received", on_message_received)

# Emit an event
event_bus.emit("message_received", {"message": "Hello, world!"})

# Async subscription and emission
async def on_async_event(data):
    await asyncio.sleep(1)
    print(f"Processed async event: {data}")
    
event_bus.subscribe("async_event", on_async_event, async_callback=True)

# Emit and wait for completion
await event_bus.emit_async("async_event", {"value": 42})
```

### 2. Plugin API

The Plugin API enables third-party extensions to integrate with the VPA.

#### Plugin Interface

```python
# src/vpa/core/plugin.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class Plugin(ABC):
    """Base plugin interface."""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin.
        
        Args:
            config: Plugin configuration
            
        Returns:
            True if initialization succeeded
        """
        pass
        
    @abstractmethod
    async def process(self, input_text: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process user input.
        
        Args:
            input_text: User input text
            context: Processing context
            
        Returns:
            Response data or None if not handled
        """
        pass
        
    @abstractmethod
    async def get_capabilities(self) -> List[str]:
        """Get plugin capabilities.
        
        Returns:
            List of capability identifiers
        """
        pass
        
    @abstractmethod
    async def shutdown(self) -> bool:
        """Shut down the plugin.
        
        Returns:
            True if shutdown succeeded
        """
        pass
        
    @property
    @abstractmethod
    def id(self) -> str:
        """Get plugin ID.
        
        Returns:
            Plugin ID
        """
        pass
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Get plugin name.
        
        Returns:
            Plugin name
        """
        pass
        
    @property
    @abstractmethod
    def version(self) -> str:
        """Get plugin version.
        
        Returns:
            Plugin version
        """
        pass
```

#### Plugin Manager API

```python
# src/vpa/core/plugin_manager.py
from typing import Dict, Any, List, Optional
import importlib
import logging
import os
import asyncio
from vpa.core.events import event_bus
from vpa.core.plugin import Plugin

logger = logging.getLogger(__name__)

class PluginManager:
    """Manages plugins for the VPA."""
    
    def __init__(self):
        """Initialize the plugin manager."""
        self._plugins = {}
        self._plugin_configs = {}
        self._initialized = False
        
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin manager.
        
        Args:
            config: Plugin configuration
            
        Returns:
            True if initialization succeeded
        """
        if self._initialized:
            return True
            
        logger.info("Initializing plugin manager")
        
        # Get plugin directory
        plugin_dir = config.get("plugin_dir", "plugins")
        
        # Discover plugins
        await self._discover_plugins(plugin_dir)
        
        # Initialize plugins
        plugin_configs = config.get("plugins", {})
        
        for plugin_id, plugin in self._plugins.items():
            # Get plugin config or empty dict
            plugin_config = plugin_configs.get(plugin_id, {})
            
            # Store config
            self._plugin_configs[plugin_id] = plugin_config
            
            # Initialize plugin
            try:
                success = await plugin.initialize(plugin_config)
                
                if not success:
                    logger.error(f"Failed to initialize plugin: {plugin_id}")
                    del self._plugins[plugin_id]
                    continue
                    
                logger.info(f"Initialized plugin: {plugin.name} v{plugin.version}")
            except Exception as e:
                logger.error(f"Error initializing plugin {plugin_id}: {e}")
                del self._plugins[plugin_id]
                
        self._initialized = True
        logger.info(f"Plugin manager initialized with {len(self._plugins)} plugins")
        
        return True
        
    async def _discover_plugins(self, plugin_dir: str) -> None:
        """Discover plugins in the plugin directory.
        
        Args:
            plugin_dir: Plugin directory path
        """
        if not os.path.exists(plugin_dir):
            logger.warning(f"Plugin directory not found: {plugin_dir}")
            return
            
        # List subdirectories
        for entry in os.listdir(plugin_dir):
            plugin_path = os.path.join(plugin_dir, entry)
            
            # Check if it's a directory and has __init__.py
            if (
                os.path.isdir(plugin_path) and
                os.path.exists(os.path.join(plugin_path, "__init__.py"))
            ):
                try:
                    # Import plugin module
                    module_name = f"{plugin_dir}.{entry}"
                    module = importlib.import_module(module_name)
                    
                    # Look for plugin class
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        
                        # Check if it's a Plugin class (not the abstract base)
                        if (
                            isinstance(attr, type) and
                            issubclass(attr, Plugin) and
                            attr.__module__ == module.__name__
                        ):
                            # Create plugin instance
                            plugin = attr()
                            self._plugins[plugin.id] = plugin
                            logger.info(f"Discovered plugin: {plugin.name} v{plugin.version}")
                            break
                except Exception as e:
                    logger.error(f"Error loading plugin {entry}: {e}")
                    
    async def start(self) -> bool:
        """Start all plugins.
        
        Returns:
            True if all plugins started successfully
        """
        if not self._initialized:
            logger.error("Plugin manager not initialized")
            return False
            
        logger.info("Starting plugins")
        
        # No specific start method in Plugin interface yet
        # This is a placeholder for future expansion
        
        return True
        
    async def stop(self) -> bool:
        """Stop all plugins.
        
        Returns:
            True if all plugins stopped successfully
        """
        if not self._initialized:
            return True
            
        logger.info("Stopping plugins")
        
        # No specific stop method in Plugin interface yet
        # This is a placeholder for future expansion
        
        return True
        
    async def process_input(
        self,
        input_text: str,
        context: Dict[str, Any] = None
    ) -> Optional[Dict[str, Any]]:
        """Process user input through plugins.
        
        Args:
            input_text: User input text
            context: Processing context
            
        Returns:
            Response data or None if not handled
        """
        if not self._initialized:
            logger.error("Plugin manager not initialized")
            return None
            
        context = context or {}
        logger.debug(f"Processing input: {input_text}")
        
        # Try each plugin in order
        for plugin_id, plugin in self._plugins.items():
            try:
                response = await plugin.process(input_text, context)
                
                if response is not None:
                    logger.debug(f"Input handled by plugin: {plugin_id}")
                    
                    # Add plugin info to response
                    response["plugin"] = {
                        "id": plugin_id,
                        "name": plugin.name,
                        "version": plugin.version
                    }
                    
                    return response
            except Exception as e:
                logger.error(f"Error in plugin {plugin_id}: {e}")
                
        logger.debug("No plugin handled the input")
        return None
        
    async def shutdown(self) -> bool:
        """Shut down the plugin manager.
        
        Returns:
            True if shutdown succeeded
        """
        if not self._initialized:
            return True
            
        logger.info("Shutting down plugin manager")
        
        # Shut down each plugin
        for plugin_id, plugin in list(self._plugins.items()):
            try:
                await plugin.shutdown()
                logger.debug(f"Shut down plugin: {plugin_id}")
            except Exception as e:
                logger.error(f"Error shutting down plugin {plugin_id}: {e}")
                
        self._plugins = {}
        self._plugin_configs = {}
        self._initialized = False
        
        logger.info("Plugin manager shutdown complete")
        return True
        
    def get_plugin_ids(self) -> List[str]:
        """Get list of plugin IDs.
        
        Returns:
            List of plugin IDs
        """
        return list(self._plugins.keys())
        
    def get_plugin_info(self) -> List[Dict[str, Any]]:
        """Get information about all plugins.
        
        Returns:
            List of plugin information dictionaries
        """
        return [
            {
                "id": plugin.id,
                "name": plugin.name,
                "version": plugin.version
            }
            for plugin in self._plugins.values()
        ]
```

#### Example Plugin Implementation

```python
# plugins/weather/weather_plugin.py
from vpa.core.plugin import Plugin
from typing import Dict, Any, List, Optional
import aiohttp
import logging

logger = logging.getLogger(__name__)

class WeatherPlugin(Plugin):
    """Weather plugin for VPA."""
    
    def __init__(self):
        """Initialize weather plugin."""
        self._api_key = None
        self._base_url = "https://api.openweathermap.org/data/2.5"
        
    @property
    def id(self) -> str:
        """Get plugin ID."""
        return "weather"
        
    @property
    def name(self) -> str:
        """Get plugin name."""
        return "Weather Plugin"
        
    @property
    def version(self) -> str:
        """Get plugin version."""
        return "1.0.0"
        
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin.
        
        Args:
            config: Plugin configuration
            
        Returns:
            True if initialization succeeded
        """
        self._api_key = config.get("api_key")
        
        if not self._api_key:
            logger.error("Weather plugin requires API key")
            return False
            
        logger.info("Weather plugin initialized")
        return True
        
    async def process(
        self,
        input_text: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Process user input.
        
        Args:
            input_text: User input text
            context: Processing context
            
        Returns:
            Response data or None if not handled
        """
        # Simple keyword matching
        input_lower = input_text.lower()
        
        # Check if this is a weather request
        weather_keywords = ["weather", "forecast", "temperature", "rain", "sunny"]
        if not any(keyword in input_lower for keyword in weather_keywords):
            return None
            
        # Extract location
        location = "New York"  # Default
        
        # Basic location extraction
        location_markers = ["in", "at", "for"]
        for marker in location_markers:
            marker_pos = input_lower.find(f"{marker} ")
            if marker_pos != -1:
                # Get text after marker
                location_part = input_text[marker_pos + len(marker) + 1:]
                
                # Stop at punctuation or end of string
                for i, char in enumerate(location_part):
                    if char in ".,!?;:":
                        location = location_part[:i].strip()
                        break
                else:
                    location = location_part.strip()
                    
                break
                
        try:
            # Get weather data
            weather_data = await self._get_weather(location)
            
            # Format response
            if weather_data:
                temp_celsius = weather_data["main"]["temp"] - 273.15
                condition = weather_data["weather"][0]["description"]
                
                response_text = (
                    f"The weather in {weather_data['name']} is {condition} "
                    f"with a temperature of {temp_celsius:.1f}°C."
                )
                
                return {
                    "text": response_text,
                    "data": weather_data
                }
        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            
        return {
            "text": f"I'm sorry, I couldn't get the weather for {location}."
        }
        
    async def get_capabilities(self) -> List[str]:
        """Get plugin capabilities.
        
        Returns:
            List of capability identifiers
        """
        return ["weather.current", "weather.forecast"]
        
    async def shutdown(self) -> bool:
        """Shut down the plugin.
        
        Returns:
            True if shutdown succeeded
        """
        logger.info("Weather plugin shut down")
        return True
        
    async def _get_weather(self, location: str) -> Optional[Dict[str, Any]]:
        """Get weather data for a location.
        
        Args:
            location: Location name
            
        Returns:
            Weather data or None if not found
        """
        url = f"{self._base_url}/weather"
        params = {
            "q": location,
            "appid": self._api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                    
        return None
```

### 3. Settings API

The Settings API provides access to application configuration.

#### Settings Interface

```python
# src/vpa/core/settings.py
from typing import Dict, Any, Optional, List, Set, TypeVar, Generic, cast
import json
import os
import logging
import asyncio

logger = logging.getLogger(__name__)

T = TypeVar('T')

class SettingsManager:
    """Manages application settings."""
    
    def __init__(self, config_path: str):
        """Initialize settings manager.
        
        Args:
            config_path: Path to configuration file
        """
        self._config_path = config_path
        self._settings = {}
        self._lock = asyncio.Lock()
        
    async def load(self) -> bool:
        """Load settings from file.
        
        Returns:
            True if settings were loaded successfully
        """
        async with self._lock:
            try:
                if not os.path.exists(self._config_path):
                    logger.warning(f"Settings file not found: {self._config_path}")
                    return False
                    
                with open(self._config_path, "r") as f:
                    self._settings = json.load(f)
                    
                logger.debug(f"Loaded settings from {self._config_path}")
                return True
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in settings file: {self._config_path}")
                return False
            except Exception as e:
                logger.error(f"Failed to load settings: {e}")
                return False
                
    async def save(self) -> bool:
        """Save settings to file.
        
        Returns:
            True if settings were saved successfully
        """
        async with self._lock:
            try:
                # Ensure directory exists
                os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
                
                with open(self._config_path, "w") as f:
                    json.dump(self._settings, f, indent=2)
                    
                logger.debug(f"Saved settings to {self._config_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to save settings: {e}")
                return False
                
    def get(self, key: str, default: Optional[T] = None) -> T:
        """Get a setting value.
        
        Args:
            key: Setting key, can use dot notation for nested settings
            default: Default value if setting not found
            
        Returns:
            Setting value or default
        """
        try:
            # Handle nested keys
            keys = key.split(".")
            value = self._settings
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
                    
            return cast(T, value)
        except Exception:
            return default
            
    async def set(self, key: str, value: Any) -> bool:
        """Set a setting value.
        
        Args:
            key: Setting key, can use dot notation for nested settings
            value: Setting value
            
        Returns:
            True if setting was set successfully
        """
        async with self._lock:
            try:
                # Handle nested keys
                keys = key.split(".")
                target = self._settings
                
                # Navigate to the innermost dict
                for k in keys[:-1]:
                    if k not in target:
                        target[k] = {}
                    elif not isinstance(target[k], dict):
                        target[k] = {}
                        
                    target = target[k]
                    
                # Set the value
                target[keys[-1]] = value
                
                return True
            except Exception as e:
                logger.error(f"Failed to set setting {key}: {e}")
                return False
                
    def get_all(self) -> Dict[str, Any]:
        """Get all settings.
        
        Returns:
            Dictionary of all settings
        """
        return dict(self._settings)
        
    def has(self, key: str) -> bool:
        """Check if a setting exists.
        
        Args:
            key: Setting key, can use dot notation for nested settings
            
        Returns:
            True if setting exists
        """
        keys = key.split(".")
        value = self._settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return False
                
        return True
        
    async def delete(self, key: str) -> bool:
        """Delete a setting.
        
        Args:
            key: Setting key, can use dot notation for nested settings
            
        Returns:
            True if setting was deleted
        """
        async with self._lock:
            try:
                # Handle nested keys
                keys = key.split(".")
                target = self._settings
                
                # Navigate to the innermost dict
                for k in keys[:-1]:
                    if k not in target or not isinstance(target[k], dict):
                        return False
                        
                    target = target[k]
                    
                # Delete the value
                if keys[-1] in target:
                    del target[keys[-1]]
                    return True
                    
                return False
            except Exception as e:
                logger.error(f"Failed to delete setting {key}: {e}")
                return False
```

#### Example Usage

```python
# Initialize settings
settings = SettingsManager("./config/settings.json")
await settings.load()

# Get and set values
theme = settings.get("appearance.theme", "light")
await settings.set("appearance.theme", "dark")

# Save settings
await settings.save()

# Check if setting exists
if settings.has("audio.voice_id"):
    voice_id = settings.get("audio.voice_id")
```

### 4. Audio System API

The Audio System API provides access to voice input and output capabilities.

#### Voice Recognition Interface

```python
# src/vpa/audio/voice_recognition.py (partial)
from typing import Dict, Any, Optional, Callable, Awaitable
import asyncio
import logging

logger = logging.getLogger(__name__)

class VoiceRecognitionManager:
    """Manages voice recognition."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize voice recognition.
        
        Args:
            config: Configuration dictionary
        """
        self._config = config or {}
        self._active = False
        self._recognition_task = None
        
    async def initialize(self) -> bool:
        """Initialize voice recognition.
        
        Returns:
            True if initialization succeeded
        """
        logger.info("Initializing voice recognition")
        # Implementation details omitted
        return True
        
    async def start_listening(self) -> bool:
        """Start listening for voice input.
        
        Returns:
            True if listening started successfully
        """
        if self._active:
            return True
            
        self._active = True
        self._recognition_task = asyncio.create_task(self._recognition_loop())
        logger.info("Started listening for voice input")
        return True
        
    async def stop_listening(self) -> bool:
        """Stop listening for voice input.
        
        Returns:
            True if listening stopped successfully
        """
        if not self._active:
            return True
            
        self._active = False
        if self._recognition_task:
            self._recognition_task.cancel()
            try:
                await self._recognition_task
            except asyncio.CancelledError:
                pass
                
        self._recognition_task = None
        logger.info("Stopped listening for voice input")
        return True
        
    async def _recognition_loop(self) -> None:
        """Recognition processing loop."""
        # Implementation details omitted
        pass
        
    async def shutdown(self) -> bool:
        """Shut down voice recognition.
        
        Returns:
            True if shutdown succeeded
        """
        await self.stop_listening()
        logger.info("Voice recognition shut down")
        return True
```

#### Voice Synthesis Interface

```python
# src/vpa/audio/voice_synthesis.py (partial)
from typing import Dict, Any, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

class VoiceSynthesisManager:
    """Manages voice synthesis."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize voice synthesis.
        
        Args:
            config: Configuration dictionary
        """
        self._config = config or {}
        self._voice_id = config.get("voice_id", "default")
        self._rate = config.get("rate", "+0%")
        self._volume = config.get("volume", "+0%")
        
    async def initialize(self) -> bool:
        """Initialize voice synthesis.
        
        Returns:
            True if initialization succeeded
        """
        logger.info("Initializing voice synthesis")
        # Implementation details omitted
        return True
        
    async def speak(
        self,
        text: str,
        voice_id: Optional[str] = None
    ) -> bool:
        """Speak text.
        
        Args:
            text: Text to speak
            voice_id: Voice ID to use (or default if None)
            
        Returns:
            True if text was spoken successfully
        """
        voice = voice_id or self._voice_id
        
        try:
            logger.debug(f"Speaking text with voice {voice}: {text}")
            # Implementation details omitted
            return True
        except Exception as e:
            logger.error(f"Failed to speak text: {e}")
            return False
            
    async def get_available_voices(self) -> Dict[str, Dict[str, Any]]:
        """Get available voices.
        
        Returns:
            Dictionary of voice ID to voice information
        """
        # Implementation details omitted
        return {}
        
    async def shutdown(self) -> bool:
        """Shut down voice synthesis.
        
        Returns:
            True if shutdown succeeded
        """
        logger.info("Voice synthesis shut down")
        return True
```

## External REST API

The VPA provides a REST API for external integration. This API follows RESTful principles and uses JSON for request and response formats.

### Authentication

API requests must include an API key for authentication:

```
Authorization: Bearer <api_key>
```

### API Endpoints

#### 1. System Status

```
GET /api/v1/status
```

Response:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime": 3600,
  "components": {
    "audio": {
      "status": "ok"
    },
    "llm": {
      "status": "ok"
    },
    "plugins": {
      "status": "ok",
      "count": 5
    }
  }
}
```

#### 2. Send Command

```
POST /api/v1/command
```

Request:
```json
{
  "command": "What's the weather today?",
  "context": {
    "source": "api",
    "user_id": "user123"
  }
}
```

Response:
```json
{
  "response": {
    "text": "The weather today is sunny with a high of 75°F.",
    "source": "weather_plugin"
  },
  "status": "success"
}
```

#### 3. Conversation Management

```
POST /api/v1/conversations
```

Request:
```json
{
  "title": "Weather Discussion"
}
```

Response:
```json
{
  "id": "conv123",
  "title": "Weather Discussion",
  "created_at": "2025-08-29T10:00:00Z",
  "messages": []
}
```

```
GET /api/v1/conversations
```

Response:
```json
{
  "conversations": [
    {
      "id": "conv123",
      "title": "Weather Discussion",
      "created_at": "2025-08-29T10:00:00Z",
      "updated_at": "2025-08-29T10:05:00Z",
      "message_count": 2
    }
  ],
  "total": 1
}
```

```
GET /api/v1/conversations/{id}
```

Response:
```json
{
  "id": "conv123",
  "title": "Weather Discussion",
  "created_at": "2025-08-29T10:00:00Z",
  "updated_at": "2025-08-29T10:05:00Z",
  "messages": [
    {
      "id": "msg1",
      "content": "What's the weather today?",
      "sender_type": "user",
      "timestamp": "2025-08-29T10:00:00Z"
    },
    {
      "id": "msg2",
      "content": "The weather today is sunny with a high of 75°F.",
      "sender_type": "assistant",
      "timestamp": "2025-08-29T10:00:05Z"
    }
  ]
}
```

```
POST /api/v1/conversations/{id}/messages
```

Request:
```json
{
  "content": "Will it rain tomorrow?",
  "sender_type": "user"
}
```

Response:
```json
{
  "id": "msg3",
  "content": "Will it rain tomorrow?",
  "sender_type": "user",
  "timestamp": "2025-08-29T10:10:00Z"
}
```

#### 4. Voice Synthesis

```
POST /api/v1/speak
```

Request:
```json
{
  "text": "Hello, world!",
  "voice_id": "en-US-AriaNeural"
}
```

Response:
```json
{
  "status": "success",
  "duration": 1.5
}
```

#### 5. Plugin Management

```
GET /api/v1/plugins
```

Response:
```json
{
  "plugins": [
    {
      "id": "weather",
      "name": "Weather Plugin",
      "version": "1.0.0",
      "enabled": true
    },
    {
      "id": "calendar",
      "name": "Calendar Plugin",
      "version": "1.1.0",
      "enabled": true
    }
  ]
}
```

```
PATCH /api/v1/plugins/{id}
```

Request:
```json
{
  "enabled": false
}
```

Response:
```json
{
  "id": "weather",
  "name": "Weather Plugin",
  "version": "1.0.0",
  "enabled": false
}
```

### REST API Implementation

```python
# src/vpa/api/rest_api.py
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging
import time
import asyncio
from vpa.core.events import event_bus
from vpa.core.plugin_manager import PluginManager

logger = logging.getLogger(__name__)

# API models
class CommandRequest(BaseModel):
    command: str
    context: Optional[Dict[str, Any]] = None

class CommandResponse(BaseModel):
    response: Dict[str, Any]
    status: str

class ConversationCreateRequest(BaseModel):
    title: str

class MessageCreateRequest(BaseModel):
    content: str
    sender_type: str = "user"

class SpeakRequest(BaseModel):
    text: str
    voice_id: Optional[str] = None

class SpeakResponse(BaseModel):
    status: str
    duration: float

class PluginUpdateRequest(BaseModel):
    enabled: bool

# API key security
api_key_header = APIKeyHeader(name="Authorization")

def get_api_key(authorization: str = Header(None)):
    """Validate API key.
    
    Args:
        authorization: Authorization header
        
    Returns:
        API key if valid
        
    Raises:
        HTTPException: If API key is invalid
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
        
    api_key = authorization.replace("Bearer ", "")
    
    # Validate API key (implementation details omitted)
    valid = True
    
    if not valid:
        raise HTTPException(status_code=401, detail="Invalid API key")
        
    return api_key

def create_api_app(plugin_manager: PluginManager):
    """Create FastAPI application.
    
    Args:
        plugin_manager: Plugin manager instance
        
    Returns:
        FastAPI application
    """
    app = FastAPI(
        title="VPA API",
        description="REST API for Virtual Personal Assistant",
        version="1.0.0"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Status endpoint
    @app.get("/api/v1/status")
    async def get_status(api_key: str = Depends(get_api_key)):
        """Get system status."""
        return {
            "status": "ok",
            "version": "1.0.0",
            "uptime": int(time.time() - app.state.start_time),
            "components": {
                "audio": {
                    "status": "ok"
                },
                "llm": {
                    "status": "ok"
                },
                "plugins": {
                    "status": "ok",
                    "count": len(plugin_manager.get_plugin_ids())
                }
            }
        }
        
    # Command endpoint
    @app.post("/api/v1/command", response_model=CommandResponse)
    async def send_command(
        request: CommandRequest,
        api_key: str = Depends(get_api_key)
    ):
        """Send a command to the VPA."""
        context = request.context or {}
        context["source"] = context.get("source", "api")
        
        # Process command through plugins
        response = await plugin_manager.process_input(request.command, context)
        
        if response:
            return {
                "response": response,
                "status": "success"
            }
        else:
            return {
                "response": {
                    "text": "I'm sorry, I couldn't process that command."
                },
                "status": "error"
            }
            
    # Speak endpoint
    @app.post("/api/v1/speak", response_model=SpeakResponse)
    async def speak_text(
        request: SpeakRequest,
        api_key: str = Depends(get_api_key)
    ):
        """Speak text through voice synthesis."""
        start_time = time.time()
        
        # Create a future to wait for completion
        speak_future = asyncio.Future()
        
        # Create a one-time callback
        async def on_speak_complete(event_data):
            if event_data.get("text") == request.text:
                speak_future.set_result(True)
                event_bus.unsubscribe("speak_complete", on_speak_complete)
                
        # Subscribe to speak_complete event
        event_bus.subscribe("speak_complete", on_speak_complete, async_callback=True)
        
        # Emit speak_text event
        event_data = {
            "text": request.text,
            "voice": request.voice_id
        }
        event_bus.emit("speak_text", event_data)
        
        # Wait for completion with timeout
        try:
            await asyncio.wait_for(speak_future, timeout=30.0)
            duration = time.time() - start_time
            
            return {
                "status": "success",
                "duration": duration
            }
        except asyncio.TimeoutError:
            event_bus.unsubscribe("speak_complete", on_speak_complete)
            return {
                "status": "timeout",
                "duration": 30.0
            }
            
    # Plugin endpoints
    @app.get("/api/v1/plugins")
    async def get_plugins(api_key: str = Depends(get_api_key)):
        """Get list of plugins."""
        return {
            "plugins": plugin_manager.get_plugin_info()
        }
        
    @app.patch("/api/v1/plugins/{plugin_id}")
    async def update_plugin(
        plugin_id: str,
        request: PluginUpdateRequest,
        api_key: str = Depends(get_api_key)
    ):
        """Update plugin configuration."""
        # Implementation details omitted
        return {
            "id": plugin_id,
            "enabled": request.enabled
        }
        
    # Store start time for uptime calculation
    app.state.start_time = time.time()
    
    return app
```

## WebSocket API

The VPA provides a WebSocket API for real-time communication with clients.

### WebSocket Endpoints

#### 1. Events

```
/api/v1/ws/events
```

This WebSocket endpoint streams system events to connected clients.

##### Message Format

```json
{
  "type": "event",
  "event_type": "voice_command",
  "data": {
    "text": "What's the weather today?",
    "confidence": 0.95
  },
  "timestamp": 1725106000
}
```

#### 2. Voice Stream

```
/api/v1/ws/voice
```

This WebSocket endpoint allows bidirectional streaming of audio data.

##### Message Format

```json
{
  "type": "audio_data",
  "format": "wav",
  "data": "base64_encoded_audio_data",
  "timestamp": 1725106000
}
```

### WebSocket Implementation

```python
# src/vpa/api/websocket_api.py
from fastapi import FastAPI, WebSocket, Depends, WebSocketDisconnect, Query
from typing import Dict, Any, List, Set
import logging
import json
import asyncio
import base64
from vpa.core.events import event_bus

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        """Initialize WebSocket manager."""
        self.active_connections: Dict[str, Set[WebSocket]] = {
            "events": set(),
            "voice": set()
        }
        
    async def connect(self, channel: str, websocket: WebSocket):
        """Connect a WebSocket to a channel.
        
        Args:
            channel: Channel name
            websocket: WebSocket connection
        """
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
            
        self.active_connections[channel].add(websocket)
        logger.debug(f"Client connected to {channel} channel")
        
    def disconnect(self, channel: str, websocket: WebSocket):
        """Disconnect a WebSocket from a channel.
        
        Args:
            channel: Channel name
            websocket: WebSocket connection
        """
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
            logger.debug(f"Client disconnected from {channel} channel")
            
    async def broadcast(self, channel: str, message: Dict[str, Any]):
        """Broadcast a message to all connections in a channel.
        
        Args:
            channel: Channel name
            message: Message to broadcast
        """
        if channel not in self.active_connections:
            return
            
        disconnected = set()
        
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
                
        # Remove disconnected clients
        for connection in disconnected:
            self.active_connections[channel].discard(connection)

def setup_websocket_api(app: FastAPI):
    """Set up WebSocket API.
    
    Args:
        app: FastAPI application
    """
    # Create WebSocket manager
    manager = WebSocketManager()
    
    # Set up event relay
    async def relay_events():
        """Relay events to WebSocket clients."""
        event_types = [
            "voice_command",
            "speak_text",
            "assistant_response",
            "plugin_action",
            "error"
        ]
        
        # Create a queue for events
        queue = asyncio.Queue()
        
        # Subscribe to events
        for event_type in event_types:
            event_bus.subscribe(
                event_type,
                lambda data, event_type=event_type: queue.put_nowait((event_type, data)),
                async_callback=False
            )
            
        # Process events
        while True:
            try:
                event_type, data = await queue.get()
                
                # Create event message
                message = {
                    "type": "event",
                    "event_type": event_type,
                    "data": data,
                    "timestamp": int(asyncio.get_event_loop().time())
                }
                
                # Broadcast to clients
                await manager.broadcast("events", message)
            except Exception as e:
                logger.error(f"Error relaying event: {e}")
                
    # Start event relay task
    @app.on_event("startup")
    async def start_event_relay():
        asyncio.create_task(relay_events())
        
    # WebSocket endpoints
    @app.websocket("/api/v1/ws/events")
    async def websocket_events(
        websocket: WebSocket,
        token: str = Query(None)
    ):
        """Events WebSocket endpoint."""
        # Validate token (implementation details omitted)
        # if not validate_token(token):
        #     await websocket.close(code=1008, reason="Invalid token")
        #     return
            
        await manager.connect("events", websocket)
        try:
            while True:
                # Keep connection alive
                await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect("events", websocket)
            
    @app.websocket("/api/v1/ws/voice")
    async def websocket_voice(
        websocket: WebSocket,
        token: str = Query(None)
    ):
        """Voice WebSocket endpoint."""
        # Validate token (implementation details omitted)
        # if not validate_token(token):
        #     await websocket.close(code=1008, reason="Invalid token")
        #     return
            
        await manager.connect("voice", websocket)
        try:
            while True:
                # Receive audio data
                data = await websocket.receive_json()
                
                if data["type"] == "audio_data":
                    # Process audio data (implementation details omitted)
                    audio_bytes = base64.b64decode(data["data"])
                    
                    # TODO: Process audio and send to voice recognition
                    
                    # Send response
                    await websocket.send_json({
                        "type": "audio_status",
                        "status": "received",
                        "timestamp": int(asyncio.get_event_loop().time())
                    })
        except WebSocketDisconnect:
            manager.disconnect("voice", websocket)
```

## API Documentation

The VPA API is documented using OpenAPI (Swagger). Documentation is automatically generated and available at:

```
/api/docs
```

API documentation includes:

1. Endpoint descriptions and parameters
2. Request and response schemas
3. Authentication requirements
4. Example requests and responses

## API Testing

API endpoints are tested using automated tests to ensure functionality, performance, and security.

```python
# tests/api/test_rest_api.py
import pytest
from fastapi.testclient import TestClient
from vpa.api.rest_api import create_api_app

class MockPluginManager:
    """Mock plugin manager for testing."""
    
    def get_plugin_ids(self):
        return ["weather", "calendar"]
        
    def get_plugin_info(self):
        return [
            {
                "id": "weather",
                "name": "Weather Plugin",
                "version": "1.0.0",
                "enabled": True
            },
            {
                "id": "calendar",
                "name": "Calendar Plugin",
                "version": "1.1.0",
                "enabled": True
            }
        ]
        
    async def process_input(self, input_text, context=None):
        return {
            "text": f"Processed: {input_text}",
            "source": "mock_plugin"
        }

@pytest.fixture
def api_client():
    """Create test client."""
    app = create_api_app(MockPluginManager())
    return TestClient(app)

def test_get_status(api_client):
    """Test status endpoint."""
    headers = {"Authorization": "Bearer test_key"}
    response = api_client.get("/api/v1/status", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    
def test_send_command(api_client):
    """Test command endpoint."""
    headers = {"Authorization": "Bearer test_key"}
    data = {
        "command": "What's the weather?",
        "context": {
            "user_id": "test_user"
        }
    }
    
    response = api_client.post("/api/v1/command", json=data, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "response" in data
    assert "text" in data["response"]
    
def test_get_plugins(api_client):
    """Test plugins endpoint."""
    headers = {"Authorization": "Bearer test_key"}
    response = api_client.get("/api/v1/plugins", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "plugins" in data
    assert len(data["plugins"]) == 2
    assert data["plugins"][0]["id"] == "weather"
```

## API Client Libraries

To facilitate integration with the VPA, client libraries are provided for common programming languages.

### Python Client

```python
# vpa_client/client.py
import aiohttp
import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class VPAClient:
    """Client for VPA API."""
    
    def __init__(self, base_url: str, api_key: str):
        """Initialize VPA client.
        
        Args:
            base_url: API base URL
            api_key: API key
        """
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    async def get_status(self) -> Dict[str, Any]:
        """Get system status.
        
        Returns:
            Status information
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self._base_url}/api/v1/status"
            async with session.get(url, headers=self._headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    text = await response.text()
                    logger.error(f"Failed to get status: {response.status} - {text}")
                    raise Exception(f"API error: {response.status}")
                    
    async def send_command(
        self,
        command: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Send a command.
        
        Args:
            command: Command text
            context: Command context
            
        Returns:
            Command response
        """
        data = {
            "command": command,
            "context": context or {}
        }
        
        async with aiohttp.ClientSession() as session:
            url = f"{self._base_url}/api/v1/command"
            async with session.post(
                url,
                headers=self._headers,
                json=data
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    text = await response.text()
                    logger.error(f"Failed to send command: {response.status} - {text}")
                    raise Exception(f"API error: {response.status}")
                    
    async def speak_text(
        self,
        text: str,
        voice_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Speak text.
        
        Args:
            text: Text to speak
            voice_id: Voice ID to use
            
        Returns:
            Response information
        """
        data = {
            "text": text
        }
        
        if voice_id:
            data["voice_id"] = voice_id
            
        async with aiohttp.ClientSession() as session:
            url = f"{self._base_url}/api/v1/speak"
            async with session.post(
                url,
                headers=self._headers,
                json=data
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    text = await response.text()
                    logger.error(f"Failed to speak text: {response.status} - {text}")
                    raise Exception(f"API error: {response.status}")
                    
    async def get_plugins(self) -> List[Dict[str, Any]]:
        """Get list of plugins.
        
        Returns:
            List of plugin information
        """
        async with aiohttp.ClientSession() as session:
            url = f"{self._base_url}/api/v1/plugins"
            async with session.get(url, headers=self._headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("plugins", [])
                else:
                    text = await response.text()
                    logger.error(f"Failed to get plugins: {response.status} - {text}")
                    raise Exception(f"API error: {response.status}")
```

### JavaScript Client

```javascript
// vpa-client.js
class VPAClient {
  /**
   * Initialize VPA client.
   * 
   * @param {string} baseUrl - API base URL
   * @param {string} apiKey - API key
   */
  constructor(baseUrl, apiKey) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.apiKey = apiKey;
    this.headers = {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    };
  }
  
  /**
   * Get system status.
   * 
   * @returns {Promise<Object>} Status information
   */
  async getStatus() {
    const url = `${this.baseUrl}/api/v1/status`;
    const response = await fetch(url, {
      method: 'GET',
      headers: this.headers
    });
    
    if (response.ok) {
      return await response.json();
    } else {
      throw new Error(`API error: ${response.status}`);
    }
  }
  
  /**
   * Send a command.
   * 
   * @param {string} command - Command text
   * @param {Object} [context] - Command context
   * @returns {Promise<Object>} Command response
   */
  async sendCommand(command, context = {}) {
    const url = `${this.baseUrl}/api/v1/command`;
    const response = await fetch(url, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({
        command,
        context
      })
    });
    
    if (response.ok) {
      return await response.json();
    } else {
      throw new Error(`API error: ${response.status}`);
    }
  }
  
  /**
   * Speak text.
   * 
   * @param {string} text - Text to speak
   * @param {string} [voiceId] - Voice ID to use
   * @returns {Promise<Object>} Response information
   */
  async speakText(text, voiceId = null) {
    const url = `${this.baseUrl}/api/v1/speak`;
    const data = { text };
    
    if (voiceId) {
      data.voice_id = voiceId;
    }
    
    const response = await fetch(url, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(data)
    });
    
    if (response.ok) {
      return await response.json();
    } else {
      throw new Error(`API error: ${response.status}`);
    }
  }
  
  /**
   * Get list of plugins.
   * 
   * @returns {Promise<Array>} List of plugin information
   */
  async getPlugins() {
    const url = `${this.baseUrl}/api/v1/plugins`;
    const response = await fetch(url, {
      method: 'GET',
      headers: this.headers
    });
    
    if (response.ok) {
      const data = await response.json();
      return data.plugins || [];
    } else {
      throw new Error(`API error: ${response.status}`);
    }
  }
  
  /**
   * Connect to events WebSocket.
   * 
   * @param {Function} onEvent - Event callback
   * @returns {WebSocket} WebSocket connection
   */
  connectToEvents(onEvent) {
    const url = `${this.baseUrl.replace('http', 'ws')}/api/v1/ws/events?token=${this.apiKey}`;
    const ws = new WebSocket(url);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onEvent(data);
    };
    
    return ws;
  }
}
```

## API Security

The VPA API implements multiple security measures:

1. **API Key Authentication**: All API requests must include a valid API key
2. **HTTPS**: All API endpoints must be accessed over HTTPS
3. **Rate Limiting**: API calls are rate-limited to prevent abuse
4. **Input Validation**: All input is validated to prevent injection attacks
5. **CORS Configuration**: Cross-Origin Resource Sharing is properly configured
6. **WebSocket Authentication**: WebSocket connections require token authentication

## Conclusion

This API specification document defines both internal and external APIs for the VPA system. By following these specifications, components can communicate effectively within the system, and external applications can integrate with the VPA functionality. All APIs follow consistent patterns, ensure type safety, and implement proper error handling.

---

*Document created: August 29, 2025*
