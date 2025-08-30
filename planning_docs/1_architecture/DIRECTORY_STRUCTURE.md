# VPA Directory Structure

## Overview

This document specifies the organization of code and resources within the VPA project. A well-structured directory layout is essential for maintaining code clarity, facilitating collaboration, and supporting future extensibility.

The VPA project follows a modular, component-based directory structure that reflects the architectural principles of separation of concerns and clear dependency boundaries.

## Root Directory Structure

```
VPA/
├── src/                  # Source code
├── tests/                # Test code
├── config/               # Configuration files
├── docs/                 # Documentation
├── resources/            # Static resources
├── plugins/              # External plugins (user-installed)
├── scripts/              # Utility scripts
├── tools/                # Development tools
└── planning_docs/        # Planning documentation
```

## Source Code Structure (`src/`)

```
src/
├── main.py               # Application entry point
├── audio/                # Audio subsystem
└── vpa/                  # Main application package
    ├── core/             # Core functionality
    ├── gui/              # GUI components
    └── plugins/          # Built-in plugins
```

### Audio Subsystem (`src/audio/`)

```
audio/
├── __init__.py           # Package initialization
├── voice_system.py       # Main voice system implementation
├── voice_catalog.py      # Voice catalog management
├── speech_recognition.py # Speech recognition implementation
├── playback.py           # Audio playback utilities
├── recording.py          # Audio recording utilities
└── utils/                # Utility functions
    ├── __init__.py       # Package initialization
    ├── audio_conversion.py # Audio format conversions
    ├── temp_files.py     # Temporary file management
    └── silence_detection.py # Silence detection utilities
```

### Core Functionality (`src/vpa/core/`)

```
core/
├── __init__.py           # Package initialization
├── app.py                # Application manager
├── events.py             # Event bus system
├── plugins.py            # Plugin management
├── performance.py        # Performance monitoring
├── config.py             # Configuration management
├── exceptions.py         # Exception definitions
├── logging_setup.py      # Logging configuration
├── constants.py          # System constants
├── version.py            # Version information
├── windows/              # Windows integration
│   ├── __init__.py       # Package initialization
│   ├── system_tray.py    # System tray integration
│   ├── notification.py   # Notification system
│   ├── registry.py       # Registry access
│   └── file_system.py    # File system operations
└── llm/                  # LLM integration
    ├── __init__.py       # Package initialization
    ├── llm_manager.py    # LLM management
    ├── models.py         # Model definitions
    ├── prompts.py        # Prompt templates
    ├── response.py       # Response processing
    └── adapters/         # LLM adapters
        ├── __init__.py   # Package initialization
        ├── base.py       # Base adapter class
        ├── ollama.py     # Ollama adapter
        └── openai.py     # OpenAI adapter
```

### GUI Components (`src/vpa/gui/`)

```
gui/
├── __init__.py           # Package initialization
├── main_window.py        # Main application window
├── chat_interface.py     # Chat interface
├── settings_panel.py     # Settings interface
├── theme_manager.py      # Theme management
├── components/           # Reusable UI components
│   ├── __init__.py       # Package initialization
│   ├── message_bubble.py # Message bubble component
│   ├── input_field.py    # Input field component
│   ├── voice_button.py   # Voice input button
│   └── settings_control.py # Settings control
├── windows/              # Additional windows
│   ├── __init__.py       # Package initialization
│   ├── about_window.py   # About window
│   ├── help_window.py    # Help window
│   └── login_window.py   # Login window
└── assets/               # GUI assets
    ├── icons/            # Icon files
    ├── themes/           # Theme definitions
    └── fonts/            # Font files
```

### Plugin System (`src/vpa/plugins/`)

```
plugins/
├── __init__.py           # Package initialization
├── base_plugin.py        # Base plugin class
├── plugin_loader.py      # Plugin loading utilities
├── plugin_registry.py    # Plugin registry
├── core_plugins/         # Built-in core plugins
│   ├── __init__.py       # Package initialization
│   ├── time_date/        # Time and date plugin
│   ├── calculator/       # Calculator plugin
│   ├── notes/            # Notes plugin
│   ├── system_info/      # System information plugin
│   └── weather/          # Weather plugin
└── marketplace/          # Plugin marketplace
    ├── __init__.py       # Package initialization
    ├── discovery.py      # Plugin discovery
    ├── installation.py   # Plugin installation
    └── validation.py     # Plugin validation
```

## Tests Structure (`tests/`)

```
tests/
├── conftest.py           # Test configuration
├── test_main.py          # Main entry point tests
├── core/                 # Core tests
│   ├── test_app.py       # App tests
│   ├── test_events.py    # Event bus tests
│   ├── test_plugins.py   # Plugin system tests
│   └── test_performance.py # Performance tests
├── audio/                # Audio tests
│   ├── test_voice_system.py # Voice system tests
│   ├── test_speech_recognition.py # Speech recognition tests
│   └── test_playback.py  # Playback tests
├── gui/                  # GUI tests
│   ├── test_main_window.py # Main window tests
│   └── test_chat_interface.py # Chat interface tests
├── plugins/              # Plugin tests
│   ├── test_base_plugin.py # Base plugin tests
│   └── test_plugin_loader.py # Plugin loader tests
└── integration/          # Integration tests
    ├── test_core_architecture.py # Core architecture tests
    ├── test_audio_system.py # Audio system tests
    └── test_plugin_system.py # Plugin system tests
```

