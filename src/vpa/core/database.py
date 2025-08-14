"""
Conversation Database Manager for VPA

Provides encrypted persistent storage for conversations, user profiles, and session data.
Implements must-have requirements from the architectural gap analysis.
"""

import sqlite3
import json
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64


@dataclass
class ConversationRecord:
    """Data class for conversation records."""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    is_pinned: bool = False
    metadata: Optional[Dict] = None


@dataclass
class MessageRecord:
    """Data class for message records."""
    id: str
    conversation_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    is_pinned: bool = False
    metadata: Optional[Dict] = None


@dataclass
class UserProfile:
    """Data class for user profile information."""
    name: Optional[str] = None
    preferences: Optional[Dict] = None
    context_window_size: int = 10
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict] = None


class ConversationDatabaseManager:
    """
    Manages encrypted persistent storage for conversations and user data.
    
    Implements requirements:
    - M01: Persistent memory across sessions
    - M02: View/edit/delete conversation history  
    - M03: Store rich user profile data
    - M07: Encryption/privacy for history/profile
    """
    
    def __init__(self, db_path: Optional[Path] = None, encryption_key: Optional[bytes] = None):
        """
        Initialize the conversation database manager.
        
        Args:
            db_path: Path to the database file (defaults to user data directory)
            encryption_key: Encryption key for data protection (auto-generated if None)
        """
        self.logger = logging.getLogger("vpa.database")
        
        # Set up database path
        if db_path is None:
            self.data_dir = Path.home() / ".vpa" / "data"
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = self.data_dir / "conversations.db"
        else:
            self.db_path = Path(db_path)
            self.data_dir = self.db_path.parent
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Set up encryption
        self._setup_encryption(encryption_key)
        
        # Database connection and lock
        self._connection: Optional[sqlite3.Connection] = None
        self._lock = threading.RLock()
        
        # Initialize database
        self._initialize_database()
        
        self.logger.info("Conversation database manager initialized", 
                        extra={"db_path": str(self.db_path), "encryption_enabled": self.encryption_enabled})
    
    def _setup_encryption(self, encryption_key: Optional[bytes] = None) -> None:
        """Set up encryption for sensitive data."""
        self.encryption_enabled = True
        
        if encryption_key is None:
            # Generate or load encryption key
            key_file = self.data_dir / ".vpa_key"
            
            if key_file.exists():
                with open(key_file, 'rb') as f:
                    self._encryption_key = f.read()
            else:
                # Generate new key
                password = os.urandom(32)  # Random password
                salt = os.urandom(16)
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                self._encryption_key = base64.urlsafe_b64encode(kdf.derive(password))
                
                # Save key securely
                with open(key_file, 'wb') as f:
                    f.write(self._encryption_key)
                key_file.chmod(0o600)  # Restrict permissions
        else:
            self._encryption_key = encryption_key
        
        self._cipher = Fernet(self._encryption_key)
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        if not self.encryption_enabled:
            return data
        return self._cipher.encrypt(data.encode()).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        if not self.encryption_enabled:
            return encrypted_data
        return self._cipher.decrypt(encrypted_data.encode()).decode()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with proper setup."""
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
        return self._connection
    
    def _initialize_database(self) -> None:
        """Initialize database schema."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_count INTEGER DEFAULT 0,
                    is_pinned BOOLEAN DEFAULT FALSE,
                    metadata TEXT  -- JSON, encrypted
                )
            """)
            
            # Create messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,  -- Encrypted
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_pinned BOOLEAN DEFAULT FALSE,
                    metadata TEXT,  -- JSON, encrypted
                    FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
                )
            """)
            
            # Create user_profile table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_profile (
                    id INTEGER PRIMARY KEY CHECK (id = 1),  -- Single user only
                    name TEXT,  -- Encrypted
                    preferences TEXT,  -- JSON, encrypted
                    context_window_size INTEGER DEFAULT 10,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT  -- JSON, encrypted
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages (conversation_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages (timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations (updated_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_pinned ON conversations (is_pinned)")
            
            conn.commit()
            
            self.logger.info("Database schema initialized")
    
    def close(self) -> None:
        """Close database connection."""
        with self._lock:
            if self._connection:
                self._connection.close()
                self._connection = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # Conversation Management
    
    def create_conversation(self, title: Optional[str] = None, metadata: Optional[Dict] = None) -> str:
        """
        Create a new conversation.
        
        Args:
            title: Conversation title (auto-generated if None)
            metadata: Additional metadata
            
        Returns:
            Conversation ID
        """
        import uuid
        
        conversation_id = str(uuid.uuid4())
        if title is None:
            title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Encrypt metadata if provided
            encrypted_metadata = None
            if metadata:
                encrypted_metadata = self._encrypt_data(json.dumps(metadata))
            
            cursor.execute("""
                INSERT INTO conversations (id, title, metadata)
                VALUES (?, ?, ?)
            """, (conversation_id, title, encrypted_metadata))
            
            conn.commit()
            
            self.logger.info("Created conversation", 
                           extra={"conversation_id": conversation_id, "title": title})
            
            return conversation_id
    
    def get_conversations(self, limit: int = 50, include_pinned_first: bool = True) -> List[ConversationRecord]:
        """
        Get conversations ordered by last update.
        
        Args:
            limit: Maximum number of conversations to return
            include_pinned_first: Whether to prioritize pinned conversations
            
        Returns:
            List of conversation records
        """
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            order_clause = "ORDER BY is_pinned DESC, updated_at DESC" if include_pinned_first else "ORDER BY updated_at DESC"
            
            cursor.execute(f"""
                SELECT * FROM conversations 
                {order_clause}
                LIMIT ?
            """, (limit,))
            
            conversations = []
            for row in cursor.fetchall():
                metadata = None
                if row['metadata']:
                    metadata = json.loads(self._decrypt_data(row['metadata']))
                
                conversations.append(ConversationRecord(
                    id=row['id'],
                    title=row['title'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    message_count=row['message_count'],
                    is_pinned=bool(row['is_pinned']),
                    metadata=metadata
                ))
            
            return conversations
    
    def get_conversation(self, conversation_id: str) -> Optional[ConversationRecord]:
        """Get a specific conversation by ID."""
        conversations = self.get_conversations(limit=1000)  # Simple implementation
        for conv in conversations:
            if conv.id == conversation_id:
                return conv
        return None
    
    def update_conversation(self, conversation_id: str, title: Optional[str] = None, 
                          is_pinned: Optional[bool] = None, metadata: Optional[Dict] = None) -> bool:
        """
        Update conversation details.
        
        Args:
            conversation_id: ID of conversation to update
            title: New title (optional)
            is_pinned: Pin status (optional)
            metadata: New metadata (optional)
            
        Returns:
            True if conversation was found and updated
        """
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Build update query dynamically
            updates = []
            params = []
            
            if title is not None:
                updates.append("title = ?")
                params.append(title)
            
            if is_pinned is not None:
                updates.append("is_pinned = ?")
                params.append(is_pinned)
            
            if metadata is not None:
                updates.append("metadata = ?")
                params.append(self._encrypt_data(json.dumps(metadata)))
            
            if updates:
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(conversation_id)
                
                query = f"UPDATE conversations SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
                
                success = cursor.rowcount > 0
                conn.commit()
                
                if success:
                    self.logger.info("Updated conversation", 
                                   extra={"conversation_id": conversation_id, "updates": len(updates)-1})
                
                return success
            
            return False
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation and all its messages.
        
        Args:
            conversation_id: ID of conversation to delete
            
        Returns:
            True if conversation was found and deleted
        """
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Delete messages first (foreign key constraint will handle this, but explicit is better)
            cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
            messages_deleted = cursor.rowcount
            
            # Delete conversation
            cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
            conversation_deleted = cursor.rowcount > 0
            
            conn.commit()
            
            if conversation_deleted:
                self.logger.info("Deleted conversation", 
                               extra={"conversation_id": conversation_id, "messages_deleted": messages_deleted})
            
            return conversation_deleted
        
        # Message Management
    
    def add_message(self, conversation_id: str, role: str, content: str, 
                    is_pinned: bool = False, metadata: Optional[Dict] = None) -> str:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: ID of the conversation
            role: Message role ('user' or 'assistant')
            content: Message content (will be encrypted)
            is_pinned: Whether the message is pinned
            metadata: Additional metadata
            
        Returns:
            Message ID
        """
        import uuid
        
        message_id = str(uuid.uuid4())
        
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Encrypt content and metadata
            encrypted_content = self._encrypt_data(content)
            encrypted_metadata = None
            if metadata:
                encrypted_metadata = self._encrypt_data(json.dumps(metadata))
            
            cursor.execute("""
                INSERT INTO messages (id, conversation_id, role, content, is_pinned, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (message_id, conversation_id, role, encrypted_content, is_pinned, encrypted_metadata))
            
            # Update conversation message count and timestamp
            cursor.execute("""
                UPDATE conversations 
                SET message_count = message_count + 1, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (conversation_id,))
            
            conn.commit()
            
            self.logger.info("Added message", 
                           extra={"message_id": message_id, "conversation_id": conversation_id, "role": role})
            
            return message_id
    
    def get_messages(self, conversation_id: str, limit: Optional[int] = None, 
                     include_pinned_first: bool = True) -> List[MessageRecord]:
        """
        Get messages for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of messages to return
            include_pinned_first: Whether to prioritize pinned messages
            
        Returns:
            List of message records
        """
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            order_clause = "ORDER BY is_pinned DESC, timestamp ASC" if include_pinned_first else "ORDER BY timestamp ASC"
            
            if limit:
                query = f"""
                    SELECT * FROM messages 
                    WHERE conversation_id = ? 
                    {order_clause}
                    LIMIT ?
                """
                cursor.execute(query, (conversation_id, limit))
            else:
                query = f"""
                    SELECT * FROM messages 
                    WHERE conversation_id = ? 
                    {order_clause}
                """
                cursor.execute(query, (conversation_id,))
            
            messages = []
            for row in cursor.fetchall():
                # Decrypt content and metadata
                content = self._decrypt_data(row['content'])
                metadata = None
                if row['metadata']:
                    metadata = json.loads(self._decrypt_data(row['metadata']))
                
                messages.append(MessageRecord(
                    id=row['id'],
                    conversation_id=row['conversation_id'],
                    role=row['role'],
                    content=content,
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    is_pinned=bool(row['is_pinned']),
                    metadata=metadata
                ))
            
            return messages
    
    def update_message(self, message_id: str, content: Optional[str] = None,
                      is_pinned: Optional[bool] = None, metadata: Optional[Dict] = None) -> bool:
        """
        Update message details.
        
        Args:
            message_id: ID of message to update
            content: New content (optional)
            is_pinned: Pin status (optional)
            metadata: New metadata (optional)
            
        Returns:
            True if message was found and updated
        """
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Build update query dynamically
            updates = []
            params = []
            
            if content is not None:
                updates.append("content = ?")
                params.append(self._encrypt_data(content))
            
            if is_pinned is not None:
                updates.append("is_pinned = ?")
                params.append(is_pinned)
            
            if metadata is not None:
                updates.append("metadata = ?")
                params.append(self._encrypt_data(json.dumps(metadata)))
            
            if updates:
                params.append(message_id)
                
                query = f"UPDATE messages SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
                
                success = cursor.rowcount > 0
                conn.commit()
                
                if success:
                    self.logger.info("Updated message", 
                                   extra={"message_id": message_id, "updates": len(updates)})
                
                return success
            
            return False
    
    def delete_message(self, message_id: str) -> bool:
        """
        Delete a message.
        
        Args:
            message_id: ID of message to delete
            
        Returns:
            True if message was found and deleted
        """
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get conversation ID for updating count
            cursor.execute("SELECT conversation_id FROM messages WHERE id = ?", (message_id,))
            result = cursor.fetchone()
            if not result:
                return False
            
            conversation_id = result['conversation_id']
            
            # Delete message
            cursor.execute("DELETE FROM messages WHERE id = ?", (message_id,))
            message_deleted = cursor.rowcount > 0
            
            if message_deleted:
                # Update conversation message count
                cursor.execute("""
                    UPDATE conversations 
                    SET message_count = message_count - 1, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (conversation_id,))
            
            conn.commit()
            
            if message_deleted:
                self.logger.info("Deleted message", 
                               extra={"message_id": message_id, "conversation_id": conversation_id})
            
            return message_deleted
    
    # User Profile Management
    
    def get_user_profile(self) -> Optional[UserProfile]:
        """
        Get the user profile (single user system).
        
        Returns:
            User profile or None if not found
        """
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM user_profile WHERE id = 1")
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Decrypt sensitive fields
            name = None
            if row['name']:
                name = self._decrypt_data(row['name'])
            
            preferences = None
            if row['preferences']:
                preferences = json.loads(self._decrypt_data(row['preferences']))
            
            metadata = None
            if row['metadata']:
                metadata = json.loads(self._decrypt_data(row['metadata']))
            
            return UserProfile(
                name=name,
                preferences=preferences,
                context_window_size=row['context_window_size'],
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
                metadata=metadata
            )
    
    def update_user_profile(self, name: Optional[str] = None, preferences: Optional[Dict] = None,
                           context_window_size: Optional[int] = None, metadata: Optional[Dict] = None) -> None:
        """
        Update or create user profile.
        
        Args:
            name: User's name
            preferences: User preferences
            context_window_size: Context window size for conversations
            metadata: Additional metadata
        """
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if profile exists
            cursor.execute("SELECT id FROM user_profile WHERE id = 1")
            exists = cursor.fetchone() is not None
            
            if exists:
                # Update existing profile
                updates = []
                params = []
                
                if name is not None:
                    updates.append("name = ?")
                    params.append(self._encrypt_data(name))
                
                if preferences is not None:
                    updates.append("preferences = ?")
                    params.append(self._encrypt_data(json.dumps(preferences)))
                
                if context_window_size is not None:
                    updates.append("context_window_size = ?")
                    params.append(context_window_size)
                
                if metadata is not None:
                    updates.append("metadata = ?")
                    params.append(self._encrypt_data(json.dumps(metadata)))
                
                if updates:
                    updates.append("updated_at = CURRENT_TIMESTAMP")
                    
                    query = f"UPDATE user_profile SET {', '.join(updates)} WHERE id = 1"
                    cursor.execute(query, params)
                    
                    self.logger.info("Updated user profile", extra={"updates": len(updates)-1})
            else:
                # Create new profile
                encrypted_name = self._encrypt_data(name) if name else None
                encrypted_preferences = self._encrypt_data(json.dumps(preferences)) if preferences else None
                encrypted_metadata = self._encrypt_data(json.dumps(metadata)) if metadata else None
                
                cursor.execute("""
                    INSERT INTO user_profile (id, name, preferences, context_window_size, metadata)
                    VALUES (1, ?, ?, ?, ?)
                """, (encrypted_name, encrypted_preferences, 
                      context_window_size or 10, encrypted_metadata))
                
                self.logger.info("Created user profile")
            
            conn.commit()
    
    def delete_user_profile(self) -> bool:
        """
        Delete the user profile.
        
        Returns:
            True if profile was deleted
        """
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM user_profile WHERE id = 1")
            deleted = cursor.rowcount > 0
            
            conn.commit()
            
            if deleted:
                self.logger.info("Deleted user profile")
            
            return deleted
    
    # Data Export and Privacy Functions
    
    def export_all_data(self) -> Dict[str, Any]:
        """
        Export all user data for backup or portability.
        
        Returns:
            Dictionary containing all user data
        """
        with self._lock:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "conversations": [],
                "user_profile": None
            }
            
            # Export conversations and messages
            conversations = self.get_conversations(limit=10000)  # Get all
            for conv in conversations:
                messages = self.get_messages(conv.id)
                
                conv_data = asdict(conv)
                conv_data['created_at'] = conv.created_at.isoformat()
                conv_data['updated_at'] = conv.updated_at.isoformat()
                conv_data['messages'] = []
                
                for msg in messages:
                    msg_data = asdict(msg)
                    msg_data['timestamp'] = msg.timestamp.isoformat()
                    conv_data['messages'].append(msg_data)
                
                export_data['conversations'].append(conv_data)
            
            # Export user profile
            profile = self.get_user_profile()
            if profile:
                profile_data = asdict(profile)
                if profile.created_at:
                    profile_data['created_at'] = profile.created_at.isoformat()
                if profile.updated_at:
                    profile_data['updated_at'] = profile.updated_at.isoformat()
                export_data['user_profile'] = profile_data
            
            self.logger.info("Exported all user data", 
                           extra={"conversations": len(export_data['conversations'])})
            
            return export_data
    
    def delete_all_conversations(self) -> int:
        """
        Delete all conversations and messages.
        
        Returns:
            Number of conversations deleted
        """
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get count before deletion
            cursor.execute("SELECT COUNT(*) as count FROM conversations")
            count = cursor.fetchone()['count']
            
            # Delete all messages and conversations
            cursor.execute("DELETE FROM messages")
            cursor.execute("DELETE FROM conversations")
            
            conn.commit()
            
            self.logger.info("Deleted all conversations", extra={"count": count})
            
            return count
    
    def search_conversations(self, query: str, limit: int = 20) -> List[ConversationRecord]:
        """
        Search conversations by title (simple text search).
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of matching conversations
        """
        # Note: This is a simple implementation that doesn't search encrypted content
        # For full-text search of encrypted content, we'd need client-side decryption
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM conversations 
                WHERE title LIKE ? 
                ORDER BY updated_at DESC 
                LIMIT ?
            """, (f"%{query}%", limit))
            
            conversations = []
            for row in cursor.fetchall():
                metadata = None
                if row['metadata']:
                    metadata = json.loads(self._decrypt_data(row['metadata']))
                
                conversations.append(ConversationRecord(
                    id=row['id'],
                    title=row['title'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                    message_count=row['message_count'],
                    is_pinned=bool(row['is_pinned']),
                    metadata=metadata
                ))
            
            return conversations
