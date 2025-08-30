# VPA Technology Stack Documentation

## Runtime Environment

### Python Platform
- **Python Version**: 3.9+ (tested with 3.11.9)
- **Target OS**: Microsoft Windows (primary support)
- **Installation**: Windows-native Python (not WSL, not remote, not SSH)
- **Architecture**: x64 Windows systems
- **Package Management**: pip with requirements.txt + pyproject.toml

### Python Standard Library Dependencies
```python
import asyncio              # Async operations (core)
import logging             # Logging system
import json                # Configuration persistence  
import pathlib             # Path handling
import tempfile            # Temporary file management
import time                # Performance timing
import sys                 # System integration
import os                  # Operating system interface
import typing              # Type hints
from dataclasses import dataclass  # Data structures
from collections import defaultdict # Event collections
```

## Core Framework Stack

### Asynchronous Computing
```yaml
AsyncIO:
  version: "Python 3.9+ stdlib"
  purpose: "Non-blocking I/O operations"
  usage: 
    - Event bus async operations
    - Voice synthesis pipeline
    - Application lifecycle management
  performance_target: "<10ms event dispatch"
  
Concurrent Processing:
  threads: "Limited use for blocking operations"  
  async_patterns: "Primary concurrency model"
  event_loops: "Single main event loop"
```

### Configuration Management
```yaml
PyYAML:
  version: ">=6.0"
  purpose: "YAML configuration file parsing"
  files:
    - config/default.yaml
    - config/audio.yaml
  features:
    - Safe loading
    - Type preservation
    - Nested configuration structures

JSON:
  version: "Python stdlib"
  purpose: "Settings persistence and API data"
  files:
    - config/voice_settings.json  
    - config/ui_settings.json
    - src/plugin_cache.json
  usage: "High-frequency read/write operations"
```

### Command Line Interface
```yaml
Click:
  version: ">=8.0.0"
  purpose: "CLI command parsing and handling"
  features:
    - Command groups and subcommands
    - Parameter validation
    - Help generation
  entry_point: "vpa" script command
```

## Audio & Voice Technology Stack

### Text-to-Speech Engines

#### Primary: Microsoft Edge-TTS
```yaml
Edge-TTS:
  version: ">=7.0.0"
  purpose: "Neural voice synthesis (13-voice catalog)"
  voices:
    male_american: [Andrew, Christopher, Guy, Roger]
    male_british: [Eric, Steffan]  
    female_american: [Emma, Ava, Aria, Jenny]
    female_british: [Libby]
    female_multilingual: [Michelle]
  quality: "Neural (high quality)"
  performance_target: "<2s TTS response"
  output_format: "44.1kHz/16-bit audio"
  dependency: "pip install edge-tts"
```

#### Fallback: Windows SAPI
```yaml
PyTTSX3:
  version: ">=2.90"  
  purpose: "Windows Speech API integration"
  fallback_for: "Edge-TTS unavailability"
  voices: "System-installed SAPI voices"
  quality: "Standard (lower quality than neural)"
  reliability: "High (system-integrated)"
  
Win32COM:
  package: "pywin32>=311"
  purpose: "Windows COM interface access"
  usage: "Direct SAPI voice control"
  platform: "Windows-only"
```

### Audio Playback
```yaml
Pygame:
  version: ">=2.6.0"
  purpose: "Cross-platform audio playback"
  features:
    - Audio file playback
    - Volume control  
    - Audio device management
    - Real-time audio processing
  supported_formats: [WAV, MP3, OGG]
  integration: "Voice system audio output"
```

## GUI Technology Stack

### Primary GUI Framework
```yaml
CustomTkinter:
  version: ">=5.2.0"
  purpose: "Modern dark-theme GUI framework"
  based_on: "tkinter (Python stdlib)"
  features:
    - Dark mode by default
    - Modern widget styling
    - Blue accent color scheme
    - Smooth animations
    - High-DPI support
  widgets_used:
    - CTk (main windows)
    - CTkToplevel (modal dialogs)
    - CTkFrame (containers)
    - CTkLabel (text display)
    - CTkEntry (text input)
    - CTkButton (interactions)
    - CTkTextbox (chat areas)
    - CTkComboBox (voice selection)
  
Tkinter:
  version: "Python 3.9+ stdlib"
  purpose: "Fallback GUI framework"
  usage: "Foundation for CustomTkinter"
  reliability: "Standard library (always available)"
```

