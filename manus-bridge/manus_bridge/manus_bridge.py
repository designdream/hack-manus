"""
Manus Bridge - Main module for connecting manus-manager to Manus.

This module provides the core functionality for interacting with the Manus system
from the manus-manager application.
"""

import os
import sys
import json
import subprocess
import logging
from typing import Dict, List, Optional, Any
import requests
from pathlib import Path

from . import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("manus_bridge")

class ManusBridge:
    """
    Bridge between manus-manager and the Manus system.
    
    This class provides methods to interact with the Manus sandbox runtime
    and manage Manus agents.
    """
    
    def __init__(self):
        """Initialize the Manus Bridge."""
        self.sandbox_path = config.MANUS_SANDBOX_PATH
        self.templates_path = config.MANUS_TEMPLATES_PATH
        self.packages_path = config.MANUS_PACKAGES_PATH
        
        # Validate paths
        self._validate_paths()
        
        logger.info(f"Initialized Manus Bridge with sandbox path: {self.sandbox_path}")
    
    def _validate_paths(self):
        """Validate that all required Manus paths exist and create them if needed."""
        # Create base directories if they don't exist
        for path in [config.MANUS_OPT_PATH, config.MANUS_OPT2_PATH, config.MANUS_OPT3_PATH]:
            os.makedirs(path, exist_ok=True)
            
        # Create subdirectories
        os.makedirs(os.path.join(config.MANUS_OPT_PATH, ".manus", "deploy", "templates"), exist_ok=True)
        os.makedirs(os.path.join(config.MANUS_OPT2_PATH, ".manus", ".packages"), exist_ok=True)
        os.makedirs(os.path.join(config.MANUS_OPT3_PATH, ".manus", ".sandbox-runtime"), exist_ok=True)
        
        paths = [
            self.sandbox_path,
            self.templates_path,
            self.packages_path
        ]
        
        for path in paths:
            if not os.path.exists(path):
                logger.warning(f"Path does not exist: {path}")
    
    def start_agent(self, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start a Manus agent with the given configuration.
        
        Args:
            agent_config: Configuration for the agent
            
        Returns:
            Dict with agent status information
        """
        agent_name = agent_config.get("name", "unnamed_agent")
        agent_id = agent_config.get("id")
        
        logger.info(f"Starting Manus agent: {agent_name} (ID: {agent_id})")
        
        # Create agent working directory if it doesn't exist
        agent_dir = os.path.join(os.path.dirname(self.sandbox_path), "agents", f"agent_{agent_id}")
        os.makedirs(agent_dir, exist_ok=True)
        
        # Create agent configuration file
        config_path = os.path.join(agent_dir, "agent_config.json")
        with open(config_path, "w") as f:
            json.dump(agent_config, f, indent=2)
        
        # Attempt to start the agent using the sandbox runtime
        try:
            # Construct the command to start the agent
            # This is a placeholder - actual command would depend on how Manus agents are started
            cmd = [
                sys.executable,
                os.path.join(self.sandbox_path, "start_server.py"),
                "--agent-config", config_path,
                "--agent-dir", agent_dir
            ]
            
            # Use subprocess to start the agent in the background
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.sandbox_path
            )
            
            # Store the process ID for later management
            with open(os.path.join(agent_dir, "agent.pid"), "w") as f:
                f.write(str(process.pid))
            
            return {
                "status": "running",
                "agent_id": agent_id,
                "process_id": process.pid,
                "agent_dir": agent_dir
            }
            
        except Exception as e:
            logger.error(f"Failed to start agent {agent_name}: {str(e)}")
            return {
                "status": "error",
                "agent_id": agent_id,
                "error": str(e)
            }
    
    def stop_agent(self, agent_id: int) -> Dict[str, Any]:
        """
        Stop a running Manus agent.
        
        Args:
            agent_id: ID of the agent to stop
            
        Returns:
            Dict with operation status
        """
        logger.info(f"Stopping Manus agent with ID: {agent_id}")
        
        agent_dir = os.path.join(os.path.dirname(self.sandbox_path), "agents", f"agent_{agent_id}")
        pid_file = os.path.join(agent_dir, "agent.pid")
        
        if not os.path.exists(pid_file):
            return {
                "status": "error",
                "agent_id": agent_id,
                "error": "Agent not running or PID file not found"
            }
        
        try:
            # Read the process ID
            with open(pid_file, "r") as f:
                pid = int(f.read().strip())
            
            # Attempt to terminate the process
            os.kill(pid, 15)  # SIGTERM
            
            # Remove the PID file
            os.remove(pid_file)
            
            return {
                "status": "stopped",
                "agent_id": agent_id
            }
            
        except ProcessLookupError:
            # Process already terminated
            os.remove(pid_file)
            return {
                "status": "stopped",
                "agent_id": agent_id,
                "message": "Process was not running"
            }
            
        except Exception as e:
            logger.error(f"Failed to stop agent {agent_id}: {str(e)}")
            return {
                "status": "error",
                "agent_id": agent_id,
                "error": str(e)
            }
    
    def pause_agent(self, agent_id: int) -> Dict[str, Any]:
        """
        Pause a running Manus agent.
        
        Args:
            agent_id: ID of the agent to pause
            
        Returns:
            Dict with operation status
        """
        logger.info(f"Pausing Manus agent with ID: {agent_id}")
        
        agent_dir = os.path.join(os.path.dirname(self.sandbox_path), "agents", f"agent_{agent_id}")
        pid_file = os.path.join(agent_dir, "agent.pid")
        
        if not os.path.exists(pid_file):
            return {
                "status": "error",
                "agent_id": agent_id,
                "error": "Agent not running or PID file not found"
            }
        
        try:
            # Read the process ID
            with open(pid_file, "r") as f:
                pid = int(f.read().strip())
            
            # Attempt to pause the process (SIGSTOP)
            os.kill(pid, 19)  # SIGSTOP
            
            # Mark the agent as paused
            with open(os.path.join(agent_dir, "agent.paused"), "w") as f:
                f.write("paused")
            
            return {
                "status": "paused",
                "agent_id": agent_id
            }
            
        except Exception as e:
            logger.error(f"Failed to pause agent {agent_id}: {str(e)}")
            return {
                "status": "error",
                "agent_id": agent_id,
                "error": str(e)
            }
    
    def resume_agent(self, agent_id: int) -> Dict[str, Any]:
        """
        Resume a paused Manus agent.
        
        Args:
            agent_id: ID of the agent to resume
            
        Returns:
            Dict with operation status
        """
        logger.info(f"Resuming Manus agent with ID: {agent_id}")
        
        agent_dir = os.path.join(os.path.dirname(self.sandbox_path), "agents", f"agent_{agent_id}")
        pid_file = os.path.join(agent_dir, "agent.pid")
        paused_file = os.path.join(agent_dir, "agent.paused")
        
        if not os.path.exists(pid_file) or not os.path.exists(paused_file):
            return {
                "status": "error",
                "agent_id": agent_id,
                "error": "Agent not paused or PID file not found"
            }
        
        try:
            # Read the process ID
            with open(pid_file, "r") as f:
                pid = int(f.read().strip())
            
            # Attempt to resume the process (SIGCONT)
            os.kill(pid, 18)  # SIGCONT
            
            # Remove the paused marker
            os.remove(paused_file)
            
            return {
                "status": "running",
                "agent_id": agent_id
            }
            
        except Exception as e:
            logger.error(f"Failed to resume agent {agent_id}: {str(e)}")
            return {
                "status": "error",
                "agent_id": agent_id,
                "error": str(e)
            }
    
    def get_agent_status(self, agent_id: int) -> Dict[str, Any]:
        """
        Get the status of a Manus agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Dict with agent status information
        """
        logger.info(f"Getting status for Manus agent with ID: {agent_id}")
        
        agent_dir = os.path.join(os.path.dirname(self.sandbox_path), "agents", f"agent_{agent_id}")
        pid_file = os.path.join(agent_dir, "agent.pid")
        paused_file = os.path.join(agent_dir, "agent.paused")
        
        if not os.path.exists(agent_dir):
            return {
                "status": "unknown",
                "agent_id": agent_id,
                "error": "Agent directory not found"
            }
        
        if not os.path.exists(pid_file):
            return {
                "status": "stopped",
                "agent_id": agent_id
            }
        
        try:
            # Read the process ID
            with open(pid_file, "r") as f:
                pid = int(f.read().strip())
            
            # Check if the process is running
            os.kill(pid, 0)  # This will raise an exception if the process is not running
            
            # Check if the agent is paused
            if os.path.exists(paused_file):
                return {
                    "status": "paused",
                    "agent_id": agent_id,
                    "process_id": pid
                }
            
            return {
                "status": "running",
                "agent_id": agent_id,
                "process_id": pid
            }
            
        except ProcessLookupError:
            # Process not running
            os.remove(pid_file)
            if os.path.exists(paused_file):
                os.remove(paused_file)
            
            return {
                "status": "stopped",
                "agent_id": agent_id,
                "message": "Process not running"
            }
            
        except Exception as e:
            logger.error(f"Failed to get status for agent {agent_id}: {str(e)}")
            return {
                "status": "error",
                "agent_id": agent_id,
                "error": str(e)
            }
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List available templates for Manus agents.
        
        Returns:
            List of template information dictionaries
        """
        templates = []
        
        try:
            for template_dir in os.listdir(self.templates_path):
                template_path = os.path.join(self.templates_path, template_dir)
                if os.path.isdir(template_path):
                    # Read package.json if it exists
                    package_json_path = os.path.join(template_path, "package.json")
                    template_info = {
                        "name": template_dir,
                        "path": template_path
                    }
                    
                    if os.path.exists(package_json_path):
                        with open(package_json_path, "r") as f:
                            package_data = json.load(f)
                            template_info.update({
                                "version": package_data.get("version", "unknown"),
                                "description": package_data.get("description", ""),
                                "dependencies": package_data.get("dependencies", {})
                            })
                    
                    templates.append(template_info)
            
            return templates
            
        except Exception as e:
            logger.error(f"Failed to list templates: {str(e)}")
            return []

# Create a singleton instance
bridge = ManusBridge()
