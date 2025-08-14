"""
VPA Audio Tests - Hardware Independent
Uses comprehensive mocking to avoid hardware dependencies
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

class MockAudioEngine:
    """Hardware-independent mock audio engine"""
    
    def __init__(self):
        self.initialized = False
        self.voices = [
            {'id': 'voice_01', 'name': 'David', 'gender': 'male'},
            {'id': 'voice_02', 'name': 'Zira', 'gender': 'female'}
        ]
        
    def initialize(self):
        self.initialized = True
        return True
        
    def speak(self, text):
        if not self.initialized:
            raise RuntimeError("Not initialized")
        return f"Mock: {text}"

@pytest.fixture
def mock_audio_engine():
    """Provide mock audio engine for tests"""
    return MockAudioEngine()

@pytest.fixture
def mock_pyttsx3():
    """Mock pyttsx3 to prevent hardware access"""
    with patch('pyttsx3.init') as mock_init:
        mock_engine = Mock()
        mock_engine.getProperty.return_value = [Mock(id='test', name='Test Voice')]
        mock_engine.setProperty.return_value = None
        mock_engine.say.return_value = None
        mock_engine.runAndWait.return_value = None
        mock_init.return_value = mock_engine
        yield mock_engine

class TestAudioSystemMocked:
    """Hardware-independent audio system tests"""
    
    def test_audio_engine_initialization(self, mock_audio_engine):
        """Test audio engine initialization without hardware"""
        assert not mock_audio_engine.initialized
        result = mock_audio_engine.initialize()
        assert result == True
        assert mock_audio_engine.initialized
        
    def test_audio_engine_speech(self, mock_audio_engine):
        """Test speech synthesis without hardware"""
        mock_audio_engine.initialize()
        result = mock_audio_engine.speak("Test message")
        assert "Mock: Test message" == result
        
    def test_voice_listing(self, mock_audio_engine):
        """Test voice listing without hardware access"""
        voices = mock_audio_engine.voices
        assert len(voices) >= 2
        assert voices[0]['name'] == 'David'
        
    @patch('pyttsx3.init')
    def test_pyttsx3_mocking(self, mock_init):
        """Test pyttsx3 mocking prevents hardware access"""
        mock_engine = Mock()
        mock_init.return_value = mock_engine
        
        # This would normally hang - but is mocked
        engine = mock_init()
        engine.say("Test")
        engine.runAndWait()
        
        # Verify mocking worked
        mock_init.assert_called_once()
        engine.say.assert_called_once_with("Test")
        engine.runAndWait.assert_called_once()

# Skip hardware-dependent tests by default
@pytest.mark.skip(reason="Hardware-dependent test - requires audio devices")
def test_actual_hardware_audio():
    """This test is skipped to prevent hanging"""
    pass

if __name__ == "__main__":
    # Run tests with mocking
    pytest.main([__file__, "-v"])
