#!/usr/bin/env python3
"""
Simple Voice Testing Script - Play actual voices for verification
Tests the real pyttsx3 audio system with available system voices
"""

import pyttsx3
import time
import sys

def test_voices():
    """Test available voices on the system"""
    print("=" * 80)
    print("🎵 VPA VOICE TESTING UTILITY")
    print("Tests actual voices through pyttsx3 for audio verification")
    print("=" * 80)
    
    try:
        # Initialize pyttsx3 engine
        print("\n🔧 Initializing pyttsx3 engine...")
        engine = pyttsx3.init()
        print("✅ pyttsx3 engine initialized successfully")
        
        # Get available voices
        print("\n🔍 Discovering available voices...")
        voices = engine.getProperty('voices')
        
        if not voices:
            print("❌ No voices found on system")
            return 1
        
        print(f"✅ Found {len(voices)} system voices:")
        
        # List all voices
        for i, voice in enumerate(voices):
            print(f"\n  [{i+1}] {voice.name}")
            print(f"      ID: {voice.id}")
            if hasattr(voice, 'languages'):
                print(f"      Languages: {voice.languages}")
        
        print("\n" + "=" * 80)
        print("🔊 VOICE TESTING BEGINS")
        print("Press Ctrl+C at any time to stop")
        print("=" * 80)
        
        # Test each voice
        for i, voice in enumerate(voices):
            try:
                print(f"\n[{i+1}/{len(voices)}] Testing: {voice.name}")
                
                # Set voice properties
                engine.setProperty('voice', voice.id)
                engine.setProperty('rate', 200)    # Words per minute
                engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
                
                # Test message
                test_message = f"Hello! This is {voice.name}, voice number {i+1}. Testing audio output."
                print(f"   Message: \"{test_message}\"")
                
                # Speak the message
                engine.say(test_message)
                engine.runAndWait()
                
                print("✅ Voice test completed")
                
                # Pause between voices (except for the last one)
                if i < len(voices) - 1:
                    print("⏸️  Pausing 2 seconds before next voice...")
                    time.sleep(2)
                
            except KeyboardInterrupt:
                print("\n⏹️  Voice testing stopped by user")
                break
            except Exception as e:
                print(f"❌ Error testing voice {voice.name}: {e}")
                continue
        
        print(f"\n🎉 Voice testing complete! Tested {len(voices)} voices.")
        
        # Ask for confirmation
        print("\n" + "=" * 80)
        print("🎯 VOICE CONFIRMATION")
        print("Did you hear all the voices clearly?")
        print("Type 'yes' to confirm voices are working, or 'no' if there were issues:")
        
        while True:
            response = input("Voice confirmation (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                print("✅ Voice confirmation received! Voices are working correctly.")
                return 0
            elif response in ['no', 'n']:
                print("⚠️  Voice issues reported. Please check audio system.")
                return 1
            else:
                print("Please enter 'yes' or 'no'")
        
    except KeyboardInterrupt:
        print("\n👋 Voice testing interrupted by user")
        return 0
    except Exception as e:
        print(f"❌ Critical error during voice testing: {e}")
        print("This might indicate audio system issues.")
        return 1
    finally:
        try:
            engine.stop()
        except:
            pass

if __name__ == "__main__":
    exit_code = test_voices()
    print(f"\n🏁 Voice testing exiting with code: {exit_code}")
    sys.exit(exit_code)
