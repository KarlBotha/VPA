"""
Tests for the conversation database manager.

Tests all must-have requirements:
- M01: Persistent memory across sessions
- M02: View/edit/delete conversation history  
- M03: Store rich user profile data
- M07: Encryption/privacy for history/profile
"""

import pytest
import tempfile
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from vpa.core.database import (
    ConversationDatabaseManager, 
    ConversationRecord, 
    MessageRecord, 
    UserProfile
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = Path(tmp.name)
    
    # Create manager with temp database
    db = ConversationDatabaseManager(db_path=db_path)
    
    yield db
    
    # Clean up
    db.close()
    if db_path.exists():
        db_path.unlink()


class TestConversationDatabaseManager:
    """Test conversation database functionality."""
    
    def test_database_initialization(self, temp_db):
        """Test database initialization creates proper schema."""
        # Database should be initialized without errors
        assert temp_db.db_path.exists()
        assert temp_db.encryption_enabled is True
        
        # Test we can create a conversation (schema works)
        conv_id = temp_db.create_conversation("Test conversation")
        assert conv_id is not None
    
    def test_encryption_setup(self, temp_db):
        """Test encryption is properly configured."""
        test_data = "sensitive information"
        
        # Encrypt and decrypt data
        encrypted = temp_db._encrypt_data(test_data)
        decrypted = temp_db._decrypt_data(encrypted)
        
        assert encrypted != test_data  # Should be encrypted
        assert decrypted == test_data  # Should decrypt back to original


class TestConversationManagement:
    """Test conversation CRUD operations."""
    
    def test_create_conversation(self, temp_db):
        """Test creating a new conversation."""
        title = "Test Conversation"
        metadata = {"topic": "testing", "priority": "high"}
        
        conv_id = temp_db.create_conversation(title=title, metadata=metadata)
        
        assert conv_id is not None
        assert isinstance(conv_id, str)
        
        # Verify conversation was created
        conv = temp_db.get_conversation(conv_id)
        assert conv is not None
        assert conv.title == title
        assert conv.metadata == metadata
        assert conv.message_count == 0
        assert conv.is_pinned is False
    
    def test_create_conversation_with_defaults(self, temp_db):
        """Test creating conversation with default values."""
        conv_id = temp_db.create_conversation()
        
        assert conv_id is not None
        
        conv = temp_db.get_conversation(conv_id)
        assert conv is not None
        assert "Conversation" in conv.title
        assert conv.metadata is None
    
    def test_get_conversations(self, temp_db):
        """Test retrieving conversations."""
        # Create test conversations
        conv1_id = temp_db.create_conversation("First conversation")
        conv2_id = temp_db.create_conversation("Second conversation")
        conv3_id = temp_db.create_conversation("Third conversation", metadata={"pinned": True})
        
        # Pin the third conversation
        temp_db.update_conversation(conv3_id, is_pinned=True)
        
        conversations = temp_db.get_conversations()
        
        assert len(conversations) == 3
        assert all(isinstance(conv, ConversationRecord) for conv in conversations)
        
        # Test pinned first ordering
        conversations_pinned_first = temp_db.get_conversations(include_pinned_first=True)
        assert conversations_pinned_first[0].is_pinned is True
    
    def test_update_conversation(self, temp_db):
        """Test updating conversation details."""
        conv_id = temp_db.create_conversation("Original title")
        
        # Update various fields
        new_title = "Updated title"
        new_metadata = {"updated": True, "version": 2}
        
        success = temp_db.update_conversation(
            conv_id, 
            title=new_title, 
            is_pinned=True, 
            metadata=new_metadata
        )
        
        assert success is True
        
        # Verify updates
        conv = temp_db.get_conversation(conv_id)
        assert conv.title == new_title
        assert conv.is_pinned is True
        assert conv.metadata == new_metadata
    
    def test_update_nonexistent_conversation(self, temp_db):
        """Test updating a conversation that doesn't exist."""
        success = temp_db.update_conversation("nonexistent-id", title="New title")
        assert success is False
    
    def test_delete_conversation(self, temp_db):
        """Test deleting a conversation."""
        conv_id = temp_db.create_conversation("To be deleted")
        
        # Add some messages
        temp_db.add_message(conv_id, "user", "Hello")
        temp_db.add_message(conv_id, "assistant", "Hi there")
        
        # Verify conversation exists
        assert temp_db.get_conversation(conv_id) is not None
        assert len(temp_db.get_messages(conv_id)) == 2
        
        # Delete conversation
        success = temp_db.delete_conversation(conv_id)
        assert success is True
        
        # Verify deletion
        assert temp_db.get_conversation(conv_id) is None
        assert len(temp_db.get_messages(conv_id)) == 0
    
    def test_delete_nonexistent_conversation(self, temp_db):
        """Test deleting a conversation that doesn't exist."""
        success = temp_db.delete_conversation("nonexistent-id")
        assert success is False


class TestMessageManagement:
    """Test message CRUD operations."""
    
    def test_add_message(self, temp_db):
        """Test adding messages to a conversation."""
        conv_id = temp_db.create_conversation("Message test")
        
        # Add user message
        user_content = "Hello, how are you?"
        user_metadata = {"source": "web", "timestamp_ms": 1234567890}
        
        msg_id = temp_db.add_message(
            conv_id, 
            "user", 
            user_content, 
            is_pinned=False, 
            metadata=user_metadata
        )
        
        assert msg_id is not None
        assert isinstance(msg_id, str)
        
        # Add assistant message
        assistant_content = "I'm doing well, thank you!"
        assistant_msg_id = temp_db.add_message(conv_id, "assistant", assistant_content)
        
        # Verify messages were added
        messages = temp_db.get_messages(conv_id)
        assert len(messages) == 2
        
        user_msg = messages[0]
        assert user_msg.role == "user"
        assert user_msg.content == user_content
        assert user_msg.metadata == user_metadata
        assert user_msg.is_pinned is False
        
        assistant_msg = messages[1]
        assert assistant_msg.role == "assistant"
        assert assistant_msg.content == assistant_content
    
    def test_get_messages_with_limit(self, temp_db):
        """Test retrieving messages with limit."""
        conv_id = temp_db.create_conversation("Limit test")
        
        # Add multiple messages
        for i in range(10):
            temp_db.add_message(conv_id, "user", f"Message {i}")
        
        # Test limit
        messages = temp_db.get_messages(conv_id, limit=5)
        assert len(messages) == 5
        
        # Test no limit
        all_messages = temp_db.get_messages(conv_id)
        assert len(all_messages) == 10
    
    def test_pinned_messages_first(self, temp_db):
        """Test that pinned messages appear first."""
        conv_id = temp_db.create_conversation("Pin test")
        
        # Add regular message
        msg1_id = temp_db.add_message(conv_id, "user", "Regular message")
        
        # Add pinned message
        msg2_id = temp_db.add_message(conv_id, "user", "Pinned message", is_pinned=True)
        
        messages = temp_db.get_messages(conv_id, include_pinned_first=True)
        assert messages[0].is_pinned is True
        assert messages[0].content == "Pinned message"
    
    def test_update_message(self, temp_db):
        """Test updating message details."""
        conv_id = temp_db.create_conversation("Update test")
        msg_id = temp_db.add_message(conv_id, "user", "Original content")
        
        new_content = "Updated content"
        new_metadata = {"edited": True, "edit_time": "2025-01-01T12:00:00"}
        
        success = temp_db.update_message(
            msg_id,
            content=new_content,
            is_pinned=True,
            metadata=new_metadata
        )
        
        assert success is True
        
        # Verify updates
        messages = temp_db.get_messages(conv_id)
        updated_msg = messages[0]
        assert updated_msg.content == new_content
        assert updated_msg.is_pinned is True
        assert updated_msg.metadata == new_metadata
    
    def test_delete_message(self, temp_db):
        """Test deleting a message."""
        conv_id = temp_db.create_conversation("Delete test")
        msg1_id = temp_db.add_message(conv_id, "user", "Keep this")
        msg2_id = temp_db.add_message(conv_id, "user", "Delete this")
        
        # Verify both messages exist
        assert len(temp_db.get_messages(conv_id)) == 2
        
        # Delete one message
        success = temp_db.delete_message(msg2_id)
        assert success is True
        
        # Verify deletion
        messages = temp_db.get_messages(conv_id)
        assert len(messages) == 1
        assert messages[0].content == "Keep this"
        
        # Verify conversation message count updated
        conv = temp_db.get_conversation(conv_id)
        assert conv.message_count == 1


class TestUserProfile:
    """Test user profile management."""
    
    def test_create_user_profile(self, temp_db):
        """Test creating a user profile."""
        name = "John Doe"
        preferences = {
            "theme": "dark",
            "language": "en",
            "notifications": True
        }
        context_window_size = 20
        metadata = {"signup_date": "2025-01-01", "plan": "free"}
        
        temp_db.update_user_profile(
            name=name,
            preferences=preferences,
            context_window_size=context_window_size,
            metadata=metadata
        )
        
        profile = temp_db.get_user_profile()
        assert profile is not None
        assert profile.name == name
        assert profile.preferences == preferences
        assert profile.context_window_size == context_window_size
        assert profile.metadata == metadata
        assert profile.created_at is not None
        assert profile.updated_at is not None
    
    def test_update_existing_profile(self, temp_db):
        """Test updating an existing user profile."""
        # Create initial profile
        temp_db.update_user_profile(name="Initial Name", context_window_size=10)
        
        # Update profile
        new_name = "Updated Name"
        new_preferences = {"theme": "light"}
        
        temp_db.update_user_profile(name=new_name, preferences=new_preferences)
        
        profile = temp_db.get_user_profile()
        assert profile.name == new_name
        assert profile.preferences == new_preferences
        assert profile.context_window_size == 10  # Should remain unchanged
    
    def test_get_nonexistent_profile(self, temp_db):
        """Test getting profile when none exists."""
        profile = temp_db.get_user_profile()
        assert profile is None
    
    def test_delete_user_profile(self, temp_db):
        """Test deleting user profile."""
        temp_db.update_user_profile(name="To Delete")
        
        # Verify profile exists
        assert temp_db.get_user_profile() is not None
        
        # Delete profile
        success = temp_db.delete_user_profile()
        assert success is True
        
        # Verify deletion
        assert temp_db.get_user_profile() is None


class TestDataExportAndPrivacy:
    """Test data export and privacy functions."""
    
    def test_export_all_data(self, temp_db):
        """Test exporting all user data."""
        # Create test data
        temp_db.update_user_profile(name="Test User", preferences={"theme": "dark"})
        
        conv_id = temp_db.create_conversation("Test conversation", metadata={"topic": "test"})
        temp_db.add_message(conv_id, "user", "Hello")
        temp_db.add_message(conv_id, "assistant", "Hi there")
        
        # Export data
        export_data = temp_db.export_all_data()
        
        assert "export_timestamp" in export_data
        assert "conversations" in export_data
        assert "user_profile" in export_data
        
        # Verify conversation data
        assert len(export_data["conversations"]) == 1
        conv_data = export_data["conversations"][0]
        assert conv_data["title"] == "Test conversation"
        assert len(conv_data["messages"]) == 2
        
        # Verify user profile data
        profile_data = export_data["user_profile"]
        assert profile_data["name"] == "Test User"
        assert profile_data["preferences"]["theme"] == "dark"
    
    def test_delete_all_conversations(self, temp_db):
        """Test deleting all conversations."""
        # Create test conversations
        conv1_id = temp_db.create_conversation("Conv 1")
        conv2_id = temp_db.create_conversation("Conv 2")
        temp_db.add_message(conv1_id, "user", "Message 1")
        temp_db.add_message(conv2_id, "user", "Message 2")
        
        # Verify conversations exist
        assert len(temp_db.get_conversations()) == 2
        
        # Delete all
        count = temp_db.delete_all_conversations()
        assert count == 2
        
        # Verify deletion
        assert len(temp_db.get_conversations()) == 0
    
    def test_search_conversations(self, temp_db):
        """Test searching conversations by title."""
        temp_db.create_conversation("Python programming help")
        temp_db.create_conversation("JavaScript debugging")
        temp_db.create_conversation("Python data analysis")
        
        # Search for Python
        results = temp_db.search_conversations("Python")
        assert len(results) == 2
        assert all("Python" in conv.title for conv in results)
        
        # Search for specific term
        results = temp_db.search_conversations("debugging")
        assert len(results) == 1
        assert "JavaScript debugging" in results[0].title


class TestEncryptionAndSecurity:
    """Test encryption and security features."""
    
    def test_message_content_encryption(self, temp_db):
        """Test that message content is encrypted in database."""
        conv_id = temp_db.create_conversation("Encryption test")
        sensitive_content = "This is sensitive information"
        
        temp_db.add_message(conv_id, "user", sensitive_content)
        
        # Check database directly to ensure content is encrypted
        with temp_db._lock:
            conn = temp_db._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM messages WHERE conversation_id = ?", (conv_id,))
            stored_content = cursor.fetchone()['content']
            
            # Stored content should be encrypted (different from original)
            assert stored_content != sensitive_content
            
            # But when retrieved through API, should be decrypted
            messages = temp_db.get_messages(conv_id)
            assert messages[0].content == sensitive_content
    
    def test_user_profile_encryption(self, temp_db):
        """Test that user profile data is encrypted."""
        sensitive_name = "Secret Agent 007"
        temp_db.update_user_profile(name=sensitive_name)
        
        # Check database directly
        with temp_db._lock:
            conn = temp_db._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM user_profile WHERE id = 1")
            stored_name = cursor.fetchone()['name']
            
            # Stored name should be encrypted
            assert stored_name != sensitive_name
            
            # But when retrieved through API, should be decrypted
            profile = temp_db.get_user_profile()
            assert profile.name == sensitive_name
    
    def test_conversation_count_updates(self, temp_db):
        """Test that conversation message counts are properly maintained."""
        conv_id = temp_db.create_conversation("Count test")
        
        # Add messages
        temp_db.add_message(conv_id, "user", "Message 1")
        temp_db.add_message(conv_id, "assistant", "Message 2")
        temp_db.add_message(conv_id, "user", "Message 3")
        
        # Check count
        conv = temp_db.get_conversation(conv_id)
        assert conv.message_count == 3
        
        # Delete a message
        messages = temp_db.get_messages(conv_id)
        temp_db.delete_message(messages[0].id)
        
        # Check count updated
        conv = temp_db.get_conversation(conv_id)
        assert conv.message_count == 2


class TestDatabasePersistence:
    """Test persistence across database connections."""
    
    def test_persistence_across_connections(self):
        """Test that data persists when database is reopened."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = Path(tmp.name)
        
        try:
            # Create data with first connection
            with ConversationDatabaseManager(db_path=db_path) as db1:
                conv_id = db1.create_conversation("Persistent conversation")
                db1.add_message(conv_id, "user", "Persistent message")
                db1.update_user_profile(name="Persistent User")
            
            # Open new connection and verify data persists
            with ConversationDatabaseManager(db_path=db_path) as db2:
                conversations = db2.get_conversations()
                assert len(conversations) == 1
                assert conversations[0].title == "Persistent conversation"
                
                messages = db2.get_messages(conversations[0].id)
                assert len(messages) == 1
                assert messages[0].content == "Persistent message"
                
                profile = db2.get_user_profile()
                assert profile.name == "Persistent User"
        
        finally:
            if db_path.exists():
                db_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__])
