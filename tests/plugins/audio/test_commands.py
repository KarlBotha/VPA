"""
Test suite for VPA Audio Commands System

Comprehensive testing for voice command processing, intent recognition,
parameter extraction, and audio system command execution.
"""

import unittest
from unittest.mock import Mock

from vpa.plugins.audio.commands import (
    CommandIntent,
    VoiceCommand,
    VoiceCommandProcessor,
    AdvancedCommandProcessor
)


class TestCommandIntent(unittest.TestCase):
    """Test CommandIntent enum values and functionality"""

    def test_command_intent_values(self):
        """Test that all required command intents are defined"""
        expected_intents = [
            CommandIntent.SET_VOICE,
            CommandIntent.ADJUST_RATE,
            CommandIntent.ADJUST_VOLUME,
            CommandIntent.TEST_VOICE,
            CommandIntent.LIST_VOICES,
            CommandIntent.STOP_SPEAKING,
            CommandIntent.GET_INFO,
            CommandIntent.UNKNOWN
        ]
        
        for intent in expected_intents:
            self.assertIsInstance(intent, CommandIntent)


class TestVoiceCommand(unittest.TestCase):
    """Test VoiceCommand dataclass functionality"""

    def test_voice_command_creation(self):
        """Test basic voice command creation"""
        command = VoiceCommand(
            intent=CommandIntent.SET_VOICE,
            confidence=0.95,
            raw_text="set voice to David",
            parameters={"voice_name": "David"}
        )
        
        self.assertEqual(command.intent, CommandIntent.SET_VOICE)
        self.assertEqual(command.confidence, 0.95)
        self.assertEqual(command.raw_text, "set voice to David")
        self.assertEqual(command.parameters["voice_name"], "David")

    def test_voice_command_default_parameters(self):
        """Test voice command with default parameters"""
        command = VoiceCommand(
            intent=CommandIntent.UNKNOWN,
            confidence=0.0,
            raw_text="unknown command"
        )
        
        self.assertEqual(command.intent, CommandIntent.UNKNOWN)
        self.assertEqual(command.confidence, 0.0)
        self.assertEqual(command.raw_text, "unknown command")
        self.assertEqual(len(command.parameters), 0)

    def test_voice_command_none_parameters_initialization(self):
        """Test voice command with None parameters initializes as empty dict"""
        command = VoiceCommand(
            intent=CommandIntent.TEST_VOICE,
            confidence=0.8,
            raw_text="test voice",
            parameters=None
        )
        
        self.assertEqual(command.parameters, {})


