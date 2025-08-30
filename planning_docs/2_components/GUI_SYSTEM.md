# VPA GUI System

## Overview

The GUI System provides the visual interface for the VPA application, offering a modern, responsive, and intuitive user experience. Built on CustomTkinter, it implements a clean, themeable interface with chat functionality, settings panels, and plugin integration capabilities.

## Core Design Principles

### 1. Modern Aesthetics
- Clean, minimalist design language
- Support for light and dark themes
- Consistent visual elements and spacing
- Professional appearance with subtle animations

### 2. Responsiveness
- Fast UI response times (<100ms)
- Visual feedback for all actions
- Progress indicators for longer operations
- Smooth transitions between states

### 3. Accessibility
- Support for screen readers
- Keyboard navigation throughout
- High-contrast mode option
- Configurable font sizes and scaling

### 4. Extensibility
- Plugin UI integration
- Customizable components
- Theme extensibility
- Layout adaptability

## Component Architecture

### Main Window (`src/vpa/gui/main_window.py`)

The Main Window serves as the container for all UI components and manages the overall application window.

#### Class Definition

```python
class MainWindow:
    """Main application window for VPA."""
    
    def __init__(self, event_bus, config_manager):
        """Initialize the main window."""
        self._event_bus = event_bus
        self._config_manager = config_manager
        self._root = None
        self._components = {}
        self._theme_manager = ThemeManager(config_manager)
        self._is_visible = False
        self._is_minimized = False
        
    def initialize(self) -> bool:
        """Initialize the window and components."""
        try:
            # Create the root window
            self._root = CTk()
            self._root.title("Virtual Personal Assistant")
            self._root.geometry("900x600")
            self._root.protocol("WM_DELETE_WINDOW", self._on_close)
            
            # Set theme
            self._apply_theme()
            
            # Create main layout
            self._create_layout()
            
            # Initialize components
            self._init_components()
            
            # Subscribe to events
            self._subscribe_to_events()
            
            return True
        except Exception as e:
            logger.error(f"Error initializing main window: {e}")
            return False
            
    def show(self) -> None:
        """Show the main window."""
        if self._root:
            self._is_visible = True
            self._is_minimized = False
            self._root.deiconify()
            self._root.lift()
            self._root.focus_force()
            
    def hide(self) -> None:
        """Hide the main window."""
        if self._root:
            self._is_visible = False
            self._root.withdraw()
            
    def minimize(self) -> None:
        """Minimize the window."""
        if self._root:
            self._is_minimized = True
            self._root.iconify()
            
    def toggle_visibility(self) -> None:
        """Toggle window visibility."""
        if self._is_visible and not self._is_minimized:
            self.hide()
        else:
            self.show()
            
    def add_component(self, component_id: str, component) -> bool:
        """Add a component to the window."""
        # Implementation
            
    def get_component(self, component_id: str):
        """Get a component by ID."""
        # Implementation
            
    def set_title(self, title: str) -> None:
        """Set the window title."""
        if self._root:
            self._root.title(title)
            
    def is_visible(self) -> bool:
        """Check if the window is visible."""
        return self._is_visible and not self._is_minimized
            
    def _create_layout(self) -> None:
        """Create the main window layout."""
        # Implementation
            
    def _init_components(self) -> None:
        """Initialize UI components."""
        # Implementation
            
    def _subscribe_to_events(self) -> None:
        """Subscribe to system events."""
        # Implementation
            
    def _apply_theme(self) -> None:
        """Apply the current theme."""
        # Implementation
            
    def _on_close(self) -> None:
        """Handle window close event."""
        # Implementation
```

#### Layout Structure

The main window uses a grid layout with the following structure:

```
┌────────────────────────────────────────────────────────┐
│ ┌──────────────┐ ┌─────────────────────────────────┐   │
│ │              │ │                                 │   │
│ │              │ │                                 │   │
│ │  History     │ │                                 │   │
│ │  Sidebar     │ │         Chat Display           │   │
│ │              │ │                                 │   │
│ │              │ │                                 │   │
│ │              │ │                                 │   │
│ │              │ │                                 │   │
│ └──────────────┘ └─────────────────────────────────┘   │
│                                                        │
│ ┌──────────────────────────────────┐ ┌──────────────┐  │
│ │                                  │ │ Send | Voice │  │
│ │          Input Field             │ └──────────────┘  │
│ └──────────────────────────────────┘                   │
└────────────────────────────────────────────────────────┘
```

#### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+Enter | Send message |
| Ctrl+N | New chat |
| Ctrl+, | Open settings |
| Alt+V | Toggle voice input |
| Esc | Cancel current operation |
| F1 | Show help |

### Chat Interface (`src/vpa/gui/chat_interface.py`)

The Chat Interface handles display and interaction with chat messages.

#### Class Definition

```python
class ChatInterface:
    """Chat interface component for message display and interaction."""
    
    def __init__(self, parent, event_bus):
        """Initialize the chat interface."""
        self._parent = parent
        self._event_bus = event_bus
        self._messages = []
        self._frame = None
        self._chat_display = None
        self._input_field = None
        self._send_button = None
        self._voice_button = None
        self._is_typing = False
        self._is_voice_active = False
        
    def initialize(self) -> bool:
        """Initialize the chat interface."""
        try:
            # Create the chat frame
            self._frame = CTkFrame(self._parent)
            
            # Create chat display
            self._create_chat_display()
            
            # Create input area
            self._create_input_area()
            
            # Subscribe to events
            self._subscribe_to_events()
            
            return True
        except Exception as e:
            logger.error(f"Error initializing chat interface: {e}")
            return False
            
    def add_message(self, message: str, sender: str, timestamp: float = None) -> None:
        """Add a message to the chat."""
        # Implementation
            
    def clear_history(self) -> None:
        """Clear the chat history."""
        # Implementation
            
    def set_typing_indicator(self, active: bool) -> None:
        """Show or hide typing indicator."""
        # Implementation
            
    def set_voice_indicator(self, active: bool) -> None:
        """Show or hide voice activity indicator."""
        # Implementation
            
    def get_input_text(self) -> str:
        """Get the current input text."""
        # Implementation
            
    def clear_input(self) -> None:
        """Clear the input field."""
        # Implementation
            
    def _create_chat_display(self) -> None:
        """Create the chat message display area."""
        # Implementation
            
    def _create_input_area(self) -> None:
        """Create the input area."""
        # Implementation
            
    def _subscribe_to_events(self) -> None:
        """Subscribe to relevant events."""
        # Implementation
            
    def _on_send(self) -> None:
        """Handle send button click."""
        # Implementation
            
    def _on_voice_toggle(self) -> None:
        """Handle voice button toggle."""
        # Implementation
```

#### Message Structure

Each message in the chat interface is represented by a bubble with the following structure:

```
┌───────────────────────────────────────────┐
│ Sender Name                      Time     │
│ ┌───────────────────────────────────────┐ │
│ │                                       │ │
│ │ Message content that can span         │ │
│ │ multiple lines and include formatting │ │
│ │                                       │ │
│ └───────────────────────────────────────┘ │
└───────────────────────────────────────────┘
```

### Settings Panel (`src/vpa/gui/settings_panel.py`)

The Settings Panel provides a tabbed interface for configuring all aspects of the application.

#### Class Definition

```python
class SettingsPanel:
    """Settings panel for application configuration."""
    
    def __init__(self, parent, event_bus, config_manager):
        """Initialize the settings panel."""
        self._parent = parent
        self._event_bus = event_bus
        self._config_manager = config_manager
        self._window = None
        self._tabs = {}
        self._settings_groups = {}
        self._current_values = {}
        self._original_values = {}
        
    def show(self) -> None:
        """Show the settings panel."""
        if self._window and self._window.winfo_exists():
            self._window.lift()
            self._window.focus_force()
        else:
            self._create_settings_window()
            
    def hide(self) -> None:
        """Hide the settings panel."""
        if self._window and self._window.winfo_exists():
            self._window.withdraw()
            
    def add_settings_group(self, group_id: str, title: str, tab: str = "General") -> None:
        """Add a settings group."""
        # Implementation
            
    def add_setting(
        self, 
        setting_id: str, 
        group_id: str, 
        label: str, 
        control_type: str, 
        options: Dict = None
    ) -> None:
        """Add a setting to a group."""
        # Implementation
            
    def get_value(self, setting_id: str):
        """Get the current value of a setting."""
        # Implementation
            
    def apply_settings(self) -> bool:
        """Apply and save settings changes."""
        # Implementation
            
    def cancel_changes(self) -> None:
        """Cancel settings changes."""
        # Implementation
            
    def _create_settings_window(self) -> None:
        """Create the settings window."""
        # Implementation
            
    def _create_tabs(self) -> None:
        """Create the settings tabs."""
        # Implementation
            
    def _populate_settings(self) -> None:
        """Populate settings controls."""
        # Implementation
            
    def _on_apply(self) -> None:
        """Handle apply button click."""
        # Implementation
            
    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        # Implementation
            
    def _on_ok(self) -> None:
        """Handle OK button click."""
        # Implementation
```

