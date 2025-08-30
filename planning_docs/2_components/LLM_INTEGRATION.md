# VPA LLM Integration

## Overview

This document outlines the approach for integrating Large Language Models (LLMs) into the VPA system. It details the architecture, components, adapters, and implementation strategy for providing AI capabilities to the Virtual Personal Assistant.

## Purpose

- Define a flexible LLM integration architecture
- Establish performance targets for LLM operations
- Specify adapters for multiple LLM providers
- Detail the implementation approach for LLM-powered features
- Ensure seamless integration with the event-driven architecture

## Architecture

### Core Components

1. **LLM Manager** (`src/vpa/core/llm/llm_manager.py`)
   - Central coordinator for LLM operations
   - Handles routing to appropriate LLM adapters
   - Manages caching and optimization strategies
   - Implements fallback mechanisms

2. **LLM Adapters** (`src/vpa/core/llm/adapters/`)
   - Provider-specific implementations
   - Abstract away provider APIs
   - Handle authentication and rate limiting
   - Implement provider-specific optimizations

3. **Prompt Management** (`src/vpa/core/llm/prompts/`)
   - Template management for system prompts
   - Context management for conversations
   - Memory management for long-term context
   - Function calling templates

4. **Response Processing** (`src/vpa/core/llm/processing/`)
   - Parser for structured responses
   - Output validation and formatting
   - Error detection and recovery
   - Content filtering

### Integration with Event System

```
┌───────────────┐       ┌────────────────┐      ┌──────────────┐
│  User Input   │       │  Event Bus     │      │ LLM Manager  │
│ (voice/text)  │──────▶│ (llm_request)  │─────▶│              │
└───────────────┘       └────────────────┘      └──────┬───────┘
                                                      │
                                                      ▼
                                               ┌──────────────┐
                                               │ LLM Adapters │
                                               │              │
                                               └──────┬───────┘
                                                      │
                                                      ▼
┌───────────────┐       ┌────────────────┐      ┌──────────────┐
│   Response    │       │  Event Bus     │      │ LLM Response │
│ (voice/text)  │◀──────│ (llm_response) │◀─────│  Processing  │
└───────────────┘       └────────────────┘      └──────────────┘
```

## LLM Provider Adapters

### Base Adapter Interface

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class LLMAdapter(ABC):
    """Base class for all LLM adapters."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of this LLM adapter."""
        pass
        
    @property
    @abstractmethod
    def capabilities(self) -> Dict[str, bool]:
        """Get the capabilities of this LLM adapter.
        
        Returns:
            Dict with capabilities like {
                "streaming": True/False,
                "function_calling": True/False,
                "vision": True/False,
                "embeddings": True/False,
                "local": True/False
            }
        """
        pass
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the adapter, loading models if needed.
        
        Returns:
            True if initialization succeeded, False otherwise.
        """
        pass
    
    @abstractmethod
    async def generate_response(
        self, 
        prompt: str, 
        system_message: str,
        conversation_history: List[Dict[str, str]],
        functions: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a response from the LLM.
        
        Args:
            prompt: The user's input prompt
            system_message: The system instructions
            conversation_history: List of previous messages
            functions: Optional list of function definitions
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dict containing:
                "text": The generated text response
                "function_call": Function call info if applicable
                "metadata": Additional response metadata
        """
        pass
        
    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding vector for the given text.
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        pass
        
    @abstractmethod
    async def shutdown(self) -> None:
        """Clean up resources used by this adapter."""
        pass
