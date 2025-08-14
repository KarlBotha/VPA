"""
Tests for VPA Plugin Error Boundaries and Isolation System.
Comprehensive test coverage for plugin fault tolerance functionality.
"""

import time
import threading
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from vpa.core.plugin_boundaries import (
    PluginState,
    ErrorSeverity,
    PluginError,
    PluginHealth,
    PluginErrorBoundary,
    ExecutionContext,
    PluginWatchdog,
    create_plugin_boundary,
    safe_plugin_execution
)


class TestPluginState:
    """Test cases for PluginState enum."""
    
    def test_plugin_state_values(self):
        """Test plugin state enum values."""
        assert PluginState.HEALTHY.value == "healthy"
        assert PluginState.DEGRADED.value == "degraded"
        assert PluginState.FAILED.value == "failed"
        assert PluginState.DISABLED.value == "disabled"
        assert PluginState.RECOVERING.value == "recovering"


class TestErrorSeverity:
    """Test cases for ErrorSeverity enum."""
    
    def test_error_severity_values(self):
        """Test error severity enum values."""
        assert ErrorSeverity.LOW.value == "low"
        assert ErrorSeverity.MEDIUM.value == "medium"
        assert ErrorSeverity.HIGH.value == "high"
        assert ErrorSeverity.CRITICAL.value == "critical"


class TestPluginError:
    """Test cases for PluginError dataclass."""
    
    def test_plugin_error_creation(self):
        """Test plugin error creation."""
        timestamp = datetime.utcnow()
        error = PluginError(
            plugin_name="test_plugin",
            error_type="ValueError",
            error_message="Test error",
            traceback="Test traceback",
            timestamp=timestamp,
            severity=ErrorSeverity.HIGH,
            context={"key": "value"},
            recovery_attempted=True
        )
        
        assert error.plugin_name == "test_plugin"
        assert error.error_type == "ValueError"
        assert error.error_message == "Test error"
        assert error.traceback == "Test traceback"
        assert error.timestamp == timestamp
        assert error.severity == ErrorSeverity.HIGH
        assert error.context == {"key": "value"}
        assert error.recovery_attempted is True


class TestPluginHealth:
    """Test cases for PluginHealth dataclass."""
    
    def test_plugin_health_creation(self):
        """Test plugin health creation."""
        health = PluginHealth(
            plugin_name="test_plugin",
            state=PluginState.HEALTHY,
            error_count=5,
            success_count=95,
            recovery_attempts=2,
            consecutive_failures=0
        )
        
        assert health.plugin_name == "test_plugin"
        assert health.state == PluginState.HEALTHY
        assert health.error_count == 5
        assert health.success_count == 95
        assert health.recovery_attempts == 2
        assert health.consecutive_failures == 0


