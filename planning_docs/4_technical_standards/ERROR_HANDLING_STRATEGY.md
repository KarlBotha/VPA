# VPA Error Handling Strategy

## Overview

This document outlines the comprehensive error handling strategy for the VPA (Virtual Personal Assistant) project. Proper error handling is critical for maintaining system stability, providing a good user experience, and facilitating debugging. The VPA system prioritizes graceful degradation and fault tolerance to ensure the application remains functional even when components fail.

## Key Principles

### 1. Graceful Degradation

The system should continue operating with reduced functionality when non-critical components fail, rather than crashing entirely.

### 2. Error Isolation

Errors should be contained within the component where they occur, preventing cascading failures throughout the system.

### 3. User Transparency

Users should be informed about errors that affect their experience, with appropriate level of detail based on severity.

### 4. Comprehensive Logging

All errors should be logged with sufficient context to facilitate debugging and problem resolution.

### 5. Recovery Mechanisms

The system should attempt to recover from errors when possible, using retry mechanisms, fallbacks, and self-healing techniques.

### 6. Predictable Behavior

Error handling should be consistent across the application, following established patterns.

## Error Categories

Errors in the VPA system are categorized by severity, which determines how they are handled:

### Critical Errors

Critical errors prevent the application from functioning properly and require immediate attention.

**Examples:**
- Failure to initialize core components (Event Bus, Application Manager)
- Database corruption
- Unrecoverable resource exhaustion

**Handling Strategy:**
1. Log error at CRITICAL level with full context
2. Emit `critical_error` event for system-wide notification
3. Attempt emergency resource cleanup
4. Present user with clear error message
5. Gracefully shut down affected components or entire application if necessary
6. Generate error report for debugging

### Standard Errors

Standard errors affect functionality but don't prevent the entire application from working.

**Examples:**
- Plugin loading failures
- Network connectivity issues
- Feature-specific failures

**Handling Strategy:**
1. Log error at ERROR level with context
2. Emit `component_error` event for notification
3. Attempt component-level recovery
4. Degrade functionality gracefully
5. Notify user about limited functionality
6. Implement retry mechanism if appropriate

### Warnings

Conditions that might lead to errors or represent suboptimal operation but don't immediately affect functionality.

**Examples:**
- Performance degradation
- Deprecated feature usage
- Missing optional dependencies

**Handling Strategy:**
1. Log at WARNING level
2. Emit `warning` event
3. Continue operation with possible mitigations
4. Display warning in appropriate admin/debug UI
5. Track warning frequency for trend analysis

### Information and Debug

Non-error conditions that should be logged for debugging purposes.

**Handling Strategy:**
1. Log at INFO or DEBUG level
2. Do not disrupt normal operation
3. Include in verbose logs only

## Implementation Patterns

### Event Bus Error Handling

```python
class EventBus:
    # ...
    
    def emit(self, event_name: str, event_data: Optional[Dict[str, Any]] = None) -> None:
        """Emit an event synchronously."""
        try:
            self._process_event(event_name, event_data or {})
        except Exception as e:
            self._logger.error(f"Error emitting event '{event_name}': {e}", exc_info=True)
            
    def _process_event(self, event_name: str, event_data: Dict[str, Any]) -> None:
        """Process event handlers synchronously."""
        # Apply middleware
        for middleware in self._middleware:
            try:
                result = middleware(event_name, event_data)
                if result is None:
                    # Event cancelled by middleware
                    return
                event_data = result
            except Exception as e:
                self._logger.error(f"Error in event middleware: {e}", exc_info=True)
                
        # Get handlers (thread-safe)
        handlers = []
        with self._lock:
            handlers = self._handlers.get(event_name, [])[:]
            
        # Call handlers
        for handler in handlers:
            try:
                handler(event_data)
            except Exception as e:
                self._logger.error(f"Error in event handler for '{event_name}': {e}", exc_info=True)
                # Continue processing other handlers despite error
```

### Plugin Error Handling

```python
class PluginManager:
    # ...
    
    async def _safely_call_plugin_method(self, plugin_id: str, method_name: str, *args, **kwargs):
        """
        Safely call a plugin method with error handling.
        
        Args:
            plugin_id: Plugin identifier
            method_name: Method to call
            *args, **kwargs: Arguments to pass
            
        Returns:
            Method result or None if error
        """
        plugin = self.plugins.get(plugin_id)
        if not plugin:
            self._logger.warning(f"Plugin {plugin_id} not found")
            return None
        
        method = getattr(plugin, method_name, None)
        if not method:
            self._logger.warning(f"Method {method_name} not found in plugin {plugin_id}")
            return None
        
        try:
            if asyncio.iscoroutinefunction(method):
                return await method(*args, **kwargs)
            else:
                return method(*args, **kwargs)
        except Exception as e:
            # Record error
            self.plugin_errors[plugin_id] = str(e)
            self.plugin_status[plugin_id] = "error"
            
            # Log error
            self._logger.error(f"Error in plugin {plugin_id}.{method_name}: {e}", exc_info=True)
            
            # Emit error event
            await self._event_bus.emit_async("plugin.error", {
                "plugin_id": plugin_id,
                "method": method_name,
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            
            return None
```

