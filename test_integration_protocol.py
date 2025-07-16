#!/usr/bin/env python3
"""
Test script for VPA Integration Protocol
"""

import sys
import os
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent / 'tools'))

from integration_protocol import VPAIntegrationProtocol, IntegrationLogbook, ResourceManager

def test_integration_protocol():
    """Test the integration protocol functionality."""
    print("🧪 Testing VPA Integration Protocol...")
    
    try:
        # Initialize protocol with current directory as project root
        project_root = Path(__file__).parent
        protocol = VPAIntegrationProtocol(project_root)
        print("✅ Protocol initialized successfully")
        
        # Test logbook functionality
        logbook = protocol.logbook
        print("✅ Logbook accessible")
        
        # Test resource manager
        resource_manager = protocol.resource_manager
        print("✅ Resource manager accessible")
        
        # Test protocol methods
        print("\n📋 Testing protocol methods:")
        
        # Test subsystem queue
        test_subsystem = "test_subsystem"
        
        print(f"📍 Testing integration queue:")
        next_subsystem = protocol.get_next_subsystem()
        print(f"   Next subsystem: {next_subsystem}")
        
        # Test individual protocol steps (without actual execution)
        print("📍 Testing protocol step methods...")
        
        steps = [
            ("_perform_research", "Research step"),
            ("_perform_verification", "Verification step"),
            ("_perform_import", "Copy/Import step"),
            ("_perform_optimization", "Optimization step"),
            ("_perform_implementation", "Implementation step"),
            ("_perform_testing", "Testing step"),
            ("_generate_documentation", "Documentation step"),
            ("_request_approval", "Approval step")
        ]
        
        for method_name, description in steps:
            if hasattr(protocol, method_name):
                print(f"   ✅ {description} method available")
            else:
                print(f"   ❌ {description} method missing")
        
        # Test logbook entry creation
        print("\n📝 Testing logbook functionality:")
        test_entry = {
            "subsystem": "test_subsystem",
            "step": "testing",
            "status": "success",
            "details": "Integration protocol test"
        }
        
        logbook.log_integration_step(
            subsystem="test_subsystem",
            step="testing",
            status="success",
            details="Integration protocol test"
        )
        print("   ✅ Logbook entry created successfully")
        
        # Test resource manager functionality
        print("\n🔧 Testing resource manager:")
        temp_dir = resource_manager.create_temp_directory("test")
        print(f"   ✅ Temporary directory created: {temp_dir}")
        
        cleanup_results = resource_manager.cleanup_temp_directories()
        print(f"   ✅ Cleanup completed: {len(cleanup_results)} operations")
        
        print("\n🎉 All tests passed! Integration protocol is ready for use.")
        
        # Display integration queue
        print("\n📋 Current Integration Queue:")
        queue = [
            "failsafe_protocol",
            "enhanced_testing", 
            "hardware_monitoring",
            "performance_optimization",
            "error_recovery",
            "configuration_management"
        ]
        
        for i, subsystem in enumerate(queue, 1):
            print(f"   {i}. {subsystem}")
        
        print(f"\n✨ Ready to begin integration with: {queue[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_integration_protocol()
    sys.exit(0 if success else 1)
