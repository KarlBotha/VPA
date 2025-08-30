# Plugin Manager System Requirements

## Overview

This document details the specific requirements for the Plugin Manager System in the VPA (Virtual Personal Assistant) project. The Plugin Manager is a core architectural component that enables modular functionality through dynamic plugin discovery, loading, and lifecycle management with strict performance and isolation targets.

## 1. Core Requirements

### 1.1 Functional Requirements

| Feature | Requirement |
|---------|-------------|
| **Plugin Discovery** | Auto-discovery of plugins from multiple locations |
| **Cache System** | Cache discovery results in `plugin_cache.json` |
| **Lazy Loading** | Load plugins on-demand to optimize startup time |
| **Dependency Resolution** | Automatic resolution of plugin dependencies |
| **Plugin Lifecycle** | Control initialization, start, stop, and unload |
| **Priority System** | Load plugins in priority order |
| **Error Isolation** | Plugin failures must not crash the main application |
| **Hot Reloading** | Optional support for reloading plugins without app restart |
| **Plugin Configuration** | Central management of plugin settings |
| **Plugin Metadata** | Standardized plugin information schema |

### 1.2 Non-Functional Requirements

| Feature | Requirement |
|---------|-------------|
| **Discovery Time** | <500ms for plugin discovery (with cache) |
| **Memory Footprint** | <10MB overhead per plugin |
| **Loading Performance** | <100ms per plugin load operation |
| **Error Rate** | <0.01% plugin load failure rate on valid plugins |
| **Isolation** | Complete error isolation between plugins |
| **Resource Control** | Monitor and limit plugin resource usage |

## 2. Plugin Manager Implementation

### 2.1 Core Plugin Manager Class

