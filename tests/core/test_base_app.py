"""
Test suite for VPA Base Application.

Tests all core conversation management functionality including:
- Conversation creation and management
- Message handling with encryption
- User profile management
- Data export and privacy features
- Search functionality
"""

import unittest
import tempfile
import json
from datetime import datetime
from pathlib import Path

# Import the base app
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from vpa.core.base_app import VPABaseApp


class TestVPABaseApp(unittest.TestCase):
    """Test suite for VPA Base Application functionality."""
    
    def setUp(self):
        """Set up test environment with temporary database."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.app = VPABaseApp(data_dir=self.temp_dir)
        self.app.__enter__()
    
    def tearDown(self):
        """Clean up test environment."""
        self.app.__exit__(None, None, None)
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)


class TestConversationManagement(TestVPABaseApp):
    """Test conversation creation, updating, and deletion."""
    
    def test_start_new_conversation(self):
        """Test creating a new conversation."""
        conv_id = self.app.start_new_conversation("Test Conversation")
        
        # Verify conversation was created
        self.assertIsNotNone(conv_id)
        self.assertEqual(self.app.current_conversation_id, conv_id)
        
        # Verify conversation appears in list
        conversations = self.app.list_conversations()
        self.assertEqual(len(conversations), 1)
        self.assertEqual(conversations[0]['title'], "Test Conversation")
        self.assertEqual(conversations[0]['id'], conv_id)
    
    def test_auto_generated_conversation_title(self):
        """Test that conversations get auto-generated titles."""
        conv_id = self.app.start_new_conversation()
        
        conversations = self.app.list_conversations()
        self.assertEqual(len(conversations), 1)
        self.assertIn("Conversation", conversations[0]['title'])
        self.assertIn(datetime.now().strftime('%Y-%m-%d'), conversations[0]['title'])
    
    def test_update_conversation_title(self):
        """Test updating conversation title."""
        conv_id = self.app.start_new_conversation("Original Title")
        
        # Update title
        success = self.app.update_conversation_title(conv_id, "New Title")
        self.assertTrue(success)
        
        # Verify title was updated
        conversations = self.app.list_conversations()
        self.assertEqual(conversations[0]['title'], "New Title")
    
    def test_delete_conversation(self):
        """Test deleting a conversation."""
        conv_id = self.app.start_new_conversation("Test Conversation")
        self.app.add_message("Test message", "user")
        
        # Verify conversation exists
        conversations = self.app.list_conversations()
        self.assertEqual(len(conversations), 1)
        
        # Delete conversation
        success = self.app.delete_conversation(conv_id)
        self.assertTrue(success)
        
        # Verify conversation was deleted
        conversations = self.app.list_conversations()
        self.assertEqual(len(conversations), 0)
        
        # Verify current conversation was cleared
        self.assertIsNone(self.app.current_conversation_id)
    
    def test_load_conversation(self):
        """Test loading an existing conversation."""
        # Create multiple conversations
        conv1_id = self.app.start_new_conversation("Conversation 1")
        conv2_id = self.app.start_new_conversation("Conversation 2")
        
        # Load first conversation
        success = self.app.load_conversation(conv1_id)
        self.assertTrue(success)
        self.assertEqual(self.app.current_conversation_id, conv1_id)
        
        # Test loading non-existent conversation
        success = self.app.load_conversation("non-existent-id")
        self.assertFalse(success)


class TestMessageManagement(TestVPABaseApp):
    """Test message adding, retrieval, and management."""
    
    def test_add_message_auto_starts_conversation(self):
        """Test that adding a message auto-starts a conversation."""
        self.assertIsNone(self.app.current_conversation_id)
        
        message_id = self.app.add_message("Hello, VPA!", "user")
        
        # Verify conversation was auto-started
        self.assertIsNotNone(self.app.current_conversation_id)
        self.assertIsNotNone(message_id)
        
        # Verify message was added
        history = self.app.get_conversation_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['content'], "Hello, VPA!")
        self.assertEqual(history[0]['role'], "user")
    
    def test_add_multiple_messages(self):
        """Test adding multiple messages to a conversation."""
        self.app.start_new_conversation("Test Chat")
        
        # Add multiple messages
        self.app.add_message("Hello", "user")
        self.app.add_message("Hi there!", "assistant")
        self.app.add_message("How are you?", "user")
        
        # Verify all messages were added
        history = self.app.get_conversation_history()
        self.assertEqual(len(history), 3)
        
        # Verify message order and content
        self.assertEqual(history[0]['content'], "Hello")
        self.assertEqual(history[0]['role'], "user")
        self.assertEqual(history[1]['content'], "Hi there!")
        self.assertEqual(history[1]['role'], "assistant")
        self.assertEqual(history[2]['content'], "How are you?")
        self.assertEqual(history[2]['role'], "user")
    
    def test_message_metadata(self):
        """Test adding messages with metadata."""
        self.app.start_new_conversation("Test Chat")
        
        metadata = {"source": "test", "priority": "high"}
        message_id = self.app.add_message("Test message", "user", metadata)
        
        history = self.app.get_conversation_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['metadata'], metadata)
    
    def test_get_conversation_history_with_limit(self):
        """Test retrieving conversation history with limit."""
        self.app.start_new_conversation("Test Chat")
        
        # Add multiple messages
        for i in range(5):
            self.app.add_message(f"Message {i+1}", "user")
        
        # Test limit
        history = self.app.get_conversation_history(limit=3)
        self.assertEqual(len(history), 3)
        
        # Test no limit
        history = self.app.get_conversation_history()
        self.assertEqual(len(history), 5)


class TestUserProfileManagement(TestVPABaseApp):
    """Test user profile creation, updating, and retrieval."""
    
    def test_create_user_profile(self):
        """Test creating a user profile."""
        success = self.app.update_user_profile(
            name="Test User",
            preferences={"theme": "dark", "language": "en"},
            metadata={"created_by": "test"}
        )
        self.assertTrue(success)
        
        # Verify profile was created
        profile = self.app.get_user_profile()
        self.assertIsNotNone(profile)
        assert profile is not None  # Type hint for mypy
        self.assertEqual(profile['name'], "Test User")
        self.assertEqual(profile['preferences'], {"theme": "dark", "language": "en"})
        self.assertEqual(profile['metadata'], {"created_by": "test"})
    
    def test_update_existing_profile(self):
        """Test updating an existing user profile."""
        # Create initial profile
        self.app.update_user_profile(name="Initial Name")
        
        # Update profile
        success = self.app.update_user_profile(
            name="Updated Name",
            preferences={"theme": "light"}
        )
        self.assertTrue(success)
        
        # Verify updates
        profile = self.app.get_user_profile()
        self.assertIsNotNone(profile)
        assert profile is not None  # Type hint for mypy
        self.assertEqual(profile['name'], "Updated Name")
        self.assertEqual(profile['preferences'], {"theme": "light"})
    
    def test_partial_profile_updates(self):
        """Test updating only specific profile fields."""
        # Create profile with multiple fields
        self.app.update_user_profile(
            name="Test User",
            preferences={"theme": "dark"},
            metadata={"version": 1}
        )
        
        # Update only preferences
        self.app.update_user_profile(preferences={"theme": "light", "language": "es"})
        
        # Verify only preferences were updated
        profile = self.app.get_user_profile()
        self.assertIsNotNone(profile)
        assert profile is not None  # Type hint for mypy
        self.assertEqual(profile['name'], "Test User")  # Unchanged
        self.assertEqual(profile['preferences'], {"theme": "light", "language": "es"})  # Updated
        self.assertEqual(profile['metadata'], {"version": 1})  # Unchanged
    
    def test_get_nonexistent_profile(self):
        """Test retrieving a profile that doesn't exist."""
        profile = self.app.get_user_profile()
        self.assertIsNone(profile)


