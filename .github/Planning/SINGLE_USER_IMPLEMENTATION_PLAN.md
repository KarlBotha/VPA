# VPA Implementation Plan for Single User

## Overview

This document outlines the implementation plan for the VPA application, focused on single-user usage rather than organization-wide deployment. It addresses packaging, database requirements, security standards, offline functionality, and user feedback mechanisms.

## 1. Packaging and Distribution

### 1.1 Single-EXE Distribution

For ease of installation, VPA will be packaged as a single executable file:

```
┌───────────────────────────────────────────────────────────┐
│                      VPA.exe                              │
│                                                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────┐  │
│  │  Application    │  │     Python      │  │  Required  │  │
│  │     Code        │  │    Runtime      │  │  Libraries │  │
│  └─────────────────┘  └─────────────────┘  └───────────┘  │
│                                                           │
│  ┌─────────────────┐  ┌─────────────────┐                 │
│  │     Assets      │  │    Database     │                 │
│  │  (UI, Sounds)   │  │    Engine       │                 │
│  └─────────────────┘  └─────────────────┘                 │
└───────────────────────────────────────────────────────────┘
```

### 1.2 Implementation Approach

We'll use PyInstaller to create a self-contained executable:

1. **Build Process**:
   ```powershell
   # Activate virtual environment
   .\.venv\Scripts\Activate.ps1
   
   # Install PyInstaller
   pip install pyinstaller
   
   # Create spec file
   pyi-makespec --onefile --windowed --icon=assets/vpa_icon.ico src/main.py
   
   # Edit spec file to include additional files
   # (Add data files, assets, etc.)
   
   # Build executable
   pyinstaller VPA.spec
   ```

2. **Included Dependencies**:
   - Python runtime (embedded)
   - Required Python packages
   - SQLite database engine
   - UI assets and resources
   - Default configuration files

