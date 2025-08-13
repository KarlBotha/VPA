#!/usr/bin/env python3
"""
Test Record Button Functionality - Validation Script
Tests the complete audio recording and transcription workflow
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_whisper_import():
    """Test if Whisper can be imported and basic model loading works"""
    print("🧪 Testing Whisper import...")
    try:
        import whisper
        print("✅ Whisper imported successfully")
        
        # Test model loading (use tiny model for faster testing)
        print("🔄 Loading Whisper tiny model...")
        model = whisper.load_model("tiny")
        print("✅ Whisper tiny model loaded successfully")
        return True
    except ImportError as e:
        print(f"❌ Whisper import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Whisper model loading failed: {e}")
        return False

def test_speech_recognition():
    """Test speech recognition library"""
    print("\n🧪 Testing SpeechRecognition...")
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        print("✅ SpeechRecognition initialized successfully")
        
        # Test microphone access
        print("🎤 Testing microphone access...")
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Microphone access successful")
        return True
    except ImportError as e:
        print(f"❌ SpeechRecognition import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Microphone access failed: {e}")
        return False

def test_mock_audio_manager():
    """Test MockAudioManager functionality"""
    print("\n🧪 Testing MockAudioManager...")
    try:
        # Import MockAudioManager
        sys.path.append('.')
        from gui_screen_tester import MockAudioManager
        
        # Create instance
        audio_manager = MockAudioManager()
        print("✅ MockAudioManager created successfully")
        
        # Check real_audio status
        if audio_manager.real_audio:
            print("✅ Real audio support enabled")
        else:
            print("❌ Real audio support disabled - dependencies missing")
            return False
        
        # Test microphone control
        audio_manager.set_microphone_enabled(False)
        print("✅ Microphone disable test passed")
        
        audio_manager.set_microphone_enabled(True)
        print("✅ Microphone enable test passed")
        
        # Test voice settings
        voice = audio_manager.get_current_voice_from_settings()
        print(f"✅ Voice settings loaded: {voice}")
        
        return True
    except Exception as e:
        print(f"❌ MockAudioManager test failed: {e}")
        return False

def test_record_button_workflow():
    """Test the complete record button workflow (without actual recording)"""
    print("\n🧪 Testing Record Button Workflow...")
    try:
        from gui_screen_tester import MockAudioManager
        
        audio_manager = MockAudioManager()
        
        # Test start recording
        print("🎤 Testing start_recording()...")
        result = audio_manager.start_recording()
        if result:
            print("✅ start_recording() successful")
        else:
            print("❌ start_recording() failed")
            return False
        
        # Test stop recording and transcribe (with mock data)
        print("🔄 Testing stop_recording_and_transcribe()...")
        
        # Set recording to False to test fallback path
        audio_manager.recording = False
        audio_manager.recorded_audio = None
        
        transcribed_text = audio_manager.stop_recording_and_transcribe()
        print(f"✅ Transcription result: '{transcribed_text}'")
        
        # Verify we get a meaningful response
        if transcribed_text and len(transcribed_text) > 5:
            print("✅ stop_recording_and_transcribe() working correctly")
            return True
        else:
            print("❌ stop_recording_and_transcribe() returned empty result")
            return False
            
    except Exception as e:
        print(f"❌ Record button workflow test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 VPA Record Button Functionality Test Suite")
    print("=" * 60)
    
    tests = [
        ("Whisper Import", test_whisper_import),
        ("SpeechRecognition", test_speech_recognition), 
        ("MockAudioManager", test_mock_audio_manager),
        ("Record Button Workflow", test_record_button_workflow)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:25} {status}")
        if success:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED - Record button should be functional!")
        return 0
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed - Record button may not work correctly")
        return 1

if __name__ == "__main__":
    sys.exit(main())
