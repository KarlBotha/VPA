"""
Comprehensive Test Suite for VPA Production Vector Database Integration

This test suite provides extensive testing for the production vector database
integration system, ensuring reliability, performance, and compatibility.

Test Categories:
- Vector database provider tests
- Document processing tests  
- Enhanced RAG system tests
- Performance and scalability tests
- Integration tests with existing systems
- Error handling and edge case tests
"""

import unittest
import asyncio
import json
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

# Import modules to test
try:
    from vpa.core.vector_database import (
        VPAVectorDatabaseManager,
        VectorDocument,
        VectorSearchResult,
        VectorDatabaseProvider,
        VectorDatabaseConfig,
        MockVectorDatabase,
        create_vector_database_manager,
        mock_embedding_function
    )
except ImportError:
    # Fallback for missing vector database components
    class VPAVectorDatabaseManager: pass
    class VectorDocument: pass
    class VectorSearchResult: pass
    class VectorDatabaseProvider: pass
    class VectorDatabaseConfig: pass
    class MockVectorDatabase: pass
    def create_vector_database_manager(*args, **kwargs): pass
    def mock_embedding_function(*args, **kwargs): return []

try:
    from vpa.core.enhanced_rag import (
        EnhancedVPARAGSystem,
        DocumentProcessor,
        DocumentChunk,
        ProcessedDocument,
        create_enhanced_rag_system
    )
except ImportError:
    # Fallback for missing enhanced RAG components
    class EnhancedVPARAGSystem: pass
    class DocumentProcessor: pass
    class DocumentChunk: pass
    class ProcessedDocument: pass
    def create_enhanced_rag_system(*args, **kwargs): pass


