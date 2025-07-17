"""
Tests for VPA RAG-LLM Integration System

This module contains comprehensive tests for the integrated RAG and LLM functionality,
ensuring seamless document retrieval and response generation.
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import Dict, List, Any

from src.vpa.core.llm import (
    VPALLMManager, MockLLMProvider, LLMConfig, LLMProvider, LLMMessage,
    VPARAGLLMIntegration, create_rag_llm_integration
)
from src.vpa.core.database import ConversationDatabaseManager


class TestVPARAGLLMIntegration:
    """Test suite for RAG-LLM Integration"""
    
    @pytest.fixture
    def llm_manager(self):
        """Create LLM manager for testing"""
        manager = VPALLMManager()
        
        # Register mock provider
        mock_config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model_name="mock-gpt-3.5-turbo"
        )
        mock_provider = MockLLMProvider(mock_config)
        manager.register_provider(LLMProvider.OPENAI, mock_provider)
        
        return manager
    
    @pytest.fixture
    def mock_rag_system(self):
        """Create mock RAG system for testing"""
        rag_system = Mock()
        
        # Mock search_knowledge method
        rag_system.search_knowledge.return_value = [
            {
                "chunk_id": "chunk_1",
                "document_id": "doc_1",
                "content": "This is relevant context about artificial intelligence.",
                "similarity": 0.85,
                "metadata": {"title": "AI Basics", "page": 1}
            },
            {
                "chunk_id": "chunk_2", 
                "document_id": "doc_1",
                "content": "Machine learning is a subset of artificial intelligence.",
                "similarity": 0.72,
                "metadata": {"title": "AI Basics", "page": 2}
            }
        ]
        
        return rag_system
    
    @pytest.fixture
    def rag_llm_integration(self, llm_manager, mock_rag_system):
        """Create RAG-LLM integration for testing"""
        return VPARAGLLMIntegration(llm_manager, mock_rag_system)
    
    def test_rag_llm_integration_initialization(self, llm_manager):
        """Test RAG-LLM integration initialization"""
        integration = VPARAGLLMIntegration(llm_manager)
        
        assert integration.llm_manager == llm_manager
        assert integration.rag_system is None
        assert integration.max_context_chunks == 5
        assert integration.min_similarity_threshold == 0.3
        assert integration.context_window_size == 2000
    
    def test_set_rag_system(self, rag_llm_integration, mock_rag_system):
        """Test setting RAG system"""
        new_rag_system = Mock()
        rag_llm_integration.set_rag_system(new_rag_system)
        
        assert rag_llm_integration.rag_system == new_rag_system
    
    @pytest.mark.asyncio
    async def test_generate_enhanced_response_with_rag(self, rag_llm_integration, mock_rag_system):
        """Test enhanced response generation with RAG"""
        user_id = "test_user"
        user_message = "What is artificial intelligence?"
        conversation_id = "test_conv"
        
        response = await rag_llm_integration.generate_enhanced_response(
            user_id=user_id,
            user_message=user_message,
            conversation_id=conversation_id,
            use_rag=True,
            rag_top_k=2
        )
        
        # Verify RAG system was called
        mock_rag_system.search_knowledge.assert_called_once_with(
            user_id=user_id,
            query=user_message,
            top_k=2,
            min_similarity=0.3
        )
        
        # Verify response structure
        assert response["success"] is True
        assert "response" in response
        assert response["rag_enabled"] is True
        assert response["rag_context_used"] is True
        assert response["rag_sources_count"] == 2
        assert len(response["rag_sources"]) == 2
        assert "rag_retrieval_time" in response
        assert "total_processing_time" in response
        assert "pipeline_stages" in response
        
        # Verify RAG sources metadata
        sources = response["rag_sources"]
        assert sources[0]["document_id"] == "doc_1"
        assert sources[0]["similarity"] == 0.85
        assert "content_preview" in sources[0]
        assert "metadata" in sources[0]
    
    @pytest.mark.asyncio
    async def test_generate_enhanced_response_without_rag(self, rag_llm_integration):
        """Test enhanced response generation without RAG"""
        user_id = "test_user"
        user_message = "Hello, how are you?"
        
        response = await rag_llm_integration.generate_enhanced_response(
            user_id=user_id,
            user_message=user_message,
            use_rag=False
        )
        
        # Verify response structure
        assert response["success"] is True
        assert "response" in response
        assert response["rag_enabled"] is False
        assert response["rag_context_used"] is False
        assert response["rag_sources_count"] == 0
        assert len(response["rag_sources"]) == 0
    
    @pytest.mark.asyncio
    async def test_generate_enhanced_response_no_rag_system(self, llm_manager):
        """Test enhanced response when no RAG system is available"""
        integration = VPARAGLLMIntegration(llm_manager, None)
        
        response = await integration.generate_enhanced_response(
            user_id="test_user",
            user_message="Test message",
            use_rag=True
        )
        
        # Should work without RAG
        assert response["success"] is True
        assert response["rag_enabled"] is False
        assert response["rag_context_used"] is False
        assert response["rag_sources_count"] == 0
    
    @pytest.mark.asyncio
    async def test_stream_enhanced_response_with_rag(self, rag_llm_integration, mock_rag_system):
        """Test streaming enhanced response with RAG"""
        user_id = "test_user"
        user_message = "Tell me about AI"
        
        chunks = []
        async for chunk in rag_llm_integration.stream_enhanced_response(
            user_id=user_id,
            user_message=user_message,
            use_rag=True,
            rag_top_k=2
        ):
            chunks.append(chunk)
        
        # Verify we got RAG context first, then LLM chunks
        assert len(chunks) > 0
        
        # First chunk should be RAG context
        rag_chunk = chunks[0]
        assert rag_chunk["type"] == "rag_context"
        assert rag_chunk["rag_sources_count"] == 2
        assert "rag_retrieval_time" in rag_chunk
        
        # Subsequent chunks should be LLM content
        llm_chunks = [c for c in chunks if c["type"] == "llm_chunk"]
        assert len(llm_chunks) > 0
        
        # Verify RAG system was called
        mock_rag_system.search_knowledge.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stream_enhanced_response_without_rag(self, rag_llm_integration):
        """Test streaming enhanced response without RAG"""
        chunks = []
        async for chunk in rag_llm_integration.stream_enhanced_response(
            user_id="test_user",
            user_message="Hello",
            use_rag=False
        ):
            chunks.append(chunk)
        
        # Should still get RAG context (empty) and LLM chunks
        assert len(chunks) > 0
        
        rag_chunk = chunks[0]
        assert rag_chunk["type"] == "rag_context"
        assert rag_chunk["rag_sources_count"] == 0
        assert rag_chunk["rag_retrieval_time"] == 0
    
    def test_build_rag_context(self, rag_llm_integration):
        """Test RAG context building"""
        rag_results = [
            {
                "content": "Content chunk 1",
                "similarity": 0.85,
                "document_id": "doc_1",
                "chunk_id": "chunk_1"
            },
            {
                "content": "Content chunk 2", 
                "similarity": 0.72,
                "document_id": "doc_2",
                "chunk_id": "chunk_2"
            }
        ]
        
        context = rag_llm_integration._build_rag_context(rag_results)
        
        assert "=== RELEVANT CONTEXT INFORMATION ===" in context
        assert "Source 1 (similarity: 0.85, doc: doc_1)" in context
        assert "Source 2 (similarity: 0.72, doc: doc_2)" in context
        assert "Content chunk 1" in context
        assert "Content chunk 2" in context
        assert "=== END CONTEXT ===" in context
    
    def test_build_rag_context_empty(self, rag_llm_integration):
        """Test RAG context building with empty results"""
        context = rag_llm_integration._build_rag_context([])
        assert context == ""
    
    def test_build_rag_context_size_limit(self, rag_llm_integration):
        """Test RAG context respects size limits"""
        # Set a very small context window
        rag_llm_integration.context_window_size = 100
        
        rag_results = [
            {
                "content": "Very long content that exceeds the context window size limit" * 10,
                "similarity": 0.85,
                "document_id": "doc_1",
                "chunk_id": "chunk_1"
            }
        ]
        
        context = rag_llm_integration._build_rag_context(rag_results)
        
        # Should be truncated
        assert len(context) <= rag_llm_integration.context_window_size + 200  # Some overhead for formatting
    
    def test_extract_source_metadata(self, rag_llm_integration):
        """Test source metadata extraction"""
        rag_results = [
            {
                "document_id": "doc_1",
                "chunk_id": "chunk_1",
                "similarity": 0.85,
                "content": "This is a test content that is longer than 100 characters to test the preview truncation functionality",
                "metadata": {"title": "Test Document", "page": 1}
            }
        ]
        
        sources = rag_llm_integration._extract_source_metadata(rag_results)
        
        assert len(sources) == 1
        source = sources[0]
        assert source["document_id"] == "doc_1"
        assert source["chunk_id"] == "chunk_1"
        assert source["similarity"] == 0.85
        assert len(source["content_preview"]) <= 103  # 100 chars + "..."
        assert source["content_preview"].endswith("...")
        assert source["metadata"]["title"] == "Test Document"
    
    @pytest.mark.asyncio
    async def test_enhanced_response_error_handling(self, llm_manager):
        """Test error handling in enhanced response generation"""
        # Create integration with failing LLM manager
        failing_manager = Mock()
        failing_manager.generate_response = AsyncMock(side_effect=Exception("LLM error"))
        
        integration = VPARAGLLMIntegration(failing_manager)
        
        response = await integration.generate_enhanced_response(
            user_id="test_user",
            user_message="Test message"
        )
        
        assert response["success"] is False
        assert "error" in response
        assert "I apologize, but I'm experiencing technical difficulties" in response["response"]
    
    @pytest.mark.asyncio
    async def test_streaming_error_handling(self, llm_manager):
        """Test error handling in streaming response"""
        # Create integration with failing LLM manager
        failing_manager = Mock()
        failing_manager.stream_response = AsyncMock(side_effect=Exception("Stream error"))
        
        integration = VPARAGLLMIntegration(failing_manager)
        
        chunks = []
        async for chunk in integration.stream_enhanced_response(
            user_id="test_user",
            user_message="Test message",
            use_rag=False
        ):
            chunks.append(chunk)
        
        # Should get RAG context and error
        assert len(chunks) >= 2
        error_chunk = next((c for c in chunks if c["type"] == "error"), None)
        assert error_chunk is not None
        assert "error" in error_chunk


class TestRAGLLMIntegrationFactory:
    """Test RAG-LLM integration factory functions"""
    
    def test_create_rag_llm_integration(self):
        """Test creating RAG-LLM integration"""
        manager = VPALLMManager()
        mock_config = LLMConfig(provider=LLMProvider.OPENAI)
        mock_provider = MockLLMProvider(mock_config)
        manager.register_provider(LLMProvider.OPENAI, mock_provider)
        
        integration = create_rag_llm_integration(manager)
        
        assert isinstance(integration, VPARAGLLMIntegration)
        assert integration.llm_manager == manager
        assert integration.rag_system is None
    
    def test_create_rag_llm_integration_with_rag(self):
        """Test creating RAG-LLM integration with RAG system"""
        manager = VPALLMManager()
        mock_config = LLMConfig(provider=LLMProvider.OPENAI)
        mock_provider = MockLLMProvider(mock_config)
        manager.register_provider(LLMProvider.OPENAI, mock_provider)
        
        mock_rag = Mock()
        integration = create_rag_llm_integration(manager, mock_rag)
        
        assert isinstance(integration, VPARAGLLMIntegration)
        assert integration.llm_manager == manager
        assert integration.rag_system == mock_rag


class TestRAGLLMPerformance:
    """Test performance characteristics of RAG-LLM integration"""
    
    @pytest.fixture
    def llm_manager(self):
        """Create LLM manager for testing"""
        manager = VPALLMManager()
        
        # Register mock provider
        mock_config = LLMConfig(
            provider=LLMProvider.OPENAI,
            model_name="mock-gpt-3.5-turbo"
        )
        mock_provider = MockLLMProvider(mock_config)
        manager.register_provider(LLMProvider.OPENAI, mock_provider)
        
        return manager
    
    @pytest.fixture
    def mock_rag_system(self):
        """Create mock RAG system for testing"""
        rag_system = Mock()
        
        # Mock search_knowledge method
        rag_system.search_knowledge.return_value = [
            {
                "chunk_id": "chunk_1",
                "document_id": "doc_1",
                "content": "This is relevant context about artificial intelligence.",
                "similarity": 0.85,
                "metadata": {"title": "AI Basics", "page": 1}
            }
        ]
        
        return rag_system
    
    @pytest.fixture
    def rag_llm_integration(self, llm_manager, mock_rag_system):
        """Create RAG-LLM integration for testing"""
        return VPARAGLLMIntegration(llm_manager, mock_rag_system)
    
    @pytest.mark.asyncio
    async def test_response_timing_metrics(self, rag_llm_integration, mock_rag_system):
        """Test that timing metrics are properly recorded"""
        # Add delay to RAG search to test timing
        import time
        original_search = mock_rag_system.search_knowledge
        
        def delayed_search(*args, **kwargs):
            time.sleep(0.01)  # 10ms delay
            return original_search.return_value
        
        mock_rag_system.search_knowledge.side_effect = delayed_search
        
        response = await rag_llm_integration.generate_enhanced_response(
            user_id="test_user",
            user_message="Test timing",
            use_rag=True
        )
        
        # Verify timing metrics exist and are reasonable
        assert response["rag_retrieval_time"] > 0
        assert response["total_processing_time"] > 0
        assert response["pipeline_stages"]["rag_retrieval"] > 0
        assert response["pipeline_stages"]["llm_generation"] > 0
        assert response["pipeline_stages"]["total"] > 0
        
        # Total should be sum of components (with some tolerance for overhead)
        total_components = (response["pipeline_stages"]["rag_retrieval"] + 
                          response["pipeline_stages"]["llm_generation"])
        assert abs(response["pipeline_stages"]["total"] - total_components) < 0.1
    
    def test_rag_context_size_optimization(self, rag_llm_integration):
        """Test that RAG context respects size limits for performance"""
        # Create moderately sized content chunks (not too large to be completely excluded)
        large_rag_results = []
        for i in range(10):
            large_rag_results.append({
                "content": "Content chunk with moderate size " * 20,  # ~600 chars each
                "similarity": 0.8 - (i * 0.05),
                "document_id": f"doc_{i}",
                "chunk_id": f"chunk_{i}"
            })
        
        context = rag_llm_integration._build_rag_context(large_rag_results)
        
        # Should be limited by context window size but not empty
        assert len(context) > 0  # Should have some content
        assert len(context) <= rag_llm_integration.context_window_size + 500  # Some overhead
        
        # Should include highest similarity chunks first if context fits
        if len(context) > 100:  # If we have reasonable content
            assert "doc_0" in context  # Highest similarity
        
        # Should not include all chunks due to size limits
        assert "doc_9" not in context  # Lowest similarity, likely excluded


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
