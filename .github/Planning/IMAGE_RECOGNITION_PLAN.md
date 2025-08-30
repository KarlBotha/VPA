# Image Recognition Implementation Plan

## 1. Overview

This document outlines the specific implementation plan for integrating image recognition capabilities into the VPA (Virtual Personal Assistant) application. The image recognition system will be built using entirely free, commercially available components with a focus on local processing, privacy, and performance.

## 2. Core Capabilities

### 2.1 Object Detection
- Detect and classify common objects in images
- Provide bounding boxes and confidence scores
- Support for 80+ common object categories

### 2.2 Text Recognition (OCR)
- Extract text from images and documents
- Support for multiple languages
- Orientation detection and correction

### 2.3 Face Detection
- Detect faces in images
- Determine facial landmarks
- Privacy-first approach with no face recognition/identification

### 2.4 Scene Classification
- Categorize images into scene types
- Identify environmental contexts
- Provide descriptive tags for images

## 3. Technical Implementation

### 3.1 Architecture Components

#### 3.1.1 ImageProcessor Class
```python
class ImageProcessor:
    def __init__(self):
        """Initialize the image processor with default settings."""
        self._opencv_version = cv2.__version__
        self._supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
        self._max_image_size = (1024, 1024)  # Default max size for processing
        
    def load_image(self, source):
        """Load image from file path, URL, bytes, or numpy array."""
        # Implementation using OpenCV
        
    def resize_image(self, image, size=None):
        """Resize image while maintaining aspect ratio."""
        # Implementation using OpenCV
        
    def preprocess_for_model(self, image, target_size, color_conversion=None):
        """Prepare image for specific model requirements."""
        # Implementation using OpenCV
        
    def apply_filters(self, image, filters):
        """Apply a sequence of filters to an image."""
        # Implementation using OpenCV
        
    def extract_features(self, image, feature_type):
        """Extract specific features from an image."""
        # Implementation using OpenCV
```

#### 3.1.2 ModelManager Class
```python
class ModelManager:
    def __init__(self, models_dir="models"):
        """Initialize the model manager with models directory."""
        self._models_dir = models_dir
        self._models = {}
        self._model_info = {}
        os.makedirs(models_dir, exist_ok=True)
        
    def download_model(self, model_name, model_url):
        """Download a model if not already present."""
        # Implementation for model downloading
        
    def load_model(self, model_name):
        """Load a model into memory."""
        # Implementation using ONNX Runtime
        
    def unload_model(self, model_name):
        """Unload a model to free memory."""
        # Implementation for memory management
        
    def get_model(self, model_name):
        """Get a loaded model, loading it if necessary."""
        # Implementation with caching
        
    def list_available_models(self):
        """List all models available locally."""
        # Implementation for discovery
        
    def get_model_info(self, model_name):
        """Get metadata about a specific model."""
        # Implementation for model details
```

#### 3.1.3 ImageAnalyzer Class
```python
class ImageAnalyzer:
    def __init__(self, processor=None, model_manager=None):
        """Initialize with processor and model manager."""
        self.processor = processor or ImageProcessor()
        self.model_manager = model_manager or ModelManager()
        self._event_bus = None  # Set later via connect_event_bus
        
    def connect_event_bus(self, event_bus):
        """Connect to the event bus for publishing results."""
        self._event_bus = event_bus
        
    async def analyze_image(self, image_path, analysis_types=None):
        """Perform requested analysis types on an image."""
        # Implementation for orchestrating analysis
        
    async def detect_objects(self, image):
        """Detect objects in an image."""
        # Implementation using YOLO or SSD model
        
    async def recognize_text(self, image):
        """Extract text from an image."""
        # Implementation using OCR model
        
    async def detect_faces(self, image):
        """Detect faces in an image."""
        # Implementation using face detection model
        
    async def classify_scene(self, image):
        """Classify the scene/environment in an image."""
        # Implementation using classification model
        
    async def _publish_results(self, analysis_type, results, image_path):
        """Publish results to the event bus."""
        # Implementation for event emission
```

### 3.2 Models and Resources

