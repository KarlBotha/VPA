"""
Test Suite for VPA Core Architecture
Unit tests for events, plugins, app, and audio systems.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch

# Add src to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from vpa.core.events import EventBus, Event, PerformanceMonitor
from vpa.core.plugins import PluginManager, Plugin, PluginMetadata
from vpa.core.app import VPAApplication, StartupPhase
from audio.voice_system import AudioSystem, VoiceProfile, VoiceQuality


class TestPerformanceMonitor:
    """Test PerformanceMonitor functionality."""
    
    def test_memory_monitoring(self):
        """Test memory usage monitoring."""
        memory_info = PerformanceMonitor.monitor_memory_usage()
        
        assert isinstance(memory_info, dict)
        assert "memory_mb" in memory_info
        assert "memory_percent" in memory_info
        assert "cpu_percent" in memory_info
        assert memory_info["memory_mb"] > 0
    
    def test_execution_time_tracking(self):
        """Test execution time tracking decorator."""
        
        @PerformanceMonitor.track_execution_time("test_function")
        def slow_function():
            time.sleep(0.01)  # 10ms
            return "result"
        
        result = slow_function()
        assert result == "result"


class TestEventBus:
    """Test EventBus functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.event_bus = EventBus()
    
    def teardown_method(self):
        """Cleanup after each test."""
        self.event_bus.cleanup()
    
    def test_event_subscription(self):
        """Test event subscription and unsubscription."""
        callback = Mock()
        
        self.event_bus.subscribe("test_event", callback)
        assert "test_event" in self.event_bus._callbacks
        
        self.event_bus.unsubscribe("test_event", callback)
        assert "test_event" not in self.event_bus._callbacks
    
    @pytest.mark.asyncio
    async def test_event_dispatch(self):
        """Test event dispatching."""
        callback = Mock()
        self.event_bus.subscribe("test_event", callback)
        
        event = Event("test_event", {"data": "test"}, time.time())
        await self.event_bus.dispatch(event)
        
        # Give some time for async execution
        await asyncio.sleep(0.1)
        
        callback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_async_event_handling(self):
        """Test async event handling."""
        async_callback = Mock()
        async_callback.return_value = asyncio.Future()
        async_callback.return_value.set_result(None)
        
        self.event_bus.subscribe("async_test", async_callback, async_callback=True)
        
        await self.event_bus.emit_async("async_test", {"data": "async_test"})
    
    def test_metrics(self):
        """Test performance metrics."""
        metrics = self.event_bus.get_metrics()
        
        assert isinstance(metrics, dict)
        assert "events_dispatched" in metrics
        assert "total_dispatch_time" in metrics
        assert "memory_usage_mb" in metrics


class MockPlugin(Plugin):
    """Mock plugin for testing."""
    
    def __init__(self):
        self.initialized = False
        self.cleaned_up = False
    
    @property
    def name(self):
        return "test_plugin"
    
    @property
    def version(self):
        return "1.0.0"
    
    @property
    def description(self):
        return "Test plugin"
    
    def can_handle(self, user_input, context):
        return "test" in user_input.lower()
    
    async def process(self, user_input, context):
        return {"response": "Test response"}
    
    def initialize(self):
        self.initialized = True
    
    def cleanup(self):
        self.cleaned_up = True


class TestPluginManager:
    """Test PluginManager functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.plugin_manager = PluginManager()
    
    def teardown_method(self):
        """Cleanup after each test."""
        self.plugin_manager.cleanup_all_plugins()
    
    def test_plugin_metadata_creation(self):
        """Test plugin metadata creation."""
        metadata = PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
            dependencies=[],
            file_path="/test/path.py"
        )
        
        assert metadata.name == "test_plugin"
        assert metadata.version == "1.0.0"
        assert metadata.enabled == True
    
    def test_plugin_loading(self):
        """Test plugin loading functionality."""
        # Mock a plugin
        mock_plugin = MockPlugin()
        
        # Simulate adding to manager
        self.plugin_manager.plugins["test_plugin"] = mock_plugin
        
        loaded_plugin = self.plugin_manager.get_plugin("test_plugin")
        assert loaded_plugin is not None
        assert loaded_plugin.name == "test_plugin"
    
    @pytest.mark.asyncio
    async def test_find_handlers(self):
        """Test finding plugin handlers."""
        mock_plugin = MockPlugin()
        mock_plugin.initialize()
        
        self.plugin_manager.plugins["test_plugin"] = mock_plugin
        
        handlers = await self.plugin_manager.find_handlers("test input", {})
        assert len(handlers) == 1
        assert handlers[0].name == "test_plugin"
    
    def test_metrics(self):
        """Test plugin manager metrics."""
        metrics = self.plugin_manager.get_metrics()
        
        assert isinstance(metrics, dict)
        assert "plugins_discovered" in metrics
        assert "plugins_loaded" in metrics
        assert "memory_usage_mb" in metrics


class TestVPAApplication:
    """Test VPAApplication functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.app = VPAApplication()
    
    @pytest.mark.asyncio
    async def test_application_startup(self):
        """Test application startup sequence."""
        success = await self.app.startup()
        
        assert success == True
        assert self.app.state.startup_phase == StartupPhase.READY
        assert self.app.state.startup_time > 0
        assert self.app.state.startup_time < 10.0  # Performance target
        
        await self.app.shutdown()
    
    def test_status_reporting(self):
        """Test application status reporting."""
        status = self.app.get_status()
        
        assert isinstance(status, dict)
        assert "startup_phase" in status
        assert "memory_usage_mb" in status
        assert "performance_targets" in status
    
    def test_shutdown_callback(self):
        """Test shutdown callback functionality."""
        callback_called = False
        
        def shutdown_callback():
            nonlocal callback_called
            callback_called = True
        
        self.app.add_shutdown_callback(shutdown_callback)
        
        # This will be tested in integration


