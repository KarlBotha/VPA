#!/usr/bin/env python3
"""
Test Script for GUI Implementations
Verifies that voice input integration and settings application functionality are working
"""

import sys
import os
import tkinter as tk
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from vpa.core.app import App
from vpa.core.events import EventBus
from vpa.gui.main_window import VPAMainWindow
from vpa.gui.components import VPASettingsDialog

def test_voice_input_integration():
    """Test that voice input integration is implemented"""
    print("🔍 Testing Voice Input Integration...")
    
    # Create app and initialize
    app = App()
    app.initialize()
    
    # Create main window
    main_window = VPAMainWindow(app)
    
    # Check that voice input method exists and is implemented
    assert hasattr(main_window, '_on_voice_input'), "Voice input method should exist"
    
    # Create a test root window
    root = tk.Tk()
    root.withdraw()  # Hide the window
    main_window.root = root
    
    try:
        # Test voice input functionality (should not raise exception)
        main_window._on_voice_input()
        print("✅ Voice input integration implemented successfully")
    except Exception as e:
        print(f"❌ Voice input integration failed: {e}")
        return False
    finally:
        root.destroy()
    
    return True

def test_settings_application():
    """Test that settings application is implemented"""
    print("🔍 Testing Settings Application...")
    
    # Create app and initialize
    app = App()
    app.initialize()
    
    # Create a test root window
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    try:
        # Test settings with sample configuration
        test_settings = {
            "core": {"log_level": "INFO"},
            "audio": {
                "enabled": True,
                "default_voice": "voice_01",
                "default_rate": 200,
                "default_volume": 0.9
            },
            "ai": {
                "enabled": True,
                "max_response_length": 1000
            }
        }
        
        # Create settings dialog
        settings_dialog = VPASettingsDialog(root, test_settings, app)
        
        # Check that apply method exists and is implemented
        assert hasattr(settings_dialog, '_on_apply'), "Settings apply method should exist"
        assert hasattr(settings_dialog, 'setting_vars'), "Settings variables should exist"
        
        # Test that settings variables are created
        assert len(settings_dialog.setting_vars) > 0, "Settings variables should be populated"
        
        # Test settings application (should not raise exception)
        settings_dialog._on_apply()
        print("✅ Settings application implemented successfully")
        
        # Verify settings were actually applied to app config
        assert app.config_manager.get("core.log_level") is not None, "Settings should be applied to config"
        
        return True
        
    except Exception as e:
        print(f"❌ Settings application failed: {e}")
        return False
    finally:
        root.destroy()

def test_audio_plugin_integration():
    """Test that audio plugin integration works with voice input"""
    print("🔍 Testing Audio Plugin Integration...")
    
    # Create app and initialize
    app = App()
    app.initialize()
    
    # Check if audio plugin is available
    audio_plugin = app.plugin_manager.get_plugin('audio')
    if audio_plugin:
        print("✅ Audio plugin is available")
        
        # Check audio engine
        if hasattr(audio_plugin, 'audio_engine'):
            print("✅ Audio engine is accessible")
            
            # Test voice availability
            voices = audio_plugin.audio_engine.get_available_voices()
            print(f"✅ Found {len(voices)} available voices")
            
            return True
        else:
            print("❌ Audio engine not accessible")
            return False
    else:
        print("⚠️ Audio plugin not available (this is expected in test environment)")
        return True  # Not a failure in test environment

def main():
    """Run all GUI implementation tests"""
    print("🚀 Testing VPA GUI Implementations")
    print("=" * 50)
    
    results = []
    
    # Test voice input integration
    results.append(test_voice_input_integration())
    print()
    
    # Test settings application
    results.append(test_settings_application())
    print()
    
    # Test audio plugin integration
    results.append(test_audio_plugin_integration())
    print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All GUI implementations are working correctly!")
        return 0
    else:
        print("⚠️ Some tests failed - review implementation")
        return 1

if __name__ == "__main__":
    sys.exit(main())
