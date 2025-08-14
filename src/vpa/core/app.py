"""
Core Application class for VPA.
Manages the main application lifecycle, configuration, and plugin system.
Performance optimized for Phase 3 requirements.
"""

import logging
import time
from typing import Optional, Dict, Any
from vpa.core.config import ConfigManager
from vpa.core.events import EventBus
from vpa.core.plugins import PluginManager


class App:
    """
    Main VPA application class with performance monitoring.
    
    Provides lifecycle management, configuration handling, and plugin coordination
    with integrated performance metrics and optimization features.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the VPA application with performance tracking."""
        self._init_start_time = time.time()
        self.logger = logging.getLogger(__name__)
        self.config_manager = ConfigManager(config_path)
        self.event_bus = EventBus()
        self.plugin_manager = PluginManager(self.event_bus)
        self._running = False
        self._performance_metrics: Dict[str, Any] = {}
        self._log_performance("app_init", time.time() - self._init_start_time)
    
    def initialize(self) -> None:
        """Initialize all application components with performance tracking."""
        init_start = time.time()
        self.logger.info("Initializing VPA application...")
        
        # Load configuration with timing
        config_start = time.time()
        self.config_manager.load()
        self._log_performance("config_load", time.time() - config_start)
        
        # Initialize event system with timing
        event_start = time.time()
        self.event_bus.initialize()
        self._log_performance("event_bus_init", time.time() - event_start)
        
        # Load plugins with timing
        plugin_start = time.time()
        self.plugin_manager.load_plugins()
        self._log_performance("plugin_load", time.time() - plugin_start)
        
        total_init_time = time.time() - init_start
        self._log_performance("total_init", total_init_time)
        
        self.logger.info(f"VPA application initialized successfully in {total_init_time:.3f}s")
    
    def _log_performance(self, operation: str, duration: float) -> None:
        """Log performance metrics for monitoring and optimization."""
        self._performance_metrics[operation] = duration
        if duration > 0.1:  # Log operations taking more than 100ms
            self.logger.info(f"Performance: {operation} took {duration:.3f}s")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics for monitoring."""
        return self._performance_metrics.copy()
    
    def start(self) -> None:
        """Start the VPA application."""
        if not self._running:
            self.logger.info("Starting VPA application...")
            self._running = True
            self.event_bus.emit("app.started")
    
    def stop(self) -> None:
        """Stop the VPA application."""
        if self._running:
            self.logger.info("Stopping VPA application...")
            self.event_bus.emit("app.stopping")
            self._running = False
            self.plugin_manager.unload_plugins()
            self.logger.info("VPA application stopped")
    
    def is_running(self) -> bool:
        """Check if the application is running."""
        return self._running
