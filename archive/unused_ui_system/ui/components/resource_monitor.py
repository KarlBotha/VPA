"""
Resource Monitor Component for VPA Chat UI
Displays live resource usage (CPU, RAM, GPU, storage) with user control.
Implements compact monitoring widget with approval/denial interface.
Integrates with VPA Resource Monitoring Service per VPA_APP_FINAL_OVERVIEW.md.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional, List
import threading
import time

from ...core.events import EventBus


class ResourceMonitor(ttk.Frame):
    """
    Resource Monitor Component - Live Resource Usage Display
    
    Features:
    - Real-time CPU, RAM, GPU, storage monitoring
    - Compact display in top-left corner
    - User approval/denial for resource actions (per master architecture)
    - Color-coded warnings (green/yellow/red)
    - Clickable for detailed view
    - Theme support
    - Integration with Resource Monitoring Service
    """
    
    def __init__(self, parent, event_bus: EventBus):
        """Initialize the resource monitor."""
        super().__init__(parent)
        self.event_bus = event_bus
        self.theme = "dark"
        
        # Resource data
        self.resource_data = {
            "cpu": 0.0,
            "memory": 0.0,
            "gpu": 0.0,
            "storage": 0.0
        }
        
        # Pending user actions and alerts
        self.pending_approvals: Dict[str, Any] = {}
        self.active_alerts: List[Dict[str, Any]] = []
        
        # Create monitor interface
        self._create_monitor_interface()
        
        # Setup auto-refresh
        self._setup_auto_refresh()
        
        # Register for resource monitoring events
        self._register_event_handlers()
        
        # Apply initial theme
        self._apply_theme()
    
    def _register_event_handlers(self) -> None:
        """Register for resource monitoring service events."""
        self.event_bus.subscribe("resource.monitor.updated", self._handle_resource_update)
        self.event_bus.subscribe("resource.monitor.alert", self._handle_resource_alert)
        self.event_bus.subscribe("resource.monitor.approval_required", self._handle_approval_required)
        self.event_bus.subscribe("resource.monitor.alert_cleared", self._handle_alert_cleared)
    
    def _create_monitor_interface(self) -> None:
        """Create the resource monitor interface."""
        # Main monitor frame with border
        self.monitor_frame = tk.Frame(
            self,
            relief="solid",
            bd=1,
            padx=8,
            pady=6
        )
        self.monitor_frame.pack(fill="both", expand=True)
        
        # Title
        self.title_label = tk.Label(
            self.monitor_frame,
            text="🖥️ Resources",
            font=("Segoe UI", 10, "bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=2, sticky="w")
        
        # CPU usage
        self.cpu_label = tk.Label(
            self.monitor_frame,
            text="CPU:",
            font=("Segoe UI", 9)
        )
        self.cpu_label.grid(row=1, column=0, sticky="w")
        
        self.cpu_value = tk.Label(
            self.monitor_frame,
            text="0%",
            font=("Segoe UI", 9, "bold"),
            fg="#00ff00"  # Green by default
        )
        self.cpu_value.grid(row=1, column=1, sticky="e")
        
        # Memory usage
        self.memory_label = tk.Label(
            self.monitor_frame,
            text="RAM:",
            font=("Segoe UI", 9)
        )
        self.memory_label.grid(row=2, column=0, sticky="w")
        
        self.memory_value = tk.Label(
            self.monitor_frame,
            text="0%",
            font=("Segoe UI", 9, "bold"),
            fg="#00ff00"
        )
        self.memory_value.grid(row=2, column=1, sticky="e")
        
        # GPU usage (if available)
        self.gpu_label = tk.Label(
            self.monitor_frame,
            text="GPU:",
            font=("Segoe UI", 9)
        )
        self.gpu_label.grid(row=3, column=0, sticky="w")
        
        self.gpu_value = tk.Label(
            self.monitor_frame,
            text="N/A",
            font=("Segoe UI", 9, "bold"),
            fg="#888888"
        )
        self.gpu_value.grid(row=3, column=1, sticky="e")
        
        # Storage usage
        self.storage_label = tk.Label(
            self.monitor_frame,
            text="Disk:",
            font=("Segoe UI", 9)
        )
        self.storage_label.grid(row=4, column=0, sticky="w")
        
        self.storage_value = tk.Label(
            self.monitor_frame,
            text="0%",
            font=("Segoe UI", 9, "bold"),
            fg="#00ff00"
        )
        self.storage_value.grid(row=4, column=1, sticky="e")
        
        # Action button (hidden by default)
        self.action_btn = tk.Button(
            self.monitor_frame,
            text="⚠️ Action Required",
            font=("Segoe UI", 8),
            command=self._handle_user_action,
            relief="flat"
        )
        # Initially hidden
        
        # Bind click for detailed view
        self.monitor_frame.bind("<Button-1>", self._show_detailed_view)
        self.title_label.bind("<Button-1>", self._show_detailed_view)
    
    def _apply_theme(self) -> None:
        """Apply the current theme to the resource monitor."""
        if self.theme == "dark":
            bg_color = "#2d2d2d"
            fg_color = "#ffffff"
            border_color = "#404040"
        else:
            bg_color = "#f0f0f0"
            fg_color = "#000000"
            border_color = "#cccccc"
        
        # Configure colors
        self.monitor_frame.configure(bg=bg_color, highlightbackground=border_color)
        self.title_label.configure(bg=bg_color, fg=fg_color)
        self.cpu_label.configure(bg=bg_color, fg=fg_color)
        self.memory_label.configure(bg=bg_color, fg=fg_color)
        self.gpu_label.configure(bg=bg_color, fg=fg_color)
        self.storage_label.configure(bg=bg_color, fg=fg_color)
    
    def _setup_auto_refresh(self) -> None:
        """Setup automatic resource data refresh."""
        def refresh_resources():
            try:
                # Request updated resource data
                self.event_bus.emit("resource.monitor.request_update", {
                    "timestamp": time.time()
                })
            except Exception as e:
                print(f"Error requesting resource update: {e}")
            
            # Schedule next refresh
            self.after(2000, refresh_resources)  # Every 2 seconds
        
        # Start auto-refresh
        self.after(1000, refresh_resources)  # First refresh after 1 second
    
    def update_resources(self, data: Dict[str, Any]) -> None:
        """
        Update resource display with new data.
        
        Args:
            data: Resource data dict with cpu, memory, gpu, storage percentages
        """
        try:
            # Update stored data
            self.resource_data.update(data)
            
            # Update CPU
            cpu_percent = data.get("cpu", 0.0)
            self.cpu_value.configure(
                text=f"{cpu_percent:.1f}%",
                fg=self._get_usage_color(cpu_percent)
            )
            
            # Update Memory
            memory_percent = data.get("memory", 0.0)
            self.memory_value.configure(
                text=f"{memory_percent:.1f}%",
                fg=self._get_usage_color(memory_percent)
            )
            
            # Update GPU
            gpu_percent = data.get("gpu")
            if gpu_percent is not None:
                self.gpu_value.configure(
                    text=f"{gpu_percent:.1f}%",
                    fg=self._get_usage_color(gpu_percent)
                )
            else:
                self.gpu_value.configure(text="N/A", fg="#888888")
            
            # Update Storage
            storage_percent = data.get("storage", 0.0)
            self.storage_value.configure(
                text=f"{storage_percent:.1f}%",
                fg=self._get_usage_color(storage_percent)
            )
            
            # Check for warnings
            self._check_resource_warnings(data)
            
        except Exception as e:
            print(f"Error updating resource monitor: {e}")
    
    def _get_usage_color(self, percent: float) -> str:
        """Get color based on usage percentage."""
        if percent >= 90:
            return "#ff4444"  # Red - Critical
        elif percent >= 75:
            return "#ffaa00"  # Orange - Warning
        elif percent >= 50:
            return "#ffff00"  # Yellow - Moderate
        else:
            return "#00ff00"  # Green - Good
    
    def _check_resource_warnings(self, data: Dict[str, Any]) -> None:
        """Check for resource warnings and show action button if needed."""
        high_usage = []
        
        for resource, percent in data.items():
            if isinstance(percent, (int, float)) and percent >= 85:
                high_usage.append(f"{resource.upper()}: {percent:.1f}%")
        
        if high_usage:
            # Show action button
            self.action_btn.grid(row=5, column=0, columnspan=2, pady=(5, 0), sticky="ew")
            self.action_btn.configure(
                text=f"⚠️ High Usage: {', '.join(high_usage[:2])}",
                bg="#ffaa00",
                fg="#000000"
            )
        else:
            # Hide action button
            self.action_btn.grid_remove()
    
    def _handle_user_action(self) -> None:
        """Handle user action for resource management."""
        try:
            # Show resource management dialog
            result = messagebox.askyesnocancel(
                "Resource Management",
                "High resource usage detected. Would you like VPA to:\n\n"
                "• YES: Automatically optimize (deactivate some addons)\n"
                "• NO: Continue monitoring without changes\n"
                "• CANCEL: Show detailed resource information",
                icon="warning"
            )
            
            if result is True:
                # User approved optimization
                self.event_bus.emit("resource.monitor.optimize_approved", {
                    "user_approved": True,
                    "timestamp": time.time()
                })
                
                # Hide action button temporarily
                self.action_btn.grid_remove()
                
            elif result is False:
                # User declined optimization
                self.event_bus.emit("resource.monitor.optimize_declined", {
                    "user_declined": True,
                    "timestamp": time.time()
                })
                
                # Hide action button
                self.action_btn.grid_remove()
                
            else:
                # User wants detailed view
                self._show_detailed_view()
            
        except Exception as e:
            print(f"Error handling user action: {e}")
    
    def _show_detailed_view(self, event=None) -> None:
        """Show detailed resource information."""
        try:
            # Create detailed view window
            detail_window = tk.Toplevel(self)
            detail_window.title("VPA Resource Monitor - Detailed View")
            detail_window.geometry("400x300")
            detail_window.resizable(False, False)
            
            # Apply theme
            if self.theme == "dark":
                detail_window.configure(bg="#2d2d2d")
            
            # Content frame
            content_frame = ttk.Frame(detail_window, padding="20")
            content_frame.pack(fill="both", expand=True)
            
            # Title
            title_label = ttk.Label(
                content_frame,
                text="Resource Usage Details",
                font=("Segoe UI", 14, "bold")
            )
            title_label.pack(pady=(0, 20))
            
            # Resource details
            for resource, percent in self.resource_data.items():
                if isinstance(percent, (int, float)):
                    frame = ttk.Frame(content_frame)
                    frame.pack(fill="x", pady=5)
                    
                    label = ttk.Label(
                        frame,
                        text=f"{resource.upper()}:",
                        font=("Segoe UI", 11)
                    )
                    label.pack(side="left")
                    
                    value = ttk.Label(
                        frame,
                        text=f"{percent:.1f}%",
                        font=("Segoe UI", 11, "bold")
                    )
                    value.pack(side="right")
                    
                    # Progress bar
                    progress = ttk.Progressbar(
                        frame,
                        length=200,
                        value=percent,
                        maximum=100
                    )
                    progress.pack(side="right", padx=(10, 10))
            
            # Close button
            close_btn = ttk.Button(
                content_frame,
                text="Close",
                command=detail_window.destroy
            )
            close_btn.pack(pady=(20, 0))
            
        except Exception as e:
            print(f"Error showing detailed view: {e}")
    
    def apply_theme(self, theme: str) -> None:
        """Apply a new theme to the resource monitor."""
        self.theme = theme
        self._apply_theme()
    
    def show_action_required(self, message: str) -> None:
        """Show action required button with custom message."""
        self.action_btn.configure(text=f"⚠️ {message}")
        self.action_btn.grid(row=5, column=0, columnspan=2, pady=(5, 0), sticky="ew")
    
    def hide_action_button(self) -> None:
        """Hide the action required button."""
        self.action_btn.grid_remove()
    
    # Event Handlers for Resource Monitoring Service Integration
    
    def _handle_resource_update(self, event_data: Dict[str, Any]) -> None:
        """Handle resource update from monitoring service."""
        try:
            metrics = event_data.get("metrics", {})
            self.update_resources({
                "cpu": metrics.get("cpu_percent", 0.0),
                "memory": metrics.get("memory_percent", 0.0),
                "gpu": 0.0,  # TODO: Add GPU monitoring
                "storage": metrics.get("disk_percent", 0.0)
            })
        except Exception as e:
            print(f"Error handling resource update: {e}")
    
    def _handle_resource_alert(self, event_data: Dict[str, Any]) -> None:
        """Handle resource alert from monitoring service."""
        try:
            alert = event_data.get("alert", {})
            alert_level = alert.get("level", "warning")
            message = alert.get("message", "Resource alert")
            
            # Store alert
            self.active_alerts.append(alert)
            
            # Update action button based on alert level
            if alert_level == "critical":
                self.show_action_required(f"CRITICAL: {message}")
            elif alert_level == "warning":
                self.show_action_required(f"WARNING: {message}")
                
        except Exception as e:
            print(f"Error handling resource alert: {e}")
    
    def _handle_approval_required(self, event_data: Dict[str, Any]) -> None:
        """Handle approval required from monitoring service."""
        try:
            alert = event_data.get("alert", {})
            alert_id = alert.get("alert_id")
            
            if alert_id:
                # Store pending approval
                self.pending_approvals[alert_id] = alert
                
                # Show approval dialog
                self._show_approval_dialog(alert)
                
        except Exception as e:
            print(f"Error handling approval required: {e}")
    
    def _handle_alert_cleared(self, event_data: Dict[str, Any]) -> None:
        """Handle alert cleared from monitoring service."""
        try:
            resource_type = event_data.get("resource_type")
            
            # Remove alerts for this resource type
            self.active_alerts = [
                alert for alert in self.active_alerts 
                if alert.get("resource_type") != resource_type
            ]
            
            # Hide action button if no more alerts
            if not self.active_alerts:
                self.hide_action_button()
                
        except Exception as e:
            print(f"Error handling alert cleared: {e}")
    
    def _show_approval_dialog(self, alert: Dict[str, Any]) -> None:
        """Show user approval dialog for resource actions."""
        try:
            alert_id = alert.get("alert_id")
            message = alert.get("message", "Resource action required")
            suggested_actions = alert.get("suggested_actions", [])
            
            # Create approval dialog message
            dialog_message = f"{message}\n\n"
            if suggested_actions:
                dialog_message += "Suggested actions:\n"
                for action in suggested_actions[:3]:  # Show first 3 suggestions
                    dialog_message += f"• {action}\n"
                dialog_message += "\nWould you like VPA to take action to optimize resource usage?"
            
            # Show dialog
            result = messagebox.askyesnocancel(
                "Resource Management Approval",
                dialog_message,
                icon="warning"
            )
            
            if result is True:
                # User approved
                self.event_bus.emit("resource.monitor.user_approval", {
                    "alert_id": alert_id,
                    "timestamp": time.time()
                })
                # Remove from pending
                if alert_id in self.pending_approvals:
                    del self.pending_approvals[alert_id]
                
            elif result is False:
                # User denied
                self.event_bus.emit("resource.monitor.user_denial", {
                    "alert_id": alert_id,
                    "timestamp": time.time()
                })
                # Remove from pending
                if alert_id in self.pending_approvals:
                    del self.pending_approvals[alert_id]
            
            # If cancelled, keep in pending for later
                
        except Exception as e:
            print(f"Error showing approval dialog: {e}")
