# LLM Integration Strategy for VPA

## 1. Overview

This document outlines the strategy for integrating Local Large Language Models (LLMs) into the VPA application, following the event-driven, modular architecture with a focus on performance and compartmentalized isolation.

## 2. Core Architecture Principles

The LLM integration will adhere to the following architectural principles:

### 2.1 Event-Driven Communication
- All LLM interactions will use the existing event bus system
- Zero direct coupling between LLM components and other systems
- Standard event patterns for requests and responses

### 2.2 Compartmentalized Isolation
- LLM functionality contained in dedicated plugin(s)
- Error boundaries prevent LLM issues from affecting core functionality
- Graceful degradation when LLM services are unavailable

### 2.3 Performance First
- Strict adherence to performance targets
- Async processing for non-blocking operation
- Configurable resource limits based on system capabilities

### 2.4 Modular Design
- Clear separation between core app and LLM capabilities
- Pluggable model backends with unified interface
- Feature flagging for progressive enhancement

## 3. LLM Component Architecture

### 3.1 Core Components

```
src/
└── vpa/
    ├── core/
    │   └── llm/
    │       ├── __init__.py
    │       ├── llm_manager.py       # Main coordinator
    │       ├── model_registry.py    # Available models tracking
    │       ├── adapters/            # Backend-specific adapters
    │       │   ├── __init__.py
    │       │   ├── base.py          # Abstract base adapter
    │       │   ├── ollama.py        # Ollama adapter
    │       │   ├── llama_cpp.py     # llama.cpp adapter
    │       │   └── openai.py        # OpenAI-compatible adapter
    │       └── utils/               # Utilities
    │           ├── __init__.py
    │           ├── prompt_builder.py
    │           ├── response_parser.py
    │           └── token_counter.py
    └── plugins/
        └── llm_assistant/           # LLM-based assistant plugin
            ├── __init__.py
            ├── assistant.py         # Main plugin class
            ├── config.py            # Configuration options
            └── skills/              # Specialized capabilities
                ├── __init__.py
                ├── calendar_helper.py
                ├── email_composer.py
                └── web_search.py
```

### 3.2 Key Interfaces

#### LLMManager

```python
class LLMManager:
    """Central coordinator for LLM functionality"""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.adapters = {}
        self.active_adapter = None
        self.model_registry = ModelRegistry()
        
        # Set up event subscriptions
        self.event_bus.subscribe("llm_request", self.handle_llm_request, async_callback=True)
        self.event_bus.subscribe("llm_system_check", self.check_system_compatibility)
        self.event_bus.subscribe("llm_model_install", self.install_model)
        self.event_bus.subscribe("llm_adapter_change", self.change_adapter)
    
    async def handle_llm_request(self, event_data):
        """Process an LLM request"""
        try:
            if not self.active_adapter:
                await self.event_bus.emit_async("llm_error", {
                    "error": "no_adapter_available",
                    "request_id": event_data.get("request_id")
                })
                return
            
            with PerformanceMonitor.track_execution_time("llm_request_processing"):
                response = await self.active_adapter.generate(
                    prompt=event_data["prompt"],
                    system_message=event_data.get("system_message"),
                    temperature=event_data.get("temperature", 0.7),
                    max_tokens=event_data.get("max_tokens", 1024)
                )
            
            await self.event_bus.emit_async("llm_response", {
                "request_id": event_data.get("request_id"),
                "response": response,
                "model": self.active_adapter.model_name
            })
            
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            await self.event_bus.emit_async("llm_error", {
                "error": str(e),
                "request_id": event_data.get("request_id")
            })
    
    async def install_model(self, event_data):
        """Install a new model"""
        model_id = event_data.get("model_id")
        adapter_type = event_data.get("adapter_type")
        
        try:
            # Get appropriate adapter
            adapter = self.adapters.get(adapter_type)
            if not adapter:
                raise ValueError(f"Unknown adapter type: {adapter_type}")
            
            # Start installation
            await self.event_bus.emit_async("llm_install_started", {
                "model_id": model_id,
                "adapter_type": adapter_type
            })
            
            # Perform installation
            success = await adapter.install_model(model_id)
            
            if success:
                # Update model registry
                self.model_registry.register_model(model_id, adapter_type)
                await self.event_bus.emit_async("llm_install_complete", {
                    "model_id": model_id,
                    "adapter_type": adapter_type,
                    "success": True
                })
            else:
                await self.event_bus.emit_async("llm_install_complete", {
                    "model_id": model_id,
                    "adapter_type": adapter_type,
                    "success": False,
                    "error": "Installation failed"
                })
        
        except Exception as e:
            logger.error(f"Model installation failed: {e}")
            await self.event_bus.emit_async("llm_install_complete", {
                "model_id": model_id,
                "adapter_type": adapter_type,
                "success": False,
                "error": str(e)
            })
    
    def check_system_compatibility(self, event_data=None):
        """Check if system meets requirements for LLM usage"""
        system_info = self._get_system_info()
        
        compatibility = {
            "cpu_compatible": self._check_cpu_compatibility(system_info),
            "ram_sufficient": system_info["ram_gb"] >= 8,
            "disk_space_sufficient": system_info["free_disk_gb"] >= 10,
            "recommended_models": self._get_recommended_models(system_info),
            "system_info": system_info
        }
        
        self.event_bus.emit("llm_system_compatibility", compatibility)
        return compatibility
    
    def _get_system_info(self):
        """Get system information for compatibility check"""
        import psutil
        
        return {
            "cpu_count": psutil.cpu_count(logical=False),
            "logical_cpu_count": psutil.cpu_count(logical=True),
            "ram_gb": psutil.virtual_memory().total / (1024**3),
            "free_disk_gb": psutil.disk_usage('/').free / (1024**3),
            "cpu_info": self._get_cpu_info(),
            "gpu_info": self._get_gpu_info()
        }
    
    def _get_recommended_models(self, system_info):
        """Get recommended models based on system capabilities"""
        recommendations = []
        
        # Basic recommendations based on RAM
        if system_info["ram_gb"] < 8:
            recommendations.append("orca-mini-3b-gguf2-q4_0")
        elif system_info["ram_gb"] < 16:
            recommendations.append("llama2-7b-chat-gguf2-q4_0")
            recommendations.append("mistral-7b-instruct-gguf2-q4_0")
        else:
            recommendations.append("llama2-13b-chat-gguf2-q4_0")
            recommendations.append("mistral-7b-instruct-gguf2-q5_K_M")
        
        # Add GPU-specific recommendations if available
        if system_info["gpu_info"] and system_info["gpu_info"]["cuda_available"]:
            if system_info["gpu_info"]["vram_gb"] > 8:
                recommendations.append("llama2-13b-chat-gguf2-q5_K_M (GPU)")
        
        return recommendations
```

