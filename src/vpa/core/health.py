"""
Health Monitoring System for VPA.
Provides health checks, system metrics, and monitoring endpoints.
"""

import json
import platform
import psutil
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict

from vpa.core.logging import get_structured_logger


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Individual health check result."""
    name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    duration_ms: float
    details: Optional[Dict[str, Any]] = None


@dataclass
class SystemMetrics:
    """System performance metrics."""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_total_mb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    uptime_seconds: float
    process_count: int
    load_average: Optional[List[float]] = None  # Unix only


@dataclass
class ComponentHealth:
    """Component health status."""
    name: str
    status: HealthStatus
    checks: List[HealthCheck]
    last_updated: datetime
    metrics: Optional[Dict[str, Any]] = None


@dataclass
class OverallHealth:
    """Overall system health status."""
    status: HealthStatus
    timestamp: datetime
    components: List[ComponentHealth]
    system_metrics: SystemMetrics
    summary: str
    uptime_seconds: float


class HealthChecker:
    """
    Health check manager that coordinates all health checks.
    """
    
    def __init__(self, service_name: str = "vpa"):
        self.service_name = service_name
        self.logger = get_structured_logger(__name__, service_name=service_name)
        self.health_checks: Dict[str, Callable[[], HealthCheck]] = {}
        self.component_healths: Dict[str, ComponentHealth] = {}
        self.start_time = time.time()
        
        # Register default system health checks
        self._register_system_checks()
    
    def _register_system_checks(self) -> None:
        """Register default system health checks."""
        self.register_health_check("system_memory", self._check_memory_usage)
        self.register_health_check("system_disk", self._check_disk_usage)
        self.register_health_check("system_cpu", self._check_cpu_usage)
    
    def register_health_check(self, name: str, check_func: Callable[[], HealthCheck]) -> None:
        """
        Register a health check function.
        
        Args:
            name: Unique name for the health check
            check_func: Function that returns a HealthCheck result
        """
        self.health_checks[name] = check_func
        self.logger.info(f"Registered health check: {name}", 
                        health_check=name, action="register")
    
    def unregister_health_check(self, name: str) -> None:
        """
        Unregister a health check.
        
        Args:
            name: Name of the health check to remove
        """
        if name in self.health_checks:
            del self.health_checks[name]
            self.logger.info(f"Unregistered health check: {name}", 
                           health_check=name, action="unregister")
    
    def run_health_check(self, name: str) -> Optional[HealthCheck]:
        """
        Run a specific health check.
        
        Args:
            name: Name of the health check to run
            
        Returns:
            HealthCheck result or None if check doesn't exist
        """
        if name not in self.health_checks:
            self.logger.warning(f"Health check not found: {name}", 
                              health_check=name, action="run", status="not_found")
            return None
        
        start_time = time.time()
        try:
            result = self.health_checks[name]()
            duration = (time.time() - start_time) * 1000
            
            self.logger.debug(f"Health check completed: {name}", 
                            health_check=name, 
                            status=result.status.value,
                            duration_ms=duration)
            
            return result
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            self.logger.error(f"Health check failed: {name}", 
                            health_check=name, 
                            error=str(e),
                            duration_ms=duration)
            
            return HealthCheck(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                timestamp=datetime.utcnow(),
                duration_ms=duration,
                details={"error": str(e), "error_type": type(e).__name__}
            )
    
    def run_all_health_checks(self) -> List[HealthCheck]:
        """
        Run all registered health checks.
        
        Returns:
            List of all health check results
        """
        results = []
        
        for name in self.health_checks:
            result = self.run_health_check(name)
            if result:
                results.append(result)
        
        return results
    
    def get_component_health(self, component_name: str) -> Optional[ComponentHealth]:
        """
        Get health status for a specific component.
        
        Args:
            component_name: Name of the component
            
        Returns:
            ComponentHealth or None if component not found
        """
        return self.component_healths.get(component_name)
    
    def update_component_health(self, component_name: str, checks: List[HealthCheck], 
                              metrics: Optional[Dict[str, Any]] = None) -> None:
        """
        Update health status for a component.
        
        Args:
            component_name: Name of the component
            checks: List of health check results
            metrics: Optional component-specific metrics
        """
        # Determine overall component status
        if not checks:
            status = HealthStatus.UNKNOWN
        elif all(check.status == HealthStatus.HEALTHY for check in checks):
            status = HealthStatus.HEALTHY
        elif any(check.status == HealthStatus.UNHEALTHY for check in checks):
            status = HealthStatus.UNHEALTHY
        else:
            status = HealthStatus.DEGRADED
        
        self.component_healths[component_name] = ComponentHealth(
            name=component_name,
            status=status,
            checks=checks,
            last_updated=datetime.utcnow(),
            metrics=metrics
        )
        
        self.logger.info(f"Updated component health: {component_name}", 
                        component=component_name, 
                        status=status.value,
                        check_count=len(checks))
    
    def get_system_metrics(self) -> SystemMetrics:
        """
        Get current system performance metrics.
        
        Returns:
            SystemMetrics with current system performance data
        """
        try:
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Process count
            process_count = len(psutil.pids())
            
            # Uptime
            uptime = time.time() - self.start_time
            
            # Load average (Unix only)
            load_avg = None
            try:
                if hasattr(psutil, 'getloadavg'):
                    load_avg = list(psutil.getloadavg())
            except (AttributeError, OSError):
                pass  # Not available on Windows
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                memory_total_mb=memory.total / 1024 / 1024,
                disk_percent=disk.percent,
                disk_used_gb=disk.used / 1024 / 1024 / 1024,
                disk_total_gb=disk.total / 1024 / 1024 / 1024,
                uptime_seconds=uptime,
                process_count=process_count,
                load_average=load_avg
            )
            
        except Exception as e:
            self.logger.error("Failed to collect system metrics", error=str(e))
            # Return default metrics on error
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                memory_total_mb=0.0,
                disk_percent=0.0,
                disk_used_gb=0.0,
                disk_total_gb=0.0,
                uptime_seconds=time.time() - self.start_time,
                process_count=0
            )
    
    def get_overall_health(self) -> OverallHealth:
        """
        Get overall system health status.
        
        Returns:
            OverallHealth with complete health assessment
        """
        # Run all health checks
        health_checks = self.run_all_health_checks()
        
        # Update default system component
        system_checks = [check for check in health_checks 
                        if check.name.startswith('system_')]
        if system_checks:
            self.update_component_health("system", system_checks)
        
        # Get system metrics
        metrics = self.get_system_metrics()
        
        # Determine overall status
        components = list(self.component_healths.values())
        if not components:
            overall_status = HealthStatus.UNKNOWN
            summary = "No components registered"
        elif all(comp.status == HealthStatus.HEALTHY for comp in components):
            overall_status = HealthStatus.HEALTHY
            summary = f"All {len(components)} components healthy"
        elif any(comp.status == HealthStatus.UNHEALTHY for comp in components):
            unhealthy_count = sum(1 for comp in components 
                                if comp.status == HealthStatus.UNHEALTHY)
            overall_status = HealthStatus.UNHEALTHY
            summary = f"{unhealthy_count}/{len(components)} components unhealthy"
        else:
            degraded_count = sum(1 for comp in components 
                               if comp.status == HealthStatus.DEGRADED)
            overall_status = HealthStatus.DEGRADED
            summary = f"{degraded_count}/{len(components)} components degraded"
        
        return OverallHealth(
            status=overall_status,
            timestamp=datetime.utcnow(),
            components=components,
            system_metrics=metrics,
            summary=summary,
            uptime_seconds=metrics.uptime_seconds
        )
    
    def _check_memory_usage(self) -> HealthCheck:
        """Check memory usage health."""
        start_time = time.time()
        
        try:
            memory = psutil.virtual_memory()
            duration = (time.time() - start_time) * 1000
            
            if memory.percent > 90:
                status = HealthStatus.UNHEALTHY
                message = f"Memory usage critically high: {memory.percent:.1f}%"
            elif memory.percent > 80:
                status = HealthStatus.DEGRADED
                message = f"Memory usage high: {memory.percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {memory.percent:.1f}%"
            
            return HealthCheck(
                name="system_memory",
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                duration_ms=duration,
                details={
                    "percent": memory.percent,
                    "used_mb": memory.used / 1024 / 1024,
                    "total_mb": memory.total / 1024 / 1024,
                    "available_mb": memory.available / 1024 / 1024
                }
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return HealthCheck(
                name="system_memory",
                status=HealthStatus.UNHEALTHY,
                message=f"Memory check failed: {str(e)}",
                timestamp=datetime.utcnow(),
                duration_ms=duration,
                details={"error": str(e)}
            )
    
    def _check_disk_usage(self) -> HealthCheck:
        """Check disk usage health."""
        start_time = time.time()
        
        try:
            disk = psutil.disk_usage('/')
            duration = (time.time() - start_time) * 1000
            
            if disk.percent > 95:
                status = HealthStatus.UNHEALTHY
                message = f"Disk usage critically high: {disk.percent:.1f}%"
            elif disk.percent > 85:
                status = HealthStatus.DEGRADED
                message = f"Disk usage high: {disk.percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk usage normal: {disk.percent:.1f}%"
            
            return HealthCheck(
                name="system_disk",
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                duration_ms=duration,
                details={
                    "percent": disk.percent,
                    "used_gb": disk.used / 1024 / 1024 / 1024,
                    "total_gb": disk.total / 1024 / 1024 / 1024,
                    "free_gb": disk.free / 1024 / 1024 / 1024
                }
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return HealthCheck(
                name="system_disk",
                status=HealthStatus.UNHEALTHY,
                message=f"Disk check failed: {str(e)}",
                timestamp=datetime.utcnow(),
                duration_ms=duration,
                details={"error": str(e)}
            )
    
    def _check_cpu_usage(self) -> HealthCheck:
        """Check CPU usage health."""
        start_time = time.time()
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            duration = (time.time() - start_time) * 1000
            
            if cpu_percent > 90:
                status = HealthStatus.UNHEALTHY
                message = f"CPU usage critically high: {cpu_percent:.1f}%"
            elif cpu_percent > 80:
                status = HealthStatus.DEGRADED
                message = f"CPU usage high: {cpu_percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"CPU usage normal: {cpu_percent:.1f}%"
            
            return HealthCheck(
                name="system_cpu",
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                duration_ms=duration,
                details={
                    "percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "count_logical": psutil.cpu_count(logical=True)
                }
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return HealthCheck(
                name="system_cpu",
                status=HealthStatus.UNHEALTHY,
                message=f"CPU check failed: {str(e)}",
                timestamp=datetime.utcnow(),
                duration_ms=duration,
                details={"error": str(e)}
            )


class HealthMonitor:
    """
    Health monitoring service that provides HTTP endpoints and periodic checks.
    """
    
    def __init__(self, service_name: str = "vpa", check_interval: int = 30):
        self.service_name = service_name
        self.check_interval = check_interval
        self.health_checker = HealthChecker(service_name)
        self.logger = get_structured_logger(__name__, service_name=service_name)
        self.last_check_time: Optional[datetime] = None
        self.cached_health: Optional[OverallHealth] = None
        
    def get_health_json(self) -> str:
        """
        Get health status as JSON string.
        
        Returns:
            JSON string representation of health status
        """
        health = self.health_checker.get_overall_health()
        self.last_check_time = datetime.utcnow()
        self.cached_health = health
        
        # Convert to JSON-serializable format
        health_dict = asdict(health)
        
        # Convert enums to their string values
        health_dict["status"] = health.status.value
        
        # Convert datetime objects to ISO strings
        health_dict["timestamp"] = health.timestamp.isoformat() + "Z"
        
        for component in health_dict["components"]:
            component["status"] = component["status"].value if hasattr(component["status"], 'value') else component["status"]
            component["last_updated"] = component["last_updated"]
            if isinstance(component["last_updated"], datetime):
                component["last_updated"] = component["last_updated"].isoformat() + "Z"
            
            for check in component["checks"]:
                check["status"] = check["status"].value if hasattr(check["status"], 'value') else check["status"]
                if isinstance(check["timestamp"], datetime):
                    check["timestamp"] = check["timestamp"].isoformat() + "Z"
        
        return json.dumps(health_dict, default=str, indent=2)
    
    def get_metrics_json(self) -> str:
        """
        Get system metrics as JSON string.
        
        Returns:
            JSON string representation of system metrics
        """
        metrics = self.health_checker.get_system_metrics()
        return json.dumps(asdict(metrics), default=str, indent=2)
    
    def is_healthy(self) -> bool:
        """
        Check if the system is healthy.
        
        Returns:
            True if system is healthy, False otherwise
        """
        health = self.health_checker.get_overall_health()
        return health.status == HealthStatus.HEALTHY
    
    def register_component_health_check(self, component_name: str, 
                                      check_name: str, 
                                      check_func: Callable[[], HealthCheck]) -> None:
        """
        Register a health check for a specific component.
        
        Args:
            component_name: Name of the component
            check_name: Name of the health check
            check_func: Function that returns a HealthCheck result
        """
        full_name = f"{component_name}_{check_name}"
        self.health_checker.register_health_check(full_name, check_func)
        
        self.logger.info(f"Registered component health check: {full_name}", 
                        component=component_name, 
                        check_name=check_name)


# Convenience functions for easy health monitoring integration
def create_health_monitor(service_name: str = "vpa") -> HealthMonitor:
    """
    Create a new health monitor instance.
    
    Args:
        service_name: Name of the service being monitored
        
    Returns:
        Configured HealthMonitor instance
    """
    return HealthMonitor(service_name)


def simple_health_check(name: str, check_func: Callable[[], bool], 
                       success_msg: str = "Check passed", 
                       failure_msg: str = "Check failed") -> Callable[[], HealthCheck]:
    """
    Create a simple health check from a boolean function.
    
    Args:
        name: Name of the health check
        check_func: Function that returns True if healthy, False if not
        success_msg: Message to return on success
        failure_msg: Message to return on failure
        
    Returns:
        Health check function compatible with HealthChecker
    """
    def health_check() -> HealthCheck:
        start_time = time.time()
        
        try:
            is_healthy = check_func()
            duration = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name=name,
                status=HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY,
                message=success_msg if is_healthy else failure_msg,
                timestamp=datetime.utcnow(),
                duration_ms=duration
            )
            
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return HealthCheck(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check exception: {str(e)}",
                timestamp=datetime.utcnow(),
                duration_ms=duration,
                details={"error": str(e), "error_type": type(e).__name__}
            )
    
    return health_check


# Example usage
if __name__ == "__main__":
    # Create health monitor
    monitor = create_health_monitor("vpa-test")
    
    # Add a custom health check
    def database_check() -> bool:
        # Simulate database connectivity check
        return True
    
    db_health_check = simple_health_check(
        "database_connection",
        database_check,
        "Database connection healthy",
        "Database connection failed"
    )
    
    monitor.register_component_health_check("database", "connection", db_health_check)
    
    # Get health status
    print("Health Status:")
    print(monitor.get_health_json())
    
    print("\nSystem Metrics:")
    print(monitor.get_metrics_json())
    
    print(f"\nIs Healthy: {monitor.is_healthy()}")
