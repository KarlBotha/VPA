# VPA Audio System Plugin

## Overview

The VPA Audio System provides comprehensive voice management and text-to-speech capabilities using the pyttsx3 engine. It features a 13-voice catalog system, event-driven architecture, and extensible command processing.

## Features

### 🎵 Voice Management
- **13-Voice Catalog**: Curated selection of professional and casual voices
- **Automatic Detection**: Discovers available system voices
- **Smart Mapping**: Maps friendly names to system voice IDs
- **Settings Persistence**: Saves user voice preferences
- **Cross-Platform**: Works on Windows, macOS, and Linux

### 🎙️ Text-to-Speech Engine
- **pyttsx3 Integration**: Reliable, cross-platform TTS
- **Event-Driven**: Integrates with VPA's event bus system
- **Thread-Safe**: Safe concurrent access to voice engine
- **Error Handling**: Graceful fallbacks and error recovery
- **Performance**: Optimized for responsive voice output

### 🗣️ Voice Commands
- **Natural Language**: Process voice control commands
- **Pattern Matching**: Regex-based command recognition
- **Extensible**: Ready for future AI/NLP integration
- **CLI Integration**: Command-line voice testing and control

## Quick Start

### Installation

The audio system requires pyttsx3:

```bash
# Install audio dependencies
pip install pyttsx3>=2.90

# For Windows (enhanced voices)
pip install pywin32>=306

# For Linux (espeak support)
sudo apt-get install espeak espeak-data libespeak1-dev
```

### Basic Usage

```python
from vpa.plugins.audio import AudioEngine
from vpa.core.events import EventBus

# Initialize audio system
event_bus = EventBus()
audio = AudioEngine(event_bus)

# List available voices
voices = audio.get_available_voices()
for voice in voices:
    print(f"{voice.voice_id}: {voice.name} ({voice.gender})")

# Set a voice and speak
audio.set_voice("voice_01")  # David
audio.speak("Hello! VPA Audio System is ready.")

# Adjust voice properties
audio.set_voice_property("voice_01", "rate", 180)
audio.set_voice_property("voice_01", "volume", 0.8)
```

### CLI Commands

```bash
# Test voice system
python -m src.vpa audio speak "Hello World"

# List available voices
python -m src.vpa audio list-voices

# Set voice by name
python -m src.vpa audio set-voice David

# Test current voice
python -m src.vpa audio test
```

## Voice Catalog

The audio system provides a curated 13-voice catalog:

| Voice ID | Name | Gender | Purpose | Provider |
|----------|------|--------|---------|----------|
| voice_01 | David | Male | Professional male | pyttsx3/SAPI |
| voice_02 | Zira | Female | Professional female | pyttsx3/SAPI |
| voice_03 | Mark | Male | Casual male | pyttsx3/SAPI |
| voice_04 | Hazel | Female | Friendly female | pyttsx3/SAPI |
| voice_05 | Helena | Female | Assistant female | pyttsx3/SAPI |
| voice_06 | James | Male | Executive male | pyttsx3/SAPI |
| voice_07 | Catherine | Female | Narrator female | pyttsx3/SAPI |
| voice_08 | Richard | Male | Technical male | pyttsx3/SAPI |
| voice_09 | Eva | Female | Assistant female | pyttsx3/SAPI |
| voice_10 | Sean | Male | Backup male | pyttsx3/SAPI |
| voice_11 | Sabina | Female | Backup female | pyttsx3/SAPI |
| voice_12 | Alex | Male | Fallback male | pyttsx3/Local |
| voice_13 | System | Neutral | System default | OS Default |

## Configuration

### Audio Configuration (config/audio.yaml)

```yaml
audio:
  # Default voice settings
  default_voice: "voice_01"
  default_rate: 200
  default_volume: 0.9
  
  # Engine settings
  engine: "pyttsx3"
  fallback_voice: "voice_13"
  
  # Voice detection
  auto_detect: true
  prefer_sapi: true  # Windows only
  
  # Command processing
  command_confidence_threshold: 0.7
  command_timeout: 5000  # ms
```

### Voice Settings Persistence

User preferences are automatically saved to `config/voice_settings.json`:

```json
{
  "current_voice": "voice_01",
  "voices": {
    "voice_01": {
      "rate": 180,
      "volume": 0.8
    },
    "voice_02": {
      "rate": 200,
      "volume": 0.9
    }
  }
}
```

## Event System Integration

### Events Emitted

- `audio.engine.initialized` - Engine startup complete
- `audio.voices.catalog_created` - Voice catalog ready
- `audio.voice.changed` - Voice selection changed
- `audio.speak.started` - Speech began
- `audio.speak.finished` - Speech completed
- `audio.speak.error` - Speech error occurred

### Events Handled

- `audio.speak` - Speak text request
- `audio.voice.set` - Change voice request
- `audio.voice.stop` - Stop speaking request

### Example Event Usage