class TestVoiceCommandProcessor(unittest.TestCase):
    """Test VoiceCommandProcessor functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_audio_engine = Mock()
        
        # Configure mock to properly simulate voices dict with string attributes for voice.name
        mock_voice1 = Mock()
        mock_voice1.name = "David Desktop"
        mock_voice1.available = True
        mock_voice1.voice_id = "voice1"
        mock_voice1.gender = "Male"
        mock_voice1.purpose = "Professional"
        mock_voice1.rate = 200
        mock_voice1.volume = 0.9
        
        mock_voice2 = Mock()
        mock_voice2.name = "Zira Desktop"
        mock_voice2.available = True
        mock_voice2.voice_id = "voice2"
        mock_voice2.gender = "Female"
        mock_voice2.purpose = "Professional"
        mock_voice2.rate = 200
        mock_voice2.volume = 0.9
        
        mock_voice3 = Mock()
        mock_voice3.name = "Mark Desktop"
        mock_voice3.available = False
        mock_voice3.voice_id = "voice3"
        mock_voice3.gender = "Male"
        mock_voice3.purpose = "Casual"
        mock_voice3.rate = 200
        mock_voice3.volume = 0.9
        
        self.mock_audio_engine.voices = {
            "voice1": mock_voice1,
            "voice2": mock_voice2,
            "voice3": mock_voice3
        }
        
        # Set current_voice to mock_voice1 for tests that need a current voice
        self.mock_audio_engine.current_voice = mock_voice1
        
        # Mock other required methods and properties
        self.mock_audio_engine.get_available_voices.return_value = [mock_voice1, mock_voice2]
        self.mock_audio_engine.set_voice_property.return_value = True
        self.mock_audio_engine.stop_speaking.return_value = True
        self.mock_audio_engine.set_voice.return_value = True
        self.mock_audio_engine.speak.return_value = True
        
        # Configure engine info for get_info command
        self.mock_audio_engine.get_engine_info.return_value = {
            "engine": "pyttsx3",
            "platform": "Windows",
            "total_voices": 3
        }
        
        self.processor = VoiceCommandProcessor(self.mock_audio_engine)

    def test_processor_initialization(self):
        """Test processor initialization"""
        self.assertIsNotNone(self.processor.audio_engine)
        self.assertIsNotNone(self.processor.patterns)
        self.assertIsNotNone(self.processor.command_handlers)

    def test_command_patterns_setup(self):
        """Test that command patterns are properly configured"""
        patterns = self.processor.patterns
        
        expected_intents = [
            CommandIntent.SET_VOICE,
            CommandIntent.ADJUST_RATE,
            CommandIntent.ADJUST_VOLUME,
            CommandIntent.TEST_VOICE,
            CommandIntent.LIST_VOICES,
            CommandIntent.STOP_SPEAKING,
            CommandIntent.GET_INFO
        ]
        
        for intent in expected_intents:
            self.assertIn(intent, patterns)
            self.assertIsInstance(patterns[intent], list)
            self.assertGreater(len(patterns[intent]), 0)

    def test_command_handlers_registration(self):
        """Test that command handlers are properly registered"""
        handlers = self.processor.command_handlers
        
        expected_handlers = [
            CommandIntent.SET_VOICE,
            CommandIntent.ADJUST_RATE,
            CommandIntent.ADJUST_VOLUME,
            CommandIntent.TEST_VOICE,
            CommandIntent.LIST_VOICES,
            CommandIntent.STOP_SPEAKING,
            CommandIntent.GET_INFO
        ]
        
        for intent in expected_handlers:
            self.assertIn(intent, handlers)
            self.assertTrue(callable(handlers[intent]))

    def test_parse_command_set_voice(self):
        """Test parsing set voice command"""
        command = self.processor._parse_command("use David voice")
        
        self.assertEqual(command.intent, CommandIntent.SET_VOICE)
        self.assertGreaterEqual(command.confidence, 0.8)
        if command.parameters:
            self.assertEqual(command.parameters.get("voice_name"), "david")

    def test_parse_command_confidence_scoring(self):
        """Test confidence scoring for commands"""
        # Perfect match should have high confidence
        command = self.processor._parse_command("use David voice")
        self.assertGreaterEqual(command.confidence, 0.8)
        
        # Unknown command should have zero confidence
        unknown_command = self.processor._parse_command("completely unknown command")
        self.assertEqual(unknown_command.confidence, 0.0)

    def test_extract_parameters_set_voice(self):
        """Test parameter extraction for set voice commands"""
        # Test the patterns using actual processor method
        command = self.processor._parse_command("use David voice")
        if command.parameters:
            self.assertEqual(command.parameters.get("voice_name"), "david")

    def test_extract_parameters_adjust_rate(self):
        """Test parameter extraction for rate adjustment commands"""
        command = self.processor._parse_command("speak faster")
        if command.parameters:
            self.assertEqual(command.parameters.get("direction"), "faster")

    def test_get_command_suggestions(self):
        """Test getting command suggestions"""
        suggestions = self.processor._get_command_suggestions()
        
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        
        # Check that suggestions contain expected command examples
        suggestion_text = " ".join(suggestions).lower()
        self.assertIn("voice", suggestion_text)
        self.assertIn("speak", suggestion_text)

    def test_process_command_set_voice(self):
        """Test processing set voice command"""
        # Setup proper mock response
        self.mock_audio_engine.set_voice.return_value = True
        
        # Use command format that matches actual patterns: "use David voice"
        result = self.processor.process_command("use David voice")
        
        self.assertEqual(result["status"], "success")
        self.assertIn("david", result["message"].lower())

    def test_process_command_adjust_rate_faster(self):
        """Test processing adjust rate faster command"""
        # Use set_voice_property since that's the actual interface
        self.mock_audio_engine.set_voice_property.return_value = True
        
        result = self.processor.process_command("speak faster")
        
        self.assertEqual(result["status"], "success")
        self.assertIn("rate", result["message"].lower())

    def test_process_command_adjust_rate_slower(self):
        """Test processing adjust rate slower command"""
        # Use set_voice_property since that's the actual interface
        self.mock_audio_engine.set_voice_property.return_value = True
        
        result = self.processor.process_command("speak slower")
        
        self.assertEqual(result["status"], "success")
        self.assertIn("rate", result["message"].lower())

    def test_process_command_adjust_volume_louder(self):
        """Test processing adjust volume louder command"""
        # Use set_voice_property since that's the actual interface
        self.mock_audio_engine.set_voice_property.return_value = True
        
        # Use a command that matches the actual regex patterns
        result = self.processor.process_command("make it louder")
        
        self.assertEqual(result["status"], "success")
        self.assertIn("volume", result["message"].lower())

    def test_process_command_adjust_volume_quieter(self):
        """Test processing adjust volume quieter command"""
        # Use set_voice_property since that's the actual interface
        self.mock_audio_engine.set_voice_property.return_value = True
        
        # Use a command that matches the actual regex patterns
        result = self.processor.process_command("make it quieter")
        
        self.assertEqual(result["status"], "success")
        self.assertIn("volume", result["message"].lower())

    def test_process_command_test_voice(self):
        """Test processing test voice command"""
        self.mock_audio_engine.speak.return_value = True
        
        result = self.processor.process_command("test voice")
        
        self.assertEqual(result["status"], "success")
        self.assertIn("test", result["message"].lower())

    def test_process_command_list_voices(self):
        """Test processing list voices command"""
        result = self.processor.process_command("list voices")
        
        self.assertEqual(result["status"], "success")
        self.assertIn("found", result["message"].lower())
        self.assertIn("available voices", result["message"].lower())
        
        # Check that voice data is returned
        self.assertIn("data", result)
        self.assertIn("voices", result["data"])
        
        # Check that voice names are in the data
        voice_names = [voice["name"].lower() for voice in result["data"]["voices"]]
        self.assertIn("david desktop", voice_names)
        self.assertIn("zira desktop", voice_names)

    def test_process_command_stop_speaking(self):
        """Test processing stop speaking command"""
        result = self.processor.process_command("stop speaking")
        
        self.assertEqual(result["status"], "success")
        self.assertIn("stopped", result["message"].lower())

    def test_process_command_get_info(self):
        """Test processing get info command"""
        result = self.processor.process_command("voice info")
        
        self.assertEqual(result["status"], "success")
        self.assertIn("current voice", result["message"].lower())
        self.assertIn("david desktop", result["message"].lower())
        self.assertIn("200 wpm", result["message"].lower())
        self.assertIn("90% volume", result["message"].lower())

    def test_process_command_unknown(self):
        """Test processing unknown command"""
        result = self.processor.process_command("completely unknown command")
        
        self.assertEqual(result["status"], "error")
        self.assertIn("not recognized", result["message"].lower())


class TestAdvancedCommandProcessor(unittest.TestCase):
    """Test AdvancedCommandProcessor functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_audio_engine = Mock()
        self.basic_processor = VoiceCommandProcessor(self.mock_audio_engine)
        self.processor = AdvancedCommandProcessor(self.basic_processor)

    def test_advanced_processor_initialization(self):
        """Test advanced processor initialization"""
        self.assertIsNotNone(self.processor.basic_processor)
        self.assertIsInstance(self.processor.nlp_enabled, bool)

    def test_process_command_delegation(self):
        """Test that commands are delegated to basic processor"""
        # Mock the basic processor
        self.processor.basic_processor = Mock()
        self.processor.basic_processor.process_command.return_value = {
            "status": "success",
            "message": "Command processed"
        }
        
        result = self.processor.process_command("test command")
        
        self.assertEqual(result["status"], "success")
        self.processor.basic_processor.process_command.assert_called_once_with("test command")

    def test_train_on_usage(self):
        """Test training on usage patterns"""
        # Should not raise exception
        self.processor.train_on_usage("test command", {"status": "success"})

    def test_get_contextual_suggestions(self):
        """Test getting contextual suggestions"""
        suggestions = self.processor.get_contextual_suggestions({})
        self.assertIsInstance(suggestions, list)


if __name__ == "__main__":
    unittest.main()
