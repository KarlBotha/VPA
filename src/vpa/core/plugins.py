"""
Plugin management system for VPA.
Handles dynamic loading and unloading of plugins with performance optimization.
"""

import os
import sys
import importlib
import logging
import time
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from vpa.core.events import EventBus


class PluginManager:
    """
    Manages plugin loading and lifecycle with performance optimization.
    
    Features lazy loading, caching, and performance monitoring for efficient
    plugin management in production environments.
    """
    
    def __init__(self, event_bus: EventBus):
        """Initialize the plugin manager with performance tracking."""
        self.logger = logging.getLogger(__name__)
        self.event_bus = event_bus
        self.loaded_plugins: Dict[str, Any] = {}
        self.plugins_dir = self._get_plugins_directory()
        self._plugin_cache: Dict[str, Any] = {}
        self._failed_plugins: Set[str] = set()
        self._load_times: Dict[str, float] = {}
    
    def _get_plugins_directory(self) -> str:
        """Get the plugins directory path with caching."""
        # Look for plugins in src/vpa/plugins/
        current_dir = Path(__file__).parent.parent
        return str(current_dir / "plugins")
    
    def load_plugins(self, plugin_names: Optional[List[str]] = None) -> None:
        """Load plugins from the plugins directory with performance optimization."""
        load_start = time.time()
        self.logger.info("Loading plugins...")
        
        if not os.path.exists(self.plugins_dir):
            self.logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return
        
        # Add plugins directory to Python path (cached check)
        if self.plugins_dir not in sys.path:
            sys.path.insert(0, self.plugins_dir)
        
        # Load specific plugins or discover all
        if plugin_names:
            for plugin_name in plugin_names:
                if plugin_name not in self._failed_plugins:  # Skip known failures
                    self._load_plugin(plugin_name)
        else:
            self._discover_and_load_plugins()
        
        total_time = time.time() - load_start
        self.logger.info(f"Loaded {len(self.loaded_plugins)} plugins in {total_time:.3f}s")
    
    def _discover_and_load_plugins(self) -> None:
        """Discover and load all available plugins with optimization."""
        discovered_plugins = []
        
        # First pass: discover plugins without loading
        for item in os.listdir(self.plugins_dir):
            plugin_path = os.path.join(self.plugins_dir, item)
            
            # Identify Python files as plugins
            if item.endswith('.py') and not item.startswith('__'):
                plugin_name = item[:-3]  # Remove .py extension
                if plugin_name not in self._failed_plugins:
                    discovered_plugins.append(plugin_name)
            # Load directories with __init__.py as plugins
            elif os.path.isdir(plugin_path) and os.path.exists(os.path.join(plugin_path, '__init__.py')):
                if item not in self._failed_plugins:
                    discovered_plugins.append(item)
        
        # Second pass: load plugins with timing
        self.logger.info(f"Discovered {len(discovered_plugins)} plugins")
        for plugin_name in discovered_plugins:
            self._load_plugin(plugin_name)
    
    def _load_plugin(self, plugin_name: str) -> None:
        """Load a specific plugin with performance tracking."""
        load_start = time.time()
        try:
            # Check cache first
            if plugin_name in self._plugin_cache:
                self.loaded_plugins[plugin_name] = self._plugin_cache[plugin_name]
                self.logger.debug(f"Loaded plugin from cache: {plugin_name}")
                return
            
            # Import the plugin module
            module = importlib.import_module(plugin_name)
            
            # Look for plugin class or initialization function
            plugin_instance = None
            if hasattr(module, 'Plugin'):
                plugin_instance = module.Plugin(self.event_bus)
            elif hasattr(module, 'initialize'):
                plugin_instance = module.initialize(self.event_bus)
            
            if plugin_instance:
                # Cache and register plugin
                self._plugin_cache[plugin_name] = plugin_instance
                self.loaded_plugins[plugin_name] = plugin_instance
                
                load_time = time.time() - load_start
                self._load_times[plugin_name] = load_time
                
                self.logger.info(f"Loaded plugin: {plugin_name} ({load_time:.3f}s)")
                
                # Notify that plugin was loaded
                self.event_bus.emit("plugin.loaded", {"name": plugin_name, "instance": plugin_instance})
            else:
                self.logger.warning(f"No valid plugin interface found in: {plugin_name}")
                self._failed_plugins.add(plugin_name)
        
        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            self._failed_plugins.add(plugin_name)
    
    def get_load_times(self) -> Dict[str, float]:
        """Get plugin load times for performance analysis."""
        return self._load_times.copy()
    
    def unload_plugins(self) -> None:
        """Unload all plugins."""
        self.logger.info("Unloading plugins...")
        
        for plugin_name, plugin_instance in self.loaded_plugins.items():
            try:
                # Call cleanup if available
                if hasattr(plugin_instance, 'cleanup'):
                    plugin_instance.cleanup()
                
                self.event_bus.emit("plugin.unloaded", {"name": plugin_name})
                self.logger.info(f"Unloaded plugin: {plugin_name}")
            
            except Exception as e:
                self.logger.error(f"Error unloading plugin {plugin_name}: {e}")
        
        self.loaded_plugins.clear()
    
    def get_plugin(self, plugin_name: str) -> Optional[Any]:
        """Get a loaded plugin instance."""
        return self.loaded_plugins.get(plugin_name)
    
    def list_plugins(self) -> List[str]:
        """List all loaded plugin names."""
        return list(self.loaded_plugins.keys())