#### LLMAdapter (Base)

```python
from abc import ABC, abstractmethod

class LLMAdapter(ABC):
    """Base class for LLM adapters"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.model_name = None
        self.initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the adapter"""
        pass
    
    @abstractmethod
    async def generate(self, prompt: str, system_message: str = None, 
                       temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """Generate text response from the model"""
        pass
    
    @abstractmethod
    async def install_model(self, model_id: str) -> bool:
        """Install a model"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> list:
        """Get list of available models"""
        pass
    
    @abstractmethod
    def get_model_info(self, model_id: str) -> dict:
        """Get information about a specific model"""
        pass
    
    async def validate_prompt(self, prompt: str, system_message: str = None) -> tuple:
        """Validate and potentially modify prompt before sending to LLM"""
        # Base implementation can do token counting, safety checks, etc.
        from .utils.token_counter import count_tokens
        
        token_count = count_tokens(prompt)
        if system_message:
            token_count += count_tokens(system_message)
        
        if token_count > self.config.get("max_input_tokens", 4096):
            return False, "Prompt exceeds maximum token limit"
        
        return True, prompt
```

#### OllamaAdapter

```python
import aiohttp
from .base import LLMAdapter

class OllamaAdapter(LLMAdapter):
    """Adapter for Ollama API"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.base_url = self.config.get("base_url", "http://localhost:11434")
        self.api_version = "v1"
    
    async def initialize(self) -> bool:
        """Initialize the adapter by checking Ollama availability"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/{self.api_version}/models") as response:
                    if response.status == 200:
                        self.initialized = True
                        return True
                    return False
        except Exception as e:
            logger.error(f"Failed to initialize Ollama adapter: {e}")
            return False
    
    async def generate(self, prompt: str, system_message: str = None, 
                      temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """Generate text using Ollama API"""
        if not self.initialized:
            await self.initialize()
            if not self.initialized:
                raise RuntimeError("Ollama adapter not initialized")
        
        valid, prompt_or_error = await self.validate_prompt(prompt, system_message)
        if not valid:
            raise ValueError(prompt_or_error)
        
        model_name = self.model_name or self.config.get("default_model", "llama2:latest")
        
        request_data = {
            "model": model_name,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        if system_message:
            request_data["system"] = system_message
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/{self.api_version}/generate", 
                    json=request_data
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise RuntimeError(f"Ollama API error: {error_text}")
                    
                    data = await response.json()
                    return data.get("response", "")
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            raise
    
    async def install_model(self, model_id: str) -> bool:
        """Install a model with Ollama"""
        if not self.initialized:
            await self.initialize()
            if not self.initialized:
                raise RuntimeError("Ollama adapter not initialized")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/{self.api_version}/pull",
                    json={"name": model_id}
                ) as response:
                    # Ollama pull is asynchronous, we just check if request was accepted
                    return response.status == 200
        except Exception as e:
            logger.error(f"Ollama model installation failed: {e}")
            return False
    
    def get_available_models(self) -> list:
        """Get list of available models in Ollama"""
        # This should be implemented with synchronous HTTP request
        # or by calling an async method from sync context
        import requests
        
        try:
            response = requests.get(f"{self.base_url}/{self.api_version}/models")
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return []
        except Exception as e:
            logger.error(f"Failed to get Ollama models: {e}")
            return []
    
    def get_model_info(self, model_id: str) -> dict:
        """Get information about a specific Ollama model"""
        # Ollama API doesn't have a dedicated endpoint for model info
        # We could parse it from the tags or implement a custom approach
        return {
            "name": model_id,
            "provider": "ollama",
            "installed": model_id in self.get_available_models()
        }
```

### 3.3 Event Schema

