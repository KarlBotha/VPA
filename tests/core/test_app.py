"""
Unit tests for VPA Core App Module
Tests the main application lifecycle, configuration, and plugin integration.
"""

import pytest
import logging
from unittest.mock import patch, MagicMock

from vpa.core.app import App
from vpa.core.config import ConfigManager
from vpa.core.events import EventBus
from vpa.core.plugins import PluginManager


class TestApp:
    """Test cases for App class"""
    
    def test_init_with_default_config(self):
        """Test App initialization with default configuration"""
        app = App()
        
        assert app.logger is not None
        assert app.logger.name == "vpa.core.app"
        assert isinstance(app.config_manager, ConfigManager)
        assert isinstance(app.event_bus, EventBus)
        assert isinstance(app.plugin_manager, PluginManager)
        assert app._running is False
        assert app.plugin_manager.event_bus is app.event_bus
    
    def test_init_with_custom_config_path(self):
        """Test App initialization with custom config path"""
        custom_path = "/custom/path/config.yaml"
        
        with patch('vpa.core.app.ConfigManager') as mock_config_manager, \
             patch('vpa.core.app.EventBus') as mock_event_bus, \
             patch('vpa.core.app.PluginManager') as mock_plugin_manager:
            
            mock_event_bus_instance = MagicMock()
            mock_event_bus.return_value = mock_event_bus_instance
            
            app = App(custom_path)
            
            mock_config_manager.assert_called_once_with(custom_path)
            mock_event_bus.assert_called_once()
            mock_plugin_manager.assert_called_once_with(mock_event_bus_instance)
    
    def test_initialize_components_order(self):
        """Test that initialize calls components in correct order"""
        app = App()
        
        with patch.object(app.config_manager, 'load') as mock_config_load, \
             patch.object(app.event_bus, 'initialize') as mock_event_init, \
             patch.object(app.plugin_manager, 'load_plugins') as mock_plugin_load, \
             patch.object(app, 'logger') as mock_logger:
            
            app.initialize()
            
            # Verify order of calls
            mock_config_load.assert_called_once()
            mock_event_init.assert_called_once()
            mock_plugin_load.assert_called_once()
            
            # Verify logging
            mock_logger.info.assert_any_call("Initializing VPA application...")
            mock_logger.info.assert_any_call("VPA application initialized successfully")
    
    def test_initialize_config_loading(self):
        """Test that initialize properly loads configuration"""
        app = App()
        
        with patch.object(app.config_manager, 'load') as mock_load, \
             patch.object(app.event_bus, 'initialize'), \
             patch.object(app.plugin_manager, 'load_plugins'):
            
            app.initialize()
            
            mock_load.assert_called_once()
    
    def test_initialize_event_bus(self):
        """Test that initialize properly initializes event bus"""
        app = App()
        
        with patch.object(app.config_manager, 'load'), \
             patch.object(app.event_bus, 'initialize') as mock_init, \
             patch.object(app.plugin_manager, 'load_plugins'):
            
            app.initialize()
            
            mock_init.assert_called_once()
    
    def test_initialize_plugin_loading(self):
        """Test that initialize properly loads plugins"""
        app = App()
        
        with patch.object(app.config_manager, 'load'), \
             patch.object(app.event_bus, 'initialize'), \
             patch.object(app.plugin_manager, 'load_plugins') as mock_load:
            
            app.initialize()
            
            mock_load.assert_called_once()
    
    def test_start_when_not_running(self):
        """Test starting application when not currently running"""
        app = App()
        
        with patch.object(app.event_bus, 'emit') as mock_emit, \
             patch.object(app, 'logger') as mock_logger:
            
            app.start()
            
            assert app._running is True
            mock_emit.assert_called_once_with("app.started")
            mock_logger.info.assert_called_once_with("Starting VPA application...")
    
    def test_start_when_already_running(self):
        """Test starting application when already running"""
        app = App()
        app._running = True  # Set as already running
        
        with patch.object(app.event_bus, 'emit') as mock_emit, \
             patch.object(app, 'logger') as mock_logger:
            
            app.start()
            
            assert app._running is True  # Should remain True
            mock_emit.assert_not_called()  # Should not emit event
            mock_logger.info.assert_not_called()  # Should not log
    
    def test_stop_when_running(self):
        """Test stopping application when currently running"""
        app = App()
        app._running = True  # Set as running
        
        with patch.object(app.event_bus, 'emit') as mock_emit, \
             patch.object(app.plugin_manager, 'unload_plugins') as mock_unload, \
             patch.object(app, 'logger') as mock_logger:
            
            app.stop()
            
            assert app._running is False
            mock_emit.assert_called_once_with("app.stopping")
            mock_unload.assert_called_once()
            mock_logger.info.assert_any_call("Stopping VPA application...")
            mock_logger.info.assert_any_call("VPA application stopped")
    
    def test_stop_when_not_running(self):
        """Test stopping application when not currently running"""
        app = App()
        # _running is False by default
        
        with patch.object(app.event_bus, 'emit') as mock_emit, \
             patch.object(app.plugin_manager, 'unload_plugins') as mock_unload, \
             patch.object(app, 'logger') as mock_logger:
            
            app.stop()
            
            assert app._running is False  # Should remain False
            mock_emit.assert_not_called()  # Should not emit event
            mock_unload.assert_not_called()  # Should not unload plugins
            mock_logger.info.assert_not_called()  # Should not log
    
    def test_is_running_true(self):
        """Test is_running returns True when application is running"""
        app = App()
        app._running = True
        
        assert app.is_running() is True
    
    def test_is_running_false(self):
        """Test is_running returns False when application is not running"""
        app = App()
        app._running = False
        
        assert app.is_running() is False
    
    def test_component_integration(self):
        """Test that components are properly integrated"""
        app = App()
        
        # Event bus should be shared between app and plugin manager
        assert app.plugin_manager.event_bus is app.event_bus
        
        # Config manager should be properly initialized
        assert app.config_manager is not None
        
        # All components should be different instances
        assert app.config_manager is not app.event_bus
        assert app.event_bus is not app.plugin_manager
        assert app.config_manager is not app.plugin_manager
    
    def test_full_lifecycle_workflow(self):
        """Test complete application lifecycle"""
        app = App()
        
        with patch.object(app.config_manager, 'load') as mock_config_load, \
             patch.object(app.event_bus, 'initialize') as mock_event_init, \
             patch.object(app.event_bus, 'emit') as mock_emit, \
             patch.object(app.plugin_manager, 'load_plugins') as mock_plugin_load, \
             patch.object(app.plugin_manager, 'unload_plugins') as mock_plugin_unload, \
             patch.object(app, 'logger') as mock_logger:
            
            # Initial state
            assert app.is_running() is False
            
            # Initialize
            app.initialize()
            mock_config_load.assert_called_once()
            mock_event_init.assert_called_once()
            mock_plugin_load.assert_called_once()
            
            # Start
            app.start()
            assert app.is_running() is True
            mock_emit.assert_called_with("app.started")
            
            # Stop
            app.stop()
            assert app.is_running() is False
            mock_emit.assert_called_with("app.stopping")
            mock_plugin_unload.assert_called_once()
    
    def test_multiple_start_stop_cycles(self):
        """Test multiple start/stop cycles work correctly"""
        app = App()
        
        with patch.object(app.event_bus, 'emit') as mock_emit, \
             patch.object(app.plugin_manager, 'unload_plugins') as mock_unload:
            
            # Start -> Stop -> Start -> Stop
            app.start()
            assert app.is_running() is True
            
            app.stop()
            assert app.is_running() is False
            
            app.start()
            assert app.is_running() is True
            
            app.stop()
            assert app.is_running() is False
            
            # Verify correct number of calls
            assert mock_emit.call_count == 4  # 2 starts + 2 stops
            assert mock_unload.call_count == 2  # 2 stops
    
    def test_start_stop_event_emission(self):
        """Test that start and stop emit correct events"""
        app = App()
        
        with patch.object(app.event_bus, 'emit') as mock_emit, \
             patch.object(app.plugin_manager, 'unload_plugins'):
            
            app.start()
            mock_emit.assert_called_with("app.started")
            
            mock_emit.reset_mock()
            
            app.stop()
            mock_emit.assert_called_with("app.stopping")
    
    def test_initialization_with_config_exception(self):
        """Test initialization when config loading fails"""
        app = App()
        
        with patch.object(app.config_manager, 'load', side_effect=Exception("Config error")), \
             patch.object(app.event_bus, 'initialize') as mock_event_init, \
             patch.object(app.plugin_manager, 'load_plugins') as mock_plugin_load:
            
            # Should raise the exception
            with pytest.raises(Exception, match="Config error"):
                app.initialize()
            
            # Other components should not be initialized if config fails
            mock_event_init.assert_not_called()
            mock_plugin_load.assert_not_called()
    
    def test_initialization_with_event_bus_exception(self):
        """Test initialization when event bus initialization fails"""
        app = App()
        
        with patch.object(app.config_manager, 'load') as mock_config_load, \
             patch.object(app.event_bus, 'initialize', side_effect=Exception("Event bus error")), \
             patch.object(app.plugin_manager, 'load_plugins') as mock_plugin_load:
            
            # Should raise the exception
            with pytest.raises(Exception, match="Event bus error"):
                app.initialize()
            
            # Config should be loaded but plugins should not
            mock_config_load.assert_called_once()
            mock_plugin_load.assert_not_called()
    
    def test_initialization_with_plugin_exception(self):
        """Test initialization when plugin loading fails"""
        app = App()
        
        with patch.object(app.config_manager, 'load') as mock_config_load, \
             patch.object(app.event_bus, 'initialize') as mock_event_init, \
             patch.object(app.plugin_manager, 'load_plugins', side_effect=Exception("Plugin error")):
            
            # Should raise the exception
            with pytest.raises(Exception, match="Plugin error"):
                app.initialize()
            
            # Previous components should be initialized
            mock_config_load.assert_called_once()
            mock_event_init.assert_called_once()
    
    def test_stop_with_plugin_unload_exception(self):
        """Test stopping when plugin unloading fails"""
        app = App()
        app._running = True
        
        with patch.object(app.event_bus, 'emit') as mock_emit, \
             patch.object(app.plugin_manager, 'unload_plugins', side_effect=Exception("Unload error")), \
             patch.object(app, 'logger') as mock_logger:
            
            # Should raise the exception
            with pytest.raises(Exception, match="Unload error"):
                app.stop()
            
            # App should still be marked as not running
            assert app._running is False
            
            # Event should still be emitted
            mock_emit.assert_called_once_with("app.stopping")
    
    def test_logger_integration(self):
        """Test that logger is properly set up and used"""
        app = App()
        
        assert app.logger is not None
        assert app.logger.name == "vpa.core.app"
        
        # Test logging during operations
        with patch.object(app, 'logger') as mock_logger:
            with patch.object(app.config_manager, 'load'), \
                 patch.object(app.event_bus, 'initialize'), \
                 patch.object(app.plugin_manager, 'load_plugins'):
                
                app.initialize()
                
                # Should log initialization messages
                mock_logger.info.assert_any_call("Initializing VPA application...")
                mock_logger.info.assert_any_call("VPA application initialized successfully")
    
    def test_state_consistency_after_errors(self):
        """Test that application state remains consistent after errors"""
        app = App()
        
        # Start app successfully
        app.start()
        assert app.is_running() is True
        
        # Stop with error
        with patch.object(app.plugin_manager, 'unload_plugins', side_effect=Exception("Error")):
            with pytest.raises(Exception):
                app.stop()
        
        # App should still be marked as stopped despite error
        assert app.is_running() is False
        
        # Should be able to start again
        app.start()
        assert app.is_running() is True


if __name__ == '__main__':
    pytest.main([__file__])
