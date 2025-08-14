"""
VPA Performance Monitor - Real-time Performance Tracking
Monitors and reports performance metrics for optimization validation
"""

import time
import psutil
import asyncio
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from collections import deque

@dataclass
class PerformanceMetric:
    """Single performance measurement"""
    timestamp: float
    memory_mb: float
    cpu_percent: float
    response_time_ms: float
    event_count: int = 0
    cache_hits: int = 0

class VPAPerformanceMonitor:
    """
    Real-time performance monitoring for VPA
    
    Tracks:
    - Memory usage trends
    - CPU utilization
    - Response times
    - Cache performance
    - Event processing rates
    """
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.metrics_history: deque = deque(maxlen=history_size)
        self.process = psutil.Process()
        self._monitoring = False
        self._start_time = time.time()
        
    async def start_monitoring(self, interval: float = 1.0):
        """Start continuous performance monitoring"""
        self._monitoring = True
        
        while self._monitoring:
            metric = self._collect_current_metrics()
            self.metrics_history.append(metric)
            await asyncio.sleep(interval)
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self._monitoring = False
    
    def _collect_current_metrics(self) -> PerformanceMetric:
        """Collect current performance metrics"""
        memory_info = self.process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        cpu_percent = self.process.cpu_percent()
        
        return PerformanceMetric(
            timestamp=time.time(),
            memory_mb=memory_mb,
            cpu_percent=cpu_percent,
            response_time_ms=0.0  # Updated by request handlers
        )
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current performance statistics"""
        if not self.metrics_history:
            return {}
        
        recent_metrics = list(self.metrics_history)[-10:]  # Last 10 measurements
        
        avg_memory = sum(m.memory_mb for m in recent_metrics) / len(recent_metrics)
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_response = sum(m.response_time_ms for m in recent_metrics) / len(recent_metrics)
        
        return {
            'uptime_seconds': time.time() - self._start_time,
            'current_memory_mb': recent_metrics[-1].memory_mb,
            'average_memory_mb': avg_memory,
            'current_cpu_percent': recent_metrics[-1].cpu_percent,
            'average_cpu_percent': avg_cpu,
            'average_response_time_ms': avg_response,
            'total_measurements': len(self.metrics_history),
            'performance_score': self._calculate_performance_score(recent_metrics)
        }
    
    def _calculate_performance_score(self, metrics: List[PerformanceMetric]) -> float:
        """Calculate overall performance score (0-100)"""
        if not metrics:
            return 0.0
        
        # Score based on memory efficiency, CPU usage, and response times
        avg_memory = sum(m.memory_mb for m in metrics) / len(metrics)
        avg_cpu = sum(m.cpu_percent for m in metrics) / len(metrics)
        avg_response = sum(m.response_time_ms for m in metrics) / len(metrics)
        
        # Lower memory and CPU usage = higher score
        memory_score = max(0, 100 - (avg_memory / 200 * 100))  # 200MB baseline
        cpu_score = max(0, 100 - avg_cpu)
        response_score = max(0, 100 - (avg_response / 1000 * 100))  # 1s baseline
        
        return (memory_score + cpu_score + response_score) / 3
    
    def export_metrics(self, filename: str = "performance_metrics.json"):
        """Export performance metrics to file"""
        import json
        
        metrics_data = {
            'collection_start': self._start_time,
            'total_measurements': len(self.metrics_history),
            'metrics': [asdict(metric) for metric in self.metrics_history],
            'summary': self.get_current_stats()
        }
        
        with open(filename, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        return filename

# Global performance monitor
performance_monitor = VPAPerformanceMonitor()
