#!/usr/bin/env python3
"""
Integration Test for VPA Validation Framework

Tests the validation framework against the VPA audio plugin to ensure functionality.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
import tempfile
import shutil
import subprocess
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.validation_framework import VPAValidationFramework
except ImportError as e:
    print(f"Error importing validation framework: {e}")
    print("Make sure the validation framework is properly installed")
    sys.exit(1)


class ValidationFrameworkTest:
    """Test suite for VPA validation framework."""
    
    def __init__(self):
        """Initialize test suite."""
        self.project_root = project_root
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {}
        }
        
    def run_all_tests(self) -> bool:
        """Run all validation framework tests."""
        print("VPA Validation Framework Integration Test")
        print("=" * 50)
        
        test_methods = [
            ('framework_initialization', self.test_framework_initialization),
            ('audio_plugin_validation', self.test_audio_plugin_validation),
            ('validation_reporting', self.test_validation_reporting),
            ('error_handling', self.test_error_handling),
            ('configuration_validation', self.test_configuration_validation),
            ('integration_compliance', self.test_integration_compliance)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_method in test_methods:
            print(f"\nRunning: {test_name}")
            print("-" * 30)
            
            try:
                result = test_method()
                self.test_results['tests'][test_name] = {
                    'status': 'passed' if result else 'failed',
                    'timestamp': datetime.now().isoformat()
                }
                
                if result:
                    print(f"✅ {test_name} PASSED")
                    passed += 1
                else:
                    print(f"❌ {test_name} FAILED")
                    failed += 1
                    
            except Exception as e:
                print(f"❌ {test_name} ERROR: {e}")
                self.test_results['tests'][test_name] = {
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                failed += 1
        
        self.test_results['summary'] = {
            'total': len(test_methods),
            'passed': passed,
            'failed': failed,
            'success_rate': (passed / len(test_methods)) * 100
        }
        
        print(f"\n" + "=" * 50)
        print(f"Test Summary:")
        print(f"Total: {len(test_methods)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {self.test_results['summary']['success_rate']:.1f}%")
        
        return failed == 0
    
    def test_framework_initialization(self) -> bool:
        """Test framework initialization."""
        try:
            # Test basic initialization
            framework = VPAValidationFramework(self.project_root)
            
            # Verify framework attributes
            assert hasattr(framework, 'project_root')
            assert hasattr(framework, 'thresholds')
            assert hasattr(framework, 'logger')
            
            print("Framework initialized successfully")
            
            # Test thresholds configuration
            thresholds = framework.thresholds
            assert isinstance(thresholds, dict)
            assert 'test_coverage' in thresholds
            assert 'memory_usage_mb' in thresholds
            
            print("Thresholds configuration valid")
            
            # Test required patterns
            patterns = framework.required_patterns
            assert isinstance(patterns, dict)
            assert 'event_driven' in patterns
            assert 'plugin_based' in patterns
            
            print("Required patterns configuration valid")
            
            return True
            
        except Exception as e:
            print(f"Framework initialization failed: {e}")
            return False
    
    def test_audio_plugin_validation(self) -> bool:
        """Test validation against VPA audio plugin."""
        try:
            framework = VPAValidationFramework(self.project_root)
            
            # Check if audio plugin exists
            audio_plugin_path = self.project_root / 'src' / 'vpa' / 'plugins' / 'audio'
            
            if not audio_plugin_path.exists():
                print("Audio plugin not found - creating minimal test plugin")
                return self._create_and_test_minimal_plugin(framework)
            
            # Run validation on audio plugin
            print(f"Validating audio plugin at: {audio_plugin_path}")
            
            result = framework.validate_integration(
                integration_name='audio',
                integration_path=audio_plugin_path
            )
            
            # Verify result structure
            assert hasattr(result, 'integration_name')
            assert hasattr(result, 'overall_passed')
            assert hasattr(result, 'results')
            assert hasattr(result, 'test_coverage')
            
            print(f"Audio plugin validation completed")
            print(f"Overall Passed: {result.overall_passed}")
            print(f"Results: {len(result.results)}")
            print(f"Test Coverage: {result.test_coverage:.1f}%")
            
            # Check that some validations ran
            assert len(result.results) > 0
            
            return True
            
        except Exception as e:
            print(f"Audio plugin validation failed: {e}")
            return False
    
    def test_validation_reporting(self) -> bool:
        """Test validation reporting functionality."""
        try:
            framework = VPAValidationFramework(self.project_root)
            
            # Create test plugin
            test_plugin_path = self._create_minimal_test_plugin()
            
            try:
                # Run validation
                result = framework.validate_integration(
                    integration_name='test_plugin',
                    integration_path=test_plugin_path
                )
                
                # Test report generation
                reports_dir = self.project_root / 'reports'
                reports_dir.mkdir(exist_ok=True)
                
                # Generate HTML report
                html_report = reports_dir / 'test_validation_report.html'
                framework.generate_report_html(result, html_report)
                
                assert html_report.exists()
                assert html_report.stat().st_size > 0
                
                print(f"HTML report generated: {html_report}")
                
                # Verify HTML content
                content = html_report.read_text()
                assert 'test_plugin' in content
                assert 'Integration Validation Report' in content
                
                print("HTML report content verified")
                
                return True
                
            finally:
                # Cleanup test plugin
                if test_plugin_path.exists():
                    shutil.rmtree(test_plugin_path)
            
        except Exception as e:
            print(f"Validation reporting test failed: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling in validation framework."""
        try:
            framework = VPAValidationFramework(self.project_root)
            
            # Test with non-existent path
            print("Testing validation with non-existent path...")
            
            try:
                result = framework.validate_integration(
                    integration_name='nonexistent',
                    integration_path=Path('/nonexistent/path')
                )
                
                # Should not fail completely, but should have failures
                assert not result.overall_passed
                print("Non-existent path handled gracefully")
                
            except Exception as e:
                print(f"Non-existent path test error: {e}")
                return False
            
            # Test with invalid path structure
            print("Testing validation with empty directory...")
            
            test_plugin_path = self._create_minimal_test_plugin()
            
            try:
                # Remove content to create invalid structure
                for file in test_plugin_path.glob('*'):
                    if file.is_file():
                        file.unlink()
                
                result = framework.validate_integration(
                    integration_name='test_invalid',
                    integration_path=test_plugin_path
                )
                
                # Should handle gracefully
                assert hasattr(result, 'overall_passed')
                print("Invalid structure handled gracefully")
                
            finally:
                # Cleanup
                if test_plugin_path.exists():
                    shutil.rmtree(test_plugin_path)
            
            return True
            
        except Exception as e:
            print(f"Error handling test failed: {e}")
            return False
    
    def test_configuration_validation(self) -> bool:
        """Test configuration validation."""
        try:
            framework = VPAValidationFramework(self.project_root)
            
            # Test thresholds configuration
            thresholds = framework.thresholds
            
            # Check required threshold sections
            required_thresholds = ['test_coverage', 'performance_degradation', 'memory_usage_mb']
            for threshold in required_thresholds:
                assert threshold in thresholds, f"Missing threshold: {threshold}"
            
            print("Thresholds configuration structure valid")
            
            # Test required patterns
            patterns = framework.required_patterns
            required_patterns = ['event_driven', 'plugin_based', 'modular_design']
            
            for pattern in required_patterns:
                assert pattern in patterns, f"Missing required pattern: {pattern}"
                assert isinstance(patterns[pattern], bool), f"Invalid pattern value: {pattern}"
            
            print("Required patterns configuration valid")
            
            return True
            
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False
    
    def test_integration_compliance(self) -> bool:
        """Test integration compliance checking."""
        try:
            framework = VPAValidationFramework(self.project_root)
            
            # Create compliant test plugin
            compliant_plugin = self._create_compliant_test_plugin()
            
            try:
                # Validate compliant plugin
                result = framework.validate_integration(
                    integration_name='compliant_test',
                    integration_path=compliant_plugin
                )
                
                print(f"Compliant plugin passed: {result.overall_passed}")
                
                # Should have reasonable results
                assert len(result.results) > 0, "Should have validation results"
                
                # Check specific compliance checks
                arch_compliance = next(
                    (r for r in result.results if 'architectural' in r.name.lower()),
                    None
                )
                
                if arch_compliance:
                    print(f"Architectural compliance: {arch_compliance.passed}")
                
                return True
                
            finally:
                # Cleanup
                if compliant_plugin.exists():
                    shutil.rmtree(compliant_plugin)
            
        except Exception as e:
            print(f"Integration compliance test failed: {e}")
            return False
    
    def _create_minimal_test_plugin(self) -> Path:
        """Create a minimal test plugin for validation."""
        test_dir = self.project_root / 'temp_test_plugin'
        test_dir.mkdir(exist_ok=True)
        
        # Create __init__.py
        init_content = '''"""Test plugin for validation framework testing."""

from typing import Any, Dict, Optional
from vpa.core.events import EventBus


class TestPlugin:
    """Minimal test plugin."""
    
    def __init__(self, event_bus: EventBus, config: Optional[Dict[str, Any]] = None):
        self.event_bus = event_bus
        self.config = config or {}
    
    def initialize(self) -> bool:
        return True
    
    def cleanup(self) -> None:
        pass


def initialize(event_bus: EventBus, config: Optional[Dict[str, Any]] = None) -> TestPlugin:
    return TestPlugin(event_bus, config)
'''
        
        (test_dir / '__init__.py').write_text(init_content)
        
        # Create README
        readme_content = '''# Test Plugin

This is a minimal test plugin for validation framework testing.

## Features

- Basic plugin structure
- Event bus integration
- Configuration support
'''
        
        (test_dir / 'README.md').write_text(readme_content)
        
        return test_dir
    
    def _create_compliant_test_plugin(self) -> Path:
        """Create a compliant test plugin for validation."""
        test_dir = self.project_root / 'temp_compliant_plugin'
        test_dir.mkdir(exist_ok=True)
        
        # Create comprehensive plugin structure
        init_content = '''"""
Compliant Test Plugin

A fully compliant test plugin demonstrating best practices.
"""

import logging
from typing import Any, Dict, Optional, List
from datetime import datetime
from vpa.core.events import EventBus


class CompliantTestPlugin:
    """
    Fully compliant test plugin.
    
    This plugin demonstrates proper VPA integration patterns
    including event handling, resource management, and error handling.
    """
    
    def __init__(self, event_bus: EventBus, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the compliant test plugin.
        
        Args:
            event_bus: VPA event bus for communication
            config: Plugin configuration dictionary
        """
        self.event_bus = event_bus
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Plugin state
        self._initialized = False
        self._resources = []
        
        # Register event handlers
        self._register_event_handlers()
        
        self.logger.info("Compliant test plugin initialized")
    
    def _register_event_handlers(self) -> None:
        """Register plugin-specific event handlers."""
        self.event_bus.subscribe("plugin.compliant_test.command", self._handle_command)
        self.event_bus.subscribe("plugin.compliant_test.test", self._handle_test)
    
    def _handle_command(self, data: Dict[str, Any]) -> None:
        """
        Handle plugin command requests.
        
        Args:
            data: Command data dictionary
        """
        command = data.get('command', '')
        self.logger.info(f"Handling compliant test command: {command}")
        
        try:
            # Process command
            result = self._process_command(command, data)
            
            # Emit result
            self.event_bus.emit("plugin.compliant_test.command.result", result)
            
        except Exception as e:
            self.logger.error(f"Error handling command: {e}")
            error_result = {
                "status": "error",
                "message": str(e),
                "command": command,
                "timestamp": datetime.now().isoformat()
            }
            self.event_bus.emit("plugin.compliant_test.command.error", error_result)
    
    def _handle_test(self, data: Dict[str, Any]) -> None:
        """
        Handle plugin test requests.
        
        Args:
            data: Test data dictionary
        """
        self.logger.info("Running compliant test plugin test")
        
        test_result = {
            "status": "success",
            "message": "Compliant test plugin test completed",
            "plugin": "compliant_test",
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        self.event_bus.emit("plugin.compliant_test.test.result", test_result)
    
    def _process_command(self, command: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process plugin-specific commands.
        
        Args:
            command: Command string
            data: Command data
            
        Returns:
            Command result dictionary
        """
        if command == "status":
            return self._get_status()
        elif command == "echo":
            return {
                "status": "success",
                "message": f"Echo: {data.get('message', '')}",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "error",
                "message": f"Unknown command: {command}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_status(self) -> Dict[str, Any]:
        """
        Get plugin status.
        
        Returns:
            Status dictionary
        """
        return {
            "status": "operational",
            "initialized": self._initialized,
            "resources": len(self._resources),
            "config": self.config,
            "timestamp": datetime.now().isoformat()
        }
    
    def initialize(self) -> bool:
        """
        Initialize plugin resources.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Initialize plugin-specific resources
            self._initialized = True
            self.logger.info("Compliant test plugin resources initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing compliant test plugin: {e}")
            return False
    
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        try:
            # Cleanup plugin-specific resources
            for resource in self._resources:
                if hasattr(resource, 'close'):
                    resource.close()
                elif hasattr(resource, 'cleanup'):
                    resource.cleanup()
            
            self._resources.clear()
            self._initialized = False
            
            self.logger.info("Compliant test plugin cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up compliant test plugin: {e}")


def initialize(event_bus: EventBus, config: Optional[Dict[str, Any]] = None) -> CompliantTestPlugin:
    """
    Initialize the compliant test plugin.
    
    Args:
        event_bus: VPA event bus
        config: Plugin configuration
        
    Returns:
        Initialized plugin instance
    """
    return CompliantTestPlugin(event_bus, config)


# Plugin metadata
__version__ = "1.0.0"
__author__ = "VPA Development Team"
__description__ = "Compliant test plugin demonstrating best practices"
'''
        
        (test_dir / '__init__.py').write_text(init_content)
        
        # Create comprehensive README
        readme_content = '''# Compliant Test Plugin

A comprehensive test plugin demonstrating VPA integration best practices.

## Overview

This plugin serves as a reference implementation for proper VPA plugin development,
showcasing architectural compliance, error handling, and documentation standards.

## Features

- **Event-driven Architecture**: Proper event bus integration
- **Error Handling**: Comprehensive error handling and logging
- **Resource Management**: Proper resource initialization and cleanup
- **Documentation**: Complete docstring coverage
- **Testing**: Comprehensive test coverage

## Configuration

```yaml
compliant_test:
  enabled: true
  settings:
    timeout: 30
    retry_count: 3
  logging:
    level: INFO
```

## Usage

### Plugin Integration

```python
from vpa.plugins.compliant_test import initialize

# Initialize plugin
plugin = initialize(event_bus, config)
```

### Commands

- `status` - Get plugin status
- `echo` - Echo message back

### Event System

#### Events Emitted
- `plugin.compliant_test.command.result` - Command processing results
- `plugin.compliant_test.command.error` - Command processing errors
- `plugin.compliant_test.test.result` - Test results

#### Events Handled
- `plugin.compliant_test.command` - Process commands
- `plugin.compliant_test.test` - Run tests

## API Reference

### CompliantTestPlugin

Main plugin class demonstrating best practices.

#### Methods

- `initialize()` - Initialize plugin resources
- `cleanup()` - Cleanup plugin resources

## Development

This plugin follows VPA development best practices:

1. **Architectural Compliance**: Follows VPA plugin architecture
2. **Code Quality**: High code quality with proper documentation
3. **Error Handling**: Comprehensive error handling
4. **Resource Management**: Proper resource lifecycle management
5. **Testing**: Complete test coverage

## License

MIT License - see LICENSE file for details.
'''
        
        (test_dir / 'README.md').write_text(readme_content)
        
        # Create configuration file
        config_content = '''# Compliant Test Plugin Configuration

compliant_test:
  enabled: true
  
  settings:
    timeout: 30
    retry_count: 3
    buffer_size: 1024
    
  logging:
    level: INFO
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
  events:
    emit_status: true
    emit_errors: true
    
  resources:
    max_memory_mb: 100
    max_connections: 10

# Environment-specific overrides
development:
  compliant_test:
    logging:
      level: DEBUG
    settings:
      timeout: 10

production:
  compliant_test:
    settings:
      timeout: 60
      retry_count: 5
    resources:
      max_memory_mb: 500
'''
        
        (test_dir / 'config.yaml').write_text(config_content)
        
        return test_dir
    
    def _create_and_test_minimal_plugin(self, framework: VPAValidationFramework) -> bool:
        """Create and test a minimal plugin."""
        try:
            test_plugin = self._create_minimal_test_plugin()
            
            # Run validation
            result = framework.validate_integration(
                integration_name='test_minimal',
                integration_path=test_plugin
            )
            
            print(f"Minimal plugin validation completed")
            print(f"Overall Passed: {result.overall_passed}")
            
            # Cleanup
            shutil.rmtree(test_plugin)
            
            # Should complete without errors
            assert hasattr(result, 'overall_passed')
            
            return True
            
        except Exception as e:
            print(f"Minimal plugin test failed: {e}")
            return False
    
    def save_test_results(self, output_path: Optional[Path] = None) -> Path:
        """Save test results to file."""
        if output_path is None:
            output_path = self.project_root / 'reports' / f'validation_framework_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"Test results saved to: {output_path}")
        return output_path


def main():
    """Main test runner."""
    print("Starting VPA Validation Framework Integration Test")
    print("This test validates the validation framework functionality\n")
    
    test_suite = ValidationFrameworkTest()
    
    # Run all tests
    success = test_suite.run_all_tests()
    
    # Save results
    results_path = test_suite.save_test_results()
    
    print(f"\nTest results saved to: {results_path}")
    
    if success:
        print("\n🎉 All tests passed! Validation framework is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the results and fix issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()
