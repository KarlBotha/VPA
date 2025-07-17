# VPA Core API Documentation

**Generated:** July 16, 2025  
**Version:** Phase 3 Enhancement  
**Coverage:** Core Application & Plugin System  

---

## Core Application API

### App Class

The main VPA application class with performance monitoring capabilities.

#### Constructor

```python
App(config_path: Optional[str] = None)
```

**Parameters:**
- `config_path` (Optional[str]): Path to configuration file. Uses default if None.

**Example:**
```python
from vpa.core.app import App

# Use default configuration
app = App()

# Use custom configuration
app = App("/path/to/config.yaml")
```

#### Methods

##### `initialize() -> None`

Initialize all application components with performance tracking.

**Behavior:**
- Loads configuration with timing
- Initializes event bus with timing
- Loads plugins with timing
- Logs total initialization time

**Example:**
```python
app = App()
app.initialize()  # Logs: "VPA application initialized successfully in 0.543s"
```

##### `start() -> None`

Start the VPA application and all loaded plugins.

**Example:**
```python
app = App()
app.initialize()
app.start()
```

##### `stop() -> None`

Stop the VPA application and clean up resources.

**Example:**
```python
app.stop()  # Graceful shutdown
```

##### `is_running() -> bool`

Check if the application is currently running.

**Returns:**
- `bool`: True if application is running, False otherwise

**Example:**
```python
if app.is_running():
    print("Application is active")
```

##### `get_performance_metrics() -> Dict[str, Any]`

Get current performance metrics for monitoring and optimization.

**Returns:**
- `Dict[str, Any]`: Performance metrics dictionary

**Metrics Included:**
- `app_init`: Application initialization time
- `config_load`: Configuration loading time
- `event_bus_init`: Event bus initialization time
- `plugin_load`: Plugin loading time
- `total_init`: Total initialization time

**Example:**
```python
metrics = app.get_performance_metrics()
print(f"Startup time: {metrics['total_init']:.3f}s")
print(f"Plugin load: {metrics['plugin_load']:.3f}s")
```

---

## Plugin Manager API

### PluginManager Class

Manages plugin loading and lifecycle with performance optimization.

#### Constructor

```python
PluginManager(event_bus: EventBus)
```

**Parameters:**
- `event_bus` (EventBus): Event bus instance for plugin communication

#### Methods

##### `load_plugins(plugin_names: Optional[List[str]] = None) -> None`

Load plugins from the plugins directory with performance optimization.

**Parameters:**
- `plugin_names` (Optional[List[str]]): Specific plugins to load. Loads all if None.

**Features:**
- Skips previously failed plugins
- Times plugin loading operations
- Caches plugin instances
- Logs performance metrics

**Example:**
```python
# Load all plugins
plugin_manager.load_plugins()

# Load specific plugins
plugin_manager.load_plugins(["core_plugin", "audio_plugin"])
```

##### `unload_plugins() -> None`

Unload all plugins and clean up resources.

**Example:**
```python
plugin_manager.unload_plugins()
```

##### `get_plugin(plugin_name: str) -> Optional[Any]`

Get a loaded plugin instance by name.

**Parameters:**
- `plugin_name` (str): Name of the plugin to retrieve

**Returns:**
- `Optional[Any]`: Plugin instance or None if not found

**Example:**
```python
audio_plugin = plugin_manager.get_plugin("audio_plugin")
if audio_plugin:
    audio_plugin.play_sound("notification.wav")
```

##### `list_plugins() -> List[str]`

List all currently loaded plugin names.

**Returns:**
- `List[str]`: List of loaded plugin names

**Example:**
```python
plugins = plugin_manager.list_plugins()
print(f"Loaded plugins: {', '.join(plugins)}")
```

##### `get_load_times() -> Dict[str, float]`

Get plugin load times for performance analysis.

**Returns:**
- `Dict[str, float]`: Plugin names mapped to load times in seconds