```python
# LLM Request Event
{
    "event": "llm_request",
    "data": {
        "request_id": "unique-request-id",
        "prompt": "User prompt text here",
        "system_message": "Optional system message",
        "temperature": 0.7,
        "max_tokens": 1024,
        "context": {
            "user_id": "user-id",
            "session_id": "session-id",
            "timestamp": 1630000000
        }
    }
}

# LLM Response Event
{
    "event": "llm_response",
    "data": {
        "request_id": "unique-request-id",
        "response": "Generated text response",
        "model": "llama2-7b",
        "tokens_used": 256,
        "processing_time_ms": 1200
    }
}

# LLM Error Event
{
    "event": "llm_error",
    "data": {
        "request_id": "unique-request-id",
        "error": "Error message",
        "error_type": "timeout|connection|validation|internal"
    }
}
```

## 4. LLM Plugin Implementation

### 4.1 Core Assistant Plugin

```python
from vpa.core.plugins import Plugin
from vpa.core.events import event_bus

class LLMAssistantPlugin(Plugin):
    """LLM-powered assistant plugin"""
    
    @property
    def name(self) -> str:
        return "llm_assistant"
    
    @property
    def priority(self) -> int:
        return 50  # Medium-high priority
    
    @property
    def dependencies(self) -> list:
        return []  # No core dependencies
    
    async def initialize(self) -> bool:
        """Initialize the plugin"""
        try:
            # Subscribe to events
            event_bus.subscribe("user_input", self.process_user_input, async_callback=True)
            event_bus.subscribe("llm_response", self.handle_llm_response, async_callback=True)
            event_bus.subscribe("llm_error", self.handle_llm_error, async_callback=True)
            
            # Check LLM availability
            result = await event_bus.emit_async("llm_system_check", {})
            self.llm_available = result.get("cpu_compatible", False) and result.get("ram_sufficient", False)
            
            # Inform about plugin status
            if self.llm_available:
                await event_bus.emit_async("system_notification", {
                    "level": "info",
                    "message": "LLM Assistant available"
                })
            else:
                await event_bus.emit_async("system_notification", {
                    "level": "warning",
                    "message": "LLM Assistant unavailable: system requirements not met"
                })
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize LLM Assistant plugin: {e}")
            return False
    
    async def process_user_input(self, event_data):
        """Process user input to determine if LLM should handle it"""
        user_input = event_data.get("input", "").strip()
        context = event_data.get("context", {})
        
        # Skip processing if no input or LLM not available
        if not user_input or not self.llm_available:
            return
        
        # Determine if this input should be handled by LLM
        if self.can_handle(user_input, context):
            request_id = f"req_{int(time.time())}_{random.randint(1000, 9999)}"
            
            # Notify about processing
            await event_bus.emit_async("processing_started", {
                "plugin": self.name,
                "request_id": request_id
            })
            
            # Forward to LLM
            await event_bus.emit_async("llm_request", {
                "request_id": request_id,
                "prompt": user_input,
                "system_message": self.get_system_message(context),
                "temperature": 0.7,
                "max_tokens": 1024,
                "context": context
            })
            
            # Store request for later matching with response
            self.pending_requests[request_id] = {
                "user_input": user_input,
                "timestamp": time.time(),
                "context": context
            }
    
    def can_handle(self, user_input: str, context: dict) -> bool:
        """Determine if this plugin can handle the user input"""
        # This is where we'd implement logic to determine if LLM should handle
        # the request or if it should be handled by other plugins
        
        # Example: handle inputs that are questions or don't match other patterns
        if user_input.endswith("?"):
            return True
            
        # Check if other plugins claimed it
        if context.get("claimed_by_plugin"):
            return False
            
        # Check if it matches specific commands we don't want to handle
        common_commands = ["play music", "set timer", "call", "send email"]
        if any(user_input.lower().startswith(cmd) for cmd in common_commands):
            return False
        
        # Default behavior: handle natural language requests
        return len(user_input.split()) > 3
    
    def get_system_message(self, context: dict) -> str:
        """Generate appropriate system message based on context"""
        base_message = (
            "You are a helpful assistant integrated into a personal assistant application. "
            "Provide concise and accurate responses. "
            "When you don't know something, admit it clearly rather than making up information. "
        )
        
        # Add context-specific instructions
        if context.get("expecting_factual_answer"):
            base_message += "Focus on providing factual information with precision."
        
        if context.get("user_preferences"):
            prefs = context["user_preferences"]
            base_message += f" The user prefers {prefs.get('response_style', 'concise')} responses."
        
        return base_message
    
    async def handle_llm_response(self, event_data):
        """Handle response from LLM"""
        request_id = event_data.get("request_id")
        response = event_data.get("response")
        
        # Check if this is a response we're waiting for
        if request_id not in self.pending_requests:
            return
        
        request_data = self.pending_requests.pop(request_id)
        
        # Process response if needed
        processed_response = self.post_process_response(
            response, 
            request_data["user_input"],
            request_data["context"]
        )
        
        # Emit assistant response event
        await event_bus.emit_async("assistant_response", {
            "response": processed_response,
            "source": "llm",
            "model": event_data.get("model"),
            "original_request": request_data["user_input"],
            "context": request_data["context"]
        })
        
        # Notify processing complete
        await event_bus.emit_async("processing_completed", {
            "plugin": self.name,
            "request_id": request_id,
            "success": True
        })
    
    def post_process_response(self, response: str, user_input: str, context: dict) -> str:
        """Process LLM response before presenting to user"""
        # This could filter out unwanted content, format the response, etc.
        return response
    
    async def handle_llm_error(self, event_data):
        """Handle errors from LLM"""
        request_id = event_data.get("request_id")
        error = event_data.get("error")
        
        if request_id not in self.pending_requests:
            return
            
        request_data = self.pending_requests.pop(request_id)
        
        # Log error
        logger.error(f"LLM error for request {request_id}: {error}")
        
        # Notify user about error
        await event_bus.emit_async("assistant_response", {
            "response": "I'm sorry, I couldn't process that request. There was a problem with the language model.",
            "source": "error_handler",
            "original_request": request_data["user_input"],
            "context": request_data["context"],
            "error": error
        })
        
        # Notify processing complete with error
        await event_bus.emit_async("processing_completed", {
            "plugin": self.name,
            "request_id": request_id,
            "success": False,
            "error": error
        })
```

