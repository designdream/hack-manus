#!/usr/bin/env python
"""
Run script for Manus Bridge.

This script starts the Manus Bridge API server.
"""

import os
import sys
import argparse
from manus_bridge.api import start_server

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run Manus Bridge API server")
    parser.add_argument(
        "--host", 
        default=os.environ.get("MANUS_BRIDGE_API_HOST", "127.0.0.1"),
        help="Host to bind the API server to"
    )
    parser.add_argument(
        "--port", 
        type=int,
        default=int(os.environ.get("MANUS_BRIDGE_API_PORT", "8080")),
        help="Port to bind the API server to"
    )
    args = parser.parse_args()
    
    # Set environment variables
    os.environ["MANUS_BRIDGE_API_HOST"] = args.host
    os.environ["MANUS_BRIDGE_API_PORT"] = str(args.port)
    
    # Start the server
    print(f"Starting Manus Bridge API server at {args.host}:{args.port}")
    start_server()

if __name__ == "__main__":
    main()
