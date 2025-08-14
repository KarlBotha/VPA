"""
Configuration management for VPA.
Handles loading and managing application configuration from YAML files.
"""

import os
import yaml
import logging
import json
from typing import Dict, Any, Optional
from pathlib import Path
from cryptography.fernet import Fernet
import base64


class SecureConfigManager:
    """Manages application configuration with secure secret handling."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the configuration manager."""
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or self._get_default_config_path()
        self.config: Dict[str, Any] = {}
        self._encryption_key = self._get_or_create_encryption_key()
        self._secure_fields = {'api_keys', 'passwords', 'secrets', 'tokens', 'credentials'}
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        # Look for config in project root/config/default.yaml
        current_dir = Path(__file__).parent.parent.parent.parent
        return str(current_dir / "config" / "default.yaml")
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for secure storage."""
        key_file = Path.home() / ".vpa" / "config.key"
        
        try:
            if key_file.exists():
                with open(key_file, 'rb') as f:
                    return f.read()
            else:
                # Create new key
                key_file.parent.mkdir(exist_ok=True)
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                # Set secure permissions
                os.chmod(key_file, 0o600)
                self.logger.info("Created new encryption key for secure configuration")
                return key
        except Exception as e:
            self.logger.error(f"Error handling encryption key: {e}")
            # Fallback to session-only key
            return Fernet.generate_key()
    
    def _encrypt_value(self, value: str) -> str:
        """Encrypt a sensitive value."""
        try:
            fernet = Fernet(self._encryption_key)
            encrypted = fernet.encrypt(value.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            self.logger.error(f"Error encrypting value: {e}")
            return value
    
    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a sensitive value."""
        try:
            fernet = Fernet(self._encryption_key)
            decoded = base64.urlsafe_b64decode(encrypted_value.encode())
            return fernet.decrypt(decoded).decode()
        except Exception as e:
            self.logger.error(f"Error decrypting value: {e}")
            return encrypted_value
    
    def _is_secure_field(self, key: str) -> bool:
        """Check if a field contains sensitive data."""
        key_lower = key.lower()
        return any(secure_term in key_lower for secure_term in self._secure_fields)
    
    def _process_config_values(self, config: Dict[str, Any], encrypt: bool = False) -> Dict[str, Any]:
        """Process configuration values for encryption/decryption."""
        processed = {}
        
        for key, value in config.items():
            if isinstance(value, dict):
                processed[key] = self._process_config_values(value, encrypt)
            elif isinstance(value, str) and self._is_secure_field(key):
                if encrypt:
                    processed[key] = self._encrypt_value(value)
                else:
                    processed[key] = self._decrypt_value(value)
            else:
                processed[key] = value
        
        return processed
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    raw_config = yaml.safe_load(file) or {}
                
                # Decrypt sensitive values
                self.config = self._process_config_values(raw_config, encrypt=False)
                self.logger.info(f"Configuration loaded from {self.config_path}")
            else:
                self.logger.warning(f"Config file not found: {self.config_path}")
                self.config = self._get_default_config()
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            self.config = self._get_default_config()
        
        return self.config
    
    def save(self) -> None:
        """Save configuration to file with encrypted sensitive values."""
        try:
            # Encrypt sensitive values before saving
            encrypted_config = self._process_config_values(self.config, encrypt=True)
            
            # Ensure config directory exists
            Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(encrypted_config, file, default_flow_style=False)
            
            # Set secure file permissions
            os.chmod(self.config_path, 0o600)
            
            self.logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
    
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
    
    def set_secure(self, key: str, value: str) -> None:
        """Set a secure configuration value (will be encrypted)."""
        # Ensure the key is marked as secure
        if not self._is_secure_field(key.split('.')[-1]):
            self.logger.warning(f"Key '{key}' may not be recognized as secure. Consider using a key containing: {', '.join(self._secure_fields)}")
        
        self.set(key, value)
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary with sensitive values hidden."""
        summary = {}
        
        def hide_sensitive(obj, path=""):
            if isinstance(obj, dict):
                result = {}
                for k, v in obj.items():
                    current_path = f"{path}.{k}" if path else k
                    if self._is_secure_field(k):
                        result[k] = "[ENCRYPTED]"
                    else:
                        result[k] = hide_sensitive(v, current_path)
                return result
            else:
                return obj
        
        return hide_sensitive(self.config)
    
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
            },
            "security": {
                "encryption_enabled": True,
                "secure_config_version": "1.0"
            }
        }


# Backward compatibility
ConfigManager = SecureConfigManager
