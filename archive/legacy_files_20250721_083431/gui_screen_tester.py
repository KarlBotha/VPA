#!/usr/bin/env python3
"""
VPA GUI Screen Tester
Test individual GUI screens for user review and feedback
"""

import sys
import os
from pathlib import Path
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import json
import time
import threading
import asyncio
import tempfile
import uuid

# Add src to path
current_dir = Path(__file__).resolve().parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

class MockGUIManager:
    """Mock GUI manager for testing with production audio system"""
    
    def __init__(self):
        self.gui_config = MockGUIConfig()
        self.current_theme = "dark"
        self.auth_coordinator = MockAuthCoordinator()
        self.llm_manager = MockLLMManager()
        
        # Initialize production audio system
        try:
            from src.vpa.core.enhanced_audio_gui import VPAEnhancedAudioManager
            self.audio_manager = VPAEnhancedAudioManager()
            print("✅ Production audio system initialized")
        except ImportError as e:
            print(f"❌ Failed to load production audio system: {e}")
            self.audio_manager = MockAudioManager()
            
        self.settings = self._load_settings()
    
    def _load_settings(self):
        """Load settings from file"""
        try:
            settings_file = os.path.join(os.path.expanduser("~"), ".vpa_settings.json")
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    print(f"✅ Loaded settings from {settings_file}")
                    return settings
        except Exception as e:
            print(f"❌ Failed to load settings: {e}")
        
        # Default settings
        return {
            "theme": "dark",
            "auto_login": True,
            "voice_enabled": True,
            "notifications": True,
            "current_voice": "Emma",
            "microphone_enabled": True,
            "volume": 0.8,
            "speech_rate": 200
        }
    
    def _save_settings(self):
        """Save settings to file"""
        try:
            settings_file = os.path.join(os.path.expanduser("~"), ".vpa_settings.json")
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            print(f"✅ Settings saved to {settings_file}")
        except Exception as e:
            print(f"❌ Failed to save settings: {e}")
    
    def get_current_settings(self):
        return self.settings.copy()
    
    def update_setting(self, key, value):
        """Update a setting and save to file"""
        self.settings[key] = value
        self._save_settings()
        print(f"🔧 Setting updated: {key} = {value}")
    
    def change_theme(self, theme):
        self.current_theme = theme
        self.update_setting("theme", theme)
        ctk.set_appearance_mode(theme)
    
    def process_user_message(self, message):
        """Process user message through LLM and return response"""
        print(f"🔄 Processing message through LLM: {message}")
        
        # Use the LLM manager to generate response
        response = self.llm_manager.process_message(message)
        
        # Speak the response using TTS (only if voice is enabled)
        if self.settings.get("voice_enabled", True) and self.audio_manager and hasattr(self.audio_manager, 'speak_response'):
            try:
                self.audio_manager.speak_response(response)
            except Exception as e:
                print(f"⚠️ TTS failed for response: {e}")
        
        return response

class MockAuthCoordinator:
    """Mock authentication coordinator"""
    
    def __init__(self):
        self.auth_manager = MockAuthManager()
    
    async def authenticate_user(self, username, password):
        print(f"Mock authenticating user: {username}")
        return MockAuthResult(success=True, user_id="test_user")

class MockAuthManager:
    """Mock authentication manager"""
    
    def register_user(self, username, email, password):
        print(f"Mock registering user: {username}, {email}")
        return MockAuthResult(success=True, user_id="test_user")

class MockAuthResult:
    """Mock authentication result"""
    
    def __init__(self, success=True, user_id=None, error=None):
        self.success = success
        self.user_id = user_id
        self.error = error