class TestVectorDatabaseProviders(unittest.TestCase):
    """Test cases for vector database providers"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_config = VectorDatabaseConfig(
            provider=VectorDatabaseProvider.MOCK,
            index_name="test-index",
            dimension=1536
        )
        self.mock_provider = MockVectorDatabase(self.mock_config)
    
    def test_mock_provider_initialization(self):
        """Test mock provider initialization"""
        self.assertEqual(self.mock_provider.config.provider, VectorDatabaseProvider.MOCK)
        self.assertEqual(self.mock_provider.config.index_name, "test-index")
        self.assertEqual(self.mock_provider.config.dimension, 1536)
        self.assertFalse(self.mock_provider.is_connected)
    
    def test_mock_provider_connection(self):
        """Test mock provider connection"""
        async def test_async():
            # Test connection
            result = await self.mock_provider.connect()
            self.assertTrue(result)
            self.assertTrue(self.mock_provider.is_connected)
            
            # Test disconnection
            await self.mock_provider.disconnect()
            self.assertFalse(self.mock_provider.is_connected)
        
        asyncio.run(test_async())
    
    def test_mock_provider_collection_management(self):
        """Test mock provider collection management"""
        async def test_async():
            await self.mock_provider.connect()
            
            # Test collection creation
            result = await self.mock_provider.create_collection("test-collection")
            self.assertTrue(result)
            self.assertEqual(self.mock_provider.collection_name, "test-collection")
            
            # Test collection deletion
            result = await self.mock_provider.delete_collection("test-collection")
            self.assertTrue(result)
            self.assertIsNone(self.mock_provider.collection_name)
        
        asyncio.run(test_async())
    
    def test_mock_provider_document_operations(self):
        """Test mock provider document operations"""
        async def test_async():
            await self.mock_provider.connect()
            await self.mock_provider.create_collection("test-collection")
            
            # Create test documents
            docs = [
                VectorDocument(
                    id="doc1",
                    content="Test document 1",
                    embedding=[0.1] * 1536,
                    metadata={"type": "test"}
                ),
                VectorDocument(
                    id="doc2",
                    content="Test document 2",
                    embedding=[0.2] * 1536,
                    metadata={"type": "test"}
                )
            ]
            
            # Test insertion
            result = await self.mock_provider.insert_documents(docs)
            self.assertTrue(result)
            self.assertEqual(len(self.mock_provider.documents), 2)
            
            # Test search
            search_results = await self.mock_provider.search([0.1] * 1536, top_k=2)
            self.assertGreater(len(search_results), 0)
            
            # Test update
            updated_doc = VectorDocument(
                id="doc1",
                content="Updated test document 1",
                embedding=[0.15] * 1536,
                metadata={"type": "updated"}
            )
            result = await self.mock_provider.update_documents([updated_doc])
            self.assertTrue(result)
            
            # Test deletion
            result = await self.mock_provider.delete_documents(["doc1"])
            self.assertTrue(result)
            self.assertEqual(len(self.mock_provider.documents), 1)
        
        asyncio.run(test_async())
    
    def test_mock_provider_search_filtering(self):
        """Test mock provider search with metadata filtering"""
        async def test_async():
            await self.mock_provider.connect()
            await self.mock_provider.create_collection("test-collection")
            
            # Create test documents with different metadata
            docs = [
                VectorDocument(
                    id="doc1",
                    content="Document about AI",
                    embedding=[0.1] * 1536,
                    metadata={"category": "AI", "author": "Alice"}
                ),
                VectorDocument(
                    id="doc2",
                    content="Document about ML",
                    embedding=[0.2] * 1536,
                    metadata={"category": "ML", "author": "Bob"}
                ),
                VectorDocument(
                    id="doc3",
                    content="Another AI document",
                    embedding=[0.3] * 1536,
                    metadata={"category": "AI", "author": "Alice"}
                )
            ]
            
            await self.mock_provider.insert_documents(docs)
            
            # Test search with metadata filter
            results = await self.mock_provider.search(
                [0.1] * 1536,
                top_k=10,
                metadata_filter={"category": "AI"}
            )
            
            # Should return only AI documents
            ai_results = [r for r in results if r.metadata.get("category") == "AI"]
            self.assertEqual(len(ai_results), len(results))
        
        asyncio.run(test_async())
    
    def test_vector_database_manager(self):
        """Test vector database manager"""
        async def test_async():
            manager = create_vector_database_manager()
            
            # Test provider registration
            self.assertIn(VectorDatabaseProvider.MOCK, manager.providers)
            
            # Test embedding function setting
            manager.set_embedding_function(mock_embedding_function)
            self.assertIsNotNone(manager.embedding_function)
            
            # Test connection
            result = await manager.connect()
            self.assertTrue(result)
            
            # Test knowledge base creation
            result = await manager.create_knowledge_base("test-kb")
            self.assertTrue(result)
            
            # Test document operations
            docs = [
                VectorDocument(
                    id="doc1",
                    content="Test document content",
                    metadata={"source": "test"}
                )
            ]
            
            result = await manager.add_documents(docs)
            self.assertTrue(result)
            
            # Test search
            results = await manager.search_knowledge("test query", top_k=5)
            self.assertIsInstance(results, list)
            
            # Test stats
            stats = await manager.get_database_stats()
            self.assertIsInstance(stats, dict)
            
            await manager.disconnect()
        
        asyncio.run(test_async())


class TestDocumentProcessor(unittest.TestCase):
    """Test cases for document processing"""
    
    def setUp(self):
        """Set up test environment"""
        self.processor = DocumentProcessor(
            chunk_size=100,
            chunk_overlap=20,
            min_chunk_size=30
        )
    
    def test_document_processing(self):
        """Test document processing into chunks"""
        content = "This is a test document. It contains multiple sentences. Each sentence should be processed correctly. The document should be split into appropriate chunks."
        
        processed_doc = self.processor.process_document(
            document_id="test-doc",
            title="Test Document",
            content=content,
            metadata={"source": "test"}
        )
        
        self.assertEqual(processed_doc.id, "test-doc")
        self.assertEqual(processed_doc.title, "Test Document")
        self.assertGreater(len(processed_doc.chunks), 0)
        
        # Check chunk properties
        for chunk in processed_doc.chunks:
            self.assertGreater(len(chunk.content), self.processor.min_chunk_size)
            self.assertLessEqual(len(chunk.content), self.processor.chunk_size + 50)  # Allow some flexibility
            self.assertEqual(chunk.document_id, "test-doc")
            self.assertIn("source", chunk.metadata)
    
    def test_chunk_overlap(self):
        """Test chunk overlap functionality"""
        content = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence. Sixth sentence."
        
        processed_doc = self.processor.process_document(
            document_id="overlap-test",
            title="Overlap Test",
            content=content
        )
        
        # Check that chunks have reasonable overlap
        if len(processed_doc.chunks) > 1:
            chunk1 = processed_doc.chunks[0]
            chunk2 = processed_doc.chunks[1]
            
            # Should have some overlapping content
            self.assertLess(len(chunk1.content) + len(chunk2.content), len(content) + self.processor.chunk_overlap)
    
    def test_vector_document_conversion(self):
        """Test conversion of document chunks to vector documents"""
        content = "Test document for vector conversion."
        
        processed_doc = self.processor.process_document(
            document_id="vector-test",
            title="Vector Test",
            content=content,
            metadata={"category": "test"}
        )
        
        for chunk in processed_doc.chunks:
            vector_doc = chunk.to_vector_document()
            
            self.assertIsInstance(vector_doc, VectorDocument)
            self.assertEqual(vector_doc.id, chunk.id)
            self.assertEqual(vector_doc.content, chunk.content)
            self.assertEqual(vector_doc.metadata["document_id"], chunk.document_id)
            self.assertEqual(vector_doc.metadata["chunk_index"], chunk.chunk_index)


class TestEnhancedRAGSystem(unittest.TestCase):
    """Test cases for enhanced RAG system"""
    
    def setUp(self):
        """Set up test environment"""
        self.rag_system = create_enhanced_rag_system()
    
    def test_rag_system_initialization(self):
        """Test RAG system initialization"""
        async def test_async():
            result = await self.rag_system.initialize()
            self.assertTrue(result)
            self.assertIsNotNone(self.rag_system.vector_db_manager)
            self.assertIsNotNone(self.rag_system.document_processor)
            
            await self.rag_system.shutdown()
        
        asyncio.run(test_async())
    
    def test_document_management(self):
        """Test document addition, update, and removal"""
        async def test_async():
            await self.rag_system.initialize()
            
            # Test document addition
            result = await self.rag_system.add_document(
                document_id="test-doc",
                title="Test Document",
                content="This is a test document for the enhanced RAG system.",
                metadata={"category": "test"}
            )
            self.assertTrue(result)
            
            # Test document search
            search_results = await self.rag_system.search_knowledge(
                user_id="test-user",
                query="test document",
                top_k=5
            )
            self.assertGreater(len(search_results), 0)
            
            # Test document update
            result = await self.rag_system.update_document(
                document_id="test-doc",
                title="Updated Test Document",
                content="This is an updated test document for the enhanced RAG system.",
                metadata={"category": "test", "updated": True}
            )
            self.assertTrue(result)
            
            # Test document removal
            result = await self.rag_system.remove_document("test-doc")
            self.assertTrue(result)
            
            await self.rag_system.shutdown()
        
        asyncio.run(test_async())
    
    def test_knowledge_search(self):
        """Test knowledge search functionality"""
        async def test_async():
            await self.rag_system.initialize()
            
            # Add test documents
            test_docs = [
                {
                    "id": "ai-doc",
                    "title": "AI Document",
                    "content": "Artificial intelligence and machine learning technologies.",
                    "metadata": {"category": "AI"}
                },
                {
                    "id": "db-doc",
                    "title": "Database Document",
                    "content": "Vector databases and semantic search capabilities.",
                    "metadata": {"category": "Database"}
                }
            ]
            
            for doc in test_docs:
                await self.rag_system.add_document(
                    doc["id"], doc["title"], doc["content"], doc["metadata"]
                )
            
            # Test search
            results = await self.rag_system.search_knowledge(
                user_id="test-user",
                query="artificial intelligence",
                top_k=3
            )
            
            self.assertGreater(len(results), 0)
            
            # Check result structure
            for result in results:
                self.assertIn("document_id", result)
                self.assertIn("content", result)
                self.assertIn("similarity", result)
                self.assertIn("metadata", result)
            
            # Test metadata filtering
            filtered_results = await self.rag_system.search_knowledge(
                user_id="test-user",
                query="technology",
                top_k=5,
                metadata_filter={"category": "AI"}
            )
            
            # Should only return AI documents
            for result in filtered_results:
                self.assertEqual(result["metadata"]["category"], "AI")
            
            await self.rag_system.shutdown()
        
        asyncio.run(test_async())
    
    def test_caching_functionality(self):
        """Test search result caching"""
        async def test_async():
            await self.rag_system.initialize()
            
            # Add test document
            await self.rag_system.add_document(
                "cache-test",
                "Cache Test",
                "This is a document for testing caching functionality.",
                {"category": "test"}
            )
            
            # First search - should not be cached
            start_time = time.time()
            results1 = await self.rag_system.search_knowledge(
                user_id="test-user",
                query="caching test",
                top_k=3
            )
            first_search_time = time.time() - start_time
            
            # Second search - should be cached
            start_time = time.time()
            results2 = await self.rag_system.search_knowledge(
                user_id="test-user",
                query="caching test",
                top_k=3
            )
            second_search_time = time.time() - start_time
            
            # Results should be identical
            self.assertEqual(len(results1), len(results2))
            
            # Cache should have been used (indicated by cache_hits)
            self.assertGreater(self.rag_system.cache_hits, 0)
            
            # Clear cache
            await self.rag_system.clear_cache()
            self.assertEqual(len(self.rag_system.simple_cache), 0)
            
            await self.rag_system.shutdown()
        
        asyncio.run(test_async())
    
    def test_system_statistics(self):
        """Test system statistics functionality"""
        async def test_async():
            await self.rag_system.initialize()
            
            # Add document and perform search
            await self.rag_system.add_document(
                "stats-test",
                "Stats Test",
                "Document for testing statistics.",
                {"category": "test"}
            )
            
            await self.rag_system.search_knowledge(
                user_id="test-user",
                query="statistics test",
                top_k=5
            )
            
            # Get system stats
            stats = await self.rag_system.get_system_stats()
            
            # Verify stats structure
            self.assertIn("vector_database", stats)
            self.assertIn("search_statistics", stats)
            self.assertIn("configuration", stats)
            
            # Verify search statistics
            search_stats = stats["search_statistics"]
            self.assertGreater(search_stats["total_searches"], 0)
            self.assertGreaterEqual(search_stats["total_search_time"], 0)
            
            await self.rag_system.shutdown()
        
        asyncio.run(test_async())


class TestPerformanceAndScalability(unittest.TestCase):
    """Test cases for performance and scalability"""
    
    def setUp(self):
        """Set up performance test environment"""
        self.rag_system = create_enhanced_rag_system()
    
    def test_document_processing_performance(self):
        """Test document processing performance"""
        processor = DocumentProcessor(chunk_size=500, chunk_overlap=100)
        
        # Create large test document
        large_content = "This is a test sentence. " * 1000  # ~25KB
        
        start_time = time.time()
        processed_doc = processor.process_document(
            document_id="perf-test",
            title="Performance Test",
            content=large_content
        )
        processing_time = time.time() - start_time
        
        # Should process quickly (under 1 second)
        self.assertLess(processing_time, 1.0)
        self.assertGreater(len(processed_doc.chunks), 0)
    
    def test_batch_document_insertion(self):
        """Test batch document insertion performance"""
        async def test_async():
            await self.rag_system.initialize()
            
            # Create multiple test documents
            start_time = time.time()
            
            for i in range(10):
                await self.rag_system.add_document(
                    f"batch-doc-{i}",
                    f"Batch Document {i}",
                    f"This is batch document number {i} for performance testing.",
                    {"batch": i, "category": "performance"}
                )
            
            batch_time = time.time() - start_time
            
            # Should complete in reasonable time
            self.assertLess(batch_time, 10.0)
            
            # Test search performance
            start_time = time.time()
            results = await self.rag_system.search_knowledge(
                user_id="perf-user",
                query="batch document",
                top_k=10
            )
            search_time = time.time() - start_time
            
            # Should search quickly
            self.assertLess(search_time, 1.0)
            self.assertGreater(len(results), 0)
            
            await self.rag_system.shutdown()
        
        asyncio.run(test_async())
    
    def test_concurrent_search_operations(self):
        """Test concurrent search operations"""
        async def test_async():
            await self.rag_system.initialize()
            
            # Add test documents
            for i in range(5):
                await self.rag_system.add_document(
                    f"concurrent-doc-{i}",
                    f"Concurrent Document {i}",
                    f"This is document {i} for concurrent testing.",
                    {"index": i}
                )
            
            # Perform concurrent searches
            async def search_task(query_id):
                return await self.rag_system.search_knowledge(
                    user_id=f"user-{query_id}",
                    query=f"concurrent document {query_id}",
                    top_k=5
                )
            
            # Run multiple searches concurrently
            tasks = [search_task(i) for i in range(10)]
            start_time = time.time()
            results = await asyncio.gather(*tasks)
            concurrent_time = time.time() - start_time
            
            # Should complete in reasonable time
            self.assertLess(concurrent_time, 5.0)
            
            # All searches should return results
            for result_set in results:
                self.assertIsInstance(result_set, list)
            
            await self.rag_system.shutdown()
        
        asyncio.run(test_async())


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling and edge cases"""
    
    def setUp(self):
        """Set up error handling test environment"""
        self.rag_system = create_enhanced_rag_system()
    
    def test_invalid_document_operations(self):
        """Test handling of invalid document operations"""
        async def test_async():
            await self.rag_system.initialize()
            
            # Test adding document with empty content
            result = await self.rag_system.add_document(
                "empty-doc",
                "Empty Document",
                "",
                {"category": "test"}
            )
            # Should handle gracefully
            self.assertIsInstance(result, bool)
            
            # Test removing non-existent document
            result = await self.rag_system.remove_document("non-existent-doc")
            # Should handle gracefully
            self.assertIsInstance(result, bool)
            
            await self.rag_system.shutdown()
        
        asyncio.run(test_async())
    
    def test_search_edge_cases(self):
        """Test search edge cases"""
        async def test_async():
            await self.rag_system.initialize()
            
            # Test empty query
            results = await self.rag_system.search_knowledge(
                user_id="test-user",
                query="",
                top_k=5
            )
            self.assertIsInstance(results, list)
            
            # Test very long query
            long_query = "test " * 1000
            results = await self.rag_system.search_knowledge(
                user_id="test-user",
                query=long_query,
                top_k=5
            )
            self.assertIsInstance(results, list)
            
            # Test search with no documents
            results = await self.rag_system.search_knowledge(
                user_id="test-user",
                query="no results",
                top_k=5
            )
            self.assertIsInstance(results, list)
            
            await self.rag_system.shutdown()
        
        asyncio.run(test_async())
    
    def test_system_resilience(self):
        """Test system resilience to errors"""
        async def test_async():
            # Test initialization failure handling
            with patch.object(self.rag_system.vector_db_manager, 'connect', side_effect=Exception("Connection failed")):
                result = await self.rag_system.initialize()
                self.assertFalse(result)
            
            # Test graceful shutdown even when not initialized
            await self.rag_system.shutdown()  # Should not raise exception
        
        asyncio.run(test_async())


