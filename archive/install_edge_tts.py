"""
VPA Edge-TTS Installation & Test Script
SOLUTION: Install Microsoft Edge-TTS Neural Voices
"""

import subprocess
import sys
import platform
import time

def install_edge_tts_dependencies():
    """Install Edge-TTS and required dependencies"""
    
    print("🔧 INSTALLING EDGE-TTS NEURAL VOICE SYSTEM")
    print("=" * 60)
    
    dependencies = [
        ("edge-tts", "Microsoft Edge Text-to-Speech"),
        ("pygame", "Audio playback system"),
        ("asyncio", "Async support (built-in)"),
    ]
    
    for package, description in dependencies:
        if package == "asyncio":
            print(f"✅ {package} - {description} (built-in)")
            continue
            
        print(f"📦 Installing {package} - {description}")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True, check=True)
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    print(f"\n🎉 ALL DEPENDENCIES INSTALLED SUCCESSFULLY!")
    return True

def test_edge_tts_basic():
    """Test basic Edge-TTS functionality"""
    
    print(f"\n🧪 TESTING EDGE-TTS FUNCTIONALITY")
    print("=" * 60)
    
    try:
        import edge_tts
        import asyncio
        import tempfile
        import os
        
        async def test_synthesis():
            text = "Hello! This is a test of Microsoft Edge neural text-to-speech."
            voice = "en-US-AriaNeural"
            
            # Create temporary file
            temp_file = os.path.join(tempfile.gettempdir(), "edge_tts_test.mp3")
            
            print(f"🎤 Testing voice: {voice}")
            print(f"📝 Text: {text}")
            print(f"💾 Output file: {temp_file}")
            
            # Generate speech
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(temp_file)
            
            # Check if file was created
            if os.path.exists(temp_file):
                file_size = os.path.getsize(temp_file)
                print(f"✅ Audio file generated successfully ({file_size} bytes)")
                
                # Clean up
                try:
                    os.remove(temp_file)
                    print("🧹 Temporary file cleaned up")
                except:
                    pass
                
                return True
            else:
                print("❌ Audio file was not generated")
                return False
        
        # Run async test
        success = asyncio.run(test_synthesis())
        
        if success:
            print(f"\n🎉 EDGE-TTS TEST PASSED!")
            print("✅ Neural voice synthesis working correctly")
            return True
        else:
            print(f"\n❌ EDGE-TTS TEST FAILED!")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Edge-TTS may not be installed correctly")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def list_available_neural_voices():
    """List all available neural voices"""
    
    print(f"\n🎭 AVAILABLE NEURAL VOICES")
    print("=" * 60)
    
    try:
        import edge_tts
        import asyncio
        
        async def get_voices():
            voices = await edge_tts.list_voices()
            return voices
        
        # Get voice list
        voices = asyncio.run(get_voices())
        
        # Filter for English neural voices
        english_neural = [
            v for v in voices 
            if 'en-' in v['Locale'] and 'Neural' in v['VoiceTag']
        ]
        
        print(f"Found {len(english_neural)} English neural voices:")
        
        for voice in english_neural[:20]:  # Show first 20
            locale = voice.get('Locale', 'Unknown')
            gender = voice.get('Gender', 'Unknown')
            name = voice.get('FriendlyName', voice.get('Name', 'Unknown'))
            short_name = voice.get('ShortName', 'Unknown')
            
            print(f"  • {short_name}")
            print(f"    Name: {name}")
            print(f"    Gender: {gender}, Locale: {locale}")
            print()
        
        if len(english_neural) > 20:
            print(f"... and {len(english_neural) - 20} more voices")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to list voices: {e}")
        return False

def main():
    """Main installation and test workflow"""
    
    print("🚀 VPA EDGE-TTS NEURAL VOICE SETUP")
    print("=" * 80)
    print("SOLUTION: Upgrade from 3 basic voices to 12+ neural voices")
    print("PROVIDER: Microsoft Edge Text-to-Speech (Azure Cognitive Services)")
    print("=" * 80)
    
    # System info
    print(f"🖥️ System: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    print()
    
    # Step 1: Install dependencies
    if not install_edge_tts_dependencies():
        print("❌ Installation failed. Cannot continue.")
        return False
    
    # Step 2: Test basic functionality
    time.sleep(2)  # Give a moment for installation to settle
    if not test_edge_tts_basic():
        print("❌ Edge-TTS testing failed.")
        return False
    
    # Step 3: List available voices
    if not list_available_neural_voices():
        print("❌ Voice listing failed.")
        return False
    
    print(f"\n🎉 EDGE-TTS SETUP COMPLETE!")
    print("=" * 60)
    print("✅ Dependencies installed")
    print("✅ Neural voice synthesis tested")
    print("✅ Voice catalog accessible")
    print()
    print("🚀 NEXT STEPS:")
    print("1. Run: python edge_tts_voice_system.py")
    print("2. Test different neural voices")
    print("3. Integrate with VPA system")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n✅ Setup completed successfully!")
        
        # Offer to run the voice system
        response = input("\nWould you like to run the voice system now? (y/n): ").lower()
        if response == 'y':
            print("\n🎤 Starting Edge-TTS Voice System...")
            try:
                import edge_tts_voice_system
                edge_tts_voice_system.main()
            except Exception as e:
                print(f"❌ Failed to start voice system: {e}")
    else:
        print(f"\n❌ Setup failed. Please check the errors above.")
