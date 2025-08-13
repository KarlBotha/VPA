#!/usr/bin/env python3
"""
Quick Record Button Dependency Check
"""

def test_dependencies():
    """Test if all required dependencies are available"""
    print("🧪 Testing Record Button Dependencies...")
    
    # Test speech_recognition
    try:
        import speech_recognition as sr
        print("✅ speech_recognition available")
    except ImportError:
        print("❌ speech_recognition missing")
        return False
    
    # Test whisper
    try:
        import whisper
        print("✅ whisper available")
    except ImportError:
        print("❌ whisper missing")
        return False
    
    # Test audio manager
    try:
        import sys
        sys.path.append('.')
        from gui_screen_tester import MockAudioManager
        audio_manager = MockAudioManager()
        print(f"✅ MockAudioManager created, real_audio: {audio_manager.real_audio}")
        
        if audio_manager.real_audio:
            print("✅ All dependencies satisfied - Record button should work!")
            return True
        else:
            print("❌ Real audio not enabled")
            return False
            
    except Exception as e:
        print(f"❌ MockAudioManager test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_dependencies()
    if success:
        print("\n🎉 RECORD BUTTON READY - All dependencies satisfied!")
    else:
        print("\n⚠️ RECORD BUTTON NOT READY - Missing dependencies!")
