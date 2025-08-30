# GPU Acceleration Integration

## Overview

This document outlines the integration of GPU acceleration capabilities into VPA, specifically focusing on NVIDIA CUDA support for LLM inference and other AI operations.

## Table of Contents

1. [GPU Acceleration Architecture](#1-gpu-acceleration-architecture)
2. [CUDA Integration](#2-cuda-integration)
3. [Performance Optimization](#3-performance-optimization)
4. [Compatibility Detection](#4-compatibility-detection)
5. [Configuration Settings](#5-configuration-settings)

## 1. GPU Acceleration Architecture

### 1.1 Architecture Overview

GPU acceleration will be integrated into the following components:

```
┌───────────────────────────────────────────────────────────────────┐
│                       LLM Processing Pipeline                      │
└───────────┬─────────────────────────────────────────────┬─────────┘
            │                                             │
            ▼                                             ▼
┌───────────────────────────┐                 ┌───────────────────────────┐
│    CPU-based Processing   │                 │    GPU-based Processing   │
│  (Fallback if GPU unavail)│                 │   (CUDA/Tensor Cores)     │
└───────────────────────────┘                 └───────────────────────────┘
```

### 1.2 Component Integration

The GPU acceleration system will integrate with:

1. **LLM Inference Engine**: Accelerating text generation
2. **Embedding Generation**: Speeding up vector embeddings
3. **Voice Processing**: Enhancing speech-to-text conversion
4. **Image Analysis**: If image processing capabilities are added

## 2. CUDA Integration

### 2.1 CUDA Requirements

VPA will integrate with NVIDIA CUDA using the following components:

1. **CUDA Toolkit**: Minimum version 11.7
2. **cuDNN**: Minimum version 8.6 for deep learning acceleration
3. **TensorRT**: For optimized inference (optional enhancement)

### 2.2 Implementation Approach

```python
class GPUAccelerationManager:
    """Manager for GPU acceleration capabilities"""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.gpu_info = None
        self.cuda_available = False
        self.tensor_cores_available = False
        self.vram_available = 0
        
    async def initialize(self):
        """Initialize GPU acceleration system"""
        try:
            # Check CUDA availability
            import torch
            self.cuda_available = torch.cuda.is_available()
            
            if self.cuda_available:
                # Get GPU information
                gpu_count = torch.cuda.device_count()
                current_device = torch.cuda.current_device()
                device_name = torch.cuda.get_device_name(current_device)
                
                # Check for tensor cores (Volta, Turing, Ampere, Ada Lovelace, Hopper architectures)
                tensor_core_architectures = [
                    'Tesla V100', 'Quadro GV100',  # Volta
                    'RTX 20', 'Quadro RTX', 'T4',  # Turing
                    'RTX 30', 'A100', 'A40', 'A10',  # Ampere
                    'RTX 40', 'L40', 'L4',  # Ada Lovelace
                    'H100'  # Hopper
                ]
                
                self.tensor_cores_available = any(arch in device_name for arch in tensor_core_architectures)
                
                # Get available VRAM
                self.vram_available = torch.cuda.get_device_properties(current_device).total_memory
                
                # Store GPU information
                self.gpu_info = {
                    'device_name': device_name,
                    'cuda_version': torch.version.cuda,
                    'gpu_count': gpu_count,
                    'vram_mb': self.vram_available / (1024 * 1024),
                    'tensor_cores_available': self.tensor_cores_available
                }
                
                logger.info(f"CUDA enabled GPU detected: {device_name} with {self.vram_available / (1024 * 1024):.0f}MB VRAM")
                
                # Update settings with detected capabilities
                await self._update_settings()
                
                return True
            else:
                logger.info("No CUDA-capable GPU detected, using CPU only")
                return False
                
        except ImportError:
            logger.warning("PyTorch not available, GPU acceleration disabled")
            return False
        except Exception as e:
            logger.error(f"Error initializing GPU acceleration: {e}")
            return False
            
    async def _update_settings(self):
        """Update settings based on GPU capabilities"""
        # Enable GPU acceleration by default if available
        self.settings_manager.set("llm.use_gpu_acceleration", True)
        
        # Set appropriate batch size based on VRAM
        vram_mb = self.vram_available / (1024 * 1024)
        
        if vram_mb >= 24000:  # High-end GPU (24GB+)
            batch_size = 32
            precision = "float16"  # Use half precision by default
        elif vram_mb >= 8000:  # Mid-range GPU (8GB+)
            batch_size = 16
            precision = "float16"
        elif vram_mb >= 4000:  # Entry GPU (4GB+)
            batch_size = 8
            precision = "float16"
        else:  # Low VRAM
            batch_size = 4
            precision = "float16"
            
        # If tensor cores available, use TF32 for better performance/accuracy balance
        if self.tensor_cores_available:
            self.settings_manager.set("llm.use_tensor_cores", True)
            
        self.settings_manager.set("llm.batch_size", batch_size)
        self.settings_manager.set("llm.precision", precision)
        
    def get_torch_device(self):
        """Get appropriate torch device based on availability"""
        try:
            import torch
            return torch.device("cuda" if torch.cuda.is_available() else "cpu")
        except ImportError:
            return "cpu"
            
    def optimize_for_inference(self, model):
        """Optimize model for inference using available GPU capabilities"""
        try:
            precision = self.settings_manager.get("llm.precision", "float32")
            
            if not self.cuda_available:
                return model
                
            # Apply optimizations based on precision setting
            if precision == "float16" and self.cuda_available:
                import torch
                model = model.half()  # Convert to float16
                
            # Enable TF32 for tensor cores if available
            if self.tensor_cores_available and self.settings_manager.get("llm.use_tensor_cores", True):
                import torch
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True
                
            return model
        except Exception as e:
            logger.error(f"Error optimizing model for inference: {e}")
            return model
```

### 2.3 LLM Adapter Integration

Update the LLM adapter to utilize GPU acceleration:

```python
class LlamaAdapter(LLMAdapterInterface):
    """Adapter for Llama local model integration with GPU acceleration"""
    
    async def initialize_model(self, model_name: str) -> bool:
        """Initialize Llama model"""
        try:
            # Initialize GPU acceleration
            self.gpu_manager = self.service_locator.get(GPUAccelerationManager)
            use_gpu = self.settings_manager.get("llm.use_gpu_acceleration", True)
            
            # Determine device to use
            if use_gpu and self.gpu_manager.cuda_available:
                self.device = "cuda"
                device_info = f"GPU: {self.gpu_manager.gpu_info['device_name']}"
            else:
                self.device = "cpu"
                device_info = "CPU (no GPU acceleration)"
                
            logger.info(f"Initializing Llama model on {device_info}")
            
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
                
            # Set GPU parameters
            n_gpu_layers = -1  # Use all layers on GPU if available
            if self.device == "cuda":
                if self.gpu_manager.vram_available < 4 * 1024 * 1024 * 1024:  # Less than 4GB VRAM
                    n_gpu_layers = 20  # Use fewer layers on GPU for low VRAM
                    
            # Load model
            from llama_cpp import Llama
            
            self.model = Llama(
                model_path=model_path,
                n_ctx=self.config.get("context_size", 2048),
                n_gpu_layers=n_gpu_layers if self.device == "cuda" else 0,
                seed=self.config.get("seed", 42),
                use_mlock=True
            )
                
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

## 3. Performance Optimization

### 3.1 Memory Management

Optimize memory usage to balance GPU and CPU resources:

```python
class MemoryOptimizer:
    """Optimizer for memory usage with GPU acceleration"""
    
    def __init__(self, gpu_manager):
        self.gpu_manager = gpu_manager
        
    def optimize_for_inference(self):
        """Apply memory optimizations for inference"""
        if not self.gpu_manager.cuda_available:
            return
            
        try:
            import torch
            import gc
            
            # Clear CUDA cache
            torch.cuda.empty_cache()
            
            # Run garbage collector
            gc.collect()
            
            # Optimize CUDA allocator
            torch.cuda.memory_stats()
            
        except ImportError:
            logger.warning("PyTorch not available, memory optimization skipped")
        except Exception as e:
            logger.error(f"Error in memory optimization: {e}")
            
    def get_memory_usage(self):
        """Get current memory usage statistics"""
        try:
            import torch
            import psutil
            
            stats = {}
            
            # System RAM
            system_memory = psutil.virtual_memory()
            stats["system_ram_total_gb"] = system_memory.total / (1024**3)
            stats["system_ram_used_gb"] = system_memory.used / (1024**3)
            stats["system_ram_percent"] = system_memory.percent
            
            # VRAM if available
            if self.gpu_manager.cuda_available:
                cuda_stats = torch.cuda.memory_stats()
                allocated = cuda_stats.get("allocated_bytes.all.current", 0)
                reserved = cuda_stats.get("reserved_bytes.all.current", 0)
                
                stats["vram_total_gb"] = self.gpu_manager.vram_available / (1024**3)
                stats["vram_allocated_gb"] = allocated / (1024**3)
                stats["vram_reserved_gb"] = reserved / (1024**3)
                stats["vram_percent"] = (allocated / self.gpu_manager.vram_available) * 100
                
            return stats
            
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return {}
```

### 3.2 Batch Processing Optimization

```python
class BatchOptimizer:
    """Optimizer for batch processing with GPU acceleration"""
    
    def __init__(self, gpu_manager, settings_manager):
        self.gpu_manager = gpu_manager
        self.settings_manager = settings_manager
        
    def get_optimal_batch_size(self):
        """Get optimal batch size based on available GPU resources"""
        if not self.gpu_manager.cuda_available:
            return 1
            
        # Get batch size from settings
        return self.settings_manager.get("llm.batch_size", 4)
        
    def process_in_batches(self, items, processing_func):
        """Process items in optimized batches"""
        batch_size = self.get_optimal_batch_size()
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_results = processing_func(batch)
            results.extend(batch_results)
            
        return results
```

## 4. Compatibility Detection

### 4.1 System Compatibility Check

```python
class SystemCompatibilityChecker:
    """Checker for system compatibility with GPU acceleration"""
    
    def check_gpu_compatibility(self):
        """Check if the system is compatible with GPU acceleration"""
        compatibility = {
            "has_compatible_gpu": False,
            "cuda_available": False,
            "cuda_version": None,
            "cudnn_available": False,
            "cudnn_version": None,
            "gpu_name": None,
            "driver_version": None,
            "vram_gb": 0,
            "tensor_cores_available": False,
            "recommendations": []
        }
        
        try:
            # Check for NVIDIA GPU
            if platform.system() == "Windows":
                import subprocess
                try:
                    output = subprocess.check_output(
                        ["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"],
                        universal_newlines=True
                    )
                    
                    if output.strip():
                        parts = output.strip().split(",")
                        if len(parts) >= 3:
                            compatibility["has_compatible_gpu"] = True
                            compatibility["gpu_name"] = parts[0].strip()
                            compatibility["driver_version"] = parts[1].strip()
                            
                            # Parse VRAM (convert from MiB to GB)
                            vram_text = parts[2].strip()
                            vram_value = float(vram_text.split()[0])
                            compatibility["vram_gb"] = vram_value / 1024
                            
                except (subprocess.SubprocessError, FileNotFoundError):
                    # nvidia-smi not available
                    pass
            
            # Check CUDA availability
            try:
                import torch
                compatibility["cuda_available"] = torch.cuda.is_available()
                
                if compatibility["cuda_available"]:
                    compatibility["cuda_version"] = torch.version.cuda
                    
                    # Check for cuDNN
                    if hasattr(torch.backends, 'cudnn'):
                        compatibility["cudnn_available"] = torch.backends.cudnn.is_available()
                        if compatibility["cudnn_available"] and hasattr(torch.backends.cudnn, 'version'):
                            compatibility["cudnn_version"] = torch.backends.cudnn.version()
                            
                    # Get GPU name if not already set
                    if not compatibility["gpu_name"] and torch.cuda.device_count() > 0:
                        compatibility["gpu_name"] = torch.cuda.get_device_name(0)
                        
                    # Check for tensor cores (based on architecture)
                    gpu_name = compatibility["gpu_name"] or ""
                    tensor_core_architectures = [
                        'Tesla V100', 'Quadro GV100',  # Volta
                        'RTX 20', 'Quadro RTX', 'T4',  # Turing
                        'RTX 30', 'A100', 'A40', 'A10',  # Ampere
                        'RTX 40', 'L40', 'L4',  # Ada Lovelace
                        'H100'  # Hopper
                    ]
                    compatibility["tensor_cores_available"] = any(arch in gpu_name for arch in tensor_core_architectures)
                    
            except ImportError:
                # PyTorch not available
                pass
                
            # Generate recommendations
            if not compatibility["has_compatible_gpu"]:
                compatibility["recommendations"].append(
                    "No NVIDIA GPU detected. For best performance, consider a system with an NVIDIA GPU."
                )
            elif not compatibility["cuda_available"]:
                compatibility["recommendations"].append(
                    "NVIDIA GPU detected but CUDA is not available. Install NVIDIA CUDA Toolkit 11.7 or later."
                )
            elif not compatibility["cudnn_available"]:
                compatibility["recommendations"].append(
                    "CUDA is available but cuDNN is not detected. Install cuDNN 8.6 or later for better performance."
                )
            elif compatibility["vram_gb"] < 4:
                compatibility["recommendations"].append(
                    f"GPU has limited VRAM ({compatibility['vram_gb']:.1f}GB). Some models may run slowly or with reduced context size."
                )
                
            return compatibility
            
        except Exception as e:
            logger.error(f"Error checking GPU compatibility: {e}")
            compatibility["recommendations"].append(
                f"Error checking GPU compatibility: {str(e)}"
            )
            return compatibility
```

## 5. Configuration Settings

### 5.1 GPU Settings Panel

Add a GPU settings panel to the application settings:

```python
class GPUSettingsPanel(SettingsPanelBase):
    """Settings panel for GPU acceleration configuration"""
    
    def __init__(self, settings_manager, gpu_manager):
        super().__init__("GPU Acceleration", settings_manager)
        self.gpu_manager = gpu_manager
        
    def create_panel(self):
        """Create the settings panel UI"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        
        # GPU information section
        gpu_group = QGroupBox("GPU Information")
        gpu_layout = QVBoxLayout(gpu_group)
        
        if self.gpu_manager.cuda_available:
            # Show GPU information
            gpu_info = self.gpu_manager.gpu_info
            
            info_layout = QFormLayout()
            info_layout.addRow("GPU Device:", QLabel(gpu_info.get('device_name', 'Unknown')))
            info_layout.addRow("CUDA Version:", QLabel(str(gpu_info.get('cuda_version', 'Unknown'))))
            info_layout.addRow("VRAM:", QLabel(f"{gpu_info.get('vram_mb', 0) / 1024:.1f} GB"))
            info_layout.addRow("Tensor Cores:", QLabel("Available" if gpu_info.get('tensor_cores_available') else "Not Available"))
            
            gpu_layout.addLayout(info_layout)
            
            # Status indicator
            status_label = QLabel("GPU Acceleration: Enabled")
            status_label.setStyleSheet("color: green; font-weight: bold;")
            gpu_layout.addWidget(status_label)
        else:
            # No GPU available
            gpu_layout.addWidget(QLabel("No CUDA-capable GPU detected"))
            
            status_label = QLabel("GPU Acceleration: Not Available")
            status_label.setStyleSheet("color: red; font-weight: bold;")
            gpu_layout.addWidget(status_label)
            
        layout.addWidget(gpu_group)
        
        # Settings section
        settings_group = QGroupBox("GPU Settings")
        settings_layout = QVBoxLayout(settings_group)
        
        # Enable GPU acceleration
        self.use_gpu_check = QCheckBox("Enable GPU Acceleration")
        self.use_gpu_check.setChecked(self.settings_manager.get("llm.use_gpu_acceleration", True))
        self.use_gpu_check.setEnabled(self.gpu_manager.cuda_available)
        self.use_gpu_check.stateChanged.connect(self._on_use_gpu_changed)
        settings_layout.addWidget(self.use_gpu_check)
        
        # Use tensor cores
        self.use_tensor_cores_check = QCheckBox("Use Tensor Cores (if available)")
        self.use_tensor_cores_check.setChecked(self.settings_manager.get("llm.use_tensor_cores", True))
        self.use_tensor_cores_check.setEnabled(self.gpu_manager.cuda_available and self.gpu_manager.tensor_cores_available)
        self.use_tensor_cores_check.stateChanged.connect(self._on_setting_changed)
        settings_layout.addWidget(self.use_tensor_cores_check)
        
        # Precision selection
        precision_layout = QHBoxLayout()
        precision_layout.addWidget(QLabel("Computation Precision:"))
        
        self.precision_combo = QComboBox()
        self.precision_combo.addItems(["float32", "float16", "bfloat16"])
        current_precision = self.settings_manager.get("llm.precision", "float16")
        self.precision_combo.setCurrentText(current_precision)
        self.precision_combo.setEnabled(self.gpu_manager.cuda_available)
        self.precision_combo.currentTextChanged.connect(self._on_setting_changed)
        precision_layout.addWidget(self.precision_combo)
        
        settings_layout.addLayout(precision_layout)
        
        # Batch size
        batch_layout = QHBoxLayout()
        batch_layout.addWidget(QLabel("Batch Size:"))
        
        self.batch_spin = QSpinBox()
        self.batch_spin.setRange(1, 64)
        self.batch_spin.setValue(self.settings_manager.get("llm.batch_size", 4))
        self.batch_spin.setEnabled(self.gpu_manager.cuda_available)
        self.batch_spin.valueChanged.connect(self._on_setting_changed)
        batch_layout.addWidget(self.batch_spin)
        
        settings_layout.addLayout(batch_layout)
        
        # Memory limit
        memory_layout = QHBoxLayout()
        memory_layout.addWidget(QLabel("Memory Usage Limit:"))
        
        self.memory_limit_spin = QSpinBox()
        self.memory_limit_spin.setRange(10, 100)
        self.memory_limit_spin.setSuffix("%")
        self.memory_limit_spin.setValue(self.settings_manager.get("llm.memory_limit_percent", 90))
        self.memory_limit_spin.setEnabled(self.gpu_manager.cuda_available)
        self.memory_limit_spin.valueChanged.connect(self._on_setting_changed)
        memory_layout.addWidget(self.memory_limit_spin)
        
        settings_layout.addLayout(memory_layout)
        
        layout.addWidget(settings_group)
        
        # Add performance tips
        tips_group = QGroupBox("Performance Tips")
        tips_layout = QVBoxLayout(tips_group)
        
        tips_text = (
            "• Lower precision (float16) gives better performance but may reduce accuracy\n"
            "• Tensor Cores provide significant speedups on supported GPUs\n"
            "• Higher batch sizes improve throughput but require more VRAM\n"
            "• Adjust memory limit if you experience out-of-memory errors"
        )
        
        tips_label = QLabel(tips_text)
        tips_label.setWordWrap(True)
        tips_layout.addWidget(tips_label)
        
        layout.addWidget(tips_group)
        
        # Add stretch to push everything to the top
        layout.addStretch(1)
        
        return panel
        
    def _on_use_gpu_changed(self, state):
        """Handle GPU acceleration toggle"""
        enabled = state == Qt.Checked
        
        # Update dependent controls
        self.use_tensor_cores_check.setEnabled(enabled and self.gpu_manager.tensor_cores_available)
        self.precision_combo.setEnabled(enabled)
        self.batch_spin.setEnabled(enabled)
        self.memory_limit_spin.setEnabled(enabled)
        
        self._on_setting_changed()
        
    def _on_setting_changed(self):
        """Handle setting changes"""
        # Mark panel as changed
        self.set_changed(True)
        
    def apply_settings(self):
        """Apply the current settings"""
        self.settings_manager.set("llm.use_gpu_acceleration", self.use_gpu_check.isChecked())
        self.settings_manager.set("llm.use_tensor_cores", self.use_tensor_cores_check.isChecked())
        self.settings_manager.set("llm.precision", self.precision_combo.currentText())
        self.settings_manager.set("llm.batch_size", self.batch_spin.value())
        self.settings_manager.set("llm.memory_limit_percent", self.memory_limit_spin.value())
        
        # Mark panel as unchanged
        self.set_changed(False)
        
        return True
        
    def reset_settings(self):
        """Reset settings to defaults"""
        # Restore default values
        self.use_gpu_check.setChecked(True)
        self.use_tensor_cores_check.setChecked(True)
        self.precision_combo.setCurrentText("float16")
        
        # Set batch size based on VRAM
        if self.gpu_manager.cuda_available:
            vram_mb = self.gpu_manager.vram_available / (1024 * 1024)
            
            if vram_mb >= 24000:  # High-end GPU (24GB+)
                self.batch_spin.setValue(32)
            elif vram_mb >= 8000:  # Mid-range GPU (8GB+)
                self.batch_spin.setValue(16)
            elif vram_mb >= 4000:  # Entry GPU (4GB+)
                self.batch_spin.setValue(8)
            else:  # Low VRAM
                self.batch_spin.setValue(4)
        else:
            self.batch_spin.setValue(1)
            
        self.memory_limit_spin.setValue(90)
        
        # Mark panel as changed
        self.set_changed(True)
```

## Conclusion

This GPU Acceleration Integration specification provides a comprehensive plan for utilizing NVIDIA CUDA GPUs in VPA. The implementation enables automatic detection of GPU capabilities, optimization of LLM inference using available tensor cores and CUDA cores, and provides user configuration through a dedicated settings panel.

By implementing this specification, VPA will benefit from significantly faster LLM inference, improved voice processing, and overall better performance on systems with NVIDIA GPUs.

---

*Document created on August 28, 2025*  
*Version: 1.0*
