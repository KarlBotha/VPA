"""
Unit tests for VPA Core Plugins Module
Tests plugin loading, management, and lifecycle functionality.
"""

import pytest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock, mock_open, call
from pathlib import Path
import importlib
import shutil

from vpa.core.plugins import PluginManager
from vpa.core.events import EventBus


class TestPluginManager:
    """Test cases for PluginManager class"""
    
    @pytest.fixture
    def event_bus(self):
        """Create a test event bus"""
        bus = EventBus()
        bus.initialize()
        return bus
    
    @pytest.fixture
    def plugin_manager(self, event_bus):
        """Create a test plugin manager"""
        return PluginManager(event_bus)
    
    def test_init(self, event_bus):
        """Test PluginManager initialization"""
        manager = PluginManager(event_bus)
        
        assert manager.event_bus is event_bus
        assert manager.loaded_plugins == {}
        assert manager.logger is not None
        assert manager.logger.name == "vpa.core.plugins"
        assert manager.plugins_dir is not None
        assert "plugins" in manager.plugins_dir
    
    def test_get_plugins_directory(self, plugin_manager):
        """Test getting plugins directory path"""
        plugins_dir = plugin_manager._get_plugins_directory()
        
        assert isinstance(plugins_dir, str)
        assert plugins_dir.endswith("plugins")
        # Should be relative to src/vpa/plugins
        assert "vpa" in plugins_dir
    
    def test_load_plugins_no_directory(self, plugin_manager):
        """Test loading plugins when plugins directory doesn't exist"""
        with patch('os.path.exists', return_value=False), \
             patch.object(plugin_manager, 'logger') as mock_logger:
            
            plugin_manager.load_plugins()
            
            mock_logger.warning.assert_called_with(f"Plugins directory not found: {plugin_manager.plugins_dir}")
            assert len(plugin_manager.loaded_plugins) == 0
    
    def test_load_plugins_with_specific_names(self, plugin_manager):
        """Test loading specific named plugins"""
        with patch('os.path.exists', return_value=True), \
             patch.object(plugin_manager, '_load_plugin') as mock_load, \
             patch.object(plugin_manager, 'logger') as mock_logger:
            
            plugin_names = ["audio", "rag", "custom"]
            plugin_manager.load_plugins(plugin_names)
            
            # Should call _load_plugin for each specified plugin
            expected_calls = [call("audio"), call("rag"), call("custom")]
            mock_load.assert_has_calls(expected_calls)
            mock_logger.info.assert_any_call("Loading plugins...")
    
    def test_load_plugins_discover_all(self, plugin_manager):
        """Test loading plugins by discovery"""
        with patch('os.path.exists', return_value=True), \
             patch.object(plugin_manager, '_discover_and_load_plugins') as mock_discover, \
             patch.object(plugin_manager, 'logger') as mock_logger:
            
            plugin_manager.load_plugins()
            
            mock_discover.assert_called_once()
            mock_logger.info.assert_any_call("Loading plugins...")
    
    def test_load_plugins_adds_to_sys_path(self, plugin_manager):
        """Test that plugins directory is added to sys.path"""
        original_path = sys.path.copy()
        
        try:
            with patch('os.path.exists', return_value=True), \
                 patch.object(plugin_manager, '_discover_and_load_plugins'):
                
                # Ensure plugins_dir is not in path initially
                if plugin_manager.plugins_dir in sys.path:
                    sys.path.remove(plugin_manager.plugins_dir)
                
                plugin_manager.load_plugins()
                
                # Should add plugins_dir to sys.path
                assert plugin_manager.plugins_dir in sys.path
        finally:
            # Restore original sys.path
            sys.path[:] = original_path
    
    def test_load_plugins_sys_path_already_exists(self, plugin_manager):
        """Test that plugins directory is not duplicated in sys.path"""
        original_path = sys.path.copy()
        
        try:
            with patch('os.path.exists', return_value=True), \
                 patch.object(plugin_manager, '_discover_and_load_plugins'):
                
                # Add plugins_dir to path first
                if plugin_manager.plugins_dir not in sys.path:
                    sys.path.insert(0, plugin_manager.plugins_dir)
                
                initial_count = sys.path.count(plugin_manager.plugins_dir)
                plugin_manager.load_plugins()
                
                # Should not duplicate in sys.path
                assert sys.path.count(plugin_manager.plugins_dir) == initial_count
        finally:
            # Restore original sys.path
            sys.path[:] = original_path
    
    def test_discover_and_load_plugins_python_files(self, plugin_manager):
        """Test discovering and loading Python file plugins"""
        mock_files = ["audio.py", "rag.py", "__init__.py", "test.txt", "config.yaml"]
        
        with patch('os.listdir', return_value=mock_files), \
             patch('os.path.join', side_effect=lambda a, b: f"{a}/{b}"), \
             patch('os.path.isdir', return_value=False), \
             patch.object(plugin_manager, '_load_plugin') as mock_load:
            
            plugin_manager._discover_and_load_plugins()
            
            # Should only load .py files that don't start with __
            expected_calls = [call("audio"), call("rag")]
            mock_load.assert_has_calls(expected_calls, any_order=True)
            assert mock_load.call_count == 2
    
    def test_discover_and_load_plugins_directories(self, plugin_manager):
        """Test discovering and loading directory plugins"""
        mock_items = ["audio", "rag", "not_a_plugin", "config.yaml"]
        
        with patch('os.listdir', return_value=mock_items), \
             patch('os.path.join', side_effect=lambda a, b: f"{a}/{b}"), \
             patch('os.path.isdir', side_effect=lambda x: x.endswith(("audio", "rag", "not_a_plugin"))), \
             patch('os.path.exists', side_effect=lambda x: x.endswith(("audio/__init__.py", "rag/__init__.py"))), \
             patch.object(plugin_manager, '_load_plugin') as mock_load:
            
            plugin_manager._discover_and_load_plugins()
            
            # Should only load directories with __init__.py
            expected_calls = [call("audio"), call("rag")]
            mock_load.assert_has_calls(expected_calls, any_order=True)
            assert mock_load.call_count == 2
    
    def test_load_plugin_with_plugin_class(self, plugin_manager):
        """Test loading plugin that has Plugin class"""
        mock_module = MagicMock()
        mock_plugin_instance = MagicMock()
        mock_module.Plugin.return_value = mock_plugin_instance
        
        with patch('importlib.import_module', return_value=mock_module), \
             patch.object(plugin_manager, 'logger') as mock_logger, \
             patch.object(plugin_manager.event_bus, 'emit') as mock_emit:
            
            plugin_manager._load_plugin("test_plugin")
            
            mock_module.Plugin.assert_called_once_with(plugin_manager.event_bus)
            assert plugin_manager.loaded_plugins["test_plugin"] is mock_plugin_instance
            mock_logger.info.assert_called_with("Loaded plugin: test_plugin")
            mock_emit.assert_called_once_with("plugin.loaded", {"name": "test_plugin", "instance": mock_plugin_instance})
    
    def test_load_plugin_with_initialize_function(self, plugin_manager):
        """Test loading plugin that has initialize function"""
        mock_module = MagicMock()
        mock_plugin_instance = MagicMock()
        del mock_module.Plugin  # No Plugin class
        mock_module.initialize.return_value = mock_plugin_instance
        
        with patch('importlib.import_module', return_value=mock_module), \
             patch.object(plugin_manager, 'logger') as mock_logger, \
             patch.object(plugin_manager.event_bus, 'emit') as mock_emit:
            
            plugin_manager._load_plugin("test_plugin")
            
            mock_module.initialize.assert_called_once_with(plugin_manager.event_bus)
            assert plugin_manager.loaded_plugins["test_plugin"] is mock_plugin_instance
            mock_logger.info.assert_called_with("Loaded plugin: test_plugin")
            mock_emit.assert_called_once_with("plugin.loaded", {"name": "test_plugin", "instance": mock_plugin_instance})
    
    def test_load_plugin_no_valid_interface(self, plugin_manager):
        """Test loading plugin with no valid interface"""
        mock_module = MagicMock()
        del mock_module.Plugin  # No Plugin class
        del mock_module.initialize  # No initialize function
        
        with patch('importlib.import_module', return_value=mock_module), \
             patch.object(plugin_manager, 'logger') as mock_logger, \
             patch.object(plugin_manager.event_bus, 'emit') as mock_emit:
            
            plugin_manager._load_plugin("test_plugin")
            
            assert "test_plugin" not in plugin_manager.loaded_plugins
            mock_logger.warning.assert_called_with("No valid plugin interface found in: test_plugin")
            mock_emit.assert_not_called()
    
    def test_load_plugin_import_error(self, plugin_manager):
        """Test loading plugin that fails to import"""
        with patch('importlib.import_module', side_effect=ImportError("Module not found")), \
             patch.object(plugin_manager, 'logger') as mock_logger, \
             patch.object(plugin_manager.event_bus, 'emit') as mock_emit:
            
            plugin_manager._load_plugin("bad_plugin")
            
            assert "bad_plugin" not in plugin_manager.loaded_plugins
            mock_logger.error.assert_called_with("Failed to load plugin bad_plugin: Module not found")
            mock_emit.assert_not_called()
    
    def test_load_plugin_plugin_class_exception(self, plugin_manager):
        """Test loading plugin when Plugin class constructor raises exception"""
        mock_module = MagicMock()
        mock_module.Plugin.side_effect = Exception("Plugin init failed")
        
        with patch('importlib.import_module', return_value=mock_module), \
             patch.object(plugin_manager, 'logger') as mock_logger:
            
            plugin_manager._load_plugin("error_plugin")
            
            assert "error_plugin" not in plugin_manager.loaded_plugins
            mock_logger.error.assert_called_with("Failed to load plugin error_plugin: Plugin init failed")
    
    def test_unload_plugins_with_cleanup(self, plugin_manager):
        """Test unloading plugins that have cleanup methods"""
        mock_plugin1 = MagicMock()
        mock_plugin2 = MagicMock()
        
        plugin_manager.loaded_plugins = {
            "plugin1": mock_plugin1,
            "plugin2": mock_plugin2
        }
        
        with patch.object(plugin_manager, 'logger') as mock_logger, \
             patch.object(plugin_manager.event_bus, 'emit') as mock_emit:
            
            plugin_manager.unload_plugins()
            
            # Should call cleanup on both plugins
            mock_plugin1.cleanup.assert_called_once()
            mock_plugin2.cleanup.assert_called_once()
            
            # Should emit unload events
            expected_calls = [
                call("plugin.unloaded", {"name": "plugin1"}),
                call("plugin.unloaded", {"name": "plugin2"})
            ]
            mock_emit.assert_has_calls(expected_calls, any_order=True)
            
            # Should log unload messages
            mock_logger.info.assert_any_call("Unloading plugins...")
            mock_logger.info.assert_any_call("Unloaded plugin: plugin1")
            mock_logger.info.assert_any_call("Unloaded plugin: plugin2")
            
            # Should clear loaded_plugins dict
            assert len(plugin_manager.loaded_plugins) == 0
    
    def test_unload_plugins_no_cleanup_method(self, plugin_manager):
        """Test unloading plugins that don't have cleanup methods"""
        mock_plugin = MagicMock()
        del mock_plugin.cleanup  # Remove cleanup method
        
        plugin_manager.loaded_plugins = {"plugin1": mock_plugin}
        
        with patch.object(plugin_manager, 'logger') as mock_logger, \
             patch.object(plugin_manager.event_bus, 'emit') as mock_emit:
            
            plugin_manager.unload_plugins()
            
            # Should not raise error for missing cleanup
            mock_emit.assert_called_once_with("plugin.unloaded", {"name": "plugin1"})
            mock_logger.info.assert_any_call("Unloaded plugin: plugin1")
            assert len(plugin_manager.loaded_plugins) == 0
    
    def test_unload_plugins_cleanup_exception(self, plugin_manager):
        """Test unloading plugins when cleanup raises exception"""
        mock_plugin1 = MagicMock()
        mock_plugin2 = MagicMock()
        mock_plugin1.cleanup.side_effect = Exception("Cleanup failed")
        
        plugin_manager.loaded_plugins = {
            "plugin1": mock_plugin1,
            "plugin2": mock_plugin2
        }
        
        with patch.object(plugin_manager, 'logger') as mock_logger, \
             patch.object(plugin_manager.event_bus, 'emit') as mock_emit:
            
            plugin_manager.unload_plugins()
            
            # Should log error for plugin1 but continue with plugin2
            mock_logger.error.assert_called_with("Error unloading plugin plugin1: Cleanup failed")
            mock_plugin2.cleanup.assert_called_once()
            
            # Should still clear all plugins
            assert len(plugin_manager.loaded_plugins) == 0
    
    def test_get_plugin_exists(self, plugin_manager):
        """Test getting an existing plugin"""
        mock_plugin = MagicMock()
        plugin_manager.loaded_plugins = {"test_plugin": mock_plugin}
        
        result = plugin_manager.get_plugin("test_plugin")
        
        assert result is mock_plugin
    
    def test_get_plugin_not_exists(self, plugin_manager):
        """Test getting a non-existent plugin"""
        plugin_manager.loaded_plugins = {"other_plugin": MagicMock()}
        
        result = plugin_manager.get_plugin("nonexistent_plugin")
        
        assert result is None
    
    def test_get_plugin_empty_plugins(self, plugin_manager):
        """Test getting plugin when no plugins are loaded"""
        result = plugin_manager.get_plugin("any_plugin")
        
        assert result is None
    
    def test_list_plugins_with_plugins(self, plugin_manager):
        """Test listing plugins when plugins are loaded"""
        plugin_manager.loaded_plugins = {
            "audio": MagicMock(),
            "rag": MagicMock(),
            "custom": MagicMock()
        }
        
        result = plugin_manager.list_plugins()
        
        assert set(result) == {"audio", "rag", "custom"}
        assert len(result) == 3
    
    def test_list_plugins_empty(self, plugin_manager):
        """Test listing plugins when no plugins are loaded"""
        result = plugin_manager.list_plugins()
        
        assert result == []
    
    def test_complex_plugin_lifecycle(self, plugin_manager):
        """Test complete plugin lifecycle with multiple operations"""
        # Setup mock plugins
        mock_audio_module = MagicMock()
        mock_audio_plugin = MagicMock()
        mock_audio_module.Plugin.return_value = mock_audio_plugin
        
        mock_rag_module = MagicMock()
        mock_rag_plugin = MagicMock()
        del mock_rag_module.Plugin  # Use initialize instead
        mock_rag_module.initialize.return_value = mock_rag_plugin
        
        def import_side_effect(name):
            if name == "audio":
                return mock_audio_module
            elif name == "rag":
                return mock_rag_module
            else:
                raise ImportError(f"Module {name} not found")
        
        with patch('os.path.exists', return_value=True), \
             patch.object(plugin_manager, '_discover_and_load_plugins') as mock_discover, \
             patch('importlib.import_module', side_effect=import_side_effect), \
             patch.object(plugin_manager, 'logger') as mock_logger, \
             patch.object(plugin_manager.event_bus, 'emit') as mock_emit:
            
            # Simulate discovery calling _load_plugin for each plugin
            def discover_side_effect():
                plugin_manager._load_plugin("audio")
                plugin_manager._load_plugin("rag")
            
            mock_discover.side_effect = discover_side_effect
            
            # Load plugins
            plugin_manager.load_plugins()
            
            # Verify loading
            assert len(plugin_manager.loaded_plugins) == 2
            assert plugin_manager.get_plugin("audio") is mock_audio_plugin
            assert plugin_manager.get_plugin("rag") is mock_rag_plugin
            assert set(plugin_manager.list_plugins()) == {"audio", "rag"}
            
            # Verify load events were emitted
            expected_load_calls = [
                call("plugin.loaded", {"name": "audio", "instance": mock_audio_plugin}),
                call("plugin.loaded", {"name": "rag", "instance": mock_rag_plugin})
            ]
            mock_emit.assert_has_calls(expected_load_calls, any_order=True)
            
            # Reset mock for unload testing
            mock_emit.reset_mock()
            
            # Unload plugins
            plugin_manager.unload_plugins()
            
            # Verify unloading
            assert len(plugin_manager.loaded_plugins) == 0
            assert plugin_manager.get_plugin("audio") is None
            assert plugin_manager.list_plugins() == []
            
            # Verify cleanup was called
            mock_audio_plugin.cleanup.assert_called_once()
            mock_rag_plugin.cleanup.assert_called_once()
            
            # Verify unload events were emitted
            expected_unload_calls = [
                call("plugin.unloaded", {"name": "audio"}),
                call("plugin.unloaded", {"name": "rag"})
            ]
            mock_emit.assert_has_calls(expected_unload_calls, any_order=True)
    
    def test_event_bus_integration(self, plugin_manager):
        """Test that plugin manager properly integrates with event bus"""
        # Test that event bus is passed to plugins
        mock_module = MagicMock()
        mock_plugin = MagicMock()
        mock_module.Plugin.return_value = mock_plugin
        
        with patch('importlib.import_module', return_value=mock_module), \
             patch.object(plugin_manager.event_bus, 'emit') as mock_emit:
            plugin_manager._load_plugin("test_plugin")
            
            # Plugin should be initialized with event bus
            mock_module.Plugin.assert_called_once_with(plugin_manager.event_bus)
            
            # Event should be emitted
            mock_emit.assert_called_once()
    
    def test_logging_integration(self, plugin_manager):
        """Test that plugin manager properly uses logging"""
        assert plugin_manager.logger is not None
        assert plugin_manager.logger.name == "vpa.core.plugins"
        
        # Test that various operations log appropriately
        with patch.object(plugin_manager, 'logger') as mock_logger:
            # Test directory not found logging
            with patch('os.path.exists', return_value=False):
                plugin_manager.load_plugins()
                mock_logger.warning.assert_called()
            
            # Test successful load logging
            mock_module = MagicMock()
            mock_module.Plugin.return_value = MagicMock()
            
            with patch('os.path.exists', return_value=True), \
                 patch('importlib.import_module', return_value=mock_module):
                plugin_manager._load_plugin("test")
                mock_logger.info.assert_any_call("Loaded plugin: test")


if __name__ == '__main__':
    pytest.main([__file__])
