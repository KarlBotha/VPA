# API Architecture and Integration

## Overview

This document specifies the API architecture for the VPA application, detailing how the frontend, backend, and external services communicate. It defines the API layer structure, integration points, and communication patterns.

## Table of Contents

1. [API Architecture](#1-api-architecture)
2. [Internal API Layer](#2-internal-api-layer)
3. [External API Integration](#3-external-api-integration)
4. [LLM API Integration](#4-llm-api-integration)
5. [Windows API Integration](#5-windows-api-integration)
6. [API Security](#6-api-security)
7. [API Performance](#7-api-performance)
8. [Error Handling](#8-error-handling)

## 1. API Architecture

### 1.1 Architecture Overview

The VPA application uses a layered API architecture:

```
┌───────────────────────────────────────────────────────────┐
│                      Frontend Layer                       │
│  (UI Components, View Models, User Interaction Handlers)  │
└─────────────────────────┬─────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────┐
│                       Event Bus                           │
│        (Asynchronous Event-Based Communication)           │
└─────────────────────────┬─────────────────────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────┐
│                     Backend Layer                         │
│    (Application Logic, Service Coordination, Plugins)     │
└────────────┬─────────────────────────────────┬────────────┘
             │                                 │
             ▼                                 ▼
┌───────────────────────────┐   ┌───────────────────────────┐
│     Internal API Layer    │   │    External API Layer     │
│  (Core Services, Storage) │   │  (LLM, Windows, Voice)    │
└───────────────────────────┘   └───────────────────────────┘
```

### 1.2 API Communication Patterns

VPA uses two primary communication patterns:

1. **Event-based Communication**: Asynchronous communication via the event bus
2. **Direct API Calls**: Synchronous calls to internal and external APIs

### 1.3 API Interface Types

The application implements three types of API interfaces:

1. **Internal APIs**: Services provided by the application itself
2. **External Integration APIs**: Integration with third-party services
3. **Platform APIs**: Integration with operating system (Windows API)

## 2. Internal API Layer

### 2.1 Core Service APIs

#### 2.1.1 Settings Service API

```python
class SettingsServiceAPI:
    """API for accessing and modifying application settings"""
    
    async def get_setting(self, path: str, default=None) -> Any:
        """Get a setting value by path"""
        pass
        
    async def set_setting(self, path: str, value: Any) -> bool:
        """Set a setting value by path"""
        pass
        
    async def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings as a dictionary"""
        pass
        
    async def reset_settings(self, category: Optional[str] = None) -> bool:
        """Reset settings to defaults"""
        pass
```

#### 2.1.2 Authentication Service API

```python
class AuthServiceAPI:
    """API for user authentication operations"""
    
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return session info"""
        pass
        
    async def logout(self) -> bool:
        """Log out current user"""
        pass
        
    async def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user info"""
        pass
        
    async def refresh_token(self) -> bool:
        """Refresh authentication token"""
        pass
```

#### 2.1.3 Chat History Service API

```python
class ChatHistoryServiceAPI:
    """API for chat history operations"""
    
    async def get_chat_history(self) -> List[Dict[str, Any]]:
        """Get list of all chat sessions"""
        pass
        
    async def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific chat by ID"""
        pass
        
    async def save_chat(self, chat_data: Dict[str, Any]) -> str:
        """Save a chat session and return its ID"""
        pass
        
    async def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat session"""
        pass
        
    async def rename_chat(self, chat_id: str, new_name: str) -> bool:
        """Rename a chat session"""
        pass
```

### 2.2 Plugin API

```python
class PluginServiceAPI:
    """API for plugin operations"""
    
    async def get_available_plugins(self) -> List[Dict[str, Any]]:
        """Get list of all available plugins"""
        pass
        
    async def get_active_plugins(self) -> List[Dict[str, Any]]:
        """Get list of currently active plugins"""
        pass
        
    async def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin by ID"""
        pass
        
    async def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin by ID"""
        pass
        
    async def get_plugin_settings(self, plugin_id: str) -> Dict[str, Any]:
        """Get settings for a specific plugin"""
        pass
```

### 2.3 Storage API

```python
class StorageServiceAPI:
    """API for data persistence operations"""
    
    async def save_data(self, collection: str, key: str, data: Any) -> bool:
        """Save data to persistent storage"""
        pass
        
    async def load_data(self, collection: str, key: str) -> Optional[Any]:
        """Load data from persistent storage"""
        pass
        
    async def delete_data(self, collection: str, key: str) -> bool:
        """Delete data from persistent storage"""
        pass
        
    async def list_collection(self, collection: str) -> List[str]:
        """List all keys in a collection"""
        pass
```

## 3. External API Integration

### 3.1 API Integration Framework

The VPA uses an adapter pattern for external API integration:

```python
class ExternalAPIAdapter:
    """Base adapter for external API integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        
    async def initialize(self) -> bool:
        """Initialize the API connection"""
        pass
        
    async def call_api(self, endpoint: str, method: str, data: Any) -> Any:
        """Call external API endpoint"""
        pass
        
    async def handle_error(self, error: Exception) -> Any:
        """Handle API errors"""
        pass
```

### 3.2 API Registration System

External APIs are registered with the system using:

```python
class APIRegistry:
    """Registry for external API integrations"""
    
    def register_api(self, api_id: str, adapter_class: Type[ExternalAPIAdapter], 
                     config: Dict[str, Any]) -> bool:
        """Register a new external API"""
        pass
        
    def get_api_adapter(self, api_id: str) -> Optional[ExternalAPIAdapter]:
        """Get an API adapter by ID"""
        pass
        
    def list_available_apis(self) -> List[str]:
        """List all registered APIs"""
        pass
```

## 4. LLM API Integration

### 4.1 LLM Adapter Interface

```python
class LLMAdapterInterface:
    """Interface for LLM integration"""
    
    async def initialize_model(self, model_name: str) -> bool:
        """Initialize the language model"""
        pass
        
    async def generate_completion(self, prompt: str, 
                                  parameters: Dict[str, Any]) -> str:
        """Generate text completion"""
        pass
        
    async def generate_completion_stream(self, prompt: str,
                                        parameters: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Generate streaming text completion"""
        pass
        
    async def embed_text(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        pass
```

### 4.2 Ollama Adapter Implementation

```python
class OllamaAdapter(LLMAdapterInterface):
    """Adapter for Ollama LLM integration"""
    
    async def initialize_model(self, model_name: str) -> bool:
        """Initialize Ollama model"""
        try:
            # Connect to Ollama server
            self.client = OllamaClient(self.config.get("server_url", "http://localhost:11434"))
            
            # Check if model exists locally
            models = await self.client.list_models()
            if model_name not in [m.get("name") for m in models]:
                # Pull model if not available
                await self.client.pull_model(model_name)
                
            self.current_model = model_name
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Ollama model: {e}")
            await self.event_bus.emit_async("llm.error", {
                "type": "initialization_error",
                "model": model_name,
                "message": str(e)
            })
            return False
            
    async def generate_completion(self, prompt: str, 
                                 parameters: Dict[str, Any]) -> str:
        """Generate completion using Ollama"""
        try:
            response = await self.client.generate(
                model=self.current_model,
                prompt=prompt,
                temperature=parameters.get("temperature", 0.7),
                max_tokens=parameters.get("max_tokens", 2048),
                top_p=parameters.get("top_p", 0.9),
                frequency_penalty=parameters.get("frequency_penalty", 0.0),
            )
            return response.get("text", "")
        except Exception as e:
            logger.error(f"Ollama completion error: {e}")
            await self.event_bus.emit_async("llm.error", {
                "type": "completion_error",
                "model": self.current_model,
                "message": str(e)
            })
            return ""
            
    async def generate_completion_stream(self, prompt: str,
                                       parameters: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """Generate streaming completion using Ollama"""
        request_id = parameters.get("request_id", str(uuid.uuid4()))
        try:
            stream = await self.client.generate_stream(
                model=self.current_model,
                prompt=prompt,
                temperature=parameters.get("temperature", 0.7),
                max_tokens=parameters.get("max_tokens", 2048),
            )
            
            full_text = ""
            async for chunk in stream:
                token = chunk.get("text", "")
                full_text += token
                
                # Emit streaming event
                await self.event_bus.emit_async("llm.response.stream", {
                    "request_id": request_id,
                    "token": token,
                    "text_so_far": full_text
                })
                
                yield token
                
            # Emit completion event
            await self.event_bus.emit_async("llm.response", {
                "request_id": request_id,
                "response": full_text,
                "model": self.current_model
            })
                
        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            await self.event_bus.emit_async("llm.error", {
                "type": "streaming_error",
                "request_id": request_id,
                "model": self.current_model,
                "message": str(e)
            })
```

### 4.3 Llama Adapter Implementation

```python
class LlamaAdapter(LLMAdapterInterface):
    """Adapter for Llama local model integration"""
    
    async def initialize_model(self, model_name: str) -> bool:
        """Initialize Llama model"""
        try:
            # Check model path
            model_path = self.config.get("model_path", "")
            if not model_path:
                model_path = os.path.join(get_models_dir(), f"{model_name}.gguf")
                
            if not os.path.exists(model_path):
                logger.error(f"Model file not found: {model_path}")
                await self.event_bus.emit_async("llm.error", {
                    "type": "model_not_found",
                    "model": model_name,
                    "path": model_path
                })
                return False
                
            # Load model in separate process to avoid blocking
            self.model_process = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "vpa.llm.loader",
                "--model", model_path,
                "--ctx_size", str(self.config.get("context_size", 2048)),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for model to load
            line = await self.model_process.stdout.readline()
            if b"MODEL_LOADED_SUCCESSFULLY" not in line:
                stderr = await self.model_process.stderr.read()
                logger.error(f"Failed to load Llama model: {stderr.decode()}")
                return False
                
            self.current_model = model_name
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Llama model: {e}")
            await self.event_bus.emit_async("llm.error", {
                "type": "initialization_error",
                "model": model_name,
                "message": str(e)
            })
            return False
```

## 5. Windows API Integration

### 5.1 Windows API Interface

```python
class WindowsAPIInterface:
    """Interface for Windows API integration"""
    
    async def set_registry_value(self, key: str, value_name: str, value: Any) -> bool:
        """Set Windows registry value"""
        pass
        
    async def get_registry_value(self, key: str, value_name: str, default=None) -> Any:
        """Get Windows registry value"""
        pass
        
    async def show_notification(self, title: str, message: str, 
                              duration: int = 5) -> bool:
        """Show Windows toast notification"""
        pass
        
    async def create_system_tray(self, icon_path: str, tooltip: str) -> Any:
        """Create system tray icon"""
        pass
        
    async def add_tray_menu_item(self, tray, label: str, callback: Callable) -> bool:
        """Add menu item to system tray"""
        pass
```

### 5.2 Windows API Implementation

```python
class WindowsAPIImplementation(WindowsAPIInterface):
    """Implementation of Windows API interface"""
    
    async def set_registry_value(self, key: str, value_name: str, value: Any) -> bool:
        """Set Windows registry value"""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                self._set_registry_value_sync,
                key, value_name, value
            )
        except Exception as e:
            logger.error(f"Failed to set registry value: {e}")
            await self.event_bus.emit_async("windows_api.error", {
                "type": "registry_error",
                "operation": "set",
                "key": key,
                "message": str(e)
            })
            return False
            
    def _set_registry_value_sync(self, key: str, value_name: str, value: Any) -> bool:
        """Synchronous implementation of registry value setting"""
        try:
            import winreg
            key_parts = key.split("\\")
            root_key_str = key_parts[0].upper()
            sub_key = "\\".join(key_parts[1:])
            
            # Map string root key to winreg constant
            root_key_map = {
                "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
                "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
                "HKCU": winreg.HKEY_CURRENT_USER,
                "HKLM": winreg.HKEY_LOCAL_MACHINE
            }
            
            root_key = root_key_map.get(root_key_str)
            if root_key is None:
                raise ValueError(f"Invalid registry root key: {root_key_str}")
                
            # Determine value type
            if isinstance(value, int):
                value_type = winreg.REG_DWORD
            elif isinstance(value, str):
                value_type = winreg.REG_SZ
            elif isinstance(value, list):
                value_type = winreg.REG_MULTI_SZ
                value = [str(v) for v in value]  # Ensure all items are strings
            else:
                value_type = winreg.REG_SZ
                value = str(value)  # Convert to string as fallback
                
            # Open key with write access
            reg_key = winreg.CreateKeyEx(root_key, sub_key, 0, winreg.KEY_WRITE)
            
            # Set value
            winreg.SetValueEx(reg_key, value_name, 0, value_type, value)
            
            # Close key
            winreg.CloseKey(reg_key)
            return True
        except Exception as e:
            logger.error(f"Registry error: {e}")
            return False
```

## 6. API Security

### 6.1 Authentication and Authorization

```python
class APISecurityManager:
    """Manager for API security"""
    
    def authenticate_request(self, request: Dict[str, Any]) -> bool:
        """Authenticate an API request"""
        pass
        
    def authorize_operation(self, user_id: str, operation: str, 
                           resource: str) -> bool:
        """Check if user is authorized for operation"""
        pass
        
    def generate_api_token(self, user_id: str, scopes: List[str]) -> str:
        """Generate API token for user"""
        pass
        
    def validate_api_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate API token and return payload"""
        pass
```

### 6.2 Request Validation

```python
class APIRequestValidator:
    """Validator for API requests"""
    
    def validate_request(self, request: Dict[str, Any], 
                        schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate request against schema"""
        pass
        
    def sanitize_input(self, input_data: Any) -> Any:
        """Sanitize input data"""
        pass
```

## 7. API Performance

### 7.1 Performance Monitoring

```python
class APIPerformanceMonitor:
    """Monitor API performance"""
    
    def start_request_timer(self, request_id: str) -> None:
        """Start timer for request"""
        pass
        
    def end_request_timer(self, request_id: str) -> float:
        """End timer and return elapsed time"""
        pass
        
    def record_metrics(self, api_name: str, operation: str, 
                      duration: float) -> None:
        """Record performance metrics"""
        pass
        
    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report"""
        pass
```

### 7.2 Rate Limiting

```python
class APIRateLimiter:
    """Rate limiter for API calls"""
    
    def check_rate_limit(self, api_name: str, user_id: str) -> bool:
        """Check if rate limit is exceeded"""
        pass
        
    def increment_counter(self, api_name: str, user_id: str) -> None:
        """Increment API call counter"""
        pass
        
    def get_remaining_calls(self, api_name: str, user_id: str) -> int:
        """Get remaining API calls for user"""
        pass
```

## 8. Error Handling

### 8.1 Error Response Format

API errors follow a standard format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "param1": "Additional error details",
      "param2": "More details"
    }
  },
  "request_id": "unique-request-identifier"
}
```

### 8.2 Error Handling and Logging

```python
class APIErrorHandler:
    """Handler for API errors"""
    
    def handle_error(self, error: Exception, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle error and return formatted response"""
        pass
        
    def log_error(self, error: Exception, request: Dict[str, Any]) -> None:
        """Log API error"""
        pass
        
    def get_error_code(self, error: Exception) -> str:
        """Get error code for exception"""
        pass
```

## Conclusion

This API Architecture specification defines how the VPA application components communicate internally and integrate with external services. It establishes a consistent pattern for API design, security, and error handling across the application.

---

*API Architecture and Integration created on August 28, 2025*  
*Version: 1.0*
