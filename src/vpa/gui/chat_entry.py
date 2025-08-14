import json, os
from ..util.dynload import load_symbol_from_paths, get_recovery_map, resolve_relative_path

def run_gui(recover_map_path="tools/recover/recover_map.json"):
    """Launch VPA GUI using recovered components or fallback"""
    
    # Try native import first
    try:
        from vpa.gui.main_application import VPAApplication  # type: ignore
        app = VPAApplication()
        app.run()
        return True
    except ImportError:
        pass
    
    # Try recovery from archive
    recovery_map = get_recovery_map(recover_map_path)
    
    # Try to find GUI manager or main window
    gui_candidates = (
        recovery_map.get("gui_manager", []) + 
        recovery_map.get("main_window", []) +
        recovery_map.get("chat_interface", [])
    )
    
    if gui_candidates:
        # Convert relative paths to absolute
        gui_candidates = [resolve_relative_path(p) for p in gui_candidates]
        
        # Try VPAGUIManager first
        gui_manager = load_symbol_from_paths("VPAGUIManager", gui_candidates)
        if gui_manager:
            try:
                manager = gui_manager()
                if hasattr(manager, 'run'):
                    manager.run()
                elif hasattr(manager, 'start'):
                    manager.start()
                elif hasattr(manager, 'show'):
                    manager.show()
                return True
            except Exception as e:
                print(f"GUI Manager failed: {e}")
        
        # Try MainWindow classes
        for class_name in ["MainWindow", "VPAMainWindow", "ChatWindow", "ChatInterface"]:
            window_class = load_symbol_from_paths(class_name, gui_candidates)
            if window_class:
                try:
                    window = window_class()
                    if hasattr(window, 'mainloop'):
                        window.mainloop()
                    elif hasattr(window, 'show'):
                        window.show()
                        # Keep window alive
                        if hasattr(window, 'exec_'):
                            window.exec_()
                    return True
                except Exception as e:
                    print(f"{class_name} failed: {e}")
    
    # Fallback to basic tkinter GUI
    return run_fallback_gui()

def run_fallback_gui():
    """Simple tkinter GUI fallback"""
    try:
        import tkinter as tk
        from tkinter import messagebox, scrolledtext
        
        class VPAFallbackGUI:
            def __init__(self):
                self.root = tk.Tk()
                self.root.title("VPA - Virtual Personal Assistant")
                self.root.geometry("600x400")
                
                self.setup_ui()
            
            def setup_ui(self):
                # Main frame
                main_frame = tk.Frame(self.root, padx=10, pady=10)
                main_frame.pack(fill=tk.BOTH, expand=True)
                
                # Title
                title = tk.Label(main_frame, text="VPA - Virtual Personal Assistant", 
                               font=("Arial", 16, "bold"))
                title.pack(pady=(0, 10))
                
                # Status
                status = tk.Label(main_frame, text="GUI Mode: Fallback Interface", 
                                fg="orange")
                status.pack()
                
                # Chat area
                chat_label = tk.Label(main_frame, text="Chat Area:")
                chat_label.pack(anchor="w", pady=(20, 5))
                
                self.chat_area = scrolledtext.ScrolledText(main_frame, height=15, width=70)
                self.chat_area.pack(fill=tk.BOTH, expand=True)
                
                # Add welcome message
                self.chat_area.insert(tk.END, "Welcome to VPA!\n")
                self.chat_area.insert(tk.END, "This is a fallback GUI interface.\n")
                self.chat_area.insert(tk.END, "Full GUI components are being recovered...\n\n")
                
                # Input frame
                input_frame = tk.Frame(main_frame)
                input_frame.pack(fill=tk.X, pady=(10, 0))
                
                input_label = tk.Label(input_frame, text="Input:")
                input_label.pack(anchor="w")
                
                self.input_entry = tk.Entry(input_frame, width=50)
                self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
                self.input_entry.bind("<Return>", self.send_message)
                
                send_btn = tk.Button(input_frame, text="Send", command=self.send_message)
                send_btn.pack(side=tk.RIGHT)
                
                # Menu
                menubar = tk.Menu(self.root)
                self.root.config(menu=menubar)
                
                file_menu = tk.Menu(menubar, tearoff=0)
                menubar.add_cascade(label="File", menu=file_menu)
                file_menu.add_command(label="Settings", command=self.show_settings)
                file_menu.add_separator()
                file_menu.add_command(label="Exit", command=self.root.quit)
                
                help_menu = tk.Menu(menubar, tearoff=0)
                menubar.add_cascade(label="Help", menu=help_menu)
                help_menu.add_command(label="About", command=self.show_about)
            
            def send_message(self, event=None):
                message = self.input_entry.get().strip()
                if message:
                    self.chat_area.insert(tk.END, f"You: {message}\n")
                    self.chat_area.insert(tk.END, f"VPA: Echo - {message}\n\n")
                    self.chat_area.see(tk.END)
                    self.input_entry.delete(0, tk.END)
            
            def show_settings(self):
                messagebox.showinfo("Settings", "Settings panel is being recovered from archives...")
            
            def show_about(self):
                messagebox.showinfo("About VPA", 
                    "VPA - Virtual Personal Assistant\n\n"
                    "Version: 0.1.0-Recovery\n"
                    "Mode: Fallback GUI\n\n"
                    "Full GUI components are being restored from archives.")
            
            def run(self):
                self.root.mainloop()
        
        gui = VPAFallbackGUI()
        gui.run()
        return True
        
    except Exception as e:
        print(f"Fallback GUI failed: {e}")
        return False

if __name__ == "__main__":
    run_gui()