class TestPluginErrorBoundary:
    """Test cases for PluginErrorBoundary class."""
    
    def setup_method(self):
        """Setup test environment."""
        self.boundary = PluginErrorBoundary("test_plugin", max_failures=2, recovery_timeout=5)
    
    def test_boundary_initialization(self):
        """Test error boundary initialization."""
        assert self.boundary.plugin_name == "test_plugin"
        assert self.boundary.max_failures == 2
        assert self.boundary.recovery_timeout == 5
        assert self.boundary.health.plugin_name == "test_plugin"
        assert self.boundary.health.state == PluginState.HEALTHY
        assert len(self.boundary.fallback_handlers) == 0
        assert len(self.boundary.recovery_handlers) == 0
    
    def test_register_fallback(self):
        """Test registering fallback handlers."""
        def test_fallback():
            return "fallback_result"
        
        self.boundary.register_fallback("test_method", test_fallback)
        
        assert "test_method" in self.boundary.fallback_handlers
        assert self.boundary.fallback_handlers["test_method"] == test_fallback
    
    def test_register_recovery_handler(self):
        """Test registering recovery handlers."""
        def test_recovery():
            pass
        
        self.boundary.register_recovery_handler(test_recovery)
        
        assert len(self.boundary.recovery_handlers) == 1
        assert self.boundary.recovery_handlers[0] == test_recovery
    
    def test_determine_error_severity_critical(self):
        """Test error severity determination for critical errors."""
        critical_error = SystemExit("Critical error")
        severity = self.boundary._determine_error_severity(critical_error, {})
        assert severity == ErrorSeverity.CRITICAL
    
    def test_determine_error_severity_high(self):
        """Test error severity determination for high severity errors."""
        high_error = TypeError("Type error")
        severity = self.boundary._determine_error_severity(high_error, {})
        assert severity == ErrorSeverity.HIGH
    
    def test_determine_error_severity_medium(self):
        """Test error severity determination for medium severity errors."""
        medium_error = RuntimeError("Runtime error")
        severity = self.boundary._determine_error_severity(medium_error, {})
        assert severity == ErrorSeverity.MEDIUM
    
    def test_determine_error_severity_low(self):
        """Test error severity determination for low severity errors."""
        low_error = Exception("Generic error")
        severity = self.boundary._determine_error_severity(low_error, {})
        assert severity == ErrorSeverity.LOW
    
    def test_record_error_first_failure(self):
        """Test recording the first error."""
        test_error = ValueError("Test error")
        plugin_error = self.boundary._record_error(test_error, {"context": "test"})
        
        assert plugin_error.plugin_name == "test_plugin"
        assert plugin_error.error_type == "ValueError"
        assert plugin_error.error_message == "Test error"
        assert plugin_error.severity == ErrorSeverity.HIGH
        
        assert self.boundary.health.error_count == 1
        assert self.boundary.health.consecutive_failures == 1
        assert self.boundary.health.state == PluginState.HEALTHY  # First error doesn't change state
    
    def test_record_error_multiple_failures(self):
        """Test recording multiple errors leading to degraded state."""
        # First error
        self.boundary._record_error(ValueError("Error 1"))
        assert self.boundary.health.state == PluginState.HEALTHY
        
        # Second error - should become degraded
        self.boundary._record_error(ValueError("Error 2"))
        assert self.boundary.health.state == PluginState.DEGRADED
        assert self.boundary.health.consecutive_failures == 2
    
    def test_record_error_max_failures(self):
        """Test recording errors that exceed max failures."""
        # Record max_failures + 1 errors to exceed the limit
        for i in range(self.boundary.max_failures + 1):
            self.boundary._record_error(ValueError(f"Error {i+1}"))
        
        assert self.boundary.health.state == PluginState.FAILED
        assert self.boundary.health.consecutive_failures == self.boundary.max_failures + 1
        assert self.boundary.health.disabled_until is not None
    
    def test_record_error_critical_severity(self):
        """Test recording critical error immediately disables plugin."""
        critical_error = SystemExit("Critical failure")
        self.boundary._record_error(critical_error)
        
        assert self.boundary.health.state == PluginState.DISABLED
        assert self.boundary.health.disabled_until is not None
    
    def test_record_success(self):
        """Test recording successful operations."""
        # First create some failures
        self.boundary._record_error(ValueError("Error 1"))
        self.boundary._record_error(ValueError("Error 2"))
        assert self.boundary.health.state == PluginState.DEGRADED
        
        # Record success should reset consecutive failures and restore health
        self.boundary._record_success()
        
        assert self.boundary.health.success_count == 1
        assert self.boundary.health.consecutive_failures == 0
        assert self.boundary.health.state == PluginState.HEALTHY
        assert self.boundary.health.last_success is not None
    
    def test_is_plugin_available_healthy(self):
        """Test plugin availability when healthy."""
        assert self.boundary._is_plugin_available() is True
    
    def test_is_plugin_available_degraded(self):
        """Test plugin availability when degraded."""
        self.boundary.health.state = PluginState.DEGRADED
        assert self.boundary._is_plugin_available() is True
    
    def test_is_plugin_available_disabled(self):
        """Test plugin availability when disabled with timeout."""
        self.boundary.health.state = PluginState.DISABLED
        self.boundary.health.disabled_until = datetime.utcnow() + timedelta(seconds=10)
        assert self.boundary._is_plugin_available() is False
    
    def test_is_plugin_available_disabled_timeout_expired(self):
        """Test plugin availability when disabled timeout has expired."""
        self.boundary.health.state = PluginState.DISABLED
        self.boundary.health.disabled_until = datetime.utcnow() - timedelta(seconds=1)
        assert self.boundary._is_plugin_available() is True
        assert self.boundary.health.state == PluginState.RECOVERING
    
    def test_attempt_recovery_success(self):
        """Test successful plugin recovery."""
        def successful_recovery():
            pass  # Successful recovery does nothing
        
        self.boundary.register_recovery_handler(successful_recovery)
        self.boundary.health.state = PluginState.FAILED
        
        result = self.boundary._attempt_recovery()
        
        assert result is True
        assert self.boundary.health.state == PluginState.HEALTHY
        assert self.boundary.health.consecutive_failures == 0
        assert self.boundary.health.disabled_until is None
        assert self.boundary.health.recovery_attempts == 1
    
    def test_attempt_recovery_failure(self):
        """Test failed plugin recovery."""
        def failing_recovery():
            raise RuntimeError("Recovery failed")
        
        self.boundary.register_recovery_handler(failing_recovery)
        self.boundary.health.state = PluginState.FAILED
        
        result = self.boundary._attempt_recovery()
        
        assert result is False
        assert self.boundary.health.state == PluginState.FAILED
        assert self.boundary.health.disabled_until is not None
        assert self.boundary.health.recovery_attempts == 1
    
    def test_execute_context_success(self):
        """Test successful execution with context manager."""
        with self.boundary.execute("test_method") as ctx:
            assert ctx.should_proceed() is True
            ctx.mark_success()
        
        assert self.boundary.health.success_count == 1
        assert self.boundary.health.consecutive_failures == 0
    
    def test_execute_context_with_error(self):
        """Test execution with error using context manager."""
        with self.boundary.execute("test_method") as ctx:
            if ctx.should_proceed():
                raise ValueError("Test error")
        
        assert self.boundary.health.error_count == 1
        assert self.boundary.health.consecutive_failures == 1
    
    def test_execute_context_with_fallback(self):
        """Test execution with fallback handler."""
        def test_fallback():
            return "fallback_result"
        
        self.boundary.register_fallback("test_method", test_fallback)
        
        try:
            with self.boundary.execute("test_method") as ctx:
                if ctx.should_proceed():
                    raise ValueError("Test error")
        except ValueError:
            pass  # Error should be caught and fallback should be available
        
        # The error should be recorded but fallback should be marked for use
        assert self.boundary.health.error_count == 1
    
    def test_execute_context_plugin_unavailable(self):
        """Test execution when plugin is unavailable."""
        # Make plugin unavailable
        self.boundary.health.state = PluginState.DISABLED
        self.boundary.health.disabled_until = datetime.utcnow() + timedelta(seconds=10)
        
        with self.boundary.execute("test_method") as ctx:
            assert ctx.should_proceed() is False
            assert ctx.use_fallback is True
    
    def test_get_health_status(self):
        """Test getting health status."""
        # Modify health state
        self.boundary._record_error(ValueError("Test error"))
        self.boundary._record_success()
        
        health = self.boundary.get_health_status()
        
        assert isinstance(health, PluginHealth)
        assert health.plugin_name == "test_plugin"
        assert health.error_count == 1
        assert health.success_count == 1
        assert health.state == PluginState.HEALTHY
    
    def test_reset_health(self):
        """Test resetting plugin health."""
        # Create some errors first
        self.boundary._record_error(ValueError("Error 1"))
        self.boundary._record_error(ValueError("Error 2"))
        assert self.boundary.health.error_count == 2
        assert len(self.boundary.errors) == 2
        
        self.boundary.reset_health()
        
        assert self.boundary.health.state == PluginState.HEALTHY
        assert self.boundary.health.consecutive_failures == 0
        assert self.boundary.health.disabled_until is None
        assert len(self.boundary.errors) == 0
    
    def test_disable_plugin(self):
        """Test manually disabling plugin."""
        self.boundary.disable_plugin("Manual test disable")
        
        assert self.boundary.health.state == PluginState.DISABLED
        assert self.boundary.health.disabled_until is None  # Indefinite disable