```python
import os
import json
import importlib
import inspect
import logging
import time
import asyncio
from typing import Dict, List, Optional, Any, Type, Set, Tuple
from abc import ABC, abstractmethod
from pathlib import Path

from vpa.core.events import event_bus
from vpa.core.performance import PerformanceMonitor

logger = logging.getLogger(__name__)

class Plugin(ABC):
    """Base class for all plugins.
    
    All plugins must inherit from this class and implement its abstract methods.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the plugin."""
        pass
        
    @property
    def version(self) -> str:
        """Return the version of the plugin."""
        return "1.0.0"
        
    @property
    def description(self) -> str:
        """Return the description of the plugin."""
        return ""
        
    @property
    def priority(self) -> int:
        """Return the priority of the plugin (higher is loaded first)."""
        return 0
        
    @property
    def dependencies(self) -> List[str]:
        """Return a list of plugin names that this plugin depends on."""
        return []
        
    def can_handle(self, user_input: str, context: Dict[str, Any]) -> bool:
        """Check if this plugin can handle the given input.
        
        Args:
            user_input: The user's input
            context: Additional context information
            
        Returns:
            True if the plugin can handle the input, False otherwise
        """
        return False
        
    async def process(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the user input.
        
        Args:
            user_input: The user's input
            context: Additional context information
            
        Returns:
            A dictionary with the result
        """
        return {"response": None}
        
    async def initialize(self) -> bool:
        """Initialize the plugin.
        
        This is called once when the plugin is loaded.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        return True
        
    async def start(self) -> bool:
        """Start the plugin.
        
        This is called when the plugin is enabled.
        
        Returns:
            True if the plugin was started successfully, False otherwise
        """
        return True
        
    async def stop(self) -> bool:
        """Stop the plugin.
        
        This is called when the plugin is disabled.
        
        Returns:
            True if the plugin was stopped successfully, False otherwise
        """
        return True
        
    async def unload(self) -> bool:
        """Unload the plugin.
        
        This is called when the plugin is unloaded.
        
        Returns:
            True if the plugin was unloaded successfully, False otherwise
        """
        return True
        
    def get_settings_schema(self) -> Dict[str, Any]:
        """Return the settings schema for this plugin.
        
        Returns:
            A dictionary describing the settings schema
        """
        return {}
        
    def get_settings(self) -> Dict[str, Any]:
        """Return the current settings for this plugin.
        
        Returns:
            A dictionary with the current settings
        """
        return {}
        
    def update_settings(self, settings: Dict[str, Any]) -> bool:
        """Update the settings for this plugin.
        
        Args:
            settings: The new settings
            
        Returns:
            True if the settings were updated successfully, False otherwise
        """
        return True


class PluginManager:
    """Manager for plugin discovery, loading, and lifecycle.
    
    The PluginManager is responsible for discovering plugins, loading them,
    and managing their lifecycle.
    """
    
    def __init__(self):
        self._plugins: Dict[str, Plugin] = {}
        self._plugin_classes: Dict[str, Type[Plugin]] = {}
        self._plugin_modules: Dict[str, Any] = {}
        self._plugin_info: Dict[str, Dict[str, Any]] = {}
        self._discovery_paths: List[str] = []
        self._enabled_plugins: Set[str] = set()
        self._initialized_plugins: Set[str] = set()
        self._cache_file = os.path.join(os.path.expanduser("~"), ".vpa", "plugin_cache.json")
        self._discovery_complete = False
        
    @PerformanceMonitor.track_execution_time("plugin_manager.add_discovery_path")
    def add_discovery_path(self, path: str) -> None:
        """Add a path for plugin discovery.
        
        Args:
            path: Path to search for plugins
        """
        if not os.path.exists(path):
            logger.warning(f"Plugin discovery path does not exist: {path}")
            return
            
        if path not in self._discovery_paths:
            self._discovery_paths.append(path)
            self._discovery_complete = False
            
    @PerformanceMonitor.track_execution_time("plugin_manager.discover_plugins")
    async def discover_plugins(self, use_cache: bool = True) -> Dict[str, Dict[str, Any]]:
        """Discover plugins in the configured paths.
        
        Args:
            use_cache: Whether to use the plugin cache
            
        Returns:
            A dictionary of plugin information
        """
        # Check if we've already discovered plugins
        if self._discovery_complete:
            return self._plugin_info
            
        # Try to load from cache first
        if use_cache and os.path.exists(self._cache_file):
            try:
                with open(self._cache_file, 'r') as f:
                    cache_data = json.load(f)
                    
                if self._validate_cache(cache_data):
                    self._plugin_info = cache_data
                    self._discovery_complete = True
                    logger.info(f"Loaded {len(self._plugin_info)} plugins from cache")
                    
                    # Emit plugin discovery event
                    await event_bus.emit_async("plugin_manager.discovery.complete", {
                        "plugin_count": len(self._plugin_info),
                        "from_cache": True
                    })
                    
                    return self._plugin_info
            except Exception as e:
                logger.error(f"Error loading plugin cache: {e}")
                
        # Perform full discovery
        plugin_info = {}
        
        # Discover plugins in each path
        for path in self._discovery_paths:
            await self._discover_in_path(path, plugin_info)
            
        # Store plugin info
        self._plugin_info = plugin_info
        self._discovery_complete = True
        
        # Save to cache
        await self._save_cache()
        
        # Emit plugin discovery event
        await event_bus.emit_async("plugin_manager.discovery.complete", {
            "plugin_count": len(self._plugin_info),
            "from_cache": False
        })
        
        return self._plugin_info
        
    @PerformanceMonitor.track_execution_time("plugin_manager.load_plugin")
    async def load_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """Load a specific plugin.
        
        Args:
            plugin_id: ID of the plugin to load
            
        Returns:
            The loaded plugin instance, or None if the plugin could not be loaded
        """
        # Check if plugin is already loaded
        if plugin_id in self._plugins:
            return self._plugins[plugin_id]
            
        # Check if we have info for this plugin
        if plugin_id not in self._plugin_info:
            # Try to discover it
            await self.discover_plugins(use_cache=False)
            
            if plugin_id not in self._plugin_info:
                logger.error(f"Plugin not found: {plugin_id}")
                
                # Emit plugin error event
                await event_bus.emit_async("plugin_manager.plugin.error", {
                    "plugin_id": plugin_id,
                    "error": "Plugin not found",
                    "phase": "load"
                })
                
                return None
                
        # Load dependencies first
        plugin_info = self._plugin_info[plugin_id]
        dependencies = plugin_info.get("dependencies", [])
        
        for dep_id in dependencies:
            if dep_id not in self._plugins:
                dep_plugin = await self.load_plugin(dep_id)
                
                if dep_plugin is None:
                    logger.error(f"Failed to load dependency {dep_id} for plugin {plugin_id}")
                    
                    # Emit plugin error event
                    await event_bus.emit_async("plugin_manager.plugin.error", {
                        "plugin_id": plugin_id,
                        "error": f"Failed to load dependency: {dep_id}",
                        "phase": "load"
                    })
                    
                    return None
                    
        # Load plugin module
        try:
            if "module_path" not in plugin_info:
                logger.error(f"Module path not found for plugin {plugin_id}")
                return None
                
            module_path = plugin_info["module_path"]
            class_name = plugin_info.get("class_name", "Plugin")
            
            # Import module
            if module_path not in self._plugin_modules:
                spec = importlib.util.spec_from_file_location(
                    f"vpa.plugins.{plugin_id}",
                    module_path
                )
                
                if spec is None:
                    logger.error(f"Could not load spec for {module_path}")
                    return None
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self._plugin_modules[module_path] = module
            else:
                module = self._plugin_modules[module_path]
                
            # Get plugin class
            if not hasattr(module, class_name):
                logger.error(f"Class {class_name} not found in module {module_path}")
                return None
                
            plugin_class = getattr(module, class_name)
            self._plugin_classes[plugin_id] = plugin_class
            
            # Create plugin instance
            plugin_instance = plugin_class()
            self._plugins[plugin_id] = plugin_instance
            
            # Emit plugin loaded event
            await event_bus.emit_async("plugin_manager.plugin.loaded", {
                "plugin_id": plugin_id,
                "name": plugin_instance.name,
                "version": plugin_instance.version
            })
            
            return plugin_instance
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_id}: {e}")
            
            # Emit plugin error event
            await event_bus.emit_async("plugin_manager.plugin.error", {
                "plugin_id": plugin_id,
                "error": str(e),
                "phase": "load"
            })
            
            return None
            
    @PerformanceMonitor.track_execution_time("plugin_manager.load_plugins")
    async def load_plugins(self, plugin_ids: Optional[List[str]] = None) -> Dict[str, Plugin]:
        """Load multiple plugins.
        
        Args:
            plugin_ids: IDs of plugins to load, or None to load all discovered plugins
            
        Returns:
            A dictionary of loaded plugin instances
        """
        # Discover plugins if not done yet
        if not self._discovery_complete:
            await self.discover_plugins()
            
        # Determine which plugins to load
        if plugin_ids is None:
            # Load all plugins
            plugin_ids = list(self._plugin_info.keys())
            
        # Sort plugins by priority
        plugin_ids = sorted(
            plugin_ids,
            key=lambda pid: self._plugin_info.get(pid, {}).get("priority", 0),
            reverse=True  # Higher priority first
        )
        
        # Load each plugin
        loaded_plugins = {}
        for plugin_id in plugin_ids:
            plugin = await self.load_plugin(plugin_id)
            if plugin is not None:
                loaded_plugins[plugin_id] = plugin
                
        return loaded_plugins
        
    @PerformanceMonitor.track_execution_time("plugin_manager.initialize_plugin")
    async def initialize_plugin(self, plugin_id: str) -> bool:
        """Initialize a plugin.
        
        Args:
            plugin_id: ID of the plugin to initialize
            
        Returns:
            True if the plugin was initialized successfully, False otherwise
        """
        # Check if plugin is already initialized
        if plugin_id in self._initialized_plugins:
            return True
            
        # Check if plugin is loaded
        if plugin_id not in self._plugins:
            plugin = await self.load_plugin(plugin_id)
            if plugin is None:
                return False
                
        # Initialize dependencies first
        plugin_info = self._plugin_info[plugin_id]
        dependencies = plugin_info.get("dependencies", [])
        
        for dep_id in dependencies:
            if dep_id not in self._initialized_plugins:
                success = await self.initialize_plugin(dep_id)
                if not success:
                    logger.error(f"Failed to initialize dependency {dep_id} for plugin {plugin_id}")
                    
                    # Emit plugin error event
                    await event_bus.emit_async("plugin_manager.plugin.error", {
                        "plugin_id": plugin_id,
                        "error": f"Failed to initialize dependency: {dep_id}",
                        "phase": "initialize"
                    })
                    
                    return False
                    
        # Initialize plugin
        try:
            plugin = self._plugins[plugin_id]
            
            # Initialize the plugin
            success = await plugin.initialize()
            
            if success:
                self._initialized_plugins.add(plugin_id)
                
                # Emit plugin initialized event
                await event_bus.emit_async("plugin_manager.plugin.initialized", {
                    "plugin_id": plugin_id,
                    "name": plugin.name
                })
                
            return success
        except Exception as e:
            logger.error(f"Error initializing plugin {plugin_id}: {e}")
            
            # Emit plugin error event
            await event_bus.emit_async("plugin_manager.plugin.error", {
                "plugin_id": plugin_id,
                "error": str(e),
                "phase": "initialize"
            })
            
            return False
            
    @PerformanceMonitor.track_execution_time("plugin_manager.enable_plugin")
    async def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin.
        
        Args:
            plugin_id: ID of the plugin to enable
            
        Returns:
            True if the plugin was enabled successfully, False otherwise
        """
        # Check if plugin is already enabled
        if plugin_id in self._enabled_plugins:
            return True
            
        # Initialize the plugin first
        if plugin_id not in self._initialized_plugins:
            success = await self.initialize_plugin(plugin_id)
            if not success:
                return False
                
        # Enable plugin
        try:
            plugin = self._plugins[plugin_id]
            
            # Start the plugin
            success = await plugin.start()
            
            if success:
                self._enabled_plugins.add(plugin_id)
                
                # Emit plugin enabled event
                await event_bus.emit_async("plugin_manager.plugin.enabled", {
                    "plugin_id": plugin_id,
                    "name": plugin.name
                })
                
            return success
        except Exception as e:
            logger.error(f"Error enabling plugin {plugin_id}: {e}")
            
            # Emit plugin error event
            await event_bus.emit_async("plugin_manager.plugin.error", {
                "plugin_id": plugin_id,
                "error": str(e),
                "phase": "enable"
            })
            
            return False
            
    @PerformanceMonitor.track_execution_time("plugin_manager.disable_plugin")
    async def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin.
        
        Args:
            plugin_id: ID of the plugin to disable
            
        Returns:
            True if the plugin was disabled successfully, False otherwise
        """
        # Check if plugin is enabled
        if plugin_id not in self._enabled_plugins:
            return True
            
        # Check if plugin is loaded
        if plugin_id not in self._plugins:
            return True
            
        # Check if other plugins depend on this one
        for other_id, plugin in self._plugins.items():
            if other_id != plugin_id and plugin_id in plugin.dependencies:
                if other_id in self._enabled_plugins:
                    # Disable dependent plugin first
                    await self.disable_plugin(other_id)
                    
        # Disable plugin
        try:
            plugin = self._plugins[plugin_id]
            
            # Stop the plugin
            success = await plugin.stop()
            
            if success:
                self._enabled_plugins.remove(plugin_id)
                
                # Emit plugin disabled event
                await event_bus.emit_async("plugin_manager.plugin.disabled", {
                    "plugin_id": plugin_id,
                    "name": plugin.name
                })
                
            return success
        except Exception as e:
            logger.error(f"Error disabling plugin {plugin_id}: {e}")
            
            # Emit plugin error event
            await event_bus.emit_async("plugin_manager.plugin.error", {
                "plugin_id": plugin_id,
                "error": str(e),
                "phase": "disable"
            })
            
            return False
            
    @PerformanceMonitor.track_execution_time("plugin_manager.unload_plugin")
    async def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin.
        
        Args:
            plugin_id: ID of the plugin to unload
            
        Returns:
            True if the plugin was unloaded successfully, False otherwise
        """
        # Disable the plugin first
        if plugin_id in self._enabled_plugins:
            success = await self.disable_plugin(plugin_id)
            if not success:
                return False
                
        # Check if other plugins depend on this one
        for other_id, plugin in self._plugins.items():
            if other_id != plugin_id and plugin_id in plugin.dependencies:
                # Dependent plugin is loaded but not enabled
                if other_id in self._plugins and other_id not in self._enabled_plugins:
                    # Unload dependent plugin first
                    await self.unload_plugin(other_id)
                    
        # Unload plugin
        try:
            if plugin_id in self._plugins:
                plugin = self._plugins[plugin_id]
                
                # Unload the plugin
                success = await plugin.unload()
                
                if success:
                    del self._plugins[plugin_id]
                    if plugin_id in self._initialized_plugins:
                        self._initialized_plugins.remove(plugin_id)
                    
                    # Emit plugin unloaded event
                    await event_bus.emit_async("plugin_manager.plugin.unloaded", {
                        "plugin_id": plugin_id,
                        "name": plugin.name
                    })
                    
                return success
            return True
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_id}: {e}")
            
            # Emit plugin error event
            await event_bus.emit_async("plugin_manager.plugin.error", {
                "plugin_id": plugin_id,
                "error": str(e),
                "phase": "unload"
            })
            
            return False
            
    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """Get a plugin instance.
        
        Args:
            plugin_id: ID of the plugin to get
            
        Returns:
            The plugin instance, or None if the plugin is not loaded
        """
        return self._plugins.get(plugin_id)
        
    def get_plugin_info(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a plugin.
        
        Args:
            plugin_id: ID of the plugin to get information about
            
        Returns:
            Dictionary with plugin information, or None if the plugin is not known
        """
        return self._plugin_info.get(plugin_id)
        
    def is_plugin_loaded(self, plugin_id: str) -> bool:
        """Check if a plugin is loaded.
        
        Args:
            plugin_id: ID of the plugin to check
            
        Returns:
            True if the plugin is loaded, False otherwise
        """
        return plugin_id in self._plugins
        
    def is_plugin_enabled(self, plugin_id: str) -> bool:
        """Check if a plugin is enabled.
        
        Args:
            plugin_id: ID of the plugin to check
            
        Returns:
            True if the plugin is enabled, False otherwise
        """
        return plugin_id in self._enabled_plugins
        
    def is_plugin_initialized(self, plugin_id: str) -> bool:
        """Check if a plugin is initialized.
        
        Args:
            plugin_id: ID of the plugin to check
            
        Returns:
            True if the plugin is initialized, False otherwise
        """
        return plugin_id in self._initialized_plugins
        
    async def get_loaded_plugins(self) -> Dict[str, Plugin]:
        """Get all loaded plugins.
        
        Returns:
            A dictionary of plugin ID to plugin instance
        """
        return self._plugins.copy()
        
    async def get_enabled_plugins(self) -> Dict[str, Plugin]:
        """Get all enabled plugins.
        
        Returns:
            A dictionary of plugin ID to plugin instance
        """
        return {pid: self._plugins[pid] for pid in self._enabled_plugins if pid in self._plugins}
        
    async def get_plugin_handling_input(self, user_input: str, context: Dict[str, Any]) -> List[Plugin]:
        """Get all plugins that can handle the given input.
        
        Args:
            user_input: The user input to check
            context: Additional context information
            
        Returns:
            A list of plugins that can handle the input
        """
        handlers = []
        
        for plugin_id in self._enabled_plugins:
            if plugin_id in self._plugins:
                plugin = self._plugins[plugin_id]
                try:
                    if plugin.can_handle(user_input, context):
                        handlers.append(plugin)
                except Exception as e:
                    logger.error(f"Error checking if plugin {plugin_id} can handle input: {e}")
                    
        return handlers
        
    async def process_input(self, user_input: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process user input with all plugins that can handle it.
        
        Args:
            user_input: The user input to process
            context: Additional context information
            
        Returns:
            A list of results from the plugins
        """
        handlers = await self.get_plugin_handling_input(user_input, context)
        results = []
        
        for plugin in handlers:
            try:
                result = await plugin.process(user_input, context)
                results.append({
                    "plugin": plugin.name,
                    "result": result
                })
            except Exception as e:
                logger.error(f"Error processing input with plugin {plugin.name}: {e}")
                results.append({
                    "plugin": plugin.name,
                    "error": str(e)
                })
                
        return results
        
    async def cleanup(self) -> None:
        """Clean up resources and stop all plugins."""
        # Stop all enabled plugins
        for plugin_id in list(self._enabled_plugins):
            await self.disable_plugin(plugin_id)
            
        # Unload all plugins
        for plugin_id in list(self._plugins.keys()):
            await self.unload_plugin(plugin_id)
            
        self._plugins = {}
        self._plugin_classes = {}
        self._plugin_modules = {}
        self._enabled_plugins = set()
        self._initialized_plugins = set()
        
    async def _discover_in_path(self, path: str, plugin_info: Dict[str, Dict[str, Any]]) -> None:
        """Discover plugins in a path.
        
        Args:
            path: Path to search for plugins
            plugin_info: Dictionary to store plugin information in
        """
        # Check if path exists
        if not os.path.exists(path):
            logger.warning(f"Plugin path does not exist: {path}")
            return
            
        # Find potential plugin directories
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            
            # Check if it's a directory
            if os.path.isdir(item_path):
                # Check if it contains a plugin manifest
                manifest_path = os.path.join(item_path, "plugin.json")
                if os.path.exists(manifest_path):
                    # Load manifest
                    try:
                        with open(manifest_path, 'r') as f:
                            manifest = json.load(f)
                            
                        # Check required fields
                        if "id" not in manifest or "name" not in manifest:
                            logger.warning(f"Invalid plugin manifest in {item_path}: missing id or name")
                            continue
                            
                        plugin_id = manifest["id"]
                        
                        # Find main module
                        main_module = manifest.get("main", "plugin.py")
                        module_path = os.path.join(item_path, main_module)
                        
                        if not os.path.exists(module_path):
                            logger.warning(f"Plugin module not found: {module_path}")
                            continue
                            
                        # Get plugin info
                        info = {
                            "id": plugin_id,
                            "name": manifest["name"],
                            "version": manifest.get("version", "1.0.0"),
                            "description": manifest.get("description", ""),
                            "author": manifest.get("author", ""),
                            "dependencies": manifest.get("dependencies", []),
                            "priority": manifest.get("priority", 0),
                            "path": item_path,
                            "module_path": module_path,
                            "class_name": manifest.get("class", "Plugin"),
                            "settings_schema": manifest.get("settings_schema", {})
                        }
                        
                        plugin_info[plugin_id] = info
                    except Exception as e:
                        logger.error(f"Error loading plugin manifest {manifest_path}: {e}")
                        
    def _validate_cache(self, cache_data: Dict[str, Dict[str, Any]]) -> bool:
        """Validate the plugin cache data.
        
        Args:
            cache_data: Cache data to validate
            
        Returns:
            True if the cache data is valid, False otherwise
        """
        # Check if cache data is a dictionary
        if not isinstance(cache_data, dict):
            return False
            
        # Check each plugin info
        for plugin_id, info in cache_data.items():
            if not isinstance(info, dict):
                return False
                
            if "path" not in info or "module_path" not in info:
                return False
                
            # Check if paths exist
            if not os.path.exists(info["path"]) or not os.path.exists(info["module_path"]):
                return False
                
        return True
        
    async def _save_cache(self) -> None:
        """Save the plugin info to the cache file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self._cache_file), exist_ok=True)
            
            # Save cache
            with open(self._cache_file, 'w') as f:
                json.dump(self._plugin_info, f)
                
            logger.info(f"Saved plugin cache with {len(self._plugin_info)} plugins")
        except Exception as e:
            logger.error(f"Error saving plugin cache: {e}")
```