```

### Local LLM Adapter

```python
from .base_adapter import LLMAdapter
import asyncio
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class LocalLLMAdapter(LLMAdapter):
    """Adapter for local LLM using llama.cpp or similar."""
    
    def __init__(self, 
                model_path: str,
                context_length: int = 4096,
                threads: int = 4,
                **kwargs):
        """Initialize the local LLM adapter.
        
        Args:
            model_path: Path to the model file
            context_length: Maximum context length
            threads: Number of threads to use
        """
        self._model_path = model_path
        self._context_length = context_length
        self._threads = threads
        self._additional_params = kwargs
        self._model = None
        
    @property
    def name(self) -> str:
        return "local_llm"
        
    @property
    def capabilities(self) -> Dict[str, bool]:
        return {
            "streaming": True,
            "function_calling": False,  # Depends on model
            "vision": False,
            "embeddings": True,
            "local": True
        }
        
    async def initialize(self) -> bool:
        try:
            # Import here to avoid loading unless needed
            from llama_cpp import Llama
            
            # Run model loading in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self._model = await loop.run_in_executor(
                None,
                lambda: Llama(
                    model_path=self._model_path,
                    n_ctx=self._context_length,
                    n_threads=self._threads,
                    **self._additional_params
                )
            )
            return True
        except Exception as e:
            logger.error(f"Failed to initialize local LLM: {e}")
            return False
            
    async def generate_response(
        self, 
        prompt: str, 
        system_message: str,
        conversation_history: List[Dict[str, str]],
        functions: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        if not self._model:
            raise RuntimeError("Local LLM not initialized")
            
        # Format the conversation for the local model
        formatted_prompt = self._format_conversation(
            system_message, conversation_history, prompt
        )
        
        # Run inference in a thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        
        # Get parameters with defaults
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 1024)
        
        response = await loop.run_in_executor(
            None,
            lambda: self._model.generate(
                formatted_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
        )
        
        return {
            "text": response.strip(),
            "function_call": None,
            "metadata": {
                "model": self._model_path,
                "tokens_used": len(response),
                "provider": "local"
            }
        }
        
    async def generate_embedding(self, text: str) -> List[float]:
        if not self._model:
            raise RuntimeError("Local LLM not initialized")
            
        # Run embedding generation in a thread pool
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None,
            lambda: self._model.embed(text)
        )
        
        return embedding.tolist()
        
    async def shutdown(self) -> None:
        # Clean up resources
        self._model = None
        
    def _format_conversation(
        self,
        system_message: str,
        conversation_history: List[Dict[str, str]],
        current_prompt: str
    ) -> str:
        """Format the conversation history for the local model."""
        formatted = f"<s>[INST] <<SYS>>\n{system_message}\n<</SYS>>\n\n"
        
        # Add conversation history
        for message in conversation_history:
            if message["role"] == "user":
                formatted += f"{message['content']} [/INST] "
            else:
                formatted += f"{message['content']} </s><s>[INST] "
                
        # Add current prompt
        formatted += f"{current_prompt} [/INST] "
        
        return formatted
```

### Cloud API Adapter (OpenAI)

```python
from .base_adapter import LLMAdapter
import asyncio
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class OpenAIAdapter(LLMAdapter):
    """Adapter for OpenAI API."""
    
    def __init__(self, 
                api_key: Optional[str] = None,
                model: str = "gpt-3.5-turbo",
                **kwargs):
        """Initialize the OpenAI adapter.
        
        Args:
            api_key: Optional API key (falls back to env var)
            model: Model name to use
        """
        self._api_key = api_key
        self._model = model
        self._client = None
        self._additional_params = kwargs
        
    @property
    def name(self) -> str:
        return "openai"
        
    @property
    def capabilities(self) -> Dict[str, bool]:
        capabilities = {
            "streaming": True,
            "function_calling": True,
            "embeddings": True,
            "local": False
        }
        
        # Add vision capability for compatible models
        if "gpt-4" in self._model and "vision" in self._model:
            capabilities["vision"] = True
        else:
            capabilities["vision"] = False
            
        return capabilities
        
    async def initialize(self) -> bool:
        try:
            # Import here to avoid loading unless needed
            from openai import AsyncOpenAI
            
            self._client = AsyncOpenAI(api_key=self._api_key)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI adapter: {e}")
            return False
            
    async def generate_response(
        self, 
        prompt: str, 
        system_message: str,
        conversation_history: List[Dict[str, str]],
        functions: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        if not self._client:
            raise RuntimeError("OpenAI client not initialized")
            
        # Format messages for OpenAI API
        messages = [{"role": "system", "content": system_message}]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        # Get parameters with defaults
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 1024)
        
        # Prepare function calling if provided
        tools = None
        if functions:
            tools = [{"type": "function", "function": func} for func in functions]
        
        try:
            # Make API call
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools
            )
            
            result = {
                "text": response.choices[0].message.content or "",
                "function_call": None,
                "metadata": {
                    "model": self._model,
                    "tokens_used": {
                        "prompt": response.usage.prompt_tokens,
                        "completion": response.usage.completion_tokens,
                        "total": response.usage.total_tokens
                    },
                    "provider": "openai"
                }
            }
            
            # Handle function calling
            if response.choices[0].message.tool_calls:
                tool_call = response.choices[0].message.tool_calls[0]
                result["function_call"] = {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                }
                
            return result
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
        
    async def generate_embedding(self, text: str) -> List[float]:
        if not self._client:
            raise RuntimeError("OpenAI client not initialized")
            
        try:
            response = await self._client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise
        
    async def shutdown(self) -> None:
        # Clean up resources
        self._client = None
```

### LLM Factory

```python
from typing import Dict, Type, Optional
from .adapters.base_adapter import LLMAdapter
from .adapters.openai_adapter import OpenAIAdapter
from .adapters.local_llm_adapter import LocalLLMAdapter
import logging

logger = logging.getLogger(__name__)

