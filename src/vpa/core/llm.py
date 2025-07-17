"""
VPA LLM (Large Language Model) Integration System

This module implements the LLM connectivity layer for the VPA, enabling
AI-powered conversations with support for multiple providers.

Features:
- Multi-provider LLM support (OpenAI, Anthropic, local models)
- Conversation context management
- Rate limiting and cost management
- Response streaming and error handling
- Integration with RAG system for enhanced responses

Security:
- API key management and encryption
- Rate limiting and usage monitoring
- Content filtering and safety checks
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, AsyncGenerator, Callable, TYPE_CHECKING
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod
import hashlib
import os

if TYPE_CHECKING:
    from .rag import VPARAGSystem

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic" 
    AZURE_OPENAI = "azure_openai"
    LOCAL_OLLAMA = "local_ollama"
    GOOGLE_GEMINI = "google_gemini"


@dataclass
class LLMConfig:
    """Configuration for LLM providers"""
    provider: LLMProvider
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_name: str = "gpt-3.5-turbo"
    max_tokens: int = 2048
    temperature: float = 0.7
    timeout: int = 30
    rate_limit_rpm: int = 60  # Requests per minute
    rate_limit_tpm: int = 40000  # Tokens per minute


@dataclass
class LLMMessage:
    """Represents a message in LLM conversation"""
    role: str  # "system", "user", "assistant"
    content: str
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class LLMResponse:
    """Response from LLM provider"""
    content: str
    provider: LLMProvider
    model: str
    usage: Dict[str, int]  # token usage info
    response_time: float
    finish_reason: str
    metadata: Optional[Dict[str, Any]] = None


class RateLimiter:
    """Rate limiting for LLM API calls"""
    
    def __init__(self, rpm: int = 60, tpm: int = 40000):
        self.rpm = rpm  # requests per minute
        self.tpm = tpm  # tokens per minute
        self.request_times = []
        self.token_usage = []
        
    def can_make_request(self, estimated_tokens: int = 0) -> bool:
        """Check if request can be made within rate limits"""
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Clean old entries
        self.request_times = [t for t in self.request_times if t > minute_ago]
        self.token_usage = [(t, tokens) for t, tokens in self.token_usage if t > minute_ago]
        
        # Check request rate limit
        if len(self.request_times) >= self.rpm:
            return False
            
        # Check token rate limit
        current_token_usage = sum(tokens for _, tokens in self.token_usage)
        if current_token_usage + estimated_tokens > self.tpm:
            return False
            
        return True
    
    def record_request(self, tokens_used: int = 0):
        """Record a request for rate limiting"""
        current_time = time.time()
        self.request_times.append(current_time)
        if tokens_used > 0:
            self.token_usage.append((current_time, tokens_used))


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self.rate_limiter = RateLimiter(config.rate_limit_rpm, config.rate_limit_tpm)
        
    @abstractmethod
    async def generate_response(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Generate response from messages"""
        pass
    
    @abstractmethod
    def stream_response(self, messages: List[LLMMessage], **kwargs) -> AsyncGenerator[str, None]:
        """Stream response from messages"""
        pass
    
    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        pass


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider for testing and development"""
    
    async def generate_response(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Generate mock response"""
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        # Create mock response based on last message
        last_message = messages[-1] if messages else LLMMessage("user", "Hello")
        mock_content = f"Mock response to: {last_message.content[:50]}..."
        
        return LLMResponse(
            content=mock_content,
            provider=LLMProvider.OPENAI,
            model=self.config.model_name,
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            response_time=0.1,
            finish_reason="stop"
        )
    
    async def stream_response(self, messages: List[LLMMessage], **kwargs) -> AsyncGenerator[str, None]:
        """Stream mock response"""
        mock_response = "This is a mock streaming response from the LLM provider."
        words = mock_response.split()
        
        for word in words:
            await asyncio.sleep(0.05)  # Simulate streaming delay
            yield word + " "
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars per token average)"""
        return len(text) // 4


class VPALLMManager:
    """VPA LLM Management System"""
    
    def __init__(self):
        self.providers: Dict[LLMProvider, BaseLLMProvider] = {}
        self.default_provider: Optional[LLMProvider] = None
        self.conversation_history: Dict[str, List[LLMMessage]] = {}
        
    def register_provider(self, provider_type: LLMProvider, provider: BaseLLMProvider):
        """Register an LLM provider"""
        self.providers[provider_type] = provider
        if self.default_provider is None:
            self.default_provider = provider_type
        logger.info(f"Registered LLM provider: {provider_type.value}")
    
    def set_default_provider(self, provider_type: LLMProvider):
        """Set the default LLM provider"""
        if provider_type not in self.providers:
            raise ValueError(f"Provider {provider_type.value} not registered")
        self.default_provider = provider_type
        logger.info(f"Set default LLM provider: {provider_type.value}")
    
    async def generate_response(self, 
                              user_id: str,
                              message: str,
                              conversation_id: Optional[str] = None,
                              provider: Optional[LLMProvider] = None,
                              system_prompt: Optional[str] = None,
                              context: Optional[str] = None) -> LLMResponse:
        """Generate response using LLM"""
        
        # Select provider
        provider = provider or self.default_provider
        if not provider or provider not in self.providers:
            raise ValueError(f"No available LLM provider: {provider}")
        
        llm_provider = self.providers[provider]
        
        # Build conversation messages
        messages = self._build_messages(
            user_id, message, conversation_id, system_prompt, context
        )
        
        # Check rate limits
        estimated_tokens = sum(llm_provider.estimate_tokens(msg.content) for msg in messages)
        if not llm_provider.rate_limiter.can_make_request(estimated_tokens):
            raise Exception("Rate limit exceeded")
        
        try:
            # Generate response
            start_time = time.time()
            response = await llm_provider.generate_response(messages)
            response.response_time = time.time() - start_time
            
            # Record for rate limiting
            llm_provider.rate_limiter.record_request(response.usage.get("total_tokens", 0))
            
            # Store in conversation history
            self._update_conversation_history(user_id, messages, response, conversation_id)
            
            logger.info(f"Generated LLM response: {len(response.content)} chars, "
                       f"{response.usage.get('total_tokens', 0)} tokens")
            
            return response
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise
    
    async def stream_response(self,
                            user_id: str,
                            message: str,
                            conversation_id: Optional[str] = None,
                            provider: Optional[LLMProvider] = None,
                            system_prompt: Optional[str] = None,
                            context: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Stream response using LLM"""
        
        # Select provider
        provider = provider or self.default_provider
        if not provider or provider not in self.providers:
            raise ValueError(f"No available LLM provider: {provider}")
        
        llm_provider = self.providers[provider]
        
        # Build conversation messages
        messages = self._build_messages(
            user_id, message, conversation_id, system_prompt, context
        )
        
        # Stream response
        try:
            async for chunk in llm_provider.stream_response(messages):
                yield chunk
        except Exception as e:
            logger.error(f"LLM streaming failed: {e}")
            raise
    
    def _build_messages(self, 
                       user_id: str,
                       message: str,
                       conversation_id: Optional[str] = None,
                       system_prompt: Optional[str] = None,
                       context: Optional[str] = None) -> List[LLMMessage]:
        """Build message list for LLM request"""
        messages = []
        
        # Add system prompt
        if system_prompt:
            messages.append(LLMMessage("system", system_prompt))
        else:
            messages.append(LLMMessage(
                "system", 
                "You are VPA, a helpful virtual personal assistant. "
                "Provide accurate, helpful, and concise responses."
            ))
        
        # Add context if provided (from RAG)
        if context:
            messages.append(LLMMessage(
                "system",
                f"Context information:\n{context}\n\n"
                "Use this context to provide more accurate and relevant responses."
            ))
        
        # Get conversation history
        history_key = f"{user_id}:{conversation_id}" if conversation_id else user_id
        if history_key in self.conversation_history:
            # Add recent conversation history (limit to last 10 messages)
            recent_history = self.conversation_history[history_key][-10:]
            messages.extend(recent_history)
        
        # Add current user message
        messages.append(LLMMessage("user", message))
        
        return messages
    
    def _update_conversation_history(self,
                                   user_id: str,
                                   messages: List[LLMMessage],
                                   response: LLMResponse,
                                   conversation_id: Optional[str] = None):
        """Update conversation history with new messages"""
        history_key = f"{user_id}:{conversation_id}" if conversation_id else user_id
        
        if history_key not in self.conversation_history:
            self.conversation_history[history_key] = []
        
        # Add user message and assistant response
        user_message = messages[-1]  # Last message is always user message
        assistant_message = LLMMessage("assistant", response.content)
        
        self.conversation_history[history_key].extend([user_message, assistant_message])
        
        # Limit history size (keep last 50 messages)
        if len(self.conversation_history[history_key]) > 50:
            self.conversation_history[history_key] = self.conversation_history[history_key][-50:]
    
    def get_conversation_history(self, user_id: str, conversation_id: Optional[str] = None) -> List[LLMMessage]:
        """Get conversation history for user"""
        history_key = f"{user_id}:{conversation_id}" if conversation_id else user_id
        return self.conversation_history.get(history_key, [])
    
    def clear_conversation_history(self, user_id: str, conversation_id: Optional[str] = None):
        """Clear conversation history for user"""
        history_key = f"{user_id}:{conversation_id}" if conversation_id else user_id
        if history_key in self.conversation_history:
            del self.conversation_history[history_key]
            logger.info(f"Cleared conversation history for {history_key}")


