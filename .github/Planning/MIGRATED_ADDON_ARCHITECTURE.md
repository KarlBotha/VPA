# VPA Addon Architecture & Integration

## 1. Core Architecture: Base App vs Addon Separation

### 1.1 Base App Responsibilities

The base application provides the core infrastructure and services:

- **Event Bus System**: Central event routing and management
- **Plugin/Addon Management**: Discovery, loading, and lifecycle management
- **Voice System**: Azure voice integration and speech synthesis
- **Configuration System**: Application-wide settings management
- **Performance Monitoring**: Resource tracking and optimization
- **GUI Framework**: Window management and core UI
- **Local Storage**: File system access and document management
- **Security**: Authentication, encryption, and credential management
- **Windows Integration**: System tray, notifications, and OS integration
- **Export System**: PDF and RTF export capabilities
- **Image Processing**: Computer vision capabilities

### 1.2 Addon Responsibilities

Addons are self-contained modules that extend functionality:

- **Domain-Specific Logic**: Weather, time, system info, etc.
- **Custom UI Components**: Addon-specific interfaces
- **External API Integration**: Service-specific API calls
- **Custom Data Storage**: Addon-specific data persistence
- **Custom Event Handlers**: Specialized event processing
- **Custom Export Templates**: Addon-specific export formats

## 2. Addon Management System

### 2.1 Addon Discovery and Loading

```python
class AddonManager:
    def __init__(self, event_bus, config_manager):
        self.event_bus = event_bus
        self.config_manager = config_manager
        self.addons = {}
        self.addon_paths = [
            "src/vpa/addons/",
            "addons/",
            os.path.expanduser("~/.vpa/addons/")
        ]
        self.cache_file = "src/addon_cache.json"
    
    def discover_addons(self):
        """Discover and catalog available addons"""
        # Implementation for addon discovery
    
    def load_addon(self, addon_id):
        """Load a specific addon dynamically"""
        # Implementation for addon loading
    
    def unload_addon(self, addon_id):
        """Safely unload an addon"""
        # Implementation for addon unloading
    
    def get_addon_info(self, addon_id=None):
        """Get information about addons"""
        # Implementation for addon info retrieval
```

### 2.2 Addon Interface

```python
class Addon:
    """Base class for all VPA addons"""
    
    @property
    def id(self) -> str:
        """Unique identifier for this addon"""
        raise NotImplementedError
    
    @property
    def name(self) -> str:
        """Human-readable name"""
        raise NotImplementedError
    
    @property
    def version(self) -> str:
        """Addon version"""
        raise NotImplementedError
    
    @property
    def description(self) -> str:
        """Addon description"""
        raise NotImplementedError
    
    @property
    def dependencies(self) -> List[str]:
        """List of addon dependencies"""
        return []
    
    @property
    def api_requirements(self) -> Dict[str, Dict]:
        """API requirements for this addon"""
        return {}
    
    def initialize(self) -> bool:
        """Initialize the addon"""
        pass
    
    def cleanup(self) -> bool:
        """Clean up resources before unloading"""
        pass
    
    def can_handle(self, event_type: str, event_data: Dict) -> bool:
        """Determine if this addon can handle an event"""
        return False
    
    async def handle_event(self, event_type: str, event_data: Dict) -> Dict:
        """Handle an event"""
        pass
    
    def get_ui_components(self) -> Dict:
        """Get UI components provided by this addon"""
        return {}
    
    def get_settings_schema(self) -> Dict:
        """Get settings schema for this addon"""
        return {}
```

## 3. Specific Addon Types

### 3.1 Weather Addon

```python
class WeatherAddon(Addon):
    @property
    def id(self) -> str:
        return "weather"
    
    @property
    def name(self) -> str:
        return "Weather Information"
    
    @property
    def api_requirements(self) -> Dict[str, Dict]:
        return {
            "openweathermap": {
                "required": True,
                "api_key": True,
                "url": "https://api.openweathermap.org/data/2.5/"
            }
        }
    
    def initialize(self) -> bool:
        # Check API key configuration
        # Subscribe to relevant events
        self.event_bus.subscribe("query_weather", self.handle_weather_query)
        return True
    
    def can_handle(self, event_type: str, event_data: Dict) -> bool:
        if event_type == "user_query":
            query = event_data.get("text", "").lower()
            weather_keywords = ["weather", "temperature", "forecast", "rain", "sunny"]
            return any(keyword in query for keyword in weather_keywords)
        return event_type == "query_weather"
    
    async def handle_event(self, event_type: str, event_data: Dict) -> Dict:
        if event_type == "user_query":
            # Extract location from query
            location = self._extract_location(event_data["text"])
            return await self._get_weather(location)
        elif event_type == "query_weather":
            location = event_data.get("location")
            return await self._get_weather(location)
    
    async def _get_weather(self, location: str) -> Dict:
        # Call OpenWeatherMap API
        # Process and format results
        # Return formatted weather data
        pass
```

