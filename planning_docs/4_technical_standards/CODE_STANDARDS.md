# VPA Code Standards

## Overview

This document defines the coding standards, practices, and patterns to be followed during the development of the VPA (Virtual Personal Assistant) project. Adherence to these standards ensures code quality, maintainability, and consistency across the codebase.

## General Principles

### 1. Clarity Over Cleverness
- Prefer clear, readable code over clever optimizations
- Comment complex algorithms and non-obvious solutions
- Use descriptive names that explain purpose and intent
- Structure code for readability and maintainability

### 2. Consistency
- Follow the same patterns throughout the codebase
- Use consistent naming, formatting, and organizational approaches
- Apply the same error handling strategies across components
- Maintain consistent documentation style

### 3. Robustness
- Never assume perfect inputs or conditions
- Validate inputs and handle edge cases
- Gracefully degrade when dependencies are unavailable
- Log errors with sufficient context for troubleshooting

### 4. Performance Awareness
- Consider performance implications of design decisions
- Optimize critical paths identified in performance requirements
- Measure and validate performance against targets
- Document performance characteristics and trade-offs

### 5. Testability
- Design components to be easily testable
- Use dependency injection to facilitate mocking
- Separate business logic from I/O operations
- Create appropriate abstractions for testing

## Python Standards

### Version Support
- Target Python 3.9+ (3.11+ recommended)
- Use modern Python features where appropriate
- Avoid deprecated features and patterns

### Code Formatting
- Follow PEP 8 style guide with the following specifications:
  - 4 spaces for indentation (no tabs)
  - Maximum line length of 88 characters
  - Use trailing commas in multi-line structures
  - Two blank lines before top-level class and function definitions
  - One blank line before method definitions
  - Group imports: standard library, third-party, local
