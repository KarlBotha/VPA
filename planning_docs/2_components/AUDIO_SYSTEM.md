# VPA Audio System Specification

## Overview

The VPA Audio System is responsible for voice synthesis, speech recognition, and audio playback. It provides a high-quality, responsive voice interface with a 13-voice catalog and robust fallback mechanisms. The system is designed for performance, with a target of <2s response time for text-to-speech operations.

## Core Components

### Voice System (`src/audio/voice_system.py`)

The central coordinator for all voice-related functionality.

#### Class Definition

```python
class VPAVoiceSystem:
    """13-voice Edge-TTS system with SAPI fallback."""
    
    def __init__(self, event_bus, config_manager):
        self._event_bus = event_bus
        self._config_manager = config_manager
        self._voice_catalog = None
        self._current_voice_id = "en-US-AriaNeural"  # Default voice
        self._tts_engine = None
        self._sr_engine = None
        self._is_speaking = False
        self._is_listening = False
        
    async def initialize(self) -> bool:
        """Initialize the voice system."""
        try:
            # Initialize voice catalog
            self._voice_catalog = VoiceCatalog(self._config_manager)
            await self._voice_catalog.initialize()
            
            # Initialize TTS engine
            self._tts_engine = EdgeTTSEngine(self._voice_catalog)
            if not await self._tts_engine.initialize():
                # Fallback to SAPI
                self._tts_engine = SAPIEngine(self._voice_catalog)
                await self._tts_engine.initialize()
            
            # Initialize speech recognition
            self._sr_engine = WindowsSpeechRecognition()
            if not await self._sr_engine.initialize():
                # Fallback to Whisper
                self._sr_engine = WhisperSpeechRecognition()
                await self._sr_engine.initialize()
            
            # Subscribe to events
            self._event_bus.subscribe(
                "command.speak", 
                self._handle_speak_command, 
                async_callback=True
            )
            self._event_bus.subscribe(
                "command.listen", 
                self._handle_listen_command, 
                async_callback=True
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize voice system: {e}")
            return False
    
    async def shutdown(self) -> bool:
        """Shut down the voice system."""
        # Implementation...
        
    async def synthesize_speech(self, text: str, voice_id: str = None) -> Dict[str, Any]:
        """Synthesize speech from text."""
        # Implementation with performance monitoring...
        
    async def recognize_speech(self, timeout: int = 5) -> Dict[str, Any]:
        """Recognize speech from microphone."""
        # Implementation...
        
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voices."""
        # Implementation...
        
    def set_voice(self, voice_id: str) -> bool:
        """Set the current voice."""
        # Implementation...
        
    # Additional methods...
```

#### Responsibilities

- Voice synthesis coordination
- Speech recognition management
- Voice catalog management
- Event handling for voice commands
- Performance monitoring and optimization

#### Performance Requirements

- TTS response time: <2s from request to audio start
- Voice switching: <100ms
- Memory footprint: <200MB including voice data
- Speech recognition response: <1.5s from end of speech

### Voice Catalog (`src/audio/voice_catalog.py`)

Manages the 13-voice catalog and voice configuration.

#### Class Definition

```python
class VoiceCatalog:
    """Manager for the 13-voice catalog."""
    
    def __init__(self, config_manager):
        self._config_manager = config_manager
        self._voices = {}
        self._default_voice_id = "en-US-AriaNeural"
        
    async def initialize(self) -> bool:
        """Initialize the voice catalog."""
        # Implementation...
        
    def get_voice_info(self, voice_id: str = None) -> Dict[str, Any]:
        """Get information about a specific voice or the default."""
        # Implementation...
        
    def get_all_voices(self) -> List[Dict[str, Any]]:
        """Get information about all available voices."""
        # Implementation...
        
    def verify_voice(self, voice_id: str) -> bool:
        """Verify if a voice is available."""
        # Implementation...
        
    def get_fallback_voice(self, preferred_gender: str = None) -> str:
        """Get a fallback voice if requested voice is unavailable."""
        # Implementation...
```

#### Voice Catalog Definition

The system provides 13 voices with diverse characteristics:

| Voice Name | Voice ID | Gender | Language | Style |
|------------|----------|--------|----------|-------|
| Aria | en-US-AriaNeural | Female | en-US | Professional |
| Guy | en-US-GuyNeural | Male | en-US | Professional |
| Jenny | en-US-JennyNeural | Female | en-US | Conversational |
| Christopher | en-US-ChristopherNeural | Male | en-US | Conversational |
| Emma | en-US-EmmaNeural | Female | en-US | Cheerful |
| Steffan | en-GB-RyanNeural | Male | en-GB | Professional |
| Michelle | en-AU-NatashaNeural | Female | en-AU | Professional |
| Roger | en-US-RogerNeural | Male | en-US | Serious |
| Ava | en-US-AvaNeutral | Female | en-US | Neutral |
| Eric | en-US-EricNeural | Male | en-US | Friendly |
| Libby | en-GB-LibbyNeural | Female | en-GB | Cheerful |
| Andrew | en-US-AndrewNeural | Male | en-US | Neutral |
| System Voice | system | - | System | System |

