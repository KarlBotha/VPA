"""
VPA Agent Response Integration
Integrates Edge-TTS neural voices with VPA agent text-to-speech responses
Replaces existing pyttsx3/SAPI system with premium neural voice output

INTEGRATION MANDATE COMPLIANCE:
✅ Replace existing Windows SAPI/pyttsx3 voice system 
✅ Route all agent responses through selected neural voice
✅ Present verified catalog of neural voices for user selection
✅ Maintain modular, testable, and auditable code
✅ Full audit logging and evidence collection
"""

import logging
import json
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime

# Import neural voice system
from .neural_voice_engine import NeuralVoiceEngine, NeuralVoice

class VPAAgentVoiceInterface:
    """
    VPA Agent Voice Interface - Neural Voice Integration
    Primary interface for all VPA agent text-to-speech responses
    Routes agent responses through Edge-TTS neural voice system
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.config_dir = config_dir or Path("vpa_config")
        self.config_dir.mkdir(exist_ok=True)
        
        # Neural voice engine
        self.neural_engine: Optional[NeuralVoiceEngine] = None
        
        # Configuration
        self.config_file = self.config_dir / "agent_voice_config.json"
        self.user_preferences = {
            "preferred_voice": "en-US-AriaNeural",  # Default professional voice
            "speech_rate": "+0%",
            "speech_volume": "+10%",
            "speech_pitch": "+0Hz",
            "auto_speak_responses": True,
            "voice_confirmation_enabled": True
        }
        
        # Integration audit
        self.integration_audit: List[Dict[str, Any]] = []
        
        # Response queue for background speech
        self.response_queue: List[str] = []
        self.speech_lock = threading.Lock()
        
        # Initialize system
        self._initialize_neural_engine()
        self._load_user_preferences()
        
        self.logger.info("VPA Agent Voice Interface initialized - Neural voice system active")
    
    def _initialize_neural_engine(self) -> bool:
        """Initialize neural voice engine for agent responses"""
        try:
            self.neural_engine = NeuralVoiceEngine()
            
            if self.neural_engine and self.neural_engine.current_voice:
                self._log_integration("neural_engine_init", {
                    "status": "success",
                    "default_voice": self.neural_engine.current_voice.name,
                    "available_voices": len(self.neural_engine.voice_catalog)
                })
                
                self.logger.info("Neural voice engine initialized for agent responses")
                return True
            else:
                self._log_integration("neural_engine_init", {
                    "status": "failed",
                    "reason": "engine_not_ready"
                })
                return False
                
        except Exception as e:
            self.logger.error(f"Neural engine initialization failed: {e}")
            self._log_integration("neural_engine_init", {
                "status": "error",
                "error": str(e)
            })
            return False
    
    def speak_agent_response(self, response_text: str, blocking: bool = False) -> bool:
        """
        Primary interface for VPA agent speech responses
        Routes all agent text through neural voice system
        
        Args:
            response_text: Agent response text to speak
            blocking: Whether to wait for speech completion
            
        Returns:
            bool: Success status
        """
        if not response_text or not response_text.strip():
            return False
        
        if not self.user_preferences.get("auto_speak_responses", True):
            self.logger.debug("Auto-speak disabled, skipping agent response")
            return True
        
        try:
            # Log agent response for audit
            current_voice_name = "Unknown"
            if self.neural_engine and self.neural_engine.current_voice:
                current_voice_name = self.neural_engine.current_voice.name
            
            self._log_integration("agent_response", {
                "text_length": len(response_text),
                "text_preview": response_text[:100],
                "voice": current_voice_name,
                "blocking": blocking,
                "timestamp": datetime.now().isoformat()
            })
            
            # Route through neural voice engine
            if self.neural_engine:
                with self.speech_lock:
                    success = self.neural_engine.speak(response_text, blocking=blocking)
                
                if success:
                    current_voice_name = "Unknown"
                    if self.neural_engine.current_voice:
                        current_voice_name = self.neural_engine.current_voice.name
                    
                    self.logger.info(f"Agent response spoken: {len(response_text)} characters")
                    self._log_integration("agent_speech_success", {
                        "text_length": len(response_text),
                        "voice": current_voice_name,
                        "blocking": blocking
                    })
                    return True
                else:
                    self.logger.warning("Agent response speech failed")
                    self._log_integration("agent_speech_failed", {
                        "text_length": len(response_text),
                        "reason": "neural_engine_failed"
                    })
                    return False
            else:
                self.logger.error("Neural engine not available for agent response")
                return False
                
        except Exception as e:
            self.logger.error(f"Agent response speech error: {e}")
            self._log_integration("agent_speech_error", {
                "text_preview": response_text[:50],
                "error": str(e)
            })
            return False
    
    def get_available_agent_voices(self) -> List[Dict[str, Any]]:
        """
        Get available neural voices for agent responses
        Provides voice catalog for user selection/configuration
        """
        if not self.neural_engine:
            return []
        
        agent_voices = []
        
        for voice in self.neural_engine.get_available_voices():
            agent_voices.append({
                "voice_id": voice.voice_id,
                "name": voice.name,
                "gender": voice.gender,
                "language": voice.language,
                "region": voice.region,
                "quality": voice.quality,
                "description": voice.description,
                "sample_phrase": voice.sample_phrase,
                "recommended_for": self._get_voice_recommendations(voice)
            })
        
        return agent_voices
    
    def _get_voice_recommendations(self, voice: NeuralVoice) -> List[str]:
        """Get usage recommendations for voice"""
        recommendations = []
        
        # Professional voices
        if voice.name in ["Aria", "Guy", "Andrew", "Emma"]:
            recommendations.append("Professional meetings")
            recommendations.append("Business presentations")
        
        # Friendly voices
        if voice.name in ["Jenny", "Christopher", "Ava"]:
            recommendations.append("Casual conversations")
            recommendations.append("Daily assistance")
        
        # British voices
        if voice.region == "GB":
            recommendations.append("Formal communications")
            recommendations.append("Educational content")
        
        return recommendations
    
    def set_agent_voice(self, voice_identifier: str) -> bool:
        """
        Set agent voice by ID or name
        Updates voice for all future agent responses
        
        Args:
            voice_identifier: Voice ID (e.g., 'en-US-AriaNeural') or name (e.g., 'Aria')
            
        Returns:
            bool: Success status
        """
        if not self.neural_engine:
            self.logger.error("Neural engine not available for voice change")
            return False
        
        try:
            # Set voice in neural engine
            success = self.neural_engine.set_voice(voice_identifier)
            
            if success and self.neural_engine.current_voice:
                # Update user preferences
                self.user_preferences["preferred_voice"] = self.neural_engine.current_voice.voice_id
                self._save_user_preferences()
                
                # Log voice change
                self._log_integration("agent_voice_changed", {
                    "voice_identifier": voice_identifier,
                    "new_voice_id": self.neural_engine.current_voice.voice_id,
                    "new_voice_name": self.neural_engine.current_voice.name,
                    "gender": self.neural_engine.current_voice.gender,
                    "region": self.neural_engine.current_voice.region
                })
                
                self.logger.info(f"Agent voice changed to: {self.neural_engine.current_voice.name}")
                
                # Optional voice confirmation
                if self.user_preferences.get("voice_confirmation_enabled", True):
                    self.test_agent_voice()
                
                return True
            else:
                self.logger.error(f"Failed to set agent voice: {voice_identifier}")
                return False
                
        except Exception as e:
            self.logger.error(f"Agent voice change error: {e}")
            self._log_integration("agent_voice_change_error", {
                "voice_identifier": voice_identifier,
                "error": str(e)
            })
            return False
    
    def test_agent_voice(self) -> bool:
        """
        Test current agent voice with sample phrase
        Provides user confirmation of voice selection
        """
        if not self.neural_engine or not self.neural_engine.current_voice:
            return False
        
        try:
            current_voice = self.neural_engine.current_voice
            test_phrase = f"Hello! I'm {current_voice.name}, your new AI assistant voice. How do I sound?"
            
            self.logger.info(f"Testing agent voice: {current_voice.name}")
            self._log_integration("agent_voice_test", {
                "voice_name": current_voice.name,
                "voice_id": current_voice.voice_id,
                "test_phrase": test_phrase
            })
            
            # Speak test phrase
            success = self.neural_engine.speak(test_phrase, blocking=True)
            
            if success:
                self.logger.info("Agent voice test completed successfully")
                return True
            else:
                self.logger.warning("Agent voice test failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Agent voice test error: {e}")
            return False
    
    def get_current_agent_voice(self) -> Optional[Dict[str, Any]]:
        """Get current agent voice information"""
        if not self.neural_engine or not self.neural_engine.current_voice:
            return None
        
        voice = self.neural_engine.current_voice
        return {
            "voice_id": voice.voice_id,
            "name": voice.name,
            "gender": voice.gender,
            "language": voice.language,
            "region": voice.region,
            "quality": voice.quality,
            "description": voice.description,
            "sample_phrase": voice.sample_phrase
        }
    
    def configure_speech_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Configure speech settings for agent responses
        
        Args:
            settings: Dictionary with speech parameters
                     - speech_rate: e.g., "+20%" or "-10%"
                     - speech_volume: e.g., "+5%" or "-15%"
                     - speech_pitch: e.g., "+10Hz" or "-5Hz"
                     - auto_speak_responses: boolean
        """
        try:
            # Update user preferences
            for key, value in settings.items():
                if key in self.user_preferences:
                    self.user_preferences[key] = value
            
            # Update neural engine settings
            if self.neural_engine:
                if "speech_rate" in settings:
                    self.neural_engine.playback_settings["rate"] = settings["speech_rate"]
                if "speech_volume" in settings:
                    self.neural_engine.playback_settings["volume"] = settings["speech_volume"]
                if "speech_pitch" in settings:
                    self.neural_engine.playback_settings["pitch"] = settings["speech_pitch"]
            
            # Save preferences
            self._save_user_preferences()
            
            self._log_integration("speech_settings_updated", {
                "settings": settings,
                "timestamp": datetime.now().isoformat()
            })
            
            self.logger.info("Agent speech settings updated")
            return True
            
        except Exception as e:
            self.logger.error(f"Speech settings update error: {e}")
            return False
    
    def get_agent_voice_status(self) -> Dict[str, Any]:
        """Get comprehensive agent voice system status"""
        status = {
            "neural_engine_available": self.neural_engine is not None,
            "current_voice": self.get_current_agent_voice(),
            "user_preferences": self.user_preferences.copy(),
            "available_voices": len(self.get_available_agent_voices()),
            "integration_events": len(self.integration_audit),
            "system_status": self.neural_engine.get_voice_status() if self.neural_engine else None
        }
        
        return status
    
    def _load_user_preferences(self):
        """Load user voice preferences"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_prefs = json.load(f)
                    self.user_preferences.update(loaded_prefs)
                
                # Set preferred voice
                if self.neural_engine and self.user_preferences.get("preferred_voice"):
                    self.neural_engine.set_voice(self.user_preferences["preferred_voice"])
                
                self.logger.info("User voice preferences loaded")
            
        except Exception as e:
            self.logger.warning(f"Failed to load user preferences: {e}")
    
    def _save_user_preferences(self):
        """Save user voice preferences"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_preferences, f, indent=2, ensure_ascii=False)
            
            self.logger.debug("User voice preferences saved")
            
        except Exception as e:
            self.logger.error(f"Failed to save user preferences: {e}")
    
    def _log_integration(self, event: str, data: Dict[str, Any]):
        """Log integration event for audit"""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "data": data
        }
        
        self.integration_audit.append(audit_entry)
        
        # Keep audit log manageable
        if len(self.integration_audit) > 1000:
            self.integration_audit = self.integration_audit[-1000:]
    
    def get_integration_audit_log(self) -> List[Dict[str, Any]]:
        """Get complete integration audit log"""
        return self.integration_audit.copy()
    
    def export_integration_evidence(self) -> Dict[str, Any]:
        """Export comprehensive integration evidence for user review"""
        evidence = {
            "integration_summary": {
                "neural_engine_active": self.neural_engine is not None,
                "total_voices_available": len(self.get_available_agent_voices()),
                "current_agent_voice": self.get_current_agent_voice(),
                "user_preferences": self.user_preferences.copy(),
                "integration_events": len(self.integration_audit)
            },
            "voice_catalog": self.get_available_agent_voices(),
            "system_status": self.get_agent_voice_status(),
            "audit_log": self.get_integration_audit_log(),
            "evidence_timestamp": datetime.now().isoformat()
        }
        
        return evidence
    
    def shutdown(self):
        """Graceful shutdown of agent voice system"""
        try:
            self.logger.info("Shutting down VPA Agent Voice Interface...")
            
            # Save preferences
            self._save_user_preferences()
            
            # Shutdown neural engine
            if self.neural_engine:
                self.neural_engine.shutdown()
            
            self._log_integration("system_shutdown", {
                "status": "complete",
                "timestamp": datetime.now().isoformat()
            })
            
            self.logger.info("VPA Agent Voice Interface shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Agent voice shutdown error: {e}")

# Export main interface
__all__ = ['VPAAgentVoiceInterface']
