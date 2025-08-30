# Windows API Integration Requirements

## Overview

This document details the specific Windows API integration requirements for the VPA (Virtual Personal Assistant) project, including registry access, file system operations, system tray integration, notifications, window management, and security considerations.

## 1. Registry Integration

### 1.1 Registry Access Requirements

| Feature | Requirement |
|---------|-------------|
| **Registry Root Keys** | HKEY_CURRENT_USER primarily, HKEY_LOCAL_MACHINE for system settings |
| **Registry Path Pattern** | Software\\VPA\\* for all application settings |
| **Key Organization** | Hierarchical with component namespaces |
| **Value Types** | REG_SZ, REG_DWORD, REG_BINARY primarily |
| **Security Context** | Least privilege model, no admin rights for normal operation |
| **Error Handling** | Graceful degradation to defaults if registry access fails |

### 1.2 Specific Registry Operations

#### Application Settings
```python
def save_setting(key_name: str, value: Any) -> bool:
    """Save application setting to registry.
    
    Args:
        key_name: Setting key name (dot notation for hierarchy)
        value: Setting value (str, int, bytes supported)
        
    Returns:
        True if successful, False otherwise
    """
    # Convert dot notation to registry path
    reg_path = "Software\\VPA\\Settings"
    key_parts = key_name.split('.')
    if len(key_parts) > 1:
        reg_path = f"{reg_path}\\{key_parts[0]}"
        key_name = key_parts[-1]
    
    # Determine value type
    if isinstance(value, int):
        value_type = winreg.REG_DWORD
    elif isinstance(value, bytes):
        value_type = winreg.REG_BINARY
    else:
        value_type = winreg.REG_SZ
        value = str(value)
    
    try:
        key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, reg_path)
        winreg.SetValueEx(key, key_name, 0, value_type, value)
        winreg.CloseKey(key)
        return True
    except WindowsError as e:
        logger.error(f"Error saving setting {key_name}: {e}")
        return False
```

#### Run at Startup Configuration
```python
def set_run_at_startup(enable: bool = True) -> bool:
    """Configure application to run at Windows startup.
    
    Args:
        enable: True to enable run at startup, False to disable
        
    Returns:
        True if successful, False otherwise
    """
    run_key = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    app_name = "VPA"
    
    try:
        if enable:
            # Get application executable path
            import sys
            app_path = sys.executable
            
            # Create registry key
            key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, run_key)
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
            winreg.CloseKey(key)
            return True
        else:
            # Remove registry key
            key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, run_key)
            try:
                winreg.DeleteValue(key, app_name)
                return True
            except WindowsError:
                # Key doesn't exist, that's fine
                return True
            finally:
                winreg.CloseKey(key)
    except WindowsError as e:
        logger.error(f"Error configuring run at startup: {e}")
        return False
```

### 1.3 Registry Schema

| Registry Path | Value Name | Type | Purpose |
|---------------|------------|------|---------|
| Software\\VPA\\Settings | Version | REG_SZ | Application version |
| Software\\VPA\\Settings\\Voice | DefaultVoice | REG_SZ | Default voice ID |
| Software\\VPA\\Settings\\Voice | Volume | REG_DWORD | Voice volume (0-100) |
| Software\\VPA\\Settings\\Voice | Speed | REG_DWORD | Voice speed (0-100) |
| Software\\VPA\\Settings\\LLM | DefaultModel | REG_SZ | Default LLM model |
| Software\\VPA\\Settings\\LLM | Temperature | REG_DWORD | Temperature * 100 |
| Software\\VPA\\Settings\\UI | Theme | REG_SZ | UI theme (light/dark) |
| Software\\VPA\\Settings\\UI | MinimizeToTray | REG_DWORD | 1 if true, 0 if false |
| Software\\VPA\\Settings\\Plugins | Enabled | REG_BINARY | Serialized enabled plugins |

## 2. File System Integration

### 2.1 File System Requirements

| Feature | Requirement |
|---------|-------------|
| **Data Location** | %APPDATA%\\VPA for user data |
| **Cache Location** | %LOCALAPPDATA%\\VPA for temporary/cache data |
| **File Monitoring** | Watch for changes in configuration files |
| **File Operations** | Async I/O for all file operations |
| **Error Handling** | Proper handling of file access errors |
| **Path Handling** | Use pathlib for cross-version compatibility |

### 2.2 Specific File System Operations

#### Data Directory Structure
```
%APPDATA%\VPA\
├── config\                # Configuration files
│   ├── config.yaml        # Main configuration
│   ├── credentials.enc    # Encrypted credentials
│   └── voice_config.yaml  # Voice settings
├── cache\                 # Cached data
│   ├── voice_cache\       # Cached voice outputs
│   └── llm_cache\         # Cached LLM responses
├── plugins\               # User-installed plugins
└── logs\                  # Application logs
    ├── vpa.log           # Main log
    └── performance.log   # Performance log
```

