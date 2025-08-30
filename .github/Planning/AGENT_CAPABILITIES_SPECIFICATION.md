# Agent Capabilities Specification

## Overview

This document specifies the capabilities of the AI agent used in the VPA application, detailing the agent's core functionality, integration with the application, and customization options available to users.

## Table of Contents

1. [Agent Architecture](#1-agent-architecture)
2. [Core Capabilities](#2-core-capabilities)
3. [Integration Points](#3-integration-points)
4. [Customization Options](#4-customization-options)
5. [Context Management](#5-context-management)
6. [Performance Considerations](#6-performance-considerations)
7. [Implementation Examples](#7-implementation-examples)

## 1. Agent Architecture

### 1.1 Agent Components

The VPA agent architecture consists of the following components:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Agent Architecture                          │
├─────────────┬─────────────────────────┬───────────────────────┐
│ Input       │ Processing              │ Output                │
│ Processing  │ Components              │ Generation            │
├─────────────┼─────────────────────────┼───────────────────────┤
│ • Text Input│ • Intent Recognition    │ • Response Formatting │
│ • Voice     │ • Context Management    │ • Action Execution    │
│   Input     │ • LLM Integration       │ • UI Updates          │
│ • Command   │ • Knowledge Base Access │ • Voice Synthesis     │
│   Parsing   │ • Tool Execution        │ • Notification        │
│             │ • Conversation History  │   Generation          │
└─────────────┴─────────────────────────┴───────────────────────┘
```

### 1.2 Agent Implementation

The agent is implemented using a modular architecture that connects user inputs to the appropriate language model and tools:

```python
class AgentManager:
    """Manages the VPA agent functionality"""
    
    def __init__(self, event_bus, settings_manager):
        self.event_bus = event_bus
        self.settings_manager = settings_manager
        self.llm_adapter = None
        self.knowledge_base = None
        self.context_manager = None
        self.tool_executor = None
        self.conversation_history = []
        
    async def initialize(self):
        """Initialize agent components"""
        try:
            # Initialize LLM adapter
            self.llm_adapter = await self._create_llm_adapter()
            
            # Initialize knowledge base
            self.knowledge_base = await self._create_knowledge_base()
            
            # Initialize context manager
            self.context_manager = ContextManager()
            
            # Initialize tool executor
            self.tool_executor = ToolExecutor()
            
            # Subscribe to events
            self._subscribe_to_events()
            
            return True
        except Exception as e:
            logger.error(f"Agent initialization failed: {e}")
            return False
            
    async def process_user_input(self, user_input, input_type="text"):
        """Process user input and generate response"""
        try:
            # Add input to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_input,
                "timestamp": time.time()
            })
            
            # Emit event for processing start
            await self.event_bus.emit_async("agent.processing.start", {
                "input": user_input,
                "input_type": input_type
            })
            
            # Get current context
            context = self.context_manager.get_current_context()
            
            # Prepare LLM request
            request = {
                "input": user_input,
                "conversation_history": self._prepare_conversation_history(),
                "context": context,
                "tools": self.tool_executor.get_available_tools()
            }
            
            # Get response from LLM
            response = await self.llm_adapter.get_response(request)
            
            # Process tool calls if any
            if "tool_calls" in response:
                tool_results = await self.tool_executor.execute_tools(response["tool_calls"])
                
                # Update response with tool results
                response = await self.llm_adapter.get_response_with_tool_results(
                    request, 
                    response,
                    tool_results
                )
            
            # Add response to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": response["content"],
                "timestamp": time.time()
            })
            
            # Update context
            self.context_manager.update_context(user_input, response["content"])
            
            # Emit event for processing complete
            await self.event_bus.emit_async("agent.processing.complete", {
                "input": user_input,
                "response": response["content"],
                "has_tools": "tool_calls" in response
            })
            
            return response["content"]
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            
            # Emit error event
            await self.event_bus.emit_async("agent.processing.error", {
                "input": user_input,
                "error": str(e)
            })
            
            return f"I'm sorry, I encountered an error while processing your request: {str(e)}"
            
    def _subscribe_to_events(self):
        """Subscribe to relevant events"""
        self.event_bus.subscribe(
            "user.input.text", 
            self._on_user_text_input,
            async_callback=True
        )
        
        self.event_bus.subscribe(
            "user.input.voice", 
            self._on_user_voice_input,
            async_callback=True
        )
        
    async def _on_user_text_input(self, event_data):
        """Handle user text input event"""
        user_input = event_data.get("text", "")
        if user_input:
            await self.process_user_input(user_input, "text")
            
    async def _on_user_voice_input(self, event_data):
        """Handle user voice input event"""
        user_input = event_data.get("text", "")
        if user_input:
            await self.process_user_input(user_input, "voice")
            
    def _prepare_conversation_history(self):
        """Prepare conversation history for LLM request"""
        # Get conversation length limit from settings
        max_length = self.settings_manager.get("agent.conversation_history_length", 10)
        
        # Get recent conversation history entries
        recent_history = self.conversation_history[-max_length:] if self.conversation_history else []
        
        return recent_history
            
    async def _create_llm_adapter(self):
        """Create LLM adapter based on settings"""
        llm_type = self.settings_manager.get("agent.llm_type", "openai")
        
        if llm_type == "openai":
            from adapters.llm.openai_adapter import OpenAIAdapter
            return OpenAIAdapter(self.settings_manager)
        elif llm_type == "anthropic":
            from adapters.llm.anthropic_adapter import AnthropicAdapter
            return AnthropicAdapter(self.settings_manager)
        elif llm_type == "local":
            from adapters.llm.local_adapter import LocalAdapter
            return LocalAdapter(self.settings_manager)
        else:
            # Default to OpenAI
            from adapters.llm.openai_adapter import OpenAIAdapter
            return OpenAIAdapter(self.settings_manager)
            
    async def _create_knowledge_base(self):
        """Create knowledge base based on settings"""
        kb_type = self.settings_manager.get("agent.knowledge_base_type", "sqlite")
        
        if kb_type == "sqlite":
            from knowledge.sqlite_kb import SQLiteKnowledgeBase
            return SQLiteKnowledgeBase(self.settings_manager)
        elif kb_type == "vector":
            from knowledge.vector_kb import VectorKnowledgeBase
            return VectorKnowledgeBase(self.settings_manager)
        else:
            # Default to SQLite
            from knowledge.sqlite_kb import SQLiteKnowledgeBase
            return SQLiteKnowledgeBase(self.settings_manager)
```

## 2. Core Capabilities

### 2.1 Information Retrieval

The agent provides access to information through:

1. **Knowledge Base Access**: Retrieving information from the VPA's local knowledge base
2. **Web Search Integration**: Searching the web for current information when appropriate
3. **Document Analysis**: Analyzing user-provided documents and files
4. **Data Summarization**: Summarizing large volumes of information into concise responses

```python
class KnowledgeAccessTool:
    """Tool for accessing knowledge base information"""
    
    def __init__(self, knowledge_base):
        self.knowledge_base = knowledge_base
        
    async def execute(self, params):
        """Execute knowledge retrieval"""
        query = params.get("query", "")
        if not query:
            return {"error": "No query provided"}
            
        # Search knowledge base
        results = await self.knowledge_base.search(query)
        
        return {
            "results": results,
            "result_count": len(results)
        }
        
class WebSearchTool:
    """Tool for web search functionality"""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.search_provider = None
        self._initialize_provider()
        
    def _initialize_provider(self):
        """Initialize search provider based on settings"""
        provider_name = self.settings_manager.get("agent.search_provider", "bing")
        
        if provider_name == "bing":
            from tools.search.bing import BingSearch
            self.search_provider = BingSearch(self.settings_manager)
        elif provider_name == "duckduckgo":
            from tools.search.duckduckgo import DuckDuckGoSearch
            self.search_provider = DuckDuckGoSearch()
        else:
            # Default to Bing
            from tools.search.bing import BingSearch
            self.search_provider = BingSearch(self.settings_manager)
            
    async def execute(self, params):
        """Execute web search"""
        query = params.get("query", "")
        result_count = params.get("result_count", 5)
        
        if not query:
            return {"error": "No query provided"}
            
        # Execute search
        results = await self.search_provider.search(query, result_count)
        
        return {
            "results": results,
            "result_count": len(results)
        }
```

### 2.2 Task Management

The agent can assist with task management through:

1. **Task Creation**: Creating tasks from conversation context
2. **Task Tracking**: Tracking task status and providing updates
3. **Reminders**: Setting up reminders for tasks and events
4. **Priority Management**: Suggesting task priorities based on context

```python
class TaskManagerTool:
    """Tool for managing tasks"""
    
    def __init__(self, task_manager):
        self.task_manager = task_manager
        
    async def execute(self, params):
        """Execute task management operation"""
        operation = params.get("operation", "")
        
        if operation == "create_task":
            return await self._create_task(params)
        elif operation == "list_tasks":
            return await self._list_tasks(params)
        elif operation == "update_task":
            return await self._update_task(params)
        elif operation == "complete_task":
            return await self._complete_task(params)
        else:
            return {"error": "Invalid operation"}
            
    async def _create_task(self, params):
        """Create a new task"""
        title = params.get("title", "")
        description = params.get("description", "")
        due_date = params.get("due_date", None)
        priority = params.get("priority", "medium")
        
        if not title:
            return {"error": "Task title is required"}
            
        # Create task
        task_id = await self.task_manager.create_task(
            title,
            description,
            due_date,
            priority
        )
        
        return {
            "task_id": task_id,
            "title": title,
            "result": "Task created successfully"
        }
        
    async def _list_tasks(self, params):
        """List tasks based on filters"""
        filters = params.get("filters", {})
        
        # Get tasks
        tasks = await self.task_manager.get_tasks(filters)
        
        return {
            "tasks": tasks,
            "count": len(tasks)
        }
        
    async def _update_task(self, params):
        """Update an existing task"""
        task_id = params.get("task_id", "")
        updates = params.get("updates", {})
        
        if not task_id:
            return {"error": "Task ID is required"}
            
        # Update task
        success = await self.task_manager.update_task(task_id, updates)
        
        return {
            "success": success,
            "task_id": task_id,
            "result": "Task updated successfully" if success else "Failed to update task"
        }
        
    async def _complete_task(self, params):
        """Mark a task as complete"""
        task_id = params.get("task_id", "")
        
        if not task_id:
            return {"error": "Task ID is required"}
            
        # Complete task
        success = await self.task_manager.complete_task(task_id)
        
        return {
            "success": success,
            "task_id": task_id,
            "result": "Task marked complete" if success else "Failed to update task"
        }
```

### 2.3 System Integration

The agent integrates with system functionality through:

1. **Application Control**: Opening/closing applications and performing operations
2. **System Information**: Retrieving system status and information
3. **Settings Management**: Adjusting VPA settings based on user preferences
4. **File Operations**: Basic file operations through system integration

```python
class SystemActionTool:
    """Tool for system actions and integration"""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.system_integrator = None
        self._initialize_integrator()
        
    def _initialize_integrator(self):
        """Initialize system integrator"""
        from tools.system.windows_integrator import WindowsIntegrator
        self.system_integrator = WindowsIntegrator(self.settings_manager)
            
    async def execute(self, params):
        """Execute system action"""
        action = params.get("action", "")
        
        if action == "open_application":
            return await self._open_application(params)
        elif action == "get_system_info":
            return await self._get_system_info(params)
        elif action == "file_operation":
            return await self._file_operation(params)
        else:
            return {"error": "Invalid action"}
            
    async def _open_application(self, params):
        """Open an application"""
        app_name = params.get("app_name", "")
        
        if not app_name:
            return {"error": "Application name is required"}
            
        # Open application
        success, result = await self.system_integrator.open_application(app_name)
        
        return {
            "success": success,
            "app_name": app_name,
            "result": result
        }
        
    async def _get_system_info(self, params):
        """Get system information"""
        info_type = params.get("info_type", "basic")
        
        # Get system info
        system_info = await self.system_integrator.get_system_info(info_type)
        
        return system_info
        
    async def _file_operation(self, params):
        """Perform file operation"""
        operation = params.get("operation", "")
        path = params.get("path", "")
        
        if not operation or not path:
            return {"error": "Operation and path are required"}
            
        # Check if operation is allowed
        allowed_operations = ["list", "info", "exists"]
        if operation not in allowed_operations:
            return {"error": f"Operation not allowed. Allowed operations: {', '.join(allowed_operations)}"}
            
        # Perform operation
        result = await self.system_integrator.file_operation(operation, path)
        
        return result
```

### 2.4 Calendar Integration

The agent can interact with calendar systems through:

1. **Event Creation**: Creating calendar events from conversation context
2. **Event Management**: Viewing, updating, and deleting calendar events
3. **Scheduling Assistance**: Finding available time slots and suggesting meeting times
4. **Notifications**: Managing event notifications and reminders

```python
class CalendarTool:
    """Tool for calendar operations"""
    
    def __init__(self, calendar_manager):
        self.calendar_manager = calendar_manager
        
    async def execute(self, params):
        """Execute calendar operation"""
        operation = params.get("operation", "")
        
        if operation == "create_event":
            return await self._create_event(params)
        elif operation == "list_events":
            return await self._list_events(params)
        elif operation == "find_available_slots":
            return await self._find_available_slots(params)
        else:
            return {"error": "Invalid operation"}
            
    async def _create_event(self, params):
        """Create a calendar event"""
        title = params.get("title", "")
        start_time = params.get("start_time", "")
        end_time = params.get("end_time", "")
        description = params.get("description", "")
        
        if not title or not start_time or not end_time:
            return {"error": "Title, start time, and end time are required"}
            
        # Create event
        event_id = await self.calendar_manager.create_event(
            title,
            start_time,
            end_time,
            description
        )
        
        return {
            "event_id": event_id,
            "title": title,
            "result": "Event created successfully"
        }
        
    async def _list_events(self, params):
        """List calendar events"""
        start_date = params.get("start_date", "")
        end_date = params.get("end_date", "")
        
        if not start_date:
            # Default to today
            start_date = datetime.now().strftime("%Y-%m-%d")
            
        if not end_date:
            # Default to today
            end_date = start_date
            
        # Get events
        events = await self.calendar_manager.get_events(start_date, end_date)
        
        return {
            "events": events,
            "count": len(events),
            "date_range": f"{start_date} to {end_date}"
        }
        
    async def _find_available_slots(self, params):
        """Find available time slots"""
        date = params.get("date", "")
        duration_minutes = params.get("duration_minutes", 30)
        
        if not date:
            # Default to today
            date = datetime.now().strftime("%Y-%m-%d")
            
        # Find slots
        slots = await self.calendar_manager.find_available_slots(date, duration_minutes)
        
        return {
            "date": date,
            "available_slots": slots,
            "duration_minutes": duration_minutes
        }
```

## 3. Integration Points

### 3.1 UI Integration

The agent integrates with the VPA UI through:

1. **Chat Interface**: Real-time interaction with users via text
2. **Voice Interface**: Processing voice inputs and providing voice responses
3. **Action Cards**: Rich UI elements for displaying structured information
4. **System Notifications**: Alerting users to important information

```python
class UIManager:
    """Manager for UI integration with agent"""
    
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self._subscribe_to_events()
        
    def _subscribe_to_events(self):
        """Subscribe to agent events"""
        self.event_bus.subscribe(
            "agent.processing.start",
            self._on_processing_start,
            async_callback=True
        )
        
        self.event_bus.subscribe(
            "agent.processing.complete",
            self._on_processing_complete,
            async_callback=True
        )
        
        self.event_bus.subscribe(
            "agent.processing.error",
            self._on_processing_error,
            async_callback=True
        )
        
    async def _on_processing_start(self, event_data):
        """Handle processing start event"""
        # Show typing indicator in UI
        await self.event_bus.emit_async("ui.chat.typing_indicator", {"show": True})
        
    async def _on_processing_complete(self, event_data):
        """Handle processing complete event"""
        # Hide typing indicator
        await self.event_bus.emit_async("ui.chat.typing_indicator", {"show": False})
        
        # Add response message to chat
        await self.event_bus.emit_async("ui.chat.add_message", {
            "role": "assistant",
            "content": event_data.get("response", "")
        })
        
        # Check if response has tool results that need special UI rendering
        if event_data.get("has_tools", False):
            await self._render_tool_results(event_data)
            
    async def _on_processing_error(self, event_data):
        """Handle processing error event"""
        # Hide typing indicator
        await self.event_bus.emit_async("ui.chat.typing_indicator", {"show": False})
        
        # Add error message to chat
        await self.event_bus.emit_async("ui.chat.add_message", {
            "role": "assistant",
            "content": f"I'm sorry, an error occurred: {event_data.get('error', 'Unknown error')}",
            "is_error": True
        })
        
    async def _render_tool_results(self, event_data):
        """Render tool results in UI if needed"""
        # Implementation depends on specific tools used
        # For example, render calendar results as a calendar widget
        pass
```

### 3.2 Plugin System

The agent integrates with the plugin system to extend its capabilities:

1. **Plugin Discovery**: Discovering available plugins and their capabilities
2. **Plugin Invocation**: Invoking plugin functionality based on user needs
3. **Result Processing**: Processing and presenting plugin results to users
4. **Permission Management**: Managing user permissions for plugin access

```python
class PluginManager:
    """Manager for plugin integration with agent"""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.plugins = {}
        self.plugin_tools = {}
        
    async def initialize(self):
        """Initialize plugin manager"""
        try:
            # Load plugins
            plugin_dir = self.settings_manager.get("plugins.directory", "plugins")
            
            # Ensure plugin directory exists
            if not os.path.exists(plugin_dir):
                os.makedirs(plugin_dir)
                
            # Load each plugin
            for plugin_name in os.listdir(plugin_dir):
                plugin_path = os.path.join(plugin_dir, plugin_name)
                
                if os.path.isdir(plugin_path) and os.path.exists(os.path.join(plugin_path, "plugin.json")):
                    await self._load_plugin(plugin_path)
                    
            return True
        except Exception as e:
            logger.error(f"Failed to initialize plugin manager: {e}")
            return False
            
    async def _load_plugin(self, plugin_path):
        """Load a plugin from its directory"""
        try:
            # Load plugin.json
            with open(os.path.join(plugin_path, "plugin.json"), "r") as f:
                plugin_info = json.load(f)
                
            plugin_id = plugin_info.get("id", "")
            if not plugin_id:
                logger.warning(f"Plugin at {plugin_path} has no ID, skipping")
                return
                
            # Check if plugin is enabled
            if not self._is_plugin_enabled(plugin_id):
                logger.info(f"Plugin {plugin_id} is disabled, skipping")
                return
                
            # Load plugin module
            plugin_module_path = os.path.join(plugin_path, plugin_info.get("main", "main.py"))
            spec = importlib.util.spec_from_file_location(f"plugin_{plugin_id}", plugin_module_path)
            plugin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin_module)
            
            # Create plugin instance
            if hasattr(plugin_module, "create_plugin"):
                plugin_instance = plugin_module.create_plugin()
                
                # Initialize plugin
                if hasattr(plugin_instance, "initialize"):
                    await plugin_instance.initialize(self.settings_manager)
                    
                # Register plugin
                self.plugins[plugin_id] = {
                    "info": plugin_info,
                    "instance": plugin_instance
                }
                
                # Register plugin tools
                if hasattr(plugin_instance, "get_tools"):
                    tools = plugin_instance.get_tools()
                    for tool in tools:
                        self.plugin_tools[tool["name"]] = {
                            "plugin_id": plugin_id,
                            "tool": tool
                        }
                        
                logger.info(f"Loaded plugin: {plugin_id}")
            else:
                logger.warning(f"Plugin {plugin_id} has no create_plugin function, skipping")
                
        except Exception as e:
            logger.error(f"Failed to load plugin from {plugin_path}: {e}")
            
    def _is_plugin_enabled(self, plugin_id):
        """Check if a plugin is enabled"""
        enabled_plugins = self.settings_manager.get("plugins.enabled", [])
        return plugin_id in enabled_plugins or enabled_plugins == ["*"]
        
    def get_plugin_tools(self):
        """Get tools provided by plugins"""
        return list(self.plugin_tools.values())
        
    async def execute_plugin_tool(self, tool_name, params):
        """Execute a plugin tool"""
        if tool_name not in self.plugin_tools:
            return {"error": f"Tool not found: {tool_name}"}
            
        plugin_tool = self.plugin_tools[tool_name]
        plugin_id = plugin_tool["plugin_id"]
        
        if plugin_id not in self.plugins:
            return {"error": f"Plugin not found: {plugin_id}"}
            
        plugin = self.plugins[plugin_id]["instance"]
        
        try:
            # Execute tool
            if hasattr(plugin, "execute_tool"):
                result = await plugin.execute_tool(tool_name, params)
                return result
            else:
                return {"error": f"Plugin {plugin_id} does not support tool execution"}
        except Exception as e:
            logger.error(f"Error executing plugin tool {tool_name}: {e}")
            return {"error": f"Tool execution error: {str(e)}"}
```

### 3.3 Event Bus

The agent uses the event bus for communication with other system components:

```python
# Agent-related events
agent.processing.start   # Agent started processing user input
agent.processing.complete   # Agent completed processing and generated response
agent.processing.error   # Agent encountered an error during processing
agent.tool.execution.start   # Agent started executing a tool
agent.tool.execution.complete   # Agent completed tool execution
agent.context.updated   # Agent context was updated

# Agent-triggered events
ui.chat.add_message   # Add a message to the chat UI
ui.chat.typing_indicator   # Show/hide typing indicator
ui.notification.show   # Show a notification
ui.action_card.show   # Show an action card
```

## 4. Customization Options

### 4.1 Agent Personality

Users can customize the agent's personality through settings:

```python
class PersonalityManager:
    """Manager for agent personality customization"""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        
    def get_personality_settings(self):
        """Get current personality settings"""
        return {
            "formality": self.settings_manager.get("agent.personality.formality", "balanced"),
            "verbosity": self.settings_manager.get("agent.personality.verbosity", "balanced"),
            "friendliness": self.settings_manager.get("agent.personality.friendliness", "balanced"),
            "humor": self.settings_manager.get("agent.personality.humor", "minimal"),
            "empathy": self.settings_manager.get("agent.personality.empathy", "balanced")
        }
        
    def set_personality_setting(self, setting, value):
        """Set a personality setting"""
        valid_settings = ["formality", "verbosity", "friendliness", "humor", "empathy"]
        valid_values = ["minimal", "reduced", "balanced", "enhanced", "maximum"]
        
        if setting not in valid_settings:
            return False
            
        if value not in valid_values:
            return False
            
        self.settings_manager.set(f"agent.personality.{setting}", value)
        return True
        
    def get_system_prompt_additions(self):
        """Get system prompt additions based on personality settings"""
        personality = self.get_personality_settings()
        prompt_additions = []
        
        # Formality setting
        if personality["formality"] == "minimal":
            prompt_additions.append("Be very casual and informal in your responses.")
        elif personality["formality"] == "reduced":
            prompt_additions.append("Be somewhat casual and conversational.")
        elif personality["formality"] == "enhanced":
            prompt_additions.append("Be somewhat formal and professional.")
        elif personality["formality"] == "maximum":
            prompt_additions.append("Be very formal and professional in your responses.")
        
        # Verbosity setting
        if personality["verbosity"] == "minimal":
            prompt_additions.append("Keep responses extremely concise and brief.")
        elif personality["verbosity"] == "reduced":
            prompt_additions.append("Keep responses relatively short and to the point.")
        elif personality["verbosity"] == "enhanced":
            prompt_additions.append("Provide somewhat detailed and comprehensive responses.")
        elif personality["verbosity"] == "maximum":
            prompt_additions.append("Provide extremely detailed and comprehensive responses.")
            
        # Friendliness setting
        if personality["friendliness"] == "minimal":
            prompt_additions.append("Maintain a strictly professional, neutral tone.")
        elif personality["friendliness"] == "reduced":
            prompt_additions.append("Be somewhat reserved but polite.")
        elif personality["friendliness"] == "enhanced":
            prompt_additions.append("Be warm and personable in your responses.")
        elif personality["friendliness"] == "maximum":
            prompt_additions.append("Be extremely warm, friendly, and enthusiastic.")
            
        # Humor setting
        if personality["humor"] == "minimal":
            prompt_additions.append("Do not use humor in your responses.")
        elif personality["humor"] == "reduced":
            prompt_additions.append("Use minimal, subtle humor only when appropriate.")
        elif personality["humor"] == "enhanced":
            prompt_additions.append("Include moderate humor in your responses where appropriate.")
        elif personality["humor"] == "maximum":
            prompt_additions.append("Use humor frequently in your responses to be entertaining.")
            
        # Empathy setting
        if personality["empathy"] == "minimal":
            prompt_additions.append("Focus solely on factual information.")
        elif personality["empathy"] == "reduced":
            prompt_additions.append("Show limited acknowledgment of emotions.")
        elif personality["empathy"] == "enhanced":
            prompt_additions.append("Be empathetic and acknowledge emotions in your responses.")
        elif personality["empathy"] == "maximum":
            prompt_additions.append("Show strong empathy and emotional understanding in all responses.")
            
        return prompt_additions
```

### 4.2 Knowledge Sources

Users can customize the knowledge sources used by the agent:

```python
class KnowledgeSourceManager:
    """Manager for knowledge source customization"""
    
    def __init__(self, settings_manager, event_bus):
        self.settings_manager = settings_manager
        self.event_bus = event_bus
        self.knowledge_sources = {}
        
    async def initialize(self):
        """Initialize knowledge sources"""
        # Get enabled knowledge sources
        enabled_sources = self.settings_manager.get("agent.knowledge_sources.enabled", ["local", "web"])
        
        # Initialize enabled sources
        if "local" in enabled_sources:
            await self._initialize_local_kb()
            
        if "web" in enabled_sources:
            await self._initialize_web_search()
            
        if "personal" in enabled_sources:
            await self._initialize_personal_kb()
            
        if "plugins" in enabled_sources:
            await self._initialize_plugin_kb()
            
    async def _initialize_local_kb(self):
        """Initialize local knowledge base"""
        from knowledge.local_kb import LocalKnowledgeBase
        
        local_kb = LocalKnowledgeBase(self.settings_manager)
        await local_kb.initialize()
        
        self.knowledge_sources["local"] = {
            "name": "Local Knowledge Base",
            "instance": local_kb,
            "priority": 100
        }
        
    async def _initialize_web_search(self):
        """Initialize web search"""
        from knowledge.web_search import WebSearch
        
        web_search = WebSearch(self.settings_manager)
        await web_search.initialize()
        
        self.knowledge_sources["web"] = {
            "name": "Web Search",
            "instance": web_search,
            "priority": 50
        }
        
    async def _initialize_personal_kb(self):
        """Initialize personal knowledge base"""
        from knowledge.personal_kb import PersonalKnowledgeBase
        
        personal_kb = PersonalKnowledgeBase(self.settings_manager)
        await personal_kb.initialize()
        
        self.knowledge_sources["personal"] = {
            "name": "Personal Knowledge",
            "instance": personal_kb,
            "priority": 150
        }
        
    async def _initialize_plugin_kb(self):
        """Initialize plugin knowledge bases"""
        # Implementation depends on plugin system
        pass
        
    async def search(self, query, max_results=5):
        """Search across all enabled knowledge sources"""
        results = []
        
        # Get sources sorted by priority
        sources = sorted(
            self.knowledge_sources.values(),
            key=lambda x: x["priority"],
            reverse=True
        )
        
        # Search each source
        for source in sources:
            if len(results) >= max_results:
                break
                
            source_results = await source["instance"].search(query, max_results - len(results))
            
            # Add source information to results
            for result in source_results:
                result["source"] = source["name"]
                
            results.extend(source_results)
            
        return results
        
    def get_enabled_sources(self):
        """Get enabled knowledge sources"""
        return list(self.knowledge_sources.keys())
        
    def enable_source(self, source_id):
        """Enable a knowledge source"""
        enabled_sources = self.settings_manager.get("agent.knowledge_sources.enabled", [])
        
        if source_id not in enabled_sources:
            enabled_sources.append(source_id)
            self.settings_manager.set("agent.knowledge_sources.enabled", enabled_sources)
            
    def disable_source(self, source_id):
        """Disable a knowledge source"""
        enabled_sources = self.settings_manager.get("agent.knowledge_sources.enabled", [])
        
        if source_id in enabled_sources:
            enabled_sources.remove(source_id)
            self.settings_manager.set("agent.knowledge_sources.enabled", enabled_sources)
```

### 4.3 Response Preferences

Users can customize how the agent responds to them:

```python
class ResponsePreferencesManager:
    """Manager for response preferences"""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        
    def get_response_preferences(self):
        """Get current response preferences"""
        return {
            "format": self.settings_manager.get("agent.response.format", "text"),
            "length": self.settings_manager.get("agent.response.length", "balanced"),
            "citations": self.settings_manager.get("agent.response.citations", True),
            "code_blocks": self.settings_manager.get("agent.response.code_blocks", True),
            "structured_data": self.settings_manager.get("agent.response.structured_data", True)
        }
        
    def set_response_preference(self, preference, value):
        """Set a response preference"""
        valid_preferences = ["format", "length", "citations", "code_blocks", "structured_data"]
        
        if preference not in valid_preferences:
            return False
            
        self.settings_manager.set(f"agent.response.{preference}", value)
        return True
        
    def get_response_formatting_instructions(self):
        """Get response formatting instructions based on preferences"""
        preferences = self.get_response_preferences()
        instructions = []
        
        # Format preference
        if preferences["format"] == "markdown":
            instructions.append("Format your responses using Markdown syntax for improved readability.")
        elif preferences["format"] == "html":
            instructions.append("Format your responses using simple HTML tags for structured content.")
        elif preferences["format"] == "plain":
            instructions.append("Format your responses as plain text without any special formatting.")
            
        # Length preference
        if preferences["length"] == "concise":
            instructions.append("Keep your responses brief and to the point.")
        elif preferences["length"] == "detailed":
            instructions.append("Provide detailed, comprehensive responses.")
            
        # Citations preference
        if preferences["citations"]:
            instructions.append("Include citations or sources for factual information where relevant.")
        else:
            instructions.append("Do not include citations or sources in your responses.")
            
        # Code blocks preference
        if preferences["code_blocks"]:
            instructions.append("When providing code, use proper code block formatting.")
        else:
            instructions.append("Avoid using code blocks in your responses.")
            
        # Structured data preference
        if preferences["structured_data"]:
            instructions.append("When appropriate, use tables, lists, or other structured formats to organize information.")
        else:
            instructions.append("Use simple paragraphs for all information without complex structures.")
            
        return instructions
```

## 5. Context Management

### 5.1 Conversation Context

The agent maintains context across the conversation:

```python
class ContextManager:
    """Manager for conversation context"""
    
    def __init__(self):
        self.context = {}
        self.context_history = []
        self.expiration_times = {}
        
    def get_current_context(self):
        """Get current conversation context"""
        # First clean expired context
        self._clean_expired_context()
        
        return self.context
        
    def update_context(self, user_input, response):
        """Update context based on new conversation turn"""
        # Extract entities from user input and response
        extracted_context = self._extract_context(user_input, response)
        
        # Update context with new information
        for key, value in extracted_context.items():
            self.context[key] = value
            
            # Set expiration time (30 minutes from now)
            expiration_time = time.time() + (30 * 60)
            self.expiration_times[key] = expiration_time
            
        # Save to history
        self.context_history.append({
            "timestamp": time.time(),
            "context": self.context.copy()
        })
        
        # Limit history size
        if len(self.context_history) > 20:
            self.context_history = self.context_history[-20:]
            
    def set_context_value(self, key, value, expiration_minutes=30):
        """Set a specific context value"""
        self.context[key] = value
        
        # Set expiration time
        expiration_time = time.time() + (expiration_minutes * 60)
        self.expiration_times[key] = expiration_time
        
    def get_context_value(self, key):
        """Get a specific context value"""
        # Check if key exists and is not expired
        if key in self.context and key in self.expiration_times:
            if time.time() < self.expiration_times[key]:
                return self.context[key]
                
        return None
        
    def clear_context(self):
        """Clear all context"""
        self.context = {}
        self.expiration_times = {}
        
    def _clean_expired_context(self):
        """Remove expired context entries"""
        current_time = time.time()
        expired_keys = []
        
        for key, expiration_time in self.expiration_times.items():
            if current_time > expiration_time:
                expired_keys.append(key)
                
        for key in expired_keys:
            if key in self.context:
                del self.context[key]
            del self.expiration_times[key]
            
    def _extract_context(self, user_input, response):
        """Extract context from user input and response"""
        # This is a simplified implementation
        # In practice, this would use NLP to extract entities and context
        
        extracted_context = {}
        
        # Extract user preferences (simplified example)
        if "prefer" in user_input.lower():
            if "dark mode" in user_input.lower():
                extracted_context["ui_preference_theme"] = "dark"
            elif "light mode" in user_input.lower():
                extracted_context["ui_preference_theme"] = "light"
                
        # Extract locations (simplified example)
        if "in " in user_input.lower():
            parts = user_input.split("in ")
            if len(parts) > 1:
                location_part = parts[1].split(" ")[0]
                extracted_context["location_reference"] = location_part
                
        # Extract time references (simplified example)
        if "tomorrow" in user_input.lower():
            from datetime import datetime, timedelta
            tomorrow = datetime.now() + timedelta(days=1)
            extracted_context["time_reference"] = tomorrow.strftime("%Y-%m-%d")
                
        return extracted_context
```

### 5.2 Long-Term Memory

The agent implements long-term memory for persistent information:

```python
class LongTermMemory:
    """Long-term memory for agent"""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.db_path = None
        self.db = None
        self._initialize()
        
    def _initialize(self):
        """Initialize long-term memory database"""
        try:
            # Get database path
            data_dir = self.settings_manager.get("agent.data_directory", "data")
            self.db_path = os.path.join(data_dir, "memory.db")
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Connect to database
            import sqlite3
            self.db = sqlite3.connect(self.db_path)
            
            # Create tables if not exists
            self._create_tables()
        except Exception as e:
            logger.error(f"Failed to initialize long-term memory: {e}")
            
    def _create_tables(self):
        """Create necessary database tables"""
        cursor = self.db.cursor()
        
        # Create memories table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_type TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata TEXT,
            importance INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create tags table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory_tags (
            memory_id INTEGER,
            tag TEXT NOT NULL,
            PRIMARY KEY (memory_id, tag),
            FOREIGN KEY (memory_id) REFERENCES memories(id)
        )
        """)
        
        self.db.commit()
        
    def store_memory(self, memory_type, content, metadata=None, importance=1, tags=None):
        """Store a memory in long-term storage"""
        try:
            cursor = self.db.cursor()
            
            # Insert memory
            cursor.execute(
                "INSERT INTO memories (memory_type, content, metadata, importance) VALUES (?, ?, ?, ?)",
                (memory_type, content, json.dumps(metadata or {}), importance)
            )
            
            memory_id = cursor.lastrowid
            
            # Add tags
            if tags:
                for tag in tags:
                    cursor.execute(
                        "INSERT INTO memory_tags (memory_id, tag) VALUES (?, ?)",
                        (memory_id, tag)
                    )
                    
            self.db.commit()
            return memory_id
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return None
            
    def retrieve_memories(self, memory_type=None, tags=None, limit=10):
        """Retrieve memories based on criteria"""
        try:
            cursor = self.db.cursor()
            
            query_parts = ["SELECT m.* FROM memories m"]
            params = []
            
            # Add tag join if needed
            if tags:
                query_parts[0] += " JOIN memory_tags t ON m.id = t.memory_id"
                
            where_clauses = []
            
            # Add memory type filter
            if memory_type:
                where_clauses.append("m.memory_type = ?")
                params.append(memory_type)
                
            # Add tag filter
            if tags:
                placeholders = ", ".join(["?"] * len(tags))
                where_clauses.append(f"t.tag IN ({placeholders})")
                params.extend(tags)
                
            # Combine where clauses
            if where_clauses:
                query_parts.append("WHERE " + " AND ".join(where_clauses))
                
            # Add ordering and limit
            query_parts.append("ORDER BY m.importance DESC, m.last_accessed DESC")
            query_parts.append("LIMIT ?")
            params.append(limit)
            
            # Execute query
            query = " ".join(query_parts)
            cursor.execute(query, params)
            
            # Process results
            results = []
            for row in cursor.fetchall():
                memory = {
                    "id": row[0],
                    "memory_type": row[1],
                    "content": row[2],
                    "metadata": json.loads(row[3]),
                    "importance": row[4],
                    "created_at": row[5],
                    "last_accessed": row[6]
                }
                results.append(memory)
                
            # Update last accessed time
            if results:
                memory_ids = [r["id"] for r in results]
                placeholders = ", ".join(["?"] * len(memory_ids))
                cursor.execute(
                    f"UPDATE memories SET last_accessed = CURRENT_TIMESTAMP WHERE id IN ({placeholders})",
                    memory_ids
                )
                self.db.commit()
                
            return results
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            return []
            
    def search_memories(self, query, limit=10):
        """Search memories by content"""
        try:
            cursor = self.db.cursor()
            
            # Perform full-text search
            cursor.execute(
                "SELECT * FROM memories WHERE content LIKE ? ORDER BY importance DESC, last_accessed DESC LIMIT ?",
                (f"%{query}%", limit)
            )
            
            # Process results
            results = []
            for row in cursor.fetchall():
                memory = {
                    "id": row[0],
                    "memory_type": row[1],
                    "content": row[2],
                    "metadata": json.loads(row[3]),
                    "importance": row[4],
                    "created_at": row[5],
                    "last_accessed": row[6]
                }
                results.append(memory)
                
            # Update last accessed time
            if results:
                memory_ids = [r["id"] for r in results]
                placeholders = ", ".join(["?"] * len(memory_ids))
                cursor.execute(
                    f"UPDATE memories SET last_accessed = CURRENT_TIMESTAMP WHERE id IN ({placeholders})",
                    memory_ids
                )
                self.db.commit()
                
            return results
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
            
    def delete_memory(self, memory_id):
        """Delete a memory"""
        try:
            cursor = self.db.cursor()
            
            # Delete memory tags
            cursor.execute("DELETE FROM memory_tags WHERE memory_id = ?", (memory_id,))
            
            # Delete memory
            cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to delete memory: {e}")
            return False
```

## 6. Performance Considerations

### 6.1 Response Time Targets

The agent aims to meet the following response time targets:

1. **Simple Queries**: < 2 seconds for factual queries and simple requests
2. **Complex Queries**: < 5 seconds for multi-step reasoning or data analysis
3. **Tool Execution**: Response time depends on the tool, but UI feedback is immediate

### 6.2 Resource Management

The agent implements resource management techniques:

```python
class ResourceManager:
    """Manager for agent resource usage"""
    
    def __init__(self, settings_manager):
        self.settings_manager = settings_manager
        self.resource_limits = self._load_resource_limits()
        
    def _load_resource_limits(self):
        """Load resource limits from settings"""
        return {
            "max_tokens_per_request": self.settings_manager.get("agent.resources.max_tokens_per_request", 4000),
            "max_conversation_length": self.settings_manager.get("agent.resources.max_conversation_length", 20),
            "max_tool_execution_time": self.settings_manager.get("agent.resources.max_tool_execution_time", 30),
            "max_concurrent_tools": self.settings_manager.get("agent.resources.max_concurrent_tools", 3)
        }
        
    def check_token_limit(self, text):
        """Check if text exceeds token limit"""
        # Simplified token counting (actual implementation would use a tokenizer)
        estimated_tokens = len(text.split())
        return estimated_tokens <= self.resource_limits["max_tokens_per_request"]
        
    def truncate_conversation_history(self, history):
        """Truncate conversation history to meet limits"""
        max_length = self.resource_limits["max_conversation_length"]
        
        if len(history) <= max_length:
            return history
            
        # Keep system message if present
        system_message = None
        for item in history:
            if item.get("role") == "system":
                system_message = item
                break
                
        # Keep most recent messages up to limit
        recent_history = history[-max_length:]
        
        # Add system message back if it was present
        if system_message and system_message not in recent_history:
            recent_history.insert(0, system_message)
            
        return recent_history
        
    async def execute_tool_with_timeout(self, tool, params):
        """Execute a tool with timeout protection"""
        max_time = self.resource_limits["max_tool_execution_time"]
        
        try:
            # Create task with timeout
            result = await asyncio.wait_for(tool.execute(params), timeout=max_time)
            return result
        except asyncio.TimeoutError:
            return {
                "error": f"Tool execution timed out after {max_time} seconds"
            }
        except Exception as e:
            return {
                "error": f"Tool execution failed: {str(e)}"
            }
```

### 6.3 Caching Strategy

The agent implements caching to improve performance:

```python
class ResponseCache:
    """Cache for agent responses"""
    
    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size
        self.access_times = {}
        
    def get(self, key):
        """Get cached response if available"""
        if key in self.cache:
            # Update access time
            self.access_times[key] = time.time()
            return self.cache[key]
        return None
        
    def set(self, key, value):
        """Cache a response"""
        # Check if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
            
        self.cache[key] = value
        self.access_times[key] = time.time()
        
    def _evict_oldest(self):
        """Evict oldest cache entry"""
        if not self.access_times:
            return
            
        # Find oldest key
        oldest_key = min(self.access_times, key=self.access_times.get)
        
        # Remove from cache
        if oldest_key in self.cache:
            del self.cache[oldest_key]
        del self.access_times[oldest_key]
        
    def clear(self):
        """Clear the cache"""
        self.cache = {}
        self.access_times = {}
        
    def _generate_cache_key(self, user_input, context):
        """Generate cache key from user input and context"""
        # Convert context to stable format for key generation
        stable_context = {}
        if context:
            for k in sorted(context.keys()):
                stable_context[k] = context[k]
                
        # Generate key
        key_parts = [
            user_input,
            json.dumps(stable_context, sort_keys=True)
        ]
        
        return hashlib.md5(json.dumps(key_parts).encode()).hexdigest()
```

## 7. Implementation Examples

### 7.1 Agent Initialization

Example of initializing the agent subsystem:

```python
async def initialize_agent_subsystem():
    """Initialize the agent subsystem"""
    from vpa.core.events import event_bus
    from vpa.core.settings import settings_manager
    
    logger.info("Initializing agent subsystem...")
    
    # Create agent manager
    agent_manager = AgentManager(event_bus, settings_manager)
    
    # Initialize agent
    success = await agent_manager.initialize()
    if not success:
        logger.error("Failed to initialize agent subsystem")
        return False
        
    # Register agent with service locator
    from vpa.core.services import service_locator
    service_locator.register("agent_manager", agent_manager)
    
    # Subscribe to input events
    event_bus.subscribe(
        "user.input.text",
        agent_manager._on_user_text_input,
        async_callback=True
    )
    
    logger.info("Agent subsystem initialized successfully")
    return True
```

### 7.2 Processing User Input

Example of processing user input through the agent:

```python
# In chat UI component

async def _on_send_message(self):
    """Handle send message button click"""
    # Get input text
    user_input = self.input_field.toPlainText().strip()
    if not user_input:
        return
        
    # Clear input field
    self.input_field.clear()
    
    # Add message to UI
    self._add_message("user", user_input)
    
    # Emit event for agent
    await self.event_bus.emit_async("user.input.text", {
        "text": user_input
    })
    
    # Show typing indicator
    self._set_typing_indicator(True)
    
# In agent manager

async def _on_user_text_input(self, event_data):
    """Handle user text input event"""
    user_input = event_data.get("text", "")
    if user_input:
        await self.process_user_input(user_input, "text")
```

### 7.3 Tool Execution

Example of executing a tool based on user request:

```python
async def _process_tool_calls(self, tool_calls):
    """Process tool calls from LLM response"""
    results = []
    
    for tool_call in tool_calls:
        tool_name = tool_call.get("name", "")
        params = tool_call.get("parameters", {})
        
        logger.info(f"Executing tool: {tool_name}")
        
        # Find tool
        tool = self.tool_executor.get_tool(tool_name)
        if not tool:
            results.append({
                "tool_name": tool_name,
                "error": f"Tool not found: {tool_name}"
            })
            continue
            
        # Execute tool with timeout protection
        try:
            # Emit tool execution start event
            await self.event_bus.emit_async("agent.tool.execution.start", {
                "tool_name": tool_name,
                "parameters": params
            })
            
            # Execute tool
            result = await self.resource_manager.execute_tool_with_timeout(tool, params)
            
            # Emit tool execution complete event
            await self.event_bus.emit_async("agent.tool.execution.complete", {
                "tool_name": tool_name,
                "parameters": params,
                "success": "error" not in result,
                "result": result
            })
            
            results.append({
                "tool_name": tool_name,
                "result": result
            })
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            
            results.append({
                "tool_name": tool_name,
                "error": f"Tool execution error: {str(e)}"
            })
            
    return results
```

## Conclusion

This Agent Capabilities Specification establishes the architecture, capabilities, and customization options for the VPA's AI agent. The agent integrates with various system components to provide a comprehensive and personalized assistant experience.

By implementing the capabilities outlined in this document, the VPA will deliver a robust AI agent that can effectively assist users with information retrieval, task management, system control, and other critical functions.

---

*Document created on August 28, 2025*  
*Version: 1.0*
