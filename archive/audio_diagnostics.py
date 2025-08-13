#!/usr/bin/env python3
"""
Audio Diagnostics and Troubleshooting
"""

import pyttsx3
import sys
import platform

def audio_diagnostics():
    print("🔧 VPA AUDIO DIAGNOSTICS")
    print("=" * 50)
    
    # System info
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    
    try:
        # Test pyttsx3 basic functionality
        print("\n📊 Testing pyttsx3 functionality...")
        engine = pyttsx3.init()
        print("✅ pyttsx3 engine created successfully")
        
        # Check current properties
        try:
            current_rate = engine.getProperty('rate')
            current_volume = engine.getProperty('volume')
            current_voice = engine.getProperty('voice')
            
            print(f"Current rate: {current_rate}")
            print(f"Current volume: {current_volume}")
            print(f"Current voice ID: {current_voice}")
        except Exception as e:
            print(f"⚠️  Property check failed: {e}")
        
        # Voice enumeration
        print("\n🎤 Available Voices:")
        voices = engine.getProperty('voices')
        
        if voices:
            for i, voice in enumerate(voices):
                print(f"  [{i}] {voice.name}")
                print(f"      ID: {voice.id}")
                print(f"      Languages: {getattr(voice, 'languages', 'Unknown')}")
                print()
        else:
            print("❌ No voices detected!")
            
        # Audio test with different settings
        print("🔊 Testing with maximum volume and slower rate...")
        engine.setProperty('volume', 1.0)  # Maximum volume
        engine.setProperty('rate', 150)    # Slower rate
        
        test_message = "This is an audio test with maximum volume and slower speech rate. Can you hear this message?"
        print(f"Test message: '{test_message}'")
        
        engine.say(test_message)
        engine.runAndWait()
        
        print("✅ Audio test completed")
        
    except Exception as e:
        print(f"❌ pyttsx3 error: {e}")
        return False
    
    return True

def main():
    if audio_diagnostics():
        print("\n" + "=" * 50)
        print("🎯 FINAL AUDIO TEST")
        print("Did you hear the final test message clearly?")
        
        while True:
            response = input("Enter 'yes' or 'no': ").lower().strip()
            if response in ['yes', 'y']:
                print("✅ AUDIO CONFIRMED: System is working!")
                return 0
            elif response in ['no', 'n']:
                print("❌ AUDIO ISSUE: Please check:")
                print("  • Speaker/headphone connections")
                print("  • Windows audio settings")
                print("  • Volume mixer settings")
                print("  • Default audio device")
                return 1
            else:
                print("Please enter 'yes' or 'no'")
    else:
        print("❌ Audio system diagnosis failed")
        return 1

if __name__ == "__main__":
    exit(main())
