"""
Chat Area Component for VPA Chat UI
Displays chat messages with bubbles, avatars, timestamps, and scrollable history.
Implements modern chat interface with accessibility features.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import math

from ...core.events import EventBus


class ChatArea(ttk.Frame):
    """
    Chat Area Component - Modern Chat Interface
    
    Features:
    - Chat bubbles for user and agent messages
    - Avatar display and timestamps
    - Scrollable message history
    - System message support
    - Accessible design with keyboard navigation
    - Dark/light theme support
    """
    
    def __init__(self, parent, event_bus: EventBus):
        """Initialize the chat area."""
        super().__init__(parent)
        self.event_bus = event_bus
        self.messages = []
        self.theme = "dark"
        
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Create scrollable chat container
        self._create_chat_container()
        
        # Apply initial styling
        self._setup_styling()
    
    def _create_chat_container(self) -> None:
        """Create the scrollable chat message container."""
        # Main canvas for scrolling
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Scrollable frame
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure scrolling
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Mouse wheel binding
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # Configure scrollable frame
        self.scrollable_frame.columnconfigure(0, weight=1)
        
        # Welcome message
        self._add_welcome_message()
    
    def _setup_styling(self) -> None:
        """Setup styling for the chat area."""
        if self.theme == "dark":
            bg_color = "#1e1e1e"
            self.canvas.configure(bg=bg_color)
            self.scrollable_frame.configure(style="Dark.TFrame")
        else:
            bg_color = "#ffffff"
            self.canvas.configure(bg=bg_color)
            self.scrollable_frame.configure(style="Light.TFrame")
    
    def _add_welcome_message(self) -> None:
        """Add initial welcome message."""
        welcome_message = {
            "type": "system",
            "content": "Welcome to VPA! I'm your virtual personal assistant. How can I help you today?",
            "timestamp": datetime.now().isoformat()
        }
        self.add_message(welcome_message)
    
    def add_message(self, message: Dict[str, Any]) -> None:
        """
        Add a message to the chat area.
        
        Args:
            message: Message dict with type, content, timestamp, etc.
        """
        try:
            message_type = message.get("type", "user")
            content = message.get("content", "")
            timestamp = message.get("timestamp", datetime.now().isoformat())
            avatar = message.get("avatar")
            metadata = message.get("metadata", {})
            
            # Create message frame
            message_frame = self._create_message_frame(message_type, content, timestamp, avatar, metadata)
            
            # Add to scrollable frame
            row = len(self.messages)
            message_frame.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
            
            # Store message
            self.messages.append(message)
            
            # Auto-scroll to bottom
            self._scroll_to_bottom()
            
        except Exception as e:
            print(f"Error adding message: {e}")
    
    def _create_message_frame(self, message_type: str, content: str, timestamp: str, avatar: Optional[str], metadata: Dict[str, Any]) -> ttk.Frame:
        """Create a styled message frame with modern rounded bubbles."""
        # Main message frame
        msg_frame = ttk.Frame(self.scrollable_frame)
        msg_frame.columnconfigure(1, weight=1)
        
        # Determine alignment and styling based on message type
        if message_type == "user":
            bg_color = "#0078d4" if self.theme == "dark" else "#0066cc"
            fg_color = "white"
            avatar_text = "👤"
            bubble_border = "#005bb5" if self.theme == "dark" else "#0052a3"
        elif message_type == "agent":
            bg_color = "#3a3a3a" if self.theme == "dark" else "#f5f5f5"
            fg_color = "white" if self.theme == "dark" else "#333333"
            avatar_text = "🤖"
            bubble_border = "#505050" if self.theme == "dark" else "#e0e0e0"
        else:  # system
            bg_color = "#4a4a4a" if self.theme == "dark" else "#e8e8e8"
            fg_color = "#cccccc" if self.theme == "dark" else "#666666"
            avatar_text = "ℹ️"
            bubble_border = "#606060" if self.theme == "dark" else "#d0d0d0"
        
        # Create canvas for rounded bubble with shadow effect
        canvas_frame = tk.Frame(msg_frame, bg=self.canvas.cget("bg"))
        
        if message_type == "user":
            canvas_frame.grid(row=0, column=1, sticky="e", padx=(50, 5), pady=3)
        else:
            canvas_frame.grid(row=0, column=1, sticky="w", padx=(5, 50), pady=3)
        
        # Calculate bubble size
        temp_label = tk.Label(canvas_frame, text=content, font=("Segoe UI", 11), wraplength=350)
        temp_label.update_idletasks()
        text_width = min(350, temp_label.winfo_reqwidth()) + 24
        text_height = temp_label.winfo_reqheight() + 16
        temp_label.destroy()
        
        # Create canvas for rounded rectangle
        bubble_canvas = tk.Canvas(
            canvas_frame,
            width=text_width + 6,
            height=text_height + 6,
            bg=self.canvas.cget("bg"),
            highlightthickness=0
        )
        bubble_canvas.pack()
        
        # Draw shadow
        shadow_color = "#000000" if self.theme == "dark" else "#cccccc"
        self._create_rounded_rectangle(bubble_canvas, 4, 4, text_width + 2, text_height + 2, 
                                     radius=16, fill=shadow_color, outline="")
        
        # Draw main bubble
        self._create_rounded_rectangle(bubble_canvas, 2, 2, text_width, text_height, 
                                     radius=16, fill=bg_color, outline=bubble_border, width=1)
        
        # Message content label
        content_label = tk.Label(
            bubble_canvas,
            text=content,
            bg=bg_color,
            fg=fg_color,
            font=("Segoe UI", 11),
            wraplength=350,
            justify="left",
            padx=0,
            pady=0
        )
        
        # Center the text in the bubble
        text_x = text_width // 2
        text_y = text_height // 2
        bubble_canvas.create_window(text_x, text_y, window=content_label)
        
        # Avatar with improved styling
        avatar_frame = tk.Frame(msg_frame, bg=self.canvas.cget("bg"))
        if message_type == "user":
            avatar_frame.grid(row=0, column=2, padx=(5, 0), sticky="ne")
        else:
            avatar_frame.grid(row=0, column=0, padx=(0, 5), sticky="nw")
        
        # Avatar with circular background
        avatar_canvas = tk.Canvas(avatar_frame, width=36, height=36, 
                                bg=self.canvas.cget("bg"), highlightthickness=0)
        avatar_canvas.pack()
        
        # Draw avatar circle
        avatar_bg = "#0078d4" if message_type == "user" else "#666666"
        avatar_canvas.create_oval(2, 2, 34, 34, fill=avatar_bg, outline="", width=0)
        
        avatar_label = tk.Label(
            avatar_canvas,
            text=avatar_text,
            bg=avatar_bg,
            fg="white",
            font=("Segoe UI", 14),
            width=2,
            height=1
        )
        avatar_canvas.create_window(18, 18, window=avatar_label)
        
        # Timestamp with improved styling
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%H:%M")
        except:
            time_str = timestamp[:5] if len(timestamp) > 5 else timestamp
        
        timestamp_color = "#888888" if self.theme == "dark" else "#666666"
        timestamp_label = tk.Label(
            msg_frame,
            text=time_str,
            font=("Segoe UI", 9),
            fg=timestamp_color,
            bg=self.canvas.cget("bg")
        )
        
        if message_type == "user":
            timestamp_label.grid(row=1, column=1, sticky="e", padx=(0, 20), pady=(2, 0))
        else:
            timestamp_label.grid(row=1, column=1, sticky="w", padx=(20, 0), pady=(2, 0))
        
        return msg_frame
    
    def _create_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius=10, **kwargs):
        """Create a rounded rectangle on a canvas."""
        points = []
        
        # Simplified rounded rectangle using curves
        # Top side
        points.extend([x1 + radius, y1])
        points.extend([x2 - radius, y1])
        
        # Top-right corner (approximated)
        points.extend([x2, y1 + radius])
        
        # Right side
        points.extend([x2, y2 - radius])
        
        # Bottom-right corner
        points.extend([x2 - radius, y2])
        
        # Bottom side
        points.extend([x1 + radius, y2])
        
        # Bottom-left corner
        points.extend([x1, y2 - radius])
        
        # Left side
        points.extend([x1, y1 + radius])
        
        # Top-left corner back to start
        points.extend([x1 + radius, y1])
        
        return canvas.create_polygon(points, smooth=True, **kwargs)
    
    def clear_messages(self) -> None:
        """Clear all messages from the chat area."""
        try:
            # Clear stored messages
            self.messages.clear()
            
            # Destroy all child widgets in scrollable frame
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            
            # Add welcome message back
            self._add_welcome_message()
            
        except Exception as e:
            print(f"Error clearing messages: {e}")
    
    def apply_theme(self, theme: str) -> None:
        """Apply a new theme to the chat area."""
        self.theme = theme
        self._setup_styling()
        
        # Refresh all messages with new theme
        messages_backup = self.messages.copy()
        self.clear_messages()
        
        # Re-add messages with new theme
        for message in messages_backup[:-1]:  # Exclude welcome message
            self.add_message(message)
    
    def _on_frame_configure(self, event) -> None:
        """Handle frame configuration changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event) -> None:
        """Handle canvas configuration changes."""
        # Update scrollable frame width to match canvas
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _on_mousewheel(self, event) -> None:
        """Handle mouse wheel scrolling."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the chat area."""
        self.update_idletasks()
        self.canvas.yview_moveto(1.0)
