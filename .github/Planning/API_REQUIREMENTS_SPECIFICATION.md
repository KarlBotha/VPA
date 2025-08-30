# VPA API Requirements Specification

> **DEPRECATION NOTICE:** This document has been migrated to the new documentation structure. Please refer to [API Integration Overview](docs/features/API_INTEGRATION/API_INTEGRATION_OVERVIEW.md) for the current version of this content.

## Overview

This document specifies the external APIs required for the VPA (Virtual Personal Assistant) project, including authentication requirements, rate limits, fallback mechanisms, and implementation details.

## 1. Azure Cognitive Services Speech API

### Service Details
- **API Version**: 1.29.0 or higher
- **SDK**: Microsoft Cognitive Services Speech SDK
- **Resource Type**: Speech service in Azure
- **Region**: West US 2 (primary), East US (failover)

### Authentication
- **Authentication Method**: Subscription Key
- **Key Management**: 
  - Store in Windows Credential Manager
  - Encrypt with AES-256 when storing in configuration
  - Implement key rotation mechanism (90-day rotation)

### Rate Limits
- **Free Tier**: 5 audio hours per month
- **Standard Tier**: 100 hours per month, 20 requests per second
- **Implementation**: Implement token bucket algorithm with 2-second retry delay

### Required Features
- **Neural Voice Support**: All specified neural voices
- **SSML Support**: Full SSML for voice styling and emotion
- **Audio Formats**: 24KHz 16-bit PCM WAV, MP3
- **Voice Styles**: Use style tags for emotional expression

### Implementation Details
```python
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer
from azure.cognitiveservices.speech.audio import AudioOutputConfig
import asyncio
from vpa.core.security import credentials

class AzureSpeechProvider:
    def __init__(self):
        self._key = credentials.get_azure_speech_key()
        self._region = "westus2"
        self._fallback_region = "eastus"
        self._speech_config = None
        self._token_bucket = TokenBucket(capacity=20, refill_rate=20, refill_time=1)
        
    async def initialize(self):
        self._speech_config = SpeechConfig(
            subscription=self._key, 
            region=self._region
        )
        # Configure audio output
        self._speech_config.set_speech_synthesis_output_format(
            SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm
        )
        
    async def synthesize_speech(self, text, voice_id, style=None):
        # Check token bucket
        if not self._token_bucket.consume():
            await asyncio.sleep(2)  # Rate limit exceeded, wait and retry
            return await self.synthesize_speech(text, voice_id, style)
            
        try:
            # Configure synthesizer
            synthesizer = SpeechSynthesizer(
                speech_config=self._speech_config, 
                audio_config=AudioOutputConfig(use_default_speaker=True)
            )
            
            # Prepare SSML if style is specified
            if style:
                ssml = f"""
                <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
                       xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
                    <voice name="{voice_id}">
                        <mstts:express-as style="{style}">
                            {text}
                        </mstts:express-as>
                    </voice>
                </speak>
                """
                result = await synthesizer.speak_ssml_async(ssml).get()
            else:
                synthesizer.speech_config.speech_synthesis_voice_name = voice_id
                result = await synthesizer.speak_text_async(text).get()
                
            # Handle result
            if result.reason == ResultReason.SynthesizingAudioCompleted:
                return {
                    "audio_data": result.audio_data,
                    "audio_format": "wav",
                    "duration": len(result.audio_data) / (24000 * 2)  # Calculate duration
                }
            else:
                raise Exception(f"Speech synthesis failed: {result.reason}")
                
        except Exception as e:
            # Try fallback region if primary fails
            if self._region != self._fallback_region:
                old_region = self._region
                self._region = self._fallback_region
                self._fallback_region = old_region
                self._speech_config = SpeechConfig(
                    subscription=self._key, 
                    region=self._region
                )
                return await self.synthesize_speech(text, voice_id, style)
            else:
                raise
```

### Fallback Mechanisms
1. **Region Failover**: Automatic switch to East US if West US 2 fails
2. **Local Fallback**: Windows TTS engine if Azure is unavailable
3. **Text Fallback**: Display text if all speech synthesis fails

