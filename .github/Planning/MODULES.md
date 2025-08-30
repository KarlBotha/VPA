# VPA Module Documentation

## Core Modules Analysis

### Application Entry Points

#### `src/main.py` (Primary Entry Point)
- **Purpose**: Async application launcher with comprehensive startup
- **Key Functions**:
  - `async def main()`: Main application entry point
  - `setup_logging()`: Comprehensive logging configuration
  - Performance monitoring during startup
  - Voice system verification
  - Graceful shutdown handling
- **Dependencies**: `vpa.core.app`, `vpa.core.events`, `audio.voice_system`
- **Performance Targets**: <10s startup, memory monitoring

#### `src/vpa/__main__.py`
- **Purpose**: Python -m vpa entry point
- **Integration**: Links to CLI system
- **Usage**: `python -m vpa [commands]`

### Core Application Modules (`src/vpa/core/`)

#### Application Manager (`app.py`) - 88 lines
```python
class App:
    """Main VPA application with performance monitoring"""
    def __init__(self, config_path: Optional[str] = None)
    async def startup() -> bool
    async def shutdown() -> None
    def get_status() -> Dict[str, Any]
```
- **Purpose**: Central application lifecycle management
- **Key Features**:
  - Performance tracking with metrics
  - Component initialization sequencing
  - Status reporting with performance targets
  - Graceful startup/shutdown coordination
- **Performance Monitoring**: 
  - Startup time tracking (<10s target)
  - Memory usage monitoring (<2GB target)
  - Service readiness validation

#### Event Bus (`events.py`) - 69 lines
```python
class EventBus:
    """Simple event bus for pub/sub messaging"""
    def subscribe(self, event_type: str, callback: Callable)
    def unsubscribe(self, event_type: str, callback: Callable)  
    def emit(self, event_type: str, data: Any = None)
    async def emit_async(self, event_type: str, data: Any = None)
```
- **Purpose**: Component communication via pub/sub pattern
- **Key Features**:
  - Zero direct coupling between components
  - Async event handling support
  - Performance target: <10ms dispatch
  - Error isolation for handlers
- **Event Types**: User input, voice synthesis, UI updates, system events

#### Plugin Manager (`plugins.py`)
```python
class PluginManager:
    """Plugin discovery and lifecycle management"""
    def load_plugins() -> None
    def get_plugin(self, name: str) -> Optional[Plugin]
    def handle_user_input(self, input_text: str, context: Dict)
```
- **Purpose**: Dynamic plugin discovery and management
- **Key Features**:
  - Auto-discovery from `src/vpa/plugins/` and `plugins/` 
  - Cached discovery via `plugin_cache.json`
  - Priority-based loading system
  - Error boundaries for plugin failures
  - Dependency resolution

#### Configuration Manager (`config.py`)
```python
class ConfigManager:
    """Configuration loading and management"""
    def load(self, config_path: Optional[str] = None)
    def get(self, key: str, default: Any = None)
    def set(self, key: str, value: Any)
```
- **Purpose**: Centralized configuration management
- **Configuration Sources**:
  - `config/default.yaml` - Application defaults
  - `config/voice_settings.json` - Voice system config  
  - `config/ui_settings.json` - GUI preferences
  - `config/audio.yaml` - Audio system settings

### Audio System Modules (`src/audio/`)

#### Primary Voice System (`voice_system.py`) - 504 lines ⭐
```python
class VPAVoiceSystem:
    """13-voice Edge-TTS system with SAPI fallback"""
    def get_available_voices(self) -> List[VoiceInfo]
    async def synthesize_speech(self, text: str, voice_id: str)
    def verify_voice_catalog(self) -> Dict[str, bool]
    def _get_neural_voices(self) -> List[VoiceInfo]
    def _get_sapi_voices(self) -> List[VoiceInfo]
```
- **Purpose**: Primary voice synthesis with 13-voice catalog
- **Voice Catalog**:
  - **Neural Voices** (Edge-TTS): Andrew, Christopher, Guy, Roger, Eric, Steffan, Emma, Ava, Aria, Jenny, Libby, Michelle
  - **Fallback**: Windows SAPI voices
- **Performance**: <2s TTS response target
- **Audio Quality**: 44.1kHz/16-bit output
- **Dependencies**: `edge-tts`, `pygame`, `win32com.client`

#### Alternative Voice Systems
- **`production_voice_system.py`**: Production-optimized voice system
- **`neural_voice_engine.py`**: Neural voice processing engine
- **`voice_system_azure_restored.py`**: Azure voice system integration
- **`vpa_agent_voice.py`**: Agent-specific voice handling

### GUI System Modules (`src/vpa/gui/`)

#### Primary GUI Components (APPROVED_RESTORE)

