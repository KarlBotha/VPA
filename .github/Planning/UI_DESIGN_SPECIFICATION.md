# UI Design Specification

## Overview

This document defines the UI architecture, components, and design principles for the VPA application. It provides detailed specifications for all user interfaces, ensuring consistent design, accessibility compliance, and optimal user experience.

## Table of Contents

1. [UI Design Principles](#1-ui-design-principles)
2. [UI Architecture](#2-ui-architecture)
3. [Core UI Components](#3-core-ui-components)
4. [UI States and Transitions](#4-ui-states-and-transitions)
5. [Theme Implementation](#5-theme-implementation)
6. [Accessibility Compliance](#6-accessibility-compliance)
7. [UI Performance](#7-ui-performance)
8. [Implementation Guidelines](#8-implementation-guidelines)

## 1. UI Design Principles

### 1.1 Visual Principles

- **Clarity**: Clear visual hierarchy and information presentation
- **Consistency**: Uniform styling, spacing, and interaction patterns
- **Minimalism**: Focus on essential elements, reduce visual clutter
- **Feedback**: Clear visual feedback for all user actions
- **Purposeful Animation**: Subtle animations that guide attention and convey state

### 1.2 Interaction Principles

- **Efficiency**: Minimize clicks/steps for common actions
- **Forgiving**: Easy error recovery and clear confirmation for destructive actions
- **Discoverable**: Features are findable without overwhelming complexity
- **Responsive**: Immediate feedback for user actions (<100ms target)
- **Contextual**: Present options relevant to current context

### 1.3 Design System Components

- **Color Palette**: Primary, secondary, accent colors with light/dark variants
- **Typography**: Clear typographic hierarchy with consistent font usage
- **Spacing**: Consistent 8px grid system for component spacing
- **Elevation**: Consistent shadow system to convey elevation
- **Components**: Reusable UI components with consistent behavior

## 2. UI Architecture

### 2.1 UI Layer Architecture

The VPA UI follows a layered architecture pattern:

```
┌─────────────────────────────────────┐
│             View Layer              │
│  (UI Components, Windows, Controls) │
└───────────────────┬─────────────────┘
                    │
┌───────────────────▼─────────────────┐
│        Presentation Layer           │
│  (View Models, State Management)    │
└───────────────────┬─────────────────┘
                    │
┌───────────────────▼─────────────────┐
│         Application Layer           │
│   (Business Logic, Event Bus)       │
└─────────────────────────────────────┘
```

### 2.2 UI Manager Implementation

```python
class UIManager:
    """Central manager for all UI components"""
    
    def __init__(self, event_bus, settings_manager):
        self.event_bus = event_bus
        self.settings_manager = settings_manager
        self.windows = {}
        self.dialogs = {}
        self.active_theme = None
        self.tray_icon = None
        
        # Subscribe to application events
        self.event_bus.subscribe("app.startup_complete", self.initialize_ui, async_callback=False)
        self.event_bus.subscribe("app.shutdown_requested", self.prepare_shutdown, async_callback=False)
        self.event_bus.subscribe("settings.changed.ui.theme", self.update_theme, async_callback=False)
        
    def initialize_ui(self, event_data=None):
        """Initialize the UI after application startup"""
        # Load theme settings
        self.active_theme = self.settings_manager.get("ui.theme", "system")
        
        # Create main window
        self.windows["main"] = MainWindow(self, self.event_bus, self.settings_manager)
        
        # Setup system tray
        self._setup_system_tray()
        
        # Apply theme
        self.apply_theme(self.active_theme)
        
        # Show window based on startup settings
        startup_behavior = self.settings_manager.get("app.startup_behavior", "fullscreen")
        if startup_behavior == "normal":
            self.windows["main"].show()
        elif startup_behavior == "minimized":
            self.windows["main"].showMinimized()
        elif startup_behavior == "fullscreen":
            self.windows["main"].showMaximized()
        elif startup_behavior == "hidden":
            # Hidden - don't show main window
            pass
        
    def _setup_system_tray(self):
        """Setup the system tray icon and menu"""
        if not self.settings_manager.get("ui.tray_icon_enabled", True):
            return
            
        # Implementation details...
        
    def update_theme(self, event_data):
        """Handle theme change event"""
        new_theme = event_data.get("new_value", "system")
        self.apply_theme(new_theme)
        
    def apply_theme(self, theme_name):
        """Apply the selected theme to all UI components"""
        self.active_theme = theme_name
        
        # Determine actual theme (resolve 'system')
        actual_theme = theme_name
        if theme_name == "system":
            # Detect system theme
            actual_theme = self._detect_system_theme()
        
        # Load theme stylesheet
        stylesheet = self._load_theme_stylesheet(actual_theme)
        
        # Apply to all windows
        for window in self.windows.values():
            window.setStyleSheet(stylesheet)
            
        # Update theme-specific icons
        self._update_theme_icons(actual_theme)
        
    def _detect_system_theme(self):
        """Detect the system theme (light/dark)"""
        # Implementation details...
        return "light"  # Default fallback
        
    def _load_theme_stylesheet(self, theme_name):
        """Load the theme stylesheet"""
        # Implementation details...
        return ""  # Default empty stylesheet
        
    def create_dialog(self, dialog_type, *args, **kwargs):
        """Create and show a dialog of the specified type"""
        # Implementation details...
        
    def prepare_shutdown(self, event_data=None):
        """Prepare UI for application shutdown"""
        # Save window states
        for name, window in self.windows.items():
            if hasattr(window, "save_state"):
                window.save_state()
                
        # Hide windows
        for window in self.windows.values():
            window.hide()
            
        # Remove tray icon
        if self.tray_icon:
            self.tray_icon.hide()
```

### 2.3 View Model Pattern

UI components will follow the MVVM (Model-View-ViewModel) pattern:

```python
class ChatViewModel:
    """ViewModel for the chat interface"""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.messages = []
        self.is_processing = False
        self.has_unread = False
        self.property_changed_handlers = {}
        
        # Subscribe to events
        self.event_bus.subscribe("llm.request", self._on_llm_request, async_callback=False)
        self.event_bus.subscribe("llm.response", self._on_llm_response, async_callback=False)
        self.event_bus.subscribe("llm.response.stream", self._on_llm_stream, async_callback=False)
        
    def add_property_changed_handler(self, property_name, handler):
        """Add handler for property change notification"""
        if property_name not in self.property_changed_handlers:
            self.property_changed_handlers[property_name] = []
        self.property_changed_handlers[property_name].append(handler)
        
    def _notify_property_changed(self, property_name):
        """Notify handlers that property has changed"""
        if property_name in self.property_changed_handlers:
            for handler in self.property_changed_handlers[property_name]:
                handler()
        
    def _on_llm_request(self, event_data):
        """Handle LLM request event"""
        self.is_processing = True
        self._notify_property_changed("is_processing")
        
        # Add user message to chat
        message = {
            "role": "user",
            "content": event_data.get("messages", [{}])[-1].get("content", ""),
            "timestamp": datetime.now().isoformat()
        }
        self.messages.append(message)
        self._notify_property_changed("messages")
        
    def _on_llm_response(self, event_data):
        """Handle LLM response event"""
        self.is_processing = False
        self._notify_property_changed("is_processing")
        
        # Check if this is a streaming response completion
        request_id = event_data.get("request_id")
        for i, msg in enumerate(self.messages):
            if msg.get("role") == "assistant" and msg.get("request_id") == request_id:
                # Update existing message
                self.messages[i]["content"] = event_data.get("response", "")
                self.messages[i]["completed"] = True
                self._notify_property_changed("messages")
                return
        
        # Add new assistant message
        message = {
            "role": "assistant",
            "content": event_data.get("response", ""),
            "request_id": event_data.get("request_id"),
            "timestamp": datetime.now().isoformat(),
            "completed": True
        }
        self.messages.append(message)
        self._notify_property_changed("messages")
        
        # Set unread flag if window not focused
        if not self._is_window_focused():
            self.has_unread = True
            self._notify_property_changed("has_unread")
        
    def _on_llm_stream(self, event_data):
        """Handle streaming response chunks"""
        # Check if message for this request already exists
        request_id = event_data.get("request_id")
        text_so_far = event_data.get("text_so_far", "")
        
        for i, msg in enumerate(self.messages):
            if msg.get("role") == "assistant" and msg.get("request_id") == request_id:
                # Update existing message
                self.messages[i]["content"] = text_so_far
                self._notify_property_changed("messages")
                return
        
        # Add new message for this stream
        message = {
            "role": "assistant",
            "content": text_so_far,
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "completed": False
        }
        self.messages.append(message)
        self._notify_property_changed("messages")
```

## 3. Core UI Components

### 3.1 Main Window

The main window serves as the primary interface for user interaction, following a modern AI chatbot interface design similar to ChatGPT and GitHub Copilot:

#### 3.1.1 Layout

```
┌─────────────────────────────────────────────────────┐
│  ┌─────────┐  │                                     │
│  │ New Chat│  │             Header                  │
│  ├─────────┤  │                                     │
│  │         │  ├─────────────────────────────────────┤
│  │         │  │                                     │
│  │         │  │                                     │
│  │ Chat    │  │                                     │
│  │ History │  │           Chat Display              │
│  │ List    │  │           (Chat Bubbles)            │
│  │         │  │                                     │
│  │         │  │                                     │
│  │         │  │                                     │
│  │         │  │                                     │
│  │         │  │                                     │
│  ├─────────┤  ├─────────────────────────────────────┤
│  │Settings │  │ [📎] Input Field       [🎤] [➤Send] │
│  └─────────┘  └─────────────────────────────────────┘
└─────────────────────────────────────────────────────┘
```

#### 3.1.2 Components

- **Header**: Title, menu, minimize/maximize/close buttons, workflow selector
- **New Chat Button**: Start a new chat session
- **Chat History List**: List of previous chat sessions with rename capability
- **Chat Display**: Scrollable message history with chat bubbles and avatars
- **Input Field**: Multi-line text input for user messages
- **Attachment Button**: Attach files or documents
- **Voice Button**: Toggle for voice input mode
- **Send Button**: Submit user input
- **Settings Button**: Open settings panel

#### 3.1.3 Implementation

```python
class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, ui_manager, event_bus, settings_manager):
        super().__init__()
        self.ui_manager = ui_manager
        self.event_bus = event_bus
        self.settings_manager = settings_manager
        
        # View models
        self.chat_view_model = ChatViewModel(event_bus)
        self.chat_history_view_model = ChatHistoryViewModel(event_bus)
        
        # Current chat session
        self.current_chat_id = None
        
        # Setup UI
        self._setup_ui()
        
        # Restore window state
        self._restore_window_state()
        
        # Load last active chat
        self._load_last_active_chat()
        
    def _setup_ui(self):
        """Setup the UI components"""
        # Window properties
        self.setWindowTitle("VPA Assistant")
        self.setMinimumSize(900, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout (horizontal split)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left sidebar (chat list)
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Right content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        main_layout.addWidget(content_widget, 1)  # 1 = stretch factor
        
        # Header
        header = self._create_header()
        content_layout.addWidget(header)
        
        # Chat display
        self.chat_display = ChatDisplay(self.chat_view_model)
        content_layout.addWidget(self.chat_display, 1)  # 1 = stretch factor
        
        # Input area
        input_area = self._create_input_area()
        content_layout.addWidget(input_area)
        
        # Setup menu
        self._setup_menu()
        
        # Connect view model signals
        self.chat_view_model.add_property_changed_handler(
            "messages", self._on_messages_changed
        )
        self.chat_view_model.add_property_changed_handler(
            "is_processing", self._on_processing_changed
        )
        
    def _create_sidebar(self):
        """Create the sidebar with chat history"""
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(10)
        
        # New chat button
        new_chat_btn = QPushButton("New Chat")
        new_chat_btn.setIcon(QIcon.fromTheme("document-new"))
        new_chat_btn.clicked.connect(self._on_new_chat_clicked)
        sidebar_layout.addWidget(new_chat_btn)
        
        # Chat list
        self.chat_list_widget = QListWidget()
        self.chat_list_widget.setIconSize(QSize(32, 32))
        self.chat_list_widget.itemClicked.connect(self._on_chat_selected)
        self.chat_list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.chat_list_widget.customContextMenuRequested.connect(self._show_chat_context_menu)
        sidebar_layout.addWidget(self.chat_list_widget, 1)  # 1 = stretch factor
        
        # Settings button
        settings_btn = QPushButton("Settings")
        settings_btn.setIcon(QIcon.fromTheme("preferences-system"))
        settings_btn.clicked.connect(self._on_settings_clicked)
        sidebar_layout.addWidget(settings_btn)
        
        # Update chat list
        self._update_chat_history_list()
        
        return sidebar_widget
        
    def _create_header(self):
        """Create the header component"""
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        # Chat title (editable)
        self.chat_title_edit = QLineEdit()
        self.chat_title_edit.setPlaceholderText("Chat Title")
        self.chat_title_edit.editingFinished.connect(self._on_chat_title_changed)
        header_layout.addWidget(self.chat_title_edit, 1)  # 1 = stretch factor
        
        # Model selector
        model_selector = QComboBox()
        self._populate_model_selector(model_selector)
        model_selector.currentIndexChanged.connect(self._on_model_changed)
        header_layout.addWidget(model_selector)
        
        return header_widget
        
    def _create_input_area(self):
        """Create the input area component"""
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(15, 10, 15, 10)
        
        # Attachment button
        attach_button = QPushButton()
        attach_button.setIcon(QIcon.fromTheme("mail-attachment"))
        attach_button.setToolTip("Attach Files")
        attach_button.clicked.connect(self._on_attach_clicked)
        input_layout.addWidget(attach_button)
        
        # Text input field
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Type a message...")
        self.input_field.setAcceptRichText(False)
        self.input_field.setMaximumHeight(100)  # Limit height
        self.input_field.textChanged.connect(self._on_input_text_changed)
        
        # Setup key events for input field
        self.input_field.installEventFilter(self)
        
        input_layout.addWidget(self.input_field, 1)  # 1 = stretch factor
        
        # Voice input button
        voice_button = QPushButton()
        voice_button.setIcon(QIcon.fromTheme("audio-input-microphone"))
        voice_button.setToolTip("Voice Input")
        voice_button.clicked.connect(self._on_voice_input_clicked)
        input_layout.addWidget(voice_button)
        
        # Send button
        self.send_button = QPushButton()
        self.send_button.setIcon(QIcon.fromTheme("mail-send"))
        self.send_button.setToolTip("Send Message")
        self.send_button.clicked.connect(self._on_send_clicked)
        self.send_button.setEnabled(False)  # Disabled until text entered
        input_layout.addWidget(self.send_button)
        
        return input_widget
        
    def _setup_menu(self):
        """Setup the application menu"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        # New chat action
        new_chat_action = QAction("New Chat", self)
        new_chat_action.setShortcut("Ctrl+N")
        new_chat_action.triggered.connect(self._on_new_chat_clicked)
        file_menu.addAction(new_chat_action)
        
        # Export chat action
        export_action = QAction("Export Chat...", self)
        export_action.triggered.connect(self._on_export_chat_clicked)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self._on_settings_clicked)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        # Logout action
        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self._on_logout_clicked)
        file_menu.addAction(logout_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        
        # Copy action
        copy_action = QAction("Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self._on_copy_clicked)
        edit_menu.addAction(copy_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
        # About action
        about_action = QAction("About VPA", self)
        about_action.triggered.connect(self._on_about_clicked)
        help_menu.addAction(about_action)
        
    def _on_messages_changed(self):
        """Handle changes to message list"""
        # Update UI to reflect new messages
        self.chat_display.update_messages()
        
        # Scroll to bottom if appropriate
        if self.settings_manager.get("chat_interface.auto_scroll", True):
            self.chat_display.scroll_to_bottom()
            
        # Save chat data
        if self.current_chat_id:
            self._save_chat_data(self.current_chat_id)
            
    def _on_processing_changed(self):
        """Handle changes to processing state"""
        is_processing = self.chat_view_model.is_processing
        
        # Update send button state
        self.send_button.setEnabled(not is_processing)
        
        # Show/hide processing indicator
        self.processing_indicator.setVisible(is_processing)
        
    def _on_new_chat_clicked(self):
        """Create a new chat session"""
        # Create new chat ID
        new_chat_id = str(uuid.uuid4())
        
        # Update current chat ID
        self.current_chat_id = new_chat_id
        
        # Clear chat display
        self.chat_view_model.messages = []
        self.chat_display.update_messages()
        
        # Set default title
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        default_title = f"New Chat ({timestamp})"
        self.chat_title_edit.setText(default_title)
        
        # Create chat metadata
        chat_metadata = {
            "id": new_chat_id,
            "title": default_title,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Add to chat history
        self.chat_history_view_model.add_chat(chat_metadata)
        
        # Update chat list
        self._update_chat_history_list()
        
        # Save as last active chat
        self.settings_manager.set("chat_interface.last_active_chat", new_chat_id)
        
    def _load_chat(self, chat_id):
        """Load a chat from storage"""
        if not chat_id:
            return
        
        # Load chat data
        chat_data = self.chat_history_view_model.get_chat_data(chat_id)
        if not chat_data:
            return
        
        # Update current chat ID
        self.current_chat_id = chat_id
        
        # Set chat title
        metadata = self.chat_history_view_model.get_chat_metadata(chat_id)
        if metadata:
            self.chat_title_edit.setText(metadata.get("title", "Untitled Chat"))
        
        # Update chat display
        self.chat_view_model.messages = chat_data.get("messages", [])
        self.chat_display.update_messages()
        
        # Save as last active chat
        self.settings_manager.set("chat_interface.last_active_chat", chat_id)
        
    def _load_last_active_chat(self):
        """Load the last active chat session"""
        # Get last active chat ID
        last_chat_id = self.settings_manager.get("chat_interface.last_active_chat")
        
        if last_chat_id:
            # Try to load the chat
            self._load_chat(last_chat_id)
        else:
            # Create a new chat if none exists
            self._on_new_chat_clicked()
            
    def _update_chat_history_list(self):
        """Update the chat history list widget"""
        self.chat_list_widget.clear()
        
        # Get chat history
        chat_history = self.chat_history_view_model.get_chat_history()
        
        # Add items to list
        for chat_metadata in chat_history:
            item = QListWidgetItem(chat_metadata.get("title", "Untitled Chat"))
            item.setData(Qt.UserRole, chat_metadata.get("id"))
            
            # Highlight current chat
            if self.current_chat_id and self.current_chat_id == chat_metadata.get("id"):
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                
            self.chat_list_widget.addItem(item)
            
    def _on_chat_selected(self, item):
        """Handle chat selection from the list"""
        chat_id = item.data(Qt.UserRole)
        if chat_id != self.current_chat_id:
            self._load_chat(chat_id)
            
    def _show_chat_context_menu(self, position):
        """Show context menu for chat list items"""
        item = self.chat_list_widget.itemAt(position)
        if not item:
            return
            
        chat_id = item.data(Qt.UserRole)
        
        # Create context menu
        menu = QMenu()
        
        # Rename action
        rename_action = menu.addAction("Rename")
        rename_action.triggered.connect(lambda: self._rename_chat_dialog(chat_id))
        
        # Delete action
        delete_action = menu.addAction("Delete")
        delete_action.triggered.connect(lambda: self._delete_chat_dialog(chat_id))
        
        # Show context menu
        menu.exec_(self.chat_list_widget.mapToGlobal(position))
        
    def _save_chat_data(self, chat_id):
        """Save current chat data to storage"""
        if not chat_id:
            return
            
        # Get current messages
        messages = self.chat_view_model.messages
        
        # Create chat data object
        chat_data = {
            "messages": messages
        }
        
        # Save chat data
        self.chat_history_view_model.save_chat_data(chat_id, chat_data)
        
        # Update chat metadata
        metadata = self.chat_history_view_model.get_chat_metadata(chat_id)
        if metadata:
            metadata["updated_at"] = datetime.now().isoformat()
            self.chat_history_view_model.update_chat_metadata(chat_id, metadata)
            
    def _on_chat_title_changed(self):
        """Handle chat title changes"""
        if not self.current_chat_id:
            return
            
        # Get new title
        new_title = self.chat_title_edit.text().strip()
        if not new_title:
            # Reset to old title if empty
            metadata = self.chat_history_view_model.get_chat_metadata(self.current_chat_id)
            if metadata:
                self.chat_title_edit.setText(metadata.get("title", "Untitled Chat"))
            return
            
        # Update chat metadata
        metadata = self.chat_history_view_model.get_chat_metadata(self.current_chat_id)
        if metadata:
            metadata["title"] = new_title
            self.chat_history_view_model.update_chat_metadata(self.current_chat_id, metadata)
            
            # Update chat list
            self._update_chat_history_list()
            
    def _on_logout_clicked(self):
        """Handle logout action"""
        if QMessageBox.question(
            self,
            "Logout",
            "Are you sure you want to log out? You will need to login again.",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            # Clear remember me setting
            self.settings_manager.set("auth.remember_me", False)
            
            # Emit logout event
            self.event_bus.emit("auth.logout_requested")
            
            # Close application (auth system will handle restart/login)
            self.close()
        
    def save_state(self):
        """Save window state for next launch"""
        # Save window geometry
        geometry = self.saveGeometry()
        self.settings_manager.set(
            "ui.main_window.geometry", 
            base64.b64encode(geometry).decode('ascii')
        )
        
        # Save window state (toolbars, docks)
        state = self.saveState()
        self.settings_manager.set(
            "ui.main_window.state",
            base64.b64encode(state).decode('ascii')
        )
        
    def _restore_window_state(self):
        """Restore window state from settings"""
        # Restore geometry
        geometry = self.settings_manager.get("ui.main_window.geometry")
        if geometry:
            self.restoreGeometry(base64.b64decode(geometry))
        
        # Restore state
        state = self.settings_manager.get("ui.main_window.state")
        if state:
            self.restoreState(base64.b64decode(state))
            
    def closeEvent(self, event):
        """Handle window close event"""
        minimize_to_tray = self.settings_manager.get("ui.minimize_to_tray", True)
        
        if minimize_to_tray and self.ui_manager.tray_icon:
            # Minimize to tray instead of closing
            event.ignore()
            self.hide()
        else:
            # Actually close
            event.accept()
            # Request application shutdown
            self.event_bus.emit("app.shutdown_requested")
```

### 3.2 Settings Window

The settings window provides interface for all application configuration:

#### 3.2.1 Layout

```
┌─────────────────────────────────────┐
│  Search:  [                    ]    │
├────────────┬────────────────────────┤
│            │                        │
│  Category  │                        │
│    Tree    │    Settings Panel      │
│            │                        │
│            │                        │
├────────────┴────────────────────────┤
│ [Reset] [Logout] [Cancel]   [Apply] │
└─────────────────────────────────────┘
```

#### 3.2.2 Components

- **Search Bar**: Filter settings across all categories
- **Category Tree**: Hierarchical display of setting categories
- **Settings Panel**: Dynamic panel showing settings for selected category
- **Action Buttons**: Apply, Cancel, Reset, and Logout buttons

#### 3.2.3 Implementation

```python
class SettingsWindow(QDialog):
    """Settings configuration window"""
    
    def __init__(self, parent, settings_manager, event_bus):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.event_bus = event_bus
        self.original_settings = {}
        self.modified_settings = {}
        
        # Setup UI
        self._setup_ui()
        
        # Load current settings
        self._load_current_settings()
        
    def _setup_ui(self):
        """Setup the UI components"""
        # Window properties
        self.setWindowTitle("Settings")
        self.setMinimumSize(900, 600)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search settings...")
        self.search_edit.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit, 1)
        layout.addLayout(search_layout)
        
        # Splitter for category tree and settings panel
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter, 1)
        
        # Category tree
        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderHidden(True)
        self.category_tree.itemClicked.connect(self._on_category_selected)
        splitter.addWidget(self.category_tree)
        
        # Settings stack
        self.settings_stack = QStackedWidget()
        splitter.addWidget(self.settings_stack)
        
        # Set initial splitter sizes
        splitter.setSizes([200, 700])  # 200px for tree, 700px for settings
        
        # Button row
        button_layout = QHBoxLayout()
        
        # Reset button
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self._on_reset_clicked)
        button_layout.addWidget(self.reset_button)
        
        # Logout button
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self._on_logout_clicked)
        button_layout.addWidget(self.logout_button)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        # Spacer
        button_layout.addStretch(1)
        
        # Apply button
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self._on_apply_clicked)
        self.apply_button.setEnabled(False)  # Disabled until changes are made
        button_layout.addWidget(self.apply_button)
        
        layout.addLayout(button_layout)
        
        # Populate category tree and settings panels
        self._populate_categories()
        
    def _populate_categories(self):
        """Populate the category tree and settings panels"""
        schema = self.settings_manager.get_schema()
        
        for category_name, category_schema in schema.items():
            # Create category item
            category_item = QTreeWidgetItem(self.category_tree)
            category_item.setText(0, self._format_category_name(category_name))
            category_item.setData(0, Qt.UserRole, category_name)
            
            # Create settings panel for this category
            panel = SettingsPanel(
                category_name, 
                category_schema, 
                self.settings_manager,
                self._on_setting_changed
            )
            self.settings_stack.addWidget(panel)
        
        # Select first category
        if self.category_tree.topLevelItemCount() > 0:
            self.category_tree.setCurrentItem(self.category_tree.topLevelItem(0))
            self.settings_stack.setCurrentIndex(0)
            
    def _format_category_name(self, name):
        """Format category name for display"""
        return name.replace('_', ' ').title()
        
    def _on_category_selected(self, item):
        """Handle category selection"""
        category_name = item.data(0, Qt.UserRole)
        
        # Find index of corresponding panel
        for i in range(self.settings_stack.count()):
            panel = self.settings_stack.widget(i)
            if panel.category_name == category_name:
                self.settings_stack.setCurrentIndex(i)
                break
                
    def _load_current_settings(self):
        """Load current settings into UI"""
        self.original_settings = self.settings_manager.get_all()
        self.modified_settings = copy.deepcopy(self.original_settings)
        
        # Update all panels with current settings
        for i in range(self.settings_stack.count()):
            panel = self.settings_stack.widget(i)
            panel.load_settings(self.modified_settings)
            
    def _on_setting_changed(self, path, value):
        """Handle setting value change"""
        # Update in our modified settings
        parts = path.split('.')
        current = self.modified_settings
        
        # Navigate to the correct nested dictionary
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
            
        # Set the value
        current[parts[-1]] = value
        
        # Enable apply button
        self.apply_button.setEnabled(True)
        
    def _on_apply_clicked(self):
        """Handle apply button click"""
        # Apply all changed settings
        for path, new_value in self._get_changed_settings():
            self.settings_manager.set(path, new_value)
            
        # Update original settings
        self.original_settings = copy.deepcopy(self.modified_settings)
        
        # Disable apply button
        self.apply_button.setEnabled(False)
        
    def _on_reset_clicked(self):
        """Handle reset button click"""
        if QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            # Reset all settings to defaults
            self.settings_manager.reset_all()
            
            # Reload settings
            self._load_current_settings()
            
            # Update UI
            for i in range(self.settings_stack.count()):
                panel = self.settings_stack.widget(i)
                panel.load_settings(self.modified_settings)
                
    def _on_logout_clicked(self):
        """Handle logout button click"""
        if QMessageBox.question(
            self,
            "Logout",
            "Are you sure you want to log out? You will need to log in again next time.",
            QMessageBox.Yes | QMessageBox.No
        ) == QMessageBox.Yes:
            # Clear remember me setting
            self.settings_manager.set("auth.remember_me", False)
            
            # Emit logout event
            self.event_bus.emit("auth.logout_requested")
            
            # Close settings dialog
            self.accept()
            
            # Close main window (auth system will handle restart/login)
            if self.parent():
                self.parent().close()
                
    def _on_search_changed(self, text):
        """Handle search text change"""
        # Implementation details...
        
    def _get_changed_settings(self):
        """Get list of changed settings as (path, value) pairs"""
        changes = []
        
        def compare_dict(original, modified, path_prefix=""):
            for key, new_value in modified.items():
                current_path = f"{path_prefix}.{key}" if path_prefix else key
                
                if key not in original:
                    # New setting
                    changes.append((current_path, new_value))
                elif isinstance(new_value, dict) and isinstance(original[key], dict):
                    # Recurse into nested dictionaries
                    compare_dict(original[key], new_value, current_path)
                elif original[key] != new_value:
                    # Changed value
                    changes.append((current_path, new_value))
                    
        compare_dict(self.original_settings, self.modified_settings)
        return changes
```

### 3.3 Chat Display Component

The chat display shows the conversation history with modern chat bubbles and avatars:

#### 3.3.1 Features

- **Chat Bubbles**: Modern chat bubble UI for messages
- **Avatars**: User and assistant avatars next to messages
- **Markdown Support**: Render markdown formatting in messages
- **Code Highlighting**: Syntax highlighting for code blocks
- **Automatic Scrolling**: Scroll to show new messages
- **Message Timestamps**: Display time for each message
- **Message Actions**: Copy, save, and react to messages
- **Attachment Display**: Show attached files and documents

#### 3.3.2 Implementation

```python
class ChatDisplay(QWidget):
    """Component to display chat messages"""
    
    def __init__(self, chat_view_model):
        super().__init__()
        self.chat_view_model = chat_view_model
        self.settings_manager = None  # Will be set by MainWindow
        
        # Setup UI
        self._setup_ui()
        
        # Connect view model handlers
        self.chat_view_model.add_property_changed_handler(
            "messages", self.update_messages
        )
        
    def set_settings_manager(self, settings_manager):
        """Set the settings manager reference"""
        self.settings_manager = settings_manager
        
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layout.addWidget(self.scroll_area)
        
        # Scroll content widget
        self.content_widget = QWidget()
        self.content_widget.setObjectName("chatContentWidget")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_layout.setContentsMargins(15, 15, 15, 15)
        self.content_layout.setSpacing(16)  # Space between message bubbles
        self.content_layout.addStretch(1)  # Push content to top
        self.scroll_area.setWidget(self.content_widget)
        
        # Welcome message
        self._add_welcome_message()
        
    def _add_welcome_message(self):
        """Add a welcome message to empty chat"""
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        
        # Logo/icon
        logo_label = QLabel()
        pixmap = QPixmap(":/images/vpa_logo.png").scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(logo_label)
        
        # Welcome text
        welcome_text = QLabel("Welcome to VPA Assistant")
        welcome_text.setAlignment(Qt.AlignCenter)
        font = welcome_text.font()
        font.setPointSize(16)
        font.setBold(True)
        welcome_text.setFont(font)
        welcome_layout.addWidget(welcome_text)
        
        # Description
        desc_text = QLabel("How can I help you today?")
        desc_text.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(desc_text)
        
        self.content_layout.addWidget(welcome_widget)
        
    def update_messages(self):
        """Update the display with current messages"""
        # Clear existing messages
        self._clear_messages()
        
        # Track if we need to scroll to bottom
        should_scroll = self._is_scrolled_to_bottom()
        
        # Get messages
        messages = self.chat_view_model.messages
        
        # If no messages, show welcome message
        if not messages:
            self._add_welcome_message()
            return
            
        # Add messages to display
        for message in messages:
            role = message.get("role")
            content = message.get("content", "")
            timestamp = message.get("timestamp")
            
            # Create message bubble
            message_widget = self._create_message_widget(role, content, timestamp)
            self.content_layout.addWidget(message_widget)
        
        # Scroll to bottom if needed
        if should_scroll:
            self.scroll_to_bottom()
            
    def _clear_messages(self):
        """Clear all message widgets"""
        # Remove all widgets except the spacer at the end
        while self.content_layout.count() > 1:
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
    def _create_message_widget(self, role, content, timestamp=None):
        """Create a message widget for the given role and content"""
        if role == "user":
            return UserMessageBubble(content, timestamp)
        elif role == "system":
            return SystemMessageBubble(content, timestamp)
        else:
            return AssistantMessageBubble(content, timestamp)
            
    def _is_scrolled_to_bottom(self):
        """Check if the scroll area is scrolled to the bottom"""
        scrollbar = self.scroll_area.verticalScrollBar()
        return scrollbar.value() >= scrollbar.maximum() - 100  # Within 100px of bottom
        
    def scroll_to_bottom(self):
        """Scroll to the bottom of the chat"""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
```

#### 3.3.3 Message Bubble Components

```python
class MessageBubbleBase(QWidget):
    """Base class for message bubbles"""
    
    def __init__(self, content, timestamp=None):
        super().__init__()
        self.content = content
        self.timestamp = timestamp
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the UI components - to be implemented by subclasses"""
        pass
        
class UserMessageBubble(MessageBubbleBase):
    """Chat bubble for user messages"""
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(10)
        
        # Add space on left to push content to right
        layout.addStretch(1)
        
        # Content area
        content_widget = QWidget()
        content_widget.setObjectName("userMessageBubble")
        content_widget.setMinimumWidth(200)
        content_widget.setMaximumWidth(600)
        
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 10, 15, 10)
        
        # Message content using markdown renderer
        content_label = QMarkdownTextEdit(self.content)
        content_label.setReadOnly(True)
        content_label.setFrameStyle(QFrame.NoFrame)
        content_label.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        content_layout.addWidget(content_label)
        
        # Timestamp if available
        if self.timestamp:
            try:
                dt = datetime.fromisoformat(self.timestamp)
                time_str = dt.strftime("%I:%M %p")
                
                time_label = QLabel(time_str)
                time_label.setObjectName("messageTimestamp")
                time_label.setAlignment(Qt.AlignRight)
                
                # Small, gray text
                font = time_label.font()
                font.setPointSize(8)
                time_label.setFont(font)
                time_label.setStyleSheet("color: #888888;")
                
                content_layout.addWidget(time_label)
            except (ValueError, TypeError):
                pass  # Invalid timestamp format
        
        layout.addWidget(content_widget)
        
        # User avatar (right side)
        avatar_label = QLabel()
        avatar_label.setFixedSize(36, 36)
        avatar_pixmap = self._get_user_avatar()
        avatar_label.setPixmap(avatar_pixmap)
        layout.addWidget(avatar_label)
        
    def _get_user_avatar(self):
        """Get the user avatar image"""
        # Try to load custom user avatar
        avatar_path = QSettings().value("user/avatar_path", "")
        if avatar_path and os.path.exists(avatar_path):
            pixmap = QPixmap(avatar_path)
        else:
            # Use default avatar
            pixmap = QPixmap(":/images/default_user_avatar.png")
            
        # Create circular avatar
        rounded_pixmap = QPixmap(36, 36)
        rounded_pixmap.fill(Qt.transparent)
        
        painter = QPainter(rounded_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(pixmap.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 36, 36)
        painter.end()
        
        return rounded_pixmap
        
class AssistantMessageBubble(MessageBubbleBase):
    """Chat bubble for assistant messages"""
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(10)
        
        # Assistant avatar (left side)
        avatar_label = QLabel()
        avatar_label.setFixedSize(36, 36)
        avatar_pixmap = self._get_assistant_avatar()
        avatar_label.setPixmap(avatar_pixmap)
        layout.addWidget(avatar_label)
        
        # Content area
        content_widget = QWidget()
        content_widget.setObjectName("assistantMessageBubble")
        content_widget.setMinimumWidth(200)
        content_widget.setMaximumWidth(600)
        
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 10, 15, 10)
        
        # Message content using markdown renderer
        content_label = QMarkdownTextEdit(self.content)
        content_label.setReadOnly(True)
        content_label.setFrameStyle(QFrame.NoFrame)
        content_label.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        content_layout.addWidget(content_label)
        
        # Timestamp if available
        if self.timestamp:
            try:
                dt = datetime.fromisoformat(self.timestamp)
                time_str = dt.strftime("%I:%M %p")
                
                time_label = QLabel(time_str)
                time_label.setObjectName("messageTimestamp")
                time_label.setAlignment(Qt.AlignRight)
                
                # Small, gray text
                font = time_label.font()
                font.setPointSize(8)
                time_label.setFont(font)
                time_label.setStyleSheet("color: #888888;")
                
                content_layout.addWidget(time_label)
            except (ValueError, TypeError):
                pass  # Invalid timestamp format
        
        layout.addWidget(content_widget)
        
        # Add space on right
        layout.addStretch(1)
        
    def _get_assistant_avatar(self):
        """Get the assistant avatar image"""
        # Use VPA assistant avatar
        pixmap = QPixmap(":/images/assistant_avatar.png")
            
        # Create circular avatar
        rounded_pixmap = QPixmap(36, 36)
        rounded_pixmap.fill(Qt.transparent)
        
        painter = QPainter(rounded_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(pixmap.scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 36, 36)
        painter.end()
        
        return rounded_pixmap
        
class SystemMessageBubble(MessageBubbleBase):
    """Chat bubble for system messages"""
    
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        
        # Content area - centered
        content_widget = QWidget()
        content_widget.setObjectName("systemMessageBubble")
        content_widget.setMaximumWidth(500)
        
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 8, 15, 8)
        
        # Message content
        content_label = QLabel(self.content)
        content_label.setWordWrap(True)
        content_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(content_label)
        
        # Center widget in layout
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(content_widget)
        h_layout.addStretch()
        
        layout.addLayout(h_layout)
```

## 4. UI States and Transitions

### 4.1 Application States

The UI can be in these primary states:

1. **Normal State**: Main window visible and interactive
2. **Minimized State**: Main window minimized to taskbar
3. **Hidden State**: Main window hidden, accessible via system tray
4. **Dialog State**: Modal dialog shown over main window
5. **Processing State**: Waiting for LLM or system operation
6. **Recording State**: Recording a custom workflow

### 4.2 State Transitions

State transitions occur based on:

1. **User Actions**: Direct UI interactions (buttons, menus)
2. **System Events**: Application events (startup, shutdown)
3. **External Events**: OS events (system theme change)

### 4.3 State Indicators

The UI indicates states through:

1. **Visual Indicators**:
   - Loading spinners for processing state
   - Status bar messages for current state
   - Highlighted elements for recording state

2. **System Tray**:
   - Different icons for different states
   - Status information in tooltip
   - Context menu reflects current state

## 5. Theme Implementation

### 5.1 Theme Architecture

Themes are implemented using:

1. **Qt Style Sheets**: Core styling mechanism
2. **Theme Definitions**: JSON files defining colors, sizes, etc.
3. **Dynamic Loading**: Runtime theme switching without restart

### 5.2 Theme Components

Each theme defines:

1. **Color Palette**:
   - Primary/secondary/accent colors
   - Background colors for different surfaces
   - Text colors for different emphasis levels

2. **Component Styling**:
   - Button appearances for different states
   - Input field styling
   - Message bubble styling
   - Dialog appearances

3. **Icons and Assets**:
   - Theme-specific icon sets
   - UI element graphics
   - Status indicators

### 5.3 Theme Example

```json
{
  "name": "Dark Theme",
  "id": "dark",
  "colors": {
    "primary": "#4285F4",
    "secondary": "#34A853",
    "accent": "#FBBC05",
    "error": "#EA4335",
    "background": {
      "primary": "#121212",
      "secondary": "#1E1E1E",
      "elevated": "#2D2D2D"
    },
    "text": {
      "primary": "#FFFFFF",
      "secondary": "#ABABAB",
      "hint": "#787878",
      "disabled": "#5F5F5F"
    },
    "divider": "#2D2D2D",
    "overlay": "#80000000"
  },
  "metrics": {
    "borderRadius": {
      "small": "4px",
      "medium": "8px",
      "large": "16px"
    },
    "spacing": {
      "small": "8px",
      "medium": "16px",
      "large": "24px"
    },
    "iconSize": {
      "small": "16px",
      "medium": "24px",
      "large": "32px"
    }
  },
  "chat": {
    "userBubble": {
      "background": "#1E4976",
      "text": "#FFFFFF",
      "border": "#1E4976"
    },
    "assistantBubble": {
      "background": "#2D2D2D",
      "text": "#FFFFFF",
      "border": "#3D3D3D"
    }
  }
}
```

### 5.4 Theme Manager

```python
class ThemeManager:
    """Manages UI themes"""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.themes = {}
        self.current_theme = None
        self.load_themes()
        
    def load_themes(self):
        """Load all available themes"""
        theme_dir = os.path.join(get_app_dir(), "themes")
        
        # Ensure theme directory exists
        if not os.path.exists(theme_dir):
            os.makedirs(theme_dir)
            
        # Load built-in themes
        self._load_builtin_themes()
        
        # Load user themes
        for filename in os.listdir(theme_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(theme_dir, filename), 'r') as file:
                        theme_data = json.load(file)
                        self._register_theme(theme_data)
                except Exception as e:
                    logger.error(f"Failed to load theme {filename}: {e}")
                    
    def _load_builtin_themes(self):
        """Load built-in themes"""
        # Light theme
        light_theme = {
            "name": "Light",
            "id": "light",
            # Theme data...
        }
        self._register_theme(light_theme)
        
        # Dark theme
        dark_theme = {
            "name": "Dark",
            "id": "dark",
            # Theme data...
        }
        self._register_theme(dark_theme)
        
    def _register_theme(self, theme_data):
        """Register a theme"""
        theme_id = theme_data.get("id")
        if not theme_id:
            logger.warning("Theme missing ID, skipping")
            return
            
        self.themes[theme_id] = theme_data
        
    def get_theme(self, theme_id):
        """Get theme by ID"""
        return self.themes.get(theme_id)
        
    def get_stylesheet(self, theme_id):
        """Generate Qt stylesheet for the theme"""
        theme = self.get_theme(theme_id)
        if not theme:
            return ""
            
        # Generate stylesheet from theme data
        stylesheet = self._generate_stylesheet(theme)
        return stylesheet
        
    def _generate_stylesheet(self, theme):
        """Generate Qt stylesheet from theme data"""
        colors = theme.get("colors", {})
        metrics = theme.get("metrics", {})
        
        # Base stylesheet
        stylesheet = f"""
        /* Base Application Styles */
        QWidget {{
            background-color: {colors.get("background", {}).get("primary", "#FFFFFF")};
            color: {colors.get("text", {}).get("primary", "#000000")};
            font-family: "Segoe UI", sans-serif;
            font-size: 10pt;
        }}
        
        /* Main Window */
        QMainWindow {{
            background-color: {colors.get("background", {}).get("primary", "#FFFFFF")};
        }}
        
        /* Buttons */
        QPushButton {{
            background-color: {colors.get("primary", "#4285F4")};
            color: #FFFFFF;
            border: none;
            border-radius: {metrics.get("borderRadius", {}).get("medium", "8px")};
            padding: 8px 16px;
        }}
        
        QPushButton:hover {{
            background-color: {self._lighten(colors.get("primary", "#4285F4"), 0.1)};
        }}
        
        QPushButton:pressed {{
            background-color: {self._darken(colors.get("primary", "#4285F4"), 0.1)};
        }}
        
        QPushButton:disabled {{
            background-color: {colors.get("background", {}).get("secondary", "#F1F1F1")};
            color: {colors.get("text", {}).get("disabled", "#9E9E9E")};
        }}
        
        /* More component styles... */
        """
        
        return stylesheet
        
    def _lighten(self, color, factor=0.1):
        """Lighten a color by the given factor"""
        # Implementation...
        
    def _darken(self, color, factor=0.1):
        """Darken a color by the given factor"""
        # Implementation...
```

## 6. Accessibility Compliance

### 6.1 Accessibility Standards

The UI will comply with these accessibility standards:

1. **WCAG 2.1 AA**: Web Content Accessibility Guidelines
2. **Section 508**: US federal requirements for software
3. **EN 301 549**: European accessibility requirements

### 6.2 Keyboard Navigation

Full keyboard navigation support:

1. **Focus Indicators**: Clear visual focus indicators
2. **Tab Order**: Logical tab order through UI elements
3. **Keyboard Shortcuts**: Shortcuts for all common actions
4. **Focus Trapping**: Modal dialogs trap keyboard focus

### 6.3 Screen Reader Support

Support for screen readers via:

1. **Accessible Names**: All controls have accessible names
2. **Role Information**: Clear roles for custom controls
3. **State Information**: Control states conveyed to screen readers
4. **Live Regions**: Dynamic content updates announced

### 6.4 Visual Accessibility

Support for users with visual impairments:

1. **Color Contrast**: All text meets minimum contrast ratios
2. **Text Scaling**: UI adapts to increased text sizes
3. **High Contrast**: Compatible with high contrast modes
4. **Non-Color Information**: Information not conveyed by color alone

## 7. UI Performance

### 7.1 Performance Targets

| Operation | Target Time | Measurement Method |
|-----------|-------------|-------------------|
| Initial Window Load | < 1000ms | Time from app.show_ui to window visible |
| Navigation/Tab Switch | < 200ms | Time to display new view |
| Button Click Response | < 100ms | Time to visual feedback |
| Settings Apply | < 300ms | Time to apply all changed settings |
| Theme Switch | < 500ms | Time to completely apply new theme |

### 7.2 Optimization Techniques

1. **Lazy Loading**:
   - Load components when needed
   - Defer non-essential UI initialization

2. **Efficient Rendering**:
   - Minimize repaints and reflows
   - Use view recycling for lists

3. **Asynchronous Operations**:
   - Move heavy work off UI thread
   - Show progress indicators for long operations

4. **Caching**:
   - Cache complex calculations
   - Pre-compute and store frequently used values

### 7.3 Performance Testing

Regular performance testing with:

1. **Automated UI Tests**: Measure interaction times
2. **Frame Rate Monitoring**: Ensure smooth animations
3. **Memory Usage Tracking**: Prevent memory leaks
4. **CPU Profiling**: Identify performance bottlenecks

## 8. Implementation Guidelines

### 8.1 UI Development Process

1. **Design First**: Create mockups before implementation
2. **Component-Based**: Build reusable UI components
3. **Consistent Patterns**: Follow same patterns across UI
4. **Incremental Testing**: Test each component as built

### 8.2 UI Code Organization

```
ui/
├── components/             # Reusable UI components
│   ├── buttons.py
│   ├── chat_display.py
│   ├── input_field.py
│   └── ...
├── windows/               # Application windows
│   ├── main_window.py
│   ├── settings_window.py
│   └── ...
├── dialogs/               # Modal dialogs
│   ├── confirmation_dialog.py
│   ├── error_dialog.py
│   └── ...
├── view_models/           # View models for UI logic
│   ├── chat_view_model.py
│   ├── settings_view_model.py
│   └── ...
├── themes/                # Theme management
│   ├── theme_manager.py
│   └── ...
└── ui_manager.py          # Central UI manager
```

### 8.3 Quality Assurance

Ensure UI quality with:

1. **UI Automation Testing**: Test key user flows
2. **Visual Regression Testing**: Compare UI screenshots
3. **Accessibility Testing**: Automated and manual checks
4. **Cross-Resolution Testing**: Test at multiple window sizes

## Conclusion

This UI Design Specification provides comprehensive guidance for implementing a consistent, accessible, and performant user interface for the VPA application. By following these guidelines, the application will deliver a high-quality user experience while maintaining alignment with the overall architectural principles of the system.

---

*UI Design Specification created on August 29, 2025*  
*Version: 1.0*  
*Related Documents: EXTENDED_REQUIREMENTS_AND_FEATURES.md (v1.0)*
