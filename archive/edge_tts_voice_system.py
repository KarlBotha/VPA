"""
VPA Edge-TTS Enhanced Voice System
SOLUTION: Microsoft Edge-TTS Neural Voices Integration
REPLACES: Basic 3-voice pyttsx3 system with 12+ neural voices
"""

import asyncio
import logging
import tempfile
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import json
import time

# Edge-TTS for neural voices
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    print("⚠️ edge-tts not available. Install with: pip install edge-tts")

# Audio playback
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("⚠️ pygame not available. Install with: pip install pygame")

# Fallback to pyttsx3
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

@dataclass
class NeuralVoice:
    """Neural voice configuration for Edge-TTS"""
    voice_id: str
    name: str
    gender: str
    language: str
    description: str
    quality: str = "Neural"
    provider: str = "Edge-TTS"

class EdgeTTSVoiceSystem:
    """
    Enhanced Voice System using Microsoft Edge-TTS Neural Voices
    UPGRADE: From 3 basic voices to 12+ high-quality neural voices
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize audio system
        self.audio_initialized = False
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.init()
                self.audio_initialized = True
                self.logger.info("Audio system initialized")
            except Exception as e:
                self.logger.error(f"Audio initialization failed: {e}")
        
        # Neural voice catalog
        self.neural_voices = self._initialize_neural_voices()
        self.current_voice = None
        self.temp_dir = Path(tempfile.gettempdir()) / "vpa_tts"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Set default voice
        self._set_default_voice()
        
        self.logger.info(f"Edge-TTS Voice System initialized with {len(self.neural_voices)} neural voices")
    
    def _initialize_neural_voices(self) -> Dict[str, NeuralVoice]:
        """Initialize the complete neural voice catalog"""
        voices = {}
        
        if not EDGE_TTS_AVAILABLE:
            self.logger.warning("Edge-TTS not available - using fallback configuration")
            return voices
        
        # MALE NEURAL VOICES
        voices["Andrew"] = NeuralVoice(
            voice_id="en-US-AndrewNeural",
            name="Andrew",
            gender="Male",
            language="en-US",
            description="Confident male voice with professional tone"
        )
        
        voices["Christopher"] = NeuralVoice(
            voice_id="en-US-ChristopherNeural", 
            name="Christopher",
            gender="Male",
            language="en-US",
            description="Clear male voice with excellent articulation"
        )
        
        voices["Guy"] = NeuralVoice(
            voice_id="en-US-GuyNeural",
            name="Guy", 
            gender="Male",
            language="en-US",
            description="Natural male voice with clear pronunciation - EXCELLENT for VPA"
        )
        
        voices["Roger"] = NeuralVoice(
            voice_id="en-US-RogerNeural",
            name="Roger",
            gender="Male", 
            language="en-US",
            description="Deep male voice with authoritative presence"
        )
        
        voices["Eric"] = NeuralVoice(
            voice_id="en-US-EricNeural",
            name="Eric",
            gender="Male",
            language="en-US", 
            description="Friendly male voice with conversational tone"
        )
        
        voices["Steffan"] = NeuralVoice(
            voice_id="en-US-SteffanNeural",
            name="Steffan",
            gender="Male",
            language="en-US",
            description="Mature male voice with professional delivery"
        )
        
        # FEMALE NEURAL VOICES
        voices["Emma"] = NeuralVoice(
            voice_id="en-US-EmmaNeural",
            name="Emma",
            gender="Female",
            language="en-US",
            description="Confident female voice with professional tone"
        )
        
        voices["Ava"] = NeuralVoice(
            voice_id="en-US-AvaNeural", 
            name="Ava",
            gender="Female",
            language="en-US",
            description="Friendly female voice with warm delivery"
        )
        
        voices["Aria"] = NeuralVoice(
            voice_id="en-US-AriaNeural",
            name="Aria",
            gender="Female", 
            language="en-US",
            description="Natural female voice with clear pronunciation - EXCELLENT for VPA"
        )
        
        voices["Jenny"] = NeuralVoice(
            voice_id="en-US-JennyNeural",
            name="Jenny",
            gender="Female",
            language="en-US",
            description="Warm female voice, perfect for conversation and assistance"
        )
        
        voices["Libby"] = NeuralVoice(
            voice_id="en-GB-LibbyNeural",
            name="Libby", 
            gender="Female",
            language="en-GB",
            description="British female voice with clear pronunciation and elegance"
        )
        
        voices["Michelle"] = NeuralVoice(
            voice_id="en-US-MichelleNeural",
            name="Michelle",
            gender="Female",
            language="en-US",
            description="Professional female voice with executive presence"
        )
        
        return voices
    
    def _set_default_voice(self):
        """Set default voice (Aria - excellent for VPA)"""
        if "Aria" in self.neural_voices:
            self.current_voice = self.neural_voices["Aria"]
            self.logger.info(f"Default voice set to: {self.current_voice.name}")
        elif self.neural_voices:
            # Fallback to first available voice
            self.current_voice = list(self.neural_voices.values())[0]
            self.logger.info(f"Fallback voice set to: {self.current_voice.name}")
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available neural voices"""
        voices = []
        for voice_name, voice in self.neural_voices.items():
            voices.append({
                "name": voice.name,
                "gender": voice.gender,
                "language": voice.language,
                "description": voice.description,
                "quality": voice.quality,
                "provider": voice.provider,
                "voice_id": voice.voice_id
            })
        return voices
    
    def set_voice(self, voice_name: str) -> bool:
        """Set active voice by name"""
        if voice_name in self.neural_voices:
            self.current_voice = self.neural_voices[voice_name]
            self.logger.info(f"Voice changed to: {self.current_voice.name}")
            return True
        else:
            self.logger.error(f"Voice '{voice_name}' not found")
            return False
    
    async def speak_async(self, text: str) -> bool:
        """Speak text using neural voice (async)"""
        if not self.current_voice:
            self.logger.error("No voice selected")
            return False
        
        if not EDGE_TTS_AVAILABLE:
            self.logger.error("Edge-TTS not available")
            return False
        
        try:
            # Generate unique filename
            audio_file = self.temp_dir / f"tts_{int(time.time() * 1000)}.mp3"
            
            # Generate speech using Edge-TTS
            communicate = edge_tts.Communicate(text, self.current_voice.voice_id)
            await communicate.save(str(audio_file))
            
            # Play audio
            if self.audio_initialized:
                pygame.mixer.music.load(str(audio_file))
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
                
                # Clean up temporary file
                try:
                    audio_file.unlink()
                except:
                    pass
                
                return True
            else:
                self.logger.error("Audio system not initialized")
                return False
                
        except Exception as e:
            self.logger.error(f"Speech synthesis failed: {e}")
            return False
    
    def speak(self, text: str) -> bool:
        """Speak text using neural voice (sync wrapper)"""
        try:
            # Run async function in sync context
            return asyncio.run(self.speak_async(text))
        except Exception as e:
            self.logger.error(f"Sync speech failed: {e}")
            return False
    
    def test_voice(self, voice_name: str = None) -> bool:
        """Test specific voice or current voice"""
        if voice_name:
            if not self.set_voice(voice_name):
                return False
        
        if not self.current_voice:
            print("No voice selected for testing")
            return False
        
        test_text = f"Hello! This is {self.current_voice.name}, a high-quality neural voice from Microsoft Edge TTS. I'm ready to be your virtual personal assistant."
        
        print(f"Testing voice: {self.current_voice.name}")
        print(f"Description: {self.current_voice.description}")
        print(f"Playing: '{test_text}'")
        
        return self.speak(test_text)
    
    def list_voices(self):
        """Display all available neural voices"""
        print(f"\n🎤 EDGE-TTS NEURAL VOICES ({len(self.neural_voices)} available)")
        print("=" * 80)
        
        # Group by gender
        male_voices = [v for v in self.neural_voices.values() if v.gender == "Male"]
        female_voices = [v for v in self.neural_voices.values() if v.gender == "Female"]
        
        print(f"\n👨 MALE VOICES ({len(male_voices)}):")
        for voice in male_voices:
            current = " ⭐ CURRENT" if self.current_voice and voice.name == self.current_voice.name else ""
            print(f"  • {voice.name} ({voice.language}){current}")
            print(f"    {voice.description}")
        
        print(f"\n👩 FEMALE VOICES ({len(female_voices)}):")
        for voice in female_voices:
            current = " ⭐ CURRENT" if self.current_voice and voice.name == self.current_voice.name else ""
            print(f"  • {voice.name} ({voice.language}){current}")
            print(f"    {voice.description}")
        
        print(f"\n💡 RECOMMENDED FOR VPA:")
        print("  • Aria (Female) - Natural voice with clear pronunciation")
        print("  • Guy (Male) - Natural voice with clear pronunciation")
        print("  • Jenny (Female) - Warm voice, perfect for conversation")
    
    def get_voice_info(self) -> Dict[str, Any]:
        """Get current voice information"""
        if not self.current_voice:
            return {"error": "No voice selected"}
        
        return {
            "name": self.current_voice.name,
            "gender": self.current_voice.gender,
            "language": self.current_voice.language,
            "description": self.current_voice.description,
            "quality": self.current_voice.quality,
            "provider": self.current_voice.provider,
            "voice_id": self.current_voice.voice_id,
            "edge_tts_available": EDGE_TTS_AVAILABLE,
            "audio_available": self.audio_initialized
        }

