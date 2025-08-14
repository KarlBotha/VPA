"""
Unit tests for VPA Core Events Module
Tests the event bus system for pub/sub messaging.
"""

import pytest
import logging
from unittest.mock import MagicMock, patch, call
from collections import defaultdict

from vpa.core.events import EventBus


class TestEventBus:
    """Test cases for EventBus class"""
    
    def test_init(self):
        """Test EventBus initialization"""
        bus = EventBus()
        
        assert bus._listeners == defaultdict(list)
        assert bus._initialized is False
        assert bus.logger is not None
        assert bus.logger.name == "vpa.core.events"
    
    def test_initialize_once(self):
        """Test EventBus initialize method"""
        bus = EventBus()
        
        with patch.object(bus, 'logger') as mock_logger:
            bus.initialize()
            
            assert bus._initialized is True
            mock_logger.info.assert_called_once_with("Event bus initialized")
    
    def test_initialize_multiple_times(self):
        """Test EventBus initialize called multiple times only initializes once"""
        bus = EventBus()
        
        with patch.object(bus, 'logger') as mock_logger:
            bus.initialize()
            bus.initialize()  # Second call
            bus.initialize()  # Third call
            
            assert bus._initialized is True
            # Should only log once
            mock_logger.info.assert_called_once_with("Event bus initialized")
    
    def test_subscribe_single_listener(self):
        """Test subscribing a single listener to an event"""
        bus = EventBus()
        callback = MagicMock()
        
        with patch.object(bus, 'logger') as mock_logger:
            bus.subscribe("test.event", callback)
            
            assert callback in bus._listeners["test.event"]
            assert len(bus._listeners["test.event"]) == 1
            mock_logger.debug.assert_called_once_with("Subscribed to event: test.event")
    
    def test_subscribe_multiple_listeners_same_event(self):
        """Test subscribing multiple listeners to the same event"""
        bus = EventBus()
        callback1 = MagicMock()
        callback2 = MagicMock()
        callback3 = MagicMock()
        
        bus.subscribe("test.event", callback1)
        bus.subscribe("test.event", callback2)
        bus.subscribe("test.event", callback3)
        
        assert len(bus._listeners["test.event"]) == 3
        assert callback1 in bus._listeners["test.event"]
        assert callback2 in bus._listeners["test.event"]
        assert callback3 in bus._listeners["test.event"]
    
    def test_subscribe_multiple_events(self):
        """Test subscribing to multiple different events"""
        bus = EventBus()
        callback1 = MagicMock()
        callback2 = MagicMock()
        
        bus.subscribe("event.one", callback1)
        bus.subscribe("event.two", callback2)
        
        assert callback1 in bus._listeners["event.one"]
        assert callback2 in bus._listeners["event.two"]
        assert len(bus._listeners["event.one"]) == 1
        assert len(bus._listeners["event.two"]) == 1
    
    def test_unsubscribe_existing_listener(self):
        """Test unsubscribing an existing listener"""
        bus = EventBus()
        callback = MagicMock()
        
        # Subscribe first
        bus.subscribe("test.event", callback)
        assert callback in bus._listeners["test.event"]
        
        # Then unsubscribe
        with patch.object(bus, 'logger') as mock_logger:
            bus.unsubscribe("test.event", callback)
            
            assert callback not in bus._listeners["test.event"]
            assert len(bus._listeners["test.event"]) == 0
            mock_logger.debug.assert_called_once_with("Unsubscribed from event: test.event")
    
    def test_unsubscribe_nonexistent_listener(self):
        """Test unsubscribing a listener that doesn't exist"""
        bus = EventBus()
        callback1 = MagicMock()
        callback2 = MagicMock()
        
        # Subscribe only callback1
        bus.subscribe("test.event", callback1)
        
        # Try to unsubscribe callback2 (not subscribed)
        with patch.object(bus, 'logger') as mock_logger:
            bus.unsubscribe("test.event", callback2)
            
            # callback1 should still be there
            assert callback1 in bus._listeners["test.event"]
            mock_logger.warning.assert_called_once_with("Callback not found for event: test.event")
    
    def test_unsubscribe_nonexistent_event(self):
        """Test unsubscribing from an event that has no listeners"""
        bus = EventBus()
        callback = MagicMock()
        
        # Try to unsubscribe from event with no listeners
        with patch.object(bus, 'logger') as mock_logger:
            bus.unsubscribe("nonexistent.event", callback)
            
            # Should not raise error, but won't log anything for nonexistent event
            assert len(mock_logger.debug.call_args_list) == 0
            assert len(mock_logger.warning.call_args_list) == 0
    
    def test_emit_event_with_data_initialized(self):
        """Test emitting event with data when bus is initialized"""
        bus = EventBus()
        bus.initialize()
        
        callback1 = MagicMock()
        callback2 = MagicMock()
        
        bus.subscribe("test.event", callback1)
        bus.subscribe("test.event", callback2)
        
        test_data = {"message": "hello", "value": 42}
        
        with patch.object(bus, 'logger') as mock_logger:
            bus.emit("test.event", test_data)
            
            callback1.assert_called_once_with(test_data)
            callback2.assert_called_once_with(test_data)
            mock_logger.debug.assert_called_once_with("Emitting event: test.event")
    
    def test_emit_event_without_data_initialized(self):
        """Test emitting event without data when bus is initialized"""
        bus = EventBus()
        bus.initialize()
        
        callback1 = MagicMock()
        callback2 = MagicMock()
        
        bus.subscribe("test.event", callback1)
        bus.subscribe("test.event", callback2)
        
        with patch.object(bus, 'logger') as mock_logger:
            bus.emit("test.event")
            
            callback1.assert_called_once_with()
            callback2.assert_called_once_with()
            mock_logger.debug.assert_called_once_with("Emitting event: test.event")
    
    def test_emit_event_not_initialized(self):
        """Test emitting event when bus is not initialized"""
        bus = EventBus()
        # Don't call initialize()
        
        callback = MagicMock()
        bus.subscribe("test.event", callback)
        
        with patch.object(bus, 'logger') as mock_logger:
            bus.emit("test.event", "test_data")
            
            # Callback should not be called
            callback.assert_not_called()
            mock_logger.warning.assert_called_once_with("Event bus not initialized, ignoring event")
    
    def test_emit_event_no_listeners(self):
        """Test emitting event with no listeners"""
        bus = EventBus()
        bus.initialize()
        
        with patch.object(bus, 'logger') as mock_logger:
            bus.emit("nonexistent.event", "test_data")
            
            # Should not raise error
            mock_logger.debug.assert_called_once_with("Emitting event: nonexistent.event")
    
    def test_emit_event_callback_exception(self):
        """Test emitting event when callback raises exception"""
        bus = EventBus()
        bus.initialize()
        
        callback1 = MagicMock()
        callback2 = MagicMock(side_effect=ValueError("Test error"))
        callback3 = MagicMock()
        
        bus.subscribe("test.event", callback1)
        bus.subscribe("test.event", callback2)  # This will raise exception
        bus.subscribe("test.event", callback3)
        
        test_data = {"test": "data"}
        
        with patch.object(bus, 'logger') as mock_logger:
            bus.emit("test.event", test_data)
            
            # All callbacks should be attempted
            callback1.assert_called_once_with(test_data)
            callback2.assert_called_once_with(test_data)
            callback3.assert_called_once_with(test_data)
            
            # Error should be logged
            mock_logger.error.assert_called_once_with("Error in event callback for test.event: Test error")
    
    def test_emit_event_with_none_data(self):
        """Test emitting event with explicit None data"""
        bus = EventBus()
        bus.initialize()
        
        callback = MagicMock()
        bus.subscribe("test.event", callback)
        
        bus.emit("test.event", None)
        
        # Should call callback without arguments when data is None
        callback.assert_called_once_with()
    
    def test_clear_listeners_specific_event(self):
        """Test clearing listeners for a specific event"""
        bus = EventBus()
        
        callback1 = MagicMock()
        callback2 = MagicMock()
        callback3 = MagicMock()
        
        bus.subscribe("event.one", callback1)
        bus.subscribe("event.one", callback2)
        bus.subscribe("event.two", callback3)
        
        with patch.object(bus, 'logger') as mock_logger:
            bus.clear_listeners("event.one")
            
            assert len(bus._listeners["event.one"]) == 0
            assert len(bus._listeners["event.two"]) == 1
            assert callback3 in bus._listeners["event.two"]
            mock_logger.debug.assert_called_once_with("Cleared listeners for event: event.one")
    
    def test_clear_listeners_all_events(self):
        """Test clearing all listeners"""
        bus = EventBus()
        
        callback1 = MagicMock()
        callback2 = MagicMock()
        callback3 = MagicMock()
        
        bus.subscribe("event.one", callback1)
        bus.subscribe("event.one", callback2)
        bus.subscribe("event.two", callback3)
        
        with patch.object(bus, 'logger') as mock_logger:
            bus.clear_listeners()
            
            assert len(bus._listeners) == 0
            mock_logger.debug.assert_called_once_with("Cleared all event listeners")
    
    def test_clear_listeners_nonexistent_event(self):
        """Test clearing listeners for nonexistent event"""
        bus = EventBus()
        
        callback = MagicMock()
        bus.subscribe("existing.event", callback)
        
        with patch.object(bus, 'logger') as mock_logger:
            bus.clear_listeners("nonexistent.event")
            
            # Existing event should still have its listener
            assert len(bus._listeners["existing.event"]) == 1
            assert callback in bus._listeners["existing.event"]
            mock_logger.debug.assert_called_once_with("Cleared listeners for event: nonexistent.event")
    
    def test_get_listener_count_existing_event(self):
        """Test getting listener count for existing event"""
        bus = EventBus()
        
        callback1 = MagicMock()
        callback2 = MagicMock()
        callback3 = MagicMock()
        
        bus.subscribe("test.event", callback1)
        bus.subscribe("test.event", callback2)
        bus.subscribe("other.event", callback3)
        
        assert bus.get_listener_count("test.event") == 2
        assert bus.get_listener_count("other.event") == 1
    
    def test_get_listener_count_nonexistent_event(self):
        """Test getting listener count for nonexistent event"""
        bus = EventBus()
        
        assert bus.get_listener_count("nonexistent.event") == 0
    
    def test_get_listener_count_after_unsubscribe(self):
        """Test getting listener count after unsubscribing"""
        bus = EventBus()
        
        callback1 = MagicMock()
        callback2 = MagicMock()
        
        bus.subscribe("test.event", callback1)
        bus.subscribe("test.event", callback2)
        
        assert bus.get_listener_count("test.event") == 2
        
        bus.unsubscribe("test.event", callback1)
        
        assert bus.get_listener_count("test.event") == 1
    
    def test_complex_workflow(self):
        """Test complex workflow with multiple operations"""
        bus = EventBus()
        
        # Initialize
        bus.initialize()
        
        # Setup callbacks
        results = []
        
        def callback1(data=None):
            results.append(f"callback1: {data}")
        
        def callback2(data=None):
            results.append(f"callback2: {data}")
        
        def callback3(data=None):
            if data == "error":
                raise ValueError("Test error")
            results.append(f"callback3: {data}")
        
        # Subscribe to events
        bus.subscribe("app.start", callback1)
        bus.subscribe("app.start", callback2)
        bus.subscribe("app.data", callback1)
        bus.subscribe("app.data", callback3)
        
        # Verify listener counts
        assert bus.get_listener_count("app.start") == 2
        assert bus.get_listener_count("app.data") == 2
        assert bus.get_listener_count("app.stop") == 0
        
        # Emit events
        bus.emit("app.start")
        bus.emit("app.data", "test_data")
        bus.emit("app.data", "error")  # This will cause callback3 to fail
        
        # Verify results
        expected_results = [
            "callback1: None",
            "callback2: None", 
            "callback1: test_data",
            "callback3: test_data",
            "callback1: error"
        ]
        assert results == expected_results
        
        # Unsubscribe and test
        bus.unsubscribe("app.start", callback1)
        results.clear()
        
        bus.emit("app.start")
        assert results == ["callback2: None"]
        
        # Clear all listeners and test
        bus.clear_listeners()
        results.clear()
        
        bus.emit("app.start")
        bus.emit("app.data", "test")
        assert results == []  # No callbacks should be called
    
    def test_event_type_variations(self):
        """Test various event type naming conventions"""
        bus = EventBus()
        bus.initialize()
        
        callback = MagicMock()
        
        # Test different event naming patterns
        event_types = [
            "simple",
            "app.start",
            "audio.voice.changed",
            "plugin.audio.engine.initialized",
            "user_input_received",
            "system-shutdown-initiated"
        ]
        
        for event_type in event_types:
            bus.subscribe(event_type, callback)
            bus.emit(event_type, f"data_for_{event_type}")
        
        # Should have been called once for each event type
        assert callback.call_count == len(event_types)
    
    def test_data_type_variations(self):
        """Test emitting events with various data types"""
        bus = EventBus()
        bus.initialize()
        
        received_data = []
        
        def callback(data=None):
            received_data.append(data)
        
        bus.subscribe("test.event", callback)
        
        # Test different data types
        test_data = [
            "string",
            42,
            3.14,
            True,
            False,
            ["list", "data"],
            {"dict": "data", "number": 123},
            None
        ]
        
        for data in test_data:
            bus.emit("test.event", data)
        
        # All data should be received as-is, including None
        assert len(received_data) == len(test_data)
        assert received_data == test_data


if __name__ == '__main__':
    pytest.main([__file__])