## 2. Windows Text-to-Speech API

### Service Details
- **API**: Windows SAPI 5.4 or later
- **Framework**: PyWin32 or pyttsx3 for interface

### Required Features
- **Default Voice**: Microsoft David Desktop (neutral) 
- **Audio Format**: 16KHz 16-bit PCM WAV
- **Playback Control**: Start, pause, stop functionality

### Implementation Details
```python
import pyttsx3
import win32com.client

class WindowsTTSProvider:
    def __init__(self):
        self._engine = None
        self._sapi = None
        
    async def initialize(self):
        # Initialize pyttsx3 engine
        self._engine = pyttsx3.init()
        # Also initialize SAPI directly for advanced features
        self._sapi = win32com.client.Dispatch("SAPI.SpVoice")
        
    async def synthesize_speech(self, text, voice_name="Microsoft David Desktop"):
        try:
            # Set voice
            voices = self._engine.getProperty('voices')
            for voice in voices:
                if voice_name in voice.name:
                    self._engine.setProperty('voice', voice.id)
                    break
            
            # Set properties
            self._engine.setProperty('rate', 175)  # Default rate
            self._engine.setProperty('volume', 0.9)  # 90% volume
            
            # Synthesize
            self._engine.save_to_file(text, 'temp_speech.wav')
            self._engine.runAndWait()
            
            # Read the file and return
            with open('temp_speech.wav', 'rb') as f:
                audio_data = f.read()
                
            return {
                "audio_data": audio_data,
                "audio_format": "wav",
                "duration": len(audio_data) / (16000 * 2)  # Calculate duration
            }
            
        except Exception as e:
            # Last resort fallback - use SAPI directly
            self._sapi.Speak(text)
            return {
                "audio_data": None,
                "audio_format": None,
                "duration": 0,
                "fallback_used": True
            }
```

## 3. LLM APIs

### 3.1 Ollama API

#### Service Details
- **API Version**: v1.0
- **Endpoint**: http://localhost:11434/api/
- **Models**: 
  - Primary: Llama 3 8B Instruct
  - Alternative: Mistral 7B Instruct
  - Gemma 2B Instruct (lightweight)

#### Authentication
- **Authentication Method**: None (local API)
- **Security**: Limit to localhost only

#### Rate Limits
- **Local Management**: Implement resource throttling based on system load
  - Max 2 concurrent requests
  - Throttle if CPU > 80% or RAM > 85%
  - Retry with exponential backoff (starting at 1s)

#### Required Features
- **Streaming**: Support token-by-token streaming for responsive UI
- **System Message**: Support for system prompt/context
- **Temperature Control**: 0.1 (precise) to 1.0 (creative)