3. **User Files Location**:
   - User data stored in `%APPDATA%\VPA\`
   - Logs stored in `%APPDATA%\VPA\logs\`
   - Configuration in `%APPDATA%\VPA\config\`

## 2. Database Selection

### 2.1 SQLite Implementation

For a single-user application, SQLite is the optimal choice:

1. **Advantages for VPA**:
   - Zero configuration required
   - No separate server process
   - Single file storage (easy backup)
   - Cross-platform compatible
   - Serverless (perfect for single user)
   - Reliable and well-tested

2. **Implementation Pattern**:
   ```python
   class DatabaseManager:
       """Manager for SQLite database operations"""
       
       def __init__(self):
           self.db_path = os.path.join(get_app_data_dir(), "vpa_data.db")
           self._ensure_tables()
           
       def _ensure_tables(self):
           """Ensure all required tables exist"""
           with self._get_connection() as conn:
               cursor = conn.cursor()
               
               # Create chat history table
               cursor.execute('''
               CREATE TABLE IF NOT EXISTS chat_history (
                   id TEXT PRIMARY KEY,
                   title TEXT NOT NULL,
                   created_at TEXT NOT NULL,
                   updated_at TEXT NOT NULL
               )
               ''')
               
               # Create chat messages table
               cursor.execute('''
               CREATE TABLE IF NOT EXISTS chat_messages (
                   id TEXT PRIMARY KEY,
                   chat_id TEXT NOT NULL,
                   role TEXT NOT NULL,
                   content TEXT NOT NULL,
                   timestamp TEXT NOT NULL,
                   FOREIGN KEY (chat_id) REFERENCES chat_history(id)
               )
               ''')
               
               # Create settings table
               cursor.execute('''
               CREATE TABLE IF NOT EXISTS settings (
                   key TEXT PRIMARY KEY,
                   value TEXT NOT NULL
               )
               ''')
               
               # Create user_data table
               cursor.execute('''
               CREATE TABLE IF NOT EXISTS user_data (
                   key TEXT PRIMARY KEY,
                   value TEXT NOT NULL
               )
               ''')
               
               conn.commit()
               
       def _get_connection(self):
           """Get a database connection"""
           os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
           return sqlite3.connect(self.db_path)
   ```

### 2.2 Schema Design

The SQLite database will use the following schema:

1. **Chat History Table**: Stores metadata about chat sessions
   - `id`: Unique identifier for the chat (UUID)
   - `title`: User-defined chat title
   - `created_at`: Creation timestamp
   - `updated_at`: Last update timestamp

2. **Chat Messages Table**: Stores individual messages
   - `id`: Unique message identifier
   - `chat_id`: Foreign key to chat_history
   - `role`: Message sender (user/assistant/system)
   - `content`: Message content
   - `timestamp`: Message timestamp

3. **Settings Table**: Key-value store for application settings
   - `key`: Setting path (dot-notation)
   - `value`: JSON-encoded setting value

4. **User Data Table**: Stores user-specific data
   - `key`: Data identifier
   - `value`: JSON-encoded data value

## 3. Security Implementation

### 3.1 Microsoft and Google Security Standards

VPA will implement security following Microsoft and Google recommended standards:

1. **Data Storage**:
   - Encryption of sensitive data at rest
   - Secure storage of credentials using Windows Data Protection API
   - No storage of plain-text passwords

2. **Authentication**:
   - Strong password requirements (if used)
   - Support for Windows Hello biometric authentication
   - OAuth 2.0 for service authentication

3. **API Security**:
   - TLS 1.2+ for all network communications
   - Secure storage of API keys using Windows Credential Manager
   - Token rotation and refresh mechanisms

### 3.2 Implementation Example

```python
class SecurityManager:
    """Manager for security operations"""
    
    def __init__(self):
        self.credential_manager = WindowsCredentialManager("VPA")
        
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data using Windows DPAPI"""
        try:
            from win32crypt import CryptProtectData
            import win32security
            
            # Convert data to bytes
            data_bytes = data.encode('utf-16-le')
            
            # Encrypt data using DPAPI (user-specific protection)
            encrypted_bytes = CryptProtectData(
                data_bytes, 
                "VPA Sensitive Data",  # Description
                None,                  # Entropy
                None,                  # Reserved
                None,                  # Prompt structure
                0                      # Flags
            )
            
            # Convert to base64 for storage
            import base64
            return base64.b64encode(encrypted_bytes).decode('ascii')
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return ""
            
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data using Windows DPAPI"""
        try:
            from win32crypt import CryptUnprotectData
            import base64
            
            # Convert from base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Decrypt data
            decrypted_data, desc = CryptUnprotectData(
                encrypted_bytes,
                None,    # Description
                None,    # Entropy
                None,    # Reserved
                None     # Prompt structure
            )
            
            # Convert bytes back to string
            return decrypted_data.decode('utf-16-le')
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return ""
            
    def store_credential(self, target: str, username: str, password: str) -> bool:
        """Store credential in Windows Credential Manager"""
        return self.credential_manager.store_credential(target, username, password)
        
    def get_credential(self, target: str) -> Tuple[str, str]:
        """Get credential from Windows Credential Manager"""
        return self.credential_manager.get_credential(target)
```

## 4. Offline Functionality

### 4.1 Offline-First Approach

VPA will use an offline-first approach where all core functions work without internet:

1. **Features Available Offline**:
   - UI and application framework
   - Settings management
   - Chat history browsing
   - Local LLM operation (if installed)
   - Voice input processing (using Windows Speech Recognition)
   - All Windows integration features

2. **Features Requiring Internet**:
   - Cloud LLM services (if configured)
   - Web API speech recognition fallback (if configured)
   - Software updates
   - Telemetry/feedback submission

### 4.2 Internet Detection

```python
class ConnectivityManager:
    """Manager for network connectivity state"""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.is_online = False
        self.check_interval = 60  # seconds
        self._start_monitoring()
        
    def _start_monitoring(self):
        """Start monitoring connectivity"""
        import threading
        self._monitor_thread = threading.Thread(
            target=self._connectivity_monitor,
            daemon=True
        )
        self._monitor_thread.start()
        
    def _connectivity_monitor(self):
        """Background thread to monitor connectivity"""
        import time
        import asyncio
        
        while True:
            # Check connectivity
            new_state = self._check_internet_connection()
            
            # If state changed, emit event
            if new_state != self.is_online:
                self.is_online = new_state
                
                # Create event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Emit event
                loop.run_until_complete(
                    self.event_bus.emit_async("connectivity.changed", {
                        "is_online": self.is_online
                    })
                )
                
                # Close loop
                loop.close()
                
            # Wait before next check
            time.sleep(self.check_interval)
            
    def _check_internet_connection(self) -> bool:
        """Check if internet connection is available"""
        try:
            # Try to connect to a reliable server
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=1)
            return True
        except OSError:
            return False
