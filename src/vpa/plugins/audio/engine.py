"""
Audio Engine for VPA - pyttsx3 Integration & Voice Management
Provides comprehensive voice management with 13-voice catalog system.
"""

import logging
import json
import pyttsx3
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from vpa.core.events import EventBus


@dataclass
class VoiceInfo:
    """Voice information structure"""
    voice_id: str
    name: str
    gender: str
    system_id: str  # pyttsx3 voice ID
    rate: int = 200
    volume: float = 0.9
    available: bool = False
    language: str = "en-US"
    purpose: str = "General"


class AudioEngine:
    """Main audio engine for VPA voice management"""
    
    def __init__(self, event_bus: EventBus, config: Optional[Dict[str, Any]] = None):
        """Initialize the audio engine"""
        self.logger = logging.getLogger(__name__)
        self.event_bus = event_bus
        self.config = config or {}
        
        # TTS Engine
        self.engine: Optional[pyttsx3.Engine] = None
        self.engine_lock = threading.Lock()
        
        # Voice Management
        self.voices: Dict[str, VoiceInfo] = {}
        self.current_voice: Optional[VoiceInfo] = None
        self.settings_file = Path("config/voice_settings.json")
        
        # State
        self.is_speaking = False
        self.speech_queue: List[str] = []
        
        # Initialize
        self._initialize_engine()
        self._create_voice_catalog()
        self._set_default_voice()
        self._load_user_settings()
        self._register_event_handlers()
    
    def _initialize_engine(self) -> None:
        """Initialize pyttsx3 TTS engine"""
        try:
            self.engine = pyttsx3.init()
            
            # Set up engine callbacks
            self.engine.connect('started-utterance', self._on_speak_start)
            self.engine.connect('finished-utterance', self._on_speak_end)
            self.engine.connect('error', self._on_speak_error)
            
            self.logger.info("pyttsx3 audio engine initialized successfully")
            self.event_bus.emit("audio.engine.initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize audio engine: {e}")
            self.event_bus.emit("audio.engine.error", {"error": str(e)})
    
    def _detect_system_voices(self) -> List[Dict[str, Any]]:
        """Detect available system voices"""
        system_voices = []
        
        if not self.engine:
            return system_voices
        
        try:
            voices = self.engine.getProperty('voices')
            if voices:
                for voice in voices:
                    # Determine gender based on voice name patterns
                    gender = self._determine_voice_gender(voice.name)
                    
                    voice_info = {
                        'id': voice.id,
                        'name': voice.name,
                        'gender': gender,
                        'languages': getattr(voice, 'languages', ['en-US'])
                    }
                    system_voices.append(voice_info)
                    
                self.logger.info(f"Detected {len(system_voices)} system voices")
        
        except Exception as e:
            self.logger.error(f"Voice detection failed: {e}")
        
        return system_voices
    
    def _determine_voice_gender(self, voice_name: str) -> str:
        """Determine voice gender from name patterns"""
        name_lower = voice_name.lower()
        
        # Female indicators
        female_patterns = ['zira', 'helena', 'hazel', 'catherine', 'eva', 'sabina', 'female']
        if any(pattern in name_lower for pattern in female_patterns):
            return 'Female'
        
        # Male indicators  
        male_patterns = ['david', 'mark', 'james', 'richard', 'sean', 'alex', 'male']
        if any(pattern in name_lower for pattern in male_patterns):
            return 'Male'
        
        # Default to neutral
        return 'Neutral'
    
    def _create_voice_catalog(self) -> None:
        """Create the 13-voice catalog from detected voices"""
        system_voices = self._detect_system_voices()
        
        # Define the 13-voice mapping
        voice_catalog = [
            ("voice_01", "David", "Male", "Professional male voice"),
            ("voice_02", "Zira", "Female", "Professional female voice"),
            ("voice_03", "Mark", "Male", "Casual male voice"),
            ("voice_04", "Hazel", "Female", "Friendly female voice"),
            ("voice_05", "Helena", "Female", "Assistant female voice"),
            ("voice_06", "James", "Male", "Executive male voice"),
            ("voice_07", "Catherine", "Female", "Narrator female voice"),
            ("voice_08", "Richard", "Male", "Technical male voice"),
            ("voice_09", "Eva", "Female", "Assistant female voice"),
            ("voice_10", "Sean", "Male", "Backup male voice"),
            ("voice_11", "Sabina", "Female", "Backup female voice"),
            ("voice_12", "Alex", "Male", "Fallback male voice"),
            ("voice_13", "System", "Neutral", "System default voice")
        ]
        
        # Map system voices to catalog
        for voice_id, preferred_name, gender, purpose in voice_catalog:
            system_voice = self._find_best_system_voice(system_voices, preferred_name, gender)
            
            if system_voice:
                self.voices[voice_id] = VoiceInfo(
                    voice_id=voice_id,
                    name=preferred_name,
                    gender=gender,
                    system_id=system_voice['id'],
                    available=True,
                    purpose=purpose
                )
            else:
                # Create unavailable voice entry
                self.voices[voice_id] = VoiceInfo(
                    voice_id=voice_id,
                    name=preferred_name,
                    gender=gender,
                    system_id="",
                    available=False,
                    purpose=purpose
                )
        
        available_count = sum(1 for v in self.voices.values() if v.available)
        self.logger.info(f"Voice catalog created: {available_count}/13 voices available")
        self.event_bus.emit("audio.voices.catalog_created", {"count": available_count})
    
    def _find_best_system_voice(self, system_voices: List[Dict], preferred_name: str, gender: str) -> Optional[Dict]:
        """Find the best matching system voice"""
        # Try exact name match first
        for voice in system_voices:
            if preferred_name.lower() in voice['name'].lower():
                return voice
        
        # Try gender match
        if gender != "Neutral":
            for voice in system_voices:
                if voice['gender'] == gender:
                    return voice
        
        # Return first available as fallback
        return system_voices[0] if system_voices else None
    
    def _set_default_voice(self) -> None:
        """Set the default voice from configuration or first available"""
        default_voice_id = self.config.get('default_voice', 'voice_01')
        
        if default_voice_id in self.voices and self.voices[default_voice_id].available:
            self.set_voice(default_voice_id)
        else:
            # Find first available voice
            for voice in self.voices.values():
                if voice.available:
                    self.set_voice(voice.voice_id)
                    break
    
    def _load_user_settings(self) -> None:
        """Load user voice settings from file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                
                # Apply saved voice settings
                for voice_id, voice_settings in settings.get('voices', {}).items():
                    if voice_id in self.voices:
                        voice = self.voices[voice_id]
                        voice.rate = voice_settings.get('rate', voice.rate)
                        voice.volume = voice_settings.get('volume', voice.volume)
                
                # Set saved current voice
                saved_voice = settings.get('current_voice')
                if saved_voice and saved_voice in self.voices:
                    self.set_voice(saved_voice)
                
                self.logger.info("User voice settings loaded")
        
        except Exception as e:
            self.logger.error(f"Failed to load voice settings: {e}")
    
    def _save_user_settings(self) -> None:
        """Save user voice settings to file"""
        try:
            settings = {
                'current_voice': self.current_voice.voice_id if self.current_voice else None,
                'voices': {}
            }
            
            for voice_id, voice in self.voices.items():
                if voice.available:
                    settings['voices'][voice_id] = {
                        'rate': voice.rate,
                        'volume': voice.volume
                    }
            
            # Ensure config directory exists
            self.settings_file.parent.mkdir(exist_ok=True)
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            self.logger.debug("User voice settings saved")
        
        except Exception as e:
            self.logger.error(f"Failed to save voice settings: {e}")
    
    def _register_event_handlers(self) -> None:
        """Register event bus handlers with error handling"""
        try:
            if not self.event_bus:
                self.logger.error("Event bus not available for audio engine")
                return
            
            if not self.event_bus._initialized:
                self.logger.warning("Event bus not initialized, initializing now")
                self.event_bus.initialize()
            
            # Register event handlers with error handling
            self.event_bus.subscribe("audio.speak", self._on_speak_request)
            self.event_bus.subscribe("audio.voice.set", self._on_voice_change_request)
            self.event_bus.subscribe("audio.voice.stop", self._on_stop_request)
            
            self.logger.info("Audio engine event handlers registered successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to register event handlers: {e}")
    
    def _on_speak_request(self, data: Dict[str, Any]) -> None:
        """Handle speak requests from event bus with validation"""
        try:
            text = data.get('text', '') if isinstance(data, dict) else str(data)
            if text and text.strip():
                self.speak(text)
            else:
                self.logger.warning("Empty text received in speak request")
        except Exception as e:
            self.logger.error(f"Error handling speak request: {e}")
    
    def _on_voice_change_request(self, data: Dict[str, Any]) -> None:
        """Handle voice change requests from event bus with validation"""
        try:
            voice_id = data.get('voice_id', '') if isinstance(data, dict) else str(data)
            if voice_id:
                success = self.set_voice(voice_id)
                if not success:
                    self.logger.warning(f"Failed to change voice to: {voice_id}")
            else:
                self.logger.warning("Empty voice_id received in voice change request")
        except Exception as e:
            self.logger.error(f"Error handling voice change request: {e}")
    
    def _on_stop_request(self, data: Optional[Dict[str, Any]] = None) -> None:
        """Handle stop speaking requests with error handling"""
        try:
            self.stop_speaking()
        except Exception as e:
            self.logger.error(f"Error handling stop request: {e}")
    
    def _on_speak_start(self, name: str) -> None:
        """Callback when speech starts with error handling"""
        try:
            self.is_speaking = True
            if self.event_bus and self.event_bus._initialized:
                self.event_bus.emit("audio.speak.started", {"text": name})
        except Exception as e:
            self.logger.error(f"Error in speak start callback: {e}")
    
    def _on_speak_end(self, name: str, completed: bool) -> None:
        """Callback when speech ends with error handling"""
        try:
            self.is_speaking = False
            if self.event_bus and self.event_bus._initialized:
                self.event_bus.emit("audio.speak.finished", {"text": name, "completed": completed})
        except Exception as e:
            self.logger.error(f"Error in speak end callback: {e}")
    
    def _on_speak_error(self, name: str, exception: Exception) -> None:
        """Callback when speech error occurs with error handling"""
        try:
            self.is_speaking = False
            self.logger.error(f"Speech error: {exception}")
            if self.event_bus and self.event_bus._initialized:
                self.event_bus.emit("audio.speak.error", {"text": name, "error": str(exception)})
        except Exception as e:
            self.logger.error(f"Error in speak error callback: {e}")
    
    # Public API Methods
    
    def get_available_voices(self) -> List[VoiceInfo]:
        """Get list of available voices"""
        return [voice for voice in self.voices.values() if voice.available]
    
    def get_voice_info(self, voice_id: str) -> Optional[VoiceInfo]:
        """Get information about a specific voice"""
        return self.voices.get(voice_id)
    
    def list_voices(self) -> Dict[str, Dict[str, Any]]:
        """List all voices with their information"""
        return {vid: asdict(voice) for vid, voice in self.voices.items()}
    
    def set_voice(self, voice_id: str) -> bool:
        """Set the active voice"""
        if voice_id not in self.voices:
            self.logger.error(f"Voice {voice_id} not found")
            return False
        
        voice = self.voices[voice_id]
        if not voice.available:
            self.logger.error(f"Voice {voice.name} not available")
            return False
        
        try:
            with self.engine_lock:
                if self.engine:
                    self.engine.setProperty('voice', voice.system_id)
                    self.engine.setProperty('rate', voice.rate)
                    self.engine.setProperty('volume', voice.volume)
                    
                    self.current_voice = voice
                    self._save_user_settings()
                    
                    self.logger.info(f"Voice changed to: {voice.name}")
                    self.event_bus.emit("audio.voice.changed", {
                        "voice_id": voice_id,
                        "voice_name": voice.name
                    })
                    return True
        
        except Exception as e:
            self.logger.error(f"Failed to set voice: {e}")
            self.event_bus.emit("audio.voice.error", {"error": str(e)})
        
        return False
    
    def speak(self, text: str, interrupt: bool = False) -> bool:
        """Speak the given text"""
        if not text or not text.strip():
            return False
        
        if not self.engine or not self.current_voice:
            self.logger.error("No audio engine or voice available")
            return False
        
        try:
            with self.engine_lock:
                if interrupt and self.is_speaking:
                    self.engine.stop()
                
                self.engine.say(text)
                
                # Run in separate thread to avoid blocking
                def run_speech():
                    try:
                        if self.engine is not None:
                            self.engine.runAndWait()
                        else:
                            self.logger.error("Audio engine is None, cannot execute speech")
                    except Exception as e:
                        self.logger.error(f"Speech execution error: {e}")
                
                speech_thread = threading.Thread(target=run_speech, daemon=True)
                speech_thread.start()
                
                return True
        
        except Exception as e:
            self.logger.error(f"Speech failed: {e}")
            self.event_bus.emit("audio.speak.error", {"error": str(e)})
            return False
    
    def stop_speaking(self) -> None:
        """Stop current speech"""
        try:
            with self.engine_lock:
                if self.engine and self.is_speaking:
                    self.engine.stop()
                    self.is_speaking = False
                    self.event_bus.emit("audio.speak.stopped")
        
        except Exception as e:
            self.logger.error(f"Failed to stop speech: {e}")
    
    def set_voice_property(self, voice_id: str, property_name: str, value: Any) -> bool:
        """Set a voice property (rate, volume)"""
        if voice_id not in self.voices:
            return False
        
        voice = self.voices[voice_id]
        
        if property_name == 'rate' and isinstance(value, int):
            voice.rate = max(50, min(400, value))  # Clamp rate
        elif property_name == 'volume' and isinstance(value, (int, float)):
            voice.volume = max(0.0, min(1.0, value))  # Clamp volume
        else:
            return False
        
        # If this is the current voice, apply immediately
        if self.current_voice and self.current_voice.voice_id == voice_id:
            try:
                with self.engine_lock:
                    if self.engine:
                        self.engine.setProperty(property_name, value)
                        self._save_user_settings()
                        return True
            except Exception as e:
                self.logger.error(f"Failed to set voice property: {e}")
        
        return False
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about the audio engine"""
        return {
            "engine": "pyttsx3",
            "version": pyttsx3.__version__ if hasattr(pyttsx3, '__version__') else "unknown",
            "voices_available": len(self.get_available_voices()),
            "current_voice": self.current_voice.name if self.current_voice else None,
            "is_speaking": self.is_speaking
        }
    
    def cleanup(self) -> None:
        """Clean up audio engine resources"""
        try:
            self.stop_speaking()
            if self.engine:
                self.engine = None
            self.logger.info("Audio engine cleanup completed")
        except Exception as e:
            self.logger.error(f"Audio engine cleanup error: {e}")
