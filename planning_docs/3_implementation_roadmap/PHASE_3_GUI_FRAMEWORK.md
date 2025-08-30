# Phase 3: GUI Framework Implementation Plan

## Overview

This document outlines the implementation plan for Phase 3 of the VPA project, focusing on the GUI Framework. Building on the core architecture (Phase 1) and audio system (Phase 2), this phase will implement a modern, responsive, and accessible graphical user interface that provides intuitive interaction with the VPA.

## Goals and Objectives

1. Implement a complete GUI framework for visual interaction with the VPA
2. Create a modern, intuitive, and accessible user interface
3. Ensure seamless integration with the event-driven architecture
4. Support both voice and text-based interaction modes
5. Provide visual feedback for voice commands and system responses
6. Create a plugin-based UI component system for extensibility

## Prerequisites

- Completion of Phase 1 (Core Architecture)
- Completion of Phase 2 (Audio System)
- Python environment with UI libraries (PyQt6/PySide6)
- Asset pipeline for icons, sounds, and visual elements
- Accessibility standards compliance requirements

## Implementation Components

### 1. GUI Manager

The `GUIManager` class will serve as the central coordinator for all GUI-related functionality, handling window creation, component management, and event coordination.

```python
# src/vpa/gui/gui_manager.py
from vpa.gui.main_window import MainWindow
from vpa.gui.settings_window import SettingsWindow
from vpa.gui.chat_interface import ChatInterface
from vpa.core.events import event_bus
import asyncio
import logging

logger = logging.getLogger(__name__)

class GUIManager:
    """Manages all GUI components and windows."""
    
    def __init__(self, config=None):
        """Initialize the GUI manager.
        
        Args:
            config: Configuration dictionary
        """
        self._config = config or {}
        self._main_window = None
        self._settings_window = None
        self._windows = {}
        self._initialized = False
        self._running = False
        
    async def initialize(self):
        """Initialize GUI subsystems."""
        if self._initialized:
            return True
            
        logger.info("Initializing GUI Manager")
        
        try:
            # Import Qt here to avoid loading unless needed
            from PyQt6.QtWidgets import QApplication
            import sys
            
            # Create Qt application if not already created
            if not QApplication.instance():
                self._app = QApplication(sys.argv)
            else:
                self._app = QApplication.instance()
                
            # Load theme and styles
            self._load_theme()
            
            # Create main window
            self._main_window = MainWindow(self._config.get("main_window", {}))
            
            # Create settings window
            self._settings_window = SettingsWindow(self._config.get("settings", {}))
            
            # Initialize chat interface
            self._chat_interface = ChatInterface(self._config.get("chat", {}))
            self._main_window.set_chat_interface(self._chat_interface)
            
            # Subscribe to events
            event_bus.subscribe("show_main_window", self._on_show_main_window)
            event_bus.subscribe("show_settings_window", self._on_show_settings_window)
            event_bus.subscribe("voice_command", self._on_voice_command)
            event_bus.subscribe("speak_text", self._on_speak_text)
            
            self._initialized = True
            logger.info("GUI Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize GUI Manager: {e}")
            return False
            
    def _load_theme(self):
        """Load theme and style resources."""
        try:
            from PyQt6.QtCore import QFile, QTextStream
            
            # Get theme name from config or use default
            theme_name = self._config.get("theme", "dark")
            theme_file = f":/themes/{theme_name}.qss"
            
            file = QFile(theme_file)
            if file.exists():
                file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text)
                stream = QTextStream(file)
                self._app.setStyleSheet(stream.readAll())
                file.close()
                logger.info(f"Loaded theme: {theme_name}")
            else:
                logger.warning(f"Theme file not found: {theme_file}")
        except Exception as e:
            logger.error(f"Failed to load theme: {e}")
            
    async def start(self):
        """Start the GUI."""
        if self._running or not self._initialized:
            return
            
        logger.info("Starting GUI")
        
        # Show main window
        self._main_window.show()
        
        self._running = True
        logger.info("GUI started")
        
    async def stop(self):
        """Stop the GUI."""
        if not self._running:
            return
            
        logger.info("Stopping GUI")
        
        # Hide all windows
        if self._main_window:
            self._main_window.hide()
        if self._settings_window:
            self._settings_window.hide()
            
        self._running = False
        logger.info("GUI stopped")
        
    async def _on_show_main_window(self, _):
        """Handle show_main_window events."""
        if self._main_window:
            self._main_window.show()
            self._main_window.raise_()
            self._main_window.activateWindow()
            
    async def _on_show_settings_window(self, _):
        """Handle show_settings_window events."""
        if self._settings_window:
            self._settings_window.show()
            self._settings_window.raise_()
            self._settings_window.activateWindow()
            
    async def _on_voice_command(self, event_data):
        """Handle voice_command events."""
        text = event_data.get("text", "")
        if text and self._chat_interface:
            self._chat_interface.add_user_message(text, "voice")
            
    async def _on_speak_text(self, event_data):
        """Handle speak_text events."""
        text = event_data.get("text", "")
        if text and self._chat_interface:
            self._chat_interface.add_assistant_message(text)
            
    def run_event_loop(self):
        """Run the Qt event loop (blocking)."""
        if self._app:
            return self._app.exec()
            
    async def shutdown(self):
        """Shut down GUI subsystems."""
        logger.info("Shutting down GUI Manager")
        
        # Stop GUI if running
        if self._running:
            await self.stop()
            
        # Unsubscribe from events
        event_bus.unsubscribe("show_main_window", self._on_show_main_window)
        event_bus.unsubscribe("show_settings_window", self._on_show_settings_window)
        event_bus.unsubscribe("voice_command", self._on_voice_command)
        event_bus.unsubscribe("speak_text", self._on_speak_text)
        
        # Clean up resources
        if self._main_window:
            self._main_window.close()
            self._main_window = None
            
        if self._settings_window:
            self._settings_window.close()
            self._settings_window = None
            
        self._initialized = False
        logger.info("GUI Manager shutdown complete")
        
        return True
```