**Example:**
```python
load_times = plugin_manager.get_load_times()
for plugin, time in load_times.items():
    print(f"{plugin}: {time:.3f}s")
```

---

## Event Bus API

### EventBus Class

Simple pub/sub event system for component communication.

#### Methods

##### `emit(event_name: str, data: Any = None) -> None`

Emit an event to all subscribers.

**Parameters:**
- `event_name` (str): Name of the event to emit
- `data` (Any): Event data payload (optional)

**Example:**
```python
# Simple event
event_bus.emit("user.login")

# Event with data
event_bus.emit("file.uploaded", {"filename": "document.pdf", "size": 1024})
```

##### `subscribe(event_name: str, callback: Callable) -> None`

Subscribe to an event with a callback function.

**Parameters:**
- `event_name` (str): Name of the event to subscribe to
- `callback` (Callable): Function to call when event is emitted

**Example:**
```python
def handle_login(data):
    print(f"User logged in: {data}")

event_bus.subscribe("user.login", handle_login)
```

##### `unsubscribe(event_name: str, callback: Callable) -> None`

Unsubscribe from an event.

**Parameters:**
- `event_name` (str): Name of the event to unsubscribe from
- `callback` (Callable): Callback function to remove

**Example:**
```python
event_bus.unsubscribe("user.login", handle_login)
```

---

## Configuration Manager API

### ConfigManager Class

Handles loading and managing configuration from YAML files.

#### Constructor

```python
ConfigManager(config_path: Optional[str] = None)
```

**Parameters:**
- `config_path` (Optional[str]): Path to configuration file

#### Methods

##### `load() -> None`

Load configuration from file or use defaults.

**Example:**
```python
config = ConfigManager("config.yaml")
config.load()
```

##### `get(key: str, default: Any = None) -> Any`

Get a configuration value by key.

**Parameters:**
- `key` (str): Configuration key (supports dot notation)
- `default` (Any): Default value if key not found

**Returns:**
- `Any`: Configuration value or default

**Example:**
```python
# Simple key
debug_mode = config.get("debug", False)

# Nested key with dot notation
db_host = config.get("database.host", "localhost")
```

##### `set(key: str, value: Any) -> None`

Set a configuration value.

**Parameters:**
- `key` (str): Configuration key
- `value` (Any): Value to set

**Example:**
```python
config.set("debug", True)
config.set("database.port", 5432)
```

---

## Usage Examples

### Complete Application Setup

```python
from vpa.core.app import App
from vpa.core.config import ConfigManager

# Initialize application
app = App("config/production.yaml")
app.initialize()

# Check performance
metrics = app.get_performance_metrics()
if metrics['total_init'] > 2.0:
    print("Warning: Slow startup detected")

# Start application
app.start()

# Application running...

# Graceful shutdown
app.stop()
```

### Plugin Development

```python
from vpa.core.events import EventBus

class MyPlugin:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.event_bus.subscribe("app.start", self.on_app_start)
    
    def on_app_start(self, data):
        print("Plugin activated on app start")
    
    def cleanup(self):
        """Called during plugin unload"""
        self.event_bus.unsubscribe("app.start", self.on_app_start)

# Plugin factory function
def initialize(event_bus: EventBus):
    return MyPlugin(event_bus)
```

### Performance Monitoring

```python
# Monitor application performance
metrics = app.get_performance_metrics()
print(f"Startup Performance Report:")
print(f"  Total Init: {metrics['total_init']:.3f}s")
print(f"  Config Load: {metrics['config_load']:.3f}s")
print(f"  Plugin Load: {metrics['plugin_load']:.3f}s")

# Monitor plugin performance
load_times = app.plugin_manager.get_load_times()
slow_plugins = {k: v for k, v in load_times.items() if v > 0.5}
if slow_plugins:
    print(f"Slow plugins detected: {slow_plugins}")
```

---

**API Version:** Phase 3  
**Last Updated:** July 16, 2025  
**Next Review:** After Phase 3 completion
