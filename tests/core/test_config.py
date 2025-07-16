"""
Unit tests for VPA Core Config Module
Tests configuration loading, getting, and setting functionality.
"""

import pytest
import tempfile
import os
import yaml
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

from vpa.core.config import ConfigManager


class TestConfigManager:
    """Test cases for ConfigManager class"""
    
    def test_init_with_default_path(self):
        """Test ConfigManager initialization with default config path"""
        manager = ConfigManager()
        
        assert manager.config_path is not None
        assert manager.config == {}
        assert "default.yaml" in manager.config_path
    
    def test_init_with_custom_path(self):
        """Test ConfigManager initialization with custom config path"""
        custom_path = "/custom/path/config.yaml"
        manager = ConfigManager(custom_path)
        
        assert manager.config_path == custom_path
        assert manager.config == {}
    
    def test_get_default_config_path(self):
        """Test default config path generation"""
        manager = ConfigManager()
        path = manager._get_default_config_path()
        
        assert isinstance(path, str)
        assert path.endswith("default.yaml")
        assert "config" in path
    
    def test_load_existing_config_file(self):
        """Test loading configuration from existing file"""
        test_config = {
            "core": {"log_level": "DEBUG"},
            "plugins": {"enabled": ["audio"]},
            "test_key": "test_value"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            result = manager.load()
            
            assert result == test_config
            assert manager.config == test_config
        finally:
            os.unlink(temp_path)
    
    def test_load_nonexistent_config_file(self):
        """Test loading configuration when file doesn't exist"""
        nonexistent_path = "/nonexistent/path/config.yaml"
        manager = ConfigManager(nonexistent_path)
        
        with patch.object(manager, 'logger') as mock_logger:
            result = manager.load()
            
            # Should return default config
            expected_default = manager._get_default_config()
            assert result == expected_default
            assert manager.config == expected_default
            mock_logger.warning.assert_called_with(f"Config file not found: {nonexistent_path}")
    
    def test_load_invalid_yaml_file(self):
        """Test loading configuration from invalid YAML file"""
        invalid_yaml = "invalid: yaml: content: ["
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(invalid_yaml)
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            
            with patch.object(manager, 'logger') as mock_logger:
                result = manager.load()
                
                # Should return default config on error
                expected_default = manager._get_default_config()
                assert result == expected_default
                assert manager.config == expected_default
                mock_logger.error.assert_called()
        finally:
            os.unlink(temp_path)
    
    def test_load_empty_config_file(self):
        """Test loading empty configuration file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")  # Empty file
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            result = manager.load()
            
            assert result == {}
            assert manager.config == {}
        finally:
            os.unlink(temp_path)
    
    def test_load_file_permission_error(self):
        """Test loading configuration when file has permission errors"""
        manager = ConfigManager("/root/restricted.yaml")  # Typically inaccessible
        
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', side_effect=PermissionError("Access denied")), \
             patch.object(manager, 'logger') as mock_logger:
            
            result = manager.load()
            
            # Should return default config on permission error
            expected_default = manager._get_default_config()
            assert result == expected_default
            assert manager.config == expected_default
            mock_logger.error.assert_called()
    
    def test_get_simple_key(self):
        """Test getting simple configuration key"""
        manager = ConfigManager()
        manager.config = {
            "simple_key": "simple_value",
            "number": 42,
            "boolean": True
        }
        
        assert manager.get("simple_key") == "simple_value"
        assert manager.get("number") == 42
        assert manager.get("boolean") is True
    
    def test_get_nested_key(self):
        """Test getting nested configuration key with dot notation"""
        manager = ConfigManager()
        manager.config = {
            "core": {
                "log_level": "DEBUG",
                "nested": {
                    "deep_value": "found"
                }
            }
        }
        
        assert manager.get("core.log_level") == "DEBUG"
        assert manager.get("core.nested.deep_value") == "found"
    
    def test_get_nonexistent_key_with_default(self):
        """Test getting nonexistent key returns default value"""
        manager = ConfigManager()
        manager.config = {"existing": "value"}
        
        assert manager.get("nonexistent") is None
        assert manager.get("nonexistent", "default") == "default"
        assert manager.get("nested.nonexistent", 42) == 42
    
    def test_get_nonexistent_nested_key(self):
        """Test getting nonexistent nested key"""
        manager = ConfigManager()
        manager.config = {
            "core": {
                "log_level": "INFO"
            }
        }
        
        assert manager.get("core.nonexistent") is None
        assert manager.get("core.nonexistent.deeper") is None
        assert manager.get("nonexistent.key") is None
    
    def test_get_invalid_path_type(self):
        """Test getting key when path encounters non-dict value"""
        manager = ConfigManager()
        manager.config = {
            "core": {
                "log_level": "INFO"  # This is a string, not a dict
            }
        }
        
        # Trying to access deeper into a string should return default
        assert manager.get("core.log_level.deeper") is None
        assert manager.get("core.log_level.deeper", "default") == "default"
    
    def test_set_simple_key(self):
        """Test setting simple configuration key"""
        manager = ConfigManager()
        manager.config = {}
        
        manager.set("simple_key", "simple_value")
        
        assert manager.config["simple_key"] == "simple_value"
    
    def test_set_nested_key_new_structure(self):
        """Test setting nested key that creates new structure"""
        manager = ConfigManager()
        manager.config = {}
        
        manager.set("core.log_level", "DEBUG")
        
        assert manager.config["core"]["log_level"] == "DEBUG"
    
    def test_set_nested_key_existing_structure(self):
        """Test setting nested key in existing structure"""
        manager = ConfigManager()
        manager.config = {
            "core": {
                "existing": "value"
            }
        }
        
        manager.set("core.log_level", "DEBUG")
        manager.set("core.nested.new_key", "new_value")
        
        assert manager.config["core"]["log_level"] == "DEBUG"
        assert manager.config["core"]["existing"] == "value"
        assert manager.config["core"]["nested"]["new_key"] == "new_value"
    
    def test_set_deep_nested_key(self):
        """Test setting deeply nested key"""
        manager = ConfigManager()
        manager.config = {}
        
        manager.set("level1.level2.level3.level4", "deep_value")
        
        assert manager.config["level1"]["level2"]["level3"]["level4"] == "deep_value"
    
    def test_set_overwrites_existing_value(self):
        """Test setting key overwrites existing value"""
        manager = ConfigManager()
        manager.config = {
            "core": {
                "log_level": "INFO"
            }
        }
        
        manager.set("core.log_level", "DEBUG")
        
        assert manager.config["core"]["log_level"] == "DEBUG"
    
    def test_get_default_config_structure(self):
        """Test default configuration structure"""
        manager = ConfigManager()
        default_config = manager._get_default_config()
        
        # Verify default structure
        assert "core" in default_config
        assert "plugins" in default_config
        assert "rag" in default_config
        
        assert default_config["core"]["log_level"] == "INFO"
        assert default_config["core"]["plugins_dir"] == "plugins"
        assert default_config["plugins"]["enabled"] == []
        assert default_config["rag"]["enabled"] is False
    
    def test_config_persistence_across_operations(self):
        """Test that config persists across multiple operations"""
        test_config = {
            "core": {"log_level": "DEBUG"},
            "plugins": {"enabled": ["audio", "rag"]}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_config, f)
            temp_path = f.name
        
        try:
            manager = ConfigManager(temp_path)
            
            # Load config
            loaded = manager.load()
            assert loaded == test_config
            
            # Get values
            assert manager.get("core.log_level") == "DEBUG"
            assert manager.get("plugins.enabled") == ["audio", "rag"]
            
            # Set new values
            manager.set("core.new_setting", "new_value")
            manager.set("plugins.enabled", ["audio", "rag", "cli"])
            
            # Verify all operations worked
            assert manager.get("core.log_level") == "DEBUG"  # Original value preserved
            assert manager.get("core.new_setting") == "new_value"  # New value set
            assert manager.get("plugins.enabled") == ["audio", "rag", "cli"]  # Updated list
            
        finally:
            os.unlink(temp_path)
    
    def test_logger_integration(self):
        """Test that logger is properly initialized and used"""
        manager = ConfigManager("/nonexistent/path/config.yaml")
        
        # Logger should be set up
        assert manager.logger is not None
        assert manager.logger.name == "vpa.core.config"


if __name__ == '__main__':
    pytest.main([__file__])
