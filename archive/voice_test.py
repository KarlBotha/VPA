#!/usr/bin/env python3
"""
Voice Testing Script for VPA Audio Verification
"""

import pyttsx3
import time

def main():
    print("🎵 VPA Voice Testing - Checking Audio Output")
    print("=" * 50)
    
    try:
        # Initialize engine
        engine = pyttsx3.init()
        print("✅ Audio engine initialized")
        
        # Get voices
        voices = engine.getProperty('voices')
        
        if voices:
            voice_count = 0
            for voice in voices:
                voice_count += 1
            
            print(f"✅ Found {voice_count} voices on system")
            print("\n🔊 Testing voices - listen carefully...")
            print("Press Ctrl+C to stop at any time\n")
            
            voice_num = 0
            for voice in voices:
                voice_num += 1
                try:
                    print(f"[{voice_num}] Testing: {voice.name}")
                    
                    # Configure voice
                    engine.setProperty('voice', voice.id)
                    engine.setProperty('rate', 200)
                    engine.setProperty('volume', 0.9)
                    
                    # Test message
                    message = f"Hello! This is voice {voice_num}, {voice.name}. Can you hear me clearly?"
                    
                    # Speak
                    engine.say(message)
                    engine.runAndWait()
                    
                    print("   ✅ Test complete")
                    
                    # Pause between voices
                    if voice_num < voice_count:
                        print("   ⏸️  Pausing...")
                        time.sleep(2)
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            
            print(f"\n🎉 All {voice_count} voices tested!")
            
        else:
            print("❌ No voices found")
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    # Get user confirmation
    print("\n" + "=" * 50)
    print("🎯 CONFIRMATION REQUIRED")
    print("Did you hear all voices playing clearly?")
    
    while True:
        response = input("Enter 'yes' if voices worked, 'no' if issues: ").lower().strip()
        if response in ['yes', 'y']:
            print("✅ CONFIRMED: Voices are working correctly!")
            print("We can proceed with the 100% mandate compliance validation.")
            return 0
        elif response in ['no', 'n']:
            print("⚠️  ISSUE REPORTED: Audio system needs attention")
            print("Please check speakers/headphones and audio drivers.")
            return 1
        else:
            print("Please enter 'yes' or 'no'")

if __name__ == "__main__":
    exit(main())
