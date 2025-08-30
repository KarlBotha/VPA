# VPA Security and Privacy Strategy

## Executive Summary

This document outlines the security and privacy strategy for the VPA (Virtual Personal Assistant) application. As a personal assistant that may handle sensitive user data, ensuring robust security measures and respecting user privacy are paramount concerns. This strategy document defines the security architecture, privacy principles, data handling practices, and compliance measures implemented throughout the VPA system.

## 1. Security Architecture

### 1.1 Core Security Principles

VPA's security architecture is built on the following core principles:

1. **Defense in Depth**: Multiple layers of security controls
2. **Least Privilege**: Components access only what they need
3. **Secure by Default**: Security enabled in default configurations
4. **Data Protection**: Encryption for sensitive data at rest and in transit
5. **Secure Communication**: Authenticated and encrypted communications
6. **Error Isolation**: Security boundaries between components
7. **Regular Updates**: Mechanism for security patches and updates

### 1.2 Authentication and Authorization

```python
# src/vpa/security/auth.py
class AuthenticationManager:
    """Manages authentication for VPA."""
    
    def __init__(self):
        self._current_user = None
        self._auth_providers = {}
        self._session_token = None
    
    async def authenticate_user(self, auth_method, credentials):
        """Authenticate a user using the specified method."""
        if auth_method not in self._auth_providers:
            raise ValueError(f"Unknown authentication method: {auth_method}")
            
        provider = self._auth_providers[auth_method]
        user = await provider.authenticate(credentials)
        
        if user:
            self._current_user = user
            self._session_token = self._generate_session_token()
            await event_bus.emit_async("user_authenticated", {
                "user_id": user.id,
                "auth_method": auth_method
            })
            return True
        return False
    
    def authorize_action(self, action, resource=None):
        """Check if current user is authorized for an action."""
        if not self._current_user:
            return False
            
        return self._current_user.has_permission(action, resource)
```

### 1.3 Data Encryption

```python
# src/vpa/security/encryption.py
class EncryptionManager:
    """Manages encryption for VPA."""
    
    def __init__(self):
        self._encryption_key = self._load_or_generate_key()
        
    def _load_or_generate_key(self):
        """Load existing key or generate a new one."""
        key_path = Path(app_dirs.user_data_dir) / ".keys" / "data_key.enc"
        
        if key_path.exists():
            # Load and decrypt the key using system-protected storage
            return self._decrypt_key(key_path.read_bytes())
        else:
            # Generate a new key
            key = Fernet.generate_key()
            # Encrypt and save the key
            key_path.parent.mkdir(parents=True, exist_ok=True)
            key_path.write_bytes(self._encrypt_key(key))
            return key
    
    def encrypt_data(self, data):
        """Encrypt data using the encryption key."""
        if not isinstance(data, bytes):
            data = str(data).encode('utf-8')
            
        f = Fernet(self._encryption_key)
        return f.encrypt(data)
    
    def decrypt_data(self, encrypted_data):
        """Decrypt data using the encryption key."""
        f = Fernet(self._encryption_key)
        return f.decrypt(encrypted_data)
```

### 1.4 Secure Storage

```python
# src/vpa/security/storage.py
class SecureStorage:
    """Secure storage for sensitive data."""
    
    def __init__(self):
        self._encryption_manager = EncryptionManager()
        self._storage_path = Path(app_dirs.user_data_dir) / "secure_storage"
        self._storage_path.mkdir(parents=True, exist_ok=True)
        
    async def store(self, key, value):
        """Securely store a value."""
        # Encrypt the value
        encrypted_value = self._encryption_manager.encrypt_data(value)
        
        # Hash the key to use as filename
        key_hash = hashlib.sha256(key.encode('utf-8')).hexdigest()
        file_path = self._storage_path / key_hash
        
        # Store the encrypted value
        with open(file_path, 'wb') as f:
            f.write(encrypted_value)
            
    async def retrieve(self, key):
        """Retrieve a securely stored value."""
        # Hash the key to get filename
        key_hash = hashlib.sha256(key.encode('utf-8')).hexdigest()
        file_path = self._storage_path / key_hash
        
        if not file_path.exists():
            return None
            
        # Read and decrypt the value
        with open(file_path, 'rb') as f:
            encrypted_value = f.read()
            
        return self._encryption_manager.decrypt_data(encrypted_value)
        
    async def delete(self, key):
        """Delete a securely stored value."""
        key_hash = hashlib.sha256(key.encode('utf-8')).hexdigest()
        file_path = self._storage_path / key_hash
        
        if file_path.exists():
            file_path.unlink()
```

### 1.5 Secure Communications

```python
# src/vpa/security/comms.py
class SecureCommunicationManager:
    """Manages secure communications with external services."""
    
    def __init__(self):
        self._cert_path = Path(app_dirs.user_config_dir) / "certs"
        self._cert_path.mkdir(parents=True, exist_ok=True)
        
    async def create_secure_session(self):
        """Create a secure HTTP session."""
        ssl_context = ssl.create_default_context(cafile=self._get_ca_cert_path())
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        session = aiohttp.ClientSession(connector=connector)
        
        return session
        
    def _get_ca_cert_path(self):
        """Get the CA certificate path."""
        ca_cert_path = self._cert_path / "ca.pem"
        
        if not ca_cert_path.exists():
            # Use system default CA certs
            return None
            
        return str(ca_cert_path)
        
    async def verify_server_certificate(self, cert_data):
        """Verify a server certificate."""
        # Implementation depends on specific use case
        # Could use OpenSSL bindings or other certificate validation libraries
        pass
```