#### File System Manager Implementation
```python
import os
import pathlib
import asyncio
import shutil
from typing import Optional, List, Dict, Any
import yaml

class FileSystemManager:
    """Manages file system operations for the application."""
    
    def __init__(self):
        # Define base paths
        self.app_data_path = pathlib.Path(os.getenv('APPDATA')) / "VPA"
        self.local_data_path = pathlib.Path(os.getenv('LOCALAPPDATA')) / "VPA"
        self.config_path = self.app_data_path / "config"
        self.cache_path = self.local_data_path / "cache"
        self.logs_path = self.app_data_path / "logs"
        self.plugins_path = self.app_data_path / "plugins"
        
        # Create directories if they don't exist
        self._ensure_directories()
        
        # File watchers
        self._watchers = {}
        
    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        os.makedirs(self.config_path, exist_ok=True)
        os.makedirs(self.cache_path, exist_ok=True)
        os.makedirs(self.logs_path, exist_ok=True)
        os.makedirs(self.plugins_path, exist_ok=True)
        os.makedirs(self.cache_path / "voice_cache", exist_ok=True)
        os.makedirs(self.cache_path / "llm_cache", exist_ok=True)
        
    async def read_config(self, config_name: str) -> Dict[str, Any]:
        """Read a configuration file asynchronously.
        
        Args:
            config_name: Name of the configuration file
            
        Returns:
            Dictionary with configuration data
        """
        config_file = self.config_path / f"{config_name}.yaml"
        
        # Default config if file doesn't exist
        if not config_file.exists():
            return {}
            
        try:
            # Read file asynchronously
            return await self._read_yaml_file(config_file)
        except Exception as e:
            logger.error(f"Error reading configuration {config_name}: {e}")
            return {}
            
    async def write_config(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """Write a configuration file asynchronously.
        
        Args:
            config_name: Name of the configuration file
            config_data: Configuration data to write
            
        Returns:
            True if successful, False otherwise
        """
        config_file = self.config_path / f"{config_name}.yaml"
        
        try:
            # Write file asynchronously
            return await self._write_yaml_file(config_file, config_data)
        except Exception as e:
            logger.error(f"Error writing configuration {config_name}: {e}")
            return False
            
    async def watch_file(self, file_path: pathlib.Path, callback) -> None:
        """Watch a file for changes.
        
        Args:
            file_path: Path to the file to watch
            callback: Coroutine to call when the file changes
        """
        if file_path in self._watchers:
            return
            
        # Create watcher task
        task = asyncio.create_task(self._watch_file_task(file_path, callback))
        self._watchers[file_path] = task
        
    async def _watch_file_task(self, file_path: pathlib.Path, callback) -> None:
        """Task to watch a file for changes.
        
        Args:
            file_path: Path to the file to watch
            callback: Coroutine to call when the file changes
        """
        if not file_path.exists():
            return
            
        last_modified = file_path.stat().st_mtime
        
        while True:
            try:
                await asyncio.sleep(1)  # Check every second
                
                if not file_path.exists():
                    continue
                    
                current_modified = file_path.stat().st_mtime
                
                if current_modified != last_modified:
                    last_modified = current_modified
                    await callback(file_path)
            except Exception as e:
                logger.error(f"Error watching file {file_path}: {e}")
                await asyncio.sleep(5)  # Longer sleep on error
                
    async def stop_watching(self, file_path: pathlib.Path) -> None:
        """Stop watching a file for changes.
        
        Args:
            file_path: Path to the file to stop watching
        """
        if file_path in self._watchers:
            self._watchers[file_path].cancel()
            del self._watchers[file_path]
            
    async def stop_all_watchers(self) -> None:
        """Stop all file watchers."""
        for task in self._watchers.values():
            task.cancel()
            
        self._watchers.clear()
        
    async def cache_data(self, cache_type: str, key: str, data: bytes) -> bool:
        """Cache binary data.
        
        Args:
            cache_type: Type of cache (e.g., 'voice', 'llm')
            key: Cache key
            data: Binary data to cache
            
        Returns:
            True if successful, False otherwise
        """
        cache_dir = self.cache_path / f"{cache_type}_cache"
        cache_file = cache_dir / key
        
        try:
            # Write binary data asynchronously
            async with aiofiles.open(cache_file, 'wb') as f:
                await f.write(data)
                
            return True
        except Exception as e:
            logger.error(f"Error caching data: {e}")
            return False
            
    async def get_cached_data(self, cache_type: str, key: str) -> Optional[bytes]:
        """Get cached binary data.
        
        Args:
            cache_type: Type of cache (e.g., 'voice', 'llm')
            key: Cache key
            
        Returns:
            Cached binary data, or None if not found
        """
        cache_dir = self.cache_path / f"{cache_type}_cache"
        cache_file = cache_dir / key
        
        if not cache_file.exists():
            return None
            
        try:
            # Read binary data asynchronously
            async with aiofiles.open(cache_file, 'rb') as f:
                return await f.read()
        except Exception as e:
            logger.error(f"Error reading cached data: {e}")
            return None
            
    async def clear_cache(self, cache_type: Optional[str] = None) -> bool:
        """Clear cache data.
        
        Args:
            cache_type: Type of cache to clear, or None to clear all
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if cache_type:
                cache_dir = self.cache_path / f"{cache_type}_cache"
                if cache_dir.exists():
                    # Remove all files in the directory
                    for file in cache_dir.glob('*'):
                        if file.is_file():
                            file.unlink()
            else:
                # Clear all caches
                if self.cache_path.exists():
                    # Recreate the cache directory
                    shutil.rmtree(self.cache_path)
                    os.makedirs(self.cache_path, exist_ok=True)
                    os.makedirs(self.cache_path / "voice_cache", exist_ok=True)
                    os.makedirs(self.cache_path / "llm_cache", exist_ok=True)
                    
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
            
    async def _read_yaml_file(self, file_path: pathlib.Path) -> Dict[str, Any]:
        """Read a YAML file asynchronously.
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            Dictionary with YAML data
        """
        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
            
        return yaml.safe_load(content)
        
    async def _write_yaml_file(self, file_path: pathlib.Path, data: Dict[str, Any]) -> bool:
        """Write a YAML file asynchronously.
        
        Args:
            file_path: Path to the YAML file
            data: Data to write
            
        Returns:
            True if successful, False otherwise
        """
        # Convert to YAML
        yaml_content = yaml.dump(data, default_flow_style=False)
        
        # Write to file asynchronously
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(yaml_content)
            
        return True
```

### 2.3 File System Security Considerations

1. **File Permissions**
   - Create files with appropriate permissions (user read/write only)
   - Check permissions before operations
   - Handle permission denied errors gracefully

2. **Path Traversal Prevention**
   - Validate all file paths
   - Use pathlib for safe path operations
   - Prevent access outside of designated directories

3. **File Locking**
   - Implement proper file locking for shared resources
   - Handle contention gracefully
   - Use try/finally to ensure locks are released

4. **Secure File Operations**
   - Use atomic operations when possible
   - Implement transactional file writes for critical data
   - Backup before modifying important files

## 3. System Tray Integration