### 2.2 Plugin Base Class

The `Plugin` base class has been defined within the `PluginManager` implementation above. This is the base class that all plugins must inherit from to be compatible with the Plugin Manager system.

### 2.3 Plugin Manifest Schema

```json
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "VPA Plugin Manifest",
    "description": "Manifest file for VPA plugins",
    "type": "object",
    "required": ["id", "name"],
    "properties": {
        "id": {
            "description": "Unique identifier for the plugin",
            "type": "string",
            "pattern": "^[a-z][a-z0-9_]*$"
        },
        "name": {
            "description": "Display name of the plugin",
            "type": "string"
        },
        "version": {
            "description": "Version of the plugin in semver format",
            "type": "string",
            "default": "1.0.0"
        },
        "description": {
            "description": "Description of the plugin",
            "type": "string",
            "default": ""
        },
        "author": {
            "description": "Author of the plugin",
            "type": "string",
            "default": ""
        },
        "dependencies": {
            "description": "List of plugin IDs that this plugin depends on",
            "type": "array",
            "items": {
                "type": "string"
            },
            "default": []
        },
        "priority": {
            "description": "Loading priority of the plugin (higher is loaded first)",
            "type": "integer",
            "default": 0
        },
        "main": {
            "description": "Main module file of the plugin",
            "type": "string",
            "default": "plugin.py"
        },
        "class": {
            "description": "Name of the plugin class",
            "type": "string",
            "default": "Plugin"
        },
        "settings_schema": {
            "description": "Schema for plugin settings",
            "type": "object",
            "default": {}
        }
    }
}
```