class TestDataExportAndPrivacy(TestVPABaseApp):
    """Test data export and privacy features."""
    
    def test_export_all_data(self):
        """Test exporting all user data."""
        # Create test data
        conv_id = self.app.start_new_conversation("Test Export")
        self.app.add_message("Hello", "user")
        self.app.add_message("Hi there!", "assistant")
        self.app.update_user_profile(name="Export User", preferences={"test": True})
        
        # Export data
        export_path = self.app.export_all_data()
        
        # Verify export file exists
        self.assertTrue(export_path.exists())
        
        # Verify export content
        with open(export_path, 'r', encoding='utf-8') as f:
            export_data = json.load(f)
        
        self.assertIn('export_timestamp', export_data)
        self.assertIn('conversations', export_data)
        self.assertIn('user_profile', export_data)
        
        # Verify conversation data
        self.assertEqual(len(export_data['conversations']), 1)
        conv_data = export_data['conversations'][0]
        self.assertEqual(conv_data['title'], "Test Export")
        self.assertEqual(len(conv_data['messages']), 2)
        
        # Verify profile data
        profile_data = export_data['user_profile']
        self.assertEqual(profile_data['name'], "Export User")
        self.assertEqual(profile_data['preferences'], {"test": True})
    
    def test_export_custom_path(self):
        """Test exporting to a custom path."""
        custom_path = self.temp_dir / "custom_export.json"
        
        # Create some data
        self.app.start_new_conversation("Test")
        
        # Export to custom path
        result_path = self.app.export_all_data(custom_path)
        
        self.assertEqual(result_path, custom_path)
        self.assertTrue(custom_path.exists())
    
    def test_delete_all_conversations(self):
        """Test deleting all conversations."""
        # Create multiple conversations
        self.app.start_new_conversation("Conv 1")
        self.app.add_message("Message 1", "user")
        
        conv2_id = self.app.start_new_conversation("Conv 2")
        self.app.add_message("Message 2", "user")
        
        # Verify conversations exist
        conversations = self.app.list_conversations()
        self.assertEqual(len(conversations), 2)
        
        # Delete all conversations
        success = self.app.delete_all_conversations()
        self.assertTrue(success)
        
        # Verify all conversations were deleted
        conversations = self.app.list_conversations()
        self.assertEqual(len(conversations), 0)
        
        # Verify current conversation was cleared
        self.assertIsNone(self.app.current_conversation_id)


