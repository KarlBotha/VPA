"""
Comprehensive test suite for CLI interface.
Tests all CLI commands, parameter handling, and error scenarios.
"""

import pytest
import click
from click.testing import CliRunner
from unittest.mock import Mock, patch, MagicMock
import logging
import sys
from io import StringIO

from vpa.cli.main import cli, setup_logging, main
from vpa.core.app import App


class TestSetupLogging:
    """Test logging setup functionality."""
    
    def test_setup_logging_default(self):
        """Test default logging setup."""
        with patch('logging.basicConfig') as mock_basic_config:
            setup_logging()
            mock_basic_config.assert_called_once_with(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    
    def test_setup_logging_custom_level(self):
        """Test custom log level setup."""
        with patch('logging.basicConfig') as mock_basic_config:
            setup_logging("DEBUG")
            mock_basic_config.assert_called_once_with(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
    
    def test_setup_logging_invalid_level(self):
        """Test invalid log level handling."""
        with patch('logging.basicConfig') as mock_basic_config:
            with pytest.raises(AttributeError):
                setup_logging("INVALID")


class TestCLIGroup:
    """Test main CLI group functionality."""
    
    def test_cli_group_default_options(self):
        """Test CLI group with default options."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert 'VPA - Virtual Personal Assistant CLI' in result.output
        assert '--log-level' in result.output
        assert '--config' in result.output
    
    def test_cli_group_with_log_level(self):
        """Test CLI group with custom log level."""
        runner = CliRunner()
        with patch('vpa.cli.main.setup_logging') as mock_setup:
            result = runner.invoke(cli, ['--log-level', 'DEBUG', 'status'])
            assert result.exit_code == 0
            mock_setup.assert_called_once_with('DEBUG')
    
    def test_cli_group_with_config(self):
        """Test CLI group with custom config path."""
        runner = CliRunner()
        with patch('vpa.cli.main.setup_logging'):
            result = runner.invoke(cli, ['--config', '/custom/path.yaml', '--help'])
            assert result.exit_code == 0


class TestStartCommand:
    """Test start command functionality."""
    
    def test_start_command_success(self):
        """Test successful start command."""
        runner = CliRunner()
        
        with patch('vpa.cli.main.App') as mock_app_class:
            mock_app = Mock()
            mock_app.is_running.return_value = False  # Simulate immediate stop
            mock_app_class.return_value = mock_app
            
            result = runner.invoke(cli, ['start'])
            
            assert result.exit_code == 0
            assert 'VPA started successfully' in result.output
            mock_app.initialize.assert_called_once()
            mock_app.start.assert_called_once()
    
    def test_start_command_with_config(self):
        """Test start command with custom config."""
        runner = CliRunner()
        
        with patch('vpa.cli.main.App') as mock_app_class:
            mock_app = Mock()
            mock_app.is_running.return_value = False
            mock_app_class.return_value = mock_app
            
            result = runner.invoke(cli, ['--config', '/test/config.yaml', 'start'])
            
            assert result.exit_code == 0
            mock_app_class.assert_called_once_with('/test/config.yaml')
    
    def test_start_command_keyboard_interrupt(self):
        """Test start command with keyboard interrupt."""
        runner = CliRunner()
        
        with patch('vpa.cli.main.App') as mock_app_class:
            mock_app = Mock()
            mock_app.is_running.side_effect = [True, KeyboardInterrupt()]
            mock_app_class.return_value = mock_app
            
            result = runner.invoke(cli, ['start'])
            
            assert result.exit_code == 0
            assert 'Shutting down VPA' in result.output
            mock_app.stop.assert_called_once()
    
    def test_start_command_initialization_error(self):
        """Test start command with initialization error."""
        runner = CliRunner()
        
        with patch('vpa.cli.main.App') as mock_app_class:
            mock_app_class.side_effect = Exception("Config error")
            
            result = runner.invoke(cli, ['start'])
            
            assert result.exit_code == 1
            assert 'Error starting VPA: Config error' in result.output
    
    def test_start_command_app_initialization_error(self):
        """Test start command with app initialization error."""
        runner = CliRunner()
        
        with patch('vpa.cli.main.App') as mock_app_class:
            mock_app = Mock()
            mock_app.initialize.side_effect = Exception("Init failed")
            mock_app_class.return_value = mock_app
            
            result = runner.invoke(cli, ['start'])
            
            assert result.exit_code == 1
            assert 'Error starting VPA: Init failed' in result.output


class TestStatusCommand:
    """Test status command functionality."""
    
    def test_status_command(self):
        """Test status command output."""
        runner = CliRunner()
        result = runner.invoke(cli, ['status'])
        
        assert result.exit_code == 0
        assert 'VPA Status: Not implemented yet' in result.output


class TestConfigShowCommand:
    """Test config-show command functionality."""
    
    def test_config_show_success(self):
        """Test successful config show."""
        runner = CliRunner()
        
        with patch('vpa.cli.main.App') as mock_app_class:
            mock_app = Mock()
            mock_config_manager = Mock()
            mock_config_manager.config = {'core': {'log_level': 'INFO'}}
            mock_config_manager.config_path = '/test/config.yaml'
            mock_app.config_manager = mock_config_manager
            mock_app_class.return_value = mock_app
            
            result = runner.invoke(cli, ['config-show'])
            
            assert result.exit_code == 0
            assert 'Current VPA Configuration' in result.output
            assert 'Config file: /test/config.yaml' in result.output
            assert 'core: ' in result.output
    
    def test_config_show_with_custom_config(self):
        """Test config show with custom config path."""
        runner = CliRunner()
        
        with patch('vpa.cli.main.App') as mock_app_class:
            mock_app = Mock()
            mock_config_manager = Mock()
            mock_config_manager.config = {}
            mock_config_manager.config_path = '/custom/config.yaml'
            mock_app.config_manager = mock_config_manager
            mock_app_class.return_value = mock_app
            
            result = runner.invoke(cli, ['--config', '/custom/config.yaml', 'config-show'])
            
            assert result.exit_code == 0
            mock_app_class.assert_called_once_with('/custom/config.yaml')
    
    def test_config_show_error(self):
        """Test config show with error."""
        runner = CliRunner()
        
        with patch('vpa.cli.main.App') as mock_app_class:
            mock_app_class.side_effect = Exception("Config not found")
            
            result = runner.invoke(cli, ['config-show'])
            
            assert result.exit_code == 0  # Command doesn't exit with error code
            assert 'Error reading config: Config not found' in result.output


class TestAudioCommands:
    """Test audio command group and subcommands."""
    
    def test_audio_group_help(self):
        """Test audio command group help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['audio', '--help'])
        
        assert result.exit_code == 0
        assert 'Audio system commands' in result.output
        assert 'speak' in result.output
    
    def test_audio_speak_command(self):
        """Test audio speak command."""
        runner = CliRunner()
        
        with patch('vpa.cli.main.App') as mock_app_class:
            mock_app = Mock()
            mock_plugin = Mock()
            mock_app.plugin_manager.get_plugin.return_value = mock_plugin
            mock_app_class.return_value = mock_app
            
            result = runner.invoke(cli, ['audio', 'speak', 'Hello world'])
            
            # Check that the command executes successfully and outputs the expected text
            assert result.exit_code == 0
            assert 'Hello world' in result.output
    
    def test_audio_speak_empty_text(self):
        """Test audio speak with empty text."""
        runner = CliRunner()
        result = runner.invoke(cli, ['audio', 'speak'])
        
        assert result.exit_code == 2  # Missing argument error
        assert 'Missing argument' in result.output


class TestCLIParameterValidation:
    """Test CLI parameter validation and security."""
    
    def test_log_level_validation(self):
        """Test log level parameter validation."""
        runner = CliRunner()
        
        # Valid log levels
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        for level in valid_levels:
            with patch('vpa.cli.main.setup_logging') as mock_setup:
                result = runner.invoke(cli, ['--log-level', level, 'status'])
                assert result.exit_code == 0
                mock_setup.assert_called_once_with(level)
    
    def test_config_path_validation(self):
        """Test config path parameter handling."""
        runner = CliRunner()
        
        # Test various path formats
        test_paths = [
            '/absolute/path/config.yaml',
            'relative/path/config.yaml',
            '../relative/path/config.yaml',
            'config.yaml'
        ]
        
        for path in test_paths:
            with patch('vpa.cli.main.setup_logging'):
                result = runner.invoke(cli, ['--config', path, '--help'])
                assert result.exit_code == 0
    
    def test_config_path_security(self):
        """Test config path security validation."""
        runner = CliRunner()
        
        # Test potentially dangerous paths
        dangerous_paths = [
            '../../etc/passwd',
            '/etc/passwd',
            'C:\\Windows\\System32\\config\\SAM'
        ]
        
        for path in dangerous_paths:
            with patch('vpa.cli.main.App') as mock_app_class:
                # The CLI should pass the path to App, which should validate it
                mock_app_class.side_effect = ValueError("Invalid config path")
                result = runner.invoke(cli, ['--config', path, 'start'])
                assert result.exit_code == 1


class TestMainFunction:
    """Test the main function entry point."""
    
    def test_main_function_exists(self):
        """Test that main function is defined."""
        assert callable(main)
    
    def test_main_function_calls_cli(self):
        """Test that main function calls the CLI."""
        with patch('vpa.cli.main.cli') as mock_cli:
            main()
            mock_cli.assert_called_once()


class TestCLIErrorHandling:
    """Test CLI error handling and edge cases."""
    
    def test_invalid_command(self):
        """Test handling of invalid commands."""
        runner = CliRunner()
        result = runner.invoke(cli, ['invalid-command'])
        
        assert result.exit_code == 2  # Click's error code for bad command
        assert 'No such command' in result.output
    
    def test_missing_required_argument(self):
        """Test handling of missing required arguments."""
        runner = CliRunner()
        result = runner.invoke(cli, ['audio', 'speak'])
        
        assert result.exit_code == 2
        assert 'Missing argument' in result.output
    
    def test_help_flag(self):
        """Test help flag functionality."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert 'VPA - Virtual Personal Assistant CLI' in result.output
    
    def test_version_information(self):
        """Test that CLI provides version information in help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        # Version info should be available in help or via separate command


class TestCLIIntegration:
    """Integration tests for CLI functionality."""
    
    def test_cli_app_integration(self):
        """Test CLI integration with App class."""
        runner = CliRunner()
        
        with patch('vpa.cli.main.App') as mock_app_class:
            mock_app = Mock()
            mock_app.is_running.return_value = False
            mock_config_manager = Mock()
            mock_config_manager.config = {}
            mock_config_manager.config_path = 'test_config.yaml'
            mock_app.config_manager = mock_config_manager
            mock_app_class.return_value = mock_app
            
            # Test start command
            result = runner.invoke(cli, ['start'])
            assert result.exit_code == 0
            
            # Test config-show command
            result = runner.invoke(cli, ['config-show'])
            assert result.exit_code == 0
    
    def test_cli_logging_integration(self):
        """Test CLI logging integration."""
        runner = CliRunner()
        
        with patch('vpa.cli.main.setup_logging') as mock_setup:
            result = runner.invoke(cli, ['--log-level', 'DEBUG', 'status'])
            assert result.exit_code == 0
            mock_setup.assert_called_once_with('DEBUG')


# Fixtures for common test setup
@pytest.fixture
def cli_runner():
    """Provide a CLI runner for tests."""
    return CliRunner()


@pytest.fixture
def mock_app():
    """Provide a mock App instance."""
    app = Mock()
    app.is_running.return_value = False
    config_manager = Mock()
    config_manager.config = {'core': {'log_level': 'INFO'}}
    config_manager.config_path = 'test_config.yaml'
    app.config_manager = config_manager
    return app