#### Implementation Details
```python
import aiohttp
import asyncio
import json
from typing import AsyncGenerator, Dict, Any, Optional

class OllamaAdapter:
    def __init__(self):
        self._base_url = "http://localhost:11434/api"
        self._default_model = "llama3"
        self._session = None
        self._concurrent_requests = 0
        self._max_concurrent = 2
        
    @property
    def name(self) -> str:
        return "ollama"
        
    async def initialize(self) -> None:
        self._session = aiohttp.ClientSession()
        
    async def check_availability(self) -> bool:
        try:
            async with self._session.get(f"{self._base_url}/tags") as response:
                if response.status == 200:
                    return True
                return False
        except:
            return False
            
    async def get_available_models(self) -> List[Dict[str, Any]]:
        models = []
        try:
            async with self._session.get(f"{self._base_url}/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    for model in data.get("models", []):
                        models.append({
                            "id": model["name"],
                            "name": model["name"],
                            "context_window": 4096,  # Default, may vary by model
                            "tokens_per_second": model.get("details", {}).get("parameter_count", 0) / 1e9  # Estimate
                        })
        except Exception as e:
            logger.error(f"Error getting Ollama models: {e}")
            
        return models
        
    async def generate_text(self, 
                           prompt: str, 
                           system_message: str = "", 
                           model: str = "", 
                           temperature: float = 0.7,
                           max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate text using Ollama API."""
        # Resource management
        while self._concurrent_requests >= self._max_concurrent:
            await asyncio.sleep(0.5)
            
        if not model:
            model = self._default_model
            
        self._concurrent_requests += 1
        
        try:
            data = {
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False  # For simplicity in this example
            }
            
            # Add system message if provided
            if system_message:
                data["system"] = system_message
                
            # Exponential backoff for retries
            max_retries = 3
            retry_delay = 1
            
            for attempt in range(max_retries):
                try:
                    async with self._session.post(f"{self._base_url}/generate", json=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            return {
                                "text": result.get("response", ""),
                                "model": model,
                                "tokens": result.get("eval_count", 0),
                                "stop_reason": "stop" if result.get("done", False) else "length"
                            }
                        elif response.status == 429:  # Too many requests
                            await asyncio.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                        else:
                            response.raise_for_status()
                except aiohttp.ClientError as e:
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2
                    else:
                        raise
                        
            raise Exception("Failed to generate text after multiple retries")
            
        finally:
            self._concurrent_requests -= 1
            
    async def generate_stream(self, 
                            prompt: str, 
                            system_message: str = "", 
                            model: str = "", 
                            temperature: float = 0.7,
                            max_tokens: int = 1000) -> AsyncGenerator[str, None]:
        """Generate text using Ollama API with streaming."""
        # Resource management
        while self._concurrent_requests >= self._max_concurrent:
            await asyncio.sleep(0.5)
            
        if not model:
            model = self._default_model
            
        self._concurrent_requests += 1
        
        try:
            data = {
                "model": model,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True
            }
            
            # Add system message if provided
            if system_message:
                data["system"] = system_message
                
            async with self._session.post(f"{self._base_url}/generate", json=data) as response:
                if response.status != 200:
                    response.raise_for_status()
                    
                # Process the streaming response
                async for line in response.content:
                    if not line.strip():
                        continue
                        
                    try:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            yield chunk["response"]
                            
                        # Check if done
                        if chunk.get("done", False):
                            break
                    except json.JSONDecodeError:
                        pass
                        
        finally:
            self._concurrent_requests -= 1
```

### 3.2 Llama.cpp API

#### Service Details
- **API Version**: Compatible with OpenAI API spec
- **Endpoint**: http://localhost:8080/v1
- **Models**: Based on downloaded GGUF files

#### Authentication
- **Authentication Method**: Optional API key (configurable)
- **Security**: Limit to localhost only

#### Implementation Details
```python
import aiohttp
import asyncio
import json
from typing import AsyncGenerator, Dict, Any, Optional, List

class LlamaCppAdapter:
    def __init__(self):
        self._base_url = "http://localhost:8080/v1"
        self._api_key = None  # Optional, can be None
        self._session = None
        self._concurrent_requests = 0
        self._max_concurrent = 1  # Llama.cpp typically handles one request at a time
        
    @property
    def name(self) -> str:
        return "llama_cpp"
        
    async def initialize(self) -> None:
        self._session = aiohttp.ClientSession()
        
    async def check_availability(self) -> bool:
        try:
            async with self._session.get(f"{self._base_url}/models") as response:
                if response.status == 200:
                    return True
                return False
        except:
            return False
            
    async def get_available_models(self) -> List[Dict[str, Any]]:
        models = []
        try:
            async with self._session.get(f"{self._base_url}/models") as response:
                if response.status == 200:
                    data = await response.json()
                    for model in data.get("data", []):
                        models.append({
                            "id": model["id"],
                            "name": model["id"],
                            "context_window": model.get("context_length", 4096),
                            "tokens_per_second": 30  # Approximate, depends on hardware
                        })
        except Exception as e:
            logger.error(f"Error getting Llama.cpp models: {e}")
            
        return models
        
    async def generate_text(self, 
                           prompt: str, 
                           system_message: str = "", 
                           model: str = "", 
                           temperature: float = 0.7,
                           max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate text using Llama.cpp API (OpenAI-compatible)."""
        # Resource management
        while self._concurrent_requests >= self._max_concurrent:
            await asyncio.sleep(1.0)
            
        self._concurrent_requests += 1
        
        try:
            headers = {}
            if self._api_key:
                headers["Authorization"] = f"Bearer {self._api_key}"
                
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
                
            messages.append({"role": "user", "content": prompt})
            
            data = {
                "messages": messages,
                "model": model if model else "default",
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            async with self._session.post(f"{self._base_url}/chat/completions", 
                                        headers=headers,
                                        json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    choices = result.get("choices", [])
                    if choices:
                        return {
                            "text": choices[0].get("message", {}).get("content", ""),
                            "model": model if model else "default",
                            "tokens": result.get("usage", {}).get("completion_tokens", 0),
                            "stop_reason": choices[0].get("finish_reason", "unknown")
                        }
                    else:
                        return {"text": "", "model": model, "tokens": 0, "stop_reason": "error"}
                else:
                    response.raise_for_status()
                    
        finally:
            self._concurrent_requests -= 1
```

