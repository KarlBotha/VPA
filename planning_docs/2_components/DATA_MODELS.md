# Data Models Specification

## Overview

This document specifies the data models used throughout the VPA system. It defines the structures, relationships, and persistence mechanisms for all data managed by the application. These models provide a consistent foundation for data manipulation, storage, and exchange between components.

## Core Data Model Principles

1. **Type Safety**: All models use strong typing for reliability and IDE assistance
2. **Immutability**: Core data objects are immutable to prevent unexpected state changes
3. **Serialization**: All models can be serialized to/from JSON for storage and transmission
4. **Validation**: Models include validation logic to ensure data integrity
5. **Extensibility**: Models support extension through composition rather than inheritance

## Data Storage Strategy

VPA uses a hybrid data storage approach:

1. **Configuration data**: JSON files in application config directory
2. **User content**: SQLite database for structured data (chat history, preferences)
3. **Cache data**: Memory-cached with disk backup for performance
4. **Large assets**: Stored as files with database references

## Core Data Models

### 1. User Model

Represents user identity and preferences.

```python
# src/vpa/models/user.py
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import datetime
import json

@dataclass(frozen=True)
class UserPreferences:
    """User preferences."""
    
    theme: str = "dark"
    voice_id: str = "en-US-AriaNeural"
    notification_enabled: bool = True
    startup_enabled: bool = True
    minimize_to_tray: bool = True
    speak_responses: bool = True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPreferences':
        """Create preferences from dictionary."""
        return cls(**{
            k: v for k, v in data.items() 
            if k in UserPreferences.__annotations__
        })
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert preferences to dictionary."""
        return {
            "theme": self.theme,
            "voice_id": self.voice_id,
            "notification_enabled": self.notification_enabled,
            "startup_enabled": self.startup_enabled,
            "minimize_to_tray": self.minimize_to_tray,
            "speak_responses": self.speak_responses
        }
        
@dataclass(frozen=True)
class User:
    """User model."""
    
    id: str
    name: str
    email: Optional[str] = None
    preferences: UserPreferences = field(default_factory=UserPreferences)
    created_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now()
    )
    last_active: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now()
    )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary."""
        preferences = UserPreferences.from_dict(
            data.get("preferences", {})
        )
        
        # Handle datetime conversions
        created_at = datetime.datetime.fromisoformat(
            data.get("created_at", datetime.datetime.now().isoformat())
        )
        last_active = datetime.datetime.fromisoformat(
            data.get("last_active", datetime.datetime.now().isoformat())
        )
        
        return cls(
            id=data["id"],
            name=data["name"],
            email=data.get("email"),
            preferences=preferences,
            created_at=created_at,
            last_active=last_active
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "preferences": self.preferences.to_dict(),
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat()
        }
        
    def with_updated_preferences(self, preferences: UserPreferences) -> 'User':
        """Create new user with updated preferences."""
        return User(
            id=self.id,
            name=self.name,
            email=self.email,
            preferences=preferences,
            created_at=self.created_at,
            last_active=datetime.datetime.now()
        )
```

### 2. Message Model

Represents a single message in a conversation.

```python
# src/vpa/models/message.py
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import datetime
import uuid

@dataclass(frozen=True)
class Message:
    """Message model."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    sender_type: str  # "user" or "assistant"
    timestamp: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now()
    )
    input_type: str = "text"  # "text" or "voice"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary."""
        # Handle timestamp conversion
        timestamp = datetime.datetime.fromisoformat(
            data.get("timestamp", datetime.datetime.now().isoformat())
        )
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            content=data["content"],
            sender_type=data["sender_type"],
            timestamp=timestamp,
            input_type=data.get("input_type", "text"),
            metadata=data.get("metadata", {})
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "sender_type": self.sender_type,
            "timestamp": self.timestamp.isoformat(),
            "input_type": self.input_type,
            "metadata": self.metadata
        }
        
    @staticmethod
    def create_user_message(
        content: str,
        input_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'Message':
        """Create a user message."""
        return Message(
            content=content,
            sender_type="user",
            input_type=input_type,
            metadata=metadata or {}
        )
        
    @staticmethod
    def create_assistant_message(
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> 'Message':
        """Create an assistant message."""
        return Message(
            content=content,
            sender_type="assistant",
            input_type="text",
            metadata=metadata or {}
        )
```