class TestAudioSystem:
    """Test AudioSystem functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.audio_system = AudioSystem()
    
    def test_voice_catalog_initialization(self):
        """Test 13-voice catalog initialization."""
        assert len(self.audio_system.voice_profiles) == 13
        
        # Check specific voices from LOGBOOK
        assert "voice_01" in self.audio_system.voice_profiles
        assert self.audio_system.voice_profiles["voice_01"].name == "Zira"
        assert "voice_13" in self.audio_system.voice_profiles
        assert self.audio_system.voice_profiles["voice_13"].name == "System"
    
    def test_voice_catalog_verification(self):
        """Test voice catalog verification."""
        verification = self.audio_system.verify_voice_catalog()
        
        assert verification["total_voices"] == 13
        assert verification["expected_voices"] == 13
        assert verification["catalog_complete"] == True
        assert verification["audio_quality"]["sample_rate"] == 44100
        assert verification["audio_quality"]["bit_depth"] == 16
    
    @pytest.mark.asyncio
    async def test_speech_synthesis(self):
        """Test speech synthesis functionality."""
        result = await self.audio_system.synthesize_speech("Hello, world!")
        
        assert result["success"] == True
        assert "response_time" in result
        assert result["response_time"] < 2.0  # Performance target
        assert result["audio_settings"]["sample_rate"] == 44100
    
    @pytest.mark.asyncio
    async def test_voice_selection(self):
        """Test voice selection and switching."""
        # Test setting specific voice
        success = self.audio_system.set_voice("voice_02")
        assert success == True
        
        current_voice = self.audio_system.get_current_voice()
        assert current_voice["voice_id"] == "voice_02"
        assert current_voice["name"] == "David"
    
    def test_available_voices(self):
        """Test getting available voices."""
        voices = self.audio_system.get_available_voices()
        
        assert len(voices) == 13
        assert all("voice_id" in voice for voice in voices)
        assert all("name" in voice for voice in voices)
        assert all("quality" in voice for voice in voices)
    
    def test_metrics(self):
        """Test audio system metrics."""
        metrics = self.audio_system.get_metrics()
        
        assert isinstance(metrics, dict)
        assert "voice_responses" in metrics
        assert "voice_catalog_size" in metrics
        assert metrics["voice_catalog_size"] == 13
        assert "performance_targets" in metrics


@pytest.mark.asyncio
async def test_integration():
    """Integration test for all components working together."""
    # Create fresh instances
    app = VPAApplication()
    
    try:
        # Test startup
        success = await app.startup()
        assert success == True
        
        # Test event system integration with proper async context
        event_received = False
        
        def test_handler(event):
            nonlocal event_received
            event_received = True
        
        from vpa.core.events import event_bus
        event_bus.subscribe("integration_test", test_handler)
        
        # Use async emit instead of sync emit
        await event_bus.emit_async("integration_test", {"test": True})
        
        # Wait for async processing
        await asyncio.sleep(0.1)
        assert event_received == True
        
        # Test audio system integration
        from audio.voice_system import audio_system
        verification = audio_system.verify_voice_catalog()
        assert verification["catalog_complete"] == True
        
        # Test performance targets
        status = app.get_status()
        assert status["performance_targets"]["startup_time_achieved"] == True
        
    finally:
        await app.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])