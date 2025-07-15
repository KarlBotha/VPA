# VPA System Rules & Architecture Guidelines

## Architecture Principles

### 1. Modular Design
- **Plugin Architecture**: All features should be implementable as plugins
- **Loose Coupling**: Components should interact through well-defined interfaces
- **High Cohesion**: Related functionality should be grouped together
- **Separation of Concerns**: Each module should have a single responsibility

### 2. Security-First Design
- **Zero Trust Architecture**: Never trust input, always validate
- **Principle of Least Privilege**: Components should have minimal required permissions
- **Defense in Depth**: Multiple layers of security controls
- **Secure by Default**: Default configurations should be secure

### 3. Scalability & Performance
- **Horizontal Scaling**: Design for distributed deployment
- **Caching Strategy**: Implement intelligent caching at multiple levels
- **Async Processing**: Use asynchronous operations for I/O bound tasks
- **Resource Management**: Proper cleanup and resource lifecycle management

## Coding Standards

### Python Code Standards

#### 1. Style Guidelines
- **PEP 8 Compliance**: Follow Python Enhancement Proposal 8
- **Line Length**: Maximum 88 characters (Black formatter standard)
- **Imports**: Group imports (standard library, third-party, local)
- **Naming Conventions**:
  - Classes: `PascalCase`
  - Functions/Variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
  - Private methods: `_leading_underscore`

#### 2. Code Quality Requirements
```python
# Example of required docstring format
def process_user_input(user_input: str, context: Dict[str, Any]) -> Response:
    """
    Process user input and generate appropriate response.
    
    Args:
        user_input: The raw input string from the user
        context: Current conversation context and user preferences
        
    Returns:
        Response object containing the assistant's reply and metadata
        
    Raises:
        ValidationError: If user_input is empty or invalid
        ProcessingError: If input processing fails
    """
    pass
```

#### 3. Type Hints
- **Required**: All function signatures must include type hints
- **Optional Parameters**: Use `Optional[Type]` or `Type | None`
- **Complex Types**: Use `typing` module for complex type definitions
- **Return Types**: Always specify return type, use `None` if no return

#### 4. Error Handling
```python
# Preferred error handling pattern
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    raise ProcessingError(f"Failed to process: {e}") from e
else:
    logger.debug("Operation completed successfully")
    return result
finally:
    cleanup_resources()
```

### Testing Standards

#### 1. Test Coverage Requirements
- **Minimum Coverage**: 90% code coverage
- **Critical Paths**: 100% coverage for security-related code
- **Edge Cases**: Test boundary conditions and error scenarios
- **Integration Tests**: Test component interactions

#### 2. Test Structure
```python
# Test naming convention: test_[function_name]_[scenario]_[expected_result]
def test_process_user_input_valid_input_returns_response():
    """Test that valid input produces expected response."""
    # Arrange
    user_input = "Hello, assistant"
    context = {"user_id": "123", "session_id": "abc"}
    
    # Act
    result = process_user_input(user_input, context)
    
    # Assert
    assert isinstance(result, Response)
    assert result.content is not None
    assert result.confidence > 0.8
```

#### 3. Test Categories
- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test component interactions
- **System Tests**: Test end-to-end functionality
- **Performance Tests**: Validate response times and resource usage
- **Security Tests**: Validate input sanitization and access controls

## Zero-Trust Validation Rules

### 1. Input Validation
```python
def validate_user_input(user_input: str) -> str:
    """
    Validate and sanitize user input according to zero-trust principles.
    
    All input is considered potentially malicious until proven otherwise.
    """
    if not isinstance(user_input, str):
        raise ValidationError("Input must be a string")
    
    if len(user_input) > MAX_INPUT_LENGTH:
        raise ValidationError(f"Input exceeds maximum length of {MAX_INPUT_LENGTH}")
    
    # Sanitize potentially dangerous characters
    sanitized = html.escape(user_input)
    
    # Check for injection patterns
    if contains_injection_patterns(sanitized):
        raise SecurityError("Potentially malicious input detected")
    
    return sanitized
```

### 2. Data Access Controls
- **Authentication Required**: All operations require valid authentication
- **Authorization Checks**: Verify permissions before data access
- **Data Encryption**: Sensitive data must be encrypted at rest and in transit
- **Audit Logging**: Log all data access and modifications

