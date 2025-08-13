"""
VPA Chat UI Simple Test
Test the new chat-first interface with synchronous approach.
"""

import sys
import os
import logging
import tkinter as tk
from tkinter import ttk

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from vpa.core.events import EventBus
from vpa.ui.components.chat_area import ChatArea
from vpa.ui.components.input_area import InputArea
from vpa.ui.components.resource_monitor import ResourceMonitor
from vpa.ui.components.settings_panel import SettingsPanel


def test_chat_components():
    """Test individual chat UI components."""
    print("🚀 VPA Chat Components Test")
    print("=" * 40)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create main window
    root = tk.Tk()
    root.title("VPA Chat UI Components Test")
    root.geometry("1000x700")
    
    # Create event bus
    event_bus = EventBus()
    event_bus.initialize()
    
    # Configure main layout
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    # Main frame
    main_frame = ttk.Frame(root, padding="10")
    main_frame.grid(row=0, column=0, sticky="nsew")
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(1, weight=1)
    
    print("📱 Creating chat components...")
    
    # Top row: Resource monitor
    resource_monitor = ResourceMonitor(main_frame, event_bus)
    resource_monitor.grid(row=0, column=0, sticky="nw", padx=(0, 10), pady=(0, 10))
    
    # Title
    title_label = ttk.Label(main_frame, text="VPA Chat Interface Test", font=("Segoe UI", 16, "bold"))
    title_label.grid(row=0, column=1, sticky="w", pady=(0, 10))
    
    # Chat area
    chat_area = ChatArea(main_frame, event_bus)
    chat_area.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
    
    # Input area
    input_frame = ttk.Frame(main_frame)
    input_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
    input_frame.columnconfigure(0, weight=1)
    
    input_area = InputArea(input_frame, event_bus)
    input_area.grid(row=0, column=0, sticky="ew")
    
    # Settings button
    def open_settings():
        settings_panel = SettingsPanel(root, event_bus)
        settings_panel.show()
    
    settings_btn = ttk.Button(input_frame, text="⚙️ Settings", command=open_settings)
    settings_btn.grid(row=0, column=1, padx=(10, 0))
    
    print("✅ Chat components created successfully!")
    
    # Test functionality
    def test_messages():
        """Add test messages to chat."""
        print("💬 Adding test messages...")
        
        chat_area.add_message({
            "type": "user",
            "content": "Hello VPA! This is a test of the new chat interface.",
            "timestamp": "2025-07-18T12:00:00"
        })
        
        chat_area.add_message({
            "type": "agent", 
            "content": "Hello! I'm your VPA assistant. The new chat-first interface is working perfectly! This interface features:\n\n• Modern chat bubbles with avatars\n• Scrollable message history\n• Multi-modal input support\n• Real-time resource monitoring\n• Comprehensive settings panel\n• Accessibility features",
            "timestamp": "2025-07-18T12:00:01"
        })
        
        chat_area.add_message({
            "type": "system",
            "content": "VPA Chat UI components loaded successfully. All systems operational.",
            "timestamp": "2025-07-18T12:00:02"
        })
    
    def test_resources():
        """Update resource monitor."""
        print("📊 Testing resource monitor...")
        resource_monitor.update_resources({
            "cpu": 45.2,
            "memory": 62.8,
            "gpu": 23.1,
            "storage": 78.5
        })
    
    # Add test data after a short delay
    root.after(500, test_messages)
    root.after(1000, test_resources)
    
    print("🖱️  Interact with the UI to test all features:")
    print("   • Type messages in the input area")
    print("   • Click the microphone button for voice input")
    print("   • Click the paperclip button for file upload")  
    print("   • Click Settings to open configuration")
    print("   • Click the resource monitor for detailed view")
    print("   • Scroll through chat history")
    
    # Handle input events
    def handle_message_sent(data):
        print(f"📤 Message sent: {data}")
        # Echo the message back as agent response
        chat_area.add_message({
            "type": "agent",
            "content": f"I received your message: \"{data.get('content', '')}\"",
            "timestamp": data.get('timestamp', '')
        })
    
    def handle_voice_recording(data):
        print(f"🎤 Voice recording started: {data}")
    
    def handle_file_upload(data):
        print(f"📎 File uploaded: {data}")
        chat_area.add_message({
            "type": "system",
            "content": f"File uploaded: {os.path.basename(data.get('file_path', 'unknown'))}",
            "timestamp": data.get('timestamp', '')
        })
    
    # Subscribe to events
    event_bus.subscribe("ui.input.message_sent", handle_message_sent)
    event_bus.subscribe("ui.input.voice_recording_started", handle_voice_recording)
    event_bus.subscribe("ui.input.file_uploaded", handle_file_upload)
    
    print("🎯 Phase 2.1 Chat UI Components Test Ready!")
    print("=" * 50)
    
    # Start the UI
    root.mainloop()


if __name__ == "__main__":
    test_chat_components()
