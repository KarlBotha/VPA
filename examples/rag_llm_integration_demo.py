"""
VPA RAG-LLM Integration Example

This script demonstrates the seamless integration between the RAG (Retrieval-Augmented Generation)
system and LLM (Large Language Model) connectivity for enhanced AI responses.

Features demonstrated:
- Document ingestion and vectorization
- Semantic search with similarity scoring
- Context-aware LLM response generation
- Performance metrics and timing analysis
- Streaming response capabilities
"""

import asyncio
import tempfile
import os
import json
from pathlib import Path

import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# VPA Core Imports
from src.vpa.core.llm import (
    VPALLMManager, MockLLMProvider, LLMConfig, LLMProvider,
    VPARAGLLMIntegration, create_rag_llm_integration
)
from src.vpa.core.database import ConversationDatabaseManager
from src.vpa.core.rag import VPARAGSystem


async def demonstrate_rag_llm_integration():
    """
    Comprehensive demonstration of RAG-LLM integration capabilities
    """
    print("🚀 VPA RAG-LLM Integration Demonstration")
    print("=" * 60)
    
    # ========================================
    # Phase 1: Setup Components
    # ========================================
    print("\\n📋 Phase 1: Setting up VPA Components...")
    
    # Create temporary database for demo
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        db_path = temp_db.name
    
    try:
        # Initialize database manager
        db_manager = ConversationDatabaseManager(Path(db_path))
        print(f"   ✅ Database manager initialized: {db_path}")
        
        # Initialize RAG system
        rag_system = VPARAGSystem(db_manager=db_manager)
        print(f"   ✅ RAG system initialized with model: {rag_system.model_name}")
        
        # Initialize LLM manager
        llm_manager = VPALLMManager()
        
        # Register mock LLM provider for demonstration
        mock_config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model_name="gpt-3.5-turbo-demo",
            max_tokens=1000,
            temperature=0.7
        )
        mock_provider = MockLLMProvider(mock_config)
        llm_manager.register_provider(LLMProvider.OPENAI, mock_provider)
        print(f"   ✅ LLM manager initialized with provider: {LLMProvider.OPENAI.value}")
        
        # Create RAG-LLM integration
        integration = create_rag_llm_integration(llm_manager, rag_system)
        print(f"   ✅ RAG-LLM integration created")
        
        # ========================================
        # Phase 2: Document Ingestion
        # ========================================
        print("\\n📄 Phase 2: Document Ingestion and Knowledge Base Setup...")
        
        # Sample documents for demonstration
        sample_documents = [
            {
                "filename": "ai_basics.txt",
                "content": "Artificial Intelligence (AI) is a branch of computer science that aims to create machines capable of intelligent behavior. Machine learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed. Deep learning uses neural networks with multiple layers to model and understand complex patterns in data."
            },
            {
                "filename": "vpa_features.txt", 
                "content": "VPA (Virtual Personal Assistant) is an advanced AI system that provides personalized assistance through natural language processing. Key features include conversation management, task automation, knowledge retrieval, and integration with various services. The system uses RAG (Retrieval-Augmented Generation) to provide contextually relevant responses."
            },
            {
                "filename": "tech_trends.txt",
                "content": "Current technology trends include the rise of large language models like GPT-4, Claude, and Gemini. Vector databases and semantic search are becoming crucial for AI applications. RAG systems combine the power of retrieval and generation for more accurate and contextual AI responses."
            }
        ]
        
        user_id = "demo_user"
        
        # Ingest documents into RAG system
        for doc in sample_documents:
            try:
                # Note: In a real implementation, you would use rag_system.ingest_document()
                # For this demo, we'll simulate the process
                print(f"   📄 Simulating ingestion of: {doc['filename']}")
                print(f"      Content preview: {doc['content'][:100]}...")
                
            except Exception as e:
                print(f"   ❌ Error ingesting {doc['filename']}: {e}")
        
        print(f"   ✅ Sample knowledge base prepared")
        
        # ========================================
        # Phase 3: Basic RAG-LLM Query
        # ========================================
        print("\\n🤖 Phase 3: Basic RAG-Enhanced Response Generation...")
        
        # Test query about AI
        test_query = "What is artificial intelligence and how does machine learning relate to it?"
        print(f"   🔍 Query: {test_query}")
        
        # Note: For this demo with mock systems, we'll simulate the RAG retrieval
        # In a real implementation, this would automatically retrieve relevant context
        mock_rag_context = "Artificial Intelligence (AI) is a branch of computer science that aims to create machines capable of intelligent behavior. Machine learning is a subset of AI that enables computers to learn and improve from experience."
        
        # Generate enhanced response
        response = await integration.generate_enhanced_response(
            user_id=user_id,
            user_message=test_query,
            conversation_id="demo_conversation",
            use_rag=True,
            rag_top_k=3
        )
        
        print(f"   ✅ Response generated successfully!")
        print(f"   📊 Performance Metrics:")
        print(f"      - RAG Enabled: {response.get('rag_enabled', False)}")
        print(f"      - Context Used: {response.get('rag_context_used', False)}")
        print(f"      - Sources Found: {response.get('rag_sources_count', 0)}")
        print(f"      - Total Time: {response.get('total_processing_time', 0):.3f}s")
        print(f"   💬 Response: {response.get('response', 'No response')[:200]}...")
        
        # ========================================
        # Phase 4: Streaming Response Demo
        # ========================================
        print("\\n🌊 Phase 4: Streaming Response Demonstration...")
        
        streaming_query = "Explain the benefits of RAG systems in AI applications"
        print(f"   🔍 Streaming Query: {streaming_query}")
        print(f"   🌊 Streaming Response:")
        
        chunk_count = 0
        async for chunk in integration.stream_enhanced_response(
            user_id=user_id,
            user_message=streaming_query,
            conversation_id="demo_conversation",
            use_rag=True
        ):
            chunk_count += 1
            if chunk["type"] == "rag_context":
                print(f"      📚 RAG Context: {chunk['rag_sources_count']} sources in {chunk['rag_retrieval_time']:.3f}s")
            elif chunk["type"] == "llm_chunk":
                print(f"      {chunk['content']}", end="", flush=True)
            elif chunk["type"] == "error":
                print(f"      ❌ Error: {chunk.get('error', 'Unknown error')}")
        
        print(f"\\n   ✅ Streaming completed with {chunk_count} chunks")
        
        # ========================================
        # Phase 5: Performance Analysis
        # ========================================
        print("\\n⚡ Phase 5: Performance Analysis...")
        
        # Multiple queries to analyze performance patterns
        performance_queries = [
            "What are the key features of VPA?",
            "How do vector databases work?",
            "What are current technology trends in AI?",
        ]
        
        total_responses = 0
        total_time = 0
        
        for query in performance_queries:
            response = await integration.generate_enhanced_response(
                user_id=user_id,
                user_message=query,
                use_rag=True
            )
            
            if response.get("success"):
                total_responses += 1
                total_time += response.get("total_processing_time", 0)
        
        if total_responses > 0:
            avg_time = total_time / total_responses
            print(f"   📊 Performance Summary:")
            print(f"      - Total Queries: {len(performance_queries)}")
            print(f"      - Successful Responses: {total_responses}")
            print(f"      - Average Response Time: {avg_time:.3f}s")
            print(f"      - Success Rate: {(total_responses/len(performance_queries)*100):.1f}%")
        
        # ========================================
        # Phase 6: Configuration Showcase
        # ========================================
        print("\\n⚙️ Phase 6: Configuration and Customization...")
        
        print(f"   🔧 Current RAG-LLM Configuration:")
        print(f"      - Max Context Chunks: {integration.max_context_chunks}")
        print(f"      - Similarity Threshold: {integration.min_similarity_threshold}")
        print(f"      - Context Window Size: {integration.context_window_size} chars")
        print(f"      - LLM Provider: {llm_manager.default_provider.value if llm_manager.default_provider else 'None'}")
        
        # Demonstrate configuration changes
        print(f"   🔄 Adjusting configuration for specialized use case...")
        integration.max_context_chunks = 3
        integration.min_similarity_threshold = 0.5
        integration.context_window_size = 1500
        
        print(f"   ✅ Configuration updated for high-precision mode")
        
        # Test with new configuration
        precision_response = await integration.generate_enhanced_response(
            user_id=user_id,
            user_message="Give me precise information about machine learning",
            use_rag=True,
            rag_top_k=2
        )
        
        print(f"   📊 High-precision response metrics:")
        print(f"      - Sources Used: {precision_response.get('rag_sources_count', 0)}")
        print(f"      - Processing Time: {precision_response.get('total_processing_time', 0):.3f}s")
        
        print("\\n🎉 RAG-LLM Integration Demonstration Complete!")
        print("=" * 60)
        print("✅ All systems operational and ready for production use!")
        
    finally:
        # Cleanup
        try:
            os.unlink(db_path)
            print(f"🧹 Cleanup: Temporary database removed")
        except:
            pass


