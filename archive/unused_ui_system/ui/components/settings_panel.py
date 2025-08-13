"""
Settings Panel Component for VPA Chat UI
Comprehensive tabbed settings interface for appearance, LLM, audio, video, addons.
Implements modern settings UI with accessibility features.
"""

import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from typing import Dict, Any, List, Optional, Callable
import json
from pathlib import Path

from ...core.events import EventBus


class SettingsPanel:
    """
    Settings Panel - Comprehensive Configuration Interface
    
    Features:
    - Tabbed interface (Appearance, LLM, Audio, Video, Addons, Advanced)
    - Theme selection (Dark/Light)
    - Font size and accessibility options
    - Audio device selection and testing
    - LLM configuration and API settings
    - Addon management and marketplace
    - Advanced system settings
    """
    
    def __init__(self, parent, event_bus: EventBus):
        """Initialize the settings panel."""
        self.parent = parent
        self.event_bus = event_bus
        self.window = None
        self.theme = "dark"
        
        # Settings data
        self.settings = {
            "appearance": {
                "theme": "dark",
                "font_size": 12,
                "font_family": "Segoe UI",
                "accessibility_mode": False,
                "high_contrast": False
            },
            "llm": {
                "provider": "openai",
                "api_key": "",
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2048
            },
            "audio": {
                "input_device": "default",
                "output_device": "default",
                "voice_model": "default",
                "voice_speed": 1.0,
                "voice_enabled": True
            },
            "video": {
                "camera_device": "default",
                "resolution": "720p",
                "fps": 30,
                "enabled": False
            },
            "addons": {
                "auto_update": True,
                "startup_addons": [],
                "addon_permissions": {}
            },
            "advanced": {
                "debug_mode": False,
                "log_level": "INFO",
                "performance_monitoring": True,
                "auto_backup": True
            }
        }
        
        # Load existing settings
        self._load_settings()
    
    def show(self) -> None:
        """Show the settings panel."""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self._create_settings_window()
    
    def hide(self) -> None:
        """Hide the settings panel."""
        if self.window:
            self.window.withdraw()
    
    def _create_settings_window(self) -> None:
        """Create the main settings window."""
        # Create window
        self.window = tk.Toplevel(self.parent)
        self.window.title("VPA Settings")
        self.window.geometry("700x500")
        self.window.resizable(True, True)
        self.window.minsize(600, 400)
        
        # Apply theme
        self._apply_window_theme()
        
        # Create main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        # Create tabs
        self._create_appearance_tab()
        self._create_llm_tab()
        self._create_audio_tab()
        self._create_video_tab()
        self._create_addons_tab()
        self._create_advanced_tab()
        
        # Create button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, sticky="ew")
        
        # Buttons
        ttk.Button(
            button_frame,
            text="Apply",
            command=self._apply_settings
        ).pack(side="right", padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="OK",
            command=self._ok_settings
        ).pack(side="right", padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._cancel_settings
        ).pack(side="right")
        
        ttk.Button(
            button_frame,
            text="Reset to Defaults",
            command=self._reset_settings
        ).pack(side="left")
    
    def _create_appearance_tab(self) -> None:
        """Create the appearance settings tab."""
        tab_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(tab_frame, text="Appearance")
        
        # Theme selection
        theme_frame = ttk.LabelFrame(tab_frame, text="Theme", padding="10")
        theme_frame.pack(fill="x", pady=(0, 15))
        
        self.theme_var = tk.StringVar(value=self.settings["appearance"]["theme"])
        
        ttk.Radiobutton(
            theme_frame,
            text="Dark Theme",
            variable=self.theme_var,
            value="dark",
            command=self._preview_theme
        ).pack(anchor="w")
        
        ttk.Radiobutton(
            theme_frame,
            text="Light Theme",
            variable=self.theme_var,
            value="light",
            command=self._preview_theme
        ).pack(anchor="w")
        
        # Font settings
        font_frame = ttk.LabelFrame(tab_frame, text="Font", padding="10")
        font_frame.pack(fill="x", pady=(0, 15))
        
        # Font family
        ttk.Label(font_frame, text="Font Family:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.font_family_var = tk.StringVar(value=self.settings["appearance"]["font_family"])
        font_combo = ttk.Combobox(
            font_frame,
            textvariable=self.font_family_var,
            values=["Segoe UI", "Arial", "Calibri", "Consolas", "Times New Roman"],
            state="readonly"
        )
        font_combo.grid(row=0, column=1, sticky="ew")
        font_frame.columnconfigure(1, weight=1)
        
        # Font size
        ttk.Label(font_frame, text="Font Size:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        self.font_size_var = tk.IntVar(value=self.settings["appearance"]["font_size"])
        font_size_spin = ttk.Spinbox(
            font_frame,
            from_=8,
            to=24,
            textvariable=self.font_size_var,
            width=10
        )
        font_size_spin.grid(row=1, column=1, sticky="w", pady=(10, 0))
        
        # Accessibility options
        accessibility_frame = ttk.LabelFrame(tab_frame, text="Accessibility", padding="10")
        accessibility_frame.pack(fill="x")
        
        self.accessibility_var = tk.BooleanVar(value=self.settings["appearance"]["accessibility_mode"])
        ttk.Checkbutton(
            accessibility_frame,
            text="Enable accessibility mode (larger UI elements, high contrast)",
            variable=self.accessibility_var
        ).pack(anchor="w")
        
        self.high_contrast_var = tk.BooleanVar(value=self.settings["appearance"]["high_contrast"])
        ttk.Checkbutton(
            accessibility_frame,
            text="High contrast mode",
            variable=self.high_contrast_var
        ).pack(anchor="w")
    
    def _create_llm_tab(self) -> None:
        """Create the LLM settings tab."""
        tab_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(tab_frame, text="AI/LLM")
        
        # Provider selection
        provider_frame = ttk.LabelFrame(tab_frame, text="AI Provider", padding="10")
        provider_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(provider_frame, text="Provider:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.llm_provider_var = tk.StringVar(value=self.settings["llm"]["provider"])
        provider_combo = ttk.Combobox(
            provider_frame,
            textvariable=self.llm_provider_var,
            values=["openai", "anthropic", "google", "local", "azure"],
            state="readonly"
        )
        provider_combo.grid(row=0, column=1, sticky="ew")
        provider_frame.columnconfigure(1, weight=1)
        
        # API Key
        ttk.Label(provider_frame, text="API Key:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        self.api_key_var = tk.StringVar(value=self.settings["llm"]["api_key"])
        api_key_entry = ttk.Entry(
            provider_frame,
            textvariable=self.api_key_var,
            show="*",
            width=40
        )
        api_key_entry.grid(row=1, column=1, sticky="ew", pady=(10, 0))
        
        # Model selection
        model_frame = ttk.LabelFrame(tab_frame, text="Model Configuration", padding="10")
        model_frame.pack(fill="x", pady=(0, 15))
        
        ttk.Label(model_frame, text="Model:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.model_var = tk.StringVar(value=self.settings["llm"]["model"])
        model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=["gpt-4", "gpt-3.5-turbo", "claude-3", "gemini-pro"],
            state="readonly"
        )
        model_combo.grid(row=0, column=1, sticky="ew")
        model_frame.columnconfigure(1, weight=1)
        
        # Temperature
        ttk.Label(model_frame, text="Temperature:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        self.temperature_var = tk.DoubleVar(value=self.settings["llm"]["temperature"])
        temp_scale = ttk.Scale(
            model_frame,
            from_=0.0,
            to=2.0,
            variable=self.temperature_var,
            orient="horizontal"
        )
        temp_scale.grid(row=1, column=1, sticky="ew", pady=(10, 0))
        
        # Max tokens
        ttk.Label(model_frame, text="Max Tokens:").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        self.max_tokens_var = tk.IntVar(value=self.settings["llm"]["max_tokens"])
        tokens_spin = ttk.Spinbox(
            model_frame,
            from_=512,
            to=8192,
            textvariable=self.max_tokens_var,
            width=10
        )
        tokens_spin.grid(row=2, column=1, sticky="w", pady=(10, 0))
    
    def _create_audio_tab(self) -> None:
        """Create the audio settings tab."""
        tab_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(tab_frame, text="Audio")
        
        # Device selection
        device_frame = ttk.LabelFrame(tab_frame, text="Audio Devices", padding="10")
        device_frame.pack(fill="x", pady=(0, 15))
        
        # Input device
        ttk.Label(device_frame, text="Input Device:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.input_device_var = tk.StringVar(value=self.settings["audio"]["input_device"])
        
        # Get available microphones
        available_mics = self._get_available_microphones()
        input_combo = ttk.Combobox(
            device_frame,
            textvariable=self.input_device_var,
            values=available_mics,
            state="readonly"
        )
        input_combo.grid(row=0, column=1, sticky="ew")
        
        ttk.Button(
            device_frame,
            text="Test",
            command=self._test_input_device,
            width=8
        ).grid(row=0, column=2, padx=(10, 0))
        
        device_frame.columnconfigure(1, weight=1)
        
        # Output device
        ttk.Label(device_frame, text="Output Device:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        self.output_device_var = tk.StringVar(value=self.settings["audio"]["output_device"])
        
        # Get available output devices
        available_outputs = self._get_available_output_devices()
        output_combo = ttk.Combobox(
            device_frame,
            textvariable=self.output_device_var,
            values=available_outputs,
            state="readonly"
        )
        output_combo.grid(row=1, column=1, sticky="ew", pady=(10, 0))
        
        ttk.Button(
            device_frame,
            text="Test",
            command=self._test_output_device,
            width=8
        ).grid(row=1, column=2, padx=(10, 0), pady=(10, 0))
        
        # Voice settings
        voice_frame = ttk.LabelFrame(tab_frame, text="Voice Settings", padding="10")
        voice_frame.pack(fill="x", pady=(0, 15))
        
        # Voice enabled
        self.voice_enabled_var = tk.BooleanVar(value=self.settings["audio"]["voice_enabled"])
        ttk.Checkbutton(
            voice_frame,
            text="Enable voice responses",
            variable=self.voice_enabled_var
        ).pack(anchor="w")
        
        # Voice model
        voice_config_frame = ttk.Frame(voice_frame)
        voice_config_frame.pack(fill="x", pady=(10, 0))
        voice_config_frame.columnconfigure(1, weight=1)
        
        ttk.Label(voice_config_frame, text="Voice:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.voice_model_var = tk.StringVar(value=self.settings["audio"]["voice_model"])
        
        # Get available voices
        available_voices = self._get_available_voices()
        voice_combo = ttk.Combobox(
            voice_config_frame,
            textvariable=self.voice_model_var,
            values=available_voices,
            state="readonly"
        )
        voice_combo.grid(row=0, column=1, sticky="ew")
        
        # Voice preview button
        ttk.Button(
            voice_config_frame,
            text="Preview",
            command=self._preview_voice,
            width=8
        ).grid(row=0, column=2, padx=(10, 0))
        
        # Voice speed
        ttk.Label(voice_config_frame, text="Speed:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        self.voice_speed_var = tk.DoubleVar(value=self.settings["audio"]["voice_speed"])
        speed_scale = ttk.Scale(
            voice_config_frame,
            from_=0.5,
            to=2.0,
            variable=self.voice_speed_var,
            orient="horizontal"
        )
        speed_scale.grid(row=1, column=1, sticky="ew", pady=(10, 0))
        
        # Speed label
        speed_label = ttk.Label(voice_config_frame, text="1.0x")
        speed_label.grid(row=1, column=2, padx=(10, 0), pady=(10, 0))
        
        # Update speed label when scale changes
        def update_speed_label(*args):
            speed_label.configure(text=f"{self.voice_speed_var.get():.1f}x")
        
        self.voice_speed_var.trace("w", update_speed_label)
        
        # Voice calibration section
        calibration_frame = ttk.LabelFrame(tab_frame, text="Voice Calibration", padding="10")
        calibration_frame.pack(fill="x", pady=(0, 15))
        
        # Microphone calibration
        ttk.Label(calibration_frame, text="Microphone Sensitivity:").pack(anchor="w")
        self.mic_sensitivity_var = tk.DoubleVar(value=0.5)
        ttk.Scale(
            calibration_frame,
            from_=0.1,
            to=1.0,
            variable=self.mic_sensitivity_var,
            orient="horizontal"
        ).pack(fill="x", pady=(5, 10))
        
        # Calibration buttons
        button_frame = ttk.Frame(calibration_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(
            button_frame,
            text="Auto Calibrate",
            command=self._auto_calibrate_microphone
        ).pack(side="left", padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="Test Recording",
            command=self._test_recording
        ).pack(side="left")
    
    def _create_video_tab(self) -> None:
        """Create the video settings tab."""
        tab_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(tab_frame, text="Video")
        
        # Video settings (placeholder for future implementation)
        info_label = ttk.Label(
            tab_frame,
            text="Video features will be available in a future update.",
            font=("Segoe UI", 11),
            foreground="gray"
        )
        info_label.pack(pady=50)
    
    def _create_addons_tab(self) -> None:
        """Create the addons management tab."""
        tab_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(tab_frame, text="Addons")
        
        # Addon management will be implemented in separate component
        addon_label = ttk.Label(
            tab_frame,
            text="Addon management interface",
            font=("Segoe UI", 12, "bold")
        )
        addon_label.pack(pady=20)
        
        # Open addon manager button
        ttk.Button(
            tab_frame,
            text="Open Addon Manager",
            command=self._open_addon_manager
        ).pack(pady=10)
    
    def _create_advanced_tab(self) -> None:
        """Create the advanced settings tab."""
        tab_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(tab_frame, text="Advanced")
        
        # Debug settings
        debug_frame = ttk.LabelFrame(tab_frame, text="Debug & Logging", padding="10")
        debug_frame.pack(fill="x", pady=(0, 15))
        
        self.debug_mode_var = tk.BooleanVar(value=self.settings["advanced"]["debug_mode"])
        ttk.Checkbutton(
            debug_frame,
            text="Enable debug mode",
            variable=self.debug_mode_var
        ).pack(anchor="w")
        
        # Log level
        log_frame = ttk.Frame(debug_frame)
        log_frame.pack(fill="x", pady=(10, 0))
        log_frame.columnconfigure(1, weight=1)
        
        ttk.Label(log_frame, text="Log Level:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.log_level_var = tk.StringVar(value=self.settings["advanced"]["log_level"])
        log_combo = ttk.Combobox(
            log_frame,
            textvariable=self.log_level_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            state="readonly"
        )
        log_combo.grid(row=0, column=1, sticky="ew")
        
        # Performance settings
        perf_frame = ttk.LabelFrame(tab_frame, text="Performance", padding="10")
        perf_frame.pack(fill="x", pady=(0, 15))
        
        self.perf_monitoring_var = tk.BooleanVar(value=self.settings["advanced"]["performance_monitoring"])
        ttk.Checkbutton(
            perf_frame,
            text="Enable performance monitoring",
            variable=self.perf_monitoring_var
        ).pack(anchor="w")
        
        # Backup settings
        backup_frame = ttk.LabelFrame(tab_frame, text="Backup", padding="10")
        backup_frame.pack(fill="x")
        
        self.auto_backup_var = tk.BooleanVar(value=self.settings["advanced"]["auto_backup"])
        ttk.Checkbutton(
            backup_frame,
            text="Enable automatic backups",
            variable=self.auto_backup_var
        ).pack(anchor="w")
    
    def _apply_window_theme(self) -> None:
        """Apply theme to the settings window."""
        if self.theme == "dark":
            self.window.configure(bg="#2d2d2d")
        else:
            self.window.configure(bg="#ffffff")
    
    def _preview_theme(self) -> None:
        """Preview theme changes."""
        new_theme = self.theme_var.get()
        # Emit preview event
        self.event_bus.emit("ui.settings.theme_preview", {
            "theme": new_theme
        })
    
    def _test_input_device(self) -> None:
        """Test the selected input device."""
        device = self.input_device_var.get()
        messagebox.showinfo("Audio Test", f"Testing input device: {device}\nSpeak into your microphone...")
        # Emit test event
        self.event_bus.emit("audio.test_input_device", {
            "device": device
        })
    
    def _test_output_device(self) -> None:
        """Test the selected output device."""
        device = self.output_device_var.get()
        # Emit test event
        self.event_bus.emit("audio.test_output_device", {
            "device": device,
            "message": "This is a test of your audio output device."
        })
    
    def _open_addon_manager(self) -> None:
        """Open the addon manager."""
        self.event_bus.emit("ui.open_addon_manager", {})
    
    def _apply_settings(self) -> None:
        """Apply the current settings."""
        try:
            # Update settings from UI
            self._update_settings_from_ui()
            
            # Save settings
            self._save_settings()
            
            # Emit settings changed events
            self._emit_settings_events()
            
            messagebox.showinfo("Settings", "Settings applied successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply settings: {e}")
    
    def _ok_settings(self) -> None:
        """Apply settings and close window."""
        self._apply_settings()
        self.window.destroy()
    
    def _cancel_settings(self) -> None:
        """Cancel changes and close window."""
        self.window.destroy()
    
    def _reset_settings(self) -> None:
        """Reset settings to defaults."""
        result = messagebox.askyesno(
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?"
        )
        
        if result:
            # Reset to defaults
            self._load_default_settings()
            self._update_ui_from_settings()
    
    def _update_settings_from_ui(self) -> None:
        """Update settings dictionary from UI elements."""
        # Appearance settings
        self.settings["appearance"]["theme"] = self.theme_var.get()
        self.settings["appearance"]["font_size"] = self.font_size_var.get()
        self.settings["appearance"]["font_family"] = self.font_family_var.get()
        self.settings["appearance"]["accessibility_mode"] = self.accessibility_var.get()
        self.settings["appearance"]["high_contrast"] = self.high_contrast_var.get()
        
        # LLM settings
        self.settings["llm"]["provider"] = self.llm_provider_var.get()
        self.settings["llm"]["api_key"] = self.api_key_var.get()
        self.settings["llm"]["model"] = self.model_var.get()
        self.settings["llm"]["temperature"] = self.temperature_var.get()
        self.settings["llm"]["max_tokens"] = self.max_tokens_var.get()
        
        # Audio settings
        self.settings["audio"]["input_device"] = self.input_device_var.get()
        self.settings["audio"]["output_device"] = self.output_device_var.get()
        self.settings["audio"]["voice_model"] = self.voice_model_var.get()
        self.settings["audio"]["voice_speed"] = self.voice_speed_var.get()
        self.settings["audio"]["voice_enabled"] = self.voice_enabled_var.get()
        
        # Advanced settings
        self.settings["advanced"]["debug_mode"] = self.debug_mode_var.get()
        self.settings["advanced"]["log_level"] = self.log_level_var.get()
        self.settings["advanced"]["performance_monitoring"] = self.perf_monitoring_var.get()
        self.settings["advanced"]["auto_backup"] = self.auto_backup_var.get()
    
    def _update_ui_from_settings(self) -> None:
        """Update UI elements from settings dictionary."""
        # This would update all UI elements with current settings
        # Implementation needed when UI is created
        pass
    
    def _emit_settings_events(self) -> None:
        """Emit events for settings changes."""
        self.event_bus.emit("ui.settings.theme_changed", {
            "theme": self.settings["appearance"]["theme"]
        })
        
        self.event_bus.emit("ui.settings.font_changed", {
            "size": self.settings["appearance"]["font_size"],
            "family": self.settings["appearance"]["font_family"]
        })
        
        self.event_bus.emit("audio.settings_changed", {
            "settings": self.settings["audio"]
        })
    
    def _load_settings(self) -> None:
        """Load settings from file."""
        try:
            settings_path = Path("config/ui_settings.json")
            if settings_path.exists():
                with open(settings_path, 'r') as f:
                    saved_settings = json.load(f)
                    # Merge with defaults
                    for category, values in saved_settings.items():
                        if category in self.settings:
                            self.settings[category].update(values)
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def _save_settings(self) -> None:
        """Save settings to file."""
        try:
            settings_path = Path("config/ui_settings.json")
            settings_path.parent.mkdir(exist_ok=True)
            
            with open(settings_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
                
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def _load_default_settings(self) -> None:
        """Load default settings."""
        # Settings are already initialized with defaults
        pass