### 3. Conversation Model

Represents a complete conversation between the user and assistant.

```python
# src/vpa/models/conversation.py
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import datetime
import uuid
from .message import Message

@dataclass(frozen=True)
class Conversation:
    """Conversation model."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    messages: List[Message] = field(default_factory=list)
    created_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now()
    )
    updated_at: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now()
    )
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create conversation from dictionary."""
        # Handle timestamp conversions
        created_at = datetime.datetime.fromisoformat(
            data.get("created_at", datetime.datetime.now().isoformat())
        )
        updated_at = datetime.datetime.fromisoformat(
            data.get("updated_at", datetime.datetime.now().isoformat())
        )
        
        # Convert message dictionaries to Message objects
        messages = [
            Message.from_dict(msg) for msg in data.get("messages", [])
        ]
        
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data["title"],
            messages=messages,
            created_at=created_at,
            updated_at=updated_at,
            metadata=data.get("metadata", {})
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata
        }
        
    def with_added_message(self, message: Message) -> 'Conversation':
        """Create new conversation with added message."""
        messages = list(self.messages)
        messages.append(message)
        
        return Conversation(
            id=self.id,
            title=self.title,
            messages=messages,
            created_at=self.created_at,
            updated_at=datetime.datetime.now(),
            metadata=self.metadata
        )
        
    def with_updated_title(self, title: str) -> 'Conversation':
        """Create new conversation with updated title."""
        return Conversation(
            id=self.id,
            title=title,
            messages=self.messages,
            created_at=self.created_at,
            updated_at=datetime.datetime.now(),
            metadata=self.metadata
        )
        
    @staticmethod
    def create_new(title: Optional[str] = None) -> 'Conversation':
        """Create a new conversation."""
        title = title or f"Conversation {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        return Conversation(
            title=title
        )
```

### 4. Plugin Configuration Model

Represents the configuration for a plugin.

```python
# src/vpa/models/plugin_config.py
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set
import json

@dataclass(frozen=True)
class PluginPermission:
    """Plugin permission."""
    
    name: str
    description: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert permission to dictionary."""
        return {
            "name": self.name,
            "description": self.description
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'PluginPermission':
        """Create permission from dictionary."""
        return cls(
            name=data["name"],
            description=data["description"]
        )

@dataclass(frozen=True)
class PluginMetadata:
    """Plugin metadata."""
    
    id: str
    name: str
    version: str
    description: str
    author: str
    permissions: List[PluginPermission] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "permissions": [p.to_dict() for p in self.permissions]
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginMetadata':
        """Create metadata from dictionary."""
        permissions = [
            PluginPermission.from_dict(p) 
            for p in data.get("permissions", [])
        ]
        
        return cls(
            id=data["id"],
            name=data["name"],
            version=data["version"],
            description=data["description"],
            author=data["author"],
            permissions=permissions
        )
        
@dataclass(frozen=True)
class PluginConfig:
    """Plugin configuration."""
    
    metadata: PluginMetadata
    enabled: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "metadata": self.metadata.to_dict(),
            "enabled": self.enabled,
            "settings": self.settings
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginConfig':
        """Create configuration from dictionary."""
        metadata = PluginMetadata.from_dict(data["metadata"])
        
        return cls(
            metadata=metadata,
            enabled=data.get("enabled", True),
            settings=data.get("settings", {})
        )
        
    def with_updated_settings(self, settings: Dict[str, Any]) -> 'PluginConfig':
        """Create new configuration with updated settings."""
        merged_settings = {**self.settings, **settings}
        
        return PluginConfig(
            metadata=self.metadata,
            enabled=self.enabled,
            settings=merged_settings
        )
        
    def with_enabled(self, enabled: bool) -> 'PluginConfig':
        """Create new configuration with updated enabled state."""
        return PluginConfig(
            metadata=self.metadata,
            enabled=enabled,
            settings=self.settings
        )
```

### 5. Application Configuration Model

Represents the overall application configuration.