## 3. Plugin Discovery and Loading Process

### 3.1 Plugin Directory Structure

```
plugins/
├── core_plugins/          # Built-in core plugins
│   ├── time_plugin/
│   │   ├── plugin.json    # Plugin manifest
│   │   └── plugin.py      # Plugin implementation
│   ├── system_plugin/
│   │   ├── plugin.json
│   │   └── plugin.py
│   └── ...
├── extension_plugins/    # User-installed extension plugins
│   ├── weather_plugin/
│   │   ├── plugin.json
│   │   └── plugin.py
│   ├── calendar_plugin/
│   │   ├── plugin.json
│   │   └── plugin.py
│   └── ...
└── user_plugins/         # User-created plugins
    ├── custom_plugin/
    │   ├── plugin.json
    │   └── plugin.py
    └── ...
```

### 3.2 Discovery Process

1. **Default Discovery Paths**:
   - `core_plugins` directory (built-in plugins)
   - `extension_plugins` directory (user-installed extension plugins)
   - `user_plugins` directory (user-created plugins)
   - `%APPDATA%\VPA\plugins` directory (user-specific plugins)

2. **Cache Usage**:
   - First check `plugin_cache.json` for cached plugin info
   - Validate cache by checking if plugin paths still exist
   - If cache is valid, load plugin info from cache
   - If cache is invalid, perform full discovery