class LLMFactory:
    """Factory for creating LLM adapters."""
    
    def __init__(self):
        self._adapter_types: Dict[str, Type[LLMAdapter]] = {
            "openai": OpenAIAdapter,
            "local": LocalLLMAdapter,
            # Add more adapter types here
        }
        
        self._adapter_instances: Dict[str, LLMAdapter] = {}
        
    async def create_adapter(self, 
                           adapter_type: str, 
                           config: Dict[str, Any]) -> Optional[LLMAdapter]:
        """Create and initialize an adapter of the specified type.
        
        Args:
            adapter_type: The type of adapter to create
            config: Configuration for the adapter
            
        Returns:
            Initialized adapter or None if initialization failed
        """
        if adapter_type not in self._adapter_types:
            logger.error(f"Unknown adapter type: {adapter_type}")
            return None
            
        # Create the adapter instance
        adapter_class = self._adapter_types[adapter_type]
        adapter = adapter_class(**config)
        
        # Initialize the adapter
        success = await adapter.initialize()
        if not success:
            logger.error(f"Failed to initialize {adapter_type} adapter")
            return None
            
        # Cache the adapter instance
        self._adapter_instances[adapter_type] = adapter
        return adapter
        
    def get_adapter(self, adapter_type: str) -> Optional[LLMAdapter]:
        """Get a previously created adapter.
        
        Args:
            adapter_type: The type of adapter to get
            
        Returns:
            The adapter instance or None if not found
        """
        return self._adapter_instances.get(adapter_type)
        
    async def shutdown_all(self) -> None:
        """Shut down all adapter instances."""
        for adapter_type, adapter in self._adapter_instances.items():
            logger.info(f"Shutting down {adapter_type} adapter")
            await adapter.shutdown()
            
        self._adapter_instances.clear()
```

## LLM Manager Implementation

### Manager Interface

```python
from typing import Dict, Any, Optional, List, Callable, Awaitable
from .adapters.base_adapter import LLMAdapter
from .factory import LLMFactory
from vpa.core.events import event_bus
import logging
import time
import asyncio
import json

logger = logging.getLogger(__name__)

