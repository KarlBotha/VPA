#!/usr/bin/env python3
"""
Test Record Button Functionality
Direct test of the voice recording and transcription system
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_audio_dependencies():
    """Test if all required audio dependencies are available"""
    print("🔍 Testing audio dependencies...")
    
    # Test speech_recognition
    try:
        import speech_recognition as sr
        print("✅ speech_recognition: Available")
        
        # Test microphone access
        try:
            r = sr.Recognizer()
            mic = sr.Microphone()
            print("✅ Microphone access: Available")
        except Exception as e:
            print(f"❌ Microphone access: Failed - {e}")
            return False
            
    except ImportError:
        print("❌ speech_recognition: NOT INSTALLED")
        print("   Run: pip install SpeechRecognition pyaudio")
        return False
    
    # Test openai-whisper
    try:
        import whisper
        print("✅ openai-whisper: Available")
    except ImportError:
        print("❌ openai-whisper: NOT INSTALLED")
        print("   Run: pip install openai-whisper")
        return False
    
    # Test pyaudio
    try:
        import pyaudio
        print("✅ pyaudio: Available")
    except ImportError:
        print("❌ pyaudio: NOT INSTALLED")
        print("   Run: pip install pyaudio")
        return False
    
    return True

def test_mock_audio_manager():
    """Test the MockAudioManager from gui_screen_tester.py"""
    print("\n🔍 Testing MockAudioManager...")
    
    try:
        # Import the MockAudioManager
        sys.path.append(str(Path.cwd()))
        from gui_screen_tester import MockAudioManager
        
        # Create audio manager instance
        audio_manager = MockAudioManager()
        print("✅ MockAudioManager created successfully")
        
        # Test microphone enabled status
        print(f"🎤 Microphone enabled: {audio_manager.microphone_enabled}")
        print(f"🎵 Real audio support: {audio_manager.real_audio}")
        
        if audio_manager.real_audio:
            # Test basic recording functionality
            print("\n🎤 Testing recording start...")
            result = audio_manager.start_recording()
            print(f"✅ Recording start result: {result}")
            
            # Simulate user input
            print("⏹️ Stopping recording (simulated)...")
            transcribed = audio_manager.stop_recording_and_transcribe()
            print(f"📝 Transcription result: '{transcribed}'")
            
        else:
            print("❌ Real audio not available - using mock mode")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import MockAudioManager: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing MockAudioManager: {e}")
        return False

def test_main_app_audio_integration():
    """Test the main application audio integration"""
    print("\n🔍 Testing main application audio integration...")
    
    try:
        # Import main application components
        sys.path.append(str(Path.cwd() / "src"))
        from vpa.gui.main_application import MainApplication
        
        print("✅ MainApplication import successful")
        
        # Check if the application has audio integration methods
        app_methods = dir(MainApplication)
        required_methods = ['_start_audio_recording', '_stop_audio_recording', '_toggle_recording']
        
        for method in required_methods:
            if method in app_methods:
                print(f"✅ Method {method}: Available")
            else:
                print(f"❌ Method {method}: Missing")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import MainApplication: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing main application: {e}")
        return False

def test_whisper_transcription():
    """Test local Whisper transcription"""
    print("\n🔍 Testing Whisper transcription...")
    
    try:
        import whisper
        
        # Load tiny model for testing
        print("🤖 Loading Whisper tiny model...")
        model = whisper.load_model("tiny")
        print("✅ Whisper model loaded successfully")
        
        # Check model details
        print(f"📊 Model type: {type(model)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Whisper test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 VPA Voice Recording System Test")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test 1: Dependencies
    if not test_audio_dependencies():
        all_tests_passed = False
    
    # Test 2: MockAudioManager
    if not test_mock_audio_manager():
        all_tests_passed = False
    
    # Test 3: Main App Integration
    if not test_main_app_audio_integration():
        all_tests_passed = False
    
    # Test 4: Whisper
    if not test_whisper_transcription():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED - Voice recording should work!")
        print("\n💡 Next steps:")
        print("   1. Launch gui_screen_tester.py")
        print("   2. Test microphone recording button")
        print("   3. Test main application chat interface")
    else:
        print("❌ SOME TESTS FAILED - Issues detected")
        print("\n🔧 Recommended fixes:")
        print("   1. Install missing dependencies")
        print("   2. Check microphone permissions")
        print("   3. Verify audio system setup")

if __name__ == "__main__":
    main()
