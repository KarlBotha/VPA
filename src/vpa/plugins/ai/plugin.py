"""
VPA AI Plugin
Connects AI logic system to core VPA application through plugin architecture
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from ...ai.addon_logic.addon_logic_coordinator import AddonLogicCoordinator
from ...core.events import EventBus


class AIPlugin:
    """
    AI Plugin for VPA System
    Integrates comprehensive AI logic capabilities with core application
    """
    
    def __init__(self, event_bus: EventBus):
        """Initialize AI plugin with event bus integration"""
        self.logger = logging.getLogger(__name__)
        self.event_bus = event_bus
        self.ai_coordinator: Optional[AddonLogicCoordinator] = None
        self.enabled_addons: List[str] = []
        self.plugin_name = "ai"
        
        # Plugin state
        self.is_initialized = False
        self.is_running = False
        
        self.logger.info("🧠 AI Plugin initialized")
    
    async def initialize(self) -> bool:
        """Initialize AI plugin and coordinator"""
        try:
            # Initialize AI coordinator
            self.ai_coordinator = AddonLogicCoordinator(self.event_bus)
            
            # Initialize the coordinator with default addons
            coordinator_result = await self.ai_coordinator.initialize_coordinator()
            
            if not coordinator_result.get("success", False):
                self.logger.error(f"❌ AI Coordinator initialization failed: {coordinator_result.get('error', 'Unknown error')}")
                return False
            
            # Store enabled addons from coordinator
            self.enabled_addons = coordinator_result.get("enabled_addons", [])
            
            # Register event handlers
            self._register_event_handlers()
            
            self.is_initialized = True
            self.logger.info("✅ AI Plugin initialization complete")
            
            # Log initialization results
            self.logger.info(f"📋 Enabled AI addons: {self.enabled_addons}")
            self.logger.info(f"📊 Total workflows: {coordinator_result.get('total_workflows', 0)}")
            self.logger.info(f"� Total capabilities: {coordinator_result.get('total_capabilities', 0)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ AI Plugin initialization failed: {e}")
            return False
    
    def start(self) -> bool:
        """Start AI plugin services"""
        if not self.is_initialized:
            self.logger.error("Cannot start AI plugin - not initialized")
            return False
        
        try:
            self.is_running = True
            self.logger.info("🚀 AI Plugin started successfully")
            
            # Emit startup event
            self.event_bus.emit("ai.plugin.started", {
                "enabled_addons": self.enabled_addons
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ AI Plugin start failed: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop AI plugin services"""
        try:
            self.is_running = False
            
            self.logger.info("⏹️ AI Plugin stopped successfully")
            
            # Emit shutdown event
            self.event_bus.emit("ai.plugin.stopped", {})
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ AI Plugin stop failed: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup AI plugin resources"""
        try:
            self.stop()
            
            # Shutdown coordinator
            if self.ai_coordinator:
                await self.ai_coordinator.shutdown()
                
            self.ai_coordinator = None
            self.enabled_addons.clear()
            self.logger.info("🧹 AI Plugin cleanup complete")
            
        except Exception as e:
            self.logger.error(f"❌ AI Plugin cleanup failed: {e}")
    
    def _register_event_handlers(self) -> None:
        """Register AI-related event handlers"""
        # AI task execution events
        self.event_bus.subscribe("ai.execute.workflow", self._handle_execute_workflow)
        self.event_bus.subscribe("ai.addon.enable", self._handle_enable_addon)
        self.event_bus.subscribe("ai.addon.disable", self._handle_disable_addon)
        self.event_bus.subscribe("ai.status.request", self._handle_status_request)
        self.event_bus.subscribe("ai.list.workflows", self._handle_list_workflows)
        self.event_bus.subscribe("ai.list.capabilities", self._handle_list_capabilities)
        
        self.logger.info("📡 AI event handlers registered")
    
    def _handle_execute_workflow(self, event_data: Dict[str, Any]) -> None:
        """Handle AI workflow execution event"""
        try:
            workflow_id = event_data.get("workflow_id", "")
            params = event_data.get("params", {})
            
            if not workflow_id:
                self.logger.warning("⚠️ AI workflow execution requested without workflow_id")
                return
            
            self.logger.info(f"🤖 Executing AI workflow: {workflow_id}")
            
            # Execute workflow through coordinator (async call)
            if self.ai_coordinator:
                # Create async task for workflow execution
                asyncio.create_task(self._execute_workflow_async(workflow_id, params))
            
        except Exception as e:
            self.logger.error(f"❌ AI workflow execution failed: {e}")
            
            # Emit failure event
            self.event_bus.emit("ai.workflow.completed", {
                "workflow_id": event_data.get("workflow_id", ""),
                "result": None,
                "success": False,
                "error": str(e)
            })
    
    async def _execute_workflow_async(self, workflow_id: str, params: Dict[str, Any]) -> None:
        """Execute workflow asynchronously"""
        try:
            if self.ai_coordinator:
                result = await self.ai_coordinator.execute_workflow(workflow_id, params)
                
                # Emit result event
                self.event_bus.emit("ai.workflow.completed", {
                    "workflow_id": workflow_id,
                    "params": params,
                    "result": result,
                    "success": result.get("success", False)
                })
            
        except Exception as e:
            self.logger.error(f"❌ Async workflow execution failed: {e}")
            
            # Emit failure event
            self.event_bus.emit("ai.workflow.completed", {
                "workflow_id": workflow_id,
                "result": None,
                "success": False,
                "error": str(e)
            })
    
    def _handle_enable_addon(self, event_data: Dict[str, Any]) -> None:
        """Handle addon enable event"""
        addon = event_data.get("addon", "")
        asyncio.create_task(self._enable_addon_async(addon))
    
    def _handle_disable_addon(self, event_data: Dict[str, Any]) -> None:
        """Handle addon disable event"""
        addon = event_data.get("addon", "")
        asyncio.create_task(self._disable_addon_async(addon))
    
    def _handle_status_request(self, event_data: Dict[str, Any]) -> None:
        """Handle AI status request event"""
        asyncio.create_task(self._get_status_async())
    
    def _handle_list_workflows(self, event_data: Dict[str, Any]) -> None:
        """Handle list workflows request"""
        addon_name = event_data.get("addon_name")
        asyncio.create_task(self._list_workflows_async(addon_name))
    
    def _handle_list_capabilities(self, event_data: Dict[str, Any]) -> None:
        """Handle list capabilities request"""
        addon_name = event_data.get("addon_name")
        asyncio.create_task(self._list_capabilities_async(addon_name))
    
    async def _enable_addon_async(self, addon_name: str) -> None:
        """Enable addon asynchronously"""
        try:
            if self.ai_coordinator:
                # Use event-based addon enabling
                self.event_bus.emit("coordinator.enable_addon", {"addon_name": addon_name})
                
                # Update local list if successful
                if addon_name not in self.enabled_addons:
                    self.enabled_addons.append(addon_name)
                
                self.logger.info(f"✅ Addon enable requested: {addon_name}")
                
                # Emit enable event
                self.event_bus.emit("ai.addon.enabled", {
                    "addon": addon_name,
                    "enabled_addons": self.enabled_addons.copy()
                })
                
        except Exception as e:
            self.logger.error(f"❌ Error enabling addon {addon_name}: {e}")
    
    async def _disable_addon_async(self, addon_name: str) -> None:
        """Disable addon asynchronously"""
        try:
            if self.ai_coordinator:
                # Use event-based addon disabling
                self.event_bus.emit("coordinator.disable_addon", {"addon_name": addon_name})
                
                # Update local list
                if addon_name in self.enabled_addons:
                    self.enabled_addons.remove(addon_name)
                
                self.logger.info(f"⏹️ Addon disable requested: {addon_name}")
                
                # Emit disable event
                self.event_bus.emit("ai.addon.disabled", {
                    "addon": addon_name,
                    "enabled_addons": self.enabled_addons.copy()
                })
                
        except Exception as e:
            self.logger.error(f"❌ Error disabling addon {addon_name}: {e}")
    
    async def _get_status_async(self) -> None:
        """Get AI status asynchronously"""
        try:
            if self.ai_coordinator:
                status = await self.ai_coordinator.get_coordinator_status()
                
                # Combine with plugin status
                full_status = {
                    "plugin_name": self.plugin_name,
                    "is_initialized": self.is_initialized,
                    "is_running": self.is_running,
                    "coordinator_available": True,
                    "coordinator_status": status
                }
                
                self.event_bus.emit("ai.status.response", full_status)
            else:
                # Coordinator not available
                status = {
                    "plugin_name": self.plugin_name,
                    "is_initialized": self.is_initialized,
                    "is_running": self.is_running,
                    "coordinator_available": False,
                    "error": "AI coordinator not available"
                }
                self.event_bus.emit("ai.status.response", status)
                
        except Exception as e:
            self.logger.error(f"❌ Error getting AI status: {e}")
    
    async def _list_workflows_async(self, addon_name: Optional[str] = None) -> None:
        """List workflows asynchronously"""
        try:
            if self.ai_coordinator:
                workflows = await self.ai_coordinator.list_workflows(addon_name)
                self.event_bus.emit("ai.workflows.listed", workflows)
            else:
                self.event_bus.emit("ai.workflows.listed", {
                    "success": False,
                    "error": "AI coordinator not available"
                })
                
        except Exception as e:
            self.logger.error(f"❌ Error listing workflows: {e}")
            self.event_bus.emit("ai.workflows.listed", {
                "success": False,
                "error": str(e)
            })
    
    async def _list_capabilities_async(self, addon_name: Optional[str] = None) -> None:
        """List capabilities asynchronously"""
        try:
            if self.ai_coordinator:
                capabilities = await self.ai_coordinator.list_capabilities(addon_name)
                self.event_bus.emit("ai.capabilities.listed", capabilities)
            else:
                self.event_bus.emit("ai.capabilities.listed", {
                    "success": False,
                    "error": "AI coordinator not available"
                })
                
        except Exception as e:
            self.logger.error(f"❌ Error listing capabilities: {e}")
            self.event_bus.emit("ai.capabilities.listed", {
                "success": False,
                "error": str(e)
            })
    
    def get_available_addons(self) -> List[str]:
        """Get list of available AI addons (synchronous - returns cached list)"""
        return self.enabled_addons.copy()
    
    async def execute_workflow(self, workflow_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow through coordinator"""
        try:
            if not self.ai_coordinator:
                return {
                    "success": False,
                    "error": "AI coordinator not available"
                }
            
            self.logger.info(f"🤖 Executing workflow '{workflow_id}' with params: {params}")
            
            # Execute through coordinator
            result = await self.ai_coordinator.execute_workflow(workflow_id, params)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ AI workflow execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "workflow_id": workflow_id,
                "params": params
            }
    
    async def get_ai_status(self) -> Dict[str, Any]:
        """Get comprehensive AI system status"""
        try:
            if self.ai_coordinator:
                coordinator_status = await self.ai_coordinator.get_coordinator_status()
                
                return {
                    "plugin_name": self.plugin_name,
                    "is_initialized": self.is_initialized,
                    "is_running": self.is_running,
                    "coordinator_available": True,
                    "enabled_addons": self.enabled_addons.copy(),
                    "coordinator_status": coordinator_status
                }
            else:
                return {
                    "plugin_name": self.plugin_name,
                    "is_initialized": self.is_initialized,
                    "is_running": self.is_running,
                    "coordinator_available": False,
                    "enabled_addons": [],
                    "error": "AI coordinator not available"
                }
                
        except Exception as e:
            self.logger.error(f"❌ Error getting AI status: {e}")
            return {
                "plugin_name": self.plugin_name,
                "is_initialized": self.is_initialized,
                "is_running": self.is_running,
                "coordinator_available": False,
                "enabled_addons": [],
                "error": str(e)
            }


# Plugin interface for VPA plugin manager
def initialize(event_bus: EventBus) -> AIPlugin:
    """
    Plugin initialization function called by VPA plugin manager
    Returns AIPlugin instance that needs async initialization
    """
    plugin = AIPlugin(event_bus)
    return plugin

async def initialize_async(event_bus: EventBus) -> AIPlugin:
    """
    Async plugin initialization function
    """
    plugin = AIPlugin(event_bus)
    await plugin.initialize()
    return plugin
