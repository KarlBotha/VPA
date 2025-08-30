# Phase 2: Audio System Implementation Plan

## Overview

This document outlines the implementation plan for Phase 2 of the VPA project, focusing on the Audio System. Building on the core architecture established in Phase 1, this phase will implement voice input and output capabilities, allowing for hands-free interaction with the assistant.

## Goals and Objectives

1. Implement a complete audio input/output system for voice interaction
2. Integrate speech recognition for converting spoken commands to text
3. Implement text-to-speech functionality with multiple voice options
4. Create audio device management for handling multiple input/output devices
5. Build an event-driven architecture for audio components
6. Ensure high performance and low latency for real-time voice interaction

## Prerequisites

- Completion of Phase 1 (Core Architecture)
- Python environment with audio libraries (sounddevice, PyAudio)
- Text-to-speech engine integration (Edge TTS)
- Speech recognition capabilities (Whisper)

## Implementation Components

### 1. Audio Manager

The `AudioManager` class will serve as the central coordinator for all audio-related functionality, managing both input (speech recognition) and output (text-to-speech) subsystems.

```python
# src/vpa/audio/audio_manager.py
from vpa.audio.voice_recognition import VoiceRecognition
from vpa.audio.voice_synthesis import VoiceSynthesis
from vpa.audio.device_manager import AudioDeviceManager
from vpa.core.events import event_bus
import asyncio
import logging

logger = logging.getLogger(__name__)

class AudioManager:
    """Manages audio input and output subsystems."""
    
    def __init__(self, config=None):
        """Initialize the audio manager.
        
        Args:
            config: Configuration dictionary
        """
        self._config = config or {}
        self._device_manager = AudioDeviceManager()
        self._voice_recognition = None
        self._voice_synthesis = None
        self._running = False
        self._processing_task = None
        
    async def initialize(self):
        """Initialize audio subsystems."""
        logger.info("Initializing Audio Manager")
        
        # Initialize device manager
        await self._device_manager.initialize()
        
        # Get device settings from config
        input_device = self._config.get("input_device")
        output_device = self._config.get("output_device")
        
        # Set devices if specified
        if input_device:
            self._device_manager.set_input_device(input_device)
        if output_device:
            self._device_manager.set_output_device(output_device)
            
        # Initialize voice recognition
        recognition_config = self._config.get("recognition", {})
        self._voice_recognition = VoiceRecognition(
            self._device_manager,
            recognition_config
        )
        await self._voice_recognition.initialize()
        
        # Initialize voice synthesis
        synthesis_config = self._config.get("synthesis", {})
        self._voice_synthesis = VoiceSynthesis(
            self._device_manager,
            synthesis_config
        )
        await self._voice_synthesis.initialize()
        
        # Subscribe to events
        event_bus.subscribe("speak_text", self._on_speak_text)
        event_bus.subscribe("start_listening", self._on_start_listening)
        event_bus.subscribe("stop_listening", self._on_stop_listening)
        
        logger.info("Audio Manager initialized successfully")
        return True
        
    async def start(self):
        """Start audio processing."""
        if self._running:
            return
            
        self._running = True
        self._processing_task = asyncio.create_task(self._process_audio())
        logger.info("Audio processing started")
        
    async def stop(self):
        """Stop audio processing."""
        if not self._running:
            return
            
        self._running = False
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
            self._processing_task = None
            
        logger.info("Audio processing stopped")
        
    async def _process_audio(self):
        """Process audio input and output."""
        while self._running:
            try:
                # Check for voice commands if active
                if self._voice_recognition.is_active():
                    result = await self._voice_recognition.process_audio_frame()
                    
                    # If we have a complete utterance, emit an event
                    if result and "text" in result:
                        await event_bus.emit_async("voice_command", {
                            "text": result["text"],
                            "confidence": result.get("confidence", 1.0)
                        })
                        
                # Allow other tasks to run
                await asyncio.sleep(0.01)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing audio: {e}")
                await asyncio.sleep(1)  # Avoid rapid error loops
                
    async def _on_speak_text(self, event_data):
        """Handle speak_text events."""
        text = event_data.get("text", "")
        voice = event_data.get("voice")
        
        if text:
            await self._voice_synthesis.speak(text, voice)
            
    async def _on_start_listening(self, _):
        """Handle start_listening events."""
        self._voice_recognition.activate()
        
    async def _on_stop_listening(self, _):
        """Handle stop_listening events."""
        self._voice_recognition.deactivate()
        
    async def shutdown(self):
        """Shut down audio subsystems."""
        logger.info("Shutting down Audio Manager")
        
        # Stop processing
        await self.stop()
        
        # Unsubscribe from events
        event_bus.unsubscribe("speak_text", self._on_speak_text)
        event_bus.unsubscribe("start_listening", self._on_start_listening)
        event_bus.unsubscribe("stop_listening", self._on_stop_listening)
        
        # Shut down subsystems
        if self._voice_recognition:
            await self._voice_recognition.shutdown()
            
        if self._voice_synthesis:
            await self._voice_synthesis.shutdown()
            
        await self._device_manager.shutdown()
        
        logger.info("Audio Manager shutdown complete")
```