### 2. Main Window Implementation

The main window serves as the primary container for the VPA interface, providing the structure for all UI components.

```python
# src/vpa/gui/main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QToolBar, QStatusBar, QLabel
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QSize
import logging

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main window for the VPA GUI."""
    
    def __init__(self, config=None):
        """Initialize the main window.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__()
        
        self._config = config or {}
        self._chat_interface = None
        
        # Set up window properties
        self._setup_window()
        
        # Set up UI components
        self._setup_ui()
        
        # Set up toolbar and status bar
        self._setup_toolbar()
        self._setup_statusbar()
        
        logger.info("Main window initialized")
        
    def _setup_window(self):
        """Set up window properties."""
        # Set window title
        self.setWindowTitle("Virtual Personal Assistant")
        
        # Set window size
        width = self._config.get("width", 1200)
        height = self._config.get("height", 800)
        self.resize(width, height)
        
        # Set window icon
        self.setWindowIcon(QIcon(":/icons/vpa_icon.png"))
        
    def _setup_ui(self):
        """Set up UI components."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create content layout for chat interface
        self._content_layout = QVBoxLayout()
        main_layout.addLayout(self._content_layout)
        
        # Create bottom control bar
        control_bar = QHBoxLayout()
        control_bar.setContentsMargins(10, 5, 10, 5)
        
        # Add microphone button
        self._mic_button = QPushButton()
        self._mic_button.setIcon(QIcon(":/icons/mic.png"))
        self._mic_button.setIconSize(QSize(24, 24))
        self._mic_button.setToolTip("Activate voice input")
        self._mic_button.clicked.connect(self._on_mic_button_clicked)
        control_bar.addWidget(self._mic_button)
        
        # Add settings button
        settings_button = QPushButton()
        settings_button.setIcon(QIcon(":/icons/settings.png"))
        settings_button.setIconSize(QSize(24, 24))
        settings_button.setToolTip("Open settings")
        settings_button.clicked.connect(self._on_settings_button_clicked)
        control_bar.addWidget(settings_button)
        
        main_layout.addLayout(control_bar)
        
    def _setup_toolbar(self):
        """Set up the toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        
        # Add new chat action
        new_chat_action = QAction(QIcon(":/icons/new_chat.png"), "New Chat", self)
        new_chat_action.triggered.connect(self._on_new_chat_action)
        toolbar.addAction(new_chat_action)
        
        # Add saved chats action
        saved_chats_action = QAction(QIcon(":/icons/saved_chats.png"), "Saved Chats", self)
        saved_chats_action.triggered.connect(self._on_saved_chats_action)
        toolbar.addAction(saved_chats_action)
        
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        
    def _setup_statusbar(self):
        """Set up the status bar."""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Add status label
        self._status_label = QLabel("Ready")
        status_bar.addPermanentWidget(self._status_label)
        
    def set_chat_interface(self, chat_interface):
        """Set the chat interface component.
        
        Args:
            chat_interface: Chat interface component
        """
        self._chat_interface = chat_interface
        
        # Clear content layout
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Add chat interface to content layout
        self._content_layout.addWidget(chat_interface)
        
    def _on_mic_button_clicked(self):
        """Handle microphone button click."""
        from vpa.core.events import event_bus
        
        # Toggle listening state
        if self._mic_button.property("listening"):
            # Stop listening
            self._mic_button.setProperty("listening", False)
            self._mic_button.setIcon(QIcon(":/icons/mic.png"))
            self._status_label.setText("Voice input deactivated")
            
            # Emit stop_listening event
            event_bus.emit("stop_listening", {})
        else:
            # Start listening
            self._mic_button.setProperty("listening", True)
            self._mic_button.setIcon(QIcon(":/icons/mic_active.png"))
            self._status_label.setText("Listening...")
            
            # Emit start_listening event
            event_bus.emit("start_listening", {})
            
    def _on_settings_button_clicked(self):
        """Handle settings button click."""
        from vpa.core.events import event_bus
        event_bus.emit("show_settings_window", {})
        
    def _on_new_chat_action(self):
        """Handle new chat action."""
        if self._chat_interface:
            self._chat_interface.clear_chat()
            
    def _on_saved_chats_action(self):
        """Handle saved chats action."""
        from vpa.core.events import event_bus
        event_bus.emit("show_saved_chats", {})
```

### 3. Chat Interface Implementation

The chat interface provides a conversation view for text and voice interactions with the VPA.

