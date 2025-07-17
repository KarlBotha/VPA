"""
Tests for VPA LLM Integration System

This module contains comprehensive tests for the LLM integration,
including mock providers, rate limiting, conversation management,
and integration with the RAG system.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.vpa.core.llm import (
    LLMProvider, LLMConfig, LLMMessage, LLMResponse,
    RateLimiter, BaseLLMProvider, MockLLMProvider,
    VPALLMManager, create_llm_manager,
    enhance_conversation_with_llm
)


class TestLLMConfig:
    """Test LLM configuration dataclass"""
    
    def test_llm_config_creation(self):
        """Test LLM config creation with defaults"""
        config = LLMConfig(provider=LLMProvider.OPENAI)
        
        assert config.provider == LLMProvider.OPENAI
        assert config.model_name == "gpt-3.5-turbo"
        assert config.max_tokens == 2048
        assert config.temperature == 0.7
        assert config.timeout == 30
        assert config.rate_limit_rpm == 60
        assert config.rate_limit_tpm == 40000
    
    def test_llm_config_custom_values(self):
        """Test LLM config with custom values"""
        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            api_key="test-key",
            model_name="claude-3",
            max_tokens=4096,
            temperature=0.9
        )
        
        assert config.provider == LLMProvider.ANTHROPIC
        assert config.api_key == "test-key"
        assert config.model_name == "claude-3"
        assert config.max_tokens == 4096
        assert config.temperature == 0.9


class TestLLMMessage:
    """Test LLM message dataclass"""
    
    def test_llm_message_creation(self):
        """Test LLM message creation"""
        message = LLMMessage(role="user", content="Hello world")
        
        assert message.role == "user"
        assert message.content == "Hello world"
        assert isinstance(message.timestamp, datetime)
        assert message.metadata is None
    
    def test_llm_message_with_metadata(self):
        """Test LLM message with metadata"""
        metadata = {"source": "test", "priority": "high"}
        message = LLMMessage(
            role="assistant",
            content="Response",
            metadata=metadata
        )
        
        assert message.metadata == metadata


class TestLLMResponse:
    """Test LLM response dataclass"""
    
    def test_llm_response_creation(self):
        """Test LLM response creation"""
        usage = {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        response = LLMResponse(
            content="Test response",
            provider=LLMProvider.OPENAI,
            model="gpt-3.5-turbo",
            usage=usage,
            response_time=0.5,
            finish_reason="stop"
        )
        
        assert response.content == "Test response"
        assert response.provider == LLMProvider.OPENAI
        assert response.model == "gpt-3.5-turbo"
        assert response.usage == usage
        assert response.response_time == 0.5
        assert response.finish_reason == "stop"


class TestRateLimiter:
    """Test rate limiting functionality"""
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization"""
        limiter = RateLimiter(rpm=100, tpm=50000)
        
        assert limiter.rpm == 100
        assert limiter.tpm == 50000
        assert limiter.request_times == []
        assert limiter.token_usage == []
    
    def test_can_make_request_empty(self):
        """Test rate limiter allows requests when empty"""
        limiter = RateLimiter(rpm=60, tpm=40000)
        
        assert limiter.can_make_request() is True
        assert limiter.can_make_request(1000) is True
    
    def test_rate_limit_enforcement(self):
        """Test rate limit enforcement"""
        limiter = RateLimiter(rpm=2, tpm=100)  # Very low limits for testing
        
        # First two requests should pass
        assert limiter.can_make_request(10) is True
        limiter.record_request(10)
        
        assert limiter.can_make_request(10) is True
        limiter.record_request(10)
        
        # Third request should fail (RPM limit)
        assert limiter.can_make_request(10) is False
    
    def test_token_limit_enforcement(self):
        """Test token rate limit enforcement"""
        limiter = RateLimiter(rpm=100, tpm=50)  # Low token limit
        
        # Request within token limit should pass
        assert limiter.can_make_request(40) is True
        limiter.record_request(40)
        
        # Request exceeding token limit should fail
        assert limiter.can_make_request(20) is False
    
    def test_rate_limit_reset_over_time(self):
        """Test that rate limits reset over time"""
        limiter = RateLimiter(rpm=1, tpm=100)
        
        # Make request
        assert limiter.can_make_request(10) is True
        limiter.record_request(10)
        
        # Immediate second request should fail
        assert limiter.can_make_request(10) is False
        
        # Simulate time passage by directly manipulating request_times
        limiter.request_times = [time.time() - 70]  # 70 seconds ago
        limiter.token_usage = [(time.time() - 70, 10)]
        
        # Should be able to make request again
        assert limiter.can_make_request(10) is True


