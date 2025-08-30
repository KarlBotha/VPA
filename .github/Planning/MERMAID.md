# VPA Mermaid Diagrams

## System Architecture Diagram

### Complete System Architecture
```mermaid
graph TB
    subgraph "User Interface Layer"
        A[User] --> B[Login Window]
        A --> C[Settings Window] 
        A --> D[Main Chat UI]
        B --> E[CustomTkinter Framework]
        C --> E
        D --> E
    end
    
    subgraph "Application Core"
        F[Event Bus] --> G[Application Manager]
        F --> H[Plugin Manager]
        F --> I[Configuration Manager]
        G --> J[Performance Monitor]
        H --> K[Plugin Cache]
    end
    
    subgraph "Voice System"
        L[Voice System Controller] --> M[Edge-TTS Neural Voices]
        L --> N[Windows SAPI Fallback]
        M --> O[13-Voice Catalog]
        N --> P[System Voices]
        L --> Q[Pygame Audio Playback]
    end
    
    subgraph "Data Layer"
        R[Config Files] --> S[voice_settings.json]
        R --> T[ui_settings.json]
        R --> U[default.yaml]
        R --> V[audio.yaml]
    end
    
    subgraph "Security & Auth"
        W[Authentication System] --> X[User Management]
        W --> Y[OAuth Integration]
        W --> Z[Session Manager]
    end
    
    %% Connections
    E --> F
    F --> L
    I --> R
    G --> W
    O --> AA[Andrew]
    O --> BB[Christopher]
    O --> CC[Guy]
    O --> DD[Roger]
    O --> EE[Eric]
    O --> FF[Steffan]
    O --> GG[Emma]
    O --> HH[Ava]
    O --> II[Aria]
    O --> JJ[Jenny]
    O --> KK[Libby]
    O --> LL[Michelle]
    
    %% Styling
    classDef coreSystem fill:#2D5B87,stroke:#1F4A73,stroke-width:2px,color:#fff
    classDef voiceSystem fill:#8B4513,stroke:#654321,stroke-width:2px,color:#fff
    classDef userInterface fill:#2E8B57,stroke:#1F5F3F,stroke-width:2px,color:#fff
    classDef dataLayer fill:#800080,stroke:#5A005A,stroke-width:2px,color:#fff
    
    class F,G,H,I,J,K coreSystem
    class L,M,N,O,P,Q voiceSystem  
    class A,B,C,D,E userInterface
    class R,S,T,U,V dataLayer
```

### Core Component Interaction
```mermaid
graph LR
    subgraph "Entry Point"
        A[main.py] --> B[App.startup()]
    end
    
    subgraph "Core Services"
        B --> C[ConfigManager.load()]
        B --> D[EventBus.initialize()]
        B --> E[PluginManager.load_plugins()]
        B --> F[VoiceSystem.initialize()]
    end
    
    subgraph "Service Dependencies"
        C --> G[config/*.json/*.yaml]
        D --> H[Event Subscriptions]
        E --> I[Plugin Discovery & Cache]
        F --> J[13-Voice Catalog Verification]
    end
    
    subgraph "Operational State"
        G --> K[App Ready]
        H --> K
        I --> K
        J --> K
        K --> L[GUI Launch Available]
        K --> M[Performance Monitoring Active]
    end
    
    %% Styling
    classDef entry fill:#FF6B6B,stroke:#E55555,stroke-width:3px,color:#fff
    classDef core fill:#4ECDC4,stroke:#3DB8B0,stroke-width:2px,color:#fff
    classDef deps fill:#45B7D1,stroke:#3A9BC1,stroke-width:2px,color:#fff
    classDef ready fill:#96CEB4,stroke:#7FB069,stroke-width:2px,color:#fff
    
    class A,B entry
    class C,D,E,F core
    class G,H,I,J deps
    class K,L,M ready
```

## Data Flow Diagrams

### User Interaction Flow
```mermaid
sequenceDiagram
    participant User
    participant GUI as GUI Component
    participant EventBus as Event Bus
    participant Plugin as Plugin Manager
    participant Voice as Voice System
    participant Audio as Audio Output

    User->>GUI: User Input (text/click/voice)
    GUI->>EventBus: emit("user_action", data)
    
    EventBus->>Plugin: dispatch_to_handlers()
    Plugin->>Plugin: find_matching_plugin()
    
    alt Plugin Found
        Plugin->>Plugin: plugin.process(input)
        Plugin->>EventBus: emit("response_ready", response)
    else No Plugin
        Plugin->>EventBus: emit("default_response", fallback)
    end
    
    EventBus->>Voice: voice_synthesis_request
    EventBus->>GUI: update_chat_display
    
    Voice->>Voice: Edge-TTS synthesis (<2s target)
    Voice->>Audio: play_audio_file()
    Audio->>User: Voice Output
    
    GUI->>User: Visual Response Update
    
    Note over User,Audio: Complete interaction cycle
```

