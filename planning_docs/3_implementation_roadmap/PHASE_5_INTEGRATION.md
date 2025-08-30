# Phase 5: Integration Implementation Plan

## Overview

Phase 5 focuses on integrating all previously developed components into a cohesive system. This phase brings together the core architecture, audio system, GUI framework, and plugin system to create a fully functional Virtual Personal Assistant. The integration process ensures that all components work harmoniously together, with well-defined interfaces and robust error handling.

## Timeline

- **Start Date:** December 1, 2025
- **End Date:** December 31, 2025
- **Duration:** 4 weeks
- **Dependencies:**
  - Phase 1 (Core Architecture) must be completed
  - Phase 2 (Audio System) must be completed
  - Phase 3 (GUI Framework) must be completed
  - Phase 4 (Plugin System) must be completed

## Goals and Objectives

1. Integrate all core components to work as a unified system
2. Ensure seamless communication between components through the event system
3. Implement robust error handling and recovery mechanisms
4. Create a comprehensive system startup and shutdown sequence
5. Develop comprehensive integration tests to verify system functionality
6. Optimize performance and resource usage across the integrated system

## Integration Architecture

The integration architecture builds upon the event-driven design established in Phase 1, with clear communication channels between components:

```
┌─────────────────────────────────────────────────────────────────┐
│                            VPA Core                             │
├─────────────┬─────────────┬──────────────────┬─────────────────┤
│ Application │  Settings   │   Event Bus      │ Command Processor│
│  Manager    │  Manager    │                  │                  │
└─────┬───────┴──────┬──────┴─────────┬────────┴────────┬────────┘
      │              │                │                 │
┌─────▼──────┐ ┌─────▼──────┐ ┌───────▼───────┐ ┌──────▼────────┐
│ Audio      │ │ GUI        │ │ Plugin        │ │ LLM           │
│ System     │ │ Framework  │ │ System        │ │ Integration   │
└─────┬──────┘ └─────┬──────┘ └───────┬───────┘ └──────┬────────┘
      │              │                │                 │
┌─────▼──────┐ ┌─────▼──────┐ ┌───────▼───────┐ ┌──────▼────────┐
│ Voice      │ │ UI         │ │ Plugins       │ │ Model         │
│ Processing │ │ Components │ │ (External)    │ │ Adapters      │
└────────────┘ └────────────┘ └───────────────┘ └───────────────┘
```

## Core Integration Components

### 1. Application Manager

The Application Manager orchestrates the startup and shutdown sequence, manages component lifecycle, and provides central error handling.