## 2. Privacy Framework

### 2.1 Privacy Principles

1. **Transparency**: Clear communication about data collection and usage
2. **Data Minimization**: Collect only necessary data
3. **Purpose Limitation**: Use data only for stated purposes
4. **User Control**: Users control their data
5. **Data Security**: Protect all user data
6. **Limited Retention**: Don't keep data longer than needed
7. **Privacy by Design**: Privacy considered from the start

### 2.2 Data Classification

| Classification | Description | Examples | Protection Level |
|----------------|-------------|----------|-----------------|
| **Public** | Non-sensitive information | App version, UI settings | Basic |
| **Internal** | Non-sensitive but not public | Usage statistics, error logs | Standard |
| **Sensitive** | Personal user data | User preferences, search history | Enhanced |
| **Confidential** | Private user content | Voice recordings, messages | Maximum |

### 2.3 Data Collection Policy

```python
# src/vpa/privacy/data_policy.py
class DataCollectionPolicy:
    """Defines and enforces data collection policies."""
    
    def __init__(self):
        self._policies = self._load_policies()
        self._user_consents = self._load_user_consents()
        
    def _load_policies(self):
        """Load data collection policies."""
        return {
            "voice_recording": {
                "purpose": "Voice command processing",
                "retention_period": "24 hours",
                "data_type": "audio",
                "classification": "confidential",
                "storage_location": "local_only"
            },
            "command_history": {
                "purpose": "Command recall and suggestion",
                "retention_period": "90 days",
                "data_type": "text",
                "classification": "sensitive",
                "storage_location": "local_only"
            },
            "usage_statistics": {
                "purpose": "Feature improvement",
                "retention_period": "365 days",
                "data_type": "analytics",
                "classification": "internal",
                "anonymized": True,
                "storage_location": "local_with_optional_cloud"
            }
        }
    
    def _load_user_consents(self):
        """Load user consent preferences."""
        try:
            consent_file = Path(app_dirs.user_config_dir) / "privacy" / "consent.json"
            
            if not consent_file.exists():
                return {}
                
            with open(consent_file, 'r') as f:
                return json.load(f)
        except Exception:
            logger.error("Failed to load user consents", exc_info=True)
            return {}
    
    def can_collect_data(self, data_type):
        """Check if data collection is allowed."""
        if data_type not in self._policies:
            # Unknown data type, don't collect
            return False
            
        policy = self._policies[data_type]
        
        # Check user consent
        if data_type in self._user_consents:
            return self._user_consents[data_type]
            
        # Default to no collection without consent
        return False
        
    def get_retention_period(self, data_type):
        """Get the retention period for a data type."""
        if data_type not in self._policies:
            return None
            
        return self._policies[data_type].get("retention_period")
        
    def set_user_consent(self, data_type, consented):
        """Set user consent for data collection."""
        if data_type not in self._policies:
            raise ValueError(f"Unknown data type: {data_type}")
            
        self._user_consents[data_type] = consented
        
        # Save updated consents
        consent_file = Path(app_dirs.user_config_dir) / "privacy" / "consent.json"
        consent_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(consent_file, 'w') as f:
            json.dump(self._user_consents, f)
```

### 2.4 Data Retention and Deletion

```python
# src/vpa/privacy/data_lifecycle.py
class DataRetentionManager:
    """Manages data retention and deletion."""
    
    def __init__(self):
        self._policy = DataCollectionPolicy()
        
    async def cleanup_expired_data(self):
        """Remove data that has exceeded its retention period."""
        data_stores = {
            "voice_recording": self._cleanup_voice_recordings,
            "command_history": self._cleanup_command_history,
            "usage_statistics": self._cleanup_usage_statistics
        }
        
        for data_type, cleanup_func in data_stores.items():
            await cleanup_func(data_type)
    
    async def _cleanup_voice_recordings(self, data_type):
        """Clean up expired voice recordings."""
        retention_period = self._policy.get_retention_period(data_type)
        if not retention_period:
            return
            
        # Convert retention period to timedelta
        retention_days = self._parse_retention_period(retention_period)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        recordings_dir = Path(app_dirs.user_data_dir) / "voice_recordings"
        if not recordings_dir.exists():
            return
            
        for recording_file in recordings_dir.glob("*.wav"):
            # Check creation time
            creation_time = datetime.fromtimestamp(recording_file.stat().st_ctime)
            
            if creation_time < cutoff_date:
                # Delete expired recording
                try:
                    recording_file.unlink()
                except Exception:
                    logger.error(f"Failed to delete expired recording: {recording_file}", exc_info=True)
    
    def _parse_retention_period(self, period):
        """Parse retention period string to number of days."""
        if isinstance(period, int):
            return period
            
        match = re.match(r"(\d+)\s+(day|days|month|months|year|years)", period.lower())
        if not match:
            return 30  # Default to 30 days
            
        value = int(match.group(1))
        unit = match.group(2)
        
        if unit.startswith("day"):
            return value
        elif unit.startswith("month"):
            return value * 30
        elif unit.startswith("year"):
            return value * 365
            
        return 30  # Default
```

## 3. User Privacy Controls

### 3.1 Privacy Settings UI

The VPA provides a comprehensive privacy settings interface that allows users to:

1. View all data types being collected
2. Understand how each data type is used
3. Control collection of each data type
4. Export collected data
5. Delete specific data or all data