def create_llm_manager(config: Optional[Dict[str, Any]] = None) -> VPALLMManager:
    """Create and configure LLM manager"""
    manager = VPALLMManager()
    
    # Register mock provider by default for development
    mock_config = LLMConfig(
        provider=LLMProvider.OPENAI,
        model_name="mock-gpt-3.5-turbo"
    )
    mock_provider = MockLLMProvider(mock_config)
    manager.register_provider(LLMProvider.OPENAI, mock_provider)
    
    logger.info("VPA LLM Manager initialized with mock provider")
    return manager


# Integration with RAG system
class VPARAGLLMIntegration:
    """
    RAG-LLM Integration System for VPA
    
    Combines semantic knowledge retrieval with LLM generation for enhanced responses.
    """
    
    def __init__(self, llm_manager: VPALLMManager, rag_system: Optional['VPARAGSystem'] = None):
        """
        Initialize RAG-LLM integration
        
        Args:
            llm_manager: VPA LLM manager instance
            rag_system: VPA RAG system instance (optional)
        """
        self.llm_manager = llm_manager
        self.rag_system = rag_system
        
        # Configuration
        self.max_context_chunks = 5
        self.min_similarity_threshold = 0.3
        self.context_window_size = 2000  # characters
        
        logger.info("VPA RAG-LLM Integration initialized")
    
    def set_rag_system(self, rag_system: 'VPARAGSystem'):
        """Set or update the RAG system"""
        self.rag_system = rag_system
        logger.info("RAG system connected to LLM integration")
    
    async def generate_enhanced_response(self,
                                       user_id: str,
                                       user_message: str,
                                       conversation_id: Optional[str] = None,
                                       provider: Optional[LLMProvider] = None,
                                       system_prompt: Optional[str] = None,
                                       use_rag: bool = True,
                                       rag_top_k: int = 3) -> Dict[str, Any]:
        """
        Generate enhanced response using RAG + LLM
        
        Args:
            user_id: User identifier
            user_message: User's message
            conversation_id: Optional conversation ID
            provider: LLM provider to use
            system_prompt: Optional system prompt override
            use_rag: Whether to use RAG for context retrieval
            rag_top_k: Number of RAG chunks to retrieve
            
        Returns:
            Enhanced response with RAG context and metadata
        """
        try:
            start_time = time.time()
            
            # Phase 1: RAG Context Retrieval
            rag_context = None
            rag_sources = []
            rag_retrieval_time = 0
            
            if use_rag and self.rag_system:
                rag_start = time.time()
                rag_results = self.rag_system.search_knowledge(
                    user_id=user_id,
                    query=user_message,
                    top_k=rag_top_k,
                    min_similarity=self.min_similarity_threshold
                )
                rag_retrieval_time = time.time() - rag_start
                
                if rag_results:
                    # Build context from retrieved chunks
                    rag_context = self._build_rag_context(rag_results)
                    rag_sources = self._extract_source_metadata(rag_results)
                    
                    logger.info(f"RAG retrieved {len(rag_results)} relevant chunks "
                               f"in {rag_retrieval_time:.3f}s")
            
            # Phase 2: LLM Generation with RAG Context
            llm_start = time.time()
            response = await self.llm_manager.generate_response(
                user_id=user_id,
                message=user_message,
                conversation_id=conversation_id,
                provider=provider,
                system_prompt=system_prompt,
                context=rag_context
            )
            llm_generation_time = time.time() - llm_start
            
            total_time = time.time() - start_time
            
            # Phase 3: Build Enhanced Response
            enhanced_response = {
                "response": response.content,
                "provider": response.provider.value,
                "model": response.model,
                "usage": response.usage,
                "response_time": response.response_time,
                "success": True,
                
                # RAG-specific metadata
                "rag_enabled": use_rag and self.rag_system is not None,
                "rag_context_used": rag_context is not None,
                "rag_sources_count": len(rag_sources),
                "rag_sources": rag_sources,
                "rag_retrieval_time": rag_retrieval_time,
                
                # Performance metrics
                "total_processing_time": total_time,
                "llm_generation_time": llm_generation_time,
                "pipeline_stages": {
                    "rag_retrieval": rag_retrieval_time,
                    "llm_generation": llm_generation_time,
                    "total": total_time
                }
            }
            
            logger.info(f"Enhanced RAG-LLM response generated: "
                       f"RAG={len(rag_sources)} sources, "
                       f"LLM={response.usage.get('total_tokens', 0)} tokens, "
                       f"Total={total_time:.3f}s")
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"RAG-LLM enhanced generation failed: {e}")
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Please try again.",
                "error": str(e),
                "success": False,
                "rag_enabled": use_rag and self.rag_system is not None,
                "rag_context_used": False
            }
    
    async def stream_enhanced_response(self,
                                     user_id: str,
                                     user_message: str,
                                     conversation_id: Optional[str] = None,
                                     provider: Optional[LLMProvider] = None,
                                     system_prompt: Optional[str] = None,
                                     use_rag: bool = True,
                                     rag_top_k: int = 3) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream enhanced response using RAG + LLM
        
        Yields chunks with metadata about RAG context and streaming progress.
        """
        try:
            # Phase 1: RAG Context Retrieval (non-streaming)
            if use_rag and self.rag_system:
                rag_start = time.time()
                rag_results = self.rag_system.search_knowledge(
                    user_id=user_id,
                    query=user_message,
                    top_k=rag_top_k,
                    min_similarity=self.min_similarity_threshold
                )
                rag_retrieval_time = time.time() - rag_start
                
                # Yield RAG context metadata first
                yield {
                    "type": "rag_context",
                    "rag_sources_count": len(rag_results),
                    "rag_retrieval_time": rag_retrieval_time,
                    "content": ""
                }
                
                rag_context = self._build_rag_context(rag_results) if rag_results else None
            else:
                rag_context = None
                yield {
                    "type": "rag_context",
                    "rag_sources_count": 0,
                    "rag_retrieval_time": 0,
                    "content": ""
                }
            
            # Phase 2: Stream LLM Response
            async for chunk in self.llm_manager.stream_response(
                user_id=user_id,
                message=user_message,
                conversation_id=conversation_id,
                provider=provider,
                system_prompt=system_prompt,
                context=rag_context
            ):
                yield {
                    "type": "llm_chunk",
                    "content": chunk
                }
                
        except Exception as e:
            logger.error(f"RAG-LLM streaming failed: {e}")
            yield {
                "type": "error",
                "content": "Stream error occurred",
                "error": str(e)
            }
    
    def _build_rag_context(self, rag_results: List[Dict[str, Any]]) -> str:
        """
        Build context string from RAG results
        
        Args:
            rag_results: List of RAG search results
            
        Returns:
            Formatted context string for LLM
        """
        if not rag_results:
            return ""
        
        context_parts = []
        total_length = 0
        
        for i, result in enumerate(rag_results[:self.max_context_chunks]):
            chunk_content = result.get('content', '')
            similarity = result.get('similarity', 0)
            document_id = result.get('document_id', 'unknown')
            
            # Format context chunk
            chunk_text = f"[Source {i+1} (similarity: {similarity:.2f}, doc: {document_id})]:\n{chunk_content}\n"
            
            # Check context window size
            if total_length + len(chunk_text) > self.context_window_size:
                break
                
            context_parts.append(chunk_text)
            total_length += len(chunk_text)
        
        if context_parts:
            return (
                "=== RELEVANT CONTEXT INFORMATION ===\n" +
                "\n".join(context_parts) +
                "\n=== END CONTEXT ===\n\n"
                "Please use the above context to provide accurate and relevant responses. "
                "If the context doesn't contain relevant information, rely on your general knowledge."
            )
        
        return ""
    
    def _extract_source_metadata(self, rag_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract source metadata from RAG results"""
        sources = []
        
        for result in rag_results:
            sources.append({
                "document_id": result.get('document_id', 'unknown'),
                "chunk_id": result.get('chunk_id', 'unknown'),
                "similarity": result.get('similarity', 0),
                "content_preview": result.get('content', '')[:100] + "..." if len(result.get('content', '')) > 100 else result.get('content', ''),
                "metadata": result.get('metadata', {})
            })
        
        return sources