### TTS Engines

#### Edge TTS Engine (`src/audio/tts/edge_tts_engine.py`)

Primary TTS engine using Microsoft Edge TTS service.

```python
class EdgeTTSEngine:
    """Microsoft Edge TTS engine implementation."""
    
    async def initialize(self) -> bool:
        """Initialize the Edge TTS engine."""
        # Implementation...
        
    async def synthesize(self, text: str, voice_id: str) -> Dict[str, Any]:
        """Synthesize speech using Edge TTS."""
        # Implementation with performance monitoring...
        
    def is_voice_available(self, voice_id: str) -> bool:
        """Check if a voice is available in Edge TTS."""
        # Implementation...
```

#### SAPI Engine (`src/audio/tts/sapi_engine.py`)

Fallback TTS engine using Windows SAPI.

```python
class SAPIEngine:
    """Windows SAPI TTS engine implementation."""
    
    async def initialize(self) -> bool:
        """Initialize the SAPI engine."""
        # Implementation...
        
    async def synthesize(self, text: str, voice_id: str) -> Dict[str, Any]:
        """Synthesize speech using SAPI."""
        # Implementation...
        
    def is_voice_available(self, voice_id: str) -> bool:
        """Check if a voice is available in SAPI."""
        # Implementation...
```

### Speech Recognition

#### Windows Speech Recognition (`src/audio/recognition/windows_sr.py`)

Primary speech recognition using Windows Speech Recognition API.

```python
class WindowsSpeechRecognition:
    """Windows Speech Recognition implementation."""
    
    async def initialize(self) -> bool:
        """Initialize Windows Speech Recognition."""
        # Implementation...
        
    async def recognize(self, timeout: int = 5) -> Dict[str, Any]:
        """Recognize speech using Windows SR."""
        # Implementation...
        
    def is_available(self) -> bool:
        """Check if Windows Speech Recognition is available."""
        # Implementation...
```

#### Whisper Speech Recognition (`src/audio/recognition/whisper_sr.py`)

Fallback speech recognition using OpenAI Whisper.

```python
class WhisperSpeechRecognition:
    """Whisper Speech Recognition implementation."""
    
    async def initialize(self) -> bool:
        """Initialize Whisper Speech Recognition."""
        # Implementation...
        
    async def recognize(self, timeout: int = 5) -> Dict[str, Any]:
        """Recognize speech using Whisper."""
        # Implementation...
        
    def is_available(self) -> bool:
        """Check if Whisper is available."""
        # Implementation...
```

### Audio Playback (`src/audio/playback.py`)

Handles audio playback using Pygame.

```python
class AudioPlayback:
    """Audio playback system using Pygame."""
    
    def __init__(self):
        self._current_sound = None
        self._is_playing = False
        
    async def initialize(self) -> bool:
        """Initialize the audio playback system."""
        # Implementation...
        
    async def play(self, audio_file: str) -> bool:
        """Play an audio file."""
        # Implementation...
        
    def stop(self) -> bool:
        """Stop currently playing audio."""
        # Implementation...
        
    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        # Implementation...
```

### Audio Utilities (`src/audio/utils/`)

#### File Management (`src/audio/utils/file_manager.py`)

Manages temporary audio files.

```python
class AudioFileManager:
    """Manager for temporary audio files."""
    
    async def create_temp_file(self, suffix: str = ".mp3") -> str:
        """Create a temporary audio file."""
        # Implementation...
        
    async def cleanup_temp_files(self, age_hours: int = 24) -> int:
        """Clean up old temporary files."""
        # Implementation...
```

#### Audio Format Conversion (`src/audio/utils/format_converter.py`)

Handles audio format conversion.

```python
class AudioFormatConverter:
    """Converter for audio formats."""
    
    async def convert(self, input_file: str, output_format: str) -> str:
        """Convert an audio file to another format."""
        # Implementation...
```

## Event Integration

### Emitted Events

