"""
VPA Core Application Manager
Main Application Performance Hardening with startup monitoring and resource tracking.
Target: <10 second complete startup sequence with memory usage optimization.
"""

import time
import asyncio
import logging
import signal
import sys
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from .events import PerformanceMonitor, event_bus
from .plugins import plugin_manager


class StartupPhase(Enum):
    """Application startup phases for monitoring."""
    INITIALIZING = "initializing"
    LOADING_PLUGINS = "loading_plugins"  
    CONFIGURING = "configuring"
    STARTING_SERVICES = "starting_services"
    READY = "ready"
    FAILED = "failed"


@dataclass
class ApplicationState:
    """Application state tracking for monitoring and recovery."""
    startup_phase: StartupPhase = StartupPhase.INITIALIZING
    startup_time: float = 0.0
    memory_usage_mb: float = 0.0
    error_count: int = 0
    services_ready: List[str] = None
    last_health_check: float = 0.0
    
    def __post_init__(self):
        if self.services_ready is None:
            self.services_ready = []


class VPAApplication:
    """
    Core VPA application with performance hardening and comprehensive monitoring.
    Ensures <10 second startup with graceful degradation and error recovery.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.state = ApplicationState()
        self.start_time = time.time()
        self._running = False
        self._shutdown_callbacks: List[Callable] = []
        self._health_check_interval = 30.0  # seconds
        self._max_startup_time = 10.0  # seconds
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Subscribe to critical events
        event_bus.subscribe("critical_error", self._handle_critical_error)
        event_bus.subscribe("plugin_load_failed", self._handle_plugin_error)
    
    @PerformanceMonitor.track_execution_time("application_startup")
    async def startup(self) -> bool:
        """Execute complete application startup sequence with monitoring."""
        try:
            self.logger.info("🚀 Starting VPA application...")
            
            # Phase 1: Initialize core systems
            if not await self._initialize_core_systems():
                return False
            
            # Phase 2: Load plugins with timeout protection
            if not await self._load_plugins_with_timeout():
                return False
            
            # Phase 3: Configure application
            if not await self._configure_application():
                return False
            
            # Phase 4: Start services
            if not await self._start_services():
                return False
            
            # Phase 5: Final readiness check
            if not await self._final_readiness_check():
                return False
            
            # Calculate and validate startup time
            self.state.startup_time = time.time() - self.start_time
            self._validate_startup_performance()
            
            self.state.startup_phase = StartupPhase.READY
            self._running = True
            
            # Start background monitoring
            asyncio.create_task(self._health_monitor_loop())
            
            self.logger.info(f"✅ VPA application ready in {self.state.startup_time:.2f}s")
            
            # Emit startup complete event
            await event_bus.emit_async("app_startup_complete", {
                "startup_time": self.state.startup_time,
                "memory_usage": self.state.memory_usage_mb
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Application startup failed: {e}")
            self.state.startup_phase = StartupPhase.FAILED
            self.state.error_count += 1
            return False
    
    async def _initialize_core_systems(self) -> bool:
        """Initialize core system components."""
        self.state.startup_phase = StartupPhase.INITIALIZING
        self.logger.info("Initializing core systems...")
        
        try:
            # Initialize event bus (already done via import)
            # Update memory usage
            memory_info = PerformanceMonitor.monitor_memory_usage()
            self.state.memory_usage_mb = memory_info["memory_mb"]
            
            # Validate memory usage is within limits (<2GB target)
            if self.state.memory_usage_mb > 2048:
                self.logger.warning(f"High memory usage: {self.state.memory_usage_mb:.1f}MB")
            
            self.state.services_ready.append("core_systems")
            return True
            
        except Exception as e:
            self.logger.error(f"Core systems initialization failed: {e}")
            return False
    
    async def _load_plugins_with_timeout(self) -> bool:
        """Load plugins with timeout protection."""
        self.state.startup_phase = StartupPhase.LOADING_PLUGINS
        self.logger.info("Loading plugins...")
        
        try:
            # Set timeout for plugin loading
            plugin_timeout = 5.0  # seconds
            
            # Discover and load plugins with timeout
            await asyncio.wait_for(
                plugin_manager.discover_plugins(use_cache=True),
                timeout=plugin_timeout
            )
            
            # Load priority plugins first
            await asyncio.wait_for(
                plugin_manager.load_all_plugins(),
                timeout=plugin_timeout
            )
            
            plugin_metrics = plugin_manager.get_metrics()
            self.logger.info(f"Loaded {plugin_metrics['plugins_loaded']} plugins")
            
            self.state.services_ready.append("plugins")
            return True
            
        except asyncio.TimeoutError:
            self.logger.error("Plugin loading timeout - continuing with partial load")
            # Graceful degradation: continue with loaded plugins
            self.state.services_ready.append("plugins_partial")
            return True
            
        except Exception as e:
            self.logger.error(f"Plugin loading failed: {e}")
            # Graceful degradation: continue without plugins
            self.state.services_ready.append("plugins_disabled")
            return True
    
    async def _configure_application(self) -> bool:
        """Configure application settings and preferences."""
        self.state.startup_phase = StartupPhase.CONFIGURING
        self.logger.info("Configuring application...")
        
        try:
            # Configuration would go here - placeholder for now
            await asyncio.sleep(0.1)  # Simulate configuration time
            
            self.state.services_ready.append("configuration")
            return True
            
        except Exception as e:
            self.logger.error(f"Application configuration failed: {e}")
            return False
    
    async def _start_services(self) -> bool:
        """Start application services."""
        self.state.startup_phase = StartupPhase.STARTING_SERVICES
        self.logger.info("Starting services...")
        
        try:
            # Service startup would go here - placeholder for now
            services_to_start = ["event_system", "plugin_system", "health_monitor"]
            
            for service in services_to_start:
                await asyncio.sleep(0.05)  # Simulate service startup
                self.state.services_ready.append(service)
                self.logger.debug(f"Service '{service}' started")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Service startup failed: {e}")
            return False
    
    async def _final_readiness_check(self) -> bool:
        """Perform final readiness checks."""
        try:
            # Check memory usage
            memory_info = PerformanceMonitor.monitor_memory_usage()
            self.state.memory_usage_mb = memory_info["memory_mb"]
            
            # Check critical services
            critical_services = ["core_systems", "configuration"]
            for service in critical_services:
                if service not in self.state.services_ready:
                    self.logger.error(f"Critical service '{service}' not ready")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Readiness check failed: {e}")
            return False
    
    def _validate_startup_performance(self) -> None:
        """Validate startup performance against targets."""
        # Check startup time target (<10 seconds)
        if self.state.startup_time < self._max_startup_time:
            self.logger.info(f"🎯 Startup performance target achieved: {self.state.startup_time:.2f}s < {self._max_startup_time}s")
        else:
            self.logger.warning(f"⚠️ Startup performance target missed: {self.state.startup_time:.2f}s > {self._max_startup_time}s")
        
        # Check memory usage target (<2GB)
        memory_target_mb = 2048
        if self.state.memory_usage_mb < memory_target_mb:
            self.logger.info(f"🎯 Memory usage target achieved: {self.state.memory_usage_mb:.1f}MB < {memory_target_mb}MB")
        else:
            self.logger.warning(f"⚠️ Memory usage target missed: {self.state.memory_usage_mb:.1f}MB > {memory_target_mb}MB")
    
    async def _health_monitor_loop(self) -> None:
        """Background health monitoring loop."""
        while self._running:
            try:
                await asyncio.sleep(self._health_check_interval)
                await self._perform_health_check()
            except Exception as e:
                self.logger.error(f"Health check failed: {e}")
    
    async def _perform_health_check(self) -> None:
        """Perform comprehensive health check."""
        try:
            # Update system metrics
            memory_info = PerformanceMonitor.monitor_memory_usage()
            self.state.memory_usage_mb = memory_info["memory_mb"]
            self.state.last_health_check = time.time()
            
            # Get component metrics
            event_metrics = event_bus.get_metrics()
            plugin_metrics = plugin_manager.get_metrics()
            
            # Log health summary
            self.logger.debug(f"Health check: {memory_info['memory_mb']:.1f}MB, "
                            f"{event_metrics['events_dispatched']} events, "
                            f"{plugin_metrics['plugins_loaded']} plugins")
            
            # Emit health status
            await event_bus.emit_async("health_check", {
                "memory_usage_mb": self.state.memory_usage_mb,
                "uptime": time.time() - self.start_time,
                "services_ready": self.state.services_ready,
                "error_count": self.state.error_count
            })
            
        except Exception as e:
            self.logger.error(f"Health check execution failed: {e}")
            self.state.error_count += 1
    
    async def _handle_critical_error(self, event) -> None:
        """Handle critical error events with recovery attempts."""
        error_data = event.data
        self.logger.error(f"Critical error received: {error_data}")
        
        self.state.error_count += 1
        
        # Implement error recovery strategies
        if self.state.error_count > 10:
            self.logger.critical("Too many errors - initiating graceful shutdown")
            await self.shutdown()
    
    async def _handle_plugin_error(self, event) -> None:
        """Handle plugin loading errors with graceful degradation."""
        plugin_data = event.data
        self.logger.warning(f"Plugin error: {plugin_data}")
        
        # Continue with remaining plugins - graceful degradation
    
    def _signal_handler(self, signum, frame) -> None:
        """Handle system signals for graceful shutdown."""
        self.logger.info(f"Received signal {signum} - initiating shutdown")
        asyncio.create_task(self.shutdown())
    
    def add_shutdown_callback(self, callback: Callable) -> None:
        """Add callback to be executed during shutdown."""
        self._shutdown_callbacks.append(callback)
    
    async def shutdown(self) -> None:
        """Graceful application shutdown with cleanup."""
        if not self._running:
            return
        
        self.logger.info("🛑 Shutting down VPA application...")
        self._running = False
        
        try:
            # Execute shutdown callbacks
            for callback in self._shutdown_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback()
                    else:
                        callback()
                except Exception as e:
                    self.logger.error(f"Shutdown callback failed: {e}")
            
            # Emit shutdown event
            await event_bus.emit_async("app_shutdown", {
                "uptime": time.time() - self.start_time,
                "error_count": self.state.error_count
            })
            
            # Cleanup components
            plugin_manager.cleanup_all_plugins()
            event_bus.cleanup()
            
            self.logger.info("✅ VPA application shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown failed: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive application status."""
        return {
            "startup_phase": self.state.startup_phase.value,
            "startup_time": self.state.startup_time,
            "memory_usage_mb": self.state.memory_usage_mb,
            "running": self._running,
            "uptime": time.time() - self.start_time if self._running else 0,
            "error_count": self.state.error_count,
            "services_ready": self.state.services_ready,
            "last_health_check": self.state.last_health_check,
            "performance_targets": {
                "startup_time_target": self._max_startup_time,
                "startup_time_achieved": self.state.startup_time < self._max_startup_time,
                "memory_target_mb": 2048,
                "memory_achieved": self.state.memory_usage_mb < 2048
            }
        }


# Global application instance
app = VPAApplication()