```python
# src/vpa/gui/chat_interface.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame, 
    QLineEdit, QPushButton, QHBoxLayout, QLabel
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize, pyqtSignal
import time
import uuid
import logging

logger = logging.getLogger(__name__)

class MessageBubble(QFrame):
    """Widget for displaying a message bubble in the chat."""
    
    def __init__(self, text, is_user=True, source="text"):
        """Initialize a message bubble.
        
        Args:
            text: Message text
            is_user: Whether the message is from the user
            source: Source of the message ("text" or "voice")
        """
        super().__init__()
        
        self._is_user = is_user
        self._source = source
        
        # Set up frame style
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("user_bubble" if is_user else "assistant_bubble")
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create header
        header_layout = QHBoxLayout()
        
        # Add icon based on source
        icon_label = QLabel()
        if is_user:
            icon = QIcon(":/icons/user.png")
            header_text = "You"
        else:
            icon = QIcon(":/icons/assistant.png")
            header_text = "Assistant"
            
        icon_label.setPixmap(icon.pixmap(QSize(16, 16)))
        header_layout.addWidget(icon_label)
        
        # Add header text
        header = QLabel(header_text)
        header.setObjectName("bubble_header")
        header_layout.addWidget(header)
        
        # Add spacer
        header_layout.addStretch()
        
        # Add source icon for user messages
        if is_user and source == "voice":
            source_icon = QLabel()
            source_icon.setPixmap(QIcon(":/icons/mic_small.png").pixmap(QSize(12, 12)))
            source_icon.setToolTip("Voice input")
            header_layout.addWidget(source_icon)
            
        layout.addLayout(header_layout)
        
        # Add message text
        message = QLabel(text)
        message.setWordWrap(True)
        message.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(message)
        
        # Add timestamp
        timestamp = QLabel(time.strftime("%H:%M:%S"))
        timestamp.setObjectName("bubble_timestamp")
        timestamp.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(timestamp)
        
class ChatInterface(QWidget):
    """Widget for displaying the chat interface."""
    
    message_sent = pyqtSignal(str)
    
    def __init__(self, config=None):
        """Initialize the chat interface.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__()
        
        self._config = config or {}
        self._message_history = []
        
        # Set up UI
        self._setup_ui()
        
        logger.info("Chat interface initialized")
        
    def _setup_ui(self):
        """Set up the UI components."""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area for messages
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        # Create message container
        self._message_container = QWidget()
        self._message_layout = QVBoxLayout(self._message_container)
        self._message_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._message_layout.setSpacing(10)
        self._message_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add spacer at the end to push messages up
        self._message_layout.addStretch()
        
        self._scroll_area.setWidget(self._message_container)
        main_layout.addWidget(self._scroll_area)
        
        # Create input area
        input_layout = QHBoxLayout()
        
        # Create text input
        self._text_input = QLineEdit()
        self._text_input.setPlaceholderText("Type your message here...")
        self._text_input.returnPressed.connect(self._on_send_clicked)
        input_layout.addWidget(self._text_input)
        
        # Create send button
        send_button = QPushButton()
        send_button.setIcon(QIcon(":/icons/send.png"))
        send_button.setIconSize(QSize(16, 16))
        send_button.clicked.connect(self._on_send_clicked)
        input_layout.addWidget(send_button)
        
        main_layout.addLayout(input_layout)
        
    def add_user_message(self, text, source="text"):
        """Add a user message to the chat.
        
        Args:
            text: Message text
            source: Source of the message ("text" or "voice")
        """
        # Create message bubble
        bubble = MessageBubble(text, True, source)
        
        # Add to layout (before the spacer)
        self._message_layout.insertWidget(self._message_layout.count() - 1, bubble)
        
        # Store in history
        self._message_history.append({
            "id": str(uuid.uuid4()),
            "type": "user",
            "text": text,
            "source": source,
            "timestamp": time.time()
        })
        
        # Scroll to bottom
        self._scroll_to_bottom()
        
    def add_assistant_message(self, text):
        """Add an assistant message to the chat.
        
        Args:
            text: Message text
        """
        # Create message bubble
        bubble = MessageBubble(text, False)
        
        # Add to layout (before the spacer)
        self._message_layout.insertWidget(self._message_layout.count() - 1, bubble)
        
        # Store in history
        self._message_history.append({
            "id": str(uuid.uuid4()),
            "type": "assistant",
            "text": text,
            "timestamp": time.time()
        })
        
        # Scroll to bottom
        self._scroll_to_bottom()
        
    def _scroll_to_bottom(self):
        """Scroll the chat view to the bottom."""
        self._scroll_area.verticalScrollBar().setValue(
            self._scroll_area.verticalScrollBar().maximum()
        )
        
    def _on_send_clicked(self):
        """Handle send button click."""
        text = self._text_input.text().strip()
        if text:
            # Add message to chat
            self.add_user_message(text, "text")
            
            # Clear input field
            self._text_input.clear()
            
            # Emit message_sent signal
            self.message_sent.emit(text)
            
            # Process message through event bus
            from vpa.core.events import event_bus
            event_bus.emit("user_input", {"text": text, "source": "text"})
            
    def clear_chat(self):
        """Clear the chat history."""
        # Clear message history
        self._message_history = []
        
        # Clear UI
        # Remove all widgets except the spacer at the end
        while self._message_layout.count() > 1:
            item = self._message_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
```

