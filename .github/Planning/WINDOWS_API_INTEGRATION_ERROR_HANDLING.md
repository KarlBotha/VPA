# Windows API Integration Error Handling

## Overview

This document extends the Windows API integration documentation with comprehensive error handling guidelines. It defines error categories, recovery strategies, event emission patterns, and implementation examples for robust Windows integration.

## Table of Contents

1. [Error Categories](#1-error-categories)
2. [Recovery Strategies](#2-recovery-strategies)
3. [Event Emission](#3-event-emission)
4. [Implementation Examples](#4-implementation-examples)
5. [Testing Approach](#5-testing-approach)

## 1. Error Categories

Windows API operations can encounter various error types, categorized as follows:

### 1.1 Permission Errors

Errors that occur when the application lacks required permissions:

| Error Type | Description | Common Scenarios | Error Code |
|------------|-------------|-----------------|------------|
| AccessDenied | Operation requires elevated permissions | Registry writes, system settings | 5 |
| UACRequired | User Account Control elevation required | Administrative operations | 740 |
| RestrictedOperation | Operation blocked by system policy | Secure settings, protected paths | Various |

### 1.2 Resource Errors

Errors related to system resources:

| Error Type | Description | Common Scenarios | Error Code |
|------------|-------------|-----------------|------------|
| ResourceBusy | Resource in use by another process | File access, registry keys | 32 |
| ResourceNotFound | Requested resource doesn't exist | Missing files, registry keys | 2 |
| InsufficientResources | System lacks resources for operation | Memory allocation, handles | 8, 14 |

### 1.3 API Errors

Errors specific to Windows API functionality:

| Error Type | Description | Common Scenarios | Error Code |
|------------|-------------|-----------------|------------|
| NotImplemented | API not implemented on this system | API version mismatch | 120 |
| InvalidParameter | Invalid parameters passed to API | Incorrect flags, options | 87 |
| InvalidOperation | Operation not valid in current state | UI manipulation when hidden | Various |
| APIFailure | General API failure | Any Windows API call | Various |

### 1.4 System State Errors

Errors related to system state or configuration:

| Error Type | Description | Common Scenarios | Error Code |
|------------|-------------|-----------------|------------|
| SessionLocked | User session is locked | UI interaction during lock | Various |
| RemoteSession | Operation invalid in remote session | Hardware access in RDP | Various |
| SystemSuspending | System entering low power state | Operations during sleep transition | Various |

## 2. Recovery Strategies

### 2.1 General Recovery Principles

1. **Graceful Degradation**: Fall back to reduced functionality rather than failing completely
2. **User Transparency**: Clearly communicate errors that affect functionality
3. **Automatic Recovery**: Attempt automatic recovery where possible
4. **Persistent Operations**: Save state to retry critical operations later

### 2.2 Strategy by Error Category

#### Permission Errors

| Strategy | Description | When to Apply |
|----------|-------------|--------------|
| Elevation Request | Prompt user for elevation | Critical system operations |
| Fallback Path | Use non-elevated alternative path | When alternative exists |
| Feature Disable | Disable feature requiring elevation | Non-critical features |
| User Guidance | Provide instructions for manual action | Last resort |

#### Resource Errors

| Strategy | Description | When to Apply |
|----------|-------------|--------------|
| Retry Logic | Implement exponential backoff retry | Temporary resource issues |
| Alternative Resource | Use alternative resource | When equivalent exists |
| Resource Creation | Create missing resource if possible | NotFound errors when creatable |
| Reduced Functionality | Operate with limited features | When resource is optional |

#### API Errors

| Strategy | Description | When to Apply |
|----------|-------------|--------------|
| API Version Check | Check and adapt to API version | Platform compatibility issues |
| Parameter Validation | Validate parameters before API calls | Prevent InvalidParameter errors |
| Polyfill | Implement functionality in app code | NotImplemented errors |
| Alternate API | Use alternative API with similar function | When multiple APIs available |

#### System State Errors

| Strategy | Description | When to Apply |
|----------|-------------|--------------|
| State Monitoring | Subscribe to state change notifications | React to system state changes |
| Operation Deferral | Queue operations for better state | Recoverable operations |
| State-Aware Design | Design features to adapt to states | All system state sensitive features |

### 2.3 Decision Flow for Recovery

```
1. Is error transient? 
   → YES: Implement retry with backoff
   → NO: Continue

2. Is there an alternative approach?
   → YES: Switch to alternative
   → NO: Continue
   
3. Is functionality critical?
   → YES: Notify user and guide resolution
   → NO: Degrade gracefully, disable feature

4. Can state be preserved for later retry?
   → YES: Save state and retry on appropriate trigger
   → NO: Log permanent failure
```

## 3. Event Emission

### 3.1 Standard Error Events

All Windows API errors should emit appropriate events through the event bus:

| Event Name | Payload | Purpose |
|------------|---------|---------|
| windows.api.error | `{"component": "component_name", "operation": "operation_name", "error_code": 123, "error_type": "error_category", "message": "Error description", "recoverable": true\|false}` | General API errors |
| windows.permission.error | `{"operation": "operation_name", "required_permission": "permission_name", "elevated": true\|false}` | Permission-related errors |
| windows.resource.error | `{"resource_type": "file\|registry\|handle", "resource_path": "path", "error_code": 123}` | Resource-related errors |
| windows.system.state.changed | `{"new_state": "state_name", "affects_operations": ["operation1", "operation2"]}` | System state changes |

### 3.2 Event Handling Pattern

```python
from vpa.core.events import event_bus
from vpa.core.windows import error_categories

def emit_windows_error(component, operation, error, recoverable=False):
    """Emit standardized Windows API error event"""
    error_code = getattr(error, "winerror", 0)
    error_type = error_categories.classify_error(error_code)
    
    event_bus.emit("windows.api.error", {
        "component": component,
        "operation": operation,
        "error_code": error_code,
        "error_type": error_type,
        "message": str(error),
        "recoverable": recoverable
    })
    
    # Emit specific category event if classified
    if error_type == "permission":
        event_bus.emit("windows.permission.error", {
            "operation": operation,
            "required_permission": error_categories.get_required_permission(error_code),
            "elevated": error_categories.requires_elevation(error_code)
        })
    
    return error_type
```

### 3.3 Subscribing to Error Events

```python
@event_bus.subscribe("windows.api.error")
def handle_windows_errors(event_data):
    """Central handler for Windows API errors"""
    component = event_data.get("component")
    operation = event_data.get("operation")
    error_type = event_data.get("error_type")
    
    # Log all Windows API errors
    logger.error(f"Windows API error in {component}.{operation}: {event_data.get('message')}")
    
    # Handle different error types
    if error_type == "permission" and event_data.get("recoverable"):
        # Show elevation dialog for recoverable permission errors
        show_elevation_dialog(operation)
    elif error_type == "resource" and operation == "startup_task":
        # Handle startup task resource errors specially
        handle_startup_task_failure()
```

## 4. Implementation Examples

### 4.1 Registry Operations with Error Handling

```python
from vpa.core.windows import registry
from vpa.core.events import event_bus
import winreg

def set_run_at_startup(enable=True, app_name="VPA Assistant", executable_path=None):
    """Set or remove application from Windows startup with robust error handling"""
    try:
        if enable:
            if not executable_path:
                executable_path = sys.executable
            
            # Try to set registry key
            registry.set_value(
                registry.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                app_name,
                executable_path
            )
            return True
        else:
            # Try to remove registry key
            registry.delete_value(
                registry.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                app_name
            )
            return True
    
    except registry.RegistryPermissionError as e:
        # Handle permission error
        error_type = emit_windows_error("registry", "set_run_at_startup", e, recoverable=True)
        
        # Try alternative approach using task scheduler
        try:
            if enable:
                create_startup_task(app_name, executable_path)
            else:
                delete_startup_task(app_name)
            return True
        except Exception as alt_e:
            emit_windows_error("task_scheduler", "startup_task", alt_e)
            return False
    
    except registry.RegistryError as e:
        # General registry error
        emit_windows_error("registry", "set_run_at_startup", e)
        return False
```

### 4.2 Notification Display with Error Handling

```python
from vpa.core.windows import notification
from vpa.core.events import event_bus

async def show_toast_notification(title, message, duration=5):
    """Show Windows toast notification with error handling"""
    try:
        # Try to show notification
        notification.show_toast(
            title=title,
            message=message,
            duration=duration
        )
        return True
        
    except notification.NotificationError as e:
        # Check specific error type
        if "disabled" in str(e).lower():
            # Notifications disabled in Windows settings
            error_type = emit_windows_error("notification", "show_toast", e)
            
            # Update application state
            event_bus.emit("notification.state.changed", {
                "available": False,
                "reason": "disabled_in_settings"
            })
            
            # Fallback to in-app notification
            event_bus.emit("ui.notification", {
                "title": title,
                "message": message,
                "duration": duration
            })
            
            return False
            
        elif "focus" in str(e).lower():
            # Focus-related error (transient)
            error_type = emit_windows_error("notification", "show_toast", e, recoverable=True)
            
            # Queue for retry
            notification.queue_notification(title, message, duration)
            return False
            
        else:
            # Other notification error
            error_type = emit_windows_error("notification", "show_toast", e)
            
            # Fallback to in-app notification
            event_bus.emit("ui.notification", {
                "title": title,
                "message": message,
                "duration": duration
            })
            
            return False
```

### 4.3 System Tray Integration with Error Handling

```python
from vpa.core.windows import system_tray
from vpa.core.events import event_bus

class SystemTrayManager:
    """Manager for system tray integration with error handling"""
    
    def __init__(self):
        self.icon_path = None
        self.tooltip = "VPA Assistant"
        self.tray_icon = None
        self.menu_items = []
        self.error_state = False
        
    def initialize(self, icon_path, tooltip=None):
        """Initialize system tray with error handling"""
        self.icon_path = icon_path
        if tooltip:
            self.tooltip = tooltip
            
        try:
            # Create tray icon
            self.tray_icon = system_tray.create_tray_icon(
                icon_path=self.icon_path,
                tooltip=self.tooltip
            )
            
            # Add default menu items
            self._add_default_menu_items()
            self.error_state = False
            return True
            
        except system_tray.IconError as e:
            # Icon-specific error
            error_type = emit_windows_error("system_tray", "create_tray_icon", e)
            
            if "file" in str(e).lower():
                # Try with default icon
                try:
                    default_icon = system_tray.get_default_icon()
                    self.tray_icon = system_tray.create_tray_icon(
                        icon_path=default_icon,
                        tooltip=self.tooltip
                    )
                    self._add_default_menu_items()
                    
                    # Report fallback
                    event_bus.emit("system_tray.fallback_icon", {})
                    self.error_state = False
                    return True
                except Exception as fallback_e:
                    emit_windows_error("system_tray", "fallback_icon", fallback_e)
                    self.error_state = True
                    return False
            else:
                self.error_state = True
                return False
                
        except system_tray.SystemTrayError as e:
            # General system tray error
            error_type = emit_windows_error("system_tray", "initialize", e)
            
            # Check if system tray is available at all
            if not system_tray.is_available():
                event_bus.emit("system_tray.unavailable", {})
                
            self.error_state = True
            return False
    
    def add_menu_item(self, label, callback):
        """Add menu item with error handling"""
        if self.error_state or not self.tray_icon:
            # System tray in error state, store for later recovery
            self.menu_items.append((label, callback))
            return False
            
        try:
            # Add menu item
            system_tray.add_menu_item(
                tray_icon=self.tray_icon,
                label=label,
                callback=callback
            )
            return True
            
        except system_tray.MenuError as e:
            error_type = emit_windows_error("system_tray", "add_menu_item", e)
            
            # Store item for recovery
            self.menu_items.append((label, callback))
            return False
    
    def recover(self):
        """Try to recover system tray after error"""
        if not self.error_state:
            return True
            
        # Try to initialize again
        success = self.initialize(self.icon_path, self.tooltip)
        
        if success:
            # Re-add stored menu items
            for label, callback in self.menu_items:
                try:
                    system_tray.add_menu_item(
                        tray_icon=self.tray_icon,
                        label=label,
                        callback=callback
                    )
                except Exception:
                    # Ignore individual item errors during recovery
                    pass
                    
            self.error_state = False
            return True
        else:
            return False
            
    def _add_default_menu_items(self):
        """Add default menu items"""
        # Implementation details...
```

## 5. Testing Approach

### 5.1 Error Simulation

```python
class WindowsAPIMock:
    """Mock Windows API for testing error handling"""
    
    def __init__(self, error_mode=None, error_code=None):
        self.error_mode = error_mode
        self.error_code = error_code
        self.calls = []
        
    def registry_set_value(self, key, subkey, name, value):
        """Mock registry set value with error simulation"""
        self.calls.append(("registry_set_value", key, subkey, name, value))
        
        if self.error_mode == "permission":
            e = WindowsError(self.error_code or 5, "Access denied")
            raise registry.RegistryPermissionError(str(e), winreg.HKEY_CURRENT_USER)
        elif self.error_mode == "not_found":
            e = WindowsError(self.error_code or 2, "The system cannot find the file specified")
            raise registry.RegistryError(str(e))
        
        return True
        
    def show_notification(self, title, message, duration):
        """Mock notification with error simulation"""
        self.calls.append(("show_notification", title, message, duration))
        
        if self.error_mode == "disabled":
            e = Exception("Notifications are disabled in Windows settings")
            raise notification.NotificationError(str(e))
            
        return True
```

### 5.2 Testing Recovery Strategies

```python
import pytest

def test_registry_permission_error_recovery(monkeypatch):
    """Test registry permission error recovery strategy"""
    # Setup mocks
    windows_mock = WindowsAPIMock(error_mode="permission")
    event_bus_mock = EventBusMock()
    
    monkeypatch.setattr("vpa.core.windows.registry.set_value", windows_mock.registry_set_value)
    monkeypatch.setattr("vpa.core.events.event_bus.emit", event_bus_mock.emit)
    
    # Alternative approach mock
    def mock_create_startup_task(name, path):
        windows_mock.calls.append(("create_startup_task", name, path))
        return True
        
    monkeypatch.setattr("vpa.core.windows.tasks.create_startup_task", mock_create_startup_task)
    
    # Test function with error handling
    result = set_run_at_startup(True, "Test App", "C:\\test.exe")
    
    # Verify behavior
    assert result is True  # Alternative approach succeeded
    assert len(windows_mock.calls) == 2  # Original call + alternative
    assert windows_mock.calls[0][0] == "registry_set_value"
    assert windows_mock.calls[1][0] == "create_startup_task"
    
    # Verify error was emitted
    assert len(event_bus_mock.events) == 1
    assert event_bus_mock.events[0][0] == "windows.api.error"
    assert event_bus_mock.events[0][1]["error_type"] == "permission"
```

### 5.3 Comprehensive Error Test Suite

For comprehensive testing, create test cases that:

1. **Simulate each error category** with various error codes
2. **Verify recovery strategies** for each error scenario
3. **Validate event emissions** match expected format and content
4. **Test retry logic** works with appropriate backoff
5. **Confirm UI feedback** appears when needed for user intervention

## Conclusion

This document extends the Windows API integration with comprehensive error handling guidelines. By following these patterns, the VPA application will maintain robust Windows integration even when facing system errors or permission issues.

The categorized approach to error handling, combined with standardized event emission and recovery strategies, ensures consistent behavior across all Windows API interactions.

---

*Windows API Integration Error Handling document created on August 29, 2025*  
*Version: 1.0*  
*Related Documents: VPA_PLANNING_ENHANCEMENT_ANALYSIS.md (v1.0)*
