````markdown
# Testing Requirements [DEPRECATED]

> **IMPORTANT NOTICE:** This document has been deprecated and moved to the proper documentation location. 
> 
> **NEW LOCATION:** [docs/development/testing_guide.md](docs/development/testing_guide.md)

## Overview

This document outlines the comprehensive testing requirements for the VPA application, ensuring reliability, functionality, and performance across all components.

## Table of Contents

1. [Testing Approach](#1-testing-approach)
2. [Unit Testing](#2-unit-testing)
3. [Integration Testing](#3-integration-testing)
4. [UI Testing](#4-ui-testing)
5. [Performance Testing](#5-performance-testing)
6. [Security Testing](#6-security-testing)
7. [Accessibility Testing](#7-accessibility-testing)
8. [Test Automation](#8-test-automation)
9. [Continuous Integration](#9-continuous-integration)

## 1. Testing Approach

### 1.1 Testing Methodology

VPA will follow a multi-layered testing approach:

1. **Test-Driven Development (TDD)**: Write tests before implementing features
2. **Continuous Testing**: Run automated tests on every code change
3. **Multi-level Testing**: Test at unit, integration, and system levels
4. **User-centric Testing**: Focus on user experience and realistic use cases

### 1.2 Testing Environments

| Environment | Purpose | Configuration |
|-------------|---------|--------------|
| Development | Local developer testing | Developer workstation |
| Integration | Component integration testing | Dedicated test environment |
| Staging | Pre-production validation | Mirror of production |
| Production | Live monitoring | Production environment |

### 1.3 Test Coverage Targets

| Component | Target Coverage | Critical Path Coverage |
|-----------|----------------|------------------------|
| Core Logic | 90%+ | 100% |
| UI Components | 80%+ | 100% |
| API Integration | 85%+ | 100% |
| Database Logic | 90%+ | 100% |
| Voice Processing | 85%+ | 100% |
| LLM Integration | 80%+ | 100% |

## 2. Unit Testing

### 2.1 Framework and Structure

VPA will use **pytest** as the primary testing framework:

```python
# Directory structure for tests
"""
tests/
  unit/
    core/
      test_event_bus.py
      test_settings_manager.py
      ...
    ui/
      test_chat_bubble.py
      test_input_field.py
      ...
    llm/
      test_model_manager.py
      test_ollama_adapter.py
      ...
    voice/
      test_voice_recognizer.py
      test_speech_to_text.py
      ...
    security/
      test_credential_manager.py
      test_encryption.py
      ...
"""
```

### 2.2 Core Components Unit Tests

All core components should have dedicated unit tests. Example for the EventBus:

```python
# test_event_bus.py
import pytest
import asyncio
from core.event_bus import EventBus

class TestEventBus:
    def setup_method(self):
        """Setup for each test"""
        self.event_bus = EventBus()
        self.received_events = []
        
    def test_subscribe_and_emit(self):
        """Test synchronous event subscription and emission"""
        # Setup
        def handler(data):
            self.received_events.append(data)
            
        # Subscribe to event
        self.event_bus.subscribe("test.event", handler)
        
        # Emit event
        self.event_bus.emit("test.event", {"value": 42})
        
        # Verify
        assert len(self.received_events) == 1
        assert self.received_events[0]["value"] == 42
        
    def test_unsubscribe(self):
        """Test unsubscribing from events"""
        # Setup
        def handler(data):
            self.received_events.append(data)
            
        # Subscribe to event
        subscription = self.event_bus.subscribe("test.event", handler)
        
        # Emit event
        self.event_bus.emit("test.event", {"value": 42})
        
        # Unsubscribe
        subscription.unsubscribe()
        
        # Emit again
        self.event_bus.emit("test.event", {"value": 43})
        
        # Verify
        assert len(self.received_events) == 1
        assert self.received_events[0]["value"] == 42
        
    @pytest.mark.asyncio
    async def test_async_subscribe_and_emit(self):
        """Test async event subscription and emission"""
        # Setup
        async def handler(data):
            self.received_events.append(data)
            
        # Subscribe to event
        self.event_bus.subscribe_async("test.async_event", handler)
        
        # Emit event
        await self.event_bus.emit_async("test.async_event", {"value": 42})
        
        # Verify
        assert len(self.received_events) == 1
        assert self.received_events[0]["value"] == 42
        
    def test_wildcard_subscription(self):
        """Test wildcard event subscription"""
        # Setup
        def handler(data):
            self.received_events.append((data, "wildcard"))
            
        def specific_handler(data):
            self.received_events.append((data, "specific"))
            
        # Subscribe with wildcard
        self.event_bus.subscribe("test.*", handler)
        self.event_bus.subscribe("test.specific", specific_handler)
        
        # Emit events
        self.event_bus.emit("test.specific", {"value": 42})
        self.event_bus.emit("test.other", {"value": 43})
        
        # Verify
        assert len(self.received_events) == 3
        assert self.received_events[0][0]["value"] == 42
        assert self.received_events[0][1] == "specific"
        assert self.received_events[1][0]["value"] == 42
        assert self.received_events[1][1] == "wildcard"
        assert self.received_events[2][0]["value"] == 43
        assert self.received_events[2][1] == "wildcard"
```

### 2.3 Mocking Strategy

VPA will use the `unittest.mock` and `pytest-mock` libraries for mocking dependencies:

```python
# test_settings_manager.py
import pytest
from unittest.mock import mock_open, patch
from core.settings_manager import SettingsManager

class TestSettingsManager:
    def setup_method(self):
        """Setup for each test"""
        # Use a mock file system
        self.mock_settings = {
            "test.setting": "value",
            "test.number": 42,
            "test.boolean": True
        }
        
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    def test_load_settings(self, mock_json_load, mock_file):
        """Test loading settings from file"""
        # Setup
        mock_json_load.return_value = self.mock_settings
        
        # Create settings manager
        manager = SettingsManager("test_settings.json")
        
        # Verify
        assert manager.get("test.setting") == "value"
        assert manager.get("test.number") == 42
        assert manager.get("test.boolean") is True
        assert mock_file.call_count == 1
        
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.load")
    @patch("json.dump")
    def test_save_settings(self, mock_json_dump, mock_json_load, mock_file):
        """Test saving settings to file"""
        # Setup
        mock_json_load.return_value = self.mock_settings
        
        # Create settings manager
        manager = SettingsManager("test_settings.json")
        
        # Change a setting
        manager.set("test.new", "new_value")
        
        # Verify
        assert manager.get("test.new") == "new_value"
        assert mock_json_dump.call_count == 1
        saved_settings = mock_json_dump.call_args[0][0]
        assert saved_settings["test.new"] == "new_value"
        assert saved_settings["test.setting"] == "value"
```

### 2.4 PyQt Testing Approach

For testing PyQt components, VPA will use `pytest-qt`:

```python
# test_chat_bubble.py
import pytest
from PyQt6.QtCore import Qt
from ui.components.chat_bubble import ChatBubble
from models.message import Message
from datetime import datetime

class TestChatBubble:
    def test_chat_bubble_creation(self, qtbot):
        """Test creating a chat bubble"""
        # Create a message
        message = Message(
            id="test-id",
            text="Hello, world!",
            timestamp=datetime.now(),
            is_user=True
        )
        
        # Create widget
        widget = ChatBubble(message)
        qtbot.addWidget(widget)
        
        # Verify widget properties
        assert widget.message.id == "test-id"
        assert widget.is_user is True
        assert widget.objectName() == "chatUserBubble"
        
        # Find message text label
        message_label = widget.findChild(QLabel, "messageText")
        assert message_label is not None
        assert message_label.text() == "Hello, world!"
        
    def test_assistant_bubble_style(self, qtbot):
        """Test assistant bubble styling"""
        # Create a message
        message = Message(
            id="test-id",
            text="I'm an assistant",
            timestamp=datetime.now(),
            is_user=False
        )
        
        # Create widget
        widget = ChatBubble(message)
        qtbot.addWidget(widget)
        
        # Verify widget properties
        assert widget.is_user is False
        assert widget.objectName() == "chatAssistantBubble"
        
    def test_bubble_layout(self, qtbot):
        """Test bubble layout structure"""
        # Create a message
        message = Message(
            id="test-id",
            text="Test message",
            timestamp=datetime.now(),
            is_user=True
        )
        
        # Create widget
        widget = ChatBubble(message)
        qtbot.addWidget(widget)
        
        # Check for avatar
        avatar = widget.findChild(QLabel, "avatarLabel")
        assert avatar is not None
        
        # Check for timestamp
        timestamp = widget.findChild(QLabel, "timestampLabel")
        assert timestamp is not None
        
        # For user messages, avatar should be on right
        main_layout = widget.layout()
        assert main_layout.itemAt(main_layout.count() - 1).widget() == avatar
```

## 3. Integration Testing

### 3.1 Component Integration Tests

Integration tests should verify interactions between components:

```python
# test_llm_integration.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.event_bus import EventBus
from core.settings_manager import SettingsManager
from llm.llm_manager import LLMManager
from llm.ollama_adapter import OllamaAdapter

class TestLLMIntegration:
    def setup_method(self):
        """Setup for each test"""
        self.event_bus = EventBus()
        self.settings_manager = MagicMock(spec=SettingsManager)
        
        # Mock settings
        self.settings_manager.get.side_effect = lambda key, default=None: {
            "llm.provider": "ollama",
            "llm.model": "llama3",
            "llm.streaming": True
        }.get(key, default)
        
        # Create components
        self.ollama_adapter = MagicMock(spec=OllamaAdapter)
        self.llm_manager = LLMManager(self.event_bus, self.settings_manager)
        
        # Inject mock adapter
        self.llm_manager._adapters = {"ollama": self.ollama_adapter}
        
    @pytest.mark.asyncio
    async def test_message_generation_flow(self):
        """Test complete flow from message request to response"""
        # Setup
        self.ollama_adapter.generate.return_value = "This is a test response"
        
        # Mock event listeners
        generation_started = AsyncMock()
        generation_complete = AsyncMock()
        
        # Subscribe to events
        self.event_bus.subscribe_async("llm.generation_started", generation_started)
        self.event_bus.subscribe_async("llm.generation_complete", generation_complete)
        
        # Call generate
        result = await self.llm_manager.generate_response(
            "Test prompt",
            conversation_id="test-conversation"
        )
        
        # Verify adapter was called
        self.ollama_adapter.generate.assert_called_once()
        call_args = self.ollama_adapter.generate.call_args[0]
        assert call_args[0] == "Test prompt"
        
        # Verify events were emitted
        assert generation_started.call_count == 1
        assert generation_started.call_args[0][0]["conversation_id"] == "test-conversation"
        
        assert generation_complete.call_count == 1
        assert generation_complete.call_args[0][0]["conversation_id"] == "test-conversation"
        assert generation_complete.call_args[0][0]["response"] == "This is a test response"
        
        # Verify result
        assert result == "This is a test response"
        
    @pytest.mark.asyncio
    async def test_streaming_response_flow(self):
        """Test streaming response flow"""
        # Setup stream response
        async def mock_stream(*args, **kwargs):
            yield "This "
            yield "is "
            yield "a "
            yield "test "
            yield "response"
            
        self.ollama_adapter.generate_stream = AsyncMock(side_effect=mock_stream)
        
        # Mock event listeners
        token_received = AsyncMock()
        
        # Subscribe to events
        self.event_bus.subscribe_async("llm.token_received", token_received)
        
        # Call generate with streaming
        result = await self.llm_manager.generate_response(
            "Test prompt",
            conversation_id="test-conversation",
            streaming=True
        )
        
        # Verify adapter was called
        self.ollama_adapter.generate_stream.assert_called_once()
        
        # Verify events were emitted
        assert token_received.call_count == 5
        assert token_received.call_args_list[0][0][0]["token"] == "This "
        assert token_received.call_args_list[1][0][0]["token"] == "is "
        assert token_received.call_args_list[2][0][0]["token"] == "a "
        assert token_received.call_args_list[3][0][0]["token"] == "test "
        assert token_received.call_args_list[4][0][0]["token"] == "response"
        
        # Verify result
        assert result == "This is a test response"
```

### 3.2 End-to-End API Tests

Test complete API interactions with external services:

```python
# test_ollama_api.py
import pytest
import aiohttp
from unittest.mock import patch, AsyncMock
from llm.ollama_adapter import OllamaAdapter

class TestOllamaAPI:
    def setup_method(self):
        """Setup for each test"""
        self.adapter = OllamaAdapter()
        self.adapter.server_url = "http://localhost:11434"
        self.adapter.current_model = "llama3"
        
    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    async def test_generate_request(self, mock_post):
        """Test generate request to Ollama API"""
        # Setup mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "response": "This is a test response",
            "model": "llama3",
            "created_at": "2025-08-28T12:00:00.000Z"
        }
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Call generate
        response = await self.adapter.generate("What is the capital of France?")
        
        # Verify request
        mock_post.assert_called_once_with(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": "What is the capital of France?",
                "stream": False
            }
        )
        
        # Verify response
        assert response == "This is a test response"
        
    @pytest.mark.asyncio
    @patch("aiohttp.ClientSession.post")
    async def test_streaming_request(self, mock_post):
        """Test streaming request to Ollama API"""
        # Setup mock response
        async def mock_iter():
            responses = [
                '{"response": "This ", "model": "llama3"}',
                '{"response": "is ", "model": "llama3"}',
                '{"response": "a ", "model": "llama3"}',
                '{"response": "test", "model": "llama3"}',
                '{"done": true}'
            ]
            for r in responses:
                yield r.encode()
                
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content.iter_any = mock_iter
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Collect tokens
        tokens = []
        async for token in self.adapter.generate_stream("What is the capital of France?"):
            tokens.append(token)
            
        # Verify request
        mock_post.assert_called_once_with(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": "What is the capital of France?",
                "stream": True
            }
        )
        
        # Verify tokens
        assert tokens == ["This ", "is ", "a ", "test"]
```

### 3.3 Database Integration Tests

Test database operations with a real database:

```python
# test_conversation_repository.py
import pytest
import os
import sqlite3
import tempfile
from data.conversation_repository import ConversationRepository
from models.conversation import Conversation
from models.message import Message
from datetime import datetime

class TestConversationRepository:
    def setup_method(self):
        """Setup for each test"""
        # Create temp database
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # Create repository
        self.repository = ConversationRepository(self.db_path)
        
        # Initialize database
        self.repository.initialize()
        
    def teardown_method(self):
        """Cleanup after each test"""
        os.close(self.db_fd)
        os.unlink(self.db_path)
        
    def test_create_conversation(self):
        """Test creating a conversation"""
        # Create conversation
        conversation = Conversation(
            id=None,  # Will be assigned by repository
            title="Test Conversation",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            messages=[]
        )
        
        # Save to repository
        conversation_id = self.repository.create_conversation(conversation)
        
        # Verify
        assert conversation_id is not None
        
        # Get from repository
        loaded_conversation = self.repository.get_conversation(conversation_id)
        
        # Verify
        assert loaded_conversation is not None
        assert loaded_conversation.id == conversation_id
        assert loaded_conversation.title == "Test Conversation"
        
    def test_add_message_to_conversation(self):
        """Test adding a message to a conversation"""
        # Create conversation
        conversation = Conversation(
            id=None,
            title="Test Conversation",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            messages=[]
        )
        
        # Save to repository
        conversation_id = self.repository.create_conversation(conversation)
        
        # Create message
        message = Message(
            id=None,
            conversation_id=conversation_id,
            text="Hello, world!",
            timestamp=datetime.now(),
            is_user=True
        )
        
        # Add message
        message_id = self.repository.add_message(conversation_id, message)
        
        # Verify
        assert message_id is not None
        
        # Get conversation with messages
        loaded_conversation = self.repository.get_conversation(conversation_id)
        
        # Verify
        assert loaded_conversation is not None
        assert len(loaded_conversation.messages) == 1
        assert loaded_conversation.messages[0].text == "Hello, world!"
        assert loaded_conversation.messages[0].is_user is True
```

## 4. UI Testing

### 4.1 Manual UI Test Cases

Document manual test cases for key UI functionality:

```markdown
# Manual UI Test Case: Chat Interaction Flow

## Test ID: UI-CHAT-001

### Preconditions:
- VPA application is running
- At least one conversation exists

### Test Steps:

1. Open the application
   - Expected: Application window opens with sidebar and chat view
   - Status: [PASS/FAIL]

2. Select existing conversation from sidebar
   - Expected: Conversation loads with history displayed
   - Status: [PASS/FAIL]

3. Type "Hello" in the chat input field
   - Expected: Text appears in the input field
   - Status: [PASS/FAIL]

4. Click the send button
   - Expected: 
     - Message appears as a user chat bubble
     - Loading indicator displays
     - Assistant response appears after processing
   - Status: [PASS/FAIL]

5. Click the voice input button
   - Expected: Voice recording starts with visual indicator
   - Status: [PASS/FAIL]

6. Speak a short phrase
   - Expected: Voice recording indicator pulses
   - Status: [PASS/FAIL]

7. Click the voice input button again
   - Expected: 
     - Recording stops
     - Transcribed text appears in input field
   - Status: [PASS/FAIL]

8. Press Enter key to send
   - Expected: Message is sent and response received
   - Status: [PASS/FAIL]

### Overall Result: [PASS/FAIL]

### Comments:
[Add any observations, issues, or additional information]

```

### 4.2 Automated UI Tests

Use pytest-qt for automated UI testing:

```python
# test_chat_view.py
import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from ui.chat_view import ChatView
from models.conversation import Conversation
from models.message import Message
from datetime import datetime
from unittest.mock import MagicMock, patch

class TestChatView:
    def setup_method(self):
        """Setup for each test"""
        self.event_bus = MagicMock()
        self.settings_manager = MagicMock()
        
        # Create test conversation
        self.conversation = Conversation(
            id="test-conversation",
            title="Test Conversation",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            messages=[
                Message(
                    id="msg1",
                    conversation_id="test-conversation",
                    text="Hello!",
                    timestamp=datetime.now(),
                    is_user=True
                ),
                Message(
                    id="msg2",
                    conversation_id="test-conversation",
                    text="Hi there! How can I help you?",
                    timestamp=datetime.now(),
                    is_user=False
                )
            ]
        )
        
    def test_chat_view_initialization(self, qtbot):
        """Test chat view initialization"""
        # Create chat view
        view = ChatView(self.event_bus, self.settings_manager)
        qtbot.addWidget(view)
        
        # Verify initial state
        assert view.conversation is None
        assert view.is_processing is False
        
        # Set conversation
        view.set_conversation(self.conversation)
        
        # Verify conversation is set
        assert view.conversation.id == "test-conversation"
        
        # Verify messages are displayed (count chat bubbles)
        chat_area = view.findChild(QScrollArea, "chatScrollArea")
        assert chat_area is not None
        
        content_widget = chat_area.widget()
        assert content_widget is not None
        
        # Count message bubbles (should be 2)
        bubbles = content_widget.findChildren(ChatBubble)
        assert len(bubbles) == 2
        
    def test_send_message(self, qtbot):
        """Test sending a message"""
        # Create chat view
        view = ChatView(self.event_bus, self.settings_manager)
        qtbot.addWidget(view)
        view.set_conversation(self.conversation)
        
        # Find input field and send button
        input_field = view.findChild(QLineEdit, "chatInput")
        send_button = view.findChild(QPushButton, "sendButton")
        
        assert input_field is not None
        assert send_button is not None
        
        # Set text and send
        qtbot.keyClicks(input_field, "Test message")
        qtbot.mouseClick(send_button, Qt.MouseButton.LeftButton)
        
        # Verify event emitted
        self.event_bus.emit_async.assert_called_once()
        event_name, event_data = self.event_bus.emit_async.call_args[0]
        
        assert event_name == "chat.send_message"
        assert event_data["conversation_id"] == "test-conversation"
        assert event_data["message"] == "Test message"
        
        # Verify input field cleared
        assert input_field.text() == ""
        
    @patch("ui.chat_view.ChatView._start_voice_recognition")
    def test_voice_button(self, mock_voice_recognition, qtbot):
        """Test voice input button"""
        # Create chat view
        view = ChatView(self.event_bus, self.settings_manager)
        qtbot.addWidget(view)
        
        # Find voice button
        voice_button = view.findChild(QPushButton, "voiceButton")
        assert voice_button is not None
        
        # Click voice button
        qtbot.mouseClick(voice_button, Qt.MouseButton.LeftButton)
        
        # Verify voice recognition started
        mock_voice_recognition.assert_called_once()
        
        # Simulate voice recognition results
        view._on_voice_recognition_result("Voice test message")
        
        # Find input field and verify text
        input_field = view.findChild(QLineEdit, "chatInput")
        assert input_field.text() == "Voice test message"
```

### 4.3 Accessibility Testing

Test accessibility features with specialized tools:

```python
# test_accessibility.py
import pytest
from PyQt6.QtCore import Qt, QAccessible
from PyQt6.QtWidgets import QApplication
from ui.chat_view import ChatView
from models.conversation import Conversation

class TestAccessibility:
    def setup_method(self):
        """Setup for each test"""
        self.event_bus = MagicMock()
        self.settings_manager = MagicMock()
        
        # Create empty conversation
        self.conversation = Conversation(
            id="test-conversation",
            title="Test Conversation",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            messages=[]
        )
        
    def test_chat_input_accessibility(self, qtbot):
        """Test chat input accessibility"""
        # Create chat view
        view = ChatView(self.event_bus, self.settings_manager)
        qtbot.addWidget(view)
        view.set_conversation(self.conversation)
        
        # Find input field
        input_field = view.findChild(QLineEdit, "chatInput")
        assert input_field is not None
        
        # Get accessibility interface
        interface = QAccessible.queryAccessibleInterface(input_field)
        assert interface is not None
        
        # Check role
        role = interface.role()
        assert role == QAccessible.Role.EditableText
        
        # Check name
        name = interface.text(QAccessible.Text.Name)
        assert "message" in name.lower()
        
        # Check keyboard focus
        qtbot.keyClick(view, Qt.Key.Key_Tab)
        focused_widget = QApplication.focusWidget()
        assert focused_widget == input_field
        
    def test_button_accessibility(self, qtbot):
        """Test button accessibility"""
        # Create chat view
        view = ChatView(self.event_bus, self.settings_manager)
        qtbot.addWidget(view)
        
        # Find send button
        send_button = view.findChild(QPushButton, "sendButton")
        assert send_button is not None
        
        # Get accessibility interface
        interface = QAccessible.queryAccessibleInterface(send_button)
        assert interface is not None
        
        # Check role
        role = interface.role()
        assert role == QAccessible.Role.PushButton
        
        # Check name and description
        name = interface.text(QAccessible.Text.Name)
        assert "send" in name.lower()
```

## 5. Performance Testing

### 5.1 Load Testing Framework

Implement load testing for key operations:

```python
# test_performance.py
import pytest
import time
import asyncio
from llm.llm_manager import LLMManager
from core.event_bus import EventBus
from core.settings_manager import SettingsManager
from unittest.mock import MagicMock

class TestPerformance:
    def setup_method(self):
        """Setup for each test"""
        self.event_bus = EventBus()
        self.settings_manager = MagicMock(spec=SettingsManager)
        
        # Mock LLM adapter
        self.mock_adapter = MagicMock()
        self.mock_adapter.generate.return_value = "Test response"
        
        # Create LLM manager with mock adapter
        self.llm_manager = LLMManager(self.event_bus, self.settings_manager)
        self.llm_manager._adapters = {"test": self.mock_adapter}
        self.llm_manager.current_model = "test"
        
    @pytest.mark.benchmark
    def test_event_bus_performance(self, benchmark):
        """Benchmark event bus performance"""
        # Setup
        received = []
        def handler(data):
            received.append(data)
            
        self.event_bus.subscribe("test.event", handler)
        
        # Run benchmark
        def emit_events():
            for i in range(100):
                self.event_bus.emit("test.event", {"index": i})
                
        benchmark(emit_events)
        
        # Verify all events were received
        assert len(received) == 100
        
    @pytest.mark.asyncio
    @pytest.mark.benchmark
    async def test_llm_response_time(self, benchmark):
        """Benchmark LLM response time"""
        # Configure mock adapter
        async def delayed_generate(*args, **kwargs):
            await asyncio.sleep(0.01)  # Simulate 10ms processing
            return "Test response"
            
        self.mock_adapter.generate = delayed_generate
        
        # Run benchmark
        result = await benchmark(self.llm_manager.generate_response, "Test prompt")
        
        # Verify
        assert result == "Test response"
        
    @pytest.mark.benchmark
    def test_ui_rendering_performance(self, qtbot, benchmark):
        """Benchmark UI rendering performance"""
        # Import here to avoid loading UI for other tests
        from ui.chat_view import ChatView
        from models.conversation import Conversation
        from models.message import Message
        
        # Create chat view
        view = ChatView(self.event_bus, self.settings_manager)
        qtbot.addWidget(view)
        
        # Create test conversation with many messages
        conversation = Conversation(
            id="test-conversation",
            title="Test Conversation",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            messages=[]
        )
        
        # Add 100 messages
        for i in range(100):
            conversation.messages.append(Message(
                id=f"msg{i}",
                conversation_id="test-conversation",
                text=f"Message {i}",
                timestamp=datetime.now(),
                is_user=i % 2 == 0
            ))
            
        # Run benchmark
        benchmark(view.set_conversation, conversation)
        
        # Verify all messages rendered
        chat_area = view.findChild(QScrollArea, "chatScrollArea")
        content_widget = chat_area.widget()
        bubbles = content_widget.findChildren(ChatBubble)
        
        # With virtual scrolling, should see viewport messages
        assert len(bubbles) > 0
```

### 5.2 Memory Usage Testing

Test memory usage patterns:

```python
# test_memory_usage.py
import pytest
import psutil
import gc
import os
from unittest.mock import patch

class TestMemoryUsage:
    def setup_method(self):
        """Setup for each test"""
        # Force garbage collection before test
        gc.collect()
        self.process = psutil.Process(os.getpid())
        self.initial_memory = self.process.memory_info().rss
        
    def teardown_method(self):
        """Cleanup after test"""
        gc.collect()
        
    def test_llm_manager_memory(self):
        """Test memory usage of LLM manager"""
        from core.event_bus import EventBus
        from core.settings_manager import SettingsManager
        from llm.llm_manager import LLMManager
        
        # Create manager
        event_bus = EventBus()
        settings_manager = SettingsManager(":memory:")
        
        # Measure memory before
        before_memory = self.process.memory_info().rss
        
        # Create LLM manager
        llm_manager = LLMManager(event_bus, settings_manager)
        
        # Measure memory after
        after_memory = self.process.memory_info().rss
        memory_increase = after_memory - before_memory
        
        # Verify reasonable memory usage (less than 5MB)
        assert memory_increase < 5 * 1024 * 1024  # 5 MB
        
    @pytest.mark.skipif(not hasattr(psutil.Process, 'memory_full_info'),
                       reason="memory_full_info not available")
    def test_conversation_repository_memory_scaling(self):
        """Test memory scaling with conversation repository"""
        from data.conversation_repository import ConversationRepository
        from models.conversation import Conversation
        from models.message import Message
        
        # Create in-memory repository
        repository = ConversationRepository(":memory:")
        repository.initialize()
        
        # Measure memory before
        before_memory = self.process.memory_info().rss
        
        # Create conversations with messages
        message_counts = [10, 100, 1000]
        memory_usage = []
        
        for count in message_counts:
            # Create conversation
            conversation = Conversation(
                id=None,
                title=f"Test Conversation {count}",
                created_at=datetime.now(),
                updated_at=datetime.now(),
                messages=[]
            )
            
            # Save to repository
            conversation_id = repository.create_conversation(conversation)
            
            # Add messages
            for i in range(count):
                message = Message(
                    id=None,
                    conversation_id=conversation_id,
                    text=f"Message {i} with some content to simulate real message size",
                    timestamp=datetime.now(),
                    is_user=i % 2 == 0
                )
                repository.add_message(conversation_id, message)
                
            # Force garbage collection
            gc.collect()
            
            # Measure memory
            current_memory = self.process.memory_info().rss
            memory_usage.append(current_memory - before_memory)
            
            # Clear conversation from memory (keep in database)
            conversation = None
            gc.collect()
            
        # Verify sublinear scaling (memory should not scale linearly with message count)
        # This means memory_usage[2] / message_counts[2] < memory_usage[0] / message_counts[0]
        mem_per_msg_small = memory_usage[0] / message_counts[0]
        mem_per_msg_large = memory_usage[2] / message_counts[2]
        
        assert mem_per_msg_large < mem_per_msg_small
```

## 6. Security Testing

### 6.1 Credential Storage Tests

Test secure credential storage:

```python
# test_security.py
import pytest
import os
from security.credential_manager import CredentialManager
from unittest.mock import patch, MagicMock

class TestCredentialManager:
    def setup_method(self):
        """Setup for each test"""
        # Use mock Windows API
        self.patcher = patch('security.credential_manager.win32cred')
        self.mock_win32cred = self.patcher.start()
        
    def teardown_method(self):
        """Cleanup after test"""
        self.patcher.stop()
        
    def test_store_credential(self):
        """Test storing credentials securely"""
        # Setup mock
        self.mock_win32cred.CredWrite = MagicMock()
        
        # Create manager
        manager = CredentialManager()
        
        # Store credential
        result = manager.store_credential("test_service", "test_username", "test_password")
        
        # Verify
        assert result is True
        self.mock_win32cred.CredWrite.assert_called_once()
        
        # Check credential structure
        cred = self.mock_win32cred.CredWrite.call_args[0][0]
        assert cred["Type"] == self.mock_win32cred.CRED_TYPE_GENERIC
        assert cred["TargetName"] == "VPA:test_service"
        assert cred["UserName"] == "test_username"
        assert cred["CredentialBlob"] == "test_password"
        
    def test_get_credential(self):
        """Test retrieving credentials"""
        # Setup mock credential
        mock_credential = {
            "UserName": "test_username",
            "CredentialBlob": "test_password"
        }
        
        # Setup mock read function
        self.mock_win32cred.CredRead = MagicMock(return_value=mock_credential)
        
        # Create manager
        manager = CredentialManager()
        
        # Get credential
        username, password = manager.get_credential("test_service")
        
        # Verify
        assert username == "test_username"
        assert password == "test_password"
        self.mock_win32cred.CredRead.assert_called_once_with(
            "VPA:test_service",
            self.mock_win32cred.CRED_TYPE_GENERIC,
            0
        )
        
    def test_get_nonexistent_credential(self):
        """Test retrieving non-existent credentials"""
        # Setup mock to raise exception
        self.mock_win32cred.CredRead = MagicMock(side_effect=Exception("Not found"))
        
        # Create manager
        manager = CredentialManager()
        
        # Get credential
        result = manager.get_credential("nonexistent_service")
        
        # Verify
        assert result is None
```

### 6.2 Encryption Tests

Test data encryption functionality:

```python
# test_encryption.py
import pytest
from security.encryption import EncryptionManager
from unittest.mock import patch, MagicMock

class TestEncryptionManager:
    def setup_method(self):
        """Setup for each test"""
        self.patcher = patch('security.encryption.win32crypt')
        self.mock_win32crypt = self.patcher.start()
        
    def teardown_method(self):
        """Cleanup after test"""
        self.patcher.stop()
        
    def test_encrypt_data(self):
        """Test encrypting data"""
        # Setup mock encryption
        self.mock_win32crypt.CryptProtectData = MagicMock(return_value=b'encrypted_data')
        
        # Create manager
        manager = EncryptionManager()
        
        # Encrypt data
        plaintext = "sensitive data"
        encrypted = manager.encrypt_data(plaintext)
        
        # Verify
        assert encrypted == b'encrypted_data'
        self.mock_win32crypt.CryptProtectData.assert_called_once()
        
        # Check data structure
        call_args = self.mock_win32crypt.CryptProtectData.call_args[0]
        assert call_args[0] == plaintext.encode('utf-8')
        
    def test_decrypt_data(self):
        """Test decrypting data"""
        # Setup mock decryption
        self.mock_win32crypt.CryptUnprotectData = MagicMock(return_value=(None, b'decrypted_data'))
        
        # Create manager
        manager = EncryptionManager()
        
        # Decrypt data
        encrypted = b'encrypted_data'
        decrypted = manager.decrypt_data(encrypted)
        
        # Verify
        assert decrypted == "decrypted_data"
        self.mock_win32crypt.CryptUnprotectData.assert_called_once_with(encrypted, None, None, None, None, 0)
        
    def test_roundtrip_encryption(self):
        """Test roundtrip encryption/decryption"""
        # Setup mocks
        def mock_encrypt(data, *args, **kwargs):
            return b'encrypted:' + data
            
        def mock_decrypt(data, *args, **kwargs):
            return (None, data[10:])  # Skip 'encrypted:' prefix
            
        self.mock_win32crypt.CryptProtectData = MagicMock(side_effect=mock_encrypt)
        self.mock_win32crypt.CryptUnprotectData = MagicMock(side_effect=mock_decrypt)
        
        # Create manager
        manager = EncryptionManager()
        
        # Test roundtrip
        original = "test secret data"
        encrypted = manager.encrypt_data(original)
        decrypted = manager.decrypt_data(encrypted)
        
        # Verify
        assert decrypted == original
```

## 7. Accessibility Testing

### 7.1 Keyboard Navigation Tests

Test keyboard navigation throughout the application:

```python
# test_keyboard_navigation.py
import pytest
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow
from unittest.mock import MagicMock

class TestKeyboardNavigation:
    def setup_method(self):
        """Setup for each test"""
        self.event_bus = MagicMock()
        self.settings_manager = MagicMock()
        
    def test_tab_navigation(self, qtbot):
        """Test tab navigation through UI elements"""
        # Create main window
        window = MainWindow(self.event_bus, self.settings_manager)
        qtbot.addWidget(window)
        
        # Show window
        window.show()
        
        # Track focus order
        focus_widgets = []
        
        # Tab through elements
        for _ in range(10):  # Tab 10 times through UI
            qtbot.keyClick(window, Qt.Key.Key_Tab)
            focused = window.focusWidget()
            if focused and focused not in focus_widgets:
                focus_widgets.append(focused)
                
        # Verify key UI elements are in focus chain
        sidebar_found = any(w.objectName() == "sidebar" or "sidebar" in str(w.__class__) for w in focus_widgets)
        chat_input_found = any(w.objectName() == "chatInput" for w in focus_widgets)
        send_button_found = any(w.objectName() == "sendButton" for w in focus_widgets)
        
        assert sidebar_found, "Sidebar not in tab navigation"
        assert chat_input_found, "Chat input not in tab navigation"
        assert send_button_found, "Send button not in tab navigation"
        
    def test_keyboard_shortcuts(self, qtbot):
        """Test keyboard shortcuts"""
        # Create main window
        window = MainWindow(self.event_bus, self.settings_manager)
        qtbot.addWidget(window)
        
        # Show window
        window.show()
        
        # Test Ctrl+N for new conversation
        with qtbot.waitSignal(self.event_bus.emit_async, timeout=1000):
            qtbot.keyClick(window, Qt.Key.Key_N, Qt.KeyboardModifier.ControlModifier)
            
        # Verify event emitted
        assert self.event_bus.emit_async.call_args[0][0] == "conversation.create"
        
        # Test Escape to clear input
        chat_view = window.findChild(QWidget, "chatView")
        chat_input = chat_view.findChild(QLineEdit, "chatInput")
        
        # Set text and press Escape
        chat_input.setText("Test text")
        qtbot.keyClick(chat_input, Qt.Key.Key_Escape)
        
        # Verify text cleared
        assert chat_input.text() == ""
```

### 7.2 Screen Reader Tests

Test screen reader compatibility:

```python
# test_screen_reader.py
import pytest
from PyQt6.QtCore import Qt, QAccessible
from PyQt6.QtWidgets import QAccessibleWidget, QApplication
from ui.main_window import MainWindow
from unittest.mock import MagicMock

class TestScreenReaderCompatibility:
    def setup_method(self):
        """Setup for each test"""
        self.event_bus = MagicMock()
        self.settings_manager = MagicMock()
        
    def test_accessibility_properties(self, qtbot):
        """Test accessibility properties on UI elements"""
        # Create main window
        window = MainWindow(self.event_bus, self.settings_manager)
        qtbot.addWidget(window)
        
        # Show window
        window.show()
        
        # Check main window accessibility
        window_acc = QAccessible.queryAccessibleInterface(window)
        assert window_acc is not None
        assert "VPA" in window_acc.text(QAccessible.Text.Name)
        
        # Check chat view
        chat_view = window.findChild(QWidget, "chatView")
        chat_view_acc = QAccessible.queryAccessibleInterface(chat_view)
        assert chat_view_acc is not None
        
        # Check chat input
        chat_input = chat_view.findChild(QLineEdit, "chatInput")
        chat_input_acc = QAccessible.queryAccessibleInterface(chat_input)
        assert chat_input_acc is not None
        assert chat_input_acc.role() == QAccessible.Role.EditableText
        
        # Check send button has accessible name
        send_button = chat_view.findChild(QPushButton, "sendButton")
        send_button_acc = QAccessible.queryAccessibleInterface(send_button)
        assert send_button_acc is not None
        assert "send" in send_button_acc.text(QAccessible.Text.Name).lower()
        
    def test_focus_events(self, qtbot):
        """Test focus change events for screen readers"""
        # Create main window
        window = MainWindow(self.event_bus, self.settings_manager)
        qtbot.addWidget(window)
        
        # Show window
        window.show()
        
        # Setup event spy for accessibility events
        events = []
        
        def event_spy(event):
            if event.type() == QAccessible.Event.Focus:
                events.append(event)
                
        # Install event spy
        QAccessible.installEventFilter(event_spy)
        
        # Change focus
        chat_view = window.findChild(QWidget, "chatView")
        chat_input = chat_view.findChild(QLineEdit, "chatInput")
        send_button = chat_view.findChild(QPushButton, "sendButton")
        
        # Focus input
        chat_input.setFocus()
        qtbot.wait(100)
        
        # Focus button
        send_button.setFocus()
        qtbot.wait(100)
        
        # Remove event filter
        QAccessible.removeEventFilter(event_spy)
        
        # Verify focus events
        assert len(events) >= 2
```

## 8. Test Automation

### 8.1 pytest Configuration

Configure pytest for automated testing:

```python
# conftest.py
import pytest
import sys
from PyQt6.QtWidgets import QApplication
import os
import tempfile

# Create Qt application for UI tests
@pytest.fixture(scope="session")
def qapp():
    """Create QApplication once per session"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app
    
# Create temporary directory for test files
@pytest.fixture
def temp_dir():
    """Create temporary directory for test files"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir
        
# Create mock settings manager
@pytest.fixture
def settings_manager():
    """Create mock settings manager"""
    from unittest.mock import MagicMock
    
    manager = MagicMock()
    # Set common settings
    manager.get.side_effect = lambda key, default=None: {
        "ui.theme": "light",
        "llm.provider": "mock",
        "llm.model": "mock-model",
        "voice_input.language": "en-US"
    }.get(key, default)
    
    return manager
    
# Create real event bus
@pytest.fixture
def event_bus():
    """Create real event bus"""
    from core.event_bus import EventBus
    return EventBus()
    
# Create in-memory database
@pytest.fixture
def db_path():
    """Create in-memory database path"""
    return ":memory:"
    
# Configure pytest-qt
def pytest_configure(config):
    """Configure pytest-qt"""
    # Set HighDPI scaling
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    # Disable animations for tests
    os.environ["QT_QUICK_NO_PLATFORM_ANIMATIONS"] = "1"
```

### 8.2 Testing Script

Create a test script to run all tests:

```powershell
# run_tests.ps1
param (
    [switch]$unit,
    [switch]$integration,
    [switch]$ui,
    [switch]$performance,
    [switch]$coverage,
    [switch]$verbose,
    [switch]$all
)

# Set default if no flags provided
if (-not ($unit -or $integration -or $ui -or $performance -or $all)) {
    $unit = $true
}

# If all is specified, run everything
if ($all) {
    $unit = $true
    $integration = $true
    $ui = $true
    $performance = $true
    $coverage = $true
}

# Base command
$command = "python -m pytest"

# Add verbose if specified
if ($verbose) {
    $command += " -v"
}

# Add test types
if ($unit) {
    $command += " tests/unit/"
}

if ($integration) {
    $command += " tests/integration/"
}

if ($ui) {
    $command += " tests/ui/"
}

if ($performance) {
    $command += " tests/performance/"
}

# Add coverage if specified
if ($coverage) {
    $command += " --cov=vpa --cov-report=xml:coverage.xml --cov-report=html:coverage_html"
}

# Execute command
Write-Host "Running: $command"
Invoke-Expression $command

# Open coverage report if generated
if ($coverage) {
    if (Test-Path "./coverage_html/index.html") {
        Start-Process "./coverage_html/index.html"
    }
}
```

## 9. Continuous Integration

### 9.1 GitHub Actions Workflow

Configure GitHub Actions for automated testing:

```yaml
# .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [ main, development ]
  pull_request:
    branches: [ main, development ]

jobs:
  test:
    runs-on: windows-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: [3.9, "3.10"]

    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pytest-cov pytest-qt pytest-xvfb pytest-asyncio
        pip install -r requirements.txt
        
    - name: Run unit tests
      run: pytest tests/unit/ -v
      
    - name: Run integration tests
      run: pytest tests/integration/ -v
      
    - name: Run UI tests
      run: pytest tests/ui/ -v
      
    - name: Generate coverage report
      run: pytest --cov=vpa --cov-report=xml
      
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
        fail_ci_if_error: false
```

### 9.2 Test Report Format

Define test report format for CI:

```python
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

junit_family = xunit2
addopts = --junitxml=test-results.xml

markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    benchmark: performance benchmark tests
    gui: tests that require a GUI
    integration: integration tests
```

## Conclusion

This Testing Requirements document provides a comprehensive plan for ensuring the quality and reliability of the VPA application. By implementing a multi-layered testing approach covering unit, integration, UI, performance, security, and accessibility testing, VPA ensures a robust and user-friendly experience.

The implementation includes test automation infrastructure, continuous integration setup, and detailed test cases for key application components. This thorough testing approach allows VPA to deliver a high-quality product that meets user expectations.

---

*Document created on August 28, 2025*  
*Version: 1.0*

````