### 3.3 Fallback Text Generation

#### Implementation Details
```python
import random
from typing import Dict, Any

class FallbackAdapter:
    """Fallback adapter for offline operation or when LLM services fail."""
    
    @property
    def name(self) -> str:
        return "fallback"
        
    async def initialize(self) -> None:
        # Load pre-generated responses
        self._responses = {
            "greeting": [
                "Hello! I'm currently operating in offline mode.",
                "Hi there! I'm working with limited capabilities at the moment.",
                "Greetings! I'm using pre-generated responses right now."
            ],
            "help": [
                "I can help with basic tasks while offline.",
                "My capabilities are limited in offline mode.",
                "I can assist with simple requests while offline."
            ],
            "error": [
                "I'm sorry, I can't process that request while offline.",
                "That requires online capabilities which aren't available.",
                "I'll need to be online to handle that request."
            ]
        }
        
    async def check_availability(self) -> bool:
        return True  # Always available as it's the fallback
        
    async def get_available_models(self) -> List[Dict[str, Any]]:
        return [{
            "id": "fallback",
            "name": "Fallback Model",
            "context_window": 0,
            "tokens_per_second": 0
        }]
        
    async def generate_text(self, 
                           prompt: str, 
                           system_message: str = "", 
                           model: str = "", 
                           temperature: float = 0.7,
                           max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate fallback text based on the prompt."""
        # Very simple prompt analysis
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["hi", "hello", "greetings"]):
            response_type = "greeting"
        elif any(word in prompt_lower for word in ["help", "assist", "can you"]):
            response_type = "help"
        else:
            response_type = "error"
            
        # Get a random response of the appropriate type
        response = random.choice(self._responses[response_type])
        
        return {
            "text": response,
            "model": "fallback",
            "tokens": len(response.split()),
            "stop_reason": "stop",
            "fallback_used": True
        }
```

## 4. Weather API (OpenWeatherMap)

### Service Details
- **API Version**: 2.5
- **Endpoint**: https://api.openweathermap.org/data/2.5/
- **Tier**: Standard subscription

### Authentication
- **Authentication Method**: API Key
- **Key Management**: Store in Windows Credential Manager

### Rate Limits
- **Standard Plan**: 60 calls/minute, 1,000,000 calls/month
- **Implementation**: Cache results for 30 minutes

### Required Features
- **Current Weather**: Location-based current conditions
- **Forecast**: 5-day forecast with 3-hour steps
- **Geocoding**: City name to coordinates