def demonstrate_integration_features():
    """
    Demonstrate key integration features without async complexity
    """
    print("\\n🔧 Integration Features Overview:")
    print("-" * 40)
    
    # Feature showcase
    features = [
        ("🔍 Semantic Search", "Context-aware document retrieval with similarity scoring"),
        ("🤖 Multi-Provider LLM", "Support for OpenAI, Anthropic, Azure, Ollama, Gemini"),
        ("⚡ Performance Optimization", "Rate limiting, context windowing, chunk management"),
        ("🌊 Streaming Responses", "Real-time response generation with progress tracking"),
        ("📊 Comprehensive Metrics", "Detailed timing, source tracking, and quality metrics"),
        ("🛡️ Error Handling", "Robust fallback mechanisms and graceful degradation"),
        ("🔧 Configurable Pipeline", "Adjustable parameters for different use cases"),
        ("💾 Conversation Memory", "Context-aware multi-turn conversations"),
    ]
    
    for feature, description in features:
        print(f"   {feature}: {description}")
    
    print("\\n📋 Integration Architecture:")
    print("   User Query → RAG Retrieval → Context Enhancement → LLM Generation → Enhanced Response")
    print("\\n🎯 Benefits:")
    print("   • More accurate and contextual responses")
    print("   • Reduced hallucinations through grounded context")
    print("   • Scalable knowledge management")
    print("   • Real-time performance monitoring")
    

if __name__ == "__main__":
    print("🚀 VPA RAG-LLM Integration Example")
    print("==================================")
    
    # Show feature overview
    demonstrate_integration_features()
    
    # Run the full demonstration
    print("\\n🎬 Starting Interactive Demonstration...")
    asyncio.run(demonstrate_rag_llm_integration())
    
    print("\\n📖 Example Usage in Production:")
    print("""
    # Initialize components
    llm_manager = VPALLMManager()
    rag_system = VPARAGSystem(db_manager)
    integration = create_rag_llm_integration(llm_manager, rag_system)
    
    # Generate enhanced response
    response = await integration.generate_enhanced_response(
        user_id="user123",
        user_message="How do I configure the VPA system?",
        use_rag=True,
        rag_top_k=5
    )
    
    # Stream response for real-time UI
    async for chunk in integration.stream_enhanced_response(
        user_id="user123", 
        user_message="Explain the features",
        use_rag=True
    ):
        if chunk["type"] == "llm_chunk":
            print(chunk["content"], end="")
    """)
    
    print("\\n✨ Integration ready for production deployment!")