##### Login System (`login_window_APPROVED_RESTORE.py`) - 637 lines ⭐
```python
class VPALoginWindow(ctk.CTkToplevel):
    """User authentication with first-time setup detection"""
    def __init__(self, parent=None, gui_manager=None)
    def setup_dialog(self)
    def create_widgets(self)  
    def handle_login(self)
    def handle_register(self)
```
- **Purpose**: User authentication and first-time setup
- **Key Features**:
  - CustomTkinter modal dialog
  - First-time user detection
  - Registration workflow integration
  - Dark theme with blue accent
  - Form validation and error handling
- **Known Issues**: Geometry positioning (hardcoded 450x750)

##### Settings Panel (`settings_window_APPROVED_RESTORE.py`) - 835 lines ⭐
```python
class VPASettingsWindow(ctk.CTk):
    """Settings panel with 13-voice integration"""
    def __init__(self, gui_manager=None)
    def create_voice_settings(self)
    def setup_voice_categories(self)
    def handle_voice_selection(self, voice_id: str)
```
- **Purpose**: System configuration with voice integration
- **Key Features**:
  - 13-voice system integration
  - Voice rate/volume controls
  - Real-time voice testing
  - Settings persistence to JSON
  - Categorized voice selection (Male, Female, British, American)

##### Main Chat UI (`main_window_APPROVED_RESTORE.py`) - 542 lines ⭐  
```python
class VPAChatUI(ctk.CTk):
    """Primary chat interface with voice integration"""
    def __init__(self, gui_manager=None)
    def create_chat_area(self)
    def handle_user_input(self, message: str)
    def add_chat_message(self, message: str, is_user: bool)
```
- **Purpose**: Primary user interface for VPA interaction
- **Key Features**:
  - Chat-based interaction model
  - Voice input/output integration
  - Message history with timestamps
  - Event bus integration for responses
  - Responsive layout with scrolling

#### GUI Framework Integration
- **CustomTkinter**: Primary GUI framework (dark theme)
- **Modal Management**: Proper window focus and lifecycle
- **Event Integration**: All GUI components emit events to event bus
- **Theme Consistency**: Dark mode with blue accents across all components

### Authentication Modules (`src/vpa/auth/`)

#### Core Authentication (`src/vpa/core/auth.py`)
```python
class AuthenticationSystem:
    """User authentication and session management"""
    def authenticate_user(self, username: str, password: str) -> bool
    def create_user(self, username: str, password: str) -> bool
    def get_current_user(self) -> Optional[User]
```
- **Purpose**: User authentication and session management
- **Features**:
  - Local user accounts with password hashing
  - Session management with security
  - First-time setup detection
  - Integration with GUI login system

#### OAuth Integration (`src/vpa/core/oauth_config.py`)
```python
class OAuthManager:
    """OAuth flow management for external providers"""
    def setup_microsoft_oauth(self) -> Dict[str, str]
    def handle_oauth_callback(self, code: str) -> bool
```
- **Purpose**: External authentication provider integration
- **Supported Providers**: Microsoft OAuth (primary)
- **Features**: Callback server, token management, secure storage

### Plugin System Modules (`src/vpa/plugins/`)

#### Plugin Base Classes
```python
class Plugin:
    """Base plugin interface"""
    @property
    def name(self) -> str: pass
    def can_handle(self, user_input: str, context: Dict) -> bool: pass
    async def process(self, user_input: str, context: Dict) -> Dict: pass
```

#### Plugin Discovery
- **Auto-Discovery**: Scans `src/vpa/plugins/` and `plugins/` directories
- **Caching**: Discovery results cached in `src/plugin_cache.json`
- **Priority System**: Higher number = higher priority loading
- **Error Isolation**: Plugin failures don't crash main application

### Configuration Modules

#### Voice Configuration (`config/voice_settings.json`)
```json
{
    "voice_01": {"name": "Andrew", "rate": 200, "volume": 0.9},
    "voice_02": {"name": "Christopher", "rate": 200, "volume": 0.9},
    // ... 13 total voices configured
}
```
- **Purpose**: 13-voice system configuration
- **Settings**: Rate (speech speed), Volume (0.0-1.0)
- **Integration**: Loaded by settings window for real-time configuration

#### UI Configuration (`config/ui_settings.json`)
```json
{
    "theme": "dark",
    "window_geometry": {"login": "450x750", "main": "800x600"},
    "font_size": 12,
    "voice_preview_enabled": true
}
```

### Utility Modules (`src/vpa/util/`)