#### 3.2.1 Object Detection Model
- **Model**: YOLOv8n ONNX model (smallest variant)
- **Source**: [Ultralytics YOLO](https://github.com/ultralytics/ultralytics)
- **License**: AGPL (model)/MIT (ONNX export)
- **Size**: ~6MB
- **Capabilities**: 80 classes (COCO dataset)
- **Performance**: ~30ms inference on CPU

#### 3.2.2 OCR Model
- **Model**: PaddleOCR ONNX export
- **Source**: [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- **License**: Apache 2.0
- **Size**: ~8MB
- **Capabilities**: Multi-language text detection and recognition
- **Performance**: ~100ms inference on CPU

#### 3.2.3 Face Detection Model
- **Model**: Ultra-Light-Fast-Generic-Face-Detector ONNX model
- **Source**: [Ultra-Light-Fast-Generic-Face-Detector](https://github.com/Linzaer/Ultra-Light-Fast-Generic-Face-Detector-1MB)
- **License**: MIT
- **Size**: ~1MB
- **Capabilities**: Face detection with bounding boxes
- **Performance**: ~10ms inference on CPU

#### 3.2.4 Scene Classification Model
- **Model**: MobileNet ONNX model
- **Source**: [ONNX Model Zoo](https://github.com/onnx/models)
- **License**: Apache 2.0
- **Size**: ~13MB
- **Capabilities**: 1000-class classification (ImageNet)
- **Performance**: ~20ms inference on CPU

### 3.3 Event Integration

#### 3.3.1 Event Types
- `image_analysis_request`: Triggered when an image analysis is requested
- `image_analysis_progress`: Periodic updates during analysis
- `image_analysis_complete`: Final results of analysis
- `image_analysis_error`: Error during analysis

#### 3.3.2 Event Data Structures

**Image Analysis Request**
```python
{
    "image_path": str,  # Path to image
    "analysis_types": List[str],  # Types of analysis to perform
    "request_id": str,  # Unique ID for this request
    "timestamp": float,  # Request time
    "priority": int,  # Priority level (higher = more important)
}
```

**Image Analysis Progress**
```python
{
    "request_id": str,  # Matching the request
    "progress": float,  # 0.0 to 1.0
    "current_operation": str,  # What's happening now
    "timestamp": float,  # Update time
}
```

**Image Analysis Complete**
```python
{
    "request_id": str,  # Matching the request
    "results": {
        "object_detection": List[Dict],  # Objects with coordinates
        "text_recognition": List[Dict],  # Text regions and content
        "face_detection": List[Dict],  # Face locations
        "scene_classification": List[Dict],  # Scene categories
    },
    "processing_time": float,  # Time taken in seconds
    "image_path": str,  # Original image path
    "timestamp": float,  # Completion time
}
```

**Image Analysis Error**
```python
{
    "request_id": str,  # Matching the request
    "error_type": str,  # Type of error
    "error_message": str,  # Human-readable error
    "image_path": str,  # Original image path
    "timestamp": float,  # Error time
}
```

### 3.4 UI Components

#### 3.4.1 Image Window Class
```python
class ImageWindow(CTkToplevel):
    def __init__(self, master, event_bus, *args, **kwargs):
        """Initialize the image window."""
        super().__init__(master, *args, **kwargs)
        self.title("Image Analysis")
        self.event_bus = event_bus
        self._setup_ui()
        
    def _setup_ui(self):
        """Create UI components for image analysis."""
        # Implementation for UI layout
        
    def load_image(self, image_path):
        """Load and display an image."""
        # Implementation using PIL/Pillow and CTkImage
        
    def show_results(self, results):
        """Display analysis results."""
        # Implementation for visualization
        
    def _on_upload_click(self):
        """Handle image upload button click."""
        # Implementation for file dialog
        
    def _on_paste_click(self):
        """Handle image paste from clipboard."""
        # Implementation for clipboard access
        
    def _on_camera_click(self):
        """Handle camera capture button click."""
        # Implementation for camera integration
        
    def _on_analyze_click(self):
        """Handle analyze button click."""
        # Implementation for analysis request emission
        
    def _subscribe_to_events(self):
        """Subscribe to relevant events."""
        # Implementation for event subscriptions
```

#### 3.4.2 Results Visualization
- Object boxes with labels and confidence scores
- Text regions with extracted content
- Face detection markers
- Scene classification results as tags
- Export options for results (JSON, CSV)

## 4. Implementation Phases

### 4.1 Phase 1: Core Framework (2 days)
- Implement `ImageProcessor` class with basic operations
- Implement `ModelManager` for model management
- Create directory structure and basic tests
- Set up ONNX Runtime integration

### 4.2 Phase 2: Model Integration (2 days)
- Download and integrate object detection model
- Implement object detection pipeline
- Create basic visualization functionality
- Add unit tests for detection

### 4.3 Phase 3: Additional Models (2 days)
- Integrate OCR, face detection, and scene classification models
- Implement complete analysis pipeline
- Add comprehensive error handling
- Create unit tests for all models

### 4.4 Phase 4: Event System Integration (1 day)
- Implement all event types and structures
- Connect analyzer to event bus
- Create progress reporting functionality
- Add performance monitoring

### 4.5 Phase 5: UI Components (2 days)
- Create `ImageWindow` class with upload functionality
- Implement visualization for all result types
- Add camera integration
- Create clipboard support
- Implement result export options

## 5. Testing Strategy

### 5.1 Unit Tests
- Test image loading from different sources
- Test model loading and inference
- Test preprocessing and postprocessing
- Test event emission and handling

### 5.2 Integration Tests
- Test end-to-end image analysis workflow
- Test UI interaction with analysis system
- Test error handling and recovery
- Test resource management

### 5.3 Performance Tests
- Benchmark analysis speed on various hardware
- Test memory usage during extended operation
- Test concurrent analysis requests
- Validate <3s response time target

## 6. User Experience Considerations

### 6.1 Image Upload Options
- File browser dialog
- Drag and drop support
- Clipboard paste (Ctrl+V)
- Camera capture
- URL input

### 6.2 Visualization Options
- Toggle different analysis results
- Adjust confidence threshold sliders
- Save annotated images
- Copy results to clipboard
- Export structured data

### 6.3 Accessibility Features
- Keyboard navigation for all functions
- Screen reader compatible result formats
- High contrast visualization option
- Text descriptions of visual results

## 7. Storage and Caching

### 7.1 Model Storage
- Models stored in `models/` directory
- Auto-download on first use (with permission)
- Version tracking for updates

### 7.2 Results Caching
- Recent analysis results cached in memory
- Persistent cache in SQLite database
- Cache invalidation on model update

### 7.3 Privacy Considerations
- All processing done locally
- No data sent to external servers
- Option to clear analysis history
- No persistent storage of analyzed images

## 8. Sample Code Implementations

### 8.1 Object Detection Implementation
```python
async def detect_objects(self, image_path):
    """Detect objects in an image using YOLOv8 ONNX model."""
    # Load and preprocess image
    image = self.processor.load_image(image_path)
    if image is None:
        return {"error": "Failed to load image"}
        
    # Prepare image for YOLO model
    input_tensor = self.processor.preprocess_for_model(
        image, 
        target_size=(640, 640),
        color_conversion=cv2.COLOR_BGR2RGB
    )
    
    # Get model and run inference
    model = self.model_manager.get_model("yolov8n")
    if model is None:
        return {"error": "Object detection model not available"}
    
    # Run inference
    start_time = time.time()
    outputs = model.run(
        None, 
        {"images": input_tensor.astype(np.float32) / 255.0}
    )
    inference_time = time.time() - start_time
    
    # Process detections
    detections = self._process_yolo_output(outputs[0], image.shape)
    
    return {
        "objects": detections,
        "processing_time": inference_time,
        "model": "yolov8n"
    }

def _process_yolo_output(self, output, original_shape):
    """Process YOLOv8 output to get meaningful detections."""
    results = []
    
    # YOLOv8 output format processing
    for detection in output:
        # Extract boxes, scores, class_ids
        boxes = detection[:, :4]  # x1, y1, x2, y2
        scores = detection[:, 4:5] * detection[:, 5:]  # obj_conf * cls_conf
        class_ids = np.argmax(detection[:, 5:], axis=1)
        
        # Filter by confidence
        mask = scores.flatten() > 0.5
        boxes = boxes[mask]
        scores = scores[mask].flatten()
        class_ids = class_ids[mask]
        
        # Rescale boxes to original image
        h, w = original_shape[:2]
        boxes = self._rescale_boxes(boxes, (640, 640), (w, h))
        
        # Create result objects
        for box, score, class_id in zip(boxes, scores, class_ids):
            x1, y1, x2, y2 = box.astype(int)
            results.append({
                "class": self.class_names[class_id],
                "confidence": float(score),
                "box": [int(x1), int(y1), int(x2), int(y2)]
            })
            
    return results
```

### 8.2 UI Integration Example
```python
class ImageAnalysisUI(CTkFrame):
    def __init__(self, master, event_bus, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.event_bus = event_bus
        self.image_path = None
        self.current_image = None
        self.analysis_results = None
        self.request_id = None
        self._setup_ui()
        self._subscribe_to_events()
        
    def _setup_ui(self):
        """Create UI components."""
        # Main layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Top controls frame
        self.controls_frame = CTkFrame(self)
        self.controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Control buttons
        self.upload_btn = CTkButton(
            self.controls_frame, 
            text="Upload Image", 
            command=self._on_upload_click
        )
        self.upload_btn.grid(row=0, column=0, padx=5, pady=5)
        
        self.paste_btn = CTkButton(
            self.controls_frame, 
            text="Paste from Clipboard", 
            command=self._on_paste_click
        )
        self.paste_btn.grid(row=0, column=1, padx=5, pady=5)
        
        self.camera_btn = CTkButton(
            self.controls_frame, 
            text="Camera Capture", 
            command=self._on_camera_click
        )
        self.camera_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Analysis options
        self.options_frame = CTkFrame(self.controls_frame)
        self.options_frame.grid(row=0, column=3, padx=10)
        
        self.objects_var = CTkBooleanVar(value=True)
        self.objects_cb = CTkCheckBox(
            self.options_frame, 
            text="Objects", 
            variable=self.objects_var
        )
        self.objects_cb.grid(row=0, column=0)
        
        self.text_var = CTkBooleanVar(value=True)
        self.text_cb = CTkCheckBox(
            self.options_frame, 
            text="Text", 
            variable=self.text_var
        )
        self.text_cb.grid(row=0, column=1)
        
        self.faces_var = CTkBooleanVar(value=True)
        self.faces_cb = CTkCheckBox(
            self.options_frame, 
            text="Faces", 
            variable=self.faces_var
        )
        self.faces_cb.grid(row=0, column=2)
        
        self.scenes_var = CTkBooleanVar(value=True)
        self.scenes_cb = CTkCheckBox(
            self.options_frame, 
            text="Scenes", 
            variable=self.scenes_var
        )
        self.scenes_cb.grid(row=0, column=3)
        
        # Analyze button
        self.analyze_btn = CTkButton(
            self.controls_frame,
            text="Analyze",
            command=self._on_analyze_click
        )
        self.analyze_btn.grid(row=0, column=4, padx=10)
        
        # Image display area
        self.image_frame = CTkFrame(self)
        self.image_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.image_frame.grid_columnconfigure(0, weight=1)
        self.image_frame.grid_rowconfigure(0, weight=1)
        
        self.image_label = CTkLabel(self.image_frame, text="No image loaded")
        self.image_label.grid(row=0, column=0, sticky="nsew")
        
        # Results panel
        self.results_frame = CTkFrame(self)
        self.results_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        
        self.results_text = CTkTextbox(self.results_frame, height=150)
        self.results_text.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.results_text.configure(state="disabled")
        
    def _on_upload_click(self):
        """Handle image upload button click."""
        file_types = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"),
            ("All files", "*.*")
        ]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if file_path:
            self.load_image(file_path)
            
    def load_image(self, image_path):
        """Load and display an image."""
        try:
            self.image_path = image_path
            pil_image = Image.open(image_path)
            
            # Resize while maintaining aspect ratio
            width, height = pil_image.size
            max_size = 800
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
                
            pil_image = pil_image.resize((new_width, new_height))
            
            # Convert to CTkImage
            self.current_image = CTkImage(
                light_image=pil_image,
                dark_image=pil_image,
                size=(new_width, new_height)
            )
            
            # Update display
            self.image_label.configure(image=self.current_image, text="")
            
            # Clear previous results
            self.results_text.configure(state="normal")
            self.results_text.delete("1.0", "end")
            self.results_text.configure(state="disabled")
            self.analysis_results = None
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            
    def _on_analyze_click(self):
        """Handle analyze button click."""
        if not self.image_path:
            messagebox.showinfo("Info", "Please load an image first")
            return
            
        # Get selected analysis types
        analysis_types = []
        if self.objects_var.get():
            analysis_types.append("object_detection")
        if self.text_var.get():
            analysis_types.append("text_recognition")
        if self.faces_var.get():
            analysis_types.append("face_detection")
        if self.scenes_var.get():
            analysis_types.append("scene_classification")
            
        if not analysis_types:
            messagebox.showinfo("Info", "Please select at least one analysis type")
            return
            
        # Generate request ID
        self.request_id = str(uuid.uuid4())
        
        # Show progress
        self.analyze_btn.configure(state="disabled", text="Analyzing...")
        
        # Emit analysis request event
        self.event_bus.emit("image_analysis_request", {
            "image_path": self.image_path,
            "analysis_types": analysis_types,
            "request_id": self.request_id,
            "timestamp": time.time(),
            "priority": 1
        })
        
    def _subscribe_to_events(self):
        """Subscribe to relevant events."""
        self.event_bus.subscribe(
            "image_analysis_progress",
            self._on_analysis_progress
        )
        self.event_bus.subscribe(
            "image_analysis_complete",
            self._on_analysis_complete
        )
        self.event_bus.subscribe(
            "image_analysis_error",
            self._on_analysis_error
        )
        
    def _on_analysis_complete(self, event_data):
        """Handle analysis completion."""
        if event_data["request_id"] != self.request_id:
            return
            
        # Store results
        self.analysis_results = event_data["results"]
        
        # Display results
        self._display_results()
        
        # Reset UI
        self.analyze_btn.configure(state="normal", text="Analyze")
        
    def _display_results(self):
        """Display analysis results on the image and in text panel."""
        if not self.analysis_results:
            return
            
        # Update text panel with results summary
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        
        # Create PIL image for drawing
        pil_image = Image.open(self.image_path)
        draw = ImageDraw.Draw(pil_image)
        
        # Process object detection results
        if "object_detection" in self.analysis_results:
            objects = self.analysis_results["object_detection"].get("objects", [])
            if objects:
                self.results_text.insert("end", f"Found {len(objects)} objects:\n")
                for i, obj in enumerate(objects):
                    # Draw box on image
                    box = obj["box"]
                    draw.rectangle(box, outline="red", width=3)
                    
                    # Add label
                    label = f"{obj['class']} ({obj['confidence']:.2f})"
                    draw.text((box[0], box[1]-15), label, fill="red")
                    
                    # Add to text results
                    self.results_text.insert("end", 
                        f"  {i+1}. {obj['class']} ({obj['confidence']:.2f})\n")
            else:
                self.results_text.insert("end", "No objects detected\n")
                
        # Process other results similarly...
        
        # Resize and display the annotated image
        width, height = pil_image.size
        max_size = 800
        if width > height:
            new_width = max_size
            new_height = int(height * (max_size / width))
        else:
            new_height = max_size
            new_width = int(width * (max_size / height))
            
        pil_image = pil_image.resize((new_width, new_height))
        
        # Update the displayed image
        self.current_image = CTkImage(
            light_image=pil_image,
            dark_image=pil_image,
            size=(new_width, new_height)
        )
        self.image_label.configure(image=self.current_image)
        
        self.results_text.configure(state="disabled")
```

## 9. Integration with VPA Core

### 9.1 Plugin Integration
- Create `ImageAnalysisPlugin` that leverages the core image system
- Respond to natural language queries about images
- Handle commands like "describe this image" or "what objects are in this picture?"

### 9.2 Event Communication
- Core system sends `image_analysis_request` events
- Image system returns `image_analysis_complete` events
- UI subscribes to events and displays results

### 9.3 Voice Integration
- TTS narration of image analysis results
- Voice commands to trigger image analysis
- Natural language processing of analysis requests

## 10. Conclusion

This image recognition implementation plan provides a comprehensive roadmap for integrating computer vision capabilities into the VPA system. By using free, commercially available components like OpenCV and ONNX Runtime with pre-trained models, we can deliver a powerful image analysis system that respects user privacy through local processing.

The implementation follows the event-driven architecture of the core VPA system and maintains the same high standards for performance, error handling, and user experience. The modular design allows for future expansion with additional models and capabilities without requiring architectural changes.

---

*This implementation plan was created on August 27, 2025, and represents the approved approach for adding image recognition capabilities to the VPA project.*
