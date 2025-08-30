# Voice Input Language Support [DEPRECATED]

> **IMPORTANT NOTICE:** This document has been deprecated and moved to the proper documentation location. 
> 
> **NEW LOCATION:** [docs/voice/requirements/VOICE_INPUT_LANGUAGE_SUPPORT.md](docs/voice/requirements/VOICE_INPUT_LANGUAGE_SUPPORT.md)

## Overview

This document details the language support for VPA's voice input system, including supported languages, regional variants, and integration with speech-to-text systems.

## Table of Contents

1. [Supported Languages](#1-supported-languages)
2. [Windows Speech Recognition Integration](#2-windows-speech-recognition-integration)
3. [Fallback Speech Recognition](#3-fallback-speech-recognition)
4. [Language Configuration](#4-language-configuration)
5. [Customization and Training](#5-customization-and-training)

## 1. Supported Languages

### 1.1 Primary Supported Languages

VPA will initially support the following languages for voice input:

| Language | Variants | Support Level | Accuracy Target |
|----------|----------|---------------|----------------|
| English | US, UK, AU, CA, IN | Primary | 95%+ |
| Spanish | ES, MX, LA | Secondary | 90%+ |
| French | FR, CA | Secondary | 90%+ |
| German | DE | Secondary | 90%+ |

### 1.2 Language Recognition Quality Matrix

Recognition quality will vary based on the recognition engine used:

| Language | Windows SR | Whisper Fallback | Vosk Fallback |
|----------|------------|------------------|---------------|
| English (US) | Excellent | Excellent | Good |
| English (UK) | Excellent | Excellent | Good |
| English (AU) | Very Good | Excellent | Fair |
| English (CA) | Very Good | Excellent | Good |
| English (IN) | Good | Very Good | Fair |
| Spanish (ES) | Very Good | Very Good | Fair |
| Spanish (MX) | Good | Very Good | Fair |
| Spanish (LA) | Fair | Good | Limited |
| French (FR) | Very Good | Very Good | Fair |
| French (CA) | Good | Very Good | Fair |
| German (DE) | Very Good | Very Good | Good |

### 1.3 Language Detection

VPA will implement automatic language detection:

1. **User Setting**: Primary method - use language set in user preferences
2. **Auto Detection**: Secondary method - detect language from first few seconds of audio
3. **Contextual**: Tertiary method - infer from recent conversation language

```python
class LanguageDetector:
    """Detects language from audio input"""
    
    def __init__(self):
        self.whisper_model = None
        self.user_language = None
        
    def initialize(self, user_language=None):
        """Initialize the language detector"""
        self.user_language = user_language
        
    async def detect_language(self, audio_data: bytes) -> str:
        """Detect language from audio data"""
        # If user has set a preferred language, use that
        if self.user_language:
            return self.user_language
            
        # Otherwise try to detect language from audio
        try:
            # Initialize whisper model if not already initialized
            if not self.whisper_model:
                import whisper
                self.whisper_model = whisper.load_model("tiny")
                
            # Convert audio data to format whisper expects
            import numpy as np
            import io
            import soundfile as sf
            
            audio_data = io.BytesIO(audio_data)
            audio_array, _ = sf.read(audio_data)
            audio_array = audio_array.astype(np.float32)
            
            # Detect language
            result = self.whisper_model.detect_language(audio_array)
            return result["language"]
        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            return "en"  # Default to English
```

## 2. Windows Speech Recognition Integration

### 2.1 Windows SR API Integration

VPA will use the Windows Speech Recognition API as the primary recognition engine:

```python
class WindowsSpeechRecognition:
    """Windows Speech Recognition integration"""
    
    def __init__(self):
        self.engine = None
        self.current_language = "en-US"
        self.supported_languages = {
            "en-US": "English (United States)",
            "en-GB": "English (United Kingdom)",
            "en-AU": "English (Australia)",
            "en-CA": "English (Canada)",
            "en-IN": "English (India)",
            "es-ES": "Spanish (Spain)",
            "es-MX": "Spanish (Mexico)",
            "fr-FR": "French (France)",
            "fr-CA": "French (Canada)",
            "de-DE": "German (Germany)"
        }
        
    async def initialize(self) -> bool:
        """Initialize Windows Speech Recognition"""
        try:
            import win32com.client
            self.engine = win32com.client.Dispatch("SAPI.SpSharedRecognizer")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Windows Speech Recognition: {e}")
            return False
            
    def get_supported_languages(self) -> dict:
        """Get dictionary of supported languages"""
        return self.supported_languages
        
    async def set_language(self, language_code: str) -> bool:
        """Set the recognition language"""
        if language_code not in self.supported_languages:
            logger.error(f"Unsupported language: {language_code}")
            return False
            
        try:
            # Check if language is installed
            import win32com.client
            token_enum = win32com.client.Dispatch("SAPI.SpObjectTokenCategory")
            token_enum.SetId("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices")
            
            voices = [token_enum.EnumTokens().Item(i) for i in range(token_enum.EnumTokens().Count)]
            has_language = any(language_code in voice.GetAttribute("Language") for voice in voices)
            
            if not has_language:
                logger.error(f"Language {language_code} is not installed")
                return False
                
            # Set language
            self.current_language = language_code
            
            # Recreate engine with new language
            self.engine = win32com.client.Dispatch("SAPI.SpSharedRecognizer")
            context = self.engine.CreateRecoContext()
            grammar = context.CreateGrammar()
            
            # Create dictation grammar for the language
            grammar.DictationSetState(1)
            
            return True
        except Exception as e:
            logger.error(f"Failed to set language to {language_code}: {e}")
            return False
            
    async def recognize(self, audio_data: bytes) -> str:
        """Recognize speech from audio data"""
        if not self.engine:
            if not await self.initialize():
                raise Exception("Failed to initialize Windows Speech Recognition")
                
        try:
            import tempfile
            import os
            
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
                temp.write(audio_data)
                temp_filename = temp.name
                
            # Create recognition context
            context = self.engine.CreateRecoContext()
            
            # Create grammar
            grammar = context.CreateGrammar()
            grammar.DictationSetState(1)
            
            # Load audio file
            stream = context.CreateRecoResult()
            stream.AudioFormat = None  # Use default format
            
            # Start recognition
            grammar.DictationSetState(1)
            context.Bookmark(1, 0, 0)
            
            # Perform recognition
            result = stream.AudioStreamFileOpen(temp_filename, 0, False)
            while not context.WaitForNotifyEvent(100):
                pass
                
            # Get result
            result = context.GetResult()
            text = result.PhraseInfo.GetText(0, -1, True)
            
            # Clean up
            os.unlink(temp_filename)
            
            return text
        except Exception as e:
            logger.error(f"Windows Speech Recognition failed: {e}")
            raise
```

### 2.2 Language Pack Detection

VPA will detect installed Windows language packs:

```python
async def detect_installed_language_packs() -> List[str]:
    """Detect installed Windows language packs"""
    try:
        import win32com.client
        token_enum = win32com.client.Dispatch("SAPI.SpObjectTokenCategory")
        token_enum.SetId("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices")
        
        voices = [token_enum.EnumTokens().Item(i) for i in range(token_enum.EnumTokens().Count)]
        languages = set(voice.GetAttribute("Language") for voice in voices)
        
        return list(languages)
    except Exception as e:
        logger.error(f"Failed to detect installed language packs: {e}")
        return ["en-US"]  # Default to US English
```

## 3. Fallback Speech Recognition

### 3.1 Whisper Model Fallback

When Windows SR fails, VPA will fall back to Whisper:

```python
class WhisperFallback:
    """Whisper speech recognition fallback"""
    
    def __init__(self):
        self.model = None
        self.model_name = "tiny"  # Options: tiny, base, small, medium, large
        
    async def initialize(self) -> bool:
        """Initialize Whisper model"""
        try:
            # Check if model size is appropriate for system
            system_memory = psutil.virtual_memory().total / (1024 ** 3)  # GB
            
            if system_memory < 4:
                self.model_name = "tiny"  # ~75MB
            elif system_memory < 8:
                self.model_name = "base"  # ~150MB
            else:
                self.model_name = "small"  # ~500MB
                
            # Import whisper (lazy loading)
            import whisper
            
            # Load model
            self.model = whisper.load_model(self.model_name)
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Whisper: {e}")
            return False
            
    async def recognize(self, audio_data: bytes, language: str = None) -> str:
        """Recognize speech from audio data"""
        if not self.model:
            if not await self.initialize():
                raise Exception("Failed to initialize Whisper")
                
        try:
            import numpy as np
            import io
            import soundfile as sf
            
            # Convert audio data to format whisper expects
            audio_data = io.BytesIO(audio_data)
            audio_array, _ = sf.read(audio_data)
            audio_array = audio_array.astype(np.float32)
            
            # Transcribe audio
            options = {}
            if language:
                # Convert language code to ISO-639-1
                language_map = {
                    "en-US": "en", "en-GB": "en", "en-AU": "en", "en-CA": "en", "en-IN": "en",
                    "es-ES": "es", "es-MX": "es",
                    "fr-FR": "fr", "fr-CA": "fr",
                    "de-DE": "de"
                }
                options["language"] = language_map.get(language, language)
                
            result = self.model.transcribe(audio_array, **options)
            
            return result["text"].strip()
        except Exception as e:
            logger.error(f"Whisper recognition failed: {e}")
            raise
```

### 3.2 Vosk Fallback

As a second fallback option, VPA will use Vosk for offline recognition:

```python
class VoskFallback:
    """Vosk speech recognition fallback"""
    
    def __init__(self):
        self.model = None
        self.recognizer = None
        self.model_path = None
        self.language_models = {
            "en": "vosk-model-small-en-us",
            "es": "vosk-model-small-es",
            "fr": "vosk-model-small-fr",
            "de": "vosk-model-small-de"
        }
        
    async def initialize(self, language: str = "en") -> bool:
        """Initialize Vosk model"""
        try:
            # Import vosk (lazy loading)
            from vosk import Model, KaldiRecognizer
            import os
            
            # Convert language code to ISO-639-1
            language_map = {
                "en-US": "en", "en-GB": "en", "en-AU": "en", "en-CA": "en", "en-IN": "en",
                "es-ES": "es", "es-MX": "es",
                "fr-FR": "fr", "fr-CA": "fr",
                "de-DE": "de"
            }
            lang_code = language_map.get(language, "en")
            
            # Get model name
            model_name = self.language_models.get(lang_code, self.language_models["en"])
            
            # Check if model exists in app data
            app_data = os.path.join(os.getenv('APPDATA'), "VPA", "speech_models")
            model_path = os.path.join(app_data, model_name)
            
            if not os.path.exists(model_path):
                # Model doesn't exist, need to download
                return False
                
            # Load model
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, 16000)
            self.model_path = model_path
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Vosk: {e}")
            return False
            
    async def recognize(self, audio_data: bytes) -> str:
        """Recognize speech from audio data"""
        if not self.recognizer:
            if not await self.initialize():
                raise Exception("Failed to initialize Vosk")
                
        try:
            import json
            
            # Reset recognizer
            self.recognizer.Reset()
            
            # Process audio data
            self.recognizer.AcceptWaveform(audio_data)
            result = self.recognizer.FinalResult()
            
            # Parse result
            result_json = json.loads(result)
            
            return result_json.get("text", "").strip()
        except Exception as e:
            logger.error(f"Vosk recognition failed: {e}")
            raise
```

## 4. Language Configuration

### 4.1 Language Settings Interface

VPA will provide a language settings interface:

```python
class LanguageSettingsWidget(QWidget):
    """Widget for language settings"""
    
    def __init__(self, settings_manager, speech_recognizer):
        super().__init__()
        self.settings_manager = settings_manager
        self.speech_recognizer = speech_recognizer
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        
        # Voice input language settings
        group_box = QGroupBox("Voice Input Language")
        group_layout = QVBoxLayout(group_box)
        
        # Get supported languages
        supported_languages = self.speech_recognizer.get_supported_languages()
        
        # Language selector
        self.language_combo = QComboBox()
        self.language_combo.setMinimumWidth(200)
        
        # Add languages to combo box
        current_language = self.settings_manager.get("voice_input.language", "en-US")
        
        for lang_code, lang_name in supported_languages.items():
            self.language_combo.addItem(lang_name, lang_code)
            if lang_code == current_language:
                self.language_combo.setCurrentIndex(self.language_combo.count() - 1)
                
        # Connect language change
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        
        # Add to layout
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Recognition Language:"))
        lang_layout.addWidget(self.language_combo)
        lang_layout.addStretch(1)
        group_layout.addLayout(lang_layout)
        
        # Auto language detection
        self.auto_detect = QCheckBox("Auto-detect language (may reduce accuracy)")
        self.auto_detect.setChecked(self.settings_manager.get("voice_input.auto_detect_language", False))
        self.auto_detect.stateChanged.connect(self._on_auto_detect_changed)
        group_layout.addWidget(self.auto_detect)
        
        # Add group box to main layout
        layout.addWidget(group_box)
        
        # Additional language settings
        advanced_group = QGroupBox("Advanced Language Settings")
        advanced_layout = QVBoxLayout(advanced_group)
        
        # Fallback engines
        self.use_whisper = QCheckBox("Use Whisper as fallback (more accurate, requires download)")
        self.use_whisper.setChecked(self.settings_manager.get("voice_input.use_whisper_fallback", True))
        self.use_whisper.stateChanged.connect(self._on_whisper_changed)
        advanced_layout.addWidget(self.use_whisper)
        
        self.use_vosk = QCheckBox("Use Vosk as secondary fallback (fully offline, less accurate)")
        self.use_vosk.setChecked(self.settings_manager.get("voice_input.use_vosk_fallback", False))
        self.use_vosk.stateChanged.connect(self._on_vosk_changed)
        advanced_layout.addWidget(self.use_vosk)
        
        # Add advanced group to main layout
        layout.addWidget(advanced_group)
        
        # Add stretch to push everything up
        layout.addStretch(1)
        
    def _on_language_changed(self, index):
        """Handle language selection change"""
        lang_code = self.language_combo.itemData(index)
        self.settings_manager.set("voice_input.language", lang_code)
        
        # Apply the language change
        asyncio.create_task(self.speech_recognizer.set_language(lang_code))
        
    def _on_auto_detect_changed(self, state):
        """Handle auto detect change"""
        self.settings_manager.set("voice_input.auto_detect_language", state == Qt.Checked)
        
        # Enable/disable language selector based on auto detect
        self.language_combo.setEnabled(state != Qt.Checked)
        
    def _on_whisper_changed(self, state):
        """Handle whisper fallback change"""
        self.settings_manager.set("voice_input.use_whisper_fallback", state == Qt.Checked)
        
    def _on_vosk_changed(self, state):
        """Handle vosk fallback change"""
        self.settings_manager.set("voice_input.use_vosk_fallback", state == Qt.Checked)
```

### 4.2 Default Language Settings

The default language settings will be:

```python
default_language_settings = {
    "voice_input.language": "en-US",
    "voice_input.auto_detect_language": False,
    "voice_input.use_whisper_fallback": True,
    "voice_input.use_vosk_fallback": False,
    "voice_input.custom_vocabulary_enabled": False
}
```

## 5. Customization and Training

### 5.1 Custom Vocabulary

VPA will allow users to add custom vocabulary:

```python
class CustomVocabularyManager:
    """Manager for custom vocabulary"""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.custom_words = []
        self.load_custom_vocabulary()
        
    def load_custom_vocabulary(self):
        """Load custom vocabulary from settings"""
        self.custom_words = self.settings_manager.get("voice_input.custom_vocabulary", [])
        
    def save_custom_vocabulary(self):
        """Save custom vocabulary to settings"""
        self.settings_manager.set("voice_input.custom_vocabulary", self.custom_words)
        
    def add_word(self, word: str) -> bool:
        """Add word to custom vocabulary"""
        if word not in self.custom_words:
            self.custom_words.append(word)
            self.save_custom_vocabulary()
            return True
        return False
        
    def remove_word(self, word: str) -> bool:
        """Remove word from custom vocabulary"""
        if word in self.custom_words:
            self.custom_words.remove(word)
            self.save_custom_vocabulary()
            return True
        return False
        
    def get_words(self) -> List[str]:
        """Get list of custom vocabulary words"""
        return self.custom_words
        
    def apply_vocabulary_to_windows_sr(self):
        """Apply custom vocabulary to Windows Speech Recognition"""
        try:
            import win32com.client
            
            # Check if enabled
            if not self.settings_manager.get("voice_input.custom_vocabulary_enabled", False):
                return
                
            # Get shared recognizer
            engine = win32com.client.Dispatch("SAPI.SpSharedRecognizer")
            
            # Create context
            context = engine.CreateRecoContext()
            
            # Add words to context
            for word in self.custom_words:
                context.AddProperty("UDWord", word)
                
        except Exception as e:
            logger.error(f"Failed to apply custom vocabulary: {e}")
```

### 5.2 Continuous Learning

VPA will implement continuous learning to improve speech recognition:

```python
class SpeechLearningManager:
    """Manager for continuous speech recognition learning"""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.corrections = {}
        self.load_corrections()
        
    def load_corrections(self):
        """Load corrections from settings"""
        self.corrections = self.settings_manager.get("voice_input.corrections", {})
        
    def save_corrections(self):
        """Save corrections to settings"""
        self.settings_manager.set("voice_input.corrections", self.corrections)
        
    def add_correction(self, misrecognized: str, corrected: str):
        """Add correction mapping"""
        self.corrections[misrecognized] = corrected
        self.save_corrections()
        
    def get_correction(self, text: str) -> str:
        """Get correction for text if available"""
        return self.corrections.get(text, text)
        
    def apply_corrections(self, text: str) -> str:
        """Apply learned corrections to recognized text"""
        result = text
        
        # Apply word-level corrections
        words = text.split()
        corrected_words = [self.get_correction(word) for word in words]
        result = " ".join(corrected_words)
        
        # Apply phrase-level corrections
        for phrase, correction in self.corrections.items():
            if " " in phrase and phrase in result:
                result = result.replace(phrase, correction)
                
        return result
```

## Conclusion

This Voice Input Language Support specification provides a comprehensive plan for supporting multiple languages in VPA's voice input system. By integrating Windows Speech Recognition with fallback options like Whisper and Vosk, VPA ensures reliable speech recognition across multiple languages.

The implementation includes language detection, custom vocabulary, and continuous learning capabilities to improve recognition accuracy over time. This approach allows VPA to provide high-quality voice input capabilities for users across different languages and regions.

---

*Document created on August 28, 2025*  
*Version: 1.0*