### Implementation Details
```python
import aiohttp
import asyncio
import json
import time
from typing import Dict, Any, Optional
from vpa.core.security import credentials

class WeatherAPI:
    def __init__(self):
        self._api_key = credentials.get_openweathermap_key()
        self._base_url = "https://api.openweathermap.org/data/2.5"
        self._session = None
        self._cache = {}
        self._cache_duration = 30 * 60  # 30 minutes in seconds
        
    async def initialize(self):
        self._session = aiohttp.ClientSession()
        
    async def get_current_weather(self, location: str) -> Dict[str, Any]:
        """Get current weather for a location."""
        cache_key = f"current_{location}"
        
        # Check cache first
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
            
        # Convert location to coordinates
        coords = await self._get_coordinates(location)
        if not coords:
            return {"error": "Location not found"}
            
        # Get weather data
        url = f"{self._base_url}/weather"
        params = {
            "lat": coords["lat"],
            "lon": coords["lon"],
            "units": "metric",
            "appid": self._api_key
        }
        
        async with self._session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                result = self._format_current_weather(data)
                
                # Cache the result
                self._add_to_cache(cache_key, result)
                
                return result
            else:
                return {"error": f"API error: {response.status}"}
                
    async def get_forecast(self, location: str) -> Dict[str, Any]:
        """Get 5-day forecast for a location."""
        cache_key = f"forecast_{location}"
        
        # Check cache first
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
            
        # Convert location to coordinates
        coords = await self._get_coordinates(location)
        if not coords:
            return {"error": "Location not found"}
            
        # Get forecast data
        url = f"{self._base_url}/forecast"
        params = {
            "lat": coords["lat"],
            "lon": coords["lon"],
            "units": "metric",
            "appid": self._api_key
        }
        
        async with self._session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                result = self._format_forecast(data)
                
                # Cache the result
                self._add_to_cache(cache_key, result)
                
                return result
            else:
                return {"error": f"API error: {response.status}"}
                
    async def _get_coordinates(self, location: str) -> Optional[Dict[str, float]]:
        """Convert location name to coordinates."""
        cache_key = f"geo_{location}"
        
        # Check cache first
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
            
        # Get coordinates
        url = "http://api.openweathermap.org/geo/1.0/direct"
        params = {
            "q": location,
            "limit": 1,
            "appid": self._api_key
        }
        
        async with self._session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if data and len(data) > 0:
                    result = {
                        "lat": data[0]["lat"],
                        "lon": data[0]["lon"],
                        "name": data[0]["name"],
                        "country": data[0]["country"]
                    }
                    
                    # Cache the result
                    self._add_to_cache(cache_key, result)
                    
                    return result
                    
            return None
            
    def _format_current_weather(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format current weather data."""
        return {
            "location": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "weather": data["weather"][0]["main"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
            "wind_direction": data["wind"]["deg"],
            "clouds": data["clouds"]["all"],
            "timestamp": data["dt"],
            "sunrise": data["sys"]["sunrise"],
            "sunset": data["sys"]["sunset"]
        }
        
    def _format_forecast(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format forecast data."""
        result = {
            "location": data["city"]["name"],
            "country": data["city"]["country"],
            "forecast": []
        }
        
        # Group forecasts by day
        days = {}
        for item in data["list"]:
            date = time.strftime("%Y-%m-%d", time.gmtime(item["dt"]))
            
            if date not in days:
                days[date] = []
                
            days[date].append({
                "time": time.strftime("%H:%M", time.gmtime(item["dt"])),
                "temperature": item["main"]["temp"],
                "feels_like": item["main"]["feels_like"],
                "humidity": item["main"]["humidity"],
                "weather": item["weather"][0]["main"],
                "description": item["weather"][0]["description"],
                "wind_speed": item["wind"]["speed"],
                "clouds": item["clouds"]["all"],
                "timestamp": item["dt"]
            })
            
        # Format each day
        for date, items in days.items():
            result["forecast"].append({
                "date": date,
                "items": items
            })
            
        return result
        
    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data from cache if not expired."""
        if key in self._cache:
            item = self._cache[key]
            if time.time() - item["timestamp"] < self._cache_duration:
                return item["data"]
                
        return None
        
    def _add_to_cache(self, key: str, data: Dict[str, Any]) -> None:
        """Add data to cache."""
        self._cache[key] = {
            "timestamp": time.time(),
            "data": data
        }
        
        # Clean up cache if too large
        if len(self._cache) > 100:
            # Remove oldest items
            oldest = sorted(
                self._cache.items(),
                key=lambda x: x[1]["timestamp"]
            )[:20]
            
            for key, _ in oldest:
                del self._cache[key]
```

## 5. Microsoft Graph API

### Service Details
- **API Version**: v1.0
- **Endpoint**: https://graph.microsoft.com/v1.0/
- **Authentication**: OAuth 2.0