### 4. Settings Window Implementation

The settings window provides access to all configurable options for the VPA.

```python
# src/vpa/gui/settings_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QPushButton, QLabel, QComboBox, QCheckBox,
    QGroupBox, QFormLayout, QSpinBox, QHBoxLayout
)
from PyQt6.QtCore import Qt
import logging

logger = logging.getLogger(__name__)

class SettingsWindow(QMainWindow):
    """Settings window for configuring the VPA."""
    
    def __init__(self, config=None):
        """Initialize the settings window.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__()
        
        self._config = config or {}
        
        # Set up window properties
        self._setup_window()
        
        # Set up UI components
        self._setup_ui()
        
        logger.info("Settings window initialized")
        
    def _setup_window(self):
        """Set up window properties."""
        # Set window title
        self.setWindowTitle("VPA Settings")
        
        # Set window size
        self.resize(600, 500)
        
        # Set window modality
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
    def _setup_ui(self):
        """Set up UI components."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Add general settings tab
        general_tab = self._create_general_tab()
        tab_widget.addTab(general_tab, "General")
        
        # Add audio settings tab
        audio_tab = self._create_audio_tab()
        tab_widget.addTab(audio_tab, "Audio")
        
        # Add LLM settings tab
        llm_tab = self._create_llm_tab()
        tab_widget.addTab(llm_tab, "Language Model")
        
        # Add plugins tab
        plugins_tab = self._create_plugins_tab()
        tab_widget.addTab(plugins_tab, "Plugins")
        
        # Add advanced tab
        advanced_tab = self._create_advanced_tab()
        tab_widget.addTab(advanced_tab, "Advanced")
        
        main_layout.addWidget(tab_widget)
        
        # Add button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Add apply button
        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self._on_apply_clicked)
        button_layout.addWidget(apply_button)
        
        # Add save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self._on_save_clicked)
        button_layout.addWidget(save_button)
        
        # Add cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self._on_cancel_clicked)
        button_layout.addWidget(cancel_button)
        
        main_layout.addLayout(button_layout)
        
    def _create_general_tab(self):
        """Create the general settings tab.
        
        Returns:
            Widget for the general tab
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Appearance group
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout(appearance_group)
        
        # Theme selection
        theme_combo = QComboBox()
        theme_combo.addItems(["Light", "Dark", "System"])
        appearance_layout.addRow("Theme:", theme_combo)
        
        # Font size
        font_size = QSpinBox()
        font_size.setRange(8, 24)
        font_size.setValue(12)
        appearance_layout.addRow("Font Size:", font_size)
        
        layout.addWidget(appearance_group)
        
        # Behavior group
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QFormLayout(behavior_group)
        
        # Start with Windows
        startup_check = QCheckBox("Start with Windows")
        startup_check.setChecked(True)
        behavior_layout.addRow(startup_check)
        
        # Minimize to system tray
        tray_check = QCheckBox("Minimize to system tray")
        tray_check.setChecked(True)
        behavior_layout.addRow(tray_check)
        
        # Show notifications
        notifications_check = QCheckBox("Show notifications")
        notifications_check.setChecked(True)
        behavior_layout.addRow(notifications_check)
        
        layout.addWidget(behavior_group)
        
        # Add spacer
        layout.addStretch()
        
        return tab
        
    def _create_audio_tab(self):
        """Create the audio settings tab.
        
        Returns:
            Widget for the audio tab
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Device selection group
        device_group = QGroupBox("Audio Devices")
        device_layout = QFormLayout(device_group)
        
        # Input device selection
        input_combo = QComboBox()
        input_combo.addItem("Default System Microphone")
        device_layout.addRow("Input Device:", input_combo)
        
        # Output device selection
        output_combo = QComboBox()
        output_combo.addItem("Default System Speakers")
        device_layout.addRow("Output Device:", output_combo)
        
        layout.addWidget(device_group)
        
        # Voice settings group
        voice_group = QGroupBox("Voice Settings")
        voice_layout = QFormLayout(voice_group)
        
        # Voice selection
        voice_combo = QComboBox()
        voice_combo.addItems([
            "en-US-AriaNeural",
            "en-US-GuyNeural",
            "en-GB-SoniaNeural",
            "en-GB-RyanNeural"
        ])
        voice_layout.addRow("Assistant Voice:", voice_combo)
        
        # Voice speed
        speed_combo = QComboBox()
        speed_combo.addItems([
            "Very Slow", "Slow", "Normal", "Fast", "Very Fast"
        ])
        speed_combo.setCurrentText("Normal")
        voice_layout.addRow("Voice Speed:", speed_combo)
        
        layout.addWidget(voice_group)
        
        # Wake word group
        wake_group = QGroupBox("Wake Word")
        wake_layout = QFormLayout(wake_group)
        
        # Enable wake word
        wake_check = QCheckBox("Enable wake word detection")
        wake_check.setChecked(True)
        wake_layout.addRow(wake_check)
        
        # Wake word selection
        wake_combo = QComboBox()
        wake_combo.addItems([
            "Hey Assistant",
            "Computer",
            "Jarvis",
            "VPA"
        ])
        wake_layout.addRow("Wake Word:", wake_combo)
        
        layout.addWidget(wake_group)
        
        # Add spacer
        layout.addStretch()
        
        return tab
        
    def _create_llm_tab(self):
        """Create the language model settings tab.
        
        Returns:
            Widget for the LLM tab
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Model selection group
        model_group = QGroupBox("Model Selection")
        model_layout = QFormLayout(model_group)
        
        # Model type
        model_combo = QComboBox()
        model_combo.addItems([
            "Default (Recommended)",
            "Local - Small",
            "Local - Medium",
            "Local - Large",
            "Remote API"
        ])
        model_layout.addRow("Model Type:", model_combo)
        
        # Local model path
        model_path = QComboBox()
        model_path.setEditable(True)
        model_path.addItems([
            "C:/Program Files/VPA/models/default",
            "Custom Path..."
        ])
        model_layout.addRow("Model Path:", model_path)
        
        layout.addWidget(model_group)
        
        # Performance group
        perf_group = QGroupBox("Performance Settings")
        perf_layout = QFormLayout(perf_group)
        
        # Memory limit
        memory_combo = QComboBox()
        memory_combo.addItems([
            "2 GB (Minimum)",
            "4 GB (Recommended)",
            "8 GB (High Performance)",
            "Unlimited (Not Recommended)"
        ])
        memory_combo.setCurrentText("4 GB (Recommended)")
        perf_layout.addRow("Memory Limit:", memory_combo)
        
        # Threading
        thread_check = QCheckBox("Use multithreading")
        thread_check.setChecked(True)
        perf_layout.addRow(thread_check)
        
        layout.addWidget(perf_group)
        
        # Context settings group
        context_group = QGroupBox("Context Settings")
        context_layout = QFormLayout(context_group)
        
        # Context size
        context_spin = QSpinBox()
        context_spin.setRange(1, 32)
        context_spin.setValue(4)
        context_layout.addRow("Context Window (K tokens):", context_spin)
        
        # Temperature
        temp_spin = QSpinBox()
        temp_spin.setRange(1, 100)
        temp_spin.setValue(70)
        temp_spin.setSingleStep(5)
        context_layout.addRow("Temperature (0-100):", temp_spin)
        
        layout.addWidget(context_group)
        
        # Add spacer
        layout.addStretch()
        
        return tab
        
    def _create_plugins_tab(self):
        """Create the plugins settings tab.
        
        Returns:
            Widget for the plugins tab
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Plugin status label
        status_label = QLabel("5 plugins installed, 4 active")
        layout.addWidget(status_label)
        
        # Create scrollable plugin list (placeholder)
        layout.addWidget(QLabel("Plugin list will be populated at runtime"))
        
        # Plugin actions group
        action_group = QGroupBox("Plugin Actions")
        action_layout = QVBoxLayout(action_group)
        
        # Add buttons
        install_button = QPushButton("Install Plugin")
        action_layout.addWidget(install_button)
        
        update_button = QPushButton("Update All Plugins")
        action_layout.addWidget(update_button)
        
        layout.addWidget(action_group)
        
        # Add spacer
        layout.addStretch()
        
        return tab
        
    def _create_advanced_tab(self):
        """Create the advanced settings tab.
        
        Returns:
            Widget for the advanced tab
        """
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Logging group
        logging_group = QGroupBox("Logging")
        logging_layout = QFormLayout(logging_group)
        
        # Log level
        log_combo = QComboBox()
        log_combo.addItems([
            "Debug", "Info", "Warning", "Error", "Critical"
        ])
        log_combo.setCurrentText("Info")
        logging_layout.addRow("Log Level:", log_combo)
        
        # Log retention
        retention_spin = QSpinBox()
        retention_spin.setRange(1, 90)
        retention_spin.setValue(30)
        logging_layout.addRow("Log Retention (days):", retention_spin)
        
        layout.addWidget(logging_group)
        
        # Developer options group
        dev_group = QGroupBox("Developer Options")
        dev_layout = QVBoxLayout(dev_group)
        
        # Debug mode
        debug_check = QCheckBox("Enable debug mode")
        dev_layout.addWidget(debug_check)
        
        # Performance monitoring
        perf_check = QCheckBox("Enable performance monitoring")
        dev_layout.addWidget(perf_check)
        
        # Debug console
        console_check = QCheckBox("Show debug console")
        dev_layout.addWidget(console_check)
        
        layout.addWidget(dev_group)
        
        # Reset group
        reset_group = QGroupBox("Reset Options")
        reset_layout = QVBoxLayout(reset_group)
        
        # Reset buttons
        reset_settings = QPushButton("Reset All Settings")
        reset_layout.addWidget(reset_settings)
        
        clear_data = QPushButton("Clear All User Data")
        reset_layout.addWidget(clear_data)
        
        factory_reset = QPushButton("Factory Reset")
        reset_layout.addWidget(factory_reset)
        
        layout.addWidget(reset_group)
        
        # Add spacer
        layout.addStretch()
        
        return tab
        
    def _on_apply_clicked(self):
        """Handle apply button click."""
        # Apply settings without closing window
        self._save_settings()
        
    def _on_save_clicked(self):
        """Handle save button click."""
        # Save settings and close window
        self._save_settings()
        self.hide()
        
    def _on_cancel_clicked(self):
        """Handle cancel button click."""
        # Close window without saving
        self.hide()
        
    def _save_settings(self):
        """Save all settings."""
        from vpa.core.events import event_bus
        
        # Collect settings from UI
        settings = {}
        
        # TODO: Collect actual settings from UI components
        
        # Emit settings_changed event
        event_bus.emit("settings_changed", {"settings": settings})
        
        logger.info("Settings saved")
```