```python
# src/vpa/models/app_config.py
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import json
import os
import logging

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class AudioConfig:
    """Audio configuration."""
    
    input_device: Optional[str] = None
    output_device: Optional[str] = None
    voice_id: str = "en-US-AriaNeural"
    voice_rate: str = "+0%"
    voice_volume: str = "+0%"
    wake_word_enabled: bool = True
    wake_word: str = "hey assistant"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audio config to dictionary."""
        return {
            "input_device": self.input_device,
            "output_device": self.output_device,
            "voice_id": self.voice_id,
            "voice_rate": self.voice_rate,
            "voice_volume": self.voice_volume,
            "wake_word_enabled": self.wake_word_enabled,
            "wake_word": self.wake_word
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioConfig':
        """Create audio config from dictionary."""
        return cls(**{
            k: v for k, v in data.items()
            if k in AudioConfig.__annotations__
        })

@dataclass(frozen=True)
class LLMConfig:
    """Language model configuration."""
    
    model_type: str = "local"
    model_name: str = "default"
    model_path: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1024
    context_window: int = 4096
    memory_limit_mb: int = 4096
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert LLM config to dictionary."""
        return {
            "model_type": self.model_type,
            "model_name": self.model_name,
            "model_path": self.model_path,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "context_window": self.context_window,
            "memory_limit_mb": self.memory_limit_mb
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMConfig':
        """Create LLM config from dictionary."""
        return cls(**{
            k: v for k, v in data.items()
            if k in LLMConfig.__annotations__
        })

@dataclass(frozen=True)
class GUIConfig:
    """GUI configuration."""
    
    theme: str = "dark"
    width: int = 1200
    height: int = 800
    minimize_to_tray: bool = True
    start_minimized: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert GUI config to dictionary."""
        return {
            "theme": self.theme,
            "width": self.width,
            "height": self.height,
            "minimize_to_tray": self.minimize_to_tray,
            "start_minimized": self.start_minimized
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GUIConfig':
        """Create GUI config from dictionary."""
        return cls(**{
            k: v for k, v in data.items()
            if k in GUIConfig.__annotations__
        })

@dataclass(frozen=True)
class AppConfig:
    """Application configuration."""
    
    user_id: str
    data_dir: str
    log_level: str = "INFO"
    headless: bool = False
    speak_responses: bool = True
    audio: AudioConfig = field(default_factory=AudioConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    gui: GUIConfig = field(default_factory=GUIConfig)
    plugins: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert app config to dictionary."""
        return {
            "user_id": self.user_id,
            "data_dir": self.data_dir,
            "log_level": self.log_level,
            "headless": self.headless,
            "speak_responses": self.speak_responses,
            "audio": self.audio.to_dict(),
            "llm": self.llm.to_dict(),
            "gui": self.gui.to_dict(),
            "plugins": self.plugins
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """Create app config from dictionary."""
        audio_config = AudioConfig.from_dict(data.get("audio", {}))
        llm_config = LLMConfig.from_dict(data.get("llm", {}))
        gui_config = GUIConfig.from_dict(data.get("gui", {}))
        
        return cls(
            user_id=data["user_id"],
            data_dir=data["data_dir"],
            log_level=data.get("log_level", "INFO"),
            headless=data.get("headless", False),
            speak_responses=data.get("speak_responses", True),
            audio=audio_config,
            llm=llm_config,
            gui=gui_config,
            plugins=data.get("plugins", {})
        )
        
    @classmethod
    def load_from_file(cls, config_path: str) -> 'AppConfig':
        """Load configuration from file."""
        try:
            with open(config_path, "r") as f:
                data = json.load(f)
                return cls.from_dict(data)
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in config file: {config_path}")
            raise
            
    def save_to_file(self, config_path: str) -> None:
        """Save configuration to file."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        try:
            with open(config_path, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config to {config_path}: {e}")
            raise
            
    def with_updated_audio(self, audio: AudioConfig) -> 'AppConfig':
        """Create new config with updated audio configuration."""
        return AppConfig(
            user_id=self.user_id,
            data_dir=self.data_dir,
            log_level=self.log_level,
            headless=self.headless,
            speak_responses=self.speak_responses,
            audio=audio,
            llm=self.llm,
            gui=self.gui,
            plugins=self.plugins
        )
        
    def with_updated_llm(self, llm: LLMConfig) -> 'AppConfig':
        """Create new config with updated LLM configuration."""
        return AppConfig(
            user_id=self.user_id,
            data_dir=self.data_dir,
            log_level=self.log_level,
            headless=self.headless,
            speak_responses=self.speak_responses,
            audio=self.audio,
            llm=llm,
            gui=self.gui,
            plugins=self.plugins
        )
        
    def with_updated_gui(self, gui: GUIConfig) -> 'AppConfig':
        """Create new config with updated GUI configuration."""
        return AppConfig(
            user_id=self.user_id,
            data_dir=self.data_dir,
            log_level=self.log_level,
            headless=self.headless,
            speak_responses=self.speak_responses,
            audio=self.audio,
            llm=self.llm,
            gui=gui,
            plugins=self.plugins
        )
        
    def with_updated_plugin_config(
        self,
        plugin_id: str,
        config: Dict[str, Any]
    ) -> 'AppConfig':
        """Create new config with updated plugin configuration."""
        plugins = dict(self.plugins)
        plugins[plugin_id] = config
        
        return AppConfig(
            user_id=self.user_id,
            data_dir=self.data_dir,
            log_level=self.log_level,
            headless=self.headless,
            speak_responses=self.speak_responses,
            audio=self.audio,
            llm=self.llm,
            gui=self.gui,
            plugins=plugins
        )
```