## 5. Performance Considerations

### 5.1 Resource Management

```python
class ResourceManager:
    """Manages resource allocation for LLM operations"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.max_concurrent_requests = self.config.get("max_concurrent_requests", 1)
        self.active_requests = 0
        self.request_queue = asyncio.Queue()
        self.processing_task = None
    
    async def start(self):
        """Start the resource manager"""
        self.processing_task = asyncio.create_task(self._process_queue())
    
    async def stop(self):
        """Stop the resource manager"""
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
    
    async def submit_request(self, request_func, *args, **kwargs):
        """Submit a request to be processed when resources available"""
        future = asyncio.Future()
        await self.request_queue.put((future, request_func, args, kwargs))
        return await future
    
    async def _process_queue(self):
        """Process requests from the queue"""
        while True:
            # Wait for queue item
            future, request_func, args, kwargs = await self.request_queue.get()
            
            # Check if we can process more requests
            while self.active_requests >= self.max_concurrent_requests:
                await asyncio.sleep(0.1)
            
            # Process request
            self.active_requests += 1
            asyncio.create_task(self._execute_request(future, request_func, args, kwargs))
            
            # Mark task as done
            self.request_queue.task_done()
    
    async def _execute_request(self, future, request_func, args, kwargs):
        """Execute the request and update active count"""
        try:
            result = await request_func(*args, **kwargs)
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)
        finally:
            self.active_requests -= 1
```

### 5.2 Performance Monitoring

```python
@PerformanceMonitor.track_execution_time("llm_processing")
async def process_with_llm(prompt, adapter):
    """Process prompt with LLM and track performance"""
    return await adapter.generate(prompt)

# Memory usage monitoring
def monitor_llm_memory():
    """Monitor memory usage during LLM operations"""
    import psutil
    process = psutil.Process()
    mem_before = process.memory_info().rss / 1024 / 1024
    
    # Yield to allow operation to happen
    yield
    
    mem_after = process.memory_info().rss / 1024 / 1024
    mem_diff = mem_after - mem_before
    
    logger.debug(f"LLM operation memory impact: {mem_diff:.2f} MB")
    if mem_diff > 500:  # 500MB threshold
        logger.warning(f"High memory impact detected: {mem_diff:.2f} MB")
```

### 5.3 Cache Management

```python
class ResponseCache:
    """Cache for LLM responses to avoid redundant requests"""
    
    def __init__(self, max_entries=100, ttl_seconds=3600):
        self.cache = {}
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        self.lock = asyncio.Lock()
    
    async def get(self, key):
        """Get item from cache if exists and not expired"""
        async with self.lock:
            if key not in self.cache:
                return None
            
            item = self.cache[key]
            if time.time() > item["expiry"]:
                del self.cache[key]
                return None
            
            return item["value"]
    
    async def set(self, key, value):
        """Add item to cache with expiry"""
        async with self.lock:
            # Ensure we don't exceed max entries
            if len(self.cache) >= self.max_entries:
                oldest_key = min(self.cache, key=lambda k: self.cache[k]["expiry"])
                del self.cache[oldest_key]
            
            self.cache[key] = {
                "value": value,
                "expiry": time.time() + self.ttl_seconds
            }
    
    def _hash_request(self, prompt, system_message, temperature, max_tokens):
        """Create hash for request parameters"""
        import hashlib
        key_str = f"{prompt}|{system_message}|{temperature}|{max_tokens}"
        return hashlib.md5(key_str.encode()).hexdigest()
```

## 6. Installation and Configuration

### 6.1 LLM Backend Installation

#### Ollama Setup

