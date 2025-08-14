"""
Neural Voice Engine - Edge-TTS Integration
Primary voice engine for VPA agent text-to-speech output
Replaces Windows SAPI/pyttsx3 with Microsoft Edge-TTS neural voices

AUDIT COMPLIANCE:
- Modular, testable, and auditable design
- Full logging of voice selection, playbook, and configuration changes
- Sample phrase testing for each neural voice
- Evidence-based implementation following user mandate
"""

import asyncio
import logging
import tempfile
import pygame
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import threading
import time

try:
    import edge_tts
except ImportError:
    edge_tts = None

@dataclass
class NeuralVoice:
    """Neural voice configuration with full metadata"""
    voice_id: str
    name: str
    gender: str
    language: str
    region: str
    quality: str
    description: str
    sample_phrase: str
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

class NeuralVoiceEngine:
    """
    Edge-TTS Neural Voice Engine
    Primary voice system for VPA agent responses
    """
    
    def __init__(self, audio_device: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.audio_device = audio_device
        
        # Voice system state
        self.current_voice: Optional[NeuralVoice] = None
        self.voice_catalog: Dict[str, NeuralVoice] = {}
        self.playback_settings = {
            "rate": "+0%",
            "volume": "+0%",
            "pitch": "+0Hz"
        }
        
        # Audio playback
        self.pygame_initialized = False
        self.temp_audio_files: List[Path] = []
        
        # Threading and async support
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.background_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        
        # Audit logging
        self.audit_log: List[Dict[str, Any]] = []
        
        # Initialize systems
        self._initialize_pygame()
        self._initialize_voice_catalog()
        self._start_async_loop()
        
        self.logger.info("Neural Voice Engine initialized - Edge-TTS primary system")
    
    def _initialize_pygame(self) -> bool:
        """Initialize pygame for audio playback"""
        try:
            if not self.pygame_initialized:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self.pygame_initialized = True
                self._log_audit("pygame_init", {"status": "success", "config": "22050Hz, 16-bit, stereo"})
                self.logger.info("Pygame audio system initialized")
            return True
        except Exception as e:
            self._log_audit("pygame_init", {"status": "failed", "error": str(e)})
            self.logger.error(f"Pygame initialization failed: {e}")
            return False
    
    def _initialize_voice_catalog(self):
        """Initialize neural voice catalog with professional voices"""
        
        # Professional neural voice catalog (verified working)
        neural_voices = [
            # Male Professional Voices
            NeuralVoice(
                voice_id="en-US-AndrewNeural",
                name="Andrew",
                gender="Male",
                language="English",
                region="US",
                quality="Premium",
                description="Professional male voice, clear and authoritative",
                sample_phrase="Hello, I'm Andrew. I'll be your AI assistant today."
            ),
            NeuralVoice(
                voice_id="en-US-ChristopherNeural",
                name="Christopher",
                gender="Male", 
                language="English",
                region="US",
                quality="Premium",
                description="Friendly male voice, conversational and warm",
                sample_phrase="Hi there! I'm Christopher, ready to help you with anything."
            ),
            NeuralVoice(
                voice_id="en-US-GuyNeural",
                name="Guy",
                gender="Male",
                language="English",
                region="US",
                quality="Premium",
                description="Mature male voice, professional and reliable",
                sample_phrase="Good day! I'm Guy, your virtual personal assistant."
            ),
            NeuralVoice(
                voice_id="en-GB-RogerNeural",
                name="Roger",
                gender="Male",
                language="English",
                region="GB",
                quality="Premium",
                description="British male voice, sophisticated and articulate",
                sample_phrase="Good afternoon. I'm Roger, pleased to assist you today."
            ),
            NeuralVoice(
                voice_id="en-US-EricNeural",
                name="Eric",
                gender="Male",
                language="English",
                region="US",
                quality="Premium",
                description="Young adult male voice, energetic and friendly",
                sample_phrase="Hey! I'm Eric, your AI companion for today's tasks."
            ),
            NeuralVoice(
                voice_id="en-GB-SteffanNeural",
                name="Steffan",
                gender="Male",
                language="English",
                region="GB",
                quality="Premium",
                description="Welsh-accented male voice, distinctive and pleasant",
                sample_phrase="Hello! I'm Steffan, ready to help with your requests."
            ),
            
            # Female Professional Voices  
            NeuralVoice(
                voice_id="en-US-EmmaNeural",
                name="Emma",
                gender="Female",
                language="English",
                region="US",
                quality="Premium",
                description="Professional female voice, clear and confident",
                sample_phrase="Hello! I'm Emma, your AI assistant for today."
            ),
            NeuralVoice(
                voice_id="en-US-AvaNeural",
                name="Ava",
                gender="Female",
                language="English",
                region="US",
                quality="Premium",
                description="Young female voice, modern and approachable",
                sample_phrase="Hi! I'm Ava, excited to help you accomplish your goals."
            ),
            NeuralVoice(
                voice_id="en-US-AriaNeural",
                name="Aria",
                gender="Female",
                language="English",
                region="US",
                quality="Premium",
                description="Sophisticated female voice, elegant and professional",
                sample_phrase="Good day! I'm Aria, your virtual personal assistant."
            ),
            NeuralVoice(
                voice_id="en-US-JennyNeural",
                name="Jenny",
                gender="Female",
                language="English",
                region="US",
                quality="Premium",
                description="Warm female voice, friendly and supportive",
                sample_phrase="Hello there! I'm Jenny, here to make your day easier."
            ),
            NeuralVoice(
                voice_id="en-GB-LibbyNeural",
                name="Libby",
                gender="Female",
                language="English",
                region="GB",
                quality="Premium",
                description="British female voice, articulate and professional",
                sample_phrase="Good morning! I'm Libby, delighted to assist you."
            ),
            NeuralVoice(
                voice_id="en-GB-MichelleNeural",
                name="Michelle",
                gender="Female",
                language="English",
                region="GB",
                quality="Premium",
                description="British female voice, warm and conversational",
                sample_phrase="Hello! I'm Michelle, your AI companion today."
            )
        ]
        
        # Build voice catalog
        for voice in neural_voices:
            self.voice_catalog[voice.voice_id] = voice
        
        # Set default voice (Aria - recommended professional voice)
        default_voice_id = "en-US-AriaNeural"
        if default_voice_id in self.voice_catalog:
            self.current_voice = self.voice_catalog[default_voice_id]
            self._log_audit("default_voice_set", {
                "voice_id": default_voice_id,
                "voice_name": self.current_voice.name
            })
        
        self.logger.info(f"Neural voice catalog initialized: {len(self.voice_catalog)} voices available")
        self._log_audit("voice_catalog_init", {
            "total_voices": len(self.voice_catalog),
            "male_voices": len([v for v in self.voice_catalog.values() if v.gender == "Male"]),
            "female_voices": len([v for v in self.voice_catalog.values() if v.gender == "Female"]),
            "default_voice": default_voice_id
        })
    
    def _start_async_loop(self):
        """Start background async event loop for Edge-TTS"""
        def run_async_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            self.logger.info("Async event loop started for Edge-TTS")
            self._log_audit("async_loop_start", {"status": "success"})
            
            try:
                self.loop.run_until_complete(self._async_loop_manager())
            except Exception as e:
                self.logger.error(f"Async loop error: {e}")
                self._log_audit("async_loop_error", {"error": str(e)})
        
        self.background_thread = threading.Thread(target=run_async_loop, daemon=True)
        self.background_thread.start()
    
    async def _async_loop_manager(self):
        """Manage the async event loop"""
        while not self._shutdown_event.is_set():
            await asyncio.sleep(0.1)
    
    def get_available_voices(self) -> List[NeuralVoice]:
        """Get list of available neural voices"""
        return [voice for voice in self.voice_catalog.values() if voice.enabled]
    
    def get_voice_by_name(self, name: str) -> Optional[NeuralVoice]:
        """Get voice by friendly name"""
        for voice in self.voice_catalog.values():
            if voice.name.lower() == name.lower():
                return voice
        return None
    
    def set_voice(self, voice_identifier: str) -> bool:
        """
        Set active neural voice by ID or name
        
        Args:
            voice_identifier: Voice ID (e.g., 'en-US-AriaNeural') or name (e.g., 'Aria')
        
        Returns:
            bool: Success status
        """
        try:
            target_voice = None
            
            # Try by voice ID first
            if voice_identifier in self.voice_catalog:
                target_voice = self.voice_catalog[voice_identifier]
            else:
                # Try by name
                target_voice = self.get_voice_by_name(voice_identifier)
            
            if not target_voice:
                self.logger.error(f"Voice not found: {voice_identifier}")
                self._log_audit("voice_set_failed", {
                    "identifier": voice_identifier,
                    "reason": "voice_not_found",
                    "available_voices": list(self.voice_catalog.keys())
                })
                return False
            
            if not target_voice.enabled:
                self.logger.error(f"Voice disabled: {target_voice.name}")
                self._log_audit("voice_set_failed", {
                    "identifier": voice_identifier,
                    "reason": "voice_disabled",
                    "voice_name": target_voice.name
                })
                return False
            
            # Set new voice
            previous_voice = self.current_voice.name if self.current_voice else "None"
            self.current_voice = target_voice
            
            self.logger.info(f"Voice changed: {previous_voice} → {target_voice.name}")
            self._log_audit("voice_changed", {
                "previous_voice": previous_voice,
                "new_voice": target_voice.name,
                "voice_id": target_voice.voice_id,
                "gender": target_voice.gender,
                "region": target_voice.region
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Voice selection failed: {e}")
            self._log_audit("voice_set_error", {
                "identifier": voice_identifier,
                "error": str(e)
            })
            return False
    
    def speak(self, text: str, blocking: bool = True) -> bool:
        """
        Speak text using current neural voice
        
        Args:
            text: Text to speak
            blocking: Whether to wait for completion
            
        Returns:
            bool: Success status
        """
        if not text or not text.strip():
            return False
        
        if not self.current_voice:
            self.logger.error("No voice selected")
            return False
        
        if not edge_tts:
            self.logger.error("edge-tts not available")
            return False
        
        try:
            # Execute async TTS synthesis
            if blocking:
                return self._speak_sync(text)
            else:
                # Non-blocking - schedule in background
                if self.loop:
                    asyncio.run_coroutine_threadsafe(self._speak_async(text), self.loop)
                return True
                
        except Exception as e:
            self.logger.error(f"Speech synthesis failed: {e}")
            self._log_audit("speech_failed", {
                "text_preview": text[:50],
                "voice": self.current_voice.name,
                "error": str(e)
            })
            return False
    
    def _speak_sync(self, text: str) -> bool:
        """Synchronous speech synthesis"""
        try:
            # Create new event loop for sync operation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(self._speak_async(text))
                return result
            finally:
                loop.close()
                
        except Exception as e:
            self.logger.error(f"Sync speech failed: {e}")
            return False
    
    async def _speak_async(self, text: str) -> bool:
        """Async speech synthesis and playback"""
        try:
            start_time = time.time()
            
            # Validate current voice
            if not self.current_voice:
                self.logger.error("No current voice set for speech synthesis")
                return False
            
            # Validate edge_tts availability
            if not edge_tts:
                self.logger.error("edge_tts module not available")
                return False
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
            temp_path = Path(temp_file.name)
            temp_file.close()
            
            self.temp_audio_files.append(temp_path)
            
            # Generate speech with Edge-TTS
            tts_communicate = edge_tts.Communicate(
                text=text,
                voice=self.current_voice.voice_id,
                rate=self.playback_settings["rate"],
                volume=self.playback_settings["volume"],
                pitch=self.playback_settings["pitch"]
            )
            
            # Save to file
            await tts_communicate.save(str(temp_path))
            
            synthesis_time = time.time() - start_time
            
            # Play audio file
            playback_start = time.time()
            
            if self.pygame_initialized:
                pygame.mixer.music.load(str(temp_path))
                pygame.mixer.music.play()
                
                # Wait for playback completion
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
            
            playback_time = time.time() - playback_start
            total_time = time.time() - start_time
            
            # Cleanup temp file
            try:
                temp_path.unlink()
                self.temp_audio_files.remove(temp_path)
            except:
                pass
            
            # Log successful playback
            self._log_audit("speech_success", {
                "text_length": len(text),
                "text_preview": text[:100],
                "voice": self.current_voice.name,
                "voice_id": self.current_voice.voice_id,
                "synthesis_time": round(synthesis_time, 3),
                "playback_time": round(playback_time, 3),
                "total_time": round(total_time, 3),
                "audio_file_size": temp_path.stat().st_size if temp_path.exists() else 0
            })
            
            self.logger.info(f"Speech synthesis complete: {len(text)} chars, {total_time:.2f}s, voice: {self.current_voice.name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Async speech synthesis failed: {e}")
            self._log_audit("speech_async_failed", {
                "text_preview": text[:50],
                "voice": self.current_voice.name if self.current_voice else "None",
                "error": str(e)
            })
            return False
    
    def test_voice(self, voice_identifier: Optional[str] = None) -> bool:
        """
        Test a voice with its sample phrase
        
        Args:
            voice_identifier: Voice ID or name (None for current voice)
            
        Returns:
            bool: Success status
        """
        try:
            if voice_identifier:
                # Test specific voice
                if voice_identifier in self.voice_catalog:
                    test_voice = self.voice_catalog[voice_identifier]
                else:
                    test_voice = self.get_voice_by_name(voice_identifier)
                
                if not test_voice:
                    self.logger.error(f"Voice not found for testing: {voice_identifier}")
                    return False
            else:
                # Test current voice
                test_voice = self.current_voice
                
            if not test_voice:
                self.logger.error("No voice available for testing")
                return False
            
            # Temporarily switch to test voice
            original_voice = self.current_voice
            self.current_voice = test_voice
            
            self.logger.info(f"Testing voice: {test_voice.name}")
            self._log_audit("voice_test_start", {
                "voice_name": test_voice.name,
                "voice_id": test_voice.voice_id,
                "sample_phrase": test_voice.sample_phrase
            })
            
            # Speak sample phrase
            success = self.speak(test_voice.sample_phrase, blocking=True)
            
            # Restore original voice
            if original_voice:
                self.current_voice = original_voice
            
            self._log_audit("voice_test_complete", {
                "voice_name": test_voice.name,
                "success": success
            })
            
            return success
            
        except Exception as e:
            self.logger.error(f"Voice testing failed: {e}")
            self._log_audit("voice_test_failed", {
                "voice_identifier": voice_identifier,
                "error": str(e)
            })
            return False
    
    def get_voice_status(self) -> Dict[str, Any]:
        """Get current voice system status"""
        status = {
            "engine": "Edge-TTS Neural Voice Engine",
            "current_voice": {
                "name": self.current_voice.name if self.current_voice else None,
                "voice_id": self.current_voice.voice_id if self.current_voice else None,
                "gender": self.current_voice.gender if self.current_voice else None,
                "language": self.current_voice.language if self.current_voice else None,
                "region": self.current_voice.region if self.current_voice else None,
                "description": self.current_voice.description if self.current_voice else None
            },
            "available_voices": len(self.voice_catalog),
            "enabled_voices": len([v for v in self.voice_catalog.values() if v.enabled]),
            "playback_settings": self.playback_settings.copy(),
            "pygame_initialized": self.pygame_initialized,
            "edge_tts_available": edge_tts is not None,
            "async_loop_running": self.loop is not None and not self.loop.is_closed(),
            "temp_files": len(self.temp_audio_files)
        }
        
        return status
    
    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get complete audit log"""
        return self.audit_log.copy()
    
    def _log_audit(self, event: str, data: Dict[str, Any]):
        """Log audit event with timestamp"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "data": data
        }
        self.audit_log.append(audit_entry)
        
        # Keep audit log size manageable (last 1000 entries)
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
    
    def save_configuration(self, config_path: Path) -> bool:
        """Save current voice configuration"""
        try:
            config = {
                "current_voice_id": self.current_voice.voice_id if self.current_voice else None,
                "playback_settings": self.playback_settings,
                "voice_catalog": {
                    voice_id: voice.to_dict() 
                    for voice_id, voice in self.voice_catalog.items()
                },
                "timestamp": datetime.now().isoformat()
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self._log_audit("config_saved", {"config_path": str(config_path)})
            self.logger.info(f"Voice configuration saved: {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration save failed: {e}")
            self._log_audit("config_save_failed", {"error": str(e)})
            return False
    
    def load_configuration(self, config_path: Path) -> bool:
        """Load voice configuration"""
        try:
            if not config_path.exists():
                self.logger.warning(f"Configuration file not found: {config_path}")
                return False
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Restore voice selection
            if config.get("current_voice_id"):
                self.set_voice(config["current_voice_id"])
            
            # Restore playback settings
            if config.get("playback_settings"):
                self.playback_settings.update(config["playback_settings"])
            
            self._log_audit("config_loaded", {"config_path": str(config_path)})
            self.logger.info(f"Voice configuration loaded: {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration load failed: {e}")
            self._log_audit("config_load_failed", {"error": str(e)})
            return False
    
    def shutdown(self):
        """Shutdown voice engine gracefully"""
        try:
            self.logger.info("Shutting down Neural Voice Engine...")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Stop pygame
            if self.pygame_initialized:
                pygame.mixer.quit()
                pygame.quit()
                self.pygame_initialized = False
            
            # Clean up temp files
            for temp_file in self.temp_audio_files:
                try:
                    if temp_file.exists():
                        temp_file.unlink()
                except:
                    pass
            self.temp_audio_files.clear()
            
            # Close async loop
            if self.loop and not self.loop.is_closed():
                self.loop.call_soon_threadsafe(self.loop.stop)
            
            # Wait for background thread
            if self.background_thread and self.background_thread.is_alive():
                self.background_thread.join(timeout=2.0)
            
            self._log_audit("engine_shutdown", {"status": "complete"})
            self.logger.info("Neural Voice Engine shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")
            self._log_audit("engine_shutdown", {"status": "error", "error": str(e)})

# Export main class
__all__ = ['NeuralVoiceEngine', 'NeuralVoice']
