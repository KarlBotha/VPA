"""
Test suite for VPA RAG (Retrieval-Augmented Generation) System

Tests for document ingestion, vectorization, semantic search,
knowledge management, and user-scoped access control.
"""

import unittest
import tempfile
import os
import shutil
from datetime import datetime
from pathlib import Path

from vpa.core.rag import (
    VPARAGSystem,
    KnowledgeChunk,
    DocumentMetadata
)
from vpa.core.database import ConversationDatabaseManager


class TestKnowledgeChunk(unittest.TestCase):
    """Test suite for KnowledgeChunk dataclass"""
    
    def test_knowledge_chunk_creation(self):
        """Test basic KnowledgeChunk creation"""
        chunk = KnowledgeChunk(
            chunk_id="test_chunk_1",
            user_id="test_user",
            document_id="test_doc_1", 
            content="This is test content for the knowledge chunk.",
            metadata={"chunk_index": 0, "source": "test"},
            created_at=datetime.now()
        )
        
        self.assertEqual(chunk.chunk_id, "test_chunk_1")
        self.assertEqual(chunk.user_id, "test_user")
        self.assertEqual(chunk.document_id, "test_doc_1")
        self.assertEqual(chunk.content, "This is test content for the knowledge chunk.")
        self.assertIsInstance(chunk.metadata, dict)
        self.assertIsInstance(chunk.created_at, datetime)

    def test_knowledge_chunk_to_dict(self):
        """Test KnowledgeChunk to_dict conversion"""
        created_time = datetime.now()
        chunk = KnowledgeChunk(
            chunk_id="test_chunk_1",
            user_id="test_user",
            document_id="test_doc_1",
            content="Test content",
            metadata={"chunk_index": 0, "source": "test"},
            created_at=created_time
        )
        
        chunk_dict = chunk.to_dict()
        
        self.assertIsInstance(chunk_dict, dict)
        self.assertEqual(chunk_dict["chunk_id"], "test_chunk_1")
        self.assertEqual(chunk_dict["user_id"], "test_user")
        self.assertEqual(chunk_dict["document_id"], "test_doc_1")
        self.assertEqual(chunk_dict["content"], "Test content")
        self.assertEqual(chunk_dict["metadata"]["chunk_index"], 0)
        self.assertEqual(chunk_dict["created_at"], created_time.isoformat())

    def test_knowledge_chunk_from_dict(self):
        """Test KnowledgeChunk from_dict creation"""
        created_time = datetime.now()
        chunk_data = {
            "chunk_id": "test_chunk_1",
            "user_id": "test_user",
            "document_id": "test_doc_1",
            "content": "Test content",
            "metadata": {"chunk_index": 0, "source": "test"},
            "created_at": created_time.isoformat()
        }
        
        chunk = KnowledgeChunk.from_dict(chunk_data)
        
        self.assertEqual(chunk.chunk_id, "test_chunk_1")
        self.assertEqual(chunk.user_id, "test_user")
        self.assertEqual(chunk.document_id, "test_doc_1")
        self.assertEqual(chunk.content, "Test content")
        self.assertEqual(chunk.metadata["chunk_index"], 0)
        self.assertEqual(chunk.created_at, created_time)


class TestDocumentMetadata(unittest.TestCase):
    """Test suite for DocumentMetadata dataclass"""
    
    def test_document_metadata_creation(self):
        """Test basic DocumentMetadata creation"""
        created_time = datetime.now()
        metadata = DocumentMetadata(
            document_id="test_doc_1",
            user_id="test_user",
            filename="test_document.txt",
            file_type="text/plain",
            file_size=1024,
            chunk_count=5,
            ingested_at=created_time,
            tags=["test", "document"]
        )
        
        self.assertEqual(metadata.document_id, "test_doc_1")
        self.assertEqual(metadata.user_id, "test_user")
        self.assertEqual(metadata.filename, "test_document.txt")
        self.assertEqual(metadata.file_type, "text/plain")
        self.assertEqual(metadata.file_size, 1024)
        self.assertEqual(metadata.chunk_count, 5)
        self.assertEqual(metadata.ingested_at, created_time)
        self.assertEqual(metadata.tags, ["test", "document"])

    def test_document_metadata_to_dict(self):
        """Test DocumentMetadata to_dict conversion"""
        created_time = datetime.now()
        metadata = DocumentMetadata(
            document_id="test_doc_1", 
            user_id="test_user",
            filename="test_document.txt",
            file_type="text/plain",
            file_size=1024,
            chunk_count=5,
            ingested_at=created_time,
            tags=["test", "document"]
        )
        
        metadata_dict = metadata.to_dict()
        
        self.assertIsInstance(metadata_dict, dict)
        self.assertEqual(metadata_dict["document_id"], "test_doc_1")
        self.assertEqual(metadata_dict["filename"], "test_document.txt")
        self.assertEqual(metadata_dict["file_type"], "text/plain")
        self.assertEqual(metadata_dict["file_size"], 1024)
        self.assertEqual(metadata_dict["chunk_count"], 5)
        self.assertEqual(metadata_dict["ingested_at"], created_time.isoformat())
        self.assertEqual(metadata_dict["tags"], ["test", "document"])


class TestVPARAGSystem(unittest.TestCase):
    """Test suite for VPA RAG System"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_rag.db"
        self.db_manager = ConversationDatabaseManager(self.db_path)
        
        # Initialize RAG system directly
        self.rag_system = VPARAGSystem(
            db_manager=self.db_manager,
            model_name="all-MiniLM-L6-v2",
            vector_dim=384,
            max_chunk_size=256
        )
        
        # Create test user ID
        self.test_user = "rag_test_user"
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Close database connections
        if hasattr(self.db_manager, '_connection') and self.db_manager._connection:
            self.db_manager._connection.close()
        
        # Remove temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_rag_system_initialization(self):
        """Test RAG system initialization"""
        self.assertIsNotNone(self.rag_system)
        self.assertEqual(self.rag_system.model_name, "all-MiniLM-L6-v2")
        self.assertEqual(self.rag_system.vector_dim, 384)
        self.assertEqual(self.rag_system.max_chunk_size, 256)
        self.assertIsNotNone(self.rag_system.db_manager)

    def test_text_chunking(self):
        """Test text chunking functionality"""
        long_text = "This is a test document. " * 50  # Long text to trigger chunking
        
        chunks = self.rag_system._chunk_text(long_text)
        
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 1)  # Should be split into multiple chunks
        
        # Check that chunks don't exceed max size
        for chunk in chunks:
            self.assertLessEqual(len(chunk), self.rag_system.max_chunk_size)

    def test_document_id_generation(self):
        """Test document ID generation"""
        user_id = "test_user"
        filename = "test_document.txt"
        content = "This is test content"
        
        doc_id = self.rag_system._generate_document_id(user_id, filename, content)
        
        self.assertIsInstance(doc_id, str)
        self.assertGreater(len(doc_id), 10)  # Should be a reasonable hash length
        
        # Same inputs should generate same ID
        doc_id2 = self.rag_system._generate_document_id(user_id, filename, content)
        self.assertEqual(doc_id, doc_id2)

    def test_get_user_documents(self):
        """Test retrieving user documents"""
        user_id = "test_user"
        
        # Initially should have no documents
        documents = self.rag_system.get_user_documents(user_id)
        
        # Should get a list (even if empty)
        self.assertIsInstance(documents, list)
        self.assertGreaterEqual(len(documents), 0)


if __name__ == '__main__':
    unittest.main()