3. **Manifest Validation**:
   - Each plugin must have a valid `plugin.json` manifest
   - Required fields: `id`, `name`
   - Optional fields: `version`, `description`, `author`, `dependencies`, etc.

### 3.3 Loading Process

1. **Dependency Resolution**:
   - Build dependency graph from plugin manifests
   - Detect circular dependencies
   - Determine loading order based on dependencies and priority

2. **Lazy Loading**:
   - Load plugins only when needed
   - Cache plugin instances for reuse

3. **Error Isolation**:
   - Each plugin loads in isolated error boundary
   - Plugin failures don't affect other plugins or the core application

### 3.4 Plugin Lifecycle

1. **Discovery**: Find plugins in configured directories
2. **Loading**: Import plugin modules and create instances
3. **Initialization**: Initialize plugin (connect to services, load resources)
4. **Enabling**: Start plugin operation
5. **Disabling**: Stop plugin operation
6. **Unloading**: Remove plugin from memory

## 4. Plugin Usage Patterns

### 4.1 Basic Plugin Implementation

```python
from vpa.core.plugins import Plugin
from vpa.core.events import event_bus

class TimePlugin(Plugin):
    """Plugin for time-related functionality."""
    
    @property
    def name(self) -> str:
        """Return the name of the plugin."""
        return "Time Plugin"
        
    @property
    def version(self) -> str:
        """Return the version of the plugin."""
        return "1.0.0"
        
    @property
    def description(self) -> str:
        """Return the description of the plugin."""
        return "Provides time-related functionality."
        
    @property
    def priority(self) -> int:
        """Return the priority of the plugin."""
        return 100  # High priority
        
    def can_handle(self, user_input: str, context: Dict[str, Any]) -> bool:
        """Check if this plugin can handle the given input."""
        input_lower = user_input.lower()
        
        time_keywords = ["time", "date", "day", "month", "year", "clock"]
        return any(keyword in input_lower for keyword in time_keywords)
        
    async def process(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the user input."""
        from datetime import datetime
        
        now = datetime.now()
        
        input_lower = user_input.lower()
        
        if "time" in input_lower:
            time_str = now.strftime("%H:%M:%S")
            return {
                "response": f"The current time is {time_str}.",
                "time": time_str
            }
        elif "date" in input_lower:
            date_str = now.strftime("%Y-%m-%d")
            return {
                "response": f"Today's date is {date_str}.",
                "date": date_str
            }
        else:
            datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")
            return {
                "response": f"Current date and time: {datetime_str}",
                "datetime": datetime_str
            }
            
    async def initialize(self) -> bool:
        """Initialize the plugin."""
        # No special initialization needed
        return True
        
    async def start(self) -> bool:
        """Start the plugin."""
        # Subscribe to events
        self._unsubscribe = event_bus.subscribe(
            "system.time_request",
            self._handle_time_request,
            async_callback=True
        )
        return True
        
    async def stop(self) -> bool:
        """Stop the plugin."""
        # Unsubscribe from events
        if hasattr(self, "_unsubscribe"):
            self._unsubscribe()
        return True
        
    async def unload(self) -> bool:
        """Unload the plugin."""
        # Clean up resources
        return True
        
    async def _handle_time_request(self, event_data: Dict[str, Any]) -> None:
        """Handle time request events."""
        from datetime import datetime
        
        request_id = event_data.get("request_id", "")
        format_str = event_data.get("format", "%Y-%m-%d %H:%M:%S")
        
        now = datetime.now()
        time_str = now.strftime(format_str)
        
        # Emit response event
        await event_bus.emit_async("system.time_response", {
            "request_id": request_id,
            "time": time_str,
            "timestamp": now.timestamp()
        })
```