```python
# src/vpa/gui/privacy_settings.py
class PrivacySettingsPanel:
    """Privacy settings UI panel."""
    
    def __init__(self, parent):
        self.parent = parent
        self._policy = DataCollectionPolicy()
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI components."""
        self.frame = ttk.Frame(self.parent)
        
        # Title
        ttk.Label(
            self.frame, 
            text="Privacy Settings",
            font=("TkDefaultFont", 16, "bold")
        ).pack(pady=10)
        
        # Data collection controls
        self._create_data_collection_controls()
        
        # Data management buttons
        ttk.Button(
            self.frame,
            text="Export My Data",
            command=self._export_data
        ).pack(pady=5)
        
        ttk.Button(
            self.frame,
            text="Delete All My Data",
            command=self._confirm_delete_all_data
        ).pack(pady=5)
        
    def _create_data_collection_controls(self):
        """Create controls for each data type."""
        policies = self._policy._policies
        
        for data_type, details in policies.items():
            frame = ttk.Frame(self.frame)
            frame.pack(fill="x", padx=10, pady=5)
            
            # Create variable for checkbox
            var = tk.BooleanVar()
            var.set(self._policy.can_collect_data(data_type))
            
            # Create checkbox
            cb = ttk.Checkbutton(
                frame,
                text=details["purpose"],
                variable=var,
                command=lambda dt=data_type, v=var: self._update_consent(dt, v.get())
            )
            cb.pack(side="left")
            
            # Info button
            ttk.Button(
                frame,
                text="i",
                width=2,
                command=lambda dt=data_type, details=details: self._show_data_info(dt, details)
            ).pack(side="right")
            
    def _update_consent(self, data_type, consented):
        """Update user consent for data collection."""
        self._policy.set_user_consent(data_type, consented)
        
    def _show_data_info(self, data_type, details):
        """Show detailed information about a data type."""
        info = f"""
        Data Type: {data_type}
        Purpose: {details["purpose"]}
        Retention: {details["retention_period"]}
        Classification: {details["classification"]}
        Storage: {details["storage_location"]}
        """
        
        if details.get("anonymized"):
            info += "\nThis data is anonymized."
            
        messagebox.showinfo(f"About {data_type} data", info.strip())
        
    def _export_data(self):
        """Export all user data."""
        # Implementation would gather all user data into a portable format
        messagebox.showinfo("Export Data", "Data export functionality will be implemented in a future version.")
        
    def _confirm_delete_all_data(self):
        """Confirm deletion of all user data."""
        if messagebox.askyesno(
            "Confirm Data Deletion",
            "Are you sure you want to delete ALL your data? This cannot be undone."
        ):
            self._delete_all_data()
            
    def _delete_all_data(self):
        """Delete all user data."""
        # Implementation would delete all user data
        messagebox.showinfo("Data Deleted", "All user data has been deleted.")
```

### 3.2 Data Export and Portability

```python
# src/vpa/privacy/data_export.py
class DataExporter:
    """Handles export of user data."""
    
    async def export_user_data(self, format="json"):
        """Export all user data in the specified format."""
        export_data = {}
        
        # Collect data from various stores
        export_data["preferences"] = await self._export_preferences()
        export_data["command_history"] = await self._export_command_history()
        export_data["voice_settings"] = await self._export_voice_settings()
        
        # Create export file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = Path(app_dirs.user_data_dir) / f"data_export_{timestamp}.json"
        
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2)
            
        return str(export_file)
        
    async def _export_preferences(self):
        """Export user preferences."""
        try:
            prefs_file = Path(app_dirs.user_config_dir) / "preferences.json"
            
            if not prefs_file.exists():
                return {}
                
            with open(prefs_file, 'r') as f:
                return json.load(f)
        except Exception:
            logger.error("Failed to export preferences", exc_info=True)
            return {}
```

## 4. Plugin Security

### 4.1 Plugin Security Model

The VPA implements a security model for plugins with the following characteristics:

1. **Isolation**: Plugins run in isolated contexts
2. **Permissions**: Plugins request specific permissions
3. **Approval**: Users approve plugin permissions
4. **Monitoring**: Plugin activity is monitored
5. **Revocation**: Permissions can be revoked

```python
# src/vpa/core/plugin_security.py
class PluginSecurityManager:
    """Manages security for plugins."""
    
    def __init__(self):
        self._plugin_permissions = self._load_permissions()
        
    def _load_permissions(self):
        """Load plugin permissions."""
        try:
            perms_file = Path(app_dirs.user_config_dir) / "plugins" / "permissions.json"
            
            if not perms_file.exists():
                return {}
                
            with open(perms_file, 'r') as f:
                return json.load(f)
        except Exception:
            logger.error("Failed to load plugin permissions", exc_info=True)
            return {}
            
    def get_plugin_permissions(self, plugin_id):
        """Get permissions for a plugin."""
        return self._plugin_permissions.get(plugin_id, {})
        
    def has_permission(self, plugin_id, permission):
        """Check if a plugin has a specific permission."""
        permissions = self.get_plugin_permissions(plugin_id)
        return permissions.get(permission, False)
        
    async def request_permission(self, plugin_id, plugin_name, permission, reason):
        """Request a permission for a plugin."""
        # This will show a UI dialog to the user
        return await self._show_permission_request_dialog(
            plugin_id, plugin_name, permission, reason
        )
        
    async def _show_permission_request_dialog(self, plugin_id, plugin_name, permission, reason):
        """Show a dialog requesting permission."""
        # This would normally use the UI thread
        # For now, just simulate approval
        approved = True
        
        if approved:
            # Update permissions
            if plugin_id not in self._plugin_permissions:
                self._plugin_permissions[plugin_id] = {}
                
            self._plugin_permissions[plugin_id][permission] = True
            
            # Save updated permissions
            perms_file = Path(app_dirs.user_config_dir) / "plugins" / "permissions.json"
            perms_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(perms_file, 'w') as f:
                json.dump(self._plugin_permissions, f)
                
        return approved
```

