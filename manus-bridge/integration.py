"""
Integration script for connecting manus-manager to Manus Bridge.

This script modifies the manus-manager backend to use the Manus Bridge
for agent management operations.
"""

import os
import sys
import shutil
import argparse
import requests
from pathlib import Path

def check_manus_manager_path(path):
    """Check if the provided path is a valid manus-manager installation."""
    if not os.path.exists(path):
        print(f"Error: Path does not exist: {path}")
        return False
    
    backend_path = os.path.join(path, "backend")
    if not os.path.exists(backend_path):
        print(f"Error: Backend directory not found at: {backend_path}")
        return False
    
    services_path = os.path.join(backend_path, "app", "services")
    if not os.path.exists(services_path):
        print(f"Error: Services directory not found at: {services_path}")
        return False
    
    return True

def backup_file(file_path):
    """Create a backup of a file."""
    backup_path = f"{file_path}.bak"
    if os.path.exists(file_path):
        shutil.copy2(file_path, backup_path)
        print(f"Created backup: {backup_path}")
    return backup_path

def patch_agent_service(manus_manager_path):
    """Patch the agent_service.py file to use Manus Bridge."""
    agent_service_path = os.path.join(
        manus_manager_path, "backend", "app", "services", "agent_service.py"
    )
    
    # Backup the original file
    backup_file(agent_service_path)
    
    # Read the original file
    with open(agent_service_path, "r") as f:
        content = f.read()
    
    # Add imports for Manus Bridge
    bridge_import = """
import requests
import os
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base_class import Base
from app.models.models import Agent, AgentStatus

# Manus Bridge API settings
MANUS_BRIDGE_API_URL = os.environ.get("MANUS_BRIDGE_API_URL", "http://localhost:8080")
"""
    
    # Replace the imports
    content = content.replace(
        "from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union\nfrom fastapi.encoders import jsonable_encoder\nfrom pydantic import BaseModel\nfrom sqlalchemy.orm import Session\n\nfrom app.db.base_class import Base\nfrom app.models.models import Agent, AgentStatus",
        bridge_import
    )
    
    # Replace the start_agent method
    start_agent_method = '''    def start_agent(self, db: Session, *, agent: Agent) -> Agent:
        """
        Start agent using Manus Bridge API
        """
        try:'''
            # Prepare agent config for Manus Bridge
            agent_config = {
                "id": agent.id,
                "name": agent.name,
                "description": agent.description,
                "owner_id": agent.owner_id,
                "api_key": agent.api_key,
                "instance_url": agent.instance_url,
                "max_tasks": agent.max_tasks
            }
            
            # Call Manus Bridge API to start the agent
            response = requests.post(
                f"{MANUS_BRIDGE_API_URL}/agents/start",
                json=agent_config
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "running":
                    agent.status = AgentStatus.RUNNING
                    db.add(agent)
                    db.commit()
                    db.refresh(agent)
                else:
                    print(f"Failed to start agent: {result.get('error', 'Unknown error')}")
            else:
                print(f"Failed to start agent: {response.status_code}")
                
        except Exception as e:
            print(f"Error starting agent: {str(e)}")
            
        return agent"""
    
    # Replace the original method
    content = content.replace(
        """    def start_agent(self, db: Session, *, agent: Agent) -> Agent:
        """
        Start agent
        """
        # Here we would implement the actual logic to start a Manus agent
        # For now, we just update the status
        agent.status = AgentStatus.RUNNING
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent""",
        start_agent_method
    )
    
    # Replace the stop_agent method
    stop_agent_method = '''    def stop_agent(self, db: Session, *, agent: Agent) -> Agent:
        """
        Stop agent using Manus Bridge API
        """
        try:'''
            # Call Manus Bridge API to stop the agent
            response = requests.post(
                f"{MANUS_BRIDGE_API_URL}/agents/{agent.id}/stop"
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "stopped":
                    agent.status = AgentStatus.IDLE
                    db.add(agent)
                    db.commit()
                    db.refresh(agent)
                else:
                    print(f"Failed to stop agent: {result.get('error', 'Unknown error')}")
            else:
                print(f"Failed to stop agent: {response.status_code}")
                
        except Exception as e:
            print(f"Error stopping agent: {str(e)}")
            
        return agent"""
    
    # Replace the original method
    content = content.replace(
        """    def stop_agent(self, db: Session, *, agent: Agent) -> Agent:
        """
        Stop agent
        """
        # Here we would implement the actual logic to stop a Manus agent
        # For now, we just update the status
        agent.status = AgentStatus.IDLE
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent""",
        stop_agent_method
    )
    
    # Replace the pause_agent method
    pause_agent_method = '''    def pause_agent(self, db: Session, *, agent: Agent) -> Agent:
        """
        Pause agent using Manus Bridge API
        """
        try:'''
            # Call Manus Bridge API to pause the agent
            response = requests.post(
                f"{MANUS_BRIDGE_API_URL}/agents/{agent.id}/pause"
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "paused":
                    agent.status = AgentStatus.PAUSED
                    db.add(agent)
                    db.commit()
                    db.refresh(agent)
                else:
                    print(f"Failed to pause agent: {result.get('error', 'Unknown error')}")
            else:
                print(f"Failed to pause agent: {response.status_code}")
                
        except Exception as e:
            print(f"Error pausing agent: {str(e)}")
            
        return agent"""
    
    # Replace the original method
    content = content.replace(
        """    def pause_agent(self, db: Session, *, agent: Agent) -> Agent:
        """
        Pause agent
        """
        # Here we would implement the actual logic to pause a Manus agent
        # For now, we just update the status
        agent.status = AgentStatus.PAUSED
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent""",
        pause_agent_method
    )
    
    # Write the modified content back to the file
    with open(agent_service_path, "w") as f:
        f.write(content)
    
    print(f"Patched agent service: {agent_service_path}")

def create_manus_bridge_api_client(manus_manager_path):
    """Create a client for the Manus Bridge API."""
    client_path = os.path.join(
        manus_manager_path, "backend", "app", "services", "manus_bridge_client.py"
    )
    
    client_content = """\"\"\"
Manus Bridge API Client.

This module provides a client for interacting with the Manus Bridge API.
\"\"\"

import os
import requests
from typing import Dict, List, Optional, Any

# Manus Bridge API settings
MANUS_BRIDGE_API_URL = os.environ.get("MANUS_BRIDGE_API_URL", "http://localhost:8080")

class ManusBridgeClient:
    \"\"\"Client for the Manus Bridge API.\"\"\"
    
    def __init__(self, api_url=None):
        \"\"\"Initialize the client.\"\"\"
        self.api_url = api_url or MANUS_BRIDGE_API_URL
    
    def get_health(self):
        \"\"\"Check the health of the Manus Bridge API.\"\"\"
        response = requests.get(f"{self.api_url}/health")
        return response.json()
    
    def start_agent(self, agent_config):
        \"\"\"Start a Manus agent.\"\"\"
        response = requests.post(
            f"{self.api_url}/agents/start",
            json=agent_config
        )
        return response.json()
    
    def stop_agent(self, agent_id):
        \"\"\"Stop a Manus agent.\"\"\"
        response = requests.post(
            f"{self.api_url}/agents/{agent_id}/stop"
        )
        return response.json()
    
    def pause_agent(self, agent_id):
        \"\"\"Pause a Manus agent.\"\"\"
        response = requests.post(
            f"{self.api_url}/agents/{agent_id}/pause"
        )
        return response.json()
    
    def resume_agent(self, agent_id):
        \"\"\"Resume a paused Manus agent.\"\"\"
        response = requests.post(
            f"{self.api_url}/agents/{agent_id}/resume"
        )
        return response.json()
    
    def get_agent_status(self, agent_id):
        \"\"\"Get the status of a Manus agent.\"\"\"
        response = requests.get(
            f"{self.api_url}/agents/{agent_id}/status"
        )
        return response.json()
    
    def list_templates(self):
        \"\"\"List available templates for Manus agents.\"\"\"
        response = requests.get(
            f"{self.api_url}/templates"
        )
        return response.json()

# Create a singleton instance
manus_bridge_client = ManusBridgeClient()
"""
    
    with open(client_path, "w") as f:
        f.write(client_content)
    
    print(f"Created Manus Bridge API client: {client_path}")

def update_env_file(manus_manager_path):
    """Update the .env file with Manus Bridge API URL."""
    env_path = os.path.join(manus_manager_path, "backend", ".env")
    
    # Backup the original file
    backup_file(env_path)
    
    # Read the original file
    with open(env_path, "r") as f:
        content = f.read()
    
    # Add Manus Bridge API URL if not already present
    if "MANUS_BRIDGE_API_URL" not in content:
        content += "\nMANUS_BRIDGE_API_URL=http://localhost:8080\n"
    
    # Write the modified content back to the file
    with open(env_path, "w") as f:
        f.write(content)
    
    print(f"Updated .env file: {env_path}")

def create_requirements_file():
    """Create requirements.txt file for Manus Bridge."""
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    
    requirements_content = """fastapi>=0.68.0
uvicorn>=0.15.0
requests>=2.26.0
pydantic>=1.8.2
"""
    
    with open(requirements_path, "w") as f:
        f.write(requirements_content)
    
    print(f"Created requirements.txt: {requirements_path}")

def create_readme_file():
    """Create README.md file for Manus Bridge."""
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    
    readme_content = """# Manus Bridge

A bridge between manus-manager and Manus for orchestrating, starting, stopping, and tracking Manus AI agents.

## Overview

Manus Bridge provides an integration layer between the manus-manager application and the Manus system. It exposes a REST API that allows manus-manager to control Manus agents.

## Features

- Start, stop, and pause Manus agents
- Monitor agent status
- List available agent templates

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure the Manus Bridge:
   ```bash
   export MANUS_OPT_PATH="/path/to/opt"
   export MANUS_OPT2_PATH="/path/to/opt2"
   export MANUS_OPT3_PATH="/path/to/opt3"
   ```

3. Integrate with manus-manager:
   ```bash
   python integration.py --manus-manager-path /path/to/manus-manager
   ```

4. Start the Manus Bridge API server:
   ```bash
   python -m manus_bridge.api
   ```

5. Configure manus-manager to use Manus Bridge:
   ```bash
   cd /path/to/manus-manager/backend
   export MANUS_BRIDGE_API_URL="http://localhost:8080"
   ```

## Usage

1. Start the Manus Bridge API server:
   ```bash
   python -m manus_bridge.api
   ```

2. Start the manus-manager backend:
   ```bash
   cd /path/to/manus-manager/backend
   uvicorn app.main:app --reload
   ```

3. Start the manus-manager frontend:
   ```bash
   cd /path/to/manus-manager/frontend
   npm start
   ```

4. Access the manus-manager web interface at http://localhost:3000
"""
    
    with open(readme_path, "w") as f:
        f.write(readme_content)
    
    print(f"Created README.md: {readme_path}")

def create_run_script():
    """Create a run script for Manus Bridge."""
    run_path = os.path.join(os.path.dirname(__file__), "run.py")
    
    run_content = """#!/usr/bin/env python
\"\"\"
Run script for Manus Bridge.

This script starts the Manus Bridge API server.
\"\"\"

import os
import sys
import argparse
from manus_bridge.api import start_server

def main():
    \"\"\"Main entry point.\"\"\"
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
"""
    
    with open(run_path, "w") as f:
        f.write(run_content)
    
    # Make the script executable
    os.chmod(run_path, 0o755)
    
    print(f"Created run script: {run_path}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Integrate manus-manager with Manus Bridge")
    parser.add_argument(
        "--manus-manager-path",
        required=True,
        help="Path to manus-manager installation"
    )
    args = parser.parse_args()
    
    # Check if the provided path is valid
    if not check_manus_manager_path(args.manus_manager_path):
        sys.exit(1)
    
    # Patch the agent service
    patch_agent_service(args.manus_manager_path)
    
    # Create the Manus Bridge API client
    create_manus_bridge_api_client(args.manus_manager_path)
    
    # Update the .env file
    update_env_file(args.manus_manager_path)
    
    # Create requirements.txt
    create_requirements_file()
    
    # Create README.md
    create_readme_file()
    
    # Create run script
    create_run_script()
    
    print("\nIntegration complete!")
    print("\nTo start the Manus Bridge API server:")
    print("  python run.py")
    print("\nTo start the manus-manager backend:")
    print(f"  cd {args.manus_manager_path}/backend")
    print("  uvicorn app.main:app --reload")
    print("\nTo start the manus-manager frontend:")
    print(f"  cd {args.manus_manager_path}/frontend")
    print("  npm start")

if __name__ == "__main__":
    main()
