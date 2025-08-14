"""
Voice Command Processing for VPA Audio System
Provides command structure and processing stubs for future NLP/AI integration.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class CommandIntent(Enum):
    """Voice command intents"""
    SET_VOICE = "set_voice"
    ADJUST_RATE = "adjust_rate"
    ADJUST_VOLUME = "adjust_volume"
    TEST_VOICE = "test_voice"
    LIST_VOICES = "list_voices"
    STOP_SPEAKING = "stop_speaking"
    GET_INFO = "get_info"
    UNKNOWN = "unknown"


@dataclass
class VoiceCommand:
    """Voice command structure"""
    intent: CommandIntent
    confidence: float = 0.0
    parameters: Optional[Dict[str, Any]] = None
    raw_text: str = ""
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class VoiceCommandProcessor:
    """Processes voice commands for audio system control"""
    
    def __init__(self, audio_engine):
        """Initialize the command processor"""
        self.logger = logging.getLogger(__name__)
        self.audio_engine = audio_engine
        self.command_handlers: Dict[CommandIntent, Callable] = {}
        
        # Setup command patterns for basic pattern matching
        self._setup_command_patterns()
        
        # Register command handlers
        self._register_handlers()
    
    def _setup_command_patterns(self) -> None:
        """Setup regex patterns for command recognition"""
        self.patterns = {
            CommandIntent.SET_VOICE: [
                r'(?:use|set|switch to|change to) (?:voice )?(?:named )?(\w+)',
                r'(?:use|set) (?:the )?(\w+) voice',
                r'switch to (?:a )?(\w+) voice',
                r'change voice to (\w+)'
            ],
            CommandIntent.ADJUST_RATE: [
                r'(?:speak|talk) (faster|slower)',
                r'(?:speed up|slow down)(?: the voice)?',
                r'set (?:speech )?rate to (\d+)',
                r'(?:make (?:it|voice) )?(faster|slower)'
            ],
            CommandIntent.ADJUST_VOLUME: [
                r'(?:turn|make) (?:it |voice )?(louder|quieter)',
                r'set volume to (\d+)(?:%)?',
                r'volume (up|down)',
                r'(?:increase|decrease) (?:the )?volume'
            ],
            CommandIntent.TEST_VOICE: [
                r'test (?:the )?(?:current )?voice',
                r'try (?:the )?(?:current )?voice',
                r'demo (?:the )?voice',
                r'preview (?:the )?voice',
                r'speak (?:a )?test'
            ],
            CommandIntent.LIST_VOICES: [
                r'(?:list|show) (?:all )?(?:available )?voices',
                r'what voices (?:are )?available',
                r'show me (?:the )?voices',
                r'voice (?:list|options)'
            ],
            CommandIntent.STOP_SPEAKING: [
                r'stop (?:speaking|talking)',
                r'be quiet',
                r'shut up',
                r'silence'
            ],
            CommandIntent.GET_INFO: [
                r'(?:voice|audio) (?:info|information|status)',
                r'current voice (?:info|settings)',
                r'what voice (?:is )?(?:currently )?(?:active|selected)'
            ]
        }
    
    def _register_handlers(self) -> None:
        """Register command handlers"""
        self.command_handlers = {
            CommandIntent.SET_VOICE: self._handle_set_voice,
            CommandIntent.ADJUST_RATE: self._handle_adjust_rate,
            CommandIntent.ADJUST_VOLUME: self._handle_adjust_volume,
            CommandIntent.TEST_VOICE: self._handle_test_voice,
            CommandIntent.LIST_VOICES: self._handle_list_voices,
            CommandIntent.STOP_SPEAKING: self._handle_stop_speaking,
            CommandIntent.GET_INFO: self._handle_get_info
        }
    
    def process_command(self, text: str) -> Dict[str, Any]:
        """Process a voice command and return result"""
        text = text.lower().strip()
        
        if not text:
            return self._create_error_response("Empty command")
        
        # Parse the command
        command = self._parse_command(text)
        
        if command.intent == CommandIntent.UNKNOWN:
            return self._create_error_response(
                "Command not recognized",
                suggestions=self._get_command_suggestions()
            )
        
        # Execute the command
        try:
            handler = self.command_handlers.get(command.intent)
            if handler:
                return handler(command)
            else:
                return self._create_error_response("No handler for command")
        
        except Exception as e:
            self.logger.error(f"Command execution error: {e}")
            return self._create_error_response(f"Command failed: {str(e)}")
    
    def _parse_command(self, text: str) -> VoiceCommand:
        """Parse text into a voice command"""
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    parameters = {}
                    
                    # Extract parameters from match groups
                    if match.groups():
                        parameters = self._extract_parameters(intent, match.groups())
                    
                    return VoiceCommand(
                        intent=intent,
                        confidence=0.8,  # Basic pattern matching confidence
                        parameters=parameters,
                        raw_text=text
                    )
        
        # No pattern matched
        return VoiceCommand(
            intent=CommandIntent.UNKNOWN,
            confidence=0.0,
            raw_text=text
        )
    
    def _extract_parameters(self, intent: CommandIntent, groups: tuple) -> Dict[str, Any]:
        """Extract parameters from regex match groups"""
        parameters = {}
        
        if intent == CommandIntent.SET_VOICE:
            if groups[0]:
                parameters['voice_name'] = groups[0].lower()
        
        elif intent == CommandIntent.ADJUST_RATE:
            if groups[0].isdigit():
                parameters['rate'] = int(groups[0])
            elif groups[0] in ['faster', 'slower']:
                parameters['direction'] = groups[0]
        
        elif intent == CommandIntent.ADJUST_VOLUME:
            if groups[0].isdigit():
                parameters['volume'] = int(groups[0]) / 100.0
            elif groups[0] in ['louder', 'up']:
                parameters['direction'] = 'up'
            elif groups[0] in ['quieter', 'down']:
                parameters['direction'] = 'down'
        
        return parameters
    
    def _create_success_response(self, message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a success response"""
        response = {
            "status": "success",
            "message": message
        }
        if data:
            response["data"] = data
        return response
    
    def _create_error_response(self, message: str, suggestions: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create an error response"""
        response = {
            "status": "error",
            "message": message
        }
        if suggestions:
            response["suggestions"] = suggestions
        return response
    
    def _get_command_suggestions(self) -> List[str]:
        """Get command suggestions for help"""
        return [
            "\"use David voice\" - Set specific voice",
            "\"speak faster\" - Adjust speech rate",
            "\"make it louder\" - Adjust volume",
            "\"test voice\" - Test current voice",
            "\"list voices\" - Show available voices",
            "\"stop speaking\" - Stop current speech"
        ]
    
    # Command Handlers
    
    def _handle_set_voice(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handle voice selection commands"""
        if not command.parameters:
            return self._create_error_response("No voice name specified")
            
        voice_name = command.parameters.get('voice_name', '').lower()
        
        if not voice_name:
            return self._create_error_response("No voice name specified")
        
        # Find matching voice by name
        matching_voices = []
        for voice_id, voice in self.audio_engine.voices.items():
            if voice.available and voice_name in voice.name.lower():
                matching_voices.append((voice_id, voice))
        
        if not matching_voices:
            available_names = [v.name for v in self.audio_engine.get_available_voices()]
            return self._create_error_response(
                f"Voice '{voice_name}' not found",
                suggestions=[f"Available voices: {', '.join(available_names)}"]
            )
        
        # Use the best match
        voice_id, voice = matching_voices[0]
        
        if self.audio_engine.set_voice(voice_id):
            return self._create_success_response(
                f"Voice changed to {voice.name}",
                data={"voice_id": voice_id, "voice_name": voice.name}
            )
        else:
            return self._create_error_response(f"Failed to set voice to {voice.name}")
    
    def _handle_adjust_rate(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handle speech rate adjustment commands"""
        if not self.audio_engine.current_voice:
            return self._create_error_response("No voice selected")
        
        if not command.parameters:
            return self._create_error_response("No rate adjustment specified")
        
        current_voice = self.audio_engine.current_voice
        current_rate = current_voice.rate
        
        if 'rate' in command.parameters:
            new_rate = command.parameters['rate']
        elif 'direction' in command.parameters:
            direction = command.parameters['direction']
            if direction == 'faster':
                new_rate = min(400, current_rate + 50)
            else:  # slower
                new_rate = max(50, current_rate - 50)
        else:
            return self._create_error_response("No rate adjustment specified")
        
        if self.audio_engine.set_voice_property(current_voice.voice_id, 'rate', new_rate):
            return self._create_success_response(
                f"Speech rate changed to {new_rate} WPM",
                data={"rate": new_rate}
            )
        else:
            return self._create_error_response("Failed to adjust speech rate")
    
    def _handle_adjust_volume(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handle volume adjustment commands"""
        if not self.audio_engine.current_voice:
            return self._create_error_response("No voice selected")
        
        if not command.parameters:
            return self._create_error_response("No volume adjustment specified")
        
        current_voice = self.audio_engine.current_voice
        current_volume = current_voice.volume
        
        if 'volume' in command.parameters:
            new_volume = command.parameters['volume']
        elif 'direction' in command.parameters:
            direction = command.parameters['direction']
            if direction == 'up':
                new_volume = min(1.0, current_volume + 0.1)
            else:  # down
                new_volume = max(0.0, current_volume - 0.1)
        else:
            return self._create_error_response("No volume adjustment specified")
        
        if self.audio_engine.set_voice_property(current_voice.voice_id, 'volume', new_volume):
            return self._create_success_response(
                f"Volume changed to {int(new_volume * 100)}%",
                data={"volume": new_volume}
            )
        else:
            return self._create_error_response("Failed to adjust volume")
    
    def _handle_test_voice(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handle voice testing commands"""
        if not self.audio_engine.current_voice:
            return self._create_error_response("No voice selected")
        
        current_voice = self.audio_engine.current_voice
        test_text = f"Hello! This is {current_voice.name}, speaking at {current_voice.rate} words per minute."
        
        if self.audio_engine.speak(test_text):
            return self._create_success_response(
                f"Testing voice: {current_voice.name}",
                data={"voice_name": current_voice.name, "test_text": test_text}
            )
        else:
            return self._create_error_response("Failed to test voice")
    
    def _handle_list_voices(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handle voice listing commands"""
        available_voices = self.audio_engine.get_available_voices()
        
        if not available_voices:
            return self._create_error_response("No voices available")
        
        voice_list = []
        for voice in available_voices:
            voice_info = {
                "id": voice.voice_id,
                "name": voice.name,
                "gender": voice.gender,
                "purpose": voice.purpose,
                "is_current": voice == self.audio_engine.current_voice
            }
            voice_list.append(voice_info)
        
        return self._create_success_response(
            f"Found {len(voice_list)} available voices",
            data={"voices": voice_list}
        )
    
    def _handle_stop_speaking(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handle stop speaking commands"""
        self.audio_engine.stop_speaking()
        return self._create_success_response("Speech stopped")
    
    def _handle_get_info(self, command: VoiceCommand) -> Dict[str, Any]:
        """Handle info request commands"""
        engine_info = self.audio_engine.get_engine_info()
        
        if self.audio_engine.current_voice:
            voice_info = {
                "name": self.audio_engine.current_voice.name,
                "gender": self.audio_engine.current_voice.gender,
                "rate": self.audio_engine.current_voice.rate,
                "volume": int(self.audio_engine.current_voice.volume * 100)
            }
            
            message = f"Current voice: {voice_info['name']} ({voice_info['gender']}) at {voice_info['rate']} WPM, {voice_info['volume']}% volume"
        else:
            voice_info = None
            message = "No voice currently selected"
        
        return self._create_success_response(
            message,
            data={
                "engine_info": engine_info,
                "current_voice": voice_info
            }
        )


# Future integration placeholder for advanced NLP/AI processing
class AdvancedCommandProcessor:
    """Placeholder for future NLP/AI-powered command processing"""
    
    def __init__(self, basic_processor: VoiceCommandProcessor):
        """Initialize with basic processor for fallback"""
        self.basic_processor = basic_processor
        self.logger = logging.getLogger(__name__)
        
        # Future: Initialize NLP models, AI services, etc.
        self.nlp_enabled = False
    
    def process_command(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process command with advanced NLP (future implementation)"""
        # For now, fallback to basic pattern matching
        return self.basic_processor.process_command(text)
    
    def train_on_usage(self, command: str, result: Dict[str, Any]) -> None:
        """Learn from command usage (future implementation)"""
        pass
    
    def get_contextual_suggestions(self, context: Dict[str, Any]) -> List[str]:
        """Get contextual command suggestions (future implementation)"""
        return self.basic_processor._get_command_suggestions()
