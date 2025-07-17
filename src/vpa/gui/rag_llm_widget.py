"""
VPA RAG-LLM UI Integration

This module provides user interface components for the RAG-LLM integration,
enabling real-time AI conversations with knowledge retrieval capabilities.

Features:
- Real-time conversation interface with RAG context
- Streaming response display
- Knowledge source visualization
- Performance metrics display
- Configuration controls
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import asyncio
import threading
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
import json

from ..core.llm import VPALLMManager, VPARAGLLMIntegration, create_rag_llm_integration, LLMProvider
from ..core.rag import VPARAGSystem
from ..core.database import ConversationDatabaseManager

logger = logging.getLogger(__name__)


class RAGLLMChatWidget:
    """
    Advanced chat widget with RAG-LLM integration
    
    Provides real-time AI conversations with knowledge context,
    streaming responses, and performance monitoring.
    """
    
    def __init__(self, parent: tk.Widget, llm_manager: VPALLMManager, 
                 rag_system: Optional[VPARAGSystem] = None):
        """
        Initialize RAG-LLM chat widget
        
        Args:
            parent: Parent tkinter widget
            llm_manager: VPA LLM manager instance
            rag_system: Optional VPA RAG system instance
        """
        self.parent = parent
        self.llm_manager = llm_manager
        self.rag_system = rag_system
        
        # Create RAG-LLM integration
        self.integration = create_rag_llm_integration(llm_manager, rag_system)
        
        # Configuration
        self.user_id = "gui_user"
        self.conversation_id = f"gui_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.use_rag = True
        self.rag_top_k = 3
        
        # UI Components
        self.main_frame: Optional[ttk.Frame] = None
        self.conversation_frame: Optional[ttk.LabelFrame] = None
        self.input_frame: Optional[ttk.Frame] = None
        self.status_frame: Optional[ttk.Frame] = None
        self.config_frame: Optional[ttk.LabelFrame] = None
        
        # Chat components
        self.conversation_text: Optional[scrolledtext.ScrolledText] = None
        self.input_entry: Optional[ttk.Entry] = None
        self.send_button: Optional[ttk.Button] = None
        self.stream_button: Optional[ttk.Button] = None
        
        # Status components
        self.status_label: Optional[ttk.Label] = None
        self.performance_label: Optional[ttk.Label] = None
        self.sources_label: Optional[ttk.Label] = None
        
        # Configuration components
        self.rag_enabled_var = tk.BooleanVar(value=True)
        self.top_k_var = tk.IntVar(value=3)
        self.provider_var = tk.StringVar(value="openai")
        
        # State
        self.is_processing = False
        self.last_response_time = 0
        self.last_sources_count = 0
        
        self._setup_ui()
        logger.info("RAG-LLM Chat Widget initialized")
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Main container
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure grid
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Create sections
        self._create_config_section()
        self._create_conversation_section()
        self._create_input_section()
        self._create_status_section()
    
    def _create_config_section(self):
        """Create configuration controls"""
        self.config_frame = ttk.LabelFrame(self.main_frame, text="RAG-LLM Configuration", padding="5")
        self.config_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        self.config_frame.columnconfigure(1, weight=1)
        
        # RAG enable/disable
        ttk.Label(self.config_frame, text="Enable RAG:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        rag_check = ttk.Checkbutton(self.config_frame, variable=self.rag_enabled_var, 
                                   command=self._on_config_change)
        rag_check.grid(row=0, column=1, sticky=tk.W)
        
        # Top-K configuration
        ttk.Label(self.config_frame, text="Top-K Sources:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        top_k_spin = ttk.Spinbox(self.config_frame, from_=1, to=10, width=5, 
                                textvariable=self.top_k_var, command=self._on_config_change)
        top_k_spin.grid(row=0, column=3, sticky=tk.W)
        
        # Provider selection
        ttk.Label(self.config_frame, text="Provider:").grid(row=0, column=4, sticky=tk.W, padx=(10, 5))
        provider_combo = ttk.Combobox(self.config_frame, textvariable=self.provider_var,
                                     values=["openai", "anthropic", "azure_openai", "local_ollama", "google_gemini"],
                                     state="readonly", width=12)
        provider_combo.grid(row=0, column=5, sticky=tk.W)
        provider_combo.bind("<<ComboboxSelected>>", lambda e: self._on_config_change())
    
    def _create_conversation_section(self):
        """Create conversation display area"""
        self.conversation_frame = ttk.LabelFrame(self.main_frame, text="Conversation", padding="5")
        self.conversation_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 5))
        self.conversation_frame.columnconfigure(0, weight=1)
        self.conversation_frame.rowconfigure(0, weight=1)
        
        # Conversation text area
        self.conversation_text = scrolledtext.ScrolledText(
            self.conversation_frame,
            height=20,
            width=80,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Consolas", 10)
        )
        self.conversation_text.grid(row=0, column=0, sticky="nsew")
        
        # Configure text tags for different message types
        self.conversation_text.tag_configure("user", foreground="blue", font=("Consolas", 10, "bold"))
        self.conversation_text.tag_configure("assistant", foreground="green", font=("Consolas", 10))
        self.conversation_text.tag_configure("system", foreground="orange", font=("Consolas", 10, "italic"))
        self.conversation_text.tag_configure("rag_context", foreground="purple", font=("Consolas", 9, "italic"))
        self.conversation_text.tag_configure("error", foreground="red", font=("Consolas", 10, "bold"))
        self.conversation_text.tag_configure("timestamp", foreground="gray", font=("Consolas", 8))
    
    def _create_input_section(self):
        """Create message input area"""
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        self.input_frame.columnconfigure(0, weight=1)
        
        # Input entry
        self.input_entry = ttk.Entry(self.input_frame, font=("Consolas", 10))
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.input_entry.bind("<Return>", lambda e: self._send_message())
        self.input_entry.bind("<Control-Return>", lambda e: self._stream_message())
        
        # Send button
        self.send_button = ttk.Button(self.input_frame, text="Send", command=self._send_message)
        self.send_button.grid(row=0, column=1, padx=(0, 5))
        
        # Stream button
        self.stream_button = ttk.Button(self.input_frame, text="Stream", command=self._stream_message)
        self.stream_button.grid(row=0, column=2, padx=(0, 5))
        
        # Clear button
        clear_button = ttk.Button(self.input_frame, text="Clear", command=self._clear_conversation)
        clear_button.grid(row=0, column=3)
    
    def _create_status_section(self):
        """Create status information area"""
        self.status_frame = ttk.Frame(self.main_frame)
        self.status_frame.grid(row=3, column=0, sticky="ew")
        self.status_frame.columnconfigure(1, weight=1)
        
        # Status labels
        ttk.Label(self.status_frame, text="Status:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.status_label = ttk.Label(self.status_frame, text="Ready", foreground="green")
        self.status_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(self.status_frame, text="Performance:").grid(row=0, column=2, sticky=tk.W, padx=(10, 5))
        self.performance_label = ttk.Label(self.status_frame, text="N/A")
        self.performance_label.grid(row=0, column=3, sticky=tk.W)
        
        ttk.Label(self.status_frame, text="Sources:").grid(row=0, column=4, sticky=tk.W, padx=(10, 5))
        self.sources_label = ttk.Label(self.status_frame, text="N/A")
        self.sources_label.grid(row=0, column=5, sticky=tk.W)
    
    def _on_config_change(self):
        """Handle configuration changes"""
        self.use_rag = self.rag_enabled_var.get()
        self.rag_top_k = self.top_k_var.get()
        
        # Update integration configuration
        if self.use_rag and self.rag_system:
            self.integration.set_rag_system(self.rag_system)
        
        # Update status
        self._add_system_message(f"Configuration updated: RAG={self.use_rag}, Top-K={self.rag_top_k}, Provider={self.provider_var.get()}")
    
    def _send_message(self):
        """Send a message and get complete response"""
        if self.is_processing or not self.input_entry:
            return
        
        message = self.input_entry.get().strip()
        if not message:
            return
        
        self.input_entry.delete(0, tk.END)
        self._add_user_message(message)
        
        # Process in background thread
        threading.Thread(target=self._process_message, args=(message, False), daemon=True).start()
    
    def _stream_message(self):
        """Send a message and get streaming response"""
        if self.is_processing or not self.input_entry:
            return
        
        message = self.input_entry.get().strip()
        if not message:
            return
        
        self.input_entry.delete(0, tk.END)
        self._add_user_message(message)
        
        # Process in background thread
        threading.Thread(target=self._process_message, args=(message, True), daemon=True).start()
    
    def _process_message(self, message: str, stream: bool = False):
        """Process message with RAG-LLM integration"""
        try:
            self._set_processing_state(True)
            
            if stream:
                self._process_streaming_message(message)
            else:
                self._process_complete_message(message)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self._add_error_message(f"Error: {e}")
        finally:
            self._set_processing_state(False)
    
    def _process_complete_message(self, message: str):
        """Process message and get complete response"""
        # Create event loop for async operation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Get provider enum
            provider = None
            try:
                provider = LLMProvider(self.provider_var.get())
            except ValueError:
                provider = LLMProvider.OPENAI  # Default fallback
            
            # Generate enhanced response
            response = loop.run_until_complete(
                self.integration.generate_enhanced_response(
                    user_id=self.user_id,
                    user_message=message,
                    conversation_id=self.conversation_id,
                    provider=provider,
                    use_rag=self.use_rag,
                    rag_top_k=self.rag_top_k
                )
            )
            
            if response.get("success"):
                # Add RAG context info if available
                if response.get("rag_context_used"):
                    sources_info = f"[RAG: {response.get('rag_sources_count', 0)} sources, {response.get('rag_retrieval_time', 0):.3f}s]"
                    self._add_rag_context_message(sources_info)
                
                # Add assistant response
                self._add_assistant_message(response.get("response", "No response"))
                
                # Update performance metrics
                self._update_performance_display(response)
                
                # Show source details if available
                sources = response.get("rag_sources", [])
                if sources:
                    self._show_source_details(sources)
            else:
                self._add_error_message(f"Error: {response.get('error', 'Unknown error')}")
                
        finally:
            loop.close()
    
    def _process_streaming_message(self, message: str):
        """Process message with streaming response"""
        # Create event loop for async operation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Get provider enum
            provider = None
            try:
                provider = LLMProvider(self.provider_var.get())
            except ValueError:
                provider = LLMProvider.OPENAI  # Default fallback
            
            # Start streaming response
            self._add_assistant_message("", end_line=False)  # Start response
            
            async def stream_handler():
                async for chunk in self.integration.stream_enhanced_response(
                    user_id=self.user_id,
                    user_message=message,
                    conversation_id=self.conversation_id,
                    provider=provider,
                    use_rag=self.use_rag,
                    rag_top_k=self.rag_top_k
                ):
                    if chunk["type"] == "rag_context":
                        if chunk["rag_sources_count"] > 0:
                            sources_info = f"[RAG: {chunk['rag_sources_count']} sources, {chunk['rag_retrieval_time']:.3f}s]"
                            self._add_rag_context_message(sources_info)
                    elif chunk["type"] == "llm_chunk":
                        self._append_to_last_message(chunk["content"])
                    elif chunk["type"] == "error":
                        self._add_error_message(f"Stream error: {chunk.get('error', 'Unknown error')}")
            
            loop.run_until_complete(stream_handler())
            
        finally:
            loop.close()
    
    def _add_user_message(self, message: str):
        """Add user message to conversation"""
        self._add_message("You", message, "user")
    
    def _add_assistant_message(self, message: str, end_line: bool = True):
        """Add assistant message to conversation"""
        self._add_message("Assistant", message, "assistant", end_line)
    
    def _add_system_message(self, message: str):
        """Add system message to conversation"""
        self._add_message("System", message, "system")
    
    def _add_rag_context_message(self, message: str):
        """Add RAG context message to conversation"""
        self._add_message("RAG", message, "rag_context")
    
    def _add_error_message(self, message: str):
        """Add error message to conversation"""
        self._add_message("Error", message, "error")
    
    def _add_message(self, sender: str, message: str, tag: str, end_line: bool = True):
        """Add a message to the conversation display"""
        if not self.conversation_text:
            return
        
        def update_ui():
            if not self.conversation_text:
                return
                
            self.conversation_text.config(state=tk.NORMAL)
            
            # Add timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.conversation_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
            
            # Add sender and message
            self.conversation_text.insert(tk.END, f"{sender}: ", tag)
            self.conversation_text.insert(tk.END, message)
            
            if end_line:
                self.conversation_text.insert(tk.END, "\\n\\n")
            
            self.conversation_text.config(state=tk.DISABLED)
            self.conversation_text.see(tk.END)
        
        # Ensure UI update happens on main thread
        self.parent.after(0, update_ui)
    
    def _append_to_last_message(self, text: str):
        """Append text to the last message (for streaming)"""
        if not self.conversation_text:
            return
        
        def update_ui():
            if not self.conversation_text:
                return
                
            self.conversation_text.config(state=tk.NORMAL)
            self.conversation_text.insert(tk.END, text)
            self.conversation_text.config(state=tk.DISABLED)
            self.conversation_text.see(tk.END)
        
        # Ensure UI update happens on main thread
        self.parent.after(0, update_ui)
    
    def _clear_conversation(self):
        """Clear the conversation display"""
        if self.conversation_text:
            self.conversation_text.config(state=tk.NORMAL)
            self.conversation_text.delete(1.0, tk.END)
            self.conversation_text.config(state=tk.DISABLED)
        
        # Clear history
        if self.integration.llm_manager:
            self.integration.llm_manager.clear_conversation_history(self.user_id, self.conversation_id)
        
        self._add_system_message("Conversation cleared")
    
    def _set_processing_state(self, processing: bool):
        """Set the processing state and update UI accordingly"""
        self.is_processing = processing
        
        def update_ui():
            if self.send_button:
                self.send_button.config(state=tk.DISABLED if processing else tk.NORMAL)
            if self.stream_button:
                self.stream_button.config(state=tk.DISABLED if processing else tk.NORMAL)
            if self.status_label:
                self.status_label.config(
                    text="Processing..." if processing else "Ready",
                    foreground="orange" if processing else "green"
                )
        
        self.parent.after(0, update_ui)
    
    def _update_performance_display(self, response: Dict[str, Any]):
        """Update performance metrics display"""
        total_time = response.get("total_processing_time", 0)
        rag_time = response.get("rag_retrieval_time", 0)
        llm_time = response.get("llm_generation_time", 0)
        sources_count = response.get("rag_sources_count", 0)
        
        self.last_response_time = total_time
        self.last_sources_count = sources_count
        
        def update_ui():
            if self.performance_label:
                perf_text = f"Total: {total_time:.3f}s (RAG: {rag_time:.3f}s, LLM: {llm_time:.3f}s)"
                self.performance_label.config(text=perf_text)
            
            if self.sources_label:
                sources_text = f"{sources_count} sources" if sources_count > 0 else "No sources"
                self.sources_label.config(text=sources_text)
        
        self.parent.after(0, update_ui)
    
    def _show_source_details(self, sources: List[Dict[str, Any]]):
        """Show detailed source information in a popup"""
        if not sources:
            return
        
        # Create popup window
        popup = tk.Toplevel(self.parent)
        popup.title("RAG Sources")
        popup.geometry("600x400")
        try:
            popup.transient(self.parent)
        except:
            pass  # Ignore transient errors
        popup.grab_set()
        
        # Create scrolled text for sources
        sources_text = scrolledtext.ScrolledText(popup, wrap=tk.WORD, font=("Consolas", 9))
        sources_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add source details
        sources_text.insert(tk.END, f"Retrieved {len(sources)} relevant sources:\\n\\n")
        
        for i, source in enumerate(sources, 1):
            sources_text.insert(tk.END, f"Source {i}:\\n")
            sources_text.insert(tk.END, f"  Document ID: {source.get('document_id', 'Unknown')}\\n")
            sources_text.insert(tk.END, f"  Similarity: {source.get('similarity', 0):.3f}\\n")
            sources_text.insert(tk.END, f"  Preview: {source.get('content_preview', 'No preview')}\\n")
            
            metadata = source.get('metadata', {})
            if metadata:
                sources_text.insert(tk.END, f"  Metadata: {json.dumps(metadata, indent=2)}\\n")
            
            sources_text.insert(tk.END, "\\n" + "-"*50 + "\\n\\n")
        
        sources_text.config(state=tk.DISABLED)
        
        # Close button
        close_btn = ttk.Button(popup, text="Close", command=popup.destroy)
        close_btn.pack(pady=5)
    
    def set_rag_system(self, rag_system: VPARAGSystem):
        """Set or update the RAG system"""
        self.rag_system = rag_system
        if self.integration:
            self.integration.set_rag_system(rag_system)
        self._add_system_message("RAG system connected")
    
    def get_widget(self) -> Optional[ttk.Frame]:
        """Get the main widget frame"""
        return self.main_frame


class RAGLLMIntegrationDialog:
    """
    Modal dialog for RAG-LLM integration setup and testing
    """
    
    def __init__(self, parent: tk.Widget, app_instance):
        """Initialize integration dialog"""
        self.parent = parent
        self.app = app_instance
        self.result = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("VPA RAG-LLM Integration")
        self.dialog.geometry("900x700")
        try:
            self.dialog.transient(parent)
        except:
            pass  # Ignore transient errors
        self.dialog.grab_set()
        
        # Initialize components
        self.llm_manager = None
        self.rag_system = None
        self.chat_widget = None
        
        self._setup_ui()
        self._initialize_systems()
    
    def _setup_ui(self):
        """Setup dialog UI"""
        # Main container
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="VPA RAG-LLM Integration Test", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_text = ("This interface demonstrates the RAG-LLM integration capabilities. "
                    "You can test AI conversations with knowledge retrieval, "
                    "streaming responses, and performance monitoring.")
        desc_label = ttk.Label(main_frame, text=desc_text, wraplength=850)
        desc_label.pack(pady=(0, 15))
        
        # Chat widget container
        chat_frame = ttk.Frame(main_frame)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Initialize chat widget placeholder
        self.chat_container = chat_frame
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Reset Systems", command=self._reset_systems).pack(side=tk.RIGHT)
    
    def _initialize_systems(self):
        """Initialize LLM and RAG systems"""
        try:
            # Create LLM manager
            from ..core.llm import create_llm_manager
            self.llm_manager = create_llm_manager()
            
            # Create RAG system (mock for now)
            # In production, this would use the real database
            self.rag_system = None  # Will be set up when database is available
            
            # Create chat widget
            self.chat_widget = RAGLLMChatWidget(
                self.chat_container, 
                self.llm_manager, 
                self.rag_system
            )
            
            logger.info("RAG-LLM Integration Dialog initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG-LLM systems: {e}")
            messagebox.showerror("Initialization Error", 
                               f"Failed to initialize systems: {e}")
    
    def _reset_systems(self):
        """Reset and reinitialize systems"""
        try:
            if self.chat_widget and self.chat_widget.main_frame:
                self.chat_widget.main_frame.destroy()
            
            self._initialize_systems()
            messagebox.showinfo("Reset Complete", "Systems have been reset successfully")
            
        except Exception as e:
            logger.error(f"Failed to reset systems: {e}")
            messagebox.showerror("Reset Error", f"Failed to reset systems: {e}")


def create_rag_llm_integration_dialog(parent: tk.Widget, app_instance) -> RAGLLMIntegrationDialog:
    """
    Create and show RAG-LLM integration dialog
    
    Args:
        parent: Parent widget
        app_instance: VPA application instance
        
    Returns:
        RAGLLMIntegrationDialog instance
    """
    return RAGLLMIntegrationDialog(parent, app_instance)


if __name__ == "__main__":
    # Test the RAG-LLM UI components
    root = tk.Tk()
    root.title("VPA RAG-LLM UI Test")
    root.geometry("1000x800")
    
    try:
        # Create test LLM manager
        from ..core.llm import create_llm_manager
        llm_manager = create_llm_manager()
        
        # Create chat widget
        chat_widget = RAGLLMChatWidget(root, llm_manager)
        
        root.mainloop()
        
    except Exception as e:
        print(f"Test failed: {e}")