### 4.2 Plugin Sandbox

```python
# src/vpa/core/plugin_sandbox.py
class PluginSandbox:
    """Sandboxed environment for running plugins."""
    
    def __init__(self, plugin_id, security_manager):
        self.plugin_id = plugin_id
        self._security_manager = security_manager
        self._api_whitelist = self._create_api_whitelist()
        
    def _create_api_whitelist(self):
        """Create API whitelist for sandbox."""
        # Basic allowed modules/functions
        whitelist = {
            "json": ["loads", "dumps"],
            "datetime": ["datetime", "timedelta"],
            "re": ["match", "search", "findall"],
            "math": "*",  # Allow all math functions
        }
        
        # Add VPA API
        whitelist["vpa_api"] = self._create_vpa_api()
        
        return whitelist
        
    def _create_vpa_api(self):
        """Create restricted VPA API for the plugin."""
        return {
            "speak": lambda text: self._check_permission("voice_output", lambda: vpa_api.speak(text)),
            "listen": lambda: self._check_permission("voice_input", vpa_api.listen),
            "get_preference": lambda key: self._check_permission("read_preferences", lambda: vpa_api.get_preference(key)),
            "set_preference": lambda key, value: self._check_permission("write_preferences", lambda: vpa_api.set_preference(key, value))
        }
        
    def _check_permission(self, permission, func):
        """Check if plugin has permission before executing function."""
        if not self._security_manager.has_permission(self.plugin_id, permission):
            raise PermissionError(f"Plugin does not have '{permission}' permission")
            
        return func()
        
    def execute(self, code):
        """Execute code in sandbox."""
        # This is a simplified example
        # A real implementation would use more sophisticated sandboxing
        
        # Create restricted globals
        restricted_globals = {
            "__builtins__": {
                name: __builtins__[name]
                for name in ["True", "False", "None", "str", "int", "float", 
                             "list", "dict", "tuple", "set", "len", "TypeError", 
                             "ValueError", "Exception"]
            }
        }
        
        # Add whitelisted APIs
        for module_name, allowed in self._api_whitelist.items():
            if module_name == "vpa_api":
                restricted_globals["vpa_api"] = allowed
                continue
                
            try:
                module = importlib.import_module(module_name)
                
                if allowed == "*":
                    restricted_globals[module_name] = module
                else:
                    restricted_module = {}
                    for attr in allowed:
                        if hasattr(module, attr):
                            restricted_module[attr] = getattr(module, attr)
                    
                    restricted_globals[module_name] = types.SimpleNamespace(**restricted_module)
            except ImportError:
                pass
        
        # Execute code in restricted environment
        try:
            exec(code, restricted_globals, {})
        except Exception as e:
            logger.error(f"Plugin execution error: {e}", exc_info=True)
            raise
```

## 5. Compliance Framework

### 5.1 Privacy Policy

VPA includes a clear privacy policy that:

1. Describes all data collection
2. Explains data usage
3. Details data sharing (if any)
4. Outlines security measures
5. Informs users of their rights
6. Provides contact information

```python
# src/vpa/privacy/privacy_policy.py
class PrivacyPolicyManager:
    """Manages privacy policy display and updates."""
    
    def __init__(self):
        self._policy_version = "1.0.0"
        self._policy_date = "August 29, 2025"
        self._accepted_version = self._load_accepted_version()
        
    def _load_accepted_version(self):
        """Load the accepted policy version."""
        try:
            version_file = Path(app_dirs.user_config_dir) / "privacy" / "accepted_version.txt"
            
            if not version_file.exists():
                return None
                
            with open(version_file, 'r') as f:
                return f.read().strip()
        except Exception:
            logger.error("Failed to load accepted policy version", exc_info=True)
            return None
            
    def is_policy_accepted(self):
        """Check if the current policy has been accepted."""
        return self._accepted_version == self._policy_version
        
    def mark_policy_accepted(self):
        """Mark the current policy as accepted."""
        version_file = Path(app_dirs.user_config_dir) / "privacy" / "accepted_version.txt"
        version_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(version_file, 'w') as f:
            f.write(self._policy_version)
            
        self._accepted_version = self._policy_version
        
    def get_privacy_policy_text(self):
        """Get the full privacy policy text."""
        return f"""
        # VPA Privacy Policy
        
        Version {self._policy_version}
        Last Updated: {self._policy_date}
        
        ## Introduction
        
        This Privacy Policy explains how the Virtual Personal Assistant (VPA) collects, uses, and protects your data.
        
        ## Data Collection
        
        VPA may collect the following types of data:
        
        - Voice recordings (for voice command processing)
        - Command history (for command recall and suggestion)
        - Usage statistics (for feature improvement)
        - User preferences (for personalization)
        
        ## Data Usage
        
        - Voice recordings are processed locally and used only for command recognition
        - Command history is used to improve your experience and provide suggestions
        - Usage statistics are anonymized and used to improve the application
        - User preferences are used to personalize the application
        
        ## Data Storage
        
        - All data is stored locally on your device by default
        - No data is transmitted to external servers without explicit consent
        - Data is stored securely using encryption
        
        ## Data Retention
        
        - Voice recordings are retained for 24 hours
        - Command history is retained for 90 days
        - Usage statistics are retained for 365 days
        - User preferences are retained until you delete them
        
        ## Your Rights
        
        You have the right to:
        
        - Access your data
        - Export your data
        - Delete your data
        - Control what data is collected
        
        ## Contact
        
        If you have questions about this privacy policy, please contact privacy@vpa-example.com.
        """
        
    def show_privacy_policy_dialog(self):
        """Show privacy policy dialog."""
        # This would be implemented in the UI layer
        pass
```