```python
# Subscribe to voice events
event_bus.subscribe("audio.voice.changed", on_voice_changed)
event_bus.subscribe("audio.speak.finished", on_speech_done)

# Request speech via events
event_bus.emit("audio.speak", {"text": "Hello World"})

# Change voice via events
event_bus.emit("audio.voice.set", {"voice_id": "voice_02"})
```

## Voice Commands

### Supported Commands

```
Voice Selection:
- "use David voice"
- "switch to female voice"
- "set voice to Zira"

Speech Rate:
- "speak faster"
- "slow down"
- "set rate to 180"

Volume Control:
- "make it louder"
- "turn volume down"
- "set volume to 80%"

Testing & Info:
- "test voice"
- "list voices"
- "voice info"
- "stop speaking"
```

### Command Processing

```python
from vpa.plugins.audio import VoiceCommandProcessor

# Initialize command processor
processor = VoiceCommandProcessor(audio_engine)

# Process natural language commands
result = processor.process_command("use David voice")
print(result["status"])  # "success"
print(result["message"]) # "Voice changed to David"

# Handle command results
if result["status"] == "success":
    print(f"✓ {result['message']}")
else:
    print(f"✗ {result['message']}")
    if "suggestions" in result:
        print("Try:", ", ".join(result["suggestions"]))
```

## Extension Points

### Custom Voice Engines

```python
class CustomTTSEngine:
    def __init__(self, event_bus):
        self.event_bus = event_bus
    
    def speak(self, text):
        # Custom TTS implementation
        pass
    
    def set_voice(self, voice_id):
        # Custom voice selection
        pass

# Register custom engine
audio_engine.register_custom_engine("custom", CustomTTSEngine)
```

### Advanced Command Processing

```python
from vpa.plugins.audio import AdvancedCommandProcessor

# Future: AI-powered command processing
ai_processor = AdvancedCommandProcessor(basic_processor)
result = ai_processor.process_command(
    "Please use a professional female voice for this presentation",
    context={"scenario": "presentation", "audience": "formal"}
)
```

## Troubleshooting

### Common Issues

**No voices detected:**
```bash
# Check system voices
python -c "import pyttsx3; engine = pyttsx3.init(); voices = engine.getProperty('voices'); print([v.name for v in voices])"
```

**Speech not working:**
- Ensure audio output is working
- Check volume settings (both system and VPA)
- Verify pyttsx3 installation
- Test with basic pyttsx3 example

**Voice quality issues:**
- Use SAPI voices on Windows for best quality
- Install additional system voices
- Adjust rate and volume settings

### Platform-Specific Notes

**Windows:**
- Uses SAPI voices for best quality
- Install additional voices via Windows Settings
- Some voices require Microsoft Speech Platform

**macOS:**
- Uses AVSpeechSynthesizer
- Voices available in System Preferences
- Limited voice customization

**Linux:**
- Uses espeak/festival
- Install additional voice packages
- May require ALSA/PulseAudio configuration

## Testing

### Unit Tests

```bash
# Run audio system tests
python -m pytest tests/audio/ -v

# Test with coverage
python -m pytest tests/audio/ --cov=vpa.plugins.audio --cov-report=html
```

### Manual Testing

```bash
# Test basic functionality
python -m src.vpa audio test

# Test voice switching
python -m src.vpa audio set-voice David
python -m src.vpa audio speak "Testing David voice"

# Test command processing
python -m src.vpa audio command "speak faster"
python -m src.vpa audio command "test voice"
```

## Performance

### Optimization Tips

1. **Voice Caching**: Voices are detected once at startup
2. **Thread Safety**: Engine operations are thread-safe
3. **Memory Usage**: Minimal memory footprint
4. **Startup Time**: Fast initialization (< 2 seconds)
5. **Response Time**: Low latency speech output

### Benchmarks

- **Voice Detection**: ~500ms (typical)
- **Voice Switching**: ~100ms
- **Speech Latency**: ~200ms
- **Memory Usage**: ~15MB base + voice data

## Future Enhancements

### Planned Features

- **Neural TTS**: Azure Cognitive Services integration
- **Voice Cloning**: Custom voice training support
- **SSML Support**: Advanced speech markup
- **Real-time Processing**: Streaming TTS capabilities
- **Multi-language**: International voice support

### AI Integration

- **Natural Language**: Advanced command understanding
- **Context Awareness**: Situational voice selection
- **Voice Learning**: Adaptive voice preferences
- **Emotion Detection**: Emotional voice modulation

## Contributing

### Adding New Voices

1. Update voice catalog in `engine.py`
2. Add voice detection patterns
3. Test voice mapping accuracy
4. Update documentation

### Adding Command Types

1. Add new `CommandIntent` enum value
2. Create regex patterns in `commands.py`
3. Implement command handler method
4. Add tests for new commands

### Performance Improvements

1. Profile voice detection speed
2. Optimize engine initialization
3. Reduce memory usage
4. Improve error recovery

## License

This audio system is part of the VPA project and follows the same MIT license terms.