### 3.1 System Tray Requirements

| Feature | Requirement |
|---------|-------------|
| **Icon Support** | Multiple icon states (normal, active, notification) |
| **Tooltip** | Dynamic tooltip with status information |
| **Context Menu** | Hierarchical context menu with dynamic items |
| **Click Handling** | Different actions for left/right click |
| **Notifications** | Balloon notifications from the tray |
| **High DPI** | Proper scaling for high DPI displays |

### 3.2 System Tray Implementation

```python
import win32api
import win32con
import win32gui
from threading import Thread
import os
from typing import Dict, List, Callable, Optional
import time
import logging

logger = logging.getLogger(__name__)

class SystemTrayIcon:
    """Windows system tray icon integration."""
    
    # Window class constants
    WINDOW_CLASS_NAME = "VPASystemTrayIcon"
    
    # Message constants
    WM_TRAY_CALLBACK = win32con.WM_USER + 1
    
    # Menu IDs
    MENU_EXIT = 1001
    MENU_SHOW = 1002
    MENU_SETTINGS = 1003
    MENU_CUSTOM_BASE = 2000
    
    def __init__(self):
        self._hwnd = None
        self._notify_id = None
        self._thread = None
        self._running = False
        self._icon_path = None
        self._menu_items = {}
        self._menu_callbacks = {}
        self._next_menu_id = self.MENU_CUSTOM_BASE
        self._tooltip = "VPA"
        self._on_left_click = None
        self._icons = {
            "normal": None,
            "active": None,
            "notification": None
        }
        
    def initialize(self, icon_path: str, tooltip: str = "VPA") -> bool:
        """Initialize the system tray icon.
        
        Args:
            icon_path: Path to the icon file
            tooltip: Tooltip text
            
        Returns:
            True if successful, False otherwise
        """
        if self._running:
            return True
            
        self._icon_path = icon_path
        self._tooltip = tooltip
        
        # Load the icon
        try:
            self._icons["normal"] = win32gui.LoadImage(
                0, icon_path, win32con.IMAGE_ICON,
                win32con.LR_DEFAULTSIZE, win32con.LR_DEFAULTSIZE,
                win32con.LR_LOADFROMFILE
            )
        except Exception as e:
            logger.error(f"Error loading icon: {e}")
            return False
            
        # Start the tray icon thread
        self._thread = Thread(target=self._tray_thread, daemon=True)
        self._thread.start()
        
        # Wait for the thread to initialize
        for _ in range(10):
            if self._hwnd:
                break
            time.sleep(0.1)
            
        return self._hwnd is not None
        
    def set_icon(self, icon_type: str = "normal") -> bool:
        """Set the active icon.
        
        Args:
            icon_type: Icon type ('normal', 'active', 'notification')
            
        Returns:
            True if successful, False otherwise
        """
        if not self._hwnd or not self._notify_id:
            return False
            
        icon = self._icons.get(icon_type)
        if not icon:
            icon = self._icons.get("normal")
            
        if not icon:
            return False
            
        try:
            message = win32gui.NIM_MODIFY
            flags = win32gui.NIF_ICON
            
            nid = (
                self._hwnd,
                0,
                flags,
                self.WM_TRAY_CALLBACK,
                icon,
                self._tooltip
            )
            
            win32gui.Shell_NotifyIcon(message, nid)
            return True
        except Exception as e:
            logger.error(f"Error setting tray icon: {e}")
            return False
            
    def set_tooltip(self, tooltip: str) -> bool:
        """Set the tooltip text.
        
        Args:
            tooltip: Tooltip text
            
        Returns:
            True if successful, False otherwise
        """
        if not self._hwnd or not self._notify_id:
            return False
            
        self._tooltip = tooltip
        
        try:
            message = win32gui.NIM_MODIFY
            flags = win32gui.NIF_TIP
            
            nid = (
                self._hwnd,
                0,
                flags,
                self.WM_TRAY_CALLBACK,
                self._icons.get("normal"),
                tooltip
            )
            
            win32gui.Shell_NotifyIcon(message, nid)
            return True
        except Exception as e:
            logger.error(f"Error setting tooltip: {e}")
            return False
            
    def show_notification(self, 
                        title: str, 
                        message: str, 
                        icon_type: str = "normal", 
                        duration: int = 10) -> bool:
        """Show a balloon notification.
        
        Args:
            title: Notification title
            message: Notification message
            icon_type: Icon type ('normal', 'active', 'notification')
            duration: Display duration in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if not self._hwnd or not self._notify_id:
            return False
            
        icon = self._icons.get(icon_type)
        if not icon:
            icon = self._icons.get("normal")
            
        try:
            message = win32gui.NIM_MODIFY
            flags = win32gui.NIF_INFO | win32gui.NIF_ICON
            
            nid = (
                self._hwnd,
                0,
                flags,
                self.WM_TRAY_CALLBACK,
                icon,
                self._tooltip,
                message,  # Info message
                duration * 1000,  # Timeout in milliseconds
                title,  # Title
                win32gui.NIIF_INFO  # Info icon
            )
            
            win32gui.Shell_NotifyIcon(message, nid)
            return True
        except Exception as e:
            logger.error(f"Error showing notification: {e}")
            return False
            
    def add_menu_item(self, label: str, callback: Callable) -> int:
        """Add an item to the context menu.
        
        Args:
            label: Menu item label
            callback: Function to call when the item is clicked
            
        Returns:
            Menu item ID
        """
        menu_id = self._next_menu_id
        self._next_menu_id += 1
        
        self._menu_items[menu_id] = label
        self._menu_callbacks[menu_id] = callback
        
        return menu_id
        
    def remove_menu_item(self, menu_id: int) -> bool:
        """Remove an item from the context menu.
        
        Args:
            menu_id: Menu item ID
            
        Returns:
            True if successful, False otherwise
        """
        if menu_id in self._menu_items:
            del self._menu_items[menu_id]
            
        if menu_id in self._menu_callbacks:
            del self._menu_callbacks[menu_id]
            
        return True
        
    def set_left_click_handler(self, callback: Callable) -> None:
        """Set the handler for left click events.
        
        Args:
            callback: Function to call on left click
        """
        self._on_left_click = callback
        
    def shutdown(self) -> None:
        """Shut down the system tray icon."""
        if not self._running:
            return
            
        self._running = False
        
        if self._hwnd:
            try:
                # Remove the icon
                win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, (self._hwnd, 0))
                
                # Post quit message to the thread
                win32gui.PostMessage(self._hwnd, win32con.WM_QUIT, 0, 0)
            except:
                pass
                
        # Wait for the thread to terminate
        if self._thread and self._thread.is_alive():
            self._thread.join(1.0)
            
    def _tray_thread(self) -> None:
        """Thread function for the system tray icon."""
        try:
            # Register window class
            wc = win32gui.WNDCLASS()
            wc.hInstance = win32gui.GetModuleHandle(None)
            wc.lpszClassName = self.WINDOW_CLASS_NAME
            wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
            wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
            wc.hbrBackground = win32con.COLOR_WINDOW
            wc.lpfnWndProc = self._window_proc
            
            # Register the window class
            class_atom = win32gui.RegisterClass(wc)
            
            # Create the window
            self._hwnd = win32gui.CreateWindow(
                class_atom,
                "VPA System Tray",
                win32con.WS_OVERLAPPED,
                0, 0, 0, 0,
                0, 0, wc.hInstance, None
            )
            
            # Add the icon
            flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
            nid = (
                self._hwnd,
                0,
                flags,
                self.WM_TRAY_CALLBACK,
                self._icons["normal"],
                self._tooltip
            )
            
            win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
            self._notify_id = nid
            
            # Mark as running
            self._running = True
            
            # Message loop
            win32gui.PumpMessages()
        except Exception as e:
            logger.error(f"Error in tray thread: {e}")
        finally:
            self._running = False
            
    def _window_proc(self, hwnd, message, wparam, lparam):
        """Window procedure for the system tray icon."""
        if message == self.WM_TRAY_CALLBACK:
            if lparam == win32con.WM_LBUTTONUP:
                # Left click
                if self._on_left_click:
                    try:
                        self._on_left_click()
                    except Exception as e:
                        logger.error(f"Error in left click handler: {e}")
            elif lparam == win32con.WM_RBUTTONUP:
                # Right click - show context menu
                self._show_context_menu()
        elif message == win32con.WM_COMMAND:
            # Menu item clicked
            menu_id = win32api.LOWORD(wparam)
            if menu_id == self.MENU_EXIT:
                # Exit application
                win32gui.PostQuitMessage(0)
            elif menu_id in self._menu_callbacks:
                # Custom menu item
                try:
                    self._menu_callbacks[menu_id]()
                except Exception as e:
                    logger.error(f"Error in menu callback: {e}")
        elif message == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
            
        return win32gui.DefWindowProc(hwnd, message, wparam, lparam)
        
    def _show_context_menu(self):
        """Show the context menu."""
        try:
            # Create the menu
            menu = win32gui.CreatePopupMenu()
            
            # Add standard items
            win32gui.AppendMenu(
                menu, win32con.MF_STRING, self.MENU_SHOW, "Show VPA"
            )
            win32gui.AppendMenu(
                menu, win32con.MF_STRING, self.MENU_SETTINGS, "Settings"
            )
            
            # Add separator
            win32gui.AppendMenu(
                menu, win32con.MF_SEPARATOR, 0, ""
            )
            
            # Add custom items
            for menu_id, label in self._menu_items.items():
                win32gui.AppendMenu(
                    menu, win32con.MF_STRING, menu_id, label
                )
                
            # Add separator
            win32gui.AppendMenu(
                menu, win32con.MF_SEPARATOR, 0, ""
            )
                
            # Add exit item
            win32gui.AppendMenu(
                menu, win32con.MF_STRING, self.MENU_EXIT, "Exit"
            )
            
            # Get cursor position
            pos = win32gui.GetCursorPos()
            
            # Display the menu
            win32gui.SetForegroundWindow(self._hwnd)
            win32gui.TrackPopupMenu(
                menu,
                win32con.TPM_LEFTALIGN | win32con.TPM_BOTTOMALIGN,
                pos[0], pos[1],
                0,
                self._hwnd,
                None
            )
            win32gui.PostMessage(self._hwnd, win32con.WM_NULL, 0, 0)
            
            # Destroy the menu
            win32gui.DestroyMenu(menu)
        except Exception as e:
            logger.error(f"Error showing context menu: {e}")
```

