# Voice Input Processing Specification [DEPRECATED]

> **IMPORTANT NOTICE:** This document has been deprecated and moved to the proper documentation location. 
> 
> **NEW LOCATION:** [docs/voice/implementation/VOICE_INPUT_PROCESSING.md](docs/voice/implementation/VOICE_INPUT_PROCESSING.md)

## Overview

This document defines the voice input processing system for VPA, which converts user speech to text and sends it to the LLM for processing.

## Table of Contents

1. [Voice Input Architecture](#1-voice-input-architecture)
2. [Speech-to-Text Implementation](#2-speech-to-text-implementation)
3. [UI Integration](#3-ui-integration)
4. [Error Handling](#4-error-handling)
5. [Performance Considerations](#5-performance-considerations)

## 1. Voice Input Architecture

### 1.1 Architecture Overview

The voice input system follows this processing flow:

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  Microphone   │────►│ Audio Capture │────►│ Speech-to-Text│────►│   Text Input  │
│   Input       │     │   System      │     │   Engine      │     │   Processing  │
└───────────────┘     └───────────────┘     └───────────────┘     └───────────┬───┘
                                                                             │
                                                                             ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  UI Display   │◄────│ LLM Response  │◄────│ LLM Processing│◄────│  Event Bus    │
│  (Chat UI)    │     │  Handler      │     │   System      │     │               │
└───────────────┘     └───────────────┘     └───────────────┘     └───────────────┘
```

### 1.2 Component Responsibilities

1. **Audio Capture System**: 
   - Activates microphone
   - Records audio input
   - Manages recording state
   - Provides visual feedback during recording

2. **Speech-to-Text Engine**:
   - Processes audio data
   - Converts speech to text
   - Handles different accents and speech patterns
   - Provides confidence scores for transcriptions

3. **Text Input Processing**:
   - Validates and formats transcribed text
   - Sends text to LLM via event bus
   - Updates UI with transcribed text
   - Handles correction of transcription errors

## 2. Speech-to-Text Implementation

### 2.1 Windows Speech Recognition Integration

VPA uses the Windows Speech Recognition API for offline speech-to-text conversion:

```python
class WindowsSpeechRecognition:
    """Windows Speech Recognition integration"""
    
    def __init__(self):
        self.engine = None
        self.is_listening = False
        self.event_bus = None
        
    async def initialize(self, event_bus):
        """Initialize the speech recognition engine"""
        try:
            # Import speech recognition modules
            import win32com.client
            import pythoncom
            
            # Initialize COM in the current thread
            pythoncom.CoInitialize()
            
            # Create speech recognition engine
            self.engine = win32com.client.Dispatch("SAPI.SpSharedRecognizer")
            
            # Create context for recognition
            self.context = self.engine.CreateRecoContext()
            
            # Set event interest
            self.context.EventInterests = 1  # Speech recognition events
            
            # Store event bus
            self.event_bus = event_bus
            
            # Set recognition language to English
            language = 0x409  # English - United States
            self.context.RecognizerSetLanguage(language)
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize speech recognition: {e}")
            return False
            
    async def start_listening(self):
        """Start listening for speech input"""
        if self.is_listening:
            return
            
        try:
            # Create grammar
            grammar = self.context.CreateGrammar()
            
            # Create dictation rule that allows free-form dictation
            rule = grammar.Rules.Add("Dictation", 1, 0)
            rule.InitialState.AddDictation()
            
            # Activate grammar
            grammar.CmdSetRuleState("Dictation", 1)  # 1 = Active
            grammar.Rules.Commit()
            
            # Set event callback
            self.context.OnRecognition = self._on_recognition
            
            # Start listening
            self.is_listening = True
            
            # Notify UI that listening started
            await self.event_bus.emit_async("voice_input.started", {})
            
            return True
        except Exception as e:
            logger.error(f"Failed to start speech recognition: {e}")
            await self.event_bus.emit_async("voice_input.error", {
                "message": str(e)
            })
            return False
            
    async def stop_listening(self):
        """Stop listening for speech input"""
        if not self.is_listening:
            return
            
        try:
            # Deactivate grammar
            grammar = self.context.CreateGrammar()
            grammar.CmdSetRuleState("Dictation", 0)  # 0 = Inactive
            
            # Stop listening
            self.is_listening = False
            
            # Notify UI that listening stopped
            await self.event_bus.emit_async("voice_input.stopped", {})
            
            return True
        except Exception as e:
            logger.error(f"Failed to stop speech recognition: {e}")
            return False
            
    def _on_recognition(self, stream_number, stream_position, recognition_type, result):
        """Callback for speech recognition results"""
        try:
            # Get recognition result
            recognized_text = result.PhraseInfo.GetText()
            
            # Post event to event bus (using asyncio.run to call async from sync)
            import asyncio
            asyncio.run(self._emit_recognition_result(recognized_text))
        except Exception as e:
            logger.error(f"Error in speech recognition callback: {e}")
            
    async def _emit_recognition_result(self, text):
        """Emit recognition result event"""
        await self.event_bus.emit_async("voice_input.result", {
            "text": text
        })
```

### 2.2 Fallback Web API Option

If the Windows Speech Recognition doesn't meet quality requirements, we can implement a fallback to an online service:

```python
class WebAPISpeechRecognition:
    """Web API-based speech recognition (fallback)"""
    
    def __init__(self, config):
        self.config = config
        self.is_listening = False
        self.event_bus = None
        self.audio_stream = None
        
    async def initialize(self, event_bus):
        """Initialize the speech recognition service"""
        self.event_bus = event_bus
        return True
        
    async def start_listening(self):
        """Start listening for speech input"""
        if self.is_listening:
            return
            
        try:
            import pyaudio
            
            # Initialize PyAudio
            audio = pyaudio.PyAudio()
            
            # Open audio stream
            self.audio_stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024
            )
            
            # Start recording in background
            self.is_listening = True
            self.recording_task = asyncio.create_task(self._record_and_recognize())
            
            # Notify UI that listening started
            await self.event_bus.emit_async("voice_input.started", {})
            
            return True
        except Exception as e:
            logger.error(f"Failed to start speech recognition: {e}")
            await self.event_bus.emit_async("voice_input.error", {
                "message": str(e)
            })
            return False
            
    async def stop_listening(self):
        """Stop listening for speech input"""
        if not self.is_listening:
            return
            
        try:
            # Stop recording
            self.is_listening = False
            if self.recording_task:
                self.recording_task.cancel()
                
            # Close audio stream
            if self.audio_stream:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio_stream = None
                
            # Notify UI that listening stopped
            await self.event_bus.emit_async("voice_input.stopped", {})
            
            return True
        except Exception as e:
            logger.error(f"Failed to stop speech recognition: {e}")
            return False
            
    async def _record_and_recognize(self):
        """Record audio and send for recognition"""
        try:
            frames = []
            
            # Record audio while listening
            while self.is_listening:
                # Read audio data
                data = self.audio_stream.read(1024)
                frames.append(data)
                
                # Check if we've recorded enough (3 seconds)
                if len(frames) >= 3 * (16000 // 1024):
                    # Send for recognition
                    audio_data = b''.join(frames)
                    text = await self._recognize_speech(audio_data)
                    if text:
                        await self.event_bus.emit_async("voice_input.result", {
                            "text": text
                        })
                    
                    # Reset frames
                    frames = []
                    
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            # Task was cancelled
            pass
        except Exception as e:
            logger.error(f"Error in recording task: {e}")
            
    async def _recognize_speech(self, audio_data):
        """Send audio data for recognition"""
        try:
            # Use selected web API for recognition
            if self.config.get("service") == "google":
                return await self._recognize_with_google(audio_data)
            else:
                # Default to Microsoft Speech API
                return await self._recognize_with_microsoft(audio_data)
        except Exception as e:
            logger.error(f"Speech recognition error: {e}")
            return None
            
    async def _recognize_with_microsoft(self, audio_data):
        """Recognize speech using Microsoft Speech API"""
        # Implementation details...
        pass
        
    async def _recognize_with_google(self, audio_data):
        """Recognize speech using Google Speech-to-Text"""
        # Implementation details...
        pass
```

### 2.3 Speech Recognition Factory

```python
class SpeechRecognitionFactory:
    """Factory for creating speech recognition instances"""
    
    @staticmethod
    async def create_recognition_engine(settings_manager, event_bus):
        """Create speech recognition engine based on settings"""
        # Get engine preference from settings
        engine_type = settings_manager.get("voice_input.engine", "windows")
        
        if engine_type == "windows":
            # Use Windows Speech Recognition
            engine = WindowsSpeechRecognition()
        elif engine_type == "web_api":
            # Use Web API for speech recognition
            config = {
                "service": settings_manager.get("voice_input.web_api_service", "microsoft"),
                "api_key": settings_manager.get("voice_input.web_api_key", "")
            }
            engine = WebAPISpeechRecognition(config)
        else:
            # Default to Windows Speech Recognition
            engine = WindowsSpeechRecognition()
            
        # Initialize engine
        success = await engine.initialize(event_bus)
        if not success:
            logger.warning("Failed to initialize preferred speech engine, trying fallback")
            
            # Try fallback
            engine = WebAPISpeechRecognition({
                "service": "microsoft"
            })
            await engine.initialize(event_bus)
            
        return engine
```

## 3. UI Integration

### 3.1 Voice Input Button

The UI provides a microphone button in the chat interface:

```python
def _create_input_area(self):
    """Create the input area component"""
    input_widget = QWidget()
    input_layout = QHBoxLayout(input_widget)
    input_layout.setContentsMargins(15, 10, 15, 10)
    
    # Attachment button
    attach_button = QPushButton()
    attach_button.setIcon(QIcon.fromTheme("mail-attachment"))
    attach_button.setToolTip("Attach Files")
    attach_button.clicked.connect(self._on_attach_clicked)
    input_layout.addWidget(attach_button)
    
    # Text input field
    self.input_field = QTextEdit()
    self.input_field.setPlaceholderText("Type a message...")
    self.input_field.setAcceptRichText(False)
    self.input_field.setMaximumHeight(100)  # Limit height
    self.input_field.textChanged.connect(self._on_input_text_changed)
    input_layout.addWidget(self.input_field, 1)  # 1 = stretch factor
    
    # Voice input button
    self.voice_button = QPushButton()
    self.voice_button.setIcon(QIcon.fromTheme("audio-input-microphone"))
    self.voice_button.setToolTip("Voice Input")
    self.voice_button.clicked.connect(self._on_voice_input_clicked)
    input_layout.addWidget(self.voice_button)
    
    # Send button
    self.send_button = QPushButton()
    self.send_button.setIcon(QIcon.fromTheme("mail-send"))
    self.send_button.setToolTip("Send Message")
    self.send_button.clicked.connect(self._on_send_clicked)
    self.send_button.setEnabled(False)  # Disabled until text entered
    input_layout.addWidget(self.send_button)
    
    return input_widget
```

### 3.2 Voice Input Handler

```python
async def _on_voice_input_clicked(self):
    """Handle voice input button click"""
    if not hasattr(self, 'is_listening') or not self.is_listening:
        # Start listening
        self.is_listening = True
        
        # Update button to show recording state
        self.voice_button.setIcon(QIcon.fromTheme("media-record"))
        self.voice_button.setStyleSheet("background-color: #ff4444;")
        
        # Show recording indicator in input field
        self.input_field.setPlaceholderText("Listening...")
        
        # Get speech recognition engine
        if not hasattr(self, 'speech_engine'):
            self.speech_engine = await SpeechRecognitionFactory.create_recognition_engine(
                self.settings_manager, 
                self.event_bus
            )
            
        # Subscribe to speech recognition events
        self.event_bus.subscribe(
            "voice_input.result", 
            self._on_voice_input_result,
            async_callback=True
        )
        
        # Start listening
        await self.speech_engine.start_listening()
    else:
        # Stop listening
        self.is_listening = False
        
        # Update button to normal state
        self.voice_button.setIcon(QIcon.fromTheme("audio-input-microphone"))
        self.voice_button.setStyleSheet("")
        
        # Reset input field placeholder
        self.input_field.setPlaceholderText("Type a message...")
        
        # Stop listening
        if hasattr(self, 'speech_engine'):
            await self.speech_engine.stop_listening()
        
        # Unsubscribe from events
        self.event_bus.unsubscribe(
            "voice_input.result", 
            self._on_voice_input_result
        )
```

### 3.3 Voice Recognition Result Handler

```python
async def _on_voice_input_result(self, event_data):
    """Handle voice input recognition result"""
    text = event_data.get("text", "")
    if not text:
        return
        
    # Add text to input field
    current_text = self.input_field.toPlainText()
    if current_text:
        # Add space if there's already text
        self.input_field.setPlainText(f"{current_text} {text}")
    else:
        self.input_field.setPlainText(text)
        
    # Stop listening after receiving text
    if self.is_listening:
        await self._on_voice_input_clicked()  # Toggle off
```

## 4. Error Handling

### 4.1 Voice Input Error Events

The voice input system emits these error events:

```python
# Initialization error
await self.event_bus.emit_async("voice_input.error", {
    "type": "initialization_error",
    "message": "Failed to initialize speech recognition engine"
})

# Recognition error
await self.event_bus.emit_async("voice_input.error", {
    "type": "recognition_error",
    "message": "Failed to recognize speech"
})

# Permission error
await self.event_bus.emit_async("voice_input.error", {
    "type": "permission_error",
    "message": "Microphone access denied"
})
```

### 4.2 Error Handling in UI

```python
def __init__(self, ui_manager, event_bus, settings_manager):
    # Other initialization...
    
    # Subscribe to voice input error events
    self.event_bus.subscribe(
        "voice_input.error", 
        self._on_voice_input_error,
        async_callback=True
    )
    
async def _on_voice_input_error(self, event_data):
    """Handle voice input errors"""
    error_type = event_data.get("type", "unknown")
    error_message = event_data.get("message", "Unknown error")
    
    # Reset voice button state
    self.is_listening = False
    self.voice_button.setIcon(QIcon.fromTheme("audio-input-microphone"))
    self.voice_button.setStyleSheet("")
    self.input_field.setPlaceholderText("Type a message...")
    
    # Show error dialog
    QMessageBox.warning(
        self,
        "Voice Input Error",
        f"Voice recognition error: {error_message}",
        QMessageBox.Ok
    )
    
    # Handle specific errors
    if error_type == "permission_error":
        # Show settings help
        QMessageBox.information(
            self,
            "Microphone Access",
            "VPA needs microphone access to use voice input. "
            "Please check your Windows privacy settings.",
            QMessageBox.Ok
        )
```

## 5. Performance Considerations

### 5.1 Resource Usage

The speech recognition system is designed to minimize resource usage:

1. **Lazy Initialization**: Speech recognition engine is only created when needed
2. **Resource Cleanup**: Audio resources are properly released after use
3. **Background Processing**: Recognition happens in background tasks
4. **Configurable Quality**: Quality settings can be adjusted based on hardware

### 5.2 Optimization Techniques

To ensure responsive performance:

1. **Chunked Processing**: Audio is processed in small chunks rather than waiting for complete utterance
2. **Progressive Feedback**: UI updates as recognition proceeds, not just at the end
3. **Timeout Handling**: Recognition automatically times out after periods of silence
4. **Resource Monitoring**: System monitors CPU/memory usage and adjusts accordingly

## Conclusion

The Voice Input Processing system enables users to interact with VPA using speech, converting voice to text that is then processed by the LLM. It provides a seamless integration between voice input, text processing, and LLM interaction while maintaining good performance and handling errors gracefully.

---

*Document created on August 28, 2025*  
*Version: 1.0*
