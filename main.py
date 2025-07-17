#!/usr/bin/env python3
"""
VPA - Virtual Personal Assistant
Simple launcher that delegates to the main package
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import and run the main application
from vpa.__main__ import main

def launch_cli() -> int:
    """Launch CLI mode wrapper"""
    from vpa.__main__ import launch_cli as _launch_cli
    return _launch_cli()

def launch_gui() -> int:
    """Launch GUI mode wrapper"""
    from vpa.core.app import App
    from vpa.__main__ import launch_gui as _launch_gui
    app = App()
    return _launch_gui(app)

if __name__ == "__main__":
    sys.exit(main())