class LLMManager:
    """Manager for LLM operations."""
    
    def __init__(self):
        self._factory = LLMFactory()
        self._default_adapter: Optional[str] = None
        self._response_callbacks: Dict[str, Callable[[Dict[str, Any]], Awaitable[None]]] = {}
        
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the LLM manager.
        
        Args:
            config: Configuration for LLM adapters
            
        Returns:
            True if initialization succeeded, False otherwise
        """
        success = True
        
        # Initialize adapters from config
        for adapter_type, adapter_config in config.get("adapters", {}).items():
            adapter = await self._factory.create_adapter(adapter_type, adapter_config)
            if not adapter:
                success = False
                
        # Set default adapter
        self._default_adapter = config.get("default_adapter")
        if not self._default_adapter or not self._factory.get_adapter(self._default_adapter):
            if self._factory._adapter_instances:
                # Use first available adapter as default
                self._default_adapter = next(iter(self._factory._adapter_instances.keys()))
            else:
                logger.error("No valid LLM adapters initialized")
                return False
                
        # Register event handlers
        event_bus.subscribe("llm_request", self._handle_llm_request, async_callback=True)
        
        return success
        
    async def _handle_llm_request(self, event_data: Dict[str, Any]) -> None:
        """Handle an LLM request event."""
        request_id = event_data.get("request_id")
        if not request_id:
            logger.error("LLM request missing request_id")
            return
            
        # Get the adapter to use
        adapter_name = event_data.get("adapter", self._default_adapter)
        adapter = self._factory.get_adapter(adapter_name)
        
        if not adapter:
            logger.error(f"Adapter {adapter_name} not found, falling back to default")
            adapter = self._factory.get_adapter(self._default_adapter)
            
        if not adapter:
            logger.error("No valid adapter available for LLM request")
            await event_bus.emit_async("llm_response", {
                "request_id": request_id,
                "error": "No valid LLM adapter available",
                "success": False
            })
            return
            
        # Extract request parameters
        prompt = event_data.get("prompt", "")
        system_message = event_data.get("system_message", "You are a helpful assistant.")
        conversation_history = event_data.get("conversation_history", [])
        functions = event_data.get("functions")
        additional_params = event_data.get("parameters", {})
        
        # Register callback if provided
        callback_id = event_data.get("callback_id")
        if callback_id:
            callback = self._response_callbacks.get(callback_id)
            if callback:
                # This will be called directly instead of emitting an event
                direct_callback = True
            else:
                direct_callback = False
        else:
            direct_callback = False
            
        # Process the request
        try:
            start_time = time.time()
            
            response = await adapter.generate_response(
                prompt=prompt,
                system_message=system_message,
                conversation_history=conversation_history,
                functions=functions,
                **additional_params
            )
            
            processing_time = time.time() - start_time
            
            # Add metadata
            response["metadata"]["processing_time"] = processing_time
            response["metadata"]["adapter"] = adapter_name
            
            result = {
                "request_id": request_id,
                "response": response.get("text", ""),
                "function_call": response.get("function_call"),
                "metadata": response.get("metadata", {}),
                "success": True
            }
            
            # Either use direct callback or emit event
            if direct_callback and callback:
                await callback(result)
            else:
                await event_bus.emit_async("llm_response", result)
                
        except Exception as e:
            logger.error(f"Error processing LLM request: {e}")
            error_response = {
                "request_id": request_id,
                "error": str(e),
                "success": False
            }
            
            # Either use direct callback or emit event
            if direct_callback and callback:
                await callback(error_response)
            else:
                await event_bus.emit_async("llm_response", error_response)
                
    async def register_response_callback(self, 
                                      callback_id: str, 
                                      callback: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """Register a callback for LLM responses.
        
        Args:
            callback_id: ID to reference this callback
            callback: Async function to call with response
        """
        self._response_callbacks[callback_id] = callback
        
    async def unregister_response_callback(self, callback_id: str) -> None:
        """Unregister a response callback.
        
        Args:
            callback_id: ID of callback to remove
        """
        if callback_id in self._response_callbacks:
            del self._response_callbacks[callback_id]
            
    async def generate_embedding(self, text: str, adapter_name: Optional[str] = None) -> List[float]:
        """Generate an embedding for the given text.
        
        Args:
            text: Text to embed
            adapter_name: Optional adapter name to use
            
        Returns:
            Embedding vector
        """
        # Get the adapter to use
        adapter_name = adapter_name or self._default_adapter
        adapter = self._factory.get_adapter(adapter_name)
        
        if not adapter:
            logger.error(f"Adapter {adapter_name} not found, falling back to default")
            adapter = self._factory.get_adapter(self._default_adapter)
            
        if not adapter:
            logger.error("No valid adapter available for embedding generation")
            raise RuntimeError("No valid LLM adapter available")
            
        return await adapter.generate_embedding(text)
        
    async def shutdown(self) -> None:
        """Shut down the LLM manager."""
        # Unsubscribe from events
        event_bus.unsubscribe("llm_request", self._handle_llm_request)
        
        # Shut down all adapters
        await self._factory.shutdown_all()
        
        # Clear callbacks
        self._response_callbacks.clear()
```

## Prompt Management

### System Prompts

System prompts are stored in JSON format in `src/vpa/core/llm/prompts/system_prompts.json`:

```json
{
  "assistant": {
    "prompt": "You are a helpful, friendly, and concise virtual personal assistant named VPA. You assist the user with their tasks, answer questions, and help manage their computer. Prioritize clarity and brevity in your responses. If you don't know something, say so rather than making up information.",
    "metadata": {
      "description": "Default assistant personality",
      "use_case": "general"
    }
  },
  "technical": {
    "prompt": "You are VPA, a technical assistant specializing in computer-related topics. Provide detailed technical explanations when appropriate, but still aim to be clear and understandable. Focus on accuracy above all else.",
    "metadata": {
      "description": "Technical specialist personality",
      "use_case": "technical_support"
    }
  },
  "concise": {
    "prompt": "You are VPA, a virtual assistant focused on extremely brief responses. Provide only the most essential information in as few words as possible. Use bullet points or very short sentences.",
    "metadata": {
      "description": "Extremely concise personality",
      "use_case": "quick_responses"
    }
  }
}
```

### Prompt Templates

```python
from string import Template
from typing import Dict, Any
import json
import os

class PromptManager:
    """Manager for system prompts and templates."""
    
    def __init__(self, prompt_dir: str):
        """Initialize the prompt manager.
        
        Args:
            prompt_dir: Directory containing prompt files
        """
        self._prompt_dir = prompt_dir
        self._system_prompts: Dict[str, Dict[str, Any]] = {}
        self._templates: Dict[str, Template] = {}
        
    def load_prompts(self) -> bool:
        """Load system prompts from files.
        
        Returns:
            True if loading succeeded, False otherwise
        """
        try:
            # Load system prompts
            system_prompt_path = os.path.join(self._prompt_dir, "system_prompts.json")
            with open(system_prompt_path, "r") as f:
                self._system_prompts = json.load(f)
                
            # Load templates
            template_dir = os.path.join(self._prompt_dir, "templates")
            for filename in os.listdir(template_dir):
                if filename.endswith(".txt"):
                    template_name = os.path.splitext(filename)[0]
                    with open(os.path.join(template_dir, filename), "r") as f:
                        self._templates[template_name] = Template(f.read())
                        
            return True
        except Exception as e:
            print(f"Error loading prompts: {e}")
            return False
            
    def get_system_prompt(self, prompt_name: str = "assistant") -> str:
        """Get a system prompt by name.
        
        Args:
            prompt_name: Name of the system prompt
            
        Returns:
            The system prompt string
        """
        prompt_data = self._system_prompts.get(prompt_name, self._system_prompts.get("assistant"))
        return prompt_data.get("prompt", "You are a helpful assistant.")
        
    def get_template(self, template_name: str, **kwargs) -> str:
        """Get a rendered template.
        
        Args:
            template_name: Name of the template
            **kwargs: Variables to substitute in the template
            
        Returns:
            The rendered template
        """
        template = self._templates.get(template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found")
            
        return template.substitute(**kwargs)
```

## Context Management

```python
from typing import List, Dict, Any, Optional
import time

class ConversationContext:
    """Manages conversation context and history."""
    
    def __init__(self, max_history: int = 10):
        """Initialize the conversation context.
        
        Args:
            max_history: Maximum number of turns to keep in history
        """
        self._max_history = max_history
        self._history: List[Dict[str, str]] = []
        self._metadata: Dict[str, Any] = {}
        self._last_interaction_time = 0
        
    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history.
        
        Args:
            role: Role of the message sender ("user" or "assistant")
            content: Content of the message
        """
        self._history.append({
            "role": role,
            "content": content
        })
        
        # Trim history if needed
        if len(self._history) > self._max_history * 2:  # *2 because we count pairs
            # Remove oldest turn (user + assistant)
            self._history = self._history[2:]
            
        self._last_interaction_time = time.time()
        
    def get_history(self) -> List[Dict[str, str]]:
        """Get the conversation history.
        
        Returns:
            List of message dictionaries
        """
        return self._history.copy()
        
    def set_metadata(self, key: str, value: Any) -> None:
        """Set a metadata value.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self._metadata[key] = value
        
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get a metadata value.
        
        Args:
            key: Metadata key
            default: Default value if key not found
            
        Returns:
            The metadata value or default
        """
        return self._metadata.get(key, default)
        
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self._history = []
        
    def time_since_last_interaction(self) -> float:
        """Get time since last interaction.
        
        Returns:
            Time in seconds since last interaction
        """
        if self._last_interaction_time == 0:
            return 0
        return time.time() - self._last_interaction_time
