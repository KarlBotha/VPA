# LLM Selection and Configuration

## Overview

This document defines the LLM (Large Language Model) selection and configuration for VPA, specifying which models to include, their requirements, and default configuration.

## Table of Contents

1. [LLM Selection](#1-llm-selection)
2. [Model Configuration](#2-model-configuration)
3. [Integration Requirements](#3-integration-requirements)
4. [Default Settings](#4-default-settings)
5. [Fallback Mechanisms](#5-fallback-mechanisms)

## 1. LLM Selection

### 1.1 Included Model Options

VPA will include support for the following LLM models:

| Model Name | Size | Type | Source | Requirements |
|------------|------|------|--------|-------------|
| Llama 3 8B | 8B | Local | Ollama | 8GB+ RAM, 4GB+ VRAM recommended |
| Phi 3 Mini | 3.8B | Local | Ollama | 6GB+ RAM, 2GB+ VRAM recommended |
| Gemma 2 9B | 9B | Local | Ollama | 8GB+ RAM, 4GB+ VRAM recommended |
| Mistral 7B | 7B | Local | Ollama | 8GB+ RAM, 4GB+ VRAM recommended |
| Claude 3 Haiku | API | Cloud | Claude API | Internet connection |
| GPT-3.5 Turbo | API | Cloud | OpenAI API | Internet connection |

### 1.2 Model Selection Criteria

Models were selected based on these criteria:

1. **Performance**: Effectiveness for assistant-type tasks
2. **Size**: Ability to run on consumer hardware
3. **Licensing**: Permissive licensing for personal use
4. **Availability**: Reliable download and update mechanisms

### 1.3 Default Model Selection

The default model selection logic will be:

1. First run: Check for GPU acceleration
   - With GPU: Llama 3 8B
   - Without GPU: Phi 3 Mini (more efficient on CPU)

2. Subsequent runs: Use last selected model

## 2. Model Configuration

### 2.1 Common Configuration Parameters

All models will support these configuration parameters:

```python
default_model_params = {
    "temperature": 0.7,      # Creativity level (0.0-1.0)
    "max_tokens": 2048,      # Maximum response length
    "top_p": 0.9,            # Nucleus sampling parameter
    "top_k": 40,             # Top-k sampling parameter
    "presence_penalty": 0.0, # Penalty for repeating topics
    "frequency_penalty": 0.0 # Penalty for repeating tokens
}
```

### 2.2 Model-Specific Configurations

#### 2.2.1 Llama 3 8B Configuration

```python
llama3_config = {
    "model_name": "llama3",
    "context_length": 4096,
    "params": {
        "temperature": 0.7,
        "max_tokens": 2048,
        "top_p": 0.9,
        "repeat_penalty": 1.1,  # Llama-specific parameter
    },
    "system_prompt": "You are a helpful personal assistant named VPA. You are designed to be helpful, harmless, and honest. Always assist users to the best of your abilities while respecting privacy and ethical boundaries."
}
```

#### 2.2.2 Phi 3 Mini Configuration

```python
phi3_config = {
    "model_name": "phi3-mini",
    "context_length": 2048,
    "params": {
        "temperature": 0.7,
        "max_tokens": 1024,
        "top_p": 0.9,
        "repeat_penalty": 1.1,
    },
    "system_prompt": "You are a helpful personal assistant named VPA. You are designed to be helpful, harmless, and honest. Always assist users to the best of your abilities while respecting privacy and ethical boundaries."
}
```

#### 2.2.3 Gemma 2 9B Configuration

```python
gemma2_config = {
    "model_name": "gemma2:9b",
    "context_length": 8192,
    "params": {
        "temperature": 0.7,
        "max_tokens": 2048,
        "top_p": 0.9,
        "repeat_penalty": 1.1,
    },
    "system_prompt": "You are a helpful personal assistant named VPA. You are designed to be helpful, harmless, and honest. Always assist users to the best of your abilities while respecting privacy and ethical boundaries."
}
```

#### 2.2.4 Mistral 7B Configuration

```python
mistral_config = {
    "model_name": "mistral",
    "context_length": 8192,
    "params": {
        "temperature": 0.7,
        "max_tokens": 2048,
        "top_p": 0.9,
        "repeat_penalty": 1.1,
    },
    "system_prompt": "You are a helpful personal assistant named VPA. You are designed to be helpful, harmless, and honest. Always assist users to the best of your abilities while respecting privacy and ethical boundaries."
}
```

#### 2.2.5 Claude 3 Haiku Configuration

```python
claude_config = {
    "model_name": "claude-3-haiku-20240307",
    "context_length": 200000,  # Claude supports very long contexts
    "params": {
        "temperature": 0.7,
        "max_tokens": 4096,
        "top_p": 0.9,
    },
    "system_prompt": "You are a helpful personal assistant named VPA. You are designed to be helpful, harmless, and honest. Always assist users to the best of your abilities while respecting privacy and ethical boundaries."
}
```

#### 2.2.6 GPT-3.5 Turbo Configuration

```python
gpt35_config = {
    "model_name": "gpt-3.5-turbo",
    "context_length": 16385,
    "params": {
        "temperature": 0.7,
        "max_tokens": 2048,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    },
    "system_prompt": "You are a helpful personal assistant named VPA. You are designed to be helpful, harmless, and honest. Always assist users to the best of your abilities while respecting privacy and ethical boundaries."
}
```

## 3. Integration Requirements

### 3.1 Ollama Integration

VPA will integrate with Ollama for local model execution:

```python
class OllamaAdapter(LLMAdapterInterface):
    """Adapter for Ollama LLM integration"""
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the adapter with configuration"""
        self.config = config
        self.server_url = config.get("server_url", "http://localhost:11434")
        self.current_model = None
        
        # Check if Ollama is installed and running
        if not await self._check_ollama_available():
            # Attempt to start Ollama if installed but not running
            if await self._check_ollama_installed():
                if await self._start_ollama_service():
                    logger.info("Started Ollama service")
                else:
                    logger.error("Failed to start Ollama service")
                    return False
            else:
                logger.error("Ollama not installed")
                return False
                
        # Check if model is downloaded
        model_name = config.get("model_name")
        if not await self._check_model_downloaded(model_name):
            # Prompt user to download
            await self.event_bus.emit_async("llm.model_download_required", {
                "model_name": model_name,
                "size_estimate_gb": self._get_model_size_estimate(model_name),
            })
            return False
            
        self.current_model = model_name
        return True
        
    async def _check_ollama_available(self) -> bool:
        """Check if Ollama server is available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/api/version", timeout=2) as resp:
                    return resp.status == 200
        except Exception:
            return False
            
    async def _check_ollama_installed(self) -> bool:
        """Check if Ollama is installed"""
        try:
            # Check for Ollama in common installation paths
            paths = [
                os.path.expanduser("~/AppData/Local/Programs/Ollama/ollama.exe"),
                "C:/Program Files/Ollama/ollama.exe",
                os.path.expanduser("~/.ollama/ollama.exe")
            ]
            
            return any(os.path.exists(path) for path in paths)
        except Exception:
            return False
            
    async def _start_ollama_service(self) -> bool:
        """Start Ollama service"""
        try:
            # Look for Ollama executable
            paths = [
                os.path.expanduser("~/AppData/Local/Programs/Ollama/ollama.exe"),
                "C:/Program Files/Ollama/ollama.exe",
                os.path.expanduser("~/.ollama/ollama.exe")
            ]
            
            ollama_path = next((path for path in paths if os.path.exists(path)), None)
            if not ollama_path:
                return False
                
            # Start Ollama service
            import subprocess
            subprocess.Popen(
                [ollama_path, "serve"],
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for service to start
            for _ in range(10):  # Try 10 times with 1s delay
                await asyncio.sleep(1)
                if await self._check_ollama_available():
                    return True
                    
            return False
        except Exception as e:
            logger.error(f"Error starting Ollama: {e}")
            return False
            
    async def _check_model_downloaded(self, model_name: str) -> bool:
        """Check if model is downloaded"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/api/tags") as resp:
                    if resp.status != 200:
                        return False
                    data = await resp.json()
                    models = data.get("models", [])
                    return any(m.get("name") == model_name for m in models)
        except Exception:
            return False
            
    def _get_model_size_estimate(self, model_name: str) -> float:
        """Get estimated size of model in GB"""
        size_estimates = {
            "llama3": 4.5,
            "phi3-mini": 2.0,
            "gemma2:9b": 5.0,
            "mistral": 4.1
        }
        
        return size_estimates.get(model_name, 5.0)  # Default to 5GB if unknown
```

### 3.2 Cloud API Integration

For cloud-based models (Claude, GPT), API key management is required:

```python
class APIKeyManager:
    """Manager for API keys"""
    
    def __init__(self, security_manager):
        self.security_manager = security_manager
        
    def get_api_key(self, service_name: str) -> Optional[str]:
        """Get API key for service"""
        credential = self.security_manager.get_credential(f"vpa_{service_name}_api")
        if credential:
            username, password = credential
            return password
        return None
        
    def set_api_key(self, service_name: str, api_key: str) -> bool:
        """Set API key for service"""
        return self.security_manager.store_credential(
            f"vpa_{service_name}_api",
            service_name,
            api_key
        )
        
    def has_api_key(self, service_name: str) -> bool:
        """Check if API key exists for service"""
        return self.get_api_key(service_name) is not None
```

## 4. Default Settings

### 4.1 Global LLM Settings

```python
default_llm_settings = {
    "active_model": "auto",  # "auto" selects based on hardware
    "download_models_automatically": False,  # Ask before downloading
    "max_history_tokens": 4096,  # Maximum history to include in context
    "streaming_enabled": True,  # Enable streaming responses
    "show_model_info": True,  # Show model name in chat
    "auto_trim_history": True  # Automatically trim history to fit context
}
```

### 4.2 Model Selector UI

The UI will provide a model selector dropdown:

```python
class ModelSelectorWidget(QWidget):
    """Widget for selecting LLM model"""
    
    def __init__(self, llm_manager):
        super().__init__()
        self.llm_manager = llm_manager
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Model label
        label = QLabel("Model:")
        layout.addWidget(label)
        
        # Model selector dropdown
        self.model_combo = QComboBox()
        self.model_combo.setMinimumWidth(150)
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        layout.addWidget(self.model_combo)
        
        # Settings button
        self.settings_button = QPushButton()
        self.settings_button.setIcon(QIcon.fromTheme("configure"))
        self.settings_button.setToolTip("Model Settings")
        self.settings_button.clicked.connect(self._on_settings_clicked)
        self.settings_button.setFixedSize(24, 24)
        layout.addWidget(self.settings_button)
        
        # Populate models
        self._populate_models()
        
    def _populate_models(self):
        """Populate model dropdown"""
        self.model_combo.clear()
        
        # Get available models
        available_models = self.llm_manager.get_available_models()
        current_model = self.llm_manager.get_current_model()
        
        # Group models by type
        local_models = [m for m in available_models if m["type"] == "local"]
        cloud_models = [m for m in available_models if m["type"] == "cloud"]
        
        # Add group headers and models
        if local_models:
            self.model_combo.addItem("-- Local Models --", None)
            for model in local_models:
                self.model_combo.addItem(
                    f"{model['name']} ({model['size']})", 
                    model["id"]
                )
                
        if cloud_models:
            self.model_combo.addItem("-- Cloud Models --", None)
            for model in cloud_models:
                self.model_combo.addItem(
                    f"{model['name']} (Cloud)", 
                    model["id"]
                )
                
        # Set current model
        for i in range(self.model_combo.count()):
            if self.model_combo.itemData(i) == current_model:
                self.model_combo.setCurrentIndex(i)
                break
                
    def _on_model_changed(self, index):
        """Handle model selection change"""
        model_id = self.model_combo.itemData(index)
        
        # Skip dividers
        if not model_id:
            # Find the next valid item
            for i in range(index + 1, self.model_combo.count()):
                if self.model_combo.itemData(i):
                    self.model_combo.setCurrentIndex(i)
                    return
                    
            # If no next valid item, try previous
            for i in range(index - 1, -1, -1):
                if self.model_combo.itemData(i):
                    self.model_combo.setCurrentIndex(i)
                    return
                    
            return
            
        # Change model
        self.llm_manager.set_current_model(model_id)
        
    def _on_settings_clicked(self):
        """Show model settings dialog"""
        dialog = ModelSettingsDialog(self, self.llm_manager)
        dialog.exec_()
        
        # Refresh models after settings change
        self._populate_models()
```

## 5. Fallback Mechanisms

### 5.1 Model Fallback Chain

If a selected model fails, VPA will implement a fallback chain:

```python
async def _handle_model_failure(self, model_id: str, error: Exception) -> bool:
    """Handle model failure by falling back to another model"""
    logger.error(f"Model {model_id} failed: {error}")
    
    # Get fallback chain based on model
    fallback_chains = {
        "llama3": ["phi3-mini", "mistral"],
        "phi3-mini": ["mistral", "llama3"],
        "gemma2:9b": ["mistral", "phi3-mini"],
        "mistral": ["phi3-mini", "llama3"],
        "claude-3-haiku-20240307": ["gpt-3.5-turbo"],
        "gpt-3.5-turbo": ["claude-3-haiku-20240307"]
    }
    
    # Get fallback chain for model
    fallback_chain = fallback_chains.get(model_id, [])
    
    # Try fallbacks one by one
    for fallback_model in fallback_chain:
        logger.info(f"Attempting fallback to {fallback_model}")
        
        try:
            # Check if model is available
            adapter = self.get_model_adapter(fallback_model)
            if adapter and await adapter.initialize(self.get_model_config(fallback_model)):
                # Set as current model
                self.current_model = fallback_model
                
                # Notify about fallback
                await self.event_bus.emit_async("llm.model_fallback", {
                    "original_model": model_id,
                    "fallback_model": fallback_model,
                    "reason": str(error)
                })
                
                return True
        except Exception as fallback_error:
            logger.error(f"Fallback to {fallback_model} failed: {fallback_error}")
            
    # If all fallbacks fail, notify failure
    await self.event_bus.emit_async("llm.critical_error", {
        "message": "All LLM models failed to initialize",
        "original_error": str(error)
    })
    
    return False
```

### 5.2 Error Handling

The system will handle these common LLM errors:

1. **Model Not Found**: Show download dialog for local models
2. **API Key Missing**: Prompt for API key configuration
3. **Context Length Exceeded**: Automatically trim history
4. **Resource Limitation**: Suggest lower resource model
5. **Network Connectivity**: Switch to local model if available

```python
async def _handle_llm_error(self, error_type: str, model_id: str, details: Dict[str, Any]):
    """Handle LLM errors"""
    if error_type == "model_not_found":
        # Show download dialog
        await self.event_bus.emit_async("llm.model_download_required", {
            "model_name": model_id,
            "size_estimate_gb": self._get_model_size_estimate(model_id)
        })
    elif error_type == "api_key_missing":
        # Prompt for API key
        await self.event_bus.emit_async("llm.api_key_required", {
            "service_name": details.get("service_name")
        })
    elif error_type == "context_length_exceeded":
        # Trim history and retry
        if self.settings_manager.get("llm.auto_trim_history", True):
            await self._trim_history_and_retry(model_id, details.get("request_id"))
        else:
            await self.event_bus.emit_async("llm.error", {
                "message": "Input is too long for this model. Please clear some chat history."
            })
    elif error_type == "resource_limitation":
        # Suggest model with lower resource requirements
        await self._handle_resource_limitation(model_id)
    elif error_type == "network_error" and details.get("model_type") == "cloud":
        # Try switching to local model
        await self._try_switch_to_local_model(model_id)
```

## Conclusion

This LLM Selection and Configuration specification provides a comprehensive plan for integrating multiple language models into VPA. By supporting both local and cloud-based models, VPA offers flexibility for different user needs and hardware capabilities.

The implementation includes automatic model selection based on hardware capabilities, fallback mechanisms for robustness, and detailed configuration options for each supported model. This approach ensures that VPA can deliver high-quality language model capabilities across a wide range of user systems.

---

*Document created on August 28, 2025*  
*Version: 1.0*
