# VPA Architecture Diagrams

## System Architecture Overview

```mermaid
graph TD
    %% Main Application Components
    User([User]) --> UI
    subgraph VPA["VPA Application"]
        UI[GUI System] --> Core
        Core[Core System] --> EB[Event Bus]
        Core --> PM[Plugin Manager]
        Core --> VS[Voice System]
        Core --> IR[Image Recognition]
        EB --> PM
        EB --> VS
        EB --> IR
        EB --> UI
        PM --> Plugins
    end
    
    %% Plugins and Extensions
    subgraph Plugins["Plugin Ecosystem"]
        WP[Weather Plugin]
        TP[Time Plugin] 
        SP[System Plugin]
        CP[Calculator Plugin]
        FP[Future Plugins...]
    end
    
    %% Voice System Details
    subgraph VoiceSystem["Voice System"]
        TTS[Text-to-Speech]
        VM[Voice Manager]
        TTS --> VM
        VM --> Voices
    end
    
    subgraph Voices["13-Voice Catalog"]
        V1[Voice 1]
        V2[Voice 2]
        V13[Voice 13]
        V1 --- V2 --- V13
    end
    
    %% Image Recognition System
    subgraph ImageSystem["Image Recognition"]
        IP[Image Processor]
        MM[Model Manager]
        IP --> MM
        MM --> Models
    end
    
    subgraph Models["Recognition Models"]
        OD[Object Detection]
        FR[Face Recognition]
        OCR[Text Recognition]
        SC[Scene Classification]
        OD --- FR --- OCR --- SC
    end
    
    %% Data Storage
    subgraph Data["Data Storage"]
        Config[Configuration]
        History[User History]
        Cache[Model Cache]
    end
    
    %% External Dependencies
    subgraph Dependencies["External Dependencies"]
        OpenCV[OpenCV]
        ONNX[ONNX Runtime]
        CTk[CustomTkinter]
        Pyttsx3[Pyttsx3]
    end
    
    %% Connections between components
    IR --> OpenCV
    IR --> ONNX
    UI --> CTk
    VS --> Pyttsx3
    Core --> Config
    IR --> Cache
    Core --> History
```

## Event Flow Architecture

```mermaid
sequenceDiagram
    participant User
    participant UI as GUI Interface
    participant Core as Application Core
    participant EB as Event Bus
    participant PM as Plugin Manager
    participant Plugin as Plugin Instance
    participant VS as Voice System
    participant IR as Image Recognition

    User->>UI: Interacts (text/voice/image)
    UI->>EB: Emits user_input event
    EB->>Core: Processes input
    Core->>PM: Requests plugin handling
    PM->>Plugin: Delegates to appropriate plugin
    Plugin->>EB: Emits processing_result event
    EB->>VS: Triggers voice synthesis
    VS->>UI: Returns audio for playback
    EB->>IR: Triggers image analysis (if image)
    IR->>EB: Emits image_analysis_result event
    EB->>UI: Updates with results
    UI->>User: Presents response
```

## Plugin Architecture

```mermaid
classDiagram
    class Plugin {
        <<interface>>
        +name() str
        +can_handle(input: str, context: Dict) bool
        +process(input: str, context: Dict) Dict
        +initialize()
        +cleanup()
    }

    class PluginManager {
        -plugins: Dict[str, Plugin]
        +load_plugins()
        +get_plugin(name: str) Plugin
        +get_all_plugins() List[Plugin]
        +find_handler(input: str, context: Dict) Plugin
    }

    class WeatherPlugin {
        +name() str
        +can_handle(input: str, context: Dict) bool
        +process(input: str, context: Dict) Dict
    }

    class TimePlugin {
        +name() str
        +can_handle(input: str, context: Dict) bool
        +process(input: str, context: Dict) Dict
    }

    class ImageAnalysisPlugin {
        +name() str
        +can_handle(input: str, context: Dict) bool
        +process(input: str, context: Dict) Dict
        -analyze_image(image_path: str) Dict
    }

    Plugin <|-- WeatherPlugin
    Plugin <|-- TimePlugin
    Plugin <|-- ImageAnalysisPlugin
    PluginManager --> Plugin
```

## Image Recognition Architecture

