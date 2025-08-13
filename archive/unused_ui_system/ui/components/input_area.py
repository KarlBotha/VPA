"""
Input Area Component for VPA Chat UI
Multi-modal input supporting text, voice, and file uploads.
Implements modern input interface with accessibility features.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import asyncio
import threading

from ...core.events import EventBus


class InputArea(ttk.Frame):
    """
    Input Area Component - Multi-Modal Input Interface
    
    Features:
    - Text input with send button
    - Voice input with microphone button
    - File upload support
    - Keyboard shortcuts (Enter to send, Shift+Enter for new line)
    - Voice recording indicator
    - Accessibility support
    """
    
    def __init__(self, parent, event_bus: EventBus):
        """Initialize the input area."""
        super().__init__(parent)
        self.event_bus = event_bus
        self.theme = "dark"
        self.voice_recording = False
        self.live_transcription = ""
        
        # Configure grid
        self.columnconfigure(1, weight=1)
        
        # Create input components
        self._create_input_components()
        
        # Setup event handlers
        self._setup_event_handlers()
        
        # Register for voice transcription events
        self._register_voice_events()
    
    def _create_input_components(self) -> None:
        """Create the input area components."""
        # File upload button
        self.file_btn = ttk.Button(
            self,
            text="📎",
            width=3,
            command=self._handle_file_upload,
            style="Secondary.TButton"
        )
        self.file_btn.grid(row=0, column=0, padx=(0, 5), sticky="s")
        self.file_btn.configure(cursor="hand2")
        
        # Text input area
        self.input_frame = ttk.Frame(self)
        self.input_frame.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        self.input_frame.columnconfigure(0, weight=1)
        
        # Text widget with scrollbar
        self.text_input = tk.Text(
            self.input_frame,
            height=3,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            relief="solid",
            bd=1,
            padx=8,
            pady=8
        )
        self.text_input.grid(row=0, column=0, sticky="ew")
        
        # Placeholder text
        self.placeholder_text = "Type your message here... (Press Enter to send, Shift+Enter for new line)"
        self._show_placeholder()
        
        # Voice button
        self.voice_btn = ttk.Button(
            self,
            text="🎤",
            width=3,
            command=self._handle_voice_input,
            style="Secondary.TButton"
        )
        self.voice_btn.grid(row=0, column=2, padx=(0, 5), sticky="s")
        self.voice_btn.configure(cursor="hand2")
        
        # Send button
        self.send_btn = ttk.Button(
            self,
            text="Send",
            command=self._handle_send_message,
            style="Accent.TButton"
        )
        self.send_btn.grid(row=0, column=3, sticky="s")
        self.send_btn.configure(cursor="hand2")
        
        # Apply initial theme
        self._apply_theme()
    
    def _setup_event_handlers(self) -> None:
        """Setup event handlers for the input area."""
        # Text input events
        self.text_input.bind("<KeyPress>", self._on_key_press)
        self.text_input.bind("<FocusIn>", self._on_focus_in)
        self.text_input.bind("<FocusOut>", self._on_focus_out)
        self.text_input.bind("<Control-Return>", lambda e: self._handle_send_message())
        
        # Voice button events
        self.voice_btn.bind("<Button-1>", self._on_voice_click)
        self.voice_btn.bind("<ButtonRelease-1>", self._on_voice_release)
    
    def _register_voice_events(self) -> None:
        """Register voice-related event handlers."""
        # Voice transcription events
        self.event_bus.subscribe("voice.transcription.update", self._handle_live_transcription)
        self.event_bus.subscribe("voice.recording.stopped", self._handle_recording_stopped)
    
    def _apply_theme(self) -> None:
        """Apply the current theme to the input area."""
        if self.theme == "dark":
            bg_color = "#2d2d2d"
            fg_color = "#ffffff"
            input_bg = "#404040"
            input_fg = "#ffffff"
        else:
            bg_color = "#ffffff"
            fg_color = "#000000"
            input_bg = "#ffffff"
            input_fg = "#000000"
        
        # Configure text input
        self.text_input.configure(
            bg=input_bg,
            fg=input_fg,
            insertbackground=input_fg,
            selectbackground="#0078d4",
            selectforeground="white"
        )
    
    def _show_placeholder(self) -> None:
        """Show placeholder text in the input area."""
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert("1.0", self.placeholder_text)
        self.text_input.configure(fg="gray")
    
    def _hide_placeholder(self) -> None:
        """Hide placeholder text and prepare for user input."""
        if self.text_input.get("1.0", tk.END).strip() == self.placeholder_text:
            self.text_input.delete("1.0", tk.END)
            self.text_input.configure(fg="white" if self.theme == "dark" else "black")
    
    def _on_key_press(self, event) -> str:
        """Handle key press events in text input."""
        # Handle Enter key
        if event.keysym == "Return":
            if event.state & 0x1:  # Shift key pressed
                return "break"  # Allow newline
            else:
                self._handle_send_message()
                return "break"  # Prevent default newline
        
        # Handle other keys
        if event.keysym in ["BackSpace", "Delete"] or event.char.isprintable():
            self._hide_placeholder()
        
        return "continue"
    
    def _on_focus_in(self, event) -> None:
        """Handle focus in event."""
        self._hide_placeholder()
    
    def _on_focus_out(self, event) -> None:
        """Handle focus out event."""
        content = self.text_input.get("1.0", tk.END).strip()
        if not content:
            self._show_placeholder()
    
    def _on_voice_click(self, event) -> None:
        """Handle voice button click (start recording)."""
        if not self.voice_recording:
            self._start_voice_recording()
    
    def _on_voice_release(self, event) -> None:
        """Handle voice button release (stop recording)."""
        if self.voice_recording:
            self._stop_voice_recording()
    
    def _handle_send_message(self) -> None:
        """Handle sending a text message."""
        try:
            # Get message content
            content = self.text_input.get("1.0", tk.END).strip()
            
            # Skip if empty or placeholder
            if not content or content == self.placeholder_text:
                return
            
            # Clear input
            self.text_input.delete("1.0", tk.END)
            self._show_placeholder()
            
            # Emit message event
            self.event_bus.emit("ui.input.message_sent", {
                "type": "text",
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Error sending message: {e}")
    
    def _handle_file_upload(self) -> None:
        """Handle file upload."""
        try:
            # Open file dialog
            file_path = filedialog.askopenfilename(
                title="Select File to Upload",
                filetypes=[
                    ("All Files", "*.*"),
                    ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("Documents", "*.pdf *.doc *.docx *.txt *.rtf"),
                    ("Audio", "*.mp3 *.wav *.ogg *.m4a"),
                    ("Video", "*.mp4 *.avi *.mov *.wmv")
                ]
            )
            
            if file_path:
                # Emit file upload event
                self.event_bus.emit("ui.input.file_uploaded", {
                    "type": "file",
                    "file_path": file_path,
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            print(f"Error uploading file: {e}")
    
    def _handle_voice_input(self) -> None:
        """Handle voice input toggle."""
        if self.voice_recording:
            self._stop_voice_recording()
        else:
            self._start_voice_recording()
    
    def _start_voice_recording(self) -> None:
        """Start voice recording."""
        try:
            self.voice_recording = True
            self.voice_btn.configure(text="🔴", style="Recording.TButton")
            
            # Emit voice recording start event
            self.event_bus.emit("ui.input.voice_recording_started", {
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Error starting voice recording: {e}")
    
    def _stop_voice_recording(self) -> None:
        """Stop voice recording."""
        try:
            self.voice_recording = False
            self.voice_btn.configure(text="🎤", style="Secondary.TButton")
            
            # Emit voice recording stop event
            self.event_bus.emit("ui.input.voice_recording_stopped", {
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"Error stopping voice recording: {e}")
    
    def set_voice_recording(self, recording: bool) -> None:
        """Set voice recording state (called from external events)."""
        if recording != self.voice_recording:
            if recording:
                self._start_voice_recording()
            else:
                self._stop_voice_recording()
    
    def apply_theme(self, theme: str) -> None:
        """Apply a new theme to the input area."""
        self.theme = theme
        self._apply_theme()
    
    def set_text(self, text: str) -> None:
        """Set text in the input area."""
        self.text_input.delete("1.0", tk.END)
        self.text_input.insert("1.0", text)
        self.text_input.configure(fg="white" if self.theme == "dark" else "black")
    
    def get_text(self) -> str:
        """Get current text from input area."""
        content = self.text_input.get("1.0", tk.END).strip()
        return content if content != self.placeholder_text else ""
    
    def clear_text(self) -> None:
        """Clear the input area."""
        self.text_input.delete("1.0", tk.END)
        self._show_placeholder()
    
    def focus_input(self) -> None:
        """Focus the text input area."""
        self.text_input.focus_set()
    
    def _handle_live_transcription(self, data: Any = None) -> None:
        """Handle live transcription updates during voice recording."""
        if isinstance(data, dict) and self.voice_recording:
            text = data.get("text", "")
            full_transcription = data.get("full_transcription", "")
            
            # Update the input area with live transcription
            if full_transcription:
                self.set_text(full_transcription)
                
                # Add visual indicator for live transcription
                self.text_input.configure(fg="#4CAF50")  # Green for live transcription
    
    def _handle_recording_stopped(self, data: Any = None) -> None:
        """Handle voice recording stopped event."""
        if isinstance(data, dict):
            final_transcription = data.get("transcription", "")
            
            # Set final transcription and restore normal text color
            if final_transcription:
                self.set_text(final_transcription)
                self.text_input.configure(fg="white" if self.theme == "dark" else "black")
            
            # Focus input area for potential editing
            self.focus_input()
