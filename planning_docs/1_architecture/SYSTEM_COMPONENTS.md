# VPA System Components

## Overview

This document details the key system components of the VPA (Virtual Personal Assistant) project, their responsibilities, and interactions. It provides a comprehensive view of all major components that make up the system architecture.

## Component Map

```
┌─────────────────────────────────────────────────────────────┐
│                       Application                           │
│                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌───────────────────┐  │
│  │    Core     │   │    Audio    │   │       GUI         │  │
│  │  Components │   │   System    │   │      System       │  │
│  │             │   │             │   │                   │  │
│  │ ┌─────────┐ │   │ ┌─────────┐ │   │ ┌───────────────┐ │  │
│  │ │Event Bus│ │   │ │  Voice  │ │   │ │ Main Window  │ │  │
│  │ └─────────┘ │   │ │ System  │ │   │ └───────────────┘ │  │
│  │ ┌─────────┐ │   │ └─────────┘ │   │ ┌───────────────┐ │  │
│  │ │  App    │ │   │ ┌─────────┐ │   │ │Chat Interface│ │  │
│  │ │ Manager │ │   │ │ Speech  │ │   │ └───────────────┘ │  │
│  │ └─────────┘ │   │ │   Rec   │ │   │ ┌───────────────┐ │  │
│  │ ┌─────────┐ │   │ └─────────┘ │   │ │   Settings    │ │  │
│  │ │ Plugin  │ │   │ ┌─────────┐ │   │ └───────────────┘ │  │
│  │ │ Manager │ │   │ │ Audio   │ │   │ ┌───────────────┐ │  │
│  │ └─────────┘ │   │ │Playback │ │   │ │  Theme Mgr    │ │  │
│  │ ┌─────────┐ │   │ └─────────┘ │   │ └───────────────┘ │  │
│  │ │ Config  │ │   │             │   │                   │  │
│  │ │ Manager │ │   │             │   │                   │  │
│  │ └─────────┘ │   │             │   │                   │  │
│  └─────────────┘   └─────────────┘   └───────────────────┘  │
│                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌───────────────────┐  │
│  │  Windows    │   │    LLM      │   │     Plugin        │  │
│  │Integration  │   │ Integration │   │     System        │  │
│  │             │   │             │   │                   │  │
│  │ ┌─────────┐ │   │ ┌─────────┐ │   │ ┌───────────────┐ │  │
│  │ │ System  │ │   │ │  LLM    │ │   │ │ Core Plugins  │ │  │
│  │ │  Tray   │ │   │ │ Manager │ │   │ └───────────────┘ │  │
│  │ └─────────┘ │   │ └─────────┘ │   │ ┌───────────────┐ │  │
│  │ ┌─────────┐ │   │ ┌─────────┐ │   │ │ Addon Plugins │ │  │
│  │ │Notific- │ │   │ │   LLM   │ │   │ └───────────────┘ │  │
│  │ │ ations  │ │   │ │ Adapters│ │   │ ┌───────────────┐ │  │
│  │ └─────────┘ │   │ └─────────┘ │   │ │  Marketplace  │ │  │
│  │ ┌─────────┐ │   │ ┌─────────┐ │   │ └───────────────┘ │  │
│  │ │ Registry│ │   │ │ Prompt  │ │   │ ┌───────────────┐ │  │
│  │ │ Access  │ │   │ │ System  │ │   │ │Plugin Settings│ │  │
│  │ └─────────┘ │   │ └─────────┘ │   │ └───────────────┘ │  │
│  └─────────────┘   └─────────────┘   └───────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### Event Bus System (`src/vpa/core/events.py`)

#### Purpose
Central communication system enabling zero direct coupling between components.

#### Responsibilities
- Provide subscription mechanism for events
- Dispatch events to appropriate handlers
- Support both synchronous and asynchronous events
- Implement event filtering and middleware
- Monitor performance of event processing
- Ensure error isolation during event handling

#### Key Interfaces
- `subscribe(event_name, handler, async_callback)` - Register handler for events
- `emit(event_name, event_data)` - Synchronously emit an event
- `emit_async(event_name, event_data)` - Asynchronously emit an event
- `add_middleware(middleware_func)` - Add middleware for event processing
- `cleanup()` - Unregister all event handlers

#### Performance Requirements
- Event dispatch time: <10ms for 95th percentile
- Memory overhead: <100 bytes per subscription

### Application Manager (`src/vpa/core/app.py`)

#### Purpose
Manages the application lifecycle and coordinates core components.

#### Responsibilities
- Initialize all system components in correct order
- Manage startup and shutdown sequences
- Monitor system health and performance
- Coordinate component interactions
- Handle global exceptions and errors
- Maintain system state information

#### Key Interfaces
- `startup()` - Initialize and start the application
- `shutdown()` - Gracefully shut down the application
- `get_status()` - Retrieve current system status
- `register_component(component)` - Register a component with the app manager
- `get_component(component_id)` - Retrieve a registered component

#### Performance Requirements
- Startup time: <10s total from launch to ready
- Shutdown time: <3s for clean shutdown
- Status retrieval: <5ms response time

### Plugin Manager (`src/vpa/core/plugins.py`)

#### Purpose
Discovers, loads, and manages plugins to extend system functionality.

#### Responsibilities
- Discover plugins from multiple locations
- Validate plugin compatibility and requirements
- Manage plugin dependencies and load order
- Handle plugin lifecycle (load, initialize, start, stop, unload)
- Isolate plugin errors to prevent system crashes
- Cache plugin information for faster startup

#### Key Interfaces
- `discover_plugins()` - Find available plugins
- `load_plugin(plugin_id)` - Load a specific plugin
- `get_plugin(plugin_id)` - Retrieve a loaded plugin
- `get_all_plugins()` - List all available plugins
- `is_plugin_enabled(plugin_id)` - Check if a plugin is enabled

#### Performance Requirements
- Plugin discovery: <1s total scan time
- Plugin loading: <500ms per plugin
- Cache hit rate: >95% for repeated startups

### Configuration Manager (`src/vpa/core/config.py`)

#### Purpose
Manages application configuration and settings.

#### Responsibilities
- Load configuration from multiple sources
- Validate configuration against schemas
- Provide access to configuration values
- Save configuration changes
- Notify system of configuration changes
- Handle default configurations

#### Key Interfaces
- `load_config()` - Load configuration from files
- `get_value(key, default)` - Get configuration value
- `set_value(key, value)` - Set configuration value
- `save_config()` - Save configuration to disk
- `register_schema(schema)` - Register validation schema

#### Performance Requirements
- Config load time: <200ms
- Config access time: <1ms per lookup
- Config save time: <500ms

### Performance Monitor (`src/vpa/core/performance.py`)

#### Purpose
Tracks and reports on system performance metrics.

#### Responsibilities
- Monitor execution times of critical operations
- Track memory usage across the application
- Validate performance against targets
- Generate performance reports
- Alert on performance anomalies

#### Key Interfaces
- `track_execution_time(function_name)` - Decorator to track function time
- `monitor_memory_usage()` - Begin tracking memory
- `get_performance_metrics()` - Retrieve current metrics
- `check_targets()` - Validate against performance targets

#### Performance Requirements
- Monitoring overhead: <5% of monitored function time
- Memory usage: <10MB for monitoring infrastructure

## Audio System

### Voice System (`src/audio/voice_system.py`)

#### Purpose
Provides text-to-speech capabilities with a 13-voice catalog.

#### Responsibilities
- Manage 13-voice catalog
- Synthesize speech from text
- Select appropriate voices
- Handle voice fallbacks
- Interface with TTS engines
- Optimize for performance

#### Key Interfaces
- `synthesize_speech(text, voice_id)` - Convert text to speech
- `get_available_voices()` - List available voices
- `set_voice(voice_id)` - Set default voice
- `is_speaking()` - Check if currently speaking

#### Performance Requirements
- TTS response time: <2s from request to audio
- Voice switching: <100ms
- Memory footprint: <200MB including voice data

### Speech Recognition (`src/audio/speech_recognition.py`)

#### Purpose
Converts spoken audio to text for processing.

#### Responsibilities
- Capture audio input
- Process speech using recognition engines
- Score confidence of recognition results
- Detect commands in speech
- Handle fallbacks between recognition engines

#### Key Interfaces
- `start_listening()` - Begin speech recognition
- `stop_listening()` - Stop speech recognition
- `is_listening()` - Check if currently listening
- `get_last_recognition()` - Get most recent result

#### Performance Requirements
- Recognition response: <1.5s from speech end
- Confidence scoring: <50ms
- Memory usage: <150MB during recognition

### Audio Playback (`src/audio/playback.py`)

#### Purpose
Handles audio output for voice synthesis and other sounds.

#### Responsibilities
- Play audio files
- Control audio playback
- Manage playback queue
- Handle audio device selection
- Optimize audio for quality and performance

#### Key Interfaces
- `play(audio_file)` - Play audio file
- `stop()` - Stop current playback
- `is_playing()` - Check playback status
- `set_volume(level)` - Adjust volume

#### Performance Requirements
- Playback start: <100ms from request
- Memory usage: <50MB during playback

## GUI System

### Main Window (`src/vpa/gui/main_window.py`)

#### Purpose
Primary application window and container for GUI components.

#### Responsibilities
- Initialize GUI framework
- Manage window layout and components
- Handle window events
- Coordinate with theme system
- Manage window state (maximize, minimize, etc.)

#### Key Interfaces
- `show()` - Display the window
- `hide()` - Hide the window
- `add_component(component)` - Add UI component
- `set_title(title)` - Set window title

#### Performance Requirements
- Window creation: <1s
- Component layout: <200ms
- Response time: <100ms for actions

### Chat Interface (`src/vpa/gui/chat_interface.py`)

#### Purpose
Handles display and interaction with chat messages.

#### Responsibilities
- Display chat messages with appropriate styling
- Handle user text input
- Manage chat history
- Display typing indicators
- Show voice activity status

#### Key Interfaces
- `add_message(message, sender)` - Add chat message
- `clear_history()` - Clear chat history
- `set_typing_indicator(active)` - Show/hide typing status
- `set_voice_indicator(active)` - Show/hide voice activity

#### Performance Requirements
- Message display: <50ms
- History loading: <200ms for 100 messages
- Smooth scrolling: >30fps

### Settings Panel (`src/vpa/gui/settings_panel.py`)

#### Purpose
Provides interface for configuration and preferences.

#### Responsibilities
- Display configuration options
- Validate user input
- Save configuration changes
- Group settings by category
- Handle plugin-specific settings

#### Key Interfaces
- `show_settings()` - Display settings panel
- `add_settings_group(group)` - Add settings category
- `get_value(setting_id)` - Get current setting
- `apply_settings()` - Save settings changes

#### Performance Requirements
- Settings load: <500ms
- Settings save: <300ms
- UI responsiveness: <100ms

### Theme Manager (`src/vpa/gui/theme_manager.py`)

#### Purpose
Manages application visual themes and appearance.

#### Responsibilities
- Provide light and dark themes
- Handle theme switching
- Manage color palettes
- Provide consistent styling
- Support custom themes

#### Key Interfaces
- `set_theme(theme_name)` - Change current theme
- `get_current_theme()` - Get active theme
- `get_color(color_id)` - Get theme color
- `register_custom_theme(theme)` - Add custom theme

#### Performance Requirements
- Theme switching: <500ms
- Color retrieval: <1ms per lookup

## Windows Integration

### System Tray (`src/vpa/core/windows/system_tray.py`)

#### Purpose
Provides system tray presence and interaction.

#### Responsibilities
- Create system tray icon
- Handle tray menu and actions
- Manage tray notifications
- Control application visibility
- Handle tray events

#### Key Interfaces
- `show_icon()` - Display tray icon
- `hide_icon()` - Remove tray icon
- `set_icon(icon_path)` - Change icon
- `set_tooltip(text)` - Set hover text
- `add_menu_item(label, callback)` - Add menu option

#### Performance Requirements
- Tray creation: <500ms
- Menu display: <100ms
- Action response: <200ms

### Notifications (`src/vpa/core/windows/notification.py`)

#### Purpose
Displays native Windows notifications to the user.

#### Responsibilities
- Show toast notifications
- Handle notification actions
- Manage notification permissions
- Control notification appearance
- Track notification history

#### Key Interfaces
- `show_notification(title, message)` - Display notification
- `dismiss_notification(id)` - Remove notification
- `get_notification_settings()` - Check notification config
- `add_action_button(text, callback)` - Add interactive button

#### Performance Requirements
- Notification display: <500ms
- Action handling: <200ms

### Registry Access (`src/vpa/core/windows/registry.py`)

#### Purpose
Provides secure access to Windows Registry.

#### Responsibilities
- Read registry values
- Write registry values safely
- Handle registry errors
- Manage application registry keys
- Support startup configuration

#### Key Interfaces
- `read_value(key_path, value_name)` - Read registry value
- `write_value(key_path, value_name, data)` - Write registry value
- `delete_value(key_path, value_name)` - Remove registry value
- `set_startup(enabled)` - Configure autostart

#### Performance Requirements
- Registry read: <50ms
- Registry write: <100ms
- Error recovery: <200ms

## LLM Integration

### LLM Manager (`src/vpa/core/llm/llm_manager.py`)

#### Purpose
Coordinates language model functionality and interactions.

#### Responsibilities
- Initialize language models
- Route requests to appropriate model
- Handle model responses
- Manage model resources
- Monitor performance and usage

#### Key Interfaces
- `process_input(text, context)` - Process text with LLM
- `get_available_models()` - List available models
- `set_default_model(model_id)` - Change default model
- `get_model_info(model_id)` - Get model information

#### Performance Requirements
- Request routing: <50ms
- Response processing: <100ms (excluding model time)
- Memory management: Efficient token handling

### LLM Adapters (`src/vpa/core/llm/adapters/`)

#### Purpose
Provides interfaces to different language model backends.

#### Responsibilities
- Connect to model backends
- Standardize request format
- Parse model responses
- Handle model-specific settings
- Manage connection state

#### Key Interfaces
- `initialize()` - Set up model connection
- `generate_response(prompt, params)` - Generate text
- `is_available()` - Check model availability
- `get_capabilities()` - Return model capabilities

#### Performance Requirements
- Adapter overhead: <100ms per request
- Connection management: Efficient pooling

### Prompt System (`src/vpa/core/llm/prompts/`)

#### Purpose
Manages templates and generation of effective prompts.

#### Responsibilities
- Store prompt templates
- Fill templates with context
- Optimize prompts for models
- Track prompt effectiveness
- Manage prompt versioning

#### Key Interfaces
- `get_template(template_id)` - Retrieve prompt template
- `fill_template(template_id, context)` - Create complete prompt
- `register_template(template)` - Add new template
- `get_prompt_stats(template_id)` - Get performance stats

#### Performance Requirements
- Template retrieval: <10ms
- Template filling: <50ms for complex templates

## Plugin System

### Core Plugins (`src/vpa/plugins/core_plugins/`)

#### Purpose
Provides essential built-in functionality.

#### Responsibilities
- Implement basic assistant features
- Provide consistent user experience
- Handle common queries
- Integrate with system components
- Demonstrate plugin capabilities

#### Key Plugins
- **Time and Date**: Time, date, calendar functions
- **Calculator**: Mathematical operations
- **Notes**: Note taking and retrieval
- **System Info**: Computer status and information
- **Weather**: Weather information (if API available)

#### Performance Requirements
- Load time: <500ms total for core plugins
- Response time: <100ms per query
- Memory usage: <50MB total for core plugins

### Addon Plugins (`src/vpa/plugins/addons/`)

#### Purpose
Extends system with optional features and integrations.

#### Responsibilities
- Add specialized functionality
- Integrate with external services
- Enhance core capabilities
- Provide customization options
- Support user-specific needs

#### Key Interfaces
- `install_addon(addon_path)` - Install addon plugin
- `remove_addon(addon_id)` - Remove addon plugin
- `enable_addon(addon_id)` - Enable addon plugin
- `disable_addon(addon_id)` - Disable addon plugin

#### Performance Requirements
- Installation: <5s per addon
- Removal: <2s per addon
- Memory impact: Monitored and reported

### Marketplace (`src/vpa/plugins/marketplace/`)

#### Purpose
Facilitates discovery and installation of additional plugins.

#### Responsibilities
- List available plugins
- Handle plugin installation
- Manage plugin updates
- Verify plugin security
- Track plugin usage

#### Key Interfaces
- `get_available_plugins()` - List marketplace plugins
- `install_plugin(plugin_id)` - Install plugin
- `update_plugin(plugin_id)` - Update plugin
- `get_plugin_details(plugin_id)` - Get plugin information

#### Performance Requirements
- Marketplace load: <3s
- Installation: <10s per plugin
- Update check: <2s

### Plugin Settings (`src/vpa/plugins/settings/`)

#### Purpose
Manages plugin-specific configuration and integration with settings UI.

#### Responsibilities
- Store plugin settings
- Validate plugin settings
- Generate settings UI
- Handle settings persistence
- Notify plugins of setting changes

#### Key Interfaces
- `get_plugin_settings(plugin_id)` - Get plugin settings
- `update_plugin_settings(plugin_id, settings)` - Update settings
- `get_settings_schema(plugin_id)` - Get settings structure
- `get_settings_ui(plugin_id)` - Get settings UI components

#### Performance Requirements
- Settings load: <100ms per plugin
- Settings save: <200ms per plugin
- UI generation: <300ms per plugin

## Component Interactions

### Startup Sequence

1. **Application Manager** initializes
2. **Configuration Manager** loads settings
3. **Event Bus** initializes
4. **Plugin Manager** discovers and loads plugins
5. **Audio System** initializes and verifies voices
6. **LLM Integration** connects to models
7. **Windows Integration** components initialize
8. **GUI System** components initialize and display

### User Input Processing Flow

1. User provides input (text or voice)
2. **GUI System** or **Speech Recognition** captures input
3. **Event Bus** distributes input event
4. **Plugin Manager** routes to appropriate plugin
5. Plugin processes input
6. Response returned via **Event Bus**
7. **Audio System** speaks response (if appropriate)
8. **GUI System** displays response

### Plugin Loading Flow

1. **Plugin Manager** scans plugin directories
2. Plugin manifests are read and validated
3. Plugin dependencies are resolved
4. Plugins are loaded in dependency order
5. Each plugin's `initialize()` method is called
6. Each plugin's `start()` method is called
7. Plugins register event handlers with **Event Bus**

## See Also

- [Architecture Overview](../1_architecture/ARCHITECTURE_OVERVIEW.md)
- [Directory Structure](../1_architecture/DIRECTORY_STRUCTURE.md)
- [Event System Design](../1_architecture/EVENT_SYSTEM_DESIGN.md)
- [Plugin Architecture](../1_architecture/PLUGIN_ARCHITECTURE.md)

---

*Document created: August 29, 2025*  
*Version: 1.0*