## Data Access Layer

The Data Access Layer provides a consistent interface for storing and retrieving model data.

### 1. Repository Pattern

```python
# src/vpa/data/repository.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any
import logging

T = TypeVar('T')
ID = TypeVar('ID')

logger = logging.getLogger(__name__)

class Repository(Generic[T, ID], ABC):
    """Base repository interface."""
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        """Save an entity.
        
        Args:
            entity: Entity to save
            
        Returns:
            Saved entity
        """
        pass
        
    @abstractmethod
    async def find_by_id(self, id: ID) -> Optional[T]:
        """Find an entity by ID.
        
        Args:
            id: Entity ID
            
        Returns:
            Entity if found, None otherwise
        """
        pass
        
    @abstractmethod
    async def find_all(self) -> List[T]:
        """Find all entities.
        
        Returns:
            List of all entities
        """
        pass
        
    @abstractmethod
    async def delete(self, id: ID) -> bool:
        """Delete an entity by ID.
        
        Args:
            id: Entity ID
            
        Returns:
            True if entity was deleted, False otherwise
        """
        pass
        
    @abstractmethod
    async def exists(self, id: ID) -> bool:
        """Check if an entity exists.
        
        Args:
            id: Entity ID
            
        Returns:
            True if entity exists, False otherwise
        """
        pass
```

### 2. SQLite Conversation Repository

