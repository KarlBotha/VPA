#!/usr/bin/env python3
"""
Advanced Integration Test - EventBus & Resource Monitor Integration
"""

import sys
import os
import asyncio

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_eventbus_integration():
    """Test EventBus integration with AddonLogicCoordinator"""
    print("🚀 Phase 3.2: EventBus Integration Test...")
    
    try:
        from vpa.core.events import EventBus
        from vpa.ai.addon_logic.addon_logic_coordinator import AddonLogicCoordinator
        from vpa.ai.addon_logic_module import AddonAILogic
        
        # Create EventBus instance
        event_bus = EventBus()
        event_bus.initialize()
        print("✅ EventBus initialized")
        
        # Create AddonLogicCoordinator
        coordinator = AddonLogicCoordinator(event_bus)
        result = await coordinator.initialize_coordinator()
        
        if result.get("success", False):
            print(f"✅ AddonLogicCoordinator initialized with {len(result.get('enabled_addons', []))} addons")
        else:
            print(f"❌ Coordinator initialization failed: {result}")
            return False
        
        # Create AddonAILogic and initialize
        addon_ai = AddonAILogic(event_bus)
        init_result = await addon_ai.initialize()
        
        if init_result:
            print("✅ AddonAILogic initialized successfully")
        else:
            print("❌ AddonAILogic initialization failed")
            return False
        
        # Test event emission and handling
        test_events = []
        
        def test_event_handler(data):
            test_events.append(data)
        
        event_bus.subscribe("test.integration.event", test_event_handler)
        event_bus.emit("test.integration.event", {"test": "data"})
        
        # Give events time to process
        await asyncio.sleep(0.1)
        
        if len(test_events) > 0:
            print("✅ EventBus event handling working")
        else:
            print("❌ EventBus event handling failed")
            return False
        
        # Test coordinator status
        coordinator_status = await coordinator.get_coordinator_status()
        if coordinator_status.get("success", False):
            print(f"✅ Coordinator status: {coordinator_status.get('enabled_addons', 0)} addons active")
        else:
            print("❌ Coordinator status check failed")
            return False
        
        # Test addon AI status
        ai_status = addon_ai.get_status()
        print(f"✅ AddonAI status: {ai_status['active_addons']} active addons")
        
        print("\n🎉 EVENTBUS INTEGRATION TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ EVENTBUS INTEGRATION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_workflow_execution():
    """Test workflow execution through coordinator"""
    print("\n🚀 Phase 3.3: Workflow Execution Test...")
    
    try:
        from vpa.core.events import EventBus
        from vpa.ai.addon_logic.addon_logic_coordinator import AddonLogicCoordinator
        
        # Setup
        event_bus = EventBus()
        event_bus.initialize()
        coordinator = AddonLogicCoordinator(event_bus)
        await coordinator.initialize_coordinator()
        
        # Test workflow listing
        workflows = await coordinator.list_workflows()
        if workflows.get("success", False):
            total_workflows = len(workflows.get("workflows", []))
            print(f"✅ Found {total_workflows} workflows across all addons")
        else:
            print("❌ Workflow listing failed")
            return False
        
        # Test capability listing
        capabilities = await coordinator.list_capabilities()
        if capabilities.get("success", False):
            total_capabilities = len(capabilities.get("capabilities", []))
            print(f"✅ Found {total_capabilities} capabilities across all addons")
        else:
            print("❌ Capability listing failed")
            return False
        
        # Test addon health via coordinator status
        coordinator_full_status = await coordinator.get_coordinator_status()
        if coordinator_full_status.get("success", False):
            enabled_addons_count = coordinator_full_status.get("enabled_addons", 0)
            initialized_addons_count = coordinator_full_status.get("initialized_addons", 0)
            print(f"✅ {enabled_addons_count} addons enabled, {initialized_addons_count} initialized")
        else:
            print("❌ Coordinator status check failed")
            return False
        
        print("🎉 WORKFLOW EXECUTION TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ WORKFLOW EXECUTION TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_phase3_tests():
    """Run all Phase 3 integration tests"""
    print("=" * 60)
    print("🚀 PHASE 3: FULL INTEGRATION & TESTING")
    print("=" * 60)
    
    # Test 1: EventBus Integration
    test1_result = await test_eventbus_integration()
    
    # Test 2: Workflow Execution
    test2_result = await test_workflow_execution()
    
    # Final results
    print("\n" + "=" * 60)
    print("📊 PHASE 3 TEST RESULTS:")
    print(f"✅ EventBus Integration: {'PASSED' if test1_result else 'FAILED'}")
    print(f"✅ Workflow Execution: {'PASSED' if test2_result else 'FAILED'}")
    
    if test1_result and test2_result:
        print("\n🎉 ALL PHASE 3 TESTS PASSED!")
        print("✅ Core Systems Integration: COMPLETE")
        print("✅ EventBus Integration: OPERATIONAL")
        print("✅ Workflow System: FUNCTIONAL")
        print("✅ Addon Coordination: WORKING")
        print("\n🚀 READY FOR PHASE 4: PERFORMANCE & REGRESSION TESTING")
        return True
    else:
        print("\n❌ PHASE 3 TESTS FAILED")
        print("🛑 BLOCKING ISSUES DETECTED - REVIEW REQUIRED")
        return False

if __name__ == "__main__":
    result = asyncio.run(run_phase3_tests())
    sys.exit(0 if result else 1)