### Voice Synthesis Pipeline  
```mermaid
flowchart TD
    A[Text Input] --> B{Voice System Available?}
    B -->|Yes| C[Select Voice from 13-Voice Catalog]
    B -->|No| D[System Error Handler]
    
    C --> E{Edge-TTS Available?}
    E -->|Yes| F[Neural Voice Synthesis]
    E -->|No| G[Windows SAPI Fallback]
    
    F --> H[Generate Audio File]
    G --> I[Generate SAPI Audio]
    
    H --> J[Pygame Audio Loading]
    I --> J
    
    J --> K{Audio Load Success?}
    K -->|Yes| L[Audio Playback]
    K -->|No| M[Audio Error Handler]
    
    L --> N[Cleanup Temp Files]
    M --> O[Error Recovery]
    
    N --> P[Performance Metrics Update]
    O --> P
    
    P --> Q{<2s Target Met?}
    Q -->|Yes| R[Success Event]
    Q -->|No| S[Performance Alert]
    
    %% Styling
    classDef success fill:#27AE60,stroke:#1E8B3A,stroke-width:2px,color:#fff
    classDef error fill:#E74C3C,stroke:#C0392B,stroke-width:2px,color:#fff
    classDef process fill:#3498DB,stroke:#2980B9,stroke-width:2px,color:#fff
    classDef decision fill:#F39C12,stroke:#E67E22,stroke-width:2px,color:#fff
    
    class R success
    class D,M,O,S error
    class A,F,G,H,I,J,L,N,P process
    class B,E,K,Q decision
```

### Plugin System Architecture
```mermaid
graph TB
    subgraph "Plugin Discovery"
        A[Directory Scan] --> B[src/vpa/plugins/]
        A --> C[plugins/]
        A --> D[~/.vpa/plugins/]
        B --> E[Plugin Cache]
        C --> E
        D --> E
    end
    
    subgraph "Plugin Loading"
        E --> F{Cache Valid?}
        F -->|Yes| G[Load from Cache]
        F -->|No| H[Full Directory Scan]
        G --> I[Dynamic Import]
        H --> I
        I --> J[Plugin Registration]
    end
    
    subgraph "Plugin Management"
        J --> K[Priority Sorting]
        K --> L[Dependency Resolution]
        L --> M[Event Subscription]
        M --> N[Error Boundary Setup]
    end
    
    subgraph "Runtime Processing"
        O[User Input] --> P[Plugin Manager]
        P --> Q{Find Handler}
        Q -->|Match| R[Plugin.can_handle()]
        Q -->|No Match| S[Default Handler]
        R --> T[Plugin.process()]
        T --> U{Success?}
        U -->|Yes| V[Return Response]
        U -->|No| W[Error Isolation]
        W --> X[Fallback Response]
    end
    
    %% Connections between subgraphs
    N --> P
    V --> Y[Event Bus Emit]
    X --> Y
    S --> Y
    
    %% Styling
    classDef discovery fill:#8E44AD,stroke:#7D3C98,stroke-width:2px,color:#fff
    classDef loading fill:#2980B9,stroke:#1F618D,stroke-width:2px,color:#fff
    classDef management fill:#27AE60,stroke:#1E8B3A,stroke-width:2px,color:#fff
    classDef runtime fill:#E67E22,stroke:#D35400,stroke-width:2px,color:#fff
    
    class A,B,C,D,E discovery
    class F,G,H,I,J loading
    class K,L,M,N management
    class O,P,Q,R,S,T,U,V,W,X,Y runtime
```

