"""
VPA Chat-First UI Implementation
Modern chat-centric interface matching Copilot-style specification.
Implements event-driven communication with accessible, responsive design.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import asyncio
import threading
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import json
from pathlib import Path

from ..core.events import EventBus
from .components.chat_area import ChatArea
from .components.input_area import InputArea
from .components.resource_monitor import ResourceMonitor
from .components.settings_panel import SettingsPanel
from .components.addon_panel import AddonPanel


class VPAChatUI:
    """
    VPA Chat-First UI - Modern Copilot-Style Interface
    
    Features:
    - Chat-centric design with bubbles, avatars, timestamps
    - Multi-modal input (text, voice, files)
    - Resource monitoring with user control
    - Comprehensive settings and addon management
    - Full accessibility compliance
    - Event-driven architecture integration
    """
    
    def __init__(self, event_bus: EventBus):
        """Initialize the VPA Chat UI."""
        self.event_bus = event_bus
        self.logger = logging.getLogger(__name__)
        
        # UI state
        self._initialized = False
        self._theme = "dark"  # dark/light
        self._font_size = 12
        self._accessibility_mode = False
        
        # Main window
        self.root: Optional[tk.Tk] = None
        self.main_frame: Optional[ttk.Frame] = None
        
        # Core components
        self.chat_area: Optional[ChatArea] = None
        self.input_area: Optional[InputArea] = None
        self.resource_monitor: Optional[ResourceMonitor] = None
        self.settings_panel: Optional[SettingsPanel] = None
        self.addon_panel: Optional[AddonPanel] = None
        
        # Chat state
        self.chat_history = []
        self.current_session_id = None
        
        # UI thread management
        self.ui_thread = None
        self.ui_queue = asyncio.Queue()
        
        self.logger.info("VPA Chat UI initialized")
    
    async def initialize(self) -> bool:
        """Initialize the chat UI and all components."""
        try:
            self.logger.info("Initializing VPA Chat UI...")
            
            # Setup UI thread
            self._setup_ui_thread()
            
            # Wait for UI to be ready
            await asyncio.sleep(0.1)
            
            # Register event handlers
            await self._register_ui_events()
            
            self._initialized = True
            self.event_bus.emit("ui.chat.initialized", {"status": "success"})
            self.logger.info("VPA Chat UI initialized successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize VPA Chat UI: {e}")
            self.event_bus.emit("ui.chat.initialized", {"status": "error", "error": str(e)})
            return False
    
    def _setup_ui_thread(self) -> None:
        """Setup the UI thread for tkinter."""
        def run_ui():
            try:
                self._create_main_window()
                self._setup_layout()
                self._apply_theme()
                self._setup_event_processing()
                
                # Mark as ready
                self._ui_ready = True
                
                # Start the tkinter main loop
                self.root.mainloop()
                
            except Exception as e:
                self.logger.error(f"UI thread error: {e}")
        
        # Add UI ready flag
        self._ui_ready = False
        
        self.ui_thread = threading.Thread(target=run_ui, daemon=True)
        self.ui_thread.start()
        
        # Wait for UI to be ready
        import time
        timeout = 5.0
        start_time = time.time()
        while not self._ui_ready and (time.time() - start_time) < timeout:
            time.sleep(0.1)
    
    def _create_main_window(self) -> None:
        """Create the main application window."""
        self.root = tk.Tk()
        self.root.title("VPA - Virtual Personal Assistant")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Configure window icon (if available)
        try:
            icon_path = Path(__file__).parent.parent.parent.parent / "assets" / "vpa_icon.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception:
            pass  # Continue without icon
        
        # Configure window closing
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        # Configure for accessibility
        self.root.option_add("*Font", "Segoe UI 12")
        
        self.logger.info("Main window created")
    
    def _setup_layout(self) -> None:
        """Setup the main UI layout."""
        # Configure grid weights for responsive design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Main container frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Top row: Resource monitor (left) + Chat area header (right)
        self._setup_top_row()
        
        # Middle row: Chat area (main content)
        self._setup_chat_area()
        
        # Bottom row: Input area + Settings button
        self._setup_bottom_row()
        
        self.logger.info("UI layout configured")
    
    def _setup_top_row(self) -> None:
        """Setup the top row with resource monitor and header."""
        # Top frame
        top_frame = ttk.Frame(self.main_frame)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        top_frame.columnconfigure(1, weight=1)
        
        # Resource monitor (top-left)
        self.resource_monitor = ResourceMonitor(top_frame, self.event_bus)
        self.resource_monitor.grid(row=0, column=0, sticky="nw")
        
        # Chat header (top-right)
        header_frame = ttk.Frame(top_frame)
        header_frame.grid(row=0, column=1, sticky="ne")
        
        # New Chat button
        self.new_chat_btn = ttk.Button(
            header_frame,
            text="+ New Chat",
            command=self._start_new_chat,
            style="Accent.TButton"
        )
        self.new_chat_btn.pack(side="right", padx=(10, 0))
        
        # Chat title
        self.chat_title = ttk.Label(
            header_frame,
            text="VPA Assistant",
            font=("Segoe UI", 16, "bold")
        )
        self.chat_title.pack(side="right", padx=(0, 20))
    
    def _setup_chat_area(self) -> None:
        """Setup the main chat area."""
        # Chat area frame
        chat_frame = ttk.Frame(self.main_frame)
        chat_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Create chat area component
        self.chat_area = ChatArea(chat_frame, self.event_bus)
        self.chat_area.grid(row=0, column=0, sticky="nsew")
    
    def _setup_bottom_row(self) -> None:
        """Setup the bottom row with input area and settings."""
        # Bottom frame
        bottom_frame = ttk.Frame(self.main_frame)
        bottom_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        bottom_frame.columnconfigure(1, weight=1)
        
        # Settings button (bottom-left)
        self.settings_btn = ttk.Button(
            bottom_frame,
            text="⚙️ Settings",
            command=self._open_settings,
            width=12
        )
        self.settings_btn.grid(row=0, column=0, sticky="sw")
        
        # Input area (bottom-center/right)
        input_frame = ttk.Frame(bottom_frame)
        input_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        input_frame.columnconfigure(0, weight=1)
        
        self.input_area = InputArea(input_frame, self.event_bus)
        self.input_area.grid(row=0, column=0, sticky="ew")
    
    def _apply_theme(self) -> None:
        """Apply the current theme to the UI."""
        try:
            if not self.root:
                return
                
            # Configure ttk styles
            style = ttk.Style()
            
            if self._theme == "dark":
                # Dark theme colors
                bg_color = "#1e1e1e"
                fg_color = "#ffffff"
                accent_color = "#0078d4"
                input_bg = "#2d2d2d"
                button_bg = "#404040"
                frame_bg = "#2d2d2d"
                
                # Configure styles
                style.theme_use("clam")
                style.configure("TFrame", background=bg_color, borderwidth=0)
                style.configure("TLabel", background=bg_color, foreground=fg_color)
                style.configure("TButton", 
                              background=button_bg, 
                              foreground=fg_color,
                              borderwidth=1,
                              focuscolor="none")
                style.map("TButton",
                         background=[('active', '#505050')])
                style.configure("Accent.TButton", 
                              background=accent_color, 
                              foreground="white",
                              borderwidth=1,
                              focuscolor="none")
                style.map("Accent.TButton",
                         background=[('active', '#106ebe')])
                style.configure("Secondary.TButton",
                              background="#505050",
                              foreground=fg_color,
                              borderwidth=1,
                              focuscolor="none")
                style.map("Secondary.TButton",
                         background=[('active', '#606060')])
                style.configure("Recording.TButton",
                              background="#dc3545",
                              foreground="white",
                              borderwidth=1,
                              focuscolor="none")
                style.map("Recording.TButton",
                         background=[('active', '#c82333')])
                
                # Configure root window
                self.root.configure(bg=bg_color)
                
            else:
                # Light theme colors
                bg_color = "#f8f9fa"
                fg_color = "#212529"
                accent_color = "#0078d4"
                input_bg = "#ffffff"
                button_bg = "#e9ecef"
                frame_bg = "#ffffff"
                
                # Configure styles
                style.theme_use("winnative")
                style.configure("TFrame", background=bg_color, borderwidth=0)
                style.configure("TLabel", background=bg_color, foreground=fg_color)
                style.configure("TButton", 
                              background=button_bg, 
                              foreground=fg_color,
                              borderwidth=1,
                              focuscolor="none")
                style.map("TButton",
                         background=[('active', '#dee2e6')])
                style.configure("Accent.TButton", 
                              background=accent_color, 
                              foreground="white",
                              borderwidth=1,
                              focuscolor="none")
                style.map("Accent.TButton",
                         background=[('active', '#106ebe')])
                style.configure("Secondary.TButton",
                              background="#6c757d",
                              foreground="white",
                              borderwidth=1,
                              focuscolor="none")
                style.map("Secondary.TButton",
                         background=[('active', '#5a6268')])
                style.configure("Recording.TButton",
                              background="#dc3545",
                              foreground="white",
                              borderwidth=1,
                              focuscolor="none")
                style.map("Recording.TButton",
                         background=[('active', '#c82333')])
                
                # Configure root window
                self.root.configure(bg=bg_color)
            
            # Add theme toggle button to header
            if hasattr(self, 'new_chat_btn') and self.new_chat_btn:
                # Create theme toggle button if it doesn't exist
                if not hasattr(self, 'theme_btn'):
                    header_frame = self.new_chat_btn.master
                    self.theme_btn = ttk.Button(
                        header_frame,
                        text="🌙" if self._theme == "light" else "☀️",
                        width=3,
                        command=self._toggle_theme,
                        style="Secondary.TButton"
                    )
                    self.theme_btn.pack(side="right", padx=(5, 10))
                else:
                    # Update existing button
                    self.theme_btn.configure(text="🌙" if self._theme == "light" else "☀️")
            
            self.logger.info(f"Applied {self._theme} theme")
            
        except Exception as e:
            self.logger.warning(f"Failed to apply theme: {e}")
    
    def _toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        try:
            new_theme = "light" if self._theme == "dark" else "dark"
            self._theme = new_theme
            
            # Apply theme to main UI
            self._apply_theme()
            
            # Update all components
            if self.chat_area:
                self.chat_area.apply_theme(new_theme)
            if self.input_area:
                self.input_area.apply_theme(new_theme)
            if self.resource_monitor:
                self.resource_monitor.apply_theme(new_theme)
            
            # Emit theme change event
            self.event_bus.emit("ui.settings.theme_changed", {"theme": new_theme})
            
            self.logger.info(f"Theme toggled to {new_theme}")
            
        except Exception as e:
            self.logger.error(f"Failed to toggle theme: {e}")
    
    def _setup_event_processing(self) -> None:
        """Setup event processing for UI updates."""
        def process_ui_events():
            try:
                # Process any queued UI events
                while not self.ui_queue.empty():
                    try:
                        event = self.ui_queue.get_nowait()
                        self._handle_ui_event(event)
                    except asyncio.QueueEmpty:
                        break
                
                # Schedule next processing
                if self.root:
                    self.root.after(100, process_ui_events)
                
            except Exception as e:
                self.logger.error(f"Error processing UI events: {e}")
        
        # Start event processing
        if self.root:
            self.root.after(100, process_ui_events)
    
    def _handle_ui_event(self, event: Dict[str, Any]) -> None:
        """Handle UI-specific events."""
        event_type = event.get("type")
        data = event.get("data", {})
        
        if event_type == "add_message":
            self._add_chat_message(data)
        elif event_type == "update_resource_monitor":
            self._update_resource_monitor(data)
        elif event_type == "show_notification":
            self._show_notification(data)
        elif event_type == "update_theme":
            self._update_theme(data)
    
    async def _register_ui_events(self) -> None:
        """Register UI event handlers."""
        # Chat events
        self.event_bus.subscribe("ui.chat.add_message", self._handle_add_message)
        self.event_bus.subscribe("ui.chat.new_session", self._handle_new_session)
        self.event_bus.subscribe("ui.chat.clear_history", self._handle_clear_history)
        
        # Input area events
        self.event_bus.subscribe("ui.input.message_sent", self._handle_message_sent)
        self.event_bus.subscribe("ui.input.file_uploaded", self._handle_file_uploaded)
        self.event_bus.subscribe("ui.input.voice_recording_started", self._handle_voice_recording)
        self.event_bus.subscribe("ui.input.voice_recording_stopped", self._handle_voice_stopped)
        
        # Resource events
        self.event_bus.subscribe("ui.resource.update", self._handle_resource_update)
        self.event_bus.subscribe("ui.resource.warning", self._handle_resource_warning)
        
        # Settings events
        self.event_bus.subscribe("ui.settings.theme_changed", self._handle_theme_changed)
        self.event_bus.subscribe("ui.settings.font_changed", self._handle_font_changed)
        
        # LLM response events
        self.event_bus.subscribe("llm.message.response", self._handle_llm_response)
        self.event_bus.subscribe("llm.message.error", self._handle_llm_error)
        
        # Addon events
        self.event_bus.subscribe("ui.addon.status_changed", self._handle_addon_status)
        
        self.logger.info("UI event handlers registered")
    
    # New event handlers for input area
    async def _handle_message_sent(self, data: Any = None) -> None:
        """Handle message sent from input area."""
        if isinstance(data, dict):
            # Add user message to chat
            user_message = {
                "type": "user",
                "content": data.get("content", ""),
                "timestamp": data.get("timestamp", datetime.now().isoformat())
            }
            await self._handle_add_message(user_message)
    
    async def _handle_file_uploaded(self, data: Any = None) -> None:
        """Handle file uploaded from input area."""
        if isinstance(data, dict):
            file_path = data.get("file_path", "")
            file_name = Path(file_path).name if file_path else "Unknown file"
            
            # Add file message to chat
            file_message = {
                "type": "user",
                "content": f"📎 Uploaded: {file_name}",
                "timestamp": data.get("timestamp", datetime.now().isoformat()),
                "metadata": {"file_path": file_path, "type": "file"}
            }
            await self._handle_add_message(file_message)
    
    async def _handle_llm_response(self, data: Any = None) -> None:
        """Handle LLM response."""
        if isinstance(data, dict):
            # Add agent response to chat
            agent_message = {
                "type": "agent",
                "content": data.get("content", ""),
                "timestamp": data.get("timestamp", datetime.now().isoformat()),
                "metadata": data.get("metadata", {})
            }
            await self._handle_add_message(agent_message)
    
    async def _handle_llm_error(self, data: Any = None) -> None:
        """Handle LLM error."""
        if isinstance(data, dict):
            error_message = data.get("error", "An error occurred while processing your request.")
            # Add system error message to chat
            system_message = {
                "type": "system",
                "content": f"❌ Error: {error_message}",
                "timestamp": datetime.now().isoformat()
            }
            await self._handle_add_message(system_message)
    
    # Event handlers
    async def _handle_add_message(self, data: Any = None) -> None:
        """Handle add message event."""
        if isinstance(data, dict):
            # Ensure both user and agent messages are displayed properly
            message_type = data.get("type", "user")
            content = data.get("content", "")
            
            # Don't echo user messages as agent messages
            if message_type == "user":
                await self._queue_ui_event("add_message", data)
            elif message_type in ["agent", "system"]:
                await self._queue_ui_event("add_message", data)
            
            # If this is a user message, also emit an event for processing
            if message_type == "user":
                self.event_bus.emit("llm.message.request", {
                    "content": content,
                    "session_id": self.current_session_id,
                    "timestamp": data.get("timestamp", datetime.now().isoformat())
                })
    
    async def _handle_new_session(self, data: Any = None) -> None:
        """Handle new session event."""
        if isinstance(data, dict):
            self.current_session_id = data.get("session_id")
            await self._queue_ui_event("add_message", {
                "type": "system",
                "content": "New chat session started",
                "timestamp": datetime.now().isoformat()
            })
    
    async def _handle_clear_history(self, data: Any = None) -> None:
        """Handle clear history event."""
        self.chat_history.clear()
        if self.chat_area:
            self.chat_area.clear_messages()
    
    async def _handle_resource_update(self, data: Any = None) -> None:
        """Handle resource update event."""
        if isinstance(data, dict):
            await self._queue_ui_event("update_resource_monitor", data)
    
    async def _handle_resource_warning(self, data: Any = None) -> None:
        """Handle resource warning event."""
        if isinstance(data, dict):
            await self._queue_ui_event("show_notification", {
                "type": "warning",
                "title": "Resource Warning",
                "message": data.get("message", "High resource usage detected")
            })
    
    async def _handle_theme_changed(self, data: Any = None) -> None:
        """Handle theme change event."""
        if isinstance(data, dict):
            new_theme = data.get("theme", "dark")
            await self._queue_ui_event("update_theme", {"theme": new_theme})
    
    async def _handle_font_changed(self, data: Any = None) -> None:
        """Handle font change event."""
        if isinstance(data, dict):
            self._font_size = data.get("size", 12)
            # Update font throughout UI
    
    async def _handle_voice_recording(self, data: Any = None) -> None:
        """Handle voice recording started event."""
        if self.input_area:
            self.input_area.set_voice_recording(True)
    
    async def _handle_voice_stopped(self, data: Any = None) -> None:
        """Handle voice recording stopped event."""
        if self.input_area:
            self.input_area.set_voice_recording(False)
    
    async def _handle_addon_status(self, data: Any = None) -> None:
        """Handle addon status change event."""
        if isinstance(data, dict):
            await self._queue_ui_event("show_notification", {
                "type": "info",
                "title": "Addon Status",
                "message": f"Addon {data.get('addon')} is now {data.get('status')}"
            })
    
    # UI interaction methods
    def _start_new_chat(self) -> None:
        """Start a new chat session."""
        try:
            # Clear current chat
            self.chat_history.clear()
            if self.chat_area:
                self.chat_area.clear_messages()
            
            # Emit new session event
            self.event_bus.emit("ui.chat.new_session_requested", {
                "timestamp": datetime.now().isoformat()
            })
            
            self.logger.info("New chat session started")
            
        except Exception as e:
            self.logger.error(f"Failed to start new chat: {e}")
    
    def _open_settings(self) -> None:
        """Open the settings panel."""
        try:
            if not self.settings_panel:
                self.settings_panel = SettingsPanel(self.root, self.event_bus)
            
            self.settings_panel.show()
            
        except Exception as e:
            self.logger.error(f"Failed to open settings: {e}")
            messagebox.showerror("Error", f"Failed to open settings: {e}")
    
    def _add_chat_message(self, data: Dict[str, Any]) -> None:
        """Add a message to the chat area."""
        try:
            message = {
                "type": data.get("type", "user"),  # user, agent, system
                "content": data.get("content", ""),
                "timestamp": data.get("timestamp", datetime.now().isoformat()),
                "avatar": data.get("avatar"),
                "metadata": data.get("metadata", {})
            }
            
            self.chat_history.append(message)
            
            if self.chat_area:
                self.chat_area.add_message(message)
            
        except Exception as e:
            self.logger.error(f"Failed to add chat message: {e}")
    
    def _update_resource_monitor(self, data: Dict[str, Any]) -> None:
        """Update the resource monitor display."""
        try:
            if self.resource_monitor:
                self.resource_monitor.update_resources(data)
        except Exception as e:
            self.logger.error(f"Failed to update resource monitor: {e}")
    
    def _show_notification(self, data: Dict[str, Any]) -> None:
        """Show a notification to the user."""
        try:
            notification_type = data.get("type", "info")
            title = data.get("title", "VPA Notification")
            message = data.get("message", "")
            
            if notification_type == "error":
                messagebox.showerror(title, message)
            elif notification_type == "warning":
                messagebox.showwarning(title, message)
            else:
                messagebox.showinfo(title, message)
                
        except Exception as e:
            self.logger.error(f"Failed to show notification: {e}")
    
    def _update_theme(self, data: Dict[str, Any]) -> None:
        """Update the UI theme."""
        try:
            new_theme = data.get("theme", "dark")
            if new_theme != self._theme:
                self._theme = new_theme
                self._apply_theme()
                
                # Update all components
                if self.chat_area:
                    self.chat_area.apply_theme(new_theme)
                if self.input_area:
                    self.input_area.apply_theme(new_theme)
                if self.resource_monitor:
                    self.resource_monitor.apply_theme(new_theme)
                    
        except Exception as e:
            self.logger.error(f"Failed to update theme: {e}")
    
    async def _queue_ui_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Queue a UI event for processing."""
        try:
            event = {"type": event_type, "data": data}
            await self.ui_queue.put(event)
        except Exception as e:
            self.logger.error(f"Failed to queue UI event: {e}")
    
    def _on_window_close(self) -> None:
        """Handle window close event."""
        try:
            # Emit close event
            self.event_bus.emit("ui.chat.closing", {
                "timestamp": datetime.now().isoformat()
            })
            
            # Close the window
            if self.root:
                self.root.quit()
                self.root.destroy()
            
        except Exception as e:
            self.logger.error(f"Error during window close: {e}")
    
    # Public methods
    async def show(self) -> None:
        """Show the chat UI."""
        if not self._initialized:
            await self.initialize()
        
        # Ensure UI is visible (handled by UI thread)
        pass
    
    async def hide(self) -> None:
        """Hide the chat UI."""
        if self.root:
            self.root.withdraw()
    
    async def add_message(self, message_type: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Add a message to the chat."""
        await self._handle_add_message({
            "type": message_type,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })
    
    async def update_resources(self, resource_data: Dict[str, Any]) -> None:
        """Update resource monitor with new data."""
        await self._handle_resource_update(resource_data)
    
    def is_running(self) -> bool:
        """Check if the UI is running."""
        try:
            return (self._initialized and 
                   self.root is not None and 
                   hasattr(self.root, 'winfo_exists') and
                   self.root.winfo_exists())
        except:
            return False
    
    async def shutdown(self) -> None:
        """Shutdown the chat UI gracefully."""
        try:
            if self.root:
                self.root.quit()
            
            self._initialized = False
            self.logger.info("VPA Chat UI shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during UI shutdown: {e}")
