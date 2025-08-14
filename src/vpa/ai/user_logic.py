"""
User AI Logic Compartment

Handles user-defined custom automation and workflows as specified in VPA_APP_FINAL_OVERVIEW.md.
This compartment manages:
- User-defined custom automation/workflows
- User preference learning and adaptation
- Personalized automation suggestions
- Custom workflow builder integration

This is one of three AI logic compartments in the VPA agentic automation platform.
"""

import logging
from typing import Dict, Any, List, Optional, Callable, Set, Union
from datetime import datetime, timedelta
import asyncio
import json
from dataclasses import dataclass, field
from enum import Enum

from ..core.events import EventBus
from ..core.logging import get_structured_logger

logger = get_structured_logger(__name__)

class WorkflowTriggerType(Enum):
    """Types of workflow triggers"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"
    CONDITION_BASED = "condition_based"
    VOICE_COMMAND = "voice_command"
    PATTERN_DETECTION = "pattern_detection"

class WorkflowComplexity(Enum):
    """Workflow complexity levels"""
    SIMPLE = "simple"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class UserPreference:
    """Represents a user preference"""
    preference_id: str
    category: str  # 'automation', 'ui', 'scheduling', 'communication', etc.
    preference_key: str
    preference_value: Any
    confidence_level: float = 0.5  # 0.0 to 1.0
    learned_from: str = "manual"  # 'manual', 'pattern', 'feedback'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

@dataclass
class CustomWorkflow:
    """Represents a user-defined custom workflow"""
    workflow_id: str
    user_id: str
    workflow_name: str
    description: str
    trigger_type: WorkflowTriggerType
    trigger_config: Dict[str, Any]
    steps: List[Dict[str, Any]]
    complexity: WorkflowComplexity = WorkflowComplexity.SIMPLE
    is_active: bool = True
    is_public: bool = False  # Can be shared with other users
    tags: List[str] = field(default_factory=list)
    success_rate: float = 0.0
    total_executions: int = 0
    successful_executions: int = 0
    created_at: Optional[datetime] = None
    last_executed: Optional[datetime] = None
    last_modified: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_modified is None:
            self.last_modified = datetime.now()

@dataclass
class WorkflowSuggestion:
    """Represents an AI-generated workflow suggestion"""
    suggestion_id: str
    user_id: str
    suggested_workflow: Dict[str, Any]
    confidence: float
    reasoning: str
    based_on_patterns: List[str]
    created_at: Optional[datetime] = None
    user_feedback: Optional[str] = None  # 'accepted', 'rejected', 'modified'

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class UserAILogic:
    """
    User AI Logic Compartment
    
    Handles user-defined custom automation and workflows as specified in VPA_APP_FINAL_OVERVIEW.md.
    Learns user preferences, provides personalized automation suggestions, and manages custom workflows.
    """
    
    def __init__(self, event_bus: EventBus, config: Optional[Dict[str, Any]] = None):
        """Initialize User AI Logic compartment"""
        self.event_bus = event_bus
        self.config = config or {}
        self.logger = get_structured_logger(f"{__name__}.UserAILogic")
        
        # User management
        self.current_user_id: Optional[str] = None
        self.user_preferences: Dict[str, List[UserPreference]] = {}  # user_id -> preferences
        self.user_workflows: Dict[str, List[CustomWorkflow]] = {}  # user_id -> workflows
        self.user_patterns: Dict[str, Dict[str, Any]] = {}  # user_id -> behavior patterns
        
        # Workflow management
        self.active_workflows: Dict[str, CustomWorkflow] = {}
        self.workflow_schedules: Dict[str, Dict[str, Any]] = {}  # workflow_id -> schedule config
        self.running_workflows: Dict[str, asyncio.Task] = {}
        
        # Learning and suggestions
        self.workflow_suggestions: Dict[str, List[WorkflowSuggestion]] = {}  # user_id -> suggestions
        self.user_interactions: Dict[str, List[Dict[str, Any]]] = {}  # user_id -> interactions
        self.pattern_detection_enabled = True
        self.suggestion_threshold = 0.7  # Minimum confidence for suggestions
        
        # Voice command integration
        self.voice_commands: Dict[str, str] = {}  # voice_phrase -> workflow_id
        self.voice_enabled = False
        
        # State management
        self.is_initialized = False
        self.is_running = False
        self.learning_mode = True
        
        self.logger.info("User AI Logic compartment created")
    
    async def initialize(self) -> bool:
        """Initialize the User AI Logic compartment"""
        try:
            if self.is_initialized:
                self.logger.warning("User AI Logic already initialized")
                return True
            
            # Register event handlers
            await self._register_event_handlers()
            
            # Initialize user data storage
            await self._initialize_user_data()
            
            # Start pattern detection
            if self.pattern_detection_enabled:
                await self._start_pattern_detection()
            
            # Load scheduled workflows
            await self._load_scheduled_workflows()
            
            self.is_initialized = True
            self.is_running = True
            
            # Notify system that User AI Logic is ready
            self.event_bus.emit("ai.user_logic.initialized", {
                "compartment": "user_logic",
                "status": "ready",
                "learning_mode": self.learning_mode,
                "pattern_detection": self.pattern_detection_enabled,
                "timestamp": datetime.now().isoformat()
            })
            
            self.logger.info("User AI Logic compartment initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize User AI Logic: {e}")
            return False
    
    async def _register_event_handlers(self) -> None:
        """Register event handlers for User AI Logic"""
        # User workflow events
        self.event_bus.subscribe("ai.user.create_workflow", self._handle_create_workflow)
        self.event_bus.subscribe("ai.user.execute_workflow", self._handle_execute_workflow)
        # Note: Update and delete workflow handlers to be implemented
        # self.event_bus.subscribe("ai.user.update_workflow", self._handle_update_workflow)
        # self.event_bus.subscribe("ai.user.delete_workflow", self._handle_delete_workflow)
        
        # User preference events
        self.event_bus.subscribe("ai.user.set_preference", self._handle_set_preference)
        self.event_bus.subscribe("ai.user.get_preferences", self._handle_get_preferences)
        # Note: Learn preference handler to be implemented
        # self.event_bus.subscribe("ai.user.learn_preference", self._handle_learn_preference)
        
        # Workflow suggestion events
        self.event_bus.subscribe("ai.user.get_suggestions", self._handle_get_suggestions)
        self.event_bus.subscribe("ai.user.feedback_suggestion", self._handle_suggestion_feedback)
        
        # User interaction tracking
        self.event_bus.subscribe("user.interaction.*", self._handle_user_interaction)
        # Note: UI action handler to be implemented
        # self.event_bus.subscribe("ui.action.*", self._handle_ui_action)
        
        # Voice command events
        self.event_bus.subscribe("voice.command.detected", self._handle_voice_command)
        self.event_bus.subscribe("ai.user.register_voice_command", self._handle_register_voice_command)
        
        # Scheduling events
        # Note: Scheduled trigger handler to be implemented
        # self.event_bus.subscribe("scheduler.trigger", self._handle_scheduled_trigger)
        
        # Pattern detection events
        # Note: Pattern detected handler to be implemented
        # self.event_bus.subscribe("ai.user.pattern_detected", self._handle_pattern_detected)
        
        # Resource monitoring integration
        self.event_bus.subscribe("resource.strain.detected", self._handle_resource_strain)
        
        # User session events
        self.event_bus.subscribe("user.login", self._handle_user_login)
        self.event_bus.subscribe("user.logout", self._handle_user_logout)
        
        self.logger.info("Event handlers registered for User AI Logic")
    
    async def _initialize_user_data(self) -> None:
        """Initialize user data storage structures"""
        # Initialize empty data structures for new users
        # In a real implementation, this would load from persistent storage
        self.logger.info("User data storage initialized")
    
    async def _start_pattern_detection(self) -> None:
        """Start background pattern detection task"""
        if self.pattern_detection_enabled:
            asyncio.create_task(self._pattern_detection_loop())
            self.logger.info("Pattern detection started")
    
    async def _pattern_detection_loop(self) -> None:
        """Background task for detecting user behavior patterns"""
        while self.is_running and self.pattern_detection_enabled:
            try:
                await asyncio.sleep(300)  # Check patterns every 5 minutes
                
                if self.current_user_id:
                    await self._analyze_user_patterns(self.current_user_id)
                    await self._generate_workflow_suggestions(self.current_user_id)
                
            except Exception as e:
                self.logger.error(f"Error in pattern detection loop: {e}")
    
    async def _load_scheduled_workflows(self) -> None:
        """Load and schedule workflows that have time-based triggers"""
        # This would load from persistent storage and set up cron-like scheduling
        self.logger.info("Scheduled workflows loaded")
    
    async def _handle_user_login(self, data: Dict[str, Any]) -> None:
        """Handle user login events"""
        user_id = data.get('user_id')
        if user_id:
            self.current_user_id = user_id
            
            # Initialize user data if new user
            if user_id not in self.user_preferences:
                self.user_preferences[user_id] = []
                self.user_workflows[user_id] = []
                self.user_patterns[user_id] = {}
                self.workflow_suggestions[user_id] = []
                self.user_interactions[user_id] = []
            
            # Load user's active workflows
            await self._load_user_workflows(user_id)
            
            self.logger.info(f"User {user_id} session started")
    
    async def _handle_user_logout(self, data: Dict[str, Any]) -> None:
        """Handle user logout events"""
        user_id = data.get('user_id')
        if user_id == self.current_user_id and user_id:
            # Save user data and clean up active workflows
            await self._save_user_data(user_id)
            await self._cleanup_user_workflows(user_id)
            
            self.current_user_id = None
            self.logger.info(f"User {user_id} session ended")
    
    async def _handle_create_workflow(self, data: Dict[str, Any]) -> None:
        """Handle custom workflow creation requests"""
        user_id = data.get('user_id', self.current_user_id)
        if not user_id:
            self.logger.error("No user ID provided for workflow creation")
            return
        
        workflow_data = data.get('workflow')
        if not workflow_data:
            self.logger.error("No workflow data provided")
            return
        
        try:
            # Create custom workflow
            workflow = CustomWorkflow(
                workflow_id=workflow_data.get('workflow_id', f"user_{user_id}_{datetime.now().timestamp()}"),
                user_id=user_id,
                workflow_name=workflow_data.get('workflow_name', 'Untitled Workflow'),
                description=workflow_data.get('description', ''),
                trigger_type=WorkflowTriggerType(workflow_data.get('trigger_type', 'manual')),
                trigger_config=workflow_data.get('trigger_config', {}),
                steps=workflow_data.get('steps', []),
                complexity=WorkflowComplexity(workflow_data.get('complexity', 'simple')),
                tags=workflow_data.get('tags', [])
            )
            
            # Add to user's workflows
            if user_id not in self.user_workflows:
                self.user_workflows[user_id] = []
            
            self.user_workflows[user_id].append(workflow)
            
            # If scheduled, set up scheduling
            if workflow.trigger_type == WorkflowTriggerType.SCHEDULED:
                await self._schedule_workflow(workflow)
            
            # Emit success event
            self.event_bus.emit("ai.user.workflow_created", {
                "user_id": user_id,
                "workflow_id": workflow.workflow_id,
                "workflow_name": workflow.workflow_name,
                "success": True
            })
            
            self.logger.info(f"Created workflow {workflow.workflow_name} for user {user_id}")
            
        except Exception as e:
            self.logger.error(f"Error creating workflow: {e}")
            self.event_bus.emit("ai.user.workflow_created", {
                "user_id": user_id,
                "success": False,
                "error": str(e)
            })
    
    async def _handle_execute_workflow(self, data: Dict[str, Any]) -> None:
        """Handle workflow execution requests"""
        user_id = data.get('user_id', self.current_user_id)
        workflow_id = data.get('workflow_id')
        parameters = data.get('parameters', {})
        
        if not user_id or not workflow_id:
            self.logger.error("Missing user_id or workflow_id for execution")
            return
        
        # Find the workflow
        workflow = self._find_user_workflow(user_id, workflow_id)
        if not workflow:
            self.logger.error(f"Workflow {workflow_id} not found for user {user_id}")
            return
        
        # Execute the workflow
        await self._execute_custom_workflow(workflow, parameters)
    
    async def _execute_custom_workflow(self, workflow: CustomWorkflow, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a custom user workflow"""
        try:
            workflow.last_executed = datetime.now()
            workflow.total_executions += 1
            
            # Start execution
            execution_id = f"{workflow.workflow_id}_{datetime.now().timestamp()}"
            
            self.event_bus.emit("ai.user.workflow_started", {
                "execution_id": execution_id,
                "workflow_id": workflow.workflow_id,
                "user_id": workflow.user_id,
                "workflow_name": workflow.workflow_name
            })
            
            results = []
            success = True
            
            # Execute each step
            for i, step in enumerate(workflow.steps):
                try:
                    step_result = await self._execute_workflow_step(workflow, step, parameters, i)
                    results.append(step_result)
                    
                    if not step_result.get('success', False):
                        success = False
                        break
                        
                except Exception as e:
                    self.logger.error(f"Error in workflow step {i}: {e}")
                    results.append({"success": False, "error": str(e), "step": i})
                    success = False
                    break
            
            # Update workflow statistics
            if success:
                workflow.successful_executions += 1
            
            workflow.success_rate = workflow.successful_executions / workflow.total_executions
            
            # Store execution result
            execution_result = {
                "execution_id": execution_id,
                "workflow_id": workflow.workflow_id,
                "user_id": workflow.user_id,
                "success": success,
                "results": results,
                "execution_time": datetime.now().isoformat(),
                "parameters": parameters
            }
            
            # Emit completion event
            self.event_bus.emit("ai.user.workflow_completed", execution_result)
            
            # Learn from execution for future suggestions
            await self._learn_from_execution(workflow, execution_result)
            
            return execution_result
            
        except Exception as e:
            self.logger.error(f"Error executing workflow {workflow.workflow_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_workflow_step(self, workflow: CustomWorkflow, step: Dict[str, Any], 
                                   parameters: Dict[str, Any], step_index: int) -> Dict[str, Any]:
        """Execute a single step of a custom workflow"""
        step_type = step.get('type', 'action')
        step_config = step.get('config', {})
        
        # Merge parameters
        merged_params = {**step_config, **parameters}
        
        try:
            if step_type == 'action':
                return await self._execute_action_step(step, merged_params)
            elif step_type == 'condition':
                return await self._execute_condition_step(step, merged_params)
            elif step_type == 'delay':
                return await self._execute_delay_step(step, merged_params)
            elif step_type == 'emit_event':
                return await self._execute_event_step(step, merged_params)
            elif step_type == 'call_addon':
                return await self._execute_addon_step(step, merged_params)
            else:
                return {"success": False, "error": f"Unknown step type: {step_type}"}
                
        except Exception as e:
            return {"success": False, "error": str(e), "step_index": step_index}
    
    async def _execute_action_step(self, step: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action step"""
        action = step.get('action')
        
        # Emit event for the action
        self.event_bus.emit(f"ai.user.action.{action}", {
            "step": step,
            "parameters": params,
            "timestamp": datetime.now().isoformat()
        })
        
        # For now, simulate successful execution
        return {"success": True, "action": action, "params": params}
    
    async def _execute_condition_step(self, step: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a condition step"""
        condition = step.get('condition')
        
        # Evaluate condition (simplified)
        # In real implementation, this would evaluate complex conditions
        result = True  # Placeholder
        
        return {"success": True, "condition": condition, "result": result}
    
    async def _execute_delay_step(self, step: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a delay step"""
        delay_seconds = step.get('delay', 1)
        await asyncio.sleep(delay_seconds)
        
        return {"success": True, "delayed": delay_seconds}
    
    async def _execute_event_step(self, step: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an event emission step"""
        event_name = step.get('event')
        event_data = step.get('data', {})
        
        if event_name:
            self.event_bus.emit(event_name, {**event_data, **params})
            return {"success": True, "event": event_name}
        else:
            return {"success": False, "error": "No event name provided"}
    
    async def _execute_addon_step(self, step: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an addon call step"""
        addon_name = step.get('addon')
        addon_action = step.get('addon_action')
        
        # Emit event to addon logic
        self.event_bus.emit(f"ai.addon.{addon_name}.{addon_action}", {
            "parameters": params,
            "from_user_workflow": True
        })
        
        return {"success": True, "addon": addon_name, "action": addon_action}
    
    async def _handle_set_preference(self, data: Dict[str, Any]) -> None:
        """Handle user preference setting"""
        user_id = data.get('user_id', self.current_user_id)
        if not user_id:
            return
        
        preference = UserPreference(
            preference_id=data.get('preference_id', f"pref_{datetime.now().timestamp()}"),
            category=data.get('category', 'general'),
            preference_key=data.get('key', 'unknown'),
            preference_value=data.get('value'),
            confidence_level=1.0,  # Manually set preferences have high confidence
            learned_from='manual'
        )
        
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = []
        
        # Update existing or add new
        existing = next((p for p in self.user_preferences[user_id] 
                        if p.preference_key == preference.preference_key), None)
        
        if existing:
            existing.preference_value = preference.preference_value
            existing.updated_at = datetime.now()
        else:
            self.user_preferences[user_id].append(preference)
        
        self.logger.info(f"Set preference {preference.preference_key} for user {user_id}")
    
    async def _handle_get_preferences(self, data: Dict[str, Any]) -> None:
        """Handle preference retrieval requests"""
        user_id = data.get('user_id', self.current_user_id)
        category = data.get('category')
        
        if not user_id or user_id not in self.user_preferences:
            preferences = []
        else:
            preferences = self.user_preferences[user_id]
            if category:
                preferences = [p for p in preferences if p.category == category]
        
        response = {
            "user_id": user_id,
            "category": category,
            "preferences": [
                {
                    "key": p.preference_key,
                    "value": p.preference_value,
                    "category": p.category,
                    "confidence": p.confidence_level,
                    "learned_from": p.learned_from
                } for p in preferences
            ]
        }
        
        self.event_bus.emit("ai.user.preferences_response", response)
    
    async def _handle_user_interaction(self, data: Dict[str, Any]) -> None:
        """Handle user interaction tracking for learning"""
        user_id = data.get('user_id', self.current_user_id)
        if not user_id:
            return
        
        # Record interaction
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "type": data.get('interaction_type'),
            "context": data.get('context', {}),
            "data": data
        }
        
        if user_id not in self.user_interactions:
            self.user_interactions[user_id] = []
        
        self.user_interactions[user_id].append(interaction)
        
        # Trigger pattern analysis if in learning mode
        if self.learning_mode:
            await self._analyze_interaction_patterns(user_id, interaction)
    
    async def _analyze_user_patterns(self, user_id: str) -> None:
        """Analyze user behavior patterns for workflow suggestions"""
        if user_id not in self.user_interactions:
            return
        
        interactions = self.user_interactions[user_id]
        
        # Analyze patterns (simplified implementation)
        patterns = {
            "frequent_actions": {},
            "time_patterns": {},
            "sequence_patterns": [],
            "context_patterns": {}
        }
        
        # Analyze frequent actions
        for interaction in interactions[-100:]:  # Last 100 interactions
            action = interaction.get('type')
            if action:
                patterns["frequent_actions"][action] = patterns["frequent_actions"].get(action, 0) + 1
        
        # Store patterns
        self.user_patterns[user_id] = patterns
        
        self.logger.info(f"Analyzed patterns for user {user_id}")
    
    async def _generate_workflow_suggestions(self, user_id: str) -> None:
        """Generate workflow suggestions based on user patterns"""
        if user_id not in self.user_patterns:
            return
        
        patterns = self.user_patterns[user_id]
        frequent_actions = patterns.get("frequent_actions", {})
        
        # Generate suggestions based on frequent actions
        suggestions = []
        
        for action, count in frequent_actions.items():
            if count >= 5:  # Threshold for suggestion
                suggestion = WorkflowSuggestion(
                    suggestion_id=f"suggestion_{user_id}_{action}_{datetime.now().timestamp()}",
                    user_id=user_id,
                    suggested_workflow={
                        "workflow_name": f"Automated {action.replace('_', ' ').title()}",
                        "description": f"Automate the {action} action based on your usage patterns",
                        "trigger_type": "pattern_detection",
                        "steps": [
                            {
                                "type": "action",
                                "action": action,
                                "config": {}
                            }
                        ]
                    },
                    confidence=min(0.9, count / 20),  # Higher frequency = higher confidence
                    reasoning=f"You've performed this action {count} times recently",
                    based_on_patterns=[action]
                )
                
                if suggestion.confidence >= self.suggestion_threshold:
                    suggestions.append(suggestion)
        
        # Store suggestions
        if user_id not in self.workflow_suggestions:
            self.workflow_suggestions[user_id] = []
        
        self.workflow_suggestions[user_id].extend(suggestions)
        
        # Emit suggestions event
        if suggestions:
            self.event_bus.emit("ai.user.suggestions_generated", {
                "user_id": user_id,
                "suggestions_count": len(suggestions),
                "suggestions": [
                    {
                        "id": s.suggestion_id,
                        "workflow_name": s.suggested_workflow["workflow_name"],
                        "confidence": s.confidence,
                        "reasoning": s.reasoning
                    } for s in suggestions
                ]
            })
            
            self.logger.info(f"Generated {len(suggestions)} suggestions for user {user_id}")
    
    async def _handle_get_suggestions(self, data: Dict[str, Any]) -> None:
        """Handle suggestion retrieval requests"""
        user_id = data.get('user_id', self.current_user_id)
        
        if not user_id or user_id not in self.workflow_suggestions:
            suggestions = []
        else:
            suggestions = self.workflow_suggestions[user_id]
            # Filter by confidence if requested
            min_confidence = data.get('min_confidence', self.suggestion_threshold)
            suggestions = [s for s in suggestions if s.confidence >= min_confidence]
        
        response = {
            "user_id": user_id,
            "suggestions": [
                {
                    "id": s.suggestion_id,
                    "workflow": s.suggested_workflow,
                    "confidence": s.confidence,
                    "reasoning": s.reasoning,
                    "created_at": s.created_at.isoformat() if s.created_at else datetime.now().isoformat()
                } for s in suggestions
            ]
        }
        
        self.event_bus.emit("ai.user.suggestions_response", response)
    
    async def _handle_suggestion_feedback(self, data: Dict[str, Any]) -> None:
        """Handle user feedback on workflow suggestions"""
        user_id = data.get('user_id', self.current_user_id)
        suggestion_id = data.get('suggestion_id')
        feedback = data.get('feedback')  # 'accepted', 'rejected', 'modified'
        
        if not user_id or not suggestion_id:
            return
        
        # Find and update suggestion
        suggestions = self.workflow_suggestions.get(user_id, [])
        suggestion = next((s for s in suggestions if s.suggestion_id == suggestion_id), None)
        
        if suggestion:
            suggestion.user_feedback = feedback
            
            # If accepted, create the workflow
            if feedback == 'accepted':
                await self._create_workflow_from_suggestion(user_id, suggestion)
            
            self.logger.info(f"Recorded feedback '{feedback}' for suggestion {suggestion_id}")
    
    async def _create_workflow_from_suggestion(self, user_id: str, suggestion: WorkflowSuggestion) -> None:
        """Create a workflow from an accepted suggestion"""
        workflow_data = suggestion.suggested_workflow
        workflow_data['workflow_id'] = f"from_suggestion_{suggestion.suggestion_id}"
        
        await self._handle_create_workflow({
            'user_id': user_id,
            'workflow': workflow_data
        })
    
    async def _handle_voice_command(self, data: Dict[str, Any]) -> None:
        """Handle voice command detection"""
        if not self.voice_enabled:
            return
        
        command_text = data.get('command_text', '').lower()
        user_id = data.get('user_id', self.current_user_id)
        
        # Find matching voice command
        workflow_id = None
        for phrase, wf_id in self.voice_commands.items():
            if phrase.lower() in command_text:
                workflow_id = wf_id
                break
        
        if workflow_id and user_id:
            # Execute the workflow
            await self._handle_execute_workflow({
                'user_id': user_id,
                'workflow_id': workflow_id,
                'parameters': {'trigger': 'voice_command', 'command_text': command_text}
            })
        else:
            self.logger.info(f"No workflow found for voice command: {command_text}")
    
    async def _handle_register_voice_command(self, data: Dict[str, Any]) -> None:
        """Handle voice command registration"""
        workflow_id = data.get('workflow_id')
        voice_phrase = data.get('voice_phrase')
        
        if workflow_id and voice_phrase:
            self.voice_commands[voice_phrase] = workflow_id
            self.logger.info(f"Registered voice command '{voice_phrase}' for workflow {workflow_id}")
    
    def _find_user_workflow(self, user_id: str, workflow_id: str) -> Optional[CustomWorkflow]:
        """Find a user's workflow by ID"""
        workflows = self.user_workflows.get(user_id, [])
        return next((w for w in workflows if w.workflow_id == workflow_id), None)
    
    async def _handle_resource_strain(self, data: Dict[str, Any]) -> None:
        """Handle resource strain notifications"""
        strain_level = data.get('strain_level', 'unknown')
        
        if strain_level in ['high', 'critical']:
            # Pause complex workflows
            await self._pause_complex_workflows()
        
        self.event_bus.emit("ai.user.resource_response", {
            "compartment": "user_logic",
            "strain_level": strain_level,
            "action": "paused_complex_workflows",
            "current_user": self.current_user_id,
            "timestamp": datetime.now().isoformat()
        })
    
    async def _pause_complex_workflows(self) -> None:
        """Pause complex workflows during resource strain"""
        if not self.current_user_id:
            return
        
        workflows = self.user_workflows.get(self.current_user_id, [])
        for workflow in workflows:
            if workflow.complexity in [WorkflowComplexity.ADVANCED, WorkflowComplexity.EXPERT]:
                workflow.is_active = False
                self.logger.info(f"Paused complex workflow: {workflow.workflow_name}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of User AI Logic compartment"""
        user_stats = {}
        if self.current_user_id:
            user_stats = {
                "workflows_count": len(self.user_workflows.get(self.current_user_id, [])),
                "preferences_count": len(self.user_preferences.get(self.current_user_id, [])),
                "suggestions_count": len(self.workflow_suggestions.get(self.current_user_id, [])),
                "interactions_count": len(self.user_interactions.get(self.current_user_id, []))
            }
        
        return {
            "compartment": "user_logic",
            "is_initialized": self.is_initialized,
            "is_running": self.is_running,
            "current_user": self.current_user_id,
            "learning_mode": self.learning_mode,
            "pattern_detection": self.pattern_detection_enabled,
            "voice_enabled": self.voice_enabled,
            "total_users": len(self.user_preferences),
            "user_stats": user_stats,
            "running_workflows": len(self.running_workflows)
        }
    
    async def shutdown(self) -> bool:
        """Shutdown the User AI Logic compartment"""
        try:
            self.is_running = False
            self.pattern_detection_enabled = False
            
            # Save user data
            if self.current_user_id:
                await self._save_user_data(self.current_user_id)
            
            # Cancel running workflows
            for task in self.running_workflows.values():
                task.cancel()
            
            self.running_workflows.clear()
            
            # Emit shutdown event
            self.event_bus.emit("ai.user_logic.shutdown", {
                "compartment": "user_logic",
                "timestamp": datetime.now().isoformat()
            })
            
            self.logger.info("User AI Logic compartment shutdown successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during User AI Logic shutdown: {e}")
            return False
    
    # Helper methods for data persistence (placeholders)
    async def _load_user_workflows(self, user_id: str) -> None:
        """Load user workflows from persistent storage"""
        pass
    
    async def _save_user_data(self, user_id: str) -> None:
        """Save user data to persistent storage"""
        pass
    
    async def _cleanup_user_workflows(self, user_id: str) -> None:
        """Clean up active workflows for a user"""
        pass
    
    async def _schedule_workflow(self, workflow: CustomWorkflow) -> None:
        """Set up scheduling for a time-based workflow"""
        pass
    
    async def _learn_from_execution(self, workflow: CustomWorkflow, result: Dict[str, Any]) -> None:
        """Learn from workflow execution results"""
        pass
    
    async def _analyze_interaction_patterns(self, user_id: str, interaction: Dict[str, Any]) -> None:
        """Analyze individual interaction for patterns"""
        pass
