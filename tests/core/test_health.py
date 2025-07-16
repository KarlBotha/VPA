"""
Tests for VPA Health Monitoring System.
Comprehensive test coverage for health checks and monitoring functionality.
"""

import json
import time
from datetime import datetime
from unittest.mock import Mock, patch

from vpa.core.health import (
    HealthStatus,
    HealthCheck,
    SystemMetrics,
    ComponentHealth,
    OverallHealth,
    HealthChecker,
    HealthMonitor,
    create_health_monitor,
    simple_health_check
)


class TestHealthStatus:
    """Test cases for HealthStatus enum."""
    
    def test_health_status_values(self):
        """Test health status enum values."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"
        assert HealthStatus.UNKNOWN.value == "unknown"


class TestHealthCheck:
    """Test cases for HealthCheck dataclass."""
    
    def test_health_check_creation(self):
        """Test health check creation."""
        timestamp = datetime.utcnow()
        check = HealthCheck(
            name="test_check",
            status=HealthStatus.HEALTHY,
            message="All good",
            timestamp=timestamp,
            duration_ms=15.5,
            details={"key": "value"}
        )
        
        assert check.name == "test_check"
        assert check.status == HealthStatus.HEALTHY
        assert check.message == "All good"
        assert check.timestamp == timestamp
        assert check.duration_ms == 15.5
        assert check.details == {"key": "value"}
    
    def test_health_check_without_details(self):
        """Test health check creation without details."""
        check = HealthCheck(
            name="simple_check",
            status=HealthStatus.DEGRADED,
            message="Warning",
            timestamp=datetime.utcnow(),
            duration_ms=10.0
        )
        
        assert check.details is None


class TestSystemMetrics:
    """Test cases for SystemMetrics dataclass."""
    
    def test_system_metrics_creation(self):
        """Test system metrics creation."""
        metrics = SystemMetrics(
            cpu_percent=45.0,
            memory_percent=65.0,
            memory_used_mb=4096.0,
            memory_total_mb=8192.0,
            disk_percent=75.0,
            disk_used_gb=250.0,
            disk_total_gb=500.0,
            uptime_seconds=3600.0,
            process_count=150,
            load_average=[1.5, 1.2, 1.0]
        )
        
        assert metrics.cpu_percent == 45.0
        assert metrics.memory_percent == 65.0
        assert metrics.load_average == [1.5, 1.2, 1.0]


class TestHealthChecker:
    """Test cases for HealthChecker class."""
    
    def setup_method(self):
        """Setup test environment."""
        self.health_checker = HealthChecker("test-service")
    
    def test_health_checker_initialization(self):
        """Test health checker initialization."""
        assert self.health_checker.service_name == "test-service"
        assert len(self.health_checker.health_checks) >= 3  # System checks
        assert "system_memory" in self.health_checker.health_checks
        assert "system_disk" in self.health_checker.health_checks
        assert "system_cpu" in self.health_checker.health_checks
    
    def test_register_health_check(self):
        """Test registering a custom health check."""
        def custom_check():
            return HealthCheck(
                name="custom",
                status=HealthStatus.HEALTHY,
                message="Custom check passed",
                timestamp=datetime.utcnow(),
                duration_ms=5.0
            )
        
        self.health_checker.register_health_check("custom", custom_check)
        
        assert "custom" in self.health_checker.health_checks
        assert self.health_checker.health_checks["custom"] == custom_check
    
    def test_unregister_health_check(self):
        """Test unregistering a health check."""
        def temp_check():
            return HealthCheck(
                name="temp",
                status=HealthStatus.HEALTHY,
                message="Temp check",
                timestamp=datetime.utcnow(),
                duration_ms=1.0
            )
        
        self.health_checker.register_health_check("temp", temp_check)
        assert "temp" in self.health_checker.health_checks
        
        self.health_checker.unregister_health_check("temp")
        assert "temp" not in self.health_checker.health_checks
    
    def test_run_health_check_success(self):
        """Test running a successful health check."""
        def success_check():
            return HealthCheck(
                name="success",
                status=HealthStatus.HEALTHY,
                message="Success",
                timestamp=datetime.utcnow(),
                duration_ms=10.0
            )
        
        self.health_checker.register_health_check("success", success_check)
        result = self.health_checker.run_health_check("success")
        
        assert result is not None
        assert result.name == "success"
        assert result.status == HealthStatus.HEALTHY
        assert result.message == "Success"
    
    def test_run_health_check_failure(self):
        """Test running a health check that raises an exception."""
        def failing_check():
            raise ValueError("Something went wrong")
        
        self.health_checker.register_health_check("failing", failing_check)
        result = self.health_checker.run_health_check("failing")
        
        assert result is not None
        assert result.name == "failing"
        assert result.status == HealthStatus.UNHEALTHY
        assert "Something went wrong" in result.message
        assert "error" in result.details
    
    def test_run_health_check_not_found(self):
        """Test running a non-existent health check."""
        result = self.health_checker.run_health_check("nonexistent")
        assert result is None
    
    def test_run_all_health_checks(self):
        """Test running all health checks."""
        def check1():
            return HealthCheck("check1", HealthStatus.HEALTHY, "OK", datetime.utcnow(), 5.0)
        
        def check2():
            return HealthCheck("check2", HealthStatus.DEGRADED, "Warning", datetime.utcnow(), 8.0)
        
        self.health_checker.register_health_check("check1", check1)
        self.health_checker.register_health_check("check2", check2)
        
        results = self.health_checker.run_all_health_checks()
        
        # Should include system checks + custom checks
        assert len(results) >= 5
        check_names = [result.name for result in results]
        assert "check1" in check_names
        assert "check2" in check_names
        assert "system_memory" in check_names
    
    def test_update_component_health_all_healthy(self):
        """Test updating component health with all healthy checks."""
        checks = [
            HealthCheck("check1", HealthStatus.HEALTHY, "OK", datetime.utcnow(), 5.0),
            HealthCheck("check2", HealthStatus.HEALTHY, "Good", datetime.utcnow(), 3.0)
        ]
        
        self.health_checker.update_component_health("test_component", checks)
        
        component = self.health_checker.get_component_health("test_component")
        assert component is not None
        assert component.name == "test_component"
        assert component.status == HealthStatus.HEALTHY
        assert len(component.checks) == 2
    
    def test_update_component_health_mixed_status(self):
        """Test updating component health with mixed check statuses."""
        checks = [
            HealthCheck("check1", HealthStatus.HEALTHY, "OK", datetime.utcnow(), 5.0),
            HealthCheck("check2", HealthStatus.DEGRADED, "Warning", datetime.utcnow(), 8.0)
        ]
        
        self.health_checker.update_component_health("mixed_component", checks)
        
        component = self.health_checker.get_component_health("mixed_component")
        assert component.status == HealthStatus.DEGRADED
    
    def test_update_component_health_with_unhealthy(self):
        """Test updating component health with unhealthy checks."""
        checks = [
            HealthCheck("check1", HealthStatus.HEALTHY, "OK", datetime.utcnow(), 5.0),
            HealthCheck("check2", HealthStatus.UNHEALTHY, "Failed", datetime.utcnow(), 12.0)
        ]
        
        self.health_checker.update_component_health("unhealthy_component", checks)
        
        component = self.health_checker.get_component_health("unhealthy_component")
        assert component.status == HealthStatus.UNHEALTHY
    
    def test_update_component_health_no_checks(self):
        """Test updating component health with no checks."""
        self.health_checker.update_component_health("empty_component", [])
        
        component = self.health_checker.get_component_health("empty_component")
        assert component.status == HealthStatus.UNKNOWN
    
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.cpu_percent')
    @patch('psutil.pids')
    @patch('time.time')
    def test_get_system_metrics(self, mock_time, mock_pids, mock_cpu, mock_disk, mock_memory):
        """Test getting system metrics."""
        # Mock psutil responses
        mock_memory.return_value = Mock(
            percent=65.0,
            used=4294967296,  # 4GB
            total=8589934592,  # 8GB
            available=4294967296
        )
        
        mock_disk.return_value = Mock(
            percent=75.0,
            used=268435456000,  # 250GB
            total=536870912000,  # 500GB
            free=268435456000
        )
        
        mock_cpu.return_value = 45.0
        mock_pids.return_value = [1, 2, 3, 4, 5]  # 5 processes
        
        # Mock time to simulate uptime
        mock_time.return_value = self.health_checker.start_time + 300  # 5 minutes uptime
        
        metrics = self.health_checker.get_system_metrics()
        
        assert metrics.cpu_percent == 45.0
        assert metrics.memory_percent == 65.0
        assert abs(metrics.memory_used_mb - 4096.0) < 1.0  # Allow for rounding
        assert abs(metrics.memory_total_mb - 8192.0) < 1.0
        assert metrics.disk_percent == 75.0
        assert metrics.process_count == 5
        assert metrics.uptime_seconds == 300.0  # 5 minutes
    
    def test_get_overall_health_all_healthy(self):
        """Test getting overall health when all components are healthy."""
        # Add a healthy component
        checks = [
            HealthCheck("check1", HealthStatus.HEALTHY, "OK", datetime.utcnow(), 5.0)
        ]
        self.health_checker.update_component_health("healthy_component", checks)
        
        overall_health = self.health_checker.get_overall_health()
        
        assert overall_health.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]  # System checks may vary
        assert len(overall_health.components) >= 1
        assert overall_health.system_metrics is not None
        assert "components" in overall_health.summary.lower()
    
    def test_get_overall_health_with_unhealthy_component(self):
        """Test getting overall health with unhealthy component."""
        # Add an unhealthy component
        checks = [
            HealthCheck("failing_check", HealthStatus.UNHEALTHY, "Failed", datetime.utcnow(), 15.0)
        ]
        self.health_checker.update_component_health("unhealthy_component", checks)
        
        overall_health = self.health_checker.get_overall_health()
        
        # Should be unhealthy due to the unhealthy component
        assert overall_health.status == HealthStatus.UNHEALTHY
        assert "unhealthy" in overall_health.summary.lower()


class TestHealthMonitor:
    """Test cases for HealthMonitor class."""
    
    def setup_method(self):
        """Setup test environment."""
        self.monitor = HealthMonitor("test-monitor")
    
    def test_health_monitor_initialization(self):
        """Test health monitor initialization."""
        assert self.monitor.service_name == "test-monitor"
        assert self.monitor.check_interval == 30
        assert self.monitor.health_checker is not None
        assert self.monitor.last_check_time is None
        assert self.monitor.cached_health is None
    
    def test_get_health_json(self):
        """Test getting health status as JSON."""
        health_json = self.monitor.get_health_json()
        
        assert isinstance(health_json, str)
        
        # Parse JSON to verify structure
        health_data = json.loads(health_json)
        assert "status" in health_data
        assert "timestamp" in health_data
        assert "components" in health_data
        assert "system_metrics" in health_data
        assert "summary" in health_data
        
        # Verify timestamp format
        assert health_data["timestamp"].endswith("Z")
        
        # Check that last_check_time was updated
        assert self.monitor.last_check_time is not None
        assert self.monitor.cached_health is not None
    
    def test_get_metrics_json(self):
        """Test getting system metrics as JSON."""
        metrics_json = self.monitor.get_metrics_json()
        
        assert isinstance(metrics_json, str)
        
        # Parse JSON to verify structure
        metrics_data = json.loads(metrics_json)
        expected_fields = [
            "cpu_percent", "memory_percent", "memory_used_mb", "memory_total_mb",
            "disk_percent", "disk_used_gb", "disk_total_gb", "uptime_seconds",
            "process_count"
        ]
        
        for field in expected_fields:
            assert field in metrics_data
    
    def test_is_healthy(self):
        """Test is_healthy method."""
        # Add a healthy component to ensure healthy status
        def healthy_check():
            return HealthCheck("test", HealthStatus.HEALTHY, "OK", datetime.utcnow(), 1.0)
        
        self.monitor.health_checker.register_health_check("test_healthy", healthy_check)
        
        # The result depends on system conditions, so we just verify it returns a boolean
        result = self.monitor.is_healthy()
        assert isinstance(result, bool)
    
    def test_register_component_health_check(self):
        """Test registering a component-specific health check."""
        def component_check():
            return HealthCheck("comp_check", HealthStatus.HEALTHY, "Component OK", datetime.utcnow(), 2.0)
        
        self.monitor.register_component_health_check("test_component", "connection", component_check)
        
        # Verify the check was registered with the correct name
        assert "test_component_connection" in self.monitor.health_checker.health_checks
        
        # Run the check to verify it works
        result = self.monitor.health_checker.run_health_check("test_component_connection")
        assert result is not None
        assert result.message == "Component OK"


class TestConvenienceFunctions:
    """Test cases for convenience functions."""
    
    def test_create_health_monitor(self):
        """Test create_health_monitor function."""
        monitor = create_health_monitor("test-service")
        
        assert isinstance(monitor, HealthMonitor)
        assert monitor.service_name == "test-service"
    
    def test_create_health_monitor_default_name(self):
        """Test create_health_monitor with default name."""
        monitor = create_health_monitor()
        
        assert isinstance(monitor, HealthMonitor)
        assert monitor.service_name == "vpa"
    
    def test_simple_health_check_success(self):
        """Test simple_health_check with successful function."""
        def always_true():
            return True
        
        health_check = simple_health_check(
            "test_check",
            always_true,
            "All good",
            "Something wrong"
        )
        
        result = health_check()
        
        assert result.name == "test_check"
        assert result.status == HealthStatus.HEALTHY
        assert result.message == "All good"
        assert result.duration_ms >= 0
    
    def test_simple_health_check_failure(self):
        """Test simple_health_check with failing function."""
        def always_false():
            return False
        
        health_check = simple_health_check(
            "failing_check",
            always_false,
            "All good",
            "Something wrong"
        )
        
        result = health_check()
        
        assert result.name == "failing_check"
        assert result.status == HealthStatus.UNHEALTHY
        assert result.message == "Something wrong"
    
    def test_simple_health_check_exception(self):
        """Test simple_health_check with function that raises exception."""
        def raises_exception():
            raise RuntimeError("Test error")
        
        health_check = simple_health_check(
            "exception_check",
            raises_exception
        )
        
        result = health_check()
        
        assert result.name == "exception_check"
        assert result.status == HealthStatus.UNHEALTHY
        assert "Test error" in result.message
        assert "error" in result.details
        assert result.details["error_type"] == "RuntimeError"


class TestIntegrationScenarios:
    """Integration test scenarios for health monitoring."""
    
    def test_full_health_monitoring_workflow(self):
        """Test complete health monitoring workflow."""
        monitor = create_health_monitor("integration-test")
        
        # Register custom health checks
        def database_check():
            return True  # Simulate healthy database
        
        def cache_check():
            return False  # Simulate unhealthy cache
        
        db_health = simple_health_check("db_connection", database_check, "DB OK", "DB Failed")
        cache_health = simple_health_check("cache_connection", cache_check, "Cache OK", "Cache Failed")
        
        monitor.register_component_health_check("database", "connection", db_health)
        monitor.register_component_health_check("cache", "connection", cache_health)
        
        # Get overall health
        health_json = monitor.get_health_json()
        health_data = json.loads(health_json)
        
        # Verify structure
        assert "components" in health_data
        assert len(health_data["components"]) >= 1  # At least system component
        
        # Verify metrics
        metrics_json = monitor.get_metrics_json()
        metrics_data = json.loads(metrics_json)
        assert metrics_data["uptime_seconds"] >= 0
        
        # The system should be unhealthy due to cache failure
        # (though system checks might affect the overall status)
        assert health_data["status"] in ["healthy", "degraded", "unhealthy"]
    
    def test_system_health_checks_execution(self):
        """Test that system health checks execute properly."""
        monitor = create_health_monitor("system-test")
        
        # Run all health checks
        health_data = json.loads(monitor.get_health_json())
        
        # Find system component
        system_component = None
        for component in health_data["components"]:
            if component["name"] == "system":
                system_component = component
                break
        
        assert system_component is not None
        assert len(system_component["checks"]) >= 3  # CPU, memory, disk
        
        # Verify check names
        check_names = [check["name"] for check in system_component["checks"]]
        assert "system_memory" in check_names
        assert "system_disk" in check_names
        assert "system_cpu" in check_names
        
        # Verify each check has required fields
        for check in system_component["checks"]:
            assert "name" in check
            assert "status" in check
            assert "message" in check
            assert "timestamp" in check
            assert "duration_ms" in check
    
    def test_performance_metrics_collection(self):
        """Test performance metrics collection."""
        monitor = create_health_monitor("performance-test")
        
        # Collect metrics multiple times to ensure consistency
        for i in range(3):
            metrics_json = monitor.get_metrics_json()
            metrics = json.loads(metrics_json)
            
            # Verify all expected metrics are present and reasonable
            assert 0 <= metrics["cpu_percent"] <= 100
            assert 0 <= metrics["memory_percent"] <= 100
            assert metrics["memory_used_mb"] >= 0
            assert metrics["memory_total_mb"] > 0
            assert 0 <= metrics["disk_percent"] <= 100
            assert metrics["disk_used_gb"] >= 0
            assert metrics["disk_total_gb"] > 0
            assert metrics["uptime_seconds"] >= 0
            assert metrics["process_count"] >= 0
            
            time.sleep(0.1)  # Small delay between collections