#### Settings Categories

The settings panel is organized into the following tabs:

1. **General**
   - Application behavior
   - Startup options
   - User preferences

2. **Voice**
   - Voice selection
   - Voice parameters (rate, pitch, volume)
   - Speech recognition settings

3. **Appearance**
   - Theme selection
   - Color customization
   - Font settings
   - Layout options

4. **Plugins**
   - Plugin management
   - Plugin-specific settings
   - Plugin marketplace

5. **Advanced**
   - Performance options
   - Logging settings
   - Development options

### Theme Manager (`src/vpa/gui/theme_manager.py`)

The Theme Manager handles application theming, including light and dark modes.

#### Class Definition

```python
class ThemeManager:
    """Manager for application themes."""
    
    def __init__(self, config_manager):
        """Initialize the theme manager."""
        self._config_manager = config_manager
        self._current_theme = "dark"  # Default theme
        self._themes = {
            "dark": self._create_dark_theme(),
            "light": self._create_light_theme()
        }
        self._custom_themes = {}
        
    def initialize(self) -> bool:
        """Initialize the theme manager."""
        try:
            # Load theme from configuration
            theme_name = self._config_manager.get_value(
                "ui.theme", 
                default="dark"
            )
            return self.set_theme(theme_name)
        except Exception as e:
            logger.error(f"Error initializing theme manager: {e}")
            return False
            
    def set_theme(self, theme_name: str) -> bool:
        """Change the current theme."""
        # Implementation
            
    def get_current_theme(self) -> str:
        """Get the name of the current theme."""
        return self._current_theme
            
    def get_color(self, color_id: str) -> str:
        """Get a color from the current theme."""
        # Implementation
            
    def register_custom_theme(self, theme_name: str, theme_data: Dict[str, Any]) -> bool:
        """Register a custom theme."""
        # Implementation
            
    def get_all_themes(self) -> List[str]:
        """Get list of all available themes."""
        # Implementation
            
    def _create_dark_theme(self) -> Dict[str, str]:
        """Create the dark theme color palette."""
        return {
            "bg_primary": "#1a1a1a",
            "bg_secondary": "#2d2d2d",
            "fg_primary": "#ffffff",
            "fg_secondary": "#cccccc",
            "accent": "#0078d7",
            "accent_hover": "#1a88e1",
            "success": "#28a745",
            "warning": "#ffc107",
            "error": "#dc3545",
            "border": "#444444",
            "input_bg": "#333333",
            "input_fg": "#ffffff",
            "bubble_user": "#0078d7",
            "bubble_assistant": "#2d2d2d",
            "bubble_user_text": "#ffffff",
            "bubble_assistant_text": "#ffffff",
        }
            
    def _create_light_theme(self) -> Dict[str, str]:
        """Create the light theme color palette."""
        return {
            "bg_primary": "#f8f8f8",
            "bg_secondary": "#ffffff",
            "fg_primary": "#000000",
            "fg_secondary": "#555555",
            "accent": "#0078d7",
            "accent_hover": "#1a88e1",
            "success": "#28a745",
            "warning": "#ffc107",
            "error": "#dc3545",
            "border": "#dddddd",
            "input_bg": "#ffffff",
            "input_fg": "#000000",
            "bubble_user": "#0078d7",
            "bubble_assistant": "#eeeeee",
            "bubble_user_text": "#ffffff",
            "bubble_assistant_text": "#000000",
        }
```

### Custom Widgets

#### ChatBubble (`src/vpa/gui/widgets/chat_bubble.py`)

Custom widget for displaying chat messages in a bubble style.