### 3.3 Usage Examples

```python
# Initialize the system tray
tray_icon = SystemTrayIcon()
tray_icon.initialize("icons/vpa.ico", "VPA - Virtual Personal Assistant")

# Add menu items
tray_icon.add_menu_item("Mute Voice", lambda: toggle_voice_mute())
tray_icon.add_menu_item("Restart VPA", lambda: restart_application())

# Set left click handler
tray_icon.set_left_click_handler(lambda: show_main_window())

# Show a notification
tray_icon.show_notification(
    "VPA Active", 
    "VPA is running in the background. Click the icon to open.", 
    "normal", 
    5
)

# Change icon state
tray_icon.set_icon("active")  # Show active state

# Update tooltip
tray_icon.set_tooltip("VPA - Processing request...")

# Clean up on exit
atexit.register(tray_icon.shutdown)
```

## 4. Notification System

### 4.1 Notification Requirements

| Feature | Requirement |
|---------|-------------|
| **Notification Types** | Toast, in-app, tray balloon |
| **Interactive Notifications** | Support for buttons and actions |
| **Priority Levels** | Low, normal, high, urgent |
| **Notification History** | Store recent notifications |
| **Customization** | Custom icons, sounds, duration |
| **Quiet Hours** | Respect system quiet hours |

### 4.2 Toast Notification Implementation