### 5. System Tray Integration

```python
# src/vpa/gui/system_tray.py
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from vpa.core.events import event_bus
import logging

logger = logging.getLogger(__name__)

class SystemTrayManager:
    """Manages the system tray icon and menu."""
    
    def __init__(self, config=None):
        """Initialize the system tray manager.
        
        Args:
            config: Configuration dictionary
        """
        self._config = config or {}
        self._tray_icon = None
        self._menu = None
        self._initialized = False
        
    def initialize(self):
        """Initialize the system tray.
        
        Returns:
            True if initialization succeeded
        """
        if self._initialized:
            return True
            
        try:
            # Import Qt here to avoid loading unless needed
            from PyQt6.QtWidgets import QApplication
            
            if not QSystemTrayIcon.isSystemTrayAvailable():
                logger.warning("System tray is not available")
                return False
                
            # Create tray icon
            self._tray_icon = QSystemTrayIcon()
            self._tray_icon.setIcon(QIcon(":/icons/vpa_tray.png"))
            self._tray_icon.setToolTip("Virtual Personal Assistant")
            
            # Create menu
            self._menu = QMenu()
            
            # Add menu items
            show_action = self._menu.addAction("Show")
            show_action.triggered.connect(self._on_show_triggered)
            
            settings_action = self._menu.addAction("Settings")
            settings_action.triggered.connect(self._on_settings_triggered)
            
            self._menu.addSeparator()
            
            exit_action = self._menu.addAction("Exit")
            exit_action.triggered.connect(self._on_exit_triggered)
            
            # Set context menu
            self._tray_icon.setContextMenu(self._menu)
            
            # Connect signals
            self._tray_icon.activated.connect(self._on_tray_activated)
            
            self._initialized = True
            logger.info("System tray initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize system tray: {e}")
            return False
            
    def show(self):
        """Show the system tray icon."""
        if self._tray_icon:
            self._tray_icon.show()
            
    def hide(self):
        """Hide the system tray icon."""
        if self._tray_icon:
            self._tray_icon.hide()
            
    def _on_tray_activated(self, reason):
        """Handle tray icon activation.
        
        Args:
            reason: Activation reason
        """
        # Show main window on double click
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._on_show_triggered()
            
    def _on_show_triggered(self):
        """Handle show action."""
        event_bus.emit("show_main_window", {})
        
    def _on_settings_triggered(self):
        """Handle settings action."""
        event_bus.emit("show_settings_window", {})
        
    def _on_exit_triggered(self):
        """Handle exit action."""
        event_bus.emit("exit_application", {})
        
    def show_notification(self, title, message):
        """Show a notification.
        
        Args:
            title: Notification title
            message: Notification message
        """
        if self._tray_icon:
            self._tray_icon.showMessage(
                title,
                message,
                QIcon(":/icons/vpa_notification.png")
            )
            
    def shutdown(self):
        """Shut down the system tray."""
        if self._tray_icon:
            self._tray_icon.hide()
            self._tray_icon = None
            
        self._menu = None
        self._initialized = False
        logger.info("System tray shutdown complete")
        
        return True
```

