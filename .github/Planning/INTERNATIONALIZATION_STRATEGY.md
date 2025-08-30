# Internationalization Strategy

## Overview

This document outlines the internationalization (i18n) and localization (l10n) strategy for the VPA (Virtual Personal Assistant) application. It defines the approach, architecture, and implementation details for making VPA accessible to users worldwide in their preferred languages.

## Table of Contents

1. [Core Principles](#1-core-principles)
2. [Architecture](#2-architecture)
3. [Translation Management](#3-translation-management)
4. [Implementation Details](#4-implementation-details)
5. [Date, Time, and Number Formatting](#5-date-time-and-number-formatting)
6. [Right-to-Left (RTL) Support](#6-right-to-left-rtl-support)
7. [Language Detection and Selection](#7-language-detection-and-selection)
8. [Quality Assurance](#8-quality-assurance)
9. [Future Expansion](#9-future-expansion)

## 1. Core Principles

### 1.1 Design Goals

The VPA internationalization system is designed with these key principles:

1. **User-Centric**: Prioritize natural, culturally appropriate experiences
2. **Scalability**: Support easy addition of new languages
3. **Maintainability**: Clear processes for updating translations
4. **Automation**: Automate translation workflow where possible
5. **Separation**: Separate code and content for easier translation
6. **Contextual Awareness**: Provide context for translations
7. **Graceful Fallbacks**: Handle missing translations elegantly

### 1.2 Supported Languages

The initial version of VPA will support the following languages:

| Language | Code | RTL | Priority |
|----------|------|-----|----------|
| English (US) | en-US | No | 1 (Default) |
| Spanish | es-ES | No | 2 |
| French | fr-FR | No | 2 |
| German | de-DE | No | 2 |
| Chinese (Simplified) | zh-CN | No | 2 |
| Japanese | ja-JP | No | 2 |
| Arabic | ar-SA | Yes | 3 |
| Hindi | hi-IN | No | 3 |
| Portuguese (Brazil) | pt-BR | No | 3 |
| Russian | ru-RU | No | 3 |

Future language additions will be prioritized based on user demand and market requirements.

## 2. Architecture

### 2.1 System Overview

The VPA internationalization architecture follows a modular design:

```
┌───────────────────────────────────────────┐
│              Application                  │
│  ┌─────────────┐      ┌────────────────┐  │
│  │ Core Logic  │      │ UI Components  │  │
│  └──────┬──────┘      └────────┬───────┘  │
│         │                      │          │
│         ▼                      ▼          │
│  ┌─────────────────────────────────────┐  │
│  │         I18n Framework              │  │
│  │  ┌────────────┐  ┌──────────────┐   │  │
│  │  │ Translator │  │ Formatters   │   │  │
│  │  └──────┬─────┘  └──────┬───────┘   │  │
│  └─────────┼────────────────┼──────────┘  │
│            │                │             │
└────────────┼────────────────┼─────────────┘
             │                │
             ▼                ▼
    ┌─────────────────┐  ┌───────────────────┐
    │  Translation    │  │ Locale Settings   │
    │  Resources      │  │ and Preferences   │
    └─────────────────┘  └───────────────────┘
```

### 2.2 Directory Structure

```
vpa/
├── core/
│   ├── i18n/
│   │   ├── __init__.py
│   │   ├── translator.py
│   │   ├── formatter.py
│   │   └── detector.py
│   └── ...
├── locales/
│   ├── en-US/
│   │   ├── ui.json
│   │   ├── messages.json
│   │   ├── help.json
│   │   └── ...
│   ├── es-ES/
│   │   ├── ui.json
│   │   ├── messages.json
│   │   ├── help.json
│   │   └── ...
│   └── ...
└── ...
```

## 3. Translation Management

### 3.1 Translation Resource Format

VPA uses JSON files for translation resources:

```json
{
  "namespace": "ui",
  "locale": "en-US",
  "translations": {
    "common.ok": "OK",
    "common.cancel": "Cancel",
    "common.save": "Save",
    "settings.title": "Settings",
    "settings.language": "Language",
    "settings.language.change": "Change Language",
    "errors.required": "{field} is required",
    "welcome.greeting": "Welcome, {name}!",
    "items.count": "{count, plural, one{# item} other{# items}}",
    "updated.time": "Updated {time, date, medium}"
  },
  "metadata": {
    "version": "1.0.0",
    "lastUpdated": "2025-07-15T14:30:00Z",
    "translator": "VPA Team"
  }
}
```

### 3.2 Translation Process

VPA's translation process follows these steps:

1. **Extraction**: Source strings are extracted from codebase
2. **Preparation**: Strings are organized with context for translators
3. **Translation**: Professional translation of strings
4. **Review**: Quality review by native speakers
5. **Integration**: Translated strings are integrated into application
6. **Testing**: Verification in context of the application

### 3.3 Translation Management System

VPA uses a Translation Management System (TMS) to:

- Track translation status and completion
- Provide context to translators
- Maintain version history
- Support collaboration between developers and translators
- Generate translation resource files

## 4. Implementation Details

### 4.1 Translator Service

```python
from typing import Dict, Any, Optional
import json
import os
import logging
from pathlib import Path

class Translator:
    """
    Core translation service for VPA
    """
    
    def __init__(self, locale_dir: str, default_locale: str = "en-US"):
        self.logger = logging.getLogger(__name__)
        self.locale_dir = locale_dir
        self.default_locale = default_locale
        self.current_locale = default_locale
        
        # Translation caches
        self.translations: Dict[str, Dict[str, Dict[str, str]]] = {}
        self.loaded_locales: set = set()
        
        # Load default locale
        self._load_locale(default_locale)
        
    def set_locale(self, locale: str) -> bool:
        """
        Set the current locale
        """
        if not self._is_locale_available(locale):
            self.logger.warning(f"Locale {locale} is not available, falling back to {self.current_locale}")
            return False
            
        # Load the locale if not already loaded
        if locale not in self.loaded_locales:
            self._load_locale(locale)
            
        self.current_locale = locale
        self.logger.info(f"Locale set to {locale}")
        return True
        
    def translate(self, key: str, params: Optional[Dict[str, Any]] = None, 
                  namespace: str = "ui", locale: Optional[str] = None) -> str:
        """
        Translate a key with optional parameters
        """
        if locale is None:
            locale = self.current_locale
            
        # Ensure locale is loaded
        if locale not in self.loaded_locales:
            if not self._load_locale(locale):
                locale = self.default_locale
                
        # Get namespace translations
        ns_translations = self.translations.get(locale, {}).get(namespace, {})
        
        # Look up translation
        translation = ns_translations.get(key)
        
        # If not found, try default locale
        if translation is None and locale != self.default_locale:
            translation = self.translations.get(self.default_locale, {}).get(namespace, {}).get(key)
            
        # If still not found, return key
        if translation is None:
            self.logger.warning(f"Missing translation for key: {key} in {namespace} ({locale})")
            translation = key
            
        # Apply parameters if provided
        if params and translation:
            try:
                import re
                
                # Simple parameter replacement
                for param, value in params.items():
                    pattern = r'\{' + re.escape(param) + r'(,\s*[^{}]+)?\}'
                    replacement = str(value)
                    translation = re.sub(pattern, replacement, translation)
                    
                # Handle plural forms using ICU-like syntax
                plural_pattern = r'\{([^{}]+),\s*plural,\s*([^{}]+)\}'
                
                def plural_replacer(match):
                    var_name = match.group(1).strip()
                    forms = match.group(2).strip()
                    
                    if var_name not in params:
                        return match.group(0)
                        
                    count = int(params[var_name])
                    
                    # Extract plural forms
                    forms_dict = {}
                    for form in re.finditer(r'(\w+)\{([^{}]*)\}', forms):
                        form_name = form.group(1).strip()
                        form_value = form.group(2).strip()
                        forms_dict[form_name] = form_value
                        
                    # Select form based on count
                    if count == 0 and "zero" in forms_dict:
                        result = forms_dict["zero"]
                    elif count == 1 and "one" in forms_dict:
                        result = forms_dict["one"]
                    elif count == 2 and "two" in forms_dict:
                        result = forms_dict["two"]
                    elif "other" in forms_dict:
                        result = forms_dict["other"]
                    else:
                        result = f"{count}"
                        
                    # Replace # with count
                    return result.replace("#", str(count))
                    
                translation = re.sub(plural_pattern, plural_replacer, translation)
                
            except Exception as e:
                self.logger.error(f"Error applying parameters to translation: {e}")
                
        return translation
        
    def get_available_locales(self) -> Dict[str, Dict[str, str]]:
        """
        Get available locales with metadata
        """
        locales = {}
        
        for locale_dir in os.listdir(self.locale_dir):
            locale_path = os.path.join(self.locale_dir, locale_dir)
            if os.path.isdir(locale_path):
                # Check for metadata
                metadata_file = os.path.join(locale_path, "metadata.json")
                if os.path.exists(metadata_file):
                    try:
                        with open(metadata_file, "r", encoding="utf-8") as f:
                            metadata = json.load(f)
                            locales[locale_dir] = metadata
                    except Exception as e:
                        self.logger.error(f"Error loading metadata for {locale_dir}: {e}")
                        locales[locale_dir] = {"name": locale_dir, "complete": False}
                else:
                    locales[locale_dir] = {"name": locale_dir, "complete": False}
                    
        return locales
        
    def _load_locale(self, locale: str) -> bool:
        """
        Load translations for a locale
        """
        locale_path = os.path.join(self.locale_dir, locale)
        
        if not os.path.exists(locale_path):
            self.logger.error(f"Locale directory not found: {locale_path}")
            return False
            
        try:
            # Initialize locale in translations dict if needed
            if locale not in self.translations:
                self.translations[locale] = {}
                
            # Load all JSON files in locale directory
            for file_path in Path(locale_path).glob("*.json"):
                if file_path.name == "metadata.json":
                    continue
                    
                namespace = file_path.stem
                
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                # Store translations for namespace
                translations = data.get("translations", {})
                self.translations[locale][namespace] = translations
                
            # Mark locale as loaded
            self.loaded_locales.add(locale)
            self.logger.info(f"Loaded translations for locale: {locale}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading translations for locale {locale}: {e}")
            return False
            
    def _is_locale_available(self, locale: str) -> bool:
        """
        Check if a locale is available
        """
        locale_path = os.path.join(self.locale_dir, locale)
        return os.path.exists(locale_path)
```

### 4.2 Translation Context Manager

To provide context for translators, VPA implements:

```python
class TranslationContext:
    """
    Provides context information for translators
    """
    
    def __init__(self):
        self.contexts = {}
        
    def register_key_context(self, namespace: str, key: str, context: Dict[str, Any]):
        """
        Register context for a translation key
        """
        if namespace not in self.contexts:
            self.contexts[namespace] = {}
            
        self.contexts[namespace][key] = context
        
    def get_key_context(self, namespace: str, key: str) -> Dict[str, Any]:
        """
        Get context for a translation key
        """
        return self.contexts.get(namespace, {}).get(key, {})
        
    def export_contexts(self, output_path: str):
        """
        Export context information for translators
        """
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.contexts, f, indent=2, ensure_ascii=False)
            
    def import_contexts(self, input_path: str):
        """
        Import context information
        """
        with open(input_path, "r", encoding="utf-8") as f:
            self.contexts = json.load(f)
```

### 4.3 UI Integration

VPA integrates translations throughout the UI:

```python
class I18nManager:
    """
    Manages internationalization across the application
    """
    
    def __init__(self, event_bus, settings_manager):
        self.event_bus = event_bus
        self.settings_manager = settings_manager
        
        # Initialize translator
        locale_dir = os.path.join(get_app_dir(), "locales")
        self.translator = Translator(locale_dir)
        
        # Initialize formatters
        self.date_formatter = DateTimeFormatter()
        self.number_formatter = NumberFormatter()
        
        # Load current locale from settings
        default_locale = self.translator.default_locale
        current_locale = settings_manager.get("app.locale", default_locale)
        self.set_locale(current_locale)
        
        # Subscribe to locale change events
        event_bus.subscribe("settings.changed.app.locale", self._handle_locale_change)
        
    def set_locale(self, locale: str) -> bool:
        """
        Set the application locale
        """
        success = self.translator.set_locale(locale)
        
        if success:
            # Update formatters
            self.date_formatter.set_locale(locale)
            self.number_formatter.set_locale(locale)
            
            # Save to settings
            self.settings_manager.set("app.locale", locale)
            
            # Emit event
            self.event_bus.emit("i18n.locale.changed", {
                "locale": locale
            })
            
        return success
        
    def get_current_locale(self) -> str:
        """
        Get the current locale
        """
        return self.translator.current_locale
        
    def get_available_locales(self) -> Dict[str, Dict[str, str]]:
        """
        Get available locales
        """
        return self.translator.get_available_locales()
        
    def translate(self, key: str, params: Optional[Dict[str, Any]] = None, 
                 namespace: str = "ui") -> str:
        """
        Translate a key
        """
        return self.translator.translate(key, params, namespace)
        
    def format_date(self, date_value, format_type="medium") -> str:
        """
        Format a date according to the current locale
        """
        return self.date_formatter.format_date(date_value, format_type)
        
    def format_number(self, number, format_type="decimal") -> str:
        """
        Format a number according to the current locale
        """
        return self.number_formatter.format_number(number, format_type)
        
    def _handle_locale_change(self, event_data: Dict[str, Any]):
        """
        Handle locale change event
        """
        if "value" in event_data:
            new_locale = event_data["value"]
            self.set_locale(new_locale)
```

### 4.4 Code Usage Examples

```python
# Initialize I18n Manager
i18n_manager = I18nManager(event_bus, settings_manager)

# Basic translation
ok_button_text = i18n_manager.translate("common.ok")

# Translation with parameters
welcome_text = i18n_manager.translate("welcome.greeting", {"name": user.name})

# Plural forms
items_text = i18n_manager.translate("items.count", {"count": items.length})

# Date formatting
updated_text = i18n_manager.translate("updated.time", {
    "time": i18n_manager.format_date(datetime.now())
})

# In UI components
class SettingsScreen(Screen):
    def __init__(self, i18n_manager):
        super().__init__()
        self.i18n = i18n_manager
        
    def build(self):
        self.title_label.text = self.i18n.translate("settings.title")
        self.language_label.text = self.i18n.translate("settings.language")
        self.save_button.text = self.i18n.translate("common.save")
```

## 5. Date, Time, and Number Formatting

### 5.1 Date Formatting Implementation

```python
class DateTimeFormatter:
    """
    Formats dates and times according to locale
    """
    
    def __init__(self, locale="en-US"):
        self.locale = locale
        self._initialize_formats()
        
    def set_locale(self, locale: str):
        """
        Set the formatter locale
        """
        self.locale = locale
        self._initialize_formats()
        
    def format_date(self, date_value, format_type="medium") -> str:
        """
        Format a date according to locale
        """
        import datetime
        from babel.dates import format_date, format_datetime, format_time
        
        try:
            # Convert string to date if needed
            if isinstance(date_value, str):
                try:
                    date_value = datetime.datetime.fromisoformat(date_value)
                except:
                    try:
                        date_value = datetime.datetime.strptime(date_value, "%Y-%m-%dT%H:%M:%S.%fZ")
                    except:
                        return date_value
            
            # Format based on type
            if isinstance(date_value, datetime.datetime):
                return format_datetime(date_value, format=format_type, locale=self.locale)
            elif isinstance(date_value, datetime.date):
                return format_date(date_value, format=format_type, locale=self.locale)
            elif isinstance(date_value, datetime.time):
                return format_time(date_value, format=format_type, locale=self.locale)
            else:
                return str(date_value)
        except Exception as e:
            logging.error(f"Error formatting date: {e}")
            return str(date_value)
            
    def format_relative_time(self, date_value) -> str:
        """
        Format a date as relative time (e.g., "5 minutes ago")
        """
        import datetime
        from babel.dates import format_timedelta
        
        try:
            # Convert string to date if needed
            if isinstance(date_value, str):
                try:
                    date_value = datetime.datetime.fromisoformat(date_value)
                except:
                    try:
                        date_value = datetime.datetime.strptime(date_value, "%Y-%m-%dT%H:%M:%S.%fZ")
                    except:
                        return date_value
            
            # Calculate delta
            if isinstance(date_value, (datetime.datetime, datetime.date)):
                now = datetime.datetime.now(date_value.tzinfo) if isinstance(date_value, datetime.datetime) else datetime.date.today()
                delta = now - date_value
                
                # Format delta
                return format_timedelta(delta, locale=self.locale, add_direction=True)
            else:
                return str(date_value)
        except Exception as e:
            logging.error(f"Error formatting relative time: {e}")
            return str(date_value)
            
    def _initialize_formats(self):
        """
        Initialize locale-specific format patterns
        """
        from babel.dates import get_date_format, get_datetime_format, get_time_format
        
        # Store format patterns
        self.date_formats = {
            "short": get_date_format("short", self.locale),
            "medium": get_date_format("medium", self.locale),
            "long": get_date_format("long", self.locale),
            "full": get_date_format("full", self.locale)
        }
        
        self.time_formats = {
            "short": get_time_format("short", self.locale),
            "medium": get_time_format("medium", self.locale),
            "long": get_time_format("long", self.locale),
            "full": get_time_format("full", self.locale)
        }
        
        self.datetime_formats = {
            "short": get_datetime_format("short", self.locale),
            "medium": get_datetime_format("medium", self.locale),
            "long": get_datetime_format("long", self.locale),
            "full": get_datetime_format("full", self.locale)
        }
```

### 5.2 Number Formatting Implementation

```python
class NumberFormatter:
    """
    Formats numbers according to locale
    """
    
    def __init__(self, locale="en-US"):
        self.locale = locale
        
    def set_locale(self, locale: str):
        """
        Set the formatter locale
        """
        self.locale = locale
        
    def format_number(self, number, format_type="decimal") -> str:
        """
        Format a number according to locale
        """
        from babel.numbers import format_decimal, format_currency, format_percent
        
        try:
            if format_type == "decimal":
                return format_decimal(number, locale=self.locale)
            elif format_type == "percent":
                return format_percent(number, locale=self.locale)
            elif format_type.startswith("currency:"):
                # Extract currency code
                parts = format_type.split(":")
                currency_code = parts[1] if len(parts) > 1 else "USD"
                return format_currency(number, currency_code, locale=self.locale)
            else:
                return str(number)
        except Exception as e:
            logging.error(f"Error formatting number: {e}")
            return str(number)
            
    def parse_number(self, number_str, format_type="decimal"):
        """
        Parse a localized number string back to a numeric value
        """
        from babel.numbers import parse_decimal, parse_number
        
        try:
            if format_type == "decimal":
                return parse_decimal(number_str, locale=self.locale)
            else:
                return parse_number(number_str, locale=self.locale)
        except Exception as e:
            logging.error(f"Error parsing number: {e}")
            try:
                # Fallback to float conversion
                return float(number_str.replace(",", "."))
            except:
                return None
```

## 6. Right-to-Left (RTL) Support

### 6.1 RTL Detection

```python
def is_rtl_language(locale: str) -> bool:
    """
    Determine if a locale uses RTL script
    """
    rtl_languages = {"ar", "he", "fa", "ur", "ps", "ku", "sd", "dv", "ha", "yi"}
    
    # Check primary language code
    primary_lang = locale.split("-")[0].lower()
    return primary_lang in rtl_languages
```

### 6.2 RTL UI Adjustments

```python
class RTLManager:
    """
    Manages right-to-left UI adjustments
    """
    
    def __init__(self, i18n_manager, ui_manager):
        self.i18n_manager = i18n_manager
        self.ui_manager = ui_manager
        self.is_rtl = False
        
        # Subscribe to locale changes
        i18n_manager.event_bus.subscribe("i18n.locale.changed", self._handle_locale_change)
        
        # Initial check
        self._handle_locale_change({"locale": i18n_manager.get_current_locale()})
        
    def _handle_locale_change(self, event_data: Dict[str, Any]):
        """
        Handle locale change
        """
        locale = event_data.get("locale", "en-US")
        new_rtl = is_rtl_language(locale)
        
        if new_rtl != self.is_rtl:
            self.is_rtl = new_rtl
            self._apply_rtl_changes()
            
    def _apply_rtl_changes(self):
        """
        Apply RTL changes to UI
        """
        # Set direction on root element
        direction = "rtl" if self.is_rtl else "ltr"
        self.ui_manager.set_root_direction(direction)
        
        # Apply RTL-specific styles
        if self.is_rtl:
            self.ui_manager.add_stylesheet("rtl.css")
        else:
            self.ui_manager.remove_stylesheet("rtl.css")
            
        # Flip icons and layouts if needed
        self.ui_manager.set_layout_mirrored(self.is_rtl)
        
        # Emit event for components to adjust
        self.i18n_manager.event_bus.emit("ui.direction.changed", {
            "is_rtl": self.is_rtl,
            "direction": direction
        })
```

### 6.3 RTL CSS Example

```css
/* rtl.css */

/* Flip layout */
.layout-container {
    direction: rtl;
}

/* Flip icons */
.icon-chevron-right {
    transform: scaleX(-1);
}

/* Adjust margins and paddings */
.sidebar {
    border-right: none;
    border-left: 1px solid var(--border-color);
}

.list-item {
    padding-left: 0;
    padding-right: 20px;
}

.list-item-icon {
    margin-right: 0;
    margin-left: 10px;
}

/* Adjust text alignment */
.text-left {
    text-align: right;
}

.text-right {
    text-align: left;
}
```

## 7. Language Detection and Selection

### 7.1 Language Detection

```python
class LanguageDetector:
    """
    Detects user language preferences
    """
    
    def __init__(self, available_locales, default_locale="en-US"):
        self.available_locales = available_locales
        self.default_locale = default_locale
        
    def detect_system_language(self) -> str:
        """
        Detect system language
        """
        import locale as system_locale
        import platform
        
        try:
            if platform.system() == "Windows":
                import ctypes
                windll = ctypes.windll.kernel32
                system_lang = locale.windows_locale[windll.GetUserDefaultUILanguage()]
            else:
                system_lang = system_locale.getdefaultlocale()[0]
                
            # Check if system language is available
            if system_lang in self.available_locales:
                return system_lang
                
            # Try language part only (e.g., 'en-US' -> 'en')
            if "-" in system_lang:
                lang_part = system_lang.split("-")[0]
                
                # Find matching locale
                for locale in self.available_locales:
                    if locale.startswith(f"{lang_part}-"):
                        return locale
                        
            return self.default_locale
        except:
            return self.default_locale
            
    def detect_user_preference(self, user_data: Dict[str, Any]) -> str:
        """
        Detect language from user profile
        """
        # Check if user has a language preference
        user_lang = user_data.get("language")
        
        if user_lang and user_lang in self.available_locales:
            return user_lang
            
        # Fall back to system language
        return self.detect_system_language()
```

### 7.2 Language Selection UI

```python
class LanguageSelector:
    """
    UI component for selecting language
    """
    
    def __init__(self, i18n_manager):
        self.i18n_manager = i18n_manager
        
    def build(self):
        """
        Build the language selector UI
        """
        # Get available locales
        locales = self.i18n_manager.get_available_locales()
        current_locale = self.i18n_manager.get_current_locale()
        
        # Create dropdown
        dropdown = Dropdown(
            label=self.i18n_manager.translate("settings.language"),
            value=current_locale
        )
        
        # Add options
        for locale_code, locale_data in locales.items():
            display_name = locale_data.get("displayName", locale_code)
            dropdown.add_option(locale_code, display_name)
            
        # Add change handler
        dropdown.on_change(self._handle_language_change)
        
        return dropdown
        
    def _handle_language_change(self, value):
        """
        Handle language selection change
        """
        self.i18n_manager.set_locale(value)
```

## 8. Quality Assurance

### 8.1 Translation Validation

VPA implements automated validation for translations:

```python
class TranslationValidator:
    """
    Validates translation files for completeness and correctness
    """
    
    def __init__(self, locale_dir, default_locale="en-US"):
        self.locale_dir = locale_dir
        self.default_locale = default_locale
        
    def validate_all(self) -> Dict[str, Dict[str, Any]]:
        """
        Validate all translations
        """
        results = {}
        
        # Get locales
        locales = [d for d in os.listdir(self.locale_dir) 
                  if os.path.isdir(os.path.join(self.locale_dir, d))]
                  
        # Load default locale keys
        default_keys = self._load_all_keys(self.default_locale)
        
        # Validate each locale
        for locale in locales:
            if locale == self.default_locale:
                continue
                
            results[locale] = self._validate_locale(locale, default_keys)
            
        return results
        
    def _validate_locale(self, locale, default_keys) -> Dict[str, Any]:
        """
        Validate a single locale
        """
        result = {
            "missing_keys": {},
            "extra_keys": {},
            "parameter_mismatches": {},
            "total_keys": 0,
            "missing_count": 0,
            "completion_percentage": 0
        }
        
        # Load locale keys
        locale_keys = self._load_all_keys(locale)
        
        # Count keys
        result["total_keys"] = sum(len(keys) for keys in default_keys.values())
        
        # Check each namespace
        for namespace, keys in default_keys.items():
            locale_ns_keys = locale_keys.get(namespace, {})
            
            # Find missing keys
            missing = []
            for key in keys:
                if key not in locale_ns_keys:
                    missing.append(key)
                    
            if missing:
                result["missing_keys"][namespace] = missing
                result["missing_count"] += len(missing)
                
            # Find extra keys
            extra = []
            for key in locale_ns_keys:
                if key not in keys:
                    extra.append(key)
                    
            if extra:
                result["extra_keys"][namespace] = extra
                
            # Check parameter mismatches
            mismatches = self._check_parameter_mismatches(
                namespace, keys, locale_ns_keys, locale
            )
            
            if mismatches:
                result["parameter_mismatches"][namespace] = mismatches
                
        # Calculate completion percentage
        if result["total_keys"] > 0:
            completion = (result["total_keys"] - result["missing_count"]) / result["total_keys"]
            result["completion_percentage"] = round(completion * 100, 2)
        else:
            result["completion_percentage"] = 0
            
        return result
        
    def _load_all_keys(self, locale) -> Dict[str, Dict[str, str]]:
        """
        Load all keys for a locale
        """
        result = {}
        locale_path = os.path.join(self.locale_dir, locale)
        
        if not os.path.exists(locale_path):
            return result
            
        for file_path in Path(locale_path).glob("*.json"):
            if file_path.name == "metadata.json":
                continue
                
            namespace = file_path.stem
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                translations = data.get("translations", {})
                result[namespace] = set(translations.keys())
            except Exception as e:
                logging.error(f"Error loading {file_path}: {e}")
                
        return result
        
    def _check_parameter_mismatches(self, namespace, default_keys, locale_keys, locale):
        """
        Check for parameter mismatches between translations
        """
        import re
        mismatches = []
        
        # Pattern to match parameters
        param_pattern = r'\{([^{}]+)(,\s*[^{}]+)?\}'
        
        default_path = os.path.join(self.locale_dir, self.default_locale, f"{namespace}.json")
        locale_path = os.path.join(self.locale_dir, locale, f"{namespace}.json")
        
        try:
            # Load translations
            with open(default_path, "r", encoding="utf-8") as f:
                default_data = json.load(f).get("translations", {})
                
            with open(locale_path, "r", encoding="utf-8") as f:
                locale_data = json.load(f).get("translations", {})
                
            # Check keys that exist in both
            common_keys = set(default_keys).intersection(locale_keys)
            
            for key in common_keys:
                default_text = default_data.get(key, "")
                locale_text = locale_data.get(key, "")
                
                # Extract parameters
                default_params = set(re.findall(param_pattern, default_text))
                locale_params = set(re.findall(param_pattern, locale_text))
                
                # Compare parameter counts
                default_param_names = {p[0].split(",")[0].strip() for p in default_params}
                locale_param_names = {p[0].split(",")[0].strip() for p in locale_params}
                
                if default_param_names != locale_param_names:
                    mismatches.append({
                        "key": key,
                        "default_params": sorted(list(default_param_names)),
                        "locale_params": sorted(list(locale_param_names))
                    })
                    
            return mismatches
        except Exception as e:
            logging.error(f"Error checking parameter mismatches: {e}")
            return []
```

### 8.2 Pseudo-Localization

For testing, VPA implements pseudo-localization:

```python
class PseudoLocalizer:
    """
    Creates pseudo-localized text for testing
    """
    
    def __init__(self):
        self.char_map = {
            'a': 'ā', 'b': 'ƀ', 'c': 'č', 'd': 'đ', 'e': 'ē', 'f': 'ƒ',
            'g': 'ğ', 'h': 'ħ', 'i': 'ī', 'j': 'ĵ', 'k': 'ķ', 'l': 'ŀ',
            'm': 'ḿ', 'n': 'ň', 'o': 'ō', 'p': 'ƥ', 'q': 'ɋ', 'r': 'ř',
            's': 'š', 't': 'ţ', 'u': 'ū', 'v': 'ṽ', 'w': 'ŵ', 'x': 'ẋ',
            'y': 'ÿ', 'z': 'ź', 'A': 'Ā', 'B': 'Ɓ', 'C': 'Č', 'D': 'Đ',
            'E': 'Ē', 'F': 'Ƒ', 'G': 'Ğ', 'H': 'Ħ', 'I': 'Ī', 'J': 'Ĵ',
            'K': 'Ķ', 'L': 'Ŀ', 'M': 'Ḿ', 'N': 'Ň', 'O': 'Ō', 'P': 'Ƥ',
            'Q': 'Ɋ', 'R': 'Ř', 'S': 'Š', 'T': 'Ţ', 'U': 'Ū', 'V': 'Ṽ',
            'W': 'Ŵ', 'X': 'Ẋ', 'Y': 'Ÿ', 'Z': 'Ź'
        }
        
    def pseudo_localize(self, text: str) -> str:
        """
        Create pseudo-localized version of text
        """
        # Preserve placeholders and formatting
        import re
        
        # Split text into parts to preserve placeholders
        parts = []
        last_end = 0
        
        # Match both ICU-style {param} and printf-style %s placeholders
        for match in re.finditer(r'(\{[^{}]+\}|%[sdifoxXeEgGcr])', text):
            start, end = match.span()
            
            # Add text before placeholder
            if start > last_end:
                parts.append(('text', text[last_end:start]))
                
            # Add placeholder
            parts.append(('placeholder', match.group()))
            
            last_end = end
            
        # Add remaining text
        if last_end < len(text):
            parts.append(('text', text[last_end:]))
            
        # Process parts
        result = []
        for part_type, part_text in parts:
            if part_type == 'text':
                # Apply pseudo-localization
                result.append(self._transform_text(part_text))
            else:
                # Keep placeholders unchanged
                result.append(part_text)
                
        return ''.join(result)
        
    def _transform_text(self, text: str) -> str:
        """
        Transform text to pseudo-localized form
        """
        # Replace characters
        result = ''.join(self.char_map.get(c, c) for c in text)
        
        # Expand text length by ~30%
        word_expansion = ' ' * (len(text) // 5)
        
        # Add brackets for visual identification
        return f"[{result}{word_expansion}]"
        
    def create_pseudo_locale(self, source_locale: str, target_locale: str, locale_dir: str):
        """
        Create a pseudo-localized version of a locale
        """
        source_dir = os.path.join(locale_dir, source_locale)
        target_dir = os.path.join(locale_dir, target_locale)
        
        # Create target directory
        os.makedirs(target_dir, exist_ok=True)
        
        # Process each file
        for file_path in Path(source_dir).glob("*.json"):
            if file_path.name == "metadata.json":
                continue
                
            # Read source file
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Create pseudo-localized version
            pseudo_data = {
                "namespace": data.get("namespace", ""),
                "locale": target_locale,
                "translations": {},
                "metadata": {
                    "version": data.get("metadata", {}).get("version", "1.0.0"),
                    "lastUpdated": datetime.datetime.now().isoformat(),
                    "translator": "PseudoLocalizer"
                }
            }
            
            # Process translations
            for key, value in data.get("translations", {}).items():
                pseudo_data["translations"][key] = self.pseudo_localize(value)
                
            # Write target file
            target_path = os.path.join(target_dir, file_path.name)
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(pseudo_data, f, ensure_ascii=False, indent=2)
                
        # Create metadata file
        metadata = {
            "displayName": f"Pseudo-{source_locale}",
            "nativeName": f"Ƥšēūđō-{source_locale}",
            "description": "Pseudo-localized version for testing",
            "isTest": True,
            "complete": True
        }
        
        metadata_path = os.path.join(target_dir, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
```

## 9. Future Expansion

### 9.1 Machine Translation Integration

For future development, VPA will integrate machine translation services:

```python
class MachineTrlationService:
    """
    Service for machine translation integration
    """
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("TRANSLATION_API_KEY")
        
    async def translate_text(self, text, source_lang, target_lang):
        """
        Translate text using machine translation
        """
        if not self.api_key:
            raise ValueError("Translation API key not configured")
            
        try:
            import aiohttp
            
            # Example using a generic translation API
            api_url = "https://translation-service.example.com/translate"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, json={
                    "text": text,
                    "source": source_lang,
                    "target": target_lang,
                    "api_key": self.api_key
                }) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("translation", text)
                    else:
                        logging.error(f"Translation API error: {response.status}")
                        return text
        except Exception as e:
            logging.error(f"Translation error: {e}")
            return text
            
    async def translate_file(self, source_file, target_file, source_lang, target_lang):
        """
        Translate a translation file
        """
        try:
            # Read source file
            with open(source_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Create target data structure
            target_data = {
                "namespace": data.get("namespace", ""),
                "locale": target_lang,
                "translations": {},
                "metadata": {
                    "version": data.get("metadata", {}).get("version", "1.0.0"),
                    "lastUpdated": datetime.datetime.now().isoformat(),
                    "translator": "Machine Translation"
                }
            }
            
            # Translate each string
            for key, value in data.get("translations", {}).items():
                if isinstance(value, str):
                    target_data["translations"][key] = await self.translate_text(
                        value, source_lang, target_lang
                    )
                    
            # Write target file
            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(target_data, f, ensure_ascii=False, indent=2)
                
            return True
        except Exception as e:
            logging.error(f"File translation error: {e}")
            return False
```

### 9.2 Community Translation Platform

Future versions will include a community translation platform:

1. **Web Interface**: Browser-based translation interface
2. **Translation Memory**: Reuse of previously translated strings
3. **Glossary**: Consistent terminology across translations
4. **Review Process**: Multi-step quality assurance
5. **Version Control**: Track changes and update history

### 9.3 Dynamic Content Translation

Future versions will support dynamic content translation:

```python
class DynamicContentTranslator:
    """
    Translates dynamic content in real-time
    """
    
    def __init__(self, i18n_manager, machine_translation_service):
        self.i18n_manager = i18n_manager
        self.mt_service = machine_translation_service
        self.translation_cache = {}
        
    async def translate_dynamic_content(self, content, content_type="text"):
        """
        Translate dynamic content
        """
        current_locale = self.i18n_manager.get_current_locale()
        cache_key = f"{content}:{current_locale}:{content_type}"
        
        # Check cache
        if cache_key in self.translation_cache:
            return self.translation_cache[cache_key]
            
        # Determine source language
        content_lang = await self._detect_language(content)
        
        # Skip translation if content is already in target language
        if content_lang == current_locale.split("-")[0]:
            return content
            
        # Translate content
        translated = await self.mt_service.translate_text(
            content, content_lang, current_locale
        )
        
        # Cache result
        self.translation_cache[cache_key] = translated
        
        return translated
        
    async def _detect_language(self, text):
        """
        Detect language of text
        """
        try:
            import langid
            return langid.classify(text)[0]
        except:
            return "en"
```

## Conclusion

The VPA internationalization strategy establishes a comprehensive approach to making the application accessible to users worldwide. By implementing a robust translation system, cultural adaptations, and flexible formatting, VPA provides a localized experience that feels natural to users regardless of their language or region.

The modular architecture allows for easy expansion to support additional languages and locales as the user base grows. The separation of code and content, along with automated tools for translation management, ensures that the localization process remains efficient and maintainable.

Through continuous testing, validation, and user feedback, the internationalization system will evolve to meet the diverse needs of the global user community.

---

*Document created on August 28, 2025*  
*Version: 1.0*