```python
# src/vpa/core/application_manager.py
from typing import Dict, Any, List, Optional
import asyncio
import logging
import signal
import sys
import traceback
import os
from vpa.core.events import event_bus
from vpa.core.settings_manager import SettingsManager
from vpa.core.command_processor import CommandProcessor
from vpa.audio.audio_manager import AudioManager
from vpa.gui.gui_manager import GuiManager
from vpa.core.plugin_manager import PluginManager
from vpa.llm.llm_manager import LLMManager
from vpa.core.error_handler import ErrorHandler

logger = logging.getLogger(__name__)

class ApplicationManager:
    """Manages the VPA application lifecycle."""
    
    def __init__(self):
        """Initialize application manager."""
        self._settings = None
        self._command_processor = None
        self._audio_manager = None
        self._gui_manager = None
        self._plugin_manager = None
        self._llm_manager = None
        self._error_handler = None
        self._initialized = False
        self._shutting_down = False
        
    async def initialize(self, config_path: str) -> bool:
        """Initialize the application.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            True if initialization succeeded
        """
        if self._initialized:
            return True
            
        logger.info("Initializing application")
        
        try:
            # Set up error handler first
            self._error_handler = ErrorHandler()
            await self._error_handler.initialize()
            
            # Initialize settings
            self._settings = SettingsManager(config_path)
            success = await self._settings.load()
            if not success:
                logger.error("Failed to load settings")
                return False
                
            # Initialize components
            self._command_processor = CommandProcessor()
            self._audio_manager = AudioManager()
            self._gui_manager = GuiManager()
            self._plugin_manager = PluginManager()
            self._llm_manager = LLMManager()
            
            # Initialize components with settings
            components = [
                ("Command Processor", self._command_processor),
                ("Audio Manager", self._audio_manager),
                ("GUI Manager", self._gui_manager),
                ("Plugin Manager", self._plugin_manager),
                ("LLM Manager", self._llm_manager)
            ]
            
            for name, component in components:
                try:
                    logger.info(f"Initializing {name}")
                    
                    # Get component-specific settings
                    component_key = name.lower().replace(" ", "_")
                    component_config = self._settings.get(component_key, {})
                    
                    # Initialize component
                    success = await component.initialize(component_config)
                    
                    if not success:
                        logger.error(f"Failed to initialize {name}")
                        return False
                except Exception as e:
                    logger.error(f"Error initializing {name}: {e}")
                    logger.error(traceback.format_exc())
                    return False
                    
            # Set up signal handlers
            self._setup_signal_handlers()
            
            # Subscribe to events
            event_bus.subscribe("error", self._handle_error)
            event_bus.subscribe("shutdown_requested", self._handle_shutdown_request)
            
            self._initialized = True
            logger.info("Application initialized successfully")
            
            # Emit application initialized event
            event_bus.emit("application_initialized", {
                "version": self._settings.get("application.version", "1.0.0")
            })
            
            return True
        except Exception as e:
            logger.error(f"Error initializing application: {e}")
            logger.error(traceback.format_exc())
            return False
            
    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers."""
        # Handle SIGINT (Ctrl+C) and SIGTERM
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self._signal_handler)
            
    def _signal_handler(self, sig, frame) -> None:
        """Handle signals.
        
        Args:
            sig: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received signal {sig}, shutting down")
        
        # Schedule shutdown in event loop
        asyncio.create_task(self.shutdown())
        
    async def _handle_error(self, data: Dict[str, Any]) -> None:
        """Handle error event.
        
        Args:
            data: Error data
        """
        error_type = data.get("type", "unknown")
        error_message = data.get("message", "Unknown error")
        error_component = data.get("component", "unknown")
        error_level = data.get("level", "error")
        
        # Log error
        if error_level == "warning":
            logger.warning(f"Warning in {error_component}: {error_message}")
        elif error_level == "critical":
            logger.critical(f"Critical error in {error_component}: {error_message}")
        else:
            logger.error(f"Error in {error_component}: {error_message}")
            
        # Handle critical errors
        if error_level == "critical":
            if not self._shutting_down:
                logger.critical("Critical error, shutting down")
                await self.shutdown()
                
    async def _handle_shutdown_request(self, data: Dict[str, Any]) -> None:
        """Handle shutdown request event.
        
        Args:
            data: Shutdown request data
        """
        reason = data.get("reason", "user_request")
        logger.info(f"Shutdown requested: {reason}")
        
        await self.shutdown()
        
    async def run(self) -> int:
        """Run the application.
        
        Returns:
            Exit code
        """
        if not self._initialized:
            logger.error("Application not initialized")
            return 1
            
        logger.info("Starting application")
        
        try:
            # Start components
            components = [
                ("Audio Manager", self._audio_manager),
                ("GUI Manager", self._gui_manager),
                ("Plugin Manager", self._plugin_manager),
                ("LLM Manager", self._llm_manager),
                ("Command Processor", self._command_processor)
            ]
            
            for name, component in components:
                try:
                    logger.info(f"Starting {name}")
                    success = await component.start()
                    
                    if not success:
                        logger.error(f"Failed to start {name}")
                        return 1
                except Exception as e:
                    logger.error(f"Error starting {name}: {e}")
                    logger.error(traceback.format_exc())
                    return 1
                    
            # Emit application started event
            event_bus.emit("application_started", {})
            
            # Keep running until shutdown is requested
            shutdown_complete = asyncio.Future()
            
            def on_shutdown_complete(data):
                shutdown_complete.set_result(True)
                
            event_bus.subscribe("shutdown_complete", on_shutdown_complete)
            
            # Wait for shutdown
            await shutdown_complete
            
            return 0
        except Exception as e:
            logger.error(f"Error running application: {e}")
            logger.error(traceback.format_exc())
            return 1
            
    async def shutdown(self) -> None:
        """Shut down the application."""
        if self._shutting_down:
            return
            
        self._shutting_down = True
        logger.info("Shutting down application")
        
        # Emit shutdown event
        event_bus.emit("shutdown_started", {})
        
        # Shutdown components in reverse order
        components = [
            ("Command Processor", self._command_processor),
            ("LLM Manager", self._llm_manager),
            ("Plugin Manager", self._plugin_manager),
            ("GUI Manager", self._gui_manager),
            ("Audio Manager", self._audio_manager)
        ]
        
        for name, component in components:
            if component:
                try:
                    logger.info(f"Shutting down {name}")
                    await component.shutdown()
                except Exception as e:
                    logger.error(f"Error shutting down {name}: {e}")
                    
        # Save settings
        if self._settings:
            await self._settings.save()
            
        # Unsubscribe from events
        event_bus.unsubscribe("error", self._handle_error)
        event_bus.unsubscribe("shutdown_requested", self._handle_shutdown_request)
        
        # Reset state
        self._initialized = False
        self._shutting_down = False
        
        # Emit shutdown complete event
        event_bus.emit("shutdown_complete", {})
        
        logger.info("Application shutdown complete")
```

### 2. Command Processor

The Command Processor integrates user input from multiple sources (voice, GUI) and routes commands to appropriate handlers.