- Use [Black](https://github.com/psf/black) for code formatting (optional)

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Modules | Lowercase with underscores | `event_bus.py` |
| Packages | Lowercase, no underscores | `vpa`, `audio` |
| Classes | CapWords (PascalCase) | `EventBus`, `VoiceCatalog` |
| Functions/Methods | Lowercase with underscores | `emit_event()`, `get_voice_info()` |
| Variables | Lowercase with underscores | `voice_id`, `event_data` |
| Constants | UPPERCASE with underscores | `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT` |
| Private Members | Prefix with underscore | `_internal_state`, `_process_data()` |

### Type Annotations
- Use type hints for all public APIs
- Include return type annotations (-> None, -> bool, etc.)
- Use Optional[Type] for nullable values
- Use Union[Type1, Type2] for multiple possible types
- Define custom types with TypedDict or NamedTuple where appropriate

Example:
```python
from typing import Dict, List, Optional, Union, Any

def process_message(
    message: str, 
    context: Dict[str, Any], 
    timeout: Optional[float] = None
) -> Union[Dict[str, Any], None]:
    """Process a message with context."""
    # Implementation
```

### Documentation

#### Docstrings
- Use Google-style docstrings
- Include descriptions of parameters, return values, and exceptions
- Document expected types even with type annotations
- Include examples for complex functionality

Example:
```python
def synthesize_speech(
    text: str, 
    voice_id: Optional[str] = None
) -> Dict[str, Any]:
    """Synthesize speech from text.
    
    Args:
        text: The text to convert to speech.
        voice_id: ID of the voice to use. If None, uses default voice.
        
    Returns:
        Dictionary containing:
        - audio_data: The synthesized audio data
        - duration: Length of audio in seconds
        - file_path: Path to the temporary audio file
        
    Raises:
        VoiceNotFoundError: If the specified voice is not available
        SynthesisError: If speech synthesis fails
        
    Example:
        >>> result = synthesize_speech("Hello world", "en-US-AriaNeural")
        >>> play_audio(result["audio_data"])
    """
    # Implementation
```

#### Comments
- Comment complex algorithms and non-obvious solutions
- Explain "why" not just "what"
- Keep comments up-to-date with code changes
- Use TODO, FIXME with issue reference for future work

### Error Handling

#### Exception Patterns
- Define custom exceptions for specific error cases
- Catch specific exceptions, not `Exception` (except in top-level handlers)
- Include context in exception messages
- Use context managers for resource cleanup

Example:
```python
class VoiceNotFoundError(Exception):
    """Raised when a requested voice is not available."""
    pass

def get_voice(voice_id: str) -> VoiceInfo:
    """Get voice information by ID."""
    try:
        return voice_catalog.get_voice(voice_id)
    except KeyError:
        raise VoiceNotFoundError(f"Voice '{voice_id}' not found in catalog")
```

#### Error Boundaries
- Implement error boundaries at component interfaces
- Log all errors with sufficient context
- Prevent exceptions from propagating across component boundaries
- Use graceful degradation to maintain functionality

### Asynchronous Code

#### Asyncio Patterns
- Use `async`/`await` syntax for all asynchronous code
- Avoid mixing asyncio with other async frameworks
- Handle cancellation properly with try/except/finally
- Use asyncio.gather for concurrent operations

Example:
```python
async def process_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a request asynchronously."""
    try:
        # Run multiple operations concurrently
        result1, result2 = await asyncio.gather(
            fetch_data(request_data["id"]),
            prepare_response_template()
        )
        return combine_results(result1, result2)
    except asyncio.CancelledError:
        # Handle cancellation
        logger.info("Request processing cancelled")
        # Clean up resources
        await cleanup_resources()
        raise
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return {"error": str(e)}
```

#### Task Management
- Always await created tasks or add them to a task registry
- Use asyncio.create_task with meaningful names
- Handle exceptions in background tasks
- Use timeouts for operations that might hang

Example:
```python
async def start_background_processing():
    """Start background processing task."""
    task = asyncio.create_task(
        background_process(), 
        name="background_processor"
    )
    # Register task for lifecycle management
    task_registry.register(task)
    
    # Handle exceptions
    task.add_done_callback(handle_background_task_done)
```

## Event-Driven Architecture Standards

### Event Naming
- Use dot-notation to organize event namespace
- Format: `category.action[.detail]`
- Use past tense for completed actions
- Use present tense for ongoing actions or states

Examples:
- `audio.speech.completed` - Speech synthesis finished
- `user.input.received` - User provided input
- `system.startup.completed` - System finished startup
- `plugin.error.occurred` - Plugin encountered an error

### Event Data Structure
- Use consistent structure for all events
- Include timestamp and source
- Keep event data serializable
- Include correlation IDs for related events

Example:
```python
event_data = {
    "timestamp": time.time(),
    "source": "audio_system",
    "correlation_id": request_id,
    "data": {
        "text": "Hello world",
        "voice_id": "en-US-AriaNeural",
        "duration_ms": 1250
    }
}
```

### Event Handling
- Keep handlers focused on single responsibility
- Use async handlers for I/O operations
- Handle exceptions within handlers
- Avoid long processing in handlers

Example:
```python
@event_bus.subscribe("audio.speech.completed", async_callback=True)
async def handle_speech_completed(event_data: Dict[str, Any]) -> None:
    """Handle speech completion event."""
    try:
        # Process the event
        await update_ui_state(event_data)
    except Exception as e:
        logger.error(f"Error handling speech completion: {e}")
        # Don't propagate the exception to the event bus
```

## Plugin Development Standards

### Plugin Structure
- Implement `Plugin` abstract base class
- Use properties for metadata
- Implement lifecycle methods
- Handle dependencies explicitly

Example:
```python
from vpa.core.plugins import Plugin
from typing import Dict, Any, List

class WeatherPlugin(Plugin):
    @property
    def name(self) -> str:
        return "weather_plugin"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def description(self) -> str:
        return "Provides weather information"
        
    @property
    def dependencies(self) -> List[str]:
        return ["location_plugin"]
        
    def can_handle(self, user_input: str, context: Dict[str, Any]) -> bool:
        """Check if plugin can handle this input."""
        # Implementation
        
    async def process(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process user input."""
        # Implementation
```

### Plugin Manifest
- Include complete metadata in plugin.json
- Specify all dependencies
- Define settings schema
- Provide clear descriptions

Example:
```json
{
  "id": "weather_plugin",
  "name": "Weather Plugin",
  "version": "1.0.0",
  "description": "Provides weather information",
  "author": "VPA Team",
  "main": "plugin.py",
  "class": "WeatherPlugin",
  "dependencies": ["location_plugin"],
  "settings": {
    "api_key": {
      "type": "string",
      "default": "",
      "description": "API key for weather service"
    },
    "units": {
      "type": "string",
      "default": "metric",
      "enum": ["metric", "imperial"],
      "description": "Units for weather data"
    }
  }
}
```

### Plugin Communication
- Use event bus for all communication
- Don't import other plugins directly
- Request capabilities via dependency system
- Use standard event patterns

## Testing Standards

### Test Organization
- Place tests in parallel directory structure
- Name test files with `test_` prefix
- Group tests by component or functionality
- Use appropriate test categories

Example:
```
src/
  vpa/
    core/
      events.py
tests/
  vpa/
    core/
      test_events.py
```

### Test Structure
- Use pytest for all testing
- Group related tests in classes
- Use descriptive test names
- Follow Arrange-Act-Assert pattern

Example:
```python
import pytest
from vpa.core.events import EventBus

class TestEventBus:
    def test_subscribe_and_emit(self):
        # Arrange
        bus = EventBus()
        received_events = []
        
        def handler(event_data):
            received_events.append(event_data)
            
        bus.subscribe("test.event", handler)
        
        # Act
        bus.emit("test.event", {"value": 42})
        
        # Assert
        assert len(received_events) == 1
        assert received_events[0]["value"] == 42
```

### Asynchronous Testing
- Use pytest-asyncio for async tests
- Mark tests with `@pytest.mark.asyncio`
- Handle coroutines properly
- Test both success and error cases

Example:
```python
import pytest
import asyncio
from vpa.core.events import EventBus

@pytest.mark.asyncio
async def test_async_event_handling():
    # Arrange
    bus = EventBus()
    results = []
    
    async def async_handler(event_data):
        await asyncio.sleep(0.1)  # Simulate async work
        results.append(event_data["value"])
    
    bus.subscribe("async.test", async_handler, async_callback=True)
    
    # Act
    await bus.emit_async("async.test", {"value": 42})
    
    # Assert
    assert results == [42]
```

### Mocking
- Use pytest fixtures for test setup
- Use unittest.mock for mocking
- Create specialized fixtures for common components
- Prefer dependency injection for testability

Example:
```python
import pytest
from unittest.mock import MagicMock
from vpa.core.events import EventBus
from vpa.audio.voice_system import VPAVoiceSystem

@pytest.fixture
def mock_event_bus():
    """Create a mock event bus."""
    bus = MagicMock(spec=EventBus)
    return bus

@pytest.fixture
def voice_system(mock_event_bus):
    """Create a voice system with a mock event bus."""
    system = VPAVoiceSystem(mock_event_bus, MagicMock())
    return system

def test_voice_system_emits_event(voice_system, mock_event_bus):
    # Act
    voice_system.synthesize_speech("Hello")
    
    # Assert
    mock_event_bus.emit.assert_called_with(
        "audio.speech.started",
        {"text": "Hello"}
    )
```

### Test Coverage
- Maintain >90% test coverage for core components
- Test both success and error paths
- Include edge case tests
- Test performance characteristics

## Performance Monitoring

### Decorator Pattern
Use the `@PerformanceMonitor.track_execution_time` decorator for critical methods:

```python
from vpa.core.performance import PerformanceMonitor

@PerformanceMonitor.track_execution_time("synthesize_speech")
async def synthesize_speech(text: str, voice_id: str = None) -> Dict[str, Any]:
    """Synthesize speech from text."""
    # Implementation
```

### Critical Paths
Always monitor these critical paths:
- Event dispatch
- Plugin loading
- Voice synthesis
- GUI operations
- Startup sequence

## Security Practices

### Data Protection
- Never store sensitive data in plaintext
- Use secure storage for API keys
- Validate all inputs, especially from plugins
- Implement proper permission checks

### Plugin Security
- Validate plugin sources
- Limit plugin capabilities based on trust level
- Monitor plugin resource usage
- Implement sandbox mechanisms where appropriate

## Dependencies Management

### Requirements Specification
- Pin exact versions in production requirements
- Use ranges in development requirements
- Document purpose of each dependency
- Group dependencies by function

Example:
```
# Core dependencies
asyncio>=3.4.3,<4.0.0
psutil==5.9.0

# Audio dependencies
edge-tts==7.0.0
pygame==2.6.0

# GUI dependencies
customtkinter==5.2.0
pillow==9.5.0

# Development dependencies
pytest>=7.0.0
black>=23.0.0
```

### Virtual Environments
- Always use virtual environments
- Document environment setup
- Include environment creation in setup scripts
- Verify dependency compatibility

## Documentation Standards

### Code Documentation
- Document all classes and public methods
- Include type information
- Explain complex algorithms
- Reference related components

### Project Documentation
- Maintain architecture documentation
- Document component interfaces
- Include setup and development guides
- Provide plugin development tutorials

## Version Control Practices

### Commit Standards
- Use descriptive commit messages
- Follow conventional commits format
- Reference issues in commits
- Keep commits focused on single changes

### Branch Strategy
- `main`: Stable, deployable code
- `develop`: Integration branch
- Feature branches: `feature/feature-name`
- Bug fix branches: `fix/bug-description`

## Development Workflow

### Code Review
- All changes require review
- Check for adherence to standards
- Verify test coverage
- Review performance implications

### CI/CD Integration
- Run tests on all pull requests
- Measure code coverage
- Perform static analysis
- Build and package on merges to main

## See Also

- [Documentation Standards](./DOCUMENTATION_STANDARDS.md)
- [Error Handling Strategy](./ERROR_HANDLING_STRATEGY.md)
- [Testing Strategy](../6_testing_quality/TESTING_STRATEGY.md)
- [Versioning Strategy](./VERSIONING_STRATEGY.md)

---

*Document created: August 29, 2025*  
*Version: 1.0*