class TestExecutionContext:
    """Test cases for ExecutionContext class."""
    
    def setup_method(self):
        """Setup test environment."""
        self.boundary = PluginErrorBoundary("test_plugin")
        self.context = ExecutionContext(self.boundary, "test_method", {"key": "value"})
    
    def test_execution_context_initialization(self):
        """Test execution context initialization."""
        assert self.context.boundary == self.boundary
        assert self.context.method_name == "test_method"
        assert self.context.context == {"key": "value"}
        assert self.context.success is False
        assert self.context.use_fallback is False
        assert self.context.error is None
    
    def test_mark_success(self):
        """Test marking execution as successful."""
        self.context.mark_success()
        assert self.context.success is True
    
    def test_should_proceed(self):
        """Test should_proceed method."""
        assert self.context.should_proceed() is True
        
        self.context.use_fallback = True
        assert self.context.should_proceed() is False
    
    def test_execute_fallback_success(self):
        """Test executing fallback handler successfully."""
        def test_fallback():
            return "fallback_result"
        
        self.boundary.register_fallback("test_method", test_fallback)
        result = self.context.execute_fallback()
        
        assert result == "fallback_result"
    
    def test_execute_fallback_not_registered(self):
        """Test executing fallback when none is registered."""
        result = self.context.execute_fallback()
        assert result is None
    
    def test_execute_fallback_failure(self):
        """Test executing fallback that raises an exception."""
        def failing_fallback():
            raise RuntimeError("Fallback failed")
        
        self.boundary.register_fallback("test_method", failing_fallback)
        
        try:
            self.context.execute_fallback()
            assert False, "Should have raised exception"
        except RuntimeError as e:
            assert str(e) == "Fallback failed"


