"""
Configuration management for VPA.
Handles loading and managing application configuration from YAML files.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the configuration manager."""
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or self._get_default_config_path()
        self.config: Dict[str, Any] = {}
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        # Look for config in project root/config/default.yaml
        current_dir = Path(__file__).parent.parent.parent.parent
        return str(current_dir / "config" / "default.yaml")
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    self.config = yaml.safe_load(file) or {}
                self.logger.info(f"Configuration loaded from {self.config_path}")
            else:
                self.logger.warning(f"Config file not found: {self.config_path}")
                self.config = self._get_default_config()
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            self.config = self._get_default_config()
        
        return self.config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        keys = key.split('.')
        config_ref = self.config
        
        for k in keys[:-1]:
            if k not in config_ref:
                config_ref[k] = {}
            config_ref = config_ref[k]
        
        config_ref[keys[-1]] = value
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "core": {
                "log_level": "INFO",
                "plugins_dir": "plugins"
            },
            "plugins": {
                "enabled": []
            },
            "rag": {
                "enabled": False
            }
        }
