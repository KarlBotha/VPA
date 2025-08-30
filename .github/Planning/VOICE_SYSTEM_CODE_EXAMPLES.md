# Voice System Code Examples

This document provides practical code examples for common tasks when working with the VPA Voice System. These examples demonstrate best practices for voice integration following VPA architectural principles.

## Table of Contents

1. [Basic Voice Operations](#1-basic-voice-operations)
2. [Advanced Voice Control](#2-advanced-voice-control)
3. [Event-Driven Voice Integration](#3-event-driven-voice-integration)
4. [Voice Integration in Plugins](#4-voice-integration-in-plugins)
5. [Error Handling Patterns](#5-error-handling-patterns)
6. [Performance Optimization](#6-performance-optimization)
7. [Voice System Extensions](#7-voice-system-extensions)

## 1. Basic Voice Operations

### 1.1 Initializing the Voice System

```python
from audio.voice_system import audio_system

async def initialize_voice_system():
    """Initialize the voice system with performance tracking"""
    from vpa.core.performance import PerformanceMonitor
    
    with PerformanceMonitor.track_execution_time("voice_system_init"):
        success = await audio_system.initialize()
        
    if not success:
        logging.error("Voice system initialization failed")
        return False
        
    logging.info(f"Voice system initialized with {len(audio_system.get_available_voices())} voices")
    return True
```

### 1.2 Getting Available Voices

```python
def get_voice_options():
    """Get formatted list of available voices with metadata"""
    voices = audio_system.get_available_voices()
    
    # Format for display or processing
    voice_options = []
    for voice in voices:
        voice_options.append({
            "name": voice.get("name", "Unknown"),
            "display_name": voice.get("name", "Unknown"),
            "gender": voice.get("gender", "unknown"),
            "description": voice.get("description", ""),
            "voice_id": voice.get("voice_id", ""),
            "is_default": voice.get("name") == "Aria"
        })
    
    # Sort voices: default first, then alphabetically
    voice_options.sort(key=lambda v: (0 if v["is_default"] else 1, v["name"]))
    return voice_options
```

### 1.3 Setting the Active Voice

```python
async def set_user_voice(voice_name):
    """Set user's preferred voice with validation and event tracking"""
    from vpa.core.events import event_bus
    
    # Validate voice exists
    voices = audio_system.get_available_voices()
    voice_names = [v.get("name") for v in voices]
    
    if voice_name not in voice_names:
        logging.error(f"Voice '{voice_name}' not found in available voices")
        return False
    
    # Set voice with performance tracking
    from vpa.core.performance import PerformanceMonitor
    with PerformanceMonitor.track_execution_time("voice_change"):
        success = await audio_system.set_voice(voice_name)
    
    if success:
        # Notify system of voice change
        await event_bus.emit_async("user.preference.updated", {
            "setting": "voice",
            "value": voice_name
        })
        
        # Confirm voice change with a test phrase
        await audio_system.speak_async(f"Voice changed to {voice_name}")
        
    return success
```

### 1.4 Basic Speech Synthesis

```python
async def speak_text(text, voice_id=None, wait_for_completion=True):
    """Basic speech synthesis with performance tracking"""
    from vpa.core.performance import PerformanceMonitor
    
    with PerformanceMonitor.track_execution_time("speech_synthesis"):
        # Start speech synthesis
        success = await audio_system.speak_async(text, voice_id)
        
    if not success:
        logging.error("Speech synthesis failed")
        return False
        
    # Optionally wait for speech to complete
    if wait_for_completion and success:
        while audio_system.is_speaking():
            await asyncio.sleep(0.1)
            
    return success
```

## 2. Advanced Voice Control

### 2.1 Using SSML for Advanced Speech Control

```python
async def speak_with_emphasis(text, emphasized_word, voice_id=None):
    """Use SSML to add emphasis to specific words"""
    # Build SSML with emphasis
    parts = text.split(emphasized_word, 1)
    if len(parts) != 2:
        # Word not found, use plain speech
        return await audio_system.speak_async(text, voice_id)
    
    ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis">
    <voice name="{voice_id or audio_system.get_voice_info().get('voice_id')}">
      {parts[0]}<emphasis level="strong">{emphasized_word}</emphasis>{parts[1]}
    </voice>
    </speak>"""
    
    return await audio_system.speak_ssml_async(ssml)
```

### 2.2 Controlling Speech Rate

```python
async def speak_with_custom_rate(text, rate=1.0, voice_id=None):
    """Speak text with custom speech rate"""
    # Validate rate is within acceptable range
    rate = max(0.5, min(2.0, rate))
    
    ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis">
    <voice name="{voice_id or audio_system.get_voice_info().get('voice_id')}">
      <prosody rate="{rate}">
        {text}
      </prosody>
    </voice>
    </speak>"""
    
    return await audio_system.speak_ssml_async(ssml)
```

### 2.3 Adding Pauses and Breaks

```python
async def speak_with_pauses(text_segments, pause_seconds=1.0, voice_id=None):
    """Speak multiple text segments with pauses between them"""
    # Join segments with pause breaks
    pause_ms = int(pause_seconds * 1000)
    combined_text = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis">
    <voice name="{voice_id or audio_system.get_voice_info().get('voice_id')}">"""
    
    for i, segment in enumerate(text_segments):
        combined_text += segment
        if i < len(text_segments) - 1:
            combined_text += f'<break time="{pause_ms}ms"/>'
    
    combined_text += "</voice></speak>"
    
    return await audio_system.speak_ssml_async(combined_text)
```

### 2.4 Voice Queue Management

```python
class VoiceQueue:
    """Manager for queuing multiple voice requests"""
    
    def __init__(self):
        self.queue = asyncio.Queue()
        self.is_processing = False
        self.current_task = None
        
    async def add_speech(self, text, voice_id=None, priority="normal"):
        """Add speech to the queue with priority"""
        # Priority determines position in queue
        if priority == "high":
            # Insert at front of queue
            # Note: Queue doesn't support direct insertion, this is a workaround
            current_items = []
            while not self.queue.empty():
                current_items.append(await self.queue.get())
            
            await self.queue.put((text, voice_id))
            
            for item in current_items:
                await self.queue.put(item)
        else:
            # Add to end of queue
            await self.queue.put((text, voice_id))
        
        # Start processing if not already running
        if not self.is_processing:
            self.current_task = asyncio.create_task(self._process_queue())
    
    async def _process_queue(self):
        """Process speech queue sequentially"""
        self.is_processing = True
        
        try:
            while not self.queue.empty():
                text, voice_id = await self.queue.get()
                
                # Process speech
                await audio_system.speak_async(text, voice_id)
                
                # Mark task as done
                self.queue.task_done()
                
        finally:
            self.is_processing = False
            
    def clear(self):
        """Clear all pending speech"""
        # Create new queue instead of trying to clear existing one
        self.queue = asyncio.Queue()
        
        # Stop current speech
        audio_system.stop_speaking()
        
        # Cancel processing task if running
        if self.current_task:
            self.current_task.cancel()
            self.is_processing = False
```

## 3. Event-Driven Voice Integration

### 3.1 Speech Events Subscription

```python
from vpa.core.events import event_bus

def setup_voice_event_listeners():
    """Set up listeners for voice events"""
    
    # Speech synthesis started
    event_bus.subscribe(
        "voice.synthesis.start",
        on_speech_started,
        async_callback=True
    )
    
    # Speech synthesis completed
    event_bus.subscribe(
        "voice.synthesis.complete",
        on_speech_completed,
        async_callback=True
    )
    
    # Speech playback started
    event_bus.subscribe(
        "voice.playback.start",
        on_playback_started,
        async_callback=True
    )
    
    # Speech playback completed
    event_bus.subscribe(
        "voice.playback.complete",
        on_playback_completed,
        async_callback=True
    )
    
    # Voice system errors
    event_bus.subscribe(
        "voice.error",
        on_voice_error,
        async_callback=True
    )

async def on_speech_started(event_data):
    """Handle speech synthesis start event"""
    text = event_data.get("text", "")
    voice_id = event_data.get("voice_id", "")
    logging.debug(f"Speech synthesis started: {voice_id} - {text[:20]}...")
    
    # Update UI if needed
    await event_bus.emit_async("ui.update", {
        "component": "status",
        "status": "speaking",
        "voice": voice_id
    })

async def on_speech_completed(event_data):
    """Handle speech synthesis completion event"""
    duration = event_data.get("duration", 0)
    logging.debug(f"Speech synthesis completed in {duration:.2f}s")
    
    # Track performance
    from vpa.core.performance import PerformanceMonitor
    PerformanceMonitor.record_metric("voice_synthesis_time", duration)
```

### 3.2 Requesting Speech Through Events

```python
async def request_speech_via_events(text, voice_id=None, priority="normal"):
    """Request speech synthesis through the event bus"""
    from vpa.core.events import event_bus
    
    # Generate unique request ID for tracking
    request_id = f"speech_{int(time.time() * 1000)}"
    
    # Create event payload
    speech_request = {
        "text": text,
        "request_id": request_id,
        "priority": priority,
        "timestamp": time.time()
    }
    
    if voice_id:
        speech_request["voice_id"] = voice_id
    
    # Emit speech request event
    await event_bus.emit_async("voice.speak", speech_request)
    
    return request_id
```

### 3.3 Complete Voice System Event Handler

```python
class VoiceSystemEventHandler:
    """Comprehensive voice system event handler"""
    
    def __init__(self):
        self.speech_history = []
        self.max_history = 50
        self._register_events()
        
    def _register_events(self):
        """Register all voice system event handlers"""
        from vpa.core.events import event_bus
        
        # Register all handlers
        self._unsubscribe_functions = [
            event_bus.subscribe("voice.speak", self._on_speak_request, async_callback=True),
            event_bus.subscribe("voice.stop", self._on_stop_request),
            event_bus.subscribe("voice.change", self._on_change_request, async_callback=True),
            event_bus.subscribe("voice.synthesis.start", self._on_synthesis_start, async_callback=True),
            event_bus.subscribe("voice.synthesis.complete", self._on_synthesis_complete, async_callback=True),
            event_bus.subscribe("voice.playback.start", self._on_playback_start, async_callback=True),
            event_bus.subscribe("voice.playback.complete", self._on_playback_complete, async_callback=True),
            event_bus.subscribe("voice.error", self._on_voice_error, async_callback=True),
        ]
    
    async def _on_speak_request(self, event_data):
        """Handle speech request"""
        from audio.voice_system import audio_system
        
        text = event_data.get("text", "")
        voice_id = event_data.get("voice_id")
        priority = event_data.get("priority", "normal")
        request_id = event_data.get("request_id", "unknown")
        
        # Check if we should interrupt current speech
        if priority in ["high", "critical"] and audio_system.is_speaking():
            audio_system.stop_speaking()
        
        # Start speech
        success = await audio_system.speak_async(text, voice_id)
        
        # Record in history
        self._add_to_history({
            "text": text,
            "voice_id": voice_id or audio_system.get_voice_info().get("name"),
            "timestamp": time.time(),
            "request_id": request_id,
            "success": success
        })
        
        # Emit response event
        await event_bus.emit_async("voice.response", {
            "request_id": request_id,
            "success": success
        })
    
    # Add other event handlers...
    
    def _add_to_history(self, entry):
        """Add entry to speech history with size limit"""
        self.speech_history.append(entry)
        
        # Maintain max history size
        if len(self.speech_history) > self.max_history:
            self.speech_history = self.speech_history[-self.max_history:]
    
    def get_speech_history(self):
        """Get copy of speech history"""
        return list(self.speech_history)
    
    def cleanup(self):
        """Clean up event subscriptions"""
        for unsubscribe in self._unsubscribe_functions:
            unsubscribe()
```

## 4. Voice Integration in Plugins

### 4.1 Basic Plugin Voice Integration

```python
from vpa.core.plugins import Plugin
from vpa.core.events import event_bus

class WeatherPlugin(Plugin):
    """Example weather plugin with voice integration"""
    
    @property
    def name(self) -> str:
        return "weather_plugin"
    
    def can_handle(self, user_input: str, context: dict) -> bool:
        """Check if plugin can handle the input"""
        weather_keywords = ["weather", "forecast", "temperature", "rain"]
        return any(keyword in user_input.lower() for keyword in weather_keywords)
    
    async def process(self, user_input: str, context: dict) -> dict:
        """Process user input and generate voice response"""
        # Generate weather info (simplified)
        weather_info = await self._get_weather_info(user_input)
        
        # Format text response
        text_response = f"The temperature is {weather_info['temperature']}°C with {weather_info['conditions']}."
        
        # Request voice feedback using user's selected voice (no voice_id means use current voice)
        await event_bus.emit_async("voice.speak", {
            "text": text_response,
            "priority": "normal",
            "plugin_id": self.name
        })
        
        # Return response for text display
        return {
            "response": text_response,
            "weather_data": weather_info
        }
    
    async def _get_weather_info(self, query):
        """Get weather information (mock implementation)"""
        # In real implementation, this would call a weather service
        return {
            "location": "Seattle",
            "temperature": 18,
            "conditions": "partly cloudy",
            "humidity": 65
        }
```

### 4.2 User Voice Preference Helper

```python
class UserVoicePreferenceHelper:
    """Helper class for managing user voice preferences"""
    
    @staticmethod
    async def get_user_preferred_voice():
        """Get the user's preferred voice from settings"""
        from vpa.core.settings import settings_manager
        
        # Get user voice preference
        voice_settings = settings_manager.get_setting_group("voice")
        preferred_voice = voice_settings.get("preferred_voice", "Aria")
        
        return preferred_voice
    
    @staticmethod
    async def save_user_voice_preference(voice_name):
        """Save the user's preferred voice to settings"""
        from vpa.core.settings import settings_manager
        from audio.voice_system import audio_system
        
        # Validate voice exists
        all_voices = audio_system.get_available_voices()
        available_voice_names = [v["name"] for v in all_voices]
        
        if voice_name not in available_voice_names:
            return False
            
        # Save preference
        await settings_manager.update_setting("voice.preferred_voice", voice_name)
        
        # Set as current voice
        success = await audio_system.set_voice(voice_name)
        
        return success
        
    @staticmethod
    def get_voice_options():
        """Get formatted list of available voices for UI selection"""
        from audio.voice_system import audio_system
        
        # Get all available voices
        all_voices = audio_system.get_available_voices()
        
        # Format for UI selection
        voice_options = []
        for voice in all_voices:
            voice_options.append({
                "value": voice["name"],
                "label": f"{voice['name']} ({voice.get('gender', 'Unknown')})",
                "description": voice.get("description", ""),
                "is_default": voice["name"] == "Aria"
            })
            
        return voice_options
```

### 4.3 Plugin With Advanced Voice Features

```python
class TutorialPlugin(Plugin):
    """Tutorial plugin with advanced voice features"""
    
    @property
    def name(self) -> str:
        return "tutorial_plugin"
    
    async def process(self, user_input: str, context: dict) -> dict:
        """Process tutorial request with advanced speech features"""
        # Get tutorial content
        tutorial = self._get_tutorial_content(user_input)
        
        # Use helper to select appropriate voice
        from .helpers import VoiceSelectionHelper
        voice = VoiceSelectionHelper.select_voice_for_content(
            content_type="technical",
            emotion="professional"
        )
        
        # Create SSML with sections and pauses
        ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis">
        <voice name="{voice}">
            <prosody rate="0.9">
                <emphasis level="strong">{tutorial["title"]}</emphasis>
                <break time="1000ms"/>
                
                {tutorial["introduction"]}
                <break time="800ms"/>
                
                First, {tutorial["steps"][0]}
                <break time="500ms"/>
                
                Next, {tutorial["steps"][1]}
                <break time="500ms"/>
                
                Finally, {tutorial["steps"][2]}
                <break time="800ms"/>
                
                {tutorial["conclusion"]}
            </prosody>
        </voice>
        </speak>"""
        
        # Request speech with SSML
        await event_bus.emit_async("voice.speak.ssml", {
            "ssml": ssml,
            "priority": "normal",
            "plugin_id": self.name
        })
        
        # Return response for text display
        return {
            "response": f"Tutorial: {tutorial['title']}",
            "tutorial": tutorial
        }
    
    def _get_tutorial_content(self, query):
        """Get tutorial content based on query"""
        # In a real implementation, this would look up actual tutorials
        return {
            "title": "How to Create a Voice Plugin",
            "introduction": "This tutorial will guide you through creating a voice-enabled plugin for VPA.",
            "steps": [
                "Create a new plugin class that extends the Plugin base class.",
                "Implement the required methods including process and can_handle.",
                "Use the event bus to request voice synthesis with your plugin responses."
            ],
            "conclusion": "Your plugin is now ready to use voice capabilities. Test it by asking a relevant question."
        }
```

## 5. Error Handling Patterns

### 5.1 Basic Error Handling

```python
async def speak_with_error_handling(text, voice_id=None):
    """Basic speech with comprehensive error handling"""
    try:
        # Try primary speech method
        success = await audio_system.speak_async(text, voice_id)
        
        if not success:
            logging.warning(f"Speech synthesis returned failure for: {text[:30]}...")
            
            # Try fallback voice
            fallback_voice = "Aria" if voice_id != "Aria" else None
            fallback_success = await audio_system.speak_async(text, fallback_voice)
            
            if not fallback_success:
                logging.error("Fallback speech synthesis also failed")
                return False
                
            return True
            
        return success
        
    except Exception as e:
        logging.exception(f"Exception during speech synthesis: {e}")
        
        # Emit error event
        from vpa.core.events import event_bus
        event_bus.emit("voice.error", {
            "error": str(e),
            "text": text,
            "voice_id": voice_id
        })
        
        return False
```

### 5.2 Voice System Health Check

```python
async def voice_system_health_check():
    """Comprehensive voice system health check"""
    from audio.voice_system import audio_system
    from vpa.core.events import event_bus
    
    health_status = {
        "system_available": False,
        "primary_provider_available": False,
        "fallback_provider_available": False,
        "voice_count": 0,
        "default_voice_available": False,
        "playback_working": False,
        "issues": []
    }
    
    try:
        # Check if system is initialized
        if not hasattr(audio_system, "is_initialized") or not audio_system.is_initialized:
            health_status["issues"].append("Voice system not initialized")
            return health_status
            
        health_status["system_available"] = True
        
        # Check providers
        if hasattr(audio_system, "providers"):
            providers = audio_system.providers
            
            if "edge-tts" in providers and providers["edge-tts"].available:
                health_status["primary_provider_available"] = True
            else:
                health_status["issues"].append("Primary voice provider (edge-tts) unavailable")
                
            if "sapi" in providers and providers["sapi"].available:
                health_status["fallback_provider_available"] = True
            else:
                health_status["issues"].append("Fallback voice provider (SAPI) unavailable")
        
        # Check voices
        voices = audio_system.get_available_voices()
        health_status["voice_count"] = len(voices)
        
        if len(voices) < 13:
            health_status["issues"].append(f"Only {len(voices)}/13 voices available")
            
        # Check default voice
        voice_info = audio_system.get_voice_info()
        if voice_info and "name" in voice_info:
            health_status["default_voice_available"] = True
        else:
            health_status["issues"].append("Default voice not available")
        
        # Test playback with short test
        if health_status["system_available"] and health_status["default_voice_available"]:
            try:
                test_result = await asyncio.wait_for(
                    audio_system.speak_async("Test", wait_for_completion=True),
                    timeout=3.0
                )
                health_status["playback_working"] = test_result
                
                if not test_result:
                    health_status["issues"].append("Playback test failed")
            except asyncio.TimeoutError:
                health_status["issues"].append("Playback test timed out")
                
        # Report health status
        await event_bus.emit_async("system.health.update", {
            "component": "voice_system",
            "status": "healthy" if not health_status["issues"] else "degraded",
            "details": health_status
        })
        
        return health_status
        
    except Exception as e:
        logging.exception(f"Voice system health check failed: {e}")
        health_status["issues"].append(f"Health check exception: {str(e)}")
        
        # Report failure
        await event_bus.emit_async("system.health.update", {
            "component": "voice_system",
            "status": "error",
            "details": health_status
        })
        
        return health_status
```

### 5.3 Graceful Degradation

```python
class VoiceSystemWithDegradation:
    """Voice system wrapper with graceful degradation"""
    
    def __init__(self, audio_system):
        self.audio_system = audio_system
        self.degraded_mode = False
        self.issues = []
        self.last_health_check = 0
        self.health_check_interval = 300  # seconds
        
    async def speak_async(self, text, voice_id=None):
        """Speak with graceful degradation"""
        # Check health periodically
        await self._check_health_if_needed()
        
        # If in degraded mode, use simplified approach
        if self.degraded_mode:
            return await self._speak_degraded(text, voice_id)
            
        # Try normal operation
        try:
            success = await self.audio_system.speak_async(text, voice_id)
            if not success:
                # Single failure doesn't trigger degraded mode
                logging.warning("Speech synthesis failed but system still operational")
                return await self._speak_degraded(text, voice_id)
            return success
        except Exception as e:
            logging.error(f"Speech error, switching to degraded mode: {e}")
            self.degraded_mode = True
            self.issues.append(f"Switched to degraded mode: {str(e)}")
            
            # Report degradation
            from vpa.core.events import event_bus
            event_bus.emit("voice.system.degraded", {
                "reason": str(e)
            })
            
            # Try degraded operation
            return await self._speak_degraded(text, voice_id)
    
    async def _speak_degraded(self, text, voice_id=None):
        """Simplified speech in degraded mode"""
        try:
            # Try with system voice (most reliable)
            if hasattr(self.audio_system, "providers") and "sapi" in self.audio_system.providers:
                provider = self.audio_system.providers["sapi"]
                if provider.available:
                    return await provider.synthesize(text, "system") is not None
            
            # Last resort - print to console and emit text event
            logging.warning(f"Voice system in degraded mode, text: {text}")
            
            # Emit text-only event
            from vpa.core.events import event_bus
            event_bus.emit("voice.text.fallback", {
                "text": text,
                "intended_voice": voice_id
            })
            
            return False
            
        except Exception as e:
            logging.error(f"Even degraded speech failed: {e}")
            return False
    
    async def _check_health_if_needed(self):
        """Perform health check if interval elapsed"""
        current_time = time.time()
        
        # Check if it's time for a health check
        if current_time - self.last_health_check > self.health_check_interval:
            await self._check_health()
            self.last_health_check = current_time
    
    async def _check_health(self):
        """Check system health and recover if possible"""
        try:
            if not self.degraded_mode:
                return  # Already in normal mode
                
            # Try to initialize system again
            if hasattr(self.audio_system, "initialize"):
                success = await self.audio_system.initialize()
                
                if success:
                    # Test with simple speech
                    test_success = await self.audio_system.speak_async(
                        "System recovered",
                        wait_for_completion=True
                    )
                    
                    if test_success:
                        # Recovery successful
                        self.degraded_mode = False
                        self.issues.append("Recovered from degraded mode")
                        
                        # Report recovery
                        from vpa.core.events import event_bus
                        event_bus.emit("voice.system.recovered", {})
                        
        except Exception as e:
            logging.error(f"Health check failed: {e}")
            # Stay in degraded mode
```

## 6. Performance Optimization

### 6.1 Voice Synthesis Performance Monitoring

```python
class VoicePerformanceMonitor:
    """Monitor voice system performance"""
    
    def __init__(self):
        self.metrics = {
            "synthesis_times": [],
            "max_synthesis_time": 0,
            "total_speech_requests": 0,
            "failed_requests": 0,
            "voice_usage": {},
            "average_synthesis_time": 0
        }
        self._register_events()
        
    def _register_events(self):
        """Register performance monitoring events"""
        from vpa.core.events import event_bus
        
        self._unsubscribe_funcs = [
            event_bus.subscribe("voice.synthesis.start", self._on_synthesis_start),
            event_bus.subscribe("voice.synthesis.complete", self._on_synthesis_complete),
            event_bus.subscribe("voice.error", self._on_synthesis_error)
        ]
        
    def _on_synthesis_start(self, event_data):
        """Track synthesis start"""
        self.metrics["total_speech_requests"] += 1
        voice_id = event_data.get("voice_id", "unknown")
        
        # Track voice usage
        if voice_id not in self.metrics["voice_usage"]:
            self.metrics["voice_usage"][voice_id] = 0
        self.metrics["voice_usage"][voice_id] += 1
        
        # Store request for timing
        event_data["_start_time"] = time.time()
        
    def _on_synthesis_complete(self, event_data):
        """Track synthesis completion and timing"""
        duration = event_data.get("duration")
        
        if duration:
            # Track synthesis time
            self.metrics["synthesis_times"].append(duration)
            
            # Limit history size
            if len(self.metrics["synthesis_times"]) > 100:
                self.metrics["synthesis_times"] = self.metrics["synthesis_times"][-100:]
                
            # Update max time
            if duration > self.metrics["max_synthesis_time"]:
                self.metrics["max_synthesis_time"] = duration
                
            # Update average
            self.metrics["average_synthesis_time"] = sum(self.metrics["synthesis_times"]) / len(self.metrics["synthesis_times"])
            
            # Check against performance target
            if duration > 2.0:
                logging.warning(f"Voice synthesis exceeded performance target: {duration:.2f}s")
                
                # Emit performance alert
                from vpa.core.events import event_bus
                event_bus.emit("performance.alert", {
                    "component": "voice_system",
                    "metric": "synthesis_time",
                    "value": duration,
                    "threshold": 2.0,
                    "text_length": len(event_data.get("text", ""))
                })
    
    def _on_synthesis_error(self, event_data):
        """Track synthesis errors"""
        self.metrics["failed_requests"] += 1
    
    def get_performance_report(self):
        """Generate comprehensive performance report"""
        # Calculate statistics
        success_rate = 0
        if self.metrics["total_speech_requests"] > 0:
            success_rate = 100 * (self.metrics["total_speech_requests"] - self.metrics["failed_requests"]) / self.metrics["total_speech_requests"]
            
        # Sort voices by usage
        voice_usage = sorted(
            self.metrics["voice_usage"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Generate report
        return {
            "average_synthesis_time": self.metrics["average_synthesis_time"],
            "max_synthesis_time": self.metrics["max_synthesis_time"],
            "total_requests": self.metrics["total_speech_requests"],
            "success_rate": success_rate,
            "top_voices": voice_usage[:3],
            "performance_status": "good" if self.metrics["average_synthesis_time"] < 1.5 else "warning",
            "meets_target": self.metrics["average_synthesis_time"] < 2.0
        }
        
    def cleanup(self):
        """Clean up event subscriptions"""
        for unsub in self._unsubscribe_funcs:
            unsub()
```

### 6.2 Voice Caching System

```python
class VoiceCacheManager:
    """Manage voice synthesis caching for improved performance"""
    
    def __init__(self, max_cache_size_mb=100):
        self.cache_dir = os.path.join(tempfile.gettempdir(), "vpa_voice_cache")
        self.max_cache_size = max_cache_size_mb * 1024 * 1024  # Convert to bytes
        self.cache_index = {}
        self._ensure_cache_dir()
        
    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
    def get_cached_speech(self, text, voice_id):
        """Get cached speech file if available"""
        cache_key = self._get_cache_key(text, voice_id)
        
        if cache_key in self.cache_index:
            file_path = os.path.join(self.cache_dir, f"{cache_key}.mp3")
            
            if os.path.exists(file_path):
                # Update last access time
                self.cache_index[cache_key]["last_accessed"] = time.time()
                return file_path
                
            # File missing but in index - remove from index
            del self.cache_index[cache_key]
            
        return None
        
    def add_to_cache(self, text, voice_id, file_path):
        """Add synthesized speech to cache"""
        # Generate cache key
        cache_key = self._get_cache_key(text, voice_id)
        
        # Get file size
        try:
            file_size = os.path.getsize(file_path)
            
            # Copy to cache location
            cached_path = os.path.join(self.cache_dir, f"{cache_key}.mp3")
            shutil.copy2(file_path, cached_path)
            
            # Add to index
            self.cache_index[cache_key] = {
                "text": text[:50] + ("..." if len(text) > 50 else ""),
                "voice_id": voice_id,
                "size": file_size,
                "created": time.time(),
                "last_accessed": time.time()
            }
            
            # Check cache size and clean if needed
            self._clean_cache_if_needed()
            
            return cached_path
            
        except Exception as e:
            logging.error(f"Failed to add file to voice cache: {e}")
            return None
    
    def _get_cache_key(self, text, voice_id):
        """Generate cache key from text and voice"""
        # Use hash of text and voice for key
        combined = f"{voice_id}:{text}"
        return hashlib.md5(combined.encode()).hexdigest()
        
    def _clean_cache_if_needed(self):
        """Clean cache if it exceeds size limit"""
        # Calculate current size
        current_size = sum(item["size"] for item in self.cache_index.values())
        
        if current_size <= self.max_cache_size:
            return  # Cache size acceptable
            
        # Need to clean cache
        logging.info(f"Voice cache exceeded size limit ({current_size / 1024 / 1024:.2f}MB). Cleaning...")
        
        # Sort items by last access time (oldest first)
        items = list(self.cache_index.items())
        items.sort(key=lambda x: x[1]["last_accessed"])
        
        # Remove items until we're under the limit
        for key, info in items:
            if current_size <= self.max_cache_size * 0.9:  # Clean until we're 10% under limit
                break
                
            # Remove file
            file_path = os.path.join(self.cache_dir, f"{key}.mp3")
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logging.error(f"Failed to remove cache file: {e}")
                
            # Update size and remove from index
            current_size -= info["size"]
            del self.cache_index[key]
            
        logging.info(f"Cache cleaned. New size: {current_size / 1024 / 1024:.2f}MB")
        
    def clear_cache(self):
        """Clear entire speech cache"""
        for key in list(self.cache_index.keys()):
            file_path = os.path.join(self.cache_dir, f"{key}.mp3")
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logging.error(f"Failed to remove cache file: {e}")
                
        self.cache_index = {}
        logging.info("Voice cache cleared")
        
    def get_cache_stats(self):
        """Get cache statistics"""
        if not self.cache_index:
            return {
                "item_count": 0,
                "total_size_mb": 0,
                "hit_rate": 0
            }
            
        total_size = sum(item["size"] for item in self.cache_index.values())
        
        return {
            "item_count": len(self.cache_index),
            "total_size_mb": total_size / 1024 / 1024,
            "usage_percent": (total_size / self.max_cache_size) * 100
        }
```

### 6.3 Optimized Voice Initialization

```python
async def initialize_voice_system_optimized():
    """Optimized voice system initialization with progressive availability"""
    from audio.voice_system import audio_system
    from vpa.core.events import event_bus
    
    # Set system to initializing state
    await event_bus.emit_async("voice.system.initializing", {})
    
    # Start background initialization
    init_task = asyncio.create_task(_full_voice_initialization())
    
    # Return immediately to let the application continue startup
    return True
    
async def _full_voice_initialization():
    """Complete voice system initialization in the background"""
    from audio.voice_system import audio_system
    from vpa.core.events import event_bus
    
    try:
        # Start with basic initialization (just system voice)
        await audio_system._initialize_basic()
        
        # Signal basic availability
        await event_bus.emit_async("voice.system.basic_ready", {
            "voices": ["System"]
        })
        
        # Initialize main provider
        success = await audio_system._initialize_primary_provider()
        
        if success:
            # Get list of available voices
            voices = audio_system.get_available_voices()
            voice_names = [v.get("name") for v in voices]
            
            # Signal full availability
            await event_bus.emit_async("voice.system.ready", {
                "voice_count": len(voices),
                "voices": voice_names
            })
        else:
            # Signal degraded mode
            await event_bus.emit_async("voice.system.degraded", {
                "reason": "Primary voice provider initialization failed"
            })
            
        # Final setup
        await audio_system._initialize_configuration()
        
    except Exception as e:
        logging.exception(f"Voice system initialization failed: {e}")
        
        # Signal error
        await event_bus.emit_async("voice.system.error", {
            "error": str(e)
        })
```

## 7. Voice System Extensions

### 7.1 Voice SSML Enhancer

```python
class VoiceSsmlEnhancer:
    """Enhance speech with SSML formatting"""
    
    @staticmethod
    def enhance_with_emphasis(text, emphasis_words):
        """Add emphasis to specific words in text"""
        # Copy text to avoid modifying original
        enhanced_text = text
        
        # Add emphasis tags around specified words
        for word in emphasis_words:
            if word in enhanced_text:
                enhanced_text = enhanced_text.replace(word, f'<emphasis level="strong">{word}</emphasis>')
        
        # Build complete SSML
        ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis">
        <prosody rate="1.0" pitch="0%">
          {enhanced_text}
        </prosody>
        </speak>"""
        
        return ssml
    
    @staticmethod
    def add_pauses(text, pause_points, pause_duration_ms=500):
        """Add pauses at specific points in text"""
        # Split text at punctuation
        segments = []
        last_pos = 0
        
        for pos in pause_points:
            if pos > last_pos:
                segments.append(text[last_pos:pos])
                last_pos = pos
                
        # Add final segment
        if last_pos < len(text):
            segments.append(text[last_pos:])
        
        # Join with pause breaks
        enhanced_text = f'<break time="{pause_duration_ms}ms"/>'.join(segments)
        
        # Build complete SSML
        ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis">
        <prosody rate="1.0" pitch="0%">
          {enhanced_text}
        </prosody>
        </speak>"""
        
        return ssml
    
    @staticmethod
    def adjust_speaking_rate(text, rate=1.0):
        """Adjust speaking rate for text"""
        # Validate rate is within acceptable range
        rate = max(0.5, min(1.5, rate))
        
        # Build SSML with rate adjustment
        ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis">
        <prosody rate="{rate}">
          {text}
        </prosody>
        </speak>"""
        
        return ssml
```

### 7.2 Voice Style Manager

```python
class VoiceStyleManager:
    """Manage voice styling options for the single user-selected voice"""
    
    @staticmethod
    async def apply_style(text, style):
        """Apply a predefined style to text using current voice"""
        from audio.voice_system import audio_system
        
        # Style parameters
        style_params = {
            "professional": {"rate": "1.0", "pitch": "+0%"},
            "technical": {"rate": "0.95", "pitch": "-5%"},
            "friendly": {"rate": "1.05", "pitch": "+8%"},
            "authoritative": {"rate": "0.97", "pitch": "-8%"},
            "calm": {"rate": "0.9", "pitch": "-3%"}
        }
        
        # Get style settings (default to professional)
        params = style_params.get(style, style_params["professional"])
        
        # Build SSML
        ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis">
          <prosody rate="{params['rate']}" pitch="{params['pitch']}">
            {text}
          </prosody>
        </speak>"""
        
        # Speak using current voice with styling
        await audio_system.speak_ssml_async(ssml)
    
    @staticmethod
    async def preview_voice(voice_name, preview_text=None):
        """Preview a voice with standard text"""
        from audio.voice_system import audio_system
        
        # Store current voice to restore later
        current_voice = audio_system.get_voice_info().get("name")
        
        # Set voice temporarily for preview
        await audio_system.set_voice(voice_name)
        
        # Use default preview text if none provided
        if not preview_text:
            preview_text = f"This is the {voice_name} voice. You can select this voice in settings."
            
        # Speak preview
        await audio_system.speak_async(preview_text)
        
        # Restore original voice
        await audio_system.set_voice(current_voice)
```

### 7.3 Voice Progress Indicator

```python
class VoiceProgressIndicator:
    """Voice-based progress indicator for long operations"""
    
    def __init__(self, operation_name, total_steps, voice_id="Aria"):
        self.operation_name = operation_name
        self.total_steps = total_steps
        self.current_step = 0
        self.voice_id = voice_id
        self.start_time = None
        self.last_update_time = 0
        self.update_interval = 5.0  # seconds between voice updates
        
    async def start(self):
        """Start the operation with voice announcement"""
        from audio.voice_system import audio_system
        
        self.start_time = time.time()
        self.last_update_time = self.start_time
        
        # Announce start
        start_text = f"Starting {self.operation_name}. This will take approximately {self._estimate_duration()} to complete."
        await audio_system.speak_async(start_text, self.voice_id)
        
    async def update(self, step=None, status_text=None):
        """Update progress with optional voice announcement"""
        from audio.voice_system import audio_system
        
        # Update step if provided
        if step is not None:
            self.current_step = min(step, self.total_steps)
        else:
            self.current_step += 1
            
        current_time = time.time()
        progress = self.current_step / self.total_steps
        
        # Check if it's time for a voice update
        if current_time - self.last_update_time >= self.update_interval:
            # Prepare update text
            if status_text:
                update_text = status_text
            else:
                percent = int(progress * 100)
                update_text = f"{self.operation_name} is {percent} percent complete."
                
                # Add time estimate for longer operations
                if progress > 0.1 and progress < 0.9:
                    remaining = self._estimate_remaining_time()
                    update_text += f" Approximately {remaining} remaining."
            
            # Announce update
            await audio_system.speak_async(update_text, self.voice_id)
            self.last_update_time = current_time
        
    async def complete(self, success=True, completion_text=None):
        """Announce operation completion"""
        from audio.voice_system import audio_system
        
        # Calculate total duration
        duration = time.time() - self.start_time
        duration_text = self._format_duration(duration)
        
        # Prepare completion text
        if completion_text:
            text = completion_text
        else:
            if success:
                text = f"{self.operation_name} completed successfully in {duration_text}."
            else:
                text = f"{self.operation_name} did not complete successfully. Total time: {duration_text}."
        
        # Announce completion
        await audio_system.speak_async(text, self.voice_id)
        
    def _estimate_duration(self):
        """Estimate total duration based on step count"""
        # Simple estimate based on step count
        if self.total_steps < 10:
            return "a minute or less"
        elif self.total_steps < 50:
            return "a few minutes"
        else:
            return "several minutes"
            
    def _estimate_remaining_time(self):
        """Estimate remaining time based on progress so far"""
        if self.current_step == 0:
            return self._estimate_duration()
            
        elapsed = time.time() - self.start_time
        progress = self.current_step / self.total_steps
        
        if progress < 0.01:
            return self._estimate_duration()
            
        total_estimated = elapsed / progress
        remaining = total_estimated - elapsed
        
        return self._format_duration(remaining)
        
    def _format_duration(self, seconds):
        """Format duration in seconds to human-readable text"""
        if seconds < 60:
            return "less than a minute"
        elif seconds < 120:
            return "about a minute"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"about {minutes} minutes"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            if minutes > 0:
                return f"about {hours} hours and {minutes} minutes"
            else:
                return f"about {hours} hours"
```

## Conclusion

These code examples demonstrate best practices for integrating with the VPA Voice System. They cover basic operations, advanced voice control, event-driven integration, plugin integration, error handling, performance optimization, and system extensions.

When working with the voice system:

1. Always use asynchronous patterns to avoid blocking the main thread
2. Handle errors gracefully with fallback mechanisms
3. Follow the event-driven architecture for loose coupling
4. Monitor performance to ensure response time targets are met
5. Consider the appropriate voice for the content being spoken

For more information, see the complete AUDIO_VOICE_SYSTEM_REQUIREMENTS.md document.

---

*Voice System Code Examples document created on August 27, 2025*