```python
# src/vpa/core/command_processor.py
from typing import Dict, Any, Optional, List
import asyncio
import logging
from vpa.core.events import event_bus
from vpa.core.utils.text_processing import extract_intent, clean_text

logger = logging.getLogger(__name__)

class CommandProcessor:
    """Processes user commands and routes them to appropriate handlers."""
    
    def __init__(self):
        """Initialize command processor."""
        self._initialized = False
        self._running = False
        self._llm_manager = None
        self._plugin_manager = None
        self._command_history = []
        self._max_history = 100
        
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the command processor.
        
        Args:
            config: Command processor configuration
            
        Returns:
            True if initialization succeeded
        """
        if self._initialized:
            return True
            
        logger.info("Initializing command processor")
        
        # Store configuration
        self._max_history = config.get("max_history", 100)
        
        # Subscribe to events
        event_bus.subscribe("voice_command", self._handle_voice_command, async_callback=True)
        event_bus.subscribe("text_command", self._handle_text_command, async_callback=True)
        event_bus.subscribe("application_initialized", self._handle_app_initialized, async_callback=True)
        
        self._initialized = True
        logger.info("Command processor initialized")
        
        return True
        
    async def _handle_app_initialized(self, data: Dict[str, Any]) -> None:
        """Handle application initialized event.
        
        Args:
            data: Event data
        """
        # Circular imports are avoided by getting references here
        # These are imported here to avoid circular imports
        from vpa.llm.llm_manager import get_llm_manager
        from vpa.core.plugin_manager import get_plugin_manager
        
        self._llm_manager = get_llm_manager()
        self._plugin_manager = get_plugin_manager()
        
    async def start(self) -> bool:
        """Start the command processor.
        
        Returns:
            True if started successfully
        """
        if not self._initialized:
            logger.error("Command processor not initialized")
            return False
            
        if self._running:
            return True
            
        self._running = True
        logger.info("Command processor started")
        
        return True
        
    async def shutdown(self) -> bool:
        """Shut down the command processor.
        
        Returns:
            True if shutdown succeeded
        """
        if not self._initialized:
            return True
            
        logger.info("Shutting down command processor")
        
        # Unsubscribe from events
        event_bus.unsubscribe("voice_command", self._handle_voice_command)
        event_bus.unsubscribe("text_command", self._handle_text_command)
        event_bus.unsubscribe("application_initialized", self._handle_app_initialized)
        
        self._running = False
        self._initialized = False
        
        logger.info("Command processor shutdown complete")
        return True
        
    async def _handle_voice_command(self, data: Dict[str, Any]) -> None:
        """Handle voice command event.
        
        Args:
            data: Voice command data
        """
        text = data.get("text")
        confidence = data.get("confidence", 1.0)
        
        if not text:
            return
            
        logger.debug(f"Processing voice command: {text} (confidence: {confidence})")
        
        # Create command context
        context = {
            "source": "voice",
            "confidence": confidence,
            "raw_text": text
        }
        
        # Process command
        await self._process_command(text, context)
        
    async def _handle_text_command(self, data: Dict[str, Any]) -> None:
        """Handle text command event.
        
        Args:
            data: Text command data
        """
        text = data.get("text")
        
        if not text:
            return
            
        logger.debug(f"Processing text command: {text}")
        
        # Create command context
        context = {
            "source": "text",
            "raw_text": text
        }
        
        # Process command
        await self._process_command(text, context)
        
    async def _process_command(
        self,
        text: str,
        context: Dict[str, Any]
    ) -> None:
        """Process a command.
        
        Args:
            text: Command text
            context: Command context
        """
        # Clean text
        cleaned_text = clean_text(text)
        
        # Add to command history
        self._add_to_history(cleaned_text, context)
        
        # Extract intent (basic)
        intent = extract_intent(cleaned_text)
        context["intent"] = intent
        
        # First try plugins
        if self._plugin_manager:
            response = await self._plugin_manager.process_input(cleaned_text, context)
            
            if response:
                # Plugin handled the command
                logger.debug(f"Command handled by plugin: {response.get('plugin', {}).get('id')}")
                
                # Emit response event
                self._emit_response_event(response, context)
                return
                
        # If no plugin handled it, use LLM
        if self._llm_manager:
            response = await self._llm_manager.process_input(cleaned_text, context)
            
            if response:
                # LLM handled the command
                logger.debug("Command handled by LLM")
                
                # Emit response event
                self._emit_response_event(response, context)
                return
                
        # If we got here, no handler was found
        logger.warning(f"No handler found for command: {cleaned_text}")
        
        # Emit fallback response
        self._emit_response_event(
            {
                "text": "I'm sorry, I don't know how to help with that."
            },
            context
        )
        
    def _emit_response_event(
        self,
        response: Dict[str, Any],
        context: Dict[str, Any]
    ) -> None:
        """Emit response event.
        
        Args:
            response: Response data
            context: Command context
        """
        # Add context to response
        response_data = {
            **response,
            "context": context
        }
        
        # Emit response event
        event_bus.emit("assistant_response", response_data)
        
        # If response contains text and source was voice, speak it
        if "text" in response and context.get("source") == "voice":
            event_bus.emit("speak_text", {"text": response["text"]})
            
    def _add_to_history(
        self,
        text: str,
        context: Dict[str, Any]
    ) -> None:
        """Add command to history.
        
        Args:
            text: Command text
            context: Command context
        """
        self._command_history.append({
            "text": text,
            "context": context,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Trim history if needed
        if len(self._command_history) > self._max_history:
            self._command_history = self._command_history[-self._max_history:]
```

### 3. Component Integration Service

The Component Integration Service provides a centralized hub for components to discover and interact with each other.