class VPAVectorDatabaseTestSuite:
    """
    Comprehensive test suite for VPA Vector Database Integration
    
    Provides a single interface to run all vector database tests
    with proper reporting and error handling.
    """
    
    def __init__(self):
        """Initialize test suite"""
        self.test_loader = unittest.TestLoader()
        self.test_suite = unittest.TestSuite()
        self.test_runner = unittest.TextTestRunner(verbosity=2)
        
        # Add all test classes
        self._add_test_classes()
    
    def _add_test_classes(self):
        """Add all test classes to the suite"""
        test_classes = [
            TestVectorDatabaseProviders,
            TestDocumentProcessor,
            TestEnhancedRAGSystem,
            TestPerformanceAndScalability,
            TestErrorHandling
        ]
        
        for test_class in test_classes:
            tests = self.test_loader.loadTestsFromTestCase(test_class)
            self.test_suite.addTests(tests)
    
    def run_tests(self) -> unittest.TestResult:
        """
        Run all vector database tests
        
        Returns:
            TestResult object with test results
        """
        print("🧪 Running VPA Vector Database Integration Tests...")
        print("=" * 60)
        
        result = self.test_runner.run(self.test_suite)
        
        print("=" * 60)
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        
        if result.testsRun > 0:
            success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
            print(f"Success rate: {success_rate:.1f}%")
        
        if result.failures:
            print("\\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")
        
        if result.errors:
            print("\\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")
        
        return result


def run_vector_database_tests():
    """
    Main function to run vector database tests
    
    Returns:
        TestResult object
    """
    test_suite = VPAVectorDatabaseTestSuite()
    return test_suite.run_tests()


if __name__ == "__main__":
    # Run tests when executed directly
    run_vector_database_tests()