### Component Initialization Error Handling

```python
class Application:
    # ...
    
    async def startup(self) -> bool:
        """Start the application and all components."""
        try:
            # Mark as starting
            self._state = "starting"
            self._startup_time = time.time()
            
            # Initialize components with error handling
            components_to_init = [
                ("performance_monitor", self._init_performance_monitoring),
                ("event_bus", self._init_event_bus),
                ("config_manager", self._init_config_manager),
                ("core_components", self._init_core_components),
                ("plugins", self._init_plugins),
                ("gui", self._init_gui)
            ]
            
            for name, init_func in components_to_init:
                try:
                    await init_func()
                except Exception as e:
                    self._logger.critical(f"Failed to initialize {name}: {e}", exc_info=True)
                    
                    # For critical components, fail startup
                    if name in ["event_bus", "config_manager"]:
                        self._state = "error"
                        raise RuntimeError(f"Critical component {name} failed to initialize") from e
                    
                    # For non-critical components, log and continue with degraded functionality
                    self._logger.warning(f"Continuing startup with degraded functionality (without {name})")
                    
                    # Emit component error event if event bus is available
                    if self._event_bus:
                        await self._event_bus.emit_async("app.component_error", {
                            "component": name,
                            "error": str(e),
                            "startup": True
                        })
            
            # Mark as running
            startup_duration = time.time() - self._startup_time
            self._state = "running"
            
            # Emit startup complete event
            if self._event_bus:
                await self._event_bus.emit_async("app.startup", {
                    "stage": "complete",
                    "duration": startup_duration
                })
                
            return True
            
        except Exception as e:
            self._logger.critical(f"Application startup failed: {e}", exc_info=True)
            self._state = "error"
            return False
```

### Function-Level Error Handling Pattern

```python
async def perform_operation():
    """Example of function-level error handling."""
    try:
        # Attempt the operation
        result = await do_something_risky()
        return result
    except NetworkError as e:
        # Handle specific error type
        logger.error(f"Network error: {e}")
        
        # Retry with exponential backoff
        for attempt in range(3):
            try:
                await asyncio.sleep(2 ** attempt)
                result = await do_something_risky()
                return result
            except NetworkError as retry_e:
                logger.warning(f"Retry {attempt+1} failed: {retry_e}")
                
        # All retries failed, emit error event and return fallback
        await event_bus.emit_async("operation.failed", {
            "error": str(e),
            "operation": "perform_operation",
            "retry_count": 3
        })
        return get_fallback_result()
        
    except ValueError as e:
        # Handle validation error
        logger.error(f"Validation error: {e}")
        raise OperationError("Invalid input provided") from e
        
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error: {e}", exc_info=True)
        
        # Report critical unexpected errors
        await event_bus.emit_async("critical_error", {
            "error": str(e),
            "operation": "perform_operation",
            "traceback": traceback.format_exc()
        })
        
        # Re-raise as appropriate error type
        raise OperationError("Operation failed due to unexpected error") from e
```

## Exception Hierarchy

The VPA project implements a custom exception hierarchy to facilitate specific error handling:

```
BaseException
└── Exception
    └── VPAError                    # Base class for all VPA exceptions
        ├── ConfigurationError      # Configuration-related errors
        │   ├── InvalidConfigError  # Invalid configuration values
        │   └── ConfigLoadError     # Error loading configuration
        │
        ├── PluginError             # Plugin-related errors
        │   ├── PluginLoadError     # Error loading plugin
        │   ├── PluginInitError     # Error initializing plugin
        │   ├── PluginDependencyError # Plugin dependency issues
        │   └── PluginNotFoundError # Plugin not found
        │
        ├── EventError              # Event system errors
        │   ├── EventHandlerError   # Error in event handler
        │   └── EventMiddlewareError # Error in event middleware
        │
        ├── AudioError              # Audio system errors
        │   ├── SynthesisError      # Text-to-speech errors
        │   └── RecognitionError    # Speech recognition errors
        │
        ├── NetworkError            # Network-related errors
        │   ├── ConnectionError     # Connection issues
        │   └── TimeoutError        # Network timeout
        │
        ├── GUIError                # GUI-related errors
        │   └── RenderingError      # Error rendering UI
        │
        └── OperationError          # General operation errors
            ├── PermissionError     # Permission issues
            ├── ResourceError       # Resource-related issues
            │   ├── ResourceNotFoundError  # Resource not found
            │   └── ResourceExhaustedError # Resource limit reached
            └── ValidationError     # Input validation errors
```

Example usage:

```python
from vpa.core.exceptions import ConfigurationError, PluginError

def load_plugin_config(plugin_id):
    try:
        config = config_manager.get_plugin_settings(plugin_id)
        if not config:
            raise ConfigurationError(f"Missing configuration for plugin {plugin_id}")
        return config
    except Exception as e:
        raise PluginError(f"Error loading configuration for plugin {plugin_id}") from e
```

