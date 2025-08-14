"""
VPA AI Logic Compartments Package

This package implements the three AI logic compartments specified in VPA_APP_FINAL_OVERVIEW.md:
- Base AI Logic: Core automation and app management
- Addon AI Logic: Addon-specific automation/workflows
- User AI Logic: Agent-guided custom workflows

All logic compartments integrate with the central event bus and core app service.
"""

from .base_logic import BaseAILogic
from .addon_logic_module import AddonAILogic
from .user_logic import UserAILogic

__all__ = [
    'BaseAILogic',
    'AddonAILogic', 
    'UserAILogic',
]

__version__ = "1.0.0"
__author__ = "VPA Development Team"
__description__ = "AI Logic Compartments for VPA Agentic Automation Platform"
