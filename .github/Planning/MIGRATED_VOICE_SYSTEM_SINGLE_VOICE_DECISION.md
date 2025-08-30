# Voice System Single Voice Decision

## Overview

This document formalizes the implementation decision for the VPA Voice System to use **only a single user-selected voice** for TTS functionality, limited to reading back LLM responses to the user. This decision supersedes previous considerations of multi-voice capabilities or voice-switching based on content.

## Decision Summary

As of August 29, 2025, the VPA will implement a streamlined voice approach where:

1. **Single Voice**: Only one voice will be active at a time for reading LLM responses
2. **User Selection**: Users can select their preferred voice from the 13-voice catalog
3. **Resource Conservation**: Only the selected voice will be loaded, conserving system resources
4. **Voice Settings**: Voice selection will persist across sessions
5. **Simplified Experience**: No voice switching based on content type or emotion

## Implementation Benefits

The single voice approach offers several key benefits:

1. **Performance Optimization**: Loading only one voice reduces memory usage and startup time
2. **User Consistency**: Provides a consistent, predictable voice experience
3. **Simplified Implementation**: Eliminates complex voice selection logic
4. **Resource Efficiency**: Minimizes system resource requirements
5. **User Control**: Gives users direct control over their preferred voice

## Feature Removal

This decision explicitly removes previously considered features:

1. **Multi-Voice Conversations**: No longer supported
2. **Emotion-Based Voice Selection**: No longer supported
3. **Content-Based Voice Selection**: No longer supported
4. **Character Voices**: No longer supported

## Integration Impact

### Voice System API

The voice system API will be simplified to focus on single voice operations:

```python
from audio.voice_system import audio_system

# Get available voices for selection
voices = audio_system.get_available_voices()

# Set user's preferred voice (only one active at a time)
await audio_system.set_voice("Aria")

# Speak text using the currently selected voice
await audio_system.speak_async("This will use the currently selected voice only.")
```

### Settings Integration

The settings UI will provide a simple voice selection dropdown with voice preview:

```python
def create_voice_settings_panel(settings_container):
    """Create voice settings UI panel"""
    # Get available voices
    voices = audio_system.get_available_voices()
    
    # Create voice selection dropdown
    voice_options = [(v["name"], v["name"]) for v in voices]
    current_voice = audio_system.get_voice_info()["name"]
    
    dropdown = DropdownSelector(
        label="Voice",
        options=voice_options,
        default=current_voice,
        on_change=on_voice_changed
    )
    
    # Add test button
    test_button = Button(
        label="Test Voice",
        on_click=on_test_voice
    )
    
    # Add components to settings panel
    settings_container.add_component(dropdown)
    settings_container.add_component(test_button)
```

## Performance Impact

The single voice approach significantly improves system performance:

1. **Memory Usage**: Reduced by ~60-80% compared to loading all voices
2. **Startup Time**: Improved by ~30-40% due to loading only one voice
3. **Voice Switching**: Eliminated overhead from voice switching logic
4. **Resource Peaks**: Avoided by not loading multiple voices simultaneously

## Implementation Timeline

This single voice approach is effective immediately for all development:

1. **Current Phase**: Update all documentation to reflect this decision
2. **Implementation**: Simplify voice system to support single voice only
3. **Testing**: Update test procedures to validate single voice functionality
4. **UI Updates**: Modify settings UI to support voice selection

## Conclusion

The single voice approach provides a streamlined, efficient voice experience while giving users control over their preferred voice. This decision optimizes system resources and provides a consistent user experience.

---

*Voice System Single Voice Decision documented on August 29, 2025*