```python
# src/vpa/core/integration_service.py
from typing import Dict, Any, Optional, List, Type, TypeVar, Generic, cast
import logging
from vpa.core.events import event_bus

logger = logging.getLogger(__name__)

T = TypeVar('T')

class ComponentRegistration:
    """Registration information for a component."""
    
    def __init__(self, component_id: str, component: Any, interfaces: List[Type]):
        """Initialize component registration.
        
        Args:
            component_id: Component ID
            component: Component instance
            interfaces: Interfaces implemented by component
        """
        self.component_id = component_id
        self.component = component
        self.interfaces = interfaces

class IntegrationService:
    """Service for component integration and discovery."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'IntegrationService':
        """Get singleton instance.
        
        Returns:
            IntegrationService instance
        """
        if cls._instance is None:
            cls._instance = IntegrationService()
            
        return cls._instance
        
    def __init__(self):
        """Initialize integration service."""
        if IntegrationService._instance is not None:
            raise RuntimeError("Use get_instance() to get IntegrationService instance")
            
        self._components: Dict[str, ComponentRegistration] = {}
        self._interface_map: Dict[Type, List[str]] = {}
        
    def register_component(
        self,
        component_id: str,
        component: Any,
        interfaces: List[Type]
    ) -> None:
        """Register a component.
        
        Args:
            component_id: Component ID
            component: Component instance
            interfaces: Interfaces implemented by component
        """
        # Check if component is already registered
        if component_id in self._components:
            logger.warning(f"Component {component_id} is already registered")
            return
            
        # Register component
        self._components[component_id] = ComponentRegistration(
            component_id,
            component,
            interfaces
        )
        
        # Update interface map
        for interface in interfaces:
            if interface not in self._interface_map:
                self._interface_map[interface] = []
                
            self._interface_map[interface].append(component_id)
            
        logger.debug(f"Registered component: {component_id}")
        
        # Emit component registered event
        event_bus.emit("component_registered", {
            "component_id": component_id,
            "interfaces": [i.__name__ for i in interfaces]
        })
        
    def unregister_component(self, component_id: str) -> bool:
        """Unregister a component.
        
        Args:
            component_id: Component ID
            
        Returns:
            True if component was unregistered
        """
        if component_id not in self._components:
            logger.warning(f"Component {component_id} is not registered")
            return False
            
        # Get component registration
        registration = self._components[component_id]
        
        # Remove from interface map
        for interface in registration.interfaces:
            if interface in self._interface_map:
                if component_id in self._interface_map[interface]:
                    self._interface_map[interface].remove(component_id)
                    
                if not self._interface_map[interface]:
                    del self._interface_map[interface]
                    
        # Remove from components
        del self._components[component_id]
        
        logger.debug(f"Unregistered component: {component_id}")
        
        # Emit component unregistered event
        event_bus.emit("component_unregistered", {
            "component_id": component_id
        })
        
        return True
        
    def get_component(self, component_id: str) -> Optional[Any]:
        """Get a component by ID.
        
        Args:
            component_id: Component ID
            
        Returns:
            Component instance or None if not found
        """
        if component_id not in self._components:
            return None
            
        return self._components[component_id].component
        
    def get_component_by_interface(self, interface: Type[T]) -> Optional[T]:
        """Get a component by interface.
        
        Args:
            interface: Interface type
            
        Returns:
            Component instance or None if not found
        """
        if interface not in self._interface_map:
            return None
            
        component_ids = self._interface_map[interface]
        if not component_ids:
            return None
            
        # Return first component implementing interface
        component_id = component_ids[0]
        return cast(T, self._components[component_id].component)
        
    def get_all_components_by_interface(self, interface: Type[T]) -> List[T]:
        """Get all components implementing an interface.
        
        Args:
            interface: Interface type
            
        Returns:
            List of component instances
        """
        if interface not in self._interface_map:
            return []
            
        component_ids = self._interface_map[interface]
        return [cast(T, self._components[component_id].component) for component_id in component_ids]
        
    def get_component_ids(self) -> List[str]:
        """Get list of registered component IDs.
        
        Returns:
            List of component IDs
        """
        return list(self._components.keys())
        
    def get_interfaces(self) -> List[Type]:
        """Get list of registered interfaces.
        
        Returns:
            List of interface types
        """
        return list(self._interface_map.keys())
```

### 4. System Event Management

The System Event Management module enhances the event system to handle system-wide events and provide robust error handling.

```python
# src/vpa/core/system_events.py
from typing import Dict, Any, Optional, List, Set
import logging
import asyncio
from vpa.core.events import event_bus

logger = logging.getLogger(__name__)

# Define system events
SYSTEM_EVENTS = {
    # Application lifecycle events
    "application_initialized",
    "application_started",
    "shutdown_requested",
    "shutdown_started",
    "shutdown_complete",
    
    # Component lifecycle events
    "component_registered",
    "component_unregistered",
    
    # Error events
    "error",
    
    # User interaction events
    "voice_command",
    "text_command",
    "assistant_response",
    
    # Audio events
    "speech_started",
    "speech_finished",
    "wake_word_detected",
    
    # GUI events
    "gui_ready",
    "view_changed",
    
    # Plugin events
    "plugin_install",
    "plugin_installed",
    "plugin_uninstall",
    "plugin_uninstalled",
    "plugin_enable",
    "plugin_enabled",
    "plugin_disable",
    "plugin_disabled",
}

class SystemEventLogger:
    """Logs system events."""
    
    def __init__(self, log_level: int = logging.DEBUG):
        """Initialize system event logger.
        
        Args:
            log_level: Logging level for events
        """
        self._log_level = log_level
        self._logger = logging.getLogger(__name__ + ".events")
        self._subscribed_events = set()
        
    def start(self, events: Optional[Set[str]] = None) -> None:
        """Start logging events.
        
        Args:
            events: Events to log (None for all system events)
        """
        # Determine events to log
        if events is None:
            events_to_log = SYSTEM_EVENTS
        else:
            events_to_log = events.intersection(SYSTEM_EVENTS)
            
        # Subscribe to events
        for event_type in events_to_log:
            if event_type not in self._subscribed_events:
                event_bus.subscribe(event_type, self._log_event)
                self._subscribed_events.add(event_type)
                
        logger.debug(f"Started logging {len(self._subscribed_events)} system events")
        
    def stop(self) -> None:
        """Stop logging events."""
        # Unsubscribe from events
        for event_type in list(self._subscribed_events):
            event_bus.unsubscribe(event_type, self._log_event)
            
        self._subscribed_events.clear()
        logger.debug("Stopped logging system events")
        
    def _log_event(self, data: Dict[str, Any]) -> None:
        """Log an event.
        
        Args:
            data: Event data
        """
        event_type = event_bus.current_event_type
        if not event_type:
            return
            
        # Don't log data for certain events to avoid sensitive information
        if event_type in {"voice_command", "text_command"}:
            self._logger.log(self._log_level, f"Event: {event_type} [data redacted]")
        else:
            self._logger.log(self._log_level, f"Event: {event_type} {data}")
```