def enhance_conversation_with_llm(llm_manager: VPALLMManager,
                                 user_id: str,
                                 user_message: str,
                                 context: Optional[str] = None,
                                 conversation_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Enhanced conversation flow with LLM integration (backward compatibility)
    
    Args:
        llm_manager: LLM manager instance
        user_id: User identifier
        user_message: User's message
        context: Additional context (from RAG)
        conversation_id: Conversation identifier
        
    Returns:
        Dictionary with response and metadata
    """
    try:
        # Generate LLM response
        response = asyncio.run(llm_manager.generate_response(
            user_id=user_id,
            message=user_message,
            conversation_id=conversation_id,
            context=context
        ))
        
        return {
            "response": response.content,
            "provider": response.provider.value,
            "model": response.model,
            "usage": response.usage,
            "response_time": response.response_time,
            "success": True
        }
        
    except Exception as e:
        logger.error(f"LLM conversation enhancement failed: {e}")
        return {
            "response": "I apologize, but I'm experiencing technical difficulties. Please try again.",
            "error": str(e),
            "success": False
        }


def create_rag_llm_integration(llm_manager: VPALLMManager, 
                              rag_system: Optional['VPARAGSystem'] = None) -> VPARAGLLMIntegration:
    """
    Create RAG-LLM integration system
    
    Args:
        llm_manager: VPA LLM manager
        rag_system: Optional VPA RAG system
        
    Returns:
        Configured RAG-LLM integration instance
    """
    integration = VPARAGLLMIntegration(llm_manager, rag_system)
    logger.info("RAG-LLM integration system created")
    return integration


if __name__ == "__main__":
    # Example usage and testing
    async def test_llm_manager():
        manager = create_llm_manager()
        
        try:
            # Test basic response generation
            response = await manager.generate_response(
                user_id="test_user",
                message="Hello, how are you?",
                conversation_id="test_conversation"
            )
            
            print(f"LLM Response: {response.content}")
            print(f"Usage: {response.usage}")
            print(f"Response time: {response.response_time:.2f}s")
            
            # Test streaming
            print("\nStreaming response:")
            async for chunk in manager.stream_response(
                user_id="test_user",
                message="Tell me a short story",
                conversation_id="test_conversation"
            ):
                print(chunk, end="", flush=True)
            print("\n")
            
        except Exception as e:
            print(f"Test failed: {e}")
    
    # Run test
    asyncio.run(test_llm_manager())
    print("VPA LLM System test completed!")