### 4.2 Plugin with Dependencies

```python
from vpa.core.plugins import Plugin
from vpa.core.events import event_bus

class CalendarPlugin(Plugin):
    """Plugin for calendar functionality."""
    
    @property
    def name(self) -> str:
        """Return the name of the plugin."""
        return "Calendar Plugin"
        
    @property
    def dependencies(self) -> List[str]:
        """Return a list of plugin IDs that this plugin depends on."""
        return ["time_plugin"]  # Depends on TimePlugin
        
    def can_handle(self, user_input: str, context: Dict[str, Any]) -> bool:
        """Check if this plugin can handle the given input."""
        input_lower = user_input.lower()
        
        calendar_keywords = ["calendar", "schedule", "event", "appointment", "reminder"]
        return any(keyword in input_lower for keyword in calendar_keywords)
        
    async def process(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the user input."""
        # Get time information from the TimePlugin
        time_info = await self._get_time_info()
        
        # Process calendar request using time info
        # ...
        
        return {
            "response": "Calendar processing complete.",
            "time_info": time_info
        }
        
    async def _get_time_info(self) -> Dict[str, Any]:
        """Get time information from TimePlugin."""
        # Create a unique request ID
        request_id = str(uuid.uuid4())
        
        # Create a future to wait for the response
        future = asyncio.Future()
        
        # Store future in a dictionary
        self._pending_requests[request_id] = future
        
        # Subscribe to the response event
        unsubscribe = event_bus.subscribe(
            "system.time_response",
            lambda e: self._handle_time_response(e, request_id),
            async_callback=False
        )
        
        try:
            # Emit time request event
            await event_bus.emit_async("system.time_request", {
                "request_id": request_id,
                "format": "%Y-%m-%d"
            })
            
            # Wait for the response with timeout
            try:
                return await asyncio.wait_for(future, timeout=5.0)
            except asyncio.TimeoutError:
                logger.error("Timeout waiting for time response")
                return {}
        finally:
            # Clean up
            if request_id in self._pending_requests:
                del self._pending_requests[request_id]
            unsubscribe()
            
    def _handle_time_response(self, event_data: Dict[str, Any], expected_request_id: str) -> None:
        """Handle time response event."""
        request_id = event_data.get("request_id", "")
        
        if request_id == expected_request_id and request_id in self._pending_requests:
            future = self._pending_requests[request_id]
            if not future.done():
                future.set_result(event_data)
```

