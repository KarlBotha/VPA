# VPA Testing Strategy

## Overview

This document outlines the comprehensive testing strategy for the VPA project. It establishes a structured approach to testing that ensures high-quality, reliable software through the combination of automated testing, manual verification, and performance validation.

## Purpose

- Define a consistent testing methodology for all VPA components
- Establish clear test coverage requirements
- Detail test types, tools, and processes
- Provide guidance for test creation and maintenance
- Ensure all performance targets are validated

## Testing Principles

1. **Test-Driven Development** - Write tests before implementation when possible
2. **Comprehensive Coverage** - Maintain >90% code coverage for core components
3. **Isolation** - Tests should be independent and not rely on other tests
4. **Automation First** - Prioritize automated testing over manual testing
5. **Fast Feedback** - Tests should execute quickly to provide rapid feedback
6. **Performance Awareness** - Performance validation is a first-class testing concern

## Test Types and Structure

### 1. Unit Testing

Focus on testing individual components in isolation:

- **Location**: `tests/unit/`
- **Naming Convention**: `test_[module]_[function].py`
- **Coverage Target**: >90% line coverage for core components

Example structure:

```
tests/
├── unit/
│   ├── core/
│   │   ├── test_events.py
│   │   ├── test_plugins.py
│   │   └── test_app.py
│   ├── audio/
│   │   └── test_voice_system.py
│   └── gui/
│       └── test_main_window.py
```

Example unit test:

```python
# tests/unit/core/test_events.py
import pytest
import asyncio
from vpa.core.events import EventBus

class TestEventBus:
    @pytest.fixture
    def event_bus(self):
        return EventBus()
        
    @pytest.mark.asyncio
    async def test_emit_async(self, event_bus):
        # Arrange
        received_events = []
        
        async def handler(event_data):
            received_events.append(event_data)
            
        event_bus.subscribe("test_event", handler, async_callback=True)
        
        # Act
        await event_bus.emit_async("test_event", {"data": "test"})
        
        # Assert
        assert len(received_events) == 1
        assert received_events[0]["data"] == "test"
        
    @pytest.mark.asyncio
    async def test_performance_target(self, event_bus):
        """Test that event dispatch meets performance target."""
        # Arrange
        received_count = 0
        
        async def handler(event_data):
            nonlocal received_count
            received_count += 1
            await asyncio.sleep(0.001)  # Simulate work
            
        # Register 10 handlers
        for _ in range(10):
            event_bus.subscribe("perf_test", handler, async_callback=True)
            
        # Act
        start_time = asyncio.get_event_loop().time()
        await event_bus.emit_async("perf_test", {})
        elapsed_ms = (asyncio.get_event_loop().time() - start_time) * 1000
        
        # Assert
        assert received_count == 10  # All handlers called
        assert elapsed_ms < 10.0  # Performance target: <10ms
```

### 2. Integration Testing

Focus on testing interactions between components:

- **Location**: `tests/integration/`
- **Naming Convention**: `test_[component1]_[component2].py`
- **Coverage Target**: All component interactions covered

Example structure:

```
tests/
├── integration/
│   ├── test_core_architecture.py
│   ├── test_app_plugins.py
│   └── test_audio_integration.py
```

Example integration test:

```python
# tests/integration/test_core_architecture.py
import pytest
import asyncio
from vpa.core.app import ApplicationManager
from vpa.core.events import event_bus
from vpa.core.plugins import PluginManager

class TestCoreArchitecture:
    @pytest.fixture
    async def app(self):
        app = ApplicationManager()
        await app.initialize()
        yield app
        await app.shutdown()
        
    @pytest.mark.asyncio
    async def test_plugin_event_integration(self, app):
        # Arrange
        test_event_received = False
        
        async def test_handler(event_data):
            nonlocal test_event_received
            test_event_received = True
            assert event_data["source"] == "test_plugin"
        
        event_bus.subscribe("test_plugin_event", test_handler, async_callback=True)
        
        # Act
        plugin_manager = app.get_plugin_manager()
        test_plugin = plugin_manager.get_plugin("test_plugin")
        await test_plugin.process("test input", {})
        
        # Allow events to process
        await asyncio.sleep(0.1)
        
        # Assert
        assert test_event_received
```

### 3. System Testing

Focus on testing the full application:

