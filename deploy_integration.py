#!/usr/bin/env python
"""
Deployment Integration Script for Manus Bridge.

This script integrates the deployed Manus Bridge API with manus-manager.
"""

import os
import sys
import shutil
import argparse
import json
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

def create_manus_bridge_client(manus_manager_path, api_url):
    """Create a client for the Manus Bridge API."""
    client_path = os.path.join(
        manus_manager_path, "backend", "app", "services", "manus_bridge_client.py"
    )
    
    client_content = f'''"""
Manus Bridge API Client.

This module provides a client for interacting with the Manus Bridge API.
"""

import os
import requests
from typing import Dict, List, Optional, Any

# Manus Bridge API settings
MANUS_BRIDGE_API_URL = os.environ.get("MANUS_BRIDGE_API_URL", "{api_url}")

class ManusBridgeClient:
    """Client for the Manus Bridge API."""
    
    def __init__(self, api_url=None):
        """Initialize the client."""
        self.api_url = api_url or MANUS_BRIDGE_API_URL
    
    def get_health(self):
        """Check the health of the Manus Bridge API."""
        response = requests.get(f"{{self.api_url}}/health")
        return response.json()
    
    def start_agent(self, agent_config):
        """Start a Manus agent."""
        # Ensure the agent config has the required fields
        if 'id' not in agent_config:
            agent_config['id'] = agent_config.get('id', hash(agent_config.get('name', '')))
        
        if isinstance(agent_config.get('owner_id'), str):
            try:
                agent_config['owner_id'] = int(agent_config['owner_id'])
            except ValueError:
                agent_config['owner_id'] = 1  # Default to user ID 1 if conversion fails
        
        response = requests.post(
            f"{{self.api_url}}/agents/start",
            json=agent_config
        )
        return response.json()
    
    def stop_agent(self, agent_id):
        """Stop a Manus agent."""
        response = requests.post(
            f"{{self.api_url}}/agents/{{agent_id}}/stop"
        )
        return response.json()
    
    def pause_agent(self, agent_id):
        """Pause a Manus agent."""
        response = requests.post(
            f"{{self.api_url}}/agents/{{agent_id}}/pause"
        )
        return response.json()
    
    def resume_agent(self, agent_id):
        """Resume a paused Manus agent."""
        response = requests.post(
            f"{{self.api_url}}/agents/{{agent_id}}/resume"
        )
        return response.json()
    
    def get_agent_status(self, agent_id):
        """Get the status of a Manus agent."""
        response = requests.get(
            f"{{self.api_url}}/agents/{{agent_id}}/status"
        )
        return response.json()
    
    def list_templates(self):
        """List available templates for Manus agents."""
        response = requests.get(
            f"{{self.api_url}}/templates"
        )
        return response.json()

# Create a singleton instance
manus_bridge_client = ManusBridgeClient()
'''
    
    with open(client_path, "w") as f:
        f.write(client_content)
    
    print(f"Created Manus Bridge API client: {client_path}")
    return True