## Retry Mechanisms

### Exponential Backoff

For transient errors, especially in network operations, exponential backoff is implemented:

```python
async def operation_with_retry(max_retries=3, base_delay=1.0):
    """Execute operation with exponential backoff retry."""
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                # Calculate backoff delay: base_delay * 2^(attempt-1) + random jitter
                delay = base_delay * (2 ** (attempt - 1)) * (0.9 + 0.2 * random.random())
                logger.info(f"Retry attempt {attempt} after {delay:.2f}s delay")
                await asyncio.sleep(delay)
                
            # Attempt the operation
            result = await perform_operation()
            
            # Operation succeeded
            if attempt > 0:
                logger.info(f"Operation succeeded after {attempt} retries")
                
            return result
            
        except TransientError as e:
            # These errors are expected to be resolved with retries
            logger.warning(f"Transient error (attempt {attempt+1}/{max_retries+1}): {e}")
            last_error = e
            continue
            
        except Exception as e:
            # Non-transient errors should not be retried
            logger.error(f"Non-transient error: {e}")
            raise
            
    # All retries failed
    logger.error(f"Operation failed after {max_retries} retries")
    raise last_error
```

### Circuit Breaker Pattern

For services that might be down or unstable:

```python
class CircuitBreaker:
    """Implements the Circuit Breaker pattern to prevent repeated failures."""
    
    def __init__(self, failure_threshold=5, reset_timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.state = "closed"  # closed = normal, open = failing, half-open = testing
        self.last_failure_time = 0
        self.lock = asyncio.Lock()
        
    async def execute(self, func, *args, **kwargs):
        """Execute function with circuit breaker pattern."""
        async with self.lock:
            # Check if circuit is open (failing)
            if self.state == "open":
                # Check if reset timeout has elapsed
                if time.time() - self.last_failure_time > self.reset_timeout:
                    logger.info("Circuit half-open, attempting reset")
                    self.state = "half-open"
                else:
                    # Circuit is open and timeout hasn't elapsed
                    raise CircuitBreakerOpenError("Circuit breaker is open")
        
        try:
            # Execute the function
            result = await func(*args, **kwargs)
            
            # Success - reset failure count if in half-open state
            async with self.lock:
                if self.state == "half-open":
                    logger.info("Circuit reset successful, closing circuit")
                    self.state = "closed"
                    self.failure_count = 0
                    
            return result
            
        except Exception as e:
            # Failure occurred
            async with self.lock:
                self.last_failure_time = time.time()
                self.failure_count += 1
                
                # Check if failure threshold reached
                if self.state == "closed" and self.failure_count >= self.failure_threshold:
                    logger.warning(f"Circuit opened after {self.failure_count} failures")
                    self.state = "open"
                elif self.state == "half-open":
                    logger.warning("Circuit reset failed, keeping circuit open")
                    self.state = "open"
                    
            # Re-raise the original exception
            raise
```

### Bulkhead Pattern

For isolating failing components:

```python
class Bulkhead:
    """
    Implements the Bulkhead pattern to isolate components.
    Limits concurrent executions to prevent resource exhaustion.
    """
    
    def __init__(self, max_concurrent=10, max_queue=20):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.max_queue = max_queue
        self.queue_size = 0
        self.queue_semaphore = asyncio.Semaphore(max_queue)
        
    async def execute(self, func, *args, **kwargs):
        """Execute function with bulkhead isolation."""
        # Check if queue has space
        if not self.queue_semaphore.acquire(blocking=False):
            raise BulkheadRejectedError("Bulkhead queue full")
            
        self.queue_size += 1
        
        try:
            # Wait for execution slot
            async with self.semaphore:
                # Decrement queue size once execution starts
                self.queue_size -= 1
                self.queue_semaphore.release()
                
                # Execute the function
                return await func(*args, **kwargs)
        except Exception as e:
            # If we haven't decremented queue size yet, do it now
            if self.queue_size > 0:
                self.queue_size -= 1
                self.queue_semaphore.release()
            raise
```

## Logging Strategy

### Log Levels

The VPA system uses standard Python logging levels with clear guidelines:

| Level | Usage |
|-------|-------|
| CRITICAL | Application-breaking issues requiring immediate attention |
| ERROR | Errors affecting functionality that require investigation |
| WARNING | Potential issues or degraded functionality |
| INFO | Regular operational information |
| DEBUG | Detailed information for debugging |

### Structured Logging

All logs include structured context information:

```python
logger.error("Plugin initialization failed", extra={
    "plugin_id": plugin_id,
    "version": plugin_version,
    "dependencies": plugin_dependencies,
    "error_type": type(error).__name__,
    "traceback": traceback.format_exc()
})
```

### Correlation IDs

For tracking operations across components:

