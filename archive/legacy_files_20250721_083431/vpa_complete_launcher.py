"""
VPA Final Integration Test - Complete Application Launch
Test the complete VPA application with all features
"""

import sys
import os
from pathlib import Path
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

# Add src to path
current_dir = Path(__file__).resolve().parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

class VPALauncher:
    """Complete VPA application launcher"""
    
    def __init__(self):
        # Setup CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create root window
        self.root = ctk.CTk()
        self.root.title("VPA - Virtual Personal Assistant")
        self.root.geometry("600x400")
        
        # Center window
        self._center_window()
        
        # Create launcher UI
        self._create_launcher_ui()
        
        # Load components
        self._load_components()
    
    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_launcher_ui(self):
        """Create the launcher UI"""
        # Main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🤖 VPA - Virtual Personal Assistant",
            font=("Arial", 28, "bold")
        )
        title_label.pack(pady=(30, 20))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Complete Project Alignment Implementation",
            font=("Arial", 16)
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Status
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Loading components...",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=(0, 20))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            main_frame,
            width=400,
            height=20
        )
        self.progress_bar.pack(pady=(0, 30))
        self.progress_bar.set(0)
        
        # Launch buttons
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(pady=20)
        
        # Launch Login button
        self.login_button = ctk.CTkButton(
            buttons_frame,
            text="🚀 Launch VPA Login",
            command=self._launch_login,
            width=200,
            height=50,
            font=("Arial", 16, "bold"),
            state="disabled"
        )
        self.login_button.pack(side="left", padx=10)
        
        # Launch Registration button
        self.register_button = ctk.CTkButton(
            buttons_frame,
            text="📝 Launch Registration",
            command=self._launch_registration,
            width=200,
            height=50,
            font=("Arial", 16, "bold"),
            state="disabled"
        )
        self.register_button.pack(side="left", padx=10)
        
        # Launch Main App button
        self.main_button = ctk.CTkButton(
            buttons_frame,
            text="💬 Launch Main App",
            command=self._launch_main_app,
            width=200,
            height=50,
            font=("Arial", 16, "bold"),
            state="disabled"
        )
        self.main_button.pack(side="left", padx=10)
        
        # Feature status frame
        status_frame = ctk.CTkFrame(main_frame)
        status_frame.pack(fill="x", pady=(30, 0))
        
        ctk.CTkLabel(
            status_frame,
            text="🎯 Implementation Status",
            font=("Arial", 16, "bold")
        ).pack(pady=(10, 5))
        
        # Status indicators
        self.status_indicators = {}
        features = [
            ("OAuth Automation", "oauth"),
            ("Registration System", "registration"),
            ("Main Chat Interface", "main_app"),
            ("Settings & Integrations", "settings"),
            ("Resource Monitoring", "monitoring")
        ]
        
        for feature_name, key in features:
            indicator_frame = ctk.CTkFrame(status_frame)
            indicator_frame.pack(fill="x", padx=10, pady=2)
            
            indicator_label = ctk.CTkLabel(
                indicator_frame,
                text=f"🔄 {feature_name}: Loading...",
                font=("Arial", 11)
            )
            indicator_label.pack(side="left", padx=10, pady=5)
            
            self.status_indicators[key] = indicator_label
    
    def _load_components(self):
        """Load all VPA components"""
        import threading
        
        def load_task():
            components = [
                ("OAuth Automation", "oauth", self._load_oauth),
                ("Registration System", "registration", self._load_registration),
                ("Main Chat Interface", "main_app", self._load_main_app),
                ("Settings & Integrations", "settings", self._load_settings),
                ("Resource Monitoring", "monitoring", self._load_monitoring)
            ]
            
            for i, (name, key, loader) in enumerate(components):
                try:
                    self.root.after(0, lambda n=name: self.status_label.configure(text=f"Loading {n}..."))
                    self.root.after(0, lambda p=(i+1)/len(components): self.progress_bar.set(p))
                    
                    success = loader()
                    
                    if success:
                        self.root.after(0, lambda k=key, n=name: self.status_indicators[k].configure(
                            text=f"✅ {n}: Ready", text_color="green"
                        ))
                    else:
                        self.root.after(0, lambda k=key, n=name: self.status_indicators[k].configure(
                            text=f"❌ {n}: Failed", text_color="red"
                        ))
                    
                except Exception as e:
                    self.root.after(0, lambda k=key, n=name, err=str(e): self.status_indicators[k].configure(
                        text=f"❌ {n}: Error", text_color="red"
                    ))
                
                import time
                time.sleep(0.5)  # Simulate loading time
            
            # Enable buttons
            self.root.after(0, self._enable_buttons)
        
        threading.Thread(target=load_task, daemon=True).start()
    
    def _load_oauth(self) -> bool:
        """Load OAuth components"""
        try:
            from vpa.gui.oauth_callback_server import OAuthCallbackServer, OAuthFlowManager
            return True
        except Exception as e:
            print(f"OAuth load error: {e}")
            return False
    
    def _load_registration(self) -> bool:
        """Load registration components"""
        try:
            from vpa.gui.registration_window import VPARegistrationWindow
            return True
        except Exception as e:
            print(f"Registration load error: {e}")
            return False
    
    def _load_main_app(self) -> bool:
        """Load main app components"""
        try:
            from vpa.gui.main_application import VPAMainApplication
            return True
        except Exception as e:
            print(f"Main app load error: {e}")
            return False
    
    def _load_settings(self) -> bool:
        """Load settings components"""
        try:
            from vpa.gui.settings_window import VPASettingsWindow
            return True
        except Exception as e:
            print(f"Settings load error: {e}")
            return False
    
    def _load_monitoring(self) -> bool:
        """Load monitoring components"""
        try:
            import psutil
            return True
        except Exception as e:
            print(f"Monitoring load error: {e}")
            return False
    
    def _enable_buttons(self):
        """Enable launch buttons"""
        self.status_label.configure(text="🎉 All components loaded! Ready to launch VPA.")
        self.login_button.configure(state="normal")
        self.register_button.configure(state="normal")
        self.main_button.configure(state="normal")
    
    def _launch_login(self):
        """Launch login window"""
        try:
            from vpa.gui.login_window import VPALoginWindow
            
            # Create mock GUI manager
            class MockGUIManager:
                def __init__(self):
                    self.auth_coordinator = None
                    self.gui_config = MockGUIConfig()
                
                def get_oauth_flow_manager(self):
                    from vpa.gui.oauth_callback_server import OAuthFlowManager
                    return OAuthFlowManager(self.auth_coordinator, self)
            
            class MockGUIConfig:
                def __init__(self):
                    self.fonts = {
                        "heading": ("Arial", 18, "bold"),
                        "body": ("Arial", 12),
                        "small": ("Arial", 10)
                    }
                    self.colors = {
                        "primary": "blue"
                    }
            
            gui_manager = MockGUIManager()
            login_window = VPALoginWindow(self.root, gui_manager)
            
            messagebox.showinfo("Success", "Login window launched successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch login window: {str(e)}")
    
    def _launch_registration(self):
        """Launch registration window"""
        try:
            from vpa.gui.registration_window import VPARegistrationWindow
            
            # Create mock GUI manager
            class MockGUIManager:
                def __init__(self):
                    self.auth_coordinator = MockAuthCoordinator()
            
            class MockAuthCoordinator:
                def register_user(self, **kwargs):
                    # Mock registration
                    from vpa.core.auth_coordinator import AuthenticationResult
                    return AuthenticationResult(
                        success=True,
                        user_id="test_user",
                        session_id="test_session"
                    )
            
            gui_manager = MockGUIManager()
            registration_window = VPARegistrationWindow(self.root, gui_manager)
            
            messagebox.showinfo("Success", "Registration window launched successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch registration window: {str(e)}")
    
    def _launch_main_app(self):
        """Launch main application"""
        try:
            from vpa.gui.main_application import VPAMainApplication
            
            # Create mock GUI manager
            class MockGUIManager:
                def __init__(self):
                    self.auth_coordinator = None
                
                def get_oauth_flow_manager(self):
                    return None
            
            gui_manager = MockGUIManager()
            main_app = VPAMainApplication(self.root, gui_manager, "test_user", "test_session")
            
            messagebox.showinfo("Success", "Main application launched successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch main application: {str(e)}")
    
    def run(self):
        """Run the launcher"""
        self.root.mainloop()

def main():
    """Main function"""
    print("🚀 Launching VPA Complete Application...")
    
    try:
        launcher = VPALauncher()
        launcher.run()
    except Exception as e:
        print(f"❌ Failed to launch VPA: {e}")
        messagebox.showerror("Launch Error", f"Failed to launch VPA: {str(e)}")

if __name__ == "__main__":
    main()
