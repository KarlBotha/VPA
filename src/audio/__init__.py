"""
VPA Audio System
Neural voice integration with legacy fallback support
"""

# Neural voice system (primary)
from .neural_voice_engine import NeuralVoiceEngine, NeuralVoice
from .vpa_voice_system import VPAVoiceSystem

# Legacy voice system (if needed)
try:
    from .voice_system import VPAVoiceSystem as LegacyVoiceSystem
except ImportError:
    LegacyVoiceSystem = None

# Audio manager
try:
    from .audio_manager import SimplifiedAudioManager
except ImportError:
    SimplifiedAudioManager = None

__all__ = [
    'NeuralVoiceEngine',
    'NeuralVoice', 
    'VPAVoiceSystem',
    'LegacyVoiceSystem',
    'SimplifiedAudioManager'
]
