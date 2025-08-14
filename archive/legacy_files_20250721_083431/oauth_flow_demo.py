"""
OAuth Flow Demo
Demonstrates the automated OAuth flow implementation
"""

import tkinter as tk
import customtkinter as ctk
from pathlib import Path
import sys
import webbrowser
import threading
import time

# Add src to path
current_dir = Path(__file__).resolve().parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

class OAuthFlowDemo:
    """Demo of the OAuth flow automation"""
    
    def __init__(self):
        # Setup CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("VPA OAuth Flow Demo")
        self.root.geometry("600x400")
        
        self.create_ui()
        
    def create_ui(self):
        """Create the demo UI"""
        # Main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="OAuth Flow Automation Demo",
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Description
        desc_label = ctk.CTkLabel(
            main_frame,
            text="This demo shows the automated OAuth flow implementation.\n" +
                 "Click a provider button to see the flow in action.\n" +
                 "(Note: No real authentication will occur in this demo)",
            font=("Arial", 14)
        )
        desc_label.pack(pady=(0, 30))
        
        # OAuth buttons
        oauth_frame = ctk.CTkFrame(main_frame)
        oauth_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            oauth_frame,
            text="OAuth Providers",
            font=("Arial", 16, "bold")
        ).pack(pady=(10, 20))
        
        # Google button
        google_button = ctk.CTkButton(
            oauth_frame,
            text="🔗 Sign in with Google",
            command=lambda: self.demo_oauth_flow("Google"),
            fg_color="#db4437",
            hover_color="#c23321",
            width=250,
            height=40
        )
        google_button.pack(pady=5)
        
        # GitHub button
        github_button = ctk.CTkButton(
            oauth_frame,
            text="🔗 Sign in with GitHub",
            command=lambda: self.demo_oauth_flow("GitHub"),
            fg_color="#333333",
            hover_color="#555555",
            width=250,
            height=40
        )
        github_button.pack(pady=5)
        
        # Microsoft button
        microsoft_button = ctk.CTkButton(
            oauth_frame,
            text="🔗 Sign in with Microsoft",
            command=lambda: self.demo_oauth_flow("Microsoft"),
            fg_color="#0078d4",
            hover_color="#106ebe",
            width=250,
            height=40
        )
        microsoft_button.pack(pady=5)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Select an OAuth provider to test the automated flow",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=(20, 10))
        
        # Features box
        features_frame = ctk.CTkFrame(main_frame)
        features_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            features_frame,
            text="✅ Automated OAuth Flow Features:",
            font=("Arial", 14, "bold")
        ).pack(pady=(10, 5))
        
        features_text = """• Automatic browser opening
• Built-in callback server
• No manual code entry required
• Automatic token exchange
• Seamless user experience
• Error handling and timeout protection"""
        
        ctk.CTkLabel(
            features_frame,
            text=features_text,
            font=("Arial", 11),
            justify="left"
        ).pack(pady=(0, 10))
    
    def demo_oauth_flow(self, provider_name: str):
        """Demonstrate OAuth flow for a provider"""
        self.status_label.configure(text=f"🔄 Starting {provider_name} OAuth flow...")
        
        def simulate_oauth():
            # Simulate OAuth flow steps
            steps = [
                f"✓ Starting callback server on localhost:8080",
                f"✓ Generating {provider_name} authorization URL",
                f"✓ Opening browser for user authentication",
                f"✓ Waiting for OAuth callback...",
                f"✓ Received authorization code",
                f"✓ Exchanging code for access token",
                f"✓ {provider_name} authentication completed successfully!"
            ]
            
            for i, step in enumerate(steps):
                time.sleep(0.5)  # Simulate processing time
                self.root.after(0, lambda s=step: self.status_label.configure(text=s))
            
            # Final success message
            self.root.after(0, lambda: self.status_label.configure(
                text=f"✅ {provider_name} OAuth flow completed! (Demo mode)",
                text_color="green"
            ))
        
        # Run simulation in background thread
        threading.Thread(target=simulate_oauth, daemon=True).start()
    
    def run(self):
        """Run the demo"""
        self.root.mainloop()

def main():
    """Main function"""
    print("Starting OAuth Flow Demo...")
    
    demo = OAuthFlowDemo()
    demo.run()

if __name__ == "__main__":
    main()