### 4.3 Plugin with Settings

```python
from vpa.core.plugins import Plugin
from vpa.core.events import event_bus
from vpa.core.config import config_manager

class WeatherPlugin(Plugin):
    """Plugin for weather functionality."""
    
    @property
    def name(self) -> str:
        """Return the name of the plugin."""
        return "Weather Plugin"
        
    def get_settings_schema(self) -> Dict[str, Any]:
        """Return the settings schema for this plugin."""
        return {
            "api_key": {
                "type": "string",
                "description": "API key for weather service",
                "required": True
            },
            "location": {
                "type": "string",
                "description": "Default location for weather",
                "default": "New York"
            },
            "units": {
                "type": "string",
                "description": "Temperature units",
                "enum": ["metric", "imperial"],
                "default": "metric"
            }
        }
        
    def get_settings(self) -> Dict[str, Any]:
        """Return the current settings for this plugin."""
        return config_manager.get_plugin_config("weather_plugin", {
            "location": "New York",
            "units": "metric"
        })
        
    def update_settings(self, settings: Dict[str, Any]) -> bool:
        """Update the settings for this plugin."""
        return config_manager.set_plugin_config("weather_plugin", settings)
        
    async def process(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the user input."""
        # Get plugin settings
        settings = self.get_settings()
        
        # Use settings in API call
        location = self._extract_location(user_input) or settings["location"]
        units = settings["units"]
        api_key = settings.get("api_key")
        
        if not api_key:
            return {
                "response": "Weather API key not configured.",
                "error": "missing_api_key"
            }
            
        # Get weather data
        weather_data = await self._get_weather(location, units, api_key)
        
        return {
            "response": f"The weather in {location} is {weather_data['description']} with a temperature of {weather_data['temperature']}°{units == 'metric' and 'C' or 'F'}.",
            "weather": weather_data
        }
```

## 5. Plugin Security Considerations

### 5.1 Plugin Isolation

1. **Error Isolation**
   - Plugin failures don't affect other plugins or core functionality
   - Each plugin runs in its own error boundary
   - Proper exception handling and logging

2. **Resource Isolation**
   - Monitor and limit plugin CPU usage
   - Monitor and limit plugin memory usage
   - Prevent plugins from overusing system resources

### 5.2 Plugin Permissions

1. **Permission Levels**
   - `basic`: Basic operations (time, calculator, etc.)
   - `user_data`: Access to user data (calendar, contacts, etc.)
   - `system`: System operations (file system, registry, etc.)
   - `network`: Network operations (API calls, etc.)

2. **Permission Declaration**
   - Plugins declare required permissions in manifest
   - User confirms permissions on plugin installation
   - Dynamic permission checks at runtime

### 5.3 Plugin Validation

1. **Manifest Validation**
   - Check manifest for required fields
   - Validate schema conformance
   - Check for version compatibility

2. **Code Validation**
   - Check for malicious code patterns
   - Verify plugin signature
   - Scan for known vulnerabilities

## 6. Plugin Manager Integration with Core Components

### 6.1 Application Manager Integration

```python
from vpa.core.app import AppManager
from vpa.core.plugins import plugin_manager
from vpa.core.events import event_bus

class AppManager:
    """Application lifecycle management."""
    
    async def start(self):
        """Start the application."""
        # Initialize plugin manager
        plugin_manager.add_discovery_path("plugins/core_plugins")
        plugin_manager.add_discovery_path("plugins/extension_plugins")
        plugin_manager.add_discovery_path(os.path.join(os.path.expanduser("~"), ".vpa", "plugins"))
        
        # Discover plugins
        await plugin_manager.discover_plugins()
        
        # Load and enable core plugins
        core_plugins = ["time_plugin", "system_plugin", "settings_plugin"]
        for plugin_id in core_plugins:
            await plugin_manager.enable_plugin(plugin_id)
            
        # Load and enable user-enabled plugins
        user_plugins = config_manager.get("enabled_plugins", [])
        for plugin_id in user_plugins:
            await plugin_manager.enable_plugin(plugin_id)
            
    async def shutdown(self):
        """Shutdown the application."""
        # Clean up plugin manager
        await plugin_manager.cleanup()
```

### 6.2 GUI Integration

```python
from vpa.core.plugins import plugin_manager
from vpa.gui.plugin_panel import PluginPanel

class PluginPanel:
    """GUI panel for plugin management."""
    
    async def load_plugins(self):
        """Load plugins into the panel."""
        # Get all discovered plugins
        plugin_info = await plugin_manager.discover_plugins()
        
        # Populate plugin list
        for plugin_id, info in plugin_info.items():
            self._add_plugin_to_list(plugin_id, info)
            
    async def toggle_plugin(self, plugin_id: str, enabled: bool):
        """Toggle a plugin's enabled state."""
        if enabled:
            await plugin_manager.enable_plugin(plugin_id)
        else:
            await plugin_manager.disable_plugin(plugin_id)
            
        # Update config
        enabled_plugins = [pid for pid in plugin_manager._enabled_plugins]
        config_manager.set("enabled_plugins", enabled_plugins)
```

### 6.3 Voice System Integration