class TestMockLLMProvider:
    """Test mock LLM provider"""
    
    @pytest.fixture
    def mock_provider(self):
        """Create mock LLM provider for testing"""
        config = LLMConfig(provider=LLMProvider.OPENAI)
        return MockLLMProvider(config)
    
    @pytest.mark.asyncio
    async def test_generate_response(self, mock_provider):
        """Test mock response generation"""
        messages = [LLMMessage("user", "Hello, how are you?")]
        
        response = await mock_provider.generate_response(messages)
        
        assert isinstance(response, LLMResponse)
        assert "Mock response to: Hello, how are you?" in response.content
        assert response.provider == LLMProvider.OPENAI
        assert response.usage["total_tokens"] == 30
        assert response.response_time > 0
    
    @pytest.mark.asyncio
    async def test_stream_response(self, mock_provider):
        """Test mock streaming response"""
        messages = [LLMMessage("user", "Tell me a story")]
        
        chunks = []
        async for chunk in mock_provider.stream_response(messages):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert "mock streaming response" in full_response.lower()
    
    def test_estimate_tokens(self, mock_provider):
        """Test token estimation"""
        text = "This is a test message"
        tokens = mock_provider.estimate_tokens(text)
        
        # Should be roughly text length / 4
        expected = len(text) // 4
        assert tokens == expected


class TestVPALLMManager:
    """Test VPA LLM Manager"""
    
    @pytest.fixture
    def llm_manager(self):
        """Create LLM manager for testing"""
        return VPALLMManager()
    
    @pytest.fixture
    def mock_provider(self):
        """Create mock provider for testing"""
        config = LLMConfig(provider=LLMProvider.OPENAI)
        return MockLLMProvider(config)
    
    def test_register_provider(self, llm_manager, mock_provider):
        """Test provider registration"""
        llm_manager.register_provider(LLMProvider.OPENAI, mock_provider)
        
        assert LLMProvider.OPENAI in llm_manager.providers
        assert llm_manager.providers[LLMProvider.OPENAI] == mock_provider
        assert llm_manager.default_provider == LLMProvider.OPENAI
    
    def test_set_default_provider(self, llm_manager, mock_provider):
        """Test setting default provider"""
        # Register multiple providers
        llm_manager.register_provider(LLMProvider.OPENAI, mock_provider)
        
        config2 = LLMConfig(provider=LLMProvider.ANTHROPIC)
        mock_provider2 = MockLLMProvider(config2)
        llm_manager.register_provider(LLMProvider.ANTHROPIC, mock_provider2)
        
        # Set default to Anthropic
        llm_manager.set_default_provider(LLMProvider.ANTHROPIC)
        assert llm_manager.default_provider == LLMProvider.ANTHROPIC
    
    def test_set_default_provider_not_registered(self, llm_manager):
        """Test setting default provider that's not registered"""
        with pytest.raises(ValueError, match="Provider anthropic not registered"):
            llm_manager.set_default_provider(LLMProvider.ANTHROPIC)
    
    @pytest.mark.asyncio
    async def test_generate_response(self, llm_manager, mock_provider):
        """Test response generation"""
        llm_manager.register_provider(LLMProvider.OPENAI, mock_provider)
        
        response = await llm_manager.generate_response(
            user_id="test_user",
            message="Hello world"
        )
        
        assert isinstance(response, LLMResponse)
        assert "Mock response to: Hello world" in response.content
        assert response.provider == LLMProvider.OPENAI
    
    @pytest.mark.asyncio
    async def test_generate_response_with_context(self, llm_manager, mock_provider):
        """Test response generation with context"""
        llm_manager.register_provider(LLMProvider.OPENAI, mock_provider)
        
        response = await llm_manager.generate_response(
            user_id="test_user",
            message="What is VPA?",
            context="VPA is a virtual personal assistant."
        )
        
        assert isinstance(response, LLMResponse)
        assert response.content is not None
    
    @pytest.mark.asyncio
    async def test_generate_response_no_provider(self, llm_manager):
        """Test response generation with no provider"""
        with pytest.raises(ValueError, match="No available LLM provider"):
            await llm_manager.generate_response(
                user_id="test_user",
                message="Hello"
            )
    
    @pytest.mark.asyncio
    async def test_stream_response(self, llm_manager, mock_provider):
        """Test streaming response"""
        llm_manager.register_provider(LLMProvider.OPENAI, mock_provider)
        
        chunks = []
        async for chunk in llm_manager.stream_response(
            user_id="test_user",
            message="Tell me a story"
        ):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert len(full_response) > 0
    
    def test_conversation_history(self, llm_manager):
        """Test conversation history management"""
        user_id = "test_user"
        conversation_id = "test_conv"
        
        # Initially empty
        history = llm_manager.get_conversation_history(user_id, conversation_id)
        assert history == []
        
        # Update history manually for testing
        messages = [
            LLMMessage("user", "Hello"),
            LLMMessage("assistant", "Hi there!")
        ]
        
        history_key = f"{user_id}:{conversation_id}"
        llm_manager.conversation_history[history_key] = messages
        
        # Retrieve history
        history = llm_manager.get_conversation_history(user_id, conversation_id)
        assert len(history) == 2
        assert history[0].content == "Hello"
        assert history[1].content == "Hi there!"
    
    def test_clear_conversation_history(self, llm_manager):
        """Test clearing conversation history"""
        user_id = "test_user"
        conversation_id = "test_conv"
        history_key = f"{user_id}:{conversation_id}"
        
        # Add some history
        llm_manager.conversation_history[history_key] = [
            LLMMessage("user", "Hello")
        ]
        
        # Clear history
        llm_manager.clear_conversation_history(user_id, conversation_id)
        
        # Should be empty
        history = llm_manager.get_conversation_history(user_id, conversation_id)
        assert history == []
    
    def test_build_messages_basic(self, llm_manager):
        """Test building messages for LLM request"""
        messages = llm_manager._build_messages(
            user_id="test_user",
            message="Hello world"
        )
        
        # Should have system prompt and user message
        assert len(messages) >= 2
        assert messages[0].role == "system"
        assert messages[-1].role == "user"
        assert messages[-1].content == "Hello world"
    
    def test_build_messages_with_context(self, llm_manager):
        """Test building messages with context"""
        messages = llm_manager._build_messages(
            user_id="test_user",
            message="What is VPA?",
            context="VPA is a virtual personal assistant."
        )
        
        # Should have system prompt, context, and user message
        assert len(messages) >= 3
        assert any("Context information" in msg.content for msg in messages)
    
    def test_build_messages_with_history(self, llm_manager):
        """Test building messages with conversation history"""
        user_id = "test_user"
        conversation_id = "test_conv"
        history_key = f"{user_id}:{conversation_id}"
        
        # Add conversation history
        llm_manager.conversation_history[history_key] = [
            LLMMessage("user", "Previous question"),
            LLMMessage("assistant", "Previous answer")
        ]
        
        messages = llm_manager._build_messages(
            user_id=user_id,
            message="Current question",
            conversation_id=conversation_id
        )
        
        # Should include history
        assert len(messages) >= 4  # system + history + current
        assert any(msg.content == "Previous question" for msg in messages)
        assert any(msg.content == "Previous answer" for msg in messages)