```python
from win10toast_click import ToastNotifier
import uuid
from typing import Dict, Callable, Any, Optional
import time
import logging
import os
import json

logger = logging.getLogger(__name__)

class NotificationSystem:
    """Windows notification system integration."""
    
    def __init__(self):
        self._toaster = ToastNotifier()
        self._notifications = {}
        self._history = []
        self._max_history = 50
        self._callbacks = {}
        
    def initialize(self) -> None:
        """Initialize the notification system."""
        self._toaster.initialize()
        
        # Load notification history
        self._load_history()
        
    def show_toast(self,
                 title: str,
                 message: str,
                 icon_path: Optional[str] = None,
                 duration: int = 5,
                 callback: Optional[Callable] = None,
                 actions: Optional[Dict[str, str]] = None) -> str:
        """Show a toast notification.
        
        Args:
            title: Notification title
            message: Notification message
            icon_path: Path to icon file (None for default)
            duration: Display duration in seconds
            callback: Function to call when notification is clicked
            actions: Dictionary of action IDs to action labels
            
        Returns:
            Notification ID
        """
        # Generate notification ID
        notification_id = str(uuid.uuid4())
        
        # Store callback if provided
        if callback:
            self._callbacks[notification_id] = callback
            
        # Use default icon if none provided
        if not icon_path:
            icon_path = os.path.join(os.path.dirname(__file__), "icons", "vpa.ico")
            
        # Show the notification
        self._toaster.show_toast(
            title,
            message,
            icon_path=icon_path,
            duration=duration,
            threaded=True,
            callback_on_click=lambda: self._on_notification_click(notification_id)
        )
        
        # Store in history
        notification = {
            "id": notification_id,
            "title": title,
            "message": message,
            "timestamp": time.time(),
            "has_callback": callback is not None,
            "has_actions": actions is not None
        }
        
        self._notifications[notification_id] = notification
        self._history.append(notification)
        
        # Trim history if needed
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
            
        # Save history
        self._save_history()
        
        return notification_id
        
    def get_notification_history(self) -> List[Dict[str, Any]]:
        """Get notification history.
        
        Returns:
            List of notification dictionaries
        """
        return self._history.copy()
        
    def clear_history(self) -> None:
        """Clear notification history."""
        self._history = []
        self._save_history()
        
    def _on_notification_click(self, notification_id: str) -> None:
        """Handle notification click event.
        
        Args:
            notification_id: ID of the clicked notification
        """
        if notification_id in self._callbacks:
            try:
                self._callbacks[notification_id]()
            except Exception as e:
                logger.error(f"Error in notification callback: {e}")
                
            # Remove the callback
            del self._callbacks[notification_id]
            
    def _load_history(self) -> None:
        """Load notification history from disk."""
        try:
            history_file = os.path.join(
                os.getenv('APPDATA'), 
                "VPA", 
                "notification_history.json"
            )
            
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    self._history = json.load(f)
                    
                # Validate and filter history
                self._history = [
                    n for n in self._history
                    if isinstance(n, dict) and "id" in n and "timestamp" in n
                ]
                
                # Sort by timestamp
                self._history.sort(key=lambda n: n["timestamp"])
                
                # Trim if needed
                if len(self._history) > self._max_history:
                    self._history = self._history[-self._max_history:]
        except Exception as e:
            logger.error(f"Error loading notification history: {e}")
            self._history = []
            
    def _save_history(self) -> None:
        """Save notification history to disk."""
        try:
            history_file = os.path.join(
                os.getenv('APPDATA'), 
                "VPA", 
                "notification_history.json"
            )
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(history_file), exist_ok=True)
            
            with open(history_file, 'w') as f:
                json.dump(self._history, f)
        except Exception as e:
            logger.error(f"Error saving notification history: {e}")
```

### 4.3 Usage Examples

```python
# Initialize notification system
notification_system = NotificationSystem()
notification_system.initialize()

# Show a simple notification
notification_id = notification_system.show_toast(
    "New Message",
    "You have received a new message from John.",
    duration=5
)

# Show a notification with a callback
def on_notification_click():
    print("Notification clicked!")
    
notification_id = notification_system.show_toast(
    "Calendar Event",
    "Meeting with Team in 15 minutes",
    callback=on_notification_click,
    duration=10
)

# Get notification history
history = notification_system.get_notification_history()
for notification in history:
    print(f"{notification['title']}: {notification['message']}")
```

## 5. Window Management

### 5.1 Window Management Requirements

| Feature | Requirement |
|---------|-------------|
| **Window Positioning** | Support for multi-monitor setups |
| **Window State** | Normal, minimized, maximized, hidden |
| **Stay on Top** | Option to keep window on top |
| **DPI Awareness** | Proper scaling for high DPI displays |
| **Window Animation** | Smooth transitions and effects |

### 5.2 Window Manager Implementation