### 2. Audio Device Manager

The `AudioDeviceManager` will handle audio device enumeration, selection, and configuration for both input and output devices.

```python
# src/vpa/audio/device_manager.py
import sounddevice as sd
import asyncio
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class AudioDeviceManager:
    """Manages audio input and output devices."""
    
    def __init__(self):
        """Initialize the device manager."""
        self._input_device = None  # ID or name of input device
        self._output_device = None  # ID or name of output device
        self._device_info = {}  # Cache of device information
        
    async def initialize(self):
        """Initialize the device manager."""
        # Refresh device information
        self._refresh_device_info()
        
        # Set default devices if none selected
        if self._input_device is None:
            self._input_device = sd.default.device[0]
            
        if self._output_device is None:
            self._output_device = sd.default.device[1]
            
        logger.info(f"Using input device: {self._get_device_name(self._input_device)}")
        logger.info(f"Using output device: {self._get_device_name(self._output_device)}")
        
        return True
        
    def _refresh_device_info(self):
        """Refresh the device information cache."""
        try:
            devices = sd.query_devices()
            self._device_info = {i: info for i, info in enumerate(devices)}
            logger.debug(f"Found {len(devices)} audio devices")
        except Exception as e:
            logger.error(f"Error querying audio devices: {e}")
            self._device_info = {}
            
    def get_input_devices(self) -> List[Dict]:
        """Get list of available input devices.
        
        Returns:
            List of input device information dictionaries
        """
        return [info for info in self._device_info.values() 
               if info.get("max_input_channels", 0) > 0]
               
    def get_output_devices(self) -> List[Dict]:
        """Get list of available output devices.
        
        Returns:
            List of output device information dictionaries
        """
        return [info for info in self._device_info.values() 
               if info.get("max_output_channels", 0) > 0]
               
    def set_input_device(self, device):
        """Set the input device.
        
        Args:
            device: Device ID, name, or index
        """
        if device in self._device_info:
            self._input_device = device
        else:
            # Try to find by name
            for idx, info in self._device_info.items():
                if info.get("name") == device:
                    self._input_device = idx
                    break
        
        logger.info(f"Set input device to: {self._get_device_name(self._input_device)}")
        
    def set_output_device(self, device):
        """Set the output device.
        
        Args:
            device: Device ID, name, or index
        """
        if device in self._device_info:
            self._output_device = device
        else:
            # Try to find by name
            for idx, info in self._device_info.items():
                if info.get("name") == device:
                    self._output_device = idx
                    break
                    
        logger.info(f"Set output device to: {self._get_device_name(self._output_device)}")
        
    def get_input_device(self):
        """Get the current input device.
        
        Returns:
            Current input device ID
        """
        return self._input_device
        
    def get_output_device(self):
        """Get the current output device.
        
        Returns:
            Current output device ID
        """
        return self._output_device
        
    def _get_device_name(self, device_id):
        """Get the name of a device by ID.
        
        Args:
            device_id: Device ID
            
        Returns:
            Device name or ID if not found
        """
        if device_id in self._device_info:
            return self._device_info[device_id].get("name", str(device_id))
        return str(device_id)
        
    def get_input_device_info(self) -> Optional[Dict]:
        """Get information about the current input device.
        
        Returns:
            Input device information or None
        """
        if self._input_device in self._device_info:
            return self._device_info[self._input_device]
        return None
        
    def get_output_device_info(self) -> Optional[Dict]:
        """Get information about the current output device.
        
        Returns:
            Output device information or None
        """
        if self._output_device in self._device_info:
            return self._device_info[self._output_device]
        return None
        
    async def shutdown(self):
        """Shut down the device manager."""
        logger.info("Audio device manager shutdown")
        return True
```