## Performance Monitoring Flow
```mermaid
graph TD
    subgraph "Performance Metrics Collection"
        A[Function Execution] --> B[@PerformanceMonitor.track_execution_time]
        B --> C[Start Timer]
        C --> D[Execute Function]
        D --> E[End Timer] 
        E --> F[Calculate Duration]
    end
    
    subgraph "Metric Analysis"
        F --> G{Target Met?}
        G -->|Startup < 10s| H[Startup Success]
        G -->|Memory < 2GB| I[Memory Success]
        G -->|Events < 10ms| J[Event Success]
        G -->|Voice < 2s| K[Voice Success]
        G -->|Target Exceeded| L[Performance Alert]
    end
    
    subgraph "Response Actions"
        H --> M[Update Success Metrics]
        I --> M
        J --> M
        K --> M
        L --> N[Emit Performance Warning]
        M --> O[Dashboard Update]
        N --> P[Optimization Trigger]
    end
    
    subgraph "Performance Targets"
        Q[Startup: 10s] --> R[Performance Goals]
        S[Memory: 2GB] --> R
        T[Events: 10ms] --> R
        U[Voice: 2s] --> R
        R --> V[System Health Score]
    end
    
    %% Styling
    classDef metrics fill:#3498DB,stroke:#2980B9,stroke-width:2px,color:#fff
    classDef analysis fill:#E74C3C,stroke:#C0392B,stroke-width:2px,color:#fff
    classDef actions fill:#27AE60,stroke:#1E8B3A,stroke-width:2px,color:#fff
    classDef targets fill:#9B59B6,stroke:#8E44AD,stroke-width:2px,color:#fff
    
    class A,B,C,D,E,F metrics
    class G,H,I,J,K,L analysis
    class M,N,O,P actions
    class Q,S,T,U,R,V targets
```

## GUI Component Lifecycle
```mermaid
stateDiagram-v2
    [*] --> WindowCreation
    
    state WindowCreation {
        [*] --> CreateTempRoot
        CreateTempRoot --> InitializeCustomTkinter
        InitializeCustomTkinter --> SetupGeometry
        SetupGeometry --> ApplyTheme
        ApplyTheme --> CreateWidgets
    }
    
    CreateWidgets --> WindowReady
    
    state WindowReady {
        [*] --> EventListening
        EventListening --> UserInteraction
        UserInteraction --> ProcessInput
        ProcessInput --> EmitEvents
        EmitEvents --> UpdateDisplay
        UpdateDisplay --> EventListening
    }
    
    WindowReady --> WindowClosing : User closes
    WindowReady --> WindowError : Error occurs
    
    state WindowClosing {
        [*] --> CleanupEvents
        CleanupEvents --> SaveWindowState
        SaveWindowState --> DestroyWindow
    }
    
    state WindowError {
        [*] --> LogError
        LogError --> AttemptRecovery
        AttemptRecovery --> WindowReady : Recovery success
        AttemptRecovery --> WindowClosing : Recovery failed
    }
    
    WindowClosing --> [*]
    WindowError --> [*] : Critical error
```

## Event Bus Architecture
```mermaid
graph TB
    subgraph "Event Producers"
        A[GUI Components] --> D[Event Bus]
        B[Plugin System] --> D
        C[Voice System] --> D
        AA[User Actions] --> D
        BB[System Events] --> D
    end
    
    subgraph "Event Bus Core"
        D --> E[Event Queue]
        E --> F[Event Dispatcher]
        F --> G[Async Handler Execution]
        G --> H{Handler Success?}
        H -->|Yes| I[Event Success]
        H -->|No| J[Error Isolation]
    end
    
    subgraph "Event Consumers"
        I --> K[Plugin Handlers]
        I --> L[GUI Updates]
        I --> M[Voice Synthesis]
        I --> N[Configuration Updates]
        I --> O[Performance Metrics]
    end
    
    subgraph "Event Types"
        P[user_action] --> D
        Q[voice_synthesis_request] --> D
        R[config_updated] --> D
        S[plugin_response] --> D
        T[performance_metric] --> D
        U[error_occurred] --> D
    end
    
    %% Error handling
    J --> V[Log Error]
    V --> W[Emit Error Event]
    W --> X[Continue Processing]
    X --> F
    
    %% Performance monitoring
    G --> Y[Track Dispatch Time]
    Y --> Z{<10ms Target?}
    Z -->|Yes| AA1[Performance Success]
    Z -->|No| BB1[Performance Warning]
    
    %% Styling
    classDef producers fill:#E74C3C,stroke:#C0392B,stroke-width:2px,color:#fff
    classDef core fill:#3498DB,stroke:#2980B9,stroke-width:2px,color:#fff
    classDef consumers fill:#27AE60,stroke:#1E8B3A,stroke-width:2px,color:#fff
    classDef events fill:#F39C12,stroke:#E67E22,stroke-width:2px,color:#fff
    
    class A,B,C,AA,BB producers
    class D,E,F,G,H,I,J core
    class K,L,M,N,O consumers
    class P,Q,R,S,T,U events
```

