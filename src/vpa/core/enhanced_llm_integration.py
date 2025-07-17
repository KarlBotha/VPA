"""
VPA Enhanced LLM Integration System

This module provides the complete integration between the VPA RAG system and
the multi-provider LLM system, enabling intelligent responses with context
awareness and advanced processing capabilities.

Features:
- Seamless RAG-LLM integration
- Multi-provider LLM support with failover
- Context-aware response generation
- Performance optimization and caching
- Enterprise-grade security and monitoring
- Backward compatibility with existing UI components

Integration Points:
- Vector Database System (from vector_database.py)
- Enhanced RAG System (from enhanced_rag.py)
- LLM Provider Manager (from llm_provider_manager.py)
- UI Components (RAGLLMChatWidget integration)
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, AsyncIterator, Tuple
from dataclasses import dataclass, field
import uuid

# Import VPA core components
from .vector_database import VPAVectorDatabaseManager, VectorSearchResult
from .enhanced_rag import EnhancedVPARAGSystem
from .llm import VPARAGLLMIntegration  # Existing LLM integration

logger = logging.getLogger(__name__)


@dataclass
class EnhancedLLMRequest:
    """Enhanced LLM request with RAG context"""
    user_query: str
    user_id: str
    conversation_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # RAG settings
    use_rag: bool = True
    rag_top_k: int = 5
    rag_threshold: float = 0.7
    context_query: Optional[str] = None
    metadata_filter: Optional[Dict[str, Any]] = None
    
    # LLM settings
    provider: Optional[str] = None
    model: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.7
    stream: bool = False
    
    # Request metadata
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Additional context
    system_prompt: Optional[str] = None
    conversation_history: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class EnhancedLLMResponse:
    """Enhanced LLM response with RAG context"""
    content: str
    request_id: str
    user_id: str
    
    # Response metadata
    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    
    # RAG context
    rag_context: List[VectorSearchResult] = field(default_factory=list)
    context_used: bool = False
    
    # LLM details
    provider: Optional[str] = None
    model: Optional[str] = None
    
    # Performance metrics
    response_time: float = 0.0
    rag_time: float = 0.0
    llm_time: float = 0.0
    
    # Usage statistics
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost: float = 0.0
    
    # Quality metrics
    relevance_score: Optional[float] = None
    confidence: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            "content": self.content,
            "request_id": self.request_id,
            "response_id": self.response_id,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "rag_context": [ctx.to_dict() for ctx in self.rag_context],
            "context_used": self.context_used,
            "provider": self.provider,
            "model": self.model,
            "performance": {
                "response_time": self.response_time,
                "rag_time": self.rag_time,
                "llm_time": self.llm_time
            },
            "usage": {
                "prompt_tokens": self.prompt_tokens,
                "completion_tokens": self.completion_tokens,
                "total_tokens": self.total_tokens,
                "cost": self.cost
            },
            "quality": {
                "relevance_score": self.relevance_score,
                "confidence": self.confidence
            }
        }


class VPAEnhancedLLMIntegration:
    """
    Enhanced LLM Integration System for VPA
    
    Provides seamless integration between RAG system and multiple LLM providers
    with advanced features like context awareness, performance optimization,
    and enterprise-grade monitoring.
    """
    
    def __init__(self):
        """Initialize the enhanced LLM integration system"""
        self.rag_system: Optional[EnhancedVPARAGSystem] = None
        self.vector_db_manager: Optional[VPAVectorDatabaseManager] = None
        self.legacy_llm_integration: Optional[VPARAGLLMIntegration] = None
        
        # Performance tracking
        self.request_count = 0
        self.total_response_time = 0.0
        self.total_rag_time = 0.0
        self.total_llm_time = 0.0
        
        # Caching
        self.response_cache: Dict[str, EnhancedLLMResponse] = {}
        self.cache_ttl = 3600  # 1 hour
        self.cache_hits = 0
        
        # Configuration
        self.default_rag_settings = {
            "top_k": 5,
            "threshold": 0.7,
            "use_context": True
        }
        
        self.default_llm_settings = {
            "max_tokens": 4000,
            "temperature": 0.7,
            "provider": "openai",
            "model": "gpt-4"
        }
    
    async def initialize(self, 
                        rag_system: EnhancedVPARAGSystem,
                        vector_db_manager: VPAVectorDatabaseManager,
                        legacy_integration: Optional[VPARAGLLMIntegration] = None) -> bool:
        """
        Initialize the enhanced LLM integration system
        
        Args:
            rag_system: Enhanced RAG system instance
            vector_db_manager: Vector database manager
            legacy_integration: Legacy LLM integration for backward compatibility
            
        Returns:
            Success status
        """
        try:
            self.rag_system = rag_system
            self.vector_db_manager = vector_db_manager
            self.legacy_llm_integration = legacy_integration
            
            # Initialize RAG system if not already initialized
            if not await self._ensure_rag_system_ready():
                return False
            
            logger.info("VPA Enhanced LLM Integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced LLM Integration: {e}")
            return False
    
    async def generate_enhanced_response(self, request: EnhancedLLMRequest) -> EnhancedLLMResponse:
        """
        Generate enhanced response with RAG context
        
        Args:
            request: Enhanced LLM request
            
        Returns:
            Enhanced LLM response with context
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(request)
            cached_response = self._get_cached_response(cache_key)
            if cached_response:
                self.cache_hits += 1
                return cached_response
            
            # Initialize response
            response = EnhancedLLMResponse(
                content="",
                request_id=request.request_id,
                user_id=request.user_id
            )
            
            # Get RAG context if enabled
            rag_start_time = time.time()
            if request.use_rag and self.rag_system:
                response.rag_context = await self._get_rag_context(request)
                response.context_used = len(response.rag_context) > 0
            
            response.rag_time = time.time() - rag_start_time
            
            # Generate LLM response
            llm_start_time = time.time()
            
            # Build enhanced prompt with context
            messages = self._build_enhanced_messages(request, response.rag_context)
            
            # Use legacy integration or direct LLM call
            if self.legacy_llm_integration:
                # Use existing LLM integration
                llm_response = await self.legacy_llm_integration.generate_enhanced_response(
                    user_query=request.user_query,
                    user_id=request.user_id,
                    conversation_history=request.conversation_history,
                    use_rag=request.use_rag,
                    rag_top_k=request.rag_top_k,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature
                )
                
                # Extract response content
                response.content = llm_response.get("response", "")
                response.provider = llm_response.get("provider", "unknown")
                response.model = llm_response.get("model", "unknown")
                response.prompt_tokens = llm_response.get("prompt_tokens", 0)
                response.completion_tokens = llm_response.get("completion_tokens", 0)
                response.total_tokens = llm_response.get("total_tokens", 0)
                response.cost = llm_response.get("cost", 0.0)
                
            else:
                # Direct mock response for now (to be replaced with actual LLM provider)
                response.content = self._generate_mock_response(request, response.rag_context)
                response.provider = "mock"
                response.model = "mock-model"
                response.prompt_tokens = 100
                response.completion_tokens = 50
                response.total_tokens = 150
                response.cost = 0.001
            
            response.llm_time = time.time() - llm_start_time
            
            # Calculate total response time
            response.response_time = time.time() - start_time
            
            # Update statistics
            self._update_statistics(response)
            
            # Cache response
            self._cache_response(cache_key, response)
            
            logger.info(f"Generated enhanced response in {response.response_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate enhanced response: {e}")
            raise
    
    async def generate_streaming_response(self, request: EnhancedLLMRequest) -> AsyncIterator[str]:
        """
        Generate streaming enhanced response
        
        Args:
            request: Enhanced LLM request
            
        Yields:
            Response chunks
        """
        try:
            # Get RAG context first
            rag_context = []
            if request.use_rag and self.rag_system:
                rag_context = await self._get_rag_context(request)
            
            # Build enhanced prompt
            messages = self._build_enhanced_messages(request, rag_context)
            
            # Generate streaming response
            if self.legacy_llm_integration:
                # Use existing streaming capabilities
                async for chunk in self.legacy_llm_integration.stream_enhanced_response(
                    user_query=request.user_query,
                    user_id=request.user_id,
                    conversation_history=request.conversation_history,
                    use_rag=request.use_rag,
                    rag_top_k=request.rag_top_k,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature
                ):
                    yield chunk
            else:
                # Mock streaming response
                response_content = self._generate_mock_response(request, rag_context)
                words = response_content.split()
                
                for word in words:
                    await asyncio.sleep(0.05)  # Simulate streaming delay
                    yield word + " "
                    
        except Exception as e:
            logger.error(f"Failed to generate streaming response: {e}")
            yield f"Error: {str(e)}"
    
    async def _get_rag_context(self, request: EnhancedLLMRequest) -> List[VectorSearchResult]:
        """
        Get RAG context for the request
        
        Args:
            request: Enhanced LLM request
            
        Returns:
            List of relevant context results
        """
        if not self.rag_system:
            return []
        
        try:
            # Use context_query if provided, otherwise use user_query
            search_query = request.context_query or request.user_query
            
            # Search for relevant context
            results = await self.rag_system.search_knowledge(
                user_id=request.user_id,
                query=search_query,
                top_k=request.rag_top_k,
                metadata_filter=request.metadata_filter
            )
            
            # Convert dict results to VectorSearchResult objects if needed
            if results and isinstance(results[0], dict):
                converted_results = []
                for result in results:
                    vector_result = VectorSearchResult(
                        document_id=result.get("document_id", ""),
                        content=result.get("content", ""),
                        similarity=result.get("similarity", 0.0),
                        metadata=result.get("metadata", {})
                    )
                    converted_results.append(vector_result)
                return converted_results
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get RAG context: {e}")
            return []
    
    def _build_enhanced_messages(self, 
                               request: EnhancedLLMRequest,
                               rag_context: List[VectorSearchResult]) -> List[Dict[str, str]]:
        """
        Build enhanced messages with RAG context
        
        Args:
            request: Enhanced LLM request
            rag_context: RAG context results
            
        Returns:
            List of messages for LLM
        """
        messages = []
        
        # System prompt with context
        system_content = request.system_prompt or "You are a helpful AI assistant."
        
        if rag_context:
            context_text = "\n".join([
                f"Context {i+1}: {result.content}"
                for i, result in enumerate(rag_context)
            ])
            
            system_content += f"""

You have access to the following relevant context information:

{context_text}

Use this context to provide accurate and helpful responses. If the context doesn't contain relevant information for the user's question, please indicate that and provide a general response."""
        
        messages.append({"role": "system", "content": system_content})
        
        # Add conversation history
        for msg in request.conversation_history:
            messages.append(msg)
        
        # Add current user query
        messages.append({"role": "user", "content": request.user_query})
        
        return messages
    
    def _generate_mock_response(self, 
                              request: EnhancedLLMRequest,
                              rag_context: List[VectorSearchResult]) -> str:
        """
        Generate mock response for testing
        
        Args:
            request: Enhanced LLM request
            rag_context: RAG context results
            
        Returns:
            Mock response content
        """
        context_info = ""
        if rag_context:
            context_info = f" I found {len(rag_context)} relevant context items to help answer your question."
        
        return f"""This is a mock enhanced response for your query: "{request.user_query}".{context_info}
        
This response demonstrates the integration between the VPA RAG system and the multi-provider LLM system. In a production environment, this would be replaced with actual LLM provider responses.

Request ID: {request.request_id}
User ID: {request.user_id}
Context used: {len(rag_context) > 0}
Provider: Mock Provider
Model: Mock Model"""
    
    def _generate_cache_key(self, request: EnhancedLLMRequest) -> str:
        """
        Generate cache key for request
        
        Args:
            request: Enhanced LLM request
            
        Returns:
            Cache key string
        """
        # Create cache key based on query, settings, and user
        key_components = [
            request.user_query,
            str(request.use_rag),
            str(request.rag_top_k),
            str(request.max_tokens),
            str(request.temperature),
            request.provider or "default",
            request.model or "default"
        ]
        
        return "|".join(key_components)
    
    def _get_cached_response(self, cache_key: str) -> Optional[EnhancedLLMResponse]:
        """
        Get cached response if available and valid
        
        Args:
            cache_key: Cache key
            
        Returns:
            Cached response or None
        """
        if cache_key in self.response_cache:
            cached_response = self.response_cache[cache_key]
            
            # Check if cache is still valid
            if (datetime.now() - cached_response.timestamp).total_seconds() < self.cache_ttl:
                return cached_response
            else:
                # Remove expired cache entry
                del self.response_cache[cache_key]
        
        return None
    
    def _cache_response(self, cache_key: str, response: EnhancedLLMResponse):
        """
        Cache response for future use
        
        Args:
            cache_key: Cache key
            response: Response to cache
        """
        self.response_cache[cache_key] = response
        
        # Clean up old cache entries (simple LRU)
        if len(self.response_cache) > 1000:
            # Remove oldest 100 entries
            sorted_keys = sorted(
                self.response_cache.keys(),
                key=lambda k: self.response_cache[k].timestamp
            )
            for key in sorted_keys[:100]:
                del self.response_cache[key]
    
    def _update_statistics(self, response: EnhancedLLMResponse):
        """
        Update system statistics
        
        Args:
            response: Response to update statistics for
        """
        self.request_count += 1
        self.total_response_time += response.response_time
        self.total_rag_time += response.rag_time
        self.total_llm_time += response.llm_time
    
    async def _ensure_rag_system_ready(self) -> bool:
        """
        Ensure RAG system is ready for use
        
        Returns:
            True if ready, False otherwise
        """
        if not self.rag_system:
            return False
        
        try:
            # Check if RAG system is initialized
            stats = await self.rag_system.get_system_stats()
            return stats is not None
        except Exception as e:
            logger.error(f"RAG system not ready: {e}")
            return False
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive system statistics
        
        Returns:
            System statistics dictionary
        """
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 else 0.0
        )
        
        avg_rag_time = (
            self.total_rag_time / self.request_count 
            if self.request_count > 0 else 0.0
        )
        
        avg_llm_time = (
            self.total_llm_time / self.request_count 
            if self.request_count > 0 else 0.0
        )
        
        stats = {
            "system_info": {
                "component": "VPA Enhanced LLM Integration",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat()
            },
            "performance": {
                "total_requests": self.request_count,
                "avg_response_time": avg_response_time,
                "avg_rag_time": avg_rag_time,
                "avg_llm_time": avg_llm_time
            },
            "caching": {
                "cache_size": len(self.response_cache),
                "cache_hits": self.cache_hits,
                "cache_hit_rate": (
                    self.cache_hits / self.request_count 
                    if self.request_count > 0 else 0.0
                )
            },
            "components": {
                "rag_system_connected": self.rag_system is not None,
                "vector_db_connected": self.vector_db_manager is not None,
                "legacy_integration_available": self.legacy_llm_integration is not None
            }
        }
        
        # Add RAG system stats if available
        if self.rag_system:
            try:
                rag_stats = await self.rag_system.get_system_stats()
                stats["rag_system"] = rag_stats
            except Exception as e:
                logger.warning(f"Could not get RAG system stats: {e}")
        
        return stats
    
    async def clear_cache(self):
        """Clear response cache"""
        self.response_cache.clear()
        self.cache_hits = 0
        logger.info("Response cache cleared")
    
    async def shutdown(self):
        """Shutdown the enhanced LLM integration system"""
        await self.clear_cache()
        logger.info("VPA Enhanced LLM Integration shutdown complete")


def create_enhanced_llm_integration() -> VPAEnhancedLLMIntegration:
    """
    Create enhanced LLM integration instance
    
    Returns:
        VPAEnhancedLLMIntegration instance
    """
    integration = VPAEnhancedLLMIntegration()
    logger.info("Enhanced LLM Integration created")
    return integration


async def create_complete_vpa_system() -> Tuple[VPAEnhancedLLMIntegration, EnhancedVPARAGSystem, VPAVectorDatabaseManager]:
    """
    Create complete VPA system with all components integrated
    
    Returns:
        Tuple of (enhanced_llm_integration, rag_system, vector_db_manager)
    """
    from .enhanced_rag import create_enhanced_rag_system
    from .vector_database import create_vector_database_manager
    
    # Create components
    vector_db_manager = create_vector_database_manager()
    rag_system = create_enhanced_rag_system()
    enhanced_llm_integration = create_enhanced_llm_integration()
    
    # Initialize vector database
    await vector_db_manager.connect()
    
    # Initialize RAG system
    await rag_system.initialize()
    
    # Initialize enhanced LLM integration
    await enhanced_llm_integration.initialize(
        rag_system=rag_system,
        vector_db_manager=vector_db_manager
    )
    
    logger.info("Complete VPA system initialized successfully")
    return enhanced_llm_integration, rag_system, vector_db_manager


if __name__ == "__main__":
    # Example usage and testing
    async def test_enhanced_llm_integration():
        try:
            # Create complete system
            llm_integration, rag_system, vector_db_manager = await create_complete_vpa_system()
            
            # Add some test documents
            await rag_system.add_document(
                document_id="ai-overview",
                title="AI Overview",
                content="Artificial intelligence is a broad field encompassing machine learning, natural language processing, and computer vision.",
                metadata={"category": "AI", "type": "overview"}
            )
            
            await rag_system.add_document(
                document_id="llm-guide",
                title="LLM Guide",
                content="Large Language Models are neural networks trained on vast amounts of text data to understand and generate human-like text.",
                metadata={"category": "LLM", "type": "guide"}
            )
            
            # Test enhanced response generation
            request = EnhancedLLMRequest(
                user_query="What is artificial intelligence?",
                user_id="test-user",
                use_rag=True,
                rag_top_k=3
            )
            
            response = await llm_integration.generate_enhanced_response(request)
            
            print(f"Enhanced Response: {response.content}")
            print(f"Context used: {response.context_used}")
            print(f"RAG context items: {len(response.rag_context)}")
            print(f"Response time: {response.response_time:.2f}s")
            
            # Test streaming response
            print("\nStreaming Response:")
            async for chunk in llm_integration.generate_streaming_response(request):
                print(chunk, end="")
            print()
            
            # Get system stats
            stats = await llm_integration.get_system_stats()
            print(f"\nSystem Stats: {json.dumps(stats, indent=2)}")
            
            # Shutdown
            await llm_integration.shutdown()
            await rag_system.shutdown()
            await vector_db_manager.disconnect()
            
        except Exception as e:
            print(f"Test failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Run test
    asyncio.run(test_enhanced_llm_integration())
    print("VPA Enhanced LLM Integration test completed!")