class MockLLMManager:
    """Enhanced LLM manager with Ollama support"""
    
    def __init__(self):
        self.current_provider = "ollama"  # Default to Ollama since user has it
        self.available_providers = ["openai", "anthropic", "google", "ollama", "local"]
        self.current_model = "llama3:latest"  # Default to your available model
        self.ollama_available = False
        self._test_ollama_connection()
    
    def _test_ollama_connection(self):
        """Test connection to local Ollama instance"""
        try:
            import ollama
            # Test if Ollama service is running
            response = ollama.list()
            
            # Handle different response formats
            models = []
            if hasattr(response, 'models'):
                # Response object with models attribute
                models = response.models
                self.available_models = []
                for model in models:
                    if hasattr(model, 'model'):
                        self.available_models.append(model.model)
                    elif hasattr(model, 'name'):
                        self.available_models.append(model.name)
                    else:
                        self.available_models.append(str(model))
            elif isinstance(response, dict) and 'models' in response:
                # Dictionary response
                models = response['models']
                self.available_models = [model['name'] for model in models]
            
            if models and self.available_models:
                self.ollama_available = True
                print(f"✅ Ollama connected! Available models: {self.available_models}")
                
                # Look for llama3 or similar models
                llama_models = [m for m in self.available_models if m and 'llama' in m.lower()]
                if llama_models:
                    self.current_model = llama_models[0]
                    print(f"📝 Using Llama model: {self.current_model}")
                elif self.available_models:
                    self.current_model = self.available_models[0]
                    print(f"📝 Using first available model: {self.current_model}")
            else:
                print("⚠️ Ollama running but no models found")
                self.ollama_available = False
                
        except ImportError:
            print("❌ Ollama package not installed")
            self.ollama_available = False
        except Exception as e:
            print(f"❌ Ollama connection failed: {e}")
            print("💡 Make sure Ollama is running with: 'ollama serve'")
            self.ollama_available = False
    
    def generate_response(self, message):
        return f"Mock AI response to: {message}"
    
    def process_message(self, message):
        """Process message with real Ollama or fallback to mock"""
        import time
        
        # Try Ollama first if available
        if self.ollama_available and self.current_provider == "ollama":
            try:
                import ollama
                print(f"🤖 Processing with Ollama model: {self.current_model}")
                
                response = ollama.chat(model=self.current_model, messages=[
                    {
                        'role': 'user',
                        'content': message,
                    },
                ])
                
                return response['message']['content']
                
            except Exception as e:
                print(f"❌ Ollama error: {e}")
                return f"Sorry, there was an error with Ollama: {str(e)}. Falling back to mock response."
        
        # Fallback to intelligent mock response
        time.sleep(1)  # Simulate processing time
        return self._generate_intelligent_response(message)
    
    def _generate_intelligent_response(self, message):
        """Generate more intelligent mock responses"""
        message_lower = message.lower()
        
        if "hello" in message_lower or "hi" in message_lower:
            return "Hello! I'm VPA, your virtual personal assistant. How can I help you today?"
        elif "how are you" in message_lower:
            return "I'm doing well, thank you for asking! I'm here and ready to assist you with any questions or tasks."
        elif "what can you do" in message_lower or "help" in message_lower and "with" in message_lower:
            return "I can help you with many things including:\n• Answering questions and providing information\n• Weather updates (through integrations)\n• Time and date information\n• General knowledge questions\n• Writing and communication assistance\n• Calculations and problem-solving\n• And much more! What would you like help with?"
        elif "weather" in message_lower:
            return "I can help you with weather information! To get accurate weather data, I would need access to weather services through the integrations in Settings → Addons tab."
        elif "time" in message_lower:
            from datetime import datetime
            current_time = datetime.now().strftime("%I:%M %p")
            return f"The current time is {current_time}."
        elif "sky" in message_lower and "blue" in message_lower:
            return "The sky appears blue due to a phenomenon called Rayleigh scattering. When sunlight enters Earth's atmosphere, it collides with gas molecules. Blue light has a shorter wavelength and gets scattered more than other colors, making the sky appear blue to our eyes!"
        elif "sun" in message_lower:
            return "The Sun is our nearest star, located about 93 million miles (150 million km) from Earth. It's a massive ball of hot gas that provides the light and heat that makes life possible on our planet!"
        elif "earth" in message_lower or "planet" in message_lower:
            return "Earth is the third planet from the Sun and the only known planet with life. It's about 4.5 billion years old and has a diameter of approximately 7,918 miles (12,742 km)."
        elif "calculate" in message_lower or "math" in message_lower or any(op in message_lower for op in ['+', '-', '*', '/', 'plus', 'minus', 'times', 'divided']):
            return "I can help with calculations! Please provide the specific math problem you'd like me to solve, and I'll work through it step by step."
        elif "thank" in message_lower:
            return "You're very welcome! I'm always happy to help. Is there anything else you'd like to know or discuss?"
        elif "bye" in message_lower or "goodbye" in message_lower:
            return "Goodbye! It was great chatting with you. Feel free to come back anytime if you need assistance!"
        else:
            # Provide a more helpful generic response
            return f"I understand you're asking about '{message}'. While I'm currently running in demo mode, I'm designed to help with a wide variety of questions and tasks. Could you rephrase your question or ask me something specific like explaining concepts, providing information, or helping with calculations?"
    
    def get_available_providers(self):
        """Get available providers with Ollama status"""
        providers = self.available_providers.copy()
        if self.ollama_available:
            return providers
        else:
            # Remove ollama from list if not available
            return [p for p in providers if p != "ollama"]
    
    def get_available_models(self):
        """Get available models for current provider"""
        if self.current_provider == "ollama" and self.ollama_available:
            return self.available_models
        else:
            return ["mock-model"]
    
    def set_provider(self, provider):
        """Set the current provider"""
        self.current_provider = provider
        print(f"📡 Provider changed to: {provider}")
        
        if provider == "ollama" and not self.ollama_available:
            print("⚠️ Ollama not available, falling back to mock")
            self.current_provider = "mock"
    
    def set_model(self, model):
        """Set the current model"""
        self.current_model = model
        print(f"🔧 Model changed to: {model}")