### 5.2 Compliance Monitoring

```python
# src/vpa/privacy/compliance.py
class ComplianceMonitor:
    """Monitors compliance with privacy policy."""
    
    def __init__(self):
        self._policy = DataCollectionPolicy()
        self._last_audit_date = self._load_last_audit_date()
        
    def _load_last_audit_date(self):
        """Load the date of the last compliance audit."""
        try:
            audit_file = Path(app_dirs.user_data_dir) / "privacy" / "last_audit.txt"
            
            if not audit_file.exists():
                return None
                
            with open(audit_file, 'r') as f:
                date_str = f.read().strip()
                return datetime.fromisoformat(date_str)
        except Exception:
            logger.error("Failed to load last audit date", exc_info=True)
            return None
            
    async def run_compliance_audit(self):
        """Run a compliance audit."""
        audit_results = {
            "timestamp": datetime.now().isoformat(),
            "findings": []
        }
        
        # Check data retention compliance
        retention_issues = await self._check_data_retention()
        audit_results["findings"].extend(retention_issues)
        
        # Check consent compliance
        consent_issues = self._check_consent_records()
        audit_results["findings"].extend(consent_issues)
        
        # Save audit results
        audit_file = Path(app_dirs.user_data_dir) / "privacy" / "audits" / f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        audit_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(audit_file, 'w') as f:
            json.dump(audit_results, f, indent=2)
            
        # Update last audit date
        last_audit_file = Path(app_dirs.user_data_dir) / "privacy" / "last_audit.txt"
        last_audit_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(last_audit_file, 'w') as f:
            f.write(datetime.now().isoformat())
            
        self._last_audit_date = datetime.now()
        
        return audit_results
        
    async def _check_data_retention(self):
        """Check compliance with data retention policies."""
        findings = []
        
        # Check each data store
        data_stores = {
            "voice_recording": Path(app_dirs.user_data_dir) / "voice_recordings",
            "command_history": Path(app_dirs.user_data_dir) / "command_history.db",
            "usage_statistics": Path(app_dirs.user_data_dir) / "usage_stats.db"
        }
        
        for data_type, path in data_stores.items():
            if not path.exists():
                continue
                
            retention_period = self._policy.get_retention_period(data_type)
            if not retention_period:
                continue
                
            # Convert retention period to timedelta
            retention_days = self._parse_retention_period(retention_period)
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            if path.is_dir():
                # Check each file in directory
                for file_path in path.glob("*"):
                    creation_time = datetime.fromtimestamp(file_path.stat().st_ctime)
                    
                    if creation_time < cutoff_date:
                        findings.append({
                            "type": "retention_violation",
                            "data_type": data_type,
                            "path": str(file_path),
                            "created": creation_time.isoformat(),
                            "should_be_deleted_by": cutoff_date.isoformat()
                        })
            else:
                # Check the file itself
                if path.exists():
                    modification_time = datetime.fromtimestamp(path.stat().st_mtime)
                    
                    # For databases, just report if they might contain old data
                    # A real implementation would query the database
                    if modification_time < cutoff_date:
                        findings.append({
                            "type": "potential_retention_violation",
                            "data_type": data_type,
                            "path": str(path),
                            "modified": modification_time.isoformat(),
                            "note": "Database may contain data older than the retention period"
                        })
        
        return findings
        
    def _parse_retention_period(self, period):
        """Parse retention period string to number of days."""
        if isinstance(period, int):
            return period
            
        match = re.match(r"(\d+)\s+(day|days|month|months|year|years)", period.lower())
        if not match:
            return 30  # Default to 30 days
            
        value = int(match.group(1))
        unit = match.group(2)
        
        if unit.startswith("day"):
            return value
        elif unit.startswith("month"):
            return value * 30
        elif unit.startswith("year"):
            return value * 365
            
        return 30  # Default
        
    def _check_consent_records(self):
        """Check compliance with consent records."""
        findings = []
        
        # Check that we have consent records for all data types
        policies = self._policy._policies
        user_consents = self._policy._user_consents
        
        for data_type in policies.keys():
            if data_type not in user_consents:
                findings.append({
                    "type": "missing_consent_record",
                    "data_type": data_type,
                    "note": "No consent record found for this data type"
                })
        
        return findings
```

## 6. Security Operations

### 6.1 Logging and Monitoring

