#!/usr/bin/env python3
"""
Voice Testing Script - Play actual voices for verification
Tests the real pyttsx3 audio system with available system voices
"""

import pyttsx3
import time
import sys
from typing import List, Dict, Any, Optional

class VoiceTester:
    """Test real voices through pyttsx3"""
    
    def __init__(self):
        self.engine = None
        self.available_voices = []
        
    def initialize_engine(self) -> bool:
        """Initialize pyttsx3 engine"""
        try:
            self.engine = pyttsx3.init()
            print("✅ pyttsx3 engine initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize pyttsx3: {e}")
            return False
    
    def discover_voices(self) -> List[Dict[str, Any]]:
        """Discover available system voices"""
        if not self.engine:
            return []
        
        try:
            voices_prop = self.engine.getProperty('voices')
            if not voices_prop:
                print("❌ No voices found")
                return []
                
            # Cast to list for type safety
            voices = list(voices_prop) if voices_prop else []
            self.available_voices = []
            
            print(f"\n🔍 Found {len(voices)} system voices:")
            for i, voice in enumerate(voices):
                voice_info = {
                    'index': i,
                    'id': voice.id,
                    'name': voice.name,
                    'languages': getattr(voice, 'languages', []),
                    'gender': getattr(voice, 'gender', 'Unknown'),
                    'age': getattr(voice, 'age', 'Unknown')
                }
                self.available_voices.append(voice_info)
                
                print(f"  [{i}] {voice.name}")
                print(f"      ID: {voice.id}")
                print(f"      Languages: {voice_info['languages']}")
                print(f"      Gender: {voice_info['gender']}")
                print()
            
            return self.available_voices
            
        except Exception as e:
            print(f"❌ Error discovering voices: {e}")
            return []
    
    def test_voice(self, voice_index: int, test_text: Optional[str] = None) -> bool:
        """Test a specific voice by index"""
        if not self.engine or voice_index >= len(self.available_voices):
            return False
        
        voice_info = self.available_voices[voice_index]
        test_text = test_text or f"Hello! This is {voice_info['name']}, testing voice number {voice_index + 1}."
        
        try:
            print(f"\n🔊 Testing voice: {voice_info['name']}")
            print(f"   Text: \"{test_text}\"")
            
            # Set the voice
            self.engine.setProperty('voice', voice_info['id'])
            
            # Set rate and volume
            self.engine.setProperty('rate', 200)  # Words per minute
            self.engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
            
            # Speak the text
            self.engine.say(test_text)
            self.engine.runAndWait()
            
            print("✅ Voice test completed")
            return True
            
        except Exception as e:
            print(f"❌ Error testing voice {voice_info['name']}: {e}")
            return False
    
    def test_all_voices(self, pause_between: float = 2.0):
        """Test all available voices"""
        print(f"\n🎵 Testing all {len(self.available_voices)} voices...")
        print(f"   Pause between voices: {pause_between} seconds")
        print("   Press Ctrl+C to stop at any time\n")
        
        for i, voice_info in enumerate(self.available_voices):
            try:
                print(f"[{i+1}/{len(self.available_voices)}] ", end="")
                self.test_voice(i)
                
                if i < len(self.available_voices) - 1:  # Don't pause after last voice
                    print(f"⏸️  Pausing {pause_between} seconds...")
                    time.sleep(pause_between)
                    
            except KeyboardInterrupt:
                print("\n⏹️  Voice testing stopped by user")
                break
            except Exception as e:
                print(f"❌ Error during voice {i}: {e}")
                continue
    
    def interactive_test(self):
        """Interactive voice testing mode"""
        if not self.available_voices:
            print("❌ No voices available for testing")
            return
        
        print("\n🎛️  Interactive Voice Testing Mode")
        print("Commands:")
        print("  test <number>  - Test voice by number (1-based)")
        print("  test all       - Test all voices")
        print("  list           - List all voices")
        print("  quit           - Exit")
        print()
        
        while True:
            try:
                command = input("Voice Test> ").strip().lower()
                
                if command == "quit" or command == "exit":
                    break
                elif command == "list":
                    for i, voice in enumerate(self.available_voices):
                        print(f"  [{i+1}] {voice['name']}")
                elif command == "test all":
                    self.test_all_voices()
                elif command.startswith("test "):
                    try:
                        voice_num = int(command.split()[1])
                        if 1 <= voice_num <= len(self.available_voices):
                            self.test_voice(voice_num - 1)
                        else:
                            print(f"❌ Voice number must be between 1 and {len(self.available_voices)}")
                    except (ValueError, IndexError):
                        print("❌ Invalid command. Use 'test <number>' (e.g., 'test 1')")
                else:
                    print("❌ Unknown command. Type 'quit' to exit.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def shutdown(self):
        """Clean shutdown"""
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass


def main():
    """Main voice testing function"""
    print("=" * 80)
    print("🎵 VPA VOICE TESTING UTILITY")
    print("Tests actual voices through pyttsx3 for audio verification")
    print("=" * 80)
    
    tester = VoiceTester()
    
    try:
        # Initialize engine
        if not tester.initialize_engine():
            print("❌ Cannot proceed without audio engine")
            return 1
        
        # Discover voices
        voices = tester.discover_voices()
        if not voices:
            print("❌ No voices found on system")
            return 1
        
        # Ask user what they want to do
        print("\nWhat would you like to do?")
        print("1. Test all voices automatically")
        print("2. Interactive testing mode")
        print("3. Test specific voice")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            tester.test_all_voices()
        elif choice == "2":
            tester.interactive_test()
        elif choice == "3":
            try:
                voice_num = int(input(f"Enter voice number (1-{len(voices)}): "))
                if 1 <= voice_num <= len(voices):
                    tester.test_voice(voice_num - 1)
                else:
                    print(f"❌ Voice number must be between 1 and {len(voices)}")
            except ValueError:
                print("❌ Please enter a valid number")
        elif choice == "4":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 Voice testing interrupted by user")
        return 0
    except Exception as e:
        print(f"❌ Critical error: {e}")
        return 1
    finally:
        tester.shutdown()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
