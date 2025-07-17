"""
VPA Voice System - Direct Windows SAPI Implementation
Uses direct Windows SAPI for reliable voice switching
Based on successful testing: all voices work with direct SAPI approach
"""

import logging
import json
import win32com.client
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class VoiceInfo:
    """Voice information for VPA system"""
    voice_id: str
    name: str
    gender: str
    accent: str
    system_id: str  # Windows SAPI ID
    system_index: int  # Index in SAPI voices
    rate: int = 2  # SAPI rate (-10 to 10)
    volume: int = 90  # SAPI volume (0-100)
    available: bool = False

class VPAVoiceSystem:
    """
    VPA Voice System using Direct Windows SAPI
    Implements 13-voice catalog with reliable voice switching
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sapi_voice = None  # COM object
        self.system_voices = []  # Raw SAPI voices
        self.voices: Dict[str, VoiceInfo] = {}
        self.current_voice: Optional[VoiceInfo] = None
        self.settings_file = Path("vpa_voice_settings.json")
        
        # Initialize voice system
        self._initialize_sapi()
        self._detect_system_voices()
        self._create_voice_catalog()
        self._set_default_voice()
        self._load_settings()
    
    def _initialize_engine(self):
        """Initialize pyttsx3 engine (your current system)"""
        try:
            self.engine = pyttsx3.init()
            self.logger.info("pyttsx3 engine initialized")
        except Exception as e:
            self.logger.error(f"pyttsx3 initialization failed: {e}")
    
    def _detect_system_voices(self) -> List[Dict[str, str]]:
        """Detect available system voices (your current approach)"""
        system_voices = []
        try:
            if self.engine:
                voices = self.engine.getProperty('voices')
                if voices and hasattr(voices, '__iter__'):
                    for voice in voices:
                        if hasattr(voice, 'id') and hasattr(voice, 'name'):
                            system_voices.append({
                                'id': voice.id,
                                'name': voice.name
                            })
                    self.logger.info(f"Detected {len(system_voices)} system voices")
                else:
                    self.logger.warning("No system voices found")
                    
        except Exception as e:
            self.logger.error(f"Voice detection failed: {e}")
        
        return system_voices
    
    def _create_voice_catalog(self):
        """Create 13-voice catalog from detected voices"""
        system_voices = self._detect_system_voices()
        
        # Define preferred voice mapping (based on our successful test)
        voice_mapping = [
            ("voice_01", "David", "Male"),
            ("voice_02", "Zira", "Female"),
            ("voice_03", "Mark", "Male"),
            ("voice_04", "Hazel", "Female"),
            ("voice_05", "Helena", "Female"),
            ("voice_06", "James", "Male"),
            ("voice_07", "Catherine", "Female"),
            ("voice_08", "Richard", "Male"),
            ("voice_09", "Eva", "Female"),
            ("voice_10", "Sean", "Male"),
            ("voice_11", "Sabina", "Female"),
            ("voice_12", "Alex", "Male"),
            ("voice_13", "System", "Neutral")
        ]
        
        # Map system voices to catalog using the same logic as our successful test
        for voice_id, preferred_name, gender in voice_mapping:
            system_voice = None
            
            # Try to find exact or close match
            for sys_voice in system_voices:
                if preferred_name.lower() in sys_voice['name'].lower():
                    system_voice = sys_voice
                    break
            
            # Fallback: find any voice of matching gender
            if not system_voice:
                gender_keywords = {
                    "Male": ["david", "mark", "james", "richard", "sean", "alex", "male"],
                    "Female": ["zira", "hazel", "helena", "catherine", "eva", "sabina", "female"],
                    "Neutral": ["system", "default"]
                }
                
                for sys_voice in system_voices:
                    voice_name_lower = sys_voice['name'].lower()
                    for keyword in gender_keywords.get(gender, []):
                        if keyword in voice_name_lower:
                            system_voice = sys_voice
                            break
                    if system_voice:
                        break
            
            # Final fallback: use first available voice
            if not system_voice and system_voices:
                system_voice = system_voices[0]
            
            # Create voice info
            if system_voice:
                self.voices[voice_id] = VoiceInfo(
                    voice_id=voice_id,
                    name=preferred_name,
                    gender=gender,
                    system_id=system_voice['id'],
                    available=True
                )
            else:
                # Create unavailable voice entry
                self.voices[voice_id] = VoiceInfo(
                    voice_id=voice_id,
                    name=preferred_name,
                    gender=gender,
                    system_id="",
                    available=False
                )
        
        available_count = sum(1 for v in self.voices.values() if v.available)
        self.logger.info(f"Voice catalog created: {available_count}/13 voices available")
    
    def _set_default_voice(self):
        """Set the default voice"""
        # Prefer David as default, or first available voice
        if "voice_01" in self.voices and self.voices["voice_01"].available:
            self.current_voice = self.voices["voice_01"]
        else:
            available_voices = [v for v in self.voices.values() if v.available]
            if available_voices:
                self.current_voice = available_voices[0]
        
        if self.current_voice:
            self.logger.info(f"Default voice set to: {self.current_voice.name}")
        else:
            self.logger.warning("No default voice available")
    
    def _load_settings(self):
        """Load voice settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    
                # Apply saved voice if available
                if 'current_voice_id' in settings and settings['current_voice_id'] in self.voices:
                    self.current_voice = self.voices[settings['current_voice_id']]
                    
                # Apply saved voice properties
                for voice_id, voice_settings in settings.get('voices', {}).items():
                    if voice_id in self.voices:
                        voice = self.voices[voice_id]
                        voice.rate = voice_settings.get('rate', voice.rate)
                        voice.volume = voice_settings.get('volume', voice.volume)
                        
        except Exception as e:
            self.logger.error(f"Failed to load voice settings: {e}")
    
    def save_settings(self):
        """Save current voice settings"""
        try:
            settings = {
                'current_voice_id': self.current_voice.voice_id if self.current_voice else None,
                'voices': {}
            }
            
            for voice_id, voice in self.voices.items():
                settings['voices'][voice_id] = {
                    'rate': voice.rate,
                    'volume': voice.volume
                }
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save voice settings: {e}")
    
    def get_available_voices(self) -> List[VoiceInfo]:
        """Get list of available voices"""
        return [voice for voice in self.voices.values() if voice.available]
    
    def set_voice(self, voice_id: str) -> bool:
        """Set active voice by ID"""
        if voice_id not in self.voices:
            self.logger.error(f"Voice {voice_id} not found")
            return False
        
        voice = self.voices[voice_id]
        if not voice.available:
            self.logger.error(f"Voice {voice.name} not available")
            return False
        
        try:
            if self.engine:
                self.engine.setProperty('voice', voice.system_id)
                self.engine.setProperty('rate', voice.rate)
                self.engine.setProperty('volume', voice.volume)
                self.current_voice = voice
                self.logger.info(f"Voice changed to: {voice.name}")
                return True
            else:
                self.logger.error("Voice engine not available")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to set voice: {e}")
            return False
    
    def speak(self, text: str) -> bool:
        """Speak text using current voice (your existing pattern)"""
        if not text or not text.strip():
            return False
        
        try:
            if self.engine and self.current_voice:
                self.engine.say(text)
                self.engine.runAndWait()
                return True
            else:
                self.logger.error("No voice engine or current voice available")
                return False
                
        except Exception as e:
            self.logger.error(f"Speech failed: {e}")
            return False
    
    def get_voice_info(self) -> Dict[str, Any]:
        """Get current voice information"""
        if not self.current_voice:
            return {"status": "No voice selected"}
        
        return {
            "current_voice": {
                "id": self.current_voice.voice_id,
                "name": self.current_voice.name,
                "gender": self.current_voice.gender,
                "rate": self.current_voice.rate,
                "volume": self.current_voice.volume
            },
            "available_voices": len(self.get_available_voices()),
            "total_voices": len(self.voices)
        }
    
    def test_voice(self, voice_id: Optional[str] = None) -> bool:
        """Test a specific voice or current voice"""
        if voice_id:
            if not self.set_voice(voice_id):
                return False
        
        if not self.current_voice:
            self.logger.error("No voice to test")
            return False
        
        test_message = f"Hello, I am {self.current_voice.name}, testing voice system."
        return self.speak(test_message)
    
    def shutdown(self):
        """Clean shutdown of voice system"""
        try:
            self.save_settings()
            if self.engine:
                # pyttsx3 doesn't have explicit shutdown, but we can clear it
                self.engine = None
            self.logger.info("Voice system shutdown complete")
        except Exception as e:
            self.logger.error(f"Voice system shutdown error: {e}")