### 3. Voice Recognition System

The `VoiceRecognition` class will handle converting spoken audio into text using Whisper or similar speech recognition technology.

```python
# src/vpa/audio/voice_recognition.py
import sounddevice as sd
import numpy as np
import asyncio
import logging
import tempfile
import os
import wave
from typing import Dict, Optional, Any
import time

logger = logging.getLogger(__name__)

class VoiceRecognition:
    """Speech recognition for converting audio to text."""
    
    def __init__(self, device_manager, config=None):
        """Initialize speech recognition.
        
        Args:
            device_manager: Audio device manager
            config: Configuration dictionary
        """
        self._device_manager = device_manager
        self._config = config or {}
        
        # Recognition settings
        self._sample_rate = config.get("sample_rate", 16000)
        self._channels = config.get("channels", 1)
        self._dtype = config.get("dtype", "float32")
        self._threshold = config.get("threshold", 0.03)
        self._silence_duration = config.get("silence_duration", 1.0)
        self._max_duration = config.get("max_duration", 10.0)
        
        # State variables
        self._active = False
        self._recognizer = None
        self._stream = None
        self._buffer = []
        self._last_audio_time = 0
        self._recording = False
        
    async def initialize(self):
        """Initialize the speech recognition system."""
        try:
            # Import here to avoid loading unless needed
            import whisper
            
            # Initialize whisper model in a thread pool
            logger.info("Loading speech recognition model...")
            
            loop = asyncio.get_event_loop()
            model_name = self._config.get("model", "base")
            self._recognizer = await loop.run_in_executor(
                None,
                lambda: whisper.load_model(model_name)
            )
            
            logger.info(f"Speech recognition model '{model_name}' loaded")
            return True
        except ImportError as e:
            logger.error(f"Failed to import whisper: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize speech recognition: {e}")
            return False
            
    def activate(self):
        """Activate speech recognition."""
        if self._active:
            return
            
        self._active = True
        self._start_stream()
        logger.info("Speech recognition activated")
        
    def deactivate(self):
        """Deactivate speech recognition."""
        if not self._active:
            return
            
        self._active = False
        self._stop_stream()
        logger.info("Speech recognition deactivated")
        
    def is_active(self) -> bool:
        """Check if speech recognition is active.
        
        Returns:
            True if active, False otherwise
        """
        return self._active
        
    def _start_stream(self):
        """Start audio input stream."""
        if self._stream is not None:
            return
            
        device_info = self._device_manager.get_input_device_info()
        device_id = self._device_manager.get_input_device()
        
        if not device_info:
            logger.error("No input device available")
            return
            
        # Start audio stream
        try:
            self._stream = sd.InputStream(
                device=device_id,
                channels=self._channels,
                samplerate=self._sample_rate,
                dtype=self._dtype,
                callback=self._audio_callback
            )
            self._stream.start()
            logger.debug("Audio input stream started")
        except Exception as e:
            logger.error(f"Failed to start audio stream: {e}")
            self._stream = None
            
    def _stop_stream(self):
        """Stop audio input stream."""
        if self._stream is None:
            return
            
        try:
            self._stream.stop()
            self._stream.close()
            logger.debug("Audio input stream stopped")
        except Exception as e:
            logger.error(f"Error stopping audio stream: {e}")
            
        self._stream = None
        self._buffer = []
        self._recording = False
        
    def _audio_callback(self, indata, frames, time_info, status):
        """Process audio data from input stream.
        
        Args:
            indata: Audio input data
            frames: Number of frames
            time_info: Time information
            status: Status information
        """
        if status:
            logger.warning(f"Audio input status: {status}")
            
        # Calculate volume level
        volume = np.abs(indata).mean()
        
        # Check if we should start recording
        if not self._recording and volume > self._threshold:
            self._recording = True
            self._buffer = [indata.copy()]
            self._last_audio_time = time.time()
            logger.debug(f"Started recording (volume: {volume:.3f})")
        elif self._recording:
            # Continue recording
            self._buffer.append(indata.copy())
            
            # Update last audio time if there's meaningful audio
            if volume > self._threshold:
                self._last_audio_time = time.time()
                
            # Check if we should stop recording due to silence
            elapsed = time.time() - self._last_audio_time
            buffer_duration = len(self._buffer) * (frames / self._sample_rate)
            
            if elapsed > self._silence_duration or buffer_duration > self._max_duration:
                # Convert buffer to WAV file for recognition
                self._process_buffer()
                
    def _process_buffer(self):
        """Process the recorded audio buffer."""
        self._recording = False
        
        if not self._buffer:
            return
            
        # Combine buffer chunks
        audio_data = np.concatenate(self._buffer)
        self._buffer = []
        
        # Save to temporary WAV file for recognition
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
            
        try:
            with wave.open(temp_path, "wb") as wav_file:
                wav_file.setnchannels(self._channels)
                wav_file.setsampwidth(2)  # 16-bit audio
                wav_file.setframerate(self._sample_rate)
                
                # Convert to 16-bit PCM
                audio_int16 = (audio_data * 32767).astype(np.int16)
                wav_file.writeframes(audio_int16.tobytes())
                
            # Schedule recognition in the background
            asyncio.create_task(self._recognize_audio(temp_path))
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    async def _recognize_audio(self, audio_path):
        """Recognize speech in audio file.
        
        Args:
            audio_path: Path to audio file
        """
        try:
            # Run recognition in a thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._recognizer.transcribe(audio_path)
            )
            
            # Clean up temp file
            os.unlink(audio_path)
            
            # Extract results
            text = result.get("text", "").strip()
            
            if text:
                logger.info(f"Recognized: '{text}'")
                return {
                    "text": text,
                    "confidence": result.get("confidence", 1.0)
                }
            else:
                logger.debug("No speech recognized")
                return None
        except Exception as e:
            logger.error(f"Recognition error: {e}")
            # Clean up temp file
            if os.path.exists(audio_path):
                os.unlink(audio_path)
            return None
            
    async def process_audio_frame(self):
        """Process an audio frame.
        
        Returns:
            Recognition result or None if not ready
        """
        # This method is called periodically by AudioManager
        # We don't need to do anything here since processing happens 
        # in the audio callback and recognize_audio task
        return None
        
    async def shutdown(self):
        """Shut down speech recognition."""
        logger.info("Shutting down speech recognition")
        
        self.deactivate()
        self._recognizer = None
        
        return True
```