### 3.2 Microsoft Integration Addon

```python
class MicrosoftAddon(Addon):
    @property
    def id(self) -> str:
        return "microsoft"
    
    @property
    def name(self) -> str:
        return "Microsoft Services"
    
    @property
    def api_requirements(self) -> Dict[str, Dict]:
        return {
            "microsoft_graph": {
                "required": True,
                "oauth": True,
                "scopes": ["User.Read", "Mail.Read", "Calendars.Read"],
                "redirect_uri": "http://localhost:8000/auth/callback",
                "tenant": "common"
            }
        }
    
    def initialize(self) -> bool:
        # Set up OAuth flow
        # Subscribe to relevant events
        self.event_bus.subscribe("microsoft_calendar", self.handle_calendar)
        self.event_bus.subscribe("microsoft_email", self.handle_email)
        return True
    
    async def handle_event(self, event_type: str, event_data: Dict) -> Dict:
        if event_type == "user_query":
            # Determine if this is a Microsoft-related query
            # Process query accordingly
            pass
        elif event_type == "microsoft_calendar":
            return await self._get_calendar_events()
        elif event_type == "microsoft_email":
            return await self._get_emails()
    
    async def _get_calendar_events(self) -> Dict:
        # Authenticate with Microsoft Graph
        # Retrieve calendar events
        # Format and return events
        pass
    
    async def _get_emails(self) -> Dict:
        # Authenticate with Microsoft Graph
        # Retrieve emails
        # Format and return emails
        pass
```

### 3.3 Google Integration Addon

```python
class GoogleAddon(Addon):
    @property
    def id(self) -> str:
        return "google"
    
    @property
    def name(self) -> str:
        return "Google Services"
    
    @property
    def api_requirements(self) -> Dict[str, Dict]:
        return {
            "google_oauth": {
                "required": True,
                "oauth": True,
                "scopes": [
                    "https://www.googleapis.com/auth/gmail.readonly",
                    "https://www.googleapis.com/auth/calendar.readonly"
                ],
                "redirect_uri": "http://localhost:8000/auth/callback"
            }
        }
    
    def initialize(self) -> bool:
        # Set up OAuth flow
        # Subscribe to relevant events
        return True
    
    # Similar methods as MicrosoftAddon for handling events
    # and interacting with Google APIs
```

### 3.4 Windows Integration Addon

```python
class WindowsAddon(Addon):
    @property
    def id(self) -> str:
        return "windows"
    
    @property
    def name(self) -> str:
        return "Windows Integration"
    
    @property
    def api_requirements(self) -> Dict[str, Dict]:
        return {
            "win32api": {
                "required": True,
                "native": True
            }
        }
    
    def initialize(self) -> bool:
        # Set up Windows API hooks
        # Subscribe to relevant events
        return True
    
    def can_handle(self, event_type: str, event_data: Dict) -> bool:
        if event_type == "user_query":
            query = event_data.get("text", "").lower()
            windows_keywords = ["open file", "open folder", "screenshot", "lock computer"]
            return any(keyword in query for keyword in windows_keywords)
        return False
    
    async def handle_event(self, event_type: str, event_data: Dict) -> Dict:
        if event_type == "user_query":
            # Process Windows-related commands
            command = self._extract_command(event_data["text"])
            return await self._execute_windows_command(command)
    
    async def _execute_windows_command(self, command: Dict) -> Dict:
        # Execute Windows command using PyWin32
        # Return results
        pass
```

## 4. API Registry and Management

### 4.1 API Registry Structure