```python
class ChatBubble(CTkFrame):
    """Custom widget for chat message bubbles."""
    
    def __init__(
        self, 
        master, 
        message: str, 
        sender: str, 
        timestamp: float,
        is_user: bool = False,
        **kwargs
    ):
        """Initialize a chat bubble."""
        super().__init__(master, **kwargs)
        
        self._message = message
        self._sender = sender
        self._timestamp = timestamp
        self._is_user = is_user
        
        self._create_bubble()
        
    def _create_bubble(self) -> None:
        """Create the bubble UI."""
        # Implementation
        
    def get_message(self) -> str:
        """Get the message text."""
        return self._message
        
    def get_sender(self) -> str:
        """Get the sender name."""
        return self._sender
        
    def get_timestamp(self) -> float:
        """Get the timestamp."""
        return self._timestamp
```

#### VoiceIndicator (`src/vpa/gui/widgets/voice_indicator.py`)

Visual indicator for voice activity.

```python
class VoiceIndicator(CTkFrame):
    """Visual indicator for voice activity."""
    
    def __init__(self, master, **kwargs):
        """Initialize the voice indicator."""
        super().__init__(master, **kwargs)
        
        self._active = False
        self._canvas = None
        self._animation_job = None
        self._create_indicator()
        
    def set_active(self, active: bool) -> None:
        """Set the active state of the indicator."""
        # Implementation
        
    def is_active(self) -> bool:
        """Get the active state."""
        return self._active
        
    def _create_indicator(self) -> None:
        """Create the indicator UI."""
        # Implementation
        
    def _animate(self) -> None:
        """Animate the voice indicator."""
        # Implementation
```

#### SettingsControl (`src/vpa/gui/widgets/settings_control.py`)

Factory for creating appropriate settings UI controls.

```python
class SettingsControl:
    """Factory for settings controls."""
    
    @staticmethod
    def create(
        parent,
        setting_id: str,
        label: str,
        control_type: str,
        current_value: Any,
        options: Dict = None
    ):
        """Create a settings control."""
        if control_type == "checkbox":
            return SettingsControl._create_checkbox(
                parent, setting_id, label, current_value
            )
        elif control_type == "dropdown":
            return SettingsControl._create_dropdown(
                parent, setting_id, label, current_value, options
            )
        elif control_type == "slider":
            return SettingsControl._create_slider(
                parent, setting_id, label, current_value, options
            )
        elif control_type == "color":
            return SettingsControl._create_color_picker(
                parent, setting_id, label, current_value
            )
        elif control_type == "text":
            return SettingsControl._create_text_input(
                parent, setting_id, label, current_value
            )
        else:
            raise ValueError(f"Unknown control type: {control_type}")
            
    @staticmethod
    def _create_checkbox(parent, setting_id: str, label: str, current_value: bool):
        """Create a checkbox control."""
        # Implementation
            
    @staticmethod
    def _create_dropdown(
        parent, 
        setting_id: str, 
        label: str, 
        current_value: str,
        options: Dict
    ):
        """Create a dropdown control."""
        # Implementation
            
    # Other control creation methods...
```

## Event Integration

### Emitted Events

| Event Name | Description | Data |
|------------|-------------|------|
| `user.input.submitted` | User submitted text input | `{"text": str, "timestamp": float}` |
| `user.voice.requested` | User requested voice input | `{"timestamp": float}` |
| `user.voice.cancelled` | User cancelled voice input | `{"timestamp": float}` |
| `ui.settings.changed` | Settings were changed | `{"setting": str, "value": Any}` |
| `ui.theme.changed` | UI theme was changed | `{"theme": str}` |
| `ui.window.closed` | Main window was closed | `{"reason": str}` |
| `ui.window.shown` | Main window was shown | `{"timestamp": float}` |
| `ui.chat.cleared` | Chat history was cleared | `{"timestamp": float}` |

### Subscribed Events

| Event Name | Description | Handler |
|------------|-------------|---------|
| `assistant.response.received` | Assistant response | `_handle_assistant_response` |
| `audio.speech.started` | TTS started | `_handle_speech_started` |
| `audio.speech.completed` | TTS completed | `_handle_speech_completed` |
| `audio.recognition.started` | SR started | `_handle_recognition_started` |
| `audio.recognition.result` | SR result | `_handle_recognition_result` |
| `plugin.ui.update` | Plugin UI update | `_handle_plugin_ui_update` |
| `system.shutdown.requested` | System shutdown | `_handle_shutdown_request` |

## Configuration

### UI Settings Schema