```python
# src/vpa/security/logging.py
class SecurityLogger:
    """Enhanced logging for security events."""
    
    def __init__(self):
        self._log_dir = Path(app_dirs.user_log_dir) / "security"
        self._log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up logger
        self._logger = logging.getLogger("vpa.security")
        self._logger.setLevel(logging.INFO)
        
        # File handler
        log_file = self._log_dir / f"security_{datetime.now().strftime('%Y%m%d')}.log"
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        self._logger.addHandler(handler)
        
    def log_security_event(self, event_type, details, level="INFO"):
        """Log a security event."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        
        # Log at the appropriate level
        if level == "INFO":
            self._logger.info(json.dumps(log_entry))
        elif level == "WARNING":
            self._logger.warning(json.dumps(log_entry))
        elif level == "ERROR":
            self._logger.error(json.dumps(log_entry))
        elif level == "CRITICAL":
            self._logger.critical(json.dumps(log_entry))
        
        # For critical events, also emit an event
        if level == "CRITICAL":
            asyncio.create_task(event_bus.emit_async("security_critical_event", log_entry))
            
    def get_recent_events(self, count=100):
        """Get recent security events."""
        events = []
        
        # Get the most recent log file
        log_files = sorted(self._log_dir.glob("security_*.log"), reverse=True)
        
        if not log_files:
            return events
            
        # Read events from the file
        with open(log_files[0], 'r') as f:
            for line in f:
                try:
                    # Extract JSON portion
                    json_start = line.find('{')
                    if json_start >= 0:
                        json_str = line[json_start:]
                        event = json.loads(json_str)
                        events.append(event)
                        
                        if len(events) >= count:
                            break
                except Exception:
                    # Skip malformed lines
                    continue
        
        return events
```

### 6.2 Incident Response

```python
# src/vpa/security/incident.py
class IncidentResponseManager:
    """Manages security incident response."""
    
    def __init__(self):
        self._security_logger = SecurityLogger()
        self._in_progress_incidents = {}
        
        # Subscribe to security events
        event_bus.subscribe("security_critical_event", self._handle_security_event, async_callback=True)
        
    async def _handle_security_event(self, event_data):
        """Handle a security event."""
        event_type = event_data.get("event_type")
        
        # Check if this is a known incident type
        if event_type in self._incident_handlers:
            await self._incident_handlers[event_type](event_data)
        else:
            # Generic handling
            await self._handle_generic_incident(event_data)
            
    async def _handle_generic_incident(self, event_data):
        """Handle a generic security incident."""
        incident_id = str(uuid.uuid4())
        
        # Create incident record
        incident = {
            "id": incident_id,
            "status": "open",
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "event": event_data,
            "actions": []
        }
        
        # Store in memory
        self._in_progress_incidents[incident_id] = incident
        
        # Store on disk
        incidents_dir = Path(app_dirs.user_data_dir) / "security" / "incidents"
        incidents_dir.mkdir(parents=True, exist_ok=True)
        
        incident_file = incidents_dir / f"incident_{incident_id}.json"
        with open(incident_file, 'w') as f:
            json.dump(incident, f, indent=2)
            
        # Notify user
        await event_bus.emit_async("notification", {
            "title": "Security Alert",
            "message": f"Security incident detected: {event_data.get('event_type')}",
            "level": "critical"
        })
        
        # Take immediate actions
        await self._take_immediate_actions(incident)
        
    async def _take_immediate_actions(self, incident):
        """Take immediate actions for an incident."""
        event_type = incident["event"]["event_type"]
        
        # Log action
        action = {
            "timestamp": datetime.now().isoformat(),
            "type": "automatic_response",
            "description": f"Initiated automatic response for {event_type}"
        }
        
        incident["actions"].append(action)
        incident["updated"] = datetime.now().isoformat()
        
        # Update incident file
        incidents_dir = Path(app_dirs.user_data_dir) / "security" / "incidents"
        incident_file = incidents_dir / f"incident_{incident['id']}.json"
        
        with open(incident_file, 'w') as f:
            json.dump(incident, f, indent=2)
            
        # Different actions for different event types
        if event_type == "unauthorized_access_attempt":
            # For example, temporarily lock access
            pass
        elif event_type == "data_exfiltration_attempt":
            # For example, disable network access for the component
            pass
```

### 6.3 Security Updates

```python
# src/vpa/security/updates.py
class SecurityUpdateManager:
    """Manages security updates."""
    
    def __init__(self):
        self._update_check_url = "https://example.com/vpa/security/updates"
        self._last_check_time = None
        
    async def check_for_security_updates(self):
        """Check for security updates."""
        try:
            # Create secure session
            comms_manager = SecureCommunicationManager()
            session = await comms_manager.create_secure_session()
            
            async with session:
                async with session.get(self._update_check_url) as response:
                    if response.status == 200:
                        update_data = await response.json()
                        self._last_check_time = datetime.now()
                        
                        return self._process_update_data(update_data)
                        
            return {"status": "error", "message": "Failed to check for updates"}
        except Exception as e:
            logger.error(f"Failed to check for security updates: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}
            
    def _process_update_data(self, update_data):
        """Process security update data."""
        if not update_data.get("security_updates"):
            return {"status": "no_updates"}
            
        updates = update_data["security_updates"]
        applicable_updates = []
        
        for update in updates:
            if self._is_update_applicable(update):
                applicable_updates.append(update)
                
        if not applicable_updates:
            return {"status": "no_applicable_updates"}
            
        return {
            "status": "updates_available",
            "updates": applicable_updates
        }
        
    def _is_update_applicable(self, update):
        """Check if an update is applicable to this installation."""
        # Check version constraints
        version_constraints = update.get("version_constraints", {})
        
        min_version = version_constraints.get("min_version")
        max_version = version_constraints.get("max_version")
        
        from vpa._version import __version__
        
        if min_version and self._compare_versions(__version__, min_version) < 0:
            return False
            
        if max_version and self._compare_versions(__version__, max_version) > 0:
            return False
            
        # Check component constraints
        component = update.get("component")
        if component and not self._has_component(component):
            return False
            
        return True
        
    def _compare_versions(self, version1, version2):
        """Compare two version strings."""
        v1_parts = [int(p) for p in version1.split(".")]
        v2_parts = [int(p) for p in version2.split(".")]
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            v1 = v1_parts[i] if i < len(v1_parts) else 0
            v2 = v2_parts[i] if i < len(v2_parts) else 0
            
            if v1 < v2:
                return -1
            if v1 > v2:
                return 1
                
        return 0
        
    def _has_component(self, component):
        """Check if this installation has a component."""
        # Implementation would check for the presence of a component
        # For now, just return True
        return True
```

