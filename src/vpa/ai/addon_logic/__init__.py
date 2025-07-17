"""
VPA AI Addon Logic Package

Provides a compartmentalized addon system with complete isolation and centralized management.
Each addon has its own dedicated logic module and the coordinator manages the entire system.

Structure:
- base_addon_logic.py - Base addon logic abstract class
- addon_logic_coordinator.py - Central addon logic coordinator
- google_logic.py - Google addon compartment
- microsoft_logic.py - Microsoft addon compartment  
- whatsapp_logic.py - WhatsApp addon compartment
- telegram_logic.py - Telegram addon compartment
- discord_logic.py - Discord addon compartment
- weather_logic.py - Weather addon compartment
- windows_logic.py - Windows addon compartment
- websearch_logic.py - Web Search addon compartment
"""

from .base_addon_logic import BaseAddonLogic, AddonWorkflow, AddonCapability
from .addon_logic_coordinator import AddonLogicCoordinator
from .google_logic import GoogleAddonLogic
from .microsoft_logic import MicrosoftAddonLogic
from .whatsapp_logic import WhatsAppAddonLogic
from .telegram_logic import TelegramAddonLogic
from .discord_logic import DiscordAddonLogic
from .weather_logic import WeatherAddonLogic
from .windows_logic import WindowsAddonLogic
from .websearch_logic import WebSearchAddonLogic

__all__ = [
    # Base classes and coordinator
    "BaseAddonLogic",
    "AddonWorkflow", 
    "AddonCapability",
    "AddonLogicCoordinator",
    
    # Individual addon logic classes
    "GoogleAddonLogic",
    "MicrosoftAddonLogic",
    "WhatsAppAddonLogic",
    "TelegramAddonLogic",
    "DiscordAddonLogic",
    "WeatherAddonLogic",
    "WindowsAddonLogic",
    "WebSearchAddonLogic"
]
