"""
Path helper for PyInstaller compatibility
==========================================
Provides correct BASE_DIR whether running as script or frozen executable.
"""

import os
import sys


def get_base_dir():
    """
    Get the base directory for the application.
    
    Works correctly both when:
    - Running as a Python script (development)
    - Running as a PyInstaller executable (production)
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))


# Use this instead of os.path.dirname(os.path.abspath(__file__))
BASE_DIR = get_base_dir()
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Ensure directories exist
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
