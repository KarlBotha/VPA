"""
VPA Core Plugin System
Plugin Manager Cache Optimization with lazy loading and performance monitoring.
Target: Startup time optimization with cached plugin discovery.
"""

import os
import time
import json
import logging
import asyncio
import importlib
import importlib.util
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from .events import PerformanceMonitor, event_bus


@dataclass
class PluginMetadata:
    """Plugin metadata for efficient caching and discovery."""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str]
    file_path: str
    load_time: Optional[float] = None
    enabled: bool = True
    priority: int = 0


class Plugin(ABC):
    """Base class for all VPA plugins ensuring compartmentalized isolation."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name identifier."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Plugin description."""
        pass
    
    @abstractmethod
    def can_handle(self, user_input: str, context: Dict[str, Any]) -> bool:
        """Determine if this plugin can handle the user input."""
        pass
    
    @abstractmethod
    async def process(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the user input and return a response."""
        pass
    
    def initialize(self) -> None:
        """Initialize plugin - called during load."""
        pass
    
    def cleanup(self) -> None:
        """Cleanup plugin resources - called during unload."""
        pass


class PluginManager:
    """
    High-performance plugin manager with lazy loading and cached discovery.
    Maintains compartmentalized addon isolation with zero direct coupling.
    """
    
    def __init__(self, plugin_paths: List[str] = None):
        self.logger = logging.getLogger(__name__)
        self.plugin_paths = plugin_paths or ["src/plugins", "plugins"]
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_metadata: Dict[str, PluginMetadata] = {}
        self.plugin_cache_file = "plugin_cache.json"
        self.cache_version = "1.0"
        self._load_executor = ThreadPoolExecutor(max_workers=4)
        self._metrics = {
            "plugins_discovered": 0,
            "plugins_loaded": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_load_time": 0.0,
            "average_load_time": 0.0
        }
        
        # Subscribe to cleanup event
        event_bus.subscribe("app_shutdown", self.cleanup_all_plugins)
    
    @PerformanceMonitor.track_execution_time("plugin_discovery")
    async def discover_plugins(self, use_cache: bool = True) -> None:
        """Discover plugins with caching for optimal startup time."""
        start_time = time.perf_counter()
        
        try:
            # Try to load from cache first
            if use_cache and await self._load_from_cache():
                self._metrics["cache_hits"] += 1
                self.logger.info("Plugins loaded from cache successfully")
                return
            
            self._metrics["cache_misses"] += 1
            
            # Discover plugins from file system
            await self._discover_from_filesystem()
            
            # Save to cache for next startup
            await self._save_to_cache()
            
            discovery_time = time.perf_counter() - start_time
            self.logger.info(f"Plugin discovery completed in {discovery_time:.3f}s")
            
        except Exception as e:
            self.logger.error(f"Plugin discovery failed: {e}")
            raise
    
    async def _discover_from_filesystem(self) -> None:
        """Discover plugins from filesystem in parallel."""
        plugin_files = []
        
        # Find all plugin files
        for plugin_path in self.plugin_paths:
            path = Path(plugin_path)
            if path.exists():
                plugin_files.extend(path.rglob("*.py"))
        
        # Process plugin files in parallel
        tasks = []
        for plugin_file in plugin_files:
            task = self._process_plugin_file(plugin_file)
            tasks.append(task)
        
        # Wait for all discovery tasks to complete
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful_discoveries = sum(1 for r in results if not isinstance(r, Exception))
            self._metrics["plugins_discovered"] = successful_discoveries
    
    async def _process_plugin_file(self, plugin_file: Path) -> Optional[PluginMetadata]:
        """Process individual plugin file and extract metadata."""
        try:
            # Read plugin file to extract metadata
            metadata = await self._extract_plugin_metadata(plugin_file)
            if metadata:
                self.plugin_metadata[metadata.name] = metadata
                return metadata
        except Exception as e:
            self.logger.warning(f"Failed to process plugin file {plugin_file}: {e}")
        
        return None
    
    async def _extract_plugin_metadata(self, plugin_file: Path) -> Optional[PluginMetadata]:
        """Extract metadata from plugin file."""
        try:
            # Load module spec
            spec = importlib.util.spec_from_file_location("plugin_temp", plugin_file)
            if not spec or not spec.loader:
                return None
            
            # Load module temporarily to extract metadata
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin classes
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, Plugin) and 
                    attr != Plugin):
                    
                    # Create instance to get metadata
                    instance = attr()
                    return PluginMetadata(
                        name=instance.name,
                        version=instance.version,
                        description=instance.description,
                        author=getattr(instance, 'author', 'Unknown'),
                        dependencies=getattr(instance, 'dependencies', []),
                        file_path=str(plugin_file),
                        enabled=True,
                        priority=getattr(instance, 'priority', 0)
                    )
        
        except Exception as e:
            self.logger.debug(f"Could not extract metadata from {plugin_file}: {e}")
        
        return None
    
    @PerformanceMonitor.track_execution_time("plugin_loading")
    async def load_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Load a specific plugin with performance monitoring."""
        if plugin_name in self.plugins:
            return self.plugins[plugin_name]
        
        if plugin_name not in self.plugin_metadata:
            self.logger.warning(f"Plugin '{plugin_name}' not found in metadata")
            return None
        
        start_time = time.perf_counter()
        
        try:
            metadata = self.plugin_metadata[plugin_name]
            
            # Load the plugin module
            spec = importlib.util.spec_from_file_location(
                plugin_name, metadata.file_path
            )
            if not spec or not spec.loader:
                raise ImportError(f"Could not load plugin spec: {metadata.file_path}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find and instantiate plugin class
            plugin_instance = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, Plugin) and 
                    attr != Plugin):
                    
                    plugin_instance = attr()
                    break
            
            if not plugin_instance:
                raise ValueError(f"No Plugin class found in {metadata.file_path}")
            
            # Initialize plugin
            plugin_instance.initialize()
            
            # Store plugin
            self.plugins[plugin_name] = plugin_instance
            
            # Update metrics
            load_time = time.perf_counter() - start_time
            metadata.load_time = load_time
            self._update_load_metrics(load_time)
            
            # Emit plugin loaded event
            event_bus.emit("plugin_loaded", {
                "plugin_name": plugin_name,
                "load_time": load_time
            })
            
            self.logger.info(f"Plugin '{plugin_name}' loaded successfully in {load_time:.3f}s")
            return plugin_instance
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin '{plugin_name}': {e}")
            return None
    
    async def load_all_plugins(self) -> None:
        """Load all discovered plugins in parallel."""
        start_time = time.perf_counter()
        
        # Sort plugins by priority
        sorted_metadata = sorted(
            self.plugin_metadata.values(),
            key=lambda x: x.priority,
            reverse=True
        )
        
        # Load plugins in parallel batches based on priority
        current_priority = None
        batch = []
        
        for metadata in sorted_metadata:
            if not metadata.enabled:
                continue
                
            if current_priority is not None and metadata.priority != current_priority:
                # Process current batch
                await self._load_plugin_batch(batch)
                batch = []
            
            batch.append(metadata.name)
            current_priority = metadata.priority
        
        # Load final batch
        if batch:
            await self._load_plugin_batch(batch)
        
        total_time = time.perf_counter() - start_time
        self.logger.info(f"All plugins loaded in {total_time:.3f}s")
    
    async def _load_plugin_batch(self, plugin_names: List[str]) -> None:
        """Load a batch of plugins in parallel."""
        tasks = [self.load_plugin(name) for name in plugin_names]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def _update_load_metrics(self, load_time: float) -> None:
        """Update plugin loading metrics."""
        self._metrics["plugins_loaded"] += 1
        self._metrics["total_load_time"] += load_time
        self._metrics["average_load_time"] = (
            self._metrics["total_load_time"] / self._metrics["plugins_loaded"]
        )
    
    async def _load_from_cache(self) -> bool:
        """Load plugin metadata from cache."""
        try:
            if not os.path.exists(self.plugin_cache_file):
                return False
            
            with open(self.plugin_cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Verify cache version
            if cache_data.get("version") != self.cache_version:
                return False
            
            # Load metadata
            for plugin_data in cache_data.get("plugins", []):
                metadata = PluginMetadata(**plugin_data)
                
                # Verify file still exists and hasn't changed
                if (os.path.exists(metadata.file_path) and 
                    os.path.getmtime(metadata.file_path) <= cache_data.get("cache_time", 0)):
                    self.plugin_metadata[metadata.name] = metadata
            
            return len(self.plugin_metadata) > 0
            
        except Exception as e:
            self.logger.debug(f"Failed to load from cache: {e}")
            return False
    
    async def _save_to_cache(self) -> None:
        """Save plugin metadata to cache."""
        try:
            cache_data = {
                "version": self.cache_version,
                "cache_time": time.time(),
                "plugins": [asdict(metadata) for metadata in self.plugin_metadata.values()]
            }
            
            with open(self.plugin_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            self.logger.warning(f"Failed to save cache: {e}")
    
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get a loaded plugin by name."""
        return self.plugins.get(plugin_name)
    
    def get_available_plugins(self) -> List[PluginMetadata]:
        """Get list of all available plugin metadata."""
        return list(self.plugin_metadata.values())
    
    def get_loaded_plugins(self) -> List[Plugin]:
        """Get list of all loaded plugins."""
        return list(self.plugins.values())
    
    async def find_handlers(self, user_input: str, context: Dict[str, Any]) -> List[Plugin]:
        """Find all plugins that can handle the given input."""
        handlers = []
        
        for plugin in self.plugins.values():
            try:
                if plugin.can_handle(user_input, context):
                    handlers.append(plugin)
            except Exception as e:
                self.logger.warning(f"Error checking handler {plugin.name}: {e}")
        
        # Sort by priority if available
        handlers.sort(key=lambda p: getattr(p, 'priority', 0), reverse=True)
        return handlers
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin."""
        if plugin_name not in self.plugins:
            return False
        
        try:
            plugin = self.plugins[plugin_name]
            plugin.cleanup()
            del self.plugins[plugin_name]
            
            # Emit unload event - handle sync context safely
            try:
                event_bus.emit("plugin_unloaded", {"plugin_name": plugin_name})
            except RuntimeError:
                # No event loop - continue without event
                pass
            
            self.logger.info(f"Plugin '{plugin_name}' unloaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unload plugin '{plugin_name}': {e}")
            return False
    
    def cleanup_all_plugins(self) -> None:
        """Cleanup all loaded plugins."""
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)
        
        self._load_executor.shutdown(wait=True)
        self.logger.info("All plugins cleaned up")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get plugin manager performance metrics."""
        memory_info = PerformanceMonitor.monitor_memory_usage()
        return {
            **self._metrics,
            "memory_usage_mb": memory_info["memory_mb"],
            "available_plugins": len(self.plugin_metadata),
            "loaded_plugins": len(self.plugins),
            "plugin_paths": self.plugin_paths
        }


# Global plugin manager instance
plugin_manager = PluginManager()