### 5. Error Handler

The Error Handler provides centralized error management and recovery mechanisms.

```python
# src/vpa/core/error_handler.py
from typing import Dict, Any, Optional, List, Callable, Type
import logging
import traceback
import sys
import os
from datetime import datetime
from vpa.core.events import event_bus

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Handles errors across the application."""
    
    def __init__(self):
        """Initialize error handler."""
        self._error_log_path = None
        self._error_handlers: Dict[str, List[Callable]] = {}
        self._error_counts: Dict[str, int] = {}
        self._error_thresholds: Dict[str, int] = {}
        
    async def initialize(self) -> bool:
        """Initialize error handler.
        
        Returns:
            True if initialization succeeded
        """
        logger.info("Initializing error handler")
        
        # Set up error log
        try:
            log_dir = os.path.join(os.path.expanduser("~"), ".vpa", "logs")
            os.makedirs(log_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._error_log_path = os.path.join(log_dir, f"errors_{timestamp}.log")
            
            # Set up global exception handler
            sys.excepthook = self._global_exception_handler
            
            # Subscribe to error events
            event_bus.subscribe("error", self._handle_error_event)
            
            # Set default error thresholds
            self._error_thresholds = {
                "audio_error": 5,
                "gui_error": 5,
                "llm_error": 3,
                "plugin_error": 3
            }
            
            logger.info("Error handler initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize error handler: {e}")
            return False
            
    def _global_exception_handler(self, exc_type, exc_value, exc_tb):
        """Handle uncaught exceptions.
        
        Args:
            exc_type: Exception type
            exc_value: Exception value
            exc_tb: Exception traceback
        """
        # Format traceback
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)
        tb_text = "".join(tb_lines)
        
        # Log error
        logger.critical(f"Uncaught exception: {exc_value}\n{tb_text}")
        
        # Write to error log
        self._write_to_error_log("UNCAUGHT_EXCEPTION", str(exc_value), tb_text)
        
        # Emit error event
        event_bus.emit("error", {
            "type": "uncaught_exception",
            "message": str(exc_value),
            "traceback": tb_text,
            "component": "system",
            "level": "critical"
        })
        
        # Call default exception handler
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        
    def _handle_error_event(self, data: Dict[str, Any]) -> None:
        """Handle error event.
        
        Args:
            data: Error data
        """
        error_type = data.get("type", "unknown")
        error_message = data.get("message", "Unknown error")
        error_component = data.get("component", "unknown")
        error_level = data.get("level", "error")
        error_traceback = data.get("traceback")
        
        # Write to error log
        self._write_to_error_log(error_type, error_message, error_traceback)
        
        # Update error count
        error_key = f"{error_component}_{error_type}"
        self._error_counts[error_key] = self._error_counts.get(error_key, 0) + 1
        
        # Check if threshold exceeded
        component_key = f"{error_component}_error"
        if component_key in self._error_thresholds:
            threshold = self._error_thresholds[component_key]
            if self._error_counts.get(error_key, 0) >= threshold:
                # Emit critical error event
                event_bus.emit("error", {
                    "type": "threshold_exceeded",
                    "message": f"Error threshold exceeded for {error_key}",
                    "component": error_component,
                    "level": "critical",
                    "related_error": {
                        "type": error_type,
                        "message": error_message
                    }
                })
                
        # Call error handlers
        if error_type in self._error_handlers:
            for handler in self._error_handlers[error_type]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Error in error handler: {e}")
                    
    def _write_to_error_log(
        self,
        error_type: str,
        error_message: str,
        traceback_text: Optional[str] = None
    ) -> None:
        """Write error to log file.
        
        Args:
            error_type: Error type
            error_message: Error message
            traceback_text: Traceback text
        """
        if not self._error_log_path:
            return
            
        try:
            timestamp = datetime.now().isoformat()
            
            with open(self._error_log_path, "a") as f:
                f.write(f"[{timestamp}] {error_type}: {error_message}\n")
                
                if traceback_text:
                    f.write(f"{traceback_text}\n")
                    
                f.write("-" * 80 + "\n")
        except Exception as e:
            logger.error(f"Failed to write to error log: {e}")
            
    def register_error_handler(
        self,
        error_type: str,
        handler: Callable[[Dict[str, Any]], None]
    ) -> None:
        """Register an error handler.
        
        Args:
            error_type: Error type to handle
            handler: Handler function
        """
        if error_type not in self._error_handlers:
            self._error_handlers[error_type] = []
            
        self._error_handlers[error_type].append(handler)
        
    def unregister_error_handler(
        self,
        error_type: str,
        handler: Callable[[Dict[str, Any]], None]
    ) -> bool:
        """Unregister an error handler.
        
        Args:
            error_type: Error type
            handler: Handler function
            
        Returns:
            True if handler was unregistered
        """
        if error_type not in self._error_handlers:
            return False
            
        if handler in self._error_handlers[error_type]:
            self._error_handlers[error_type].remove(handler)
            return True
            
        return False
        
    def set_error_threshold(self, error_key: str, threshold: int) -> None:
        """Set error threshold.
        
        Args:
            error_key: Error key
            threshold: Threshold value
        """
        self._error_thresholds[error_key] = threshold
```

