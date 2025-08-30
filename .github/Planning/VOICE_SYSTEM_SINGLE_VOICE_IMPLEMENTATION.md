# [DEPRECATED] Voice System Single Voice Implementation

## ⚠️ DEPRECATION NOTICE

This document has been moved to its proper location according to VPA architecture standards.

**Please use the updated version at: [docs/voice/requirements/VOICE_SYSTEM_SINGLE_VOICE_IMPLEMENTATION.md](docs/voice/requirements/VOICE_SYSTEM_SINGLE_VOICE_IMPLEMENTATION.md)**

This file is maintained temporarily for reference but will be removed in a future update.

---

## Overview

This document outlines the requirements, implementation approach, and testing procedures for the VPA voice system's single voice approach. Based on project decisions, the VPA will only use a single user-selected voice for TTS functionality, limited to reading back LLM responses to the user.

## Table of Contents

1. [Requirements](#1-requirements)
2. [Implementation Approach](#2-implementation-approach)
3. [Voice Selection](#3-voice-selection)
4. [Integration Points](#4-integration-points)
5. [Performance Considerations](#5-performance-considerations)
6. [Testing Requirements](#6-testing-requirements)
7. [Removed Functionality](#7-removed-functionality)

## 1. Requirements

### 1.1 Core Requirements

- **SV-01**: The system SHALL provide TTS functionality using only a single user-selected voice
- **SV-02**: The system SHALL only use TTS to read LLM responses back to the user
- **SV-03**: The system SHALL allow users to select their preferred voice from the 13-voice catalog
- **SV-04**: The system SHALL persist user voice selection across sessions
- **SV-05**: The system SHALL provide an option to enable/disable voice playback

### 1.2 Voice Behavior

- **SV-06**: The system SHALL speak the complete LLM response in the selected voice
- **SV-07**: The system SHALL NOT use multiple voices for response playback
- **SV-08**: The system SHALL maintain consistent voice characteristics throughout response
- **SV-09**: The system SHALL NOT modify voice based on content emotion or context
- **SV-10**: The system SHALL support voice stop/interrupt functionality

### 1.3 User Control

- **SV-11**: The system SHALL allow users to change voice selection at any time
- **SV-12**: The system SHALL provide a voice test function for each available voice
- **SV-13**: The system SHALL allow users to adjust voice volume
- **SV-14**: The system SHALL allow users to toggle voice playback on/off globally
- **SV-15**: The system SHALL remember voice playback state (on/off) between sessions

## 2. Implementation Approach

The system will implement the single voice approach through a simplified version of the voice system:

```python
class VoiceSystem:
    """Single voice system for VPA TTS functionality"""
    
    def __init__(self):
        self.voice_catalog = []  # List of available voices
        self.current_voice = None  # Currently selected voice
        self.is_enabled = False  # Voice playback enabled state
        self.provider = None  # TTS provider (Edge TTS)
        self.fallback_provider = None  # Fallback provider (SAPI)
        
    async def initialize(self):
        """Initialize the voice system"""
        try:
            # Initialize Edge TTS provider
            self.provider = EdgeTTSProvider()
            await self.provider.initialize()
            
            # Initialize fallback provider
            self.fallback_provider = SAPIProvider()
            await self.fallback_provider.initialize()
            
            # Load voice catalog
            self.voice_catalog = self._build_voice_catalog()
            
            # Load user preferences
            await self._load_user_preferences()
            
            return True
        except Exception as e:
            logging.error(f"Voice system initialization failed: {e}")
            return False
    
    async def speak_text(self, text):
        """Speak text using the selected voice"""
        # Check if voice playback is enabled
        if not self.is_enabled:
            return False
            
        # Ensure we have a voice selected
        if not self.current_voice:
            self.current_voice = self._get_default_voice()
            
        try:
            # Use primary provider
            result = await self.provider.synthesize_speech(
                text,
                self.current_voice["voice_id"]
            )
            
            if not result:
                # Try fallback provider
                result = await self.fallback_provider.synthesize_speech(
                    text,
                    "system"
                )
                
            return result is not None
        except Exception as e:
            logging.error(f"Speech synthesis failed: {e}")
            return False
    
    def set_voice(self, voice_name):
        """Set the current voice by name"""
        for voice in self.voice_catalog:
            if voice["name"] == voice_name:
                self.current_voice = voice
                # Save preference
                self._save_user_preferences()
                return True
        return False
    
    def set_enabled(self, enabled):
        """Enable or disable voice playback"""
        self.is_enabled = enabled
        self._save_user_preferences()
    
    def get_available_voices(self):
        """Get list of available voices"""
        return self.voice_catalog
    
    def get_current_voice(self):
        """Get current voice information"""
        return self.current_voice
    
    def stop_speaking(self):
        """Stop current speech"""
        try:
            self.provider.stop()
            self.fallback_provider.stop()
            return True
        except:
            return False
    
    # Private methods
    def _build_voice_catalog(self):
        """Build the voice catalog"""
        # Implementation as specified in AUDIO_VOICE_SYSTEM_REQUIREMENTS.md
        return [...]
    
    def _get_default_voice(self):
        """Get default voice (Aria)"""
        for voice in self.voice_catalog:
            if voice["name"] == "Aria":
                return voice
        return self.voice_catalog[0] if self.voice_catalog else None
    
    async def _load_user_preferences(self):
        """Load user preferences for voice"""
        try:
            from vpa.core.settings import settings
            
            # Load voice selection
            voice_name = settings.get("voice.selected_voice", "Aria")
            self.set_voice(voice_name)
            
            # Load enabled state
            self.is_enabled = settings.get("voice.enabled", False)
        except Exception as e:
            logging.error(f"Failed to load voice preferences: {e}")
    
    def _save_user_preferences(self):
        """Save user preferences for voice"""
        try:
            from vpa.core.settings import settings
            
            # Save voice selection
            if self.current_voice:
                settings.set("voice.selected_voice", self.current_voice["name"])
            
            # Save enabled state
            settings.set("voice.enabled", self.is_enabled)
        except Exception as e:
            logging.error(f"Failed to save voice preferences: {e}")
```

## 3. Voice Selection

The voice selection will follow these principles:

1. **Default Selection**: "Aria" will be the default voice if no user preference exists
2. **Persistence**: User voice selection will be stored in the application settings
3. **UI Integration**: Voice selection will be available in the settings panel
4. **Testing**: Each voice will have a "Test" button to preview before selection

### 3.1 Voice Selection UI

The voice selection UI will be implemented as follows:

```python
class VoiceSelectionPanel:
    """UI panel for voice selection"""
    
    def __init__(self, parent):
        self.parent = parent
        self.voice_system = audio_system
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up voice selection UI"""
        # Create voice selection dropdown
        self.voice_selector = Dropdown(
            label="Voice",
            options=self._get_voice_options(),
            selected=self.voice_system.get_current_voice()["name"]
        )
        
        # Create test button
        self.test_button = Button(
            label="Test Voice",
            on_click=self._on_test_voice
        )
        
        # Create enable checkbox
        self.enable_checkbox = Checkbox(
            label="Enable voice playback",
            checked=self.voice_system.is_enabled,
            on_change=self._on_toggle_voice
        )
        
        # Layout components
        self.layout = VLayout([
            self.voice_selector,
            HLayout([self.test_button]),
            self.enable_checkbox
        ])
    
    def _get_voice_options(self):
        """Get formatted voice options for dropdown"""
        voices = self.voice_system.get_available_voices()
        return [{"label": v["name"], "value": v["name"]} for v in voices]
    
    def _on_test_voice(self):
        """Handle test button click"""
        selected_voice = self.voice_selector.selected
        
        # Temporarily set selected voice
        original_voice = self.voice_system.get_current_voice()["name"]
        self.voice_system.set_voice(selected_voice)
        
        # Speak test phrase
        test_phrase = f"This is the {selected_voice} voice."
        asyncio.create_task(self.voice_system.speak_text(test_phrase))
        
        # Restore original voice
        self.voice_system.set_voice(original_voice)
    
    def _on_toggle_voice(self, value):
        """Handle voice enable/disable toggle"""
        self.voice_system.set_enabled(value)
    
    def on_selection_changed(self, value):
        """Handle voice selection change"""
        self.voice_system.set_voice(value)
```

## 4. Integration Points

### 4.1 LLM Response Integration

The voice system will integrate with LLM responses through these event handlers:

```python
from vpa.core.events import event_bus

def setup_voice_llm_integration():
    """Set up integration between LLM and voice system"""
    event_bus.subscribe(
        "llm.response.complete",
        on_llm_response,
        async_callback=True
    )

async def on_llm_response(event_data):
    """Handle completed LLM response"""
    from audio.voice_system import audio_system
    
    # Check if we should speak the response
    if not audio_system.is_enabled:
        return
    
    # Get response text
    response_text = event_data.get("response", "")
    if not response_text:
        return
    
    # Speak the response
    await audio_system.speak_text(response_text)
```

### 4.2 Plugin API

Plugins will NOT have direct access to voice functionality except through the standard LLM response flow. This ensures consistency in the voice experience.

### 4.3 Settings Integration

The voice system will integrate with the VPA settings system as follows:

```python
from vpa.core.settings import settings
from vpa.core.events import event_bus

def register_voice_settings():
    """Register voice system settings"""
    event_bus.emit("settings.register_category", {
        "id": "voice",
        "name": "Voice Settings",
        "icon": "microphone",
        "priority": 3
    })
    
    event_bus.emit("settings.register_panel", {
        "category": "voice",
        "id": "voice_selection",
        "name": "Voice Selection",
        "component": "VoiceSelectionPanel",
        "priority": 1
    })
```

## 5. Performance Considerations

### 5.1 Performance Requirements

The single voice implementation shall meet these performance targets:

| Metric | Target |
|--------|--------|
| TTS Response Time | < 2 seconds for typical responses |
| Voice Switching | < 200ms |
| Memory Usage | < 50MB for voice components |
| CPU Usage | < 10% during speech synthesis |

### 5.2 Optimizations

To achieve these targets, the implementation will use these optimizations:

1. **Lazy Initialization**: Only initialize voice system when needed
2. **Resource Cleanup**: Properly dispose of audio resources after playback
3. **Background Processing**: Process TTS in background threads to avoid UI blocking
4. **Error Handling**: Graceful error handling with automatic fallback to text-only

## 6. Testing Requirements

### 6.1 Core Testing

| Test ID | Test Description | Expected Outcome |
|---------|-----------------|------------------|
| SV-T01 | Initialize voice system | System initializes successfully |
| SV-T02 | Set voice by name | Voice changes correctly |
| SV-T03 | Toggle voice enabled state | State toggles correctly |
| SV-T04 | Speak text with voice enabled | Text spoken correctly |
| SV-T05 | Attempt speech with voice disabled | No speech produced |

### 6.2 Integration Testing

| Test ID | Test Description | Expected Outcome |
|---------|-----------------|------------------|
| SV-IT01 | LLM response event triggers speech | Response spoken correctly |
| SV-IT02 | Settings changes persist | Voice selection remembered |
| SV-IT03 | Voice test button works | Test phrase spoken in selected voice |

### 6.3 Performance Testing

| Test ID | Test Description | Expected Outcome |
|---------|-----------------|------------------|
| SV-PT01 | Measure TTS response time | < 2 seconds for typical responses |
| SV-PT02 | Measure voice switching time | < 200ms |
| SV-PT03 | Measure memory usage | < 50MB for voice components |

## 7. Removed Functionality

The following functionality has been explicitly removed from scope:

### 7.1 Multi-Voice Conversations

Multi-voice conversations (using different voices for different parts of content) have been removed. The system will only use a single consistent voice for all TTS playback.

### 7.2 Emotion-Based Voice Selection

Automatic emotion detection and voice selection based on content has been removed. The system will use the user's selected voice regardless of content emotion.

### 7.3 Voice Progress Indicators

Specialized voice progress indicators for long-running operations have been removed. The system will only use voice for LLM response playback.

### 7.4 Voice Character Profiles

The concept of different voice "characters" with distinct personalities has been removed. The system will provide voices with consistent characteristics but without character personas.

## Conclusion

This document establishes the requirements and implementation approach for the VPA's single voice approach. By focusing exclusively on reading LLM responses with a single user-selected voice, the system will deliver a straightforward, consistent, and high-quality voice experience aligned with the project's priorities.

---

*Voice System Single Voice Implementation document created on August 29, 2025*  
*Related Documents: AUDIO_VOICE_SYSTEM_REQUIREMENTS.md (v1.3), VOICE_SYSTEM_DOCUMENTATION_ANALYSIS.md (v1.0)*