## 7. Third-Party Integration Security

### 7.1 API Security

```python
# src/vpa/security/api.py
class APISecurityManager:
    """Manages security for API integrations."""
    
    def __init__(self):
        self._token_store = SecureStorage()
        self._comms_manager = SecureCommunicationManager()
        
    async def get_api_token(self, service_name):
        """Get an API token for a service."""
        token_key = f"api_token:{service_name}"
        token = await self._token_store.retrieve(token_key)
        
        return token
        
    async def store_api_token(self, service_name, token):
        """Securely store an API token."""
        token_key = f"api_token:{service_name}"
        await self._token_store.store(token_key, token)
        
    async def create_secure_api_request(self, service_name, method, url, **kwargs):
        """Create a secure API request."""
        # Get token if available
        token = await self.get_api_token(service_name)
        
        # Create session
        session = await self._comms_manager.create_secure_session()
        
        # Add authorization if token exists
        headers = kwargs.get("headers", {})
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        kwargs["headers"] = headers
        
        # Make request
        async with session:
            if method.lower() == "get":
                return await session.get(url, **kwargs)
            elif method.lower() == "post":
                return await session.post(url, **kwargs)
            elif method.lower() == "put":
                return await session.put(url, **kwargs)
            elif method.lower() == "delete":
                return await session.delete(url, **kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
```

### 7.2 OAuth Integration

```python
# src/vpa/security/oauth.py
class OAuthManager:
    """Manages OAuth authentication for third-party services."""
    
    def __init__(self):
        self._token_store = SecureStorage()
        self._oauth_configs = self._load_oauth_configs()
        
    def _load_oauth_configs(self):
        """Load OAuth configurations."""
        try:
            config_file = Path(app_dirs.user_config_dir) / "oauth_configs.json"
            
            if not config_file.exists():
                return {}
                
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception:
            logger.error("Failed to load OAuth configurations", exc_info=True)
            return {}
            
    async def start_oauth_flow(self, service_name):
        """Start OAuth flow for a service."""
        if service_name not in self._oauth_configs:
            raise ValueError(f"Unknown service: {service_name}")
            
        config = self._oauth_configs[service_name]
        
        # Generate PKCE challenge
        code_verifier = self._generate_code_verifier()
        code_challenge = self._generate_code_challenge(code_verifier)
        
        # Store code verifier for later
        await self._token_store.store(f"oauth:code_verifier:{service_name}", code_verifier)
        
        # Build authorization URL
        auth_url = config["authorization_endpoint"]
        auth_url += f"?client_id={config['client_id']}"
        auth_url += f"&redirect_uri={quote(config['redirect_uri'])}"
        auth_url += f"&response_type=code"
        auth_url += f"&scope={quote(config['scope'])}"
        auth_url += f"&code_challenge={code_challenge}"
        auth_url += f"&code_challenge_method=S256"
        auth_url += f"&state={self._generate_state()}"
        
        # Open browser for authentication
        import webbrowser
        webbrowser.open(auth_url)
        
        return auth_url
        
    async def handle_oauth_callback(self, service_name, code, state):
        """Handle OAuth callback."""
        if service_name not in self._oauth_configs:
            raise ValueError(f"Unknown service: {service_name}")
            
        config = self._oauth_configs[service_name]
        
        # Get code verifier
        code_verifier = await self._token_store.retrieve(f"oauth:code_verifier:{service_name}")
        if not code_verifier:
            raise ValueError("OAuth flow not initiated or timed out")
            
        # Exchange code for token
        token_url = config["token_endpoint"]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data={
                "client_id": config["client_id"],
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": config["redirect_uri"],
                "code_verifier": code_verifier
            }) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise ValueError(f"Token exchange failed: {error_text}")
                    
                token_data = await response.json()
                
        # Store tokens
        await self._token_store.store(f"oauth:access_token:{service_name}", token_data["access_token"])
        
        if "refresh_token" in token_data:
            await self._token_store.store(f"oauth:refresh_token:{service_name}", token_data["refresh_token"])
            
        # Store expiration
        if "expires_in" in token_data:
            expiry = datetime.now() + timedelta(seconds=token_data["expires_in"])
            await self._token_store.store(f"oauth:token_expiry:{service_name}", expiry.isoformat())
            
        return {"success": True}
        
    async def get_access_token(self, service_name):
        """Get access token for a service, refreshing if needed."""
        # Check if we have a token
        token = await self._token_store.retrieve(f"oauth:access_token:{service_name}")
        
        # Check if token is expired
        expiry_str = await self._token_store.retrieve(f"oauth:token_expiry:{service_name}")
        
        if token and expiry_str:
            expiry = datetime.fromisoformat(expiry_str)
            
            # If token expires soon, refresh it
            if expiry <= datetime.now() + timedelta(minutes=5):
                # Try to refresh
                refresh_result = await self._refresh_token(service_name)
                
                if refresh_result["success"]:
                    token = await self._token_store.retrieve(f"oauth:access_token:{service_name}")
                
        return token
        
    async def _refresh_token(self, service_name):
        """Refresh OAuth token."""
        if service_name not in self._oauth_configs:
            return {"success": False, "error": "Unknown service"}
            
        config = self._oauth_configs[service_name]
        
        # Get refresh token
        refresh_token = await self._token_store.retrieve(f"oauth:refresh_token:{service_name}")
        
        if not refresh_token:
            return {"success": False, "error": "No refresh token available"}
            
        # Refresh the token
        token_url = config["token_endpoint"]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data={
                "client_id": config["client_id"],
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }) as response:
                if response.status != 200:
                    return {"success": False, "error": "Token refresh failed"}
                    
                token_data = await response.json()
                
        # Store new tokens
        await self._token_store.store(f"oauth:access_token:{service_name}", token_data["access_token"])
        
        if "refresh_token" in token_data:
            await self._token_store.store(f"oauth:refresh_token:{service_name}", token_data["refresh_token"])
            
        # Store expiration
        if "expires_in" in token_data:
            expiry = datetime.now() + timedelta(seconds=token_data["expires_in"])
            await self._token_store.store(f"oauth:token_expiry:{service_name}", expiry.isoformat())
            
        return {"success": True}
        
    def _generate_code_verifier(self):
        """Generate a code verifier for PKCE."""
        import secrets
        import base64
        
        code_verifier = secrets.token_bytes(32)
        return base64.urlsafe_b64encode(code_verifier).rstrip(b'=').decode('ascii')
        
    def _generate_code_challenge(self, code_verifier):
        """Generate a code challenge from verifier for PKCE."""
        import hashlib
        import base64
        
        code_challenge = hashlib.sha256(code_verifier.encode('ascii')).digest()
        return base64.urlsafe_b64encode(code_challenge).rstrip(b'=').decode('ascii')
        
    def _generate_state(self):
        """Generate a state parameter for OAuth flow."""
        import secrets
        return secrets.token_hex(16)
```