### 6. Resource Management

```python
# src/vpa/gui/resources.py
from PyQt6.QtCore import QResource
import logging

logger = logging.getLogger(__name__)

def initialize_resources():
    """Initialize GUI resources.
    
    Returns:
        True if initialization succeeded
    """
    try:
        # Register resources file
        if not QResource.registerResource("resources/vpa_resources.rcc"):
            logger.error("Failed to register resources")
            return False
            
        logger.info("GUI resources initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize resources: {e}")
        return False
```

## Implementation Tasks

### Task 1: Environment Setup

1. **Verify Dependencies**
   - Install required packages:
   ```bash
   pip install PyQt6 PyQt6-tools
   ```
   - Set up resource compiler:
   ```bash
   pyrcc6 -o resources/vpa_resources.py resources/vpa_resources.qrc
   ```

2. **Create Directory Structure**
   ```
   src/vpa/
   ├── gui/
   │   ├── __init__.py
   │   ├── gui_manager.py
   │   ├── main_window.py
   │   ├── settings_window.py
   │   ├── chat_interface.py
   │   ├── system_tray.py
   │   └── resources.py
   ├── resources/
   │   ├── icons/
   │   │   ├── vpa_icon.png
   │   │   ├── vpa_tray.png
   │   │   ├── mic.png
   │   │   ├── mic_active.png
   │   │   └── ... (other icons)
   │   ├── themes/
   │   │   ├── light.qss
   │   │   └── dark.qss
   │   └── vpa_resources.qrc
   ```

### Task 2: Core GUI Components

1. **Resource Compilation**
   - Create resource collection file (QRC)
   - Compile resources for embedding

2. **Theme System Implementation**
   - Create light and dark themes
   - Implement theme loading and switching

3. **GUI Manager Implementation**
   - Implement `GUIManager` class
   - Connect to event system

### Task 3: Window Implementations

1. **Main Window Implementation**
   - Create main application window
   - Implement layout and basic controls