```json
{
  "ui": {
    "theme": {
      "type": "string",
      "default": "dark",
      "enum": ["dark", "light", "high_contrast"],
      "description": "UI theme"
    },
    "font_size": {
      "type": "string",
      "default": "medium",
      "enum": ["small", "medium", "large"],
      "description": "UI font size"
    },
    "startup_minimized": {
      "type": "boolean",
      "default": false,
      "description": "Start application minimized"
    },
    "show_typing_indicator": {
      "type": "boolean",
      "default": true,
      "description": "Show typing indicator"
    },
    "show_timestamps": {
      "type": "boolean",
      "default": true,
      "description": "Show message timestamps"
    },
    "window": {
      "width": {
        "type": "number",
        "default": 900,
        "description": "Window width"
      },
      "height": {
        "type": "number",
        "default": 600,
        "description": "Window height"
      },
      "position_x": {
        "type": "number",
        "default": null,
        "description": "Window X position"
      },
      "position_y": {
        "type": "number",
        "default": null,
        "description": "Window Y position"
      }
    }
  }
}
```

## Plugin UI Integration

### Plugin UI Component Registration

Plugins can register UI components that will be integrated into the main interface:

```python
async def get_ui_components(self) -> Dict[str, Any]:
    """Return UI components for this plugin."""
    return {
        "settings_panel": self._create_settings_panel(),
        "chat_action": {
            "name": "Weather",
            "icon": "weather_icon.png",
            "tooltip": "Check weather",
            "callback": self._on_weather_action
        },
        "sidebar_item": {
            "name": "Weather Forecast",
            "icon": "forecast_icon.png",
            "callback": self._show_forecast
        }
    }
```

### Plugin Settings Integration

Plugin settings are automatically integrated into the Settings Panel:

```python
# In plugin.json
{
  "id": "weather_plugin",
  "name": "Weather Plugin",
  "settings": {
    "api_key": {
      "type": "string",
      "default": "",
      "description": "API key for weather service"
    },
    "units": {
      "type": "string",
      "default": "metric",
      "enum": ["metric", "imperial"],
      "description": "Units for weather data"
    },
    "location": {
      "type": "string",
      "default": "auto",
      "description": "Default location"
    }
  }
}
```

## Accessibility Features

### Keyboard Navigation

- Tab order follows logical flow
- Focus indicators for all interactive elements
- Keyboard shortcuts for common actions
- Escape key exits dialogs and modals

### Screen Reader Support

- Proper ARIA labels for all elements
- Meaningful alternative text for images
- Announcement of state changes
- Structural semantics for navigation

### Visual Accessibility

- High-contrast mode
- Adjustable font sizes
- Configurable color schemes
- Sufficient color contrast ratios

## Performance Optimization

### Rendering Optimizations

- Virtualized list for chat messages
- Lazy loading of images and content
- UI operations on separate thread
- Throttling of rapid updates

### Memory Management

- Limit chat history size
- Clean up unused resources
- Optimize image storage
- Efficient data structures

## Responsive Design

The UI adapts to different window sizes with the following breakpoints:

| Size | Width | Layout Adjustments |
|------|-------|-------------------|
| Small | <600px | Collapse sidebar, single column layout |
| Medium | 600-900px | Narrower sidebar, adjusted proportions |
| Large | >900px | Full layout with optimal proportions |

## Error Handling

### UI Error Boundaries

- Each major component has error boundary
- Errors contained within component hierarchy
- Graceful fallback UI for failed components
- Error reporting without crashing application

### User Feedback

- Toast notifications for errors
- Status indicators for operations
- Progress feedback for long-running tasks
- Helpful error messages with recovery options

## Testing

### Unit Tests

- Test individual components in isolation
- Test theme application and switching
- Verify event emission and handling
- Test accessibility features

### UI Tests

- Verify component rendering
- Test user interaction flows
- Validate keyboard navigation
- Test screen reader compatibility

## Related Documents

- [Implementation Plan Phase 3: GUI Framework](../3_implementation_roadmap/PHASE_3_GUI_FRAMEWORK.md)
- [Performance Targets](../1_architecture/PERFORMANCE_TARGETS.md)
- [Accessibility Standards](../4_technical_standards/DOCUMENTATION_STANDARDS.md)
- [Plugin Communication Patterns](../1_architecture/PLUGIN_ARCHITECTURE.md)

---

*Document created: August 29, 2025*  
*Version: 1.0*
