#!/usr/bin/env python3
"""
VPA - Virtual Personal Assistant
Main Application Launcher

This is the primary entry point for the VPA application.
Supports both CLI and GUI modes with proper initialization.
"""

import sys
import os
import logging
import asyncio
import argparse
from pathlib import Path
from typing import Optional

# Add src directory to Python path if needed
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from vpa.core.app import App
from vpa.cli.main import cli


def setup_logging(level: str = "INFO") -> None:
    """Setup basic logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(project_root / "logs" / "vpa.log", mode='a')
        ]
    )


def check_environment() -> bool:
    """Check if the environment is properly configured"""
    logger = logging.getLogger(__name__)
    
    # Check Python version
    if sys.version_info < (3, 9):
        logger.error("Python 3.9 or higher is required")
        return False
    
    # Create logs directory if it doesn't exist
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Check if running in virtual environment (recommended)
    if not hasattr(sys, 'real_prefix') and not sys.base_prefix != sys.prefix:
        logger.warning("Not running in virtual environment - this is not recommended")
    
    logger.info("Environment check passed")
    return True


def launch_gui(app: App) -> int:
    """Launch the GUI application"""
    logger = logging.getLogger(__name__)
    
    try:
        # Import GUI components
        from vpa.gui.main_window import VPAMainWindow
        
        logger.info("🚀 Starting VPA GUI Application...")
        
        # Initialize the app
        app.initialize()
        app.start()
        
        # Create and run GUI
        main_window = VPAMainWindow(app)
        main_window.run()
        
        # Cleanup
        app.stop()
        logger.info("✅ VPA GUI Application stopped")
        return 0
        
    except ImportError as e:
        logger.error(f"❌ GUI components not available: {e}")
        logger.info("💡 Try running in CLI mode with --cli flag")
        return 1
    except Exception as e:
        logger.error(f"❌ GUI application failed: {e}")
        return 1


def launch_cli(config_path: Optional[str] = None) -> int:
    """Launch the CLI application"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("🖥️ Starting VPA CLI Application...")
        
        # Use the existing CLI system
        sys.argv = ['vpa-cli'] + (sys.argv[1:] if len(sys.argv) > 1 else ['--help'])
        cli()
        return 0
        
    except Exception as e:
        logger.error(f"❌ CLI application failed: {e}")
        return 1


def main() -> int:
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="VPA - Virtual Personal Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Launch GUI (default)
  %(prog)s --cli              # Launch CLI interface
  %(prog)s --gui              # Launch GUI explicitly
  %(prog)s --log-level DEBUG  # Set debug logging
  %(prog)s --config myconfig.yaml  # Use custom config
        """
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Launch in CLI mode'
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Launch in GUI mode (default)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set logging level'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='VPA 0.1.0 - Phase 2'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("🤖 VPA - Virtual Personal Assistant")
    logger.info("📦 Version: 0.1.0 - Phase 2")
    logger.info("🐍 Python: %s", sys.version.split()[0])
    logger.info("📁 Project Root: %s", project_root)
    logger.info("=" * 60)
    
    # Environment check
    if not check_environment():
        logger.error("❌ Environment check failed")
        return 1
    
    try:
        # Create VPA app instance
        app = App(config_path=args.config)
        
        # Determine launch mode
        if args.cli:
            mode = "CLI"
            exit_code = launch_cli(args.config)
        elif args.gui:
            mode = "GUI"
            exit_code = launch_gui(app)
        else:
            # Default to GUI, fallback to CLI if GUI not available
            mode = "GUI (with CLI fallback)"
            exit_code = launch_gui(app)
            if exit_code != 0:
                logger.info("🔄 Falling back to CLI mode...")
                exit_code = launch_cli(args.config)
        
        logger.info(f"🏁 VPA {mode} mode exited with code: {exit_code}")
        return exit_code
        
    except KeyboardInterrupt:
        logger.info("⌨️ Interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"💥 Critical error: {e}")
        logger.debug("Full traceback:", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
