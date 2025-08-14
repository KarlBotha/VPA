"""
Feature flags for optional domains. Defaults OFF to preserve zero-bloat and fast imports.
Enable by setting environment variables to "1".
"""
import os

def is_enterprise_enabled() -> bool:
    """Check if enterprise features are enabled."""
    return os.getenv("VPA_ENABLE_ENTERPRISE", "0") == "1"

def is_advanced_llm_enabled() -> bool:
    """Check if advanced LLM features are enabled."""
    return os.getenv("VPA_ENABLE_ADVANCED_LLM", "0") == "1"

def is_gui_enabled() -> bool:
    """Check if GUI features are enabled."""
    return os.getenv("VPA_ENABLE_GUI", "1") == "1"  # GUI defaults to enabled

def is_voice_enabled() -> bool:
    """Check if voice features are enabled."""
    return os.getenv("VPA_ENABLE_VOICE", "1") == "1"  # Voice defaults to enabled

# Export flags
__all__ = [
    'is_enterprise_enabled',
    'is_advanced_llm_enabled', 
    'is_gui_enabled',
    'is_voice_enabled'
]
