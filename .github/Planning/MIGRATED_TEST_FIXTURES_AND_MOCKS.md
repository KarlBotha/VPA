# Test Fixtures and Mocks Specification

## Overview

This document defines standard test fixtures, mocking approaches, and testing patterns for the VPA system. It establishes consistent testing methodologies across all components to ensure robust verification while maintaining the architectural principles of isolation and performance.

## Table of Contents

1. [Test Framework Structure](#1-test-framework-structure)
2. [Mock Components](#2-mock-components)
3. [Test Fixtures](#3-test-fixtures)
4. [Async Testing Patterns](#4-async-testing-patterns)
5. [Performance Testing](#5-performance-testing)
6. [Plugin Testing](#6-plugin-testing)
7. [Windows API Testing](#7-windows-api-testing)

## 1. Test Framework Structure

### 1.1 Directory Structure

```
tests/
├── conftest.py                # Shared fixtures
├── test_core_architecture.py  # Integration tests for core components
├── core/
│   ├── test_app.py            # Application manager tests
│   ├── test_events.py         # Event bus tests
│   ├── test_plugins.py        # Plugin system tests
│   ├── test_settings.py       # Settings system tests
│   └── llm/
│       ├── test_llm_manager.py  # LLM manager tests
│       └── test_adapters.py     # Adapter tests
├── audio/
│   └── test_voice_system.py   # Voice system tests
├── windows/
│   ├── test_registry.py       # Windows registry tests
│   ├── test_notification.py   # Notification tests
│   └── test_system_tray.py    # System tray tests
└── plugins/
    └── test_core_plugins.py   # Core plugin tests
```

### 1.2 Test Configuration

Standard test configuration in `conftest.py`:

```python
import pytest
import asyncio
import logging
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List, Callable

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)

# Shared fixtures
@pytest.fixture
def event_bus_mock():
    """Mock event bus with tracking capabilities"""
    class EventBusMock:
        def __init__(self):
            self.events = []
            self.subscriptions = {}
            
        async def emit_async(self, event_name: str, data: Dict[str, Any] = None):
            """Track emitted events"""
            self.events.append((event_name, data or {}))
            
            # Call any registered handlers
            if event_name in self.subscriptions:
                for handler in self.subscriptions[event_name]:
                    await handler(data or {})
            
            return True
            
        def emit(self, event_name: str, data: Dict[str, Any] = None):
            """Synchronous version"""
            self.events.append((event_name, data or {}))
            return True
            
        def subscribe(self, event_name: str, handler: Callable, async_callback: bool = False):
            """Register a subscription"""
            if event_name not in self.subscriptions:
                self.subscriptions[event_name] = []
            self.subscriptions[event_name].append(handler)
            return True
            
        def get_events(self, event_name: str = None) -> List[tuple]:
            """Get emitted events, optionally filtered by name"""
            if event_name:
                return [e for e in self.events if e[0] == event_name]
            return self.events
            
        def reset(self):
            """Reset tracked events"""
            self.events = []
    
    return EventBusMock()

@pytest.fixture
def settings_mock():
    """Mock settings manager"""
    class SettingsMock:
        def __init__(self):
            self.settings = {}
            self.calls = []
            
        def get(self, path: str, default=None):
            """Get setting with tracking"""
            self.calls.append(("get", path, default))
            if path in self.settings:
                return self.settings[path]
            return default
            
        def set(self, path: str, value):
            """Set setting with tracking"""
            self.calls.append(("set", path, value))
            self.settings[path] = value
            return True
            
        def has(self, path: str) -> bool:
            """Check if setting exists"""
            self.calls.append(("has", path))
            return path in self.settings
            
        def reset_calls(self):
            """Reset tracked calls"""
            self.calls = []
    
    return SettingsMock()
```

## 2. Mock Components

### 2.1 Event Bus Mock

Standard mock implementation for the event bus:

```python
class EventBusMock:
    """Mock event bus with tracking and async support"""
    
    def __init__(self):
        self.events = []
        self.subscriptions = {}
        
    async def emit_async(self, event_name: str, data: Dict[str, Any] = None):
        """Track emitted events"""
        self.events.append((event_name, data or {}))
        
        # Call any registered handlers
        if event_name in self.subscriptions:
            for handler in self.subscriptions[event_name]:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data or {})
                else:
                    handler(data or {})
        
        return True
        
    def emit(self, event_name: str, data: Dict[str, Any] = None):
        """Synchronous version"""
        self.events.append((event_name, data or {}))
        
        # Call synchronous handlers
        if event_name in self.subscriptions:
            for handler in self.subscriptions[event_name]:
                if not asyncio.iscoroutinefunction(handler):
                    handler(data or {})
                    
        return True
        
    def subscribe(self, event_name: str, handler: Callable, async_callback: bool = False):
        """Register a subscription"""
        if event_name not in self.subscriptions:
            self.subscriptions[event_name] = []
        self.subscriptions[event_name].append(handler)
        return True
        
    def get_events(self, event_name: str = None) -> List[tuple]:
        """Get emitted events, optionally filtered by name"""
        if event_name:
            return [e for e in self.events if e[0] == event_name]
        return self.events
        
    def reset(self):
        """Reset tracked events"""
        self.events = []
```

### 2.2 LLM Adapter Mock

Standard mock for LLM adapters:

```python
class LLMAdapterMock:
    """Mock LLM adapter with configurable responses"""
    
    def __init__(self, name="mock_adapter", available_models=None, response_delay=0.1):
        self.name = name
        self._available_models = available_models or [
            {"id": "mock_model", "name": "Mock Model", "provider": name}
        ]
        self.requests = []
        self.initialized = False
        self.response_delay = response_delay
        self.should_fail = False
        self.response_override = None
        
    @property
    def available_models(self):
        return self._available_models
        
    async def initialize(self):
        """Initialize the mock adapter"""
        self.initialized = True
        return True
        
    async def process_request(self, request):
        """Process a request and return mock response"""
        self.requests.append(request)
        
        # Simulate processing delay
        await asyncio.sleep(self.response_delay)
        
        # Handle failure case
        if self.should_fail:
            return {
                "request_id": request.get("request_id", "unknown"),
                "response": None,
                "metadata": {},
                "actions": [],
                "error": {
                    "type": "mock_error",
                    "message": "Mock adapter error",
                    "retry_possible": False
                }
            }
            
        # Use override if available
        if self.response_override:
            return self.response_override
            
        # Default response
        return {
            "request_id": request.get("request_id", "unknown"),
            "response": f"Mock response from {self.name}",
            "metadata": {
                "model": request.get("model", "mock_model"),
                "tokens": {
                    "prompt": 10,
                    "completion": 20,
                    "total": 30
                },
                "processing_time": self.response_delay
            },
            "actions": [],
            "error": None
        }
        
    async def health_check(self):
        """Mock health check"""
        return not self.should_fail
```

### 2.3 Windows API Mock

Standard mock for Windows API components:

```python
class WindowsAPIMock:
    """Mock for Windows API calls"""
    
    def __init__(self, error_mode=None, error_code=None):
        self.error_mode = error_mode  # None, "permission", "not_found", etc.
        self.error_code = error_code
        self.calls = []
        self.registry_data = {}
        
    def registry_set_value(self, key, subkey, name, value):
        """Mock registry set value with error simulation"""
        self.calls.append(("registry_set_value", key, subkey, name, value))
        
        if self.error_mode == "permission":
            e = WindowsError(self.error_code or 5, "Access denied")
            raise registry.RegistryPermissionError(str(e))
        elif self.error_mode == "not_found":
            e = WindowsError(self.error_code or 2, "The system cannot find the file specified")
            raise registry.RegistryError(str(e))
        
        # Store value
        key_path = f"{key}\\{subkey}"
        if key_path not in self.registry_data:
            self.registry_data[key_path] = {}
        self.registry_data[key_path][name] = value
        
        return True
        
    def registry_get_value(self, key, subkey, name):
        """Mock registry get value"""
        self.calls.append(("registry_get_value", key, subkey, name))
        
        if self.error_mode == "not_found":
            e = WindowsError(self.error_code or 2, "The system cannot find the file specified")
            raise registry.RegistryError(str(e))
        
        # Retrieve value
        key_path = f"{key}\\{subkey}"
        if key_path in self.registry_data and name in self.registry_data[key_path]:
            return self.registry_data[key_path][name]
        
        if self.error_mode == "key_not_exist":
            e = WindowsError(self.error_code or 2, "The system cannot find the specified registry key")
            raise registry.RegistryError(str(e))
            
        return None
        
    def show_notification(self, title, message, duration=5):
        """Mock notification with error simulation"""
        self.calls.append(("show_notification", title, message, duration))
        
        if self.error_mode == "disabled":
            e = Exception("Notifications are disabled in Windows settings")
            raise notification.NotificationError(str(e))
            
        return True
        
    def create_tray_icon(self, icon_path, tooltip=None):
        """Mock tray icon creation"""
        self.calls.append(("create_tray_icon", icon_path, tooltip))
        
        if self.error_mode == "icon_error":
            e = Exception("Failed to load icon")
            raise system_tray.IconError(str(e))
            
        # Return mock tray icon object
        return "mock_tray_icon_object"
        
    def add_menu_item(self, tray_icon, label, callback):
        """Mock menu item addition"""
        self.calls.append(("add_menu_item", tray_icon, label))
        
        if self.error_mode == "menu_error":
            e = Exception("Failed to add menu item")
            raise system_tray.MenuError(str(e))
            
        return True
        
    def reset(self):
        """Reset tracking"""
        self.calls = []
        self.registry_data = {}
```

### 2.4 Voice System Mock

Standard mock for the audio system:

```python
class VoiceSystemMock:
    """Mock for voice/audio system"""
    
    def __init__(self, simulate_delay=True):
        self.synthesize_calls = []
        self.simulate_delay = simulate_delay
        self.voices = [
            {"id": f"voice_{i:02d}", "name": f"Voice {i}", "gender": "female" if i % 2 else "male"}
            for i in range(1, 14)  # 13 voices
        ]
        self.error_mode = None
        
    async def synthesize_speech(self, text, voice_id=None, **kwargs):
        """Mock speech synthesis with optional delay"""
        self.synthesize_calls.append((text, voice_id, kwargs))
        
        if self.error_mode == "synthesis_error":
            raise Exception("Speech synthesis failed")
            
        # Simulate realistic delay based on text length
        if self.simulate_delay:
            words = len(text.split())
            delay = min(1.5, words * 0.02)  # ~50 words per second, max 1.5s
            await asyncio.sleep(delay)
            
        return {
            "audio_data": b"mock_audio_data",
            "duration": len(text) * 0.07,  # Rough estimate
            "format": "wav",
            "sample_rate": 44100,
            "voice_id": voice_id or "voice_01"
        }
        
    def get_available_voices(self):
        """Return mock voice catalog"""
        return self.voices
        
    def reset(self):
        """Reset tracking"""
        self.synthesize_calls = []
```

## 3. Test Fixtures

### 3.1 Core Application Fixtures

```python
@pytest.fixture
def app_fixture():
    """Fixture for application manager testing"""
    from vpa.core.app import ApplicationManager
    
    # Create application manager with mock dependencies
    event_bus_mock = MagicMock()
    settings_mock = MagicMock()
    
    app = ApplicationManager(event_bus=event_bus_mock, settings=settings_mock)
    
    yield app
    
    # Cleanup
    if hasattr(app, 'cleanup') and callable(app.cleanup):
        asyncio.run(app.cleanup())

@pytest.fixture
def plugin_manager_fixture():
    """Fixture for plugin manager testing"""
    from vpa.core.plugins import PluginManager
    
    # Create plugin manager with mock dependencies
    event_bus_mock = MagicMock()
    settings_mock = MagicMock()
    
    # Mock settings for plugin paths
    settings_mock.get.return_value = ["test_plugins"]
    
    manager = PluginManager(event_bus=event_bus_mock, settings=settings_mock)
    
    yield manager
    
    # Cleanup
    if hasattr(manager, 'cleanup') and callable(manager.cleanup):
        asyncio.run(manager.cleanup())
```

### 3.2 LLM Integration Fixtures

```python
@pytest.fixture
def llm_manager_fixture(event_bus_mock, settings_mock):
    """Fixture for LLM manager testing with mock adapters"""
    from vpa.core.llm import LLMManager
    
    # Create LLM manager with mock dependencies
    manager = LLMManager()
    
    # Patch dependencies
    with patch('vpa.core.events.event_bus', event_bus_mock), \
         patch('vpa.core.settings.settings_manager', settings_mock):
        
        # Setup mock adapters
        ollama_adapter_mock = LLMAdapterMock(name="ollama")
        llama_adapter_mock = LLMAdapterMock(name="direct")
        
        # Register mock adapters
        manager._register_adapter(ollama_adapter_mock)
        manager._register_adapter(llama_adapter_mock)
        
        yield manager
        
        # Cleanup
        if hasattr(manager, 'cleanup') and callable(manager.cleanup):
            asyncio.run(manager.cleanup())

@pytest.fixture
def ollama_adapter_fixture():
    """Fixture for Ollama adapter testing"""
    adapter = LLMAdapterMock(name="ollama", available_models=[
        {"id": "llama3", "name": "Llama 3", "provider": "ollama"},
        {"id": "codellama", "name": "CodeLlama", "provider": "ollama"}
    ])
    
    yield adapter
```

### 3.3 Windows Integration Fixtures

```python
@pytest.fixture
def windows_registry_fixture():
    """Fixture for Windows registry testing"""
    mock = WindowsAPIMock()
    
    with patch('vpa.core.windows.registry.set_value', mock.registry_set_value), \
         patch('vpa.core.windows.registry.get_value', mock.registry_get_value):
        
        yield mock

@pytest.fixture
def windows_notification_fixture():
    """Fixture for Windows notification testing"""
    mock = WindowsAPIMock()
    
    with patch('vpa.core.windows.notification.show_toast', mock.show_notification):
        yield mock

@pytest.fixture
def windows_tray_fixture():
    """Fixture for Windows system tray testing"""
    mock = WindowsAPIMock()
    
    with patch('vpa.core.windows.system_tray.create_tray_icon', mock.create_tray_icon), \
         patch('vpa.core.windows.system_tray.add_menu_item', mock.add_menu_item):
        
        yield mock
```

## 4. Async Testing Patterns

### 4.1 Standard Async Test Pattern

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    """Test pattern for async functions"""
    # Setup
    mock_dependencies = setup_mocks()
    
    # Execute async function
    result = await function_to_test(mock_dependencies)
    
    # Assert results
    assert result == expected_result
    
    # Assert side effects (e.g., events emitted)
    assert mock_dependencies.event_called_with(expected_args)
```

### 4.2 Event-Based Testing Pattern

```python
@pytest.mark.asyncio
async def test_event_handler():
    """Test pattern for event handlers"""
    # Setup
    event_bus_mock = EventBusMock()
    handler = EventHandler(event_bus=event_bus_mock)
    
    # Subscribe handler to event
    event_bus_mock.subscribe("test.event", handler.handle_event, async_callback=True)
    
    # Emit test event
    test_data = {"key": "value"}
    await event_bus_mock.emit_async("test.event", test_data)
    
    # Allow handler to process
    await asyncio.sleep(0.01)
    
    # Assert expected side effects
    assert handler.processed_data == test_data
    assert event_bus_mock.get_events("response.event")
```

### 4.3 Timeout Pattern for Long-Running Tests

```python
@pytest.mark.asyncio
async def test_with_timeout():
    """Test pattern with timeout for long-running operations"""
    # Setup
    mock_service = MockService(response_delay=1.0)  # 1 second delay
    
    # Execute with timeout
    try:
        # Timeout after 2 seconds
        result = await asyncio.wait_for(mock_service.long_operation(), timeout=2.0)
        assert result == expected_result
    except asyncio.TimeoutError:
        pytest.fail("Operation timed out")
```

## 5. Performance Testing

### 5.1 Performance Test Fixtures

```python
@pytest.fixture
def performance_tracker():
    """Fixture for tracking execution time"""
    class PerformanceTracker:
        def __init__(self):
            self.timings = {}
            
        async def time_operation(self, name, coroutine):
            """Time an async operation"""
            start = asyncio.get_event_loop().time()
            result = await coroutine
            duration = asyncio.get_event_loop().time() - start
            
            self.timings[name] = duration
            return result, duration
            
        def assert_max_time(self, name, max_seconds):
            """Assert operation took at most max_seconds"""
            assert name in self.timings, f"No timing recorded for {name}"
            assert self.timings[name] <= max_seconds, \
                f"Operation {name} took {self.timings[name]:.3f}s, expected <= {max_seconds}s"
    
    return PerformanceTracker()
```

### 5.2 Standard Performance Test

```python
@pytest.mark.asyncio
async def test_event_dispatch_performance(performance_tracker):
    """Test event dispatch meets performance target (<10ms)"""
    # Setup
    event_bus_mock = EventBusMock()
    received = []
    
    @event_bus_mock.subscribe("test.event", async_callback=True)
    async def handler(data):
        received.append(data)
    
    # Time event dispatch
    test_data = {"key": "value"}
    _, duration = await performance_tracker.time_operation(
        "event_dispatch",
        event_bus_mock.emit_async("test.event", test_data)
    )
    
    # Assert performance target
    assert duration < 0.010, f"Event dispatch took {duration:.3f}s, target: <0.010s"
    assert received == [test_data]
```

### 5.3 Startup Performance Test

```python
@pytest.mark.asyncio
async def test_app_startup_performance(performance_tracker):
    """Test application startup meets performance target (<10s)"""
    from vpa.core.app import ApplicationManager
    
    # Create application with mock dependencies
    event_bus_mock = EventBusMock()
    settings_mock = MagicMock()
    app = ApplicationManager(event_bus=event_bus_mock, settings=settings_mock)
    
    # Time startup
    _, duration = await performance_tracker.time_operation(
        "app_startup",
        app.start()
    )
    
    # Assert performance target
    assert duration < 10.0, f"Application startup took {duration:.3f}s, target: <10s"
    
    # Assert startup completed event
    startup_events = event_bus_mock.get_events("app.startup_complete")
    assert len(startup_events) == 1
```

## 6. Plugin Testing

### 6.1 Mock Plugin

```python
class MockPlugin:
    """Mock plugin for testing"""
    
    def __init__(self, name="mock_plugin", can_handle_result=True):
        self.name = name
        self.can_handle_result = can_handle_result
        self.process_calls = []
        self.can_handle_calls = []
        
    @property
    def plugin_name(self) -> str:
        return self.name
        
    def can_handle(self, user_input: str, context: Dict[str, Any]) -> bool:
        """Mock can_handle implementation"""
        self.can_handle_calls.append((user_input, context))
        return self.can_handle_result
        
    async def process(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Mock process implementation"""
        self.process_calls.append((user_input, context))
        return {"response": f"Processed by {self.name}", "processed": True}
```

### 6.2 Plugin Discovery Test

```python
@pytest.mark.asyncio
async def test_plugin_discovery():
    """Test plugin discovery and loading"""
    # Setup mock plugin directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create mock plugin file
        plugin_dir = os.path.join(temp_dir, "plugins")
        os.makedirs(plugin_dir)
        
        with open(os.path.join(plugin_dir, "mock_plugin.py"), "w") as f:
            f.write("""
from vpa.core.plugins import Plugin

class MockPlugin(Plugin):
    @property
    def name(self) -> str:
        return "mock_plugin"
    
    def can_handle(self, user_input, context):
        return "mock" in user_input.lower()
    
    async def process(self, user_input, context):
        return {"response": "Mock response"}
""")
        
        # Setup plugin manager with mock dependencies
        event_bus_mock = EventBusMock()
        settings_mock = MagicMock()
        settings_mock.get.return_value = [plugin_dir]
        
        # Create plugin manager
        from vpa.core.plugins import PluginManager
        manager = PluginManager(event_bus=event_bus_mock, settings=settings_mock)
        
        # Discover plugins
        await manager.discover_plugins()
        
        # Assert plugin was discovered
        assert "mock_plugin" in manager.plugins
        assert manager.plugins["mock_plugin"].name == "mock_plugin"
        
        # Test plugin functionality
        plugin = manager.plugins["mock_plugin"]
        assert plugin.can_handle("test mock command", {}) == True
        assert plugin.can_handle("other command", {}) == False
        
        result = await plugin.process("test mock command", {})
        assert result["response"] == "Mock response"
```

### 6.3 Plugin Integration Test

```python
@pytest.mark.asyncio
async def test_plugin_integration():
    """Test plugin integration with event system"""
    # Setup
    event_bus_mock = EventBusMock()
    
    # Register mock plugin
    mock_plugin = MockPlugin(name="test_plugin")
    
    # Create plugin manager with mock
    from vpa.core.plugins import PluginManager
    manager = PluginManager(event_bus=event_bus_mock)
    manager.plugins = {"test_plugin": mock_plugin}
    
    # Subscribe to plugin events
    await manager.initialize()
    
    # Emit user input event
    test_input = "test command"
    test_context = {"user_id": "test_user"}
    
    await event_bus_mock.emit_async("user.input", {
        "text": test_input,
        "context": test_context
    })
    
    # Assert plugin was called
    assert len(mock_plugin.can_handle_calls) == 1
    assert mock_plugin.can_handle_calls[0] == (test_input, test_context)
    
    assert len(mock_plugin.process_calls) == 1
    assert mock_plugin.process_calls[0] == (test_input, test_context)
    
    # Assert response event was emitted
    response_events = event_bus_mock.get_events("plugin.response")
    assert len(response_events) == 1
    assert response_events[0][1]["plugin"] == "test_plugin"
    assert response_events[0][1]["response"]["processed"] == True
```

## 7. Windows API Testing

### 7.1 Registry Operation Test

```python
@pytest.mark.asyncio
async def test_registry_operations(windows_registry_fixture):
    """Test registry operations with error handling"""
    from vpa.core.windows import registry
    
    # Test successful operation
    result = registry.set_run_at_startup(
        enable=True,
        app_name="TestApp",
        executable_path="C:\\test.exe"
    )
    
    assert result is True
    assert len(windows_registry_fixture.calls) == 1
    assert windows_registry_fixture.calls[0][0] == "registry_set_value"
    assert windows_registry_fixture.calls[0][3] == "TestApp"  # name
    assert windows_registry_fixture.calls[0][4] == "C:\\test.exe"  # value
    
    # Test error handling
    windows_registry_fixture.error_mode = "permission"
    
    with patch('vpa.core.windows.registry.emit_windows_error') as mock_emit_error:
        result = registry.set_run_at_startup(
            enable=True,
            app_name="TestApp",
            executable_path="C:\\test.exe"
        )
        
        assert result is False
        assert mock_emit_error.called
```

### 7.2 Notification Test

```python
@pytest.mark.asyncio
async def test_notification_with_fallback(windows_notification_fixture, event_bus_mock):
    """Test notification with fallback on error"""
    from vpa.core.windows import notification
    
    # Test successful notification
    result = await notification.show_toast_notification(
        title="Test Title",
        message="Test Message"
    )
    
    assert result is True
    assert len(windows_notification_fixture.calls) == 1
    assert windows_notification_fixture.calls[0][0] == "show_notification"
    
    # Test fallback on error
    windows_notification_fixture.error_mode = "disabled"
    windows_notification_fixture.reset()
    
    with patch('vpa.core.events.event_bus', event_bus_mock), \
         patch('vpa.core.windows.notification.emit_windows_error'):
        
        result = await notification.show_toast_notification(
            title="Error Test",
            message="Should Fallback"
        )
        
        assert result is False
        
        # Verify fallback event
        ui_events = event_bus_mock.get_events("ui.notification")
        assert len(ui_events) == 1
        assert ui_events[0][1]["title"] == "Error Test"
        assert ui_events[0][1]["message"] == "Should Fallback"
```

### 7.3 System Tray Test

```python
def test_system_tray_manager(windows_tray_fixture, event_bus_mock):
    """Test system tray manager with error recovery"""
    from vpa.core.windows.system_tray import SystemTrayManager
    
    # Setup
    with patch('vpa.core.events.event_bus', event_bus_mock):
        manager = SystemTrayManager()
        
        # Test successful initialization
        result = manager.initialize("C:\\icon.ico", "Test Tooltip")
        
        assert result is True
        assert manager.error_state is False
        assert manager.icon_path == "C:\\icon.ico"
        assert manager.tooltip == "Test Tooltip"
        
        # Test menu item addition
        callback = lambda: None
        result = manager.add_menu_item("Settings", callback)
        
        assert result is True
        assert len(windows_tray_fixture.calls) == 2  # init + add item
        
        # Test recovery from error
        windows_tray_fixture.error_mode = "icon_error"
        windows_tray_fixture.reset()
        
        # Force error state
        manager.error_state = True
        
        # Now recover with default icon
        with patch('vpa.core.windows.system_tray.get_default_icon', 
                  return_value="C:\\default.ico"):
            result = manager.recover()
            
            assert result is True
            assert manager.error_state is False
            
            # Check fallback event
            events = event_bus_mock.get_events("system_tray.fallback_icon")
            assert len(events) == 1
```

## Conclusion

This document establishes standardized testing patterns, fixtures, and mocks for the VPA system. By following these guidelines, all components will have consistent, thorough testing that validates functionality while respecting architectural boundaries.

The testing approach emphasizes:

1. **Isolation**: Components are tested with mock dependencies
2. **Performance**: Critical paths include performance validation
3. **Error Handling**: Tests include explicit error scenarios
4. **Event-Driven**: Test patterns respect the event-driven architecture
5. **Windows Integration**: Specialized testing for Windows API components

These patterns ensure that the VPA system maintains its architectural integrity and performance targets while providing robust verification of all functionality.

---

*Test Fixtures and Mocks Specification created on August 29, 2025*  
*Version: 1.0*  
*Related Documents: DOCUMENTATION_ALIGNMENT_CROSS_CHECK.md (v1.0)*
