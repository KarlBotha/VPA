#!/usr/bin/env python3
"""
VPA Launcher Script

This script makes VPA easily accessible without needing to set PYTHONPATH.
Usage: python vpa_launcher.py [VPA_ARGS]
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import and run VPA main
from vpa.__main__ import main

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)