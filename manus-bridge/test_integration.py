#!/usr/bin/env python
"""
Test script for Manus Bridge integration with manus-manager.

This script tests the integration between Manus Bridge and manus-manager
by simulating agent operations.
"""

import os
import sys
import json
import argparse
import requests
import time
from pathlib import Path

def test_manus_bridge_api(api_url):
    """Test the Manus Bridge API."""
    print(f"Testing Manus Bridge API at {api_url}...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{api_url}/health")
        if response.status_code == 200:
            print("✅ Health check successful")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False
    
    # Test templates endpoint
    try:
        response = requests.get(f"{api_url}/templates")
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ Templates endpoint successful: {len(templates)} templates found")
        else:
            print(f"❌ Templates endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Templates endpoint failed: {str(e)}")
        return False
    
    return True

def test_agent_operations(api_url):
    """Test agent operations using the Manus Bridge API."""
    print("\nTesting agent operations...")
    
    # Create a test agent configuration
    agent_config = {
        "id": 999,
        "name": "Test Agent",
        "description": "A test agent for Manus Bridge",
        "owner_id": 1,
        "api_key": "test_api_key",
        "instance_url": "http://localhost:8000",
        "max_tasks": 5
    }
    
    # Test starting an agent
    try:
        response = requests.post(
            f"{api_url}/agents/start",
            json=agent_config
        )
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "running":
                print("✅ Agent start successful")
            else:
                print(f"❌ Agent start failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Agent start failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Agent start failed: {str(e)}")
        return False
    
    # Wait a moment for the agent to start
    time.sleep(1)
    
    # Test getting agent status
    try:
        response = requests.get(f"{api_url}/agents/999/status")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Agent status check successful: {result.get('status')}")
        else:
            print(f"❌ Agent status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Agent status check failed: {str(e)}")
        return False
    
    # Test pausing the agent
    try:
        response = requests.post(f"{api_url}/agents/999/pause")
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "paused":
                print("✅ Agent pause successful")
            else:
                print(f"❌ Agent pause failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Agent pause failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Agent pause failed: {str(e)}")
        return False
    
    # Wait a moment for the agent to pause
    time.sleep(1)
    
    # Test resuming the agent
    try:
        response = requests.post(f"{api_url}/agents/999/resume")
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "running":
                print("✅ Agent resume successful")
            else:
                print(f"❌ Agent resume failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Agent resume failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Agent resume failed: {str(e)}")
        return False
    
    # Wait a moment for the agent to resume
    time.sleep(1)
    
    # Test stopping the agent
    try:
        response = requests.post(f"{api_url}/agents/999/stop")
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "stopped":
                print("✅ Agent stop successful")
            else:
                print(f"❌ Agent stop failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Agent stop failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Agent stop failed: {str(e)}")
        return False
    
    return True

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test Manus Bridge integration")
    parser.add_argument(
        "--api-url",
        default="http://localhost:8080",
        help="URL of the Manus Bridge API"
    )
    parser.add_argument(
        "--manus-manager-path",
        help="Path to manus-manager installation"
    )
    args = parser.parse_args()
    
    # Test Manus Bridge API
    if not test_manus_bridge_api(args.api_url):
        print("\n❌ Manus Bridge API tests failed")
        return 1
    
    # Test agent operations
    if not test_agent_operations(args.api_url):
        print("\n❌ Agent operations tests failed")
        return 1
    
    print("\n✅ All tests passed successfully!")
    
    # If manus-manager path is provided, suggest integration
    if args.manus_manager_path:
        print(f"\nTo integrate with manus-manager at {args.manus_manager_path}:")
        print(f"  python integration.py --manus-manager-path {args.manus_manager_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