2. **Settings Window Implementation**
   - Create settings panels
   - Connect settings to configuration system

3. **Chat Interface Implementation**
   - Create chat message components
   - Implement message display and input system

### Task 4: Integration with Core and Audio Systems

1. **Event Integration**
   - Define GUI events:
     - `show_main_window`
     - `show_settings_window`
     - `settings_changed`
     - `exit_application`
   - Subscribe to audio events:
     - `voice_command`
     - `speak_text`

2. **System Tray Integration**
   - Implement system tray icon and menu
   - Add notifications support

3. **Application Integration**
   - Modify Application Manager to initialize GUI
   - Ensure proper shutdown sequence

## Testing and Validation

1. **Unit Tests**
   ```python
   # tests/unit/gui/test_gui_manager.py
   import pytest
   from unittest.mock import patch, MagicMock
   from vpa.gui.gui_manager import GUIManager
   
   class TestGUIManager:
       @pytest.fixture
       def mock_app(self):
           with patch("PyQt6.QtWidgets.QApplication") as mock:
               mock.instance.return_value = None
               yield mock
               
       @pytest.fixture
       async def gui_manager(self, mock_app):
           manager = GUIManager()
           yield manager
           await manager.shutdown()
           
       @pytest.mark.asyncio
       async def test_initialize(self, gui_manager, mock_app):
           # Act
           result = await gui_manager.initialize()
           
           # Assert
           assert result is True
           mock_app.assert_called_once()
   ```

2. **Integration Tests**
   ```python
   # tests/integration/test_gui_integration.py
   import pytest
   import asyncio
   from vpa.core.events import event_bus
   from vpa.gui.gui_manager import GUIManager
   
   class TestGUIIntegration:
       @pytest.fixture
       async def gui_manager(self):
           with patch("PyQt6.QtWidgets.QApplication") as mock_app:
               mock_app.instance.return_value = None
               manager = GUIManager()
               await manager.initialize()
               yield manager
               await manager.shutdown()
               
       @pytest.mark.asyncio
       async def test_event_handling(self, gui_manager):
           # Mock main window show method
           gui_manager._main_window.show = MagicMock()
           
           # Emit event
           event_bus.emit("show_main_window", {})
           
           # Wait for event processing
           await asyncio.sleep(0.1)
           
           # Assert
           gui_manager._main_window.show.assert_called_once()
   ```

3. **Accessibility Testing**
   ```python
   # tests/accessibility/test_gui_accessibility.py
   import pytest
   from vpa.gui.main_window import MainWindow
   
   class TestAccessibility:
       @pytest.fixture
       def main_window(self):
           with patch("PyQt6.QtWidgets.QApplication") as mock_app:
               mock_app.instance.return_value = None
               window = MainWindow()
               yield window
               window.close()
               
       def test_keyboard_navigation(self, main_window):
           # Test focus order is logical
           assert main_window.focusWidget() is not None
           
       def test_color_contrast(self, main_window):
           # Use Qt's accessibility checker
           from PyQt6.QtGui import QColor
           
           # Get background and text colors
           bg_color = main_window.palette().color(QPalette.ColorRole.Window)
           text_color = main_window.palette().color(QPalette.ColorRole.WindowText)
           
           # Calculate contrast ratio
           contrast_ratio = calculate_contrast(bg_color, text_color)
           
           # WCAG AA requires 4.5:1 for normal text
           assert contrast_ratio >= 4.5
   ```

## Integration with Phase 1 and Phase 2

The GUI system must integrate seamlessly with the core architecture (Phase 1) and audio system (Phase 2):

