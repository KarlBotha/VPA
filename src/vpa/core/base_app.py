"""
VPA Base Application - Core conversation management interface.

This module implements the foundational base app requirements:
- M01: Persistent memory across sessions
- M02: View/edit/delete conversation history  
- M03: Store rich user profile data
- M05: Start new conversation
- M06: Export/delete full chat history
- M07: Encryption/privacy for history/profile
- M08: Timeline/history view of conversations
"""

import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

from vpa.core.database import ConversationDatabaseManager

# Simple print-based logging to avoid circular imports
class SimpleLogger:
    def info(self, message: str, extra: Optional[dict] = None):
        """Simple logging function."""
        extra_info = ", ".join(f"{k}={v}" for k, v in (extra or {}).items())
        if extra_info:
            print(f"INFO: {message} | {extra_info}")
        else:
            print(f"INFO: {message}")

    def warning(self, message: str, extra: Optional[dict] = None):
        """Simple warning function."""
        extra_info = ", ".join(f"{k}={v}" for k, v in (extra or {}).items())
        if extra_info:
            print(f"WARNING: {message} | {extra_info}")
        else:
            print(f"WARNING: {message}")

logger = SimpleLogger()


class VPABaseApp:
    """
    VPA Base Application implementing core conversation management.
    
    This class provides the foundational features required for the VPA:
    - Persistent conversation memory with encryption
    - User profile management
    - Conversation history management
    - Data export and privacy controls
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize the VPA base application."""
        self.data_dir = data_dir or Path.home() / ".vpa" / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        db_path = self.data_dir / "conversations.db"
        self.db = ConversationDatabaseManager(db_path=db_path)
        
        # Current conversation tracking
        self.current_conversation_id: Optional[str] = None
        self.current_user_id: str = "default_user"  # Single user for now
        
        logger.info("VPA Base App initialized", extra={
            "data_dir": str(self.data_dir),
            "db_path": str(db_path)
        })
    
    def __enter__(self):
        """Context manager entry."""
        self.db.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.db.__exit__(exc_type, exc_val, exc_tb)
    
    # M05: Start new conversation
    def start_new_conversation(self, title: Optional[str] = None) -> str:
        """
        Start a new conversation.
        
        Args:
            title: Optional conversation title
            
        Returns:
            str: The new conversation ID
        """
        if title is None:
            title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        conversation_id = self.db.create_conversation(
            title=title
        )
        
        self.current_conversation_id = conversation_id
        
        logger.info("New conversation started", extra={
            "conversation_id": conversation_id,
            "title": title
        })
        
        return conversation_id
    
    # M01: Persistent memory across sessions
    def add_message(self, content: str, role: str = "user", metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a message to the current conversation.
        
        Args:
            content: Message content
            role: Message role (user, assistant, system)
            metadata: Optional message metadata
            
        Returns:
            str: The message ID
        """
        if not self.current_conversation_id:
            # Auto-start a conversation if none exists
            self.start_new_conversation()
        
        # Ensure current_conversation_id is not None after auto-start
        assert self.current_conversation_id is not None
        
        message_id = self.db.add_message(
            conversation_id=self.current_conversation_id,
            role=role,
            content=content,
            metadata=metadata or {}
        )
        
        logger.info("Message added", extra={
            "message_id": message_id,
            "conversation_id": self.current_conversation_id,
            "role": role,
            "content_length": len(content)
        })
        
        return message_id
    
    # M02: View conversation history
    def get_conversation_history(self, conversation_id: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get conversation history.
        
        Args:
            conversation_id: Specific conversation ID, or current if None
            limit: Maximum number of messages to return
            
        Returns:
            List of message dictionaries
        """
        conv_id = conversation_id or self.current_conversation_id
        if not conv_id:
            return []
        
        message_records = self.db.get_messages(conv_id, limit=limit)
        
        # Convert MessageRecord objects to dictionaries
        messages = []
        for msg in message_records:
            messages.append({
                'id': msg.id,
                'conversation_id': msg.conversation_id,
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'is_pinned': msg.is_pinned,
                'metadata': msg.metadata
            })
        
        logger.info("Retrieved conversation history", extra={
            "conversation_id": conv_id,
            "message_count": len(messages),
            "limit": limit
        })
        
        return messages
    
    # M08: Timeline/history view of conversations
    def list_conversations(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List all conversations in chronological order.
        
        Args:
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversation dictionaries
        """
        conversation_records = self.db.get_conversations(limit=limit or 50)
        
        # Convert ConversationRecord objects to dictionaries
        conversations = []
        for conv in conversation_records:
            conversations.append({
                'id': conv.id,
                'title': conv.title,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat(),
                'message_count': conv.message_count,
                'is_pinned': conv.is_pinned,
                'metadata': conv.metadata
            })
        
        logger.info("Listed conversations", extra={
            "conversation_count": len(conversations),
            "limit": limit
        })
        
        return conversations
    
    # M02: Edit conversation
    def update_conversation_title(self, conversation_id: str, new_title: str) -> bool:
        """
        Update a conversation's title.
        
        Args:
            conversation_id: The conversation to update
            new_title: New title for the conversation
            
        Returns:
            bool: True if successful
        """
        success = self.db.update_conversation(conversation_id, title=new_title)
        
        if success:
            logger.info("Conversation title updated", extra={
                "conversation_id": conversation_id,
                "new_title": new_title
            })
        else:
            logger.warning("Failed to update conversation title", extra={
                "conversation_id": conversation_id,
                "new_title": new_title
            })
        
        return success
    
    # M02: Delete conversation
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation and all its messages.
        
        Args:
            conversation_id: The conversation to delete
            
        Returns:
            bool: True if successful
        """
        success = self.db.delete_conversation(conversation_id)
        
        if success:
            # Clear current conversation if it was deleted
            if self.current_conversation_id == conversation_id:
                self.current_conversation_id = None
            
            logger.info("Conversation deleted", extra={
                "conversation_id": conversation_id
            })
        else:
            logger.warning("Failed to delete conversation", extra={
                "conversation_id": conversation_id
            })
        
        return success
    
    # M03: Store rich user profile data
    def update_user_profile(self, name: Optional[str] = None, 
                          preferences: Optional[Dict[str, Any]] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update user profile information.
        
        Args:
            name: User's display name
            preferences: User preferences dictionary
            metadata: Additional user metadata
            
        Returns:
            bool: True if successful
        """
        try:
            self.db.update_user_profile(
                name=name,
                preferences=preferences,
                metadata=metadata
            )
            
            logger.info("User profile updated", extra={
                "updated_fields": [k for k, v in [
                    ("name", name), ("preferences", preferences), ("metadata", metadata)
                ] if v is not None]
            })
            return True
        except Exception as e:
            logger.warning("Failed to update user profile", extra={
                "error": str(e)
            })
            return False
    
    def get_user_profile(self) -> Optional[Dict[str, Any]]:
        """
        Get current user's profile.
        
        Returns:
            User profile dictionary or None if not found
        """
        profile_record = self.db.get_user_profile()
        
        if profile_record is None:
            logger.info("Retrieved user profile", extra={
                "profile_exists": False
            })
            return None
        
        # Convert UserProfile object to dictionary
        profile = {
            'name': profile_record.name,
            'preferences': profile_record.preferences,
            'context_window_size': profile_record.context_window_size,
            'created_at': profile_record.created_at.isoformat() if profile_record.created_at else None,
            'updated_at': profile_record.updated_at.isoformat() if profile_record.updated_at else None,
            'metadata': profile_record.metadata
        }
        
        logger.info("Retrieved user profile", extra={
            "profile_exists": True
        })
        
        return profile
    
    # M06: Export full chat history
    def export_all_data(self, export_path: Optional[Path] = None) -> Path:
        """
        Export all user data to a JSON file.
        
        Args:
            export_path: Path for export file, or auto-generate if None
            
        Returns:
            Path to the exported file
        """
        if export_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = self.data_dir / f"vpa_export_{timestamp}.json"
        
        export_data = self.db.export_all_data()
        
        # Write to file
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info("Data exported successfully", extra={
            "export_path": str(export_path),
            "conversations_count": len(export_data.get('conversations', [])),
            "messages_count": len(export_data.get('messages', [])),
            "profile_exists": 'user_profile' in export_data
        })
        
        return export_path
    
    # M06: Delete all conversations
    def delete_all_conversations(self) -> bool:
        """
        Delete all conversations for the current user.
        
        Returns:
            bool: True if successful
        """
        try:
            count = self.db.delete_all_conversations()
            self.current_conversation_id = None
            
            logger.info("All conversations deleted", extra={
                "conversations_deleted": count
            })
            return True
        except Exception as e:
            logger.warning("Failed to delete all conversations", extra={
                "error": str(e)
            })
            return False
    
    # Search functionality
    def search_conversations(self, query: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search conversations by content.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching conversations
        """
        conversation_records = self.db.search_conversations(
            query=query,
            limit=limit or 20
        )
        
        # Convert ConversationRecord objects to dictionaries
        results = []
        for conv in conversation_records:
            results.append({
                'id': conv.id,
                'title': conv.title,
                'created_at': conv.created_at.isoformat(),
                'updated_at': conv.updated_at.isoformat(),
                'message_count': conv.message_count,
                'is_pinned': conv.is_pinned,
                'metadata': conv.metadata
            })
        
        logger.info("Conversation search performed", extra={
            "query": query,
            "results_count": len(results),
            "limit": limit
        })
        
        return results
    
    # Session management
    def load_conversation(self, conversation_id: str) -> bool:
        """
        Load an existing conversation as the current conversation.
        
        Args:
            conversation_id: The conversation to load
            
        Returns:
            bool: True if successful
        """
        # Verify conversation exists by trying to get it
        conversation = self.db.get_conversation(conversation_id)
        
        if conversation:
            self.current_conversation_id = conversation_id
            logger.info("Conversation loaded", extra={
                "conversation_id": conversation_id
            })
            return True
        else:
            logger.warning("Conversation not found", extra={
                "conversation_id": conversation_id
            })
            return False
    
    def get_current_conversation_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the current conversation.
        
        Returns:
            Current conversation info or None
        """
        if not self.current_conversation_id:
            return None
        
        conversation = self.db.get_conversation(self.current_conversation_id)
        
        if conversation:
            return {
                'id': conversation.id,
                'title': conversation.title,
                'created_at': conversation.created_at.isoformat(),
                'updated_at': conversation.updated_at.isoformat(),
                'message_count': conversation.message_count,
                'is_pinned': conversation.is_pinned,
                'metadata': conversation.metadata
            }
        else:
            return None


def main():
    """Simple CLI interface for testing the base app."""
    print("VPA Base Application - Conversation Management")
    print("=" * 50)
    
    with VPABaseApp() as app:
        # Create a test conversation
        conv_id = app.start_new_conversation("Test Session")
        print(f"Started new conversation: {conv_id}")
        
        # Add some messages
        app.add_message("Hello, VPA!", "user")
        app.add_message("Hello! How can I help you today?", "assistant")
        app.add_message("Can you remember this conversation?", "user")
        app.add_message("Yes, I can access our conversation history.", "assistant")
        
        # Show conversation history
        history = app.get_conversation_history()
        print(f"\nConversation history ({len(history)} messages):")
        for msg in history:
            print(f"  [{msg['role']}] {msg['content'][:50]}...")
        
        # List all conversations
        conversations = app.list_conversations()
        print(f"\nAll conversations ({len(conversations)}):")
        for conv in conversations:
            print(f"  {conv['id']}: {conv['title']} ({conv['message_count']} messages)")
        
        # Update user profile
        app.update_user_profile(
            name="Test User",
            preferences={"theme": "dark", "language": "en"},
            metadata={"test_session": True}
        )
        
        profile = app.get_user_profile()
        print(f"\nUser profile: {profile}")
        
        # Export data
        export_path = app.export_all_data()
        print(f"\nData exported to: {export_path}")


if __name__ == "__main__":
    main()
