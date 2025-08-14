"""
Comprehensive tests for enhanced Telegram Addon Logic

Tests real API integration with Telegram Bot API, messaging operations,
media sharing, and bot management functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime
import json
import os

# Import the enhanced Telegram logic
from src.vpa.ai.addon_logic.telegram_logic_enhanced import TelegramAPIClient, TelegramLogicEnhanced
from src.vpa.ai.addon_logic.base_addon_logic import AddonWorkflow, AddonCapability

@pytest.fixture
def mock_telegram_bot():
    """Create a mock Telegram bot for testing"""
    mock_bot = AsyncMock()
    
    # Mock message object
    mock_message = Mock()
    mock_message.message_id = 123
    mock_message.chat.id = 456
    mock_message.date = datetime.now()
    mock_message.text = "Test message"
    mock_message.caption = "Test caption"
    
    # Mock photo and document
    mock_photo = Mock()
    mock_photo.file_id = "photo_file_id_123"
    mock_message.photo = [mock_photo]
    
    mock_document = Mock()
    mock_document.file_id = "document_file_id_123"
    mock_message.document = mock_document
    
    # Mock chat object
    mock_chat = Mock()
    mock_chat.id = 456
    mock_chat.type = "private"
    mock_chat.title = "Test Chat"
    mock_chat.username = "testuser"
    mock_chat.description = "Test description"
    
    # Mock bot info
    mock_bot_info = Mock()
    mock_bot_info.id = 789
    mock_bot_info.username = "test_bot"
    mock_bot_info.first_name = "Test Bot"
    mock_bot_info.can_join_groups = True
    mock_bot_info.can_read_all_group_messages = True
    mock_bot_info.supports_inline_queries = False
    
    # Setup method returns
    mock_bot.send_message.return_value = mock_message
    mock_bot.send_photo.return_value = mock_message
    mock_bot.send_document.return_value = mock_message
    mock_bot.get_chat.return_value = mock_chat
    mock_bot.get_me.return_value = mock_bot_info
    mock_bot.set_webhook.return_value = True
    
    return mock_bot

@pytest.fixture
def telegram_api_client(mock_telegram_bot):
    """Create Telegram API client with mocked bot"""
    with patch('src.vpa.ai.addon_logic.telegram_logic_enhanced.Bot', return_value=mock_telegram_bot), \
         patch('src.vpa.ai.addon_logic.telegram_logic_enhanced.AiogramBot'):
        client = TelegramAPIClient(bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
        return client

@pytest.fixture
def telegram_logic():
    """Create Telegram logic instance"""
    return TelegramLogicEnhanced()

class TestTelegramAPIClient:
    """Test the Telegram API client functionality"""
    
    def test_api_client_initialization(self):
        """Test API client initialization with different token scenarios"""
        # Test with valid token format (mock)
        with patch('src.vpa.ai.addon_logic.telegram_logic_enhanced.Bot'), \
             patch('src.vpa.ai.addon_logic.telegram_logic_enhanced.AiogramBot'):
            client = TelegramAPIClient(bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
            assert client.bot_token == "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
        
        # Test with missing token
        client_no_token = TelegramAPIClient()
        assert client_no_token.bot is None
        assert client_no_token.aiogram_bot is None
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, telegram_api_client):
        """Test successful message sending"""
        result = await telegram_api_client.send_message("456", "Test message")
        
        assert result['status'] == 'success'
        assert result['message_id'] == 123
        assert result['chat_id'] == 456
        assert result['text'] == "Test message"
    
    @pytest.mark.asyncio
    async def test_send_message_no_bot(self):
        """Test message sending without bot token"""
        client = TelegramAPIClient()  # No token
        result = await client.send_message("456", "Test message")
        
        assert result['status'] == 'error'
        assert 'not configured' in result['error']
    
    @pytest.mark.asyncio
    async def test_send_photo_success(self, telegram_api_client):
        """Test successful photo sending"""
        result = await telegram_api_client.send_photo(
            "456", 
            "https://example.com/photo.jpg", 
            "Test caption"
        )
        
        assert result['status'] == 'success'
        assert result['message_id'] == 123
        assert result['chat_id'] == 456
        assert result['photo_file_id'] == "photo_file_id_123"
        assert result['caption'] == "Test caption"
    
    @pytest.mark.asyncio
    async def test_send_document_success(self, telegram_api_client):
        """Test successful document sending"""
        result = await telegram_api_client.send_document(
            "456",
            "https://example.com/document.pdf",
            "Test document"
        )
        
        assert result['status'] == 'success'
        assert result['message_id'] == 123
        assert result['document_file_id'] == "document_file_id_123"
    
    @pytest.mark.asyncio
    async def test_get_chat_info_success(self, telegram_api_client):
        """Test successful chat info retrieval"""
        result = await telegram_api_client.get_chat_info("456")
        
        assert result['status'] == 'success'
        assert result['chat_id'] == 456
        assert result['chat_type'] == "private"
        assert result['title'] == "Test Chat"
        assert result['username'] == "testuser"
    
    @pytest.mark.asyncio
    async def test_get_bot_info_success(self, telegram_api_client):
        """Test successful bot info retrieval"""
        result = await telegram_api_client.get_bot_info()
        
        assert result['status'] == 'success'
        assert result['bot_id'] == 789
        assert result['bot_username'] == "test_bot"
        assert result['bot_first_name'] == "Test Bot"
        assert result['can_join_groups'] is True
    
    @pytest.mark.asyncio
    async def test_set_webhook_success(self, telegram_api_client):
        """Test successful webhook setting"""
        result = await telegram_api_client.set_webhook("https://example.com/webhook")
        
        assert result['status'] == 'success'
        assert result['webhook_set'] is True
        assert result['webhook_url'] == "https://example.com/webhook"

class TestTelegramLogicEnhanced:
    """Test the enhanced Telegram logic functionality"""
    
    def test_initialization(self, telegram_logic):
        """Test Telegram logic initialization"""
        assert telegram_logic._get_addon_name() == "telegram"
        assert hasattr(telegram_logic, 'api_client')
        assert hasattr(telegram_logic, 'bot_commands')
    
    def test_bot_commands(self, telegram_logic):
        """Test bot command definitions"""
        commands = telegram_logic.bot_commands
        
        assert '/start' in commands
        assert '/help' in commands
        assert '/status' in commands
        assert '/info' in commands
        
        assert 'Welcome' in commands['/start']
        assert 'Available commands' in commands['/help']
    
    @pytest.mark.asyncio
    async def test_register_workflows(self, telegram_logic):
        """Test workflow registration"""
        await telegram_logic._register_workflows()
        
        # Check that workflows were registered
        assert len(telegram_logic.workflows) >= 3
        
        # Check specific workflows
        workflow_ids = [w.workflow_id for w in telegram_logic.workflows]
        assert "telegram_messaging_enhanced" in workflow_ids
        assert "telegram_media_enhanced" in workflow_ids
        assert "telegram_bot_enhanced" in workflow_ids
    
    @pytest.mark.asyncio
    async def test_register_capabilities(self, telegram_logic):
        """Test capability registration"""
        await telegram_logic._register_capabilities()
        
        # Check that capabilities were registered
        assert len(telegram_logic.capabilities) >= 3
        
        # Check specific capabilities
        capability_ids = [c.capability_id for c in telegram_logic.capabilities]
        assert "telegram_messaging_real" in capability_ids
        assert "telegram_bot_real" in capability_ids
        assert "telegram_media_real" in capability_ids
    
    @pytest.mark.asyncio
    async def test_execute_action_authenticate_bot(self, telegram_logic):
        """Test bot authentication action"""
        with patch.object(telegram_logic.api_client, 'get_bot_info') as mock_get_info:
            mock_get_info.return_value = {
                'status': 'success',
                'bot_id': 789,
                'bot_username': 'test_bot'
            }
            
            result = await telegram_logic._execute_action("authenticate_bot", {})
            
            assert result["success"] is True
            assert result["action"] == "authenticate_bot"
            assert result["result"]["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_execute_action_send_message_real(self, telegram_logic):
        """Test real message sending action"""
        with patch.object(telegram_logic.api_client, 'send_message') as mock_send:
            mock_send.return_value = {
                'status': 'success',
                'message_id': 123,
                'chat_id': 456
            }
            
            result = await telegram_logic._execute_action("send_message_real", {
                'chat_id': '456',
                'text': 'Test message'
            })
            
            assert result["success"] is True
            assert result["action"] == "send_message_real"
            assert result["result"]["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_execute_action_send_photo_real(self, telegram_logic):
        """Test real photo sending action"""
        with patch.object(telegram_logic.api_client, 'send_photo') as mock_send:
            mock_send.return_value = {
                'status': 'success',
                'message_id': 123,
                'photo_file_id': 'photo_123'
            }
            
            result = await telegram_logic._execute_action("send_photo_real", {
                'chat_id': '456',
                'photo_url': 'https://example.com/photo.jpg',
                'caption': 'Test photo'
            })
            
            assert result["success"] is True
            assert result["action"] == "send_photo_real"
            assert result["result"]["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_execute_action_send_document_real(self, telegram_logic):
        """Test real document sending action"""
        with patch.object(telegram_logic.api_client, 'send_document') as mock_send:
            mock_send.return_value = {
                'status': 'success',
                'message_id': 123,
                'document_file_id': 'doc_123'
            }
            
            result = await telegram_logic._execute_action("send_document_real", {
                'chat_id': '456',
                'document_url': 'https://example.com/document.pdf',
                'caption': 'Test document'
            })
            
            assert result["success"] is True
            assert result["action"] == "send_document_real"
            assert result["result"]["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_execute_action_get_chat_info_real(self, telegram_logic):
        """Test chat info retrieval action"""
        with patch.object(telegram_logic.api_client, 'get_chat_info') as mock_get_info:
            mock_get_info.return_value = {
                'status': 'success',
                'chat_id': 456,
                'chat_type': 'private'
            }
            
            result = await telegram_logic._execute_action("get_chat_info_real", {
                'chat_id': '456'
            })
            
            assert result["success"] is True
            assert result["action"] == "get_chat_info_real"
            assert result["result"]["chat_type"] == "private"
    
    @pytest.mark.asyncio
    async def test_execute_action_handle_commands(self, telegram_logic):
        """Test bot command handling action"""
        result = await telegram_logic._execute_action("handle_commands", {
            'command': '/start'
        })
        
        assert result["success"] is True
        assert result["action"] == "handle_bot_commands"
        assert result["command"] == "/start"
        assert "Welcome" in result["response"]
    
    @pytest.mark.asyncio
    async def test_execute_action_manage_webhooks(self, telegram_logic):
        """Test webhook management action"""
        with patch.object(telegram_logic.api_client, 'set_webhook') as mock_set_webhook:
            mock_set_webhook.return_value = {
                'status': 'success',
                'webhook_set': True
            }
            
            result = await telegram_logic._execute_action("manage_webhooks", {
                'webhook_url': 'https://example.com/webhook'
            })
            
            assert result["success"] is True
            assert result["action"] == "manage_webhooks"
            assert result["operation"] == "set_webhook"
    
    @pytest.mark.asyncio
    async def test_execute_action_missing_parameters(self, telegram_logic):
        """Test action execution with missing parameters"""
        result = await telegram_logic._execute_action("send_message_real", {
            'chat_id': '456'
            # Missing 'text' parameter
        })
        
        assert result["success"] is False
        assert "Missing required parameters" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_action_unknown_action(self, telegram_logic):
        """Test execution of unknown action"""
        result = await telegram_logic._execute_action("unknown_action", {})
        
        assert result["success"] is False
        assert "Unknown enhanced Telegram action" in result["error"]

class TestTelegramIntegration:
    """Test Telegram integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_full_bot_workflow(self, telegram_logic):
        """Test complete bot workflow"""
        with patch.object(telegram_logic.api_client, 'get_bot_info') as mock_bot_info, \
             patch.object(telegram_logic.api_client, 'send_message') as mock_send_message:
            
            # Mock bot authentication
            mock_bot_info.return_value = {
                'status': 'success',
                'bot_id': 789,
                'bot_username': 'test_bot'
            }
            
            # Mock message sending
            mock_send_message.return_value = {
                'status': 'success',
                'message_id': 123,
                'chat_id': 456
            }
            
            # Test authentication
            auth_result = await telegram_logic._execute_action("authenticate_bot", {})
            assert auth_result["success"] is True
            
            # Test message sending
            msg_result = await telegram_logic._execute_action("send_message_real", {
                'chat_id': '456',
                'text': 'Hello from VPA Bot!'
            })
            assert msg_result["success"] is True
    
    @pytest.mark.asyncio
    async def test_media_sharing_workflow(self, telegram_logic):
        """Test media sharing workflow"""
        with patch.object(telegram_logic.api_client, 'send_photo') as mock_send_photo, \
             patch.object(telegram_logic.api_client, 'send_document') as mock_send_document:
            
            # Mock photo sending
            mock_send_photo.return_value = {
                'status': 'success',
                'message_id': 123,
                'photo_file_id': 'photo_123'
            }
            
            # Mock document sending
            mock_send_document.return_value = {
                'status': 'success',
                'message_id': 124,
                'document_file_id': 'doc_123'
            }
            
            # Test photo sending
            photo_result = await telegram_logic._execute_action("send_photo_real", {
                'chat_id': '456',
                'photo_url': 'https://example.com/image.jpg',
                'caption': 'Test image'
            })
            assert photo_result["success"] is True
            
            # Test document sending
            doc_result = await telegram_logic._execute_action("send_document_real", {
                'chat_id': '456',
                'document_url': 'https://example.com/document.pdf',
                'caption': 'Test document'
            })
            assert doc_result["success"] is True
    
    @pytest.mark.asyncio
    async def test_command_handling_workflow(self, telegram_logic):
        """Test bot command handling workflow"""
        # Test all predefined commands
        commands_to_test = ['/start', '/help', '/status', '/info']
        
        for command in commands_to_test:
            result = await telegram_logic._execute_action("handle_commands", {
                'command': command
            })
            assert result["success"] is True
            assert result["command"] == command
            assert len(result["response"]) > 0
        
        # Test unknown command
        unknown_result = await telegram_logic._execute_action("handle_commands", {
            'command': '/unknown'
        })
        assert unknown_result["success"] is True
        assert "Unknown command" in unknown_result["response"]
    
    @pytest.mark.asyncio
    async def test_error_handling(self, telegram_logic):
        """Test error handling in various scenarios"""
        # Test with invalid parameters
        result = await telegram_logic._execute_action("send_message_real", {})
        assert result["success"] is False
        
        # Test with API error simulation
        with patch.object(telegram_logic.api_client, 'send_message') as mock_send:
            mock_send.side_effect = Exception("API Error")
            
            result = await telegram_logic._execute_action("send_message_real", {
                'chat_id': '456',
                'text': 'Test'
            })
            assert result["success"] is False
            assert "error" in result

class TestTelegramAPI:
    """Test Telegram API specific scenarios"""
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, telegram_api_client):
        """Test API error handling"""
        # Simulate API error
        telegram_api_client.bot.send_message.side_effect = Exception("Telegram API Error")
        
        result = await telegram_api_client.send_message("456", "Test message")
        
        assert result['status'] == 'error'
        assert 'Telegram API Error' in result['error']
        assert result['error_type'] == 'Exception'
    
    @pytest.mark.asyncio
    async def test_parse_mode_support(self, telegram_api_client):
        """Test parse mode support in messages"""
        result = await telegram_api_client.send_message(
            "456", 
            "<b>Bold text</b>", 
            parse_mode="HTML"
        )
        
        # Verify that parse_mode was passed to the API call
        telegram_api_client.bot.send_message.assert_called_with(
            chat_id="456",
            text="<b>Bold text</b>",
            parse_mode="HTML"
        )
        
        assert result['status'] == 'success'

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