#### Performance Monitoring (`src/vpa/core/performance_monitor.py`)
```python
class PerformanceMonitor:
    """Performance tracking and optimization"""
    @staticmethod
    def track_execution_time(function_name: str)
    def monitor_memory_usage(self) -> float
    def check_performance_targets(self) -> Dict[str, bool]
```
- **Purpose**: System performance tracking
- **Targets**: Startup <10s, Memory <2GB, Events <10ms, TTS <2s
- **Usage**: Decorator pattern for function monitoring

#### Resource Management (`src/vpa/core/resource_monitoring.py`)
```python
class ResourceMonitor:
    """System resource monitoring"""
    def get_cpu_usage(self) -> float
    def get_memory_usage(self) -> Dict[str, float] 
    def get_disk_usage(self) -> Dict[str, float]
```
- **Purpose**: System resource tracking via PSUtil
- **Integration**: GUI resource monitor widget

### Service Modules (`src/vpa/services/`)

#### Session Management (`src/vpa/core/session_manager.py`)
```python
class SessionManager:
    """User session lifecycle management"""
    def create_session(self, user_id: str) -> str
    def validate_session(self, session_id: str) -> bool
    def cleanup_expired_sessions(self) -> None
```

#### Cache Management (`src/vpa/core/cache_manager.py`)
```python
class CacheManager:
    """Application caching system"""
    def get(self, key: str) -> Optional[Any]
    def set(self, key: str, value: Any, ttl: int = 3600)
    def clear(self) -> None
```

### LLM Integration Modules (`src/vpa/llm/`)

#### LLM Provider Manager (`src/vpa/core/llm_provider_manager.py`)
```python  
class LLMProviderManager:
    """LLM provider abstraction"""
    def get_available_providers(self) -> List[str]
    def set_active_provider(self, provider: str) -> bool
    async def generate_response(self, prompt: str) -> str
```
- **Purpose**: Abstraction layer for LLM providers
- **Supported**: Ollama (local), extensible for cloud providers
- **Integration**: Optional dependency, enabled via configuration

### CLI Modules (`src/vpa/cli/`)

#### Command Line Interface
```python
@click.group()
def cli():
    """VPA Command Line Interface"""
    pass

@cli.command()
def start():
    """Start the VPA application"""
    pass
```
- **Purpose**: Command-line entry points
- **Framework**: Click for command parsing
- **Integration**: `vpa` script entry point in pyproject.toml

## Module Dependencies

### Core Dependency Graph
```
main.py
├── vpa.core.app (App lifecycle)
├── vpa.core.events (Event bus)
├── vpa.core.plugins (Plugin system)
└── audio.voice_system (Voice synthesis)

vpa.core.app
├── vpa.core.config (Configuration)
├── vpa.core.events (Communication)
├── vpa.core.plugins (Extensions)
└── vpa.core.performance_monitor (Metrics)

audio.voice_system  
├── edge-tts (Neural voices)
├── pygame (Audio playback)
├── win32com.client (SAPI fallback)
└── json (Configuration)
```

### GUI Dependency Graph
```
login_window_APPROVED_RESTORE.py
├── customtkinter (GUI framework)
├── vpa.core.events (Event communication)
└── vpa.core.auth (Authentication)

settings_window_APPROVED_RESTORE.py
├── customtkinter (GUI framework)
├── audio.voice_system (Voice integration)
├── json (Settings persistence)
└── vpa.core.events (Event communication)

main_window_APPROVED_RESTORE.py
├── customtkinter (GUI framework)  
├── vpa.core.events (Event communication)
├── vpa.core.plugins (Plugin responses)
└── audio.voice_system (Voice output)
```

## Module Load Order

### Application Startup Sequence
1. **`main.py`** - Entry point initialization
2. **`vpa.core.config`** - Configuration loading
3. **`vpa.core.events`** - Event bus initialization  
4. **`vpa.core.plugins`** - Plugin discovery and loading
5. **`audio.voice_system`** - Voice system initialization
6. **`vpa.core.app`** - Application startup completion
7. **GUI Components** - Window creation (on-demand)

### Performance-Critical Modules
- **`vpa.core.events`**: <10ms event dispatch requirement
- **`audio.voice_system`**: <2s TTS synthesis requirement  
- **`vpa.core.app`**: <10s total startup requirement
- **`vpa.core.performance_monitor`**: Real-time performance tracking

## Module Testing Coverage

### High-Priority Test Modules
- **`tests/core/test_app.py`**: Application lifecycle testing
- **`tests/core/test_events.py`**: Event bus functionality
- **`tests/audio/test_voice_system.py`**: Voice synthesis testing
- **`tests/gui/test_approved_restore.py`**: GUI component testing

### Integration Test Module
- **`tests/test_core_architecture.py`**: End-to-end integration validation

---

*This module documentation reflects the current implementation as analyzed from the actual source code structure and content.*
