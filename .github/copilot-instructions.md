# VPA (Virtual Personal Assistant) - Copilot Instructions

## 🏗️ Architecture Overview

VPA is an **event-driven, modular Virtual Personal Assistant** with a plugin architecture focused on performance and compartmentalized isolation. The system is built around three core patterns:

### Core Components
- **Event Bus System** (`src/vpa/core/events.py`) - Central async communication with <10ms dispatch target
- **Plugin Manager** (`src/vpa/core/plugins.py`) - Cached lazy loading with dependency management
- **Audio System** (`src/audio/voice_system.py`) - 13-voice catalog with <2s TTS response target
- **Application Manager** (`src/vpa/core/app.py`) - Lifecycle management with <10s startup target

### Key Architectural Principles
- **Performance First**: Strict performance targets (startup <10s, memory <2GB, events <10ms, TTS <2s)
- **Event-Driven**: Zero direct coupling between components - all communication via `event_bus`
- **Compartmentalized**: Plugins isolated with error boundaries and graceful degradation
- **Async-First**: All I/O operations use `asyncio` patterns for non-blocking execution

## 🚀 Development Workflows

### Essential Commands
```powershell
# Run application (development)
cd src && python main.py

# Run tests with coverage
python -m pytest tests/ --cov=src/vpa --cov-report=html

# Test specific component
python -m pytest tests/test_core_architecture.py -v

# Performance validation
python -c "import time; start=time.time(); import src.vpa.core.app; print(f'Import time: {time.time()-start:.3f}s')"
```

### Performance Monitoring
Always use `@PerformanceMonitor.track_execution_time("function_name")` decorator for functions that might exceed 10ms. The system tracks:
- Startup time (target: <10s)
- Memory usage (target: <2GB)
- Event dispatch (target: <10ms)
- Voice synthesis (target: <2s)

## 🔌 Plugin Development

### Plugin Interface Pattern
```python
from vpa.core.plugins import Plugin

class YourPlugin(Plugin):
    @property
    def name(self) -> str:
        return "your_plugin"
    
    def can_handle(self, user_input: str, context: Dict[str, Any]) -> bool:
        return "your_trigger" in user_input.lower()
    
    async def process(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Use event bus for communication
        from vpa.core.events import event_bus
        await event_bus.emit_async("plugin_action", {"data": "value"})
        return {"response": "processed"}
```

### Plugin Discovery
- Place plugins in `src/plugins/` or `plugins/` directories
- Plugins auto-discovered on startup with caching (`plugin_cache.json`)
- Use priority system for load order (higher number = higher priority)

## 🎯 Code Patterns & Conventions

### Event Communication Pattern
```python
# Subscribe to events (use async_callback=True for async handlers)
event_bus.subscribe("event_name", handler_function, async_callback=True)

# Emit events (prefer async version)
await event_bus.emit_async("event_name", {"key": "value"})

# Always handle exceptions in event handlers
async def safe_handler(event):
    try:
        # Your logic here
        pass
    except Exception as e:
        logger.error(f"Handler failed: {e}")
```

### Error Handling Pattern
- Use **graceful degradation**: system continues with reduced functionality
- All exceptions logged with context
- Critical errors trigger `critical_error` event for coordinated response
- Plugin errors isolated - don't crash main application

### Voice System Integration
```python
from audio.voice_system import audio_system

# Get available voices (13-voice catalog)
voices = audio_system.get_available_voices()

# Synthesize speech with performance monitoring
result = await audio_system.synthesize_speech("Hello world", voice_id="voice_01")
```

## 📊 Testing & Quality

### Test Structure
- `tests/test_core_architecture.py` - Integration tests for all core components
- `tests/core/` - Unit tests for core modules
- `tests/audio/` - Audio system tests with mocking
- Always test async functionality with `@pytest.mark.asyncio`

### Coverage Requirements
Maintain >90% test coverage. Run `pytest --cov=src/vpa --cov-report=html` and check `htmlcov/index.html`.

### Performance Validation
Integration test validates all performance targets. Critical check:
```python
status = app.get_status()
assert status["performance_targets"]["startup_time_achieved"] == True
```

## 🔧 Configuration & Settings

### Dependencies
Core dependencies in `requirements.txt`:
- `psutil>=5.9.0` (performance monitoring)
- `pytest>=7.0.0` with `pytest-asyncio>=0.21.0` (testing)
- `pytest-cov>=4.0.0` (coverage)

### Project Structure
```
src/
├── main.py              # Application entry point
├── audio/               # Voice system (13-voice catalog)
└── vpa/
    ├── core/            # Core application logic
    │   ├── app.py       # Application manager
    │   ├── events.py    # Event bus system
    │   └── plugins.py   # Plugin management
    ├── gui/             # GUI components (minimal)
    └── plugins/         # Plugin modules
```

## ⚡ Performance Optimization

### Critical Performance Paths
1. **Startup Sequence**: Core → Plugins → Services → Ready (monitored phases)
2. **Event Dispatch**: <10ms target with async parallel execution
3. **Plugin Loading**: Cached discovery with parallel initialization
4. **Voice Synthesis**: <2s response with 44.1kHz/16-bit quality

### Memory Management
- Monitor with `PerformanceMonitor.monitor_memory_usage()`
- Target: <2GB total usage
- Plugin cleanup on shutdown to prevent leaks
- Use `event_bus.cleanup()` in shutdown sequence

## 🎨 UI Integration Points

Current UI is minimal - focus on **event-driven integration**:
- Subscribe to `app_startup_complete` for UI initialization
- Use `voice_synthesis_complete` for TTS feedback
- Emit `user_input` events for processing
- Handle `critical_error` events for user notification

---

*For questions about undocumented patterns, check `tests/test_core_architecture.py` integration test - it demonstrates all component interactions.*