### 3. API Security
```python
@require_authentication
@rate_limit(requests_per_minute=60)
@validate_input
def api_endpoint(request: Request) -> Response:
    """Example of properly secured API endpoint."""
    user = get_authenticated_user(request)
    
    if not user.has_permission("read_data"):
        raise UnauthorizedError("Insufficient permissions")
    
    # Process request with validated input
    result = process_request(request.validated_data)
    
    # Log the operation
    audit_logger.info(f"User {user.id} accessed endpoint", extra={
        "user_id": user.id,
        "endpoint": request.endpoint,
        "timestamp": datetime.utcnow()
    })
    
    return result
```

## Architecture Components

### 1. Core Components
```
VPA/
├── src/
│   ├── core/               # Core system components
│   │   ├── assistant.py    # Main assistant orchestrator
│   │   ├── nlp/           # Natural language processing
│   │   ├── plugins/       # Plugin management system
│   │   └── security/      # Security and validation
│   ├── interfaces/        # User interfaces (CLI, web, API)
│   ├── integrations/      # External service integrations
│   └── utils/             # Utility functions and helpers
```

### 2. Plugin Architecture
```python
class Plugin(ABC):
    """Base class for all VPA plugins."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name identifier."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass
    
    @abstractmethod
    def can_handle(self, user_input: str, context: Dict[str, Any]) -> bool:
        """Determine if this plugin can handle the user input."""
        pass
    
    @abstractmethod
    def process(self, user_input: str, context: Dict[str, Any]) -> Response:
        """Process the user input and return a response."""
        pass
```

### 3. Configuration Management
- **Environment-based**: Use environment variables for deployment configs
- **Hierarchical**: Support multiple configuration layers (default, user, runtime)
- **Validation**: Validate all configuration values at startup
- **Security**: Never store secrets in configuration files

## Performance Standards

### 1. Response Time Requirements
- **Simple Queries**: < 500ms response time
- **Complex Operations**: < 2 seconds response time
- **Background Tasks**: Async processing with progress updates
- **File Operations**: Streaming for large files

### 2. Resource Usage Limits
- **Memory**: < 512MB for basic operations
- **CPU**: Optimize for multi-core processing
- **Disk I/O**: Minimize synchronous disk operations
- **Network**: Implement connection pooling and caching

### 3. Monitoring & Observability
```python
import logging
import time
from functools import wraps

def monitor_performance(func):
    """Decorator to monitor function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            success = True
            return result
        except Exception as e:
            success = False
            raise
        finally:
            duration = time.time() - start_time
            logger.info(f"{func.__name__} completed", extra={
                "function": func.__name__,
                "duration": duration,
                "success": success
            })
    return wrapper
```

## Deployment & Operations

### 1. Environment Management
- **Development**: Local development with hot-reload
- **Testing**: Automated testing environment
- **Staging**: Production-like environment for final testing
- **Production**: Optimized for performance and reliability

### 2. Monitoring Requirements
- **Health Checks**: System health and component status
- **Performance Metrics**: Response times, throughput, error rates
- **Security Monitoring**: Failed authentication attempts, suspicious activity
- **Business Metrics**: User engagement, feature usage

### 3. Backup & Recovery
- **Data Backup**: Regular automated backups
- **Configuration Backup**: Version-controlled configuration
- **Disaster Recovery**: Documented recovery procedures
- **Testing**: Regular backup restoration testing

## Documentation Standards

### 1. Code Documentation
- **Docstrings**: Required for all public functions and classes
- **Inline Comments**: Explain complex logic and business rules
- **Type Hints**: Comprehensive type annotations
- **Examples**: Include usage examples in docstrings

### 2. System Documentation
- **Architecture Diagrams**: Visual representation of system components
- **API Documentation**: Auto-generated from code annotations
- **Deployment Guides**: Step-by-step deployment instructions
- **Troubleshooting**: Common issues and solutions

### 3. User Documentation
- **Getting Started**: Quick start guide for new users
- **User Manual**: Comprehensive feature documentation
- **FAQ**: Frequently asked questions and answers
- **Examples**: Real-world usage examples and tutorials
