"""
Addon Panel Component for VPA Chat UI
Addon marketplace and management interface.
Implements addon discovery, activation, and configuration.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List, Optional

from ...core.events import EventBus


class AddonPanel:
    """
    Addon Panel - Addon Management and Marketplace
    
    Features:
    - Available addons display
    - Addon activation/deactivation
    - Addon configuration
    - Marketplace integration
    - Status monitoring
    """
    
    def __init__(self, parent, event_bus: EventBus):
        """Initialize the addon panel."""
        self.parent = parent
        self.event_bus = event_bus
        self.window = None
        self.theme = "dark"
        
        # Addon data
        self.available_addons = {}
        self.active_addons = {}
        
        # Request initial addon data
        self._request_addon_data()
    
    def show(self) -> None:
        """Show the addon panel."""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self._create_addon_window()
    
    def _create_addon_window(self) -> None:
        """Create the addon management window."""
        # Create window
        self.window = tk.Toplevel(self.parent)
        self.window.title("VPA Addon Manager")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        # Create main container
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill="both", expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Addon Manager",
            font=("Segoe UI", 16, "bold")
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Create addon list
        self._create_addon_list(main_frame)
        
        # Create button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        ttk.Button(
            button_frame,
            text="Refresh",
            command=self._refresh_addons
        ).pack(side="left")
        
        ttk.Button(
            button_frame,
            text="Close",
            command=self.window.destroy
        ).pack(side="right")
    
    def _create_addon_list(self, parent) -> None:
        """Create the addon list interface."""
        # Create notebook for different views
        notebook = ttk.Notebook(parent)
        notebook.grid(row=1, column=0, sticky="nsew")
        
        # Available addons tab
        available_frame = ttk.Frame(notebook)
        notebook.add(available_frame, text="Available Addons")
        self._create_available_addons_view(available_frame)
        
        # Active addons tab
        active_frame = ttk.Frame(notebook)
        notebook.add(active_frame, text="Active Addons")
        self._create_active_addons_view(active_frame)
    
    def _create_available_addons_view(self, parent) -> None:
        """Create the available addons view."""
        # Placeholder for available addons
        label = ttk.Label(
            parent,
            text="Available addons will be displayed here",
            font=("Segoe UI", 11),
            foreground="gray"
        )
        label.pack(expand=True)
    
    def _create_active_addons_view(self, parent) -> None:
        """Create the active addons view."""
        # Placeholder for active addons
        label = ttk.Label(
            parent,
            text="Active addons will be displayed here",
            font=("Segoe UI", 11),
            foreground="gray"
        )
        label.pack(expand=True)
    
    def _request_addon_data(self) -> None:
        """Request addon data from the system."""
        self.event_bus.emit("addon.manager.request_status", {})
    
    def _refresh_addons(self) -> None:
        """Refresh addon data."""
        self._request_addon_data()
        messagebox.showinfo("Refresh", "Addon data refreshed!")
