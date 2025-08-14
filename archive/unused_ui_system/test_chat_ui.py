"""
VPA Chat UI Test
Test the new chat-first interface implementation.
"""

import asyncio
import sys
import os
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from vpa.core.events import EventBus
from vpa.ui.chat_ui import VPAChatUI


async def test_chat_ui():
    """Test the VPA Chat UI implementation."""
    print("🚀 VPA Chat UI Test - Phase 2.1")
    print("=" * 50)
    
    try:
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        
        # Create event bus
        event_bus = EventBus()
        event_bus.initialize()
        
        # Create chat UI
        print("📱 Creating VPA Chat UI...")
        chat_ui = VPAChatUI(event_bus)
        
        # Initialize UI
        print("🔄 Initializing chat interface...")
        success = await chat_ui.initialize()
        
        if success:
            print("✅ Chat UI initialized successfully!")
            
            # Show UI
            await chat_ui.show()
            
            # Add test messages
            print("💬 Adding test messages...")
            await chat_ui.add_message("system", "VPA Chat UI Test Started")
            await asyncio.sleep(1)
            
            await chat_ui.add_message("user", "Hello VPA! This is a test message.")
            await asyncio.sleep(1)
            
            await chat_ui.add_message("agent", "Hello! I'm your VPA assistant. The new chat interface is working perfectly!")
            await asyncio.sleep(1)
            
            # Test resource monitor
            print("📊 Testing resource monitor...")
            await chat_ui.update_resources({
                "cpu": 45.2,
                "memory": 62.8,
                "gpu": 23.1,
                "storage": 78.5
            })
            
            print("✨ Chat UI test completed!")
            print("🖱️  Interact with the UI to test all features")
            print("⚙️  Click Settings to test configuration panel")
            print("📦 Click the + button to test new chat functionality")
            print("🎤 Click the microphone to test voice input")
            print("📎 Click the paperclip to test file upload")
            
            # Keep running until user closes
            while chat_ui.is_running():
                await asyncio.sleep(0.1)
                
        else:
            print("❌ Failed to initialize Chat UI")
            
    except Exception as e:
        print(f"❌ Chat UI test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_chat_ui())