class TestLLMIntegration:
    """Test LLM integration functions"""
    
    def test_create_llm_manager(self):
        """Test LLM manager creation"""
        manager = create_llm_manager()
        
        assert isinstance(manager, VPALLMManager)
        assert LLMProvider.OPENAI in manager.providers
        assert manager.default_provider == LLMProvider.OPENAI
    
    def test_enhance_conversation_with_llm_success(self):
        """Test conversation enhancement with LLM"""
        manager = create_llm_manager()
        
        result = enhance_conversation_with_llm(
            llm_manager=manager,
            user_id="test_user",
            user_message="Hello world"
        )
        
        assert result["success"] is True
        assert "response" in result
        assert "provider" in result
        assert "usage" in result
        assert result["provider"] == "openai"
    
    def test_enhance_conversation_with_llm_with_context(self):
        """Test conversation enhancement with context"""
        manager = create_llm_manager()
        
        result = enhance_conversation_with_llm(
            llm_manager=manager,
            user_id="test_user",
            user_message="What is VPA?",
            context="VPA is a virtual personal assistant system."
        )
        
        assert result["success"] is True
        assert result["response"] is not None
    
    @patch('src.vpa.core.llm.asyncio.run')
    def test_enhance_conversation_with_llm_error(self, mock_run):
        """Test conversation enhancement error handling"""
        mock_run.side_effect = Exception("LLM API error")
        
        manager = create_llm_manager()
        
        result = enhance_conversation_with_llm(
            llm_manager=manager,
            user_id="test_user",
            user_message="Hello"
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "I apologize" in result["response"]


class TestLLMProviderEnum:
    """Test LLM provider enumeration"""
    
    def test_provider_values(self):
        """Test provider enum values"""
        assert LLMProvider.OPENAI.value == "openai"
        assert LLMProvider.ANTHROPIC.value == "anthropic"
        assert LLMProvider.AZURE_OPENAI.value == "azure_openai"
        assert LLMProvider.LOCAL_OLLAMA.value == "local_ollama"
        assert LLMProvider.GOOGLE_GEMINI.value == "google_gemini"


if __name__ == "__main__":
    # Run tests if file is executed directly
    pytest.main([__file__, "-v"])
