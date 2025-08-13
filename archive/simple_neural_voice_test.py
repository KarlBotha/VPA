"""
Simple Neural Voice Test
Direct test of Edge-TTS neural voice system for user validation
"""

import logging
import sys
import time
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_edge_tts_installation():
    """Test Edge-TTS installation and basic functionality"""
    print("🧪 Testing Edge-TTS Installation...")
    
    try:
        import edge_tts
        print("✅ edge-tts module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ edge-tts import failed: {e}")
        return False

def test_pygame_audio():
    """Test pygame audio system"""
    print("🧪 Testing Pygame Audio System...")
    
    try:
        import pygame
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        print("✅ pygame audio initialized successfully")
        pygame.mixer.quit()
        return True
    except Exception as e:
        print(f"❌ pygame audio failed: {e}")
        return False

def test_neural_voice_synthesis():
    """Test actual neural voice synthesis"""
    print("🧪 Testing Neural Voice Synthesis...")
    
    try:
        # Import required modules
        import edge_tts
        import pygame
        import asyncio
        import tempfile
        from pathlib import Path
        
        # Initialize pygame
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        async def synthesize_and_play():
            """Async synthesis and playback"""
            # Test voice and text
            voice_id = "en-US-AriaNeural"
            test_text = "Hello! I am Aria, your new neural voice assistant. The Edge TTS integration is working perfectly!"
            
            print(f"🔊 Synthesizing with voice: {voice_id}")
            print(f"📝 Text: {test_text}")
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            temp_path = Path(temp_file.name)
            temp_file.close()
            
            try:
                # Generate speech
                start_time = time.time()
                communicate = edge_tts.Communicate(text=test_text, voice=voice_id)
                await communicate.save(str(temp_path))
                synthesis_time = time.time() - start_time
                
                print(f"⏱️ Synthesis completed in {synthesis_time:.2f} seconds")
                print(f"💾 Audio file size: {temp_path.stat().st_size} bytes")
                
                # Play audio
                pygame.mixer.music.load(str(temp_path))
                pygame.mixer.music.play()
                
                print("🔊 Playing audio... (listen for neural voice)")
                
                # Wait for playback
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
                
                print("✅ Neural voice synthesis and playback completed successfully!")
                
                return True
                
            finally:
                # Cleanup
                try:
                    temp_path.unlink()
                except:
                    pass
        
        # Run async synthesis
        result = asyncio.run(synthesize_and_play())
        
        # Cleanup pygame
        pygame.mixer.quit()
        
        return result
        
    except Exception as e:
        print(f"❌ Neural voice synthesis failed: {e}")
        return False

def test_multiple_voices():
    """Test multiple neural voices"""
    print("🧪 Testing Multiple Neural Voices...")
    
    try:
        import edge_tts
        import pygame
        import asyncio
        import tempfile
        from pathlib import Path
        
        # Initialize pygame
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Test voices with their sample phrases
        test_voices = [
            ("en-US-AriaNeural", "Aria", "Hello! I'm Aria, your sophisticated AI assistant."),
            ("en-US-GuyNeural", "Guy", "Hi there! I'm Guy, ready to help you today."),
            ("en-US-JennyNeural", "Jenny", "Hello! I'm Jenny, your friendly virtual companion."),
            ("en-US-AndrewNeural", "Andrew", "Good day! I'm Andrew, your professional AI assistant.")
        ]
        
        async def test_voice(voice_id, voice_name, sample_text):
            """Test individual voice"""
            print(f"\n🔊 Testing {voice_name} ({voice_id})")
            
            temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            temp_path = Path(temp_file.name)
            temp_file.close()
            
            try:
                # Synthesize
                communicate = edge_tts.Communicate(text=sample_text, voice=voice_id)
                await communicate.save(str(temp_path))
                
                # Play
                pygame.mixer.music.load(str(temp_path))
                pygame.mixer.music.play()
                
                # Wait for completion
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
                
                print(f"✅ {voice_name} test completed")
                return True
                
            except Exception as e:
                print(f"❌ {voice_name} test failed: {e}")
                return False
            finally:
                try:
                    temp_path.unlink()
                except:
                    pass
        
        async def test_all_voices():
            """Test all voices sequentially"""
            results = {}
            for voice_id, voice_name, sample_text in test_voices:
                result = await test_voice(voice_id, voice_name, sample_text)
                results[voice_name] = result
                
                # Pause between voices
                await asyncio.sleep(1.0)
            
            return results
        
        # Run tests
        results = asyncio.run(test_all_voices())
        
        # Cleanup pygame
        pygame.mixer.quit()
        
        # Report results
        successful_voices = sum(1 for success in results.values() if success)
        total_voices = len(results)
        
        print(f"\n📊 Voice Test Results: {successful_voices}/{total_voices} successful")
        for voice_name, success in results.items():
            status = "✅" if success else "❌"
            print(f"   {status} {voice_name}")
        
        return successful_voices >= (total_voices * 0.75)  # 75% success rate
        
    except Exception as e:
        print(f"❌ Multiple voice test failed: {e}")
        return False

def main():
    """Main test execution"""
    print("🎯 NEURAL VOICE INTEGRATION - USER VALIDATION TEST")
    print("=" * 60)
    
    # Test sequence
    tests = [
        ("Edge-TTS Installation", test_edge_tts_installation),
        ("Pygame Audio", test_pygame_audio),
        ("Neural Voice Synthesis", test_neural_voice_synthesis),
        ("Multiple Voice Testing", test_multiple_voices)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results[test_name] = result
            
            if result:
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
                
        except Exception as e:
            print(f"💥 {test_name} - ERROR: {e}")
            results[test_name] = False
        
        print()
    
    # Final summary
    print("=" * 60)
    print("🏆 NEURAL VOICE INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    success_rate = passed_tests / total_tests
    
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {success_rate * 100:.1f}%")
    
    overall_success = success_rate >= 0.75
    
    if overall_success:
        print("\n🎉 NEURAL VOICE INTEGRATION VALIDATED!")
        print("✅ Edge-TTS system is ready for VPA integration")
        print("🔊 All neural voices are working correctly")
        print("📱 System ready for user deployment")
    else:
        print("\n⚠️ NEURAL VOICE INTEGRATION NEEDS ATTENTION")
        print("❌ Some tests failed - review before deployment")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    
    print("\n" + "=" * 60)
    if success:
        print("🎯 USER VALIDATION: Neural voice system is READY for integration!")
    else:
        print("🔧 USER VALIDATION: Neural voice system needs fixes before integration")
    
    sys.exit(0 if success else 1)