### Authentication
- **Authentication Flow**: OAuth 2.0 Authorization Code flow with PKCE
- **Scope Requirements**:
  - User.Read (basic profile)
  - Calendars.ReadWrite (calendar access)
  - Mail.ReadWrite (email access)
  - Tasks.ReadWrite (todo access)

### Rate Limits
- **Standard Usage**: 2,000 requests/user/minute
- **Implementation**: Adhere to Retry-After headers

### Implementation Details
```python
import aiohttp
import asyncio
import json
import time
import msal
from typing import Dict, Any, Optional, List
from vpa.core.security import credentials
from vpa.core.events import event_bus

class MSGraphAPI:
    def __init__(self):
        self._config = {
            "client_id": credentials.get_msgraph_client_id(),
            "authority": "https://login.microsoftonline.com/common",
            "scope": ["User.Read", "Calendars.ReadWrite", "Mail.ReadWrite", "Tasks.ReadWrite"],
            "redirect_uri": "http://localhost:8123"
        }
        self._session = None
        self._app = None
        self._token_cache = msal.SerializableTokenCache()
        self._user_account = None
        
    async def initialize(self):
        self._session = aiohttp.ClientSession()
        self._app = msal.PublicClientApplication(
            self._config["client_id"],
            authority=self._config["authority"],
            token_cache=self._token_cache
        )
        
        # Try to load cached token
        await self._load_token_cache()
        
        # Find an account that we've saved a token for
        accounts = self._app.get_accounts()
        if accounts:
            self._user_account = accounts[0]
            
    async def login(self) -> bool:
        """Initiate login flow."""
        # Start interactive login with PKCE
        flow = self._app.initiate_device_flow(scopes=self._config["scope"])
        
        if "user_code" not in flow:
            return False
            
        # Emit login event
        await event_bus.emit_async("msgraph_login_required", {
            "message": flow["message"],
            "user_code": flow["user_code"],
            "verification_uri": flow["verification_uri"]
        })
        
        # Wait for user to complete login
        result = self._app.acquire_token_by_device_flow(flow)
        
        if "access_token" not in result:
            await event_bus.emit_async("msgraph_login_failed", {
                "error": result.get("error", "Unknown error"),
                "error_description": result.get("error_description", "No description available")
            })
            return False
            
        # Save account
        accounts = self._app.get_accounts()
        if accounts:
            self._user_account = accounts[0]
            
        # Save token cache
        await self._save_token_cache()
        
        await event_bus.emit_async("msgraph_login_success", {
            "user_id": self._user_account["id"],
            "username": self._user_account["username"]
        })
        
        return True
        
    async def get_calendar_events(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get calendar events for a date range."""
        token = await self._ensure_token()
        if not token:
            return {"error": "Not authenticated"}
            
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        url = "https://graph.microsoft.com/v1.0/me/calendarview"
        params = {
            "startDateTime": start_date,
            "endDateTime": end_date,
            "$select": "subject,organizer,start,end,location",
            "$orderby": "start/dateTime",
            "$top": 50
        }
        
        async with self._session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return self._format_calendar_events(data)
            elif response.status == 429:  # Rate limited
                retry_after = int(response.headers.get("Retry-After", "60"))
                await asyncio.sleep(retry_after)
                return await self.get_calendar_events(start_date, end_date)
            else:
                return {"error": f"API error: {response.status}"}
                
    async def create_calendar_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a calendar event."""
        token = await self._ensure_token()
        if not token:
            return {"error": "Not authenticated"}
            
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        url = "https://graph.microsoft.com/v1.0/me/events"
        
        # Format the event data for Graph API
        graph_event = {
            "subject": event_data["subject"],
            "start": {
                "dateTime": event_data["start_time"],
                "timeZone": event_data.get("timezone", "UTC")
            },
            "end": {
                "dateTime": event_data["end_time"],
                "timeZone": event_data.get("timezone", "UTC")
            }
        }
        
        if "location" in event_data:
            graph_event["location"] = {
                "displayName": event_data["location"]
            }
            
        if "body" in event_data:
            graph_event["body"] = {
                "contentType": "text",
                "content": event_data["body"]
            }
            
        async with self._session.post(url, headers=headers, json=graph_event) as response:
            if response.status == 201:
                data = await response.json()
                return {"success": True, "event_id": data["id"]}
            elif response.status == 429:  # Rate limited
                retry_after = int(response.headers.get("Retry-After", "60"))
                await asyncio.sleep(retry_after)
                return await self.create_calendar_event(event_data)
            else:
                error_data = await response.json()
                return {
                    "error": f"API error: {response.status}",
                    "details": error_data.get("error", {}).get("message", "Unknown error")
                }
                
    async def _ensure_token(self) -> Optional[str]:
        """Ensure we have a valid token."""
        if not self._user_account:
            return None
            
        # Try to get token silently
        result = self._app.acquire_token_silent(
            self._config["scope"],
            account=self._user_account
        )
        
        if result and "access_token" in result:
            return result["access_token"]
            
        # Token expired and refresh failed, need to re-login
        await event_bus.emit_async("msgraph_token_expired", {})
        return None
        
    async def _save_token_cache(self) -> None:
        """Save token cache to secure storage."""
        if self._token_cache.has_state_changed:
            cache_data = self._token_cache.serialize()
            await credentials.save_msgraph_token_cache(cache_data)
            
    async def _load_token_cache(self) -> None:
        """Load token cache from secure storage."""
        cache_data = await credentials.load_msgraph_token_cache()
        if cache_data:
            self._token_cache.deserialize(cache_data)
            
    def _format_calendar_events(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format calendar events."""
        result = {
            "events": []
        }
        
        for event in data.get("value", []):
            formatted_event = {
                "id": event["id"],
                "subject": event["subject"],
                "start": event["start"]["dateTime"],
                "end": event["end"]["dateTime"],
                "timezone": event["start"]["timeZone"],
                "organizer": event["organizer"]["emailAddress"]["name"]
            }
            
            if "location" in event and event["location"]["displayName"]:
                formatted_event["location"] = event["location"]["displayName"]
                
            result["events"].append(formatted_event)
            
        return result
```