def main():
    """Demo the Edge-TTS voice system"""
    
    print("🚀 VPA EDGE-TTS NEURAL VOICE SYSTEM")
    print("=" * 80)
    print("UPGRADE: From 3 basic voices to 12+ neural voices")
    print("SOLUTION: Microsoft Edge-TTS Neural Text-to-Speech")
    print("=" * 80)
    
    # Check dependencies
    if not EDGE_TTS_AVAILABLE:
        print("❌ edge-tts not installed. Install with: pip install edge-tts")
        return
    
    if not PYGAME_AVAILABLE:
        print("❌ pygame not installed. Install with: pip install pygame")
        return
    
    # Initialize voice system
    voice_system = EdgeTTSVoiceSystem()
    
    # Display available voices
    voice_system.list_voices()
    
    # Interactive testing
    while True:
        print(f"\n🎯 VOICE TESTING MENU")
        print("1. Test current voice")
        print("2. Change voice")
        print("3. Custom speech test")
        print("4. List all voices")
        print("5. Voice info")
        print("6. Exit")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            voice_system.test_voice()
            
        elif choice == "2":
            voice_system.list_voices()
            voice_name = input("\nEnter voice name: ").strip()
            if voice_system.set_voice(voice_name):
                print(f"✅ Voice changed to {voice_name}")
                voice_system.test_voice()
            else:
                print(f"❌ Voice '{voice_name}' not found")
                
        elif choice == "3":
            custom_text = input("Enter text to speak: ").strip()
            if custom_text:
                print(f"Speaking with {voice_system.current_voice.name}...")
                voice_system.speak(custom_text)
                
        elif choice == "4":
            voice_system.list_voices()
            
        elif choice == "5":
            info = voice_system.get_voice_info()
            print(f"\n📋 Current Voice Info:")
            for key, value in info.items():
                print(f"  {key}: {value}")
                
        elif choice == "6":
            print("👋 Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
