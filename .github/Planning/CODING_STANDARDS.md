# VPA Coding Standards

## Overview

This document defines the coding standards, conventions, and best practices for the VPA (Virtual Personal Assistant) project. Following these standards ensures code consistency, maintainability, readability, and performance across the codebase.

## 1. Python Version and Compatibility

### Version Requirements
- **Python Version**: 3.9+ (3.11 recommended)
- **Windows Compatibility**: Windows 10/11 (21H1 or newer)
- **Minimum System**: 4GB RAM, dual-core CPU

### Version-Specific Features
- Type hints/annotations (PEP 484, PEP 585)
- Async/await syntax (PEP 492)
- F-strings for string formatting (PEP 498)
- Dataclasses for data containers (PEP 557)
- Walrus operator `:=` allowed where it improves readability

## 2. Code Organization

### Project Structure
```
src/
├── main.py                 # Application entry point
├── audio/                  # Voice system (13-voice catalog)
│   ├── __init__.py
│   ├── voice_system.py     # Main voice system interface
│   ├── azure_provider.py   # Azure voice provider
│   └── windows_provider.py # Windows fallback provider
└── vpa/
    ├── __init__.py
    ├── core/               # Core application logic
    │   ├── __init__.py
    │   ├── app.py          # Application manager
    │   ├── events.py       # Event bus system
    │   ├── plugins.py      # Plugin management
    │   ├── config.py       # Configuration management
    │   ├── performance.py  # Performance monitoring
    │   ├── security.py     # Security utilities
    │   ├── windows/        # Windows API integration components
    │   │   ├── __init__.py
    │   │   ├── registry.py       # Windows Registry access
    │   │   ├── notification.py   # Toast/notification system
    │   │   ├── system_tray.py    # System tray integration
    │   │   └── file_system.py    # File system operations
    │   └── llm/           # LLM integration
    │       ├── __init__.py
    │       ├── llm_manager.py    # Main coordinator
    │       ├── adapters/         # Backend-specific adapters
    │       │   ├── __init__.py
    │       │   ├── ollama_adapter.py
    │       │   ├── llama_cpp_adapter.py
    │       │   └── fallback_adapter.py
    │       └── model_registry.py # Available models tracking
    ├── gui/               # GUI components
    │   ├── __init__.py
    │   ├── main_window.py        # Main application window
    │   ├── settings_panel.py     # Settings interface
    │   ├── chat_interface.py     # Chat/interaction UI
    │   └── theme.py             # Theme management
    ├── services/          # Service integrations
    │   ├── __init__.py
    │   ├── weather.py     # Weather service
    │   ├── calendar.py    # Calendar service
    │   ├── email.py       # Email service
    │   └── news.py        # News service
    └── plugins/           # Plugin modules
        ├── __init__.py
        ├── core_plugins/         # Built-in functionality
        │   ├── __init__.py
        │   ├── time_plugin.py
        │   ├── system_info_plugin.py
        │   └── settings_plugin.py
        └── addons/              # Optional addon features
            └── __init__.py
```

### Module Organization
Each module should follow this structure:
```python
"""Module docstring explaining purpose and usage."""

# Standard library imports
import os
import sys
import time

# Third-party imports
import aiohttp
import numpy as np

# Local application imports
from vpa.core.events import event_bus
from vpa.core.plugins import Plugin

# Constants (ALL_CAPS)
DEFAULT_TIMEOUT = 10
MAX_RETRY_COUNT = 3

# Classes
class MyClass:
    """Class docstring."""
    
    def __init__(self):
        """Initialize the class."""
        pass
        
# Functions
def my_function():
    """Function docstring."""
    pass
    
# Main execution (if applicable)
if __name__ == "__main__":
    # Code to execute when run as script
    pass
```

## 3. Naming Conventions

### General Rules
- **Use English** for all code, comments, and documentation
- **Be descriptive** - prefer clarity over brevity
- **Avoid abbreviations** unless universally understood

### Specific Naming Patterns

| Type | Convention | Example |
|------|------------|---------|
| Variables | Snake case | `user_input`, `event_data` |
| Constants | Upper snake case | `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT` |
| Functions | Snake case | `get_user_data()`, `process_input()` |
| Classes | Pascal case | `EventBus`, `PluginManager` |
| Methods | Snake case | `initialize()`, `process_event()` |
| Modules | Snake case | `voice_system.py`, `event_bus.py` |
| Private members | Leading underscore | `_cache`, `_handle_event()` |
| Protected members | Double leading underscore | `__secure_data` |

### Special Naming Cases
- **Event names**: `noun_verb` format - `user_input`, `speech_synthesized`
- **Plugin names**: Descriptive noun - `weather_plugin`, `calendar_plugin`
- **Config keys**: Hierarchical with dots - `voice.default_voice`, `llm.temperature`

## 4. Docstrings and Comments

### Docstring Format
Use Google style docstrings:

```python
def function_name(param1: type, param2: type) -> return_type:
    """Short description of function.
    
    Longer description with more details if needed.
    
    Args:
        param1: Description of param1.
        param2: Description of param2.
        
    Returns:
        Description of return value.
        
    Raises:
        ExceptionType: When and why this exception is raised.
    """
    pass
```