```python
async def process_user_request(user_input, correlation_id=None):
    """Process a user request with correlation ID for tracing."""
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
        
    logger.info(f"Processing user request", extra={
        "correlation_id": correlation_id,
        "user_input": user_input[:100]  # Truncate for privacy
    })
    
    try:
        # Pass correlation ID to sub-operations
        intent = await analyze_intent(user_input, correlation_id=correlation_id)
        response = await generate_response(intent, correlation_id=correlation_id)
        return response
    except Exception as e:
        logger.error("Error processing request", extra={
            "correlation_id": correlation_id,
            "error": str(e)
        })
        raise
```

### Log Configuration

Log configuration is centralized and configurable:

```python
def configure_logging():
    """Configure the logging system."""
    # Get log level from config
    log_level_name = config.get_value("app.log_level", "INFO")
    log_level = getattr(logging, log_level_name)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler("logs/vpa.log"),
            logging.StreamHandler()
        ]
    )
    
    # Configure specific loggers
    logging.getLogger("vpa.core").setLevel(log_level)
    
    # Third-party libraries might be too verbose
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
```

## Error Reporting

### User-Facing Errors

Guidelines for presenting errors to users:

1. **Be specific but not technical**: Explain what went wrong in user-friendly terms
2. **Provide next steps**: Tell the user what they can do about the error
3. **Match severity to presentation**: Critical errors are more prominent than warnings
4. **Maintain privacy**: Never expose sensitive information in error messages
5. **Use appropriate UI**: Toast notifications for minor issues, dialogs for critical errors

Example implementation:

```python
async def display_error(error, severity="standard"):
    """Display an error to the user."""
    if severity == "critical":
        # Show modal dialog for critical errors
        await gui.show_error_dialog(
            title="Application Error",
            message=str(error),
            details="The application encountered a problem. Please restart."
        )
    elif severity == "standard":
        # Show toast notification for standard errors
        await gui.show_notification(
            title="Error",
            message=str(error),
            type="error",
            duration=5000
        )
    else:  # warning
        # Show subtle notification for warnings
        await gui.show_notification(
            title="Warning",
            message=str(error),
            type="warning",
            duration=3000
        )
```

### Developer Error Reports

For collecting information to assist with debugging:

```python
async def generate_error_report(error, context=None):
    """Generate a detailed error report for developers."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
        "system_info": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "vpa_version": app.version,
            "memory_usage": get_memory_usage_mb()
        },
        "app_state": {
            "uptime": get_app_uptime_seconds(),
            "components": list(app.get_components()),
            "active_plugins": list(plugin_manager.get_active_plugins())
        }
    }
    
    # Add context if provided
    if context:
        report["context"] = context
        
    # Save to file
    report_path = f"error_reports/error_{int(time.time())}.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
        
    logger.info(f"Error report generated: {report_path}")
    
    # Optionally send report to error tracking service
    if config.get_value("app.error_reporting.enabled", False):
        await send_error_report(report)
        
    return report_path
```

## Error Monitoring

### Tracking Error Frequency

```python
class ErrorTracker:
    """Track error frequency to detect patterns."""
    
    def __init__(self):
        self.error_counts = {}
        self.window_size = 3600  # 1 hour window
        self.error_timestamps = {}
        
    def record_error(self, error_type, context=None):
        """Record an error occurrence."""
        # Initialize if this is a new error type
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
            self.error_timestamps[error_type] = []
            
        # Increment count
        self.error_counts[error_type] += 1
        
        # Add timestamp
        now = time.time()
        self.error_timestamps[error_type].append(now)
        
        # Remove timestamps outside the window
        cutoff = now - self.window_size
        self.error_timestamps[error_type] = [
            t for t in self.error_timestamps[error_type] if t >= cutoff
        ]
        
        # Check for error spikes
        recent_count = len(self.error_timestamps[error_type])
        if recent_count >= 5:
            logger.warning(f"Error spike detected: {error_type} occurred {recent_count} times in the last hour")
            event_bus.emit("error.spike", {
                "error_type": error_type,
                "count": recent_count,
                "window": self.window_size
            })
            
    def get_frequent_errors(self, threshold=5):
        """Get errors occurring above threshold frequency in the window."""
        now = time.time()
        cutoff = now - self.window_size
        
        frequent_errors = {}
        for error_type, timestamps in self.error_timestamps.items():
            # Count timestamps in window
            recent_count = sum(1 for t in timestamps if t >= cutoff)
            if recent_count >= threshold:
                frequent_errors[error_type] = recent_count
                
        return frequent_errors
```

### Health Monitoring

