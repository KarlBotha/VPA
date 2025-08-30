# Plugin System

## Overview

This document defines the plugin architecture for VPA (Virtual Personal Assistant), enabling developers to extend the application's functionality through custom plugins. The plugin system is designed to be modular, secure, and extensible.

## Table of Contents

1. [Architecture](#1-architecture)
2. [Plugin Interface](#2-plugin-interface)
3. [Plugin Lifecycle](#3-plugin-lifecycle)
4. [Plugin Discovery and Loading](#4-plugin-discovery-and-loading)
5. [Security and Isolation](#5-security-and-isolation)
6. [Inter-Plugin Communication](#6-inter-plugin-communication)
7. [UI Integration](#7-ui-integration)
8. [Development Guidelines](#8-development-guidelines)
9. [Deployment and Distribution](#9-deployment-and-distribution)

## 1. Architecture

### 1.1 Core Principles

The VPA plugin system is built on the following principles:

1. **Modularity**: Plugins are self-contained with well-defined boundaries
2. **Isolation**: Plugins run in controlled environments to prevent system-wide issues
3. **Event-Driven**: Plugins communicate via the event bus without direct coupling
4. **Versioning**: Clear API versioning for backward compatibility
5. **Performance**: Minimal impact on application startup and runtime performance

### 1.2 Component Overview

```
┌──────────────────────────────────────────────┐
│                  VPA Core                    │
│                                              │
│  ┌─────────────┐    ┌─────────────────────┐  │
│  │ Event Bus   │◄──►│ Plugin Manager      │  │
│  └─────────────┘    └─────────────────────┘  │
│                             │                │
│  ┌─────────────┐            │                │
│  │ Core API    │◄───────────┘                │
│  └─────────────┘                             │
└──────────────────────────────────────────────┘
                    │
     ┌──────────────┼──────────────┐
     │              │              │
┌────▼─────┐   ┌────▼─────┐   ┌────▼─────┐
│ Plugin A  │   │ Plugin B  │   │ Plugin C  │
└──────────┘   └──────────┘   └──────────┘
```

### 1.3 Directory Structure

```
vpa/
├── core/
│   ├── plugins/
│   │   ├── __init__.py
│   │   ├── plugin_manager.py
│   │   ├── plugin_base.py
│   │   └── plugin_registry.py
│   └── ...
├── plugins/
│   ├── core_plugins/          # Built-in plugins
│   │   ├── assistant/
│   │   │   ├── __init__.py
│   │   │   ├── plugin.json
│   │   │   └── assistant_plugin.py
│   │   └── ...
│   └── addons/                # Third-party plugins
│       ├── weather/
│       │   ├── __init__.py
│       │   ├── plugin.json
│       │   └── weather_plugin.py
│       └── ...
└── ...
```

## 2. Plugin Interface

### 2.1 Base Plugin Class

All plugins inherit from the `Plugin` base class:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class Plugin(ABC):
    """Base class for all VPA plugins"""
    
    def __init__(self):
        self._metadata = None
        self._event_bus = None
        self._logger = None
        
    def initialize(self, event_bus, logger, settings):
        """Initialize the plugin with required dependencies"""
        self._event_bus = event_bus
        self._logger = logger
        self._settings = settings
        
        # Load metadata if not already loaded
        if not self._metadata:
            self._metadata = self.get_metadata()
            
        return self.on_initialize()
        
    def on_initialize(self) -> bool:
        """Called when the plugin is initialized"""
        return True
        
    def shutdown(self):
        """Perform cleanup when plugin is being shut down"""
        self.on_shutdown()
        
    def on_shutdown(self):
        """Called when the plugin is being shut down"""
        pass
        
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the plugin"""
        pass
        
    def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author
        }
        
    @property
    def version(self) -> str:
        """The version of the plugin"""
        return "1.0.0"
        
    @property
    def description(self) -> str:
        """The description of the plugin"""
        return ""
        
    @property
    def author(self) -> str:
        """The author of the plugin"""
        return "Unknown"
        
    def can_handle(self, user_input: str, context: Dict[str, Any]) -> bool:
        """Determine if this plugin can handle the user input"""
        return False
        
    async def process(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process user input and return a response"""
        return {"response": ""}
        
    async def get_ui_components(self) -> Dict[str, Any]:
        """Return any UI components provided by this plugin"""
        return {}
        
    def get_settings_schema(self) -> Dict[str, Any]:
        """Get the settings schema for this plugin"""
        return {}
        
    def get_permissions(self) -> List[str]:
        """Get the permissions required by this plugin"""
        return []
        
    def validate_settings(self, settings: Dict[str, Any]) -> Dict[str, str]:
        """Validate plugin settings, return dict of error messages or empty dict if valid"""
        return {}
```

### 2.2 Plugin Manifest

Each plugin must include a `plugin.json` manifest file:

```json
{
    "id": "weather",
    "name": "Weather Forecast",
    "version": "1.0.0",
    "description": "Provides weather forecasts and alerts",
    "author": "VPA Team",
    "author_email": "team@vpa-example.com",
    "website": "https://vpa-example.com/plugins/weather",
    "license": "MIT",
    "main_class": "WeatherPlugin",
    "main_file": "weather_plugin.py",
    "api_version": "1.0",
    "requirements": ["requests>=2.25.0", "pytz>=2021.1"],
    "dependencies": ["location_services"],
    "permissions": ["network", "location"],
    "settings": {
        "api_key": {
            "type": "string",
            "description": "API key for weather service",
            "required": true
        },
        "units": {
            "type": "string",
            "description": "Temperature units",
            "enum": ["celsius", "fahrenheit"],
            "default": "celsius"
        }
    },
    "priority": 50,
    "triggers": ["weather", "forecast", "temperature"],
    "supported_platforms": ["windows"],
    "minimum_app_version": "1.0.0",
    "tags": ["weather", "forecast", "utility"],
    "icon": "weather_icon.png"
}
```

### 2.3 Plugin Example

```python
from vpa.core.plugins import Plugin

class WeatherPlugin(Plugin):
    """Weather forecast plugin"""
    
    @property
    def name(self) -> str:
        return "weather"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def description(self) -> str:
        return "Provides weather forecasts and alerts"
        
    @property
    def author(self) -> str:
        return "VPA Team"
        
    def on_initialize(self) -> bool:
        """Initialize the weather plugin"""
        # Subscribe to events
        self._event_bus.subscribe("query.weather", self._handle_weather_query, async_callback=True)
        
        # Initialize weather service
        self._weather_service = WeatherService(self._settings.get("weather.api_key"))
        
        return True
        
    def on_shutdown(self):
        """Clean up resources"""
        # Unsubscribe from events
        self._event_bus.unsubscribe("query.weather", self._handle_weather_query)
        
    def can_handle(self, user_input: str, context: Dict[str, Any]) -> bool:
        """Check if this plugin can handle the user input"""
        # Simple keyword matching
        weather_keywords = ["weather", "temperature", "forecast", "rain", "sunny"]
        return any(keyword in user_input.lower() for keyword in weather_keywords)
        
    async def process(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process weather-related query"""
        location = context.get("location", "current")
        
        try:
            # Get weather data from service
            weather_data = await self._weather_service.get_forecast(location)
            
            # Format response
            response = self._format_weather_response(weather_data)
            
            return {
                "response": response,
                "weather_data": weather_data,
                "display_type": "weather_card"
            }
        except Exception as e:
            self._logger.error(f"Error getting weather data: {e}")
            return {
                "response": "I'm sorry, I couldn't retrieve the weather information.",
                "error": str(e)
            }
            
    async def get_ui_components(self) -> Dict[str, Any]:
        """Return UI components for this plugin"""
        from ui.components import WeatherCard, WeatherSettingsPanel
        
        return {
            "weather_card": WeatherCard(),
            "settings_panel": WeatherSettingsPanel(self._settings)
        }
        
    def get_settings_schema(self) -> Dict[str, Any]:
        """Return settings schema for this plugin"""
        return {
            "api_key": {
                "type": "string",
                "label": "API Key",
                "description": "API key for the weather service",
                "required": True
            },
            "units": {
                "type": "string",
                "label": "Temperature Units",
                "description": "Units to display temperature in",
                "options": [
                    {"label": "Celsius (°C)", "value": "celsius"},
                    {"label": "Fahrenheit (°F)", "value": "fahrenheit"}
                ],
                "default": "celsius"
            },
            "update_frequency": {
                "type": "integer",
                "label": "Update Frequency",
                "description": "How often to update weather data (in minutes)",
                "min": 15,
                "max": 120,
                "default": 30
            }
        }
        
    async def _handle_weather_query(self, event_data: Dict[str, Any]):
        """Handle weather query events"""
        query = event_data.get("query", "")
        location = event_data.get("location", "current")
        
        try:
            weather_data = await self._weather_service.get_forecast(location)
            
            await self._event_bus.emit_async("weather.forecast.result", {
                "location": location,
                "data": weather_data,
                "query_id": event_data.get("query_id")
            })
        except Exception as e:
            self._logger.error(f"Error handling weather query: {e}")
            
            await self._event_bus.emit_async("weather.forecast.error", {
                "location": location,
                "error": str(e),
                "query_id": event_data.get("query_id")
            })
            
    def _format_weather_response(self, weather_data: Dict[str, Any]) -> str:
        """Format weather data into a user-friendly response"""
        location = weather_data.get("location", "")
        current = weather_data.get("current", {})
        forecast = weather_data.get("forecast", [])
        
        temp_unit = "°C" if self._settings.get("weather.units") == "celsius" else "°F"
        
        current_temp = current.get("temperature", "unknown")
        current_condition = current.get("condition", "")
        
        response = f"Currently in {location}, it's {current_temp}{temp_unit} and {current_condition}. "
        
        if forecast:
            tomorrow = forecast[0]
            response += f"Tomorrow will be {tomorrow.get('condition', '')} with a high of {tomorrow.get('high', '')}{temp_unit}."
            
        return response
```

## 3. Plugin Lifecycle

### 3.1 Lifecycle Phases

Plugins go through the following lifecycle phases:

1. **Discovery**: Plugin is found in the plugin directory
2. **Validation**: Plugin manifest and structure are validated
3. **Loading**: Plugin code is loaded into memory
4. **Initialization**: Plugin is initialized with dependencies
5. **Activation**: Plugin becomes active and responds to events
6. **Deactivation**: Plugin is temporarily deactivated
7. **Shutdown**: Plugin resources are released

### 3.2 Plugin States

```
┌─────────────┐      ┌─────────────┐      ┌────────────┐
│ DISCOVERED  │─────►│ INITIALIZED │─────►│ ACTIVATED  │
└─────────────┘      └─────────────┘      └────────────┘
       │                    ▲                    │
       │                    │                    │
       │                    │                    ▼
       │              ┌──────────────┐     ┌────────────┐
       └─────────────►│ DEACTIVATED  │◄────┤ ERROR      │
                      └──────────────┘     └────────────┘
                             │
                             ▼
                      ┌──────────────┐
                      │ SHUTDOWN     │
                      └──────────────┘
```

### 3.3 Error Handling

The plugin system implements graceful error handling:

```python
class PluginError(Exception):
    """Base class for plugin-related errors"""
    
    def __init__(self, plugin_id, message):
        self.plugin_id = plugin_id
        self.message = message
        super().__init__(f"Plugin '{plugin_id}': {message}")

class PluginInitializationError(PluginError):
    """Error during plugin initialization"""
    pass

class PluginValidationError(PluginError):
    """Error during plugin validation"""
    pass

class PluginDependencyError(PluginError):
    """Error with plugin dependencies"""
    pass

class PluginRuntimeError(PluginError):
    """Error during plugin execution"""
    pass
```

## 4. Plugin Discovery and Loading

### 4.1 Plugin Manager

The `PluginManager` handles plugin discovery, loading, and lifecycle management:

```python
class PluginManager:
    """Manages the lifecycle of plugins"""
    
    def __init__(self, event_bus, logger, settings_manager):
        self.event_bus = event_bus
        self.logger = logger
        self.settings_manager = settings_manager
        
        # Plugin storage
        self.plugins = {}  # id -> Plugin instance
        self.plugin_states = {}  # id -> state
        self.plugin_metadata = {}  # id -> metadata
        
        # Plugin directories
        self.plugin_dirs = [
            os.path.join(get_app_dir(), "plugins", "core_plugins"),
            os.path.join(get_app_dir(), "plugins", "addons")
        ]
        
        # Plugin cache
        self.cache_path = os.path.join(get_app_dir(), "cache", "plugin_cache.json")
        self.plugin_cache = self._load_plugin_cache()
        
    async def discover_plugins(self):
        """Discover available plugins"""
        discovered_plugins = {}
        
        # Track changes to detect if cache needs updating
        cache_changed = False
        
        for plugin_dir in self.plugin_dirs:
            if not os.path.exists(plugin_dir):
                continue
                
            # Scan for plugin directories
            for item in os.listdir(plugin_dir):
                item_path = os.path.join(plugin_dir, item)
                
                # Skip non-directories
                if not os.path.isdir(item_path):
                    continue
                    
                # Check for plugin.json
                manifest_path = os.path.join(item_path, "plugin.json")
                if not os.path.exists(manifest_path):
                    continue
                    
                try:
                    # Load and validate manifest
                    with open(manifest_path, "r") as f:
                        manifest = json.load(f)
                        
                    plugin_id = manifest.get("id")
                    if not plugin_id:
                        self.logger.warning(f"Skipping plugin in {item_path}: missing id in manifest")
                        continue
                        
                    # Check if plugin metadata has changed
                    plugin_hash = self._calculate_plugin_hash(manifest_path)
                    cached_hash = self.plugin_cache.get(plugin_id, {}).get("hash")
                    
                    if plugin_hash != cached_hash:
                        # Plugin is new or changed, validate fully
                        validation_result = self._validate_plugin_manifest(manifest, item_path)
                        
                        if not validation_result["valid"]:
                            self.logger.warning(f"Skipping plugin {plugin_id}: {validation_result['error']}")
                            continue
                            
                        # Update cache
                        self.plugin_cache[plugin_id] = {
                            "hash": plugin_hash,
                            "path": item_path,
                            "manifest": manifest,
                            "last_validated": time.time()
                        }
                        cache_changed = True
                    else:
                        # Use cached metadata
                        manifest = self.plugin_cache[plugin_id]["manifest"]
                    
                    # Store metadata
                    self.plugin_metadata[plugin_id] = manifest
                    discovered_plugins[plugin_id] = {
                        "path": item_path,
                        "manifest": manifest
                    }
                except Exception as e:
                    self.logger.error(f"Error discovering plugin in {item_path}: {e}")
        
        # Save updated cache if needed
        if cache_changed:
            self._save_plugin_cache()
            
        return discovered_plugins
        
    async def load_plugins(self):
        """Load and initialize discovered plugins"""
        # Discover plugins
        discovered_plugins = await self.discover_plugins()
        
        # Sort plugins by priority
        sorted_plugins = sorted(
            discovered_plugins.items(),
            key=lambda x: x[1]["manifest"].get("priority", 0),
            reverse=True
        )
        
        # Track loaded plugins
        loaded_plugins = {}
        
        # Resolve dependencies
        dependency_graph = {}
        for plugin_id, plugin_info in discovered_plugins.items():
            dependencies = plugin_info["manifest"].get("dependencies", [])
            dependency_graph[plugin_id] = dependencies
        
        # Check for circular dependencies
        try:
            load_order = self._resolve_dependencies(dependency_graph)
        except ValueError as e:
            self.logger.error(f"Circular dependency detected: {e}")
            # Load plugins without respecting dependencies
            load_order = list(discovered_plugins.keys())
            
        # Load plugins in dependency order
        for plugin_id in load_order:
            plugin_info = discovered_plugins.get(plugin_id)
            if not plugin_info:
                continue
                
            try:
                # Load plugin
                plugin_instance = await self._load_plugin(plugin_id, plugin_info)
                
                if plugin_instance:
                    loaded_plugins[plugin_id] = plugin_instance
                    self.plugin_states[plugin_id] = "INITIALIZED"
                    
                    # Emit plugin loaded event
                    self.event_bus.emit("plugin.loaded", {
                        "plugin_id": plugin_id,
                        "plugin_name": plugin_instance.name
                    })
            except Exception as e:
                self.logger.error(f"Failed to load plugin {plugin_id}: {e}")
                self.plugin_states[plugin_id] = "ERROR"
                
                # Emit plugin error event
                self.event_bus.emit("plugin.error", {
                    "plugin_id": plugin_id,
                    "error": str(e),
                    "phase": "loading"
                })
        
        # Store loaded plugins
        self.plugins.update(loaded_plugins)
        
        # Return loaded plugins
        return loaded_plugins
        
    async def activate_plugins(self):
        """Activate all initialized plugins"""
        activated_count = 0
        
        for plugin_id, plugin in self.plugins.items():
            # Skip plugins that aren't in INITIALIZED state
            if self.plugin_states.get(plugin_id) != "INITIALIZED":
                continue
                
            try:
                # Check if plugin is enabled in settings
                plugin_enabled = self.settings_manager.get(f"plugins.{plugin_id}.enabled", True)
                
                if not plugin_enabled:
                    self.plugin_states[plugin_id] = "DEACTIVATED"
                    self.logger.info(f"Plugin {plugin_id} is disabled in settings, skipping activation")
                    continue
                    
                # Set state to ACTIVATED
                self.plugin_states[plugin_id] = "ACTIVATED"
                activated_count += 1
                
                # Emit plugin activated event
                self.event_bus.emit("plugin.activated", {
                    "plugin_id": plugin_id,
                    "plugin_name": plugin.name
                })
            except Exception as e:
                self.logger.error(f"Failed to activate plugin {plugin_id}: {e}")
                self.plugin_states[plugin_id] = "ERROR"
                
                # Emit plugin error event
                self.event_bus.emit("plugin.error", {
                    "plugin_id": plugin_id,
                    "error": str(e),
                    "phase": "activation"
                })
                
        return activated_count
        
    async def shutdown_plugins(self):
        """Shutdown all plugins"""
        for plugin_id, plugin in list(self.plugins.items()):
            try:
                # Call plugin shutdown
                plugin.shutdown()
                
                # Update state
                self.plugin_states[plugin_id] = "SHUTDOWN"
                
                # Emit plugin shutdown event
                self.event_bus.emit("plugin.shutdown", {
                    "plugin_id": plugin_id
                })
            except Exception as e:
                self.logger.error(f"Error shutting down plugin {plugin_id}: {e}")
                
                # Emit plugin error event
                self.event_bus.emit("plugin.error", {
                    "plugin_id": plugin_id,
                    "error": str(e),
                    "phase": "shutdown"
                })
                
        # Clear plugin references
        self.plugins.clear()
        
    async def _load_plugin(self, plugin_id, plugin_info):
        """Load a single plugin"""
        path = plugin_info["path"]
        manifest = plugin_info["manifest"]
        
        # Get main class and file info
        main_class = manifest.get("main_class")
        main_file = manifest.get("main_file", "__init__.py")
        
        if not main_class:
            raise PluginValidationError(plugin_id, "Missing main_class in manifest")
            
        # Import plugin module
        module_path = os.path.join(path, main_file)
        module_name = f"vpa_plugin_{plugin_id}"
        
        try:
            # Create plugin-specific settings
            plugin_settings = PluginSettings(plugin_id, self.settings_manager)
            
            # Create plugin-specific logger
            plugin_logger = self.logger.get_child(f"plugin.{plugin_id}")
            
            # Import the plugin module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get plugin class
            if not hasattr(module, main_class):
                raise PluginValidationError(
                    plugin_id,
                    f"Main class {main_class} not found in {main_file}"
                )
                
            plugin_class = getattr(module, main_class)
            
            # Create plugin instance
            plugin_instance = plugin_class()
            
            # Initialize plugin
            init_success = plugin_instance.initialize(
                self.event_bus,
                plugin_logger,
                plugin_settings
            )
            
            if not init_success:
                raise PluginInitializationError(
                    plugin_id,
                    "Plugin initialization returned False"
                )
                
            return plugin_instance
        except Exception as e:
            self.logger.error(f"Error loading plugin {plugin_id}: {e}")
            raise
            
    def _validate_plugin_manifest(self, manifest, plugin_path):
        """Validate a plugin manifest"""
        required_fields = ["id", "name", "version", "main_class"]
        
        # Check required fields
        for field in required_fields:
            if field not in manifest:
                return {"valid": False, "error": f"Missing required field: {field}"}
                
        # Check plugin ID format
        plugin_id = manifest["id"]
        if not re.match(r'^[a-z0-9_]+$', plugin_id):
            return {
                "valid": False,
                "error": "Invalid plugin ID. Use only lowercase letters, numbers, and underscores."
            }
            
        # Check main file exists
        main_file = manifest.get("main_file", "__init__.py")
        main_file_path = os.path.join(plugin_path, main_file)
        
        if not os.path.exists(main_file_path):
            return {"valid": False, "error": f"Main file not found: {main_file}"}
            
        # Check API version compatibility
        api_version = manifest.get("api_version", "1.0")
        supported_versions = ["1.0"]  # List of supported API versions
        
        if api_version not in supported_versions:
            return {
                "valid": False,
                "error": f"Unsupported API version: {api_version}. Supported versions: {supported_versions}"
            }
            
        # Check app version compatibility
        min_app_version = manifest.get("minimum_app_version")
        if min_app_version:
            app_version = self.settings_manager.get("app.version", "1.0.0")
            
            if version.parse(app_version) < version.parse(min_app_version):
                return {
                    "valid": False,
                    "error": f"Plugin requires app version {min_app_version} or higher"
                }
                
        return {"valid": True}
        
    def _calculate_plugin_hash(self, manifest_path):
        """Calculate a hash of the plugin files for cache validation"""
        import hashlib
        
        hasher = hashlib.sha256()
        
        # Add manifest content to hash
        with open(manifest_path, "rb") as f:
            hasher.update(f.read())
            
        # Add main file content to hash
        plugin_dir = os.path.dirname(manifest_path)
        
        try:
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
                
            main_file = manifest.get("main_file", "__init__.py")
            main_file_path = os.path.join(plugin_dir, main_file)
            
            if os.path.exists(main_file_path):
                with open(main_file_path, "rb") as f:
                    hasher.update(f.read())
        except:
            pass
            
        return hasher.hexdigest()
        
    def _load_plugin_cache(self):
        """Load plugin cache from disk"""
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, "r") as f:
                    return json.load(f)
            except:
                pass
                
        return {}
        
    def _save_plugin_cache(self):
        """Save plugin cache to disk"""
        try:
            # Create cache directory if it doesn't exist
            os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
            
            # Save cache
            with open(self.cache_path, "w") as f:
                json.dump(self.plugin_cache, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving plugin cache: {e}")
            
    def _resolve_dependencies(self, dependency_graph):
        """Resolve plugin dependencies and return loading order"""
        # Detect circular dependencies
        visited = set()
        temp_visited = set()
        
        def check_circular(node):
            if node in temp_visited:
                raise ValueError(f"Circular dependency detected involving plugin {node}")
                
            if node in visited:
                return
                
            temp_visited.add(node)
            
            for dependency in dependency_graph.get(node, []):
                if dependency in dependency_graph:
                    check_circular(dependency)
                    
            temp_visited.remove(node)
            visited.add(node)
            
        # Check for circular dependencies
        for node in dependency_graph:
            if node not in visited:
                check_circular(node)
                
        # Perform topological sort
        result = []
        visited = set()
        
        def dfs(node):
            if node in visited:
                return
                
            visited.add(node)
            
            for dependency in dependency_graph.get(node, []):
                if dependency in dependency_graph:
                    dfs(dependency)
                    
            result.append(node)
            
        for node in dependency_graph:
            if node not in visited:
                dfs(node)
                
        return result
```

### 4.2 Plugin Settings

The `PluginSettings` class provides plugin-specific settings access:

```python
class PluginSettings:
    """Provides plugin-specific settings access"""
    
    def __init__(self, plugin_id, settings_manager):
        self.plugin_id = plugin_id
        self.settings_manager = settings_manager
        
    def get(self, key, default=None):
        """Get a plugin setting"""
        # Try plugin-specific setting first
        plugin_key = f"plugins.{self.plugin_id}.{key}"
        value = self.settings_manager.get(plugin_key)
        
        if value is not None:
            return value
            
        # Fall back to default value
        return default
        
    def set(self, key, value):
        """Set a plugin setting"""
        plugin_key = f"plugins.{self.plugin_id}.{key}"
        return self.settings_manager.set(plugin_key, value)
        
    def get_all(self):
        """Get all settings for this plugin"""
        prefix = f"plugins.{self.plugin_id}."
        all_settings = self.settings_manager.get_all()
        
        plugin_settings = {}
        for key, value in all_settings.items():
            if key.startswith(prefix):
                plugin_key = key[len(prefix):]
                plugin_settings[plugin_key] = value
                
        return plugin_settings
```

## 5. Security and Isolation

### 5.1 Permission System

The plugin system implements a permission-based security model:

```python
class PermissionManager:
    """Manages plugin permissions"""
    
    # Available permissions
    PERMISSIONS = {
        # File system permissions
        "file_read": "Read files",
        "file_write": "Write files",
        "file_delete": "Delete files",
        
        # Network permissions
        "network": "Access the network",
        "network_unrestricted": "Unrestricted network access",
        
        # Hardware permissions
        "microphone": "Access the microphone",
        "camera": "Access the camera",
        "location": "Access location information",
        
        # System permissions
        "system_execute": "Execute system commands",
        "system_settings": "Access system settings",
        
        # Data permissions
        "data_user_profile": "Access user profile data",
        "data_conversations": "Access conversation history",
        "data_learning": "Access learning and personalization data",
        
        # UI permissions
        "ui_dialogs": "Show dialogs and notifications",
        "ui_main_view": "Modify main UI view",
        "ui_system_tray": "Access system tray"
    }
    
    def __init__(self, settings_manager, event_bus):
        self.settings_manager = settings_manager
        self.event_bus = event_bus
        
        # Cache plugin permissions
        self.plugin_permissions = {}
        
    def register_plugin_permissions(self, plugin_id, requested_permissions):
        """Register requested permissions for a plugin"""
        # Store requested permissions
        self.plugin_permissions[plugin_id] = requested_permissions
        
        # Check for auto-grant setting
        auto_grant = self.settings_manager.get("plugins.permissions.auto_grant", False)
        
        if not auto_grant:
            # Emit permission request event
            self.event_bus.emit("plugin.permissions.request", {
                "plugin_id": plugin_id,
                "permissions": requested_permissions
            })
            
        return auto_grant
        
    def check_permission(self, plugin_id, permission):
        """Check if a plugin has a specific permission"""
        # Get granted permissions
        granted = self.settings_manager.get(f"plugins.{plugin_id}.permissions", [])
        
        # Requested permissions
        requested = self.plugin_permissions.get(plugin_id, [])
        
        # Check if permission is granted
        return permission in granted
        
    def grant_permission(self, plugin_id, permission):
        """Grant a permission to a plugin"""
        # Get current permissions
        granted = self.settings_manager.get(f"plugins.{plugin_id}.permissions", [])
        
        # Add permission if not already granted
        if permission not in granted:
            granted.append(permission)
            
        # Save updated permissions
        self.settings_manager.set(f"plugins.{plugin_id}.permissions", granted)
        
        # Emit permission granted event
        self.event_bus.emit("plugin.permissions.granted", {
            "plugin_id": plugin_id,
            "permission": permission
        })
        
    def revoke_permission(self, plugin_id, permission):
        """Revoke a permission from a plugin"""
        # Get current permissions
        granted = self.settings_manager.get(f"plugins.{plugin_id}.permissions", [])
        
        # Remove permission if granted
        if permission in granted:
            granted.remove(permission)
            
        # Save updated permissions
        self.settings_manager.set(f"plugins.{plugin_id}.permissions", granted)
        
        # Emit permission revoked event
        self.event_bus.emit("plugin.permissions.revoked", {
            "plugin_id": plugin_id,
            "permission": permission
        })
        
    def get_plugin_permissions(self, plugin_id):
        """Get all permissions for a plugin"""
        return self.settings_manager.get(f"plugins.{plugin_id}.permissions", [])
```

### 5.2 Sandbox Implementation

Plugins are executed in a controlled environment:

```python
class PluginSandbox:
    """Provides a sandboxed environment for plugin execution"""
    
    def __init__(self, plugin_id, permission_manager):
        self.plugin_id = plugin_id
        self.permission_manager = permission_manager
        
        # Resource usage tracking
        self.memory_usage = 0
        self.cpu_usage = 0
        self.api_calls = {}
        
    async def run(self, callable_func, *args, **kwargs):
        """Run a function in the sandbox"""
        # Check if plugin is allowed to run
        if not self._can_execute():
            raise PermissionError(f"Plugin {self.plugin_id} is not allowed to execute code")
            
        # Track start time and resources
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        try:
            # Run function with timeout
            result = await asyncio.wait_for(
                self._run_tracked(callable_func, *args, **kwargs),
                timeout=5.0  # 5 second timeout
            )
            
            return result
        except asyncio.TimeoutError:
            raise PluginRuntimeError(self.plugin_id, "Execution timed out")
        finally:
            # Update resource usage
            end_time = time.time()
            end_memory = self._get_memory_usage()
            
            self.memory_usage = end_memory - start_memory
            self.cpu_usage = end_time - start_time
            
    async def _run_tracked(self, callable_func, *args, **kwargs):
        """Run function with resource tracking"""
        try:
            if asyncio.iscoroutinefunction(callable_func):
                return await callable_func(*args, **kwargs)
            else:
                return callable_func(*args, **kwargs)
        except Exception as e:
            # Wrap exception with plugin context
            raise PluginRuntimeError(self.plugin_id, str(e))
            
    def check_permission(self, permission):
        """Check if plugin has a specific permission"""
        has_permission = self.permission_manager.check_permission(self.plugin_id, permission)
        
        # Track API call
        self._track_api_call("check_permission", has_permission)
        
        return has_permission
        
    def enforce_permission(self, permission):
        """Enforce that plugin has a specific permission"""
        if not self.check_permission(permission):
            raise PermissionError(
                f"Plugin {self.plugin_id} does not have the required permission: {permission}"
            )
            
    def _can_execute(self):
        """Check if plugin is allowed to execute code"""
        # All plugins can execute basic code
        return True
        
    def _get_memory_usage(self):
        """Get current memory usage"""
        try:
            import psutil
            return psutil.Process().memory_info().rss
        except:
            return 0
            
    def _track_api_call(self, api_name, success):
        """Track API call for resource monitoring"""
        if api_name not in self.api_calls:
            self.api_calls[api_name] = {"count": 0, "success": 0, "failed": 0}
            
        self.api_calls[api_name]["count"] += 1
        
        if success:
            self.api_calls[api_name]["success"] += 1
        else:
            self.api_calls[api_name]["failed"] += 1
```

## 6. Inter-Plugin Communication

### 6.1 Event-Based Communication

Plugins communicate through the event bus:

```python
# In Plugin A
await self._event_bus.emit_async("data.location.request", {
    "request_id": "123",
    "accuracy": "high"
})

# In Plugin B
def initialize(self):
    self._event_bus.subscribe("data.location.request", self._handle_location_request)
    return True
    
async def _handle_location_request(self, event_data):
    request_id = event_data.get("request_id")
    
    # Get location
    location = await self._get_location()
    
    # Send response
    await self._event_bus.emit_async("data.location.response", {
        "request_id": request_id,
        "location": location
    })
```

### 6.2 Service Registration

Plugins can register services for other plugins to use:

```python
# In Plugin A (service provider)
def on_initialize(self):
    # Register weather service
    service_registry = ServiceRegistry.get_instance()
    service_registry.register_service("weather_service", self._weather_service)
    return True
    
# In Plugin B (service consumer)
def on_initialize(self):
    # Get weather service
    service_registry = ServiceRegistry.get_instance()
    self._weather_service = service_registry.get_service("weather_service")
    return True
    
# Service registry implementation
class ServiceRegistry:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ServiceRegistry()
        return cls._instance
        
    def __init__(self):
        self._services = {}
        
    def register_service(self, service_id, service_instance):
        """Register a service"""
        self._services[service_id] = service_instance
        
    def unregister_service(self, service_id):
        """Unregister a service"""
        if service_id in self._services:
            del self._services[service_id]
            
    def get_service(self, service_id):
        """Get a registered service"""
        return self._services.get(service_id)
        
    def get_all_services(self):
        """Get all registered services"""
        return self._services
```

## 7. UI Integration

### 7.1 UI Extension Points

Plugins can extend the UI at designated extension points:

```python
class UIExtensionRegistry:
    """Registry for plugin UI extensions"""
    
    def __init__(self):
        self.extension_points = {
            "main_sidebar": [],
            "chat_actions": [],
            "settings_panels": [],
            "status_bar": [],
            "system_tray": []
        }
        
    def register_extension(self, extension_point, plugin_id, component):
        """Register a UI extension"""
        if extension_point not in self.extension_points:
            raise ValueError(f"Invalid extension point: {extension_point}")
            
        self.extension_points[extension_point].append({
            "plugin_id": plugin_id,
            "component": component
        })
        
    def unregister_extensions(self, plugin_id):
        """Unregister all extensions for a plugin"""
        for extension_point in self.extension_points:
            self.extension_points[extension_point] = [
                ext for ext in self.extension_points[extension_point]
                if ext["plugin_id"] != plugin_id
            ]
            
    def get_extensions(self, extension_point):
        """Get all extensions for a specific extension point"""
        if extension_point not in self.extension_points:
            return []
            
        return self.extension_points[extension_point]
```

### 7.2 UI Component Example

```python
# In a plugin
async def get_ui_components(self):
    """Return UI components for extension points"""
    from ui.components import SettingsPanel, SidebarItem
    
    weather_settings = SettingsPanel(
        title="Weather Settings",
        icon="cloud",
        settings_schema=self.get_settings_schema()
    )
    
    sidebar_item = SidebarItem(
        title="Weather",
        icon="cloud",
        on_click=self._open_weather_view
    )
    
    return {
        "settings_panels": weather_settings,
        "main_sidebar": sidebar_item
    }
    
# In main application
async def _initialize_plugin_ui(self):
    """Initialize plugin UI components"""
    ui_registry = UIExtensionRegistry()
    
    # Get UI components from all plugins
    for plugin_id, plugin in self.plugin_manager.plugins.items():
        try:
            components = await plugin.get_ui_components()
            
            for extension_point, component in components.items():
                ui_registry.register_extension(extension_point, plugin_id, component)
        except Exception as e:
            self.logger.error(f"Error getting UI components from plugin {plugin_id}: {e}")
            
    # Add components to UI
    self._add_settings_panels(ui_registry.get_extensions("settings_panels"))
    self._add_sidebar_items(ui_registry.get_extensions("main_sidebar"))
    self._add_status_items(ui_registry.get_extensions("status_bar"))
    self._add_system_tray_items(ui_registry.get_extensions("system_tray"))
```

## 8. Development Guidelines

### 8.1 Best Practices

When developing plugins, follow these best practices:

1. **Minimal Dependencies**: Limit dependencies to reduce conflicts
2. **Async-First**: Use async functions for I/O operations
3. **Resource Cleanup**: Release resources in `on_shutdown`
4. **Error Handling**: Catch and log errors appropriately
5. **Performance**: Minimize startup impact and resource usage
6. **Event-Driven**: Use events rather than direct method calls
7. **Least Privilege**: Request only needed permissions

### 8.2 Plugin Template

```python
from vpa.core.plugins import Plugin
from typing import Dict, Any, List, Optional

class MyPlugin(Plugin):
    """Template for a VPA plugin"""
    
    @property
    def name(self) -> str:
        return "my_plugin"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def description(self) -> str:
        return "Description of my plugin"
        
    @property
    def author(self) -> str:
        return "Your Name"
        
    def on_initialize(self) -> bool:
        """Initialize the plugin"""
        # Subscribe to events
        self._event_bus.subscribe("some.event", self._handle_event, async_callback=True)
        
        # Initialize components
        self._component = MyComponent()
        
        return True
        
    def on_shutdown(self):
        """Clean up resources"""
        # Unsubscribe from events
        self._event_bus.unsubscribe("some.event", self._handle_event)
        
        # Clean up components
        self._component.close()
        
    def can_handle(self, user_input: str, context: Dict[str, Any]) -> bool:
        """Determine if this plugin can handle the input"""
        # Check if input matches plugin's capabilities
        return "my feature" in user_input.lower()
        
    async def process(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process user input"""
        try:
            # Process the input
            result = await self._component.process(user_input)
            
            return {
                "response": f"Result: {result}",
                "data": result
            }
        except Exception as e:
            self._logger.error(f"Error processing input: {e}")
            return {
                "response": "I encountered an error processing your request.",
                "error": str(e)
            }
            
    async def get_ui_components(self) -> Dict[str, Any]:
        """Return UI components"""
        return {
            "settings_panel": MySettingsPanel(self._settings)
        }
        
    def get_settings_schema(self) -> Dict[str, Any]:
        """Return settings schema"""
        return {
            "option_1": {
                "type": "string",
                "label": "Option 1",
                "description": "Description of option 1",
                "default": "default value"
            },
            "option_2": {
                "type": "boolean",
                "label": "Enable Feature",
                "description": "Enable an optional feature",
                "default": False
            }
        }
        
    def get_permissions(self) -> List[str]:
        """Return required permissions"""
        return ["network"]
        
    async def _handle_event(self, event_data: Dict[str, Any]):
        """Handle an event"""
        self._logger.info(f"Received event: {event_data}")
        # Handle the event
```

### 8.3 Documentation Requirements

All plugins should include:

1. **README.md**: Overview, installation, and usage
2. **CHANGELOG.md**: Version history and changes
3. **LICENSE**: License information
4. **Code Comments**: Docstrings and in-line comments
5. **Examples**: Example usage or tutorials

## 9. Deployment and Distribution

### 9.1 Plugin Packaging

Plugins should be packaged as follows:

```
plugin_name/
├── __init__.py
├── plugin.json
├── main_plugin_file.py
├── README.md
├── CHANGELOG.md
├── LICENSE
├── assets/
│   ├── icons/
│   └── data/
└── lib/
    └── dependencies/
```

### 9.2 Plugin Installation

Plugins can be installed via:

1. **Manual Installation**: Copy to plugins directory
2. **Plugin Marketplace**: In-app plugin browser
3. **Command Line**: Installation script

```python
class PluginInstaller:
    """Handles plugin installation"""
    
    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager
        
    async def install_from_directory(self, source_dir):
        """Install a plugin from a directory"""
        # Validate plugin
        if not self._validate_plugin_directory(source_dir):
            raise ValueError("Invalid plugin directory")
            
        # Read manifest
        manifest_path = os.path.join(source_dir, "plugin.json")
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
            
        plugin_id = manifest.get("id")
        if not plugin_id:
            raise ValueError("Invalid plugin manifest: missing id")
            
        # Determine target directory
        target_dir = os.path.join(get_app_dir(), "plugins", "addons", plugin_id)
        
        # Check if plugin already exists
        if os.path.exists(target_dir):
            raise ValueError(f"Plugin {plugin_id} is already installed")
            
        # Copy plugin files
        shutil.copytree(source_dir, target_dir)
        
        # Install dependencies if specified
        requirements = manifest.get("requirements", [])
        if requirements:
            await self._install_requirements(requirements)
            
        # Refresh plugin cache
        await self.plugin_manager.discover_plugins()
        
        return plugin_id
        
    async def install_from_marketplace(self, plugin_id, version=None):
        """Install a plugin from the marketplace"""
        # Get marketplace API URL
        marketplace_url = "https://vpa-example.com/api/plugins"
        
        # Build request URL
        request_url = f"{marketplace_url}/{plugin_id}"
        if version:
            request_url += f"/version/{version}"
            
        # Download plugin info
        async with aiohttp.ClientSession() as session:
            async with session.get(request_url) as response:
                if response.status != 200:
                    raise ValueError(f"Plugin not found: {plugin_id}")
                    
                plugin_info = await response.json()
                
        # Download plugin
        download_url = plugin_info.get("download_url")
        if not download_url:
            raise ValueError("No download URL available")
            
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download plugin zip
            zip_path = os.path.join(temp_dir, "plugin.zip")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(download_url) as response:
                    if response.status != 200:
                        raise ValueError("Failed to download plugin")
                        
                    with open(zip_path, "wb") as f:
                        f.write(await response.read())
                        
            # Extract plugin
            extract_dir = os.path.join(temp_dir, "extracted")
            os.makedirs(extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)
                
            # Install from extracted directory
            return await self.install_from_directory(extract_dir)
            
    def _validate_plugin_directory(self, directory):
        """Validate a plugin directory structure"""
        # Check if directory exists
        if not os.path.isdir(directory):
            return False
            
        # Check if manifest exists
        manifest_path = os.path.join(directory, "plugin.json")
        if not os.path.exists(manifest_path):
            return False
            
        # Check if main file exists
        try:
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
                
            main_file = manifest.get("main_file", "__init__.py")
            main_file_path = os.path.join(directory, main_file)
            
            if not os.path.exists(main_file_path):
                return False
        except:
            return False
            
        return True
        
    async def _install_requirements(self, requirements):
        """Install plugin requirements"""
        import subprocess
        import sys
        
        # Create requirements file
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as temp:
            temp.write("\n".join(requirements))
            temp_path = temp.name
            
        try:
            # Install requirements
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "-r", temp_path
            ])
        finally:
            # Clean up temp file
            os.unlink(temp_path)
```

### 9.3 Plugin Updates

Plugin updates are managed through version tracking:

```python
class PluginUpdater:
    """Manages plugin updates"""
    
    def __init__(self, plugin_manager):
        self.plugin_manager = plugin_manager
        
    async def check_for_updates(self):
        """Check for plugin updates"""
        updates = {}
        
        # Get installed plugins
        plugins = self.plugin_manager.plugin_metadata
        
        # Get marketplace API URL
        marketplace_url = "https://vpa-example.com/api/plugins"
        
        # Check each plugin
        async with aiohttp.ClientSession() as session:
            for plugin_id, metadata in plugins.items():
                current_version = metadata.get("version", "1.0.0")
                
                # Skip plugins with no version
                if not current_version:
                    continue
                    
                # Check marketplace for newer version
                try:
                    request_url = f"{marketplace_url}/{plugin_id}/latest"
                    async with session.get(request_url) as response:
                        if response.status != 200:
                            continue
                            
                        plugin_info = await response.json()
                        latest_version = plugin_info.get("version")
                        
                        if not latest_version:
                            continue
                            
                        # Compare versions
                        if version.parse(latest_version) > version.parse(current_version):
                            updates[plugin_id] = {
                                "current_version": current_version,
                                "latest_version": latest_version,
                                "update_url": plugin_info.get("download_url"),
                                "release_notes": plugin_info.get("release_notes")
                            }
                except Exception as e:
                    logger.error(f"Error checking for updates for plugin {plugin_id}: {e}")
                    
        return updates
        
    async def update_plugin(self, plugin_id):
        """Update a specific plugin"""
        # Check for updates
        updates = await self.check_for_updates()
        
        if plugin_id not in updates:
            raise ValueError(f"No update available for plugin {plugin_id}")
            
        update_info = updates[plugin_id]
        download_url = update_info.get("update_url")
        
        if not download_url:
            raise ValueError(f"No download URL available for plugin {plugin_id}")
            
        # Unload plugin
        await self.plugin_manager.unload_plugin(plugin_id)
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download plugin zip
            zip_path = os.path.join(temp_dir, "plugin.zip")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(download_url) as response:
                    if response.status != 200:
                        raise ValueError("Failed to download plugin update")
                        
                    with open(zip_path, "wb") as f:
                        f.write(await response.read())
                        
            # Extract plugin
            extract_dir = os.path.join(temp_dir, "extracted")
            os.makedirs(extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)
                
            # Validate plugin
            installer = PluginInstaller(self.plugin_manager)
            if not installer._validate_plugin_directory(extract_dir):
                raise ValueError("Invalid plugin update")
                
            # Read manifest to verify plugin ID
            manifest_path = os.path.join(extract_dir, "plugin.json")
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
                
            update_plugin_id = manifest.get("id")
            if update_plugin_id != plugin_id:
                raise ValueError(f"Plugin ID mismatch: expected {plugin_id}, got {update_plugin_id}")
                
            # Determine plugin directory
            plugin_dir = os.path.join(get_app_dir(), "plugins", "addons", plugin_id)
            
            # Backup existing plugin
            backup_dir = os.path.join(get_app_dir(), "backups", "plugins", 
                                     f"{plugin_id}_{int(time.time())}")
            os.makedirs(os.path.dirname(backup_dir), exist_ok=True)
            
            if os.path.exists(plugin_dir):
                shutil.copytree(plugin_dir, backup_dir)
                shutil.rmtree(plugin_dir)
                
            # Install updated plugin
            shutil.copytree(extract_dir, plugin_dir)
            
            # Install dependencies if specified
            requirements = manifest.get("requirements", [])
            if requirements:
                await installer._install_requirements(requirements)
                
        # Reload plugins
        await self.plugin_manager.load_plugins()
        
        return update_info["latest_version"]
```

## Conclusion

The VPA plugin system provides a flexible and secure way to extend the application's functionality. By following an event-driven architecture with clear interfaces and isolation, plugins can add new features without compromising the core application's stability or security.

Developers can create custom plugins that integrate seamlessly with the VPA ecosystem, while users benefit from a growing library of extensions that enhance their virtual personal assistant experience.

---

*Document created on August 28, 2025*  
*Version: 1.0*
