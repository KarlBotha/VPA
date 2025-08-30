# LLM Adapter Implementation Guide for Ollama and Llama

## Overview

This document provides detailed implementation guidance for integrating Ollama and Llama models into the VPA system. It extends the general LLM Interface Specification with Ollama-specific implementation details, configuration settings, and performance optimizations.

## Table of Contents

1. [Ollama Integration Architecture](#1-ollama-integration-architecture)
2. [Local Llama Model Setup](#2-local-llama-model-setup)
3. [Adapter Implementation](#3-adapter-implementation)
4. [Settings Configuration](#4-settings-configuration)
5. [Performance Optimization](#5-performance-optimization)
6. [Error Handling](#6-error-handling)
7. [Testing Strategy](#7-testing-strategy)

## 1. Ollama Integration Architecture

### 1.1 Ollama Adapter Position in Architecture

The Ollama adapter sits within the LLM subsystem as follows:

```
VPA Application
└── vpa/
    └── core/
        └── llm/
            ├── llm_manager.py            # Coordinates all LLM operations
            ├── model_registry.py         # Tracks available models
            ├── request_processor.py       # Formats requests per interface spec
            ├── response_processor.py      # Processes/validates responses
            └── adapters/
                ├── adapter_base.py       # Base adapter interface
                ├── ollama_adapter.py     # Ollama-specific implementation
                └── llama_adapter.py      # Direct Llama integration
```

### 1.2 Ollama Communication Flow

```
┌───────────────┐         ┌─────────────┐         ┌──────────────┐
│ Event Bus     │         │ LLM Manager │         │ Ollama       │
│ llm.request   │────────▶│             │────────▶│ Adapter      │
└───────────────┘         └─────────────┘         └──────┬───────┘
                                                         │
                                                         ▼
┌───────────────┐         ┌─────────────┐         ┌──────────────┐
│ Event Bus     │         │ Response    │         │ Ollama API   │
│ llm.response  │◀────────│ Processor   │◀────────│ (local:11434)│
└───────────────┘         └─────────────┘         └──────────────┘
```

### 1.3 Required Components

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| Ollama HTTP Client | API communication | `aiohttp` for async requests |
| Model Registry | Track available models | JSON configuration with model metadata |
| Request Formatter | Adapt VPA format to Ollama | Format converter in adapter |
| Response Parser | Process Ollama responses | Extract text and metadata |
| Health Checker | Verify Ollama availability | Periodic connection test |

## 2. Local Llama Model Setup

### 2.1 Model Requirements

| Requirement | Minimum | Recommended |
|------------|---------|-------------|
| RAM | 8GB | 16GB+ |
| Storage | 10GB free | 20GB+ free |
| CPU | 4 cores | 8+ cores |
| GPU | Optional | CUDA-compatible |

### 2.2 Models to Support

| Model | Size | Use Cases | Parameters |
|-------|------|-----------|------------|
| Llama 3 8B | ~4GB | General assistance, fast responses | 8 billion |
| Llama 3 70B | ~35GB | Advanced reasoning, complex tasks | 70 billion |
| CodeLlama | ~7GB | Code generation and analysis | 7-34 billion |

### 2.3 Installation Verification

The adapter must verify Ollama installation and model availability on startup:

```python
async def verify_ollama_installation(self):
    """Verify Ollama is installed and running"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/version", timeout=2.0) as response:
                if response.status == 200:
                    version_info = await response.json()
                    self.ollama_version = version_info.get("version")
                    return True
                else:
                    logger.error(f"Ollama returned status {response.status}")
                    return False
    except Exception as e:
        logger.error(f"Failed to connect to Ollama: {e}")
        return False
```

## 3. Adapter Implementation

### 3.1 Adapter Interface

The Ollama adapter must implement this interface:

```python
class OllamaAdapter(BaseAdapter):
    """Adapter for Ollama API"""
    
    @property
    def name(self) -> str:
        return "ollama"
    
    @property
    def available_models(self) -> List[Dict[str, Any]]:
        """Return list of available models"""
        return self._models
    
    async def initialize(self) -> bool:
        """Initialize adapter and check connection"""
        pass
        
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process LLM request"""
        pass
    
    async def health_check(self) -> bool:
        """Check if service is healthy"""
        pass
```

### 3.2 Request Translation

Translate VPA request format to Ollama format:

```python
def _translate_request(self, vpa_request: Dict[str, Any]) -> Dict[str, Any]:
    """Convert VPA request format to Ollama API format"""
    # Extract messages from VPA request
    vpa_messages = vpa_request.get("messages", [])
    
    # Build Ollama-compatible messages
    ollama_messages = []
    for msg in vpa_messages:
        ollama_messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })
    
    # Build Ollama request
    ollama_request = {
        "model": vpa_request.get("model", self.default_model),
        "messages": ollama_messages,
        "options": {
            "temperature": vpa_request.get("parameters", {}).get("temperature", 0.7),
            "top_p": vpa_request.get("parameters", {}).get("top_p", 1.0),
            "max_tokens": vpa_request.get("parameters", {}).get("max_tokens", 1024)
        },
        "stream": False
    }
    
    # Add system message if present
    system_message = vpa_request.get("system_message")
    if system_message:
        ollama_request["system"] = system_message
        
    return ollama_request
```

### 3.3 Response Translation

Convert Ollama response to standardized VPA format:

```python
def _translate_response(self, ollama_response: Dict[str, Any], request_id: str) -> Dict[str, Any]:
    """Convert Ollama response to VPA format"""
    try:
        response_content = ollama_response.get("message", {}).get("content", "")
        
        # Extract metadata
        metadata = {
            "model": ollama_response.get("model", "unknown"),
            "tokens": {
                "prompt": ollama_response.get("prompt_eval_count", 0),
                "completion": ollama_response.get("eval_count", 0),
                "total": (
                    ollama_response.get("prompt_eval_count", 0) + 
                    ollama_response.get("eval_count", 0)
                )
            },
            "processing_time": ollama_response.get("total_duration", 0) / 1_000_000_000  # Convert ns to s
        }
        
        # Parse for any actions in the response (if using structured output)
        actions = self._extract_actions(response_content)
        
        # Build standard response format
        vpa_response = {
            "request_id": request_id,
            "response": response_content,
            "metadata": metadata,
            "actions": actions,
            "error": None
        }
        
        return vpa_response
    except Exception as e:
        logger.error(f"Error translating Ollama response: {e}")
        return {
            "request_id": request_id,
            "response": None,
            "metadata": {},
            "actions": [],
            "error": {
                "type": "response_parsing_error",
                "message": f"Failed to parse Ollama response: {str(e)}",
                "retry_possible": False
            }
        }
```

### 3.4 Complete Adapter Implementation

```python
from vpa.core.llm.adapters.base_adapter import BaseAdapter
from vpa.core.events import event_bus
from vpa.core.performance import PerformanceMonitor
import aiohttp
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class OllamaAdapter(BaseAdapter):
    """Adapter for Ollama LLM service"""
    
    def __init__(self):
        self.api_base = "http://localhost:11434/api"
        self.default_model = "llama3"  # Default model name
        self._models = []
        self.ollama_version = None
        self.health_check_interval = 60  # seconds
        self.initialized = False
        self._health_check_task = None
    
    @property
    def name(self) -> str:
        return "ollama"
    
    @property
    def available_models(self) -> List[Dict[str, Any]]:
        return self._models
    
    @PerformanceMonitor.track_execution_time("ollama_adapter_initialize")
    async def initialize(self) -> bool:
        """Initialize adapter and check connection"""
        # Check if Ollama is running
        if not await self.verify_ollama_installation():
            logger.error("Ollama not available - adapter initialization failed")
            return False
            
        # Get available models
        if not await self._refresh_models():
            logger.warning("Could not retrieve Ollama models")
        
        # Start health check loop
        self._start_health_check_loop()
        
        self.initialized = True
        return True
    
    async def verify_ollama_installation(self) -> bool:
        """Verify Ollama is installed and running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base}/version", timeout=2.0) as response:
                    if response.status == 200:
                        version_info = await response.json()
                        self.ollama_version = version_info.get("version")
                        logger.info(f"Connected to Ollama version {self.ollama_version}")
                        return True
                    else:
                        logger.error(f"Ollama returned status {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return False
    
    async def _refresh_models(self) -> bool:
        """Get list of available models from Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base}/tags", timeout=5.0) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("models", [])
                        
                        # Transform to standard format
                        self._models = []
                        for model in models:
                            self._models.append({
                                "id": model.get("name"),
                                "name": model.get("name"),
                                "provider": "ollama",
                                "size": model.get("size", 0),
                                "modified_at": model.get("modified_at"),
                                "parameters": model.get("parameters", 0),
                                "quantization_level": model.get("details", {}).get("quantization_level", "unknown")
                            })
                        
                        logger.info(f"Found {len(self._models)} Ollama models")
                        return True
                    else:
                        logger.error(f"Failed to get Ollama models: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Error refreshing Ollama models: {e}")
            return False
    
    def _start_health_check_loop(self) -> None:
        """Start background health check loop"""
        if self._health_check_task is not None:
            self._health_check_task.cancel()
        
        self._health_check_task = asyncio.create_task(self._health_check_loop())
    
    async def _health_check_loop(self) -> None:
        """Periodic health check loop"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                is_healthy = await self.health_check()
                await event_bus.emit_async("llm.adapter.health", {
                    "adapter": self.name,
                    "healthy": is_healthy,
                    "models_count": len(self._models)
                })
                
                # Refresh models list periodically
                await self._refresh_models()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
    
    @PerformanceMonitor.track_execution_time("ollama_adapter_process")
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process LLM request"""
        if not self.initialized:
            await self.initialize()
        
        request_id = request.get("request_id", "unknown")
        
        try:
            # Convert to Ollama format
            ollama_request = self._translate_request(request)
            
            # Send to Ollama API
            async with aiohttp.ClientSession() as session:
                start_time = asyncio.get_event_loop().time()
                
                async with session.post(
                    f"{self.api_base}/chat", 
                    json=ollama_request,
                    timeout=30.0  # Configurable timeout
                ) as response:
                    processing_time = asyncio.get_event_loop().time() - start_time
                    
                    if response.status == 200:
                        # Process successful response
                        response_data = await response.json()
                        
                        # Add processing time if not included
                        if "total_duration" not in response_data:
                            response_data["total_duration"] = processing_time * 1_000_000_000  # Convert to ns
                        
                        # Convert to standard format
                        return self._translate_response(response_data, request_id)
                    else:
                        # Handle error response
                        error_text = await response.text()
                        return {
                            "request_id": request_id,
                            "response": None,
                            "metadata": {},
                            "actions": [],
                            "error": {
                                "type": "api_error",
                                "message": f"Ollama API error {response.status}: {error_text}",
                                "retry_possible": response.status >= 500  # Server errors may be retryable
                            }
                        }
        
        except asyncio.TimeoutError:
            return {
                "request_id": request_id,
                "response": None,
                "metadata": {},
                "actions": [],
                "error": {
                    "type": "timeout",
                    "message": "Request to Ollama API timed out",
                    "retry_possible": True
                }
            }
        except Exception as e:
            logger.error(f"Error processing Ollama request: {e}")
            return {
                "request_id": request_id,
                "response": None,
                "metadata": {},
                "actions": [],
                "error": {
                    "type": "processing_error",
                    "message": f"Error processing request: {str(e)}",
                    "retry_possible": False
                }
            }
    
    def _translate_request(self, vpa_request: Dict[str, Any]) -> Dict[str, Any]:
        """Convert VPA request format to Ollama API format"""
        # Extract messages from VPA request
        vpa_messages = vpa_request.get("messages", [])
        
        # Build Ollama-compatible messages
        ollama_messages = []
        for msg in vpa_messages:
            ollama_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Get model from request or default
        model_name = vpa_request.get("model")
        if not model_name:
            model_name = self.default_model
            
            # Check user preferences if available
            context = vpa_request.get("context", {})
            user_context = context.get("user_context", {})
            if "preferred_model" in user_context:
                model_name = user_context.get("preferred_model")
        
        # Build Ollama request
        parameters = vpa_request.get("parameters", {})
        ollama_request = {
            "model": model_name,
            "messages": ollama_messages,
            "options": {
                "temperature": parameters.get("temperature", 0.7),
                "top_p": parameters.get("top_p", 1.0),
                "num_predict": parameters.get("max_tokens", 1024)
            },
            "stream": False
        }
        
        # Add system message if present
        system_message = vpa_request.get("system_message")
        if system_message:
            ollama_request["system"] = system_message
            
        return ollama_request
    
    def _translate_response(self, ollama_response: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """Convert Ollama response to VPA format"""
        try:
            response_content = ollama_response.get("message", {}).get("content", "")
            
            # Extract metadata
            metadata = {
                "model": ollama_response.get("model", "unknown"),
                "tokens": {
                    "prompt": ollama_response.get("prompt_eval_count", 0),
                    "completion": ollama_response.get("eval_count", 0),
                    "total": (
                        ollama_response.get("prompt_eval_count", 0) + 
                        ollama_response.get("eval_count", 0)
                    )
                },
                "processing_time": ollama_response.get("total_duration", 0) / 1_000_000_000  # Convert ns to s
            }
            
            # Parse for any actions in the response (if using structured output)
            actions = self._extract_actions(response_content)
            
            # Build standard response format
            vpa_response = {
                "request_id": request_id,
                "response": response_content,
                "metadata": metadata,
                "actions": actions,
                "error": None
            }
            
            return vpa_response
        except Exception as e:
            logger.error(f"Error translating Ollama response: {e}")
            return {
                "request_id": request_id,
                "response": None,
                "metadata": {},
                "actions": [],
                "error": {
                    "type": "response_parsing_error",
                    "message": f"Failed to parse Ollama response: {str(e)}",
                    "retry_possible": False
                }
            }
    
    def _extract_actions(self, text: str) -> List[Dict[str, Any]]:
        """Extract potential actions from response text"""
        actions = []
        
        # Simple action extraction based on patterns
        # This is a basic implementation - could be enhanced with more sophisticated parsing
        
        # Check for web search suggestions
        if "search the web for" in text.lower():
            # Extract search terms
            search_terms = self._extract_search_terms(text)
            if search_terms:
                actions.append({
                    "type": "web_search",
                    "parameters": {"query": search_terms}
                })
        
        # Check for application opening suggestions
        app_match = re.search(r"open (\w+)", text.lower())
        if app_match:
            app_name = app_match.group(1)
            actions.append({
                "type": "open_app",
                "parameters": {"app_name": app_name}
            })
        
        return actions
    
    def _extract_search_terms(self, text: str) -> Optional[str]:
        """Extract search terms from text"""
        patterns = [
            r"search the web for[:\s]+['\"](.*?)['\"]",
            r"search for[:\s]+['\"](.*?)['\"]",
            r"search[:\s]+['\"](.*?)['\"]",
            r"look up[:\s]+['\"](.*?)['\"]"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    async def health_check(self) -> bool:
        """Check if Ollama service is healthy"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base}/version", timeout=2.0) as response:
                    return response.status == 200
        except:
            return False
    
    async def shutdown(self) -> None:
        """Clean up resources"""
        if self._health_check_task is not None:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
```

## 4. Settings Configuration

### 4.1 LLM Settings Schema

Add these settings to `settings_schema.py`:

```python
LLM_SETTINGS_SCHEMA = {
    "llm": {
        "type": "object",
        "properties": {
            "provider": {
                "type": "string",
                "enum": ["ollama", "direct", "openai"],
                "default": "ollama",
                "description": "LLM provider to use"
            },
            "default_model": {
                "type": "string",
                "default": "llama3",
                "description": "Default model to use"
            },
            "api_base": {
                "type": "string",
                "default": "http://localhost:11434/api",
                "description": "Base URL for Ollama API"
            },
            "timeout": {
                "type": "number",
                "default": 30.0,
                "description": "Request timeout in seconds"
            },
            "parameters": {
                "type": "object",
                "properties": {
                    "temperature": {
                        "type": "number",
                        "default": 0.7,
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Model temperature (creativity)"
                    },
                    "max_tokens": {
                        "type": "integer",
                        "default": 1024,
                        "minimum": 1,
                        "description": "Maximum tokens to generate"
                    },
                    "top_p": {
                        "type": "number",
                        "default": 1.0,
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Top-p sampling parameter"
                    }
                }
            },
            "system_message": {
                "type": "string",
                "default": "You are a helpful virtual assistant named VPA. Provide concise, accurate responses.",
                "description": "Default system message for LLM"
            }
        }
    }
}
```

### 4.2 LLM Manager Configuration

Configure LLM manager to use the adapter:

```python
from vpa.core.events import event_bus
from vpa.core.settings import settings_manager
from vpa.core.llm.adapters.ollama_adapter import OllamaAdapter
from vpa.core.llm.adapters.llama_adapter import LlamaAdapter
import logging

logger = logging.getLogger(__name__)

class LLMManager:
    """Manager for LLM operations"""
    
    def __init__(self):
        self.adapters = {}
        self.active_adapter = None
        self.active_adapter_name = None
    
    async def initialize(self):
        """Initialize LLM subsystem"""
        # Register adapters
        self._register_adapter(OllamaAdapter())
        self._register_adapter(LlamaAdapter())
        
        # Select active adapter based on settings
        provider = settings_manager.get("llm.provider", "ollama")
        await self.set_active_adapter(provider)
        
        # Subscribe to request events
        event_bus.subscribe("llm.request", self.handle_request, async_callback=True)
        
        logger.info(f"LLM manager initialized with {len(self.adapters)} adapters")
        return True
    
    def _register_adapter(self, adapter):
        """Register an LLM adapter"""
        self.adapters[adapter.name] = adapter
    
    async def set_active_adapter(self, adapter_name):
        """Set the active LLM adapter"""
        if adapter_name not in self.adapters:
            logger.error(f"Adapter '{adapter_name}' not found")
            return False
        
        adapter = self.adapters[adapter_name]
        if not await adapter.initialize():
            logger.error(f"Failed to initialize {adapter_name} adapter")
            return False
        
        self.active_adapter = adapter
        self.active_adapter_name = adapter_name
        logger.info(f"Active LLM adapter set to {adapter_name}")
        
        # Update settings
        settings_manager.set("llm.provider", adapter_name)
        
        # Emit event
        await event_bus.emit_async("llm.adapter.changed", {
            "adapter": adapter_name,
            "models": adapter.available_models
        })
        
        return True
    
    async def handle_request(self, event_data):
        """Handle LLM request"""
        if not self.active_adapter:
            logger.error("No active LLM adapter")
            await self._emit_error_response(
                event_data.get("request_id", "unknown"),
                "no_adapter",
                "No active LLM adapter"
            )
            return
        
        try:
            # Process request with active adapter
            response = await self.active_adapter.process_request(event_data)
            
            # Emit response
            await event_bus.emit_async("llm.response", response)
        except Exception as e:
            logger.error(f"Error processing LLM request: {e}")
            await self._emit_error_response(
                event_data.get("request_id", "unknown"),
                "processing_error",
                f"Error processing request: {str(e)}"
            )
    
    async def _emit_error_response(self, request_id, error_type, error_message):
        """Emit error response"""
        await event_bus.emit_async("llm.response", {
            "request_id": request_id,
            "response": None,
            "metadata": {},
            "actions": [],
            "error": {
                "type": error_type,
                "message": error_message,
                "retry_possible": False
            }
        })
    
    def get_available_models(self):
        """Get list of all available models across adapters"""
        all_models = []
        for adapter_name, adapter in self.adapters.items():
            models = adapter.available_models
            for model in models:
                model["adapter"] = adapter_name
            all_models.extend(models)
        return all_models
```

## 5. Performance Optimization

### 5.1 Response Streaming

For faster perceived response time, implement streaming:

```python
async def process_streaming_request(self, request: Dict[str, Any]) -> None:
    """Process streaming LLM request"""
    request_id = request.get("request_id", "unknown")
    
    try:
        # Convert to Ollama format
        ollama_request = self._translate_request(request)
        ollama_request["stream"] = True
        
        # Track performance
        start_time = asyncio.get_event_loop().time()
        total_tokens = 0
        first_token_time = None
        
        # Send to Ollama API with streaming
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/chat", 
                json=ollama_request,
                timeout=60.0  # Longer timeout for streaming
            ) as response:
                if response.status == 200:
                    # Process streaming response
                    buffer = ""
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if not line:
                            continue
                        
                        try:
                            data = json.loads(line)
                            
                            # Extract token
                            token = data.get("message", {}).get("content", "")
                            buffer += token
                            total_tokens += 1
                            
                            # Record time to first token
                            if total_tokens == 1:
                                first_token_time = asyncio.get_event_loop().time() - start_time
                                
                                # Emit first token metric
                                await event_bus.emit_async("llm.metrics", {
                                    "request_id": request_id,
                                    "metric": "time_to_first_token",
                                    "value": first_token_time
                                })
                            
                            # Emit token
                            if total_tokens % 5 == 0 or data.get("done", False):  # Send every 5 tokens or on completion
                                await event_bus.emit_async("llm.response.stream", {
                                    "request_id": request_id,
                                    "token": token,
                                    "text_so_far": buffer,
                                    "done": data.get("done", False)
                                })
                            
                            # If done, send complete response
                            if data.get("done", False):
                                total_time = asyncio.get_event_loop().time() - start_time
                                
                                # Build final response
                                final_response = {
                                    "request_id": request_id,
                                    "response": buffer,
                                    "metadata": {
                                        "model": data.get("model", "unknown"),
                                        "tokens": {
                                            "prompt": data.get("prompt_eval_count", 0),
                                            "completion": data.get("eval_count", 0),
                                            "total": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                                        },
                                        "processing_time": total_time
                                    },
                                    "actions": self._extract_actions(buffer),
                                    "error": None
                                }
                                
                                # Emit final response
                                await event_bus.emit_async("llm.response", final_response)
                                break
                        except json.JSONDecodeError:
                            continue
                else:
                    # Handle error response
                    error_text = await response.text()
                    await self._emit_error_response(
                        request_id,
                        "api_error",
                        f"Ollama API error {response.status}: {error_text}"
                    )
    
    except Exception as e:
        logger.error(f"Error processing streaming Ollama request: {e}")
        await self._emit_error_response(
            request_id,
            "streaming_error",
            f"Error processing streaming request: {str(e)}"
        )
```

### 5.2 Model Parameter Optimization

Optimize model parameters based on request type:

```python
def _optimize_parameters(self, request_type, parameters):
    """Optimize model parameters based on request type"""
    optimized = parameters.copy()
    
    if request_type == "short_answer":
        # Optimize for quick responses
        optimized["temperature"] = 0.3
        optimized["num_predict"] = 256
    elif request_type == "creative":
        # Optimize for creativity
        optimized["temperature"] = 0.9
        optimized["top_p"] = 0.9
    elif request_type == "factual":
        # Optimize for accuracy
        optimized["temperature"] = 0.1
    
    return optimized
```

### 5.3 Caching Strategy

Implement response caching for common requests:

```python
import hashlib

class ResponseCache:
    """Cache for LLM responses"""
    
    def __init__(self, max_size=100, ttl=3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl  # seconds
        
    def _generate_key(self, request):
        """Generate cache key from request"""
        # Extract relevant parts for caching
        model = request.get("model", "")
        messages = request.get("messages", [])
        system = request.get("system_message", "")
        temp = request.get("parameters", {}).get("temperature", 0)
        
        # Create hash key
        key_parts = [
            model,
            json.dumps(messages, sort_keys=True),
            system,
            str(temp)
        ]
        
        key_str = "|".join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, request):
        """Get cached response if available"""
        key = self._generate_key(request)
        cached = self.cache.get(key)
        
        if not cached:
            return None
            
        # Check TTL
        timestamp, response = cached
        if time.time() - timestamp > self.ttl:
            # Expired
            del self.cache[key]
            return None
            
        return response
    
    def set(self, request, response):
        """Cache response"""
        # Don't cache error responses
        if response.get("error"):
            return
            
        key = self._generate_key(request)
        self.cache[key] = (time.time(), response)
        
        # Enforce max size
        if len(self.cache) > self.max_size:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][0])
            del self.cache[oldest_key]
```

## 6. Error Handling

### 6.1 Specific Ollama Error Handling

Implement specialized error handling for Ollama-specific issues:

```python
async def _handle_ollama_error(self, response, error_text):
    """Handle specific Ollama errors"""
    
    # Check for known error patterns
    if "no model found" in error_text.lower():
        # Model not found error
        return {
            "type": "model_not_found",
            "message": "The requested model is not installed in Ollama",
            "retry_possible": False,
            "resolution_steps": [
                "Install the model using Ollama CLI: ollama pull [model_name]",
                "Verify available models with: ollama list",
                "Check model name spelling in your request"
            ]
        }
    elif "failed to connect" in error_text.lower():
        # Connection error
        
        # Check if Ollama is running at all
        if await self._is_ollama_process_running():
            return {
                "type": "connection_error",
                "message": "Cannot connect to Ollama API",
                "retry_possible": True,
                "resolution_steps": [
                    "Ensure Ollama is running",
                    "Check if another process is using port 11434",
                    "Restart the Ollama service"
                ]
            }
        else:
            # Ollama not running
            return {
                "type": "ollama_not_running",
                "message": "Ollama service is not running",
                "retry_possible": True,
                "resolution_steps": [
                    "Start Ollama manually",
                    "Check Ollama installation",
                    "Consider setting up auto-start for Ollama"
                ]
            }
    elif "out of memory" in error_text.lower():
        # OOM error
        return {
            "type": "out_of_memory",
            "message": "Ollama ran out of memory while processing the request",
            "retry_possible": False,
            "resolution_steps": [
                "Try using a smaller model",
                "Reduce context length in your prompt",
                "Close other memory-intensive applications",
                "Consider adding more RAM to your system"
            ]
        }
    
    # General API error
    return {
        "type": "api_error",
        "message": f"Ollama API error: {error_text}",
        "retry_possible": response.status >= 500,
        "resolution_steps": [
            "Check Ollama logs for more details",
            "Verify your request format",
            "Restart Ollama if the issue persists"
        ]
    }

async def _is_ollama_process_running(self):
    """Check if Ollama process is running"""
    try:
        if sys.platform == "win32":
            # Windows
            output = subprocess.check_output("tasklist /fi \"imagename eq ollama.exe\"", shell=True)
            return b"ollama.exe" in output
        else:
            # Unix-like
            output = subprocess.check_output("pgrep -x ollama", shell=True)
            return bool(output.strip())
    except:
        return False
```

### 6.2 Fallback Chain

Implement a fallback chain for robust operation:

```python
async def process_request_with_fallback(self, request: Dict[str, Any]) -> Dict[str, Any]:
    """Process request with fallback chain"""
    request_id = request.get("request_id", "unknown")
    original_model = request.get("model")
    
    # Try with specified model first
    response = await self.process_request(request)
    
    # If successful or non-recoverable error, return
    if not response.get("error") or not response.get("error", {}).get("retry_possible", False):
        return response
    
    # Try fallback models if appropriate
    if response.get("error", {}).get("type") in ["model_not_found", "out_of_memory"]:
        logger.info(f"Attempting fallback for request {request_id}")
        
        # Try smaller models in sequence
        fallback_models = ["llama3:8b", "gemma:2b"]
        
        for fallback_model in fallback_models:
            if fallback_model != original_model:
                # Clone request with fallback model
                fallback_request = copy.deepcopy(request)
                fallback_request["model"] = fallback_model
                
                logger.info(f"Trying fallback model {fallback_model} for request {request_id}")
                fallback_response = await self.process_request(fallback_request)
                
                # If successful, return with fallback notice
                if not fallback_response.get("error"):
                    fallback_response["metadata"]["fallback_used"] = True
                    fallback_response["metadata"]["original_model"] = original_model
                    return fallback_response
    
    # All fallbacks failed or inappropriate fallback scenario
    return response
```

## 7. Testing Strategy

### 7.1 Adapter Tests

Test adapter functionality with mocked API responses:

```python
import pytest
import aiohttp
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_ollama_adapter_initialization():
    """Test OllamaAdapter initialization"""
    adapter = OllamaAdapter()
    
    # Mock API responses
    with patch('aiohttp.ClientSession.get') as mock_get:
        # Mock version response
        mock_version_response = MagicMock()
        mock_version_response.status = 200
        mock_version_response.json.return_value = {"version": "0.1.14"}
        
        # Mock models response
        mock_models_response = MagicMock()
        mock_models_response.status = 200
        mock_models_response.json.return_value = {
            "models": [
                {
                    "name": "llama3",
                    "size": 4563402752,
                    "modified_at": "2023-09-01T15:00:00Z",
                    "details": {"quantization_level": "Q4_0"}
                }
            ]
        }
        
        # Setup mock to return different responses based on URL
        def get_side_effect(*args, **kwargs):
            url = args[0]
            if "version" in url:
                return mock_version_response
            elif "tags" in url:
                return mock_models_response
            return MagicMock()
            
        mock_get.side_effect = get_side_effect
        
        # Test initialization
        result = await adapter.initialize()
        
        # Assertions
        assert result is True
        assert adapter.ollama_version == "0.1.14"
        assert len(adapter.available_models) == 1
        assert adapter.available_models[0]["name"] == "llama3"
        assert adapter.initialized is True

@pytest.mark.asyncio
async def test_ollama_adapter_process_request():
    """Test processing a request"""
    adapter = OllamaAdapter()
    adapter.initialized = True
    
    # Test request
    request = {
        "request_id": "test-123",
        "system_message": "You are a helpful assistant",
        "messages": [
            {
                "role": "user",
                "content": "Hello, how are you?",
                "timestamp": "2023-09-01T15:00:00Z"
            }
        ],
        "parameters": {
            "temperature": 0.7,
            "max_tokens": 512
        }
    }
    
    # Mock API response
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "model": "llama3",
            "message": {
                "role": "assistant",
                "content": "I'm doing well, thank you! How can I assist you today?"
            },
            "prompt_eval_count": 14,
            "eval_count": 16,
            "total_duration": 2500000000  # 2.5 seconds
        }
        
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Process request
        response = await adapter.process_request(request)
        
        # Assertions
        assert response["request_id"] == "test-123"
        assert "I'm doing well" in response["response"]
        assert response["metadata"]["model"] == "llama3"
        assert response["metadata"]["tokens"]["total"] == 30
        assert response["metadata"]["processing_time"] == 2.5
        assert response["error"] is None
```

### 7.2 Error Case Tests

```python
@pytest.mark.asyncio
async def test_ollama_adapter_model_not_found_error():
    """Test handling model not found error"""
    adapter = OllamaAdapter()
    adapter.initialized = True
    
    # Test request with non-existent model
    request = {
        "request_id": "test-456",
        "model": "nonexistent-model",
        "messages": [{"role": "user", "content": "Hello"}]
    }
    
    # Mock API error response
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status = 404
        mock_response.text.return_value = "no model found"
        
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Process request
        response = await adapter.process_request(request)
        
        # Assertions
        assert response["request_id"] == "test-456"
        assert response["response"] is None
        assert response["error"]["type"] == "api_error"
        assert "no model found" in response["error"]["message"]
```

### 7.3 Integration Tests

```python
@pytest.mark.asyncio
async def test_llm_manager_with_ollama_adapter():
    """Test LLM manager with Ollama adapter"""
    # Create LLM manager
    manager = LLMManager()
    
    # Mock adapters
    mock_ollama_adapter = MagicMock()
    mock_ollama_adapter.name = "ollama"
    mock_ollama_adapter.initialize.return_value = True
    mock_ollama_adapter.available_models = [{"id": "llama3", "name": "llama3"}]
    
    # Mock event bus
    mock_event_bus = MagicMock()
    
    # Patch dependencies
    with patch('vpa.core.llm.adapters.ollama_adapter.OllamaAdapter', return_value=mock_ollama_adapter), \
         patch('vpa.core.events.event_bus', mock_event_bus):
        
        # Initialize manager
        await manager.initialize()
        
        # Test adapter initialization
        assert manager.active_adapter_name == "ollama"
        assert manager.active_adapter == mock_ollama_adapter
        
        # Test request handling
        test_request = {
            "request_id": "test-789",
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        # Setup mock response
        mock_response = {
            "request_id": "test-789",
            "response": "Hello! How can I help you?",
            "metadata": {},
            "actions": [],
            "error": None
        }
        mock_ollama_adapter.process_request.return_value = mock_response
        
        # Handle request
        await manager.handle_request(test_request)
        
        # Verify adapter was called
        mock_ollama_adapter.process_request.assert_called_with(test_request)
        
        # Verify response was emitted
        mock_event_bus.emit_async.assert_called_with("llm.response", mock_response)
```

## Conclusion

This implementation guide provides detailed specifications for integrating Ollama and Llama models into the VPA system. By following these guidelines, the VPA application will maintain its architectural principles while providing robust LLM capabilities through local models.

The adapter pattern allows for easy extension to other LLM providers while maintaining consistent behavior, error handling, and performance monitoring across all implementations.

---

*LLM Adapter Implementation Guide created on August 29, 2025*  
*Version: 1.0*  
*Related Documents: LLM_INTERFACE_SPECIFICATION.md (v1.0), WINDOWS_API_INTEGRATION_ERROR_HANDLING.md (v1.0)*
