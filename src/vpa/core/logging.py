"""
VPA Core Logging Module.

This module provides structured logging functionality for the VPA system.
It's a compatibility layer that imports from vpa_logging.py.
"""

# Import all public items from vpa_logging
from vpa.core.vpa_logging import (
    StructuredFormatter,
    StructuredLogger,
    CorrelationContext,
    setup_structured_logging,
    get_structured_logger,
    log_performance,
    correlation_id
)

__all__ = [
    "StructuredFormatter",
    "StructuredLogger", 
    "CorrelationContext",
    "setup_structured_logging",
    "get_structured_logger",
    "log_performance",
    "correlation_id"
]