- **Location**: `tests/system/`
- **Coverage Target**: All critical user flows covered

Example structure:

```
tests/
├── system/
│   ├── test_application_startup.py
│   ├── test_voice_interaction.py
│   └── test_plugin_lifecycle.py
```

### 4. Performance Testing

Focus on validating performance targets:

- **Location**: `tests/performance/`
- **Coverage Target**: All defined performance targets validated

Example structure:

```
tests/
├── performance/
│   ├── test_startup_time.py
│   ├── test_memory_usage.py
│   ├── test_event_dispatch.py
│   └── test_voice_synthesis.py
```

Example performance test:

```python
# tests/performance/test_startup_time.py
import time
import pytest
import psutil
import os
from vpa.core.app import ApplicationManager

def test_startup_time():
    # Arrange
    start_time = time.time()
    
    # Act
    app = ApplicationManager()
    asyncio.run(app.initialize())
    
    # Calculate startup time
    startup_time = time.time() - start_time
    
    # Assert
    assert startup_time < 10.0  # Target: <10s startup
    
    # Cleanup
    asyncio.run(app.shutdown())
    
def test_memory_usage():
    # Arrange
    process = psutil.Process(os.getpid())
    baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Act
    app = ApplicationManager()
    asyncio.run(app.initialize())
    
    # Get memory usage after initialization
    memory_usage = process.memory_info().rss / 1024 / 1024  # MB
    memory_increase = memory_usage - baseline_memory
    
    # Assert
    assert memory_increase < 2048.0  # Target: <2GB memory usage
    
    # Cleanup
    asyncio.run(app.shutdown())
```

## Test Execution and Automation

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage report
python -m pytest --cov=src/vpa --cov-report=html

# Run specific test category
python -m pytest tests/unit/

# Run specific test file
python -m pytest tests/unit/core/test_events.py

# Run tests with performance monitoring
python -m pytest tests/performance/ -v
```

### Continuous Integration

Tests automatically run on:

1. **Pull Requests**: Full test suite
2. **Main Branch Commits**: Full test suite with coverage
3. **Nightly Builds**: Performance tests and extended validation

### Test Reports

Generated after test execution:

1. **Coverage Report**: `htmlcov/index.html`
2. **Performance Report**: `performance_report.json`
3. **Test Results**: JUnit XML format for CI integration

## Mocking and Test Doubles

### Mocking External Services

Use pytest fixtures for consistent mocking:

```python
# tests/conftest.py
import pytest
from unittest.mock import MagicMock, AsyncMock

@pytest.fixture
def mock_tts_service():
    """Mock text-to-speech service."""
    mock = AsyncMock()
    mock.synthesize.return_value = b"mock_audio_data"
    mock.get_available_voices.return_value = ["en-US-AriaNeural"]
    return mock

@pytest.fixture
def mock_speech_recognition():
    """Mock speech recognition service."""
    mock = AsyncMock()
    mock.recognize_speech.return_value = {"text": "mock recognition", "confidence": 0.95}
    return mock
```

### Mock Usage Example

```python
# tests/unit/audio/test_voice_system.py
import pytest
from vpa.audio.voice_system import VoiceSystem

class TestVoiceSystem:
    @pytest.fixture
    def voice_system(self, mock_tts_service):
        system = VoiceSystem()
        system._tts_service = mock_tts_service
        return system
        
    @pytest.mark.asyncio
    async def test_synthesize_speech(self, voice_system):
        # Act
        result = await voice_system.synthesize_speech("Hello world", "en-US-AriaNeural")
        
        # Assert
        assert result == b"mock_audio_data"
        voice_system._tts_service.synthesize.assert_called_once_with(
            "Hello world", voice_id="en-US-AriaNeural"
        )
```

## Test Data Management

### Test Data Directory

```
tests/
├── data/
│   ├── audio_samples/
│   │   ├── sample1.wav
│   │   └── sample2.wav
│   ├── mock_responses/
│   │   └── llm_response.json
│   └── test_plugins/
│       └── test_plugin.py
```

### Fixtures for Data Loading

```python
# tests/conftest.py
import os
import json
import pytest

@pytest.fixture
def test_data_path():
    """Return the path to the test data directory."""
    return os.path.join(os.path.dirname(__file__), "data")
    