class MockAudioManager:
    """Enhanced audio manager with real microphone support"""
    
    def __init__(self):
        self.recording = False
        self.voice_enabled = True
        self.microphone_enabled = True  # Add microphone enable/disable control
        self.current_voice = "emma"  # Default to Emma, will be updated from settings
        self.voices = self._create_mock_voices()
        self.audio_data = None
        self.recorded_audio = None
        
        # Try to import local audio libraries (no cloud dependencies)
        try:
            import speech_recognition as sr
            import threading
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.real_audio = True
            self.recording_thread = None
            print("✅ Local microphone support enabled (no cloud services)")
        except ImportError:
            self.recognizer = None
            self.microphone = None
            self.real_audio = False
            print("❌ Using mock audio (install speech_recognition for real microphone)")
    
    def _create_mock_voices(self):
        """Create the 13 high-quality voices from reference documents"""
        return {
            "male": [
                {"id": "andrew", "name": "Andrew", "gender": "male", "engine": "edge-tts", "voice_id": "en-US-AndrewNeural", "description": "Confident male voice"},
                {"id": "christopher", "name": "Christopher", "gender": "male", "engine": "edge-tts", "voice_id": "en-US-ChristopherNeural", "description": "Clear male voice"},
                {"id": "guy", "name": "Guy", "gender": "male", "engine": "edge-tts", "voice_id": "en-US-GuyNeural", "description": "Natural male voice"},
                {"id": "roger", "name": "Roger", "gender": "male", "engine": "edge-tts", "voice_id": "en-US-RogerNeural", "description": "Deep male voice"},
                {"id": "eric", "name": "Eric", "gender": "male", "engine": "edge-tts", "voice_id": "en-US-EricNeural", "description": "Friendly male voice"},
                {"id": "steffan", "name": "Steffan", "gender": "male", "engine": "edge-tts", "voice_id": "en-US-SteffanNeural", "description": "Mature male voice"}
            ],
            "female": [
                {"id": "emma", "name": "Emma", "gender": "female", "engine": "edge-tts", "voice_id": "en-US-EmmaNeural", "description": "Confident female voice"},
                {"id": "ava", "name": "Ava", "gender": "female", "engine": "edge-tts", "voice_id": "en-US-AvaNeural", "description": "Friendly female voice"},
                {"id": "aria", "name": "Aria", "gender": "female", "engine": "edge-tts", "voice_id": "en-US-AriaNeural", "description": "Natural female voice"},
                {"id": "jenny", "name": "Jenny", "gender": "female", "engine": "edge-tts", "voice_id": "en-US-JennyNeural", "description": "Warm female voice"},
                {"id": "libby", "name": "Libby", "gender": "female", "engine": "edge-tts", "voice_id": "en-GB-LibbyNeural", "description": "British female voice"},
                {"id": "michelle", "name": "Michelle", "gender": "female", "engine": "edge-tts", "voice_id": "en-US-MichelleNeural", "description": "Professional female voice"}
            ],
            "system": [
                {"id": "default", "name": "Default", "gender": "system", "engine": "pyttsx3", "voice_id": "system_default", "description": "Default system voice"}
            ]
        }
    
    def get_voices(self):
        return self.voices
    
    def set_voice(self, voice_id):
        """Set the current voice"""
        self.current_voice = voice_id
        print(f"🔊 Voice changed to: {voice_id}")
    
    def set_microphone_enabled(self, enabled):
        """Enable or disable microphone input"""
        self.microphone_enabled = enabled
        status = "enabled" if enabled else "disabled"
        print(f"🎤 Microphone {status}")
    
    def get_current_voice_from_settings(self):
        """Load the current voice from settings file"""
        try:
            import json
            import os
            settings_file = os.path.join(os.path.expanduser("~"), ".vpa_settings.json")
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    voice = settings.get("current_voice", "Emma")
                    voice_id = voice.lower()
                    self.current_voice = voice_id
                    print(f"🔊 Loaded voice from settings: {voice} -> {voice_id}")
                    return voice_id
        except Exception as e:
            print(f"❌ Failed to load voice settings: {e}")
        
        # Default fallback
        self.current_voice = "emma"
        return "emma"
    
    def test_voice(self, voice_id, text="Hello! This is a test of the voice system. Can you hear me clearly?"):
        """Test voice with actual TTS playback - only loads the specific voice"""
        print(f"🔊 Testing voice {voice_id}: {text}")
        
        try:
            # Get the specific voice configuration only
            voice_config = self._get_voice_config_by_id(voice_id)
            
            if not voice_config:
                print(f"❌ Voice {voice_id} not found")
                messagebox.showerror("Voice Test", f"Voice {voice_id} not found")
                return
            
            print(f"✅ Found voice: {voice_config['name']} ({voice_config['voice_id']})")
            
            # Generate and play TTS audio for this specific voice only
            self._generate_and_play_tts(voice_config, text)
            
        except Exception as e:
            print(f"❌ Voice test failed: {e}")
            messagebox.showerror("Voice Test Error", f"Voice test failed: {str(e)}")
    
    def _generate_and_play_tts(self, voice_config, text):
        """Generate TTS audio and play it"""
        try:
            import asyncio
            import tempfile
            import os
            import threading
            
            def tts_task():
                try:
                    if voice_config['engine'] == 'edge-tts':
                        # Use Edge TTS for high-quality voices
                        asyncio.run(self._edge_tts_generate(voice_config, text))
                    else:
                        # Use pyttsx3 for system default
                        self._pyttsx3_generate(voice_config, text)
                except Exception as e:
                    print(f"❌ TTS generation failed: {e}")
            
            # Run TTS in separate thread
            tts_thread = threading.Thread(target=tts_task)
            tts_thread.daemon = True
            tts_thread.start()
            
        except Exception as e:
            print(f"❌ TTS setup failed: {e}")
            messagebox.showerror("TTS Error", f"Text-to-speech failed: {str(e)}")
    
    async def _edge_tts_generate(self, voice_config, text):
        """Generate speech using Edge TTS"""
        try:
            import edge_tts
            import pygame
            import tempfile
            import os
            import asyncio
            
            # Initialize pygame mixer if not done
            try:
                pygame.mixer.init()
            except:
                pass
            
            # Generate TTS audio
            voice_id = voice_config['voice_id']
            communicate = edge_tts.Communicate(text, voice_id)
            
            # Save to temporary file with proper error handling
            import tempfile
            import os
            
            # Create temp directory if it doesn't exist
            temp_dir = tempfile.gettempdir()
            os.makedirs(temp_dir, exist_ok=True)
            
            # Create a unique filename
            import uuid
            temp_filename = f"vpa_tts_{uuid.uuid4().hex[:8]}.mp3"
            temp_path = os.path.join(temp_dir, temp_filename)
            
            try:
                # Generate audio file
                await communicate.save(temp_path)
                
                # Verify file exists and has content
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                    # Play audio
                    try:
                        pygame.mixer.music.load(temp_path)
                        pygame.mixer.music.play()
                        
                        print(f"🔊 Playing TTS with voice: {voice_config['name']}")
                        
                        # Wait for playback to finish
                        while pygame.mixer.music.get_busy():
                            await asyncio.sleep(0.1)
                        
                        print(f"✅ TTS playback completed for voice: {voice_config['name']}")
                        
                    except Exception as e:
                        print(f"❌ Audio playback failed: {e}")
                        # Fallback to system voice
                        self._pyttsx3_generate(voice_config, text)
                else:
                    print(f"❌ TTS file was not created properly: {temp_path}")
                    self._pyttsx3_generate(voice_config, text)
                    
            except Exception as save_error:
                print(f"❌ TTS file generation failed: {save_error}")
                self._pyttsx3_generate(voice_config, text)
            finally:
                # Clean up temp file (with delay to avoid file locks)
                def cleanup_file():
                    import time
                    time.sleep(1)  # Wait for playback to fully complete
                    try:
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                    except Exception as e:
                        pass  # Ignore cleanup errors
                
                import threading
                threading.Thread(target=cleanup_file, daemon=True).start()
                        
        except ImportError:
            print("❌ Edge TTS not available, falling back to system voice")
            self._pyttsx3_generate(voice_config, text)
        except Exception as e:
            print(f"❌ Edge TTS failed: {e}")
            # Fallback to system voice
            self._pyttsx3_generate(voice_config, text)
    
    def _pyttsx3_generate(self, voice_config, text):
        """Generate speech using pyttsx3 (system default)"""
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            engine.setProperty('rate', 200)
            engine.setProperty('volume', 1.0)
            
            # Get available voices and select one
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[0].id)
            
            print(f"🔊 Playing TTS with system voice: {voice_config['name']}")
            engine.say(text)
            engine.runAndWait()
            
        except Exception as e:
            print(f"❌ pyttsx3 TTS failed: {e}")
            messagebox.showinfo("Voice Test", f"Testing voice: {voice_config['name']}\nText: {text}")

    def speak_response(self, text, voice_id=None):
        """Speak a response using the selected voice only"""
        # Get voice from settings if not provided
        if not voice_id:
            voice_id = self.get_current_voice_from_settings()
            
        print(f"🔊 Speaking response with voice {voice_id}: {text[:50]}...")
        
        try:
            # Find the specific voice config for the selected voice only
            voice_config = self._get_voice_config_by_id(voice_id)
            
            if voice_config:
                print(f"✅ Using voice: {voice_config['name']} ({voice_config['voice_id']})")
                self._generate_and_play_tts(voice_config, text)
            else:
                print(f"❌ Voice {voice_id} not found, using default")
                # Use Emma as fallback
                emma_config = self._get_voice_config_by_id("emma")
                if emma_config:
                    self._generate_and_play_tts(emma_config, text)
                else:
                    print(f"❌ No voices available for response")
                
        except Exception as e:
            print(f"❌ Failed to speak response: {e}")
    
    def _get_voice_config_by_id(self, voice_id):
        """Get voice configuration for a specific voice ID"""
        for category in self.voices.values():
            for voice in category:
                if voice['id'] == voice_id:
                    return voice
        return None
    
    def start_recording(self):
        """Start real microphone recording only if microphone is enabled"""
        if not self.microphone_enabled:
            print("🎤 Microphone is disabled, cannot start recording")
            return
            
        self.recording = True
        self.recorded_audio = None
        
        if self.real_audio:
            try:
                import threading
                print("🎤 Starting real microphone recording...")
                
                def record_audio():
                    try:
                        with self.microphone as source:
                            # Adjust for ambient noise with longer duration
                            print("🔧 Calibrating microphone for ambient noise...")
                            self.recognizer.adjust_for_ambient_noise(source, duration=2)
                            
                            # More flexible listening parameters
                            print("🔊 Listening... speak now! (You have 10 seconds)")
                            
                            # Increased timeout and phrase limits for better capture
                            audio = self.recognizer.listen(
                                source, 
                                timeout=10,           # Wait up to 10 seconds for speech to start
                                phrase_time_limit=8   # Allow up to 8 seconds of continuous speech
                            )
                            self.recorded_audio = audio
                            print("📝 Audio captured successfully")
                    except Exception as e:
                        print(f"❌ Recording error: {e}")
                        self.recorded_audio = None
                
                # Start recording in a separate thread
                self.recording_thread = threading.Thread(target=record_audio)
                self.recording_thread.daemon = True
                self.recording_thread.start()
                
                return True
            except Exception as e:
                print(f"❌ Failed to start real recording: {e}")
                print("📱 Falling back to mock recording...")
        
        print("🎤 Started mock recording...")
        return True

    def stop_recording(self):
        """Stop recording (basic method)"""
        self.recording = False
        print("⏹️ Stopped recording...")
        return "Mock transcribed text from recording"

    def stop_recording_and_transcribe(self):
        """Stop recording and return transcribed text using LOCAL Whisper"""
        self.recording = False
        
        if self.real_audio and self.recorded_audio:
            try:
                print("🔄 Transcribing captured audio with local Whisper...")
                
                # Wait for recording thread to complete
                if self.recording_thread and self.recording_thread.is_alive():
                    self.recording_thread.join(timeout=2)
                
                if self.recorded_audio:
                    try:
                        # Save audio to temporary file for Whisper
                        import tempfile
                        import wave
                        import whisper
                        import os
                        
                        # Save recorded audio to a temporary wav file
                        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                            temp_path = tmp_file.name
                            
                        try:
                            with wave.open(temp_path, 'wb') as wav_file:
                                wav_file.setnchannels(1)
                                wav_file.setsampwidth(2)
                                wav_file.setframerate(16000)
                                wav_file.writeframes(self.recorded_audio.get_wav_data())
                            
                            # Use local Whisper model for transcription
                            print("🤖 Loading Whisper model for transcription...")
                            model = whisper.load_model("tiny")  # Use tiny model for faster processing
                            result = model.transcribe(temp_path)
                            text = result["text"].strip()
                            
                            print(f"✅ Transcribed with Whisper: '{text}'")
                            return text
                            
                        finally:
                            # Clean up temporary file
                            try:
                                os.unlink(temp_path)
                            except:
                                pass
                            
                    except ImportError:
                        print("❌ Whisper not installed. Install with: pip install openai-whisper")
                        return "Error: Whisper transcription library not available. Please install openai-whisper to use voice recording."
                    except Exception as whisper_error:
                        print(f"⚠️ Whisper transcription failed: {whisper_error}")
                        # Fallback to basic test message
                        return "Audio was captured but transcription failed. Using fallback: Hello assistant, I want to test the voice system."
                else:
                    print("❌ No audio was captured during recording")
                    return "Sorry, no audio was captured. Please try speaking louder or check your microphone settings."
                
            except Exception as e:
                print(f"❌ Audio processing failed: {e}")
                return "Audio recording failed due to technical error. Please try again."
        
        elif self.real_audio and not self.recorded_audio:
            print("❌ No audio was recorded - possible microphone issue")
            return "No audio detected. Please check that your microphone is working and not muted, then try again."
        
        else:
            print("⏹️ Using local text input fallback...")
            # Return a test message so user can proceed
            return "Voice recording system in test mode. Using fallback: Hello assistant, I want to test the system."
    
    def is_recording(self):
        return self.recording

