"""
Plugin Error Boundaries and Isolation System for VPA.
Provides fault tolerance, graceful degradation, and plugin watchdog capabilities.
"""

import asyncio
import threading
import time
import traceback
from contextlib import contextmanager
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from vpa.core.logging import get_structured_logger, CorrelationContext


class PluginState(Enum):
    """Plugin execution state."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    DISABLED = "disabled"
    RECOVERING = "recovering"


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PluginError:
    """Plugin error information."""
    plugin_name: str
    error_type: str
    error_message: str
    traceback: str
    timestamp: datetime
    severity: ErrorSeverity
    context: Dict[str, Any] = field(default_factory=dict)
    recovery_attempted: bool = False


@dataclass
class PluginHealth:
    """Plugin health status."""
    plugin_name: str
    state: PluginState
    last_error: Optional[PluginError] = None
    error_count: int = 0
    success_count: int = 0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    recovery_attempts: int = 0
    disabled_until: Optional[datetime] = None
    consecutive_failures: int = 0


class PluginErrorBoundary:
    """
    Error boundary wrapper that isolates plugin execution failures.
    Provides graceful degradation and recovery mechanisms.
    """
    
    def __init__(self, plugin_name: str, max_failures: int = 3, 
                 recovery_timeout: int = 60, circuit_breaker_timeout: int = 300):
        self.plugin_name = plugin_name
        self.max_failures = max_failures
        self.recovery_timeout = recovery_timeout
        self.circuit_breaker_timeout = circuit_breaker_timeout
        
        self.logger = get_structured_logger(__name__, service_name="vpa")
        self.health = PluginHealth(plugin_name, PluginState.HEALTHY)
        self.errors: List[PluginError] = []
        self.fallback_handlers: Dict[str, Callable] = {}
        self.recovery_handlers: List[Callable] = []
        
        self._lock = threading.Lock()
    
    def register_fallback(self, method_name: str, fallback_func: Callable) -> None:
        """
        Register a fallback function for a specific plugin method.
        
        Args:
            method_name: Name of the plugin method
            fallback_func: Function to call when the method fails
        """
        self.fallback_handlers[method_name] = fallback_func
        self.logger.info(f"Registered fallback for {self.plugin_name}.{method_name}",
                        plugin=self.plugin_name, method=method_name, action="register_fallback")
    
    def register_recovery_handler(self, recovery_func: Callable) -> None:
        """
        Register a recovery handler for the plugin.
        
        Args:
            recovery_func: Function to call for plugin recovery
        """
        self.recovery_handlers.append(recovery_func)
        self.logger.info(f"Registered recovery handler for {self.plugin_name}",
                        plugin=self.plugin_name, action="register_recovery")
    
    def _determine_error_severity(self, error: BaseException, context: Dict[str, Any]) -> ErrorSeverity:
        """
        Determine the severity of an error based on its type and context.
        
        Args:
            error: The exception that occurred
            context: Context information about the error
            
        Returns:
            ErrorSeverity level
        """
        # Critical errors that should immediately disable the plugin
        critical_errors = (SystemExit, KeyboardInterrupt, MemoryError, RecursionError)
        if isinstance(error, critical_errors):
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        high_severity_errors = (ImportError, AttributeError, TypeError, ValueError)
        if isinstance(error, high_severity_errors):
            return ErrorSeverity.HIGH
        
        # Medium severity for common runtime errors
        medium_severity_errors = (RuntimeError, OSError, IOError, ConnectionError)
        if isinstance(error, medium_severity_errors):
            return ErrorSeverity.MEDIUM
        
        # Default to low severity
        return ErrorSeverity.LOW
    
    def _record_error(self, error: BaseException, context: Optional[Dict[str, Any]] = None) -> PluginError:
        """
        Record an error and update plugin health status.
        
        Args:
            error: The exception that occurred
            context: Additional context about the error
            
        Returns:
            PluginError object
        """
        with self._lock:
            severity = self._determine_error_severity(error, context or {})
            
            plugin_error = PluginError(
                plugin_name=self.plugin_name,
                error_type=type(error).__name__,
                error_message=str(error),
                traceback=traceback.format_exc(),
                timestamp=datetime.utcnow(),
                severity=severity,
                context=context or {}
            )
            
            self.errors.append(plugin_error)
            self.health.last_error = plugin_error
            self.health.error_count += 1
            self.health.last_failure = datetime.utcnow()
            self.health.consecutive_failures += 1
            
            # Update plugin state based on error severity and frequency
            if severity == ErrorSeverity.CRITICAL:
                self.health.state = PluginState.DISABLED
                self.health.disabled_until = datetime.utcnow() + timedelta(seconds=self.circuit_breaker_timeout)
            elif self.health.consecutive_failures > self.max_failures:
                self.health.state = PluginState.FAILED
                self.health.disabled_until = datetime.utcnow() + timedelta(seconds=self.recovery_timeout)
            elif self.health.consecutive_failures >= self.max_failures:
                self.health.state = PluginState.DEGRADED
            elif self.health.consecutive_failures > 1:
                self.health.state = PluginState.DEGRADED
            
            self.logger.error(f"Plugin error recorded: {self.plugin_name}",
                            plugin=self.plugin_name,
                            error_type=plugin_error.error_type,
                            error_message=plugin_error.error_message,
                            severity=severity.value,
                            consecutive_failures=self.health.consecutive_failures,
                            plugin_state=self.health.state.value)
            
            return plugin_error
    
    def _record_success(self) -> None:
        """Record a successful plugin operation."""
        with self._lock:
            self.health.success_count += 1
            self.health.last_success = datetime.utcnow()
            self.health.consecutive_failures = 0
            
            # Restore health if plugin was degraded
            if self.health.state == PluginState.DEGRADED:
                self.health.state = PluginState.HEALTHY
                self.logger.info(f"Plugin recovered: {self.plugin_name}",
                               plugin=self.plugin_name, action="recovery", state="healthy")
    
    def _is_plugin_available(self) -> bool:
        """
        Check if the plugin is available for execution.
        
        Returns:
            True if plugin can be executed, False otherwise
        """
        with self._lock:
            if self.health.state == PluginState.DISABLED:
                if self.health.disabled_until and datetime.utcnow() < self.health.disabled_until:
                    return False
                else:
                    # Try to recover after timeout
                    self.health.state = PluginState.RECOVERING
                    return True
            
            return self.health.state in [PluginState.HEALTHY, PluginState.DEGRADED, PluginState.RECOVERING]
    
    def _attempt_recovery(self) -> bool:
        """
        Attempt to recover the plugin using registered recovery handlers.
        
        Returns:
            True if recovery was successful, False otherwise
        """
        with self._lock:
            self.health.recovery_attempts += 1
            self.health.state = PluginState.RECOVERING
        
        self.logger.info(f"Attempting plugin recovery: {self.plugin_name}",
                        plugin=self.plugin_name, action="recovery_attempt",
                        attempt=self.health.recovery_attempts)
        
        # Try each recovery handler
        for recovery_handler in self.recovery_handlers:
            try:
                with CorrelationContext():
                    recovery_handler()
                
                with self._lock:
                    self.health.state = PluginState.HEALTHY
                    self.health.consecutive_failures = 0
                    self.health.disabled_until = None
                
                self.logger.info(f"Plugin recovery successful: {self.plugin_name}",
                               plugin=self.plugin_name, action="recovery_success")
                return True
                
            except Exception as recovery_error:
                self.logger.error(f"Recovery handler failed: {self.plugin_name}",
                                plugin=self.plugin_name, 
                                recovery_error=str(recovery_error),
                                action="recovery_failed")
        
        # Recovery failed
        with self._lock:
            self.health.state = PluginState.FAILED
            self.health.disabled_until = datetime.utcnow() + timedelta(seconds=self.recovery_timeout)
        
        return False
    
    @contextmanager
    def execute(self, method_name: str = "unknown", context: Optional[Dict[str, Any]] = None):
        """
        Context manager for safe plugin execution with error boundaries.
        
        Args:
            method_name: Name of the method being executed
            context: Additional context for error reporting
            
        Yields:
            ExecutionContext that can be used to check if execution should proceed
        """
        execution_context = ExecutionContext(self, method_name, context or {})
        
        if not self._is_plugin_available():
            execution_context.use_fallback = True
            self.logger.warning(f"Plugin unavailable, using fallback: {self.plugin_name}",
                              plugin=self.plugin_name, method=method_name,
                              state=self.health.state.value)
        
        try:
            yield execution_context
            
            if execution_context.success:
                self._record_success()
            
        except Exception as error:
            execution_context.error = error
            self._record_error(error, execution_context.context)
            
            # Try fallback if available
            if method_name in self.fallback_handlers:
                execution_context.use_fallback = True
                self.logger.info(f"Using fallback for failed method: {self.plugin_name}.{method_name}",
                               plugin=self.plugin_name, method=method_name)
            # Error boundary suppresses exceptions to allow graceful degradation
    
    def get_health_status(self) -> PluginHealth:
        """
        Get current plugin health status.
        
        Returns:
            PluginHealth object with current status
        """
        with self._lock:
            return PluginHealth(
                plugin_name=self.health.plugin_name,
                state=self.health.state,
                last_error=self.health.last_error,
                error_count=self.health.error_count,
                success_count=self.health.success_count,
                last_success=self.health.last_success,
                last_failure=self.health.last_failure,
                recovery_attempts=self.health.recovery_attempts,
                disabled_until=self.health.disabled_until,
                consecutive_failures=self.health.consecutive_failures
            )
    
    def reset_health(self) -> None:
        """Reset plugin health status to healthy state."""
        with self._lock:
            self.health.state = PluginState.HEALTHY
            self.health.consecutive_failures = 0
            self.health.disabled_until = None
            self.errors.clear()
        
        self.logger.info(f"Plugin health reset: {self.plugin_name}",
                        plugin=self.plugin_name, action="health_reset")
    
    def disable_plugin(self, reason: str = "Manual disable") -> None:
        """
        Manually disable the plugin.
        
        Args:
            reason: Reason for disabling the plugin
        """
        with self._lock:
            self.health.state = PluginState.DISABLED
            self.health.disabled_until = None  # Indefinite disable
        
        self.logger.warning(f"Plugin manually disabled: {self.plugin_name}",
                          plugin=self.plugin_name, reason=reason, action="manual_disable")


class ExecutionContext:
    """Context object for plugin execution within error boundaries."""
    
    def __init__(self, boundary: PluginErrorBoundary, method_name: str, context: Dict[str, Any]):
        self.boundary = boundary
        self.method_name = method_name
        self.context = context
        self.success = False
        self.use_fallback = False
        self.error: Optional[Exception] = None
    
    def mark_success(self) -> None:
        """Mark the execution as successful."""
        self.success = True
    
    def should_proceed(self) -> bool:
        """Check if execution should proceed (plugin is available)."""
        return not self.use_fallback
    
    def execute_fallback(self) -> Any:
        """Execute the fallback handler if available."""
        if self.method_name in self.boundary.fallback_handlers:
            try:
                return self.boundary.fallback_handlers[self.method_name]()
            except Exception as fallback_error:
                self.boundary.logger.error(f"Fallback execution failed: {self.boundary.plugin_name}",
                                         plugin=self.boundary.plugin_name,
                                         method=self.method_name,
                                         fallback_error=str(fallback_error))
                raise
        return None


class PluginWatchdog:
    """
    Watchdog service that monitors plugin health and attempts recovery.
    """
    
    def __init__(self, check_interval: int = 30, auto_recovery: bool = True):
        self.check_interval = check_interval
        self.auto_recovery = auto_recovery
        self.boundaries: Dict[str, PluginErrorBoundary] = {}
        self.logger = get_structured_logger(__name__, service_name="vpa")
        self.running = False
        self._monitor_thread: Optional[threading.Thread] = None
    
    def register_plugin(self, boundary: PluginErrorBoundary) -> None:
        """
        Register a plugin for monitoring.
        
        Args:
            boundary: PluginErrorBoundary instance to monitor
        """
        self.boundaries[boundary.plugin_name] = boundary
        self.logger.info(f"Plugin registered with watchdog: {boundary.plugin_name}",
                        plugin=boundary.plugin_name, action="watchdog_register")
    
    def unregister_plugin(self, plugin_name: str) -> None:
        """
        Unregister a plugin from monitoring.
        
        Args:
            plugin_name: Name of the plugin to unregister
        """
        if plugin_name in self.boundaries:
            del self.boundaries[plugin_name]
            self.logger.info(f"Plugin unregistered from watchdog: {plugin_name}",
                           plugin=plugin_name, action="watchdog_unregister")
    
    def start_monitoring(self) -> None:
        """Start the watchdog monitoring service."""
        if self.running:
            return
        
        self.running = True
        self._monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitor_thread.start()
        
        self.logger.info("Plugin watchdog monitoring started",
                        action="watchdog_start", check_interval=self.check_interval)
    
    def stop_monitoring(self) -> None:
        """Stop the watchdog monitoring service."""
        self.running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5.0)
        
        self.logger.info("Plugin watchdog monitoring stopped", action="watchdog_stop")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop."""
        while self.running:
            try:
                self._check_plugin_health()
                time.sleep(self.check_interval)
            except Exception as error:
                self.logger.error("Watchdog monitoring error", error=str(error))
                time.sleep(self.check_interval)
    
    def _check_plugin_health(self) -> None:
        """Check health of all registered plugins."""
        for plugin_name, boundary in self.boundaries.items():
            try:
                health = boundary.get_health_status()
                
                # Log health status
                self.logger.debug(f"Plugin health check: {plugin_name}",
                                plugin=plugin_name,
                                state=health.state.value,
                                error_count=health.error_count,
                                success_count=health.success_count,
                                consecutive_failures=health.consecutive_failures)
                
                # Attempt auto-recovery for failed plugins
                if (self.auto_recovery and 
                    health.state == PluginState.FAILED and 
                    health.disabled_until and 
                    datetime.utcnow() >= health.disabled_until):
                    
                    self.logger.info(f"Attempting auto-recovery: {plugin_name}",
                                   plugin=plugin_name, action="auto_recovery")
                    boundary._attempt_recovery()
                
            except Exception as check_error:
                self.logger.error(f"Health check failed for plugin: {plugin_name}",
                                plugin=plugin_name, error=str(check_error))
    
    def get_all_plugin_health(self) -> Dict[str, PluginHealth]:
        """
        Get health status for all monitored plugins.
        
        Returns:
            Dictionary mapping plugin names to their health status
        """
        return {name: boundary.get_health_status() 
                for name, boundary in self.boundaries.items()}
    
    def force_recovery(self, plugin_name: str) -> bool:
        """
        Force recovery attempt for a specific plugin.
        
        Args:
            plugin_name: Name of the plugin to recover
            
        Returns:
            True if recovery was successful, False otherwise
        """
        if plugin_name in self.boundaries:
            return self.boundaries[plugin_name]._attempt_recovery()
        return False


