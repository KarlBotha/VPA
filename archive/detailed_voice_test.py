#!/usr/bin/env python3
"""
Focused Voice Diagnostics - Test specific voice issues
"""

import pyttsx3
import time

def test_voice_individually():
    print("🔧 FOCUSED VOICE DIAGNOSTICS")
    print("Testing each voice individually with detailed settings")
    print("=" * 60)
    
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        print(f"System Info:")
        print(f"  Engine: {engine}")
        print(f"  Total voices: {len(voices) if voices else 0}")
        print()
        
        if not voices:
            print("❌ No voices found!")
            return
        
        for i, voice in enumerate(voices):
            print(f"{'='*60}")
            print(f"TESTING VOICE {i+1}: {voice.name}")
            print(f"{'='*60}")
            print(f"Voice ID: {voice.id}")
            print(f"Languages: {getattr(voice, 'languages', 'Unknown')}")
            
            # Test with maximum volume and slower rate
            engine.setProperty('voice', voice.id)
            engine.setProperty('volume', 1.0)  # Maximum volume
            engine.setProperty('rate', 150)    # Slower rate
            
            # Get current properties to verify they were set
            current_voice = engine.getProperty('voice')
            current_volume = engine.getProperty('volume')
            current_rate = engine.getProperty('rate')
            
            print(f"Settings applied:")
            print(f"  Voice ID set to: {current_voice}")
            print(f"  Volume: {current_volume}")
            print(f"  Rate: {current_rate}")
            
            # Test message
            test_message = f"This is voice number {i+1}, {voice.name}. Testing maximum volume and slower speech. Can you hear me clearly?"
            print(f"\n🔊 Playing: \"{test_message}\"")
            print("Listen carefully...")
            
            try:
                engine.say(test_message)
                engine.runAndWait()
                print("✅ Voice playback completed")
            except Exception as e:
                print(f"❌ Playback error: {e}")
            
            # Ask for individual confirmation
            while True:
                response = input(f"\nDid you hear voice {i+1} ({voice.name}) clearly? (yes/no): ").lower().strip()
                if response in ['yes', 'y']:
                    print(f"✅ {voice.name} - CONFIRMED WORKING")
                    break
                elif response in ['no', 'n']:
                    print(f"❌ {voice.name} - NOT WORKING")
                    break
                else:
                    print("Please enter 'yes' or 'no'")
            
            # Pause between voices (except last)
            if i < len(voices) - 1:
                print("\n⏸️  Pausing 3 seconds before next voice...")
                time.sleep(3)
        
        print(f"\n{'='*60}")
        print("🎯 FINAL VOICE ASSESSMENT")
        print("Which voices are working correctly?")
        print("Please list the voice numbers that you can hear clearly.")
        
        working_voices = input("Enter voice numbers (e.g., '1,3' or 'only 1'): ").strip()
        print(f"\nYour feedback: {working_voices}")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")

if __name__ == "__main__":
    test_voice_individually()