class TestSearchFunctionality(TestVPABaseApp):
    """Test conversation search functionality."""
    
    def test_search_conversations(self):
        """Test searching conversations by title."""
        # Create conversations with different titles
        self.app.start_new_conversation("Python Discussion")
        self.app.start_new_conversation("JavaScript Chat")
        self.app.start_new_conversation("Python Advanced Topics")
        
        # Search for Python conversations
        results = self.app.search_conversations("Python")
        self.assertEqual(len(results), 2)
        
        # Verify search results
        titles = [conv['title'] for conv in results]
        self.assertIn("Python Discussion", titles)
        self.assertIn("Python Advanced Topics", titles)
        self.assertNotIn("JavaScript Chat", titles)
    
    def test_search_with_limit(self):
        """Test searching with result limit."""
        # Create multiple matching conversations
        for i in range(5):
            self.app.start_new_conversation(f"Test Conversation {i+1}")
        
        # Search with limit
        results = self.app.search_conversations("Test", limit=3)
        self.assertEqual(len(results), 3)
    
    def test_search_no_results(self):
        """Test searching with no matching results."""
        self.app.start_new_conversation("Python Discussion")
        
        results = self.app.search_conversations("NonExistent")
        self.assertEqual(len(results), 0)


class TestSessionManagement(TestVPABaseApp):
    """Test session and conversation state management."""
    
    def test_current_conversation_info(self):
        """Test getting current conversation information."""
        # No current conversation
        info = self.app.get_current_conversation_info()
        self.assertIsNone(info)
        
        # Create and load conversation
        conv_id = self.app.start_new_conversation("Test Session")
        self.app.add_message("Test message", "user")
        
        # Get current conversation info
        info = self.app.get_current_conversation_info()
        self.assertIsNotNone(info)
        assert info is not None  # Type hint for mypy
        self.assertEqual(info['id'], conv_id)
        self.assertEqual(info['title'], "Test Session")
        self.assertEqual(info['message_count'], 1)
    
    def test_conversation_state_persistence(self):
        """Test that conversation state persists across operations."""
        conv_id = self.app.start_new_conversation("Persistent Session")
        
        # Add some messages
        self.app.add_message("Message 1", "user")
        self.app.add_message("Response 1", "assistant")
        
        # Verify state is maintained
        self.assertEqual(self.app.current_conversation_id, conv_id)
        
        # List conversations (this shouldn't change current conversation)
        conversations = self.app.list_conversations()
        self.assertEqual(self.app.current_conversation_id, conv_id)
        
        # Add another message
        self.app.add_message("Message 2", "user")
        
        # Verify messages are in correct conversation
        history = self.app.get_conversation_history()
        self.assertEqual(len(history), 3)


if __name__ == '__main__':
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)  # Reduce noise during tests
    
    # Run tests
    unittest.main(verbosity=2)
