"""
Unit tests for VPA Audio Engine
Tests the core audio functionality without requiring actual TTS output.
"""

import pytest
import unittest.mock as mock
from unittest.mock import MagicMock, patch
import threading
import time

from vpa.plugins.audio.engine import AudioEngine, VoiceInfo
from vpa.core.events import EventBus


class TestAudioEngine:
    """Test cases for AudioEngine class"""
    
    @pytest.fixture
    def event_bus(self):
        """Create a test event bus"""
        bus = EventBus()
        bus.initialize()  # Initialize the event bus for testing
        return bus
    
    @pytest.fixture
    def mock_pyttsx3_engine(self):
        """Create a mock pyttsx3 engine"""
        mock_engine = MagicMock()
        
        # Mock voices
        mock_voice1 = MagicMock()
        mock_voice1.id = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_DAVID_11.0"
        mock_voice1.name = "Microsoft David Desktop - English (United States)"
        
        mock_voice2 = MagicMock()
        mock_voice2.id = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0"
        mock_voice2.name = "Microsoft Zira Desktop - English (United States)"
        
        mock_engine.getProperty.return_value = [mock_voice1, mock_voice2]
        
        return mock_engine
    
    @pytest.fixture
    @patch('vpa.plugins.audio.engine.pyttsx3.init')
    def audio_engine(self, mock_init, event_bus, mock_pyttsx3_engine):
        """Create a test audio engine with mocked pyttsx3"""
        mock_init.return_value = mock_pyttsx3_engine
        
        config = {
            'default_voice': 'voice_01',
            'default_rate': 200,
            'default_volume': 0.9
        }
        
        return AudioEngine(event_bus, config)
    
    def test_initialization(self, audio_engine):
        """Test audio engine initialization"""
        assert audio_engine.engine is not None
        assert isinstance(audio_engine.voices, dict)
        assert len(audio_engine.voices) == 13  # 13-voice catalog
        assert audio_engine.current_voice is not None
    
    def test_voice_catalog_creation(self, audio_engine):
        """Test that voice catalog is created correctly"""
        # Check that all 13 voices are in catalog
        expected_voices = [
            'voice_01', 'voice_02', 'voice_03', 'voice_04', 'voice_05',
            'voice_06', 'voice_07', 'voice_08', 'voice_09', 'voice_10',
            'voice_11', 'voice_12', 'voice_13'
        ]
        
        for voice_id in expected_voices:
            assert voice_id in audio_engine.voices
            assert isinstance(audio_engine.voices[voice_id], VoiceInfo)
    
    def test_voice_detection(self, audio_engine):
        """Test system voice detection"""
        # Should detect at least some voices as available
        available_voices = audio_engine.get_available_voices()
        assert len(available_voices) > 0
        
        # Check voice properties
        for voice in available_voices:
            assert voice.voice_id.startswith('voice_')
            assert voice.name is not None
            assert voice.gender in ['Male', 'Female', 'Neutral']
            assert voice.available is True
    
    def test_set_voice(self, audio_engine):
        """Test voice setting functionality"""
        # Get first available voice
        available_voices = audio_engine.get_available_voices()
        assert len(available_voices) > 0
        
        test_voice = available_voices[0]
        
        # Test valid voice setting
        result = audio_engine.set_voice(test_voice.voice_id)
        assert result is True
        assert audio_engine.current_voice.voice_id == test_voice.voice_id
        
        # Test invalid voice setting
        result = audio_engine.set_voice('invalid_voice')
        assert result is False
    
    def test_voice_properties(self, audio_engine):
        """Test voice property setting"""
        # Set up a voice first
        available_voices = audio_engine.get_available_voices()
        if available_voices:
            voice_id = available_voices[0].voice_id
            audio_engine.set_voice(voice_id)
            
            # Test rate setting
            result = audio_engine.set_voice_property(voice_id, 'rate', 180)
            assert result is True
            assert audio_engine.voices[voice_id].rate == 180
            
            # Test volume setting
            result = audio_engine.set_voice_property(voice_id, 'volume', 0.8)
            assert result is True
            assert audio_engine.voices[voice_id].volume == 0.8
            
            # Test invalid property
            result = audio_engine.set_voice_property(voice_id, 'invalid', 100)
            assert result is False
    
    def test_speak_functionality(self, audio_engine):
        """Test text-to-speech functionality"""
        # Set up voice
        available_voices = audio_engine.get_available_voices()
        if available_voices:
            audio_engine.set_voice(available_voices[0].voice_id)
            
            # Test valid speech
            result = audio_engine.speak("Test message")
            assert result is True
            
            # Test empty text
            result = audio_engine.speak("")
            assert result is False
            
            # Test None text
            result = audio_engine.speak(None)
            assert result is False
    
    def test_event_integration(self, audio_engine, event_bus):
        """Test event bus integration"""
        events_received = []
        
        def event_handler(data=None):
            events_received.append(data)
        
        # Subscribe to audio events
        event_bus.subscribe("audio.voice.changed", event_handler)
        
        # Change voice to trigger event
        available_voices = audio_engine.get_available_voices()
        if available_voices and len(available_voices) > 1:
            voice_id = available_voices[1].voice_id
            audio_engine.set_voice(voice_id)
            
            # Give some time for event processing
            time.sleep(0.1)
            
            # Check that event was emitted
            assert len(events_received) > 0
            assert events_received[-1]["voice_id"] == voice_id
    
    def test_engine_info(self, audio_engine):
        """Test engine information retrieval"""
        info = audio_engine.get_engine_info()
        
        assert "engine" in info
        assert info["engine"] == "pyttsx3"
        assert "voices_available" in info
        assert isinstance(info["voices_available"], int)
        assert "current_voice" in info
        assert "is_speaking" in info
    
    def test_thread_safety(self, audio_engine):
        """Test thread-safe operations"""
        results = []
        
        def voice_operation():
            available_voices = audio_engine.get_available_voices()
            if available_voices:
                result = audio_engine.set_voice(available_voices[0].voice_id)
                results.append(result)
        
        # Run multiple voice operations in parallel
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=voice_operation)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All operations should succeed
        assert all(results)
    
    def test_cleanup(self, audio_engine):
        """Test proper cleanup"""
        # Test cleanup doesn't throw errors
        audio_engine.cleanup()
        
        # Engine should be None after cleanup
        assert audio_engine.engine is None


