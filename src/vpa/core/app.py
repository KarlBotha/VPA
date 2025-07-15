"""
Core Application class for VPA.
Manages the main application lifecycle, configuration, and plugin system.
"""

import logging
from typing import Optional
from vpa.core.config import ConfigManager
from vpa.core.events import EventBus
from vpa.core.plugins import PluginManager


class App:
    """Main VPA application class."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the VPA application."""
        self.logger = logging.getLogger(__name__)
        self.config_manager = ConfigManager(config_path)
        self.event_bus = EventBus()
        self.plugin_manager = PluginManager(self.event_bus)
        self._running = False
    
    def initialize(self) -> None:
        """Initialize all application components."""
        self.logger.info("Initializing VPA application...")
        
        # Load configuration
        self.config_manager.load()
        
        # Initialize event system
        self.event_bus.initialize()
        
        # Load plugins
        self.plugin_manager.load_plugins()
        
        self.logger.info("VPA application initialized successfully")
    
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