```

## Integration with Plugins

### LLM-enabled Plugin

```python
from vpa.core.plugins import Plugin
from vpa.core.events import event_bus
from typing import Dict, Any
import asyncio
import uuid

class LLMEnabledPlugin(Plugin):
    """Base class for plugins that use LLM capabilities."""
    
    def __init__(self):
        """Initialize the LLM-enabled plugin."""
        self._pending_requests = {}
        
    async def initialize(self) -> bool:
        """Initialize the plugin.
        
        Returns:
            True if initialization succeeded, False otherwise
        """
        # Subscribe to LLM responses
        event_bus.subscribe("llm_response", self._handle_llm_response, async_callback=True)
        return await super().initialize()
        
    async def _send_llm_request(self, 
                              prompt: str, 
                              system_message: str,
                              conversation_history: List[Dict[str, str]],
                              functions: Optional[List[Dict[str, Any]]] = None,
                              **kwargs) -> str:
        """Send a request to the LLM and wait for the response.
        
        Args:
            prompt: User prompt
            system_message: System instructions
            conversation_history: Previous conversation messages
            functions: Optional function definitions
            **kwargs: Additional parameters
            
        Returns:
            The LLM response text
        """
        request_id = str(uuid.uuid4())
        
        # Create a future to wait for the response
        future = asyncio.Future()
        self._pending_requests[request_id] = future
        
        # Send the request
        await event_bus.emit_async("llm_request", {
            "request_id": request_id,
            "prompt": prompt,
            "system_message": system_message,
            "conversation_history": conversation_history,
            "functions": functions,
            "parameters": kwargs
        })
        
        # Wait for the response
        try:
            response = await asyncio.wait_for(future, timeout=30.0)
            return response
        except asyncio.TimeoutError:
            del self._pending_requests[request_id]
            raise TimeoutError("LLM request timed out")
            
    async def _handle_llm_response(self, event_data: Dict[str, Any]) -> None:
        """Handle an LLM response event.
        
        Args:
            event_data: Response event data
        """
        request_id = event_data.get("request_id")
        if request_id and request_id in self._pending_requests:
            future = self._pending_requests.pop(request_id)
            
            if event_data.get("success", False):
                future.set_result(event_data.get("response", ""))
            else:
                future.set_exception(RuntimeError(event_data.get("error", "Unknown error")))
                
    async def shutdown(self) -> None:
        """Shut down the plugin."""
        # Unsubscribe from LLM responses
        event_bus.unsubscribe("llm_response", self._handle_llm_response)
        
        # Cancel any pending requests
        for future in self._pending_requests.values():
            if not future.done():
                future.cancel()
                
        self._pending_requests.clear()
        await super().shutdown()
