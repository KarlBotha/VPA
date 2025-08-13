"""
VPA GUI Test Application
Test the GUI components and integration
"""

import customtkinter as ctk
import tkinter as tk
from pathlib import Path
import sys
import os

# Add the src directory to the Python path
current_dir = Path(__file__).resolve().parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from vpa.gui.gui_manager import VPAGUIManager
from vpa.core.auth_coordinator import VPAAuthenticationCoordinator
from vpa.core.config import SecureConfigManager
from vpa.core.database import ConversationDatabaseManager
from vpa.core.logging import get_structured_logger

logger = get_structured_logger(__name__)

class VPAGUITestApp:
    """Test application for VPA GUI components"""
    
    def __init__(self):
        self.logger = logger
        
        # Initialize core components
        self.config_manager = SecureConfigManager()
        self.database_manager = ConversationDatabaseManager()
        self.auth_coordinator = VPAAuthenticationCoordinator(
            self.database_manager,
            self.config_manager
        )
        
        # Initialize GUI manager
        self.gui_manager = VPAGUIManager(
            self.auth_coordinator,
            self.config_manager,
            self.database_manager
        )
        
        self.logger.info("VPA GUI test application initialized")
    
    def run(self):
        """Run the test application"""
        try:
            self.logger.info("Starting VPA GUI test application")
            
            # Start the GUI application (which includes showing login window)
            self.gui_manager.start_gui()
            
        except Exception as e:
            self.logger.error(f"Failed to run GUI test application: {e}")
            print(f"Error: {e}")
            return False
        
        return True

def main():
    """Main entry point for the test application"""
    try:
        app = VPAGUITestApp()
        success = app.run()
        
        if success:
            print("GUI test application completed successfully")
        else:
            print("GUI test application failed")
            
    except Exception as e:
        print(f"Failed to start GUI test application: {e}")

if __name__ == "__main__":
    main()