```python
async def setup_ollama():
    """Set up Ollama on the system"""
    import platform
    import os
    import tempfile
    from vpa.core.events import event_bus
    
    system = platform.system()
    if system != "Windows":
        await event_bus.emit_async("llm_install_error", {
            "error": f"Automatic Ollama installation not supported on {system}"
        })
        return False
    
    # Download Ollama installer
    await event_bus.emit_async("llm_installation_progress", {
        "stage": "download",
        "message": "Downloading Ollama installer"
    })
    
    temp_dir = tempfile.gettempdir()
    installer_path = os.path.join(temp_dir, "ollama-installer.exe")
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get("https://ollama.com/download/ollama-windows-amd64.exe") as response:
                if response.status != 200:
                    raise RuntimeError(f"Failed to download Ollama: {response.status}")
                
                content = await response.read()
                with open(installer_path, "wb") as f:
                    f.write(content)
        
        # Run installer
        await event_bus.emit_async("llm_installation_progress", {
            "stage": "install",
            "message": "Running Ollama installer"
        })
        
        import subprocess
        result = subprocess.run([installer_path, "--quiet"], capture_output=True)
        
        if result.returncode != 0:
            raise RuntimeError(f"Ollama installation failed: {result.stderr.decode()}")
        
        # Start Ollama service
        await event_bus.emit_async("llm_installation_progress", {
            "stage": "start_service",
            "message": "Starting Ollama service"
        })
        
        # Wait for service to start
        import time
        for _ in range(10):  # Try for 10 seconds
            try:
                import requests
                response = requests.get("http://localhost:11434/api/version")
                if response.status_code == 200:
                    await event_bus.emit_async("llm_installation_complete", {
                        "success": True,
                        "message": "Ollama installed and started successfully"
                    })
                    return True
            except:
                pass
            
            time.sleep(1)
        
        raise RuntimeError("Ollama service failed to start")
        
    except Exception as e:
        logger.error(f"Ollama installation failed: {e}")
        await event_bus.emit_async("llm_install_error", {
            "error": f"Ollama installation failed: {str(e)}"
        })
        return False
```

### 6.2 Model Download Management

```python
class ModelManager:
    """Manages model downloads and installations"""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.downloads = {}
    
    async def download_model(self, adapter_name: str, model_id: str):
        """Start model download process"""
        # Generate unique download ID
        download_id = f"{adapter_name}_{model_id}_{int(time.time())}"
        
        # Check if already downloading
        for dl_id, dl_info in self.downloads.items():
            if dl_info["adapter"] == adapter_name and dl_info["model_id"] == model_id:
                await self.event_bus.emit_async("llm_download_already_in_progress", {
                    "download_id": dl_id,
                    "model_id": model_id,
                    "adapter": adapter_name,
                    "progress": dl_info["progress"]
                })
                return dl_id
        
        # Start new download
        self.downloads[download_id] = {
            "adapter": adapter_name,
            "model_id": model_id,
            "progress": 0,
            "status": "starting",
            "start_time": time.time()
        }
        
        # Notify download started
        await self.event_bus.emit_async("llm_download_started", {
            "download_id": download_id,
            "model_id": model_id,
            "adapter": adapter_name
        })
        
        # Start download task
        asyncio.create_task(self._perform_download(download_id, adapter_name, model_id))
        
        return download_id
    
    async def _perform_download(self, download_id: str, adapter_name: str, model_id: str):
        """Perform the actual download"""
        try:
            # Get adapter instance
            adapter = self._get_adapter(adapter_name)
            if not adapter:
                raise ValueError(f"Unknown adapter: {adapter_name}")
            
            # Start installation
            success = await adapter.install_model(model_id)
            
            if success:
                self.downloads[download_id]["status"] = "completed"
                self.downloads[download_id]["progress"] = 100
                
                await self.event_bus.emit_async("llm_download_complete", {
                    "download_id": download_id,
                    "model_id": model_id,
                    "adapter": adapter_name,
                    "duration_seconds": time.time() - self.downloads[download_id]["start_time"]
                })
            else:
                self.downloads[download_id]["status"] = "failed"
                
                await self.event_bus.emit_async("llm_download_failed", {
                    "download_id": download_id,
                    "model_id": model_id,
                    "adapter": adapter_name,
                    "error": "Installation failed"
                })
        
        except Exception as e:
            logger.error(f"Model download failed: {e}")
            
            self.downloads[download_id]["status"] = "failed"
            self.downloads[download_id]["error"] = str(e)
            
            await self.event_bus.emit_async("llm_download_failed", {
                "download_id": download_id,
                "model_id": model_id,
                "adapter": adapter_name,
                "error": str(e)
            })
```

## 7. Security Considerations

### 7.1 Data Privacy

```python
class PrivacyManager:
    """Manages data privacy for LLM operations"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.sensitive_patterns = self._compile_patterns(
            self.config.get("sensitive_patterns", DEFAULT_SENSITIVE_PATTERNS)
        )
    
    def _compile_patterns(self, patterns):
        """Compile regex patterns for sensitive data"""
        import re
        compiled = []
        
        for pattern in patterns:
            try:
                compiled.append(re.compile(pattern, re.IGNORECASE))
            except Exception as e:
                logger.error(f"Failed to compile pattern {pattern}: {e}")
        
        return compiled
    
    def sanitize_prompt(self, prompt: str) -> str:
        """Sanitize prompt by removing sensitive information"""
        sanitized = prompt
        
        for pattern in self.sensitive_patterns:
            sanitized = pattern.sub("[REDACTED]", sanitized)
        
        return sanitized
    
    def is_sensitive_data_present(self, text: str) -> bool:
        """Check if text contains sensitive data"""
        for pattern in self.sensitive_patterns:
            if pattern.search(text):
                return True
        return False
```

### 7.2 Model Validation

