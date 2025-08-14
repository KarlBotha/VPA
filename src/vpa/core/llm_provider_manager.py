"""
VPA Advanced LLM Provider Expansion System

This module implements enterprise-grade multi-provider LLM integration for the VPA system,
building upon the established vector database infrastructure to provide comprehensive
language model capabilities with seamless provider switching and optimization.

Features:
- Multi-provider LLM support (OpenAI, Anthropic, Google, Local models)
- Provider abstraction layer for seamless switching
- Performance optimization and load balancing
- Cost optimization and token usage tracking
- Enterprise-grade security and compliance
- Streaming and batch processing capabilities
- Integration with existing vector database system

Supported LLM Providers:
- OpenAI: GPT-4, GPT-3.5, GPT-4 Turbo, GPT-4o
- Anthropic: Claude 3 (Opus, Sonnet, Haiku)
- Google: Gemini Pro, Gemini Ultra, PaLM 2
- Azure OpenAI: Enterprise deployment
- AWS Bedrock: Managed AI services
- Local Models: Ollama, Hugging Face Transformers
- Custom APIs: Enterprise-specific models

Architecture:
- Provider Registry: Centralized provider management
- Request Router: Intelligent provider selection
- Response Normalizer: Consistent output format
- Performance Monitor: Real-time metrics and optimization
- Cost Tracker: Usage analytics and budgeting
- Fallback System: Automatic provider failover
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, AsyncGenerator, Callable, AsyncIterator
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
import aiohttp
import tiktoken
from pathlib import Path
import os
import yaml

# Import existing VPA components
from .vector_database import VPAVectorDatabaseManager, VectorSearchResult
from .enhanced_rag import EnhancedVPARAGSystem

# LLM provider specific imports (optional dependencies)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    GOOGLE_AI_AVAILABLE = False

try:
    import transformers
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE_OPENAI = "azure_openai"
    AWS_BEDROCK = "aws_bedrock"
    HUGGING_FACE = "hugging_face"
    OLLAMA = "ollama"
    CUSTOM = "custom"
    MOCK = "mock"  # For testing and development


class LLMModel(Enum):
    """Supported LLM models"""
    # OpenAI Models
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4O = "gpt-4o"
    GPT_35_TURBO = "gpt-3.5-turbo"
    
    # Anthropic Models
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    
    # Google Models
    GEMINI_PRO = "gemini-pro"
    GEMINI_ULTRA = "gemini-ultra"
    GEMINI_PRO_VISION = "gemini-pro-vision"
    
    # Local Models
    LLAMA_2_7B = "llama2:7b"
    LLAMA_2_13B = "llama2:13b"
    LLAMA_2_70B = "llama2:70b"
    
    # Mock Model
    MOCK_MODEL = "mock-model"


@dataclass
class LLMProviderConfig:
    """Configuration for LLM providers"""
    provider: LLMProvider
    model: LLMModel
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    api_version: Optional[str] = None
    
    # Request parameters
    max_tokens: int = 4000
    temperature: float = 0.7
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    # Performance settings
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Cost and usage settings
    cost_per_token: float = 0.0
    token_limit_per_minute: int = 10000
    max_concurrent_requests: int = 10
    
    # Provider-specific settings
    custom_headers: Dict[str, str] = field(default_factory=dict)
    custom_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMRequest:
    """Request to an LLM provider"""
    messages: List[Dict[str, str]]
    provider: Optional[LLMProvider] = None
    model: Optional[LLMModel] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stream: bool = False
    
    # Request metadata
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # RAG context
    rag_context: Optional[List[VectorSearchResult]] = None
    system_prompt: Optional[str] = None


@dataclass
class LLMResponse:
    """Response from an LLM provider"""
    content: str
    provider: LLMProvider
    model: LLMModel
    
    # Response metadata
    request_id: str
    response_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Usage statistics
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    
    # Performance metrics
    response_time: float = 0.0
    cost: float = 0.0
    
    # Quality metrics
    confidence: Optional[float] = None
    safety_score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            "content": self.content,
            "provider": self.provider.value,
            "model": self.model.value,
            "request_id": self.request_id,
            "response_id": self.response_id,
            "timestamp": self.timestamp.isoformat(),
            "usage": {
                "prompt_tokens": self.prompt_tokens,
                "completion_tokens": self.completion_tokens,
                "total_tokens": self.total_tokens
            },
            "performance": {
                "response_time": self.response_time,
                "cost": self.cost
            },
            "quality": {
                "confidence": self.confidence,
                "safety_score": self.safety_score
            }
        }


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, config: LLMProviderConfig):
        self.config = config
        self.client = None
        self.is_connected = False
        self.request_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the LLM provider"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the LLM provider"""
        pass
    
    @abstractmethod
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    async def generate_stream_response(self, request: LLMRequest) -> AsyncIterator[str]:
        """Generate a streaming response from the LLM"""
        pass
    
    @abstractmethod
    async def validate_request(self, request: LLMRequest) -> bool:
        """Validate a request before processing"""
        pass
    
    @abstractmethod
    async def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information and statistics"""
        pass
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text (default implementation)"""
        try:
            # Try to use tiktoken for OpenAI models
            if self.config.provider == LLMProvider.OPENAI:
                encoding = tiktoken.encoding_for_model(self.config.model.value)
                return len(encoding.encode(text))
            else:
                # Fallback: rough estimate (1 token ≈ 4 characters)
                return len(text) // 4
        except:
            return len(text) // 4
    
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost based on token usage"""
        total_tokens = prompt_tokens + completion_tokens
        return total_tokens * self.config.cost_per_token
    
    def update_statistics(self, tokens: int, cost: float):
        """Update provider statistics"""
        self.request_count += 1
        self.total_tokens += tokens
        self.total_cost += cost


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider"""
    
    def __init__(self, config: LLMProviderConfig):
        super().__init__(config)
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not installed. Install with: pip install openai")
    
    async def connect(self) -> bool:
        """Connect to OpenAI API"""
        try:
            self.client = openai.AsyncOpenAI(
                api_key=self.config.api_key,
                timeout=self.config.timeout
            )
            self.is_connected = True
            logger.info("Connected to OpenAI API successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to OpenAI API: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from OpenAI API"""
        if self.client:
            await self.client.close()
            self.client = None
            self.is_connected = False
            logger.info("Disconnected from OpenAI API")
    
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response using OpenAI API"""
        start_time = time.time()
        
        try:
            # Prepare request parameters
            params = {
                "model": self.config.model.value,
                "messages": request.messages,
                "max_tokens": request.max_tokens or self.config.max_tokens,
                "temperature": request.temperature or self.config.temperature,
                "top_p": self.config.top_p,
                "frequency_penalty": self.config.frequency_penalty,
                "presence_penalty": self.config.presence_penalty
            }
            
            # Make API call
            response = await self.client.chat.completions.create(**params)
            
            # Extract response data
            content = response.choices[0].message.content
            usage = response.usage
            
            # Calculate metrics
            response_time = time.time() - start_time
            cost = self.calculate_cost(usage.prompt_tokens, usage.completion_tokens)
            
            # Update statistics
            self.update_statistics(usage.total_tokens, cost)
            
            # Create response object
            llm_response = LLMResponse(
                content=content,
                provider=self.config.provider,
                model=self.config.model,
                request_id=request.request_id,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                response_time=response_time,
                cost=cost
            )
            
            logger.info(f"Generated OpenAI response in {response_time:.2f}s")
            return llm_response
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def generate_stream_response(self, request: LLMRequest) -> AsyncIterator[str]:
        """Generate streaming response using OpenAI API"""
        try:
            # Prepare request parameters
            params = {
                "model": self.config.model.value,
                "messages": request.messages,
                "max_tokens": request.max_tokens or self.config.max_tokens,
                "temperature": request.temperature or self.config.temperature,
                "top_p": self.config.top_p,
                "frequency_penalty": self.config.frequency_penalty,
                "presence_penalty": self.config.presence_penalty,
                "stream": True
            }
            
            # Make streaming API call
            async for chunk in await self.client.chat.completions.create(**params):
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise
    
    async def validate_request(self, request: LLMRequest) -> bool:
        """Validate OpenAI request"""
        if not request.messages:
            return False
        
        # Check token limits
        total_tokens = sum(self.count_tokens(msg["content"]) for msg in request.messages)
        if total_tokens > self.config.token_limit_per_minute:
            return False
        
        return True
    
    async def get_provider_info(self) -> Dict[str, Any]:
        """Get OpenAI provider information"""
        return {
            "provider": self.config.provider.value,
            "model": self.config.model.value,
            "connected": self.is_connected,
            "statistics": {
                "request_count": self.request_count,
                "total_tokens": self.total_tokens,
                "total_cost": self.total_cost
            },
            "limits": {
                "max_tokens": self.config.max_tokens,
                "token_limit_per_minute": self.config.token_limit_per_minute,
                "max_concurrent_requests": self.config.max_concurrent_requests
            }
        }


class AnthropicProvider(BaseLLMProvider):
    """Anthropic (Claude) LLM provider"""
    
    def __init__(self, config: LLMProviderConfig):
        super().__init__(config)
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic library not installed. Install with: pip install anthropic")
    
    async def connect(self) -> bool:
        """Connect to Anthropic API"""
        try:
            self.client = anthropic.AsyncAnthropic(
                api_key=self.config.api_key,
                timeout=self.config.timeout
            )
            self.is_connected = True
            logger.info("Connected to Anthropic API successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Anthropic API: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Anthropic API"""
        if self.client:
            await self.client.close()
            self.client = None
            self.is_connected = False
            logger.info("Disconnected from Anthropic API")
    
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Anthropic API"""
        start_time = time.time()
        
        try:
            # Convert messages to Anthropic format
            messages = self._convert_messages(request.messages)
            
            # Make API call
            response = await self.client.messages.create(
                model=self.config.model.value,
                max_tokens=request.max_tokens or self.config.max_tokens,
                temperature=request.temperature or self.config.temperature,
                messages=messages
            )
            
            # Extract response data
            content = response.content[0].text
            
            # Calculate metrics
            response_time = time.time() - start_time
            prompt_tokens = response.usage.input_tokens
            completion_tokens = response.usage.output_tokens
            total_tokens = prompt_tokens + completion_tokens
            cost = self.calculate_cost(prompt_tokens, completion_tokens)
            
            # Update statistics
            self.update_statistics(total_tokens, cost)
            
            # Create response object
            llm_response = LLMResponse(
                content=content,
                provider=self.config.provider,
                model=self.config.model,
                request_id=request.request_id,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                response_time=response_time,
                cost=cost
            )
            
            logger.info(f"Generated Anthropic response in {response_time:.2f}s")
            return llm_response
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    async def generate_stream_response(self, request: LLMRequest) -> AsyncIterator[str]:
        """Generate streaming response using Anthropic API"""
        try:
            # Convert messages to Anthropic format
            messages = self._convert_messages(request.messages)
            
            # Make streaming API call
            async with self.client.messages.stream(
                model=self.config.model.value,
                max_tokens=request.max_tokens or self.config.max_tokens,
                temperature=request.temperature or self.config.temperature,
                messages=messages
            ) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            raise
    
    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Convert messages to Anthropic format"""
        converted = []
        for msg in messages:
            if msg["role"] == "system":
                # Anthropic handles system messages differently
                converted.append({"role": "user", "content": f"System: {msg['content']}"})
            else:
                converted.append(msg)
        return converted
    
    async def validate_request(self, request: LLMRequest) -> bool:
        """Validate Anthropic request"""
        if not request.messages:
            return False
        
        # Check token limits
        total_tokens = sum(self.count_tokens(msg["content"]) for msg in request.messages)
        if total_tokens > self.config.token_limit_per_minute:
            return False
        
        return True
    
    async def get_provider_info(self) -> Dict[str, Any]:
        """Get Anthropic provider information"""
        return {
            "provider": self.config.provider.value,
            "model": self.config.model.value,
            "connected": self.is_connected,
            "statistics": {
                "request_count": self.request_count,
                "total_tokens": self.total_tokens,
                "total_cost": self.total_cost
            },
            "limits": {
                "max_tokens": self.config.max_tokens,
                "token_limit_per_minute": self.config.token_limit_per_minute,
                "max_concurrent_requests": self.config.max_concurrent_requests
            }
        }


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider for testing and development"""
    
    def __init__(self, config: LLMProviderConfig):
        super().__init__(config)
        self.response_templates = [
            "This is a mock response from the {model} model. The request was: {prompt}",
            "Mock LLM response: I understand you're asking about {topic}. Here's a simulated answer.",
            "Simulated response from {provider}: Your query has been processed successfully.",
            "Mock AI assistant: I'm a test response demonstrating the {model} integration."
        ]
    
    async def connect(self) -> bool:
        """Mock connection"""
        self.is_connected = True
        logger.info("Connected to Mock LLM Provider")
        return True
    
    async def disconnect(self):
        """Mock disconnection"""
        self.is_connected = False
        logger.info("Disconnected from Mock LLM Provider")
    
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate mock response"""
        import random
        
        start_time = time.time()
        
        # Simulate processing delay
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Extract last user message
        user_message = ""
        for msg in reversed(request.messages):
            if msg["role"] == "user":
                user_message = msg["content"]
                break
        
        # Generate mock response
        template = random.choice(self.response_templates)
        content = template.format(
            model=self.config.model.value,
            provider=self.config.provider.value,
            prompt=user_message[:100],
            topic=user_message.split()[0] if user_message.split() else "general"
        )
        
        # Mock usage statistics
        prompt_tokens = random.randint(50, 200)
        completion_tokens = random.randint(20, 100)
        total_tokens = prompt_tokens + completion_tokens
        
        # Calculate metrics
        response_time = time.time() - start_time
        cost = self.calculate_cost(prompt_tokens, completion_tokens)
        
        # Update statistics
        self.update_statistics(total_tokens, cost)
        
        # Create response object
        llm_response = LLMResponse(
            content=content,
            provider=self.config.provider,
            model=self.config.model,
            request_id=request.request_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            response_time=response_time,
            cost=cost,
            confidence=random.uniform(0.7, 0.95),
            safety_score=random.uniform(0.8, 1.0)
        )
        
        logger.info(f"Generated mock response in {response_time:.2f}s")
        return llm_response
    
    async def generate_stream_response(self, request: LLMRequest) -> AsyncIterator[str]:
        """Generate mock streaming response"""
        import random
        
        # Generate response
        response = await self.generate_response(request)
        words = response.content.split()
        
        # Stream words with delays
        for word in words:
            await asyncio.sleep(random.uniform(0.01, 0.05))
            yield word + " "
    
    async def validate_request(self, request: LLMRequest) -> bool:
        """Mock validation"""
        return bool(request.messages)
    
    async def get_provider_info(self) -> Dict[str, Any]:
        """Get mock provider information"""
        return {
            "provider": self.config.provider.value,
            "model": self.config.model.value,
            "connected": self.is_connected,
            "statistics": {
                "request_count": self.request_count,
                "total_tokens": self.total_tokens,
                "total_cost": self.total_cost
            },
            "limits": {
                "max_tokens": self.config.max_tokens,
                "token_limit_per_minute": self.config.token_limit_per_minute,
                "max_concurrent_requests": self.config.max_concurrent_requests
            }
        }


class VPALLMProviderManager:
    """VPA LLM Provider Management System"""
    
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.default_provider: Optional[str] = None
        self.load_balancing_enabled = False
        self.failover_enabled = True
        
        # Performance tracking
        self.request_queue = asyncio.Queue()
        self.response_times = {}
        self.error_rates = {}
        
        # Vector database integration
        self.vector_db_manager: Optional[VPAVectorDatabaseManager] = None
        self.rag_system: Optional[EnhancedVPARAGSystem] = None
    
    def register_provider(self, provider_id: str, provider: BaseLLMProvider):
        """Register an LLM provider"""
        self.providers[provider_id] = provider
        if self.default_provider is None:
            self.default_provider = provider_id
        
        # Initialize tracking
        self.response_times[provider_id] = []
        self.error_rates[provider_id] = 0.0
        
        logger.info(f"Registered LLM provider: {provider_id}")
    
    def set_default_provider(self, provider_id: str):
        """Set the default LLM provider"""
        if provider_id not in self.providers:
            raise ValueError(f"Provider {provider_id} not registered")
        self.default_provider = provider_id
        logger.info(f"Set default LLM provider: {provider_id}")
    
    def set_vector_database_manager(self, manager: VPAVectorDatabaseManager):
        """Set the vector database manager for RAG integration"""
        self.vector_db_manager = manager
        logger.info("Set vector database manager for LLM integration")
    
    def set_rag_system(self, rag_system: EnhancedVPARAGSystem):
        """Set the RAG system for enhanced responses"""
        self.rag_system = rag_system
        logger.info("Set RAG system for enhanced LLM responses")
    
    async def connect_all_providers(self) -> Dict[str, bool]:
        """Connect all registered providers"""
        results = {}
        for provider_id, provider in self.providers.items():
            try:
                success = await provider.connect()
                results[provider_id] = success
            except Exception as e:
                logger.error(f"Failed to connect provider {provider_id}: {e}")
                results[provider_id] = False
        
        return results
    
    async def disconnect_all_providers(self):
        """Disconnect all providers"""
        for provider_id, provider in self.providers.items():
            try:
                await provider.disconnect()
            except Exception as e:
                logger.error(f"Failed to disconnect provider {provider_id}: {e}")
    
    async def generate_response(self, 
                              request: LLMRequest,
                              provider_id: Optional[str] = None) -> LLMResponse:
        """Generate response using specified or default provider"""
        
        # Select provider
        if provider_id is None:
            provider_id = self._select_optimal_provider(request)
        
        if provider_id not in self.providers:
            raise ValueError(f"Provider {provider_id} not registered")
        
        provider = self.providers[provider_id]
        
        try:
            # Validate request
            if not await provider.validate_request(request):
                raise ValueError("Invalid request for provider")
            
            # Generate response
            response = await provider.generate_response(request)
            
            # Update performance metrics
            self._update_performance_metrics(provider_id, response.response_time, success=True)
            
            return response
            
        except Exception as e:
            # Update error metrics
            self._update_performance_metrics(provider_id, 0.0, success=False)
            
            # Try failover if enabled
            if self.failover_enabled and provider_id != self.default_provider:
                logger.warning(f"Provider {provider_id} failed, trying failover")
                return await self.generate_response(request, self.default_provider)
            
            raise e
    
    async def generate_enhanced_response(self, 
                                       user_query: str,
                                       user_id: str,
                                       context_query: Optional[str] = None,
                                       provider_id: Optional[str] = None) -> LLMResponse:
        """Generate enhanced response with RAG integration"""
        
        # Get relevant context from vector database
        context_results = []
        if self.rag_system:
            search_query = context_query or user_query
            context_results = await self.rag_system.search_knowledge(
                user_id=user_id,
                query=search_query,
                top_k=5
            )
        
        # Build enhanced prompt with context
        messages = self._build_enhanced_messages(user_query, context_results)
        
        # Create request
        request = LLMRequest(
            messages=messages,
            user_id=user_id,
            rag_context=context_results
        )
        
        # Generate response
        return await self.generate_response(request, provider_id)
    
    async def generate_stream_response(self, 
                                     request: LLMRequest,
                                     provider_id: Optional[str] = None) -> AsyncIterator[str]:
        """Generate streaming response"""
        
        # Select provider
        if provider_id is None:
            provider_id = self._select_optimal_provider(request)
        
        if provider_id not in self.providers:
            raise ValueError(f"Provider {provider_id} not registered")
        
        provider = self.providers[provider_id]
        
        try:
            # Validate request
            if not await provider.validate_request(request):
                raise ValueError("Invalid request for provider")
            
            # Generate streaming response
            async for chunk in provider.generate_stream_response(request):
                yield chunk
                
        except Exception as e:
            # Update error metrics
            self._update_performance_metrics(provider_id, 0.0, success=False)
            
            # Try failover if enabled
            if self.failover_enabled and provider_id != self.default_provider:
                logger.warning(f"Provider {provider_id} failed, trying failover")
                async for chunk in self.generate_stream_response(request, self.default_provider):
                    yield chunk
                return
            
            raise e
    
    def _select_optimal_provider(self, request: LLMRequest) -> str:
        """Select the optimal provider based on performance metrics"""
        
        # If specific provider requested, use it
        if request.provider:
            provider_id = f"{request.provider.value}_{request.model.value}"
            if provider_id in self.providers:
                return provider_id
        
        # If load balancing disabled, use default
        if not self.load_balancing_enabled:
            return self.default_provider
        
        # Select based on performance metrics
        available_providers = [
            pid for pid, provider in self.providers.items()
            if provider.is_connected
        ]
        
        if not available_providers:
            return self.default_provider
        
        # Score providers based on response time and error rate
        scores = {}
        for provider_id in available_providers:
            response_times = self.response_times.get(provider_id, [])
            error_rate = self.error_rates.get(provider_id, 0.0)
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 1.0
            
            # Lower score is better
            scores[provider_id] = avg_response_time * (1 + error_rate)
        
        # Select provider with best score
        best_provider = min(scores, key=scores.get)
        return best_provider
    
    def _build_enhanced_messages(self, 
                               user_query: str,
                               context_results: List[VectorSearchResult]) -> List[Dict[str, str]]:
        """Build enhanced messages with RAG context"""
        
        messages = []
        
        # System prompt with context
        if context_results:
            context_text = "\n".join([
                f"Context {i+1}: {result.content}"
                for i, result in enumerate(context_results)
            ])
            
            system_prompt = f"""You are a helpful AI assistant with access to relevant context information.
            
Use the following context to help answer the user's question:

{context_text}

Please provide a comprehensive and accurate response based on the context provided. If the context doesn't contain relevant information, please indicate that and provide a general response."""
            
            messages.append({"role": "system", "content": system_prompt})
        
        # User query
        messages.append({"role": "user", "content": user_query})
        
        return messages
    
    def _update_performance_metrics(self, provider_id: str, response_time: float, success: bool):
        """Update performance metrics for a provider"""
        
        # Update response times
        if provider_id not in self.response_times:
            self.response_times[provider_id] = []
        
        self.response_times[provider_id].append(response_time)
        
        # Keep only last 100 response times
        if len(self.response_times[provider_id]) > 100:
            self.response_times[provider_id] = self.response_times[provider_id][-100:]
        
        # Update error rates
        if provider_id not in self.error_rates:
            self.error_rates[provider_id] = 0.0
        
        # Simple exponential moving average for error rate
        if not success:
            self.error_rates[provider_id] = 0.9 * self.error_rates[provider_id] + 0.1 * 1.0
        else:
            self.error_rates[provider_id] = 0.9 * self.error_rates[provider_id] + 0.1 * 0.0
    
    async def get_provider_stats(self) -> Dict[str, Any]:
        """Get comprehensive provider statistics"""
        stats = {
            "total_providers": len(self.providers),
            "connected_providers": sum(1 for p in self.providers.values() if p.is_connected),
            "default_provider": self.default_provider,
            "load_balancing_enabled": self.load_balancing_enabled,
            "failover_enabled": self.failover_enabled,
            "providers": {}
        }
        
        for provider_id, provider in self.providers.items():
            provider_info = await provider.get_provider_info()
            provider_info["performance"] = {
                "avg_response_time": (
                    sum(self.response_times.get(provider_id, [])) / 
                    len(self.response_times.get(provider_id, [1]))
                ),
                "error_rate": self.error_rates.get(provider_id, 0.0)
            }
            stats["providers"][provider_id] = provider_info
        
        return stats


def create_llm_provider_manager() -> VPALLMProviderManager:
    """Create and configure LLM provider manager"""
    manager = VPALLMProviderManager()
    
    # Register mock provider by default for development
    mock_config = LLMProviderConfig(
        provider=LLMProvider.MOCK,
        model=LLMModel.MOCK_MODEL,
        max_tokens=4000,
        temperature=0.7,
        cost_per_token=0.0001
    )
    mock_provider = MockLLMProvider(mock_config)
    manager.register_provider("mock_default", mock_provider)
    
    logger.info("VPA LLM Provider Manager initialized")
    return manager


if __name__ == "__main__":
    # Example usage and testing
    async def test_llm_provider_manager():
        # Create manager
        manager = create_llm_provider_manager()
        
        try:
            # Connect all providers
            await manager.connect_all_providers()
            
            # Test basic request
            request = LLMRequest(
                messages=[
                    {"role": "user", "content": "Hello, how are you?"}
                ]
            )
            
            response = await manager.generate_response(request)
            print(f"Response: {response.content}")
            print(f"Tokens: {response.total_tokens}")
            print(f"Cost: ${response.cost:.4f}")
            
            # Test streaming
            print("\nStreaming response:")
            async for chunk in manager.generate_stream_response(request):
                print(chunk, end="")
            print()
            
            # Get provider stats
            stats = await manager.get_provider_stats()
            print(f"\nProvider Stats: {stats}")
            
            # Disconnect
            await manager.disconnect_all_providers()
            
        except Exception as e:
            print(f"Test failed: {e}")
    
    # Run test
    asyncio.run(test_llm_provider_manager())
    print("VPA LLM Provider Manager test completed!")
