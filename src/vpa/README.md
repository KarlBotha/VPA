# VPA Core Package

This is the main VPA (Virtual Personal Assistant) package containing the core application logic.

## Structure

```
vpa/
├── __main__.py         # Main entry point
├── core/               # Core application components
│   ├── app.py         # Main App class
│   ├── config.py      # Configuration management
│   ├── events.py      # Event bus system
│   └── plugins.py     # Plugin management
├── plugins/           # Plugin directory
├── services/          # Service components
├── cli/               # Command line interface
│   └── main.py       # CLI main entry
└── gui/               # GUI components (future)
```

## Core Components

### App (app.py)
The main application class that orchestrates all VPA components:
- Configuration loading
- Plugin management
- Event system coordination
- Application lifecycle management

### ConfigManager (config.py)
Handles loading and managing configuration from YAML files:
- YAML configuration file support
- Default configuration fallback
- Hierarchical configuration access

### EventBus (events.py)
Simple pub/sub event system for component communication:
- Event subscription and emission
- Decoupled component communication
- Error handling for event callbacks

### PluginManager (plugins.py)
Dynamic plugin loading and management:
- Automatic plugin discovery
- Plugin lifecycle management
- Event-driven plugin communication

## Usage

### Running VPA
```bash
# Run from package directory
python -m vpa start

# With custom config
python -m vpa --config /path/to/config.yaml start

# Show current configuration
python -m vpa config-show
```

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests (when implemented)
pytest tests/
```

## Architecture Principles

1. **Event-Driven**: Components communicate through events
2. **Plugin-Based**: Extensible through plugins
3. **Configuration-Driven**: Behavior controlled by configuration
4. **Modular**: Clear separation of concerns
5. **Testable**: Design supports comprehensive testing