```python
async def validate_model_integrity(adapter_name: str, model_id: str) -> dict:
    """Validate model integrity and safety"""
    import hashlib
    
    # Get adapter
    adapter = get_adapter(adapter_name)
    if not adapter:
        return {
            "valid": False,
            "error": f"Unknown adapter: {adapter_name}"
        }
    
    # Get model info including file path
    model_info = adapter.get_model_info(model_id)
    if not model_info or "file_path" not in model_info:
        return {
            "valid": False,
            "error": "Model not found or file path not available"
        }
    
    file_path = model_info["file_path"]
    
    # Calculate file hash
    try:
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            # Read in chunks to avoid memory issues with large models
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        file_hash = sha256_hash.hexdigest()
        
        # For a real implementation, this would check against a trusted source
        # of known good model hashes
        return {
            "valid": True,
            "hash": file_hash,
            "size_bytes": os.path.getsize(file_path)
        }
    
    except Exception as e:
        return {
            "valid": False,
            "error": f"Validation failed: {str(e)}"
        }
```

## 8. GUI Integration

### 8.1 Settings UI

```python
class LLMSettingsPanel:
    """LLM settings UI panel"""
    
    def __init__(self, parent, event_bus):
        self.parent = parent
        self.event_bus = event_bus
        self.models_info = {}
        self.selected_adapter = None
        self.selected_model = None
        
        # Set up event listeners
        self.event_bus.subscribe("llm_system_compatibility", self.update_compatibility_info)
        self.event_bus.subscribe("llm_adapter_changed", self.update_adapter_selection)
        
        # Initialize panel
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """Initialize UI components"""
        # Create settings panel
        self.frame = QFrame(self.parent)
        self.layout = QVBoxLayout(self.frame)
        
        # Add adapter selection
        self.adapter_group = QGroupBox("LLM Provider")
        self.adapter_layout = QVBoxLayout(self.adapter_group)
        self.adapter_combo = QComboBox()
        self.adapter_combo.currentIndexChanged.connect(self._on_adapter_changed)
        self.adapter_layout.addWidget(self.adapter_combo)
        
        # Add model selection
        self.model_group = QGroupBox("Language Model")
        self.model_layout = QVBoxLayout(self.model_group)
        self.model_combo = QComboBox()
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        self.model_layout.addWidget(self.model_combo)
        
        # Add install button
        self.install_button = QPushButton("Install Model")
        self.install_button.clicked.connect(self._on_install_clicked)
        self.model_layout.addWidget(self.install_button)
        
        # Add model info section
        self.model_info_group = QGroupBox("Model Information")
        self.model_info_layout = QFormLayout(self.model_info_group)
        self.model_size_label = QLabel("Size: ")
        self.model_capabilities_label = QLabel("Capabilities: ")
        self.model_info_layout.addRow("Size:", self.model_size_label)
        self.model_info_layout.addRow("Capabilities:", self.model_capabilities_label)
        
        # Add system compatibility info
        self.compat_group = QGroupBox("System Compatibility")
        self.compat_layout = QFormLayout(self.compat_group)
        self.cpu_compat_label = QLabel("Checking...")
        self.ram_compat_label = QLabel("Checking...")
        self.disk_compat_label = QLabel("Checking...")
        self.compat_layout.addRow("CPU:", self.cpu_compat_label)
        self.compat_layout.addRow("RAM:", self.ram_compat_label)
        self.compat_layout.addRow("Disk Space:", self.disk_compat_label)
        
        # Add behavior settings
        self.behavior_group = QGroupBox("LLM Behavior")
        self.behavior_layout = QFormLayout(self.behavior_group)
        self.temperature_slider = QSlider(Qt.Horizontal)
        self.temperature_slider.setMinimum(1)
        self.temperature_slider.setMaximum(10)
        self.temperature_slider.setValue(7)
        self.behavior_layout.addRow("Temperature:", self.temperature_slider)
        
        # Add all components to main layout
        self.layout.addWidget(self.adapter_group)
        self.layout.addWidget(self.model_group)
        self.layout.addWidget(self.model_info_group)
        self.layout.addWidget(self.compat_group)
        self.layout.addWidget(self.behavior_group)
        self.layout.addStretch()
    
    def _load_data(self):
        """Load initial data"""
        # Check system compatibility
        self.event_bus.emit("llm_system_check")
        
        # Load adapters
        self.event_bus.emit("llm_get_adapters")
    
    def update_compatibility_info(self, data):
        """Update compatibility information display"""
        system_info = data.get("system_info", {})
        
        # Update CPU compatibility
        cpu_compatible = data.get("cpu_compatible", False)
        cpu_info = system_info.get("cpu_info", {})
        cpu_text = f"{cpu_info.get('brand', 'Unknown')} - {'Compatible' if cpu_compatible else 'Not Compatible'}"
        self.cpu_compat_label.setText(cpu_text)
        
        # Update RAM compatibility
        ram_sufficient = data.get("ram_sufficient", False)
        ram_gb = system_info.get("ram_gb", 0)
        ram_text = f"{ram_gb:.1f} GB - {'Sufficient' if ram_sufficient else 'Insufficient'}"
        self.ram_compat_label.setText(ram_text)
        
        # Update disk space compatibility
        disk_sufficient = data.get("disk_space_sufficient", False)
        free_disk_gb = system_info.get("free_disk_gb", 0)
        disk_text = f"{free_disk_gb:.1f} GB Free - {'Sufficient' if disk_sufficient else 'Insufficient'}"
        self.disk_compat_label.setText(disk_text)
        
        # Update recommended models
        self.recommended_models = data.get("recommended_models", [])
    
    def update_adapters(self, adapters_data):
        """Update adapter list"""
        self.adapter_combo.clear()
        
        for adapter in adapters_data:
            self.adapter_combo.addItem(adapter["display_name"], adapter["id"])
            
        # Select first adapter by default
        if self.adapter_combo.count() > 0:
            self.adapter_combo.setCurrentIndex(0)
    
    def update_models(self, models_data):
        """Update model list for selected adapter"""
        self.model_combo.clear()
        self.models_info = {}
        
        for model in models_data:
            self.model_combo.addItem(model["display_name"], model["id"])
            self.models_info[model["id"]] = model
            
        # Highlight recommended models
        for i in range(self.model_combo.count()):
            model_id = self.model_combo.itemData(i)
            if model_id in self.recommended_models:
                self.model_combo.setItemText(i, f"✓ {self.model_combo.itemText(i)} (Recommended)")
                
        # Select first model by default
        if self.model_combo.count() > 0:
            self.model_combo.setCurrentIndex(0)
    
    def _on_adapter_changed(self, index):
        """Handle adapter selection change"""
        if index >= 0:
            adapter_id = self.adapter_combo.itemData(index)
            self.selected_adapter = adapter_id
            
            # Request models for this adapter
            self.event_bus.emit("llm_get_models", {"adapter": adapter_id})
    
    def _on_model_changed(self, index):
        """Handle model selection change"""
        if index >= 0:
            model_id = self.model_combo.itemData(index)
            self.selected_model = model_id
            
            # Update model info display
            if model_id in self.models_info:
                model_info = self.models_info[model_id]
                
                # Update size
                size_gb = model_info.get("size_bytes", 0) / (1024**3)
                self.model_size_label.setText(f"{size_gb:.1f} GB")
                
                # Update capabilities
                capabilities = model_info.get("capabilities", [])
                self.model_capabilities_label.setText(", ".join(capabilities))
                
                # Update install button
                is_installed = model_info.get("installed", False)
                self.install_button.setText("Remove Model" if is_installed else "Install Model")
                self.install_button.setEnabled(True)
            else:
                self.model_size_label.setText("Unknown")
                self.model_capabilities_label.setText("Unknown")
                self.install_button.setEnabled(False)
    
    def _on_install_clicked(self):
        """Handle install/remove button click"""
        if not self.selected_adapter or not self.selected_model:
            return
            
        is_installed = self.models_info.get(self.selected_model, {}).get("installed", False)
        
        if is_installed:
            # Request model removal
            self.event_bus.emit("llm_remove_model", {
                "adapter": self.selected_adapter,
                "model_id": self.selected_model
            })
            self.install_button.setText("Removing...")
            self.install_button.setEnabled(False)
        else:
            # Request model installation
            self.event_bus.emit("llm_install_model", {
                "adapter": self.selected_adapter,
                "model_id": self.selected_model
            })
            self.install_button.setText("Installing...")
            self.install_button.setEnabled(False)
```