@pytest.fixture
def load_audio_sample(test_data_path):
    """Load an audio sample for testing."""
    def _load(sample_name):
        path = os.path.join(test_data_path, "audio_samples", sample_name)
        with open(path, "rb") as f:
            return f.read()
    return _load
    
@pytest.fixture
def load_mock_response(test_data_path):
    """Load a mock response from JSON."""
    def _load(response_name):
        path = os.path.join(test_data_path, "mock_responses", response_name)
        with open(path, "r") as f:
            return json.load(f)
    return _load
```

## Async Testing

Use pytest-asyncio for testing async code:

```python
# Example of testing async code
import pytest

@pytest.mark.asyncio
async def test_async_function():
    # Arrange
    from vpa.core.events import event_bus
    received = []
    
    async def handler(data):
        received.append(data)
    
    event_bus.subscribe("test", handler, async_callback=True)
    
    # Act
    await event_bus.emit_async("test", {"value": 42})
    
    # Assert
    assert len(received) == 1
    assert received[0]["value"] == 42
```

## Test Coverage Requirements

### Minimum Coverage Targets

- **Core Components**: >90% line coverage
- **Feature Components**: >80% line coverage
- **Plugins**: >70% line coverage
- **Event Handlers**: 100% coverage
- **Error Handling**: 100% coverage of error paths

### Coverage Validation

```bash
# Generate coverage report
python -m pytest --cov=src/vpa --cov-report=html

# Check coverage meets targets
python tools/validate_coverage.py
```

## Error Testing

### Error Injection

Test system resilience through error injection:

```python
# tests/unit/core/test_error_handling.py
import pytest
from vpa.core.events import event_bus
from vpa.core.plugins import PluginManager

class TestErrorHandling:
    @pytest.fixture
    def plugin_manager(self):
        return PluginManager()
        
    @pytest.mark.asyncio
    async def test_plugin_error_isolation(self, plugin_manager):
        # Arrange
        error_events = []
        
        async def error_handler(event_data):
            error_events.append(event_data)
            
        event_bus.subscribe("plugin_error", error_handler, async_callback=True)
        
        # Create a plugin that will raise an exception
        class ErrorPlugin:
            @property
            def name(self):
                return "error_plugin"
                
            async def process(self, user_input, context):
                raise ValueError("Simulated error")
                
        plugin_manager._plugins["error_plugin"] = ErrorPlugin()
        
        # Act - this should not raise an exception due to isolation
        await plugin_manager.process_input("test input", {})
        
        # Assert
        assert len(error_events) == 1
        assert "error_plugin" in error_events[0]["plugin_name"]
        assert "Simulated error" in error_events[0]["error_message"]
```

## Performance Testing Framework

### Performance Decorator

```python
# src/vpa/core/performance.py
import time
import asyncio
import functools

class PerformanceMonitor:
    _performance_data = {}
    
    @classmethod
    def track_execution_time(cls, name):
        """Decorator to track execution time of a function."""
        def decorator(func):
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000  # ms
                cls._record_execution_time(name, execution_time)
                return result
                
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = asyncio.get_event_loop().time()
                result = await func(*args, **kwargs)
                execution_time = (asyncio.get_event_loop().time() - start_time) * 1000  # ms
                cls._record_execution_time(name, execution_time)
                return result
                
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper
        return decorator
        
    @classmethod
    def _record_execution_time(cls, name, execution_time):
        """Record the execution time for a function."""
        if name not in cls._performance_data:
            cls._performance_data[name] = {
                "count": 0,
                "total_time": 0,
                "min_time": float('inf'),
                "max_time": 0,
            }
            
        data = cls._performance_data[name]
        data["count"] += 1
        data["total_time"] += execution_time
        data["min_time"] = min(data["min_time"], execution_time)
        data["max_time"] = max(data["max_time"], execution_time)
        
    @classmethod
    def get_statistics(cls):
        """Get performance statistics."""
        result = {}
        for name, data in cls._performance_data.items():
            avg_time = data["total_time"] / data["count"] if data["count"] > 0 else 0
            result[name] = {
                "count": data["count"],
                "avg_time_ms": avg_time,
                "min_time_ms": data["min_time"],
                "max_time_ms": data["max_time"],
            }
        return result
```

### Performance Test Example

```python
# tests/performance/test_event_performance.py
import pytest
import asyncio
from vpa.core.events import event_bus
from vpa.core.performance import PerformanceMonitor

