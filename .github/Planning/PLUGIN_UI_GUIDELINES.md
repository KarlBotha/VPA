# Plugin UI Integration Guidelines

## Overview

This document outlines the standard practices, patterns, and requirements for integrating plugin UIs within the VPA application. Following these guidelines ensures consistent user experience, proper event handling, and maintainable UI code across all plugins.

## Table of Contents

1. [Core Principles](#1-core-principles)
2. [UI Component Integration](#2-ui-component-integration)
3. [Event-Driven UI Pattern](#3-event-driven-ui-pattern)
4. [Styling and Theming](#4-styling-and-theming)
5. [Accessibility Requirements](#5-accessibility-requirements)
6. [Performance Guidelines](#6-performance-guidelines)
7. [Integration Testing](#7-integration-testing)
8. [Best Practices](#8-best-practices)
9. [Example Implementations](#9-example-implementations)

## 1. Core Principles

### 1.1 Separation of Concerns

All plugin UI components must follow strict separation between:
- **Business Logic**: Handled by the plugin core class
- **UI Logic**: Managed by the plugin's UI components
- **Event Communication**: Through the central event bus

```python
# ❌ Don't mix business logic with UI
class BadPluginUI:
    def __init__(self):
        self.button = Button("Process")
        self.button.on_click(self.process_data)
    
    def process_data(self):
        # Business logic mixed with UI
        result = complex_calculation()
        self.update_display(result)

# ✅ Proper separation of concerns
class GoodPluginUI:
    def __init__(self, plugin_id):
        from vpa.core.events import event_bus
        
        self.button = Button("Process")
        self.plugin_id = plugin_id
        
        # UI only emits events, doesn't process
        self.button.on_click(lambda: event_bus.emit_async(
            "plugin.request.process", 
            {"plugin_id": self.plugin_id}
        ))
        
        # Subscribe to receive results
        event_bus.subscribe(
            f"plugin.response.{plugin_id}", 
            self.update_display,
            async_callback=True
        )
    
    async def update_display(self, event_data):
        # UI only handles display updates
        self.result_label.text = event_data.get("result", "")
```

### 1.2 Non-blocking UI

Plugin UIs must never block the main thread. All potentially time-consuming operations must be:
1. Offloaded to background tasks
2. Processed asynchronously
3. Provide visual feedback during processing

## 2. UI Component Integration

### 2.1 Registration Pattern

Plugins with UI components must register them with the main application using the standard registration pattern:

```python
from vpa.core.plugins import Plugin
from vpa.core.events import event_bus

class WeatherPlugin(Plugin):
    @property
    def name(self) -> str:
        return "weather_plugin"
    
    async def initialize(self):
        # Register main UI component
        await event_bus.emit_async("ui.register.plugin", {
            "plugin_id": self.name,
            "component_type": "settings",
            "component_factory": self.create_settings_ui,
            "display_name": "Weather Settings",
            "priority": 5
        })
        
        # Register chat component
        await event_bus.emit_async("ui.register.plugin", {
            "plugin_id": self.name,
            "component_type": "chat_card",
            "component_factory": self.create_chat_card,
            "conditions": {"message_type": "weather"}
        })
    
    def create_settings_ui(self, parent):
        # Return settings UI component
        from .ui.settings_panel import WeatherSettings
        return WeatherSettings(parent, self.config)
    
    def create_chat_card(self, parent, message_data):
        # Return specialized chat card
        from .ui.weather_card import WeatherCard
        return WeatherCard(parent, message_data)
```

### 2.2 Integration Points

Plugins may provide UI components for the following integration points:

| Integration Point | Event | Purpose | Component Type |
|-------------------|-------|---------|---------------|
| Settings Panel | `ui.register.plugin` | Plugin configuration | Settings panel |
| Chat Interface | `ui.register.plugin` | Custom message rendering | Chat card |
| System Tray | `ui.register.tray_item` | System tray menu items | Menu item |
| Main Window | `ui.register.widget` | Additional UI widgets | Widget |
| Notification Area | `ui.notification.show` | Custom notifications | Notification |

## 3. Event-Driven UI Pattern

### 3.1 Standard UI Events

All plugin UI components must use the standard event system for communication:

| Event Name | Direction | Purpose | Example Payload |
|------------|-----------|---------|----------------|
| `plugin.ui.update` | Core → UI | Update UI with new data | `{"plugin_id": "weather", "data": {...}}` |
| `plugin.ui.action` | UI → Core | User performed action | `{"plugin_id": "weather", "action": "refresh"}` |
| `plugin.ui.state` | UI → Core | UI state changed | `{"plugin_id": "weather", "state": "expanded"}` |

### 3.2 Event Handler Pattern

```python
from vpa.core.events import event_bus
from vpa.gui.components import PluginComponent

class WeatherWidget(PluginComponent):
    def __init__(self, parent, plugin_id):
        super().__init__(parent)
        self.plugin_id = plugin_id
        
        # Set up UI elements
        self._setup_ui()
        
        # Register event handlers
        self._subscribe_to_events()
    
    def _setup_ui(self):
        # Create and layout UI elements
        self.refresh_button = Button("Refresh")
        self.refresh_button.on_click(self._on_refresh_click)
        # ... more UI setup
    
    def _subscribe_to_events(self):
        # Subscribe to events with proper context
        self._unsubscribe_funcs = [
            event_bus.subscribe(
                f"plugin.ui.update.{self.plugin_id}",
                self._handle_update,
                async_callback=True
            )
        ]
    
    async def _handle_update(self, event_data):
        # Update UI safely
        await self._safe_ui_update(lambda: self._update_display(event_data))
    
    def _on_refresh_click(self):
        # Emit user action event
        event_bus.emit("plugin.ui.action", {
            "plugin_id": self.plugin_id,
            "action": "refresh",
            "source": "refresh_button"
        })
    
    async def _safe_ui_update(self, update_func):
        # Safely update UI from any thread
        try:
            # Use appropriate mechanism to invoke on UI thread
            # This is framework-dependent
            update_func()
        except Exception as e:
            logging.error(f"UI update failed: {e}")
    
    def cleanup(self):
        # Clean up event subscriptions
        for unsub in self._unsubscribe_funcs:
            unsub()
```

## 4. Styling and Theming

### 4.1 Theme Compliance

All plugin UI components must use the VPA theming system:

```python
from vpa.gui.theme import get_theme, ThemeManager

class ThemedPluginUI:
    def __init__(self, parent):
        self.parent = parent
        self.theme = get_theme()
        
        # Use theme colors
        self.background_color = self.theme.get("background")
        self.text_color = self.theme.get("text")
        
        # Subscribe to theme changes
        ThemeManager.subscribe(self.on_theme_changed)
    
    def on_theme_changed(self, new_theme):
        self.theme = new_theme
        self.background_color = new_theme.get("background")
        self.text_color = new_theme.get("text")
        self.update_appearance()
    
    def update_appearance(self):
        # Apply theme to all components
        # Implementation depends on UI framework
        pass
```

### 4.2 Style Guidelines

Plugin UIs must adhere to these style standards:

| Element | Guideline |
|---------|-----------|
| Font | System font, size 12-14px for content, 16-18px for headings |
| Color | Use theme colors only, no hardcoded values |
| Spacing | 8px base unit, with 8/16/24px standard spacing |
| Layout | Responsive, min width 300px, graceful resize |
| Icons | Use standard icon set from `vpa.gui.icons` |

## 5. Accessibility Requirements

### 5.1 Required Accessibility Features

All plugin UIs must implement:

1. **Keyboard Navigation**: Full tab order implementation
2. **Screen Reader Support**: Proper ARIA labels and roles
3. **Color Contrast**: Minimum 4.5:1 for text, 3:1 for UI elements
4. **Resizable Text**: Text scales properly with system settings

### 5.2 Accessibility Implementation

```python
class AccessiblePluginUI:
    def __init__(self, parent):
        # Set proper tab order
        self.button1.tabOrder = 1
        self.input1.tabOrder = 2
        
        # Set ARIA labels
        self.button1.aria_label = "Refresh weather data"
        self.input1.aria_label = "Enter city name"
        
        # High contrast support
        from vpa.gui.accessibility import get_high_contrast_mode
        if get_high_contrast_mode():
            self.apply_high_contrast_theme()
```

## 6. Performance Guidelines

### 6.1 Performance Requirements

Plugin UIs must meet these performance targets:

| Metric | Target |
|--------|--------|
| Initial Load Time | < 300ms |
| Action Response Time | < 100ms |
| Memory Usage | < 50MB per plugin |
| Animation Frame Rate | ≥ 60 FPS |

### 6.2 Performance Optimization Techniques

1. **Lazy Loading**: Only load UI components when needed
2. **Virtualization**: For lists/grids with many items
3. **Efficient Rendering**: Minimize repaints and reflows
4. **Memory Management**: Clean up resources properly

```python
from vpa.gui.optimization import VirtualizedList, LazyComponent

class PerformantPluginUI:
    def __init__(self, parent):
        # Lazy load expensive components
        self.settings_panel = LazyComponent(
            lambda: ExpensiveSettingsPanel(self)
        )
        
        # Virtualize long lists
        self.results_list = VirtualizedList(
            item_height=48,
            item_renderer=self.render_result_item
        )
    
    def render_result_item(self, item_data, index):
        # Only render items in view
        return ResultItemView(item_data)
```

## 7. Integration Testing

### 7.1 UI Test Requirements

All plugin UIs must include tests for:

1. **Component Rendering**: Verify visual appearance
2. **Event Handling**: Confirm proper event emission
3. **Accessibility**: Validate a11y features
4. **Theme Compliance**: Test with multiple themes

### 7.2 Test Implementation

```python
import pytest
from vpa.testing.ui import UITestHarness

class TestWeatherPluginUI:
    @pytest.fixture
    def ui_harness(self):
        return UITestHarness("weather_plugin")
    
    def test_component_renders(self, ui_harness):
        # Test component renders properly
        component = ui_harness.render_component("settings")
        assert component is not None
        assert component.find_by_id("location_input") is not None
    
    def test_event_emission(self, ui_harness):
        # Test UI emits proper events
        component = ui_harness.render_component("settings")
        
        # Track events
        emitted_events = ui_harness.track_events("plugin.ui.action")
        
        # Trigger UI action
        refresh_button = component.find_by_id("refresh_button")
        refresh_button.click()
        
        # Verify event was emitted
        assert len(emitted_events) == 1
        assert emitted_events[0]["action"] == "refresh"
    
    def test_theme_compliance(self, ui_harness):
        # Test with multiple themes
        component = ui_harness.render_component("settings")
        
        # Switch theme
        ui_harness.set_theme("dark")
        
        # Verify colors match theme
        title = component.find_by_id("panel_title")
        assert title.get_computed_style("color") == ui_harness.get_theme_color("text")
```

## 8. Best Practices

### 8.1 UI Component Lifecycle

Plugin UIs must properly manage lifecycle:

1. **Initialization**: Register event handlers
2. **State Management**: Maintain clean state model
3. **Cleanup**: Unsubscribe from events, release resources

```python
class WellBehavedPluginUI:
    def __init__(self, parent, plugin_id):
        self.plugin_id = plugin_id
        self.subscriptions = []
        
        # Initialize UI and subscribe to events
        self._initialize()
    
    def _initialize(self):
        # Set up UI components
        self._setup_ui()
        
        # Subscribe to events
        self.subscriptions = [
            event_bus.subscribe(f"plugin.ui.update.{self.plugin_id}", self._on_update),
            event_bus.subscribe("ui.theme.changed", self._on_theme_changed)
        ]
    
    def cleanup(self):
        # Unsubscribe from all events
        for unsubscribe in self.subscriptions:
            unsubscribe()
        
        # Release resources
        self._release_resources()
    
    def _release_resources(self):
        # Clean up any resources
        # Example: Close files, release memory, etc.
        pass
```

### 8.2 Error Handling

Robust error handling in plugin UIs:

```python
class RobustPluginUI:
    def __init__(self, parent):
        self.parent = parent
        
        try:
            self._initialize()
        except Exception as e:
            self._handle_initialization_error(e)
    
    def _handle_initialization_error(self, error):
        # Log detailed error
        logging.error(f"Plugin UI initialization failed: {error}", exc_info=True)
        
        # Show fallback UI
        from vpa.gui.components import ErrorPanel
        self.error_panel = ErrorPanel(
            self.parent,
            "Plugin UI could not be loaded",
            str(error),
            retry_action=self._initialize
        )
    
    async def _on_update(self, event_data):
        try:
            # Process update
            self._update_ui(event_data)
        except Exception as e:
            # Log and handle error
            logging.error(f"UI update failed: {e}")
            
            # Show error in UI
            self.status_label.text = "Error updating display"
            
            # Report error
            await event_bus.emit_async("plugin.error", {
                "plugin_id": self.plugin_id,
                "component": "ui",
                "error": str(e),
                "event": "update"
            })
```

## 9. Example Implementations

### 9.1 Settings Panel Example

```python
from vpa.core.events import event_bus
from vpa.gui.components import SettingsPanel, TextField, Button, ToggleSwitch

class WeatherSettingsPanel(SettingsPanel):
    def __init__(self, parent, plugin_id, config):
        super().__init__(parent, "Weather Settings")
        self.plugin_id = plugin_id
        self.config = config
        
        self._setup_ui()
        self._subscribe_to_events()
        
    def _setup_ui(self):
        # Location settings
        self.add_section("Location")
        self.location_input = self.add_component(
            TextField(
                label="Default Location",
                value=self.config.get("location", ""),
                placeholder="Enter city name"
            )
        )
        
        # Units settings
        self.add_section("Display Units")
        self.unit_toggle = self.add_component(
            ToggleSwitch(
                label="Temperature Units",
                options=["Celsius", "Fahrenheit"],
                selected=self.config.get("units", "Celsius")
            )
        )
        
        # Update frequency
        self.add_section("Update Settings")
        self.frequency = self.add_component(
            TextField(
                label="Update Frequency (minutes)",
                value=str(self.config.get("update_frequency_minutes", 30)),
                placeholder="30"
            )
        )
        
        # Auto-update toggle
        self.auto_update = self.add_component(
            ToggleSwitch(
                label="Auto Update",
                options=["On", "Off"],
                selected="On" if self.config.get("auto_update", True) else "Off"
            )
        )
        
        # Save button
        self.save_button = self.add_component(
            Button(
                label="Save Settings",
                on_click=self._on_save
            ),
            section="actions"
        )
        
    def _subscribe_to_events(self):
        # Listen for config updates
        self._unsubscribe_funcs = [
            event_bus.subscribe(
                f"plugin.config.updated.{self.plugin_id}",
                self._on_config_updated,
                async_callback=True
            )
        ]
        
    async def _on_config_updated(self, event_data):
        """Handle external config updates"""
        new_config = event_data.get("config", {})
        
        # Update UI with new values
        await self._safe_ui_update(lambda: self._update_ui_from_config(new_config))
        
    def _update_ui_from_config(self, config):
        """Update UI controls from config"""
        self.location_input.value = config.get("location", self.location_input.value)
        self.unit_toggle.selected = config.get("units", self.unit_toggle.selected)
        self.frequency.value = str(config.get("update_frequency_minutes", self.frequency.value))
        self.auto_update.selected = "On" if config.get("auto_update", True) else "Off"
        
    def _on_save(self):
        """Handle save button click"""
        try:
            # Validate input
            frequency = int(self.frequency.value)
            if frequency <= 0:
                raise ValueError("Update frequency must be positive")
                
            # Build config object
            new_config = {
                "location": self.location_input.value,
                "units": self.unit_toggle.selected,
                "update_frequency_minutes": frequency,
                "auto_update": self.auto_update.selected == "On"
            }
            
            # Emit config update event
            event_bus.emit("plugin.config.update", {
                "plugin_id": self.plugin_id,
                "config": new_config
            })
            
            # Show success indication
            self.show_success_message("Settings saved successfully")
            
        except ValueError as e:
            # Show validation error
            self.show_error_message(f"Invalid settings: {e}")
            
    async def _safe_ui_update(self, update_func):
        """Safely update UI from any thread"""
        try:
            # Framework-specific thread safety mechanism
            update_func()
        except Exception as e:
            logging.error(f"UI update failed: {e}")
            
    def cleanup(self):
        """Clean up resources and event subscriptions"""
        for unsub in self._unsubscribe_funcs:
            unsub()
```

### 9.2 Custom Chat Card Example

```python
from vpa.core.events import event_bus
from vpa.gui.components import ChatCard, Label, Icon, Button

class WeatherChatCard(ChatCard):
    def __init__(self, parent, message_data):
        super().__init__(parent)
        self.message_data = message_data
        self.plugin_id = "weather_plugin"
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up weather-specific chat card UI"""
        weather_data = self.message_data.get("weather_data", {})
        
        # Weather information display
        self.add_header(
            title=f"Weather for {weather_data.get('location', 'Unknown')}",
            icon="weather"
        )
        
        # Current conditions
        self.add_section("Current Conditions")
        
        # Temperature
        temp = weather_data.get("temperature", "N/A")
        units = weather_data.get("units", "°C")
        self.add_info_row(
            label="Temperature",
            value=f"{temp} {units}",
            icon="thermometer"
        )
        
        # Conditions
        conditions = weather_data.get("conditions", "Unknown")
        self.add_info_row(
            label="Conditions",
            value=conditions,
            icon=self._get_condition_icon(conditions)
        )
        
        # Humidity
        humidity = weather_data.get("humidity", "N/A")
        self.add_info_row(
            label="Humidity",
            value=f"{humidity}%",
            icon="droplet"
        )
        
        # Forecast section
        if "forecast" in weather_data:
            self.add_section("Forecast")
            
            forecast = weather_data["forecast"]
            for day in forecast[:3]:  # Show next 3 days
                self.add_forecast_day(day)
        
        # Add refresh button
        self.add_action_button(
            label="Refresh",
            icon="refresh",
            on_click=self._on_refresh
        )
        
    def _get_condition_icon(self, condition):
        """Map weather condition to appropriate icon"""
        condition_map = {
            "clear": "sun",
            "sunny": "sun",
            "partly cloudy": "cloud-sun",
            "cloudy": "cloud",
            "rain": "cloud-rain",
            "showers": "cloud-rain",
            "snow": "snowflake",
            "storm": "cloud-lightning",
            "thunderstorm": "cloud-lightning",
            "fog": "fog",
            "mist": "fog"
        }
        
        # Find matching condition (case insensitive)
        condition_lower = condition.lower()
        for key, icon in condition_map.items():
            if key in condition_lower:
                return icon
                
        return "cloud"  # Default icon
        
    def add_forecast_day(self, day_data):
        """Add a forecast day to the card"""
        day_name = day_data.get("day", "Unknown")
        high = day_data.get("high", "N/A")
        low = day_data.get("low", "N/A")
        conditions = day_data.get("conditions", "Unknown")
        
        self.add_info_row(
            label=day_name,
            value=f"{high} / {low} - {conditions}",
            icon=self._get_condition_icon(conditions)
        )
        
    def _on_refresh(self):
        """Handle refresh button click"""
        location = self.message_data.get("weather_data", {}).get("location", "")
        
        # Emit refresh action event
        event_bus.emit("plugin.ui.action", {
            "plugin_id": self.plugin_id,
            "action": "refresh_weather",
            "location": location,
            "message_id": self.message_data.get("id")
        })
        
        # Show loading state
        self.set_loading(True, "Refreshing weather data...")
```

### 9.3 System Tray Menu Item

```python
from vpa.core.events import event_bus
from vpa.gui.system_tray import TrayMenuItem

def register_weather_tray_menu():
    """Register weather plugin tray menu items"""
    event_bus.emit("ui.register.tray_item", {
        "plugin_id": "weather_plugin",
        "menu_item": {
            "label": "Weather",
            "icon": "weather",
            "submenu": [
                {
                    "label": "View Current Weather",
                    "action": "weather_plugin.view_current"
                },
                {
                    "label": "View Forecast",
                    "action": "weather_plugin.view_forecast"
                },
                {
                    "label": "Update Location",
                    "action": "weather_plugin.update_location"
                }
            ]
        }
    })

# Handling tray menu actions
@event_bus.subscribe("ui.tray.action")
def handle_tray_action(event_data):
    """Handle tray menu actions"""
    action = event_data.get("action", "")
    
    if action == "weather_plugin.view_current":
        # Show current weather
        event_bus.emit("plugin.request.action", {
            "plugin_id": "weather_plugin",
            "action": "show_current_weather"
        })
    
    elif action == "weather_plugin.view_forecast":
        # Show forecast
        event_bus.emit("plugin.request.action", {
            "plugin_id": "weather_plugin",
            "action": "show_forecast"
        })
    
    elif action == "weather_plugin.update_location":
        # Show location update dialog
        event_bus.emit("ui.dialog.show", {
            "dialog_type": "input",
            "title": "Update Weather Location",
            "message": "Enter your location:",
            "default_value": get_current_location(),
            "callback_event": "weather_plugin.location_updated"
        })
```

## Conclusion

Following these UI integration guidelines ensures a consistent, high-quality user experience across all plugin components in the VPA system. These patterns support the core architectural principles of the VPA platform, particularly the event-driven architecture and compartmentalized plugin design.

By adhering to these standards, plugin developers can create UIs that are performant, accessible, visually consistent, and properly integrated with the core application.

---

*Plugin UI Integration Guidelines document completed on August 27, 2025*