## 6. Additional API Requirements

### 6.1 Google Maps Geocoding API (Optional)

- **Purpose**: Location lookup and validation
- **API Key**: Store in Windows Credential Manager
- **Cache Results**: 30 days for static locations

### 6.2 News API

- **Provider**: NewsAPI.org
- **Endpoint**: https://newsapi.org/v2/
- **Features**:
  - Top headlines by country and category
  - Search functionality
  - Article content retrieval
- **Rate Limits**: Developer plan - 100 requests per day

## API Security Considerations

### 1. API Key Management
- All API keys stored in Windows Credential Manager
- Keys never exposed in code or logs
- Encryption for configuration files

### 2. Data Privacy
- User data cached only as needed
- Clear cache options for sensitive data
- Privacy policy compliance

### 3. Error Handling
- Graceful degradation for API failures
- Fallback mechanisms for all APIs
- No sensitive data in error logs

## Fallback Strategy

### Tier 1: Primary Services
- Azure Speech Service
- Ollama or Llama.cpp

### Tier 2: Alternative Services
- Alternate Azure region
- Secondary LLM model

### Tier 3: Local Fallbacks
- Windows TTS
- Pre-generated responses

### Tier 4: Text-Only Mode
- Text display when all voice services fail
- Static content when all APIs fail

## Implementation Best Practices

1. **Retry Logic**:
   - Implement exponential backoff for all APIs
   - Honor Retry-After headers when provided
   - Maximum 3 retry attempts before fallback

2. **Caching Strategy**:
   - Cache voice output for common phrases
   - Cache API responses with appropriate TTL
   - Cache invalidation on context changes

3. **Resource Management**:
   - Connection pooling for all HTTP clients
   - Proper session cleanup on application shutdown
   - Memory-conscious buffer management for audio

4. **Monitoring**:
   - Log all API interactions (excluding sensitive data)
   - Track success/failure rates
   - Monitor performance metrics

---

*API Requirements Specification completed on August 27, 2025*
