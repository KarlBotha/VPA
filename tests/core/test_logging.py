"""
Tests for VPA Structured Logging System.
Comprehensive test coverage for structured logging functionality.
"""

import json
import logging
import pytest
import time
import uuid
from io import StringIO
from unittest.mock import patch, Mock

from vpa.core.logging import (
    StructuredFormatter,
    StructuredLogger,
    CorrelationContext,
    setup_structured_logging,
    get_structured_logger,
    log_performance,
    correlation_id
)


class TestStructuredFormatter:
    """Test cases for StructuredFormatter."""
    
    def test_formatter_initialization(self):
        """Test formatter initialization with default values."""
        formatter = StructuredFormatter()
        assert formatter.service_name == "vpa"
        assert formatter.version == "1.0.0"
    
    def test_formatter_initialization_custom(self):
        """Test formatter initialization with custom values."""
        formatter = StructuredFormatter(service_name="test-service", version="2.0.0")
        assert formatter.service_name == "test-service"
        assert formatter.version == "2.0.0"
    
    def test_format_basic_log_record(self):
        """Test formatting of basic log record."""
        formatter = StructuredFormatter()
        
        # Create test log record
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=123,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Format the record
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        # Verify structure
        assert "timestamp" in log_data
        assert log_data["service"] == "vpa"
        assert log_data["version"] == "1.0.0"
        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test.logger"
        assert log_data["message"] == "Test message"
        assert log_data["line"] == 123
    
    def test_format_with_correlation_id(self):
        """Test formatting with correlation ID in context."""
        formatter = StructuredFormatter()
        test_corr_id = str(uuid.uuid4())
        
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=123,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Set correlation ID in context
        with CorrelationContext(test_corr_id):
            formatted = formatter.format(record)
            log_data = json.loads(formatted)
            assert log_data["correlation_id"] == test_corr_id
    
    def test_format_with_exception(self):
        """Test formatting with exception information."""
        formatter = StructuredFormatter()
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
            record = logging.LogRecord(
                name="test.logger",
                level=logging.ERROR,
                pathname="/test/path.py",
                lineno=123,
                msg="Error occurred",
                args=(),
                exc_info=exc_info
            )
            
            formatted = formatter.format(record)
            log_data = json.loads(formatted)
            
            assert "exception" in log_data
            assert log_data["exception"]["type"] == "ValueError"
            assert log_data["exception"]["message"] == "Test exception"
            assert "traceback" in log_data["exception"]
    
    def test_format_with_extra_fields(self):
        """Test formatting with extra fields."""
        formatter = StructuredFormatter()
        
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/test/path.py",
            lineno=123,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Add extra fields
        record.custom_field = "custom_value"
        record.request_id = "req_123"
        
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        assert "extra" in log_data
        assert log_data["extra"]["custom_field"] == "custom_value"
        assert log_data["extra"]["request_id"] == "req_123"


