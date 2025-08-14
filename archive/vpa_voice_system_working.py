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
    
    def _initialize_sapi(self):
        """Initialize direct Windows SAPI connection"""
        try:
            self.sapi_voice = win32com.client.Dispatch("SAPI.SpVoice")
            self.logger.info("Direct Windows SAPI initialized successfully")
        except Exception as e:
            self.logger.error(f"SAPI initialization failed: {e}")
            raise
    
    def _detect_system_voices(self):
        """Detect available Windows SAPI voices"""
        try:
            if not self.sapi_voice:
                return
            
            voices = self.sapi_voice.GetVoices()
            self.system_voices = []
            
            for i in range(voices.Count):
                voice = voices.Item(i)
                voice_info = {
                    'index': i,
                    'name': voice.GetDescription(),
                    'id': voice.Id,
                    'object': voice
                }
                self.system_voices.append(voice_info)
                self.logger.info(f"Detected voice {i}: {voice_info['name']}")
            
            self.logger.info(f"Found {len(self.system_voices)} system voices")
            
        except Exception as e:
            self.logger.error(f"Voice detection failed: {e}")
    
    def _create_voice_catalog(self):
        """Create 13-voice catalog mapping to system voices"""
        
        # Define VPA voice catalog with smart mapping
        voice_catalog = [
            # Primary voices (map to actual system voices)
            ("voice_01", "David", "Male", "American", "david"),
            ("voice_02", "Hazel", "Female", "British", "hazel"),
            ("voice_03", "Zira", "Female", "American", "zira"),
            
            # Extended catalog (smart fallbacks)
            ("voice_04", "Mark", "Male", "American", "david"),  # Fallback to David
            ("voice_05", "Helena", "Female", "American", "zira"),  # Fallback to Zira
            ("voice_06", "James", "Male", "British", "david"),  # Fallback to David
            ("voice_07", "Catherine", "Female", "British", "hazel"),  # Fallback to Hazel
            ("voice_08", "Richard", "Male", "American", "david"),  # Fallback to David
            ("voice_09", "Eva", "Female", "American", "zira"),  # Fallback to Zira
            ("voice_10", "Sean", "Male", "American", "david"),  # Fallback to David
            ("voice_11", "Sabina", "Female", "British", "hazel"),  # Fallback to Hazel
            ("voice_12", "Alex", "Male", "System", "david"),  # Fallback to David
            ("voice_13", "System", "Neutral", "System", "david")  # Final fallback
        ]
        
        for voice_id, name, gender, accent, search_key in voice_catalog:
            # Find matching system voice
            system_voice = self._find_system_voice(search_key)
            
            if system_voice:
                self.voices[voice_id] = VoiceInfo(
                    voice_id=voice_id,
                    name=name,
                    gender=gender,
                    accent=accent,
                    system_id=system_voice['id'],
                    system_index=system_voice['index'],
                    available=True
                )
            else:
                # Create unavailable voice entry
                self.voices[voice_id] = VoiceInfo(
                    voice_id=voice_id,
                    name=name,
                    gender=gender,
                    accent=accent,
                    system_id="",
                    system_index=-1,
                    available=False
                )
        
        available_count = sum(1 for v in self.voices.values() if v.available)
        self.logger.info(f"VPA voice catalog created: {available_count}/13 voices available")
    
    def _find_system_voice(self, search_key: str) -> Optional[Dict[str, Any]]:
        """Find system voice by search key"""
        search_key = search_key.lower()
        
        # Try exact name match first
        for voice in self.system_voices:
            if search_key in voice['name'].lower():
                return voice
        
        # Fallback to first available voice
        if self.system_voices:
            return self.system_voices[0]
        
        return None
    
    def _set_default_voice(self):
        """Set default voice (preferably David)"""
        # Try to set David as default
        if "voice_01" in self.voices and self.voices["voice_01"].available:
            self.current_voice = self.voices["voice_01"]
        else:
            # Fallback to first available voice
            available_voices = [v for v in self.voices.values() if v.available]
            if available_voices:
                self.current_voice = available_voices[0]
        
        if self.current_voice:
            self.logger.info(f"Default voice set: {self.current_voice.name}")
        else:
            self.logger.warning("No default voice available")
    
    def _load_settings(self):
        """Load voice settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                
                # Load current voice
                current_voice_id = settings.get('current_voice')
                if current_voice_id and current_voice_id in self.voices:
                    self.current_voice = self.voices[current_voice_id]
                
                # Load voice-specific settings
                voice_settings = settings.get('voice_settings', {})
                for voice_id, voice_config in voice_settings.items():
                    if voice_id in self.voices:
                        voice = self.voices[voice_id]
                        voice.rate = voice_config.get('rate', voice.rate)
                        voice.volume = voice_config.get('volume', voice.volume)
                
                self.logger.info("Voice settings loaded successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to load voice settings: {e}")
    
    def _save_settings(self):
        """Save current voice settings"""
        try:
            settings = {
                'current_voice': self.current_voice.voice_id if self.current_voice else None,
                'voice_settings': {}
            }
            
            # Save voice-specific settings
            for voice_id, voice in self.voices.items():
                if voice.available:
                    settings['voice_settings'][voice_id] = {
                        'rate': voice.rate,
                        'volume': voice.volume
                    }
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            self.logger.info("Voice settings saved successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to save voice settings: {e}")
    
    def get_available_voices(self) -> List[VoiceInfo]:
        """Get list of available voices"""
        return [voice for voice in self.voices.values() if voice.available]
    
    def get_voice_by_id(self, voice_id: str) -> Optional[VoiceInfo]:
        """Get voice by ID"""
        return self.voices.get(voice_id)
    
    def get_voice_by_name(self, name: str) -> Optional[VoiceInfo]:
        """Get voice by name (case-insensitive)"""
        name_lower = name.lower()
        for voice in self.voices.values():
            if voice.name.lower() == name_lower:
                return voice
        return None
    
    def get_voices_by_gender(self, gender: str) -> List[VoiceInfo]:
        """Get voices by gender"""
        gender_lower = gender.lower()
        return [voice for voice in self.voices.values() 
                if voice.available and voice.gender.lower() == gender_lower]
    
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
            # Find system voice object
            system_voice = None
            for sys_voice in self.system_voices:
                if sys_voice['index'] == voice.system_index:
                    system_voice = sys_voice['object']
                    break
            
            if not system_voice:
                self.logger.error(f"System voice not found for {voice.name}")
                return False
            
            # Set voice using direct SAPI
            self.sapi_voice.Voice = system_voice
            self.sapi_voice.Rate = voice.rate
            self.sapi_voice.Volume = voice.volume
            
            # Update current voice
            self.current_voice = voice
            self._save_settings()
            
            self.logger.info(f"Voice changed to: {voice.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set voice {voice.name}: {e}")
            return False
    
    def set_voice_by_name(self, name: str) -> bool:
        """Set active voice by name"""
        voice = self.get_voice_by_name(name)
        if voice:
            return self.set_voice(voice.voice_id)
        
        self.logger.error(f"Voice '{name}' not found")
        return False
    
    def speak(self, text: str) -> bool:
        """Speak text using current voice"""
        if not text or not text.strip():
            return False
        
        if not self.current_voice or not self.current_voice.available:
            self.logger.error("No voice available for speech")
            return False
        
        try:
            # Ensure current voice settings are applied
            if self.sapi_voice:
                self.sapi_voice.Rate = self.current_voice.rate
                self.sapi_voice.Volume = self.current_voice.volume
                
                # Speak using SAPI
                self.sapi_voice.Speak(text.strip())
                return True
            else:
                self.logger.error("SAPI voice not initialized")
                return False
                
        except Exception as e:
            self.logger.error(f"Speech failed: {e}")
            return False
    
    def test_voice(self, voice_id: Optional[str] = None, test_text: Optional[str] = None) -> bool:
        """Test a specific voice or current voice"""
        # Determine which voice to test
        if voice_id:
            test_voice = self.get_voice_by_id(voice_id)
            if not test_voice:
                self.logger.error(f"Voice {voice_id} not found for testing")
                return False
        else:
            test_voice = self.current_voice
        
        if not test_voice or not test_voice.available:
            self.logger.error("No voice available for testing")
            return False
        
        # Save current voice
        original_voice = self.current_voice
        
        try:
            # Set test voice
            if voice_id and test_voice != self.current_voice:
                self.set_voice(voice_id)
            
            # Generate test text
            if not test_text:
                test_text = f"Hello, this is {test_voice.name}, testing voice {test_voice.voice_id}"
            
            # Speak test text
            success = self.speak(test_text)
            
            # Restore original voice if we changed it
            if voice_id and original_voice and original_voice != test_voice:
                self.set_voice(original_voice.voice_id)
            
            return success
            
        except Exception as e:
            self.logger.error(f"Voice test failed: {e}")
            
            # Restore original voice on error
            if original_voice:
                self.set_voice(original_voice.voice_id)
            
            return False
    
    def adjust_rate(self, rate: int) -> bool:
        """Adjust speech rate for current voice (-10 to 10)"""
        if not self.current_voice:
            return False
        
        # Clamp rate to SAPI range
        rate = max(-10, min(10, rate))
        
        try:
            self.current_voice.rate = rate
            if self.sapi_voice:
                self.sapi_voice.Rate = rate
            
            self._save_settings()
            self.logger.info(f"Rate adjusted to {rate} for {self.current_voice.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to adjust rate: {e}")
            return False
    
    def adjust_volume(self, volume: int) -> bool:
        """Adjust volume for current voice (0-100)"""
        if not self.current_voice:
            return False
        
        # Clamp volume to SAPI range
        volume = max(0, min(100, volume))
        
        try:
            self.current_voice.volume = volume
            if self.sapi_voice:
                self.sapi_voice.Volume = volume
            
            self._save_settings()
            self.logger.info(f"Volume adjusted to {volume} for {self.current_voice.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to adjust volume: {e}")
            return False
    
    def get_voice_status(self) -> Dict[str, Any]:
        """Get comprehensive voice system status"""
        return {
            "current_voice": {
                "id": self.current_voice.voice_id if self.current_voice else None,
                "name": self.current_voice.name if self.current_voice else None,
                "gender": self.current_voice.gender if self.current_voice else None,
                "accent": self.current_voice.accent if self.current_voice else None,
                "rate": self.current_voice.rate if self.current_voice else None,
                "volume": self.current_voice.volume if self.current_voice else None
            },
            "available_voices": len([v for v in self.voices.values() if v.available]),
            "total_voices": len(self.voices),
            "system_voices": len(self.system_voices),
            "sapi_initialized": self.sapi_voice is not None
        }
    
    def shutdown(self):
        """Clean shutdown of voice system"""
        try:
            self._save_settings()
            
            if self.sapi_voice:
                # Stop any ongoing speech
                try:
                    self.sapi_voice.Speak("", 2)  # 2 = SVSFPurgeBeforeSpeak
                except:
                    pass
            
            self.logger.info("VPA voice system shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Voice system shutdown error: {e}")


# Convenience functions for easy integration
def create_voice_system() -> VPAVoiceSystem:
    """Create and initialize VPA voice system"""
    return VPAVoiceSystem()

def test_voice_system():
    """Quick test of voice system functionality"""
    print("🎵 Testing VPA Voice System...")
    
    try:
        voice_system = create_voice_system()
        
        # Get status
        status = voice_system.get_voice_status()
        print(f"Voice System Status: {status}")
        
        # Test available voices
        available_voices = voice_system.get_available_voices()
        print(f"Available voices: {len(available_voices)}")
        
        for voice in available_voices[:3]:  # Test first 3 voices
            print(f"Testing {voice.name}...")
            voice_system.test_voice(voice.voice_id)
            time.sleep(1)
        
        print("✅ Voice system test complete")
        
    except Exception as e:
        print(f"❌ Voice system test failed: {e}")

if __name__ == "__main__":
    test_voice_system()