```python
class HealthMonitor:
    """Monitor system health and error rates."""
    
    def __init__(self, event_bus, app):
        self.event_bus = event_bus
        self.app = app
        self.health_metrics = {
            "error_rate": 0,
            "critical_errors": 0,
            "performance_issues": 0,
            "plugin_errors": {},
            "component_status": {}
        }
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        
    async def start_monitoring(self):
        """Start health monitoring."""
        # Subscribe to relevant events
        self.event_bus.subscribe("app.error", self._on_app_error)
        self.event_bus.subscribe("critical_error", self._on_critical_error)
        self.event_bus.subscribe("plugin.error", self._on_plugin_error)
        self.event_bus.subscribe("user.request", self._on_user_request)
        self.event_bus.subscribe("performance.issue", self._on_performance_issue)
        
        # Start periodic health check
        asyncio.create_task(self._periodic_health_check())
        
    async def _periodic_health_check(self):
        """Perform periodic health check."""
        while True:
            await asyncio.sleep(300)  # Check every 5 minutes
            
            # Update health metrics
            self._update_health_metrics()
            
            # Check overall health
            health_status = self._evaluate_health()
            
            # Emit health status event
            await self.event_bus.emit_async("app.health", {
                "status": health_status,
                "metrics": self.health_metrics
            })
            
            # Log health status
            logger.info(f"Health check: {health_status}", extra={
                "metrics": self.health_metrics
            })
            
    def _update_health_metrics(self):
        """Update health metrics."""
        uptime = time.time() - self.start_time
        
        # Calculate error rate (errors per request)
        if self.request_count > 0:
            self.health_metrics["error_rate"] = self.error_count / self.request_count
        else:
            self.health_metrics["error_rate"] = 0
            
        # Get component status
        for component_id, component in self.app._components.items():
            if hasattr(component, "get_status"):
                try:
                    status = component.get_status()
                    self.health_metrics["component_status"][component_id] = status
                except Exception as e:
                    logger.error(f"Error getting status for component {component_id}: {e}")
                    self.health_metrics["component_status"][component_id] = "error"
                    
    def _evaluate_health(self):
        """Evaluate overall system health."""
        if self.health_metrics["critical_errors"] > 0:
            return "critical"
        elif self.health_metrics["error_rate"] > 0.1:  # >10% error rate
            return "unhealthy"
        elif self.health_metrics["error_rate"] > 0.05:  # >5% error rate
            return "degraded"
        elif self.health_metrics["performance_issues"] > 3:
            return "degraded"
        else:
            return "healthy"
            
    # Event handlers
    def _on_app_error(self, event_data):
        self.error_count += 1
        
    def _on_critical_error(self, event_data):
        self.health_metrics["critical_errors"] += 1
        
    def _on_plugin_error(self, event_data):
        plugin_id = event_data.get("plugin_id")
        if plugin_id not in self.health_metrics["plugin_errors"]:
            self.health_metrics["plugin_errors"][plugin_id] = 0
        self.health_metrics["plugin_errors"][plugin_id] += 1
        
    def _on_user_request(self, event_data):
        self.request_count += 1
        
    def _on_performance_issue(self, event_data):
        self.health_metrics["performance_issues"] += 1
```

## Recovery Strategies

### Component Recovery

For restarting failed components:

```python
class ComponentRecovery:
    """Handles recovery of failed components."""
    
    def __init__(self, app, event_bus):
        self.app = app
        self.event_bus = event_bus
        self.recovery_attempts = {}
        self.max_recovery_attempts = 3
        
    async def start(self):
        """Start the recovery manager."""
        # Subscribe to component error events
        self.event_bus.subscribe("app.component_error", self._handle_component_error, async_callback=True)
        
    async def _handle_component_error(self, event_data):
        """Handle component error event."""
        component_id = event_data.get("component")
        error = event_data.get("error")
        
        # Skip if no component ID
        if not component_id:
            return
            
        # Get current recovery attempts
        attempts = self.recovery_attempts.get(component_id, 0)
        
        # Check if max attempts reached
        if attempts >= self.max_recovery_attempts:
            logger.warning(
                f"Component {component_id} failed {attempts} times, no further recovery attempts"
            )
            await self.event_bus.emit_async("app.component_disabled", {
                "component_id": component_id,
                "reason": "max_recovery_attempts_exceeded",
                "attempts": attempts
            })
            return
            
        # Increment attempts
        self.recovery_attempts[component_id] = attempts + 1
        
        # Log recovery attempt
        logger.info(f"Attempting to recover component {component_id} (attempt {attempts + 1}/{self.max_recovery_attempts})")
        
        # Get component recovery method
        recovery_method = getattr(self, f"_recover_{component_id}", self._recover_generic)
        
        # Attempt recovery
        try:
            success = await recovery_method(component_id)
            if success:
                logger.info(f"Successfully recovered component {component_id}")
                
                # Reset recovery attempts on success
                self.recovery_attempts[component_id] = 0
                
                # Emit recovery event
                await self.event_bus.emit_async("app.component_recovered", {
                    "component_id": component_id
                })
            else:
                logger.warning(f"Failed to recover component {component_id}")
        except Exception as e:
            logger.error(f"Error during recovery of component {component_id}: {e}", exc_info=True)
            
    async def _recover_generic(self, component_id):
        """Generic component recovery method."""
        # Get component
        component = self.app.get_component(component_id)
        if not component:
            return False
            
        # Check if component has restart method
        if hasattr(component, "restart"):
            try:
                # Call restart method
                if asyncio.iscoroutinefunction(component.restart):
                    await component.restart()
                else:
                    component.restart()
                return True
            except Exception as e:
                logger.error(f"Error restarting component {component_id}: {e}")
                return False
                
        return False
        
    async def _recover_plugin_manager(self, component_id):
        """Recover plugin manager."""
        plugin_manager = self.app.get_component("plugin_manager")
        if not plugin_manager:
            return False
            
        try:
            # Reload plugins with errors
            reloaded = 0
            for plugin_id, status in plugin_manager.plugin_status.items():
                if status == "error":
                    logger.info(f"Attempting to reload plugin {plugin_id}")
                    success = await plugin_manager.reload_plugin(plugin_id)
                    if success:
                        reloaded += 1
                        
            logger.info(f"Reloaded {reloaded} plugins")
            return reloaded > 0
        except Exception as e:
            logger.error(f"Error recovering plugin manager: {e}")
            return False
```