### 4. Voice Synthesis System

The `VoiceSynthesis` class will handle converting text into spoken audio using Edge TTS or a similar text-to-speech engine.

```python
# src/vpa/audio/voice_synthesis.py
import asyncio
import logging
import sounddevice as sd
import numpy as np
from typing import Dict, List, Optional, Any
import tempfile
import os
import wave

logger = logging.getLogger(__name__)

class VoiceSynthesis:
    """Text-to-speech for converting text to audio."""
    
    def __init__(self, device_manager, config=None):
        """Initialize text-to-speech.
        
        Args:
            device_manager: Audio device manager
            config: Configuration dictionary
        """
        self._device_manager = device_manager
        self._config = config or {}
        
        # TTS settings
        self._default_voice = config.get("default_voice", "en-US-AriaNeural")
        self._rate = config.get("rate", "+0%")
        self._volume = config.get("volume", "+0%")
        self._sample_rate = config.get("sample_rate", 24000)
        self._voices = {}
        
        # State variables
        self._speaking = False
        self._tts = None
        
    async def initialize(self):
        """Initialize text-to-speech."""
        try:
            # Import here to avoid loading unless needed
            import edge_tts
            
            self._tts = edge_tts
            
            # Get available voices
            voices = await edge_tts.VoicesManager.create()
            self._voices = {voice.get("ShortName"): voice for voice in voices.voices}
            
            logger.info(f"Text-to-speech initialized with {len(self._voices)} voices")
            return True
        except ImportError as e:
            logger.error(f"Failed to import edge_tts: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize text-to-speech: {e}")
            return False
            
    async def speak(self, text: str, voice: Optional[str] = None) -> bool:
        """Speak text using text-to-speech.
        
        Args:
            text: Text to speak
            voice: Voice to use (or default if None)
            
        Returns:
            True if successful
        """
        if not text or not self._tts:
            return False
            
        # Avoid speaking while already speaking
        if self._speaking:
            logger.debug("Already speaking, queuing new request")
            # Wait for current speech to finish
            while self._speaking:
                await asyncio.sleep(0.1)
                
        voice = voice or self._default_voice
        
        if voice not in self._voices:
            logger.warning(f"Voice {voice} not found, using default")
            voice = self._default_voice
            
        try:
            self._speaking = True
            
            # Set up TTS communicator
            communicator = self._tts.Communicate(
                text, 
                voice,
                rate=self._rate,
                volume=self._volume
            )
            
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                
            # Synthesize speech to file
            await communicator.save(temp_path)
            
            # Play the audio
            await self._play_audio(temp_path)
            
            # Clean up the temporary file
            os.unlink(temp_path)
            
            self._speaking = False
            return True
        except Exception as e:
            logger.error(f"Speech synthesis error: {e}")
            self._speaking = False
            return False
            
    async def _play_audio(self, file_path: str):
        """Play audio from a file.
        
        Args:
            file_path: Path to audio file
        """
        try:
            # Read the WAV file
            with wave.open(file_path, "rb") as wav_file:
                sample_width = wav_file.getsampwidth()
                channels = wav_file.getnchannels()
                sample_rate = wav_file.getframerate()
                frames = wav_file.readframes(wav_file.getnframes())
                
            # Convert to numpy array
            dtype = None
            if sample_width == 1:
                dtype = np.int8
            elif sample_width == 2:
                dtype = np.int16
            elif sample_width == 4:
                dtype = np.float32
                
            if not dtype:
                logger.error(f"Unsupported sample width: {sample_width}")
                return
                
            audio_data = np.frombuffer(frames, dtype=dtype)
            
            # Reshape for multiple channels
            if channels > 1:
                audio_data = audio_data.reshape(-1, channels)
                
            # Get output device
            device_id = self._device_manager.get_output_device()
            
            # Play audio
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: sd.play(audio_data, sample_rate, device=device_id)
            )
            
            # Wait for audio to finish
            await asyncio.get_event_loop().run_in_executor(
                None,
                sd.wait
            )
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            
    async def get_available_voices(self) -> List[Dict]:
        """Get available TTS voices.
        
        Returns:
            List of voice information dictionaries
        """
        return list(self._voices.values())
        
    async def shutdown(self):
        """Shut down text-to-speech."""
        logger.info("Shutting down text-to-speech")
        return True
```

