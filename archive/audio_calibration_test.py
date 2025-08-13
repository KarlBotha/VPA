#!/usr/bin/env python3
"""
Audio Calibration Test Script
Tests microphone input and speaker output independently
"""

import time
import sys

def test_microphone():
    """Test microphone recording"""
    print("🎤 MICROPHONE TEST")
    print("=" * 50)
    
    try:
        import speech_recognition as sr
        
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("🔧 Calibrating for ambient noise... (2 seconds)")
            r.adjust_for_ambient_noise(source, duration=2)
            
            print("🎤 SAY SOMETHING NOW! (You have 10 seconds)")
            print("   Try saying: 'Hello computer, this is a microphone test'")
            
            try:
                # Record audio
                audio = r.listen(source, timeout=10, phrase_time_limit=8)
                print("✅ Audio captured successfully!")
                
                # Try to transcribe
                print("🔄 Transcribing...")
                try:
                    text = r.recognize_google(audio)
                    print(f"✅ TRANSCRIPTION: '{text}'")
                    return True, text
                except:
                    print("⚠️ Could not transcribe (no internet or unclear speech)")
                    return True, "Audio captured but not transcribed"
                    
            except sr.WaitTimeoutError:
                print("❌ No speech detected - microphone may not be working")
                return False, "Timeout"
                
    except ImportError:
        print("❌ SpeechRecognition not installed")
        return False, "Missing library"
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False, str(e)

def test_speakers():
    """Test speaker output"""
    print("\n🔊 SPEAKER TEST")
    print("=" * 50)
    
    try:
        import asyncio
        import edge_tts
        import pygame
        import tempfile
        import os
        
        async def generate_test_audio():
            # Test different voices
            test_voices = [
                ("en-US-EmmaNeural", "Emma"),
                ("en-US-AndrewNeural", "Andrew"),
                ("en-US-AriaNeural", "Aria")
            ]
            
            pygame.mixer.init()
            
            for voice_id, voice_name in test_voices:
                print(f"🔊 Testing voice: {voice_name}")
                
                text = f"Hello! This is {voice_name}. Can you hear me clearly through your speakers or headphones?"
                
                # Generate TTS
                communicate = edge_tts.Communicate(text, voice_id)
                
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                    await communicate.save(tmp_file.name)
                    
                    try:
                        pygame.mixer.music.load(tmp_file.name)
                        pygame.mixer.music.play()
                        
                        # Wait for playback
                        while pygame.mixer.music.get_busy():
                            await asyncio.sleep(0.1)
                        
                        print(f"✅ {voice_name} test completed")
                        
                        # Ask user for feedback
                        response = input(f"   Did you hear {voice_name} clearly? (y/n): ").lower()
                        if response.startswith('y'):
                            print(f"✅ {voice_name} voice working correctly")
                        else:
                            print(f"⚠️ {voice_name} voice may have issues")
                            
                    finally:
                        try:
                            os.unlink(tmp_file.name)
                        except:
                            pass
                
                await asyncio.sleep(1)  # Pause between tests
            
            return True
        
        # Run the async test
        result = asyncio.run(generate_test_audio())
        return result
        
    except ImportError as e:
        print(f"❌ Missing required library: {e}")
        return False
    except Exception as e:
        print(f"❌ Speaker test failed: {e}")
        return False

def main():
    """Run complete audio calibration test"""
    print("🎧 VPA AUDIO CALIBRATION TEST")
    print("=" * 60)
    print("This will test your microphone and speakers/headphones")
    print("Make sure your audio devices are connected and working")
    print()
    
    input("Press Enter to start the test...")
    
    # Test microphone
    mic_success, mic_result = test_microphone()
    
    # Test speakers
    speaker_success = test_speakers()
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 50)
    print(f"🎤 Microphone: {'✅ WORKING' if mic_success else '❌ FAILED'}")
    if mic_success:
        print(f"   Result: {mic_result}")
    
    print(f"🔊 Speakers:   {'✅ WORKING' if speaker_success else '❌ FAILED'}")
    
    if mic_success and speaker_success:
        print("\n🎉 ALL AUDIO SYSTEMS WORKING!")
        print("Your VPA is ready for voice interaction.")
    else:
        print("\n⚠️ SOME ISSUES DETECTED")
        if not mic_success:
            print("• Check microphone connection and permissions")
        if not speaker_success:
            print("• Check speaker/headphone connection")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()
