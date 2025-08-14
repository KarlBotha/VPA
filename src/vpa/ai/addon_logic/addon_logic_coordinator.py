"""
Addon Logic Coordinator

Central coordinator for managing all addon logic compartments.
Provides a unified interface for loading, registering, and orchestrating addon operations.

This coordinator maintains complete isolation between addons while providing centralized management.
"""

from typing import Dict, Any, List, Optional, Type
from datetime import datetime
import asyncio
import importlib

from .base_addon_logic import BaseAddonLogic, AddonWorkflow, AddonCapability
from ...core.events import EventBus
from ...core.logging import get_structured_logger

# Import all addon logic classes
from .google_logic import GoogleAddonLogic
from .microsoft_logic import MicrosoftAddonLogic
from .whatsapp_logic import WhatsAppAddonLogic
from .telegram_logic import TelegramAddonLogic
from .discord_logic import DiscordAddonLogic
from .weather_logic import WeatherAddonLogic
from .windows_logic import WindowsAddonLogic
from .websearch_logic import WebSearchAddonLogic

class AddonLogicCoordinator:
    """
    Central Coordinator for Addon Logic Compartments
    
    Manages the lifecycle and operations of all addon compartments:
    - Loading and initialization of addon logic modules
    - Registration of workflows and capabilities
    - Orchestration of cross-addon operations
    - Monitoring and health checks
    """
    
    def __init__(self, event_bus: EventBus):
        """Initialize the addon logic coordinator"""
        self.event_bus = event_bus
        self.logger = get_structured_logger(__name__)
        
        # Registry of all addon logic instances
        self.addon_instances: Dict[str, BaseAddonLogic] = {}
        
        # Registry of available addon classes
        self.addon_classes: Dict[str, Type[BaseAddonLogic]] = {
            "google": GoogleAddonLogic,
            "microsoft": MicrosoftAddonLogic,
            "whatsapp": WhatsAppAddonLogic,
            "telegram": TelegramAddonLogic,
            "discord": DiscordAddonLogic,
            "weather": WeatherAddonLogic,
            "windows": WindowsAddonLogic,
            "websearch": WebSearchAddonLogic
        }
        
        # Centralized registries
        self.all_workflows: Dict[str, AddonWorkflow] = {}
        self.all_capabilities: Dict[str, AddonCapability] = {}
        
        # Configuration and state
        self.enabled_addons: List[str] = []
        self.initialization_status: Dict[str, bool] = {}
        self.health_status: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("AddonLogicCoordinator initialized")
    
    async def initialize_coordinator(self, enabled_addons: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Initialize the coordinator and load enabled addons
        
        Args:
            enabled_addons: List of addon names to enable. If None, all addons are enabled.
            
        Returns:
            Dict containing initialization results
        """
        try:
            # Determine which addons to enable
            if enabled_addons is None:
                self.enabled_addons = list(self.addon_classes.keys())
            else:
                self.enabled_addons = [addon for addon in enabled_addons if addon in self.addon_classes]
            
            self.logger.info(f"Initializing coordinator with {len(self.enabled_addons)} addons")
            
            # Initialize each enabled addon
            initialization_results = {}
            for addon_name in self.enabled_addons:
                try:
                    result = await self._initialize_addon(addon_name)
                    initialization_results[addon_name] = result
                    self.initialization_status[addon_name] = result["success"]
                except Exception as e:
                    self.logger.error(f"Failed to initialize addon {addon_name}: {e}")
                    initialization_results[addon_name] = {"success": False, "error": str(e)}
                    self.initialization_status[addon_name] = False
            
            # Register coordinator event handlers
            await self._register_coordinator_events()
            
            # Perform initial health check
            await self._perform_health_check()
            
            return {
                "success": True,
                "coordinator_initialized": True,
                "enabled_addons": self.enabled_addons,
                "initialization_results": initialization_results,
                "total_workflows": len(self.all_workflows),
                "total_capabilities": len(self.all_capabilities),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initialize coordinator: {e}")
            return {"success": False, "error": str(e)}
    
    async def _initialize_addon(self, addon_name: str) -> Dict[str, Any]:
        """Initialize a specific addon"""
        try:
            addon_class = self.addon_classes[addon_name]
            
            # Create addon instance
            addon_instance = addon_class(self.event_bus)
            
            # Initialize the addon
            init_result = await addon_instance.initialize()
            
            if isinstance(init_result, dict) and init_result.get("success", False):
                # Store the instance
                self.addon_instances[addon_name] = addon_instance
                
                # Register workflows and capabilities in central registries
                await self._register_addon_workflows(addon_name, addon_instance)
                await self._register_addon_capabilities(addon_name, addon_instance)
                
                self.logger.info(f"Successfully initialized addon: {addon_name}")
                return {
                    "success": True,
                    "addon_name": addon_name,
                    "workflows_registered": len(addon_instance.workflows),
                    "capabilities_registered": len(addon_instance.capabilities)
                }
            else:
                error_msg = "Unknown error"
                if isinstance(init_result, dict):
                    error_msg = init_result.get('error', 'Unknown error')
                self.logger.error(f"Failed to initialize addon {addon_name}: {error_msg}")
                return {"success": False, "error": error_msg}
                
        except Exception as e:
            self.logger.error(f"Exception initializing addon {addon_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _register_addon_workflows(self, addon_name: str, addon_instance: BaseAddonLogic) -> None:
        """Register workflows from an addon in the central registry"""
        for workflow in addon_instance.workflows:
            workflow_key = f"{addon_name}.{workflow.workflow_id}"
            self.all_workflows[workflow_key] = workflow
        
        self.logger.info(f"Registered {len(addon_instance.workflows)} workflows for addon {addon_name}")
    
    async def _register_addon_capabilities(self, addon_name: str, addon_instance: BaseAddonLogic) -> None:
        """Register capabilities from an addon in the central registry"""
        for capability in addon_instance.capabilities:
            capability_key = f"{addon_name}.{capability.capability_id}"
            self.all_capabilities[capability_key] = capability
        
        self.logger.info(f"Registered {len(addon_instance.capabilities)} capabilities for addon {addon_name}")
    
    async def _register_coordinator_events(self) -> None:
        """Register coordinator-level event handlers"""
        # Addon management events
        self.event_bus.subscribe("coordinator.enable_addon", self._handle_enable_addon)
        self.event_bus.subscribe("coordinator.disable_addon", self._handle_disable_addon)
        self.event_bus.subscribe("coordinator.restart_addon", self._handle_restart_addon)
        
        # Workflow orchestration events
        self.event_bus.subscribe("coordinator.execute_workflow", self._handle_execute_workflow)
        self.event_bus.subscribe("coordinator.list_workflows", self._handle_list_workflows)
        
        # Capability management events
        self.event_bus.subscribe("coordinator.list_capabilities", self._handle_list_capabilities)
        self.event_bus.subscribe("coordinator.check_capability", self._handle_check_capability)
        
        # Health and monitoring events
        self.event_bus.subscribe("coordinator.health_check", self._handle_health_check)
        self.event_bus.subscribe("coordinator.get_status", self._handle_get_status)
        
        self.logger.info("Coordinator event handlers registered")
    
    async def execute_workflow(self, workflow_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow by ID"""
        try:
            # Find the workflow
            workflow = None
            addon_name = None
            
            for key, wf in self.all_workflows.items():
                if wf.workflow_id == workflow_id or key == workflow_id:
                    workflow = wf
                    addon_name = key.split('.')[0]
                    break
            
            if not workflow:
                return {"success": False, "error": f"Workflow not found: {workflow_id}"}
            
            # Get the addon instance
            if addon_name is None:
                return {"success": False, "error": "Invalid addon name"}
                
            addon_instance = self.addon_instances.get(addon_name)
            if not addon_instance:
                return {"success": False, "error": f"Addon not initialized: {addon_name}"}
            
            # Execute the workflow by finding it and calling the internal method
            workflow_obj = None
            for wf in addon_instance.workflows:
                if wf.workflow_id == workflow_id:
                    workflow_obj = wf
                    break
            
            if not workflow_obj:
                return {"success": False, "error": f"Workflow {workflow_id} not found in addon {addon_name}"}
                
            result = await addon_instance._execute_workflow(workflow_obj, params)
            
            # Emit workflow execution event
            self.event_bus.emit("coordinator.workflow_executed", {
                "workflow_id": workflow_id,
                "addon_name": addon_name,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing workflow {workflow_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_addon_status(self, addon_name: str) -> Dict[str, Any]:
        """Get status of a specific addon"""
        if addon_name not in self.addon_instances:
            return {"success": False, "error": f"Addon not found: {addon_name}"}
        
        addon_instance = self.addon_instances[addon_name]
        
        return {
            "success": True,
            "addon_name": addon_name,
            "initialized": self.initialization_status.get(addon_name, False),
            "health_status": self.health_status.get(addon_name, {}),
            "workflows_count": len(addon_instance.workflows),
            "capabilities_count": len(addon_instance.capabilities),
            "last_activity": getattr(addon_instance, 'last_activity', None)
        }
    
    async def get_coordinator_status(self) -> Dict[str, Any]:
        """Get overall coordinator status"""
        total_addons = len(self.addon_classes)
        enabled_addons = len(self.enabled_addons)
        initialized_addons = sum(1 for status in self.initialization_status.values() if status)
        
        return {
            "success": True,
            "coordinator_status": "active",
            "total_addons_available": total_addons,
            "enabled_addons": enabled_addons,
            "initialized_addons": initialized_addons,
            "total_workflows": len(self.all_workflows),
            "total_capabilities": len(self.all_capabilities),
            "addon_status": {name: self.initialization_status.get(name, False) for name in self.enabled_addons},
            "health_status": self.health_status,
            "timestamp": datetime.now().isoformat()
        }
    
    async def list_workflows(self, addon_name: Optional[str] = None) -> Dict[str, Any]:
        """List workflows, optionally filtered by addon"""
        if addon_name:
            workflows = {k: v for k, v in self.all_workflows.items() if k.startswith(f"{addon_name}.")}
        else:
            workflows = self.all_workflows
        
        return {
            "success": True,
            "workflows": {
                k: {
                    "workflow_id": v.workflow_id,
                    "addon_name": v.addon_name,
                    "workflow_name": v.workflow_name,
                    "description": v.description,
                    "steps_count": len(v.steps),
                    "triggers": v.triggers
                }
                for k, v in workflows.items()
            },
            "total_count": len(workflows)
        }
    
    async def list_capabilities(self, addon_name: Optional[str] = None) -> Dict[str, Any]:
        """List capabilities, optionally filtered by addon"""
        if addon_name:
            capabilities = {k: v for k, v in self.all_capabilities.items() if k.startswith(f"{addon_name}.")}
        else:
            capabilities = self.all_capabilities
        
        return {
            "success": True,
            "capabilities": {
                k: {
                    "capability_id": v.capability_id,
                    "addon_name": v.addon_name,
                    "capability_type": v.capability_type,
                    "description": v.description,
                    "parameters": v.parameters
                }
                for k, v in capabilities.items()
            },
            "total_count": len(capabilities)
        }
    
    async def _perform_health_check(self) -> None:
        """Perform health check on all addons"""
        for addon_name, addon_instance in self.addon_instances.items():
            try:
                # Perform basic health check
                health_data = {
                    "status": "healthy",
                    "initialized": self.initialization_status.get(addon_name, False),
                    "workflows_count": len(addon_instance.workflows),
                    "capabilities_count": len(addon_instance.capabilities),
                    "last_check": datetime.now().isoformat()
                }
                
                self.health_status[addon_name] = health_data
                
            except Exception as e:
                self.logger.error(f"Health check failed for addon {addon_name}: {e}")
                self.health_status[addon_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.now().isoformat()
                }
    
    # Event handlers
    async def _handle_enable_addon(self, data: Dict[str, Any]) -> None:
        """Handle enable addon requests"""
        addon_name = data.get('addon_name')
        if addon_name and addon_name in self.addon_classes and addon_name not in self.enabled_addons:
            result = await self._initialize_addon(addon_name)
            if result["success"]:
                self.enabled_addons.append(addon_name)
            self.event_bus.emit("coordinator.addon_enabled", {"addon_name": addon_name, "result": result})
    
    async def _handle_disable_addon(self, data: Dict[str, Any]) -> None:
        """Handle disable addon requests"""
        addon_name = data.get('addon_name')
        if addon_name and addon_name in self.enabled_addons:
            # Remove from enabled list
            self.enabled_addons.remove(addon_name)
            # Clean up instance
            if addon_name in self.addon_instances:
                del self.addon_instances[addon_name]
            # Clean up status
            self.initialization_status.pop(addon_name, None)
            self.health_status.pop(addon_name, None)
            
            self.event_bus.emit("coordinator.addon_disabled", {"addon_name": addon_name})
    
    async def _handle_restart_addon(self, data: Dict[str, Any]) -> None:
        """Handle restart addon requests"""
        addon_name = data.get('addon_name')
        if addon_name:
            # Disable then enable
            await self._handle_disable_addon(data)
            await self._handle_enable_addon(data)
    
    async def _handle_execute_workflow(self, data: Dict[str, Any]) -> None:
        """Handle workflow execution requests"""
        workflow_id = data.get('workflow_id')
        params = data.get('params', {})
        
        if workflow_id is None:
            result = {"success": False, "error": "workflow_id is required"}
        else:
            result = await self.execute_workflow(workflow_id, params)
            
        self.event_bus.emit("coordinator.workflow_result", {"workflow_id": workflow_id, "result": result})
    
    async def _handle_list_workflows(self, data: Dict[str, Any]) -> None:
        """Handle list workflows requests"""
        addon_name = data.get('addon_name')
        result = await self.list_workflows(addon_name)
        self.event_bus.emit("coordinator.workflows_listed", result)
    
    async def _handle_list_capabilities(self, data: Dict[str, Any]) -> None:
        """Handle list capabilities requests"""
        addon_name = data.get('addon_name')
        result = await self.list_capabilities(addon_name)
        self.event_bus.emit("coordinator.capabilities_listed", result)
    
    async def _handle_check_capability(self, data: Dict[str, Any]) -> None:
        """Handle check capability requests"""
        capability_id = data.get('capability_id')
        result = {"success": capability_id in self.all_capabilities, "capability_id": capability_id}
        self.event_bus.emit("coordinator.capability_checked", result)
    
    async def _handle_health_check(self, data: Dict[str, Any]) -> None:
        """Handle health check requests"""
        await self._perform_health_check()
        result = {"success": True, "health_status": self.health_status}
        self.event_bus.emit("coordinator.health_checked", result)
    
    async def _handle_get_status(self, data: Dict[str, Any]) -> None:
        """Handle get status requests"""
        result = await self.get_coordinator_status()
        self.event_bus.emit("coordinator.status_retrieved", result)
    
    async def shutdown(self) -> Dict[str, Any]:
        """Shutdown the coordinator and all addons"""
        try:
            self.logger.info("Shutting down AddonLogicCoordinator")
            
            # Shutdown all addon instances
            shutdown_results = {}
            for addon_name, addon_instance in self.addon_instances.items():
                try:
                    if hasattr(addon_instance, 'shutdown'):
                        await addon_instance.shutdown()
                    shutdown_results[addon_name] = {"success": True}
                except Exception as e:
                    self.logger.error(f"Error shutting down addon {addon_name}: {e}")
                    shutdown_results[addon_name] = {"success": False, "error": str(e)}
            
            # Clear all registries
            self.addon_instances.clear()
            self.all_workflows.clear()
            self.all_capabilities.clear()
            self.enabled_addons.clear()
            self.initialization_status.clear()
            self.health_status.clear()
            
            return {
                "success": True,
                "coordinator_shutdown": True,
                "addon_shutdown_results": shutdown_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error during coordinator shutdown: {e}")
            return {"success": False, "error": str(e)}
