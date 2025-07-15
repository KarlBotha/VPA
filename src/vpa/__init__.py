"""
VPA - Virtual Personal Assistant
"""

__version__ = "0.1.0"
__author__ = "Karl Botha"

from vpa.core.app import App
from vpa.core.config import ConfigManager
from vpa.core.events import EventBus
from vpa.core.plugins import PluginManager

__all__ = ["App", "ConfigManager", "EventBus", "PluginManager"]