### Required Docstrings
- All modules
- All classes
- All public methods and functions
- All complex private methods

### Comments
- Use comments to explain "why" not "what"
- Keep comments up-to-date with code changes
- Use TODO/FIXME comments for future work: `# TODO: Implement caching`

## 5. Type Hints

### Type Annotation Guidelines
- Use type hints for all function parameters and return values
- Use the typing module for complex types
- Use Optional[] for parameters that might be None
- Use Union[] for parameters that might be multiple types

### Examples
```python
from typing import Dict, List, Optional, Union, Any, Callable, TypeVar, Generic

# Basic types
def process_text(text: str) -> bool:
    return bool(text)

# Complex types
def handle_event(event_data: Dict[str, Any]) -> None:
    pass
    
# Optional parameters
def get_user(user_id: str, include_profile: Optional[bool] = None) -> Dict[str, Any]:
    pass
    
# Union types
def process_input(data: Union[str, Dict[str, Any], List[str]]) -> None:
    pass
    
# Callable
def register_handler(event_name: str, handler: Callable[[Dict[str, Any]], None]) -> None:
    pass
    
# Generics
T = TypeVar('T')
class Cache(Generic[T]):
    def get(self, key: str) -> Optional[T]:
        pass
```

## 6. Code Style

### Formatting
- **Line Length**: 88 characters maximum (Black formatter default)
- **Indentation**: 4 spaces (no tabs)
- **String Quotes**: Single quotes for simple strings, double quotes for docstrings
- **Whitespace**: Follow PEP 8 recommendations

### Tool Usage
- **Code Formatter**: Black (default settings)
- **Linter**: Flake8 with settings:
  ```
  [flake8]
  max-line-length = 88
  extend-ignore = E203
  ```
- **Type Checker**: mypy with strict mode

### Imports
- Group imports as standard library, third-party, and local
- Sort alphabetically within each group
- Use absolute imports for external modules
- Use relative imports for internal modules

## 7. Asynchronous Programming

### Async Guidelines
- All I/O operations must be asynchronous
- Use `async def` for all coroutine functions
- Use `await` for all awaitable calls
- Avoid mixing synchronous and asynchronous code

### Specific Patterns
```python
# Preferred pattern for async event handlers
@event_bus.subscribe("event_name", async_callback=True)
async def handle_event(event_data: Dict[str, Any]) -> None:
    try:
        # Async operation
        result = await async_operation()
        
        # Emit result
        await event_bus.emit_async("result_event", {"result": result})
    except Exception as e:
        logger.error(f"Error in event handler: {e}")

# Correct pattern for running async code from sync context
def sync_function():
    asyncio.run_coroutine_threadsafe(
        async_function(), 
        asyncio.get_event_loop()
    )
```

### Common Anti-Patterns to Avoid
- ❌ Using `asyncio.run()` in an existing event loop
- ❌ Blocking the event loop with synchronous code
- ❌ Using `time.sleep()` instead of `await asyncio.sleep()`
- ❌ Not handling exceptions in asynchronous code

## 8. Error Handling

### Exception Hierarchy
```
BaseException
 ├── Exception
 │    ├── VPAError                  # Base for all VPA exceptions
 │    │    ├── ConfigurationError   # Configuration issues
 │    │    ├── PluginError          # Plugin-related errors
 │    │    │    ├── PluginLoadError
 │    │    │    └── PluginExecutionError
 │    │    ├── APIError             # External API issues
 │    │    │    ├── NetworkError
 │    │    │    ├── AuthenticationError
 │    │    │    └── RateLimitError
 │    │    └── ResourceError        # Resource issues
 │    │         ├── AudioError
 │    │         └── LLMError
```

### Exception Handling Patterns
```python
# Basic pattern
try:
    result = operation_that_might_fail()
except SpecificError as e:
    logger.error(f"Specific error: {e}")
    # Handle specific error
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Handle general error
else:
    # Code to run if no exception
finally:
    # Code to always run
```

### Guidelines
- Never use bare except
- Handle specific exceptions before general ones
- Log all exceptions with appropriate level
- Provide context in error messages
- Implement graceful degradation for all errors

### Error Messages
- Be specific about what went wrong
- Include relevant context
- Suggest potential fixes when possible
- Never include sensitive data

## 9. Logging

### Logging Levels
- **DEBUG**: Detailed information for debugging
- **INFO**: Confirmation that things are working
- **WARNING**: Something unexpected but not an error
- **ERROR**: Failed operation but can continue
- **CRITICAL**: Application cannot continue

### Logging Format
```python
# Logger configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("vpa.log"),
        logging.StreamHandler()
    ]
)

# Create module logger
logger = logging.getLogger(__name__)

# Usage
logger.debug("Detailed information")
logger.info("Confirmation message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error")
```

### Logging Guidelines
- Use appropriate level for each message
- Include relevant context in messages
- Never log sensitive information
- Use structured logging for machine-parseable logs