## Implementation Tasks

### Week 1: Core Integration (December 1-7, 2025)

#### Task 1.1: Application Manager
- **Description**: Implement the ApplicationManager class
- **Deliverable**: `src/vpa/core/application_manager.py` with ApplicationManager class
- **Estimated Time**: 3 days
- **Dependencies**: Core components from Phase 1

#### Task 1.2: Component Integration Service
- **Description**: Implement the IntegrationService class
- **Deliverable**: `src/vpa/core/integration_service.py` with IntegrationService class
- **Estimated Time**: 2 days
- **Dependencies**: None

#### Task 1.3: System Event Management
- **Description**: Implement the SystemEventLogger class
- **Deliverable**: `src/vpa/core/system_events.py` with SystemEventLogger class
- **Estimated Time**: 1 day
- **Dependencies**: Event bus from Phase 1

#### Task 1.4: Error Handler
- **Description**: Implement the ErrorHandler class
- **Deliverable**: `src/vpa/core/error_handler.py` with ErrorHandler class
- **Estimated Time**: 2 days
- **Dependencies**: Event bus from Phase 1

### Week 2: Component Integration (December 8-14, 2025)

#### Task 2.1: Audio System Integration
- **Description**: Integrate the audio system with the core architecture
- **Deliverable**: Updates to AudioManager to work with IntegrationService
- **Estimated Time**: 2 days
- **Dependencies**: Audio System from Phase 2, IntegrationService

#### Task 2.2: GUI Integration
- **Description**: Integrate the GUI framework with the core architecture
- **Deliverable**: Updates to GuiManager to work with IntegrationService
- **Estimated Time**: 2 days
- **Dependencies**: GUI Framework from Phase 3, IntegrationService

#### Task 2.3: Plugin System Integration
- **Description**: Integrate the plugin system with the core architecture
- **Deliverable**: Updates to PluginManager to work with IntegrationService
- **Estimated Time**: 2 days
- **Dependencies**: Plugin System from Phase 4, IntegrationService

#### Task 2.4: LLM Integration
- **Description**: Integrate the LLM system with the core architecture
- **Deliverable**: Updates to LLMManager to work with IntegrationService
- **Estimated Time**: 2 days
- **Dependencies**: LLM components, IntegrationService

### Week 3: Command and Event Integration (December 15-21, 2025)

#### Task 3.1: Command Processor
- **Description**: Implement the CommandProcessor class
- **Deliverable**: `src/vpa/core/command_processor.py` with CommandProcessor class
- **Estimated Time**: 3 days
- **Dependencies**: Core components, LLM integration, Plugin integration

#### Task 3.2: Event Routing
- **Description**: Implement event routing between components
- **Deliverable**: Updates to event handling in all components
- **Estimated Time**: 2 days
- **Dependencies**: All components, event bus

#### Task 3.3: System Startup Sequence
- **Description**: Implement the system startup sequence
- **Deliverable**: Startup sequence in ApplicationManager
- **Estimated Time**: 1 day
- **Dependencies**: ApplicationManager, all components

#### Task 3.4: System Shutdown Sequence
- **Description**: Implement the system shutdown sequence
- **Deliverable**: Shutdown sequence in ApplicationManager
- **Estimated Time**: 1 day
- **Dependencies**: ApplicationManager, all components

### Week 4: Testing and Optimization (December 22-31, 2025)

#### Task 4.1: Integration Testing
- **Description**: Create and run integration tests
- **Deliverable**: Integration test suite
- **Estimated Time**: 3 days
- **Dependencies**: All integrated components

#### Task 4.2: Error Handling and Recovery Testing
- **Description**: Test error handling and recovery mechanisms
- **Deliverable**: Error handling test suite
- **Estimated Time**: 2 days
- **Dependencies**: ErrorHandler, all components

#### Task 4.3: Performance Optimization
- **Description**: Optimize performance of integrated system
- **Deliverable**: Performance optimizations in critical components
- **Estimated Time**: 3 days
- **Dependencies**: All integrated components

#### Task 4.4: Final Integration Validation
- **Description**: Validate the complete integrated system
- **Deliverable**: Validation report
- **Estimated Time**: 2 days
- **Dependencies**: All tasks completed

## Integration Test Plan

### Test Categories

1. **Component Integration Tests**
   - Test interaction between components through IntegrationService
   - Verify component registration and discovery
   - Test interface-based component access