### 5. Wake Word Detection

```python
# src/vpa/audio/wake_word.py
import numpy as np
import asyncio
import logging
from typing import Dict, List, Optional, Any
import sounddevice as sd
import time

logger = logging.getLogger(__name__)

class WakeWordDetector:
    """Detects wake words in audio."""
    
    def __init__(self, device_manager, config=None):
        """Initialize wake word detection.
        
        Args:
            device_manager: Audio device manager
            config: Configuration dictionary
        """
        self._device_manager = device_manager
        self._config = config or {}
        
        # Detection settings
        self._sample_rate = config.get("sample_rate", 16000)
        self._channels = config.get("channels", 1)
        self._dtype = config.get("dtype", "float32")
        self._threshold = config.get("threshold", 0.6)
        self._wake_words = config.get("wake_words", ["hey assistant"])
        
        # State variables
        self._active = False
        self._detector = None
        self._stream = None
        
    async def initialize(self):
        """Initialize wake word detection."""
        try:
            # Import here to avoid loading unless needed
            from porcupine import Porcupine
            
            # Initialize wake word detector in a thread pool
            logger.info("Loading wake word detection model...")
            
            loop = asyncio.get_event_loop()
            self._detector = await loop.run_in_executor(
                None,
                lambda: Porcupine(
                    keywords=self._wake_words,
                    sensitivities=[self._threshold] * len(self._wake_words)
                )
            )
            
            logger.info(f"Wake word detector initialized for: {', '.join(self._wake_words)}")
            return True
        except ImportError as e:
            logger.error(f"Failed to import wake word library: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize wake word detection: {e}")
            return False
            
    def activate(self):
        """Activate wake word detection."""
        if self._active:
            return
            
        self._active = True
        self._start_stream()
        logger.info("Wake word detection activated")
        
    def deactivate(self):
        """Deactivate wake word detection."""
        if not self._active:
            return
            
        self._active = False
        self._stop_stream()
        logger.info("Wake word detection deactivated")
        
    def is_active(self) -> bool:
        """Check if wake word detection is active.
        
        Returns:
            True if active, False otherwise
        """
        return self._active
        
    def _start_stream(self):
        """Start audio input stream for wake word detection."""
        if self._stream is not None:
            return
            
        device_info = self._device_manager.get_input_device_info()
        device_id = self._device_manager.get_input_device()
        
        if not device_info:
            logger.error("No input device available")
            return
            
        # Start audio stream
        try:
            self._stream = sd.InputStream(
                device=device_id,
                channels=self._channels,
                samplerate=self._sample_rate,
                dtype=self._dtype,
                callback=self._audio_callback
            )
            self._stream.start()
            logger.debug("Wake word detection stream started")
        except Exception as e:
            logger.error(f"Failed to start wake word detection stream: {e}")
            self._stream = None
            
    def _stop_stream(self):
        """Stop audio input stream."""
        if self._stream is None:
            return
            
        try:
            self._stream.stop()
            self._stream.close()
            logger.debug("Wake word detection stream stopped")
        except Exception as e:
            logger.error(f"Error stopping wake word detection stream: {e}")
            
        self._stream = None
        
    def _audio_callback(self, indata, frames, time_info, status):
        """Process audio data from input stream for wake word detection.
        
        Args:
            indata: Audio input data
            frames: Number of frames
            time_info: Time information
            status: Status information
        """
        if status:
            logger.warning(f"Audio input status: {status}")
            
        if not self._detector:
            return
            
        try:
            # Process audio frame for wake word detection
            pcm = np.frombuffer(indata, dtype=np.int16).squeeze()
            result = self._detector.process(pcm)
            
            if result >= 0:
                # Wake word detected
                wake_word = self._wake_words[result]
                logger.info(f"Wake word detected: {wake_word}")
                
                # Emit event in main thread
                asyncio.run_coroutine_threadsafe(
                    self._on_wake_word_detected(wake_word),
                    asyncio.get_event_loop()
                )
        except Exception as e:
            logger.error(f"Error processing audio for wake word: {e}")
            
    async def _on_wake_word_detected(self, wake_word):
        """Handle wake word detection.
        
        Args:
            wake_word: Detected wake word
        """
        from vpa.core.events import event_bus
        
        # Emit wake word event
        await event_bus.emit_async("wake_word_detected", {
            "wake_word": wake_word,
            "timestamp": time.time()
        })
        
    async def shutdown(self):
        """Shut down wake word detection."""
        logger.info("Shutting down wake word detection")
        
        self.deactivate()
        
        # Release detector resources
        if self._detector:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._detector.delete)
            self._detector = None
            
        return True
```

