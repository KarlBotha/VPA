"""
Plugin management system for VPA.
Handles dynamic loading and unloading of plugins.
"""

import os
import sys
import importlib
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from vpa.core.events import EventBus


class PluginManager:
    """Manages plugin loading and lifecycle."""
    
    def __init__(self, event_bus: EventBus):
        """Initialize the plugin manager."""
        self.logger = logging.getLogger(__name__)
        self.event_bus = event_bus
        self.loaded_plugins: Dict[str, Any] = {}
        self.plugins_dir = self._get_plugins_directory()
    
    def _get_plugins_directory(self) -> str:
        """Get the plugins directory path."""
        # Look for plugins in src/vpa/plugins/
        current_dir = Path(__file__).parent.parent
        return str(current_dir / "plugins")
    
    def load_plugins(self, plugin_names: Optional[List[str]] = None) -> None:
        """Load plugins from the plugins directory."""
        self.logger.info("Loading plugins...")
        
        if not os.path.exists(self.plugins_dir):
            self.logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            return
        
        # Add plugins directory to Python path
        if self.plugins_dir not in sys.path:
            sys.path.insert(0, self.plugins_dir)
        
        # Load specific plugins or discover all
        if plugin_names:
            for plugin_name in plugin_names:
                self._load_plugin(plugin_name)
        else:
            self._discover_and_load_plugins()
        
        self.logger.info(f"Loaded {len(self.loaded_plugins)} plugins")
    
    def _discover_and_load_plugins(self) -> None:
        """Discover and load all available plugins."""
        for item in os.listdir(self.plugins_dir):
            plugin_path = os.path.join(self.plugins_dir, item)
            
            # Load Python files as plugins
            if item.endswith('.py') and not item.startswith('__'):
                plugin_name = item[:-3]  # Remove .py extension
                self._load_plugin(plugin_name)
            
            # Load directories with __init__.py as plugins
            elif os.path.isdir(plugin_path) and os.path.exists(os.path.join(plugin_path, '__init__.py')):
                self._load_plugin(item)
    
    def _load_plugin(self, plugin_name: str) -> None:
        """Load a specific plugin."""
        try:
            # Import the plugin module
            module = importlib.import_module(plugin_name)
            
            # Look for plugin class or initialization function
            plugin_instance = None
            if hasattr(module, 'Plugin'):
                plugin_instance = module.Plugin(self.event_bus)
            elif hasattr(module, 'initialize'):
                plugin_instance = module.initialize(self.event_bus)
            
            if plugin_instance:
                self.loaded_plugins[plugin_name] = plugin_instance
                self.logger.info(f"Loaded plugin: {plugin_name}")
                
                # Notify that plugin was loaded
                self.event_bus.emit("plugin.loaded", {"name": plugin_name, "instance": plugin_instance})
            else:
                self.logger.warning(f"No valid plugin interface found in: {plugin_name}")
        
        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
    
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
