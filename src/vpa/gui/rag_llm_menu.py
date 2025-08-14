"""
VPA RAG-LLM Menu Integration

This module provides menu integration for RAG-LLM capabilities
in the existing VPA main window without complex inheritance.

Features:
- Menu-based RAG-LLM access
- Standalone RAG chat windows
- Integration with existing VPA systems
- Event bus connectivity
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from .rag_llm_widget import RAGLLMChatWidget, create_rag_llm_integration_dialog
from ..core.llm import create_llm_manager, VPALLMManager
from ..core.rag import VPARAGSystem

logger = logging.getLogger(__name__)


class VPARAGLLMMenuIntegration:
    """
    Menu integration for RAG-LLM capabilities
    
    Provides menu-based access to RAG-LLM features
    without modifying the existing main window structure.
    """
    
    def __init__(self, main_window_root: tk.Tk, event_bus=None):
        """
        Initialize RAG-LLM menu integration
        
        Args:
            main_window_root: The main window root widget
            event_bus: Optional event bus for integration
        """
        self.root = main_window_root
        self.event_bus = event_bus
        
        # RAG-LLM components
        self.llm_manager: Optional[VPALLMManager] = None
        self.rag_system: Optional[VPARAGSystem] = None
        
        # Chat windows
        self.chat_windows: List[tk.Toplevel] = []
        
        # Initialize systems
        self._initialize_systems()
        
        # Add menu integration
        self._add_menu_items()
        
        logger.info("VPA RAG-LLM Menu Integration initialized")
    
    def _initialize_systems(self):
        """Initialize RAG-LLM systems"""
        try:
            # Create LLM manager
            self.llm_manager = create_llm_manager()
            logger.info("LLM Manager initialized for menu integration")
            
            # RAG system will be set when available
            self.rag_system = None
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG-LLM systems: {e}")
    
    def _add_menu_items(self):
        """Add RAG-LLM menu items to existing menu"""
        try:
            # Get existing menubar
            menubar = None
            for child in self.root.winfo_children():
                if isinstance(child, tk.Menu):
                    menubar = child
                    break
            
            if not menubar:
                # Create menubar if it doesn't exist
                menubar = tk.Menu(self.root)
                self.root.config(menu=menubar)
            
            # Add AI menu
            ai_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="AI Assistant", menu=ai_menu)
            
            # RAG-LLM menu items
            ai_menu.add_command(label="Open AI Chat", command=self.open_rag_chat_window)
            ai_menu.add_command(label="RAG Integration Test", command=self.open_integration_dialog)
            ai_menu.add_separator()
            ai_menu.add_command(label="AI System Status", command=self.show_system_status)
            ai_menu.add_command(label="Load Knowledge Base", command=self.load_knowledge_base)
            ai_menu.add_separator()
            ai_menu.add_command(label="Export Conversations", command=self.export_conversations)
            ai_menu.add_command(label="Clear All Chats", command=self.clear_all_chats)
            
        except Exception as e:
            logger.error(f"Failed to add RAG-LLM menu items: {e}")
    
    def open_rag_chat_window(self):
        """Open a new RAG chat window"""
        try:
            # Create new chat window
            chat_window = tk.Toplevel(self.root)
            chat_window.title("VPA AI Assistant")
            chat_window.geometry("800x600")
            
            # Configure window
            chat_window.transient(self.root)
            chat_window.grab_set()
            
            # Add to chat windows list
            self.chat_windows.append(chat_window)
            
            # Create chat widget
            if self.llm_manager:
                chat_widget = RAGLLMChatWidget(
                    chat_window,
                    self.llm_manager,
                    self.rag_system
                )
                
                # Add welcome message
                chat_widget._add_system_message(
                    "Welcome to VPA AI Assistant! "
                    "I can help you with questions and tasks using advanced AI capabilities."
                )
                
                # Handle window close
                def on_close():
                    if chat_window in self.chat_windows:
                        self.chat_windows.remove(chat_window)
                    chat_window.destroy()
                
                chat_window.protocol("WM_DELETE_WINDOW", on_close)
            
            else:
                messagebox.showerror("Error", "LLM Manager not available")
                chat_window.destroy()
                
        except Exception as e:
            logger.error(f"Failed to open RAG chat window: {e}")
            messagebox.showerror("Error", f"Failed to open chat window: {e}")
    
    def open_integration_dialog(self):
        """Open RAG integration testing dialog"""
        try:
            if not self.root:
                messagebox.showerror("Error", "Main window not available")
                return
            
            # Create integration test dialog
            dialog = create_rag_llm_integration_dialog(self.root, self)
            
        except Exception as e:
            logger.error(f"Failed to open integration dialog: {e}")
            messagebox.showerror("Error", f"Failed to open integration dialog: {e}")
    
    def show_system_status(self):
        """Show AI system status"""
        try:
            status_window = tk.Toplevel(self.root)
            status_window.title("VPA AI System Status")
            status_window.geometry("500x400")
            status_window.transient(self.root)
            
            main_frame = ttk.Frame(status_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            ttk.Label(main_frame, text="VPA AI System Status", 
                     font=("Arial", 14, "bold")).pack(pady=(0, 15))
            
            # Status display
            status_text = tk.Text(main_frame, height=20, width=60, wrap=tk.WORD, font=("Consolas", 10))
            status_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=status_text.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            status_text.config(yscrollcommand=scrollbar.set)
            
            # Generate status information
            status_info = []
            status_info.append("=== VPA AI SYSTEM STATUS ===")
            status_info.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            status_info.append("")
            
            # Core systems
            status_info.append("Core Systems:")
            status_info.append(f"  LLM Manager: {'✅ Active' if self.llm_manager else '❌ Not Available'}")
            status_info.append(f"  RAG System: {'✅ Connected' if self.rag_system else '⚠️ Not Connected'}")
            status_info.append(f"  Event Bus: {'✅ Connected' if self.event_bus else '⚠️ Not Connected'}")
            status_info.append("")
            
            # Chat windows
            status_info.append(f"Active Chat Windows: {len(self.chat_windows)}")
            for i, window in enumerate(self.chat_windows, 1):
                try:
                    title = window.title()
                    status_info.append(f"  Chat {i}: {title}")
                except:
                    status_info.append(f"  Chat {i}: Closed")
            status_info.append("")
            
            # LLM capabilities
            if self.llm_manager:
                status_info.append("LLM Capabilities:")
                status_info.append("  Supported Providers:")
                status_info.append("    • OpenAI (GPT models)")
                status_info.append("    • Anthropic (Claude models)")
                status_info.append("    • Azure OpenAI")
                status_info.append("    • Local Ollama")
                status_info.append("    • Google Gemini")
                status_info.append("")
                status_info.append("  Features:")
                status_info.append("    • Conversation management")
                status_info.append("    • Streaming responses")
                status_info.append("    • Multiple model support")
                status_info.append("    • Performance monitoring")
            
            status_info.append("")
            status_info.append("RAG System Status:")
            if self.rag_system:
                status_info.append("  ✅ Knowledge retrieval active")
                status_info.append("  ✅ Semantic search available")
                status_info.append("  ✅ Source attribution enabled")
            else:
                status_info.append("  ⚠️ RAG system not connected")
                status_info.append("  ⚠️ Knowledge base not available")
                status_info.append("  ℹ️ Operating in basic LLM mode")
            
            # Insert status information
            status_text.insert(tk.END, "\\n".join(status_info))
            status_text.config(state=tk.DISABLED)
            
            # Close button
            ttk.Button(main_frame, text="Close", 
                      command=status_window.destroy).pack(pady=(10, 0))
            
        except Exception as e:
            logger.error(f"Failed to show system status: {e}")
            messagebox.showerror("Error", f"Failed to show system status: {e}")
    
    def load_knowledge_base(self):
        """Load knowledge base from files"""
        try:
            file_paths = filedialog.askopenfilenames(
                title="Select Knowledge Base Files",
                filetypes=[
                    ("Text files", "*.txt"),
                    ("PDF files", "*.pdf"),
                    ("Markdown files", "*.md"),
                    ("Word documents", "*.docx"),
                    ("All files", "*.*")
                ]
            )
            
            if file_paths:
                # Show loading dialog
                load_dialog = tk.Toplevel(self.root)
                load_dialog.title("Loading Knowledge Base")
                load_dialog.geometry("400x200")
                load_dialog.transient(self.root)
                load_dialog.grab_set()
                
                frame = ttk.Frame(load_dialog, padding="20")
                frame.pack(fill=tk.BOTH, expand=True)
                
                ttk.Label(frame, text="Knowledge Base Loading", 
                         font=("Arial", 12, "bold")).pack(pady=(0, 10))
                
                ttk.Label(frame, text=f"Selected {len(file_paths)} files for processing.").pack()
                ttk.Label(frame, text="RAG system integration required for full functionality.").pack(pady=(10, 0))
                
                # File list
                file_list = tk.Listbox(frame, height=5)
                file_list.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
                
                for file_path in file_paths:
                    file_list.insert(tk.END, file_path.split("/")[-1])  # Just filename
                
                ttk.Button(frame, text="Close", 
                          command=load_dialog.destroy).pack(pady=(10, 0))
            
        except Exception as e:
            logger.error(f"Failed to load knowledge base: {e}")
            messagebox.showerror("Error", f"Failed to load knowledge base: {e}")
    
    def export_conversations(self):
        """Export conversation history"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Export Conversations",
                defaultextension=".json",
                filetypes=[
                    ("JSON files", "*.json"),
                    ("Text files", "*.txt"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                # Show export information
                export_dialog = tk.Toplevel(self.root)
                export_dialog.title("Export Conversations")
                export_dialog.geometry("400x250")
                export_dialog.transient(self.root)
                export_dialog.grab_set()
                
                frame = ttk.Frame(export_dialog, padding="20")
                frame.pack(fill=tk.BOTH, expand=True)
                
                ttk.Label(frame, text="Conversation Export", 
                         font=("Arial", 12, "bold")).pack(pady=(0, 10))
                
                info_text = f"""Export Location:
{file_path}

Export would include:
• Conversation history
• RAG source references
• Performance metrics
• Timestamps and metadata

Note: Database integration required for full export functionality."""
                
                ttk.Label(frame, text=info_text, justify=tk.LEFT).pack(pady=(0, 10))
                
                ttk.Button(frame, text="Close", 
                          command=export_dialog.destroy).pack()
            
        except Exception as e:
            logger.error(f"Failed to export conversations: {e}")
            messagebox.showerror("Error", f"Failed to export conversations: {e}")
    
    def clear_all_chats(self):
        """Clear all chat windows"""
        try:
            if not self.chat_windows:
                messagebox.showinfo("Info", "No active chat windows to clear.")
                return
            
            result = messagebox.askyesno("Confirm", 
                                       f"Close all {len(self.chat_windows)} chat windows?")
            
            if result:
                for window in self.chat_windows[:]:  # Copy list to avoid modification during iteration
                    try:
                        window.destroy()
                    except:
                        pass  # Window may already be closed
                
                self.chat_windows.clear()
                messagebox.showinfo("Success", "All chat windows closed.")
            
        except Exception as e:
            logger.error(f"Failed to clear chat windows: {e}")
            messagebox.showerror("Error", f"Failed to clear chat windows: {e}")
    
    def set_rag_system(self, rag_system: VPARAGSystem):
        """Set the RAG system"""
        self.rag_system = rag_system
        logger.info("RAG system connected to menu integration")
    
    def get_llm_manager(self) -> Optional[VPALLMManager]:
        """Get the LLM manager instance"""
        return self.llm_manager


def integrate_rag_llm_menu(main_window_root: tk.Tk, event_bus=None) -> VPARAGLLMMenuIntegration:
    """
    Integrate RAG-LLM menu into existing VPA main window
    
    Args:
        main_window_root: The main window root widget
        event_bus: Optional event bus for integration
        
    Returns:
        VPARAGLLMMenuIntegration instance
    """
    return VPARAGLLMMenuIntegration(main_window_root, event_bus)


if __name__ == "__main__":
    # Test the menu integration
    root = tk.Tk()
    root.title("VPA Main Window Test")
    root.geometry("600x400")
    
    # Add some basic content
    ttk.Label(root, text="VPA Main Window with RAG-LLM Integration", 
              font=("Arial", 14)).pack(pady=20)
    
    # Integrate RAG-LLM menu
    integration = integrate_rag_llm_menu(root)
    
    root.mainloop()
