#!/usr/bin/env python3
"""
Phase 4: Performance & Regression Testing Suite

Comprehensive testing framework for load testing, stress testing, memory analysis,
and regression validation of the compartmentalized addon system.
"""

import sys
import os
import asyncio
import time
import gc
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

class PerformanceMonitor:
    """Monitor system performance during tests (simplified version)"""
    
    def __init__(self):
        self.start_time = 0
        self.metrics = []
    
    def start_monitoring(self):
        """Start performance monitoring"""
        self.start_time = time.time()
        self.metrics = []
        print(f"📊 Performance monitoring started")
    
    def record_metric(self, operation: str, duration: float, memory_delta: float = 0):
        """Record a performance metric"""
        metric = {
            "operation": operation,
            "duration": duration,
            "memory_delta": memory_delta,
            "timestamp": datetime.now().isoformat()
        }
        self.metrics.append(metric)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        total_time = time.time() - self.start_time
        
        return {
            "total_duration": total_time,
            "total_operations": len(self.metrics),
            "avg_operation_time": sum(m["duration"] for m in self.metrics) / len(self.metrics) if self.metrics else 0
        }

class LoadTestSuite:
    """Load testing suite for addon system"""
    
    def __init__(self):
        self.monitor = PerformanceMonitor()
        self.test_results = {}
        
    async def setup_test_environment(self):
        """Setup test environment"""
        try:
            from vpa.core.events import EventBus
            from vpa.ai.addon_logic.addon_logic_coordinator import AddonLogicCoordinator
            from vpa.ai.addon_logic_module import AddonAILogic
            
            self.event_bus = EventBus()
            self.event_bus.initialize()
            
            self.coordinator = AddonLogicCoordinator(self.event_bus)
            await self.coordinator.initialize_coordinator()
            
            self.addon_ai = AddonAILogic(self.event_bus)
            await self.addon_ai.initialize()
            
            print("✅ Test environment setup complete")
            return True
            
        except Exception as e:
            print(f"❌ Test environment setup failed: {e}")
            return False
    
    async def test_concurrent_workflow_execution(self, num_concurrent: int = 10) -> Dict[str, Any]:
        """Test concurrent workflow execution"""
        print(f"\n🔄 Testing {num_concurrent} concurrent workflow executions...")
        
        start_time = time.time()
        
        # Get available workflows
        workflows_response = await self.coordinator.list_workflows()
        if not workflows_response.get("success", False):
            return {"success": False, "error": "Failed to get workflows"}
        
        workflows = workflows_response.get("workflows", [])
        if not workflows:
            return {"success": False, "error": "No workflows available for testing"}
        
        # Select first few workflows for testing
        test_workflows = workflows[:min(5, len(workflows))]
        
        # Create concurrent execution tasks
        tasks = []
        for i in range(num_concurrent):
            workflow = test_workflows[i % len(test_workflows)]
            workflow_id = workflow.get("workflow_id")
            task = self.coordinator.execute_workflow(workflow_id, {"test_run": True, "iteration": i})
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        
        # Analyze results
        successful_executions = sum(1 for r in results if isinstance(r, dict) and r.get("success", False))
        failed_executions = len(results) - successful_executions
        
        test_result = {
            "test_name": "concurrent_workflow_execution",
            "num_concurrent": num_concurrent,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "success_rate": (successful_executions / len(results)) * 100,
            "total_duration": end_time - start_time,
            "avg_execution_time": (end_time - start_time) / len(results),
            "workflows_tested": [w.get("workflow_id") for w in test_workflows]
        }
        
        self.monitor.record_metric("concurrent_workflows", end_time - start_time)
        print(f"✅ Concurrent test complete: {successful_executions}/{len(results)} successful ({test_result['success_rate']:.1f}%)")
        
        return test_result
    
    async def test_memory_leak_detection(self, iterations: int = 50) -> Dict[str, Any]:
        """Test for memory leaks during repeated operations"""
        print(f"\n🧠 Testing memory leak detection over {iterations} iterations...")
        
        memory_samples = []
        
        for i in range(iterations):
            memory_before = self.monitor.process.memory_info().rss / 1024 / 1024
            
            # Perform operations that might cause memory leaks
            status = await self.coordinator.get_coordinator_status()
            workflows = await self.coordinator.list_workflows()
            capabilities = await self.coordinator.list_capabilities()
            
            # Force garbage collection
            gc.collect()
            
            memory_after = self.monitor.process.memory_info().rss / 1024 / 1024
            memory_samples.append(memory_after)
            
            if i % 10 == 0:
                print(f"  Iteration {i}: {memory_after:.2f} MB")
        
        # Analyze memory trend
        memory_start = memory_samples[0]
        memory_end = memory_samples[-1]
        memory_growth = memory_end - memory_start
        
        # Calculate trend (linear regression slope)
        n = len(memory_samples)
        sum_x = sum(range(n))
        sum_y = sum(memory_samples)
        sum_xy = sum(i * memory_samples[i] for i in range(n))
        sum_x2 = sum(i * i for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        test_result = {
            "test_name": "memory_leak_detection",
            "iterations": iterations,
            "memory_start": memory_start,
            "memory_end": memory_end,
            "memory_growth": memory_growth,
            "memory_trend_slope": slope,
            "potential_leak": slope > 0.1,  # More than 0.1 MB per iteration
            "memory_samples": memory_samples[-10:]  # Last 10 samples
        }
        
        if test_result["potential_leak"]:
            print(f"⚠️  Potential memory leak detected: {slope:.3f} MB/iteration growth")
        else:
            print(f"✅ No significant memory leak detected: {slope:.3f} MB/iteration")
        
        return test_result
    
    async def test_addon_initialization_performance(self) -> Dict[str, Any]:
        """Test addon initialization performance"""
        print("\n⚡ Testing addon initialization performance...")
        
        # Test fresh coordinator initialization
        start_time = time.time()
        memory_before = self.monitor.process.memory_info().rss / 1024 / 1024
        
        test_coordinator = AddonLogicCoordinator(self.event_bus)
        init_result = await test_coordinator.initialize_coordinator()
        
        end_time = time.time()
        memory_after = self.monitor.process.memory_info().rss / 1024 / 1024
        
        test_result = {
            "test_name": "addon_initialization_performance",
            "initialization_time": end_time - start_time,
            "memory_usage": memory_after - memory_before,
            "success": init_result.get("success", False),
            "addons_initialized": len(init_result.get("enabled_addons", [])),
            "workflows_loaded": init_result.get("total_workflows", 0),
            "capabilities_loaded": init_result.get("total_capabilities", 0)
        }
        
        print(f"✅ Initialization: {test_result['initialization_time']:.2f}s, {test_result['addons_initialized']} addons")
        
        return test_result
    
    async def test_event_bus_performance(self, num_events: int = 1000) -> Dict[str, Any]:
        """Test EventBus performance under load"""
        print(f"\n📡 Testing EventBus performance with {num_events} events...")
        
        received_events = []
        
        def event_handler(data):
            received_events.append(data)
        
        # Subscribe to test events
        self.event_bus.subscribe("performance.test.event", event_handler)
        
        start_time = time.time()
        memory_before = self.monitor.process.memory_info().rss / 1024 / 1024
        
        # Emit events rapidly
        for i in range(num_events):
            self.event_bus.emit("performance.test.event", {"event_id": i, "timestamp": time.time()})
        
        # Wait for event processing
        await asyncio.sleep(0.1)
        
        end_time = time.time()
        memory_after = self.monitor.process.memory_info().rss / 1024 / 1024
        
        test_result = {
            "test_name": "event_bus_performance",
            "events_sent": num_events,
            "events_received": len(received_events),
            "success_rate": (len(received_events) / num_events) * 100,
            "total_duration": end_time - start_time,
            "events_per_second": num_events / (end_time - start_time),
            "memory_usage": memory_after - memory_before
        }
        
        print(f"✅ EventBus: {test_result['events_per_second']:.0f} events/sec, {test_result['success_rate']:.1f}% delivery")
        
        return test_result

async def run_phase4_performance_tests():
    """Run comprehensive Phase 4 performance tests"""
    print("=" * 70)
    print("🚀 PHASE 4: PERFORMANCE & REGRESSION TESTING")
    print("=" * 70)
    
    test_suite = LoadTestSuite()
    test_suite.monitor.start_monitoring()
    
    # Setup test environment
    if not await test_suite.setup_test_environment():
        print("❌ PHASE 4 FAILED - Could not setup test environment")
        return False
    
    all_results = {}
    
    try:
        # Test 1: Addon Initialization Performance
        print("\n🔸 PHASE 4.1: INITIALIZATION PERFORMANCE")
        all_results["initialization"] = await test_suite.test_addon_initialization_performance()
        
        # Test 2: EventBus Performance
        print("\n🔸 PHASE 4.2: EVENTBUS PERFORMANCE") 
        all_results["eventbus"] = await test_suite.test_event_bus_performance(1000)
        
        # Test 3: Concurrent Workflow Execution
        print("\n🔸 PHASE 4.3: CONCURRENT WORKFLOW EXECUTION")
        all_results["concurrent_light"] = await test_suite.test_concurrent_workflow_execution(5)
        all_results["concurrent_moderate"] = await test_suite.test_concurrent_workflow_execution(15)
        all_results["concurrent_heavy"] = await test_suite.test_concurrent_workflow_execution(30)
        
        # Test 4: Memory Leak Detection
        print("\n🔸 PHASE 4.4: MEMORY LEAK DETECTION")
        all_results["memory_leak"] = await test_suite.test_memory_leak_detection(50)
        
        # Performance Summary
        performance_summary = test_suite.monitor.get_summary()
        all_results["performance_summary"] = performance_summary
        
        print("\n" + "=" * 70)
        print("📊 PHASE 4 PERFORMANCE RESULTS SUMMARY")
        print("=" * 70)
        
        print(f"⏱️  Total Test Duration: {performance_summary['total_duration']:.2f} seconds")
        print(f"🧠 Memory Usage: {performance_summary['memory_start']:.2f} → {performance_summary['memory_current']:.2f} MB")
        print(f"📈 Memory Growth: {performance_summary['memory_growth']:.2f} MB")
        print(f"🚀 Peak Memory: {performance_summary['peak_memory']:.2f} MB")
        print(f"⚡ Avg Operation Time: {performance_summary['avg_operation_time']:.3f} seconds")
        
        # Analyze results for issues
        issues_detected = []
        
        # Check initialization performance
        init_time = all_results["initialization"]["initialization_time"]
        if init_time > 5.0:
            issues_detected.append(f"Slow initialization: {init_time:.2f}s (target: <5s)")
        
        # Check concurrent performance
        heavy_success_rate = all_results["concurrent_heavy"]["success_rate"]
        if heavy_success_rate < 95:
            issues_detected.append(f"Poor concurrent performance: {heavy_success_rate:.1f}% success rate")
        
        # Check memory leaks
        if all_results["memory_leak"]["potential_leak"]:
            slope = all_results["memory_leak"]["memory_trend_slope"]
            issues_detected.append(f"Potential memory leak: {slope:.3f} MB/iteration")
        
        # Check EventBus performance
        eventbus_rate = all_results["eventbus"]["events_per_second"]
        if eventbus_rate < 1000:
            issues_detected.append(f"Slow EventBus: {eventbus_rate:.0f} events/sec (target: >1000)")
        
        if issues_detected:
            print("\n⚠️  PERFORMANCE ISSUES DETECTED:")
            for issue in issues_detected:
                print(f"   • {issue}")
            print("\n🛑 PHASE 4 COMPLETED WITH ISSUES - REVIEW REQUIRED")
            return False
        else:
            print("\n✅ ALL PERFORMANCE TESTS PASSED!")
            print("🎯 System meets performance requirements")
            print("🚀 READY FOR PHASE 4.5: REGRESSION TESTING")
            return True
            
    except Exception as e:
        print(f"\n❌ PHASE 4 PERFORMANCE TESTING FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(run_phase4_performance_tests())
    sys.exit(0 if result else 1)
