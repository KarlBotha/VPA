# VPA Component Integration Sequence

This document provides a detailed sequence diagram and explanation of how the VPA components integrate and communicate with each other, addressing the integration sequence gap identified in the assessment report.

## 1. System Startup Sequence

The following sequence diagram illustrates the initialization flow of the VPA application:

```mermaid
sequenceDiagram
    participant Main as main.py
    participant App as App
    participant Config as ConfigManager
    participant EventBus as EventBus
    participant PluginMgr as PluginManager
    participant Audio as AudioSystem
    participant GUI as GUIManager
    
    Main->>App: create App instance
    activate App
    
    App->>Config: load()
    activate Config
    Config-->>App: configuration loaded
    deactivate Config
    
    App->>EventBus: initialize()
    activate EventBus
    EventBus-->>App: event bus ready
    deactivate EventBus
    
    App->>PluginMgr: load_plugins()
    activate PluginMgr
    PluginMgr->>PluginMgr: discover plugins
    PluginMgr->>PluginMgr: load core plugins
    PluginMgr->>PluginMgr: load addon plugins
    PluginMgr-->>App: plugins loaded
    deactivate PluginMgr
    
    App->>Audio: initialize()
    activate Audio
    Audio->>Audio: verify_voice_catalog()
    Audio-->>App: audio system ready
    deactivate Audio
    
    App->>App: emit app.phase1.complete
    
    App->>GUI: initialize()
    activate GUI
    GUI->>GUI: setup windows
    GUI->>GUI: connect to event_bus
    GUI-->>App: GUI ready
    deactivate GUI
    
    App->>App: emit app.phase2.complete
    App->>App: emit app.startup.complete
    
    Main->>App: await run()
    App-->>Main: running main event loop
```

## 2. Event Communication Flow

This sequence diagram shows how events flow through the system when a user interacts with the application:

```mermaid
sequenceDiagram
    participant User
    participant GUI as GUI Components
    participant EventBus as Event Bus
    participant Plugins as Plugin Manager
    participant Audio as Audio System
    
    User->>GUI: inputs text/voice
    GUI->>EventBus: emit "user_input" event
    
    EventBus->>Plugins: dispatch to handlers
    activate Plugins
    Plugins->>Plugins: find plugin that can handle
    Plugins->>EventBus: emit "processing_started"
    
    Plugins->>Plugins: process input
    Plugins->>EventBus: emit "response_ready" with text
    deactivate Plugins
    
    EventBus->>GUI: update display with response
    EventBus->>Audio: synthesize speech
    activate Audio
    Audio->>Audio: generate TTS audio
    Audio->>Audio: play audio
    Audio->>EventBus: emit "speech_complete"
    deactivate Audio
    
    EventBus->>GUI: update status
    GUI->>User: display complete/ready for next input
```

## 3. Plugin Registration and Discovery

This sequence illustrates how plugins are registered and discovered at runtime:

```mermaid
sequenceDiagram
    participant App as App
    participant PluginMgr as Plugin Manager
    participant Cache as Plugin Cache
    participant FS as File System
    participant Plugin as Plugin Module
    
    App->>PluginMgr: load_plugins()
    activate PluginMgr
    
    PluginMgr->>Cache: check plugin_cache.json
    Cache-->>PluginMgr: cache data (if exists)
    
    alt Cache exists and is valid
        PluginMgr->>PluginMgr: load plugins from cache
    else Cache missing or invalid
        PluginMgr->>FS: scan plugins directories
        FS-->>PluginMgr: plugin file paths
        
        loop For each plugin file
            PluginMgr->>Plugin: import module
            Plugin-->>PluginMgr: module loaded
            PluginMgr->>Plugin: instantiate Plugin class
            Plugin-->>PluginMgr: plugin instance
        end
        
        PluginMgr->>Cache: update plugin_cache.json
    end
    
    PluginMgr->>PluginMgr: sort by priority
    PluginMgr->>PluginMgr: resolve dependencies
    
    loop For each valid plugin
        PluginMgr->>Plugin: initialize()
        Plugin-->>PluginMgr: initialization result
    end
    
    PluginMgr-->>App: plugins loaded
    deactivate PluginMgr
```

## 4. Voice System Integration

This sequence demonstrates how the voice system integrates with other components:

```mermaid
sequenceDiagram
    participant EventBus as Event Bus
    participant VoiceSystem as Voice System
    participant EdgeTTS as Edge-TTS
    participant SAPI as Windows SAPI
    participant AudioPlayer as Audio Playback
    
    EventBus->>VoiceSystem: emit "synthesize_speech" with text
    activate VoiceSystem
    
    VoiceSystem->>VoiceSystem: select voice
    
    alt Edge-TTS Available
        VoiceSystem->>EdgeTTS: generate speech
        EdgeTTS-->>VoiceSystem: audio data
    else Edge-TTS Not Available
        VoiceSystem->>SAPI: generate speech
        SAPI-->>VoiceSystem: audio data
    end
    
    VoiceSystem->>AudioPlayer: play audio
    activate AudioPlayer
    AudioPlayer-->>VoiceSystem: playback started
    deactivate AudioPlayer
    
    VoiceSystem->>EventBus: emit "speech_started"
    
    AudioPlayer-->>VoiceSystem: playback completed
    
    VoiceSystem->>EventBus: emit "speech_completed"
    deactivate VoiceSystem
```

## 5. Component Dependency Graph

The following diagram illustrates the dependencies between major components:

