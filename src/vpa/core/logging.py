"""
Compatibility shim for legacy imports.

Keeps zero-bloat by re-exporting the structured logging API from vpa_logging.
Prevents ImportError when modules import `vpa.core.logging`.
"""

import logging
import sys
from typing import Any, Dict, Optional

# Standard logging compatibility
def get_structured_logger(name: str) -> logging.Logger:
    """
    Compatibility shim for get_structured_logger imports.
    Returns a standard Python logger until full structured logging is implemented.
    """
    return logging.getLogger(name)

def get_logger(name: str) -> logging.Logger:
    """Standard logger getter for compatibility."""
    return logging.getLogger(name)

# Basic structured formatter placeholder
class StructuredFormatter(logging.Formatter):
    """
    Compatibility shim for StructuredFormatter.
    Uses standard formatter until structured logging is fully implemented.
    """
    def __init__(self, *args, **kwargs):
        # Use standard format if no format specified
        if not args and 'fmt' not in kwargs:
            kwargs['fmt'] = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        super().__init__(*args, **kwargs)

# Basic structured logger placeholder
class StructuredLogger(logging.Logger):
    """
    Compatibility shim for StructuredLogger.
    Extends standard logger until structured logging is fully implemented.
    """
    def __init__(self, name: str):
        super().__init__(name)
    
    def log_structured(self, level: int, message: str, **kwargs) -> None:
        """Log with structured data (compatibility mode)."""
        extra_info = " | ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
        full_message = f"{message} {extra_info}".strip()
        super().log(level, full_message)

# Correlation context placeholder
class CorrelationContext:
    """Placeholder for correlation context until implemented."""
    
    @staticmethod
    def get_correlation_id() -> Optional[str]:
        return None
    
    @staticmethod
    def set_correlation_id(correlation_id: str) -> None:
        pass

# Module level compatibility
def configure_logging(level: str = "INFO", **kwargs) -> None:
    """Basic logging configuration for compatibility."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def setup_structured_logging(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Compatibility shim for setup_structured_logging.
    Uses basic logging configuration until structured logging is implemented.
    """
    level = "INFO"
    if config and "level" in config:
        level = config["level"]
    configure_logging(level)

def log_performance(operation: str, duration: float, **kwargs) -> None:
    """
    Compatibility shim for performance logging.
    Uses standard logger until performance logging is implemented.
    """
    logger = logging.getLogger("vpa.performance")
    extra_info = " | ".join(f"{k}={v}" for k, v in kwargs.items()) if kwargs else ""
    message = f"Performance: {operation} took {duration:.3f}s {extra_info}".strip()
    logger.info(message)

def log_structured_event(event_type: str, **data) -> None:
    """
    Compatibility shim for structured event logging.
    Uses standard logger until structured logging is implemented.
    """
    logger = logging.getLogger("vpa.events")
    event_data = " | ".join(f"{k}={v}" for k, v in data.items()) if data else ""
    message = f"Event: {event_type} {event_data}".strip()
    logger.info(message)

def correlation_id() -> Optional[str]:
    """
    Compatibility shim for correlation ID generation.
    Returns None until correlation tracking is implemented.
    """
    return None

# Export compatibility symbols
__all__ = [
    'get_structured_logger',
    'get_logger', 
    'StructuredFormatter',
    'StructuredLogger',
    'CorrelationContext',
    'configure_logging',
    'setup_structured_logging',
    'log_performance',
    'log_structured_event',
    'correlation_id'
]