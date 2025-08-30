# Settings Schema Definition

## Overview

This document defines the comprehensive schema for the VPA settings system, including all settings categories, fields, data types, validation rules, and default values. It serves as the authoritative reference for all components that interact with user settings.

## Table of Contents

1. [Schema Structure](#1-schema-structure)
2. [Core Settings](#2-core-settings)
3. [Voice Settings](#3-voice-settings)
4. [LLM Settings](#4-llm-settings)
5. [UI Settings](#5-ui-settings)
6. [Plugin Settings](#6-plugin-settings)
7. [Windows Integration Settings](#7-windows-integration-settings)
8. [Settings Validation](#8-settings-validation)
9. [Settings Persistence](#9-settings-persistence)
10. [Migration Path](#10-migration-path)

## 1. Schema Structure

### 1.1 Settings Organization

The VPA settings are organized hierarchically as follows:

```
settings/
├── core/            # Core application settings
├── voice/           # Voice/audio system settings
├── llm/             # Language model settings
├── ui/              # User interface settings
├── plugins/         # Plugin-specific settings
│   ├── plugin_id_1/ # Settings for specific plugin
│   └── plugin_id_2/
└── windows/         # Windows integration settings
```

### 1.2 Setting Types

| Type | Description | Validation |
|------|-------------|------------|
| string | Text value | Min/max length |
| boolean | True/false value | N/A |
| integer | Whole number | Min/max value |
| float | Decimal number | Min/max value |
| enum | Value from predefined set | Must be in allowed values |
| array | List of values | Min/max elements |
| object | Nested structure | Schema validation |
| file_path | Path to file | Existence check (optional) |
| directory_path | Path to directory | Existence check (optional) |

### 1.3 Setting Definition Format

```json
{
  "key": "setting.path.name",
  "type": "data_type",
  "default": "default value",
  "description": "Human-readable description",
  "validation": {
    "min": 0,           // For numbers or string length
    "max": 100,         // For numbers or string length
    "pattern": "regex", // For string validation
    "enum": ["val1", "val2"] // For enum types
  },
  "ui": {
    "category": "Category name",
    "display_name": "User-facing name",
    "help_text": "Tooltip text",
    "control_type": "slider|checkbox|text|dropdown"
  },
  "flags": {
    "restart_required": false,
    "sensitive": false, // Sensitive data (password, etc.)
    "expert": false     // Expert-level setting (hidden by default)
  }
}
```

## 2. Core Settings

### 2.1 General Settings

| Key | Type | Default | Description | Validation | UI Category |
|-----|------|---------|-------------|------------|-------------|
| core.startup_on_boot | boolean | false | Start application on system boot | N/A | General |
| core.minimize_to_tray | boolean | true | Minimize to system tray | N/A | General |
| core.save_history | boolean | true | Save conversation history | N/A | General |
| core.history_retention_days | integer | 30 | Days to keep conversation history | min: 1, max: 365 | General |
| core.log_level | enum | "info" | Application log level | enum: ["debug", "info", "warning", "error"] | Advanced |
| core.auto_update | boolean | true | Automatically check for updates | N/A | General |
| core.update_channel | enum | "stable" | Update channel | enum: ["stable", "beta"] | Advanced |

### 2.2 Performance Settings

| Key | Type | Default | Description | Validation | UI Category |
|-----|------|---------|-------------|------------|-------------|
| core.performance.startup_optimization | boolean | true | Optimize startup time | N/A | Performance |
| core.performance.memory_limit_mb | integer | 512 | Memory usage limit (MB) | min: 256, max: 2048 | Performance |
| core.performance.plugin_concurrency | integer | 5 | Max concurrent plugin executions | min: 1, max: 20 | Advanced |
| core.performance.enable_metrics | boolean | true | Collect performance metrics | N/A | Advanced |

## 3. Voice Settings

### 3.1 Voice Selection

| Key | Type | Default | Description | Validation | UI Category |
|-----|------|---------|-------------|------------|-------------|
| voice.enabled | boolean | false | Enable voice feedback | N/A | Voice |
| voice.selected_voice | string | "Aria" | Currently selected voice | enum: [all voice names] | Voice |
| voice.volume | integer | 75 | Voice volume | min: 0, max: 100 | Voice |

### 3.2 Voice Behavior

| Key | Type | Default | Description | Validation | UI Category |
|-----|------|---------|-------------|------------|-------------|
| voice.auto_interrupt | boolean | true | Allow interrupting current speech | N/A | Voice |
| voice.rate | float | 1.0 | Speech rate multiplier | min: 0.5, max: 2.0 | Voice |
| voice.pitch | float | 1.0 | Speech pitch multiplier | min: 0.5, max: 2.0 | Voice Advanced |
| voice.test_phrase | string | "This is a test of the voice system." | Phrase for testing voices | max: 100 | Voice Advanced |

## 4. LLM Settings

### 4.1 Model Configuration

| Key | Type | Default | Description | Validation | UI Category |
|-----|------|---------|-------------|------------|-------------|
| llm.primary_model | string | "default" | Primary language model | enum: [available models] | LLM |
| llm.fallback_model | string | "default-small" | Fallback model | enum: [available models] | LLM |
| llm.max_history | integer | 10 | Max conversation history turns | min: 1, max: 50 | LLM |
| llm.temperature | float | 0.7 | Response creativity | min: 0.0, max: 1.0 | LLM |
| llm.model_directory | directory_path | "./models" | Directory for local models | N/A | LLM Advanced |

### 4.2 Response Behavior

| Key | Type | Default | Description | Validation | UI Category |
|-----|------|---------|-------------|------------|-------------|
| llm.max_response_tokens | integer | 1024 | Maximum response length | min: 50, max: 4096 | LLM Advanced |
| llm.stream_responses | boolean | true | Stream responses as generated | N/A | LLM |
| llm.timeout_seconds | integer | 30 | Request timeout in seconds | min: 5, max: 120 | LLM Advanced |
| llm.save_responses | boolean | true | Save responses to history | N/A | LLM |

## 5. UI Settings

### 5.1 Appearance

| Key | Type | Default | Description | Validation | UI Category |
|-----|------|---------|-------------|------------|-------------|
| ui.theme | enum | "system" | UI theme | enum: ["light", "dark", "system"] | Appearance |
| ui.accent_color | string | "#0078d4" | UI accent color | pattern: "^#[0-9A-Fa-f]{6}$" | Appearance |
| ui.font_size | integer | 14 | UI font size | min: 8, max: 24 | Appearance |
| ui.compact_mode | boolean | false | Use compact UI mode | N/A | Appearance |
| ui.show_timestamps | boolean | true | Show message timestamps | N/A | Appearance |

### 5.2 Chat Interface

| Key | Type | Default | Description | Validation | UI Category |
|-----|------|---------|-------------|------------|-------------|
| ui.chat.message_alignment | enum | "right" | User message alignment | enum: ["left", "right"] | Chat |
| ui.chat.show_typing_indicator | boolean | true | Show typing indicator | N/A | Chat |
| ui.chat.enable_markdown | boolean | true | Enable markdown in messages | N/A | Chat |
| ui.chat.enable_code_highlighting | boolean | true | Enable code syntax highlighting | N/A | Chat |
| ui.chat.font_family | string | "Segoe UI" | Chat font family | N/A | Chat Advanced |

## 6. Plugin Settings

### 6.1 Plugin Management

| Key | Type | Default | Description | Validation | UI Category |
|-----|------|---------|------------|-------------|
| plugins.enable_all | boolean | true | Enable all plugins | N/A | Plugins |
| plugins.safe_mode | boolean | false | Load only core plugins | N/A | Plugins Advanced |
| plugins.allow_external | boolean | false | Allow external plugins | N/A | Plugins Advanced |
| plugins.external_directories | array | [] | Additional plugin directories | N/A | Plugins Advanced |

### 6.2 Plugin-Specific Settings

Plugin-specific settings follow this naming pattern:
`plugins.<plugin_id>.<setting_name>`

Each plugin defines its own settings schema that must be validated by the plugin manager during registration.

Example for a weather plugin:
```json
{
  "plugins.weather.location": {
    "type": "string",
    "default": "auto",
    "description": "Weather location",
    "ui": {
      "category": "Weather Plugin",
      "display_name": "Location"
    }
  },
  "plugins.weather.units": {
    "type": "enum",
    "default": "metric",
    "enum": ["metric", "imperial"],
    "description": "Temperature units",
    "ui": {
      "category": "Weather Plugin",
      "display_name": "Units",
      "control_type": "dropdown"
    }
  }
}
```

## 7. Windows Integration Settings

### 7.1 System Integration

| Key | Type | Default | Description | Validation | UI Category |
|-----|------|---------|-------------|------------|-------------|
| windows.enable_notifications | boolean | true | Enable system notifications | N/A | Windows |
| windows.notification_sound | boolean | true | Play sound with notifications | N/A | Windows |
| windows.startup_task_name | string | "VPA Assistant" | Name for startup task | max: 50 | Windows Advanced |
| windows.tray_icon | file_path | "assets/icon.ico" | System tray icon path | N/A | Windows Advanced |

### 7.2 Windows Features

| Key | Type | Default | Description | Validation | UI Category |
|-----|------|---------|-------------|------------|-------------|
| windows.clipboard_integration | boolean | true | Enable clipboard integration | N/A | Windows |
| windows.hotkey_enabled | boolean | false | Enable global hotkey | N/A | Windows |
| windows.hotkey_combination | string | "Ctrl+Alt+V" | Global hotkey combination | pattern: "^(Ctrl\+)?(Alt\+)?(Shift\+)?[A-Z0-9]$" | Windows |
| windows.minimize_esc | boolean | true | Minimize on ESC key | N/A | Windows |

## 8. Settings Validation

### 8.1 Validation Process

The settings system must validate all settings according to these rules:

1. **Type checking**: Ensure the value matches the defined type
2. **Range validation**: For numeric types, ensure within min/max bounds
3. **Pattern validation**: For string types with patterns, validate against regex
4. **Enum validation**: For enum types, ensure value is in allowed set
5. **Custom validation**: For complex settings, use custom validation functions

### 8.2 Validation Implementation

```python
def validate_setting(key, value, schema):
    """Validate a single setting against its schema definition"""
    if key not in schema:
        raise ValueError(f"Unknown setting: {key}")
        
    setting_def = schema[key]
    setting_type = setting_def.get("type")
    
    # Type validation
    if setting_type == "string" and not isinstance(value, str):
        raise TypeError(f"Setting {key} must be a string")
    elif setting_type == "boolean" and not isinstance(value, bool):
        raise TypeError(f"Setting {key} must be a boolean")
    elif setting_type == "integer" and not isinstance(value, int):
        raise TypeError(f"Setting {key} must be an integer")
    elif setting_type == "float" and not isinstance(value, (int, float)):
        raise TypeError(f"Setting {key} must be a number")
    elif setting_type == "array" and not isinstance(value, list):
        raise TypeError(f"Setting {key} must be an array")
    elif setting_type == "object" and not isinstance(value, dict):
        raise TypeError(f"Setting {key} must be an object")
        
    # Value validation
    validation = setting_def.get("validation", {})
    
    if setting_type in ["integer", "float"]:
        if "min" in validation and value < validation["min"]:
            raise ValueError(f"Setting {key} must be at least {validation['min']}")
        if "max" in validation and value > validation["max"]:
            raise ValueError(f"Setting {key} must be at most {validation['max']}")
            
    elif setting_type == "string":
        if "min" in validation and len(value) < validation["min"]:
            raise ValueError(f"Setting {key} must be at least {validation['min']} characters")
        if "max" in validation and len(value) > validation["max"]:
            raise ValueError(f"Setting {key} must be at most {validation['max']} characters")
        if "pattern" in validation and not re.match(validation["pattern"], value):
            raise ValueError(f"Setting {key} must match pattern: {validation['pattern']}")
            
    elif setting_type == "enum":
        allowed = validation.get("enum", [])
        if allowed and value not in allowed:
            raise ValueError(f"Setting {key} must be one of: {', '.join(allowed)}")
            
    elif setting_type == "array":
        if "min" in validation and len(value) < validation["min"]:
            raise ValueError(f"Setting {key} must have at least {validation['min']} items")
        if "max" in validation and len(value) > validation["max"]:
            raise ValueError(f"Setting {key} must have at most {validation['max']} items")
            
    # Return validated value (may be modified by validation)
    return value
```

## 9. Settings Persistence

### 9.1 Storage Format

Settings are stored in JSON format in the user's application data directory:

```
%APPDATA%\VPA\settings.json
```

The file structure follows the hierarchical organization defined in the schema:

```json
{
  "core": {
    "startup_on_boot": true,
    "minimize_to_tray": true,
    "performance": {
      "memory_limit_mb": 512
    }
  },
  "voice": {
    "enabled": true,
    "selected_voice": "Aria"
  },
  "llm": {
    "primary_model": "default",
    "temperature": 0.7
  }
}
```

### 9.2 Settings Access Pattern

```python
from vpa.core.settings import settings

# Get setting with default fallback
minimize_to_tray = settings.get("core.minimize_to_tray", True)

# Set setting with validation
settings.set("voice.selected_voice", "Aria")

# Get nested settings object
performance_settings = settings.get_section("core.performance")

# Set multiple settings
settings.set_multiple({
    "ui.theme": "dark",
    "ui.accent_color": "#0078d4"
})

# Register for settings changes
settings.on_change("voice.enabled", on_voice_enabled_changed)
```

## 10. Migration Path

### 10.1 Version Tracking

Settings files include a version identifier:

```json
{
  "_schema_version": "1.0",
  "core": { ... }
}
```

### 10.2 Migration Strategy

When the settings schema changes:

1. New settings are added with their default values
2. Removed settings are ignored
3. Settings with changed types are migrated if possible, or reset to defaults
4. The schema version is updated

### 10.3 Migration Implementation

```python
def migrate_settings(settings_data, current_version, target_version):
    """Migrate settings from one schema version to another"""
    if current_version == "1.0" and target_version == "1.1":
        # Example migration from 1.0 to 1.1
        
        # Add new setting with default
        if "ui" not in settings_data:
            settings_data["ui"] = {}
        if "compact_mode" not in settings_data["ui"]:
            settings_data["ui"]["compact_mode"] = False
            
        # Migrate renamed setting
        if "voice" in settings_data and "voice_name" in settings_data["voice"]:
            settings_data["voice"]["selected_voice"] = settings_data["voice"].pop("voice_name")
            
        # Update version
        settings_data["_schema_version"] = "1.1"
        
    # Add migrations for other version pairs as needed
    
    return settings_data
```

## Conclusion

This document defines the comprehensive schema for the VPA settings system. It provides the structure, validation rules, and access patterns needed to ensure consistent settings management across all components of the application.

By following this schema, all components will maintain a consistent approach to settings, ensuring proper validation, persistence, and user experience.

---

*Settings Schema Definition created on August 29, 2025*  
*Version: 1.0*  
*Related Documents: VPA_PLANNING_ENHANCEMENT_ANALYSIS.md (v1.0)*
