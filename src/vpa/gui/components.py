"""
VPA GUI Components
Reusable GUI components for VPA Virtual Personal Assistant
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional, Callable


class VPAComponents:
    """Collection of reusable VPA GUI components"""
    
    @staticmethod
    def create_status_indicator(parent: tk.Widget, text: str, status: str = "unknown") -> ttk.Label:
        """Create a status indicator with color coding"""
        colors = {
            "ready": "green",
            "running": "green", 
            "warning": "orange",
            "error": "red",
            "unknown": "gray"
        }
        
        # Create label with text
        label = ttk.Label(parent, text=text)
        
        # Configure color - use style for ttk compatibility
        try:
            color = colors.get(status, "gray")
            style = ttk.Style()
            style_name = f"Status_{status}.TLabel"
            style.configure(style_name, foreground=color)
            label.configure(style=style_name)
        except Exception:
            # Fallback for test environments - try direct foreground
            try:
                label.configure(foreground=colors.get(status, "gray"))
            except Exception:
                pass
            
        return label
    
    @staticmethod
    def create_info_frame(parent: tk.Widget, title: str, info_dict: Dict[str, str]) -> ttk.LabelFrame:
        """Create an information display frame"""
        frame = ttk.LabelFrame(parent, text=title, padding="5")
        
        row = 0
        for key, value in info_dict.items():
            ttk.Label(frame, text=f"{key}:").grid(row=row, column=0, sticky="w", padx=(0, 5))
            ttk.Label(frame, text=value).grid(row=row, column=1, sticky="w")
            row += 1
        
        return frame
    
    @staticmethod
    def create_button_group(parent: tk.Widget, buttons: Dict[str, Callable]) -> ttk.Frame:
        """Create a group of buttons"""
        frame = ttk.Frame(parent)
        
        col = 0
        for text, command in buttons.items():
            btn = ttk.Button(frame, text=text, command=command)
            btn.grid(row=0, column=col, padx=(0, 5) if col > 0 else 0)
            col += 1
        
        return frame


class VPADialog:
    """Base class for VPA dialog windows"""
    
    def __init__(self, parent: tk.Widget, title: str, size: tuple = (400, 300)):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry(f"{size[0]}x{size[1]}")
        if hasattr(parent, 'winfo_toplevel'):
            self.dialog.transient(parent.winfo_toplevel())
        self.dialog.grab_set()
        
        # Center the dialog
        self._center_dialog()
        
        self.result = None
    
    def _center_dialog(self) -> None:
        """Center the dialog on the parent window"""
        self.dialog.update_idletasks()
        x = (self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 
             (self.dialog.winfo_width() // 2))
        y = (self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 
             (self.dialog.winfo_height() // 2))
        self.dialog.geometry(f"+{x}+{y}")
    
    def destroy(self) -> None:
        """Destroy the dialog"""
        self.dialog.destroy()


class VPAProgressDialog(VPADialog):
    """Progress dialog for long-running operations"""
    
    def __init__(self, parent: tk.Widget, title: str, message: str):
        super().__init__(parent, title, (300, 150))
        
        # Create progress UI
        self.message_label = ttk.Label(self.dialog, text=message)
        self.message_label.pack(pady=20)
        
        self.progress_bar = ttk.Progressbar(self.dialog, mode='indeterminate')
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 20))
        self.progress_bar.start()
        
        self.cancel_button = ttk.Button(self.dialog, text="Cancel", command=self.destroy)
        self.cancel_button.pack(pady=(0, 10))
    
    def update_message(self, message: str) -> None:
        """Update the progress message"""
        self.message_label.config(text=message)
        self.dialog.update()
    
    def set_progress(self, value: int) -> None:
        """Set progress bar value (0-100)"""
        self.progress_bar.config(mode='determinate')
        self.progress_bar['value'] = value
        self.dialog.update()


class VPASettingsDialog(VPADialog):
    """Settings configuration dialog"""
    
    def __init__(self, parent: tk.Widget, current_settings: Dict[str, Any], app=None):
        super().__init__(parent, "VPA Settings", (600, 500))
        
        self.settings = current_settings.copy()
        self.app = app  # Add reference to app for plugin access
        self.setting_vars = {}  # Store tkinter variables for settings
        self._create_settings_ui()
    
    def _create_settings_ui(self) -> None:
        """Create the settings UI"""
        # Main frame
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Notebook for different setting categories
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 10))
        
        # Create settings tabs
        self._create_general_tab(notebook)
        self._create_ai_tab(notebook)
        self._create_audio_tab(notebook)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="OK", command=self._on_ok).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side="right")
        ttk.Button(button_frame, text="Apply", command=self._on_apply).pack(side="right", padx=(0, 5))
    
    def _create_general_tab(self, notebook: ttk.Notebook) -> None:
        """Create general settings tab"""
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="General")
        
        # Application settings group
        app_group = ttk.LabelFrame(general_frame, text="Application Settings", padding="10")
        app_group.pack(fill="x", padx=5, pady=5)
        
        # Log level setting
        ttk.Label(app_group, text="Log Level:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        log_var = tk.StringVar(value=self.settings.get("core", {}).get("log_level", "INFO"))
        self.setting_vars["core.log_level"] = log_var
        log_combo = ttk.Combobox(app_group, textvariable=log_var, values=["DEBUG", "INFO", "WARNING", "ERROR"], state="readonly")
        log_combo.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        app_group.columnconfigure(1, weight=1)
        
        # Startup settings group
        startup_group = ttk.LabelFrame(general_frame, text="Startup Settings", padding="10")
        startup_group.pack(fill="x", padx=5, pady=5)
        
        # Auto-start plugins
        auto_start_var = tk.BooleanVar(value=self.settings.get("plugins", {}).get("auto_start", True))
        self.setting_vars["plugins.auto_start"] = auto_start_var
        ttk.Checkbutton(startup_group, text="Auto-start plugins on application launch", 
                       variable=auto_start_var).pack(anchor="w")
    
    def _create_ai_tab(self, notebook: ttk.Notebook) -> None:
        """Create AI system settings tab"""
        ai_frame = ttk.Frame(notebook)
        notebook.add(ai_frame, text="AI System")
        
        # AI Engine settings group
        ai_group = ttk.LabelFrame(ai_frame, text="AI Engine Settings", padding="10")
        ai_group.pack(fill="x", padx=5, pady=5)
        
        # AI system enabled
        ai_enabled_var = tk.BooleanVar(value=self.settings.get("ai", {}).get("enabled", True))
        self.setting_vars["ai.enabled"] = ai_enabled_var
        ttk.Checkbutton(ai_group, text="Enable AI system", variable=ai_enabled_var).pack(anchor="w")
        
        # Response settings group
        response_group = ttk.LabelFrame(ai_frame, text="Response Settings", padding="10")
        response_group.pack(fill="x", padx=5, pady=5)
        
        # Max response length
        ttk.Label(response_group, text="Max Response Length:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        max_length_var = tk.IntVar(value=self.settings.get("ai", {}).get("max_response_length", 1000))
        self.setting_vars["ai.max_response_length"] = max_length_var
        ttk.Spinbox(response_group, from_=100, to=5000, increment=100, textvariable=max_length_var, width=10).grid(row=0, column=1, sticky="w")
        response_group.columnconfigure(1, weight=1)
    
    def _create_audio_tab(self, notebook: ttk.Notebook) -> None:
        """Create audio settings tab"""
        audio_frame = ttk.Frame(notebook)
        notebook.add(audio_frame, text="Audio")
        
        # Audio Engine settings group
        audio_group = ttk.LabelFrame(audio_frame, text="Audio Engine Settings", padding="10")
        audio_group.pack(fill="x", padx=5, pady=5)
        
        # Audio enabled
        audio_enabled_var = tk.BooleanVar(value=self.settings.get("audio", {}).get("enabled", True))
        self.setting_vars["audio.enabled"] = audio_enabled_var
        ttk.Checkbutton(audio_group, text="Enable audio system", variable=audio_enabled_var).pack(anchor="w")
        
        # Voice settings group
        voice_group = ttk.LabelFrame(audio_frame, text="Voice Settings", padding="10")
        voice_group.pack(fill="x", padx=5, pady=5)
        
        # Default voice
        ttk.Label(voice_group, text="Default Voice:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        default_voice_var = tk.StringVar(value=self.settings.get("audio", {}).get("default_voice", "voice_01"))
        self.setting_vars["audio.default_voice"] = default_voice_var
        
        # Get available voices from audio plugin if available
        voice_options = ["voice_01", "voice_02", "voice_03", "voice_04", "voice_05"]
        if self.app and hasattr(self.app, 'plugin_manager'):
            try:
                audio_plugin = self.app.plugin_manager.get_plugin('audio')
                if audio_plugin and hasattr(audio_plugin, 'audio_engine'):
                    available_voices = audio_plugin.audio_engine.get_available_voices()
                    voice_options = [voice.voice_id for voice in available_voices]
            except Exception:
                pass  # Use default voice options
        
        voice_combo = ttk.Combobox(voice_group, textvariable=default_voice_var, values=voice_options, state="readonly")
        voice_combo.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        voice_group.columnconfigure(1, weight=1)
        
        # Default speech rate
        ttk.Label(voice_group, text="Speech Rate (WPM):").grid(row=1, column=0, sticky="w", padx=(0, 5))
        rate_var = tk.IntVar(value=self.settings.get("audio", {}).get("default_rate", 200))
        self.setting_vars["audio.default_rate"] = rate_var
        ttk.Spinbox(voice_group, from_=50, to=400, increment=10, textvariable=rate_var, width=10).grid(row=1, column=1, sticky="w")
        
        # Default volume
        ttk.Label(voice_group, text="Volume (0.0-1.0):").grid(row=2, column=0, sticky="w", padx=(0, 5))
        volume_var = tk.DoubleVar(value=self.settings.get("audio", {}).get("default_volume", 0.9))
        self.setting_vars["audio.default_volume"] = volume_var
        ttk.Spinbox(voice_group, from_=0.0, to=1.0, increment=0.1, textvariable=volume_var, width=10, format="%.1f").grid(row=2, column=1, sticky="w")
    
    def _on_ok(self) -> None:
        """Handle OK button click"""
        self._on_apply()
        self.destroy()
    
    def _on_apply(self) -> None:
        """Handle Apply button click - Apply settings to the application"""
        try:
            # Collect all settings from UI
            updated_settings = {}
            for key, var in self.setting_vars.items():
                # Split nested keys (e.g., "core.log_level" -> ["core", "log_level"])
                key_parts = key.split('.')
                current_dict = updated_settings
                
                # Navigate/create nested structure
                for part in key_parts[:-1]:
                    if part not in current_dict:
                        current_dict[part] = {}
                    current_dict = current_dict[part]
                
                # Set the value
                current_dict[key_parts[-1]] = var.get()
            
            # Apply settings to the application configuration
            if self.app and hasattr(self.app, 'config_manager'):
                # Update configuration
                for key, var in self.setting_vars.items():
                    self.app.config_manager.set(key, var.get())
                
                # Save configuration to file
                self.app.config_manager.save()
                
                # Apply audio settings immediately if audio plugin is available
                self._apply_audio_settings_immediately()
                
                # Emit settings changed event
                if hasattr(self.app, 'event_bus'):
                    self.app.event_bus.emit("settings.changed", updated_settings)
                
                # Show success message
                messagebox.showinfo("Settings Applied", 
                                   "Settings have been applied successfully!")
            else:
                # Fallback: just update internal settings
                for key_path, value in self._flatten_settings(updated_settings).items():
                    self._set_nested_value(self.settings, key_path, value)
                
                messagebox.showinfo("Settings Applied", 
                                   "Settings have been applied (application restart may be required)!")
                
        except Exception as e:
            messagebox.showerror("Settings Error", 
                               f"Error applying settings: {str(e)}")
    
    def _apply_audio_settings_immediately(self) -> None:
        """Apply audio settings to the audio engine immediately"""
        try:
            if not self.app or not hasattr(self.app, 'plugin_manager'):
                return
                
            audio_plugin = self.app.plugin_manager.get_plugin('audio')
            if not audio_plugin or not hasattr(audio_plugin, 'audio_engine'):
                return
            
            # Apply voice settings
            default_voice = self.setting_vars.get("audio.default_voice", tk.StringVar()).get()
            if default_voice:
                audio_plugin.audio_engine.set_voice(default_voice)
            
            # Apply voice properties if current voice is available
            if audio_plugin.audio_engine.current_voice:
                voice_id = audio_plugin.audio_engine.current_voice.voice_id
                
                rate = self.setting_vars.get("audio.default_rate", tk.IntVar()).get()
                volume = self.setting_vars.get("audio.default_volume", tk.DoubleVar()).get()
                
                if rate:
                    audio_plugin.audio_engine.set_voice_property(voice_id, "rate", rate)
                if volume:
                    audio_plugin.audio_engine.set_voice_property(voice_id, "volume", volume)
        
        except Exception as e:
            # Log error but don't interrupt settings application
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error applying audio settings immediately: {e}")
    
    def _flatten_settings(self, settings: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """Flatten nested settings dictionary"""
        result = {}
        for key, value in settings.items():
            new_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                result.update(self._flatten_settings(value, new_key))
            else:
                result[new_key] = value
        return result
    
    def _set_nested_value(self, dictionary: Dict[str, Any], key_path: str, value: Any) -> None:
        """Set a nested value in a dictionary using dot notation"""
        keys = key_path.split('.')
        current = dictionary
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