2. **Event Flow Tests**
   - Test event propagation between components
   - Verify event handlers are called correctly
   - Test event-based communication patterns

3. **Lifecycle Tests**
   - Test system startup sequence
   - Test system shutdown sequence
   - Test component initialization and shutdown

4. **Error Handling Tests**
   - Test error detection and reporting
   - Test error recovery mechanisms
   - Test error thresholds and escalation

5. **End-to-End Tests**
   - Test complete user interaction flows
   - Test voice input to response output
   - Test text input to response output

### Test Implementation

```python
# tests/integration/test_system_integration.py
import pytest
import asyncio
from vpa.core.application_manager import ApplicationManager
from vpa.core.events import event_bus
from vpa.core.integration_service import IntegrationService

class TestSystemIntegration:
    """System integration tests."""
    
    @pytest.fixture
    async def app_manager(self):
        """Create application manager."""
        app = ApplicationManager()
        yield app
        await app.shutdown()
        
    @pytest.mark.asyncio
    async def test_system_startup(self, app_manager):
        """Test system startup."""
        # Initialize app
        success = await app_manager.initialize("tests/fixtures/test_config.json")
        assert success, "Application initialization failed"
        
        # Create future to wait for startup complete
        startup_complete = asyncio.Future()
        
        def on_started(data):
            startup_complete.set_result(True)
            
        # Subscribe to application started event
        event_bus.subscribe("application_started", on_started)
        
        # Start application in background task
        task = asyncio.create_task(app_manager.run())
        
        try:
            # Wait for startup with timeout
            await asyncio.wait_for(startup_complete, timeout=5.0)
            
            # Verify components are registered
            integration_service = IntegrationService.get_instance()
            component_ids = integration_service.get_component_ids()
            
            # Check for required components
            required_components = [
                "audio_manager",
                "gui_manager",
                "plugin_manager",
                "llm_manager",
                "command_processor"
            ]
            
            for component in required_components:
                assert component in component_ids, f"Component {component} not registered"
                
            # Trigger shutdown
            event_bus.emit("shutdown_requested", {"reason": "test_complete"})
            
            # Wait for task to complete
            await task
        finally:
            # Clean up
            event_bus.unsubscribe("application_started", on_started)
            if not task.done():
                task.cancel()
                
    @pytest.mark.asyncio
    async def test_command_processing(self, app_manager):
        """Test command processing."""
        # Initialize and start app
        await app_manager.initialize("tests/fixtures/test_config.json")
        task = asyncio.create_task(app_manager.run())
        
        # Wait for application to start
        startup_complete = asyncio.Future()
        event_bus.subscribe("application_started", lambda data: startup_complete.set_result(True))
        await asyncio.wait_for(startup_complete, timeout=5.0)
        
        try:
            # Create future to wait for response
            response_received = asyncio.Future()
            
            def on_response(data):
                response_received.set_result(data)
                
            # Subscribe to assistant response event
            event_bus.subscribe("assistant_response", on_response)
            
            # Send test command
            event_bus.emit("text_command", {"text": "What time is it?"})
            
            # Wait for response with timeout
            response = await asyncio.wait_for(response_received, timeout=5.0)
            
            # Verify response
            assert "text" in response, "Response missing text field"
            assert response["context"]["source"] == "text", "Context source incorrect"
            
            # Trigger shutdown
            event_bus.emit("shutdown_requested", {"reason": "test_complete"})
            
            # Wait for task to complete
            await task
        finally:
            # Clean up
            event_bus.unsubscribe("application_started", lambda data: startup_complete.set_result(True))
            event_bus.unsubscribe("assistant_response", on_response)
            if not task.done():
                task.cancel()
                
    @pytest.mark.asyncio
    async def test_error_handling(self, app_manager):
        """Test error handling."""
        # Initialize and start app
        await app_manager.initialize("tests/fixtures/test_config.json")
        task = asyncio.create_task(app_manager.run())
        
        # Wait for application to start
        startup_complete = asyncio.Future()
        event_bus.subscribe("application_started", lambda data: startup_complete.set_result(True))
        await asyncio.wait_for(startup_complete, timeout=5.0)
        
        try:
            # Create futures to wait for error events
            error_received = asyncio.Future()
            critical_error_received = asyncio.Future()
            
            def on_error(data):
                if data.get("level") == "critical":
                    critical_error_received.set_result(data)
                else:
                    error_received.set_result(data)
                    
            # Subscribe to error event
            event_bus.subscribe("error", on_error)
            
            # Emit test error
            event_bus.emit("error", {
                "type": "test_error",
                "message": "Test error message",
                "component": "test",
                "level": "error"
            })
            
            # Wait for error with timeout
            error = await asyncio.wait_for(error_received, timeout=5.0)
            
            # Verify error
            assert error["type"] == "test_error", "Error type incorrect"
            assert error["component"] == "test", "Error component incorrect"
            
            # Emit multiple errors to trigger threshold
            for i in range(5):
                event_bus.emit("error", {
                    "type": "test_error",
                    "message": f"Test error message {i}",
                    "component": "audio",
                    "level": "error"
                })
                
            # Wait for critical error with timeout
            critical_error = await asyncio.wait_for(critical_error_received, timeout=5.0)
            
            # Verify critical error
            assert critical_error["type"] == "threshold_exceeded", "Critical error type incorrect"
            assert critical_error["component"] == "audio", "Critical error component incorrect"
            
            # Trigger shutdown
            event_bus.emit("shutdown_requested", {"reason": "test_complete"})
            
            # Wait for task to complete
            await task
        finally:
            # Clean up
            event_bus.unsubscribe("application_started", lambda data: startup_complete.set_result(True))
            event_bus.unsubscribe("error", on_error)
            if not task.done():
                task.cancel()
```