```python
# src/vpa/core/app.py (modified to include GUI)
from vpa.core.events import event_bus
from vpa.core.plugins import PluginManager
from vpa.audio.audio_manager import AudioManager
from vpa.gui.gui_manager import GUIManager
import asyncio
import logging

logger = logging.getLogger(__name__)

class ApplicationManager:
    """Application manager for the VPA."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self, config=None):
        """Initialize the application manager.
        
        Args:
            config: Application configuration
        """
        if hasattr(self, "_initialized"):
            return
            
        self._config = config or {}
        self._plugin_manager = PluginManager()
        self._audio_manager = AudioManager(config.get("audio", {}))
        self._gui_manager = GUIManager(config.get("gui", {}))
        self._running = False
        self._initialized = False
        self._headless = config.get("headless", False)
        
    async def initialize(self):
        """Initialize the application.
        
        Returns:
            True if initialization succeeded
        """
        if self._initialized:
            return True
            
        logger.info("Initializing application")
        
        # Initialize audio system
        if not await self._audio_manager.initialize():
            logger.error("Failed to initialize audio system")
            return False
            
        # Initialize plugin manager
        if not await self._plugin_manager.initialize(self._config.get("plugins", {})):
            logger.error("Failed to initialize plugin manager")
            return False
            
        # Initialize GUI unless in headless mode
        if not self._headless:
            if not await self._gui_manager.initialize():
                logger.error("Failed to initialize GUI")
                return False
            
        # Subscribe to events
        event_bus.subscribe("voice_command", self._on_voice_command, async_callback=True)
        event_bus.subscribe("user_input", self._on_user_input, async_callback=True)
        event_bus.subscribe("exit_application", self._on_exit_application, async_callback=True)
        
        self._initialized = True
        logger.info("Application initialized")
        return True
        
    async def start(self):
        """Start the application."""
        if self._running:
            return
            
        logger.info("Starting application")
        self._running = True
        
        # Start audio system
        await self._audio_manager.start()
        
        # Start plugins
        await self._plugin_manager.start()
        
        # Start GUI unless in headless mode
        if not self._headless:
            await self._gui_manager.start()
            
        logger.info("Application started")
        
    async def stop(self):
        """Stop the application."""
        if not self._running:
            return
            
        logger.info("Stopping application")
        self._running = False
        
        # Stop audio system
        await self._audio_manager.stop()
        
        # Stop plugins
        await self._plugin_manager.stop()
        
        # Stop GUI unless in headless mode
        if not self._headless:
            await self._gui_manager.stop()
            
        logger.info("Application stopped")
        
    async def _on_voice_command(self, event_data):
        """Handle voice command events."""
        text = event_data.get("text", "")
        confidence = event_data.get("confidence", 0)
        
        if text:
            logger.info(f"Processing voice command: '{text}' (confidence: {confidence:.2f})")
            
            # Process command through plugin manager
            response = await self._plugin_manager.process_input(text, {"source": "voice"})
            
            # Speak response if available
            if response and "text" in response:
                await event_bus.emit_async("speak_text", {"text": response["text"]})
                
    async def _on_user_input(self, event_data):
        """Handle user input events."""
        text = event_data.get("text", "")
        source = event_data.get("source", "text")
        
        if text:
            logger.info(f"Processing user input: '{text}' (source: {source})")
            
            # Process input through plugin manager
            response = await self._plugin_manager.process_input(text, {"source": source})
            
            # Emit response event
            if response and "text" in response:
                await event_bus.emit_async("assistant_response", {"text": response["text"]})
                
                # Also speak response if configured
                if self._config.get("speak_responses", True):
                    await event_bus.emit_async("speak_text", {"text": response["text"]})
                    
    async def _on_exit_application(self, _):
        """Handle exit_application events."""
        logger.info("Exit application requested")
        await self.shutdown()
        
    async def run_main_loop(self):
        """Run the main application loop."""
        if not self._initialized:
            if not await self.initialize():
                logger.error("Failed to initialize application")
                return False
                
        await self.start()
        
        # If not headless, run GUI event loop
        if not self._headless and self._gui_manager:
            # This will block until GUI is closed
            exit_code = self._gui_manager.run_event_loop()
            await self.shutdown()
            return exit_code
        else:
            # In headless mode, just wait for stop signal
            try:
                while self._running:
                    await asyncio.sleep(0.1)
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
            finally:
                await self.shutdown()
                
            return 0
        
    async def shutdown(self):
        """Shut down the application."""
        logger.info("Shutting down application")
        
        # Stop application if running
        if self._running:
            await self.stop()
            
        # Unsubscribe from events
        event_bus.unsubscribe("voice_command", self._on_voice_command)
        event_bus.unsubscribe("user_input", self._on_user_input)
        event_bus.unsubscribe("exit_application", self._on_exit_application)
        
        # Shut down components in reverse order
        if not self._headless:
            await self._gui_manager.shutdown()
            
        await self._plugin_manager.shutdown()
        await self._audio_manager.shutdown()
        
        self._initialized = False
        logger.info("Application shut down complete")
        
    def is_running(self):
        """Check if the application is running."""
        return self._running
```

## Performance Targets

The GUI system must meet the following performance targets:

1. **Startup Time**
   - Window creation: < 1 second
   - Complete UI initialization: < 3 seconds

2. **Responsiveness**
   - UI thread response time: < 50ms for input handling
   - Animation smoothness: 60 FPS for transitions

3. **Memory Usage**
   - Base memory footprint: < 100MB
   - Peak memory usage: < 500MB with all components loaded

4. **Accessibility**
   - WCAG 2.1 AA compliance for all components
   - Full keyboard navigation support
   - Screen reader compatibility

## Risk Management

1. **Dependency Risks**
   - PyQt6/PySide6 are large dependencies
   - Mitigation: Lazy loading of GUI components

2. **Performance Risks**
   - GUI operations might block the event loop
   - Mitigation: Run heavy operations in background threads

3. **Integration Risks**
   - Coordinating async events with Qt's event loop
   - Mitigation: Proper signal/slot bridging between async and Qt events

## Success Criteria

Phase 3 will be considered complete when:

1. Users can interact with the VPA using a modern GUI
2. The GUI seamlessly integrates with voice and text input
3. All performance targets are met
4. UI is accessible according to WCAG 2.1 AA standards
5. All tests pass with >90% coverage
6. Documentation is complete and up-to-date

## Timeline

- **Week 1**: Environment setup and resource compilation
- **Week 2**: Core window implementations
- **Week 3**: Chat interface and system tray integration
- **Week 4**: Integration with event system and testing

## Conclusion

Phase 3 focuses on building the GUI framework that will enable visual interaction with the VPA. By implementing a modern, accessible, and responsive user interface, the system will become more usable and provide a complete user experience. The GUI system integrates with the core architecture established in Phase 1 and the audio system from Phase 2, following the same event-driven design patterns for consistency and modularity.

---

*Document created: August 29, 2025*