# Convenience functions
def create_plugin_boundary(plugin_name: str, **kwargs) -> PluginErrorBoundary:
    """
    Create a new plugin error boundary.
    
    Args:
        plugin_name: Name of the plugin
        **kwargs: Additional configuration options
        
    Returns:
        Configured PluginErrorBoundary instance
    """
    return PluginErrorBoundary(plugin_name, **kwargs)


def safe_plugin_execution(boundary: PluginErrorBoundary, method_name: str = "execute"):
    """
    Decorator for safe plugin method execution.
    
    Args:
        boundary: PluginErrorBoundary to use for protection
        method_name: Name of the method being decorated
        
    Returns:
        Decorated function with error boundary protection
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with boundary.execute(method_name, {"args": args, "kwargs": kwargs}) as ctx:
                if ctx.should_proceed():
                    result = func(*args, **kwargs)
                    ctx.mark_success()
                    return result
                else:
                    # Plugin not available, use fallback
                    return ctx.execute_fallback()
            
            # After context manager, check if we need to use fallback due to error
            if ctx.error is not None:
                return ctx.execute_fallback()
        
        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    # Create error boundary for a plugin
    boundary = create_plugin_boundary("example_plugin", max_failures=2)
    
    # Register fallback handler
    def fallback_operation():
        return "Fallback result"
    
    boundary.register_fallback("risky_operation", fallback_operation)
    
    # Use error boundary in plugin method
    @safe_plugin_execution(boundary, "risky_operation")
    def risky_plugin_method():
        # Simulate a failing operation
        raise RuntimeError("Something went wrong")
    
    # Test the error boundary
    try:
        result = risky_plugin_method()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Check plugin health
    health = boundary.get_health_status()
    print(f"Plugin State: {health.state.value}")
    print(f"Error Count: {health.error_count}")
    
    # Create and start watchdog
    watchdog = PluginWatchdog(check_interval=10)
    watchdog.register_plugin(boundary)
    watchdog.start_monitoring()
    
    # Monitor for a bit then stop
    time.sleep(2)
    watchdog.stop_monitoring()