### GUI Architecture Pattern
```python
# Modal Dialog Pattern (Login)
class VPALoginWindow(ctk.CTkToplevel):
    """Modal dialog with temporary root handling"""
    
# Main Application Window Pattern  
class VPASettingsWindow(ctk.CTk):
    """Primary window with full application lifecycle"""
    
# Event Integration Pattern
def handle_user_action(self):
    """GUI actions emit events to event bus"""
    event_bus.emit("user_action", {"data": "value"})
```

## Performance & Monitoring Stack

### Performance Monitoring
```yaml
PSUtil:
  version: ">=5.9.0"
  purpose: "System performance monitoring"
  metrics:
    - CPU usage percentage
    - Memory usage (RSS/VMS)
    - Disk I/O statistics
    - Process information
  integration: "Resource monitor widget"
  targets:
    memory_limit: "<2GB total usage"
    startup_time: "<10s application startup"
    
Performance Monitor:
  type: "Custom implementation"
  file: "src/vpa/core/performance_monitor.py"  
  features:
    - Function execution time tracking
    - Memory usage monitoring
    - Performance target validation
  pattern: "@PerformanceMonitor.track_execution_time()"
```

### Resource Management
```python
# Memory Monitoring
def monitor_memory_usage() -> Dict[str, float]:
    process = psutil.Process()
    return {
        "rss_mb": process.memory_info().rss / 1024 / 1024,
        "vms_mb": process.memory_info().vms / 1024 / 1024,
        "percent": process.memory_percent()
    }

# Performance Target Validation  
def check_performance_targets() -> Dict[str, bool]:
    return {
        "startup_time_achieved": startup_time < 10.0,
        "memory_target_achieved": memory_usage_mb < 2048,
        "event_dispatch_achieved": avg_event_time < 0.01
    }
```

## Security & Cryptography Stack

### Cryptographic Operations
```yaml
Cryptography:
  version: ">=41.0.0"
  purpose: "Secure cryptographic operations"
  features:
    - Password hashing (bcrypt/scrypt)
    - Symmetric encryption (AES)
    - Key derivation functions
    - Secure token generation
  usage:
    - User password storage
    - Session token security
    - Configuration encryption
    - OAuth token handling
```

### Windows Security Integration
```yaml
PyWin32:
  version: ">=311"
  purpose: "Windows API security integration"
  features:
    - Windows authentication
    - Credential storage
    - Process security
    - File system permissions
  components:
    - win32security
    - win32cred
    - win32api
```

## Testing & Quality Stack

### Testing Framework
```yaml
PyTest:
  version: ">=7.0.0"
  purpose: "Primary testing framework"
  features:
    - Test discovery
    - Fixtures and parametrization
    - Assert introspection
    - Plugin system
  configuration: "pytest.ini"
  
PyTest-AsyncIO:
  version: ">=0.21.0" 
  purpose: "Async test support"
  usage: "@pytest.mark.asyncio"
  integration: "Event bus and voice system testing"
  
PyTest-Cov:
  version: ">=4.0.0"
  purpose: "Coverage reporting"
  target: "90%+ code coverage"
  output: "HTML reports (htmlcov/)"
  
PyTest-Mock:
  version: ">=3.0"
  purpose: "Mocking and test doubles"
  usage: "Audio system testing without hardware"
```

### Code Quality Tools (Optional)
```yaml
Black:
  version: ">=23.0"
  purpose: "Code formatting"
  configuration: "pyproject.toml"
  
MyPy:  
  version: ">=1.0"
  purpose: "Static type checking"
  configuration: "pyproject.toml"
  
Flake8:
  version: ">=6.0"
  purpose: "Linting and style checking"
```

## Network & HTTP Stack

### HTTP Client/Server
```yaml
AIOHTTP:
  version: ">=3.12.0"
  purpose: "Async HTTP client and server"
  usage:
    - OAuth callback server
    - External API integration
    - LLM provider communication
  features:
    - Async request handling
    - WebSocket support
    - SSL/TLS support
    - Session management
```

## Optional Integration Stacks

### LLM Integration (Optional)
```yaml
Ollama:
  version: ">=0.1.0"  
  purpose: "Local LLM integration"
  dependency_group: "llm"
  installation: "pip install vpa[llm]"
  usage: "Local language model responses"
  
OpenAI:
  purpose: "Cloud LLM integration (potential)"
  status: "Framework ready, not implemented"
```

