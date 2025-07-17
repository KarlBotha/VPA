"""
VPA Vector Database Integration Testing Script

This script performs comprehensive integration testing of the VPA vector database
system, ensuring all components work together correctly in production scenarios.

Integration Test Categories:
- End-to-end workflow testing
- Component interaction validation
- Data consistency verification
- Performance under load
- Error recovery testing
- Production scenario simulation
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegrationTestResult:
    """Container for integration test results"""
    
    def __init__(self, test_name: str, test_category: str):
        self.test_name = test_name
        self.test_category = test_category
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.status = "pending"  # pending, running, passed, failed
        self.error_message = None
        self.details = {}
        self.assertions = []
    
    def start(self):
        """Start the test"""
        self.start_time = datetime.now()
        self.status = "running"
        logger.info(f"Starting test: {self.test_name}")
    
    def end(self, success: bool = True, error_message: str = None):
        """End the test"""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.status = "passed" if success else "failed"
        self.error_message = error_message
        
        if success:
            logger.info(f"Test passed: {self.test_name} ({self.duration:.2f}s)")
        else:
            logger.error(f"Test failed: {self.test_name} - {error_message}")
    
    def add_assertion(self, assertion: str, result: bool, details: str = None):
        """Add assertion result"""
        self.assertions.append({
            "assertion": assertion,
            "result": result,
            "details": details
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "test_name": self.test_name,
            "test_category": self.test_category,
            "status": self.status,
            "duration": self.duration,
            "error_message": self.error_message,
            "details": self.details,
            "assertions": self.assertions,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }


class VPAVectorDatabaseIntegrationTester:
    """
    Comprehensive integration tester for VPA Vector Database system
    
    Tests the entire system from document ingestion to search results,
    ensuring all components work together seamlessly.
    """
    
    def __init__(self):
        """Initialize integration tester"""
        self.test_results: List[IntegrationTestResult] = []
        self.rag_system = None
        self.vector_db_manager = None
        self.document_processor = None
        
        # Test data
        self.test_documents = self._create_test_documents()
        self.test_queries = self._create_test_queries()
    
    def _create_test_documents(self) -> List[Dict[str, Any]]:
        """Create comprehensive test documents"""
        return [
            {
                "id": "ai-fundamentals",
                "title": "Artificial Intelligence Fundamentals",
                "content": "Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines capable of performing tasks that typically require human intelligence. These tasks include learning, reasoning, problem-solving, perception, and language understanding. AI systems can be categorized into narrow AI, which is designed for specific tasks, and general AI, which would have human-like cognitive abilities across multiple domains.",
                "metadata": {
                    "category": "AI",
                    "difficulty": "beginner",
                    "author": "Dr. Smith",
                    "tags": ["artificial intelligence", "machine learning", "fundamentals"]
                }
            },
            {
                "id": "vector-databases",
                "title": "Introduction to Vector Databases",
                "content": "Vector databases are specialized database systems designed to store, index, and query high-dimensional vector embeddings. These databases are essential for applications involving semantic search, recommendation systems, and similarity matching. Popular vector databases include Pinecone, Weaviate, Chroma, and Qdrant. They use advanced indexing techniques like HNSW (Hierarchical Navigable Small World) and IVF (Inverted File) to enable efficient similarity search.",
                "metadata": {
                    "category": "Database",
                    "difficulty": "intermediate",
                    "author": "Dr. Johnson",
                    "tags": ["vector database", "embeddings", "semantic search"]
                }
            },
            {
                "id": "nlp-processing",
                "title": "Natural Language Processing Techniques",
                "content": "Natural Language Processing (NLP) is a field of artificial intelligence that focuses on the interaction between computers and humans through natural language. Key techniques include tokenization, named entity recognition, part-of-speech tagging, sentiment analysis, and language modeling. Modern NLP relies heavily on transformer architectures and large language models like BERT, GPT, and T5.",
                "metadata": {
                    "category": "NLP",
                    "difficulty": "intermediate",
                    "author": "Prof. Williams",
                    "tags": ["NLP", "natural language processing", "transformers"]
                }
            },
            {
                "id": "machine-learning",
                "title": "Machine Learning Algorithms Overview",
                "content": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. Key algorithms include supervised learning (linear regression, decision trees, support vector machines), unsupervised learning (k-means clustering, hierarchical clustering), and reinforcement learning. The choice of algorithm depends on the problem type, data characteristics, and performance requirements.",
                "metadata": {
                    "category": "ML",
                    "difficulty": "intermediate",
                    "author": "Dr. Brown",
                    "tags": ["machine learning", "algorithms", "supervised learning"]
                }
            },
            {
                "id": "deep-learning",
                "title": "Deep Learning and Neural Networks",
                "content": "Deep learning is a subset of machine learning that uses artificial neural networks with multiple layers to model and understand complex patterns in data. Key architectures include convolutional neural networks (CNNs) for computer vision, recurrent neural networks (RNNs) for sequential data, and transformer networks for natural language processing. Deep learning has revolutionized fields like image recognition, natural language understanding, and game playing.",
                "metadata": {
                    "category": "Deep Learning",
                    "difficulty": "advanced",
                    "author": "Prof. Davis",
                    "tags": ["deep learning", "neural networks", "CNN", "RNN"]
                }
            }
        ]
    
    def _create_test_queries(self) -> List[Dict[str, Any]]:
        """Create test queries with expected results"""
        return [
            {
                "query": "What is artificial intelligence?",
                "expected_docs": ["ai-fundamentals"],
                "category": "basic_search"
            },
            {
                "query": "vector database indexing techniques",
                "expected_docs": ["vector-databases"],
                "category": "technical_search"
            },
            {
                "query": "neural networks and deep learning",
                "expected_docs": ["deep-learning"],
                "category": "specific_search"
            },
            {
                "query": "machine learning algorithms clustering",
                "expected_docs": ["machine-learning"],
                "category": "algorithmic_search"
            },
            {
                "query": "transformer architecture language models",
                "expected_docs": ["nlp-processing"],
                "category": "advanced_search"
            }
        ]
    
    async def setup_test_environment(self):
        """Setup the test environment"""
        logger.info("Setting up integration test environment...")
        
        try:
            # Import and initialize components
            from src.vpa.core.enhanced_rag import create_enhanced_rag_system
            from src.vpa.core.vector_database import create_vector_database_manager, mock_embedding_function
            from src.vpa.core.enhanced_rag import DocumentProcessor
            
            # Initialize systems
            self.rag_system = create_enhanced_rag_system()
            self.vector_db_manager = create_vector_database_manager()
            self.document_processor = DocumentProcessor()
            
            # Connect and setup
            await self.rag_system.initialize()
            await self.vector_db_manager.connect()
            self.vector_db_manager.set_embedding_function(mock_embedding_function)
            
            logger.info("Test environment setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup test environment: {e}")
            return False
    
    async def teardown_test_environment(self):
        """Teardown the test environment"""
        logger.info("Tearing down integration test environment...")
        
        try:
            if self.rag_system:
                await self.rag_system.shutdown()
            
            if self.vector_db_manager:
                await self.vector_db_manager.disconnect()
            
            logger.info("Test environment teardown completed")
            
        except Exception as e:
            logger.error(f"Error during teardown: {e}")
    
    async def test_document_ingestion_workflow(self):
        """Test complete document ingestion workflow"""
        test_result = IntegrationTestResult(
            "document_ingestion_workflow",
            "end_to_end"
        )
        test_result.start()
        
        try:
            # Test document addition
            for doc in self.test_documents:
                success = await self.rag_system.add_document(
                    doc["id"],
                    doc["title"],
                    doc["content"],
                    doc["metadata"]
                )
                
                test_result.add_assertion(
                    f"Document {doc['id']} added successfully",
                    success,
                    f"Document addition returned: {success}"
                )
                
                if not success:
                    raise Exception(f"Failed to add document {doc['id']}")
            
            # Verify documents are retrievable
            for doc in self.test_documents:
                search_results = await self.rag_system.search_knowledge(
                    user_id="test-user",
                    query=doc["title"],
                    top_k=5
                )
                
                found_doc = any(
                    result.get("document_id") == doc["id"] 
                    for result in search_results
                )
                
                test_result.add_assertion(
                    f"Document {doc['id']} is retrievable",
                    found_doc,
                    f"Search returned {len(search_results)} results"
                )
            
            test_result.details = {
                "documents_processed": len(self.test_documents),
                "total_assertions": len(test_result.assertions),
                "passed_assertions": sum(1 for a in test_result.assertions if a["result"])
            }
            
            test_result.end(success=True)
            
        except Exception as e:
            test_result.end(success=False, error_message=str(e))
        
        self.test_results.append(test_result)
    
    async def test_semantic_search_accuracy(self):
        """Test semantic search accuracy"""
        test_result = IntegrationTestResult(
            "semantic_search_accuracy",
            "search_quality"
        )
        test_result.start()
        
        try:
            total_queries = 0
            accurate_results = 0
            
            for query_data in self.test_queries:
                query = query_data["query"]
                expected_docs = query_data["expected_docs"]
                
                # Perform search
                search_results = await self.rag_system.search_knowledge(
                    user_id="test-user",
                    query=query,
                    top_k=3
                )
                
                # Check if expected documents are in results
                found_expected = any(
                    result.get("document_id") in expected_docs
                    for result in search_results
                )
                
                total_queries += 1
                if found_expected:
                    accurate_results += 1
                
                test_result.add_assertion(
                    f"Query '{query}' returns relevant results",
                    found_expected,
                    f"Expected: {expected_docs}, Got: {[r.get('document_id') for r in search_results]}"
                )
            
            accuracy = accurate_results / total_queries if total_queries > 0 else 0
            
            test_result.details = {
                "total_queries": total_queries,
                "accurate_results": accurate_results,
                "accuracy_percentage": accuracy * 100
            }
            
            # Consider test passed if accuracy > 70%
            test_result.end(success=accuracy > 0.7)
            
        except Exception as e:
            test_result.end(success=False, error_message=str(e))
        
        self.test_results.append(test_result)
    
    async def test_metadata_filtering(self):
        """Test metadata filtering functionality"""
        test_result = IntegrationTestResult(
            "metadata_filtering",
            "search_functionality"
        )
        test_result.start()
        
        try:
            # Test filtering by category
            categories = ["AI", "Database", "NLP", "ML", "Deep Learning"]
            
            for category in categories:
                search_results = await self.rag_system.search_knowledge(
                    user_id="test-user",
                    query="artificial intelligence",
                    top_k=10,
                    metadata_filter={"category": category}
                )
                
                # Check that all results have the correct category
                correct_category = all(
                    result.get("metadata", {}).get("category") == category
                    for result in search_results
                )
                
                test_result.add_assertion(
                    f"Category filter '{category}' works correctly",
                    correct_category,
                    f"Results: {[r.get('metadata', {}).get('category') for r in search_results]}"
                )
            
            # Test filtering by difficulty
            difficulties = ["beginner", "intermediate", "advanced"]
            
            for difficulty in difficulties:
                search_results = await self.rag_system.search_knowledge(
                    user_id="test-user",
                    query="learning",
                    top_k=10,
                    metadata_filter={"difficulty": difficulty}
                )
                
                # Check that all results have the correct difficulty
                correct_difficulty = all(
                    result.get("metadata", {}).get("difficulty") == difficulty
                    for result in search_results
                )
                
                test_result.add_assertion(
                    f"Difficulty filter '{difficulty}' works correctly",
                    correct_difficulty,
                    f"Results: {[r.get('metadata', {}).get('difficulty') for r in search_results]}"
                )
            
            test_result.details = {
                "categories_tested": len(categories),
                "difficulties_tested": len(difficulties),
                "total_filters_tested": len(categories) + len(difficulties)
            }
            
            test_result.end(success=True)
            
        except Exception as e:
            test_result.end(success=False, error_message=str(e))
        
        self.test_results.append(test_result)
    
    async def test_document_update_workflow(self):
        """Test document update workflow"""
        test_result = IntegrationTestResult(
            "document_update_workflow",
            "data_consistency"
        )
        test_result.start()
        
        try:
            # Select a document to update
            original_doc = self.test_documents[0]
            doc_id = original_doc["id"]
            
            # Update document content
            updated_content = original_doc["content"] + " This is additional content added during testing."
            updated_metadata = {**original_doc["metadata"], "updated": True, "version": 2}
            
            # Perform update
            update_success = await self.rag_system.update_document(
                doc_id,
                original_doc["title"] + " (Updated)",
                updated_content,
                updated_metadata
            )
            
            test_result.add_assertion(
                "Document update operation succeeds",
                update_success,
                f"Update operation returned: {update_success}"
            )
            
            # Verify updated content is searchable
            search_results = await self.rag_system.search_knowledge(
                user_id="test-user",
                query="additional content added during testing",
                top_k=5
            )
            
            found_updated = any(
                result.get("document_id") == doc_id
                for result in search_results
            )
            
            test_result.add_assertion(
                "Updated content is searchable",
                found_updated,
                f"Search for updated content returned {len(search_results)} results"
            )
            
            # Verify metadata update
            metadata_search = await self.rag_system.search_knowledge(
                user_id="test-user",
                query="intelligence",
                top_k=10,
                metadata_filter={"updated": True}
            )
            
            found_metadata = any(
                result.get("document_id") == doc_id
                for result in metadata_search
            )
            
            test_result.add_assertion(
                "Updated metadata is filterable",
                found_metadata,
                f"Metadata filter search returned {len(metadata_search)} results"
            )
            
            test_result.details = {
                "document_updated": doc_id,
                "content_length_increase": len(updated_content) - len(original_doc["content"]),
                "metadata_fields_added": 2
            }
            
            test_result.end(success=True)
            
        except Exception as e:
            test_result.end(success=False, error_message=str(e))
        
        self.test_results.append(test_result)
    
    async def test_document_removal_workflow(self):
        """Test document removal workflow"""
        test_result = IntegrationTestResult(
            "document_removal_workflow",
            "data_consistency"
        )
        test_result.start()
        
        try:
            # Select a document to remove
            doc_to_remove = self.test_documents[-1]
            doc_id = doc_to_remove["id"]
            
            # Verify document exists before removal
            pre_removal_search = await self.rag_system.search_knowledge(
                user_id="test-user",
                query=doc_to_remove["title"],
                top_k=5
            )
            
            found_before = any(
                result.get("document_id") == doc_id
                for result in pre_removal_search
            )
            
            test_result.add_assertion(
                "Document exists before removal",
                found_before,
                f"Pre-removal search returned {len(pre_removal_search)} results"
            )
            
            # Perform removal
            removal_success = await self.rag_system.remove_document(doc_id)
            
            test_result.add_assertion(
                "Document removal operation succeeds",
                removal_success,
                f"Removal operation returned: {removal_success}"
            )
            
            # Verify document no longer exists
            post_removal_search = await self.rag_system.search_knowledge(
                user_id="test-user",
                query=doc_to_remove["title"],
                top_k=5
            )
            
            found_after = any(
                result.get("document_id") == doc_id
                for result in post_removal_search
            )
            
            test_result.add_assertion(
                "Document not found after removal",
                not found_after,
                f"Post-removal search returned {len(post_removal_search)} results"
            )
            
            test_result.details = {
                "document_removed": doc_id,
                "search_results_before": len(pre_removal_search),
                "search_results_after": len(post_removal_search)
            }
            
            test_result.end(success=True)
            
        except Exception as e:
            test_result.end(success=False, error_message=str(e))
        
        self.test_results.append(test_result)
    
    async def test_concurrent_operations(self):
        """Test concurrent operations"""
        test_result = IntegrationTestResult(
            "concurrent_operations",
            "performance"
        )
        test_result.start()
        
        try:
            # Define concurrent tasks
            async def concurrent_search(task_id: int):
                query = f"artificial intelligence task {task_id}"
                return await self.rag_system.search_knowledge(
                    user_id=f"concurrent-user-{task_id}",
                    query=query,
                    top_k=3
                )
            
            # Run concurrent searches
            concurrent_tasks = [concurrent_search(i) for i in range(10)]
            start_time = time.time()
            results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
            end_time = time.time()
            
            # Check results
            successful_tasks = [r for r in results if not isinstance(r, Exception)]
            failed_tasks = [r for r in results if isinstance(r, Exception)]
            
            test_result.add_assertion(
                "All concurrent searches succeed",
                len(failed_tasks) == 0,
                f"Successful: {len(successful_tasks)}, Failed: {len(failed_tasks)}"
            )
            
            test_result.add_assertion(
                "Concurrent operations complete in reasonable time",
                end_time - start_time < 10.0,
                f"Total time: {end_time - start_time:.2f} seconds"
            )
            
            test_result.details = {
                "concurrent_tasks": len(concurrent_tasks),
                "successful_tasks": len(successful_tasks),
                "failed_tasks": len(failed_tasks),
                "total_time": end_time - start_time
            }
            
            test_result.end(success=len(failed_tasks) == 0)
            
        except Exception as e:
            test_result.end(success=False, error_message=str(e))
        
        self.test_results.append(test_result)
    
    async def test_system_stats_and_monitoring(self):
        """Test system statistics and monitoring"""
        test_result = IntegrationTestResult(
            "system_stats_monitoring",
            "system_health"
        )
        test_result.start()
        
        try:
            # Get system statistics
            stats = await self.rag_system.get_system_stats()
            
            # Verify stats structure
            required_sections = ["vector_database", "search_statistics", "configuration"]
            
            for section in required_sections:
                test_result.add_assertion(
                    f"Stats contain {section} section",
                    section in stats,
                    f"Available sections: {list(stats.keys())}"
                )
            
            # Verify search statistics
            search_stats = stats.get("search_statistics", {})
            
            test_result.add_assertion(
                "Search statistics are tracked",
                "total_searches" in search_stats,
                f"Search stats keys: {list(search_stats.keys())}"
            )
            
            test_result.add_assertion(
                "Search count is positive",
                search_stats.get("total_searches", 0) > 0,
                f"Total searches: {search_stats.get('total_searches', 0)}"
            )
            
            test_result.details = {
                "stats_sections": list(stats.keys()),
                "total_searches": search_stats.get("total_searches", 0),
                "total_search_time": search_stats.get("total_search_time", 0)
            }
            
            test_result.end(success=True)
            
        except Exception as e:
            test_result.end(success=False, error_message=str(e))
        
        self.test_results.append(test_result)
    
    async def run_all_integration_tests(self):
        """Run all integration tests"""
        logger.info("🧪 Starting VPA Vector Database Integration Tests")
        logger.info("=" * 60)
        
        # Setup test environment
        if not await self.setup_test_environment():
            logger.error("Failed to setup test environment")
            return False
        
        try:
            # Run all tests
            await self.test_document_ingestion_workflow()
            await self.test_semantic_search_accuracy()
            await self.test_metadata_filtering()
            await self.test_document_update_workflow()
            await self.test_document_removal_workflow()
            await self.test_concurrent_operations()
            await self.test_system_stats_and_monitoring()
            
        finally:
            # Teardown test environment
            await self.teardown_test_environment()
        
        # Print summary
        self.print_test_summary()
        
        return True
    
    def print_test_summary(self):
        """Print test summary"""
        logger.info("=" * 60)
        logger.info("🎯 Integration Test Summary")
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "passed"])
        failed_tests = len([r for r in self.test_results if r.status == "failed"])
        
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {failed_tests}")
        
        if failed_tests > 0:
            logger.info("\\nFailed tests:")
            for result in self.test_results:
                if result.status == "failed":
                    logger.info(f"  ❌ {result.test_name}: {result.error_message}")
        
        # Print assertion summary
        total_assertions = sum(len(r.assertions) for r in self.test_results)
        passed_assertions = sum(
            len([a for a in r.assertions if a["result"]])
            for r in self.test_results
        )
        
        logger.info(f"\\nAssertion summary: {passed_assertions}/{total_assertions} passed")
        
        # Success rate
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        logger.info(f"Success rate: {success_rate:.1f}%")
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        report = {
            "summary": {
                "total_tests": len(self.test_results),
                "passed": len([r for r in self.test_results if r.status == "passed"]),
                "failed": len([r for r in self.test_results if r.status == "failed"]),
                "timestamp": datetime.now().isoformat()
            },
            "test_results": [result.to_dict() for result in self.test_results],
            "assertion_summary": {
                "total_assertions": sum(len(r.assertions) for r in self.test_results),
                "passed_assertions": sum(
                    len([a for a in r.assertions if a["result"]])
                    for r in self.test_results
                )
            }
        }
        
        return report
    
    def save_test_report(self, filename: str = "vpa_integration_test_report.json"):
        """Save test report to file"""
        report = self.generate_test_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📁 Test report saved to {filename}")
        return filename


async def run_integration_tests():
    """
    Main function to run VPA Vector Database integration tests
    
    Returns:
        Dict containing test results
    """
    tester = VPAVectorDatabaseIntegrationTester()
    
    try:
        await tester.run_all_integration_tests()
        
        # Generate and save report
        report_file = tester.save_test_report()
        
        return tester.generate_test_report()
        
    except Exception as e:
        logger.error(f"Integration test suite failed: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    # Run integration tests
    asyncio.run(run_integration_tests())
