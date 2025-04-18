"""
Configuration for the Manus Bridge.
This file contains paths and settings for connecting to the Manus system.
"""

import os
from pathlib import Path

# Paths to Manus system components
MANUS_OPT_PATH = os.environ.get(
    "MANUS_OPT_PATH", 
    "/Users/feliperecalde/Downloads/Manual Library/opt"
)
MANUS_OPT2_PATH = os.environ.get(
    "MANUS_OPT2_PATH", 
    "/Users/feliperecalde/Downloads/Manual Library/opt 2"
)
MANUS_OPT3_PATH = os.environ.get(
    "MANUS_OPT3_PATH", 
    "/Users/feliperecalde/Downloads/Manual Library/opt 3"
)

# Manus sandbox runtime path
MANUS_SANDBOX_PATH = os.path.join(MANUS_OPT3_PATH, ".manus", ".sandbox-runtime")

# Manus deployment templates path
MANUS_TEMPLATES_PATH = os.path.join(MANUS_OPT_PATH, ".manus", "deploy", "templates")

# Manus packages path
MANUS_PACKAGES_PATH = os.path.join(MANUS_OPT2_PATH, ".manus", ".packages")

# Database settings
DB_URL = os.environ.get(
    "MANUS_BRIDGE_DB_URL", 
    "sqlite:///./manus_bridge.db"
)

# API settings
API_HOST = os.environ.get("MANUS_BRIDGE_API_HOST", "127.0.0.1")
API_PORT = int(os.environ.get("MANUS_BRIDGE_API_PORT", "8080"))
