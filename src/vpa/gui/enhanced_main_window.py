"""
Enhanced VPA Main Window with RAG-LLM Integration

This module extends the existing VPA main window to include
advanced RAG-LLM capabilities for intelligent conversations.

Features:
- Integrated RAG-LLM chat interface
- Menu integration for easy access
- Event bus connectivity with existing VPA systems
- Real-time AI conversation capabilities
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from typing import Optional, Dict, Any
import asyncio
import threading
from datetime import datetime

from .main_window import VPAMainWindow
from .rag_llm_widget import RAGLLMChatWidget, create_rag_llm_integration_dialog
from ..core.llm import create_llm_manager, VPALLMManager
from ..core.rag import VPARAGSystem
from ..core.event_bus import VPAEventBus

logger = logging.getLogger(__name__)


class EnhancedVPAMainWindow(VPAMainWindow):
    """
    Enhanced VPA Main Window with RAG-LLM Integration
    
    Extends the base VPA main window to include:
    - RAG-LLM chat capabilities
    - Advanced AI conversation interface
    - Knowledge base integration
    - Performance monitoring
    """
    
    def __init__(self, event_bus: Optional[VPAEventBus] = None):
        """
        Initialize enhanced VPA main window
        
        Args:
            event_bus: Optional VPA event bus instance
        """
        # Initialize base window
        super().__init__(event_bus)
        
        # RAG-LLM components
        self.llm_manager: Optional[VPALLMManager] = None
        self.rag_system: Optional[VPARAGSystem] = None
        self.rag_chat_widget: Optional[RAGLLMChatWidget] = None
        
        # UI components
        self.rag_notebook: Optional[ttk.Notebook] = None
        self.rag_frame: Optional[ttk.Frame] = None
        
        # Initialize RAG-LLM systems
        self._initialize_rag_llm_systems()
        
        logger.info("Enhanced VPA Main Window initialized with RAG-LLM integration")
    
    def _initialize_rag_llm_systems(self):
        """Initialize RAG-LLM systems"""
        try:
            # Create LLM manager
            self.llm_manager = create_llm_manager()
            logger.info("LLM Manager initialized successfully")
            
            # RAG system will be initialized when database is available
            self.rag_system = None
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG-LLM systems: {e}")
    
    def create_window(self) -> Optional[tk.Tk]:
        """Create the enhanced main window with RAG-LLM integration"""
        # Call parent method to create base window
        root = super().create_window()
        
        if root:
            # Add RAG-LLM enhancements
            self._add_rag_llm_menu()
            self._create_rag_llm_interface()
            
        return root
    
    def _add_rag_llm_menu(self):
        """Add RAG-LLM menu items"""
        if not self.root:
            return
        
        try:
            # Get or create menubar
            menubar = self.root.nametowidget(".!menu") if self.root.winfo_children() else None
            if not menubar:
                menubar = tk.Menu(self.root)
                self.root.config(menu=menubar)
            
            # Add AI menu
            ai_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="AI", menu=ai_menu)
            
            # RAG-LLM submenu
            ai_menu.add_command(label="Open RAG Chat", command=self._open_rag_chat)
            ai_menu.add_command(label="RAG Integration Dialog", command=self._open_rag_integration_dialog)
            ai_menu.add_separator()
            ai_menu.add_command(label="Configure LLM Providers", command=self._configure_llm_providers)
            ai_menu.add_command(label="RAG System Status", command=self._show_rag_status)
            ai_menu.add_separator()
            ai_menu.add_command(label="Load Knowledge Base", command=self._load_knowledge_base)
            ai_menu.add_command(label="Export Conversations", command=self._export_conversations)
            
        except Exception as e:
            logger.error(f"Failed to add RAG-LLM menu: {e}")
    
    def _create_rag_llm_interface(self):
        """Create integrated RAG-LLM interface"""
        if not self.root:
            return
        
        try:
            # Find the existing notebook or create one
            notebook = None
            for child in self.root.winfo_children():
                if isinstance(child, ttk.Notebook):
                    notebook = child
                    break
            
            if not notebook:
                # Create notebook if it doesn't exist
                notebook = ttk.Notebook(self.root)
                notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Create RAG-LLM tab
            self.rag_frame = ttk.Frame(notebook)
            notebook.add(self.rag_frame, text="AI Chat")
            
            # Create RAG chat widget
            if self.llm_manager:
                self.rag_chat_widget = RAGLLMChatWidget(
                    self.rag_frame, 
                    self.llm_manager, 
                    self.rag_system
                )
                
                # Connect to event bus
                self._connect_rag_chat_events()
            
            self.rag_notebook = notebook
            
        except Exception as e:
            logger.error(f"Failed to create RAG-LLM interface: {e}")
    
    def _connect_rag_chat_events(self):
        """Connect RAG chat widget to VPA event bus"""
        if not self.event_bus or not self.rag_chat_widget:
            return
        
        try:
            # Listen for AI workflow events
            self.event_bus.subscribe("ai.workflow.completed", self._on_ai_workflow_completed)
            self.event_bus.subscribe("ai.status.response", self._on_ai_status_response)
            
            # Subscribe to RAG-specific events
            self.event_bus.subscribe("rag.search.completed", self._on_rag_search_completed)
            self.event_bus.subscribe("llm.response.generated", self._on_llm_response_generated)
            
        except Exception as e:
            logger.error(f"Failed to connect RAG chat events: {e}")
    
    def _on_ai_workflow_completed(self, event_data: Dict[str, Any]):
        """Handle AI workflow completion"""
        try:
            if self.rag_chat_widget:
                # Add workflow result to chat
                result = event_data.get("result", "Workflow completed")
                self.rag_chat_widget._add_system_message(f"Workflow: {result}")
            
        except Exception as e:
            logger.error(f"Error handling AI workflow completion: {e}")
    
    def _on_ai_status_response(self, event_data: Dict[str, Any]):
        """Handle AI status response"""
        try:
            if self.rag_chat_widget:
                status = event_data.get("status", "Unknown")
                self.rag_chat_widget._add_system_message(f"AI Status: {status}")
            
        except Exception as e:
            logger.error(f"Error handling AI status response: {e}")
    
    def _on_rag_search_completed(self, event_data: Dict[str, Any]):
        """Handle RAG search completion"""
        try:
            if self.rag_chat_widget:
                sources_count = event_data.get("sources_count", 0)
                search_time = event_data.get("search_time", 0)
                self.rag_chat_widget._add_rag_context_message(
                    f"Knowledge search completed: {sources_count} sources in {search_time:.3f}s"
                )
            
        except Exception as e:
            logger.error(f"Error handling RAG search completion: {e}")
    
    def _on_llm_response_generated(self, event_data: Dict[str, Any]):
        """Handle LLM response generation"""
        try:
            if self.rag_chat_widget:
                response_time = event_data.get("generation_time", 0)
                tokens = event_data.get("tokens", 0)
                self.rag_chat_widget._add_system_message(
                    f"Response generated: {tokens} tokens in {response_time:.3f}s"
                )
            
        except Exception as e:
            logger.error(f"Error handling LLM response generation: {e}")
    
    def _open_rag_chat(self):
        """Open dedicated RAG chat interface"""
        try:
            if self.rag_notebook and self.rag_frame:
                # Select the AI Chat tab
                for i, tab_id in enumerate(self.rag_notebook.tabs()):
                    if self.rag_notebook.tab(tab_id, "text") == "AI Chat":
                        self.rag_notebook.select(i)
                        break
            else:
                # Create the interface if it doesn't exist
                self._create_rag_llm_interface()
            
        except Exception as e:
            logger.error(f"Failed to open RAG chat: {e}")
            messagebox.showerror("Error", f"Failed to open RAG chat: {e}")
    
    def _open_rag_integration_dialog(self):
        """Open RAG integration testing dialog"""
        try:
            if not self.root:
                messagebox.showerror("Error", "Main window not available")
                return
            
            dialog = create_rag_llm_integration_dialog(self.root, self)
            
        except Exception as e:
            logger.error(f"Failed to open RAG integration dialog: {e}")
            messagebox.showerror("Error", f"Failed to open integration dialog: {e}")
    
    def _configure_llm_providers(self):
        """Open LLM provider configuration dialog"""
        try:
            # Create configuration dialog
            config_dialog = tk.Toplevel(self.root)
            config_dialog.title("LLM Provider Configuration")
            config_dialog.geometry("500x400")
            config_dialog.transient(self.root)
            config_dialog.grab_set()
            
            # Configuration interface
            main_frame = ttk.Frame(config_dialog, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text="LLM Provider Configuration", 
                     font=("Arial", 12, "bold")).pack(pady=(0, 10))
            
            # Provider selection
            ttk.Label(main_frame, text="Available Providers:").pack(anchor=tk.W)
            
            providers = ["OpenAI", "Anthropic", "Azure OpenAI", "Local Ollama", "Google Gemini"]
            for provider in providers:
                ttk.Label(main_frame, text=f"• {provider}").pack(anchor=tk.W, padx=(20, 0))
            
            ttk.Label(main_frame, text="\\nConfiguration is managed through environment variables.",
                     wraplength=450).pack(pady=(10, 0))
            
            # Close button
            ttk.Button(main_frame, text="Close", 
                      command=config_dialog.destroy).pack(pady=(20, 0))
            
        except Exception as e:
            logger.error(f"Failed to open LLM configuration: {e}")
            messagebox.showerror("Error", f"Failed to open configuration: {e}")
    
    def _show_rag_status(self):
        """Show RAG system status"""
        try:
            status_dialog = tk.Toplevel(self.root)
            status_dialog.title("RAG System Status")
            status_dialog.geometry("400x300")
            status_dialog.transient(self.root)
            status_dialog.grab_set()
            
            main_frame = ttk.Frame(status_dialog, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text="RAG System Status", 
                     font=("Arial", 12, "bold")).pack(pady=(0, 10))
            
            # Status information
            status_text = tk.Text(main_frame, height=15, width=50, wrap=tk.WORD)
            status_text.pack(fill=tk.BOTH, expand=True)
            
            # Populate status
            status_info = []
            status_info.append(f"LLM Manager: {'✅ Connected' if self.llm_manager else '❌ Not Available'}")
            status_info.append(f"RAG System: {'✅ Connected' if self.rag_system else '❌ Not Available'}")
            status_info.append(f"Chat Widget: {'✅ Active' if self.rag_chat_widget else '❌ Not Active'}")
            status_info.append("")
            status_info.append("System Information:")
            status_info.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            if self.llm_manager:
                try:
                    # Get available providers
                    status_info.append(f"Available LLM Providers: OpenAI, Anthropic, Azure, Ollama, Gemini")
                except:
                    status_info.append("LLM Provider info: Not available")
            
            status_text.insert(tk.END, "\\n".join(status_info))
            status_text.config(state=tk.DISABLED)
            
            # Close button
            ttk.Button(main_frame, text="Close", 
                      command=status_dialog.destroy).pack(pady=(10, 0))
            
        except Exception as e:
            logger.error(f"Failed to show RAG status: {e}")
            messagebox.showerror("Error", f"Failed to show status: {e}")
    
    def _load_knowledge_base(self):
        """Load knowledge base from files"""
        try:
            file_paths = filedialog.askopenfilenames(
                title="Select Knowledge Base Files",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("PDF files", "*.pdf"),
                    ("Markdown files", "*.md"),
                    ("All files", "*.*")
                ]
            )
            
            if file_paths:
                # This would integrate with the RAG system to load documents
                messagebox.showinfo("Knowledge Base", 
                                  f"Selected {len(file_paths)} files for knowledge base.\\n"
                                  "RAG system integration required for processing.")
            
        except Exception as e:
            logger.error(f"Failed to load knowledge base: {e}")
            messagebox.showerror("Error", f"Failed to load knowledge base: {e}")
    
    def _export_conversations(self):
        """Export conversation history"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Export Conversations",
                defaultextension=".json",
                filetypes=[
                    ("JSON files", "*.json"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                # This would export conversation data
                messagebox.showinfo("Export", 
                                  f"Conversations would be exported to:\\n{file_path}\\n"
                                  "Feature requires conversation database integration.")
            
        except Exception as e:
            logger.error(f"Failed to export conversations: {e}")
            messagebox.showerror("Error", f"Failed to export conversations: {e}")
    
    def set_rag_system(self, rag_system: VPARAGSystem):
        """Set the RAG system for the enhanced window"""
        self.rag_system = rag_system
        
        if self.rag_chat_widget:
            self.rag_chat_widget.set_rag_system(rag_system)
        
        logger.info("RAG system connected to enhanced main window")
    
    def get_rag_chat_widget(self) -> Optional[RAGLLMChatWidget]:
        """Get the RAG chat widget instance"""
        return self.rag_chat_widget
    
    def show_rag_response(self, response: str, sources: list = None):
        """Display a RAG response in the chat interface"""
        if self.rag_chat_widget:
            self.rag_chat_widget._add_assistant_message(response)
            
            if sources:
                self.rag_chat_widget._show_source_details(sources)


def create_enhanced_vpa_window(event_bus: Optional[VPAEventBus] = None) -> EnhancedVPAMainWindow:
    """
    Create an enhanced VPA main window with RAG-LLM integration
    
    Args:
        event_bus: Optional VPA event bus instance
        
    Returns:
        EnhancedVPAMainWindow instance
    """
    return EnhancedVPAMainWindow(event_bus)


if __name__ == "__main__":
    # Test the enhanced main window
    try:
        window = create_enhanced_vpa_window()
        window.run()
    except Exception as e:
        print(f"Failed to run enhanced VPA window: {e}")