```python
# src/vpa/data/conversation_repository.py
from typing import List, Optional, Dict, Any
import aiosqlite
import json
import logging
from .repository import Repository
from vpa.models.conversation import Conversation
from vpa.models.message import Message

logger = logging.getLogger(__name__)

class ConversationRepository(Repository[Conversation, str]):
    """Repository for conversations stored in SQLite."""
    
    def __init__(self, db_path: str):
        """Initialize conversation repository.
        
        Args:
            db_path: Path to SQLite database
        """
        self._db_path = db_path
        
    async def initialize(self):
        """Initialize the repository."""
        async with aiosqlite.connect(self._db_path) as db:
            # Create conversations table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT
                )
            ''')
            
            # Create messages table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    sender_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    input_type TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                )
            ''')
            
            await db.commit()
            logger.info(f"Conversation repository initialized at {self._db_path}")
            
    async def save(self, conversation: Conversation) -> Conversation:
        """Save a conversation.
        
        Args:
            conversation: Conversation to save
            
        Returns:
            Saved conversation
        """
        async with aiosqlite.connect(self._db_path) as db:
            # Save conversation
            metadata_json = json.dumps(conversation.metadata)
            
            await db.execute('''
                INSERT OR REPLACE INTO conversations
                (id, title, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                conversation.id,
                conversation.title,
                conversation.created_at.isoformat(),
                conversation.updated_at.isoformat(),
                metadata_json
            ))
            
            # Delete existing messages for this conversation
            await db.execute('''
                DELETE FROM messages WHERE conversation_id = ?
            ''', (conversation.id,))
            
            # Save messages
            for message in conversation.messages:
                metadata_json = json.dumps(message.metadata)
                
                await db.execute('''
                    INSERT OR REPLACE INTO messages
                    (id, conversation_id, content, sender_type, timestamp, input_type, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    message.id,
                    conversation.id,
                    message.content,
                    message.sender_type,
                    message.timestamp.isoformat(),
                    message.input_type,
                    metadata_json
                ))
                
            await db.commit()
            logger.debug(f"Saved conversation: {conversation.id}")
            
            return conversation
            
    async def find_by_id(self, id: str) -> Optional[Conversation]:
        """Find a conversation by ID.
        
        Args:
            id: Conversation ID
            
        Returns:
            Conversation if found, None otherwise
        """
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Get conversation
            cursor = await db.execute('''
                SELECT * FROM conversations WHERE id = ?
            ''', (id,))
            row = await cursor.fetchone()
            
            if not row:
                return None
                
            # Get messages
            cursor = await db.execute('''
                SELECT * FROM messages
                WHERE conversation_id = ?
                ORDER BY timestamp ASC
            ''', (id,))
            message_rows = await cursor.fetchall()
            
            # Convert to message objects
            messages = []
            for msg_row in message_rows:
                metadata = json.loads(msg_row["metadata"]) if msg_row["metadata"] else {}
                
                messages.append(Message(
                    id=msg_row["id"],
                    content=msg_row["content"],
                    sender_type=msg_row["sender_type"],
                    timestamp=msg_row["timestamp"],
                    input_type=msg_row["input_type"],
                    metadata=metadata
                ))
                
            # Convert to conversation object
            metadata = json.loads(row["metadata"]) if row["metadata"] else {}
            
            return Conversation(
                id=row["id"],
                title=row["title"],
                messages=messages,
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                metadata=metadata
            )
            
    async def find_all(self) -> List[Conversation]:
        """Find all conversations.
        
        Returns:
            List of all conversations
        """
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Get all conversation IDs
            cursor = await db.execute('''
                SELECT id FROM conversations ORDER BY updated_at DESC
            ''')
            rows = await cursor.fetchall()
            
            # Load each conversation
            conversations = []
            for row in rows:
                conversation = await self.find_by_id(row["id"])
                if conversation:
                    conversations.append(conversation)
                    
            return conversations
            
    async def delete(self, id: str) -> bool:
        """Delete a conversation by ID.
        
        Args:
            id: Conversation ID
            
        Returns:
            True if conversation was deleted, False otherwise
        """
        async with aiosqlite.connect(self._db_path) as db:
            cursor = await db.execute('''
                DELETE FROM conversations WHERE id = ?
            ''', (id,))
            
            await db.commit()
            return cursor.rowcount > 0
            
    async def exists(self, id: str) -> bool:
        """Check if a conversation exists.
        
        Args:
            id: Conversation ID
            
        Returns:
            True if conversation exists, False otherwise
        """
        async with aiosqlite.connect(self._db_path) as db:
            cursor = await db.execute('''
                SELECT COUNT(*) FROM conversations WHERE id = ?
            ''', (id,))
            
            row = await cursor.fetchone()
            return row[0] > 0
            
    async def find_recent(self, limit: int = 10) -> List[Conversation]:
        """Find recent conversations.
        
        Args:
            limit: Maximum number of conversations to return
            
        Returns:
            List of recent conversations
        """
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Get recent conversation IDs
            cursor = await db.execute('''
                SELECT id FROM conversations
                ORDER BY updated_at DESC
                LIMIT ?
            ''', (limit,))
            
            rows = await cursor.fetchall()
            
            # Load each conversation
            conversations = []
            for row in rows:
                conversation = await self.find_by_id(row["id"])
                if conversation:
                    conversations.append(conversation)
                    
            return conversations
```

### 3. JSON Configuration Repository

