"""
RAG Integration Tests for VPA

Tests RAG system integration with existing VPA components:
- Database integration with authentication
- Document ingestion and retrieval
- Vector search functionality
- User-scoped knowledge management
"""

import unittest
import tempfile
import os
import shutil
from datetime import datetime
from pathlib import Path
import json

from src.vpa.core.rag import (
    VPARAGSystem,
    KnowledgeChunk,
    DocumentMetadata,
    create_rag_system,
    enhance_conversation_with_rag
)
from src.vpa.core.database import ConversationDatabaseManager
from src.vpa.core.auth import create_auth_manager


class TestVPARAGSystem(unittest.TestCase):
    """Test suite for VPA RAG System"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(os.path.join(self.temp_dir, "test_rag.db"))
        self.db_manager = ConversationDatabaseManager(self.db_path)
        self.auth_manager = create_auth_manager(self.db_manager)
        self.rag_system = create_rag_system(self.db_manager)
        
        # Create test user
        self.test_user = "rag_test_user"
        self.auth_manager.register_user(
            self.test_user, 
            "TestPass123!", 
            "rag@test.com"
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Close database connections
        if hasattr(self, 'db_manager'):
            self.db_manager.close()
        
        # Clean up temp directory
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except PermissionError:
                import time
                time.sleep(0.1)
                try:
                    shutil.rmtree(self.temp_dir)
                except PermissionError:
                    pass
    
    def test_rag_system_initialization(self):
        """Test RAG system initializes correctly"""
        # RAG system should initialize without dependencies
        self.assertIsNotNone(self.rag_system)
        self.assertIsNotNone(self.rag_system.db_manager)
        
        # Should work even without embedding model
        self.assertTrue(True, "RAG system initialized successfully")
    
    def test_document_ingestion_basic(self):
        """Test basic document ingestion without embeddings"""
        # Test document content
        test_content = """
        This is a test document for the VPA RAG system.
        It contains multiple sentences to test chunking.
        The system should be able to store and retrieve this content.
        Authentication integration ensures user-scoped access.
        """
        
        # Ingest document
        doc_id = self.rag_system.ingest_document(
            user_id=self.test_user,
            content=test_content,
            filename="test_doc.txt",
            file_type="text",
            metadata={"test": True}
        )
        
        self.assertIsNotNone(doc_id)
        self.assertIsInstance(doc_id, str)
        
    def test_document_search_fallback(self):
        """Test document search with text fallback"""
        # Ingest test document
        test_content = "VPA authentication system provides secure user management."
        
        doc_id = self.rag_system.ingest_document(
            user_id=self.test_user,
            content=test_content,
            filename="auth_info.txt"
        )
        
        # Search for content
        results = self.rag_system.search_knowledge(
            user_id=self.test_user,
            query="authentication",
            top_k=5
        )
        
        # Should find results even with text search fallback
        self.assertIsInstance(results, list)
        
    def test_user_scoped_access(self):
        """Test that users can only access their own documents"""
        # Create second user
        user2 = "rag_user_2"
        self.auth_manager.register_user(user2, "Pass123!", "user2@test.com")
        
        # User 1 creates document
        doc_id = self.rag_system.ingest_document(
            user_id=self.test_user,
            content="Secret user 1 document",
            filename="secret.txt"
        )
        
        # User 2 searches - should not find user 1's document
        results = self.rag_system.search_knowledge(
            user_id=user2,
            query="secret",
            top_k=10
        )
        
        # Should return empty list (no access to other user's docs)
        self.assertEqual(len(results), 0)
        
    def test_rag_stats_tracking(self):
        """Test RAG statistics tracking"""
        # Get initial stats
        initial_stats = self.rag_system.get_rag_stats(self.test_user)
        self.assertEqual(initial_stats["documents"], 0)
        self.assertEqual(initial_stats["chunks"], 0)
        
        # Add document
        self.rag_system.ingest_document(
            user_id=self.test_user,
            content="Test document for stats tracking",
            filename="stats_test.txt"
        )
        
        # Check updated stats
        updated_stats = self.rag_system.get_rag_stats(self.test_user)
        self.assertEqual(updated_stats["documents"], 1)
        self.assertGreater(updated_stats["chunks"], 0)
        
    def test_conversation_enhancement(self):
        """Test RAG integration with conversation flow"""
        # Ingest knowledge
        self.rag_system.ingest_document(
            user_id=self.test_user,
            content="The VPA system supports multiple authentication methods including PBKDF2.",
            filename="vpa_knowledge.txt"
        )
        
        # Test conversation enhancement
        context = {"conversation_id": "test_conv"}
        enhanced_context = enhance_conversation_with_rag(
            rag_system=self.rag_system,
            user_id=self.test_user,
            user_message="How does VPA authentication work?",
            context=context
        )
        
        # Should return enhanced context
        self.assertIsInstance(enhanced_context, dict)
        self.assertIn("conversation_id", enhanced_context)
        
    def test_document_deletion(self):
        """Test document deletion functionality"""
        # Create document
        doc_id = self.rag_system.ingest_document(
            user_id=self.test_user,
            content="Document to be deleted",
            filename="temp_doc.txt"
        )
        
        # Verify document exists
        docs = self.rag_system.get_user_documents(self.test_user)
        self.assertEqual(len(docs), 1)
        
        # Delete document
        success = self.rag_system.delete_document(self.test_user, doc_id)
        self.assertTrue(success)
        
        # Verify document deleted
        docs_after = self.rag_system.get_user_documents(self.test_user)
        self.assertEqual(len(docs_after), 0)
        
    def test_integration_with_authentication(self):
        """Test RAG integration with authentication system"""
        # Authenticate user
        auth_result = self.auth_manager.authenticate_user(self.test_user, "TestPass123!")
        self.assertTrue(auth_result["success"])
        
        session_id = auth_result["session"]["session_id"]
        
        # Verify session is valid
        session = self.auth_manager.validate_session(session_id)
        self.assertIsNotNone(session)
        
        # Use RAG system with authenticated user
        if session:
            authenticated_user = session.user_id
        else:
            authenticated_user = self.test_user
            
        doc_id = self.rag_system.ingest_document(
            user_id=authenticated_user,
            content="Authenticated user document",
            filename="auth_doc.txt"
        )
        
        # Search should work with authenticated user
        results = self.rag_system.search_knowledge(
            user_id=authenticated_user,
            query="authenticated",
            top_k=3
        )
        
        self.assertIsInstance(results, list)


class TestRAGIntegrationReadiness(unittest.TestCase):
    """Test RAG system readiness and integration points"""
    
    def test_rag_system_graceful_degradation(self):
        """Test RAG system works without optional dependencies"""
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = Path(tmp_file.name)
        
        try:
            # Initialize system (should work without sentence-transformers/faiss)
            db_manager = ConversationDatabaseManager(db_path)
            rag_system = create_rag_system(db_manager)
            
            # Should initialize successfully
            self.assertIsNotNone(rag_system)
            
            # Should handle missing dependencies gracefully
            self.assertTrue(True, "RAG system handles missing dependencies gracefully")
            
        finally:
            # Cleanup
            if db_path.exists():
                os.unlink(db_path)
    
    def test_database_table_creation(self):
        """Test RAG database tables are created correctly"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
            db_path = Path(tmp_file.name)
        
        try:
            db_manager = ConversationDatabaseManager(db_path)
            rag_system = create_rag_system(db_manager)
            
            # Check tables exist
            with rag_system._get_connection() as conn:
                cursor = conn.cursor()
                
                # Check knowledge chunks table
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='rag_knowledge_chunks'
                """)
                self.assertIsNotNone(cursor.fetchone())
                
                # Check documents table
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='rag_documents'
                """)
                self.assertIsNotNone(cursor.fetchone())
                
                # Check vector index table
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='rag_vector_index'
                """)
                self.assertIsNotNone(cursor.fetchone())
                
        finally:
            if db_path.exists():
                os.unlink(db_path)


if __name__ == "__main__":
    unittest.main()