class TestPluginWatchdog:
    """Test cases for PluginWatchdog class."""
    
    def setup_method(self):
        """Setup test environment."""
        self.watchdog = PluginWatchdog(check_interval=1, auto_recovery=True)
        self.boundary = PluginErrorBoundary("test_plugin")
    
    def teardown_method(self):
        """Cleanup test environment."""
        if self.watchdog.running:
            self.watchdog.stop_monitoring()
    
    def test_watchdog_initialization(self):
        """Test watchdog initialization."""
        assert self.watchdog.check_interval == 1
        assert self.watchdog.auto_recovery is True
        assert len(self.watchdog.boundaries) == 0
        assert self.watchdog.running is False
        assert self.watchdog._monitor_thread is None
    
    def test_register_plugin(self):
        """Test registering plugin with watchdog."""
        self.watchdog.register_plugin(self.boundary)
        
        assert "test_plugin" in self.watchdog.boundaries
        assert self.watchdog.boundaries["test_plugin"] == self.boundary
    
    def test_unregister_plugin(self):
        """Test unregistering plugin from watchdog."""
        self.watchdog.register_plugin(self.boundary)
        assert "test_plugin" in self.watchdog.boundaries
        
        self.watchdog.unregister_plugin("test_plugin")
        assert "test_plugin" not in self.watchdog.boundaries
    
    def test_unregister_nonexistent_plugin(self):
        """Test unregistering plugin that doesn't exist."""
        # Should not raise exception
        self.watchdog.unregister_plugin("nonexistent")
    
    def test_start_stop_monitoring(self):
        """Test starting and stopping monitoring."""
        assert self.watchdog.running is False
        
        self.watchdog.start_monitoring()
        assert self.watchdog.running is True
        assert self.watchdog._monitor_thread is not None
        assert self.watchdog._monitor_thread.is_alive()
        
        self.watchdog.stop_monitoring()
        assert self.watchdog.running is False
    
    def test_start_monitoring_twice(self):
        """Test starting monitoring when already running."""
        self.watchdog.start_monitoring()
        thread1 = self.watchdog._monitor_thread
        
        self.watchdog.start_monitoring()  # Should not create new thread
        thread2 = self.watchdog._monitor_thread
        
        assert thread1 == thread2
        self.watchdog.stop_monitoring()
    
    def test_get_all_plugin_health(self):
        """Test getting health status for all plugins."""
        boundary1 = PluginErrorBoundary("plugin1")
        boundary2 = PluginErrorBoundary("plugin2")
        
        self.watchdog.register_plugin(boundary1)
        self.watchdog.register_plugin(boundary2)
        
        health_status = self.watchdog.get_all_plugin_health()
        
        assert len(health_status) == 2
        assert "plugin1" in health_status
        assert "plugin2" in health_status
        assert isinstance(health_status["plugin1"], PluginHealth)
        assert isinstance(health_status["plugin2"], PluginHealth)
    
    def test_force_recovery_success(self):
        """Test forcing recovery for a specific plugin."""
        def recovery_handler():
            pass  # Successful recovery
        
        self.boundary.register_recovery_handler(recovery_handler)
        self.boundary.health.state = PluginState.FAILED
        self.watchdog.register_plugin(self.boundary)
        
        result = self.watchdog.force_recovery("test_plugin")
        
        assert result is True
        assert self.boundary.health.state == PluginState.HEALTHY
    
    def test_force_recovery_nonexistent_plugin(self):
        """Test forcing recovery for non-existent plugin."""
        result = self.watchdog.force_recovery("nonexistent")
        assert result is False
    
    def test_monitoring_loop_integration(self):
        """Test monitoring loop with auto-recovery."""
        def recovery_handler():
            pass  # Successful recovery
        
        self.boundary.register_recovery_handler(recovery_handler)
        self.boundary.health.state = PluginState.FAILED
        self.boundary.health.disabled_until = datetime.utcnow() - timedelta(seconds=1)  # Past timeout
        
        self.watchdog.register_plugin(self.boundary)
        self.watchdog.start_monitoring()
        
        # Wait for monitoring loop to run
        time.sleep(1.5)
        
        # Plugin should be recovered
        health = self.boundary.get_health_status()
        assert health.state == PluginState.HEALTHY
        
        self.watchdog.stop_monitoring()