```python
# src/vpa/data/config_repository.py
from typing import Optional
import json
import os
import logging
import asyncio
from vpa.models.app_config import AppConfig

logger = logging.getLogger(__name__)

class ConfigRepository:
    """Repository for application configuration stored in JSON."""
    
    def __init__(self, config_path: str):
        """Initialize configuration repository.
        
        Args:
            config_path: Path to configuration file
        """
        self._config_path = config_path
        self._lock = asyncio.Lock()
        
    async def load(self) -> Optional[AppConfig]:
        """Load configuration.
        
        Returns:
            Application configuration or None if not found
        """
        async with self._lock:
            try:
                if not os.path.exists(self._config_path):
                    logger.warning(f"Config file not found: {self._config_path}")
                    return None
                    
                with open(self._config_path, "r") as f:
                    data = json.load(f)
                    return AppConfig.from_dict(data)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in config file: {self._config_path}")
                return None
            except Exception as e:
                logger.error(f"Failed to load config from {self._config_path}: {e}")
                return None
                
    async def save(self, config: AppConfig) -> bool:
        """Save configuration.
        
        Args:
            config: Application configuration
            
        Returns:
            True if configuration was saved successfully
        """
        async with self._lock:
            try:
                # Ensure directory exists
                os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
                
                with open(self._config_path, "w") as f:
                    json.dump(config.to_dict(), f, indent=2)
                    
                logger.debug(f"Saved config to {self._config_path}")
                return True
            except Exception as e:
                logger.error(f"Failed to save config to {self._config_path}: {e}")
                return False
```

## Data Validation

Validation ensures that data models remain consistent and valid throughout the application lifecycle.

### 1. Validator Interface

```python
# src/vpa/validation/validator.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Dict, Any

T = TypeVar('T')

class ValidationError:
    """Validation error."""
    
    def __init__(self, field: str, message: str):
        """Initialize validation error.
        
        Args:
            field: Field name
            message: Error message
        """
        self.field = field
        self.message = message
        
    def __str__(self):
        return f"{self.field}: {self.message}"

class ValidationResult:
    """Result of validation."""
    
    def __init__(self, valid: bool, errors: List[ValidationError] = None):
        """Initialize validation result.
        
        Args:
            valid: Whether validation passed
            errors: List of validation errors
        """
        self.valid = valid
        self.errors = errors or []
        
    def __bool__(self):
        return self.valid
        
    def __str__(self):
        if self.valid:
            return "Valid"
        return f"Invalid: {', '.join(str(e) for e in self.errors)}"

class Validator(Generic[T], ABC):
    """Validator interface."""
    
    @abstractmethod
    def validate(self, value: T) -> ValidationResult:
        """Validate a value.
        
        Args:
            value: Value to validate
            
        Returns:
            Validation result
        """
        pass
```

### 2. Message Validator

```python
# src/vpa/validation/message_validator.py
from .validator import Validator, ValidationResult, ValidationError
from vpa.models.message import Message

class MessageValidator(Validator[Message]):
    """Validator for messages."""
    
    def validate(self, message: Message) -> ValidationResult:
        """Validate a message.
        
        Args:
            message: Message to validate
            
        Returns:
            Validation result
        """
        errors = []
        
        # Check required fields
        if not message.id:
            errors.append(ValidationError("id", "ID is required"))
            
        if not message.content:
            errors.append(ValidationError("content", "Content is required"))
            
        # Check sender type
        valid_sender_types = {"user", "assistant"}
        if message.sender_type not in valid_sender_types:
            errors.append(ValidationError(
                "sender_type", 
                f"Invalid sender type: {message.sender_type}. "
                f"Must be one of: {', '.join(valid_sender_types)}"
            ))
            
        # Check input type
        valid_input_types = {"text", "voice"}
        if message.input_type not in valid_input_types:
            errors.append(ValidationError(
                "input_type",
                f"Invalid input type: {message.input_type}. "
                f"Must be one of: {', '.join(valid_input_types)}"
            ))
            
        # Check timestamp
        if not message.timestamp:
            errors.append(ValidationError("timestamp", "Timestamp is required"))
            
        return ValidationResult(not errors, errors)
```

### 3. User Validator

```python
# src/vpa/validation/user_validator.py
from .validator import Validator, ValidationResult, ValidationError
from vpa.models.user import User
import re

class UserValidator(Validator[User]):
    """Validator for users."""
    
    def validate(self, user: User) -> ValidationResult:
        """Validate a user.
        
        Args:
            user: User to validate
            
        Returns:
            Validation result
        """
        errors = []
        
        # Check required fields
        if not user.id:
            errors.append(ValidationError("id", "ID is required"))
            
        if not user.name:
            errors.append(ValidationError("name", "Name is required"))
            
        # Check email format if provided
        if user.email:
            email_pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
            if not email_pattern.match(user.email):
                errors.append(ValidationError("email", "Invalid email format"))
                
        return ValidationResult(not errors, errors)
```