## 10. Performance Considerations

### Performance Monitoring
```python
@PerformanceMonitor.track_execution_time("function_name")
async def performance_critical_function(param: str) -> Result:
    # Function implementation
    pass
```

### Memory Management
- Avoid large objects in memory when possible
- Use generators for large data processing
- Implement proper cleanup in `__del__` or `close()` methods
- Monitor memory usage with PerformanceMonitor

### CPU Optimization
- Use async for I/O-bound operations
- Use threading for CPU-bound operations
- Implement caching for expensive operations
- Profile and optimize hot code paths

## 11. Testing Standards

### Test Organization
```
tests/
├── conftest.py             # Shared test fixtures
├── test_core_architecture.py  # Core architecture tests
├── core/                   # Core component tests
│   ├── test_events.py
│   ├── test_plugins.py
│   └── test_app.py
├── audio/                  # Audio system tests
│   └── test_voice_system.py
└── plugins/                # Plugin tests
    └── test_plugins.py
```

### Test Requirements
- Minimum 90% code coverage
- Unit tests for all components
- Integration tests for component interactions
- Performance tests for critical paths

### Test Patterns
```python
# Basic test pattern
def test_function_name():
    # Arrange
    input_data = prepare_input()
    expected_output = expected_result()
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected_output

# Async test pattern
@pytest.mark.asyncio
async def test_async_function():
    # Arrange
    input_data = prepare_input()
    expected_output = expected_result()
    
    # Act
    result = await async_function_under_test(input_data)
    
    # Assert
    assert result == expected_output

# Exception test pattern
def test_function_raises_exception():
    with pytest.raises(ExpectedException) as exc_info:
        function_that_should_raise()
        
    assert "expected message" in str(exc_info.value)
```

### Mocking Guidelines
- Use pytest-mock for mocking
- Mock external dependencies
- Use fixture patterns for test setup
- Clean up resources after tests

## 12. Security Guidelines

### Data Security
- Never store sensitive data in plain text
- Use Windows Credential Manager for API keys
- Use AES-256 encryption for sensitive configuration
- Implement proper key management

### Input Validation
- Validate all user input
- Use type hints and runtime checks
- Implement input sanitization
- Use allowlists instead of denylists

### Output Encoding
- Encode all output to prevent injection
- Use HTML escaping for web content
- Use proper quoting for command-line arguments
- Implement context-appropriate encoding

### Other Security Considerations
- Verify dependencies for security issues
- Implement secure update mechanisms
- Follow least privilege principle
- Document security assumptions

## 13. Windows Integration Guidelines

### Registry Access
- Use dedicated registry class for all access
- Implement proper error handling
- Follow least privilege principle
- Document all registry keys used

### File System Access
- Use pathlib for path manipulation
- Handle file permissions properly
- Implement proper error handling
- Use secure file operations

### System Tray Integration
- Follow Windows UI guidelines
- Implement proper resource cleanup
- Handle high DPI displays
- Support light/dark themes

## 14. Documentation Requirements

### Code Documentation
- All public APIs must be documented
- Include examples for non-trivial functions
- Document assumptions and limitations
- Keep documentation in sync with code

### User Documentation
- Installation guide
- User manual
- FAQ
- Troubleshooting guide

### Developer Documentation
- Architecture overview
- Component documentation
- API reference
- Plugin development guide

## 15. Version Control Guidelines

### Branching Strategy
- `main`: Production-ready code
- `develop`: Development branch
- `feature/*`: Feature branches
- `bugfix/*`: Bug fix branches
- `release/*`: Release preparation branches

### Commit Messages
Use conventional commits format:
```
<type>(scope): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions or changes
- `chore`: Build process or tool changes

Example:
```
feat(voice): add support for voice styles in Azure TTS

Implement SSML templates for emotion and style tags in Azure voice synthesis.
Support 'cheerful', 'sad', 'angry', and 'friendly' styles.

Closes #123
```

### Pull Requests
- Use descriptive titles
- Provide detailed descriptions
- Reference related issues
- Ensure all tests pass
- Ensure code review by at least one other developer

## 16. Dependency Management

### Requirements Files
- `requirements.txt`: Core dependencies
- `requirements-dev.txt`: Development dependencies
- `requirements-test.txt`: Testing dependencies

### Version Pinning
- Pin exact versions for critical dependencies
- Use compatible release specifier (~=) for others
- Document dependency decisions

### Example Requirements.txt
```
# Core dependencies
asyncio>=3.4.3,<4.0.0
aiohttp==3.8.3
pydantic==1.10.2
azure-cognitiveservices-speech==1.24.2
msal==1.20.0
PyWin32==304
pyttsx3==2.90
psutil>=5.9.0

# Performance and monitoring
prometheus-client==0.15.0
```

## Conclusion

These coding standards ensure consistency, maintainability, and quality across the VPA codebase. All contributors should follow these guidelines for new code and update existing code to conform when making changes.

For questions or clarifications about these standards, consult with the lead developer or open a discussion in the project repository.

---

*Coding Standards completed on August 27, 2025*