class TestConvenienceFunctions:
    """Test cases for convenience functions."""
    
    def test_create_plugin_boundary(self):
        """Test create_plugin_boundary function."""
        boundary = create_plugin_boundary("test_plugin", max_failures=5, recovery_timeout=30)
        
        assert isinstance(boundary, PluginErrorBoundary)
        assert boundary.plugin_name == "test_plugin"
        assert boundary.max_failures == 5
        assert boundary.recovery_timeout == 30
    
    def test_safe_plugin_execution_decorator_success(self):
        """Test safe_plugin_execution decorator with successful function."""
        boundary = create_plugin_boundary("test_plugin")
        
        @safe_plugin_execution(boundary, "test_method")
        def successful_function(x, y):
            return x + y
        
        result = successful_function(2, 3)
        assert result == 5
        
        health = boundary.get_health_status()
        assert health.success_count == 1
        assert health.error_count == 0
    
    def test_safe_plugin_execution_decorator_failure(self):
        """Test safe_plugin_execution decorator with failing function."""
        boundary = create_plugin_boundary("test_plugin")
        
        def fallback_function():
            return "fallback_result"
        
        boundary.register_fallback("test_method", fallback_function)
        
        @safe_plugin_execution(boundary, "test_method")
        def failing_function():
            raise ValueError("Function failed")
        
        result = failing_function()
        assert result == "fallback_result"
        
        health = boundary.get_health_status()
        assert health.error_count == 1
    
    def test_safe_plugin_execution_decorator_no_fallback(self):
        """Test safe_plugin_execution decorator with failing function and no fallback."""
        boundary = create_plugin_boundary("test_plugin")
        
        @safe_plugin_execution(boundary, "test_method")
        def failing_function():
            raise ValueError("Function failed")
        
        result = failing_function()
        assert result is None  # No fallback registered
        
        health = boundary.get_health_status()
        assert health.error_count == 1