| Event Name | Description | Data |
|------------|-------------|------|
| `audio.speech.started` | Speech synthesis started | `{"text": str, "voice_id": str}` |
| `audio.speech.completed` | Speech synthesis completed | `{"text": str, "voice_id": str, "duration_ms": int}` |
| `audio.speech.error` | Speech synthesis error | `{"text": str, "error": str}` |
| `audio.recognition.started` | Speech recognition started | `{"timeout": int}` |
| `audio.recognition.result` | Speech recognition result | `{"text": str, "confidence": float}` |
| `audio.recognition.error` | Speech recognition error | `{"error": str}` |
| `audio.playback.started` | Audio playback started | `{"file": str, "duration": float}` |
| `audio.playback.completed` | Audio playback completed | `{"file": str}` |

### Subscribed Events

| Event Name | Description | Handler |
|------------|-------------|---------|
| `command.speak` | Request to speak text | `_handle_speak_command` |
| `command.listen` | Request to listen for speech | `_handle_listen_command` |
| `command.stop_audio` | Request to stop audio | `_handle_stop_audio_command` |
| `setting.voice_changed` | Voice setting changed | `_handle_voice_changed` |

## Configuration

### Voice Settings Schema

```json
{
  "default_voice": "en-US-AriaNeural",
  "voices": {
    "en-US-AriaNeural": {
      "rate": 0,
      "volume": 1.0,
      "pitch": 0
    },
    "en-US-GuyNeural": {
      "rate": 0,
      "volume": 1.0,
      "pitch": 0
    },
    // Additional voices...
  },
  "speech_recognition": {
    "engine": "windows",
    "timeout": 5,
    "min_confidence": 0.7
  },
  "audio": {
    "output_device": "default",
    "sample_rate": 44100,
    "channels": 2,
    "bit_depth": 16
  }
}
```

### Audio Configuration

- **Sample Rate**: 44.1kHz (CD quality)
- **Bit Depth**: 16-bit
- **Channels**: Stereo (2 channels)
- **Format**: MP3 for storage, WAV for playback

## Performance Optimization

### Response Time Optimization

- **Caching**: Cache frequently used phrases
- **Parallel Processing**: Process audio while sending events
- **Streaming Playback**: Begin playback before full synthesis completes
- **Voice Preloading**: Preload voice data for frequently used voices
- **Efficient File Handling**: Use memory-mapped files where appropriate

### Memory Usage Optimization

- **Temporary File Management**: Clean up files after use
- **Resource Pooling**: Reuse audio resources where possible
- **Lazy Loading**: Load voices only when needed
- **Memory Monitoring**: Track memory usage during operations

## Error Handling

### Error Categories

| Error Type | Handling Strategy |
|------------|-------------------|
| **Voice Not Available** | Fall back to default voice, log error, notify user |
| **TTS Service Failure** | Fall back to SAPI, log error, notify user |
| **Speech Recognition Failure** | Fall back to text input, log error, notify user |
| **Audio Playback Error** | Log error, notify user, attempt alternative playback |
| **File System Error** | Log error, use memory playback if possible |

### Graceful Degradation

The audio system implements graceful degradation at multiple levels:

1. Edge TTS → SAPI fallback for synthesis
2. Windows SR → Whisper fallback for recognition
3. File playback → Memory playback if file system unavailable
4. Specific voice → Default voice if requested voice unavailable
5. Audio output → Text output if audio completely unavailable

## Testing

### Unit Tests

- Test each component in isolation
- Mock dependencies
- Verify correct behavior with various inputs
- Test error handling paths

### Integration Tests

- Test voice synthesis end-to-end
- Test speech recognition with various inputs
- Verify event handling and propagation
- Test fallback mechanisms

### Performance Tests

- Measure TTS response time
- Validate <2s performance target
- Test memory usage under load
- Verify audio quality meets standards

## Dependencies

- **Edge TTS**: 7.0.0+ (Microsoft neural voices)
- **Pygame**: 2.6.0+ (cross-platform audio playback)
- **PyWin32**: Windows API integration for SAPI
- **Whisper**: Optional dependency for fallback speech recognition
- **NumPy**: For audio processing

## Implementation Timeline

| Week | Focus | Deliverables |
|------|-------|--------------|
| 1 | Basic voice synthesis | Edge TTS integration, basic playback |
| 2 | Voice catalog and speech recognition | 13-voice catalog, Windows SR integration |
| 3 | Optimization and fallbacks | Performance optimization, fallback mechanisms |

## See Also

- [Implementation Plan Phase 2: Audio System](../3_implementation_roadmap/PHASE_2_AUDIO_SYSTEM.md)
- [Performance Targets](../1_architecture/PERFORMANCE_TARGETS.md)
- [Event System Design](../1_architecture/EVENT_SYSTEM_DESIGN.md)

---

*Document created: August 29, 2025*  
*Version: 1.0*