def modify_agent_service(manus_manager_path):
    """Modify the agent_service.py file to use Manus Bridge."""
    agent_service_path = os.path.join(
        manus_manager_path, "backend", "app", "services", "agent_service.py"
    )
    
    # Backup the original file
    backup_file(agent_service_path)
    
    # Read the original file
    with open(agent_service_path, "r") as f:
        content = f.read()
    
    # Add imports for Manus Bridge client
    if "from app.services.manus_bridge_client import manus_bridge_client" not in content:
        import_section = "from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union\nfrom fastapi.encoders import jsonable_encoder\nfrom pydantic import BaseModel\nfrom sqlalchemy.orm import Session\n\nfrom app.db.base_class import Base\nfrom app.models.models import Agent, AgentStatus"
        
        new_import_section = "from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union\nfrom fastapi.encoders import jsonable_encoder\nfrom pydantic import BaseModel\nfrom sqlalchemy.orm import Session\n\nfrom app.db.base_class import Base\nfrom app.models.models import Agent, AgentStatus\nfrom app.services.manus_bridge_client import manus_bridge_client"
        
        content = content.replace(import_section, new_import_section)
    
    # Replace the start_agent method
    start_agent_method = '''    def start_agent(self, db: Session, *, agent: Agent) -> Agent:
        """
        Start agent
        """
        # Here we would implement the actual logic to start a Manus agent
        # For now, we just update the status
        agent.status = AgentStatus.RUNNING
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent'''
    
    new_start_agent_method = '''    def start_agent(self, db: Session, *, agent: Agent) -> Agent:
        """
        Start agent using Manus Bridge API
        """
        try:
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
            result = manus_bridge_client.start_agent(agent_config)
            
            if result.get("status") == "running":
                agent.status = AgentStatus.RUNNING
                db.add(agent)
                db.commit()
                db.refresh(agent)
            else:
                print(f"Failed to start agent: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"Error starting agent: {str(e)}")
            
        return agent'''
    
    content = content.replace(start_agent_method, new_start_agent_method)
    
    # Replace the stop_agent method
    stop_agent_method = '''    def stop_agent(self, db: Session, *, agent: Agent) -> Agent:
        """
        Stop agent
        """
        # Here we would implement the actual logic to stop a Manus agent
        # For now, we just update the status
        agent.status = AgentStatus.IDLE
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent'''
    
    new_stop_agent_method = '''    def stop_agent(self, db: Session, *, agent: Agent) -> Agent:
        """
        Stop agent using Manus Bridge API
        """
        try:
            # Call Manus Bridge API to stop the agent
            result = manus_bridge_client.stop_agent(agent.id)
            
            if result.get("status") == "stopped":
                agent.status = AgentStatus.IDLE
                db.add(agent)
                db.commit()
                db.refresh(agent)
            else:
                print(f"Failed to stop agent: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"Error stopping agent: {str(e)}")
            
        return agent'''
    
    content = content.replace(stop_agent_method, new_stop_agent_method)
    
    # Replace the pause_agent method
    pause_agent_method = '''    def pause_agent(self, db: Session, *, agent: Agent) -> Agent:
        """
        Pause agent
        """
        # Here we would implement the actual logic to pause a Manus agent
        # For now, we just update the status
        agent.status = AgentStatus.PAUSED
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent'''
    
    new_pause_agent_method = '''    def pause_agent(self, db: Session, *, agent: Agent) -> Agent:
        """
        Pause agent using Manus Bridge API
        """
        try:
            # Call Manus Bridge API to pause the agent
            result = manus_bridge_client.pause_agent(agent.id)
            
            if result.get("status") == "paused":
                agent.status = AgentStatus.PAUSED
                db.add(agent)
                db.commit()
                db.refresh(agent)
            else:
                print(f"Failed to pause agent: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"Error pausing agent: {str(e)}")
            
        return agent'''
    
    content = content.replace(pause_agent_method, new_pause_agent_method)
    
    # Write the modified content back to the file
    with open(agent_service_path, "w") as f:
        f.write(content)
    
    print(f"Modified agent service: {agent_service_path}")
    return True

def update_env_file(manus_manager_path, api_url):
    """Update the .env file with Manus Bridge API URL."""
    env_path = os.path.join(manus_manager_path, "backend", ".env")
    
    # Backup the original file
    backup_file(env_path)
    
    # Create the .env file if it doesn't exist
    if not os.path.exists(env_path):
        with open(env_path, "w") as f:
            f.write(f"MANUS_BRIDGE_API_URL={api_url}\n")
        print(f"Created .env file: {env_path}")
        return True
    
    # Read the original file
    with open(env_path, "r") as f:
        content = f.read()
    
    # Update or add Manus Bridge API URL
    if "MANUS_BRIDGE_API_URL" in content:
        # Replace the existing URL
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            if line.startswith("MANUS_BRIDGE_API_URL="):
                new_lines.append(f"MANUS_BRIDGE_API_URL={api_url}")
            else:
                new_lines.append(line)
        content = "\n".join(new_lines)
    else:
        # Add the URL
        content += f"\nMANUS_BRIDGE_API_URL={api_url}\n"
    
    # Write the modified content back to the file
    with open(env_path, "w") as f:
        f.write(content)
    
    print(f"Updated .env file: {env_path}")
    return True

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Integrate manus-manager with deployed Manus Bridge API")
    parser.add_argument(
        "--manus-manager-path",
        required=True,
        help="Path to manus-manager installation"
    )
    parser.add_argument(
        "--api-url",
        default="https://manus-bridge-9jpjr.ondigitalocean.app",
        help="URL of the deployed Manus Bridge API"
    )
    args = parser.parse_args()
    
    # Check if the provided path is valid
    if not check_manus_manager_path(args.manus_manager_path):
        sys.exit(1)
    
    # Create the Manus Bridge API client
    if not create_manus_bridge_client(args.manus_manager_path, args.api_url):
        print("Failed to create Manus Bridge API client")
        sys.exit(1)
    
    # Modify the agent service
    if not modify_agent_service(args.manus_manager_path):
        print("Failed to modify agent service")
        sys.exit(1)
    
    # Update the .env file
    if not update_env_file(args.manus_manager_path, args.api_url):
        print("Failed to update .env file")
        sys.exit(1)
    
    print("\nIntegration complete!")
    print(f"\nManus Bridge API URL: {args.api_url}")
    print("\nTo start the manus-manager backend:")
    print(f"  cd {args.manus_manager_path}/backend")
    print("  uvicorn app.main:app --reload")
    print("\nTo start the manus-manager frontend:")
    print(f"  cd {args.manus_manager_path}/frontend")
    print("  npm start")

if __name__ == "__main__":
    main()