class TestStructuredLogger:
    """Test cases for StructuredLogger."""
    
    def setup_method(self):
        """Setup test environment."""
        self.logger = StructuredLogger("test.logger")
        self.log_stream = StringIO()
        self.handler = logging.StreamHandler(self.log_stream)
        self.handler.setFormatter(StructuredFormatter())
        
        # Setup test logger
        logging.getLogger("test.logger").handlers.clear()
        logging.getLogger("test.logger").addHandler(self.handler)
        logging.getLogger("test.logger").setLevel(logging.DEBUG)
    
    def get_last_log_entry(self):
        """Get the last log entry as parsed JSON."""
        log_output = self.log_stream.getvalue().strip()
        if log_output:
            last_line = log_output.split('\n')[-1]
            try:
                return json.loads(last_line)
            except json.JSONDecodeError:
                return None
        return None
    
    def assert_log_entry_exists(self):
        """Assert that a log entry exists and return it."""
        log_entry = self.get_last_log_entry()
        assert log_entry is not None, f"No log entry found. Log output: {self.log_stream.getvalue()}"
        return log_entry
    
    def test_debug_logging(self):
        """Test debug level logging."""
        self.logger.debug("Debug message", component="test")
        log_entry = self.assert_log_entry_exists()
        
        assert log_entry["level"] == "DEBUG"
        assert log_entry["message"] == "Debug message"
        assert log_entry["extra"]["component"] == "test"
    
    def test_info_logging(self):
        """Test info level logging."""
        self.logger.info("Info message", operation="test_op")
        log_entry = self.get_last_log_entry()
        
        assert log_entry["level"] == "INFO"
        assert log_entry["message"] == "Info message"
        assert log_entry["extra"]["operation"] == "test_op"
    
    def test_warning_logging(self):
        """Test warning level logging."""
        self.logger.warning("Warning message", warning_type="config")
        log_entry = self.get_last_log_entry()
        
        assert log_entry["level"] == "WARNING"
        assert log_entry["message"] == "Warning message"
        assert log_entry["extra"]["warning_type"] == "config"
    
    def test_error_logging(self):
        """Test error level logging."""
        self.logger.error("Error message", error_code="E001")
        log_entry = self.get_last_log_entry()
        
        assert log_entry["level"] == "ERROR"
        assert log_entry["message"] == "Error message"
        assert log_entry["extra"]["error_code"] == "E001"
    
    def test_critical_logging(self):
        """Test critical level logging."""
        self.logger.critical("Critical message", severity="high")
        log_entry = self.get_last_log_entry()
        
        assert log_entry["level"] == "CRITICAL"
        assert log_entry["message"] == "Critical message"
        assert log_entry["extra"]["severity"] == "high"
    
    def test_performance_logging(self):
        """Test performance logging."""
        self.logger.log_performance("test_operation", 0.123, status="success")
        log_entry = self.get_last_log_entry()
        
        assert log_entry["level"] == "INFO"
        assert "Performance: test_operation" in log_entry["message"]
        assert log_entry["extra"]["operation"] == "test_operation"
        assert log_entry["extra"]["duration_ms"] == 123.0
        assert log_entry["extra"]["performance"] is True
        assert log_entry["extra"]["status"] == "success"
    
    def test_security_event_logging(self):
        """Test security event logging."""
        details = {"user": "test_user", "ip": "127.0.0.1"}
        self.logger.log_security_event("login_attempt", details, severity="medium")
        log_entry = self.get_last_log_entry()
        
        assert log_entry["level"] == "WARNING"
        assert "Security Event: login_attempt" in log_entry["message"]
        assert log_entry["extra"]["security_event"] is True
        assert log_entry["extra"]["event_type"] == "login_attempt"
        assert log_entry["extra"]["details"] == details
        assert log_entry["extra"]["severity"] == "medium"
    
    def test_user_action_logging(self):
        """Test user action logging."""
        self.logger.log_user_action("file_upload", user_id="user123", file_name="test.txt")
        log_entry = self.get_last_log_entry()
        
        assert log_entry["level"] == "INFO"
        assert "User Action: file_upload" in log_entry["message"]
        assert log_entry["extra"]["user_action"] is True
        assert log_entry["extra"]["action"] == "file_upload"
        assert log_entry["extra"]["user_id"] == "user123"
        assert log_entry["extra"]["file_name"] == "test.txt"
    
    def test_user_action_logging_no_user_id(self):
        """Test user action logging without user ID."""
        self.logger.log_user_action("system_backup", location="/backup")
        log_entry = self.get_last_log_entry()
        
        assert log_entry["level"] == "INFO"
        assert log_entry["extra"]["user_id"] is None
        assert log_entry["extra"]["location"] == "/backup"