## Configuration Management Flow
```mermaid
flowchart LR
    subgraph "Configuration Sources"
        A[config/default.yaml] --> E[Config Manager]
        B[config/voice_settings.json] --> E
        C[config/ui_settings.json] --> E
        D[config/audio.yaml] --> E
        F[Environment Variables] --> E
        G[Command Line Args] --> E
    end
    
    subgraph "Configuration Processing"
        E --> H[Parse & Validate]
        H --> I[Merge Configurations]
        I --> J[Apply Defaults]
        J --> K[Type Conversion]
        K --> L[Configuration Ready]
    end
    
    subgraph "Configuration Distribution"
        L --> M[App Manager]
        L --> N[Voice System]
        L --> O[GUI Components]
        L --> P[Plugin Manager]
        L --> Q[Event Bus]
    end
    
    subgraph "Runtime Updates"
        R[Settings Window] --> S[User Changes]
        S --> T[Validate Changes]
        T --> U[Update JSON Files]
        U --> V[Emit Config Event]
        V --> W[Live Reload Components]
    end
    
    %% Connections
    W --> N
    W --> O
    
    %% Styling
    classDef sources fill:#8E44AD,stroke:#7D3C98,stroke-width:2px,color:#fff
    classDef processing fill:#2980B9,stroke:#1F618D,stroke-width:2px,color:#fff  
    classDef distribution fill:#27AE60,stroke:#1E8B3A,stroke-width:2px,color:#fff
    classDef runtime fill:#E67E22,stroke:#D35400,stroke-width:2px,color:#fff
    
    class A,B,C,D,F,G sources
    class E,H,I,J,K,L processing
    class M,N,O,P,Q distribution
    class R,S,T,U,V,W runtime
```

## Authentication & Security Flow
```mermaid
sequenceDiagram
    participant User
    participant LoginUI as Login Window
    participant Auth as Auth System
    participant Session as Session Manager
    participant Crypto as Cryptography
    participant Storage as Secure Storage

    User->>LoginUI: Enter credentials
    LoginUI->>Auth: authenticate(username, password)
    
    Auth->>Crypto: hash_password(password)
    Crypto-->>Auth: password_hash
    
    Auth->>Storage: verify_user(username, hash)
    Storage-->>Auth: user_verified
    
    alt Authentication Success
        Auth->>Session: create_session(user_id)
        Session->>Crypto: generate_session_token()
        Crypto-->>Session: secure_token
        Session-->>Auth: session_created
        Auth-->>LoginUI: authentication_success
        LoginUI-->>User: Access Granted
    else Authentication Failed
        Auth-->>LoginUI: authentication_failed
        LoginUI-->>User: Invalid Credentials
    end
    
    Note over User,Storage: Session lifecycle
    
    User->>Session: User activity
    Session->>Session: update_last_activity()
    
    alt Session Expired
        Session->>Auth: session_expired_event
        Auth->>LoginUI: show_login_prompt
    end
```

## Error Handling & Recovery Flow
```mermaid
graph TD
    A[Error Detected] --> B{Error Severity}
    
    B -->|INFO| C[Log Information]
    B -->|WARNING| D[Log Warning]
    B -->|ERROR| E[Attempt Recovery]
    B -->|CRITICAL| F[Emergency Shutdown]
    
    C --> G[Continue Normal Operation]
    D --> H[User Notification]
    
    E --> I{Recovery Type}
    I -->|Voice System| J[Switch to SAPI Fallback]
    I -->|Plugin Error| K[Isolate Plugin]
    I -->|GUI Error| L[Refresh Component]
    I -->|Network Error| M[Retry with Backoff]
    
    J --> N[Recovery Success Check]
    K --> N
    L --> N
    M --> N
    
    N --> O{Recovery Successful?}
    O -->|Yes| P[Emit Recovery Event]
    O -->|No| Q[Escalate to Critical]
    
    P --> R[Update Performance Metrics]
    Q --> F
    
    F --> S[Save Application State]
    S --> T[Cleanup Resources]
    T --> U[Graceful Exit]
    
    H --> V[Continue with Notification]
    R --> V
    V --> G
    
    %% Styling
    classDef info fill:#3498DB,stroke:#2980B9,stroke-width:2px,color:#fff
    classDef warning fill:#F39C12,stroke:#E67E22,stroke-width:2px,color:#fff
    classDef error fill:#E74C3C,stroke:#C0392B,stroke-width:2px,color:#fff
    classDef critical fill:#8B0000,stroke:#660000,stroke-width:3px,color:#fff
    classDef recovery fill:#27AE60,stroke:#1E8B3A,stroke-width:2px,color:#fff
    
    class C,G info
    class D,H,V warning
    class E,I,J,K,L,M,N,O,Q error
    class F,S,T,U critical
    class P,R recovery
```

---

*These Mermaid diagrams provide visual representations of the VPA system architecture, data flows, and component interactions based on the actual codebase analysis.*