```python
import win32gui
import win32con
import win32api
from typing import Tuple, Dict, Any, Optional
import ctypes
from ctypes import wintypes
import logging

logger = logging.getLogger(__name__)

class WindowManager:
    """Windows window management utilities."""
    
    def __init__(self):
        self._hwnd = None
        self._window_rect = (0, 0, 0, 0)  # x, y, width, height
        self._is_visible = False
        self._is_on_top = False
        
    def set_window_handle(self, hwnd) -> None:
        """Set the window handle to manage.
        
        Args:
            hwnd: Window handle
        """
        self._hwnd = hwnd
        
        # Get initial window position
        if self._hwnd:
            self._update_window_rect()
            self._is_visible = win32gui.IsWindowVisible(self._hwnd)
            
    def _update_window_rect(self) -> None:
        """Update the stored window rectangle."""
        if not self._hwnd:
            return
            
        try:
            rect = win32gui.GetWindowRect(self._hwnd)
            self._window_rect = (
                rect[0],
                rect[1],
                rect[2] - rect[0],
                rect[3] - rect[1]
            )
        except Exception as e:
            logger.error(f"Error getting window rectangle: {e}")
            
    def get_window_position(self) -> Tuple[int, int]:
        """Get the window position.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        return (self._window_rect[0], self._window_rect[1])
        
    def get_window_size(self) -> Tuple[int, int]:
        """Get the window size.
        
        Returns:
            Tuple of (width, height)
        """
        return (self._window_rect[2], self._window_rect[3])
        
    def set_window_position(self, x: int, y: int) -> bool:
        """Set the window position.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if successful, False otherwise
        """
        if not self._hwnd:
            return False
            
        try:
            win32gui.SetWindowPos(
                self._hwnd,
                0,
                x, y,
                self._window_rect[2],
                self._window_rect[3],
                win32con.SWP_NOSIZE | win32con.SWP_NOZORDER
            )
            
            self._window_rect = (
                x,
                y,
                self._window_rect[2],
                self._window_rect[3]
            )
            
            return True
        except Exception as e:
            logger.error(f"Error setting window position: {e}")
            return False
            
    def set_window_size(self, width: int, height: int) -> bool:
        """Set the window size.
        
        Args:
            width: Window width
            height: Window height
            
        Returns:
            True if successful, False otherwise
        """
        if not self._hwnd:
            return False
            
        try:
            win32gui.SetWindowPos(
                self._hwnd,
                0,
                self._window_rect[0],
                self._window_rect[1],
                width,
                height,
                win32con.SWP_NOMOVE | win32con.SWP_NOZORDER
            )
            
            self._window_rect = (
                self._window_rect[0],
                self._window_rect[1],
                width,
                height
            )
            
            return True
        except Exception as e:
            logger.error(f"Error setting window size: {e}")
            return False
            
    def show_window(self) -> bool:
        """Show the window.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._hwnd:
            return False
            
        try:
            win32gui.ShowWindow(self._hwnd, win32con.SW_SHOW)
            win32gui.SetForegroundWindow(self._hwnd)
            self._is_visible = True
            return True
        except Exception as e:
            logger.error(f"Error showing window: {e}")
            return False
            
    def hide_window(self) -> bool:
        """Hide the window.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._hwnd:
            return False
            
        try:
            win32gui.ShowWindow(self._hwnd, win32con.SW_HIDE)
            self._is_visible = False
            return True
        except Exception as e:
            logger.error(f"Error hiding window: {e}")
            return False
            
    def minimize_window(self) -> bool:
        """Minimize the window.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._hwnd:
            return False
            
        try:
            win32gui.ShowWindow(self._hwnd, win32con.SW_MINIMIZE)
            return True
        except Exception as e:
            logger.error(f"Error minimizing window: {e}")
            return False
            
    def maximize_window(self) -> bool:
        """Maximize the window.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._hwnd:
            return False
            
        try:
            win32gui.ShowWindow(self._hwnd, win32con.SW_MAXIMIZE)
            return True
        except Exception as e:
            logger.error(f"Error maximizing window: {e}")
            return False
            
    def restore_window(self) -> bool:
        """Restore the window to normal size.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._hwnd:
            return False
            
        try:
            win32gui.ShowWindow(self._hwnd, win32con.SW_RESTORE)
            return True
        except Exception as e:
            logger.error(f"Error restoring window: {e}")
            return False
            
    def set_stay_on_top(self, on_top: bool) -> bool:
        """Set whether the window stays on top.
        
        Args:
            on_top: True to stay on top, False otherwise
            
        Returns:
            True if successful, False otherwise
        """
        if not self._hwnd:
            return False
            
        try:
            if on_top:
                win32gui.SetWindowPos(
                    self._hwnd,
                    win32con.HWND_TOPMOST,
                    0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
                )
            else:
                win32gui.SetWindowPos(
                    self._hwnd,
                    win32con.HWND_NOTOPMOST,
                    0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
                )
                
            self._is_on_top = on_top
            return True
        except Exception as e:
            logger.error(f"Error setting stay on top: {e}")
            return False
            
    def center_window_on_screen(self) -> bool:
        """Center the window on the current screen.
        
        Returns:
            True if successful, False otherwise
        """
        if not self._hwnd:
            return False
            
        try:
            # Get current monitor info
            monitor_info = self._get_monitor_info()
            if not monitor_info:
                return False
                
            # Calculate center position
            work_area = monitor_info["work_area"]
            center_x = work_area[0] + (work_area[2] - work_area[0] - self._window_rect[2]) // 2
            center_y = work_area[1] + (work_area[3] - work_area[1] - self._window_rect[3]) // 2
            
            # Set position
            return self.set_window_position(center_x, center_y)
        except Exception as e:
            logger.error(f"Error centering window: {e}")
            return False
            
    def _get_monitor_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the monitor containing the window.
        
        Returns:
            Dictionary with monitor information, or None if failed
        """
        if not self._hwnd:
            return None
            
        try:
            # Get monitor handle
            monitor = win32api.MonitorFromWindow(self._hwnd, win32con.MONITOR_DEFAULTTONEAREST)
            
            # Get monitor info
            monitor_info = win32api.GetMonitorInfo(monitor)
            
            return {
                "monitor": monitor,
                "monitor_rect": monitor_info["Monitor"],
                "work_area": monitor_info["Work"],
                "is_primary": monitor_info["Flags"] == 1
            }
        except Exception as e:
            logger.error(f"Error getting monitor info: {e}")
            return None
            
    def is_visible(self) -> bool:
        """Check if the window is visible.
        
        Returns:
            True if visible, False otherwise
        """
        return self._is_visible
        
    def is_on_top(self) -> bool:
        """Check if the window is set to stay on top.
        
        Returns:
            True if on top, False otherwise
        """
        return self._is_on_top
```

### 5.3 Usage Examples

```python
# Initialize window manager
window_manager = WindowManager()
window_manager.set_window_handle(hwnd)

# Position the window
window_manager.set_window_position(100, 100)
window_manager.set_window_size(800, 600)

# Center on screen
window_manager.center_window_on_screen()

# Window state
window_manager.minimize_window()
window_manager.restore_window()
window_manager.maximize_window()

# Stay on top
window_manager.set_stay_on_top(True)

# Show/hide
window_manager.hide_window()
window_manager.show_window()
```

## 6. Windows Security Integration

