# UI Theme and Branding Finalization

## Overview

This document finalizes the UI theme and branding for VPA, establishing a consistent visual identity that enhances user experience across the application.

## Table of Contents

1. [Brand Identity](#1-brand-identity)
2. [Color Palette](#2-color-palette)
3. [Typography](#3-typography)
4. [UI Components](#4-ui-components)
5. [Dark Mode and Light Mode](#5-dark-mode-and-light-mode)
6. [Implementation](#6-implementation)

## 1. Brand Identity

### 1.1 Brand Name and Logo

**Brand Name**: VPA (Virtual Personal Assistant)

**Logo Design**:
- Primary Logo: Simple, modern "VPA" logotype with an abstract assistant icon
- App Icon: Simplified icon version for taskbar/desktop
- Logo Variants: Light, dark, and monochrome versions for different backgrounds

![VPA Logo](assets/branding/vpa_logo_primary.png)

### 1.2 Brand Guidelines

**Brand Voice**:
- Friendly and approachable
- Professional and reliable
- Helpful without being intrusive
- Modern and tech-forward

**Brand Values**:
- Privacy-focused
- Efficiency and productivity
- User empowerment
- Clarity and simplicity

### 1.3 Tagline

"Your Personal AI Assistant, Privately Yours"

## 2. Color Palette

### 2.1 Primary Colors

| Color Name | Hex Code | RGB | Role |
|------------|----------|-----|------|
| Primary Blue | #2563EB | rgb(37, 99, 235) | Primary accent, buttons, links |
| Secondary Purple | #7C3AED | rgb(124, 58, 237) | Secondary accent, highlights |
| Neutral Gray | #334155 | rgb(51, 65, 85) | Primary text, icons |

### 2.2 Secondary Colors

| Color Name | Hex Code | RGB | Role |
|------------|----------|-----|------|
| Success Green | #10B981 | rgb(16, 185, 129) | Success states, confirmations |
| Warning Amber | #F59E0B | rgb(245, 158, 11) | Warning states, important notices |
| Error Red | #EF4444 | rgb(239, 68, 68) | Error states, critical alerts |
| Info Cyan | #06B6D4 | rgb(6, 182, 212) | Information, system messages |

### 2.3 Neutral Colors

| Color Name | Hex Code | RGB | Role |
|------------|----------|-----|------|
| Background Light | #F8FAFC | rgb(248, 250, 252) | Light mode background |
| Background Dark | #0F172A | rgb(15, 23, 42) | Dark mode background |
| Surface Light | #FFFFFF | rgb(255, 255, 255) | Light mode cards/panels |
| Surface Dark | #1E293B | rgb(30, 41, 59) | Dark mode cards/panels |
| Text Primary Light | #334155 | rgb(51, 65, 85) | Light mode primary text |
| Text Primary Dark | #E2E8F0 | rgb(226, 232, 240) | Dark mode primary text |
| Text Secondary Light | #64748B | rgb(100, 116, 139) | Light mode secondary text |
| Text Secondary Dark | #94A3B8 | rgb(148, 163, 184) | Dark mode secondary text |
| Border Light | #E2E8F0 | rgb(226, 232, 240) | Light mode borders |
| Border Dark | #334155 | rgb(51, 65, 85) | Dark mode borders |

### 2.4 Gradients

| Gradient Name | Colors | Usage |
|---------------|--------|-------|
| Primary Gradient | #2563EB to #7C3AED | Headers, feature highlights |
| Accent Gradient | #7C3AED to #C084FC | Special actions, premium features |
| Surface Gradient Light | #F8FAFC to #FFFFFF | Subtle backgrounds (light mode) |
| Surface Gradient Dark | #0F172A to #1E293B | Subtle backgrounds (dark mode) |

## 3. Typography

### 3.1 Font Families

**Primary Font**: Inter
- Regular (400) for body text
- Medium (500) for emphasis
- SemiBold (600) for subheadings
- Bold (700) for headings

**Monospace Font**: JetBrains Mono
- Regular (400) for code blocks
- Medium (500) for emphasis in code

### 3.2 Type Scale

| Element | Font | Weight | Size | Line Height |
|---------|------|--------|------|------------|
| Heading 1 | Inter | Bold (700) | 24px | 32px |
| Heading 2 | Inter | Bold (700) | 20px | 28px |
| Heading 3 | Inter | SemiBold (600) | 16px | 24px |
| Body | Inter | Regular (400) | 14px | 20px |
| Body Small | Inter | Regular (400) | 12px | 16px |
| Caption | Inter | Medium (500) | 11px | 16px |
| Code | JetBrains Mono | Regular (400) | 14px | 20px |
| Button | Inter | Medium (500) | 14px | 20px |

### 3.3 Font Implementation

```python
class FontManager:
    """Manages font loading and application"""
    
    def __init__(self):
        self.font_families = {
            "primary": "Inter",
            "monospace": "JetBrains Mono"
        }
        self.fonts_loaded = False
        
    def initialize(self):
        """Initialize and load fonts"""
        from PyQt6.QtGui import QFontDatabase
        
        # Add font files
        font_dir = os.path.join(os.path.dirname(__file__), "../assets/fonts")
        
        # Load Inter font
        inter_fonts = [
            "Inter-Regular.ttf",
            "Inter-Medium.ttf",
            "Inter-SemiBold.ttf",
            "Inter-Bold.ttf"
        ]
        
        for font in inter_fonts:
            font_path = os.path.join(font_dir, "Inter", font)
            QFontDatabase.addApplicationFont(font_path)
            
        # Load JetBrains Mono font
        jetbrains_fonts = [
            "JetBrainsMono-Regular.ttf",
            "JetBrainsMono-Medium.ttf",
            "JetBrainsMono-Bold.ttf"
        ]
        
        for font in jetbrains_fonts:
            font_path = os.path.join(font_dir, "JetBrainsMono", font)
            QFontDatabase.addApplicationFont(font_path)
            
        self.fonts_loaded = True
        
    def get_font_family(self, font_type):
        """Get font family by type"""
        return self.font_families.get(font_type, self.font_families["primary"])
```

## 4. UI Components

### 4.1 Chat Components

#### 4.1.1 Chat Bubbles

**User Message Bubble**:
- Background: Surface Light/Dark
- Text: Text Primary Light/Dark
- Border: None
- Border Radius: 16px
- Padding: 12px 16px
- Max Width: 80% of container
- Alignment: Right side
- Avatar: User profile picture or default avatar
- Timestamp: Below message, Text Secondary Light/Dark

**Assistant Message Bubble**:
- Background: Very light primary color (#EFF6FF in light mode, #1E3A8A in dark mode)
- Text: Text Primary Light/Dark
- Border: None
- Border Radius: 16px
- Padding: 12px 16px
- Max Width: 80% of container
- Alignment: Left side
- Avatar: VPA logo/icon
- Timestamp: Below message, Text Secondary Light/Dark

#### 4.1.2 Chat Input

**Text Input Field**:
- Background: Surface Light/Dark
- Border: Border Light/Dark
- Border Radius: 24px
- Padding: 12px 16px
- Focus State: Primary Blue border
- Placeholder: Text Secondary Light/Dark

**Send Button**:
- Icon: Paper plane icon
- Background: Primary Blue
- Border Radius: 50%
- Size: 40px × 40px
- Hover: Slight brightness increase

**Voice Input Button**:
- Icon: Microphone icon
- Background: Secondary Purple
- Border Radius: 50%
- Size: 40px × 40px
- Active State: Pulsing animation
- Hover: Slight brightness increase

**Attachment Button**:
- Icon: Paperclip icon
- Background: Transparent
- Border: Border Light/Dark
- Border Radius: 50%
- Size: 40px × 40px
- Hover: Light background

### 4.2 Navigation Components

#### 4.2.1 Sidebar

**Container**:
- Background: Surface Dark in both themes (for contrast)
- Width: 250px (collapsible to 70px)
- Height: 100% of window

**Menu Items**:
- Text: Text Primary Dark
- Padding: 12px 16px
- Hover: 10% white overlay
- Active: Primary Blue left border, 10% Primary Blue overlay
- Icon: Left-aligned, 20px × 20px
- Text: 14px, Medium weight

**Categories**:
- Divider: Border Dark
- Category Label: Text Secondary Dark, all caps, 11px

**User Profile**:
- Avatar: 40px × 40px, circular
- Username: Text Primary Dark, 14px, Medium
- Status: Text Secondary Dark, 12px

#### 4.2.2 Top Navigation Bar

**Container**:
- Background: Surface Light/Dark
- Height: 60px
- Border Bottom: Border Light/Dark

**Title**:
- Text: Text Primary Light/Dark, 16px, SemiBold
- Alignment: Center

**Controls**:
- Background: Transparent
- Icon Color: Text Secondary Light/Dark
- Hover: 10% Text Secondary overlay
- Size: 40px × 40px

### 4.3 Common Components

#### 4.3.1 Buttons

**Primary Button**:
- Background: Primary Blue
- Text: White
- Border Radius: 8px
- Padding: 8px 16px
- Hover: Brightness increase
- Disabled: 50% opacity

**Secondary Button**:
- Background: Transparent
- Text: Primary Blue
- Border: 1px Primary Blue
- Border Radius: 8px
- Padding: 8px 16px
- Hover: Light Primary Blue background
- Disabled: 50% opacity

**Tertiary Button**:
- Background: Transparent
- Text: Text Primary Light/Dark
- Border: None
- Padding: 8px 16px
- Hover: Border Light/Dark background
- Disabled: 50% opacity

#### 4.3.2 Form Controls

**Text Input**:
- Background: Surface Light/Dark
- Border: Border Light/Dark
- Border Radius: 8px
- Padding: 8px 12px
- Focus: Primary Blue border
- Error: Error Red border

**Checkbox**:
- Border: Border Light/Dark
- Border Radius: 4px
- Checked: Primary Blue background, white checkmark
- Size: 16px × 16px

**Radio Button**:
- Border: Border Light/Dark
- Border Radius: 50%
- Checked: Primary Blue outer ring, Primary Blue center dot
- Size: 16px × 16px

**Dropdown**:
- Background: Surface Light/Dark
- Border: Border Light/Dark
- Border Radius: 8px
- Arrow: Text Secondary Light/Dark
- Options Background: Surface Light/Dark
- Option Hover: 10% Primary Blue overlay

#### 4.3.3 Cards

**Standard Card**:
- Background: Surface Light/Dark
- Border: Border Light/Dark
- Border Radius: 12px
- Shadow: Light shadow in light mode, none in dark mode
- Padding: 16px

**Feature Card**:
- Background: Surface Light/Dark
- Border: Border Light/Dark
- Border Radius: 12px
- Shadow: Medium shadow in light mode, slight shadow in dark mode
- Header: Primary Gradient background
- Header Text: White
- Body Padding: 16px

#### 4.3.4 Dialogs

**Modal Dialog**:
- Background: Surface Light/Dark
- Border Radius: 16px
- Shadow: Strong shadow in light mode, medium shadow in dark mode
- Header: Border bottom Border Light/Dark
- Header Text: Text Primary Light/Dark, 18px, SemiBold
- Body Padding: 24px
- Footer: Border top Border Light/Dark
- Footer Padding: 16px

## 5. Dark Mode and Light Mode

### 5.1 Theme Management

```python
class ThemeManager:
    """Manages application theming"""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.current_theme = "system"  # "light", "dark", or "system"
        self.load_theme_preference()
        
    def load_theme_preference(self):
        """Load theme preference from settings"""
        self.current_theme = self.settings_manager.get("ui.theme", "system")
        
    def save_theme_preference(self):
        """Save theme preference to settings"""
        self.settings_manager.set("ui.theme", self.current_theme)
        
    def get_effective_theme(self):
        """Get the effective theme based on preference and system"""
        if self.current_theme == "system":
            # Detect system theme
            import darkdetect
            return "dark" if darkdetect.isDark() else "light"
        return self.current_theme
        
    def set_theme(self, theme):
        """Set theme and apply it"""
        if theme in ["light", "dark", "system"]:
            self.current_theme = theme
            self.save_theme_preference()
            self.apply_theme()
            
    def apply_theme(self):
        """Apply the current theme to the application"""
        effective_theme = self.get_effective_theme()
        
        # Get theme colors
        colors = self._get_theme_colors(effective_theme)
        
        # Create stylesheet
        stylesheet = self._generate_stylesheet(colors)
        
        # Apply stylesheet to application
        from PyQt6.QtWidgets import QApplication
        QApplication.instance().setStyleSheet(stylesheet)
        
    def _get_theme_colors(self, theme):
        """Get colors for the specified theme"""
        if theme == "light":
            return {
                "background": "#F8FAFC",
                "surface": "#FFFFFF",
                "text_primary": "#334155",
                "text_secondary": "#64748B",
                "border": "#E2E8F0",
                "primary": "#2563EB",
                "secondary": "#7C3AED",
                "success": "#10B981",
                "warning": "#F59E0B",
                "error": "#EF4444",
                "info": "#06B6D4",
                "chat_user_bg": "#F8FAFC",
                "chat_assistant_bg": "#EFF6FF"
            }
        else:  # dark
            return {
                "background": "#0F172A",
                "surface": "#1E293B",
                "text_primary": "#E2E8F0",
                "text_secondary": "#94A3B8",
                "border": "#334155",
                "primary": "#3B82F6",
                "secondary": "#8B5CF6",
                "success": "#10B981",
                "warning": "#F59E0B",
                "error": "#EF4444",
                "info": "#06B6D4",
                "chat_user_bg": "#1E293B",
                "chat_assistant_bg": "#1E3A8A"
            }
            
    def _generate_stylesheet(self, colors):
        """Generate application stylesheet from colors"""
        return f"""
            /* Global Styles */
            QWidget {{
                background-color: {colors["background"]};
                color: {colors["text_primary"]};
                font-family: "Inter";
                font-size: 14px;
            }}
            
            /* Window */
            QMainWindow {{
                background-color: {colors["background"]};
            }}
            
            /* Buttons */
            QPushButton {{
                background-color: {colors["primary"]};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
            }}
            
            QPushButton:hover {{
                background-color: {self._adjust_brightness(colors["primary"], 1.1)};
            }}
            
            QPushButton:disabled {{
                background-color: {colors["primary"]};
                opacity: 0.5;
            }}
            
            QPushButton.secondary {{
                background-color: transparent;
                color: {colors["primary"]};
                border: 1px solid {colors["primary"]};
            }}
            
            QPushButton.secondary:hover {{
                background-color: {self._adjust_brightness(colors["primary"], 0.1)};
            }}
            
            QPushButton.tertiary {{
                background-color: transparent;
                color: {colors["text_primary"]};
                border: none;
            }}
            
            QPushButton.tertiary:hover {{
                background-color: {colors["border"]};
            }}
            
            /* Input Fields */
            QLineEdit, QTextEdit, QPlainTextEdit {{
                background-color: {colors["surface"]};
                color: {colors["text_primary"]};
                border: 1px solid {colors["border"]};
                border-radius: 8px;
                padding: 8px 12px;
            }}
            
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border: 1px solid {colors["primary"]};
            }}
            
            /* Checkboxes and Radio Buttons */
            QCheckBox, QRadioButton {{
                spacing: 8px;
                color: {colors["text_primary"]};
            }}
            
            QCheckBox::indicator, QRadioButton::indicator {{
                width: 16px;
                height: 16px;
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {colors["primary"]};
                border: 1px solid {colors["primary"]};
            }}
            
            QCheckBox::indicator:unchecked {{
                background-color: {colors["surface"]};
                border: 1px solid {colors["border"]};
            }}
            
            QRadioButton::indicator:checked {{
                background-color: {colors["primary"]};
                border: 2px solid {colors["primary"]};
            }}
            
            QRadioButton::indicator:unchecked {{
                background-color: {colors["surface"]};
                border: 1px solid {colors["border"]};
            }}
            
            /* Combobox (Dropdown) */
            QComboBox {{
                background-color: {colors["surface"]};
                color: {colors["text_primary"]};
                border: 1px solid {colors["border"]};
                border-radius: 8px;
                padding: 8px 12px;
                min-width: 6em;
            }}
            
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 0px;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {colors["surface"]};
                color: {colors["text_primary"]};
                border: 1px solid {colors["border"]};
                selection-background-color: {self._adjust_brightness(colors["primary"], 0.2)};
            }}
            
            /* Scrollbars */
            QScrollBar:vertical {{
                border: none;
                background: {colors["background"]};
                width: 8px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {colors["border"]};
                border-radius: 4px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {colors["text_secondary"]};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            /* Tabs */
            QTabWidget::pane {{
                border: 1px solid {colors["border"]};
                border-radius: 8px;
                top: -1px;
            }}
            
            QTabBar::tab {{
                background-color: transparent;
                color: {colors["text_secondary"]};
                border-bottom: 2px solid transparent;
                padding: 8px 16px;
            }}
            
            QTabBar::tab:selected {{
                color: {colors["primary"]};
                border-bottom: 2px solid {colors["primary"]};
            }}
            
            QTabBar::tab:hover:!selected {{
                color: {colors["text_primary"]};
            }}
            
            /* Menu */
            QMenuBar {{
                background-color: {colors["surface"]};
                color: {colors["text_primary"]};
                border-bottom: 1px solid {colors["border"]};
            }}
            
            QMenuBar::item {{
                padding: 4px 8px;
                background: transparent;
            }}
            
            QMenuBar::item:selected {{
                background-color: {self._adjust_brightness(colors["primary"], 0.2)};
            }}
            
            QMenu {{
                background-color: {colors["surface"]};
                color: {colors["text_primary"]};
                border: 1px solid {colors["border"]};
            }}
            
            QMenu::item {{
                padding: 6px 20px 6px 20px;
            }}
            
            QMenu::item:selected {{
                background-color: {self._adjust_brightness(colors["primary"], 0.2)};
            }}
            
            /* Custom Chat Components */
            QWidget#chatUserBubble {{
                background-color: {colors["chat_user_bg"]};
                border-radius: 16px;
                padding: 12px;
            }}
            
            QWidget#chatAssistantBubble {{
                background-color: {colors["chat_assistant_bg"]};
                border-radius: 16px;
                padding: 12px;
            }}
            
            QLineEdit#chatInput {{
                border-radius: 24px;
                padding: 12px 16px;
                background-color: {colors["surface"]};
            }}
            
            QPushButton#voiceButton {{
                background-color: {colors["secondary"]};
                border-radius: 20px;
                min-width: 40px;
                min-height: 40px;
                max-width: 40px;
                max-height: 40px;
                padding: 0px;
            }}
            
            QPushButton#sendButton {{
                background-color: {colors["primary"]};
                border-radius: 20px;
                min-width: 40px;
                min-height: 40px;
                max-width: 40px;
                max-height: 40px;
                padding: 0px;
            }}
            
            QPushButton#attachmentButton {{
                background-color: transparent;
                border: 1px solid {colors["border"]};
                border-radius: 20px;
                min-width: 40px;
                min-height: 40px;
                max-width: 40px;
                max-height: 40px;
                padding: 0px;
            }}
            
            /* Sidebar */
            QWidget#sidebar {{
                background-color: {colors["surface"]};
                min-width: 250px;
                max-width: 250px;
                padding: 0px;
            }}
            
            QPushButton.sidebarItem {{
                background-color: transparent;
                border: none;
                border-radius: 0px;
                padding: 12px 16px;
                text-align: left;
                color: {colors["text_primary"]};
            }}
            
            QPushButton.sidebarItem:hover {{
                background-color: {self._adjust_brightness(colors["surface"], 1.1 if theme == "light" else 0.9)};
            }}
            
            QPushButton.sidebarItemActive {{
                background-color: {self._adjust_brightness(colors["primary"], 0.2)};
                border-left: 3px solid {colors["primary"]};
                color: {colors["primary"]};
            }}
            
            QLabel.sidebarCategory {{
                color: {colors["text_secondary"]};
                font-size: 11px;
                font-weight: 500;
                text-transform: uppercase;
                padding: 8px 16px 4px 16px;
            }}
            
            /* Top Navigation */
            QWidget#topNavigation {{
                background-color: {colors["surface"]};
                border-bottom: 1px solid {colors["border"]};
                min-height: 60px;
                max-height: 60px;
            }}
            
            QLabel#windowTitle {{
                color: {colors["text_primary"]};
                font-size: 16px;
                font-weight: 600;
            }}
            
            /* Cards */
            QFrame.card {{
                background-color: {colors["surface"]};
                border: 1px solid {colors["border"]};
                border-radius: 12px;
            }}
            
            /* Dialogs */
            QDialog {{
                background-color: {colors["background"]};
            }}
            
            QWidget#dialogHeader {{
                background-color: {colors["surface"]};
                border-bottom: 1px solid {colors["border"]};
                min-height: 50px;
            }}
            
            QLabel#dialogTitle {{
                color: {colors["text_primary"]};
                font-size: 18px;
                font-weight: 600;
            }}
            
            QWidget#dialogFooter {{
                background-color: {colors["surface"]};
                border-top: 1px solid {colors["border"]};
                min-height: 60px;
            }}
        """
        
    def _adjust_brightness(self, hex_color, factor):
        """Adjust color brightness by factor"""
        import colorsys
        
        # Convert hex to RGB
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Convert RGB to HLS
        h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
        
        # Adjust lightness
        l = max(min(l * factor, 1.0), 0.0)
        
        # Convert back to RGB
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        
        # Convert to hex
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
```

### 5.2 Theme Settings UI

```python
class ThemeSettingsWidget(QWidget):
    """Widget for theme settings"""
    
    def __init__(self, theme_manager):
        super().__init__()
        self.theme_manager = theme_manager
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        
        # Theme group
        theme_group = QGroupBox("Appearance")
        theme_layout = QVBoxLayout(theme_group)
        
        # Theme radio buttons
        self.theme_system = QRadioButton("Use System Setting")
        self.theme_light = QRadioButton("Light Mode")
        self.theme_dark = QRadioButton("Dark Mode")
        
        # Set current selection
        current_theme = self.theme_manager.current_theme
        if current_theme == "system":
            self.theme_system.setChecked(True)
        elif current_theme == "light":
            self.theme_light.setChecked(True)
        else:
            self.theme_dark.setChecked(True)
            
        # Connect signals
        self.theme_system.toggled.connect(self._on_theme_changed)
        self.theme_light.toggled.connect(self._on_theme_changed)
        self.theme_dark.toggled.connect(self._on_theme_changed)
        
        # Add to layout
        theme_layout.addWidget(self.theme_system)
        theme_layout.addWidget(self.theme_light)
        theme_layout.addWidget(self.theme_dark)
        
        # Add theme group to main layout
        layout.addWidget(theme_group)
        
        # UI density
        density_group = QGroupBox("UI Density")
        density_layout = QVBoxLayout(density_group)
        
        self.density_compact = QRadioButton("Compact (more content)")
        self.density_standard = QRadioButton("Standard")
        self.density_comfortable = QRadioButton("Comfortable (more spacing)")
        
        # Set current selection
        density = self.theme_manager.settings_manager.get("ui.density", "standard")
        if density == "compact":
            self.density_compact.setChecked(True)
        elif density == "standard":
            self.density_standard.setChecked(True)
        else:
            self.density_comfortable.setChecked(True)
            
        # Connect signals
        self.density_compact.toggled.connect(self._on_density_changed)
        self.density_standard.toggled.connect(self._on_density_changed)
        self.density_comfortable.toggled.connect(self._on_density_changed)
        
        # Add to layout
        density_layout.addWidget(self.density_compact)
        density_layout.addWidget(self.density_standard)
        density_layout.addWidget(self.density_comfortable)
        
        # Add density group to main layout
        layout.addWidget(density_group)
        
        # Accent color
        accent_group = QGroupBox("Accent Color")
        accent_layout = QGridLayout(accent_group)
        
        # Color options
        accent_colors = [
            {"name": "Blue", "value": "#2563EB"},
            {"name": "Purple", "value": "#7C3AED"},
            {"name": "Green", "value": "#10B981"},
            {"name": "Pink", "value": "#EC4899"},
            {"name": "Orange", "value": "#F59E0B"},
            {"name": "Red", "value": "#EF4444"}
        ]
        
        # Create color buttons
        self.accent_buttons = []
        current_accent = self.theme_manager.settings_manager.get("ui.accent_color", "#2563EB")
        
        for i, color in enumerate(accent_colors):
            button = QPushButton()
            button.setFixedSize(30, 30)
            button.setStyleSheet(f"background-color: {color['value']}; border-radius: 15px;")
            button.setCheckable(True)
            button.setChecked(color['value'] == current_accent)
            button.setToolTip(color['name'])
            button.color_value = color['value']
            button.toggled.connect(self._on_accent_color_changed)
            
            # Add to grid, 3 colors per row
            accent_layout.addWidget(button, i // 3, i % 3)
            self.accent_buttons.append(button)
            
        # Add accent group to main layout
        layout.addWidget(accent_group)
        
        # Add stretch to push everything up
        layout.addStretch(1)
        
    def _on_theme_changed(self):
        """Handle theme change"""
        if self.theme_system.isChecked():
            self.theme_manager.set_theme("system")
        elif self.theme_light.isChecked():
            self.theme_manager.set_theme("light")
        else:
            self.theme_manager.set_theme("dark")
            
    def _on_density_changed(self):
        """Handle density change"""
        if self.density_compact.isChecked():
            density = "compact"
        elif self.density_standard.isChecked():
            density = "standard"
        else:
            density = "comfortable"
            
        self.theme_manager.settings_manager.set("ui.density", density)
        self.theme_manager.apply_theme()
        
    def _on_accent_color_changed(self):
        """Handle accent color change"""
        sender = self.sender()
        if sender.isChecked():
            # Uncheck other buttons
            for button in self.accent_buttons:
                if button != sender:
                    button.setChecked(False)
                    
            # Set accent color
            self.theme_manager.settings_manager.set("ui.accent_color", sender.color_value)
            self.theme_manager.apply_theme()
```

## 6. Implementation

### 6.1 Theme Application

The VPA UI theme will be implemented through:

1. **Stylesheet Approach**: Using Qt stylesheets for basic styling
2. **Custom Painting**: Custom widget painting for advanced UI components
3. **Themed Icons**: SVG icons with dynamic color adaptation
4. **Component Library**: Reusable styled components

### 6.2 Icon System

VPA will use an icon system with theme-aware capabilities:

```python
class IconProvider:
    """Provides themed icons"""
    
    def __init__(self, theme_manager):
        self.theme_manager = theme_manager
        self.icon_cache = {}
        
    def get_icon(self, icon_name):
        """Get themed icon by name"""
        theme = self.theme_manager.get_effective_theme()
        cache_key = f"{icon_name}_{theme}"
        
        # Check cache first
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
            
        # Get icon path
        icon_path = self._get_icon_path(icon_name, theme)
        
        # Create QIcon
        from PyQt6.QtGui import QIcon
        icon = QIcon(icon_path)
        
        # Cache icon
        self.icon_cache[cache_key] = icon
        
        return icon
        
    def _get_icon_path(self, icon_name, theme):
        """Get path to icon file"""
        # Check theme-specific icon first
        theme_path = f"assets/icons/{theme}/{icon_name}.svg"
        if os.path.exists(theme_path):
            return theme_path
            
        # Fall back to common icon
        common_path = f"assets/icons/common/{icon_name}.svg"
        if os.path.exists(common_path):
            return common_path
            
        # Fall back to default icon
        return f"assets/icons/common/default.svg"
        
    def clear_cache(self):
        """Clear icon cache"""
        self.icon_cache = {}
```

### 6.3 Animation System

VPA will include subtle animations to enhance the user experience:

```python
class AnimationManager:
    """Manages UI animations"""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.animations_enabled = self.settings_manager.get("ui.animations_enabled", True)
        
    def is_enabled(self):
        """Check if animations are enabled"""
        return self.animations_enabled
        
    def set_enabled(self, enabled):
        """Enable or disable animations"""
        self.animations_enabled = enabled
        self.settings_manager.set("ui.animations_enabled", enabled)
        
    def create_fade_animation(self, target, property_name, start_value, end_value, duration=300):
        """Create a fade animation"""
        if not self.animations_enabled:
            # If animations disabled, just set the end value
            target.setProperty(property_name, end_value)
            return None
            
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
        
        animation = QPropertyAnimation(target, property_name.encode())
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        return animation
        
    def create_slide_animation(self, target, start_pos, end_pos, duration=300):
        """Create a slide animation"""
        if not self.animations_enabled:
            # If animations disabled, just set the end position
            target.move(end_pos)
            return None
            
        from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
        
        animation = QPropertyAnimation(target, b"pos")
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        return animation
```

### 6.4 Component Usage Examples

#### 6.4.1 Chat Bubble Implementation

```python
class ChatBubble(QWidget):
    """Chat message bubble widget"""
    
    def __init__(self, message, is_user=False, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_user = is_user
        self.setObjectName("chatUserBubble" if is_user else "chatAssistantBubble")
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the UI components"""
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Avatar
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(36, 36)
        
        # Set avatar image
        if self.is_user:
            # User avatar from settings or default
            user_avatar = self.parent().parent().settings_manager.get("user.avatar")
            if user_avatar and os.path.exists(user_avatar):
                pixmap = QPixmap(user_avatar)
            else:
                pixmap = QPixmap("assets/images/default_user.png")
        else:
            # VPA avatar
            pixmap = QPixmap("assets/images/vpa_avatar.png")
            
        # Make avatar circular
        rounded_pixmap = QPixmap(36, 36)
        rounded_pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(rounded_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, 36, 36)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap.scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
        painter.end()
        
        self.avatar_label.setPixmap(rounded_pixmap)
        
        # Message layout (bubble + timestamp)
        message_layout = QVBoxLayout()
        message_layout.setSpacing(4)
        
        # Message bubble
        bubble_widget = QWidget()
        bubble_widget.setObjectName("chatUserBubble" if self.is_user else "chatAssistantBubble")
        bubble_layout = QVBoxLayout(bubble_widget)
        bubble_layout.setContentsMargins(12, 12, 12, 12)
        
        # Message text
        message_text = QLabel(self.message.text)
        message_text.setWordWrap(True)
        message_text.setTextFormat(Qt.TextFormat.RichText)
        message_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        message_text.setOpenExternalLinks(True)
        
        bubble_layout.addWidget(message_text)
        
        # Add bubble to message layout
        message_layout.addWidget(bubble_widget)
        
        # Timestamp
        timestamp_label = QLabel(self.message.timestamp.strftime("%H:%M"))
        timestamp_label.setStyleSheet("color: #64748B; font-size: 11px;")
        timestamp_label.setAlignment(Qt.AlignmentFlag.AlignLeft if not self.is_user else Qt.AlignmentFlag.AlignRight)
        
        message_layout.addWidget(timestamp_label)
        
        # Add components to main layout based on user/assistant
        if self.is_user:
            main_layout.addStretch(1)
            main_layout.addLayout(message_layout)
            main_layout.addWidget(self.avatar_label)
        else:
            main_layout.addWidget(self.avatar_label)
            main_layout.addLayout(message_layout)
            main_layout.addStretch(1)
```

#### 6.4.2 Chat Input Implementation

```python
class ChatInputWidget(QWidget):
    """Chat input widget with voice button"""
    
    messageSubmitted = pyqtSignal(str)
    voiceInputRequested = pyqtSignal()
    attachmentRequested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_recording = False
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the UI components"""
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Attachment button
        self.attachment_button = QPushButton()
        self.attachment_button.setObjectName("attachmentButton")
        self.attachment_button.setIcon(self.parent().icon_provider.get_icon("attachment"))
        self.attachment_button.setFixedSize(40, 40)
        self.attachment_button.setToolTip("Add attachment")
        self.attachment_button.clicked.connect(self.attachmentRequested)
        
        # Text input
        self.input_field = QLineEdit()
        self.input_field.setObjectName("chatInput")
        self.input_field.setPlaceholderText("Type a message...")
        self.input_field.returnPressed.connect(self._on_send)
        
        # Voice input button
        self.voice_button = QPushButton()
        self.voice_button.setObjectName("voiceButton")
        self.voice_button.setIcon(self.parent().icon_provider.get_icon("microphone"))
        self.voice_button.setFixedSize(40, 40)
        self.voice_button.setToolTip("Voice input")
        self.voice_button.clicked.connect(self._on_voice)
        
        # Send button
        self.send_button = QPushButton()
        self.send_button.setObjectName("sendButton")
        self.send_button.setIcon(self.parent().icon_provider.get_icon("send"))
        self.send_button.setFixedSize(40, 40)
        self.send_button.setToolTip("Send message")
        self.send_button.clicked.connect(self._on_send)
        
        # Add to layout
        layout.addWidget(self.attachment_button)
        layout.addWidget(self.input_field, 1)
        layout.addWidget(self.voice_button)
        layout.addWidget(self.send_button)
        
        # Update send button state
        self._update_send_button()
        self.input_field.textChanged.connect(self._update_send_button)
        
    def _update_send_button(self):
        """Update send button state based on input"""
        self.send_button.setEnabled(bool(self.input_field.text()))
        
    def _on_send(self):
        """Handle send button click"""
        message = self.input_field.text().strip()
        if message:
            self.messageSubmitted.emit(message)
            self.input_field.clear()
            
    def _on_voice(self):
        """Handle voice button click"""
        if self.is_recording:
            # Stop recording
            self.voice_button.setIcon(self.parent().icon_provider.get_icon("microphone"))
            self.voice_button.setStyleSheet("")
            self.is_recording = False
        else:
            # Start recording
            self.voice_button.setIcon(self.parent().icon_provider.get_icon("microphone_active"))
            self.voice_button.setStyleSheet("background-color: #EF4444;")  # Red when recording
            self.is_recording = True
            
        self.voiceInputRequested.emit()
        
    def set_voice_active(self, active):
        """Set voice button active state from outside"""
        self.is_recording = active
        if active:
            self.voice_button.setIcon(self.parent().icon_provider.get_icon("microphone_active"))
            self.voice_button.setStyleSheet("background-color: #EF4444;")  # Red when recording
        else:
            self.voice_button.setIcon(self.parent().icon_provider.get_icon("microphone"))
            self.voice_button.setStyleSheet("")
```

## Conclusion

This UI Theme and Branding Finalization document establishes a comprehensive visual identity for VPA. By defining consistent color palettes, typography, and component designs, VPA provides users with a modern, accessible, and visually appealing interface.

The implementation supports both light and dark modes, with careful attention to accessibility and user experience. The component library approach ensures visual consistency across the application while allowing for efficient development.

---

*Document created on August 28, 2025*  
*Version: 1.0*