```python
class APIRegistry:
    """Central registry for managing API requirements and credentials"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.apis = {}
        self.oauth_flows = {}
        self.rate_limiters = {}
    
    def register_api(self, api_id, requirements):
        """Register API requirements"""
        self.apis[api_id] = requirements
    
    def get_api_client(self, api_id):
        """Get configured client for an API"""
        pass
    
    def check_api_configuration(self, api_id):
        """Check if an API is properly configured"""
        pass
    
    def setup_oauth_flow(self, api_id):
        """Set up OAuth flow for an API"""
        pass
    
    def handle_oauth_callback(self, api_id, code):
        """Handle OAuth callback"""
        pass
    
    def get_api_credentials(self, api_id):
        """Get credentials for an API (encrypted)"""
        pass
    
    def set_api_credentials(self, api_id, credentials):
        """Set credentials for an API (encrypted)"""
        pass
```

### 4.2 Rate Limiting and Quota Management

```python
class APIRateLimiter:
    """Rate limiting for API calls"""
    
    def __init__(self, api_id, limits):
        self.api_id = api_id
        self.limits = limits
        self.call_history = {}
    
    async def acquire(self, endpoint=None):
        """Acquire permission to make an API call"""
        pass
    
    def release(self, endpoint=None):
        """Release after API call completion"""
        pass
    
    def update_limits(self, response_headers):
        """Update rate limits based on response headers"""
        pass
```

## 5. Addon Loading and Lifecycle

### 5.1 Addon Discovery Process

1. Scan directory paths for Python modules with addon definitions
2. Check addon cache for previously discovered addons
3. For each potential addon:
   - Load module dynamically
   - Check for Addon subclass implementations
   - Validate addon interface compliance
   - Add to addon registry with metadata

### 5.2 Addon Initialization Process

1. Sort addons by dependencies and priority
2. For each addon to be initialized:
   - Check dependencies are satisfied
   - Verify API requirements
   - Call initialize() method
   - Subscribe to event types
   - Register UI components
   - Update addon status

### 5.3 Addon API Verification

1. For each addon's API requirements:
   - Check if API is registered in APIRegistry
   - Verify credentials are available
   - Test API connectivity
   - Configure rate limits
   - Set up fallback mechanisms

## 6. Windows API Integration

### 6.1 File System Access

```python
class FileSystemManager:
    """Manages file system access for the application"""
    
    def list_directory(self, path):
        """List contents of a directory"""
        pass
    
    def read_file(self, path):
        """Read file contents"""
        pass
    
    def write_file(self, path, content):
        """Write content to file"""
        pass
    
    def delete_file(self, path):
        """Delete a file"""
        pass
    
    def watch_directory(self, path, callback):
        """Set up directory change monitoring"""
        pass
```

### 6.2 System Tray Integration

```python
class SystemTrayManager:
    """Manages system tray icon and menu"""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.icon = None
        self.menu_items = []
    
    def setup_tray(self, icon_path, tooltip):
        """Set up system tray icon"""
        pass
    
    def add_menu_item(self, label, callback):
        """Add item to tray menu"""
        pass
    
    def show_notification(self, title, message, duration=5):
        """Show system notification"""
        pass
    
    def remove_tray(self):
        """Remove tray icon"""
        pass
```

### 6.3 Windows Registry Access

```python
class RegistryManager:
    """Manages Windows Registry access"""
    
    def get_registry_value(self, key, value_name):
        """Get value from registry"""
        pass
    
    def set_registry_value(self, key, value_name, value_data, value_type):
        """Set value in registry"""
        pass
    
    def delete_registry_value(self, key, value_name):
        """Delete value from registry"""
        pass
    
    def set_startup(self, enable=True):
        """Configure application to run at startup"""
        pass
```

## 7. LLM Integration Framework (Future)

### 7.1 LLM Manager Structure

```python
class LLMManager:
    """Manages LLM integration for future expansion"""
    
    def __init__(self, event_bus, config_manager):
        self.event_bus = event_bus
        self.config_manager = config_manager
        self.models = {}
        self.default_model = None
    
    def discover_local_models(self):
        """Discover locally installed LLM models"""
        pass
    
    def recommend_models(self, system_specs):
        """Recommend suitable models based on system specifications"""
        pass
    
    async def install_model(self, model_id, model_url):
        """Install a model with progress tracking"""
        pass
    
    async def query_model(self, prompt, model_id=None, parameters=None):
        """Query a model with a prompt"""
        pass
    
    def uninstall_model(self, model_id):
        """Uninstall a model and free resources"""
        pass
```

### 7.2 LLM Installation Assistant

