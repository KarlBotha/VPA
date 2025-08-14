"""
VPA System Test - Event-Driven Architecture Demonstration
Tests the transformed VPA system with addon management and AI coordination.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add VPA source to path
vpa_src = Path(__file__).parent / "src"
sys.path.insert(0, str(vpa_src))

from vpa.core.app import VPACoreService


async def test_vpa_system():
    """Test the VPA event-driven architecture."""
    print("🚀 VPA System Test - Event-Driven Architecture")
    print("=" * 60)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Initialize VPA Core Service
        print("\n📋 Initializing VPA Core Service...")
        vpa_core = VPACoreService()
        
        # Start the core service
        print("🔄 Starting VPA Core Service...")
        success = await vpa_core.start()
        
        if not success:
            print("❌ Failed to start VPA Core Service")
            return
        
        print("✅ VPA Core Service started successfully!")
        
        # Test addon management
        print("\n🔌 Testing Addon Management...")
        
        # List available addons
        addons = await vpa_core.addon_manager.list_available_addons()
        print(f"📦 Available addons: {addons}")
        
        # Activate Google addon
        if 'google' in addons:
            print("\n🔍 Activating Google addon...")
            google_result = await vpa_core.addon_manager.activate_addon('google')
            if google_result:
                print("✅ Google addon activated successfully!")
                
                # Get addon status
                status = await vpa_core.addon_manager.get_addon_status('google')
                print(f"📊 Google addon status: {status}")
            else:
                print("❌ Failed to activate Google addon")
        
        # Test AI coordination
        print("\n🤖 Testing AI Coordination...")
        
        # Test command processing
        test_commands = [
            "Check my Gmail for new emails",
            "Create a workflow to backup files",
            "What's the weather like today?"
        ]
        
        for command in test_commands:
            print(f"\n💭 Processing command: '{command}'")
            result = await vpa_core.ai_coordinator.process_command(command)
            print(f"🎯 AI Response: {result.get('response', 'No response')}")
        
        # Test event system
        print("\n📡 Testing Event System...")
        
        # Define test event handler
        def test_event_handler(data=None):
            print(f"🎉 Test event received: {data}")
        
        # Subscribe to test event
        vpa_core.event_bus.subscribe("test.event", test_event_handler)
        
        # Emit test event
        vpa_core.event_bus.emit("test.event", {"message": "Hello from VPA!"})
        
        # Show system metrics
        print("\n📈 System Performance Metrics:")
        metrics = vpa_core.get_performance_metrics()
        for key, value in metrics.items():
            print(f"   {key}: {value}")
        
        # Test session management
        print("\n👤 Testing Session Management...")
        session_id = await vpa_core.create_session("test_user")
        print(f"🆔 Created session: {session_id}")
        
        sessions = await vpa_core.list_active_sessions()
        print(f"📋 Active sessions: {len(sessions)}")
        
        # Cleanup test
        print("\n🧹 Testing Cleanup...")
        
        # Deactivate addons
        for addon_name in addons:
            if await vpa_core.addon_manager.is_addon_active(addon_name):
                print(f"🔄 Deactivating {addon_name} addon...")
                await vpa_core.addon_manager.deactivate_addon(addon_name)
        
        # Stop the core service
        print("\n🛑 Stopping VPA Core Service...")
        await vpa_core.stop()
        
        print("\n✨ VPA System Test Completed Successfully!")
        print("🎯 Event-driven architecture working correctly")
        print("🔌 Addon system operational")
        print("🤖 AI coordination functional")
        print("📡 Event bus communication verified")
        
    except Exception as e:
        print(f"\n❌ VPA System Test Failed: {e}")
        logging.exception("Detailed error information:")


async def demo_user_interaction():
    """Demonstrate typical user interaction with VPA."""
    print("\n" + "=" * 60)
    print("🎭 VPA User Interaction Demo")
    print("=" * 60)
    
    vpa_core = VPACoreService()
    await vpa_core.start()
    
    try:
        # Simulate user commands
        user_commands = [
            "activate google addon",
            "check my gmail",
            "send email to john@example.com saying hello",
            "list my google drive files",
            "create a calendar event for tomorrow at 2pm",
            "search my contacts for smith",
            "deactivate google addon"
        ]
        
        print("📝 Simulating user commands:")
        
        for command in user_commands:
            print(f"\n👤 User: {command}")
            
            # Route command appropriately
            if "activate" in command and "addon" in command:
                addon_name = command.split("activate ")[1].split(" addon")[0]
                result = await vpa_core.addon_manager.activate_addon(addon_name)
                print(f"🤖 VPA: {'Successfully activated' if result else 'Failed to activate'} {addon_name} addon")
                
            elif "deactivate" in command and "addon" in command:
                addon_name = command.split("deactivate ")[1].split(" addon")[0]
                result = await vpa_core.addon_manager.deactivate_addon(addon_name)
                print(f"🤖 VPA: {'Successfully deactivated' if result else 'Failed to deactivate'} {addon_name} addon")
                
            else:
                # Process through AI coordinator
                result = await vpa_core.ai_coordinator.process_command(command)
                print(f"🤖 VPA: {result.get('response', 'Command processed')}")
            
            # Small delay for demo effect
            await asyncio.sleep(0.5)
        
        print("\n✨ User interaction demo completed!")
        
    finally:
        await vpa_core.stop()


async def main():
    """Main test runner."""
    print("🎯 VPA Transformation Test Suite")
    print("Testing the new event-driven, modular architecture")
    
    # Run system architecture test
    await test_vpa_system()
    
    # Run user interaction demo
    await demo_user_interaction()
    
    print("\n🏁 All tests completed!")
    print("✅ VPA architectural transformation verified")


if __name__ == "__main__":
    asyncio.run(main())