### Self-Healing Mechanisms

```python
class SelfHealing:
    """Implements self-healing mechanisms."""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.healing_stats = {
            "healed_components": 0,
            "failed_healing_attempts": 0
        }
        
    async def start(self):
        """Start self-healing system."""
        # Subscribe to relevant events
        self.event_bus.subscribe("app.component_error", self._on_component_error, async_callback=True)
        self.event_bus.subscribe("performance.issue", self._on_performance_issue, async_callback=True)
        self.event_bus.subscribe("resource.low", self._on_resource_low, async_callback=True)
        
    async def _on_component_error(self, event_data):
        """Handle component error."""
        component = event_data.get("component")
        error = event_data.get("error")
        
        # Log healing attempt
        logger.info(f"Self-healing: Attempting to heal component {component}")
        
        try:
            # Try component-specific healing
            healing_method = getattr(self, f"_heal_{component}", None)
            if healing_method:
                success = await healing_method(error)
                if success:
                    self.healing_stats["healed_components"] += 1
                    logger.info(f"Self-healing: Successfully healed component {component}")
                    return
                    
            # Generic healing failed
            self.healing_stats["failed_healing_attempts"] += 1
            logger.warning(f"Self-healing: Failed to heal component {component}")
            
        except Exception as e:
            logger.error(f"Error during self-healing of {component}: {e}")
            
    async def _on_performance_issue(self, event_data):
        """Handle performance issue."""
        issue = event_data.get("issue")
        target = event_data.get("target")
        
        logger.info(f"Self-healing: Addressing performance issue with {target}")
        
        try:
            # Performance healing strategies
            if target == "memory":
                await self._heal_memory_usage()
            elif target == "response_time":
                await self._heal_response_time()
        except Exception as e:
            logger.error(f"Error during performance self-healing: {e}")
            
    async def _on_resource_low(self, event_data):
        """Handle low resource situation."""
        resource = event_data.get("resource")
        level = event_data.get("level")
        
        logger.info(f"Self-healing: Addressing low resource {resource} ({level})")
        
        try:
            if resource == "memory":
                await self._heal_memory_usage()
            elif resource == "disk":
                await self._heal_disk_space()
        except Exception as e:
            logger.error(f"Error during resource self-healing: {e}")
            
    # Healing strategies
    
    async def _heal_memory_usage(self):
        """Heal excessive memory usage."""
        # Emit garbage collection request
        await self.event_bus.emit_async("app.gc_request", {})
        
        # Request components to reduce memory
        await self.event_bus.emit_async("app.reduce_memory", {})
        
        # Force Python garbage collection
        import gc
        gc.collect()
        
        # Check result
        memory_before = self._get_memory_usage()
        memory_after = self._get_memory_usage()
        
        return memory_after < memory_before
        
    async def _heal_disk_space(self):
        """Heal low disk space."""
        # Clean temporary files
        temp_dir = self._get_temp_dir()
        files_removed = await self._clean_old_files(temp_dir)
        
        # Clean log files
        log_dir = "logs"
        logs_removed = await self._clean_old_files(log_dir, pattern="*.log", days=7)
        
        return files_removed > 0 or logs_removed > 0
        
    async def _clean_old_files(self, directory, pattern="*", days=1):
        """Clean old files from directory."""
        try:
            count = 0
            cutoff = time.time() - (days * 86400)
            
            for file_path in pathlib.Path(directory).glob(pattern):
                try:
                    if file_path.stat().st_mtime < cutoff:
                        file_path.unlink()
                        count += 1
                except Exception as e:
                    logger.warning(f"Error deleting file {file_path}: {e}")
                    
            logger.info(f"Cleaned {count} files from {directory}")
            return count
        except Exception as e:
            logger.error(f"Error cleaning directory {directory}: {e}")
            return 0
            
    def _get_memory_usage(self):
        """Get current memory usage in MB."""
        import psutil
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
        
    def _get_temp_dir(self):
        """Get temporary directory."""
        return os.path.join("temp")
```