### 6.1 Windows Credential Manager Integration

```python
import win32cred
import win32credui
import win32con
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class CredentialManager:
    """Windows Credential Manager integration."""
    
    # Target name prefix for credentials
    TARGET_PREFIX = "VPA_"
    
    def __init__(self):
        pass
        
    def save_credential(self, key: str, value: str) -> bool:
        """Save a credential to Windows Credential Manager.
        
        Args:
            key: Credential key (API name)
            value: Credential value (API key/token)
            
        Returns:
            True if successful, False otherwise
        """
        target_name = f"{self.TARGET_PREFIX}{key}"
        
        try:
            credential = {
                'Type': win32cred.CRED_TYPE_GENERIC,
                'TargetName': target_name,
                'UserName': 'VPA_API',
                'CredentialBlob': value.encode('utf-16'),
                'Comment': 'Saved by VPA',
                'Persist': win32cred.CRED_PERSIST_LOCAL_MACHINE
            }
            
            win32cred.CredWrite(credential, 0)
            return True
        except Exception as e:
            logger.error(f"Error saving credential: {e}")
            return False
            
    def get_credential(self, key: str) -> Optional[str]:
        """Get a credential from Windows Credential Manager.
        
        Args:
            key: Credential key (API name)
            
        Returns:
            Credential value if found, None otherwise
        """
        target_name = f"{self.TARGET_PREFIX}{key}"
        
        try:
            cred = win32cred.CredRead(target_name, win32cred.CRED_TYPE_GENERIC, 0)
            return cred['CredentialBlob'].decode('utf-16')
        except Exception as e:
            if not isinstance(e, win32cred.error) or e.winerror != 1168:  # Not found error
                logger.error(f"Error getting credential: {e}")
            return None
            
    def delete_credential(self, key: str) -> bool:
        """Delete a credential from Windows Credential Manager.
        
        Args:
            key: Credential key (API name)
            
        Returns:
            True if successful, False otherwise
        """
        target_name = f"{self.TARGET_PREFIX}{key}"
        
        try:
            win32cred.CredDelete(target_name, win32cred.CRED_TYPE_GENERIC, 0)
            return True
        except Exception as e:
            if not isinstance(e, win32cred.error) or e.winerror != 1168:  # Not found error
                logger.error(f"Error deleting credential: {e}")
            return False
            
    def prompt_for_credential(self, key: str, message: str) -> Optional[str]:
        """Prompt the user for a credential.
        
        Args:
            key: Credential key (API name)
            message: Message to display to the user
            
        Returns:
            Credential value if provided, None otherwise
        """
        target_name = f"{self.TARGET_PREFIX}{key}"
        
        try:
            flags = win32credui.CREDUI_FLAGS_GENERIC_CREDENTIALS | \
                   win32credui.CREDUI_FLAGS_ALWAYS_SHOW_UI | \
                   win32credui.CREDUI_FLAGS_DO_NOT_PERSIST
                   
            result, cred = win32credui.CredUIPromptForCredentials(
                target_name,
                0,
                None,
                None,
                False,
                flags,
                {
                    "Message": message,
                    "Caption": f"VPA - {key} API Credentials"
                }
            )
            
            if result == 0:  # Success
                return cred[1]  # Password/token
                
            return None
        except Exception as e:
            logger.error(f"Error prompting for credential: {e}")
            return None
```

### 6.2 Usage Examples

```python
# Initialize credential manager
credential_manager = CredentialManager()

# Save API key
success = credential_manager.save_credential(
    "OPENWEATHERMAP", 
    "1234567890abcdef"
)

# Get API key
api_key = credential_manager.get_credential("OPENWEATHERMAP")
if api_key:
    # Use API key
    weather_api.set_api_key(api_key)
else:
    # Prompt for API key
    api_key = credential_manager.prompt_for_credential(
        "OPENWEATHERMAP",
        "Please enter your OpenWeatherMap API key:"
    )
    if api_key:
        credential_manager.save_credential("OPENWEATHERMAP", api_key)
        weather_api.set_api_key(api_key)
    else:
        # User canceled
        weather_api.disable()
        
# Delete credential
credential_manager.delete_credential("OPENWEATHERMAP")
```

## 7. Windows Process and Power Management

### 7.1 Process Management

```python
import psutil
import os
import sys
import win32process
import win32api
import win32con
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ProcessManager:
    """Windows process management utilities."""
    
    def __init__(self):
        self._current_pid = os.getpid()
        
    def get_process_info(self) -> Dict[str, Any]:
        """Get information about the current process.
        
        Returns:
            Dictionary with process information
        """
        try:
            process = psutil.Process(self._current_pid)
            
            return {
                "pid": process.pid,
                "name": process.name(),
                "exe": process.exe(),
                "cwd": process.cwd(),
                "create_time": process.create_time(),
                "cpu_percent": process.cpu_percent(),
                "memory_info": {
                    "rss": process.memory_info().rss,
                    "vms": process.memory_info().vms
                },
                "status": process.status(),
                "username": process.username()
            }
        except Exception as e:
            logger.error(f"Error getting process info: {e}")
            return {
                "pid": self._current_pid,
                "error": str(e)
            }
            
    def set_process_priority(self, priority: str) -> bool:
        """Set the priority of the current process.
        
        Args:
            priority: Priority level ('low', 'below_normal', 'normal', 'above_normal', 'high', 'realtime')
            
        Returns:
            True if successful, False otherwise
        """
        priority_map = {
            'low': win32process.IDLE_PRIORITY_CLASS,
            'below_normal': win32process.BELOW_NORMAL_PRIORITY_CLASS,
            'normal': win32process.NORMAL_PRIORITY_CLASS,
            'above_normal': win32process.ABOVE_NORMAL_PRIORITY_CLASS,
            'high': win32process.HIGH_PRIORITY_CLASS,
            'realtime': win32process.REALTIME_PRIORITY_CLASS
        }
        
        if priority not in priority_map:
            logger.error(f"Invalid priority: {priority}")
            return False
            
        try:
            handle = win32api.OpenProcess(
                win32con.PROCESS_ALL_ACCESS,
                False,
                self._current_pid
            )
            
            win32process.SetPriorityClass(handle, priority_map[priority])
            win32api.CloseHandle(handle)
            
            return True
        except Exception as e:
            logger.error(f"Error setting process priority: {e}")
            return False
            
    def is_another_instance_running(self) -> bool:
        """Check if another instance of this application is running.
        
        Returns:
            True if another instance is running, False otherwise
        """
        try:
            current_process = psutil.Process(self._current_pid)
            my_name = os.path.basename(current_process.exe())
            
            for process in psutil.process_iter(['pid', 'name', 'exe']):
                if process.info['pid'] == self._current_pid:
                    continue
                    
                if process.info['exe'] and os.path.basename(process.info['exe']) == my_name:
                    return True
                    
            return False
        except Exception as e:
            logger.error(f"Error checking for another instance: {e}")
            return False
            
    def restart_application(self) -> None:
        """Restart the application."""
        try:
            # Start a new instance
            executable = sys.executable
            args = sys.argv[:]
            
            # Add a special argument to indicate restart
            if "--restarted" not in args:
                args.append("--restarted")
                
            args.insert(0, executable)
            
            # Use os.execv or subprocess depending on platform
            if sys.platform == 'win32':
                import subprocess
                subprocess.Popen(args)
            else:
                os.execv(executable, args)
                
            # Exit this instance
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error restarting application: {e}")
```