## Data Events

The system uses events to communicate data changes throughout the application.

### Data Event Types

| Event Name | Description | Data |
|------------|-------------|------|
| `config_changed` | Configuration has been updated | `{"config": AppConfig}` |
| `conversation_created` | New conversation created | `{"conversation": Conversation}` |
| `conversation_updated` | Conversation updated | `{"conversation": Conversation, "previous": Conversation}` |
| `conversation_deleted` | Conversation deleted | `{"conversation_id": str}` |
| `message_added` | Message added to conversation | `{"conversation_id": str, "message": Message}` |
| `plugin_config_changed` | Plugin configuration changed | `{"plugin_id": str, "config": PluginConfig}` |

## Usage Examples

### Creating and Storing a Conversation

```python
# Example of creating and storing a conversation
from vpa.models.conversation import Conversation
from vpa.models.message import Message
from vpa.data.conversation_repository import ConversationRepository
import asyncio

async def example_conversation_workflow():
    # Initialize repository
    repo = ConversationRepository("./data/conversations.db")
    await repo.initialize()
    
    # Create a new conversation
    conversation = Conversation.create_new("Weather Discussion")
    
    # Add messages
    user_message = Message.create_user_message("What's the weather today?")
    conversation = conversation.with_added_message(user_message)
    
    assistant_message = Message.create_assistant_message(
        "The weather today is sunny with a high of 75°F."
    )
    conversation = conversation.with_added_message(assistant_message)
    
    # Save conversation
    saved_conversation = await repo.save(conversation)
    print(f"Saved conversation: {saved_conversation.id}")
    
    # Retrieve conversation
    retrieved = await repo.find_by_id(saved_conversation.id)
    print(f"Retrieved conversation with {len(retrieved.messages)} messages")
    
    # List recent conversations
    recent = await repo.find_recent(5)
    print(f"Found {len(recent)} recent conversations")
    
# Run the example
asyncio.run(example_conversation_workflow())
```

### Managing Application Configuration

```python
# Example of managing application configuration
from vpa.models.app_config import AppConfig, AudioConfig
from vpa.data.config_repository import ConfigRepository
from vpa.core.events import event_bus
import asyncio
import os

async def example_config_workflow():
    # Initialize repository
    config_dir = os.path.expanduser("~/.vpa")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "config.json")
    
    repo = ConfigRepository(config_path)
    
    # Create default config
    default_config = AppConfig(
        user_id="default_user",
        data_dir=os.path.join(config_dir, "data")
    )
    
    # Save default config
    success = await repo.save(default_config)
    print(f"Saved default config: {success}")
    
    # Load config
    config = await repo.load()
    print(f"Loaded config for user: {config.user_id}")
    
    # Update audio config
    new_audio_config = AudioConfig(
        voice_id="en-GB-SoniaNeural",
        wake_word="hey computer"
    )
    updated_config = config.with_updated_audio(new_audio_config)
    
    # Save updated config
    await repo.save(updated_config)
    
    # Emit config changed event
    event_bus.emit("config_changed", {"config": updated_config})
    
# Run the example
asyncio.run(example_config_workflow())
```

## Data Migration Strategy

As the application evolves, data models will need to change. The following strategy ensures backward compatibility:

1. **Version Tracking**: Each data model includes a version field
2. **Migration Scripts**: Dedicated scripts for upgrading data from one version to another
3. **Schema Validation**: On startup, validate schema version and migrate if necessary
4. **Backup Before Migration**: Automatic backup of data before migration
5. **Rollback Support**: Ability to restore from backup if migration fails

## Performance Considerations

1. **Lazy Loading**: Messages are loaded only when needed, not with conversation list
2. **Caching**: Frequently accessed objects are cached in memory
3. **Connection Pooling**: Database connections are pooled for efficiency
4. **Batch Operations**: Bulk operations are used where possible
5. **Indexing**: Database indexes on frequently queried fields

## Conclusion

This document specifies the data models used throughout the VPA system. These models provide a consistent foundation for data manipulation, storage, and exchange between components. By following the patterns and practices outlined in this document, developers can ensure that data is handled consistently and efficiently throughout the application.

---

*Document created: August 29, 2025*