class TestIntegrationScenarios:
    """Integration test scenarios for plugin error boundaries."""
    
    def test_full_plugin_lifecycle_with_errors(self):
        """Test complete plugin lifecycle with errors and recovery."""
        # Create boundary with recovery handler
        boundary = create_plugin_boundary("integration_plugin", max_failures=2)
        
        recovery_called = False
        def recovery_handler():
            nonlocal recovery_called
            recovery_called = True
        
        boundary.register_recovery_handler(recovery_handler)
        
        # Register fallback
        def fallback_operation():
            return "fallback_executed"
        
        boundary.register_fallback("critical_operation", fallback_operation)
        
        # Simulate plugin operations with errors
        with boundary.execute("critical_operation") as ctx:
            if ctx.should_proceed():
                ctx.mark_success()
        
        health = boundary.get_health_status()
        assert health.state == PluginState.HEALTHY
        assert health.success_count == 1
        
        # Cause some failures
        try:
            with boundary.execute("critical_operation") as ctx:
                if ctx.should_proceed():
                    raise RuntimeError("First failure")
        except RuntimeError:
            pass
        
        health = boundary.get_health_status()
        assert health.state == PluginState.HEALTHY  # Still healthy after first failure
        assert health.consecutive_failures == 1
        
        # Second failure should degrade plugin
        try:
            with boundary.execute("critical_operation") as ctx:
                if ctx.should_proceed():
                    raise RuntimeError("Second failure")
        except RuntimeError:
            pass
        
        health = boundary.get_health_status()
        assert health.state == PluginState.DEGRADED
        assert health.consecutive_failures == 2
        
        # Third failure should fail plugin
        try:
            with boundary.execute("critical_operation") as ctx:
                if ctx.should_proceed():
                    raise RuntimeError("Third failure")
        except RuntimeError:
            pass
        
        health = boundary.get_health_status()
        assert health.state == PluginState.FAILED
        assert health.disabled_until is not None
        
        # Attempt recovery
        success = boundary._attempt_recovery()
        assert success is True
        assert recovery_called is True
        
        health = boundary.get_health_status()
        assert health.state == PluginState.HEALTHY
        assert health.consecutive_failures == 0
    
    def test_watchdog_with_multiple_plugins(self):
        """Test watchdog monitoring multiple plugins."""
        watchdog = PluginWatchdog(check_interval=1, auto_recovery=True)
        
        # Create multiple plugins
        plugin1 = create_plugin_boundary("plugin1", max_failures=1)
        plugin2 = create_plugin_boundary("plugin2", max_failures=1)
        
        # Add recovery handlers
        def recovery1():
            pass
        
        def recovery2():
            pass
        
        plugin1.register_recovery_handler(recovery1)
        plugin2.register_recovery_handler(recovery2)
        
        # Register with watchdog
        watchdog.register_plugin(plugin1)
        watchdog.register_plugin(plugin2)
        
        # Fail one plugin
        plugin1._record_error(RuntimeError("Plugin1 failed"))
        plugin1._record_error(RuntimeError("Plugin1 failed again"))
        assert plugin1.get_health_status().state == PluginState.FAILED
        
        # Set recovery timeout in the past
        plugin1.health.disabled_until = datetime.utcnow() - timedelta(seconds=1)
        
        # Start monitoring
        watchdog.start_monitoring()
        
        # Wait for auto-recovery
        time.sleep(1.5)
        
        # Check that plugin1 was recovered
        health1 = plugin1.get_health_status()
        assert health1.state == PluginState.HEALTHY
        
        # Plugin2 should still be healthy
        health2 = plugin2.get_health_status()
        assert health2.state == PluginState.HEALTHY
        
        watchdog.stop_monitoring()
    
    def test_decorator_integration_with_watchdog(self):
        """Test decorator integration with watchdog monitoring."""
        boundary = create_plugin_boundary("decorator_plugin")
        watchdog = PluginWatchdog(check_interval=1)
        watchdog.register_plugin(boundary)
        
        # Register fallback
        def fallback_func():
            return "decorator_fallback"
        
        boundary.register_fallback("decorated_method", fallback_func)
        
        # Create decorated function
        @safe_plugin_execution(boundary, "decorated_method")
        def risky_function(should_fail=False):
            if should_fail:
                raise ValueError("Decorator test failure")
            return "success"
        
        # Test successful execution
        result = risky_function(should_fail=False)
        assert result == "success"
        
        health = boundary.get_health_status()
        assert health.success_count == 1
        assert health.error_count == 0
        
        # Test failure with fallback
        result = risky_function(should_fail=True)
        assert result == "decorator_fallback"
        
        health = boundary.get_health_status()
        assert health.error_count == 1
        
        # Start watchdog monitoring
        watchdog.start_monitoring()
        time.sleep(0.5)  # Let it run briefly
        watchdog.stop_monitoring()
        
        # Verify watchdog tracked the plugin
        all_health = watchdog.get_all_plugin_health()
        assert "decorator_plugin" in all_health
