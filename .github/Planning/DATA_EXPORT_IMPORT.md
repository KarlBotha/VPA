# Data Export and Import Specification

## Overview

This document specifies the data export and import functionality for VPA, enabling users to backup, transfer, and migrate their data between different VPA installations or versions.

## Table of Contents

1. [Data Structure](#1-data-structure)
2. [Export Functionality](#2-export-functionality)
3. [Import Functionality](#3-import-functionality)
4. [Privacy and Security](#4-privacy-and-security)
5. [Integration Points](#5-integration-points)
6. [Implementation Examples](#6-implementation-examples)

## 1. Data Structure

### 1.1 Export Directory Structure

VPA exports data in a structured directory format:

```
vpa_export_YYYY-MM-DD/
├── export_metadata.json         # Export metadata (version, date, etc.)
├── README.txt                   # Human-readable information
├── settings.json                # User settings
├── personal_data/               # Personal data
│   ├── user_profile.json        # User profile information
│   ├── api_keys.json.enc        # Encrypted API keys
│   └── preferences.json         # User preferences
├── conversations/               # Conversation history
│   ├── conversations.db         # Database of conversations
│   ├── attachments/             # Message attachments
│   └── metadata.json            # Conversation metadata
├── learning_data/               # LLM learning data
│   ├── context_memory.json      # Contextual memory
│   ├── knowledge_base.db        # Knowledge base
│   └── custom_instructions.json # Custom LLM instructions
└── workflows/                   # Custom workflows
    ├── workflow_definitions/    # Workflow definition files
    ├── workflow_data/           # Workflow data files
    └── metadata.json            # Workflow metadata
```

### 1.2 Data Format Standards

VPA uses standardized formats for exported data:

1. **JSON**: For configuration files, metadata, and structured data
2. **SQLite**: For databases (conversations, knowledge base)
3. **Encrypted JSON**: For sensitive data (API keys, credentials)
4. **Binary**: For attachments and non-text data

### 1.3 Metadata Structure

The `export_metadata.json` file contains:

```json
{
  "version": "1.0",
  "export_date": "2025-08-28T10:15:30Z",
  "app_version": "1.5.2",
  "includes": {
    "personal_data": true,
    "conversations": true,
    "learning_data": true,
    "workflows": true
  },
  "sanitized": true,
  "sanitization_level": 2,
  "items": {
    "conversations": 45,
    "workflows": 12,
    "attachments": 23
  },
  "checksum": "sha256:a1b2c3d4e5f6..."
}
```

## 2. Export Functionality

### 2.1 Core Export Manager

The `DataExportManager` class handles data export:

```python
class DataExportManager:
    """Manages data export functionality"""
    
    def __init__(self, settings_manager, event_bus):
        self.settings_manager = settings_manager
        self.event_bus = event_bus
        self.data_sanitizer = DataSanitizer(settings_manager)
        
    async def export_all_data(self, export_path, include_personal=True, include_conversations=True,
                             include_learning_data=True, include_workflows=True,
                             sanitize=True, sanitize_level=1):
        """Export all user data to the specified path"""
        try:
            # Create timestamp for export directory
            timestamp = datetime.now().strftime('%Y-%m-%d')
            export_dir = os.path.join(export_path, f"vpa_export_{timestamp}")
            os.makedirs(export_dir, exist_ok=True)
            
            # Track export statistics
            export_stats = {
                "conversations": 0,
                "workflows": 0,
                "attachments": 0
            }
            
            # Export settings
            settings_path = os.path.join(export_dir, "settings.json")
            await self._export_settings(settings_path, sanitize, sanitize_level)
            
            # Export user data
            if include_personal:
                personal_path = os.path.join(export_dir, "personal_data")
                os.makedirs(personal_path, exist_ok=True)
                await self._export_personal_data(personal_path, sanitize, sanitize_level)
            
            # Export conversations
            if include_conversations:
                conversations_path = os.path.join(export_dir, "conversations")
                os.makedirs(conversations_path, exist_ok=True)
                stats = await self._export_conversations(conversations_path, sanitize, sanitize_level)
                export_stats["conversations"] = stats["conversations"]
                export_stats["attachments"] = stats["attachments"]
            
            # Export LLM learning data
            if include_learning_data:
                learning_path = os.path.join(export_dir, "learning_data")
                os.makedirs(learning_path, exist_ok=True)
                await self._export_learning_data(learning_path, sanitize, sanitize_level)
            
            # Export workflows
            if include_workflows:
                workflows_path = os.path.join(export_dir, "workflows")
                os.makedirs(workflows_path, exist_ok=True)
                stats = await self._export_workflows(workflows_path, sanitize, sanitize_level)
                export_stats["workflows"] = stats["workflows"]
            
            # Create export metadata
            metadata_path = os.path.join(export_dir, "export_metadata.json")
            await self._create_export_metadata(metadata_path, {
                "version": "1.0",
                "export_date": datetime.now().isoformat(),
                "app_version": self.settings_manager.get("app.version", "1.0.0"),
                "includes": {
                    "personal_data": include_personal,
                    "conversations": include_conversations,
                    "learning_data": include_learning_data,
                    "workflows": include_workflows
                },
                "sanitized": sanitize,
                "sanitization_level": sanitize_level,
                "items": export_stats
            })
            
            # Create README file
            readme_path = os.path.join(export_dir, "README.txt")
            with open(readme_path, "w") as f:
                f.write("VPA Data Export\n")
                f.write("==============\n\n")
                f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Application Version: {self.settings_manager.get('app.version', '1.0.0')}\n\n")
                f.write("This directory contains your exported VPA data.\n")
                f.write("To import this data into a new VPA installation, use the 'Import Data' feature.\n\n")
                f.write("Contents:\n")
                if include_personal:
                    f.write("- Personal settings and preferences\n")
                if include_conversations:
                    f.write(f"- {export_stats['conversations']} conversations with {export_stats['attachments']} attachments\n")
                if include_learning_data:
                    f.write("- LLM learning data and knowledge base\n")
                if include_workflows:
                    f.write(f"- {export_stats['workflows']} custom workflows\n")
            
            # Calculate checksum for verification
            checksum = await self._calculate_export_checksum(export_dir)
            
            # Update metadata with checksum
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            metadata["checksum"] = f"sha256:{checksum}"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Emit event indicating export is complete
            await self.event_bus.emit_async("data.export.complete", {
                "export_path": export_dir
            })
            
            return True, export_dir
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            
            # Emit error event
            await self.event_bus.emit_async("data.export.error", {
                "error": str(e)
            })
            
            return False, str(e)
    
    async def _calculate_export_checksum(self, export_dir):
        """Calculate checksum for export verification"""
        import hashlib
        
        sha256_hash = hashlib.sha256()
        
        for root, _, files in os.walk(export_dir):
            for file in sorted(files):
                if file == "export_metadata.json":
                    continue
                filepath = os.path.join(root, file)
                with open(filepath, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                        
        return sha256_hash.hexdigest()
```

### 2.2 Settings Export

```python
async def _export_settings(self, settings_path, sanitize=True, sanitize_level=1):
    """Export user settings"""
    try:
        # Get all settings
        all_settings = self.settings_manager.get_all()
        
        # Remove sensitive settings if sanitizing
        if sanitize:
            sensitive_keys = [
                "api_keys.",
                "credentials.",
                "authentication.",
                "user.email",
                "user.phone"
            ]
            
            sanitized_settings = {}
            for key, value in all_settings.items():
                # Skip sensitive keys
                if any(key.startswith(prefix) for prefix in sensitive_keys):
                    continue
                sanitized_settings[key] = value
        else:
            sanitized_settings = all_settings
        
        # Write settings to file
        with open(settings_path, 'w') as f:
            json.dump(sanitized_settings, f, indent=2)
            
        return True
    except Exception as e:
        logger.error(f"Failed to export settings: {e}")
        return False
```

### 2.3 Conversation Export

```python
async def _export_conversations(self, conversations_path, sanitize=True, sanitize_level=1):
    """Export conversations"""
    try:
        from data.conversation_repository import ConversationRepository
        
        # Statistics
        stats = {
            "conversations": 0,
            "messages": 0,
            "attachments": 0
        }
        
        # Get database path
        db_path = self.settings_manager.get("conversations.db_path")
        
        # Create attachments directory
        attachments_dir = os.path.join(conversations_path, "attachments")
        os.makedirs(attachments_dir, exist_ok=True)
        
        # Export database file
        export_db_path = os.path.join(conversations_path, "conversations.db")
        
        # Create a copy of the database
        import shutil
        shutil.copy2(db_path, export_db_path)
        
        # If sanitizing, need to process the exported database
        if sanitize:
            # Connect to copied database
            import sqlite3
            conn = sqlite3.connect(export_db_path)
            cursor = conn.cursor()
            
            # Get all conversations
            cursor.execute("SELECT id, title FROM conversations")
            conversations = cursor.fetchall()
            stats["conversations"] = len(conversations)
            
            for conv_id, title in conversations:
                # Sanitize conversation title if needed
                if sanitize:
                    sanitized_title = self.data_sanitizer.sanitize_text(title, sanitize_level)
                    if sanitized_title != title:
                        cursor.execute(
                            "UPDATE conversations SET title = ? WHERE id = ?",
                            (sanitized_title, conv_id)
                        )
                
                # Get messages for this conversation
                cursor.execute("SELECT id, text FROM messages WHERE conversation_id = ?", (conv_id,))
                messages = cursor.fetchall()
                stats["messages"] += len(messages)
                
                # Sanitize messages if needed
                if sanitize:
                    for msg_id, text in messages:
                        sanitized_text = self.data_sanitizer.sanitize_text(text, sanitize_level)
                        if sanitized_text != text:
                            cursor.execute(
                                "UPDATE messages SET text = ? WHERE id = ?",
                                (sanitized_text, msg_id)
                            )
            
            # Commit changes and close
            conn.commit()
            conn.close()
        
        # Export attachments
        attachment_dir = os.path.join(os.path.dirname(db_path), "attachments")
        if os.path.exists(attachment_dir):
            for attachment in os.listdir(attachment_dir):
                src = os.path.join(attachment_dir, attachment)
                dst = os.path.join(attachments_dir, attachment)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                    stats["attachments"] += 1
        
        # Create metadata file
        metadata = {
            "export_date": datetime.now().isoformat(),
            "conversations": stats["conversations"],
            "messages": stats["messages"],
            "attachments": stats["attachments"]
        }
        
        with open(os.path.join(conversations_path, "metadata.json"), 'w') as f:
            json.dump(metadata, f, indent=2)
            
        return stats
    except Exception as e:
        logger.error(f"Failed to export conversations: {e}")
        return {"conversations": 0, "messages": 0, "attachments": 0}
```

### 2.4 Learning Data Export

```python
async def _export_learning_data(self, learning_path, sanitize=True, sanitize_level=1):
    """Export LLM learning data"""
    try:
        # Export context memory
        context_memory_path = os.path.join(learning_path, "context_memory.json")
        await self._export_context_memory(context_memory_path, sanitize, sanitize_level)
        
        # Export knowledge base
        kb_path = os.path.join(learning_path, "knowledge_base.db")
        await self._export_knowledge_base(kb_path, sanitize, sanitize_level)
        
        # Export custom instructions
        custom_instructions_path = os.path.join(learning_path, "custom_instructions.json")
        await self._export_custom_instructions(custom_instructions_path, sanitize, sanitize_level)
        
        # Create metadata file
        metadata = {
            "export_date": datetime.now().isoformat()
        }
        
        with open(os.path.join(learning_path, "metadata.json"), 'w') as f:
            json.dump(metadata, f, indent=2)
            
        return True
    except Exception as e:
        logger.error(f"Failed to export learning data: {e}")
        return False
        
async def _export_context_memory(self, context_memory_path, sanitize=True, sanitize_level=1):
    """Export context memory"""
    try:
        # Get context memory from LLM manager
        from core.services import service_locator
        llm_manager = service_locator.get("llm_manager")
        
        if not llm_manager or not hasattr(llm_manager, "context_manager"):
            return False
            
        context_memory = llm_manager.context_manager.export_memory()
        
        # Sanitize if needed
        if sanitize:
            context_memory = self.data_sanitizer.sanitize_json(context_memory, sanitize_level)
            
        # Write to file
        with open(context_memory_path, 'w') as f:
            json.dump(context_memory, f, indent=2)
            
        return True
    except Exception as e:
        logger.error(f"Failed to export context memory: {e}")
        return False
```

### 2.5 Workflow Export

```python
async def _export_workflows(self, workflows_path, sanitize=True, sanitize_level=1):
    """Export custom workflows"""
    try:
        from workflow.workflow_manager import WorkflowManager
        
        # Get workflow manager
        from core.services import service_locator
        workflow_manager = service_locator.get("workflow_manager")
        
        if not workflow_manager:
            return {"workflows": 0}
            
        # Get all workflows
        workflows = workflow_manager.get_all_workflows()
        
        # Create directories
        definitions_dir = os.path.join(workflows_path, "workflow_definitions")
        data_dir = os.path.join(workflows_path, "workflow_data")
        os.makedirs(definitions_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)
        
        # Export each workflow
        for workflow in workflows:
            # Export definition
            definition_path = os.path.join(definitions_dir, f"{workflow.id}.json")
            definition = workflow.to_dict()
            
            # Sanitize if needed
            if sanitize:
                definition = self.data_sanitizer.sanitize_json(definition, sanitize_level)
                
            with open(definition_path, 'w') as f:
                json.dump(definition, f, indent=2)
                
            # Export data
            data_path = os.path.join(data_dir, f"{workflow.id}_data.json")
            data = workflow_manager.get_workflow_data(workflow.id)
            
            # Sanitize if needed
            if sanitize:
                data = self.data_sanitizer.sanitize_json(data, sanitize_level)
                
            with open(data_path, 'w') as f:
                json.dump(data, f, indent=2)
        
        # Create metadata
        metadata = {
            "export_date": datetime.now().isoformat(),
            "workflow_count": len(workflows)
        }
        
        with open(os.path.join(workflows_path, "metadata.json"), 'w') as f:
            json.dump(metadata, f, indent=2)
            
        return {"workflows": len(workflows)}
    except Exception as e:
        logger.error(f"Failed to export workflows: {e}")
        return {"workflows": 0}
```

## 3. Import Functionality

### 3.1 Core Import Manager

The `DataImportManager` class handles data import:

```python
class DataImportManager:
    """Manages data import functionality"""
    
    def __init__(self, settings_manager, event_bus):
        self.settings_manager = settings_manager
        self.event_bus = event_bus
        self.data_validator = DataValidator()
        
    async def import_data(self, import_path, import_settings=True, import_personal=True,
                        import_conversations=True, import_learning_data=True, 
                        import_workflows=True, overwrite=False):
        """Import data from the specified path"""
        try:
            # Verify this is a valid export directory
            metadata_path = os.path.join(import_path, "export_metadata.json")
            if not os.path.exists(metadata_path):
                raise ValueError("Invalid export directory: missing metadata file")
                
            # Read metadata
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
                
            # Validate metadata
            valid, message = self.data_validator.validate_export_format(metadata)
            if not valid:
                raise ValueError(f"Invalid export format: {message}")
                
            # Verify checksum if available
            if "checksum" in metadata:
                checksum = metadata["checksum"].split(":")[1]
                calculated_checksum = await self._calculate_import_checksum(import_path)
                
                if checksum != calculated_checksum:
                    raise ValueError("Export data integrity check failed: checksum mismatch")
            
            # Check version compatibility
            export_version = metadata.get("app_version", "1.0.0")
            current_version = self.settings_manager.get("app.version", "1.0.0")
            
            # Parse versions for comparison
            from packaging import version
            export_ver = version.parse(export_version)
            current_ver = version.parse(current_version)
            
            # Warn about version mismatch if export is from newer version
            if export_ver > current_ver:
                await self.event_bus.emit_async("data.import.warning", {
                    "message": f"The imported data is from a newer version ({export_version}) than the current application ({current_version}). Some features may not import correctly."
                })
            
            # Import settings
            if import_settings and os.path.exists(os.path.join(import_path, "settings.json")):
                settings_path = os.path.join(import_path, "settings.json")
                await self._import_settings(settings_path, overwrite)
            
            # Import personal data
            if import_personal and metadata.get("includes", {}).get("personal_data", False):
                personal_path = os.path.join(import_path, "personal_data")
                if os.path.exists(personal_path):
                    await self._import_personal_data(personal_path, overwrite)
            
            # Import conversations
            if import_conversations and metadata.get("includes", {}).get("conversations", False):
                conversations_path = os.path.join(import_path, "conversations")
                if os.path.exists(conversations_path):
                    await self._import_conversations(conversations_path, overwrite)
            
            # Import LLM learning data
            if import_learning_data and metadata.get("includes", {}).get("learning_data", False):
                learning_path = os.path.join(import_path, "learning_data")
                if os.path.exists(learning_path):
                    await self._import_learning_data(learning_path, overwrite)
            
            # Import workflows
            if import_workflows and metadata.get("includes", {}).get("workflows", False):
                workflows_path = os.path.join(import_path, "workflows")
                if os.path.exists(workflows_path):
                    await self._import_workflows(workflows_path, overwrite)
            
            # Emit event indicating import is complete
            await self.event_bus.emit_async("data.import.complete", {
                "import_path": import_path
            })
            
            return True, "Data import complete"
        except Exception as e:
            logger.error(f"Failed to import data: {e}")
            
            # Emit error event
            await self.event_bus.emit_async("data.import.error", {
                "error": str(e)
            })
            
            return False, str(e)
    
    async def _calculate_import_checksum(self, import_dir):
        """Calculate checksum for import verification"""
        import hashlib
        
        sha256_hash = hashlib.sha256()
        
        for root, _, files in os.walk(import_dir):
            for file in sorted(files):
                if file == "export_metadata.json":
                    continue
                filepath = os.path.join(root, file)
                with open(filepath, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                        
        return sha256_hash.hexdigest()
```

### 3.2 Conversation Import

```python
async def _import_conversations(self, conversations_path, overwrite=False):
    """Import conversations"""
    try:
        # Get destination database path
        db_path = self.settings_manager.get("conversations.db_path")
        
        # Get source database path
        source_db_path = os.path.join(conversations_path, "conversations.db")
        if not os.path.exists(source_db_path):
            logger.error("Conversations database not found in import directory")
            return False
        
        # Import strategy depends on overwrite flag
        if overwrite:
            # Backup existing database
            import shutil
            backup_path = f"{db_path}.backup.{int(time.time())}"
            shutil.copy2(db_path, backup_path)
            
            # Replace database with imported one
            shutil.copy2(source_db_path, db_path)
        else:
            # Merge conversations from imported database
            await self._merge_conversations_db(source_db_path, db_path)
        
        # Import attachments
        source_attachments = os.path.join(conversations_path, "attachments")
        dest_attachments = os.path.join(os.path.dirname(db_path), "attachments")
        
        if os.path.exists(source_attachments):
            os.makedirs(dest_attachments, exist_ok=True)
            
            # Copy attachments
            for attachment in os.listdir(source_attachments):
                src = os.path.join(source_attachments, attachment)
                dst = os.path.join(dest_attachments, attachment)
                if os.path.isfile(src) and (overwrite or not os.path.exists(dst)):
                    shutil.copy2(src, dst)
        
        return True
    except Exception as e:
        logger.error(f"Failed to import conversations: {e}")
        return False

async def _merge_conversations_db(self, source_db, dest_db):
    """Merge conversations from source database to destination database"""
    import sqlite3
    
    # Connect to databases
    source_conn = sqlite3.connect(source_db)
    source_cursor = source_conn.cursor()
    
    dest_conn = sqlite3.connect(dest_db)
    dest_cursor = dest_conn.cursor()
    
    try:
        # Get existing conversation IDs in destination
        dest_cursor.execute("SELECT id FROM conversations")
        existing_ids = set(row[0] for row in dest_cursor.fetchall())
        
        # Get conversations from source
        source_cursor.execute(
            "SELECT id, title, created_at, updated_at FROM conversations"
        )
        conversations = source_cursor.fetchall()
        
        # Import conversations not already in destination
        for conv_id, title, created_at, updated_at in conversations:
            if conv_id not in existing_ids:
                dest_cursor.execute(
                    "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
                    (conv_id, title, created_at, updated_at)
                )
                
                # Get messages for this conversation
                source_cursor.execute(
                    "SELECT id, text, timestamp, is_user FROM messages WHERE conversation_id = ?",
                    (conv_id,)
                )
                messages = source_cursor.fetchall()
                
                # Insert messages
                for msg_id, text, timestamp, is_user in messages:
                    dest_cursor.execute(
                        "INSERT INTO messages (id, conversation_id, text, timestamp, is_user) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (msg_id, conv_id, text, timestamp, is_user)
                    )
        
        # Commit changes
        dest_conn.commit()
        
        return True
    except Exception as e:
        logger.error(f"Failed to merge conversations: {e}")
        return False
    finally:
        source_conn.close()
        dest_conn.close()
```

### 3.3 Learning Data Import

```python
async def _import_learning_data(self, learning_path, overwrite=False):
    """Import LLM learning data"""
    try:
        # Import context memory
        context_memory_path = os.path.join(learning_path, "context_memory.json")
        if os.path.exists(context_memory_path):
            await self._import_context_memory(context_memory_path, overwrite)
        
        # Import knowledge base
        kb_path = os.path.join(learning_path, "knowledge_base.db")
        if os.path.exists(kb_path):
            await self._import_knowledge_base(kb_path, overwrite)
        
        # Import custom instructions
        custom_instructions_path = os.path.join(learning_path, "custom_instructions.json")
        if os.path.exists(custom_instructions_path):
            await self._import_custom_instructions(custom_instructions_path, overwrite)
        
        return True
    except Exception as e:
        logger.error(f"Failed to import learning data: {e}")
        return False

async def _import_context_memory(self, context_memory_path, overwrite=False):
    """Import context memory"""
    try:
        # Read context memory file
        with open(context_memory_path, 'r') as f:
            context_memory = json.load(f)
        
        # Get LLM manager
        from core.services import service_locator
        llm_manager = service_locator.get("llm_manager")
        
        if not llm_manager or not hasattr(llm_manager, "context_manager"):
            return False
        
        # Import memory
        if overwrite:
            llm_manager.context_manager.import_memory(context_memory, clear_existing=True)
        else:
            llm_manager.context_manager.import_memory(context_memory, clear_existing=False)
        
        return True
    except Exception as e:
        logger.error(f"Failed to import context memory: {e}")
        return False
```

## 4. Privacy and Security

### 4.1 Data Sanitization

VPA implements data sanitization to protect privacy:

```python
class DataSanitizer:
    """Sanitizes sensitive information from exported data"""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.sanitize_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            "address": r'\d+\s+[A-Za-z\s]+(?:Road|Rd|Street|St|Avenue|Ave|Boulevard|Blvd|Lane|Ln|Drive|Dr|Terrace|Ter|Place|Pl|Court|Ct)\b',
            "ip": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            "auth_token": r'(bearer|token|auth|jwt)\s+[a-zA-Z0-9_\-\.]+',
            "api_key": r'[a-zA-Z0-9]{32,}'
        }
        
        # Additional patterns for higher sensitivity levels
        self.high_sensitivity_patterns = {
            "name": r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
            "age": r'\b(?:age|aged)\s+\d{1,2}\b',
            "date": r'\b(?:0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](19|20)\d\d\b'
        }
        
    def sanitize_text(self, text, sensitivity_level=1):
        """Sanitize text based on sensitivity level"""
        if sensitivity_level == 0:  # No sanitization
            return text
            
        result = text
        
        # Apply standard patterns
        for pattern_type, pattern in self.sanitize_patterns.items():
            replacement = f"[REDACTED {pattern_type.upper()}]"
            result = re.sub(pattern, replacement, result)
        
        # Apply additional patterns for higher sensitivity levels
        if sensitivity_level >= 2:
            for pattern_type, pattern in self.high_sensitivity_patterns.items():
                replacement = f"[REDACTED {pattern_type.upper()}]"
                result = re.sub(pattern, replacement, result)
        
        # For maximum sensitivity (level 3), replace all numbers
        if sensitivity_level >= 3:
            result = re.sub(r'\b\d+\b', '[REDACTED NUMBER]', result)
        
        return result
        
    def sanitize_json(self, json_data, sensitivity_level=1):
        """Sanitize JSON data"""
        if sensitivity_level == 0:
            return json_data
            
        if isinstance(json_data, dict):
            result = {}
            for key, value in json_data.items():
                # Skip keys that should never be exported
                if key in ["password", "secret", "api_key", "token", "credential"]:
                    result[key] = "[REDACTED]"
                    continue
                    
                if isinstance(value, (dict, list)):
                    result[key] = self.sanitize_json(value, sensitivity_level)
                elif isinstance(value, str):
                    result[key] = self.sanitize_text(value, sensitivity_level)
                else:
                    result[key] = value
            return result
        elif isinstance(json_data, list):
            return [self.sanitize_json(item, sensitivity_level) for item in json_data]
        else:
            return json_data
```

### 4.2 Credential Protection

Sensitive credentials are encrypted before export:

```python
class CredentialManager:
    """Manages secure credentials"""
    
    def __init__(self):
        from security.encryption import EncryptionManager
        self.encryption_manager = EncryptionManager()
        
    def encrypt_credentials(self, credentials_data):
        """Encrypt credentials for export"""
        # Convert to JSON
        credentials_json = json.dumps(credentials_data)
        
        # Encrypt
        encrypted = self.encryption_manager.encrypt_data(credentials_json)
        
        # Return as base64 for storage
        import base64
        return base64.b64encode(encrypted).decode('utf-8')
        
    def decrypt_credentials(self, encrypted_data):
        """Decrypt credentials from import"""
        try:
            # Decode base64
            import base64
            encrypted = base64.b64decode(encrypted_data)
            
            # Decrypt
            decrypted = self.encryption_manager.decrypt_data(encrypted)
            
            # Parse JSON
            return json.loads(decrypted)
        except Exception as e:
            logger.error(f"Failed to decrypt credentials: {e}")
            return {}
```

### 4.3 Data Validation

Import data is validated to ensure integrity:

```python
class DataValidator:
    """Validates data being imported"""
    
    def validate_export_format(self, metadata):
        """Validate export format based on metadata"""
        required_keys = ["version", "export_date", "app_version", "includes"]
        for key in required_keys:
            if key not in metadata:
                return False, f"Missing required key: {key}"
        
        # Check version format
        if "version" in metadata:
            try:
                version_parts = metadata["version"].split(".")
                if len(version_parts) < 2 or not all(part.isdigit() for part in version_parts):
                    return False, "Invalid version format"
            except:
                return False, "Invalid version format"
        
        # Check date format
        if "export_date" in metadata:
            try:
                from dateutil import parser
                parser.parse(metadata["export_date"])
            except:
                return False, "Invalid date format in metadata"
        
        # Check includes format
        if "includes" in metadata and not isinstance(metadata["includes"], dict):
            return False, "Invalid includes format"
            
        return True, "Valid export format"
```

## 5. Integration Points

### 5.1 System Integration

The data export/import system integrates with other VPA components:

1. **Settings Manager**: For reading/writing user settings
2. **Event Bus**: For notifying components about export/import events
3. **Conversation Repository**: For exporting/importing conversations
4. **LLM Manager**: For exporting/importing learning data
5. **Workflow Manager**: For exporting/importing custom workflows

### 5.2 Event Bus Events

The following events are emitted:

```
# Export events
data.export.start             # Export process has started
data.export.progress          # Export progress update
data.export.complete          # Export process is complete
data.export.error             # Error during export

# Import events
data.import.start             # Import process has started
data.import.progress          # Import progress update
data.import.complete          # Import process is complete
data.import.error             # Error during import
data.import.warning           # Warning during import (e.g., version mismatch)
```

### 5.3 UI Integration

The export/import functionality is integrated into the UI through:

1. **Main Menu**: File → Export Data and File → Import Data
2. **Settings Panel**: Data Management section
3. **First Run Wizard**: Option to import data
4. **Uninstall Process**: Option to export data before uninstalling

## 6. Implementation Examples

### 6.1 Integration in Main Window

```python
class MainWindow(QMainWindow):
    def __init__(self, event_bus, settings_manager):
        super().__init__()
        self.event_bus = event_bus
        self.settings_manager = settings_manager
        
        # Create managers
        self.data_export_manager = DataExportManager(settings_manager, event_bus)
        self.data_import_manager = DataImportManager(settings_manager, event_bus)
        
        # Setup UI
        self._setup_ui()
        
    def _setup_ui(self):
        # ... other UI setup ...
        
        # Create menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Export action
        export_action = QAction("Export Data...", self)
        export_action.setStatusTip("Export your data for backup or transfer")
        export_action.triggered.connect(self._show_export_dialog)
        file_menu.addAction(export_action)
        
        # Import action
        import_action = QAction("Import Data...", self)
        import_action.setStatusTip("Import data from a previous export")
        import_action.triggered.connect(self._show_import_dialog)
        file_menu.addAction(import_action)
        
    def _show_export_dialog(self):
        """Show export dialog"""
        dialog = DataExportDialog(self, self.data_export_manager)
        dialog.exec()
        
    def _show_import_dialog(self):
        """Show import dialog"""
        dialog = DataImportDialog(self, self.data_import_manager)
        dialog.exec()
```

### 6.2 Command Line Interface

```python
def add_data_management_commands(parser):
    """Add data management commands to CLI parser"""
    data_parser = parser.add_subparsers(dest="data_command")
    
    # Export command
    export_parser = data_parser.add_parser("export", help="Export data")
    export_parser.add_argument("--output", "-o", help="Output directory", required=True)
    export_parser.add_argument("--include-personal", action="store_true", help="Include personal data")
    export_parser.add_argument("--include-conversations", action="store_true", help="Include conversations")
    export_parser.add_argument("--include-learning", action="store_true", help="Include learning data")
    export_parser.add_argument("--include-workflows", action="store_true", help="Include workflows")
    export_parser.add_argument("--sanitize", action="store_true", help="Sanitize sensitive data")
    export_parser.add_argument("--sanitize-level", type=int, choices=[1, 2, 3], default=1, help="Sanitization level")
    
    # Import command
    import_parser = data_parser.add_parser("import", help="Import data")
    import_parser.add_argument("--input", "-i", help="Input directory", required=True)
    import_parser.add_argument("--include-personal", action="store_true", help="Include personal data")
    import_parser.add_argument("--include-conversations", action="store_true", help="Include conversations")
    import_parser.add_argument("--include-learning", action="store_true", help="Include learning data")
    import_parser.add_argument("--include-workflows", action="store_true", help="Include workflows")
    import_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing data")

async def handle_data_command(args):
    """Handle data management commands"""
    # Setup components
    settings_manager = SettingsManager()
    event_bus = EventBus()
    
    if args.data_command == "export":
        # Create export manager
        export_manager = DataExportManager(settings_manager, event_bus)
        
        # Determine what to include
        include_all = not any([
            args.include_personal,
            args.include_conversations,
            args.include_learning,
            args.include_workflows
        ])
        
        # Perform export
        success, result = await export_manager.export_all_data(
            args.output,
            include_personal=args.include_personal or include_all,
            include_conversations=args.include_conversations or include_all,
            include_learning_data=args.include_learning or include_all,
            include_workflows=args.include_workflows or include_all,
            sanitize=args.sanitize,
            sanitize_level=args.sanitize_level
        )
        
        if success:
            print(f"Data exported successfully to: {result}")
        else:
            print(f"Export failed: {result}")
            sys.exit(1)
    
    elif args.data_command == "import":
        # Create import manager
        import_manager = DataImportManager(settings_manager, event_bus)
        
        # Determine what to include
        include_all = not any([
            args.include_personal,
            args.include_conversations,
            args.include_learning,
            args.include_workflows
        ])
        
        # Perform import
        success, result = await import_manager.import_data(
            args.input,
            import_settings=args.include_personal or include_all,
            import_personal=args.include_personal or include_all,
            import_conversations=args.include_conversations or include_all,
            import_learning_data=args.include_learning or include_all,
            import_workflows=args.include_workflows or include_all,
            overwrite=args.overwrite
        )
        
        if success:
            print("Data imported successfully")
        else:
            print(f"Import failed: {result}")
            sys.exit(1)
```

## Conclusion

The Data Export and Import functionality enables users to backup, transfer, and migrate their data between different VPA installations or versions. The implementation ensures data privacy through sanitization, protects sensitive information through encryption, and validates data integrity during the import process.

By providing a comprehensive export/import system, VPA ensures users have full control over their data and can easily transition between updates or different installations without losing their personalized settings, conversations, or custom workflows.

---

*Document created on August 28, 2025*  
*Version: 1.0*