@pytest.mark.asyncio
async def test_event_dispatch_performance():
    # Arrange
    received_count = 0
    
    async def handler(event_data):
        nonlocal received_count
        received_count += 1
    
    # Register 10 handlers
    for _ in range(10):
        event_bus.subscribe("perf_test", handler, async_callback=True)
    
    # Act - dispatch 100 events
    start_time = asyncio.get_event_loop().time()
    for i in range(100):
        await event_bus.emit_async("perf_test", {"index": i})
    elapsed = (asyncio.get_event_loop().time() - start_time) * 1000
    
    # Assert
    assert received_count == 10 * 100  # All handlers called for all events
    assert elapsed / 100 < 10.0  # Target: <10ms average per dispatch
    
    # Check performance statistics
    stats = PerformanceMonitor.get_statistics()
    if "event_dispatch" in stats:
        assert stats["event_dispatch"]["avg_time_ms"] < 10.0
```

## Benchmark Testing

### Startup Benchmark

```python
# tests/benchmarks/test_startup_benchmark.py
import time
import pytest
import statistics

def measure_startup_time():
    """Measure application startup time."""
    import time
    start_time = time.time()
    
    from vpa.core.app import ApplicationManager
    import asyncio
    
    app = ApplicationManager()
    asyncio.run(app.initialize())
    
    startup_time = time.time() - start_time
    asyncio.run(app.shutdown())
    
    return startup_time

def test_startup_benchmark():
    # Run 5 startup measurements
    times = []
    for _ in range(5):
        times.append(measure_startup_time())
    
    # Calculate statistics
    avg_time = statistics.mean(times)
    max_time = max(times)
    min_time = min(times)
    
    # Output results
    print(f"\nStartup Performance:")
    print(f"  Average: {avg_time:.3f}s")
    print(f"  Min: {min_time:.3f}s")
    print(f"  Max: {max_time:.3f}s")
    
    # Assert targets
    assert avg_time < 10.0  # Target: <10s average startup
```

## Test Environment Setup

### pytest Configuration

```python
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    asyncio: mark a test as an asyncio coroutine
    slow: mark test as slow
    performance: mark as a performance test
```

### Pre-Test Setup

```python
# tests/conftest.py
import pytest
import os
import shutil

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up the test environment."""
    # Create test directories
    os.makedirs("test_output", exist_ok=True)
    
    # Set environment variables for testing
    os.environ["VPA_TESTING"] = "1"
    os.environ["VPA_CONFIG_PATH"] = "tests/data/test_config.json"
    
    yield
    
    # Clean up
    shutil.rmtree("test_output", ignore_errors=True)
    
@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    from vpa.core.events import event_bus
    from vpa.core.app import ApplicationManager
    
    # Reset the event bus
    event_bus._handlers = {}
    
    # Reset other singletons as needed
    ApplicationManager._instance = None
```

## Test Reporting

### Coverage Report

```bash
# Generate HTML coverage report
python -m pytest --cov=src/vpa --cov-report=html

# Check coverage threshold
python -m pytest --cov=src/vpa --cov-fail-under=90
```

### Performance Report

```python
# tools/generate_performance_report.py
import json
import datetime
from vpa.core.performance import PerformanceMonitor

def generate_performance_report():
    """Generate a performance report after tests have run."""
    # Run tests that collect performance data
    import pytest
    pytest.main(["tests/performance/", "-v"])
    
    # Get performance statistics
    stats = PerformanceMonitor.get_statistics()
    
    # Add timestamp
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "statistics": stats
    }
    
    # Write report to file
    with open("performance_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"Performance report written to performance_report.json")

if __name__ == "__main__":
    generate_performance_report()
```

## Test Review Process

1. **Automated Checks**:
   - All tests pass
   - Coverage meets targets
   - Performance targets validated
   - No linting issues in test code

2. **Manual Review**:
   - Test coverage is appropriate
   - Edge cases are considered
   - Performance tests validate user experience
   - Error handling is tested

## Conclusion

This comprehensive testing strategy ensures that the VPA project maintains high quality, reliability, and performance. By following these guidelines, we can confidently develop and refine features while ensuring they meet our strict quality standards.

---

*Document created: August 29, 2025*