class MockGUIConfig:
    """Mock GUI configuration"""
    
    def __init__(self):
        self.fonts = {
            "heading": ("Segoe UI", 18, "bold"),
            "subheading": ("Segoe UI", 14, "bold"),
            "body": ("Segoe UI", 12),
            "small": ("Segoe UI", 10)
        }

class VPAGUIScreenTester:
    """GUI Screen Tester for user review"""
    
    def __init__(self):
        # Setup CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create root window
        self.root = ctk.CTk()
        self.root.title("VPA GUI Screen Tester")
        self.root.geometry("400x600")
        
        # Center window
        self._center_window()
        
        # Create launcher UI
        self._create_launcher_ui()
    
    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_launcher_ui(self):
        """Create the launcher UI"""
        # Main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="VPA GUI Screen Tester",
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Test each screen for user review",
            font=("Arial", 14)
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Screen test buttons
        screens = [
            ("1. Registration Screen", self._test_registration),
            ("2. Login Screen", self._test_login),
            ("3. Main Application", self._test_main_app),
            ("4. Settings Window", self._test_settings),
            ("5. OAuth Setup", self._test_oauth_setup),
        ]
        
        for screen_name, command in screens:
            button = ctk.CTkButton(
                main_frame,
                text=screen_name,
                command=command,
                width=300,
                height=50,
                font=("Arial", 14, "bold")
            )
            button.pack(pady=10)
        
        # Instructions
        instructions = ctk.CTkTextbox(main_frame, height=100, width=350)
        instructions.pack(pady=(20, 0))
        instructions.insert("0.0", 
            "Instructions:\n"
            "1. Click each button to test the corresponding screen\n"
            "2. Provide feedback on look, feel, and functionality\n"
            "3. We'll proceed when you're satisfied with each screen"
        )
        instructions.configure(state="disabled")
    
    def _test_registration(self):
        """Test registration screen"""
        try:
            from vpa.gui.registration_window import VPARegistrationWindow
            gui_manager = MockGUIManager()
            registration_window = VPARegistrationWindow(self.root, gui_manager)
            messagebox.showinfo("Screen Test", "Registration screen opened! Please review and provide feedback.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open registration screen: {e}")
    
    def _test_login(self):
        """Test login screen"""
        try:
            from vpa.gui.ultra_simple_login import VPAUltraSimpleLogin
            gui_manager = MockGUIManager()
            login_window = VPAUltraSimpleLogin(self.root, gui_manager)
            messagebox.showinfo("Screen Test", "Ultra-simple login screen opened!\n\nThis version focuses on VPA account login only.\nOAuth integrations moved to Settings > Integrations.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open login screen: {e}")
    
    def _test_main_app(self):
        """Test main application window"""
        try:
            from vpa.gui.main_application import VPAMainApplication
            gui_manager = MockGUIManager()
            
            # Check LLM status and show appropriate message
            if gui_manager.llm_manager.ollama_available:
                print(f"🎯 Ollama detected with models: {gui_manager.llm_manager.available_models}")
                print(f"🔧 Current model: {gui_manager.llm_manager.current_model}")
                messagebox.showinfo("LLM Ready", f"✅ Ollama Connected!\n\nAvailable models:\n{', '.join(gui_manager.llm_manager.available_models)}\n\nCurrent model: {gui_manager.llm_manager.current_model}\n\nYou can change models in Settings → LLM Selection")
            else:
                from vpa.core.llm_auto_setup import show_llm_setup_wizard
                messagebox.showinfo("LLM Setup", "No LLM detected! Opening LLM Setup Wizard...")
                show_llm_setup_wizard()
            
            main_app = VPAMainApplication(self.root, gui_manager, "test_user", "test_session")
            
            # Don't auto-close - let user interact
            messagebox.showinfo("Screen Test", "✅ Main application ready!\n\nFeatures:\n- Real Ollama LLM integration\n- Voice recording with microphone\n- Settings with LLM selection\n- Integration buttons moved to Settings → Addons\n\nTry typing a message or recording voice!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not open main application: {e}")
    
    def _test_settings(self):
        """Test settings window"""
        try:
            from vpa.gui.enhanced_settings_window import VPAEnhancedSettingsWindow
            gui_manager = MockGUIManager()
            settings_window = VPAEnhancedSettingsWindow(self.root, gui_manager)
            messagebox.showinfo("Screen Test", "Enhanced settings window opened!\n\nFeatures:\n- Voice & Audio (13 voices)\n- LLM Selection\n- Addons (OAuth integrations)\n- General settings")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open settings window: {e}")
    
    def _test_oauth_setup(self):
        """Test OAuth setup window"""
        try:
            from vpa.gui.oauth_setup_window import VPAOAuthSetupWindow
            gui_manager = MockGUIManager()
            oauth_window = VPAOAuthSetupWindow(self.root, gui_manager, "google")
            messagebox.showinfo("Screen Test", "OAuth setup window opened! Please review and provide feedback.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open OAuth setup window: {e}")
    
    def run(self):
        """Run the GUI tester"""
        print("Starting VPA GUI Screen Tester...")
        print("Click buttons to test individual screens")
        self.root.mainloop()

if __name__ == "__main__":
    try:
        tester = VPAGUIScreenTester()
        tester.run()
    except Exception as e:
        print(f"Error starting GUI tester: {e}")
        sys.exit(1)