### Enterprise Extensions (Optional)
```yaml
Advanced Analytics:
  components:
    - Response optimization
    - User behavior analysis
    - Performance analytics
  files:
    - advanced_analytics_proactive_optimization.py
    - continuous_improvement_monitoring.py
    
Enterprise Features:
  components:
    - Multi-user support  
    - Global deployment
    - Enterprise rollout
  files:
    - enterprise_expansion_intelligent_automation.py
    - global_scale_operations.py
```

## Dependency Management

### Core Dependencies (requirements.txt)
```pip-requirements
# Essential runtime
psutil>=5.9.0              # Performance monitoring
pyyaml>=6.0                # Configuration  
click>=8.0.0               # CLI interface

# Audio system
pyttsx3>=2.90              # TTS engine
edge-tts>=7.0.0            # Neural voices
pygame>=2.6.0              # Audio playback

# Async/network
aiohttp>=3.12.0            # HTTP client/server

# Security
cryptography>=41.0.0       # Cryptographic operations

# Testing (dev only)
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
pytest-mock>=3.0
```

### Optional Dependencies (pyproject.toml)
```toml
[project.optional-dependencies]
gui = ["customtkinter>=5.2.0"]
llm = ["ollama>=0.1.0"] 
dev = ["pytest>=7.0.0", "black>=23.0", "mypy>=1.0"]
all = ["vpa[dev,gui,llm]"]
```

### Platform-Specific Dependencies
```yaml
Windows:
  pywin32: ">=311 (auto-installed on Windows)"
  comtypes: ">=1.4.0 (COM interface support)"
  
Cross-Platform:
  pathlib: "stdlib (path handling)"
  tempfile: "stdlib (temporary files)"
  asyncio: "stdlib (async operations)"
```

## Development Environment

### Recommended Setup
```yaml
IDE: "Visual Studio Code"
Python: "3.9+ (Windows-native installation)"
Virtual_Environment: "venv or conda"
Package_Manager: "pip"
Git: "Version control"

VS_Code_Extensions:
  - Python
  - Pylance  
  - Python Debugger
  - GitLens
  - Auto Docstring
```

### Build System
```yaml
Build_Backend: "setuptools.build_meta"
Build_Requirements: ["setuptools>=68", "wheel"]
Package_Format: "wheel (.whl) and source (.tar.gz)"
Entry_Points: "console_scripts in pyproject.toml"
```

## Production Deployment Stack

### Package Distribution
```yaml
PyPI_Ready: true
Wheel_Support: true
Source_Distribution: true
Entry_Scripts: "vpa command"
Platform_Tags: "win_amd64"
```

### System Requirements
```yaml
Operating_System: "Windows 10/11 (x64)"
Python: "3.9+ (Windows-native)"
Memory: "Minimum 1GB, Target <2GB"
Disk_Space: "~500MB including dependencies"
Audio: "Windows audio system (for voice output)"
Network: "Optional (for LLM integration)"
```

## Integration Standards

### Event Bus Protocol
```python
# Event emission standard
await event_bus.emit_async("event_name", {
    "timestamp": datetime.utcnow().isoformat(),
    "source": "component_name",
    "data": payload
})

# Event subscription standard  
event_bus.subscribe("event_name", handler_function, async_callback=True)
```

### Configuration Standards
```yaml
# JSON configuration pattern
{
    "component_name": {
        "enabled": true,
        "settings": {
            "key": "value"
        },
        "metadata": {
            "version": "1.0.0",
            "updated": "2025-08-27T17:00:00Z"
        }
    }
}

# YAML configuration pattern
component_name:
  enabled: true
  settings:
    key: value
  metadata:
    version: "1.0.0"
    updated: "2025-08-27T17:00:00Z"
```

### Performance Standards
```yaml
Timing_Targets:
  startup: "<10 seconds"
  event_dispatch: "<10 milliseconds" 
  voice_synthesis: "<2 seconds"
  gui_response: "<100 milliseconds"
  
Memory_Targets:
  total_usage: "<2GB"
  startup_memory: "<500MB"
  plugin_isolation: "Error boundaries"
  
Quality_Targets:
  test_coverage: ">90%"
  error_handling: "Graceful degradation"
  logging: "Comprehensive with context"
```

---

*This technology stack documentation reflects the current implementation as specified in requirements.txt, pyproject.toml, and analyzed source code dependencies.*
