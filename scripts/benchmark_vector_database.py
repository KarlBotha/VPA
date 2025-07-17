"""
VPA Vector Database Performance Benchmarking Suite

This script provides comprehensive performance benchmarking for the VPA
vector database integration system, testing various scenarios and providers.

Benchmark Categories:
- Document processing performance
- Vector database operations
- Search performance and scalability
- Memory usage and resource optimization
- Concurrent operations testing
- Provider comparison benchmarks
"""

import time
import asyncio
import statistics
import psutil
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import tracemalloc
from concurrent.futures import ThreadPoolExecutor

# Import VPA modules
from src.vpa.core.vector_database import (
    VPAVectorDatabaseManager,
    VectorDocument,
    VectorDatabaseProvider,
    VectorDatabaseConfig,
    create_vector_database_manager,
    mock_embedding_function
)

from src.vpa.core.enhanced_rag import (
    EnhancedVPARAGSystem,
    DocumentProcessor,
    create_enhanced_rag_system
)


class BenchmarkResult:
    """Container for benchmark results"""
    
    def __init__(self, name: str, operation: str):
        self.name = name
        self.operation = operation
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.memory_usage = None
        self.cpu_usage = None
        self.success = True
        self.error = None
        self.metadata = {}
    
    def start(self):
        """Start timing the benchmark"""
        self.start_time = time.time()
        self.memory_usage = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        self.cpu_usage = psutil.cpu_percent()
    
    def end(self):
        """End timing the benchmark"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        self.memory_usage = end_memory - self.memory_usage
        self.cpu_usage = psutil.cpu_percent() - self.cpu_usage
    
    def set_error(self, error: Exception):
        """Set benchmark error"""
        self.success = False
        self.error = str(error)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "operation": self.operation,
            "duration": self.duration,
            "memory_usage": self.memory_usage,
            "cpu_usage": self.cpu_usage,
            "success": self.success,
            "error": self.error,
            "metadata": self.metadata
        }


class VPAVectorDatabaseBenchmarkSuite:
    """
    Comprehensive benchmark suite for VPA Vector Database Integration
    
    Provides detailed performance analysis across multiple dimensions
    including throughput, latency, memory usage, and scalability.
    """
    
    def __init__(self):
        """Initialize benchmark suite"""
        self.results: List[BenchmarkResult] = []
        self.rag_system = None
        self.vector_db_manager = None
        self.document_processor = None
        
        # Test configurations
        self.test_document_sizes = [100, 1000, 10000, 100000]  # characters
        self.test_batch_sizes = [1, 10, 100, 1000]
        self.test_concurrency_levels = [1, 5, 10, 20]
        self.test_search_query_counts = [10, 100, 1000]
    
    async def setup(self):
        """Setup benchmark environment"""
        print("🚀 Setting up VPA Vector Database Benchmark Suite...")
        
        # Initialize systems
        self.rag_system = create_enhanced_rag_system()
        self.vector_db_manager = create_vector_database_manager()
        self.document_processor = DocumentProcessor(chunk_size=500, chunk_overlap=100)
        
        # Connect systems
        await self.rag_system.initialize()
        await self.vector_db_manager.connect()
        self.vector_db_manager.set_embedding_function(mock_embedding_function)
        
        print("✅ Benchmark environment setup complete")
    
    async def teardown(self):
        """Teardown benchmark environment"""
        print("🧹 Tearing down benchmark environment...")
        
        if self.rag_system:
            await self.rag_system.shutdown()
        
        if self.vector_db_manager:
            await self.vector_db_manager.disconnect()
        
        print("✅ Benchmark environment teardown complete")
    
    def create_test_document(self, doc_id: str, size: int) -> str:
        """Create test document of specified size"""
        base_content = "This is a test document for performance benchmarking. It contains various information about artificial intelligence, machine learning, and vector databases. The content is designed to simulate real-world documents with meaningful text for semantic search testing. "
        
        # Repeat base content to reach desired size
        content = base_content * (size // len(base_content) + 1)
        return content[:size]
    
    def create_test_documents(self, count: int, avg_size: int = 1000) -> List[Dict[str, Any]]:
        """Create multiple test documents"""
        documents = []
        
        for i in range(count):
            doc_id = f"benchmark-doc-{i}"
            title = f"Benchmark Document {i}"
            content = self.create_test_document(doc_id, avg_size)
            metadata = {
                "category": f"category-{i % 5}",
                "author": f"author-{i % 10}",
                "benchmark_id": i,
                "size": len(content)
            }
            
            documents.append({
                "id": doc_id,
                "title": title,
                "content": content,
                "metadata": metadata
            })
        
        return documents
    
    async def benchmark_document_processing(self):
        """Benchmark document processing performance"""
        print("📄 Benchmarking document processing...")
        
        for doc_size in self.test_document_sizes:
            # Create test document
            content = self.create_test_document(f"size-test-{doc_size}", doc_size)
            
            # Benchmark processing
            result = BenchmarkResult(
                f"document_processing_{doc_size}_chars",
                "document_processing"
            )
            
            try:
                result.start()
                
                processed_doc = self.document_processor.process_document(
                    document_id=f"size-test-{doc_size}",
                    title=f"Size Test {doc_size}",
                    content=content,
                    metadata={"size": doc_size}
                )
                
                result.end()
                result.metadata = {
                    "document_size": doc_size,
                    "chunk_count": len(processed_doc.chunks),
                    "chunks_per_second": len(processed_doc.chunks) / result.duration
                }
                
            except Exception as e:
                result.set_error(e)
            
            self.results.append(result)
    
    async def benchmark_document_insertion(self):
        """Benchmark document insertion performance"""
        print("📝 Benchmarking document insertion...")
        
        for batch_size in self.test_batch_sizes:
            # Create test documents
            test_docs = self.create_test_documents(batch_size, 1000)
            
            result = BenchmarkResult(
                f"document_insertion_batch_{batch_size}",
                "document_insertion"
            )
            
            try:
                result.start()
                
                # Insert documents using RAG system
                for doc in test_docs:
                    await self.rag_system.add_document(
                        doc["id"],
                        doc["title"],
                        doc["content"],
                        doc["metadata"]
                    )
                
                result.end()
                result.metadata = {
                    "batch_size": batch_size,
                    "docs_per_second": batch_size / result.duration,
                    "avg_doc_size": statistics.mean([len(doc["content"]) for doc in test_docs])
                }
                
            except Exception as e:
                result.set_error(e)
            
            self.results.append(result)
    
    async def benchmark_search_performance(self):
        """Benchmark search performance"""
        print("🔍 Benchmarking search performance...")
        
        # First, add some documents for searching
        setup_docs = self.create_test_documents(100, 1000)
        for doc in setup_docs:
            await self.rag_system.add_document(
                doc["id"],
                doc["title"],
                doc["content"],
                doc["metadata"]
            )
        
        # Test search queries
        test_queries = [
            "artificial intelligence machine learning",
            "vector database semantic search",
            "document processing benchmarking",
            "performance testing optimization",
            "real-world applications technology"
        ]
        
        for query_count in self.test_search_query_counts:
            result = BenchmarkResult(
                f"search_performance_{query_count}_queries",
                "search_performance"
            )
            
            try:
                result.start()
                
                # Perform multiple searches
                for i in range(query_count):
                    query = test_queries[i % len(test_queries)]
                    await self.rag_system.search_knowledge(
                        user_id=f"benchmark-user-{i}",
                        query=query,
                        top_k=5
                    )
                
                result.end()
                result.metadata = {
                    "query_count": query_count,
                    "queries_per_second": query_count / result.duration,
                    "avg_query_time": result.duration / query_count
                }
                
            except Exception as e:
                result.set_error(e)
            
            self.results.append(result)
    
    async def benchmark_concurrent_operations(self):
        """Benchmark concurrent operations"""
        print("🔄 Benchmarking concurrent operations...")
        
        # Setup documents for concurrent testing
        setup_docs = self.create_test_documents(50, 1000)
        for doc in setup_docs:
            await self.rag_system.add_document(
                doc["id"],
                doc["title"],
                doc["content"],
                doc["metadata"]
            )
        
        for concurrency_level in self.test_concurrency_levels:
            result = BenchmarkResult(
                f"concurrent_search_{concurrency_level}_threads",
                "concurrent_search"
            )
            
            try:
                result.start()
                
                # Define concurrent search task
                async def search_task(task_id: int):
                    query = f"concurrent search task {task_id}"
                    return await self.rag_system.search_knowledge(
                        user_id=f"concurrent-user-{task_id}",
                        query=query,
                        top_k=5
                    )
                
                # Execute concurrent searches
                tasks = [search_task(i) for i in range(concurrency_level)]
                await asyncio.gather(*tasks)
                
                result.end()
                result.metadata = {
                    "concurrency_level": concurrency_level,
                    "operations_per_second": concurrency_level / result.duration,
                    "avg_operation_time": result.duration / concurrency_level
                }
                
            except Exception as e:
                result.set_error(e)
            
            self.results.append(result)
    
    async def benchmark_memory_usage(self):
        """Benchmark memory usage patterns"""
        print("💾 Benchmarking memory usage...")
        
        # Start memory tracing
        tracemalloc.start()
        
        # Test memory usage with increasing document counts
        doc_counts = [10, 50, 100, 500, 1000]
        
        for doc_count in doc_counts:
            result = BenchmarkResult(
                f"memory_usage_{doc_count}_docs",
                "memory_usage"
            )
            
            try:
                # Get initial memory snapshot
                initial_snapshot = tracemalloc.take_snapshot()
                initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
                
                result.start()
                
                # Add documents
                test_docs = self.create_test_documents(doc_count, 1000)
                for doc in test_docs:
                    await self.rag_system.add_document(
                        doc["id"],
                        doc["title"],
                        doc["content"],
                        doc["metadata"]
                    )
                
                # Perform some searches
                for i in range(10):
                    await self.rag_system.search_knowledge(
                        user_id=f"memory-user-{i}",
                        query=f"memory test query {i}",
                        top_k=5
                    )
                
                result.end()
                
                # Get final memory snapshot
                final_snapshot = tracemalloc.take_snapshot()
                final_memory = psutil.Process().memory_info().rss / 1024 / 1024
                
                # Calculate memory usage
                memory_diff = final_memory - initial_memory
                
                result.metadata = {
                    "document_count": doc_count,
                    "memory_increase_mb": memory_diff,
                    "memory_per_document_kb": (memory_diff * 1024) / doc_count if doc_count > 0 else 0,
                    "total_memory_mb": final_memory
                }
                
            except Exception as e:
                result.set_error(e)
            
            self.results.append(result)
        
        tracemalloc.stop()
    
    async def benchmark_scalability(self):
        """Benchmark system scalability"""
        print("📈 Benchmarking system scalability...")
        
        # Test scalability with various document set sizes
        scalability_tests = [
            {"docs": 100, "searches": 50},
            {"docs": 500, "searches": 100},
            {"docs": 1000, "searches": 200},
            {"docs": 2000, "searches": 400}
        ]
        
        for test_config in scalability_tests:
            doc_count = test_config["docs"]
            search_count = test_config["searches"]
            
            result = BenchmarkResult(
                f"scalability_{doc_count}_docs_{search_count}_searches",
                "scalability"
            )
            
            try:
                result.start()
                
                # Add documents
                test_docs = self.create_test_documents(doc_count, 1000)
                for doc in test_docs:
                    await self.rag_system.add_document(
                        doc["id"],
                        doc["title"],
                        doc["content"],
                        doc["metadata"]
                    )
                
                # Perform searches
                for i in range(search_count):
                    query = f"scalability test query {i}"
                    await self.rag_system.search_knowledge(
                        user_id=f"scalability-user-{i}",
                        query=query,
                        top_k=5
                    )
                
                result.end()
                
                result.metadata = {
                    "document_count": doc_count,
                    "search_count": search_count,
                    "total_operations": doc_count + search_count,
                    "operations_per_second": (doc_count + search_count) / result.duration,
                    "docs_per_second": doc_count / result.duration,
                    "searches_per_second": search_count / result.duration
                }
                
            except Exception as e:
                result.set_error(e)
            
            self.results.append(result)
    
    async def run_all_benchmarks(self):
        """Run all benchmark tests"""
        print("🎯 Running VPA Vector Database Benchmark Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            await self.setup()
            
            # Run all benchmark categories
            await self.benchmark_document_processing()
            await self.benchmark_document_insertion()
            await self.benchmark_search_performance()
            await self.benchmark_concurrent_operations()
            await self.benchmark_memory_usage()
            await self.benchmark_scalability()
            
        finally:
            await self.teardown()
        
        total_time = time.time() - start_time
        
        print("=" * 60)
        print(f"✅ Benchmark suite completed in {total_time:.2f} seconds")
        print(f"📊 Total benchmarks run: {len(self.results)}")
        
        # Print summary
        successful_benchmarks = [r for r in self.results if r.success]
        failed_benchmarks = [r for r in self.results if not r.success]
        
        print(f"✅ Successful: {len(successful_benchmarks)}")
        print(f"❌ Failed: {len(failed_benchmarks)}")
        
        if failed_benchmarks:
            print("\\nFailed benchmarks:")
            for result in failed_benchmarks:
                print(f"  - {result.name}: {result.error}")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive benchmark report"""
        report = {
            "summary": {
                "total_benchmarks": len(self.results),
                "successful": len([r for r in self.results if r.success]),
                "failed": len([r for r in self.results if not r.success]),
                "timestamp": datetime.now().isoformat()
            },
            "results": [result.to_dict() for result in self.results],
            "analysis": self._analyze_results()
        }
        
        return report
    
    def _analyze_results(self) -> Dict[str, Any]:
        """Analyze benchmark results"""
        successful_results = [r for r in self.results if r.success]
        
        if not successful_results:
            return {"error": "No successful benchmarks to analyze"}
        
        # Calculate statistics
        durations = [r.duration for r in successful_results if r.duration]
        memory_usage = [r.memory_usage for r in successful_results if r.memory_usage]
        
        analysis = {
            "performance_stats": {
                "avg_duration": statistics.mean(durations) if durations else 0,
                "min_duration": min(durations) if durations else 0,
                "max_duration": max(durations) if durations else 0,
                "duration_std": statistics.stdev(durations) if len(durations) > 1 else 0
            },
            "memory_stats": {
                "avg_memory_usage": statistics.mean(memory_usage) if memory_usage else 0,
                "min_memory_usage": min(memory_usage) if memory_usage else 0,
                "max_memory_usage": max(memory_usage) if memory_usage else 0,
                "memory_std": statistics.stdev(memory_usage) if len(memory_usage) > 1 else 0
            },
            "operation_breakdown": {}
        }
        
        # Group by operation type
        operation_groups = {}
        for result in successful_results:
            op_type = result.operation
            if op_type not in operation_groups:
                operation_groups[op_type] = []
            operation_groups[op_type].append(result)
        
        for op_type, results in operation_groups.items():
            op_durations = [r.duration for r in results if r.duration]
            analysis["operation_breakdown"][op_type] = {
                "count": len(results),
                "avg_duration": statistics.mean(op_durations) if op_durations else 0,
                "total_duration": sum(op_durations) if op_durations else 0
            }
        
        return analysis
    
    def save_report(self, filename: str = "vpa_vector_db_benchmark_report.json"):
        """Save benchmark report to file"""
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📁 Benchmark report saved to {filename}")
        return filename


async def run_benchmark_suite():
    """
    Main function to run the VPA Vector Database benchmark suite
    
    Returns:
        Dict containing benchmark results and analysis
    """
    suite = VPAVectorDatabaseBenchmarkSuite()
    
    try:
        await suite.run_all_benchmarks()
        
        # Generate and save report
        report_file = suite.save_report()
        
        # Print summary statistics
        report = suite.generate_report()
        analysis = report["analysis"]
        
        print("\\n📊 Benchmark Summary:")
        print(f"Average operation duration: {analysis['performance_stats']['avg_duration']:.3f}s")
        print(f"Average memory usage: {analysis['memory_stats']['avg_memory_usage']:.2f}MB")
        
        print("\\n🔄 Operation Breakdown:")
        for op_type, stats in analysis["operation_breakdown"].items():
            print(f"  {op_type}: {stats['count']} operations, {stats['avg_duration']:.3f}s avg")
        
        return report
        
    except Exception as e:
        print(f"❌ Benchmark suite failed: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    # Run benchmark suite
    asyncio.run(run_benchmark_suite())