### 8.2 Chat Interface

```python
class LLMChatInterface:
    """Chat interface for LLM interaction"""
    
    def __init__(self, parent, event_bus):
        self.parent = parent
        self.event_bus = event_bus
        self.chat_history = []
        self.is_processing = False
        self.request_id = None
        
        # Set up event listeners
        self.event_bus.subscribe("assistant_response", self.handle_assistant_response)
        self.event_bus.subscribe("processing_started", self.handle_processing_started)
        self.event_bus.subscribe("processing_completed", self.handle_processing_completed)
        
        # Initialize UI
        self._init_ui()
    
    def _init_ui(self):
        """Initialize UI components"""
        self.frame = QFrame(self.parent)
        self.layout = QVBoxLayout(self.frame)
        
        # Chat history display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        
        # Input area
        self.input_frame = QFrame()
        self.input_layout = QHBoxLayout(self.input_frame)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        
        self.progress_indicator = QProgressBar()
        self.progress_indicator.setRange(0, 0)  # Indeterminate progress
        self.progress_indicator.hide()
        
        # Add components to layouts
        self.input_layout.addWidget(self.input_field)
        self.input_layout.addWidget(self.send_button)
        
        self.layout.addWidget(self.chat_display)
        self.layout.addWidget(self.progress_indicator)
        self.layout.addWidget(self.input_frame)
    
    def send_message(self):
        """Send user message"""
        message = self.input_field.text().strip()
        if not message or self.is_processing:
            return
            
        # Clear input field
        self.input_field.setText("")
        
        # Add message to chat display
        self._add_message_to_display("user", message)
        
        # Emit user input event
        self.event_bus.emit("user_input", {
            "input": message,
            "context": {
                "source": "chat_interface",
                "expecting_response": True
            }
        })
    
    def handle_assistant_response(self, event_data):
        """Handle assistant response"""
        response = event_data.get("response", "")
        source = event_data.get("source", "unknown")
        
        # Only show responses from LLM or error handler
        if source in ["llm", "error_handler"]:
            self._add_message_to_display("assistant", response)
    
    def handle_processing_started(self, event_data):
        """Handle processing started event"""
        plugin = event_data.get("plugin", "")
        request_id = event_data.get("request_id", "")
        
        # Only react to LLM plugin events
        if plugin == "llm_assistant":
            self.is_processing = True
            self.request_id = request_id
            
            # Show progress indicator
            self.progress_indicator.show()
            self.input_field.setEnabled(False)
            self.send_button.setEnabled(False)
    
    def handle_processing_completed(self, event_data):
        """Handle processing completed event"""
        plugin = event_data.get("plugin", "")
        request_id = event_data.get("request_id", "")
        
        # Only react to events for our request
        if plugin == "llm_assistant" and request_id == self.request_id:
            self.is_processing = False
            self.request_id = None
            
            # Hide progress indicator
            self.progress_indicator.hide()
            self.input_field.setEnabled(True)
            self.send_button.setEnabled(True)
            
            # Focus input field
            self.input_field.setFocus()
    
    def _add_message_to_display(self, role, message):
        """Add message to chat display"""
        self.chat_history.append({
            "role": role,
            "content": message,
            "timestamp": time.time()
        })
        
        # Format message for display
        html = ""
        if role == "user":
            html = f'<div style="text-align: right; margin: 8px;"><span style="background-color: #e1e1ff; padding: 8px; border-radius: 12px; display: inline-block; max-width: 80%;">{message}</span></div>'
        else:
            html = f'<div style="text-align: left; margin: 8px;"><span style="background-color: #e1ffe1; padding: 8px; border-radius: 12px; display: inline-block; max-width: 80%;">{message}</span></div>'
        
        # Add to display
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertHtml(html)
        
        # Scroll to bottom
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
```