## Implementation Tasks

### Task 1: Environment Setup

1. **Verify Dependencies**
   - Install required packages:
   ```bash
   pip install sounddevice numpy whisper edge-tts porcupine
   ```
   - Ensure audio devices are properly configured
   - Test basic audio recording and playback

2. **Create Directory Structure**
   ```
   src/vpa/
   ├── audio/
   │   ├── __init__.py
   │   ├── audio_manager.py
   │   ├── device_manager.py
   │   ├── voice_recognition.py
   │   ├── voice_synthesis.py
   │   └── wake_word.py
   ```

### Task 2: Core Audio Components

1. **Audio Device Manager**
   - Implement device enumeration and selection
   - Create APIs for device listing and selection
   - Add persistence for device settings

2. **Voice Recognition Implementation**
   - Integrate Whisper for speech recognition
   - Implement audio buffering and processing
   - Add silence detection for end-of-speech

3. **Voice Synthesis Implementation**
   - Integrate Edge TTS for speech synthesis
   - Implement voice selection and configuration
   - Add audio playback capabilities

### Task 3: Integration with Event System

1. **Define Audio Events**
   - `wake_word_detected` - When wake word is recognized
   - `voice_command` - When speech is converted to text
   - `speak_text` - Request to speak text
   - `start_listening` - Request to start voice recognition
   - `stop_listening` - Request to stop voice recognition

2. **Event Handlers**
   - Implement handlers for all audio events
   - Connect to event bus from Phase 1

### Task 4: Testing and Validation

