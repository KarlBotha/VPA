"""
Addon AI Logic Compartment

Handles addon-specific automation and workflows as specified in VPA_APP_FINAL_OVERVIEW.md.
This compartment manages:
- Addon-specific automation/workflows using the new compartmentalized system
- Integration with individual addon logic modules through AddonLogicCoordinator
- Coordination between multiple active addons
- Centralized management of all addon workflows and capabilities

This is one of three AI logic compartments in the VPA agentic automation platform.
"""

import logging
from typing import Dict, Any, List, Optional, Callable, Set
from datetime import datetime
import asyncio
from dataclasses import dataclass

from ..core.events import EventBus
from ..core.logging import get_structured_logger
from .addon_logic.addon_logic_coordinator import AddonLogicCoordinator

logger = get_structured_logger(__name__)

@dataclass
class AddonWorkflow:
    """Represents an addon-specific workflow"""
    workflow_id: str
    addon_name: str  # Which addon this workflow belongs to
    workflow_name: str
    description: str
    steps: List[Dict[str, Any]]
    triggers: List[str]  # Event types that trigger this workflow
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
    capability_type: str  # 'automation', 'integration', 'communication', etc.
    description: str
    parameters: Dict[str, Any]
    dependencies: Optional[List[str]] = None
    is_enabled: bool = True

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class AddonAILogic:
    """
    Addon AI Logic Compartment
    
    Handles addon-specific automation and workflows as specified in VPA_APP_FINAL_OVERVIEW.md.
    Now integrates with the new compartmentalized addon system through AddonLogicCoordinator.
    """
    
    def __init__(self, event_bus: EventBus, config: Optional[Dict[str, Any]] = None):
        """Initialize Addon AI Logic compartment"""
        self.event_bus = event_bus
        self.config = config or {}
        self.logger = get_structured_logger(f"{__name__}.AddonAILogic")
        
        # New compartmentalized addon system
        self.addon_coordinator = AddonLogicCoordinator(event_bus)
        
        # Legacy compatibility - keeping for gradual migration
        self.active_addons: Set[str] = set()
        self.addon_workflows: Dict[str, List[AddonWorkflow]] = {}  # addon_name -> workflows
        self.addon_capabilities: Dict[str, List[AddonCapability]] = {}  # addon_name -> capabilities
        self.addon_instances: Dict[str, Any] = {}  # addon_name -> addon instance
        
        # Workflow execution tracking
        self.running_workflows: Dict[str, AddonWorkflow] = {}
        self.workflow_results: Dict[str, Dict[str, Any]] = {}
        
        # State management
        self.is_initialized = False
        self.is_running = False
        
        # Supported addon types from VPA_APP_FINAL_OVERVIEW.md
        self.supported_addons = {
            'google', 'microsoft', 'whatsapp', 'telegram', 
            'discord', 'weather', 'windows', 'websearch'
        }
        
        self.logger.info("Addon AI Logic compartment created with compartmentalized addon system")
    
    async def initialize(self) -> bool:
        """Initialize the Addon AI Logic compartment"""
        try:
            if self.is_initialized:
                self.logger.warning("Addon AI Logic already initialized")
                return True
            
            # Initialize the new compartmentalized addon coordinator
            self.logger.info("Initializing compartmentalized addon system...")
            coordinator_result = await self.addon_coordinator.initialize_coordinator()
            
            if not coordinator_result.get("success", False):
                self.logger.error("Failed to initialize addon coordinator")
                return False
            
            self.logger.info(f"Addon coordinator initialized with {coordinator_result.get('enabled_addons', 0)} addons")
            
            # Register event handlers for this AI logic compartment
            await self._register_event_handlers()
            
            # Initialize legacy addon containers for backward compatibility
            await self._initialize_addon_containers()
            
            # Register any additional builtin workflows
            await self._register_builtin_addon_workflows()
            
            self.is_initialized = True
            self.is_running = True
            
            # Notify system that Addon AI Logic is ready
            self.event_bus.emit("ai.addon_logic.initialized", {
                "compartment": "addon_logic",
                "status": "ready",
                "enabled_addons": list(self.addon_coordinator.enabled_addons),
                "total_workflows": len(self.addon_coordinator.all_workflows),
                "total_capabilities": len(self.addon_coordinator.all_capabilities),
                "timestamp": datetime.now().isoformat()
            })
            
            self.logger.info("Addon AI Logic compartment initialized successfully with compartmentalized system")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Addon AI Logic: {e}")
            return False
    
    async def _register_event_handlers(self) -> None:
        """Register event handlers for Addon AI Logic"""
        # Addon lifecycle events
        self.event_bus.subscribe("addon.activated", self._handle_addon_activated)
        self.event_bus.subscribe("addon.deactivated", self._handle_addon_deactivated)
        
        # Addon workflow events
        self.event_bus.subscribe("ai.addon.execute_workflow", self._handle_execute_addon_workflow)
        self.event_bus.subscribe("ai.addon.register_workflow", self._handle_register_workflow)
        self.event_bus.subscribe("ai.addon.query_capabilities", self._handle_query_capabilities)
        
        # Specific addon automation events
        self.event_bus.subscribe("ai.addon.google.*", self._handle_google_automation)
        self.event_bus.subscribe("ai.addon.microsoft.*", self._handle_microsoft_automation)
        self.event_bus.subscribe("ai.addon.communication.*", self._handle_communication_automation)
        self.event_bus.subscribe("ai.addon.system.*", self._handle_system_automation)
        
        # Cross-addon coordination events
        self.event_bus.subscribe("ai.addon.coordinate", self._handle_addon_coordination)
        
        # Resource monitoring integration
        self.event_bus.subscribe("resource.strain.detected", self._handle_resource_strain)
        
        self.logger.info("Event handlers registered for Addon AI Logic")
    
    async def _initialize_addon_containers(self) -> None:
        """Initialize containers for addon-specific logic"""
        for addon_name in self.supported_addons:
            self.addon_workflows[addon_name] = []
            self.addon_capabilities[addon_name] = []
        
        self.logger.info("Addon logic containers initialized")
    
    async def _register_builtin_addon_workflows(self) -> None:
        """Register built-in workflows for each addon type"""
        
        # Google addon workflows
        self.addon_workflows['google'].extend([
            AddonWorkflow(
                workflow_id="gmail_automation",
                addon_name="google",
                workflow_name="Gmail Automation",
                description="Automate Gmail operations (send, read, organize)",
                steps=[
                    {"action": "authenticate", "params": {"service": "gmail"}},
                    {"action": "check_inbox", "params": {}},
                    {"action": "process_emails", "params": {"rules": "default"}}
                ],
                triggers=["gmail.automation.request"]
            ),
            AddonWorkflow(
                workflow_id="drive_sync",
                addon_name="google",
                workflow_name="Google Drive Sync",
                description="Synchronize files with Google Drive",
                steps=[
                    {"action": "authenticate", "params": {"service": "drive"}},
                    {"action": "sync_files", "params": {"direction": "bidirectional"}}
                ],
                triggers=["drive.sync.request"]
            )
        ])
        
        # Microsoft addon workflows
        self.addon_workflows['microsoft'].extend([
            AddonWorkflow(
                workflow_id="outlook_automation",
                addon_name="microsoft",
                workflow_name="Outlook Automation",
                description="Automate Outlook operations",
                steps=[
                    {"action": "authenticate", "params": {"service": "outlook"}},
                    {"action": "manage_calendar", "params": {}},
                    {"action": "process_emails", "params": {}}
                ],
                triggers=["outlook.automation.request"]
            ),
            AddonWorkflow(
                workflow_id="onedrive_backup",
                addon_name="microsoft",
                workflow_name="OneDrive Backup",
                description="Backup files to OneDrive",
                steps=[
                    {"action": "authenticate", "params": {"service": "onedrive"}},
                    {"action": "backup_files", "params": {"selective": True}}
                ],
                triggers=["onedrive.backup.request"]
            )
        ])
        
        # Communication addon workflows (WhatsApp, Telegram, Discord)
        for comm_addon in ['whatsapp', 'telegram', 'discord']:
            self.addon_workflows[comm_addon].append(
                AddonWorkflow(
                    workflow_id=f"{comm_addon}_messaging",
                    addon_name=comm_addon,
                    workflow_name=f"{comm_addon.title()} Messaging",
                    description=f"Automate {comm_addon} messaging operations",
                    steps=[
                        {"action": "authenticate", "params": {"platform": comm_addon}},
                        {"action": "send_message", "params": {}},
                        {"action": "check_messages", "params": {}}
                    ],
                    triggers=[f"{comm_addon}.message.request"]
                )
            )
        
        # Weather addon workflow
        self.addon_workflows['weather'].append(
            AddonWorkflow(
                workflow_id="weather_monitoring",
                addon_name="weather",
                workflow_name="Weather Monitoring",
                description="Monitor and report weather conditions",
                steps=[
                    {"action": "fetch_weather", "params": {"location": "auto"}},
                    {"action": "analyze_conditions", "params": {}},
                    {"action": "send_alerts", "params": {"conditions": ["severe"]}}
                ],
                triggers=["weather.check.request", "weather.alert.trigger"]
            )
        )
        
        # Windows automation workflow
        self.addon_workflows['windows'].extend([
            AddonWorkflow(
                workflow_id="system_automation",
                addon_name="windows",
                workflow_name="Windows System Automation",
                description="Automate Windows system operations",
                steps=[
                    {"action": "system_check", "params": {}},
                    {"action": "optimize_performance", "params": {}},
                    {"action": "manage_services", "params": {}}
                ],
                triggers=["windows.automation.request"]
            )
        ])
        
        # Web search workflow
        self.addon_workflows['websearch'].append(
            AddonWorkflow(
                workflow_id="intelligent_search",
                addon_name="websearch",
                workflow_name="Intelligent Web Search",
                description="Perform intelligent web searches and information gathering",
                steps=[
                    {"action": "parse_query", "params": {}},
                    {"action": "search_multiple_sources", "params": {}},
                    {"action": "aggregate_results", "params": {}},
                    {"action": "rank_relevance", "params": {}}
                ],
                triggers=["websearch.query.request"]
            )
        )
        
        total_workflows = sum(len(workflows) for workflows in self.addon_workflows.values())
        self.logger.info(f"Registered {total_workflows} built-in addon workflows")
    
    async def _handle_addon_activated(self, data: Dict[str, Any]) -> None:
        """Handle addon activation events"""
        addon_name = data.get('addon_name')
        if addon_name in self.supported_addons:
            self.active_addons.add(addon_name)
            
            # Load addon-specific logic
            await self._load_addon_logic(addon_name)
            
            # Notify that addon logic is loaded
            self.event_bus.emit("ai.addon.logic_loaded", {
                "addon_name": addon_name,
                "workflows_available": len(self.addon_workflows.get(addon_name, [])),
                "capabilities_available": len(self.addon_capabilities.get(addon_name, [])),
                "timestamp": datetime.now().isoformat()
            })
            
            self.logger.info(f"Activated addon logic for: {addon_name}")
        else:
            self.logger.warning(f"Unsupported addon activation request: {addon_name}")
    
    async def _handle_addon_deactivated(self, data: Dict[str, Any]) -> None:
        """Handle addon deactivation events"""
        addon_name = data.get('addon_name')
        if addon_name in self.active_addons:
            self.active_addons.remove(addon_name)
            
            # Stop any running workflows for this addon
            await self._stop_addon_workflows(addon_name)
            
            # Unload addon instance
            if addon_name in self.addon_instances:
                del self.addon_instances[addon_name]
            
            # Notify that addon logic is unloaded
            self.event_bus.emit("ai.addon.logic_unloaded", {
                "addon_name": addon_name,
                "timestamp": datetime.now().isoformat()
            })
            
            self.logger.info(f"Deactivated addon logic for: {addon_name}")
    
    async def _load_addon_logic(self, addon_name: str) -> None:
        """Load addon-specific AI logic"""
        try:
            # Register addon capabilities based on type
            if addon_name == 'google':
                await self._register_google_capabilities()
            elif addon_name == 'microsoft':
                await self._register_microsoft_capabilities()
            elif addon_name in ['whatsapp', 'telegram', 'discord']:
                await self._register_communication_capabilities(addon_name)
            elif addon_name == 'weather':
                await self._register_weather_capabilities()
            elif addon_name == 'windows':
                await self._register_windows_capabilities()
            elif addon_name == 'websearch':
                await self._register_websearch_capabilities()
            
            self.logger.info(f"Loaded AI logic for addon: {addon_name}")
            
        except Exception as e:
            self.logger.error(f"Error loading addon logic for {addon_name}: {e}")
    
    async def _register_google_capabilities(self) -> None:
        """Register Google addon capabilities"""
        capabilities = [
            AddonCapability("gmail_operations", "google", "communication", "Gmail email operations", {}),
            AddonCapability("drive_storage", "google", "storage", "Google Drive file operations", {}),
            AddonCapability("calendar_management", "google", "scheduling", "Google Calendar operations", {}),
            AddonCapability("docs_collaboration", "google", "productivity", "Google Docs operations", {})
        ]
        self.addon_capabilities['google'].extend(capabilities)
    
    async def _register_microsoft_capabilities(self) -> None:
        """Register Microsoft addon capabilities"""
        capabilities = [
            AddonCapability("outlook_operations", "microsoft", "communication", "Outlook email operations", {}),
            AddonCapability("onedrive_storage", "microsoft", "storage", "OneDrive file operations", {}),
            AddonCapability("teams_collaboration", "microsoft", "communication", "Microsoft Teams operations", {}),
            AddonCapability("office_productivity", "microsoft", "productivity", "Office suite operations", {})
        ]
        self.addon_capabilities['microsoft'].extend(capabilities)
    
    async def _register_communication_capabilities(self, addon_name: str) -> None:
        """Register communication addon capabilities"""
        capabilities = [
            AddonCapability(f"{addon_name}_messaging", addon_name, "communication", f"{addon_name.title()} messaging", {}),
            AddonCapability(f"{addon_name}_automation", addon_name, "automation", f"{addon_name.title()} automation", {})
        ]
        self.addon_capabilities[addon_name].extend(capabilities)
    
    async def _register_weather_capabilities(self) -> None:
        """Register weather addon capabilities"""
        capabilities = [
            AddonCapability("weather_monitoring", "weather", "monitoring", "Weather condition monitoring", {}),
            AddonCapability("weather_alerts", "weather", "notification", "Weather alert system", {}),
            AddonCapability("weather_forecasting", "weather", "analysis", "Weather forecast analysis", {})
        ]
        self.addon_capabilities['weather'].extend(capabilities)
    
    async def _register_windows_capabilities(self) -> None:
        """Register Windows addon capabilities"""
        capabilities = [
            AddonCapability("system_automation", "windows", "automation", "Windows system automation", {}),
            AddonCapability("file_management", "windows", "file_operations", "Windows file operations", {}),
            AddonCapability("process_management", "windows", "system", "Windows process management", {}),
            AddonCapability("registry_operations", "windows", "system", "Windows registry operations", {})
        ]
        self.addon_capabilities['windows'].extend(capabilities)
    
    async def _register_websearch_capabilities(self) -> None:
        """Register web search addon capabilities"""
        capabilities = [
            AddonCapability("intelligent_search", "websearch", "search", "Intelligent web search", {}),
            AddonCapability("information_aggregation", "websearch", "analysis", "Information aggregation", {}),
            AddonCapability("source_validation", "websearch", "verification", "Source validation", {}),
            AddonCapability("content_summarization", "websearch", "analysis", "Content summarization", {})
        ]
        self.addon_capabilities['websearch'].extend(capabilities)
    
    async def _handle_execute_addon_workflow(self, data: Dict[str, Any]) -> None:
        """Handle addon workflow execution requests"""
        addon_name = data.get('addon_name')
        workflow_name = data.get('workflow_name')
        parameters = data.get('parameters', {})
        
        if addon_name not in self.active_addons:
            self.logger.error(f"Cannot execute workflow for inactive addon: {addon_name}")
            return
        
        # Find the workflow
        workflow = None
        for wf in self.addon_workflows.get(addon_name, []):
            if wf.workflow_name == workflow_name or wf.workflow_id == workflow_name:
                workflow = wf
                break
        
        if workflow:
            await self._execute_addon_workflow(workflow, parameters)
        else:
            self.logger.error(f"Workflow not found: {workflow_name} for addon: {addon_name}")
    
    async def _execute_addon_workflow(self, workflow: AddonWorkflow, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an addon-specific workflow"""
        try:
            workflow.last_executed = datetime.now()
            workflow.execution_count += 1
            
            self.running_workflows[workflow.workflow_id] = workflow
            
            results = []
            for step in workflow.steps:
                step_result = await self._execute_workflow_step(workflow.addon_name, step, parameters)
                results.append(step_result)
                
                if not step_result.get('success', False):
                    break  # Stop on failure
            
            # Store results
            self.workflow_results[workflow.workflow_id] = {
                "success": True,
                "workflow": workflow.workflow_name,
                "addon": workflow.addon_name,
                "results": results,
                "executed_at": workflow.last_executed.isoformat()
            }
            
            # Remove from running workflows
            if workflow.workflow_id in self.running_workflows:
                del self.running_workflows[workflow.workflow_id]
            
            # Emit completion event
            self.event_bus.emit("ai.addon.workflow.completed", self.workflow_results[workflow.workflow_id])
            
            return self.workflow_results[workflow.workflow_id]
            
        except Exception as e:
            self.logger.error(f"Error executing addon workflow {workflow.workflow_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_workflow_step(self, addon_name: str, step: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow step for an addon"""
        action = step.get('action')
        step_params = {**step.get('params', {}), **parameters}
        
        # Validate action parameter
        if not action or not isinstance(action, str):
            return {"success": False, "error": f"Invalid or missing action in step: {action}"}
        
        # Route to addon-specific handler
        if addon_name == 'google':
            return await self._execute_google_action(action, step_params)
        elif addon_name == 'microsoft':
            return await self._execute_microsoft_action(action, step_params)
        elif addon_name in ['whatsapp', 'telegram', 'discord']:
            return await self._execute_communication_action(addon_name, action, step_params)
        elif addon_name == 'weather':
            return await self._execute_weather_action(action, step_params)
        elif addon_name == 'windows':
            return await self._execute_windows_action(action, step_params)
        elif addon_name == 'websearch':
            return await self._execute_websearch_action(action, step_params)
        else:
            return {"success": False, "error": f"Unknown addon: {addon_name}"}
    
    # Placeholder implementations for addon-specific actions
    async def _execute_google_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Google addon action"""
        return {"success": True, "addon": "google", "action": action, "params": params}
    
    async def _execute_microsoft_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Microsoft addon action"""
        return {"success": True, "addon": "microsoft", "action": action, "params": params}
    
    async def _execute_communication_action(self, addon_name: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute communication addon action"""
        return {"success": True, "addon": addon_name, "action": action, "params": params}
    
    async def _execute_weather_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute weather addon action"""
        return {"success": True, "addon": "weather", "action": action, "params": params}
    
    async def _execute_windows_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Windows addon action"""
        return {"success": True, "addon": "windows", "action": action, "params": params}
    
    async def _execute_websearch_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web search addon action"""
        return {"success": True, "addon": "websearch", "action": action, "params": params}
    
    async def _handle_register_workflow(self, data: Dict[str, Any]) -> None:
        """Handle workflow registration requests"""
        addon_name = data.get('addon_name')
        workflow_data = data.get('workflow')
        
        if addon_name in self.supported_addons and workflow_data:
            workflow = AddonWorkflow(
                workflow_id=workflow_data.get('workflow_id'),
                addon_name=addon_name,
                workflow_name=workflow_data.get('workflow_name'),
                description=workflow_data.get('description', ''),
                steps=workflow_data.get('steps', []),
                triggers=workflow_data.get('triggers', [])
            )
            
            self.addon_workflows[addon_name].append(workflow)
            self.logger.info(f"Registered workflow {workflow.workflow_name} for addon {addon_name}")
    
    async def _handle_query_capabilities(self, data: Dict[str, Any]) -> None:
        """Handle capability query requests"""
        addon_name = data.get('addon_name')
        
        if addon_name:
            capabilities = self.addon_capabilities.get(addon_name, [])
            response = {
                "addon_name": addon_name,
                "capabilities": [
                    {
                        "id": cap.capability_id,
                        "type": cap.capability_type,
                        "description": cap.description,
                        "enabled": cap.is_enabled
                    } for cap in capabilities
                ]
            }
        else:
            # Return all capabilities
            response = {
                "all_capabilities": {
                    addon: [
                        {
                            "id": cap.capability_id,
                            "type": cap.capability_type,
                            "description": cap.description,
                            "enabled": cap.is_enabled
                        } for cap in caps
                    ] for addon, caps in self.addon_capabilities.items()
                }
            }
        
        self.event_bus.emit("ai.addon.capabilities.response", response)
    
    async def _handle_google_automation(self, data: Dict[str, Any]) -> None:
        """Handle Google addon automation requests"""
        if 'google' in self.active_addons:
            # Route to appropriate Google automation
            await self._execute_google_action(data.get('action', ''), data.get('parameters', {}))
    
    async def _handle_microsoft_automation(self, data: Dict[str, Any]) -> None:
        """Handle Microsoft addon automation requests"""
        if 'microsoft' in self.active_addons:
            # Route to appropriate Microsoft automation
            await self._execute_microsoft_action(data.get('action', ''), data.get('parameters', {}))
    
    async def _handle_communication_automation(self, data: Dict[str, Any]) -> None:
        """Handle communication addon automation requests"""
        addon_name = data.get('addon_name')
        if addon_name in self.active_addons and addon_name in ['whatsapp', 'telegram', 'discord']:
            await self._execute_communication_action(addon_name, data.get('action', ''), data.get('parameters', {}))
    
    async def _handle_system_automation(self, data: Dict[str, Any]) -> None:
        """Handle system addon automation requests"""
        addon_name = data.get('addon_name', 'windows')
        if addon_name in self.active_addons:
            if addon_name == 'windows':
                await self._execute_windows_action(data.get('action', ''), data.get('parameters', {}))
            elif addon_name == 'websearch':
                await self._execute_websearch_action(data.get('action', ''), data.get('parameters', {}))
    
    async def _handle_addon_coordination(self, data: Dict[str, Any]) -> None:
        """Handle cross-addon coordination requests"""
        involved_addons = data.get('addons', [])
        coordination_type = data.get('coordination_type', 'sequential')
        workflow_steps = data.get('steps', [])
        
        # Execute coordination based on type
        if coordination_type == 'sequential':
            await self._execute_sequential_coordination(involved_addons, workflow_steps)
        elif coordination_type == 'parallel':
            await self._execute_parallel_coordination(involved_addons, workflow_steps)
        else:
            self.logger.error(f"Unknown coordination type: {coordination_type}")
    
    async def _execute_sequential_coordination(self, addons: List[str], steps: List[Dict[str, Any]]) -> None:
        """Execute sequential coordination between addons"""
        results = []
        for step in steps:
            addon_name = step.get('addon')
            if addon_name in addons and addon_name in self.active_addons:
                result = await self._execute_workflow_step(addon_name, step, {})
                results.append(result)
        
        self.event_bus.emit("ai.addon.coordination.completed", {
            "type": "sequential",
            "addons": addons,
            "results": results
        })
    
    async def _execute_parallel_coordination(self, addons: List[str], steps: List[Dict[str, Any]]) -> None:
        """Execute parallel coordination between addons"""
        tasks = []
        for step in steps:
            addon_name = step.get('addon')
            if addon_name in addons and addon_name in self.active_addons:
                task = asyncio.create_task(self._execute_workflow_step(addon_name, step, {}))
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        self.event_bus.emit("ai.addon.coordination.completed", {
            "type": "parallel",
            "addons": addons,
            "results": [r for r in results if not isinstance(r, Exception)]
        })
    
    async def _stop_addon_workflows(self, addon_name: str) -> None:
        """Stop all running workflows for an addon"""
        workflows_to_stop = [
            wf_id for wf_id, wf in self.running_workflows.items()
            if wf.addon_name == addon_name
        ]
        
        for workflow_id in workflows_to_stop:
            if workflow_id in self.running_workflows:
                del self.running_workflows[workflow_id]
                self.logger.info(f"Stopped workflow {workflow_id} for deactivated addon {addon_name}")
    
    async def _handle_resource_strain(self, data: Dict[str, Any]) -> None:
        """Handle resource strain notifications"""
        strain_level = data.get('strain_level', 'unknown')
        
        if strain_level in ['high', 'critical']:
            # Pause non-critical addon workflows
            await self._pause_non_critical_addon_workflows()
        
        self.event_bus.emit("ai.addon.resource_response", {
            "compartment": "addon_logic",
            "strain_level": strain_level,
            "action": "paused_non_critical_workflows",
            "active_addons": list(self.active_addons),
            "timestamp": datetime.now().isoformat()
        })
    
    async def _pause_non_critical_addon_workflows(self) -> None:
        """Pause non-critical addon workflows during resource strain"""
        non_critical_addons = ['weather', 'websearch']  # These can be paused safely
        
        for addon_name in non_critical_addons:
            if addon_name in self.active_addons:
                await self._stop_addon_workflows(addon_name)
                self.logger.info(f"Paused workflows for non-critical addon: {addon_name}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of Addon AI Logic compartment"""
        return {
            "compartment": "addon_logic",
            "is_initialized": self.is_initialized,
            "is_running": self.is_running,
            "active_addons": list(self.active_addons),
            "supported_addons": list(self.supported_addons),
            "running_workflows": len(self.running_workflows),
            "total_workflows": sum(len(wf) for wf in self.addon_workflows.values()),
            "total_capabilities": sum(len(cap) for cap in self.addon_capabilities.values())
        }
    
    async def shutdown(self) -> bool:
        """Shutdown the Addon AI Logic compartment"""
        try:
            self.is_running = False
            
            # Stop all running workflows
            for addon_name in list(self.active_addons):
                await self._stop_addon_workflows(addon_name)
            
            # Clear state
            self.active_addons.clear()
            self.running_workflows.clear()
            self.addon_instances.clear()
            
            # Emit shutdown event
            self.event_bus.emit("ai.addon_logic.shutdown", {
                "compartment": "addon_logic",
                "timestamp": datetime.now().isoformat()
            })
            
            self.logger.info("Addon AI Logic compartment shutdown successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during Addon AI Logic shutdown: {e}")
            return False
        
    # New coordinator delegation methods
    async def execute_workflow_by_coordinator(self, workflow_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow using the new compartmentalized coordinator"""
        if not self.is_initialized:
            return {"success": False, "error": "Addon AI Logic not initialized"}
        
        return await self.addon_coordinator.execute_workflow(workflow_id, params)
    
    async def get_coordinator_status(self) -> Dict[str, Any]:
        """Get status from the compartmentalized addon coordinator"""
        if not self.is_initialized:
            return {"success": False, "error": "Addon AI Logic not initialized"}
        
        return await self.addon_coordinator.get_coordinator_status()
    
    async def list_coordinator_workflows(self, addon_name: Optional[str] = None) -> Dict[str, Any]:
        """List workflows from the compartmentalized coordinator"""
        if not self.is_initialized:
            return {"success": False, "error": "Addon AI Logic not initialized"}
        
        return await self.addon_coordinator.list_workflows(addon_name)
    
    async def list_coordinator_capabilities(self, addon_name: Optional[str] = None) -> Dict[str, Any]:
        """List capabilities from the compartmentalized coordinator"""
        if not self.is_initialized:
            return {"success": False, "error": "Addon AI Logic not initialized"}
        
        return await self.addon_coordinator.list_capabilities(addon_name)