```mermaid
graph TD
    Main[main.py] --> App
    App --> EventBus
    App --> PluginManager
    App --> ConfigManager
    App --> AudioSystem
    App --> GUIManager
    
    EventBus --> ErrorHandler
    
    PluginManager --> EventBus
    PluginManager --> ConfigManager
    
    AudioSystem --> EventBus
    AudioSystem --> ConfigManager
    
    GUIManager --> EventBus
    GUIManager --> AudioSystem
    GUIManager --> PluginManager
    
    CorePlugins --> PluginManager
    CorePlugins --> EventBus
    
    AddonPlugins --> PluginManager
    AddonPlugins --> EventBus
    
    LLMAdapter --> EventBus
    LLMAdapter --> ConfigManager
```

## 6. Error Handling and Recovery Flow

This sequence demonstrates how errors are handled across components:

```mermaid
sequenceDiagram
    participant Component
    participant EventBus as Event Bus
    participant ErrorHandler as Error Handler
    participant Logger as Logger
    participant App as App
    
    Component->>Component: Error occurs
    
    alt Non-critical error
        Component->>Logger: log error
        Component->>EventBus: emit "error" event
        EventBus->>ErrorHandler: handle error
        ErrorHandler->>EventBus: emit "error_handled"
    else Critical error
        Component->>Logger: log critical error
        Component->>EventBus: emit "critical_error" event
        EventBus->>App: handle critical error
        App->>App: initiate graceful degradation
        App->>EventBus: emit "component_disabled" event
    end
```

## 7. Plugin Event Communication Pattern

This diagram shows how plugins communicate with the system and each other:

```mermaid
sequenceDiagram
    participant User
    participant GUI as GUI
    participant EventBus as Event Bus
    participant PluginA as Plugin A
    participant PluginB as Plugin B
    
    User->>GUI: input "weather tomorrow"
    GUI->>EventBus: emit "user_input" with text
    
    EventBus->>PluginA: handle "user_input"
    activate PluginA
    PluginA->>PluginA: can_handle() -> false
    PluginA-->>EventBus: not handled
    deactivate PluginA
    
    EventBus->>PluginB: handle "user_input"
    activate PluginB
    PluginB->>PluginB: can_handle() -> true
    PluginB->>EventBus: emit "processing_started"
    
    PluginB->>EventBus: emit "plugin_data_request"
    EventBus->>PluginA: handle "plugin_data_request" 
    PluginA->>EventBus: emit "plugin_data_response"
    EventBus->>PluginB: handle "plugin_data_response"
    
    PluginB->>EventBus: emit "response_ready" with result
    deactivate PluginB
    
    EventBus->>GUI: update with response
    GUI->>User: display weather forecast
```

## 8. Integration with Windows OS Services

This sequence shows how the VPA integrates with Windows OS services:

```mermaid
sequenceDiagram
    participant App as App
    participant WinService as Windows Service
    participant SysTray as System Tray
    participant Notifications as Toast Notifications
    participant Registry as Windows Registry
    
    App->>WinService: initialize Windows integration
    activate WinService
    
    WinService->>SysTray: create system tray icon
    SysTray-->>WinService: icon created
    
    WinService->>Notifications: setup notification channel
    Notifications-->>WinService: channel ready
    
    WinService->>Registry: read saved settings
    Registry-->>WinService: settings loaded
    
    WinService-->>App: Windows services initialized
    deactivate WinService
    
    Note over App,WinService: Later during operation
    
    App->>WinService: show notification
    WinService->>Notifications: display toast
    
    App->>WinService: update tray icon
    WinService->>SysTray: change icon/tooltip
    
    App->>WinService: save user setting
    WinService->>Registry: write setting value
```

## 9. LLM Integration Flow

This sequence shows the integration flow with Language Models:

```mermaid
sequenceDiagram
    participant App as App
    participant EventBus as Event Bus
    participant LLMManager as LLM Manager
    participant LLMAdapter as LLM Adapter
    participant ModelBackend as Model Backend
    
    App->>EventBus: emit "llm_request"
    EventBus->>LLMManager: handle "llm_request"
    activate LLMManager
    
    LLMManager->>LLMAdapter: process_prompt()
    activate LLMAdapter
    
    LLMAdapter->>ModelBackend: generate_response()
    activate ModelBackend
    ModelBackend-->>LLMAdapter: model response
    deactivate ModelBackend
    
    LLMAdapter-->>LLMManager: processed response
    deactivate LLMAdapter
    
    LLMManager->>EventBus: emit "llm_response"
    deactivate LLMManager
    
    EventBus->>App: handle "llm_response"
```

## 10. Integration Points Summary

| Component | Integration Points | Events Emitted | Events Subscribed |
|-----------|-------------------|----------------|-------------------|
| **App** | EventBus, PluginManager, ConfigManager | app.startup.complete, app.startup.failed, app.stopping, app.stopped | system_tray.exit |
| **EventBus** | All components | N/A (transport only) | All events |
| **PluginManager** | EventBus, Plugins | plugin.loaded, plugin.unloaded | app.startup.complete |
| **AudioSystem** | EventBus | speech_started, speech_completed | synthesize_speech |
| **GUIManager** | EventBus | user_input, gui.ready | response_ready, speech_completed |
| **Plugins** | EventBus, PluginManager | response_ready, plugin.data_* | user_input, plugin.data_* |
| **LLMManager** | EventBus, LLMAdapter | llm_response | llm_request |
| **WindowsServices** | EventBus, OS Services | notification.shown, registry.updated | system_tray.action |

---

*Document created: August 29, 2025*