class TestCorrelationContext:
    """Test cases for CorrelationContext."""
    
    def test_context_creation_with_id(self):
        """Test correlation context creation with provided ID."""
        test_id = "test-correlation-id"
        with CorrelationContext(test_id) as corr_id:
            assert corr_id == test_id
            assert correlation_id.get() == test_id
    
    def test_context_creation_auto_id(self):
        """Test correlation context creation with auto-generated ID."""
        with CorrelationContext() as corr_id:
            assert corr_id is not None
            assert len(corr_id) > 0
            assert correlation_id.get() == corr_id
    
    def test_context_cleanup(self):
        """Test correlation context cleanup after exit."""
        test_id = "test-correlation-id"
        
        # Before context
        assert correlation_id.get() is None
        
        # During context
        with CorrelationContext(test_id):
            assert correlation_id.get() == test_id
        
        # After context
        assert correlation_id.get() is None
    
    def test_nested_contexts(self):
        """Test nested correlation contexts."""
        outer_id = "outer-id"
        inner_id = "inner-id"
        
        with CorrelationContext(outer_id):
            assert correlation_id.get() == outer_id
            
            with CorrelationContext(inner_id):
                assert correlation_id.get() == inner_id
            
            # Should restore outer context
            assert correlation_id.get() == outer_id


class TestSetupStructuredLogging:
    """Test cases for setup_structured_logging function."""
    
    def setup_method(self):
        """Setup test environment."""
        # Store original handlers
        self.original_handlers = logging.getLogger().handlers.copy()
    
    def teardown_method(self):
        """Cleanup test environment."""
        # Restore original handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.handlers.extend(self.original_handlers)
    
    def test_setup_default_config(self):
        """Test setup with default configuration."""
        setup_structured_logging()
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO
        assert len(root_logger.handlers) == 1
        assert isinstance(root_logger.handlers[0], logging.StreamHandler)
        assert isinstance(root_logger.handlers[0].formatter, StructuredFormatter)
    
    def test_setup_custom_level(self):
        """Test setup with custom log level."""
        setup_structured_logging(level="DEBUG")
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG
    
    def test_setup_with_file_handler(self):
        """Test setup with file handler."""
        with patch('logging.FileHandler') as mock_file_handler:
            mock_handler = Mock()
            mock_file_handler.return_value = mock_handler
            
            setup_structured_logging(log_file="/test/log.json")
            
            root_logger = logging.getLogger()
            assert len(root_logger.handlers) == 2  # Console + File
            mock_file_handler.assert_called_once_with("/test/log.json")
    
    def test_setup_service_info(self):
        """Test setup with custom service information."""
        setup_structured_logging(service_name="test-service", version="2.0.0")
        
        root_logger = logging.getLogger()
        formatter = root_logger.handlers[0].formatter
        assert formatter.service_name == "test-service"
        assert formatter.version == "2.0.0"


class TestLogPerformanceDecorator:
    """Test cases for log_performance decorator."""
    
    def setup_method(self):
        """Setup test environment."""
        self.logger = Mock(spec=StructuredLogger)
    
    def test_performance_decorator_success(self):
        """Test performance decorator on successful function."""
        @log_performance(self.logger, "test_operation")
        def test_function():
            time.sleep(0.001)  # Small delay
            return "success"
        
        result = test_function()
        
        assert result == "success"
        self.logger.log_performance.assert_called_once()
        
        # Check call arguments
        call_args = self.logger.log_performance.call_args
        assert call_args[0][0] == "test_operation"  # operation name
        assert call_args[1]["status"] == "success"
        assert len(call_args[0]) == 2  # operation name and duration
        assert isinstance(call_args[0][1], float)  # duration should be a float
    
    def test_performance_decorator_with_exception(self):
        """Test performance decorator when function raises exception."""
        @log_performance(self.logger, "failing_operation")
        def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            failing_function()
        
        self.logger.log_performance.assert_called_once()
        
        # Check call arguments
        call_args = self.logger.log_performance.call_args
        assert call_args[0][0] == "failing_operation"
        assert call_args[1]["status"] == "error"
        assert call_args[1]["error"] == "Test error"
    
    def test_performance_decorator_default_operation_name(self):
        """Test performance decorator with default operation name."""
        @log_performance(self.logger)
        def my_test_function():
            return "done"
        
        my_test_function()
        
        call_args = self.logger.log_performance.call_args
        assert call_args[0][0] == "my_test_function"