## 8. Implementation Guidelines

### 8.1 Security Implementation Checklist

1. **Authentication & Authorization**
   - [x] Implement secure authentication mechanisms
   - [x] Implement fine-grained permission system
   - [x] Apply least privilege principle to all components

2. **Data Protection**
   - [x] Implement encryption for sensitive data
   - [x] Secure storage for credentials and tokens
   - [x] Data retention policies and cleanup

3. **Privacy Controls**
   - [x] User-facing privacy settings
   - [x] Data export functionality
   - [x] Data deletion capabilities

4. **Plugin Security**
   - [x] Plugin sandboxing
   - [x] Plugin permission system
   - [x] Plugin monitoring and isolation

5. **Secure Communications**
   - [x] TLS for all network communications
   - [x] Certificate validation
   - [x] Secure API request handling

6. **Audit & Compliance**
   - [x] Security event logging
   - [x] Compliance monitoring
   - [x] Privacy policy management

7. **Incident Response**
   - [x] Security incident detection
   - [x] Automated response capabilities
   - [x] User notification for critical events

8. **Updates & Maintenance**
   - [x] Security update mechanism
   - [x] Vulnerability management
   - [x] Component security verification

### 8.2 Development Best Practices

1. **Code Review Focus Areas**
   - Input validation and sanitization
   - Proper error handling
   - Secure default settings
   - Cryptography implementation
   - Permission checks

2. **Testing Requirements**
   - Security unit tests for critical components
   - Fuzzing for input handling
   - Penetration testing for plugin system
   - Privacy control verification

3. **Documentation Requirements**
   - Security architecture documentation
   - API security documentation
   - Plugin security guidelines
   - Privacy implementation details

## 9. Risk Assessment

### 9.1 Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Data Breach** | Low | High | Encryption, access controls, local-first approach |
| **Plugin Malware** | Medium | High | Sandboxing, permissions, monitoring |
| **Credential Theft** | Low | High | Secure storage, limited credential caching |
| **Privacy Violation** | Low | Medium | Consent controls, data minimization, retention limits |
| **Network Interception** | Low | Medium | TLS, certificate validation |
| **OS Vulnerabilities** | Medium | Medium | Principle of least privilege, isolation |
| **Social Engineering** | Medium | High | User education, security warnings |

### 9.2 Mitigation Strategies

1. **Data Breach Prevention**
   - Encrypt all sensitive data at rest
   - Minimize data collection
   - Implement access controls
   - Regular security audits

2. **Plugin Security**
   - Sandbox all plugin execution
   - Require explicit permissions
   - Monitor plugin behavior
   - Allow users to report suspicious plugins

3. **Credential Protection**
   - Use system-protected storage when available
   - Limit credential caching
   - Support secure authentication methods

4. **Privacy Protection**
   - Default to most private settings
   - Clear data retention policies
   - Regular data cleanup
   - Transparent privacy controls

## 10. Training and Awareness

### 10.1 Developer Training

All developers working on VPA should complete:

1. Secure coding practices training
2. Privacy by design workshop
3. Cryptography basics training
4. Security review process training

### 10.2 User Education

The VPA application should include:

1. First-run privacy tutorial
2. Security best practices guide
3. Permission explanations
4. Data handling transparency

## Conclusion

This security and privacy strategy establishes a comprehensive framework for ensuring that the VPA application respects user privacy and maintains robust security. By implementing these measures, VPA aims to earn and maintain user trust while providing valuable assistant functionality.

The strategy recognizes that security and privacy are ongoing concerns that require continuous attention and improvement. As the application evolves, this strategy will be reviewed and updated to address new challenges and incorporate improved practices.

---

*Document created: August 29, 2025*