## Performance Optimization

### Performance Hotspots

1. **Event Processing**
   - Optimize event routing and handling
   - Reduce event payload size
   - Use event batching where appropriate

2. **Component Communication**
   - Minimize cross-component calls
   - Use efficient data structures for communication
   - Cache frequently used data

3. **Resource Usage**
   - Monitor memory usage
   - Implement resource pooling
   - Use lazy loading for components

### Optimization Strategies

```python
# src/vpa/core/performance_monitor.py
from typing import Dict, Any, Optional, List
import time
import logging
import asyncio
import psutil
import gc
from vpa.core.events import event_bus

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitors system performance."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self._running = False
        self._monitoring_task = None
        self._monitor_interval = 10.0  # seconds
        self._event_counts: Dict[str, int] = {}
        self._last_check_time = time.time()
        self._process = psutil.Process()
        
    async def start(self) -> None:
        """Start performance monitoring."""
        if self._running:
            return
            
        self._running = True
        self._last_check_time = time.time()
        self._event_counts.clear()
        
        # Subscribe to all events
        event_bus.subscribe("*", self._count_event)
        
        # Start monitoring task
        self._monitoring_task = asyncio.create_task(self._monitor_loop())
        logger.info("Performance monitoring started")
        
    async def stop(self) -> None:
        """Stop performance monitoring."""
        if not self._running:
            return
            
        self._running = False
        
        # Unsubscribe from events
        event_bus.unsubscribe("*", self._count_event)
        
        # Stop monitoring task
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
                
        self._monitoring_task = None
        logger.info("Performance monitoring stopped")
        
    def _count_event(self, data: Dict[str, Any]) -> None:
        """Count event for performance monitoring.
        
        Args:
            data: Event data
        """
        event_type = event_bus.current_event_type
        if not event_type:
            return
            
        self._event_counts[event_type] = self._event_counts.get(event_type, 0) + 1
        
    async def _monitor_loop(self) -> None:
        """Performance monitoring loop."""
        while self._running:
            try:
                # Wait for interval
                await asyncio.sleep(self._monitor_interval)
                
                # Check performance metrics
                await self._check_performance()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in performance monitor: {e}")
                
    async def _check_performance(self) -> None:
        """Check performance metrics."""
        current_time = time.time()
        elapsed = current_time - self._last_check_time
        self._last_check_time = current_time
        
        # Memory usage
        memory_info = self._process.memory_info()
        memory_mb = memory_info.rss / (1024 * 1024)
        
        # CPU usage
        cpu_percent = self._process.cpu_percent()
        
        # Event rates
        event_rates = {}
        for event_type, count in self._event_counts.items():
            event_rates[event_type] = count / elapsed
            
        # Log performance metrics
        logger.debug(f"Memory usage: {memory_mb:.2f} MB, CPU: {cpu_percent:.2f}%")
        
        # Reset event counts
        self._event_counts.clear()
        
        # Check for memory leaks
        if memory_mb > 500:  # Threshold in MB
            logger.warning(f"High memory usage detected: {memory_mb:.2f} MB")
            
            # Force garbage collection
            gc.collect()
            
            # Emit performance warning event
            event_bus.emit("performance_warning", {
                "type": "high_memory",
                "memory_mb": memory_mb,
                "cpu_percent": cpu_percent
            })
            
        # Check for high CPU usage
        if cpu_percent > 80:  # Threshold in percent
            logger.warning(f"High CPU usage detected: {cpu_percent:.2f}%")
            
            # Emit performance warning event
            event_bus.emit("performance_warning", {
                "type": "high_cpu",
                "memory_mb": memory_mb,
                "cpu_percent": cpu_percent
            })
            
        # Check for high event rates
        for event_type, rate in event_rates.items():
            if rate > 100:  # Events per second
                logger.warning(f"High event rate detected for {event_type}: {rate:.2f}/s")
                
                # Emit performance warning event
                event_bus.emit("performance_warning", {
                    "type": "high_event_rate",
                    "event_type": event_type,
                    "rate": rate
                })
```

## Final Integration Strategy

1. **Step-by-Step Integration**
   - Start with core components
   - Add one subsystem at a time
   - Test each integration thoroughly

2. **Staged Deployment**
   - Deploy in development environment first
   - Perform comprehensive testing
   - Move to production when stable

3. **Fallback Mechanisms**
   - Implement feature flags for new integrations
   - Provide fallback paths for critical functionality
   - Allow disabling problematic components

4. **Monitoring and Logging**
   - Implement comprehensive logging
   - Set up performance monitoring
   - Create alerting for critical issues

## Conclusion

Phase 5 brings together all the components developed in previous phases to create a cohesive, integrated system. The focus is on robust integration with clear communication channels, comprehensive error handling, and optimized performance. By following the implementation tasks and strategies outlined in this document, we will create a reliable and maintainable system that provides a seamless user experience.

---

*Document created: August 29, 2025*