## Error Prevention

### Input Validation

```python
def validate_input(input_data, schema):
    """Validate input against schema."""
    try:
        # Use validation library (e.g., jsonschema, pydantic)
        from jsonschema import validate
        validate(instance=input_data, schema=schema)
        return True, None
    except Exception as e:
        return False, str(e)

# Example usage
async def process_user_settings(settings):
    # Define schema
    schema = {
        "type": "object",
        "properties": {
            "username": {"type": "string", "minLength": 3, "maxLength": 50},
            "volume": {"type": "number", "minimum": 0, "maximum": 100},
            "notifications": {"type": "boolean"}
        },
        "required": ["username"]
    }
    
    # Validate input
    valid, error = validate_input(settings, schema)
    if not valid:
        logger.warning(f"Invalid settings: {error}")
        raise ValidationError(f"Invalid settings: {error}")
        
    # Process valid settings
    return await save_user_settings(settings)
```

### Preconditions and Assertions

```python
def ensure(condition, message):
    """Ensure a condition is true."""
    if not condition:
        raise AssertionError(message)

# Example usage
async def send_notification(user_id, message):
    ensure(user_id, "User ID must be provided")
    ensure(message, "Message must not be empty")
    
    # Get user preferences
    preferences = await get_user_preferences(user_id)
    ensure(preferences, f"User preferences not found for {user_id}")
    
    # Check if notifications enabled
    if not preferences.get("notifications_enabled", True):
        logger.info(f"Notifications disabled for user {user_id}")
        return False
        
    # Send notification
    return await _send_notification_internal(user_id, message)
```

### Pre-emptive Resource Checking

```python
async def check_system_resources():
    """Check system resources before operations."""
    import psutil
    
    # Check memory
    memory = psutil.virtual_memory()
    if memory.available < 500 * 1024 * 1024:  # Less than 500MB available
        logger.warning("Low memory available: {:.1f}MB".format(memory.available / 1024 / 1024))
        await event_bus.emit_async("resource.low", {
            "resource": "memory",
            "available": memory.available,
            "percent": memory.percent
        })
        
    # Check disk space
    disk = psutil.disk_usage(".")
    if disk.free < 1 * 1024 * 1024 * 1024:  # Less than 1GB free
        logger.warning("Low disk space: {:.1f}GB free".format(disk.free / 1024 / 1024 / 1024))
        await event_bus.emit_async("resource.low", {
            "resource": "disk",
            "available": disk.free,
            "percent": disk.percent
        })
        
    # Check CPU load
    cpu_load = psutil.cpu_percent(interval=1)
    if cpu_load > 90:  # >90% CPU usage
        logger.warning(f"High CPU usage: {cpu_load}%")
        await event_bus.emit_async("resource.high", {
            "resource": "cpu",
            "percent": cpu_load
        })
        
    return {
        "memory": {
            "available": memory.available,
            "percent": memory.percent
        },
        "disk": {
            "free": disk.free,
            "percent": disk.percent
        },
        "cpu": {
            "percent": cpu_load
        }
    }
```

## Testing Error Handling

### Unit Testing Error Paths

```python
@pytest.mark.asyncio
async def test_event_bus_handler_error():
    """Test that EventBus handles errors in event handlers."""
    # Create event bus
    event_bus = EventBus()
    
    # Create a handler that raises an exception
    def failing_handler(event_data):
        raise ValueError("Test error")
    
    # Create a second handler that shouldn't be affected
    second_handler_called = False
    def second_handler(event_data):
        nonlocal second_handler_called
        second_handler_called = True
    
    # Subscribe both handlers
    event_bus.subscribe("test.event", failing_handler)
    event_bus.subscribe("test.event", second_handler)
    
    # Emit event and check that the exception doesn't propagate
    # and the second handler is still called
    event_bus.emit("test.event", {"test": "data"})
    
    # Second handler should still be called despite first handler error
    assert second_handler_called == True
```

### Chaos Testing

