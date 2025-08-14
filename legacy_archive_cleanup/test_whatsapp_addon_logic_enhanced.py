"""
Comprehensive tests for enhanced WhatsApp Addon Logic

Tests real API integration with Twilio, messaging operations,
media sharing, and business automation functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime
import json
import os

# Import the enhanced WhatsApp logic
from src.vpa.ai.addon_logic.whatsapp_logic_enhanced import WhatsAppAPIClient, WhatsAppLogicEnhanced
from src.vpa.ai.addon_logic.base_addon_logic import AddonWorkflow, AddonCapability

@pytest.fixture
def mock_twilio_client():
    """Create a mock Twilio client for testing"""
    mock_client = Mock()
    mock_message = Mock()
    mock_message.sid = "test_message_sid_123"
    mock_message.status = "sent"
    mock_message.error_code = None
    mock_message.error_message = None
    mock_message.date_sent = datetime.now()
    mock_message.date_updated = datetime.now()
    
    mock_client.messages.create.return_value = mock_message
    mock_client.messages.return_value.fetch.return_value = mock_message
    
    # Mock account info
    mock_account = Mock()
    mock_account.status = "active"
    mock_client.api.accounts.return_value.fetch.return_value = mock_account
    
    return mock_client

@pytest.fixture
def whatsapp_api_client(mock_twilio_client):
    """Create WhatsApp API client with mocked Twilio"""
    with patch('src.vpa.ai.addon_logic.whatsapp_logic_enhanced.Client', return_value=mock_twilio_client):
        client = WhatsAppAPIClient(
            account_sid="test_account_sid",
            auth_token="test_auth_token",
            whatsapp_number="whatsapp:+1234567890"
        )
        return client

@pytest.fixture
def whatsapp_logic():
    """Create WhatsApp logic instance"""
    return WhatsAppLogicEnhanced()

class TestWhatsAppAPIClient:
    """Test the WhatsApp API client functionality"""
    
    @pytest.mark.asyncio
    async def test_api_client_initialization(self):
        """Test API client initialization with different credential scenarios"""
        # Test with explicit credentials
        client = WhatsAppAPIClient(
            account_sid="test_sid",
            auth_token="test_token",
            whatsapp_number="whatsapp:+1234567890"
        )
        assert client.account_sid == "test_sid"
        assert client.auth_token == "test_token"
        assert client.whatsapp_number == "whatsapp:+1234567890"
        
        # Test with missing credentials
        client_no_creds = WhatsAppAPIClient()
        assert client_no_creds.client is None
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, whatsapp_api_client):
        """Test successful message sending"""
        result = await whatsapp_api_client.send_message("+1234567890", "Test message")
        
        assert result['status'] == 'success'
        assert result['message_id'] == "test_message_sid_123"
        assert result['message_status'] == "sent"
        assert result['method'] == 'twilio'
    
    @pytest.mark.asyncio
    async def test_send_message_no_client(self):
        """Test message sending without Twilio client"""
        client = WhatsAppAPIClient()  # No credentials
        result = await client.send_message("+1234567890", "Test message")
        
        assert result['status'] == 'error'
        assert 'not configured' in result['error']
    
    @pytest.mark.asyncio
    async def test_send_message_formats_phone_number(self, whatsapp_api_client):
        """Test that phone numbers are properly formatted"""
        await whatsapp_api_client.send_message("+1234567890", "Test message")
        
        # Check that the phone number was formatted for WhatsApp
        whatsapp_api_client.client.messages.create.assert_called_with(
            from_="whatsapp:+1234567890",
            body="Test message",
            to="whatsapp:+1234567890"
        )
    
    @pytest.mark.asyncio
    async def test_send_media_message_success(self, whatsapp_api_client):
        """Test successful media message sending"""
        result = await whatsapp_api_client.send_media_message(
            "+1234567890", 
            "https://example.com/image.jpg", 
            "Test caption"
        )
        
        assert result['status'] == 'success'
        assert result['message_id'] == "test_message_sid_123"
        assert result['media_url'] == "https://example.com/image.jpg"
    
    @pytest.mark.asyncio
    async def test_send_media_message_no_client(self):
        """Test media message sending without Twilio client"""
        client = WhatsAppAPIClient()  # No credentials
        result = await client.send_media_message(
            "+1234567890", 
            "https://example.com/image.jpg"
        )
        
        assert result['status'] == 'error'
        assert 'require Twilio Business API' in result['error']
    
    @pytest.mark.asyncio
    async def test_send_template_message_success(self, whatsapp_api_client):
        """Test successful template message sending"""
        result = await whatsapp_api_client.send_template_message(
            "+1234567890",
            "template_sid_123",
            {"name": "John", "order_id": "12345"}
        )
        
        assert result['status'] == 'success'
        assert result['message_id'] == "test_message_sid_123"
        assert result['template_sid'] == "template_sid_123"
    
    @pytest.mark.asyncio
    async def test_get_message_status_success(self, whatsapp_api_client):
        """Test successful message status retrieval"""
        result = await whatsapp_api_client.get_message_status("test_message_sid_123")
        
        assert result['status'] == 'success'
        assert result['message_id'] == "test_message_sid_123"
        assert result['message_status'] == "sent"

class TestWhatsAppLogicEnhanced:
    """Test the enhanced WhatsApp logic functionality"""
    
    def test_initialization(self, whatsapp_logic):
        """Test WhatsApp logic initialization"""
        assert whatsapp_logic._get_addon_name() == "whatsapp"
        assert hasattr(whatsapp_logic, 'api_client')
        assert hasattr(whatsapp_logic, 'default_templates')
    
    @pytest.mark.asyncio
    async def test_register_workflows(self, whatsapp_logic):
        """Test workflow registration"""
        await whatsapp_logic._register_workflows()
        
        # Check that workflows were registered
        assert len(whatsapp_logic.workflows) >= 3
        
        # Check specific workflows
        workflow_ids = [w.workflow_id for w in whatsapp_logic.workflows]
        assert "whatsapp_messaging_enhanced" in workflow_ids
        assert "whatsapp_media_enhanced" in workflow_ids
        assert "whatsapp_business_enhanced" in workflow_ids
    
    @pytest.mark.asyncio
    async def test_register_capabilities(self, whatsapp_logic):
        """Test capability registration"""
        await whatsapp_logic._register_capabilities()
        
        # Check that capabilities were registered
        assert len(whatsapp_logic.capabilities) >= 3
        
        # Check specific capabilities
        capability_ids = [c.capability_id for c in whatsapp_logic.capabilities]
        assert "whatsapp_messaging_real" in capability_ids
        assert "whatsapp_media_real" in capability_ids
        assert "whatsapp_business_real" in capability_ids
    
    @pytest.mark.asyncio
    async def test_execute_action_authenticate_twilio(self, whatsapp_logic):
        """Test Twilio authentication action"""
        with patch.object(whatsapp_logic.api_client, 'client') as mock_client:
            with patch.object(whatsapp_logic.api_client, 'account_sid', 'test_sid'):
                mock_account = Mock()
                mock_account.status = "active"
                mock_client.api.accounts.return_value.fetch.return_value = mock_account
                
                result = await whatsapp_logic._execute_action("authenticate_twilio", {"api_version": "v1"})
                
                assert result["success"] is True
                assert result["authenticated"] is True
                assert result["account_status"] == "active"
    
    @pytest.mark.asyncio
    async def test_execute_action_send_message_real(self, whatsapp_logic):
        """Test real message sending action"""
        with patch.object(whatsapp_logic.api_client, 'send_message') as mock_send:
            mock_send.return_value = {
                'status': 'success',
                'message_id': 'test_msg_123',
                'method': 'twilio'
            }
            
            result = await whatsapp_logic._execute_action("send_message_real", {
                'to_number': '+1234567890',
                'message': 'Test message'
            })
            
            assert result["success"] is True
            assert result["action"] == "send_message_real"
            assert result["result"]["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_execute_action_send_media_message(self, whatsapp_logic):
        """Test real media message sending action"""
        with patch.object(whatsapp_logic.api_client, 'send_media_message') as mock_send:
            mock_send.return_value = {
                'status': 'success',
                'message_id': 'test_media_123',
                'media_url': 'https://example.com/image.jpg'
            }
            
            result = await whatsapp_logic._execute_action("send_media_message", {
                'to_number': '+1234567890',
                'media_url': 'https://example.com/image.jpg',
                'caption': 'Test image'
            })
            
            assert result["success"] is True
            assert result["action"] == "send_media_message_real"
            assert result["result"]["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_execute_action_send_template_message(self, whatsapp_logic):
        """Test real template message sending action"""
        with patch.object(whatsapp_logic.api_client, 'send_template_message') as mock_send:
            mock_send.return_value = {
                'status': 'success',
                'message_id': 'test_template_123',
                'template_sid': 'template_456'
            }
            
            result = await whatsapp_logic._execute_action("send_template_message", {
                'to_number': '+1234567890',
                'template_sid': 'template_456',
                'variables': {'name': 'John'}
            })
            
            assert result["success"] is True
            assert result["action"] == "send_template_message_real"
            assert result["result"]["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_execute_action_check_message_status(self, whatsapp_logic):
        """Test message status checking action"""
        with patch.object(whatsapp_logic.api_client, 'get_message_status') as mock_status:
            mock_status.return_value = {
                'status': 'success',
                'message_id': 'test_msg_123',
                'message_status': 'delivered'
            }
            
            result = await whatsapp_logic._execute_action("check_message_status", {
                'message_sid': 'test_msg_123'
            })
            
            assert result["success"] is True
            assert result["action"] == "check_message_status_real"
            assert result["result"]["message_status"] == "delivered"
    
    @pytest.mark.asyncio
    async def test_execute_action_customer_service(self, whatsapp_logic):
        """Test customer service automation action"""
        result = await whatsapp_logic._execute_action("handle_customer_service", {
            'inquiry_type': 'support',
            'customer_message': 'I need help'
        })
        
        assert result["success"] is True
        assert result["action"] == "handle_customer_service_real"
        assert result["inquiry_type"] == "support"
        assert result["ai_generated"] is True
        assert "support" in result["response"]
    
    @pytest.mark.asyncio
    async def test_execute_action_missing_parameters(self, whatsapp_logic):
        """Test action execution with missing parameters"""
        result = await whatsapp_logic._execute_action("send_message_real", {
            'to_number': '+1234567890'
            # Missing 'message' parameter
        })
        
        assert result["success"] is False
        assert "Missing required parameters" in result["error"]
    
    @pytest.mark.asyncio
    async def test_execute_action_unknown_action(self, whatsapp_logic):
        """Test execution of unknown action"""
        result = await whatsapp_logic._execute_action("unknown_action", {})
        
        assert result["success"] is False
        assert "Unknown enhanced WhatsApp action" in result["error"]

class TestWhatsAppIntegration:
    """Test WhatsApp integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_full_message_workflow(self, whatsapp_logic):
        """Test complete message sending workflow"""
        with patch.object(whatsapp_logic.api_client, 'client') as mock_client:
            with patch.object(whatsapp_logic.api_client, 'account_sid', 'test_sid'):
                # Mock authentication
                mock_account = Mock()
                mock_account.status = "active"
                mock_client.api.accounts.return_value.fetch.return_value = mock_account
                
                # Mock message sending
                mock_message = Mock()
                mock_message.sid = "msg_123"
                mock_message.status = "sent"
                mock_client.messages.create.return_value = mock_message
                
                # Test authentication
                auth_result = await whatsapp_logic._execute_action("authenticate_twilio", {})
                assert auth_result["success"] is True
                
                # Test message sending
                msg_result = await whatsapp_logic._execute_action("send_message_real", {
                    'to_number': '+1234567890',
                    'message': 'Hello from VPA!'
                })
                assert msg_result["success"] is True
    
    @pytest.mark.asyncio
    async def test_business_automation_workflow(self, whatsapp_logic):
        """Test business automation workflow"""
        # Test customer service handling
        cs_result = await whatsapp_logic._execute_action("handle_customer_service", {
            'inquiry_type': 'billing',
            'customer_message': 'Question about my bill'
        })
        
        assert cs_result["success"] is True
        assert cs_result["inquiry_type"] == "billing"
        assert "billing" in cs_result["response"].lower()
    
    @pytest.mark.asyncio
    async def test_error_handling(self, whatsapp_logic):
        """Test error handling in various scenarios"""
        # Test with invalid parameters
        result = await whatsapp_logic._execute_action("send_message_real", {})
        assert result["success"] is False
        
        # Test with API error simulation
        with patch.object(whatsapp_logic.api_client, 'send_message') as mock_send:
            mock_send.side_effect = Exception("API Error")
            
            result = await whatsapp_logic._execute_action("send_message_real", {
                'to_number': '+1234567890',
                'message': 'Test'
            })
            assert result["success"] is False
            assert "error" in result

class TestWhatsAppTemplates:
    """Test WhatsApp message templates"""
    
    def test_default_templates(self, whatsapp_logic):
        """Test default message templates"""
        templates = whatsapp_logic.default_templates
        
        assert 'welcome' in templates
        assert 'support' in templates
        assert 'order_confirmation' in templates
        assert 'appointment_reminder' in templates
        
        # Test template formatting
        order_template = templates['order_confirmation']
        assert '{order_id}' in order_template
        
        appointment_template = templates['appointment_reminder']
        assert '{date}' in appointment_template
        assert '{time}' in appointment_template

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