```python
class LLMInstallationAssistant:
    """Guides users through LLM selection and installation"""
    
    def __init__(self, llm_manager, event_bus):
        self.llm_manager = llm_manager
        self.event_bus = event_bus
    
    def check_system_requirements(self):
        """Check system capabilities for LLM compatibility"""
        pass
    
    def get_recommendations(self):
        """Get recommended models for this system"""
        pass
    
    async def guide_installation(self, model_id):
        """Guide user through installation process"""
        pass
    
    def configure_model(self, model_id, settings):
        """Configure model settings"""
        pass
```

## 8. Event Types for Addon Communication

### 8.1 Standard Event Types

| Event Type | Description | Data Structure | Source | Consumers |
|------------|-------------|----------------|--------|-----------|
| `addon_loaded` | Addon loaded successfully | `{"addon_id": str}` | AddonManager | App, UI |
| `addon_failed` | Addon failed to load | `{"addon_id": str, "error": str}` | AddonManager | App, UI |
| `user_query` | User input query | `{"text": str, "timestamp": float}` | UI | Addons |
| `query_result` | Result of user query | `{"response": str, "source": str}` | Addons | UI |
| `api_request` | Request to an external API | `{"api": str, "endpoint": str}` | Addons | APIRegistry |
| `api_response` | Response from an external API | `{"api": str, "data": dict}` | APIRegistry | Addons |
| `api_error` | Error from an external API | `{"api": str, "error": str}` | APIRegistry | Addons |
| `file_operation` | File system operation | `{"operation": str, "path": str}` | App, Addons | FileSystemManager |
| `settings_changed` | Settings were updated | `{"section": str, "settings": dict}` | UI | App, Addons |
| `export_request` | Request to export data | `{"format": str, "data": dict}` | UI, Addons | ExportManager |

### 8.2 Addon-Specific Event Types

| Addon | Event Type | Description | Data Structure |
|-------|------------|-------------|----------------|
| Weather | `weather_query` | Weather information request | `{"location": str, "forecast": bool}` |
| Microsoft | `ms_calendar_query` | Calendar information request | `{"start_date": str, "end_date": str}` |
| Microsoft | `ms_email_query` | Email information request | `{"folder": str, "count": int}` |
| Google | `google_calendar_query` | Calendar information request | `{"start_date": str, "end_date": str}` |
| Google | `google_email_query` | Email information request | `{"folder": str, "count": int}` |
| Windows | `windows_command` | Windows operation request | `{"command": str, "params": dict}` |

## 9. Addon Configuration and Settings

### 9.1 Addon Settings Schema

```json
{
  "addon_id": "weather",
  "settings": {
    "api_key": {
      "type": "string",
      "sensitive": true,
      "description": "OpenWeatherMap API key",
      "required": true
    },
    "default_location": {
      "type": "string",
      "description": "Default location for weather queries",
      "default": "London"
    },
    "units": {
      "type": "enum",
      "options": ["metric", "imperial"],
      "default": "metric",
      "description": "Units for temperature and measurements"
    },
    "auto_update": {
      "type": "boolean",
      "default": true,
      "description": "Automatically update weather information"
    },
    "update_interval": {
      "type": "integer",
      "default": 30,
      "min": 15,
      "max": 120,
      "description": "Update interval in minutes",
      "depends_on": {
        "auto_update": true
      }
    }
  }
}
```

### 9.2 Addon Configuration Storage

Addons store their configuration in the central configuration system:

```
config/
├── addons/
│   ├── weather.yaml
│   ├── microsoft.yaml
│   ├── google.yaml
│   └── windows.yaml
├── api_credentials.yaml (encrypted)
├── default.yaml
└── ui_settings.yaml
```

## 10. Conclusion

This architecture document provides a comprehensive framework for separating base app functionality from addon capabilities in the VPA system. By following this design:

1. **Clear Separation of Concerns**: The base app provides core infrastructure, while addons implement domain-specific functionality
2. **Standardized Interfaces**: All addons follow a consistent interface for discoverability and lifecycle management
3. **API Integration**: Centralized API registry manages credentials, rate limiting, and error handling
4. **Event-Driven Communication**: All inter-component communication happens through the event bus
5. **Future-Proof Design**: Architecture supports future extensions like LLM integration

Implementation should follow these patterns to ensure a maintainable, extensible system with clear boundaries between core functionality and addons.

---

*This document was created on August 27, 2025, to guide the implementation of the VPA addon architecture.*