```python
class ChaosTester:
    """
    Introduces controlled chaos to test error handling.
    Only used in development and testing environments.
    """
    
    def __init__(self, app, event_bus):
        self.app = app
        self.event_bus = event_bus
        self.active = False
        self.failure_rate = 0.05  # 5% failure rate
        self.targets = []
        
    async def start(self, targets=None, failure_rate=0.05):
        """
        Start chaos testing.
        
        Args:
            targets: List of component names to target, or None for all
            failure_rate: Probability of failure (0.0 to 1.0)
        """
        # Only allowed in development
        if config.get_value("app.environment") != "development":
            logger.warning("Chaos testing only allowed in development environment")
            return False
            
        self.failure_rate = failure_rate
        self.targets = targets or []
        self.active = True
        
        # Register monkey patches
        self._patch_components()
        
        logger.warning(
            f"Chaos testing started with {failure_rate*100:.1f}% failure rate"
            f" targeting {', '.join(self.targets) if self.targets else 'all components'}"
        )
        
        return True
        
    def stop(self):
        """Stop chaos testing."""
        if self.active:
            self.active = False
            # Remove patches
            self._unpatch_components()
            logger.info("Chaos testing stopped")
            
    def _should_fail(self):
        """Determine if an operation should fail."""
        if not self.active:
            return False
        return random.random() < self.failure_rate
        
    def _patch_components(self):
        """Patch target components with chaos."""
        # Example: Patch plugin manager
        if not self.targets or "plugin_manager" in self.targets:
            self._patch_plugin_manager()
            
        # Example: Patch event bus
        if not self.targets or "event_bus" in self.targets:
            self._patch_event_bus()
            
    def _unpatch_components(self):
        """Remove patches."""
        # Implementation depends on how patching was done
        pass
        
    def _patch_plugin_manager(self):
        """Add chaos to plugin manager."""
        plugin_manager = self.app.get_component("plugin_manager")
        if not plugin_manager:
            return
            
        # Save original method
        original_load_plugin = plugin_manager.load_plugin
        
        # Replace with chaos version
        async def chaos_load_plugin(plugin_id):
            if self._should_fail():
                logger.info(f"Chaos: Injecting failure in load_plugin({plugin_id})")
                raise RuntimeError(f"Chaos-induced failure loading plugin {plugin_id}")
            return await original_load_plugin(plugin_id)
            
        # Apply patch
        plugin_manager.load_plugin = chaos_load_plugin
        
    def _patch_event_bus(self):
        """Add chaos to event bus."""
        event_bus = self.app.get_component("event_bus")
        if not event_bus:
            return
            
        # Save original method
        original_emit_async = event_bus.emit_async
        
        # Replace with chaos version
        async def chaos_emit_async(event_name, event_data=None):
            if self._should_fail():
                logger.info(f"Chaos: Injecting failure in emit_async({event_name})")
                # Randomly choose between different failure modes
                failure_type = random.choice(["exception", "delay", "success"])
                
                if failure_type == "exception":
                    raise RuntimeError(f"Chaos-induced failure emitting event {event_name}")
                elif failure_type == "delay":
                    # Add significant delay
                    await asyncio.sleep(2.0)
                    
            # Call original if not failing or after delay
            return await original_emit_async(event_name, event_data)
            
        # Apply patch
        event_bus.emit_async = chaos_emit_async
```

## Integration with System Components

### Application Manager Integration

```python
# In Application class
def register_error_handlers(self):
    """Register global error handlers."""
    # Create error manager
    from vpa.core.errors import ErrorManager
    self._error_manager = ErrorManager(self, self._event_bus)
    self.register_component("error_manager", self._error_manager)
    
    # Set up unhandled exception handler
    def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
        logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
        
        # Log critical error
        if self._error_manager:
            asyncio.create_task(self._error_manager.report_critical_error(
                exc_value,
                {"traceback": "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))}
            ))
            
        # Call original handler
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        
    # Register handler
    sys.excepthook = handle_unhandled_exception
```

### Plugin System Integration

```python
# In PluginManager class
async def _handle_plugin_error(self, plugin_id, error, context=None):
    """Handle plugin error."""
    # Record error
    self.plugin_errors[plugin_id] = str(error)
    self.plugin_status[plugin_id] = "error"
    
    # Log error
    self._logger.error(f"Error in plugin {plugin_id}: {error}", exc_info=True)
    
    # Emit error event
    await self._event_bus.emit_async("plugin.error", {
        "plugin_id": plugin_id,
        "error": str(error),
        "context": context or {},
        "traceback": traceback.format_exc()
    })
    
    # Check if this is a critical plugin
    if plugin_id in self.critical_plugins:
        await self._event_bus.emit_async("critical_error", {
            "component": "plugin_manager",
            "plugin_id": plugin_id,
            "error": str(error),
            "message": f"Critical plugin {plugin_id} failed: {error}"
        })
        return
        
    # Attempt recovery for non-critical plugins
    if self._auto_recovery_enabled:
        await self._attempt_plugin_recovery(plugin_id)
```

## Conclusion

A comprehensive error handling strategy is essential for creating a robust, reliable application that can withstand unexpected conditions and continue to function. By implementing the patterns and practices outlined in this document, the VPA system will provide a dependable user experience even when components fail.

The key to effective error handling is planning for failure at all levels of the system, from individual functions to component interactions, and implementing appropriate strategies for detection, isolation, reporting, and recovery.

## See Also

- [Architecture Overview](../1_architecture/ARCHITECTURE_OVERVIEW.md)
- [System Components](../1_architecture/SYSTEM_COMPONENTS.md)
- [Event System Design](../1_architecture/EVENT_SYSTEM_DESIGN.md)
- [Plugin Architecture](../1_architecture/PLUGIN_ARCHITECTURE.md)
- [Core Components](../2_components/CORE_COMPONENTS.md)

---

*Document created: August 29, 2025*  
*Version: 1.0*