```python
from vpa.core.plugins import plugin_manager
from vpa.core.events import event_bus
from vpa.audio.voice_system import voice_system

# Voice system subscribes to plugin events
event_bus.subscribe(
    "plugin_manager.plugin.error",
    lambda e: voice_system.speak(f"Plugin error: {e['error']}"),
    async_callback=False
)

# Process user voice input through plugins
async def process_voice_input(text: str):
    # Create context
    context = {
        "input_type": "voice",
        "timestamp": time.time()
    }
    
    # Process with plugins
    results = await plugin_manager.process_input(text, context)
    
    # Handle results
    for result in results:
        if "error" in result:
            voice_system.speak(f"Error processing command: {result['error']}")
        elif "response" in result.get("result", {}):
            voice_system.speak(result["result"]["response"])
```

## 7. Plugin Testing and Validation

### 7.1 Unit Testing

```python
import pytest
from vpa.core.plugins import Plugin, PluginManager

class TestPlugin(Plugin):
    """Test plugin implementation."""
    
    @property
    def name(self) -> str:
        return "Test Plugin"
        
    def can_handle(self, user_input: str, context: Dict[str, Any]) -> bool:
        return "test" in user_input.lower()
        
    async def process(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"response": "Test successful"}

@pytest.fixture
def plugin_manager():
    """Create a plugin manager for testing."""
    manager = PluginManager()
    yield manager
    asyncio.run(manager.cleanup())

@pytest.mark.asyncio
async def test_plugin_discovery(plugin_manager, tmp_path):
    """Test plugin discovery."""
    # Create a test plugin
    plugin_dir = tmp_path / "test_plugin"
    plugin_dir.mkdir()
    
    # Create plugin manifest
    manifest = {
        "id": "test_plugin",
        "name": "Test Plugin",
        "version": "1.0.0"
    }
    
    with open(plugin_dir / "plugin.json", "w") as f:
        json.dump(manifest, f)
        
    # Create plugin module
    with open(plugin_dir / "plugin.py", "w") as f:
        f.write("""
from vpa.core.plugins import Plugin

class TestPlugin(Plugin):
    @property
    def name(self):
        return "Test Plugin"
        
    def can_handle(self, user_input, context):
        return "test" in user_input.lower()
        
    async def process(self, user_input, context):
        return {"response": "Test successful"}
""")
        
    # Add discovery path
    plugin_manager.add_discovery_path(str(tmp_path))
    
    # Discover plugins
    plugin_info = await plugin_manager.discover_plugins(use_cache=False)
    
    # Check if plugin was discovered
    assert "test_plugin" in plugin_info
    assert plugin_info["test_plugin"]["name"] == "Test Plugin"
```

### 7.2 Integration Testing

```python
@pytest.mark.asyncio
async def test_plugin_lifecycle(plugin_manager):
    """Test plugin lifecycle."""
    # Create a test plugin
    plugin = TestPlugin()
    
    # Mock plugin info
    plugin_manager._plugin_info = {
        "test_plugin": {
            "id": "test_plugin",
            "name": "Test Plugin",
            "version": "1.0.0",
            "dependencies": []
        }
    }
    
    # Add plugin
    plugin_manager._plugins["test_plugin"] = plugin
    
    # Initialize plugin
    success = await plugin_manager.initialize_plugin("test_plugin")
    assert success
    assert plugin_manager.is_plugin_initialized("test_plugin")
    
    # Enable plugin
    success = await plugin_manager.enable_plugin("test_plugin")
    assert success
    assert plugin_manager.is_plugin_enabled("test_plugin")
    
    # Process input
    results = await plugin_manager.process_input("run a test", {})
    assert len(results) == 1
    assert results[0]["plugin"] == "Test Plugin"
    assert results[0]["result"]["response"] == "Test successful"
    
    # Disable plugin
    success = await plugin_manager.disable_plugin("test_plugin")
    assert success
    assert not plugin_manager.is_plugin_enabled("test_plugin")
    
    # Unload plugin
    success = await plugin_manager.unload_plugin("test_plugin")
    assert success
    assert not plugin_manager.is_plugin_loaded("test_plugin")
```

### 7.3 Performance Testing

```python
@pytest.mark.asyncio
async def test_plugin_performance(plugin_manager):
    """Test plugin performance."""
    # Create multiple test plugins
    for i in range(10):
        plugin = TestPlugin()
        plugin_id = f"test_plugin_{i}"
        
        # Add plugin info
        plugin_manager._plugin_info[plugin_id] = {
            "id": plugin_id,
            "name": f"Test Plugin {i}",
            "version": "1.0.0",
            "dependencies": []
        }
        
        # Add plugin
        plugin_manager._plugins[plugin_id] = plugin
        
        # Enable plugin
        await plugin_manager.enable_plugin(plugin_id)
        
    # Measure processing time
    start_time = time.time()
    results = await plugin_manager.process_input("run a test", {})
    end_time = time.time()
    
    # Check performance
    duration = end_time - start_time
    assert duration < 0.1  # Should process in less than 100ms
    assert len(results) == 10
```

## Conclusion

This document provides detailed requirements and implementation guidance for the Plugin Manager System in the VPA project. The Plugin Manager is a core architectural component that enables modular functionality through dynamic plugin discovery, loading, and lifecycle management with strict performance and isolation targets. Implementation follows the architectural principles defined in the project planning documents and ensures a robust foundation for the plugin-based architecture of the VPA system.

---

*Plugin Manager System Requirements completed on August 27, 2025*
