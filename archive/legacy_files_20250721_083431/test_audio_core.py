#!/usr/bin/env python3
"""
Simple Audio Recording Test - No GUI
Direct test of the core audio recording functionality
"""

import logging
import tempfile
import os
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_microphone_basic():
    """Test basic microphone functionality"""
    print("🎤 Testing basic microphone access...")
    
    try:
        import speech_recognition as sr
        
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        print("✅ Speech recognition and microphone initialized")
        
        # Test microphone list
        mic_list = sr.Microphone.list_microphone_names()
        print(f"🎵 Available microphones: {len(mic_list)}")
        for i, mic_name in enumerate(mic_list[:3]):  # Show first 3
            print(f"   {i}: {mic_name}")
        
        # Test ambient noise adjustment
        print("🔧 Testing ambient noise calibration...")
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
        print("✅ Ambient noise calibration successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False

def test_recording_and_transcription():
    """Test actual recording and transcription"""
    print("\n🎤 Testing recording and transcription...")
    
    try:
        import speech_recognition as sr
        import whisper
        
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        print("🔊 Recording for 3 seconds... Please speak now!")
        
        with microphone as source:
            # Quick calibration
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Record audio
            audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=3)
        
        print("✅ Audio recorded successfully")
        
        # Save to temporary file for Whisper
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            temp_path = tmp_file.name
        
        try:
            # Write audio data to file
            with open(temp_path, "wb") as f:
                f.write(audio_data.get_wav_data())
            
            print("🤖 Transcribing with Whisper...")
            model = whisper.load_model("tiny")
            result = model.transcribe(temp_path)
            
            transcribed_text = result["text"].strip()
            print(f"📝 Transcription: '{transcribed_text}'")
            
            if transcribed_text:
                print("✅ Recording and transcription working correctly!")
                return True
            else:
                print("⚠️ No speech detected in recording")
                return False
                
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
        
    except Exception as e:
        print(f"❌ Recording/transcription test failed: {e}")
        return False

def test_dependencies():
    """Check all required dependencies"""
    print("🔍 Checking dependencies...")
    
    dependencies = [
        ("speech_recognition", "SpeechRecognition"),
        ("whisper", "openai-whisper"),
        ("pyaudio", "PyAudio")
    ]
    
    all_available = True
    
    for module_name, package_name in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {package_name}: Available")
        except ImportError:
            print(f"❌ {package_name}: Missing")
            all_available = False
    
    return all_available

def main():
    """Run focused audio tests"""
    print("🚀 VPA Audio Recording Test - Core Functionality")
    print("=" * 55)
    
    # Test 1: Dependencies
    if not test_dependencies():
        print("\n❌ Missing dependencies detected!")
        print("Please install missing packages and try again.")
        return
    
    # Test 2: Basic microphone
    if not test_microphone_basic():
        print("\n❌ Basic microphone test failed!")
        return
    
    # Test 3: Recording and transcription
    print("\n" + "="*55)
    print("🎯 ACTUAL RECORDING TEST")
    print("When prompted, please speak clearly for 3 seconds")
    input("Press ENTER when ready to start recording...")
    
    if test_recording_and_transcription():
        print("\n🎉 SUCCESS! Voice recording and transcription working!")
        print("\n💡 Your microphone and audio system are functioning correctly.")
        print("The issue may be in the GUI integration or main application.")
    else:
        print("\n❌ Recording test failed.")
        print("Check your microphone settings and try again.")

if __name__ == "__main__":
    main()