1. **Unit Tests**
   ```python
   # tests/unit/audio/test_voice_synthesis.py
   import pytest
   import asyncio
   from unittest.mock import patch, MagicMock
   from vpa.audio.voice_synthesis import VoiceSynthesis
   
   class TestVoiceSynthesis:
       @pytest.fixture
       def mock_device_manager(self):
           device_manager = MagicMock()
           device_manager.get_output_device.return_value = 0
           return device_manager
           
       @pytest.fixture
       async def voice_synthesis(self, mock_device_manager):
           synthesis = VoiceSynthesis(mock_device_manager)
           
           # Mock edge_tts
           synthesis._tts = MagicMock()
           synthesis._tts.Communicate.return_value = AsyncMock()
           synthesis._voices = {"en-US-AriaNeural": {"ShortName": "en-US-AriaNeural"}}
           
           yield synthesis
           await synthesis.shutdown()
           
       @pytest.mark.asyncio
       async def test_speak(self, voice_synthesis):
           # Arrange
           with patch.object(voice_synthesis, '_play_audio') as mock_play:
               mock_play.return_value = asyncio.Future()
               mock_play.return_value.set_result(None)
               
               # Act
               result = await voice_synthesis.speak("Hello world")
               
               # Assert
               assert result is True
               mock_play.assert_called_once()
               voice_synthesis._tts.Communicate.assert_called_once()
   ```

2. **Integration Tests**
   ```python
   # tests/integration/test_audio_system.py
   import pytest
   import asyncio
   from vpa.audio.audio_manager import AudioManager
   from vpa.core.events import event_bus
   
   class TestAudioSystem:
       @pytest.fixture
       async def audio_manager(self):
           # Create manager with test configuration
           manager = AudioManager({
               "synthesis": {
                   "default_voice": "en-US-AriaNeural"
               }
           })
           
           await manager.initialize()
           yield manager
           await manager.shutdown()
           
       @pytest.mark.asyncio
       async def test_speak_text_event(self, audio_manager):
           # Arrange
           test_complete = asyncio.Future()
           
           # Mock the speak method
           original_speak = audio_manager._voice_synthesis.speak
           
           async def mock_speak(text, voice=None):
               assert text == "Test message"
               test_complete.set_result(True)
               return True
               
           audio_manager._voice_synthesis.speak = mock_speak
           
           # Act
           event_bus.emit("speak_text", {
               "text": "Test message"
           })
           
           # Wait for processing
           result = await asyncio.wait_for(test_complete, timeout=2.0)
           
           # Assert
           assert result is True
           
           # Restore original method
           audio_manager._voice_synthesis.speak = original_speak
   ```

3. **Performance Testing**
   ```python
   # tests/performance/test_audio_performance.py
   import pytest
   import asyncio
   import time
   from vpa.audio.voice_synthesis import VoiceSynthesis
   from vpa.audio.device_manager import AudioDeviceManager
   
   class TestAudioPerformance:
       @pytest.fixture
       async def voice_synthesis(self):
           # Create real components for performance testing
           device_manager = AudioDeviceManager()
           await device_manager.initialize()
           
           synthesis = VoiceSynthesis(device_manager)
           await synthesis.initialize()
           
           yield synthesis
           
           await synthesis.shutdown()
           await device_manager.shutdown()
           
       @pytest.mark.asyncio
       async def test_synthesis_performance(self, voice_synthesis):
           # Prepare test phrases
           phrases = [
               "Hello world",
               "This is a test of the speech synthesis system",
               "The quick brown fox jumps over the lazy dog",
               "Testing speech synthesis performance"
           ]
           
           durations = []
           
           # Test each phrase
           for phrase in phrases:
               start_time = time.time()
               await voice_synthesis.speak(phrase)
               duration = time.time() - start_time
               durations.append(duration)
               print(f"Phrase: '{phrase}' - Time: {duration:.3f}s")
               
           # Calculate statistics
           avg_time = sum(durations) / len(durations)
           max_time = max(durations)
           min_time = min(durations)
           
           print(f"\nSynthesis Performance:")
           print(f"  Average: {avg_time:.3f}s")
           print(f"  Min: {min_time:.3f}s")
           print(f"  Max: {max_time:.3f}s")
           
           # Assert performance target (adjust as needed)
           assert avg_time < 3.0, f"Average synthesis time ({avg_time:.3f}s) exceeds target (3.0s)"
   ```

## Integration with Phase 1

The audio system must integrate seamlessly with the core architecture established in Phase 1:

