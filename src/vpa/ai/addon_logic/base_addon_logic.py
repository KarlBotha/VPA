"""
Base Addon Logic

Base class for all individual addon logic compartments.
Provides common functionality and interface for addon implementations.
"""

import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass
from abc import ABC, abstractmethod

from ...core.events import EventBus
from ...core.logging import get_structured_logger

@dataclass
class AddonWorkflow:
    """Represents an addon-specific workflow"""
    workflow_id: str
    addon_name: str
    workflow_name: str
    description: str
    steps: List[Dict[str, Any]]
    triggers: List[str]
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_executed: Optional[datetime] = None
    execution_count: int = 0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class AddonCapability:
    """Represents a capability provided by an addon"""
    capability_id: str
    addon_name: str
    capability_type: str
    description: str
    parameters: Dict[str, Any]
    dependencies: Optional[List[str]] = None
    is_enabled: bool = True

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class BaseAddonLogic(ABC):
    """
    Base class for all addon logic compartments.
    
    Each addon must extend this class and implement the abstract methods.
    Provides standardized interface and common functionality.
    """
    
    def __init__(self, event_bus: EventBus, config: Optional[Dict[str, Any]] = None):
        """Initialize base addon logic"""
        self.event_bus = event_bus
        self.config = config or {}
        self.addon_name = self._get_addon_name()
        self.logger = get_structured_logger(f"{__name__}.{self.__class__.__name__}")
        
        # Workflow and capability management
        self.workflows: List[AddonWorkflow] = []
        self.capabilities: List[AddonCapability] = []
        self.running_workflows: Dict[str, AddonWorkflow] = {}
        self.workflow_results: Dict[str, Dict[str, Any]] = {}
        
        # State management
        self.is_initialized = False
        self.is_active = False
        self.is_running = False
        
        self.logger.info(f"{self.addon_name} addon logic created")
    
    @abstractmethod
    def _get_addon_name(self) -> str:
        """Return the addon name (e.g., 'google', 'microsoft')"""
        pass
    
    @abstractmethod
    async def _register_workflows(self) -> None:
        """Register addon-specific workflows"""
        pass
    
    @abstractmethod
    async def _register_capabilities(self) -> None:
        """Register addon-specific capabilities"""
        pass
    
    @abstractmethod
    async def _register_event_handlers(self) -> None:
        """Register addon-specific event handlers"""
        pass
    
    @abstractmethod
    async def _execute_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute addon-specific action"""
        pass
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialize the addon logic"""
        try:
            if self.is_initialized:
                self.logger.warning(f"{self.addon_name} addon logic already initialized")
                return {"success": True, "message": "Already initialized"}
            
            # Register workflows, capabilities, and event handlers
            await self._register_workflows()
            await self._register_capabilities()
            await self._register_event_handlers()
            
            # Register common event handlers
            await self._register_common_event_handlers()
            
            self.is_initialized = True
            self.logger.info(f"{self.addon_name} addon logic initialized successfully")
            return {
                "success": True,
                "addon_name": self.addon_name,
                "workflows_count": len(self.workflows),
                "capabilities_count": len(self.capabilities)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.addon_name} addon logic: {e}")
            return {"success": False, "error": str(e)}
    
    async def _register_common_event_handlers(self) -> None:
        """Register common event handlers for all addons"""
        # Addon lifecycle events
        self.event_bus.subscribe(f"addon.{self.addon_name}.activate", self._handle_activate)
        self.event_bus.subscribe(f"addon.{self.addon_name}.deactivate", self._handle_deactivate)
        
        # Workflow execution events
        self.event_bus.subscribe(f"ai.addon.{self.addon_name}.execute_workflow", self._handle_execute_workflow)
        self.event_bus.subscribe(f"ai.addon.{self.addon_name}.query_capabilities", self._handle_query_capabilities)
        
        # Resource monitoring
        self.event_bus.subscribe("resource.strain.detected", self._handle_resource_strain)
    
    async def _handle_activate(self, data: Dict[str, Any]) -> None:
        """Handle addon activation"""
        if not self.is_active:
            self.is_active = True
            self.is_running = True
            
            # Emit activation event
            self.event_bus.emit(f"ai.addon.{self.addon_name}.activated", {
                "addon_name": self.addon_name,
                "workflows_count": len(self.workflows),
                "capabilities_count": len(self.capabilities),
                "timestamp": datetime.now().isoformat()
            })
            
            self.logger.info(f"{self.addon_name} addon activated")
    
    async def _handle_deactivate(self, data: Dict[str, Any]) -> None:
        """Handle addon deactivation"""
        if self.is_active:
            self.is_active = False
            self.is_running = False
            
            # Stop running workflows
            await self._stop_all_workflows()
            
            # Emit deactivation event
            self.event_bus.emit(f"ai.addon.{self.addon_name}.deactivated", {
                "addon_name": self.addon_name,
                "timestamp": datetime.now().isoformat()
            })
            
            self.logger.info(f"{self.addon_name} addon deactivated")
    
    async def _handle_execute_workflow(self, data: Dict[str, Any]) -> None:
        """Handle workflow execution requests"""
        workflow_name = data.get('workflow_name')
        parameters = data.get('parameters', {})
        
        if not self.is_active:
            self.logger.error(f"Cannot execute workflow for inactive {self.addon_name} addon")
            return
        
        # Find the workflow
        workflow = None
        for wf in self.workflows:
            if wf.workflow_name == workflow_name or wf.workflow_id == workflow_name:
                workflow = wf
                break
        
        if workflow:
            await self._execute_workflow(workflow, parameters)
        else:
            self.logger.error(f"Workflow not found: {workflow_name} for {self.addon_name} addon")
    
    async def _execute_workflow(self, workflow: AddonWorkflow, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an addon workflow"""
        try:
            workflow.last_executed = datetime.now()
            workflow.execution_count += 1
            
            self.running_workflows[workflow.workflow_id] = workflow
            
            # Emit workflow started event
            self.event_bus.emit(f"ai.addon.{self.addon_name}.workflow_started", {
                "workflow_id": workflow.workflow_id,
                "workflow_name": workflow.workflow_name,
                "addon_name": self.addon_name
            })
            
            results = []
            success = True
            
            # Execute each step
            for i, step in enumerate(workflow.steps):
                try:
                    step_result = await self._execute_workflow_step(step, parameters, i)
                    results.append(step_result)
                    
                    if not step_result.get('success', False):
                        success = False
                        break
                        
                except Exception as e:
                    self.logger.error(f"Error in workflow step {i}: {e}")
                    results.append({"success": False, "error": str(e), "step": i})
                    success = False
                    break
            
            # Store results
            execution_result = {
                "success": success,
                "workflow": workflow.workflow_name,
                "addon": self.addon_name,
                "results": results,
                "executed_at": workflow.last_executed.isoformat()
            }
            
            self.workflow_results[workflow.workflow_id] = execution_result
            
            # Remove from running workflows
            if workflow.workflow_id in self.running_workflows:
                del self.running_workflows[workflow.workflow_id]
            
            # Emit completion event
            self.event_bus.emit(f"ai.addon.{self.addon_name}.workflow_completed", execution_result)
            
            return execution_result
            
        except Exception as e:
            self.logger.error(f"Error executing {self.addon_name} workflow {workflow.workflow_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_workflow_step(self, step: Dict[str, Any], parameters: Dict[str, Any], step_index: int) -> Dict[str, Any]:
        """Execute a single workflow step"""
        action = step.get('action', '')
        step_params = {**step.get('params', {}), **parameters}
        
        try:
            return await self._execute_action(action, step_params)
        except Exception as e:
            return {"success": False, "error": str(e), "step_index": step_index}
    
    async def _handle_query_capabilities(self, data: Dict[str, Any]) -> None:
        """Handle capability query requests"""
        response = {
            "addon_name": self.addon_name,
            "capabilities": [
                {
                    "id": cap.capability_id,
                    "type": cap.capability_type,
                    "description": cap.description,
                    "enabled": cap.is_enabled,
                    "parameters": cap.parameters
                } for cap in self.capabilities
            ]
        }
        
        self.event_bus.emit(f"ai.addon.{self.addon_name}.capabilities_response", response)
    
    async def _handle_resource_strain(self, data: Dict[str, Any]) -> None:
        """Handle resource strain notifications"""
        strain_level = data.get('strain_level', 'unknown')
        
        if strain_level in ['high', 'critical']:
            # Pause non-critical workflows
            await self._pause_non_critical_workflows()
        
        self.event_bus.emit(f"ai.addon.{self.addon_name}.resource_response", {
            "addon_name": self.addon_name,
            "strain_level": strain_level,
            "action": "paused_non_critical_workflows",
            "timestamp": datetime.now().isoformat()
        })
    
    async def _pause_non_critical_workflows(self) -> None:
        """Pause non-critical workflows during resource strain"""
        # Implementation can be overridden by specific addons
        pass
    
    async def _stop_all_workflows(self) -> None:
        """Stop all running workflows"""
        for workflow_id in list(self.running_workflows.keys()):
            if workflow_id in self.running_workflows:
                del self.running_workflows[workflow_id]
                self.logger.info(f"Stopped workflow {workflow_id}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the addon"""
        return {
            "addon_name": self.addon_name,
            "is_initialized": self.is_initialized,
            "is_active": self.is_active,
            "is_running": self.is_running,
            "workflows_count": len(self.workflows),
            "capabilities_count": len(self.capabilities),
            "running_workflows": len(self.running_workflows)
        }
    
    async def shutdown(self) -> bool:
        """Shutdown the addon logic"""
        try:
            self.is_running = False
            self.is_active = False
            
            # Stop all workflows
            await self._stop_all_workflows()
            
            # Emit shutdown event
            self.event_bus.emit(f"ai.addon.{self.addon_name}.shutdown", {
                "addon_name": self.addon_name,
                "timestamp": datetime.now().isoformat()
            })
            
            self.logger.info(f"{self.addon_name} addon logic shutdown successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during {self.addon_name} addon shutdown: {e}")
            return False