## 9. Testing Strategy

```python
# Example test for the LLMAdapter base class
import pytest
import asyncio

@pytest.mark.asyncio
async def test_llm_adapter_validate_prompt():
    """Test the validate_prompt method of LLMAdapter"""
    from vpa.core.llm.adapters.base import LLMAdapter
    
    # Create a minimal concrete implementation
    class TestAdapter(LLMAdapter):
        async def initialize(self): 
            return True
        async def generate(self, prompt, **kwargs): 
            return "Test response"
        async def install_model(self, model_id): 
            return True
        def get_available_models(self): 
            return ["test-model"]
        def get_model_info(self, model_id): 
            return {"name": model_id}
    
    # Create adapter with token limit
    adapter = TestAdapter(config={"max_input_tokens": 10})
    
    # Test valid prompt
    valid, result = await adapter.validate_prompt("Short prompt")
    assert valid is True
    assert result == "Short prompt"
    
    # Test prompt too long
    # This assumes token_counter counts each word as a token for simplicity
    valid, error = await adapter.validate_prompt(
        "This is a very long prompt that exceeds the token limit set in the configuration")
    assert valid is False
    assert "exceeds maximum token limit" in error

# Example test for OllamaAdapter
@pytest.mark.asyncio
async def test_ollama_adapter_generate(mocker):
    """Test the generate method of OllamaAdapter"""
    from vpa.core.llm.adapters.ollama import OllamaAdapter
    
    # Mock aiohttp.ClientSession and response
    mock_response = mocker.Mock()
    mock_response.status = 200
    mock_response.json = mocker.AsyncMock(return_value={"response": "Test completion"})
    
    mock_session = mocker.AsyncMock()
    mock_session.__aenter__ = mocker.AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = mocker.AsyncMock(return_value=None)
    mock_session.post = mocker.AsyncMock(return_value=mock_response)
    
    mocker.patch('aiohttp.ClientSession', return_value=mock_session)
    
    # Create adapter
    adapter = OllamaAdapter(config={"base_url": "http://localhost:11434"})
    adapter.initialized = True
    adapter.model_name = "test-model"
    
    # Mock validate_prompt to always return valid
    mocker.patch.object(adapter, 'validate_prompt', 
                       return_value=(True, "Test prompt"))
    
    # Test generate method
    response = await adapter.generate("Test prompt")
    assert response == "Test completion"
    
    # Verify correct API call was made
    mock_session.post.assert_called_once()
    args, kwargs = mock_session.post.call_args
    assert args[0] == "http://localhost:11434/v1/generate"
    assert kwargs["json"]["model"] == "test-model"
    assert kwargs["json"]["prompt"] == "Test prompt"
```

## 10. Conclusion

This LLM Integration Strategy outlines a comprehensive approach to integrating Local Large Language Models into the VPA application, adhering to the established architectural principles of event-driven communication, compartmentalized isolation, and performance optimization.

The implementation provides:

1. **Modular LLM Backend**: Supporting multiple LLM providers via adapters
2. **Event-Driven Communication**: All LLM interactions through the event bus
3. **Graceful Degradation**: Proper error handling and fallbacks
4. **User Experience**: Settings UI for model management and Chat UI for interaction
5. **Performance Monitoring**: Resource management and performance tracking
6. **Security Considerations**: Data privacy and model validation

By following this strategy, the VPA application can incorporate powerful LLM capabilities while maintaining its core architectural principles and performance targets.

---

*LLM Integration Strategy document created on August 27, 2025*
