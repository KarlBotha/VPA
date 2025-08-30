# Performance Targets

## Overview

This document establishes concrete performance targets for the VPA application, defining metrics for responsiveness, resource usage, and scalability to ensure an optimal user experience.

## Table of Contents

1. [Response Time Targets](#1-response-time-targets)
2. [Resource Usage Targets](#2-resource-usage-targets)
3. [Scalability Targets](#3-scalability-targets)
4. [Performance Monitoring](#4-performance-monitoring)
5. [Performance Optimization Strategies](#5-performance-optimization-strategies)

## 1. Response Time Targets

### 1.1 UI Responsiveness

| Interaction | Target Time | Maximum Acceptable |
|-------------|-------------|-------------------|
| Application startup | < 3 seconds | 5 seconds |
| Window rendering | < 100ms | 200ms |
| Button/control response | < 50ms | 100ms |
| Menu opening | < 100ms | 200ms |
| Tab switching | < 150ms | 300ms |
| Settings changes | < 200ms | 500ms |

### 1.2 Chat Interaction Response Times

| Interaction | Target Time | Maximum Acceptable |
|-------------|-------------|-------------------|
| Message display | < 100ms | 200ms |
| Input field response | < 50ms | 100ms |
| Chat history loading (50 messages) | < 500ms | 1 second |
| Chat history scrolling | < 50ms | 150ms |
| Image attachment preview | < 200ms | 500ms |

### 1.3 LLM Response Times

| Model Type | First Token Response | Tokens Per Second | Complete Response |
|------------|---------------------|-------------------|------------------|
| Local - Small (Phi-3 Mini) | < 500ms | 15+ | < 5 seconds |
| Local - Medium (Llama 3 8B) | < 1 second | 10+ | < 8 seconds |
| Cloud API | < 1 second | 20+ | < 5 seconds |

### 1.4 Voice Processing Times

| Operation | Target Time | Maximum Acceptable |
|-----------|-------------|-------------------|
| Voice recording start | < 100ms | 250ms |
| Voice-to-text (5 seconds audio) | < 1 second | 3 seconds |
| Voice-to-text (30 seconds audio) | < 3 seconds | 8 seconds |
| Text-to-speech generation | < 500ms | 2 seconds |

## 2. Resource Usage Targets

### 2.1 Memory Usage

| Configuration | Idle Memory | Active Memory | Peak Memory |
|--------------|-------------|--------------|-------------|
| Minimum (UI only) | < 150MB | < 250MB | < 350MB |
| Standard (UI + API models) | < 200MB | < 300MB | < 500MB |
| Full (UI + local small model) | < 500MB | < 2GB | < 4GB |
| Full (UI + local medium model) | < 600MB | < 5GB | < 8GB |

### 2.2 CPU Usage

| Operation | Target CPU Usage | Maximum Acceptable |
|-----------|-----------------|-------------------|
| Idle | < 0.5% | 1% |
| Chat interaction | < 5% | 15% |
| LLM inference (CPU only) | < 60% | 90% |
| Voice processing | < 30% | 60% |
| Background operations | < 10% | 20% |

### 2.3 GPU Usage

| Operation | Target GPU Usage | Maximum Acceptable | VRAM Usage |
|-----------|-----------------|-------------------|-----------|
| Idle | < 0.1% | 1% | < 100MB |
| UI rendering | < 5% | 10% | < 200MB |
| LLM inference (small model) | < 40% | 70% | < 2GB |
| LLM inference (medium model) | < 60% | 90% | < 4GB |

### 2.4 Disk Usage

| Component | Target Size | Maximum Acceptable |
|-----------|------------|-------------------|
| Application core | < 100MB | 150MB |
| Application with dependencies | < 200MB | 300MB |
| Per LLM model | Varies by model | Model specific |
| Database (1000 conversations) | < 50MB | 100MB |
| Settings and cache | < 20MB | 50MB |
| Total installation (no models) | < 250MB | 400MB |

### 2.5 Network Usage

| Operation | Target Usage | Maximum Acceptable | Frequency |
|-----------|-------------|-------------------|-----------|
| API model chat (1000 tokens) | < 100KB | 250KB | Per interaction |
| Update check | < 10KB | 20KB | Daily |
| Telemetry (if enabled) | < 5KB | 10KB | Per session |

## 3. Scalability Targets

### 3.1 Conversation History

| Metric | Target | Maximum Supported |
|--------|--------|-------------------|
| Messages per conversation | 1,000 | 10,000 |
| Concurrent conversation documents | 100 | 1,000 |
| Attachments per conversation | 50 | 200 |
| Total conversations | 1,000 | Limited by disk space |

### 3.2 Event Processing

| Metric | Target Throughput | Maximum Throughput |
|--------|-------------------|-------------------|
| UI events | 1,000/second | 5,000/second |
| Application events | 500/second | 2,000/second |
| Background tasks | 50/second | 200/second |

### 3.3 Database Operations

| Operation | Target Time | Maximum Acceptable |
|-----------|-------------|-------------------|
| Message insert | < 10ms | 50ms |
| Conversation retrieval | < 50ms | 200ms |
| Full-text search | < 200ms | 1 second |
| Batch operation (100 records) | < 500ms | 2 seconds |

## 4. Performance Monitoring

### 4.1 Metrics Collection

The following metrics will be collected to monitor performance:

```python
class PerformanceMonitor:
    """Monitors application performance"""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.metrics = {}
        self.start_time = time.time()
        self.is_enabled = settings_manager.get("performance.monitoring_enabled", True)
        
    def start_measurement(self, metric_name):
        """Start measuring a performance metric"""
        if not self.is_enabled:
            return
            
        self.metrics[metric_name] = {
            "start": time.perf_counter(),
            "memory_start": self._get_memory_usage()
        }
        
    def end_measurement(self, metric_name):
        """End measuring a performance metric and record results"""
        if not self.is_enabled or metric_name not in self.metrics:
            return
            
        metric = self.metrics[metric_name]
        end_time = time.perf_counter()
        
        # Calculate duration
        duration = end_time - metric["start"]
        
        # Get memory usage
        memory_end = self._get_memory_usage()
        memory_diff = memory_end - metric["memory_start"]
        
        # Record metrics
        if "samples" not in metric:
            metric["samples"] = []
            
        metric["samples"].append({
            "duration": duration,
            "memory_diff": memory_diff,
            "timestamp": time.time()
        })
        
        # Keep only recent samples
        max_samples = self.settings_manager.get("performance.max_metric_samples", 100)
        if len(metric["samples"]) > max_samples:
            metric["samples"] = metric["samples"][-max_samples:]
            
        # Update statistics
        self._update_statistics(metric_name)
        
        return duration
        
    def _update_statistics(self, metric_name):
        """Update statistics for a metric"""
        metric = self.metrics[metric_name]
        samples = [s["duration"] for s in metric["samples"]]
        
        metric["min"] = min(samples)
        metric["max"] = max(samples)
        metric["avg"] = sum(samples) / len(samples)
        
        # Calculate 95th percentile
        sorted_samples = sorted(samples)
        index = int(len(sorted_samples) * 0.95)
        metric["p95"] = sorted_samples[index]
        
    def _get_memory_usage(self):
        """Get current memory usage in bytes"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss
        except:
            return 0
            
    def get_metrics_report(self):
        """Get a report of all metrics"""
        if not self.is_enabled:
            return {"enabled": False}
            
        report = {
            "enabled": True,
            "uptime": time.time() - self.start_time,
            "metrics": {}
        }
        
        # Add metrics to report
        for name, metric in self.metrics.items():
            if "avg" in metric:
                report["metrics"][name] = {
                    "min": metric["min"],
                    "max": metric["max"],
                    "avg": metric["avg"],
                    "p95": metric["p95"],
                    "samples": len(metric["samples"])
                }
                
        # Add system metrics
        try:
            import psutil
            process = psutil.Process()
            
            report["system"] = {
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent(),
                "memory_mb": process.memory_info().rss / (1024 * 1024),
                "threads": len(process.threads())
            }
        except:
            report["system"] = {}
            
        return report
        
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = {}
        self.start_time = time.time()
```

### 4.2 Performance Monitoring UI

```python
class PerformanceMonitorDialog(QDialog):
    """Dialog for monitoring application performance"""
    
    def __init__(self, parent=None, performance_monitor=None):
        super().__init__(parent)
        self.performance_monitor = performance_monitor
        self.setWindowTitle("Performance Monitor")
        self.setMinimumSize(700, 500)
        self._setup_ui()
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_metrics)
        self.update_timer.start(1000)  # Update every second
        
    def _setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        
        # System metrics section
        system_group = QGroupBox("System Resources")
        system_layout = QGridLayout(system_group)
        
        # CPU usage
        system_layout.addWidget(QLabel("CPU Usage:"), 0, 0)
        self.cpu_usage = QProgressBar()
        system_layout.addWidget(self.cpu_usage, 0, 1)
        
        # Memory usage
        system_layout.addWidget(QLabel("Memory Usage:"), 1, 0)
        self.memory_usage = QProgressBar()
        system_layout.addWidget(self.memory_usage, 1, 1)
        
        # Memory amount
        system_layout.addWidget(QLabel("Memory (MB):"), 2, 0)
        self.memory_amount = QLabel("0 MB")
        system_layout.addWidget(self.memory_amount, 2, 1)
        
        # Thread count
        system_layout.addWidget(QLabel("Threads:"), 3, 0)
        self.thread_count = QLabel("0")
        system_layout.addWidget(self.thread_count, 3, 1)
        
        # Uptime
        system_layout.addWidget(QLabel("Uptime:"), 4, 0)
        self.uptime_label = QLabel("0:00:00")
        system_layout.addWidget(self.uptime_label, 4, 1)
        
        layout.addWidget(system_group)
        
        # Metrics table
        metrics_group = QGroupBox("Performance Metrics")
        metrics_layout = QVBoxLayout(metrics_group)
        
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(5)
        self.metrics_table.setHorizontalHeaderLabels(["Metric", "Min (ms)", "Avg (ms)", "Max (ms)", "95% (ms)"])
        self.metrics_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        metrics_layout.addWidget(self.metrics_table)
        
        layout.addWidget(metrics_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._update_metrics)
        
        self.reset_button = QPushButton("Reset Metrics")
        self.reset_button.clicked.connect(self._reset_metrics)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Initial update
        self._update_metrics()
        
    def _update_metrics(self):
        """Update displayed metrics"""
        report = self.performance_monitor.get_metrics_report()
        
        # Update system metrics
        system = report.get("system", {})
        
        # CPU usage
        cpu_percent = system.get("cpu_percent", 0)
        self.cpu_usage.setValue(int(cpu_percent))
        self.cpu_usage.setFormat(f"{cpu_percent:.1f}%")
        
        # Memory usage
        memory_percent = system.get("memory_percent", 0)
        self.memory_usage.setValue(int(memory_percent))
        self.memory_usage.setFormat(f"{memory_percent:.1f}%")
        
        # Memory amount
        memory_mb = system.get("memory_mb", 0)
        self.memory_amount.setText(f"{memory_mb:.1f} MB")
        
        # Thread count
        self.thread_count.setText(str(system.get("threads", 0)))
        
        # Uptime
        uptime = report.get("uptime", 0)
        hours = int(uptime / 3600)
        minutes = int((uptime % 3600) / 60)
        seconds = int(uptime % 60)
        self.uptime_label.setText(f"{hours}:{minutes:02d}:{seconds:02d}")
        
        # Update metrics table
        metrics = report.get("metrics", {})
        self.metrics_table.setRowCount(len(metrics))
        
        for i, (name, data) in enumerate(metrics.items()):
            # Metric name
            self.metrics_table.setItem(i, 0, QTableWidgetItem(name))
            
            # Min (convert to ms)
            min_ms = data.get("min", 0) * 1000
            self.metrics_table.setItem(i, 1, QTableWidgetItem(f"{min_ms:.2f}"))
            
            # Avg (convert to ms)
            avg_ms = data.get("avg", 0) * 1000
            self.metrics_table.setItem(i, 2, QTableWidgetItem(f"{avg_ms:.2f}"))
            
            # Max (convert to ms)
            max_ms = data.get("max", 0) * 1000
            self.metrics_table.setItem(i, 3, QTableWidgetItem(f"{max_ms:.2f}"))
            
            # 95th percentile (convert to ms)
            p95_ms = data.get("p95", 0) * 1000
            self.metrics_table.setItem(i, 4, QTableWidgetItem(f"{p95_ms:.2f}"))
            
        self.metrics_table.sortItems(0)
        
    def _reset_metrics(self):
        """Reset all metrics"""
        self.performance_monitor.reset_metrics()
        self._update_metrics()
```

## 5. Performance Optimization Strategies

### 5.1 Application Startup Optimization

#### 5.1.1 Lazy Loading

Implement lazy loading for non-essential components:

```python
class LazyLoadManager:
    """Manages lazy loading of application components"""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.loaded_components = set()
        self.component_loaders = {}
        self.priorities = {}
        self.loading_queue = []
        self.is_loading = False
        
    def register_component(self, component_id, loader_func, priority=5):
        """Register a component for lazy loading"""
        self.component_loaders[component_id] = loader_func
        self.priorities[component_id] = priority
        
    def load_component(self, component_id):
        """Load a specific component"""
        if component_id in self.loaded_components:
            return True
            
        if component_id not in self.component_loaders:
            return False
            
        # Add to loading queue
        if component_id not in self.loading_queue:
            self.loading_queue.append(component_id)
            
        # Start loading if not already
        if not self.is_loading:
            self._process_loading_queue()
            
        return True
        
    async def _process_loading_queue(self):
        """Process loading queue"""
        if not self.loading_queue or self.is_loading:
            return
            
        self.is_loading = True
        
        try:
            # Sort by priority
            self.loading_queue.sort(key=lambda c: self.priorities.get(c, 5))
            
            # Process queue
            while self.loading_queue:
                component_id = self.loading_queue[0]
                
                if component_id not in self.loaded_components:
                    # Notify loading
                    await self.event_bus.emit_async("component.loading", {
                        "component_id": component_id
                    })
                    
                    # Load component
                    loader = self.component_loaders[component_id]
                    await loader()
                    
                    # Mark as loaded
                    self.loaded_components.add(component_id)
                    
                    # Notify loaded
                    await self.event_bus.emit_async("component.loaded", {
                        "component_id": component_id
                    })
                    
                # Remove from queue
                self.loading_queue.pop(0)
                
        finally:
            self.is_loading = False
```

#### 5.1.2 Background Initialization

Implement background initialization for heavy components:

```python
class BackgroundInitializer:
    """Initializes components in background threads"""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.init_tasks = {}
        self.completed_tasks = set()
        
    def schedule_init(self, task_id, init_func):
        """Schedule initialization task"""
        self.init_tasks[task_id] = init_func
        
        # Start task in background thread
        threading.Thread(target=self._run_task, args=(task_id, init_func), daemon=True).start()
        
    def _run_task(self, task_id, init_func):
        """Run initialization task in background"""
        try:
            # Initialize component
            init_func()
            
            # Mark as completed
            self.completed_tasks.add(task_id)
            
            # Notify completion
            asyncio.run(self.event_bus.emit_async("background_init.completed", {
                "task_id": task_id
            }))
            
        except Exception as e:
            # Notify error
            asyncio.run(self.event_bus.emit_async("background_init.error", {
                "task_id": task_id,
                "error": str(e)
            }))
```

### 5.2 UI Rendering Optimization

#### 5.2.1 Virtual Scrolling for Chat History

Implement virtual scrolling for chat history to improve performance:

```python
class VirtualScrollChat(QScrollArea):
    """Chat view with virtual scrolling"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(16, 16, 16, 16)
        self.content_layout.setSpacing(16)
        self.content_layout.addStretch(1)  # Push messages to top
        self.setWidget(self.content_widget)
        
        # Message containers
        self.visible_widgets = {}
        self.recycled_widgets = []
        
        # Message data
        self.messages = []
        self.visible_range = (0, 0)
        
        # Connect scroll
        self.verticalScrollBar().valueChanged.connect(self._on_scroll)
        
    def set_messages(self, messages):
        """Set messages data"""
        self.messages = messages
        self._update_visible_messages()
        
    def add_message(self, message):
        """Add a new message"""
        self.messages.append(message)
        self._update_visible_messages()
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        
    def clear_messages(self):
        """Clear all messages"""
        self.messages = []
        self._update_visible_messages()
        
    def _on_scroll(self, value):
        """Handle scroll events"""
        self._update_visible_messages()
        
    def _update_visible_messages(self):
        """Update visible messages based on scroll position"""
        if not self.messages:
            # Clear all widgets
            for widget in self.visible_widgets.values():
                widget.setParent(None)
                self.recycled_widgets.append(widget)
            self.visible_widgets = {}
            return
            
        # Calculate visible range
        scroll_value = self.verticalScrollBar().value()
        viewport_height = self.viewport().height()
        
        # Estimate message height (assuming average message height of 100px)
        message_height = 100
        
        # Calculate visible range (with buffer)
        first_visible = max(0, scroll_value // message_height - 5)
        last_visible = min(len(self.messages), (scroll_value + viewport_height) // message_height + 5)
        
        new_range = (first_visible, last_visible)
        
        if new_range == self.visible_range:
            return
            
        # Update visible range
        self.visible_range = new_range
        
        # Remove no longer visible messages
        to_remove = []
        for idx in self.visible_widgets.keys():
            if idx < first_visible or idx >= last_visible:
                widget = self.visible_widgets[idx]
                widget.setParent(None)
                self.recycled_widgets.append(widget)
                to_remove.append(idx)
                
        for idx in to_remove:
            del self.visible_widgets[idx]
            
        # Add newly visible messages
        for idx in range(first_visible, last_visible):
            if idx not in self.visible_widgets:
                message = self.messages[idx]
                
                # Create or reuse widget
                if self.recycled_widgets:
                    widget = self.recycled_widgets.pop()
                    widget.update_message(message)
                else:
                    widget = ChatBubble(message, message.is_user)
                    
                # Add to layout
                self.content_layout.insertWidget(idx, widget)
                self.visible_widgets[idx] = widget
```

#### 5.2.2 Efficient Rendering with QPixmapCache

Optimize image rendering using QPixmapCache:

```python
class OptimizedImageProvider:
    """Provides optimized image loading and caching"""
    
    def __init__(self):
        from PyQt6.QtGui import QPixmapCache
        # Set cache size to 50MB
        QPixmapCache.setCacheLimit(50 * 1024)
        
    def get_pixmap(self, image_path, size=None, border_radius=0):
        """Get pixmap from path with optional size and rounding"""
        from PyQt6.QtGui import QPixmap, QPixmapCache, QPainter, QPainterPath
        
        # Create cache key
        cache_key = f"{image_path}_{size}_{border_radius}"
        
        # Check cache
        pixmap = QPixmapCache.find(cache_key)
        if pixmap:
            return pixmap
            
        # Load image
        pixmap = QPixmap(image_path)
        
        # Resize if needed
        if size and (pixmap.width() > size[0] or pixmap.height() > size[1]):
            pixmap = pixmap.scaled(size[0], size[1], Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            
        # Apply border radius if needed
        if border_radius > 0:
            rounded = QPixmap(pixmap.size())
            rounded.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            path = QPainterPath()
            path.addRoundedRect(0, 0, pixmap.width(), pixmap.height(), border_radius, border_radius)
            
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            
            pixmap = rounded
            
        # Add to cache
        QPixmapCache.insert(cache_key, pixmap)
        
        return pixmap
```

### 5.3 Memory Management

#### 5.3.1 Memory Monitor and Optimization

```python
class MemoryManager:
    """Manages memory usage and optimizations"""
    
    def __init__(self, settings_manager, event_bus):
        self.settings_manager = settings_manager
        self.event_bus = event_bus
        self.memory_threshold = settings_manager.get("performance.memory_threshold_mb", 1000) * 1024 * 1024  # MB to bytes
        self.critical_threshold = settings_manager.get("performance.critical_memory_threshold_mb", 1500) * 1024 * 1024  # MB to bytes
        self.monitor_interval = settings_manager.get("performance.memory_monitor_interval_seconds", 30)
        self.is_running = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start memory monitoring"""
        if self.is_running:
            return
            
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop memory monitoring"""
        self.is_running = False
        
    def _monitor_loop(self):
        """Memory monitoring loop"""
        while self.is_running:
            self._check_memory()
            time.sleep(self.monitor_interval)
            
    def _check_memory(self):
        """Check current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_usage = process.memory_info().rss
            
            # Log memory usage
            logging.debug(f"Memory usage: {memory_usage / (1024 * 1024):.2f} MB")
            
            # Check thresholds
            if memory_usage > self.critical_threshold:
                # Critical memory usage - perform immediate optimization
                logging.warning(f"Critical memory usage: {memory_usage / (1024 * 1024):.2f} MB")
                asyncio.run(self.event_bus.emit_async("memory.critical", {
                    "memory_mb": memory_usage / (1024 * 1024)
                }))
                self._optimize_memory(True)
                
            elif memory_usage > self.memory_threshold:
                # High memory usage - perform standard optimization
                logging.info(f"High memory usage: {memory_usage / (1024 * 1024):.2f} MB")
                asyncio.run(self.event_bus.emit_async("memory.high", {
                    "memory_mb": memory_usage / (1024 * 1024)
                }))
                self._optimize_memory(False)
                
        except Exception as e:
            logging.error(f"Error in memory monitor: {e}")
            
    def _optimize_memory(self, is_critical):
        """Optimize memory usage"""
        try:
            # Clear pixmap cache
            from PyQt6.QtGui import QPixmapCache
            QPixmapCache.clear()
            
            # Run garbage collection
            import gc
            gc.collect()
            
            if is_critical:
                # More aggressive optimizations for critical state
                
                # Clear LLM cache if available
                asyncio.run(self.event_bus.emit_async("llm.clear_cache"))
                
                # Trim conversation history in memory
                asyncio.run(self.event_bus.emit_async("conversation.trim_history"))
                
                # Notify user
                asyncio.run(self.event_bus.emit_async("notification.show", {
                    "title": "Memory Optimization",
                    "message": "High memory usage detected. Some cached data has been cleared to optimize performance.",
                    "type": "warning"
                }))
                
        except Exception as e:
            logging.error(f"Error optimizing memory: {e}")
```

### 5.4 LLM Optimization

#### 5.4.1 Quantization and Optimization

Implement adaptive model quantization based on hardware:

```python
class ModelOptimizer:
    """Optimizes LLM models based on hardware"""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        
    async def get_optimal_settings(self, model_id):
        """Get optimal settings for a model based on hardware"""
        # Get hardware capabilities
        capabilities = await self._detect_hardware()
        
        # Default settings
        settings = {
            "quantization": "q4_K_M",  # Default: 4-bit quantization
            "gpu_layers": 0,           # Default: CPU only
            "num_threads": 4,          # Default: 4 threads
            "context_size": 2048,      # Default: 2K context
            "batch_size": 512          # Default: 512 token batch
        }
        
        # Optimize based on hardware
        if capabilities["cuda_available"]:
            # GPU optimizations
            gpu_vram = capabilities["gpu_vram_gb"]
            
            if gpu_vram >= 8:
                # High-end GPU
                settings["quantization"] = "q5_K_M"
                settings["gpu_layers"] = 100  # All layers on GPU
                settings["context_size"] = 8192
                settings["batch_size"] = 1024
            elif gpu_vram >= 6:
                # Mid-range GPU
                settings["quantization"] = "q4_K_M"
                settings["gpu_layers"] = 100  # All layers on GPU
                settings["context_size"] = 4096
                settings["batch_size"] = 512
            elif gpu_vram >= 4:
                # Entry GPU
                settings["quantization"] = "q4_0"
                settings["gpu_layers"] = 20  # Some layers on GPU
                settings["context_size"] = 4096
                settings["batch_size"] = 512
            else:
                # Low VRAM GPU
                settings["quantization"] = "q4_0"
                settings["gpu_layers"] = 1  # Only attention on GPU
                settings["context_size"] = 2048
                settings["batch_size"] = 256
                
        else:
            # CPU optimizations
            cpu_cores = capabilities["cpu_cores"]
            ram_gb = capabilities["total_ram_gb"]
            
            # Set thread count
            settings["num_threads"] = max(4, min(cpu_cores, 8))
            
            # Memory-based optimizations
            if ram_gb >= 16:
                settings["quantization"] = "q5_K_M"
                settings["context_size"] = 4096
            elif ram_gb >= 8:
                settings["quantization"] = "q4_K_M"
                settings["context_size"] = 2048
            else:
                settings["quantization"] = "q4_0"
                settings["context_size"] = 1024
                settings["batch_size"] = 256
                
        return settings
        
    async def _detect_hardware(self):
        """Detect hardware capabilities"""
        capabilities = {
            "cuda_available": False,
            "gpu_vram_gb": 0,
            "total_ram_gb": 8,  # Default
            "cpu_cores": 4      # Default
        }
        
        try:
            # Check CPU and RAM
            import psutil
            capabilities["total_ram_gb"] = psutil.virtual_memory().total / (1024**3)
            capabilities["cpu_cores"] = psutil.cpu_count(logical=False) or 4
            
            # Check CUDA
            try:
                import torch
                capabilities["cuda_available"] = torch.cuda.is_available()
                if capabilities["cuda_available"]:
                    capabilities["gpu_vram_gb"] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            except:
                pass
                
        except Exception as e:
            logging.error(f"Error detecting hardware: {e}")
            
        return capabilities
```

## Conclusion

This Performance Targets document establishes clear metrics and optimization strategies for the VPA application. By defining concrete goals for response times, resource usage, and scalability, VPA ensures a responsive and efficient user experience across different hardware configurations.

The implementation includes comprehensive monitoring and optimization mechanisms to track performance in real-time and adaptively manage resources. These strategies will help VPA meet its performance targets while providing a smooth and reliable user experience.

---

*Document created on August 28, 2025*  
*Version: 1.0*