```

## Performance Optimization

### Response Caching

```python
from typing import Dict, Any, Optional, Tuple
import hashlib
import json
import time
import asyncio
import logging

logger = logging.getLogger(__name__)

class ResponseCache:
    """Cache for LLM responses to reduce redundant API calls."""
    
    def __init__(self, ttl: int = 3600, max_size: int = 1000):
        """Initialize the response cache.
        
        Args:
            ttl: Time-to-live for cache entries in seconds
            max_size: Maximum number of entries in the cache
        """
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._ttl = ttl
        self._max_size = max_size
        
    def _compute_key(self, request_data: Dict[str, Any]) -> str:
        """Compute a cache key for the request.
        
        Args:
            request_data: Request data
            
        Returns:
            Cache key
        """
        # Remove non-deterministic fields
        data_copy = request_data.copy()
        data_copy.pop("request_id", None)
        
        # Serialize and hash
        serialized = json.dumps(data_copy, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()
        
    def get(self, request_data: Dict[str, Any]) -> Optional[Any]:
        """Get a cached response.
        
        Args:
            request_data: Request data
            
        Returns:
            Cached response or None if not found
        """
        key = self._compute_key(request_data)
        if key in self._cache:
            value, timestamp = self._cache[key]
            
            # Check if expired
            if time.time() - timestamp > self._ttl:
                del self._cache[key]
                return None
                
            return value
            
        return None
        
    def set(self, request_data: Dict[str, Any], response: Any) -> None:
        """Set a cached response.
        
        Args:
            request_data: Request data
            response: Response to cache
        """
        key = self._compute_key(request_data)
        self._cache[key] = (response, time.time())
        
        # Evict if cache is too large
        if len(self._cache) > self._max_size:
            # Remove oldest entries
            sorted_keys = sorted(self._cache.keys(), 
                              key=lambda k: self._cache[k][1])
            for old_key in sorted_keys[:len(self._cache) - self._max_size]:
                del self._cache[old_key]
                
    def clear(self) -> None:
        """Clear all cached responses."""
        self._cache.clear()
        
    def size(self) -> int:
        """Get the current cache size.
        
        Returns:
            Number of entries in the cache
        """
        return len(self._cache)
        
    async def maintenance_task(self) -> None:
        """Periodic task to remove expired entries."""
        while True:
            try:
                # Wait for next maintenance cycle
                await asyncio.sleep(self._ttl / 2)
                
                # Remove expired entries
                current_time = time.time()
                keys_to_remove = []
                for key, (_, timestamp) in self._cache.items():
                    if current_time - timestamp > self._ttl:
                        keys_to_remove.append(key)
                        
                for key in keys_to_remove:
                    del self._cache[key]
                    
                logger.debug(f"Cache maintenance: removed {len(keys_to_remove)} expired entries")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cache maintenance: {e}")
```

### Local First, Remote Fallback

```python
from typing import Dict, Any, List, Optional
from .adapters.base_adapter import LLMAdapter
import logging

logger = logging.getLogger(__name__)

class AdaptiveRouter:
    """Routes requests to appropriate LLM based on capabilities and performance."""
    
    def __init__(self, adapters: Dict[str, LLMAdapter]):
        """Initialize the router.
        
        Args:
            adapters: Dict of name -> adapter
        """
        self._adapters = adapters
        self._performance_stats: Dict[str, Dict[str, float]] = {}
        
    def route(self, 
             request: Dict[str, Any],
             preferred_adapter: Optional[str] = None) -> str:
        """Route a request to the appropriate adapter.
        
        Args:
            request: Request data
            preferred_adapter: Name of preferred adapter
            
        Returns:
            Name of the selected adapter
        """
        # Use preferred adapter if specified and available
        if preferred_adapter and preferred_adapter in self._adapters:
            return preferred_adapter
            
        # Check for function calling
        requires_function_calling = "functions" in request and request["functions"]
        
        # Check for local adapters first
        local_adapters = []
        remote_adapters = []
        
        for name, adapter in self._adapters.items():
            capabilities = adapter.capabilities
            
            # Skip if adapter doesn't support required capabilities
            if requires_function_calling and not capabilities.get("function_calling"):
                continue
                
            if capabilities.get("local", False):
                local_adapters.append(name)
            else:
                remote_adapters.append(name)
                
        # Prefer local adapters if available and capable
        if local_adapters:
            # Sort by performance (if available)
            sorted_adapters = sorted(
                local_adapters,
                key=lambda name: self._performance_stats.get(name, {}).get("avg_time", float("inf"))
            )
            return sorted_adapters[0]
            
        # Fall back to remote adapters
        if remote_adapters:
            # Sort by performance (if available)
            sorted_adapters = sorted(
                remote_adapters,
                key=lambda name: self._performance_stats.get(name, {}).get("avg_time", float("inf"))
            )
            return sorted_adapters[0]
            
        # If no suitable adapter found, return any adapter
        return next(iter(self._adapters.keys()))
        
    def update_performance(self, adapter_name: str, response_time: float) -> None:
        """Update performance stats for an adapter.
        
        Args:
            adapter_name: Name of the adapter
            response_time: Response time in seconds
        """
        if adapter_name not in self._performance_stats:
            self._performance_stats[adapter_name] = {
                "count": 0,
                "total_time": 0,
                "avg_time": 0
            }
            
        stats = self._performance_stats[adapter_name]
        stats["count"] += 1
        stats["total_time"] += response_time
        stats["avg_time"] = stats["total_time"] / stats["count"]
```

## Security and Privacy

### Data Handling

1. **Local Processing Priority**
   - Use local models when possible to keep data private
   - Only send to cloud services when necessary based on capability requirements

2. **Sensitive Data Filtering**
   - Filter out sensitive information before sending to LLMs
   - Redact personal identifiable information (PII)
   - Use regular expressions to detect and redact credit cards, SSNs, etc.

3. **Data Retention**
   - Do not store conversation history longer than necessary
   - Provide options to clear history
   - Implement automatic conversation expiry

## Testing Strategy

### Unit Testing

```python
# tests/unit/core/llm/test_llm_manager.py
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from vpa.core.llm.manager import LLMManager
from vpa.core.events import event_bus

class TestLLMManager:
    @pytest.fixture
    def mock_adapter(self):
        """Create a mock LLM adapter."""
        adapter = AsyncMock()
        adapter.name = "mock_adapter"
        adapter.capabilities.return_value = {
            "streaming": True,
            "function_calling": True,
            "embeddings": True,
            "local": True
        }
        adapter.generate_response.return_value = {
            "text": "Mock response",
            "function_call": None,
            "metadata": {"model": "mock", "provider": "mock"}
        }
        adapter.generate_embedding.return_value = [0.1, 0.2, 0.3]
        
        return adapter
        
    @pytest.fixture
    def mock_factory(self, mock_adapter):
        """Create a mock LLM factory."""
        factory = MagicMock()
        factory.create_adapter.return_value = asyncio.Future()
        factory.create_adapter.return_value.set_result(mock_adapter)
        factory.get_adapter.return_value = mock_adapter
        
        return factory
        
    @pytest.fixture
    async def llm_manager(self, mock_factory):
        """Create an LLM manager with mocked dependencies."""
        manager = LLMManager()
        manager._factory = mock_factory
        
        config = {
            "adapters": {
                "mock": {}
            },
            "default_adapter": "mock"
        }
        
        await manager.initialize(config)
        yield manager
        await manager.shutdown()
        
    @pytest.mark.asyncio
    async def test_handle_llm_request(self, llm_manager, mock_adapter):
        """Test handling an LLM request."""
        # Create a future to capture the response event
        response_future = asyncio.Future()
        
        async def capture_response(event_data):
            response_future.set_result(event_data)
            
        event_bus.subscribe("llm_response", capture_response, async_callback=True)
        
        # Send a request
        await event_bus.emit_async("llm_request", {
            "request_id": "test_request",
            "prompt": "Test prompt",
            "system_message": "You are a test assistant",
            "conversation_history": []
        })
        
        # Wait for response
        response = await asyncio.wait_for(response_future, timeout=1.0)
        
        # Verify response
        assert response["request_id"] == "test_request"
        assert response["response"] == "Mock response"
        assert response["success"] is True
        
        # Verify adapter was called correctly
        mock_adapter.generate_response.assert_called_once()
        call_args = mock_adapter.generate_response.call_args[1]
        assert call_args["prompt"] == "Test prompt"
        assert call_args["system_message"] == "You are a test assistant"
        
        # Clean up
        event_bus.unsubscribe("llm_response", capture_response)
```

### Integration Testing

```python
# tests/integration/test_llm_integration.py
import pytest
import asyncio
from vpa.core.llm.manager import LLMManager
from vpa.core.events import event_bus

class TestLLMIntegration:
    @pytest.fixture
    async def setup_llm_system(self):
        """Set up the LLM system for testing."""
        # Create and initialize the manager
        manager = LLMManager()
        
        # Configuration for testing (use local mock adapter)
        config = {
            "adapters": {
                "mock": {
                    "type": "mock",
                    "responses": {
                        "default": "This is a mock response",
                        "weather": "The weather is sunny",
                        "help": "I can help you with various tasks"
                    }
                }
            },
            "default_adapter": "mock"
        }
        
        await manager.initialize(config)
        
        yield manager
        
        await manager.shutdown()
        
    @pytest.mark.asyncio
    async def test_llm_request_response_flow(self, setup_llm_system):
        """Test the full LLM request/response flow."""
        # Create a future to capture the response
        response_future = asyncio.Future()
        
        async def capture_response(event_data):
            if event_data.get("request_id") == "test_integration":
                response_future.set_result(event_data)
                
        # Subscribe to response events
        event_bus.subscribe("llm_response", capture_response, async_callback=True)
        
        # Send a request
        await event_bus.emit_async("llm_request", {
            "request_id": "test_integration",
            "prompt": "What's the weather like?",
            "system_message": "You are a weather assistant",
            "conversation_history": []
        })
        
        # Wait for and verify response
        response = await asyncio.wait_for(response_future, timeout=2.0)
        assert response["request_id"] == "test_integration"
        assert "response" in response
        assert response["success"] is True
        
        # Clean up
        event_bus.unsubscribe("llm_response", capture_response)
```

### Performance Testing

```python
# tests/performance/test_llm_performance.py
import pytest
import asyncio
import time
from vpa.core.llm.manager import LLMManager
from vpa.core.events import event_bus

class TestLLMPerformance:
    @pytest.fixture
    async def setup_llm_system(self):
        """Set up the LLM system for performance testing."""
        manager = LLMManager()
        
        # Use local adapter for performance testing
        config = {
            "adapters": {
                "local": {
                    "model_path": "models/tinyllama.gguf",
                    "context_length": 2048,
                    "threads": 4
                }
            },
            "default_adapter": "local"
        }
        
        await manager.initialize(config)
        
        yield manager
        
        await manager.shutdown()
        
    @pytest.mark.asyncio
    async def test_response_time(self, setup_llm_system):
        """Test LLM response time performance."""
        response_times = []
        
        async def measure_response_time(prompt):
            # Create a future to capture the response
            response_future = asyncio.Future()
            
            async def capture_response(event_data):
                response_future.set_result(event_data)
                
            # Subscribe to response events
            event_bus.subscribe("llm_response", capture_response, async_callback=True)
            
            # Measure time
            start_time = time.time()
            
            # Send request
            await event_bus.emit_async("llm_request", {
                "request_id": f"perf_{len(response_times)}",
                "prompt": prompt,
                "system_message": "Be concise.",
                "conversation_history": []
            })
            
            # Wait for response
            await response_future
            
            # Record time
            elapsed = time.time() - start_time
            response_times.append(elapsed)
            
            # Clean up
            event_bus.unsubscribe("llm_response", capture_response)
            
            return elapsed
            
        # Test with various prompts
        prompts = [
            "Hello, how are you?",
            "What's the weather like today?",
            "Tell me a short joke.",
            "What's the capital of France?",
            "How do I make pasta?"
        ]
        
        for prompt in prompts:
            elapsed = await measure_response_time(prompt)
            print(f"Prompt: '{prompt}' - Response time: {elapsed:.2f}s")
            
        # Calculate statistics
        avg_time = sum(response_times) / len(response_times)
        max_time = max(response_times)
        min_time = min(response_times)
        
        print(f"\nResponse Time Statistics:")
        print(f"  Average: {avg_time:.2f}s")
        print(f"  Min: {min_time:.2f}s")
        print(f"  Max: {max_time:.2f}s")
        
        # Assert performance targets
        assert avg_time < 2.0, f"Average response time ({avg_time:.2f}s) exceeds target (2.0s)"
```

## Implementation Roadmap

### Phase 1: Core LLM Framework

1. Implement base adapter interface
2. Create LLM factory and manager
3. Integrate with event system
4. Implement basic prompt management
5. Add response processing and error handling

### Phase 2: Local Model Support

1. Implement local LLM adapter using llama.cpp
2. Add model loading and management
3. Optimize for performance on target hardware
4. Implement embedding generation for semantic search

### Phase 3: Cloud Integration

1. Implement OpenAI adapter
2. Add function calling support
3. Implement advanced context management
4. Add security and privacy features

### Phase 4: Advanced Features

1. Implement response caching
2. Add adaptive routing based on request complexity
3. Implement streaming responses
4. Add structured output parsing

## Conclusion

This LLM Integration document provides a comprehensive framework for integrating language models into the VPA system. By using an adapter-based approach with local-first processing, the system can provide high-quality AI capabilities while maintaining performance and privacy. The event-driven architecture ensures seamless integration with other system components.

The implementation roadmap provides a clear path forward for developing these capabilities incrementally, starting with the core framework and progressively adding more advanced features.

---

*Document created: August 29, 2025*
