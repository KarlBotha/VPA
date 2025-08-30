# UI Theme and Branding Guidelines

## Overview

This document defines the visual identity, design language, and UI theme guidelines for VPA (Virtual Personal Assistant). It provides a comprehensive framework for creating a consistent, accessible, and engaging user experience across all components of the application.

## Table of Contents

1. [Brand Identity](#1-brand-identity)
2. [Color Palette](#2-color-palette)
3. [Typography](#3-typography)
4. [UI Components](#4-ui-components)
5. [Iconography](#5-iconography)
6. [Layout Principles](#6-layout-principles)
7. [Animation and Transitions](#7-animation-and-transitions)
8. [Accessibility Guidelines](#8-accessibility-guidelines)
9. [Theme Implementation](#9-theme-implementation)
10. [Future Considerations](#10-future-considerations)

## 1. Brand Identity

### 1.1 Brand Essence

VPA represents:

- **Intelligence**: Sophisticated AI capabilities that adapt to user needs
- **Reliability**: Consistent and trustworthy performance
- **Simplicity**: Intuitive design that reduces complexity
- **Personalization**: Tailored experiences based on user preferences
- **Privacy**: Respect for user data and confidential information

### 1.2 Logo Guidelines

The VPA logo consists of two elements:

- **Logomark**: A stylized "V" that incorporates a sound wave and circuit pattern
- **Logotype**: "VPA" in the primary font with optional subtitle "Virtual Personal Assistant"

Logo usage rules:
- Maintain clear space (equal to height of "V") around the logo
- Minimum size of 32px height for digital use
- Do not stretch, recolor outside the approved palette, or add effects
- Preferred placement is top-left in the application header

### 1.3 Brand Voice

All text in the application should follow these principles:
- **Concise**: Direct and efficient communication
- **Helpful**: Focusing on assisting the user
- **Professional**: Technically accurate but not overly formal
- **Encouraging**: Positive reinforcement of user actions

## 2. Color Palette

### 2.1 Primary Colors

```
Primary Blue: #2D7FF9
  - Dark: #1A63D0
  - Light: #6BA5FA

Primary Purple: #7E57C2
  - Dark: #5E35B1
  - Light: #9575CD
```

### 2.2 Secondary Colors

```
Accent Green: #26A69A
  - Dark: #00897B
  - Light: #4DB6AC

Accent Amber: #FFB300
  - Dark: #FF8F00
  - Light: #FFD54F
```

### 2.3 Neutral Colors

```
Background Gray: #F5F7FA
Dark Gray: #333333
Medium Gray: #757575
Light Gray: #E0E0E0
White: #FFFFFF
```

### 2.4 Semantic Colors

```
Success: #43A047
Warning: #FB8C00
Error: #E53935
Info: #2196F3
```

### 2.5 Dark Mode Colors

```
Dark Background: #121212
Dark Surface: #1E1E1E
Dark Card: #252525
Dark Border: #333333
Dark Text Primary: #E0E0E0
Dark Text Secondary: #A0A0A0
```

### 2.6 Color Usage Guidelines

- Primary colors should be used for main actions, navigation, and branding
- Secondary colors are for accents, highlighting, and secondary actions
- Neutral colors form the foundation of layouts and text
- Semantic colors should only be used for their specific meaning
- Maintain a 4.5:1 contrast ratio minimum for text legibility

## 3. Typography

### 3.1 Font Families

```
Primary Font: Inter
Secondary Font: Roboto Mono (for code and technical information)
```

### 3.2 Font Sizes

```
Display Large: 40px / 48px line height
Display Medium: 36px / 44px line height
Display Small: 30px / 38px line height

Heading 1: 24px / 32px line height
Heading 2: 20px / 28px line height
Heading 3: 18px / 26px line height
Heading 4: 16px / 24px line height

Body Large: 16px / 24px line height
Body Medium: 14px / 22px line height
Body Small: 12px / 20px line height

Caption: 12px / 16px line height
```

### 3.3 Font Weights

```
Light: 300
Regular: 400
Medium: 500
SemiBold: 600
Bold: 700
```

### 3.4 Typography Guidelines

- Use font weights to create hierarchy rather than multiple font sizes
- Maintain consistent line heights for readability
- Limit use of all-caps to short labels and buttons
- Follow a consistent type scale throughout the application
- Allow dynamic font sizing to support accessibility needs

## 4. UI Components

### 4.1 Buttons

Primary buttons should:
- Use the primary color
- Have 8px padding top/bottom and 16px padding left/right
- Include 4px rounded corners
- Display a subtle hover and active state
- Include a 500ms transition for hover states

```python
class ThemeButton(QPushButton):
    """Styled button component following design system"""
    
    VARIANTS = {
        "primary": {
            "background": "#2D7FF9",
            "text": "#FFFFFF",
            "hover_background": "#1A63D0",
            "active_background": "#0D47A1",
            "border": "none"
        },
        "secondary": {
            "background": "#FFFFFF",
            "text": "#2D7FF9",
            "hover_background": "#F5F7FA",
            "active_background": "#E0E0E0",
            "border": "1px solid #2D7FF9"
        },
        "tertiary": {
            "background": "transparent",
            "text": "#2D7FF9",
            "hover_background": "rgba(45, 127, 249, 0.1)",
            "active_background": "rgba(45, 127, 249, 0.2)",
            "border": "none"
        },
        "danger": {
            "background": "#E53935",
            "text": "#FFFFFF",
            "hover_background": "#D32F2F",
            "active_background": "#C62828",
            "border": "none"
        }
    }
    
    def __init__(self, text="", parent=None, variant="primary", size="medium", icon=None):
        super().__init__(text, parent)
        self.variant = variant
        self.size = size
        self.icon_path = icon
        
        self._apply_styles()
        
    def _apply_styles(self):
        """Apply styles based on variant and size"""
        variant_styles = self.VARIANTS.get(self.variant, self.VARIANTS["primary"])
        
        # Set base style
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {variant_styles["background"]};
                color: {variant_styles["text"]};
                border: {variant_styles["border"]};
                border-radius: 4px;
                font-weight: 500;
                padding: 8px 16px;
                outline: none;
            }}
            
            QPushButton:hover {{
                background-color: {variant_styles["hover_background"]};
            }}
            
            QPushButton:pressed {{
                background-color: {variant_styles["active_background"]};
            }}
            
            QPushButton:disabled {{
                background-color: #E0E0E0;
                color: #757575;
                border: none;
            }}
        """)
        
        # Set size
        if self.size == "small":
            self.setFixedHeight(32)
            font = self.font()
            font.setPointSize(12)
            self.setFont(font)
        elif self.size == "medium":
            self.setFixedHeight(40)
            font = self.font()
            font.setPointSize(14)
            self.setFont(font)
        elif self.size == "large":
            self.setFixedHeight(48)
            font = self.font()
            font.setPointSize(16)
            self.setFont(font)
            
        # Set icon if provided
        if self.icon_path:
            self.setIcon(QIcon(self.icon_path))
            self.setIconSize(QSize(18, 18))
```

### 4.2 Cards

Cards should:
- Have 8px rounded corners
- Include subtle shadows (0px 2px 4px rgba(0,0,0,0.1))
- Maintain consistent padding (16px or 24px)
- Use white background in light mode and dark surface color in dark mode

```python
class ThemeCard(QFrame):
    """Styled card component following design system"""
    
    def __init__(self, parent=None, padding=16, elevation=1):
        super().__init__(parent)
        self.padding = padding
        self.elevation = elevation
        
        self._setup_layout()
        self._apply_styles()
        
    def _setup_layout(self):
        """Set up the layout for the card"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(self.padding, self.padding, self.padding, self.padding)
        self.main_layout.setSpacing(8)
        self.setLayout(self.main_layout)
        
    def _apply_styles(self):
        """Apply card styles"""
        # Shadow effects based on elevation
        shadow_styles = {
            0: "none",
            1: "0px 2px 4px rgba(0, 0, 0, 0.1)",
            2: "0px 4px 8px rgba(0, 0, 0, 0.12)",
            3: "0px 8px 16px rgba(0, 0, 0, 0.14)"
        }
        
        shadow = shadow_styles.get(self.elevation, shadow_styles[1])
        
        self.setStyleSheet(f"""
            ThemeCard {{
                background-color: #FFFFFF;
                border-radius: 8px;
                box-shadow: {shadow};
                border: 1px solid #E0E0E0;
            }}
        """)
    
    def add_widget(self, widget):
        """Add a widget to the card"""
        self.main_layout.addWidget(widget)
        
    def add_layout(self, layout):
        """Add a layout to the card"""
        self.main_layout.addLayout(layout)
```

### 4.3 Input Fields

Input fields should:
- Have a clear focused state with the primary color
- Include descriptive labels above the field
- Show validation states visually
- Have consistent height (40px)

```python
class ThemeInputField(QWidget):
    """Styled input field following design system"""
    
    textChanged = Signal(str)
    
    def __init__(self, label="", placeholder="", parent=None, password_mode=False, helper_text=None):
        super().__init__(parent)
        self.label_text = label
        self.placeholder_text = placeholder
        self.password_mode = password_mode
        self.helper_text = helper_text
        self.error_text = None
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the input field UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Label
        if self.label_text:
            self.label = QLabel(self.label_text)
            font = self.label.font()
            font.setPointSize(12)
            font.setWeight(500)
            self.label.setFont(font)
            layout.addWidget(self.label)
            
        # Input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(self.placeholder_text)
        self.input_field.setFixedHeight(40)
        if self.password_mode:
            self.input_field.setEchoMode(QLineEdit.Password)
            
        # Apply styling
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px 12px;
                background-color: #FFFFFF;
                color: #333333;
            }
            
            QLineEdit:focus {
                border: 2px solid #2D7FF9;
            }
            
            QLineEdit:disabled {
                background-color: #F5F7FA;
                color: #757575;
            }
        """)
        
        layout.addWidget(self.input_field)
        
        # Helper text
        if self.helper_text:
            self.helper_label = QLabel(self.helper_text)
            font = self.helper_label.font()
            font.setPointSize(11)
            self.helper_label.setFont(font)
            self.helper_label.setStyleSheet("color: #757575;")
            layout.addWidget(self.helper_label)
        
        # Error text (hidden by default)
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #E53935;")
        font = self.error_label.font()
        font.setPointSize(11)
        self.error_label.setFont(font)
        self.error_label.hide()
        layout.addWidget(self.error_label)
        
        # Connect signals
        self.input_field.textChanged.connect(self._on_text_changed)
        
    def _on_text_changed(self, text):
        """Handle text changes"""
        self.textChanged.emit(text)
        # Clear error when user starts typing
        if self.error_text:
            self.clear_error()
            
    def set_error(self, error_text):
        """Set error state"""
        self.error_text = error_text
        self.error_label.setText(error_text)
        self.error_label.show()
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E53935;
                border-radius: 4px;
                padding: 8px 12px;
                background-color: #FFFFFF;
                color: #333333;
            }
            
            QLineEdit:focus {
                border: 2px solid #E53935;
            }
        """)
        
    def clear_error(self):
        """Clear error state"""
        self.error_text = None
        self.error_label.hide()
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px 12px;
                background-color: #FFFFFF;
                color: #333333;
            }
            
            QLineEdit:focus {
                border: 2px solid #2D7FF9;
            }
            
            QLineEdit:disabled {
                background-color: #F5F7FA;
                color: #757575;
            }
        """)
        
    def get_text(self):
        """Get current text"""
        return self.input_field.text()
        
    def set_text(self, text):
        """Set text programmatically"""
        self.input_field.setText(text)
```

### 4.4 Dialogs

Dialogs should:
- Be centered on screen
- Include a clear title and close button
- Have consistent action button placement (right-aligned)
- Use a semi-transparent overlay to focus attention

```python
class ThemeDialog(QDialog):
    """Styled dialog following design system"""
    
    def __init__(self, parent=None, title="", width=400, height=None):
        super().__init__(parent)
        self.dialog_title = title
        self.dialog_width = width
        self.dialog_height = height
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the dialog UI"""
        # Set fixed width and optional height
        self.setFixedWidth(self.dialog_width)
        if self.dialog_height:
            self.setFixedHeight(self.dialog_height)
            
        # Remove window frame
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create a frame to hold the dialog content
        self.frame = QFrame()
        self.frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 8px;
                border: 1px solid #E0E0E0;
            }
        """)
        
        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 4)
        self.frame.setGraphicsEffect(shadow)
        
        # Frame layout
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(24, 20, 24, 24)
        
        # Title bar
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 16)
        
        title_label = QLabel(self.dialog_title)
        font = title_label.font()
        font.setPointSize(18)
        font.setWeight(QFont.Bold)
        title_label.setFont(font)
        
        close_button = QPushButton()
        close_button.setIcon(QIcon("icons/close.svg"))
        close_button.setFixedSize(24, 24)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 12px;
            }
            
            QPushButton:hover {
                background-color: #F5F7FA;
            }
            
            QPushButton:pressed {
                background-color: #E0E0E0;
            }
        """)
        close_button.clicked.connect(self.reject)
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(close_button)
        frame_layout.addLayout(title_layout)
        
        # Content area
        self.content_area = QVBoxLayout()
        self.content_area.setContentsMargins(0, 0, 0, 24)
        frame_layout.addLayout(self.content_area)
        
        # Button area
        self.button_area = QHBoxLayout()
        self.button_area.setContentsMargins(0, 0, 0, 0)
        self.button_area.setAlignment(Qt.AlignRight)
        frame_layout.addLayout(self.button_area)
        
        main_layout.addWidget(self.frame)
        
    def add_content(self, widget):
        """Add a widget to the content area"""
        self.content_area.addWidget(widget)
        
    def add_button(self, button, primary=False):
        """Add a button to the button area"""
        self.button_area.addWidget(button)
        
    def set_overlay_opacity(self, opacity=0.5):
        """Set the background overlay opacity"""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: rgba(0, 0, 0, {opacity});
            }}
        """)
        
    def showEvent(self, event):
        """Center the dialog when shown"""
        if self.parent():
            parent_rect = self.parent().geometry()
            self.move(
                parent_rect.center().x() - self.width() // 2,
                parent_rect.center().y() - self.height() // 2
            )
        super().showEvent(event)
```

### 4.5 Lists and Tables

Lists should:
- Have consistent item heights
- Include hover states for interactive items
- Clearly indicate selected state
- Support hierarchical data with indentation

Tables should:
- Use alternating row colors for better readability
- Have sticky headers when scrolling
- Include proper cell padding (12px)
- Allow for row selection with visual feedback

### 4.6 Navigation Components

Navigation elements should:
- Clearly indicate the current location
- Use consistent iconography
- Provide hover and active states
- Be accessible via keyboard navigation

## 5. Iconography

### 5.1 Icon System

VPA uses a custom icon set with the following characteristics:
- 24x24px base size
- 2px stroke width
- Rounded corners and stroke caps
- Optimized for clarity at small sizes

### 5.2 Icon Usage Guidelines

- Maintain consistent sizes within similar UI components
- Use icons sparingly and with purpose
- Always include text labels for important actions
- Ensure icons have adequate touch targets (minimum 44x44px)

### 5.3 Common Icon Set

```python
class IconProvider:
    """Provides access to the application icon set"""
    
    ICON_PATH = "assets/icons"
    
    # Dictionary mapping icon names to filenames
    ICONS = {
        # Navigation
        "home": "home.svg",
        "settings": "settings.svg",
        "chat": "chat.svg",
        "user": "user.svg",
        "search": "search.svg",
        "menu": "menu.svg",
        
        # Actions
        "add": "add.svg",
        "delete": "delete.svg",
        "edit": "edit.svg",
        "save": "save.svg",
        "export": "export.svg",
        "import": "import.svg",
        "download": "download.svg",
        "upload": "upload.svg",
        
        # Media
        "play": "play.svg",
        "pause": "pause.svg",
        "stop": "stop.svg",
        "record": "record.svg",
        "mic": "mic.svg",
        "mic_off": "mic_off.svg",
        
        # UI Elements
        "check": "check.svg",
        "close": "close.svg",
        "alert": "alert.svg",
        "info": "info.svg",
        "error": "error.svg",
        "warning": "warning.svg",
        "help": "help.svg",
        "arrow_right": "arrow_right.svg",
        "arrow_left": "arrow_left.svg",
        "arrow_up": "arrow_up.svg",
        "arrow_down": "arrow_down.svg",
    }
    
    @classmethod
    def get_icon(cls, name, color=None, size=None):
        """Get an icon by name"""
        if name not in cls.ICONS:
            logger.warning(f"Icon '{name}' not found")
            return QIcon()
            
        icon_path = os.path.join(cls.ICON_PATH, cls.ICONS[name])
        
        # If color or size is specified, we need to modify the SVG
        if color or size:
            return cls._create_colored_icon(icon_path, color, size)
        
        return QIcon(icon_path)
        
    @classmethod
    def _create_colored_icon(cls, icon_path, color=None, size=None):
        """Create a colored version of an SVG icon"""
        if not os.path.exists(icon_path):
            return QIcon()
            
        # Read SVG file
        with open(icon_path, 'r') as f:
            svg_content = f.read()
            
        # Modify SVG
        if color:
            # Replace stroke and fill colors
            svg_content = re.sub(r'stroke="[^"]+"', f'stroke="{color}"', svg_content)
            svg_content = re.sub(r'fill="[^"]+"', f'fill="{color}"', svg_content)
            
        if size:
            # Update width and height
            svg_content = re.sub(r'width="[^"]+"', f'width="{size}"', svg_content)
            svg_content = re.sub(r'height="[^"]+"', f'height="{size}"', svg_content)
            
        # Create QIcon from modified SVG
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(svg_content.encode()))
        return QIcon(pixmap)
```

## 6. Layout Principles

### 6.1 Grid System

VPA uses an 8-point grid system:
- Base unit of 8 pixels
- Components should align to the grid
- Spacing follows multiples of 8px (8, 16, 24, 32, 40, 48, etc.)
- Smaller elements can use 4px increments for fine details

### 6.2 Spacing Guidelines

- **Tight spacing (8px)**: For related elements within a component
- **Standard spacing (16px)**: Between components within a section
- **Loose spacing (24px)**: Between distinct sections
- **Extra loose spacing (32px+)**: For major layout divisions

```python
class ThemeSpacing:
    """Spacing constants following the 8-point grid system"""
    
    # Base unit (in pixels)
    UNIT = 8
    
    # Spacing values
    XXXS = UNIT // 2  # 4px
    XXS = UNIT  # 8px
    XS = UNIT * 1.5  # 12px
    S = UNIT * 2  # 16px
    M = UNIT * 3  # 24px
    L = UNIT * 4  # 32px
    XL = UNIT * 5  # 40px
    XXL = UNIT * 6  # 48px
    XXXL = UNIT * 8  # 64px
    
    @classmethod
    def scale_for_density(cls, density_factor=1.0):
        """Scale spacing for different screen densities"""
        cls.UNIT = int(8 * density_factor)
        # Update all derived values
        cls.XXXS = cls.UNIT // 2
        cls.XXS = cls.UNIT
        cls.XS = int(cls.UNIT * 1.5)
        cls.S = cls.UNIT * 2
        cls.M = cls.UNIT * 3
        cls.L = cls.UNIT * 4
        cls.XL = cls.UNIT * 5
        cls.XXL = cls.UNIT * 6
        cls.XXXL = cls.UNIT * 8
```

### 6.3 Responsive Design

VPA uses a responsive layout system to adapt to different screen sizes:
- Small: Up to 640px width
- Medium: 641px to 1024px width
- Large: 1025px to 1440px width
- Extra Large: Above 1440px width

Layout components should:
- Stack vertically on smaller screens
- Use appropriate margins based on screen size
- Adjust content density for different devices

### 6.4 Component Alignment

- Form labels and inputs should left-align
- Buttons in dialogs should right-align
- Section headings should align with their content
- Related actions should be grouped together

## 7. Animation and Transitions

### 7.1 Principles

All animations should:
- Have purpose and enhance usability
- Be subtle and not distracting
- Use consistent timing and easing
- Be performant and not cause stuttering

### 7.2 Duration and Easing

```
Instant: 100ms
Fast: 200ms
Standard: 300ms
Entrance: 400ms
Exit: 250ms

Standard Easing: Ease-out cubic
Entrance Easing: Ease-out quint
Exit Easing: Ease-in quad
```

### 7.3 Common Animations

```python
class ThemeAnimations:
    """Animation utilities following the design system"""
    
    # Duration constants (in milliseconds)
    DURATION_INSTANT = 100
    DURATION_FAST = 200
    DURATION_STANDARD = 300
    DURATION_ENTRANCE = 400
    DURATION_EXIT = 250
    
    # Easing curves
    EASING_STANDARD = QEasingCurve.OutCubic
    EASING_ENTRANCE = QEasingCurve.OutQuint
    EASING_EXIT = QEasingCurve.InQuad
    
    @staticmethod
    def fade_in(widget, duration=None, finished_callback=None):
        """Fade in a widget"""
        if duration is None:
            duration = ThemeAnimations.DURATION_ENTRANCE
            
        opacity_effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(opacity_effect)
        
        # Create animation
        animation = QPropertyAnimation(opacity_effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.setEasingCurve(ThemeAnimations.EASING_ENTRANCE)
        
        if finished_callback:
            animation.finished.connect(finished_callback)
            
        animation.start(QAbstractAnimation.DeleteWhenStopped)
        return animation
        
    @staticmethod
    def fade_out(widget, duration=None, finished_callback=None):
        """Fade out a widget"""
        if duration is None:
            duration = ThemeAnimations.DURATION_EXIT
            
        opacity_effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(opacity_effect)
        
        # Create animation
        animation = QPropertyAnimation(opacity_effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(1)
        animation.setEndValue(0)
        animation.setEasingCurve(ThemeAnimations.EASING_EXIT)
        
        if finished_callback:
            animation.finished.connect(finished_callback)
            
        animation.start(QAbstractAnimation.DeleteWhenStopped)
        return animation
        
    @staticmethod
    def slide_in_right(widget, duration=None, distance=50, finished_callback=None):
        """Slide in a widget from the right"""
        if duration is None:
            duration = ThemeAnimations.DURATION_ENTRANCE
            
        # Store original position
        original_pos = widget.pos()
        start_pos = QPoint(original_pos.x() + distance, original_pos.y())
        widget.move(start_pos)
        
        # Create animation
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(original_pos)
        animation.setEasingCurve(ThemeAnimations.EASING_ENTRANCE)
        
        if finished_callback:
            animation.finished.connect(finished_callback)
            
        animation.start(QAbstractAnimation.DeleteWhenStopped)
        return animation
```

## 8. Accessibility Guidelines

### 8.1 Color Contrast

- Text must maintain a minimum contrast ratio of 4.5:1
- UI controls must maintain a minimum contrast ratio of 3:1
- Focus indicators must have sufficient contrast with the background

### 8.2 Focus Management

- All interactive elements must be focusable
- Focus order should follow a logical sequence
- Focus state must be visually apparent
- Keyboard shortcuts should be provided for common actions

### 8.3 Text Scaling

- The UI must support text scaling up to 200%
- No content should be cut off when text is enlarged
- Line height should increase proportionally with text size

### 8.4 Screen Reader Support

- All UI elements must have appropriate accessibility labels
- Dynamic content updates should be announced to screen readers
- Form controls must have associated labels

```python
class AccessibilityHelper:
    """Utilities for improving application accessibility"""
    
    @staticmethod
    def set_accessible_name(widget, name):
        """Set accessible name for a widget"""
        widget.setAccessibleName(name)
        
    @staticmethod
    def set_accessible_description(widget, description):
        """Set accessible description for a widget"""
        widget.setAccessibleDescription(description)
        
    @staticmethod
    def announce(message, priority=Qt.AccessibleAlertMessage):
        """Announce a message to screen readers"""
        QAccessible.updateAccessibility(
            QAccessibleEvent(
                QApplication.focusWidget(),
                QAccessible.Focus
            )
        )
        # Use the active widget to announce
        active = QApplication.activeWindow()
        if active:
            # This requires proper screen reader support in the OS
            active.setStatusTip(message)
            active.setStatusTip("")
            
    @staticmethod
    def enhance_button(button, shortcut=None, tooltip=None):
        """Enhance a button with accessibility features"""
        if shortcut:
            button.setShortcut(shortcut)
            
        if tooltip:
            button.setToolTip(tooltip)
            if shortcut:
                button.setToolTip(f"{tooltip} ({shortcut.toString()})")
                
        # Make sure button is focusable
        button.setFocusPolicy(Qt.StrongFocus)
```

## 9. Theme Implementation

### 9.1 Theme Manager

The ThemeManager class manages application-wide theming:

```python
class ThemeManager:
    """Manages application themes and styling"""
    
    # Available themes
    THEMES = {
        "light": {
            "name": "Light",
            "colors": {
                "primary": "#2D7FF9",
                "primary_dark": "#1A63D0",
                "primary_light": "#6BA5FA",
                "accent": "#7E57C2",
                "background": "#F5F7FA",
                "surface": "#FFFFFF",
                "text": "#333333",
                "text_secondary": "#757575",
                "border": "#E0E0E0",
                "success": "#43A047",
                "warning": "#FB8C00",
                "error": "#E53935",
                "info": "#2196F3"
            }
        },
        "dark": {
            "name": "Dark",
            "colors": {
                "primary": "#4285F4",
                "primary_dark": "#3367D6",
                "primary_light": "#80B1FF",
                "accent": "#B388FF",
                "background": "#121212",
                "surface": "#1E1E1E",
                "text": "#E0E0E0",
                "text_secondary": "#A0A0A0",
                "border": "#333333",
                "success": "#81C784",
                "warning": "#FFB74D",
                "error": "#E57373",
                "info": "#64B5F6"
            }
        }
    }
    
    def __init__(self, settings_manager, event_bus):
        self.settings_manager = settings_manager
        self.event_bus = event_bus
        self.current_theme = None
        
        # Load theme from settings
        self._load_theme()
        
    def _load_theme(self):
        """Load theme from settings"""
        theme_name = self.settings_manager.get("ui.theme", "light")
        self.set_theme(theme_name)
        
    def set_theme(self, theme_name):
        """Set the application theme"""
        if theme_name not in self.THEMES:
            logger.warning(f"Theme '{theme_name}' not found. Using light theme.")
            theme_name = "light"
            
        self.current_theme = self.THEMES[theme_name]
        
        # Save to settings
        self.settings_manager.set("ui.theme", theme_name)
        
        # Apply theme
        self._apply_theme()
        
        # Notify about theme change
        self.event_bus.emit("theme.changed", {"theme": theme_name})
        
    def _apply_theme(self):
        """Apply the current theme to the application"""
        if not self.current_theme:
            return
            
        colors = self.current_theme["colors"]
        
        # Build stylesheet
        stylesheet = f"""
            QWidget {{
                color: {colors["text"]};
                background-color: {colors["background"]};
            }}
            
            QMainWindow, QDialog {{
                background-color: {colors["background"]};
            }}
            
            QPushButton {{
                background-color: {colors["primary"]};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 500;
            }}
            
            QPushButton:hover {{
                background-color: {colors["primary_dark"]};
            }}
            
            QPushButton:disabled {{
                background-color: {colors["border"]};
                color: {colors["text_secondary"]};
            }}
            
            QLineEdit, QTextEdit, QPlainTextEdit {{
                border: 1px solid {colors["border"]};
                border-radius: 4px;
                padding: 8px;
                background-color: {colors["surface"]};
                color: {colors["text"]};
            }}
            
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border: 2px solid {colors["primary"]};
            }}
            
            QLabel {{
                color: {colors["text"]};
                background-color: transparent;
            }}
            
            QCheckBox {{
                spacing: 8px;
                color: {colors["text"]};
                background-color: transparent;
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid {colors["border"]};
                border-radius: 4px;
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {colors["primary"]};
                border-color: {colors["primary"]};
            }}
            
            QScrollBar:vertical {{
                border: none;
                background: {colors["background"]};
                width: 8px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {colors["border"]};
                min-height: 20px;
                border-radius: 4px;
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
            
            QMenu {{
                background-color: {colors["surface"]};
                border: 1px solid {colors["border"]};
                border-radius: 4px;
            }}
            
            QMenu::item {{
                padding: 6px 32px 6px 16px;
                color: {colors["text"]};
            }}
            
            QMenu::item:selected {{
                background-color: {colors["primary_light"]};
            }}
            
            QTabWidget::pane {{
                border: 1px solid {colors["border"]};
                border-top: none;
                background-color: {colors["surface"]};
            }}
            
            QTabBar::tab {{
                background-color: {colors["background"]};
                color: {colors["text_secondary"]};
                padding: 8px 16px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                border: 1px solid {colors["border"]};
                border-bottom: none;
                margin-right: 2px;
            }}
            
            QTabBar::tab:selected {{
                color: {colors["primary"]};
                background-color: {colors["surface"]};
                border-bottom: 2px solid {colors["primary"]};
            }}
        """
        
        # Apply stylesheet
        QApplication.instance().setStyleSheet(stylesheet)
        
    def get_color(self, name):
        """Get a color from the current theme"""
        if not self.current_theme:
            return None
            
        return self.current_theme["colors"].get(name)
        
    def get_current_theme_name(self):
        """Get the name of the current theme"""
        for name, theme in self.THEMES.items():
            if theme == self.current_theme:
                return name
        return "light"  # Default
```

### 9.2 Dark Mode Support

VPA fully supports dark mode through:
- Automatic detection of system theme preference
- Manual theme selection in settings
- Appropriate color palette for dark environments
- SVG icons that adapt to dark mode

### 9.3 Custom UI Controls

All custom UI controls should:
- Support both light and dark themes
- Use appropriate colors from the theme
- Maintain consistent sizing and spacing
- Handle focus and hover states consistently

## 10. Future Considerations

### 10.1 Design Language Evolution

The VPA design language will evolve over time:
- Annual reviews of the design system
- Incorporation of user feedback
- Refinement based on usability studies
- Adaptation to new platform capabilities

### 10.2 Multiple Theme Support

Future versions may add:
- Additional built-in themes
- Custom theme creation
- Theme sharing between users
- Time-based theme switching

### 10.3 Component Library Expansion

The component library will be expanded with:
- Advanced data visualization components
- Specialized AI interaction elements
- Custom input methods
- Enhanced accessibility components

### 10.4 Localization Design

Visual design must account for:
- Text expansion in different languages
- Right-to-left (RTL) layout support
- Cultural design preferences
- Variable font requirements

---

*Document created on August 28, 2025*  
*Version: 1.0*
