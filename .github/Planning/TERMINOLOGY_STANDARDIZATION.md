# VPA Terminology Standardization and TTS Strategy

## Overview

This document clarifies standard terminology and resolves discrepancies identified in VPA documentation, particularly around plugin architecture terminology and text-to-speech (TTS) technology implementation.

## 1. Plugin Architecture Terminology

### 1.1 Standardized Terms

| Standard Term | Previous Terms | Description |
|---------------|----------------|-------------|
| **Plugin** | Plugin | Base unit of functionality extension, conforming to the VPA plugin interface |
| **Core Plugin** | Core Plugin | Built-in functionality provided with VPA base installation |
| **Extension Plugin** | Addon, Add-on | User-installed plugins that extend VPA functionality |
| **User Plugin** | User Plugin, Custom Plugin | User-created plugins for personalized functionality |

### 1.2 Directory Structure

```
plugins/
├── core_plugins/          # Built-in functionality plugins
├── extension_plugins/     # User-installed extension plugins
└── user_plugins/          # User-created custom plugins
```

### 1.3 Implementation Standard

All plugin types implement the same `Plugin` base class defined in `vpa.core.plugins`, with the only difference being their location and discovery path. All plugins should follow the same lifecycle and interface standards.

## 2. TTS Provider Strategy

### 2.1 TTS Technology Stack

| Component | Provider | Status |
|-----------|----------|--------|
| **Primary TTS Engine** | Edge-TTS | Main neural voice provider |
| **Fallback Engine** | Windows SAPI | Local fallback when Edge-TTS is unavailable |

### 2.2 Implementation Details

The VPA implementation uses **Edge-TTS** as its primary neural voice engine. Edge-TTS provides high-quality neural voices through Microsoft's online service but does not require Azure account setup or API keys. This was selected for ease of implementation and user experience.

Edge-TTS provides:
- Complete 13-voice catalog with neural quality
- No API key requirements
- Simple integration path
- Full range of voice characteristics

### 2.4 Documentation Standardization

All references should use:
- **Edge-TTS** as the current neural voice provider
- **Windows SAPI** as the local fallback mechanism
- **Azure Cognitive Services** only when referring to future premium voice options

## 3. Audio System Terminology

### 3.1 Component Naming

| Standard Term | Previous Terms | Description |
|---------------|----------------|-------------|
| **Audio/Voice System** | Voice System, Audio System, TTS System | The complete audio synthesis and playback component |
| **Voice Catalog** | Voice List, Voices | The collection of 13 available voices |
| **TTS Engine** | Voice Engine, Speech Synthesizer | The underlying technology providing speech synthesis |

### 3.2 Voice vs Audio Clarification

- **Voice**: Refers specifically to the speech synthesis voices/personas
- **Audio**: Refers to the broader system including playback and sound processing

Therefore, "Audio/Voice System" is the correct comprehensive term for the entire component.

## 4. Implementation Guidance

### 4.1 Code References

```python
# Correct plugin references
from vpa.core.plugins import Plugin

# Correct TTS engine references
from vpa.audio.voice_system import audio_system

# Setting voice (correct terminology)
audio_system.set_voice("Aria")  # Primary neural voice through Edge-TTS
```

### 4.2 Directory Structure

```
src/
├── vpa/
│   ├── core/
│   │   ├── plugins.py          # Plugin management
│   │   └── ...
│   └── plugins/                # All plugin types use same base class
│       ├── core_plugins/       # Built-in functionality 
│       ├── extension_plugins/  # User-installed extensions (not "addons")
│       └── user_plugins/       # User-created plugins
└── audio/
    └── voice_system.py        # Audio/Voice System implementation
```

## 5. Documentation Updates

This document serves as the authoritative reference for VPA terminology. All documentation should be aligned with these standards.

---

*Terminology Standardization Document completed on August 27, 2025*