class TestGetStructuredLogger:
    """Test cases for get_structured_logger function."""
    
    def test_get_logger_default_params(self):
        """Test getting logger with default parameters."""
        logger = get_structured_logger("test.module")
        
        assert isinstance(logger, StructuredLogger)
        assert logger.service_name == "vpa"
        assert logger.version == "1.0.0"
    
    def test_get_logger_custom_params(self):
        """Test getting logger with custom parameters."""
        logger = get_structured_logger(
            "test.module", 
            service_name="custom-service", 
            version="3.0.0"
        )
        
        assert isinstance(logger, StructuredLogger)
        assert logger.service_name == "custom-service"
        assert logger.version == "3.0.0"


class TestIntegrationScenarios:
    """Integration test scenarios for structured logging."""
    
    def setup_method(self):
        """Setup integration test environment."""
        self.log_stream = StringIO()
        setup_structured_logging()
        
        # Replace console handler with string stream
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        handler = logging.StreamHandler(self.log_stream)
        handler.setFormatter(StructuredFormatter(service_name="test-vpa", version="1.0.0"))
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.DEBUG)
    
    def get_log_entries(self):
        """Get all log entries as parsed JSON objects."""
        log_output = self.log_stream.getvalue().strip()
        if not log_output:
            return []
        
        entries = []
        for line in log_output.split('\n'):
            if line.strip():
                entries.append(json.loads(line))
        return entries
    
    def test_full_workflow_with_correlation(self):
        """Test complete workflow with correlation tracking."""
        logger = get_structured_logger(__name__, service_name="test-vpa")
        
        with CorrelationContext() as corr_id:
            logger.info("Starting operation", operation="test_workflow")
            logger.debug("Processing data", step=1, data_size=100)
            logger.log_performance("data_processing", 0.050, records_processed=100)
            logger.info("Operation completed", operation="test_workflow", status="success")
        
        entries = self.get_log_entries()
        assert len(entries) == 4
        
        # All entries should have the same correlation ID
        for entry in entries:
            assert entry["correlation_id"] == corr_id
            assert entry["service"] == "test-vpa"
        
        # Verify operation flow
        assert entries[0]["message"] == "Starting operation"
        assert entries[1]["message"] == "Processing data"
        assert "Performance: data_processing" in entries[2]["message"]
        assert entries[3]["message"] == "Operation completed"
    
    def test_error_handling_workflow(self):
        """Test error handling and logging workflow."""
        logger = get_structured_logger(__name__, service_name="test-vpa")
        
        with CorrelationContext():
            logger.info("Starting risky operation", operation="risky_task")
            
            try:
                # Simulate an error
                raise ConnectionError("Database connection failed")
            except ConnectionError as e:
                logger.error("Operation failed", 
                           operation="risky_task",
                           error_type="ConnectionError",
                           error_message=str(e))
                
                logger.log_security_event("database_failure", {
                    "database": "main_db",
                    "error": str(e),
                    "retry_attempt": 1
                })
        
        entries = self.get_log_entries()
        assert len(entries) == 3
        
        # Check error logging
        error_entry = entries[1]
        assert error_entry["level"] == "ERROR"
        assert error_entry["extra"]["error_type"] == "ConnectionError"
        
        # Check security event
        security_entry = entries[2]
        assert security_entry["level"] == "WARNING"
        assert security_entry["extra"]["security_event"] is True
    
    def test_performance_monitoring_workflow(self):
        """Test performance monitoring workflow."""
        logger = get_structured_logger(__name__, service_name="test-vpa")
        
        @log_performance(logger, "file_processing")
        def process_file(filename: str, size: int):
            logger.info(f"Processing file: {filename}", file_size=size)
            time.sleep(0.001)  # Simulate processing
            logger.debug("File processing completed", file_name=filename)  # Changed from filename to file_name
            return f"processed_{filename}"
        
        with CorrelationContext():
            result = process_file("test.txt", 1024)
        
        entries = self.get_log_entries()
        assert len(entries) == 3
        
        # Check performance entry
        perf_entry = next(e for e in entries if e["extra"].get("performance"))
        assert perf_entry["extra"]["operation"] == "file_processing"
        assert perf_entry["extra"]["status"] == "success"
        assert "duration_ms" in perf_entry["extra"]
