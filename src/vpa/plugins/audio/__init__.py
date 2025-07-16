"""
VPA Audio System Plugin
Provides comprehensive voice management and TTS capabilities using pyttsx3.
"""

from .engine import AudioEngine, VoiceInfo
from .commands import VoiceCommandProcessor, CommandIntent, VoiceCommand

__all__ = ["AudioEngine", "VoiceInfo", "VoiceCommandProcessor", "CommandIntent", "VoiceCommand"]


class AudioPlugin:
    """Main audio plugin class for VPA integration"""
    
    def __init__(self, event_bus, config=None):
        """Initialize the audio plugin"""
        self.event_bus = event_bus
        self.config = config or {}
        
        # Initialize audio engine
        self.audio_engine = AudioEngine(event_bus, config)
        
        # Initialize command processor
        self.command_processor = VoiceCommandProcessor(self.audio_engine)
        
        # Register plugin with event bus
        self._register_plugin_events()
    
    def _register_plugin_events(self):
        """Register plugin-specific events"""
        # Register for plugin lifecycle events
        self.event_bus.subscribe("plugin.audio.command", self._handle_audio_command)
        self.event_bus.subscribe("plugin.audio.test", self._handle_test_request)
    
    def _handle_audio_command(self, data):
        """Handle audio command requests"""
        command_text = data.get('command', '')
        if command_text:
            result = self.command_processor.process_command(command_text)
            self.event_bus.emit("plugin.audio.command.result", result)
    
    def _handle_test_request(self, data=None):
        """Handle audio test requests"""
        if self.audio_engine.current_voice:
            test_text = "VPA Audio System is working correctly."
            self.audio_engine.speak(test_text)
    
    def cleanup(self):
        """Clean up plugin resources"""
        if hasattr(self, 'audio_engine'):
            self.audio_engine.cleanup()


# Plugin factory function for VPA plugin system
def initialize(event_bus, config=None):
    """Initialize the audio plugin"""
    return AudioPlugin(event_bus, config)
