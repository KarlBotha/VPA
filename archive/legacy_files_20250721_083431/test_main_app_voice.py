#!/usr/bin/env python3
"""
Direct VPA Main Application Launcher - For Voice Recording Test
"""

import sys
import os
from pathlib import Path
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

# Add src to path
current_dir = Path(__file__).resolve().parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

# Import the mock managers from gui_screen_tester
from gui_screen_tester import MockGUIManager

def launch_main_app():
    """Launch the main application directly"""
    try:
        # Setup CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create root window (hidden)
        root = ctk.CTk()
        root.withdraw()  # Hide the root window
        
        # Import and create main application
        from vpa.gui.main_application import VPAMainApplication
        
        # Create mock GUI manager with real audio
        gui_manager = MockGUIManager()
        
        # Show LLM status
        if gui_manager.llm_manager.ollama_available:
            print(f"✅ Ollama detected: {gui_manager.llm_manager.current_model}")
            print(f"📝 Available models: {gui_manager.llm_manager.available_models}")
        else:
            print("⚠️ Ollama not available - using mock responses")
        
        # Test audio manager
        print(f"🎤 Audio manager real_audio: {gui_manager.audio_manager.real_audio}")
        print(f"🔊 Voice system ready: {len(gui_manager.audio_manager.get_voices())} voices")
        
        # Launch main application
        print("🚀 Launching VPA Main Application...")
        main_app = VPAMainApplication(root, gui_manager, "test_user", "test_session")
        
        print("\n" + "="*60)
        print("🎯 VPA MAIN APPLICATION READY FOR VOICE TESTING!")
        print("="*60)
        print("📋 TESTING INSTRUCTIONS:")
        print("1. Look for the 🎤 Record button in the chat interface")
        print("2. Click it to start recording (button turns red ⏹️)")
        print("3. Speak clearly: 'Hello, test the voice recording system'")
        print("4. Click the ⏹️ Stop button")
        print("5. Watch for:")
        print("   ✅ Transcribed text appears as your message")
        print("   ✅ VPA responds to your transcribed message")
        print("   ❌ Any error messages about audio capture")
        print("="*60)
        print("⚠️ FOCUS: Test the MAIN CHAT voice recording, not settings!")
        print("="*60)
        
        # Run the application
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Failed to launch main application: {e}")
        messagebox.showerror("Launch Error", f"Failed to launch: {str(e)}")

if __name__ == "__main__":
    try:
        launch_main_app()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