## Configuration Structure (`config/`)

```
config/
├── default_config.json   # Default configuration
├── logging_config.json   # Logging configuration
├── voice_settings.json   # Voice system settings
├── plugin_config.json    # Plugin configuration
├── theme_config.json     # Theme configuration
└── user/                 # User-specific configs
    └── user_config.json  # User configuration
```

## Documentation Structure (`docs/`)

```
docs/
├── index.md              # Documentation index
├── user_guide/           # User documentation
│   ├── getting_started.md # Getting started guide
│   ├── features.md       # Feature guide
│   └── troubleshooting.md # Troubleshooting guide
├── developer_guide/      # Developer documentation
│   ├── architecture.md   # Architecture guide
│   ├── plugin_development.md # Plugin development guide
│   └── contribution.md   # Contribution guide
└── api/                  # API documentation
    ├── core_api.md       # Core API docs
    ├── plugin_api.md     # Plugin API docs
    └── gui_api.md        # GUI API docs
```

## Resources Structure (`resources/`)

```
resources/
├── audio/                # Audio resources
│   ├── sounds/           # Sound effects
│   └── samples/          # Sample audio
├── icons/                # Icon files
│   ├── app_icon.ico      # Application icon
│   ├── tray_icon.ico     # System tray icon
│   └── action_icons/     # Action icons
└── data/                 # Static data files
    ├── initial_prompts.json # Initial prompt templates
    └── default_responses.json # Default responses
```

## External Plugins Structure (`plugins/`)

```
plugins/
├── README.md             # Plugin directory readme
└── (plugin directories)  # User-installed plugins
```

## Development Scripts (`scripts/`)

```
scripts/
├── setup_dev.py          # Development environment setup
├── build_app.py          # Application build script
├── run_tests.py          # Test runner
└── generate_docs.py      # Documentation generator
```

## Development Tools (`tools/`)

```
tools/
├── plugin_template/      # Plugin template generator
├── performance_analyzer/ # Performance analysis tools
└── mock_data_generator/  # Mock data generation
```

## Planning Documentation (`planning_docs/`)

```
planning_docs/
├── INDEX.md              # Documentation index
├── 1_architecture/       # Architecture documents
├── 2_components/         # Component specifications
├── 3_implementation_roadmap/ # Implementation plans
├── 4_technical_standards/ # Technical standards
├── 5_security_privacy/   # Security and privacy
├── 6_testing_quality/    # Testing and quality
└── 7_deployment/         # Deployment documents
```

## File Naming Conventions

1. **Python Modules**: Snake case (lowercase with underscores)
   - Example: `voice_system.py`

2. **Classes**: Pascal case (uppercase first letter of each word)
   - Example: `class EventBus:`

3. **Functions and Methods**: Snake case
   - Example: `def process_audio_data():`

4. **Constants**: Uppercase with underscores
   - Example: `MAX_AUDIO_BUFFER_SIZE = 8192`

5. **Configuration Files**: Snake case with appropriate extension
   - Example: `default_config.json`

6. **Documentation Files**: Uppercase with underscores and .md extension
   - Example: `ARCHITECTURE_OVERVIEW.md`

## Import Structure Conventions

1. **Absolute Imports**: Use absolute imports from the root package
   - Example: `from vpa.core.events import event_bus`

2. **Import Ordering**:
   - Standard library imports
   - Third-party library imports
   - Application imports

3. **Module-Level Exports**: Define `__all__` for public interfaces
   - Example: `__all__ = ['EventBus', 'event_bus']`

## Directory Creation Guidelines

1. **New Plugins**: Place in appropriate directory based on type
   - Core plugins: `src/vpa/plugins/core_plugins/`
   - Addon plugins: `plugins/`

2. **New Components**: Follow existing structure and architectural principles
   - Create appropriate package structure with `__init__.py`
   - Include relevant tests in corresponding test directory

3. **New Resources**: Place in appropriate resource directory
   - Follow existing categorization (audio, icons, data)

## Conclusion

This directory structure provides a clear organization for the VPA project that supports the architectural principles of modularity, separation of concerns, and clear dependency boundaries. All developers should adhere to this structure when adding new files or components.

As the project evolves, minor adjustments to this structure may be made, but they should preserve the core organizational principles outlined here.

## Related Documents

- [Architecture Overview](./ARCHITECTURE_OVERVIEW.md)
- [System Components](./SYSTEM_COMPONENTS.md)
- [Code Standards](../4_technical_standards/CODE_STANDARDS.md)

---

*Document created: August 29, 2025*  
*Version: 1.0*