```mermaid
classDiagram
    class ImageProcessor {
        +process_image(image_path: str) Image
        +resize_image(image: Image, dims: Tuple) Image
        +convert_color_space(image: Image, space: str) Image
        +apply_filters(image: Image, filters: List) Image
        +extract_features(image: Image) Dict
    }

    class ModelManager {
        -models: Dict[str, Model]
        +load_model(model_name: str) Model
        +get_model(model_name: str) Model
        +unload_model(model_name: str) bool
        +list_models() List[str]
    }

    class Model {
        <<interface>>
        +name: str
        +predict(input_data: np.ndarray) Dict
        +get_metadata() Dict
        +get_requirements() Dict
    }

    class ObjectDetectionModel {
        +predict(input_data: np.ndarray) Dict
        -process_detections(raw_output: np.ndarray) Dict
    }

    class TextRecognitionModel {
        +predict(input_data: np.ndarray) Dict
        -process_text(raw_output: np.ndarray) Dict
    }

    class ImageAnalyzer {
        -image_processor: ImageProcessor
        -model_manager: ModelManager
        +analyze_image(image_path: str, analysis_types: List[str]) Dict
        +detect_objects(image: Image) Dict
        +recognize_text(image: Image) Dict
        +detect_faces(image: Image) Dict
        +classify_scene(image: Image) Dict
    }

    Model <|-- ObjectDetectionModel
    Model <|-- TextRecognitionModel
    ImageAnalyzer --> ImageProcessor
    ImageAnalyzer --> ModelManager
    ModelManager --> Model
```

## Voice System Architecture

```mermaid
classDiagram
    class VoiceSystem {
        -voices: Dict[str, VoiceInfo]
        +initialize()
        +get_available_voices() List[VoiceInfo]
        +synthesize_speech(text: str, voice_id: str) AudioResult
        +verify_voice_catalog() Dict[str, bool]
    }

    class VoiceInfo {
        +id: str
        +name: str
        +gender: str
        +language: str
        +engine: str
    }

    class AudioResult {
        +audio_data: bytes
        +duration: float
        +sample_rate: int
        +channels: int
    }

    class TTSEngine {
        <<interface>>
        +get_voices() List[VoiceInfo]
        +synthesize(text: str, voice_id: str) AudioResult
    }

    class Pyttsx3Engine {
        +get_voices() List[VoiceInfo]
        +synthesize(text: str, voice_id: str) AudioResult
    }

    class SAAPIEngine {
        +get_voices() List[VoiceInfo]
        +synthesize(text: str, voice_id: str) AudioResult
    }

    TTSEngine <|-- Pyttsx3Engine
    TTSEngine <|-- SAAPIEngine
    VoiceSystem --> TTSEngine
    VoiceSystem --> VoiceInfo
    VoiceSystem --> AudioResult
```

## Event Bus Architecture

```mermaid
classDiagram
    class EventBus {
        -subscribers: Dict[str, List[Callback]]
        +subscribe(event_type: str, callback: Callable, async_callback: bool)
        +unsubscribe(event_type: str, callback: Callable)
        +emit(event_type: str, data: Dict) None
        +emit_async(event_type: str, data: Dict) Awaitable[None]
        +cleanup() None
    }

    class Callback {
        +func: Callable
        +async_callback: bool
        +call(data: Dict) Any
    }

    class Event {
        +type: str
        +data: Dict
        +timestamp: float
    }

    EventBus --> Callback
    EventBus --> Event
```

## Database Architecture

```mermaid
erDiagram
    SETTINGS {
        string key PK
        string value
        string category
        datetime last_updated
    }
    
    PLUGIN {
        string name PK
        boolean enabled
        int priority
        string version
        string path
        datetime last_loaded
    }
    
    VOICE {
        string id PK
        string name
        string gender
        string language
        string engine
        float rate
        float volume
    }
    
    IMAGE_ANALYSIS {
        string id PK
        string path
        datetime timestamp
        string analysis_type
        json results
        int processing_time
    }
    
    USER_INPUT {
        string id PK
        string input_text
        datetime timestamp
        string input_type
        string handled_by
    }
    
    USER_INTERACTION {
        string id PK
        string session_id FK
        string type
        datetime timestamp
        json data
    }
    
    SESSION {
        string id PK
        datetime start_time
        datetime end_time
        string user
    }
    
    PLUGIN ||--o{ USER_INTERACTION : "generates"
    SESSION ||--o{ USER_INTERACTION : "contains"
    SESSION ||--o{ USER_INPUT : "contains"
    IMAGE_ANALYSIS }|--|| USER_INPUT : "derived_from"
```

---

*These architectural diagrams represent the planned implementation for the VPA system with image recognition capabilities. The diagrams are generated using Mermaid syntax and can be rendered in compatible Markdown viewers.*
