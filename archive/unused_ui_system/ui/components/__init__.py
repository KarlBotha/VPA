"""
VPA UI Components Package
Modern UI components for chat-first interface.
"""

from .chat_area import ChatArea
from .input_area import InputArea
from .resource_monitor import ResourceMonitor
from .settings_panel import SettingsPanel
from .addon_panel import AddonPanel

__all__ = [
    'ChatArea',
    'InputArea', 
    'ResourceMonitor',
    'SettingsPanel',
    'AddonPanel'
]