```python
# src/vpa/core/app.py (modified to include audio)
from vpa.core.events import event_bus
from vpa.core.plugins import PluginManager
from vpa.audio.audio_manager import AudioManager
import asyncio
import logging

logger = logging.getLogger(__name__)

class ApplicationManager:
    """Application manager for the VPA."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
        
    def __init__(self, config=None):
        """Initialize the application manager.
        
        Args:
            config: Application configuration
        """
        if hasattr(self, "_initialized"):
            return
            
        self._config = config or {}
        self._plugin_manager = PluginManager()
        self._audio_manager = AudioManager(config.get("audio", {}))
        self._running = False
        self._initialized = False
        
    async def initialize(self):
        """Initialize the application.
        
        Returns:
            True if initialization succeeded
        """
        if self._initialized:
            return True
            
        logger.info("Initializing application")
        
        # Initialize audio system
        if not await self._audio_manager.initialize():
            logger.error("Failed to initialize audio system")
            return False
            
        # Initialize plugin manager
        if not await self._plugin_manager.initialize(self._config.get("plugins", {})):
            logger.error("Failed to initialize plugin manager")
            return False
            
        # Subscribe to voice command events
        event_bus.subscribe("voice_command", self._on_voice_command, async_callback=True)
        
        self._initialized = True
        logger.info("Application initialized")
        return True
        
    async def start(self):
        """Start the application."""
        if self._running:
            return
            
        logger.info("Starting application")
        self._running = True
        
        # Start audio system
        await self._audio_manager.start()
        
        # Start plugins
        await self._plugin_manager.start()
        
        logger.info("Application started")
        
    async def stop(self):
        """Stop the application."""
        if not self._running:
            return
            
        logger.info("Stopping application")
        self._running = False
        
        # Stop audio system
        await self._audio_manager.stop()
        
        # Stop plugins
        await self._plugin_manager.stop()
        
        logger.info("Application stopped")
        
    async def _on_voice_command(self, event_data):
        """Handle voice command events."""
        text = event_data.get("text", "")
        confidence = event_data.get("confidence", 0)
        
        if text:
            logger.info(f"Processing voice command: '{text}' (confidence: {confidence:.2f})")
            
            # Process command through plugin manager
            response = await self._plugin_manager.process_input(text, {"source": "voice"})
            
            # Speak response if available
            if response and "text" in response:
                await event_bus.emit_async("speak_text", {"text": response["text"]})
                
    async def shutdown(self):
        """Shut down the application."""
        logger.info("Shutting down application")
        
        # Stop application if running
        if self._running:
            await self.stop()
            
        # Unsubscribe from events
        event_bus.unsubscribe("voice_command", self._on_voice_command)
        
        # Shut down components
        await self._audio_manager.shutdown()
        await self._plugin_manager.shutdown()
        
        self._initialized = False
        logger.info("Application shut down complete")
        
    def is_running(self):
        """Check if the application is running."""
        return self._running
```

## Performance Targets

The audio system must meet the following performance targets:

1. **Voice Recognition**
   - Recognition latency: < 3 seconds for normal phrases
   - Accuracy: > 90% for standard speech in quiet environment
   - Resource usage: < 500MB memory during recognition

2. **Voice Synthesis**
   - Synthesis latency: < 2 seconds for standard phrases
   - Audio quality: Clear and natural sounding speech
   - Resource usage: < 300MB memory during synthesis

3. **Wake Word Detection**
   - Detection accuracy: > 95% for configured wake words
   - False positive rate: < 1 per hour
   - Resource usage: < 150MB continuous usage

## Risk Management

1. **Dependency Risks**
   - Whisper and Edge TTS are third-party dependencies
   - Mitigation: Implement adapter pattern for easy replacement

2. **Performance Risks**
   - Speech recognition may be slow on low-end hardware
   - Mitigation: Implement configurable model sizes and optimization

3. **Integration Risks**
   - Audio system must work seamlessly with Phase 1 components
   - Mitigation: Thorough integration testing and event-based communication

## Success Criteria

Phase 2 will be considered complete when:

1. Users can interact with the VPA using voice commands
2. The system can respond with natural-sounding speech
3. All performance targets are met
4. Unit and integration tests are passing
5. Documentation is complete and up-to-date

## Timeline

- **Week 1**: Environment setup and core audio components
- **Week 2**: Voice recognition and synthesis implementation
- **Week 3**: Integration with event system and testing
- **Week 4**: Performance optimization and documentation

## Conclusion

Phase 2 focuses on building the audio system that will enable voice interaction with the VPA. By implementing high-quality speech recognition and synthesis capabilities, the system will become more accessible and natural to use. The audio system integrates with the core architecture established in Phase 1, following the same event-driven design patterns for consistency and modularity.

---

*Document created: August 29, 2025*
