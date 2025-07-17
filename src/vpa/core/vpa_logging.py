"""
Structured Logging System for VPA.
Provides JSON-based structured logging with correlation IDs, metadata, and searchable fields.
"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Union
from contextvars import ContextVar

# Context variable for correlation tracking
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs JSON-structured log messages.
    """
    
    def __init__(self, service_name: str = "vpa", version: str = "1.0.0"):
        super().__init__()
        self.service_name = service_name
        self.version = version
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as structured JSON.
        """
        # Get correlation ID from context
        corr_id = correlation_id.get()
        
        # Build structured log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": self.service_name,
            "version": self.version,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process
        }
        
        # Add correlation ID if available
        if corr_id:
            log_entry["correlation_id"] = corr_id
        
        # Add exception information if present
        if record.exc_info and record.exc_info != (None, None, None):
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info) if record.exc_info else None
            }
        
        # Add extra fields if present (avoid reserved LogRecord attributes)
        reserved_attrs = {
            'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
            'filename', 'module', 'lineno', 'funcName', 'created', 
            'msecs', 'relativeCreated', 'thread', 'threadName', 
            'processName', 'process', 'exc_info', 'exc_text', 'stack_info',
            'message', 'asctime'  # Additional reserved attributes
        }
        
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in reserved_attrs:
                extra_fields[key] = value
        
        if extra_fields:
            log_entry["extra"] = extra_fields
        
        return json.dumps(log_entry, default=str)


class StructuredLogger:
    """
    Structured logging wrapper that provides enhanced logging capabilities.
    """
    
    def __init__(self, name: str, service_name: str = "vpa", version: str = "1.0.0"):
        self.logger = logging.getLogger(name)
        self.service_name = service_name
        self.version = version
    
    def _log_with_context(self, level: int, message: str, **kwargs) -> None:
        """
        Log message with additional context and metadata.
        """
        extra = kwargs.copy()
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with context."""
        self._log_with_context(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message with context."""
        self._log_with_context(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with context."""
        self._log_with_context(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message with context."""
        self._log_with_context(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message with context."""
        self._log_with_context(logging.CRITICAL, message, **kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """Log exception with full traceback."""
        self.logger.exception(message, extra=kwargs)
    
    def log_performance(self, operation: str, duration: float, **kwargs) -> None:
        """Log performance metrics."""
        self.info(f"Performance: {operation}", 
                 operation=operation, 
                 duration_ms=round(duration * 1000, 2),
                 performance=True,
                 **kwargs)
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], **kwargs) -> None:
        """Log security-related events."""
        self.warning(f"Security Event: {event_type}", 
                    security_event=True,
                    event_type=event_type,
                    details=details,
                    **kwargs)
    
    def log_user_action(self, action: str, user_id: Optional[str] = None, **kwargs) -> None:
        """Log user actions for audit trail."""
        self.info(f"User Action: {action}",
                 user_action=True,
                 action=action,
                 user_id=user_id,
                 **kwargs)


class CorrelationContext:
    """
    Context manager for correlation ID tracking across operations.
    """
    
    def __init__(self, correlation_id_value: Optional[str] = None):
        self.correlation_id_value = correlation_id_value or str(uuid.uuid4())
        self.token = None
    
    def __enter__(self):
        self.token = correlation_id.set(self.correlation_id_value)
        return self.correlation_id_value
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.token:
            correlation_id.reset(self.token)


def setup_structured_logging(
    level: str = "INFO",
    service_name: str = "vpa",
    version: str = "1.0.0",
    log_file: Optional[str] = None
) -> None:
    """
    Setup structured logging for the application.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        service_name: Name of the service for log identification
        version: Version of the service
        log_file: Optional file path for log output
    """
    # Create structured formatter
    formatter = StructuredFormatter(service_name=service_name, version=version)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with structured output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Disable propagation for some noisy loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)


def get_structured_logger(name: str, service_name: str = "vpa", version: str = "1.0.0") -> StructuredLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        service_name: Service name for identification
        version: Service version
        
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name, service_name, version)


# Performance timing decorator
def log_performance(logger: StructuredLogger, operation: Optional[str] = None):
    """
    Decorator to log performance metrics for functions.
    
    Args:
        logger: StructuredLogger instance
        operation: Optional operation name (defaults to function name)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            op_name = operation or func.__name__
            start_time = time.time()
            
            with CorrelationContext():
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    logger.log_performance(op_name, duration, status="success")
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    logger.log_performance(op_name, duration, status="error", error=str(e))
                    raise
        
        return wrapper
    return decorator


# Example usage and testing
if __name__ == "__main__":
    # Setup structured logging
    setup_structured_logging(level="DEBUG", service_name="vpa-test", version="1.0.0")
    
    # Get logger
    logger = get_structured_logger(__name__)
    
    # Test different log types
    with CorrelationContext() as corr_id:
        logger.info("Application starting", component="main", startup=True)
        logger.debug("Debug information", debug_data={"key": "value"})
        logger.warning("Warning message", warning_type="config")
        
        # Test performance logging
        @log_performance(logger, "test_operation")
        def test_function():
            time.sleep(0.1)  # Simulate work
            return "success"
        
        result = test_function()
        
        # Test security event
        logger.log_security_event("login_attempt", {"username": "test", "ip": "127.0.0.1"})
        
        # Test user action
        logger.log_user_action("file_upload", user_id="user123", file_name="test.txt")
        
        # Test exception logging
        try:
            raise ValueError("Test exception")
        except Exception:
            logger.exception("Exception occurred during processing", component="test")