### 7.2 Power Management

```python
import win32api
import win32con
import win32security
import win32ts
import ctypes
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PowerManager:
    """Windows power management utilities."""
    
    # Constants
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ES_DISPLAY_REQUIRED = 0x00000002
    ES_AWAYMODE_REQUIRED = 0x00000040
    
    def __init__(self):
        self._prevent_sleep_mode = False
        
    def get_power_status(self) -> Dict[str, Any]:
        """Get the power status of the system.
        
        Returns:
            Dictionary with power status information
        """
        try:
            status = win32api.GetSystemPowerStatus()
            
            return {
                "ac_line_status": status[0],  # 1 if on AC power, 0 if on battery
                "battery_flag": status[1],    # Battery charge status
                "battery_life_percent": status[2],  # 0-100
                "battery_life_time": status[3],     # Seconds of battery life remaining
                "battery_full_life_time": status[4]  # Seconds of battery life when fully charged
            }
        except Exception as e:
            logger.error(f"Error getting power status: {e}")
            return {
                "error": str(e)
            }
            
    def prevent_system_sleep(self, prevent: bool = True) -> bool:
        """Prevent the system from sleeping.
        
        Args:
            prevent: True to prevent sleep, False to allow sleep
            
        Returns:
            True if successful, False otherwise
        """
        if prevent == self._prevent_sleep_mode:
            return True
            
        try:
            if prevent:
                # Prevent system sleep
                ctypes.windll.kernel32.SetThreadExecutionState(
                    self.ES_CONTINUOUS | self.ES_SYSTEM_REQUIRED
                )
            else:
                # Allow system sleep
                ctypes.windll.kernel32.SetThreadExecutionState(
                    self.ES_CONTINUOUS
                )
                
            self._prevent_sleep_mode = prevent
            return True
        except Exception as e:
            logger.error(f"Error setting system sleep state: {e}")
            return False
            
    def is_user_active(self) -> bool:
        """Check if the user is active.
        
        Returns:
            True if the user is active, False otherwise
        """
        try:
            # Get the idle time
            idle_info = win32api.GetLastInputInfo()
            idle_time = (win32api.GetTickCount() - idle_info) // 1000  # Seconds
            
            # Consider the user inactive if idle for more than 5 minutes
            return idle_time < 300
        except Exception as e:
            logger.error(f"Error checking user activity: {e}")
            return True  # Assume active if we can't determine
            
    def lock_workstation(self) -> bool:
        """Lock the workstation.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            win32api.LockWorkStation()
            return True
        except Exception as e:
            logger.error(f"Error locking workstation: {e}")
            return False
```

### 7.3 Usage Examples

```python
# Initialize managers
process_manager = ProcessManager()
power_manager = PowerManager()

# Check if another instance is running
if process_manager.is_another_instance_running():
    # Show message and exit
    print("Another instance of VPA is already running.")
    sys.exit(1)
    
# Set process priority
process_manager.set_process_priority("above_normal")

# Check power status
power_status = power_manager.get_power_status()
if power_status["ac_line_status"] == 0:  # On battery
    # Use energy-saving mode
    power_mode = "energy_saving"
else:
    # Use performance mode
    power_mode = "performance"
    
# Prevent system sleep during important operations
power_manager.prevent_system_sleep(True)
try:
    # Perform important operation
    pass
finally:
    # Allow system sleep again
    power_manager.prevent_system_sleep(False)
    
# Check user activity
if not power_manager.is_user_active():
    # User is away, pause voice notifications
    voice_system.pause_notifications()
```

## 8. Security Considerations

### 8.1 Registry Security
- Use least privilege principle - only access what's needed
- Store sensitive data in Windows Credential Manager, not registry
- Validate all registry values before use
- Handle registry access errors gracefully

### 8.2 File System Security
- Use proper file permissions
- Validate file paths to prevent traversal attacks
- Implement secure file operations for sensitive data
- Use atomic operations for configuration changes

### 8.3 API Credential Security
- Store all API keys in Windows Credential Manager
- Encrypt any cached credentials
- Never log sensitive information
- Implement key rotation mechanisms

### 8.4 General Security Considerations
- Follow the principle of least privilege
- Implement proper error handling and input validation
- Use secure communication channels
- Follow secure coding practices

## Conclusion

This document provides detailed requirements and implementations for Windows API integration in the VPA project, focusing on registry access, file system operations, system tray integration, notifications, window management, and security considerations. These implementations follow the architectural principles defined in the project planning documents and ensure deep integration with the Windows operating system.

---

*Windows API Integration Requirements completed on August 27, 2025*