```

## 5. User Feedback and Error Reporting

### 5.1 Error Logging System

VPA implements comprehensive error logging:

```python
class LoggingManager:
    """Manager for application logging"""
    
    def __init__(self, config):
        self.config = config
        self.log_dir = os.path.join(get_app_data_dir(), "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Set up logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure logging system"""
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Create root logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create file handler for detailed logs
        detailed_log_path = os.path.join(self.log_dir, "vpa_detailed.log")
        detailed_handler = RotatingFileHandler(
            detailed_log_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        detailed_handler.setLevel(logging.DEBUG)
        detailed_handler.setFormatter(detailed_formatter)
        
        # Create file handler for error logs
        error_log_path = os.path.join(self.log_dir, "vpa_errors.log")
        error_handler = RotatingFileHandler(
            error_log_path,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        
        # Add handlers to logger
        logger.addHandler(detailed_handler)
        logger.addHandler(error_handler)
        
    def get_log_files(self) -> List[str]:
        """Get list of log files"""
        return [
            os.path.join(self.log_dir, f)
            for f in os.listdir(self.log_dir)
            if f.endswith('.log')
        ]
```

### 5.2 Feedback Submission UI

```python
class FeedbackDialog(QDialog):
    """Dialog for submitting user feedback"""
    
    def __init__(self, parent, logging_manager):
        super().__init__(parent)
        self.logging_manager = logging_manager
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the UI components"""
        # Window properties
        self.setWindowTitle("Send Feedback")
        self.setMinimumSize(500, 400)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Feedback type
        type_layout = QHBoxLayout()
        type_label = QLabel("Feedback type:")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Bug Report", "Feature Request", "General Feedback"])
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo, 1)
        layout.addLayout(type_layout)
        
        # Feedback description
        layout.addWidget(QLabel("Description:"))
        self.description_edit = QTextEdit()
        layout.addWidget(self.description_edit)
        
        # Email for contact (optional)
        email_layout = QHBoxLayout()
        email_label = QLabel("Your email (optional):")
        self.email_edit = QLineEdit()
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_edit, 1)
        layout.addLayout(email_layout)
        
        # Include logs option
        self.include_logs_check = QCheckBox("Include log files")
        self.include_logs_check.setChecked(True)
        layout.addWidget(self.include_logs_check)
        
        # Log file selection (initially hidden)
        self.log_files_group = QGroupBox("Select log files to include:")
        log_files_layout = QVBoxLayout(self.log_files_group)
        
        # Add log files as checkboxes
        self.log_file_checks = {}
        for log_file in self.logging_manager.get_log_files():
            check = QCheckBox(os.path.basename(log_file))
            check.setChecked(True)
            check.setData(log_file)
            log_files_layout.addWidget(check)
            self.log_file_checks[log_file] = check
            
        layout.addWidget(self.log_files_group)
        
        # Connect checkbox signal
        self.include_logs_check.stateChanged.connect(self._on_include_logs_changed)
        self._on_include_logs_changed(Qt.Checked)
        
        # Button row
        button_layout = QHBoxLayout()
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        # Spacer
        button_layout.addStretch(1)
        
        # Manual export button
        self.export_button = QPushButton("Export Logs")
        self.export_button.clicked.connect(self._on_export_clicked)
        button_layout.addWidget(self.export_button)
        
        # Send button
        self.send_button = QPushButton("Send Feedback")
        self.send_button.clicked.connect(self._on_send_clicked)
        button_layout.addWidget(self.send_button)
        
        layout.addLayout(button_layout)
        
    def _on_include_logs_changed(self, state):
        """Handle include logs checkbox state change"""
        self.log_files_group.setVisible(state == Qt.Checked)
        
    def _on_export_clicked(self):
        """Handle export logs button click"""
        # Show file dialog to select export location
        export_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Log Files",
            os.path.join(QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation), "vpa_logs.zip"),
            "ZIP Files (*.zip)"
        )
        
        if not export_path:
            return
            
        # Create zip file
        try:
            self._export_logs(export_path)
            QMessageBox.information(
                self,
                "Logs Exported",
                f"Log files have been exported to:\n{export_path}",
                QMessageBox.Ok
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export log files:\n{str(e)}",
                QMessageBox.Ok
            )
            
    def _export_logs(self, export_path):
        """Export log files to ZIP archive"""
        import zipfile
        
        with zipfile.ZipFile(export_path, 'w') as zipf:
            # Add selected log files
            for log_file, check in self.log_file_checks.items():
                if check.isChecked():
                    zipf.write(log_file, os.path.basename(log_file))
                    
            # Add system info
            zipf.writestr("system_info.txt", self._get_system_info())
            
    def _get_system_info(self):
        """Get system information text"""
        import platform
        import psutil
        
        info = []
        info.append("VPA System Information")
        info.append("=====================")
        info.append(f"VPA Version: 1.0.0")
        info.append(f"OS: {platform.system()} {platform.version()}")
        info.append(f"Python: {platform.python_version()}")
        info.append(f"CPU: {platform.processor()}")
        info.append(f"Memory: {psutil.virtual_memory().total / (1024**3):.2f} GB")
        
        return "\n".join(info)
        
    def _on_send_clicked(self):
        """Handle send feedback button click"""
        # Validate input
        description = self.description_edit.toPlainText().strip()
        if not description:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please provide a description of your feedback.",
                QMessageBox.Ok
            )
            return
            
        # Show sending dialog
        sending_dialog = QProgressDialog("Sending feedback...", "Cancel", 0, 0, self)
        sending_dialog.setWindowModality(Qt.WindowModal)
        sending_dialog.setMinimumDuration(500)
        sending_dialog.setValue(0)
        
        # Prepare feedback data
        feedback_data = {
            "type": self.type_combo.currentText(),
            "description": description,
            "email": self.email_edit.text().strip(),
            "include_logs": self.include_logs_check.isChecked()
        }
        
        # Show information to user
        QMessageBox.information(
            self,
            "Feedback Information",
            "To submit your feedback, please send an email to:\n\n"
            "feedback@vpa-assistant.com\n\n"
            "If you selected to include logs, please attach the exported log file.",
            QMessageBox.Ok
        )
        
        # Close sending dialog
        sending_dialog.cancel()
        
        # Export logs if needed
        if self.include_logs_check.isChecked():
            self._on_export_clicked()
            
        # Accept dialog
        self.accept()
```

### 5.3 Menu Integration

```python
# Add Help menu item for feedback
help_menu = self.menuBar().addMenu("Help")

# Feedback action
feedback_action = QAction("Send Feedback...", self)
feedback_action.triggered.connect(self._show_feedback_dialog)
help_menu.addAction(feedback_action)

def _show_feedback_dialog(self):
    """Show the feedback dialog"""
    dialog = FeedbackDialog(self, self.logging_manager)
    dialog.exec_()
```

## Outstanding Gaps and Items

Based on the updates and clarifications provided, here's a list of outstanding items that require further input:

1. **LLM Selection and Configuration**:
   - Need to confirm specific Ollama and Llama models to include
   - Required model configuration parameters
   - Default model selection for first-time users

2. **Voice Input Language Support**:
   - While focusing on English, need to specify which English variants to support
   - Accent handling capabilities for speech recognition

3. **Installation Requirements**:
   - Minimum Windows version specification (Windows 10/11?)
   - Minimum hardware requirements (RAM, CPU)
   - Disk space requirements for application and data

4. **User Authentication**:
   - Determine if user authentication is needed beyond Windows login
   - If so, what authentication method (local password, Windows Hello, etc.)

5. **Specific Security Requirements**:
   - Any specific security standards that need to be met beyond Microsoft/Google recommendations
   - Data retention policies for user data and logs

6. **UI Theme and Branding**:
   - Final color scheme and design elements
   - Logo and icon design for the application
   - Light/dark theme implementation details

7. **Error Handling Policy**:
   - Define what types of errors should be automatically reported
   - Privacy considerations for error reporting
   - Criteria for critical errors vs. minor issues

8. **Performance Targets**:
   - Specific performance benchmarks for LLM response time
   - Voice processing latency targets
   - Memory usage limits for different hardware tiers

9. **Testing Requirements**:
   - Types of tests required (unit, integration, UI)
   - Coverage requirements for codebase
   - User acceptance testing criteria

10. **Release Schedule and Versioning**:
    - Version numbering scheme
    - Release frequency
    - Update mechanism details

---

*Document created on August 28, 2025*  
*Version: 1.0*