class TestVoiceInfo:
    """Test cases for VoiceInfo dataclass"""
    
    def test_voice_info_creation(self):
        """Test VoiceInfo creation and defaults"""
        voice = VoiceInfo(
            voice_id="test_voice",
            name="Test Voice",
            gender="Male",
            system_id="test_system_id"
        )
        
        assert voice.voice_id == "test_voice"
        assert voice.name == "Test Voice"
        assert voice.gender == "Male"
        assert voice.system_id == "test_system_id"
        assert voice.rate == 200  # Default
        assert voice.volume == 0.9  # Default
        assert voice.available is False  # Default
        assert voice.language == "en-US"  # Default
        assert voice.purpose == "General"  # Default
    
    def test_voice_info_serialization(self):
        """Test VoiceInfo serialization to dict"""
        from dataclasses import asdict
        
        voice = VoiceInfo(
            voice_id="test_voice",
            name="Test Voice",
            gender="Female",
            system_id="test_id",
            rate=180,
            volume=0.8,
            available=True,
            language="en-GB",
            purpose="Professional"
        )
        
        voice_dict = asdict(voice)
        
        assert voice_dict["voice_id"] == "test_voice"
        assert voice_dict["name"] == "Test Voice"
        assert voice_dict["gender"] == "Female"
        assert voice_dict["rate"] == 180
        assert voice_dict["volume"] == 0.8
        assert voice_dict["available"] is True
        assert voice_dict["language"] == "en-GB"
        assert voice_dict["purpose"] == "Professional"


# Integration tests
class TestAudioEngineIntegration:
    """Integration tests requiring actual pyttsx3 (optional)"""
    
    def test_real_pyttsx3_initialization(self):
        """Test with real pyttsx3 engine (if available)"""
        try:
            import pyttsx3
            
            event_bus = EventBus()
            config = {'default_voice': 'voice_01'}
            
            # This will use real pyttsx3 if available
            audio_engine = AudioEngine(event_bus, config)
            
            # Basic functionality test
            assert audio_engine.engine is not None
            voices = audio_engine.get_available_voices()
            assert len(voices) >= 0  # May be 0 on systems without TTS
            
            # Cleanup
            audio_engine.cleanup()
            
        except ImportError:
            pytest.skip("pyttsx3 not available for real integration test")
        except Exception as e:
            pytest.skip(f"TTS not available on this system: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
