"""
Browser Control Module for Manus Bridge.

This module provides functionality for controlling browser sessions,
allowing human intervention when agents get stuck.
"""

import os
import sys
import time
import json
import logging
import socket
import subprocess
import threading
import uuid
from typing import Dict, Any, Optional, List
from pathlib import Path

from . import config

# Configure logging
logger = logging.getLogger("manus_bridge.browser_control")

class BrowserSession:
    """
    Manages a browser session that can be controlled by a human or an agent.
    """
    
    def __init__(self, agent_id: int, session_id: str = None, headless: bool = True):
        """Initialize a browser session."""
        self.agent_id = agent_id
        self.session_id = session_id or str(uuid.uuid4())
        self.headless = headless
        self.process = None
        self.port = self._find_available_port()
        self.debug_port = self._find_available_port()
        self.status = "initializing"
        self.start_time = time.time()
        self.last_activity = time.time()
        self.control_mode = "agent"  # "agent" or "human"
        
        # Create session directory
        self.session_dir = os.path.join(config.BASE_DIR, "data", "browser_sessions", str(agent_id), self.session_id)
        os.makedirs(self.session_dir, exist_ok=True)
        
        # Session metadata
        self.metadata = {
            "agent_id": agent_id,
            "session_id": self.session_id,
            "port": self.port,
            "debug_port": self.debug_port,
            "status": self.status,
            "start_time": self.start_time,
            "control_mode": self.control_mode
        }
        self._save_metadata()
    
    def _find_available_port(self) -> int:
        """Find an available port to use for the browser session."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    def _save_metadata(self):
        """Save session metadata to disk."""
        metadata_path = os.path.join(self.session_dir, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(self.metadata, f, indent=2)
    
    def start(self) -> Dict[str, Any]:
        """Start the browser session."""
        try:
            # Prepare command for Chrome/Chromium with remote debugging
            cmd = [
                "chromium-browser" if os.path.exists("/usr/bin/chromium-browser") else "google-chrome",
                f"--remote-debugging-port={self.debug_port}",
                f"--user-data-dir={self.session_dir}/user_data",
                "--no-first-run",
                "--no-default-browser-check"
            ]
            
            if self.headless:
                cmd.append("--headless=new")
            
            # Start browser process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Start monitoring thread
            threading.Thread(target=self._monitor_process, daemon=True).start()
            
            # Update status
            self.status = "running"
            self.metadata["status"] = self.status
            self.metadata["process_id"] = self.process.pid
            self._save_metadata()
            
            logger.info(f"Started browser session {self.session_id} for agent {self.agent_id} on port {self.debug_port}")
            
            return {
                "session_id": self.session_id,
                "status": self.status,
                "debug_url": f"http://localhost:{self.debug_port}",
                "control_url": f"/browser-control/{self.agent_id}/{self.session_id}"
            }
            
        except Exception as e:
            logger.error(f"Failed to start browser session: {str(e)}")
            self.status = "error"
            self.metadata["status"] = self.status
            self.metadata["error"] = str(e)
            self._save_metadata()
            return {
                "session_id": self.session_id,
                "status": "error",
                "error": str(e)
            }
    
    def _monitor_process(self):
        """Monitor the browser process and capture output."""
        log_path = os.path.join(self.session_dir, "browser.log")
        with open(log_path, "w") as log_file:
            while self.process and self.process.poll() is None:
                # Read output
                if self.process.stdout:
                    for line in iter(self.process.stdout.readline, ""):
                        if not line:
                            break
                        log_file.write(line)
                        log_file.flush()
                
                # Check if process is still running
                if self.process.poll() is not None:
                    break
                
                time.sleep(0.1)
            
            # Process has ended
            if self.process:
                exit_code = self.process.returncode
                logger.info(f"Browser session {self.session_id} ended with exit code {exit_code}")
                self.status = "stopped"
                self.metadata["status"] = self.status
                self.metadata["exit_code"] = exit_code
                self._save_metadata()
    
    def stop(self) -> Dict[str, Any]:
        """Stop the browser session."""
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                time.sleep(1)
                if self.process.poll() is None:
                    self.process.kill()
                
                self.status = "stopped"
                self.metadata["status"] = self.status
                self._save_metadata()
                
                logger.info(f"Stopped browser session {self.session_id}")
                return {"session_id": self.session_id, "status": "stopped"}
                
            except Exception as e:
                logger.error(f"Error stopping browser session: {str(e)}")
                return {"session_id": self.session_id, "status": "error", "error": str(e)}
        else:
            return {"session_id": self.session_id, "status": self.status}
    
    def transfer_control(self, mode: str) -> Dict[str, Any]:
        """
        Transfer control between agent and human.
        
        Args:
            mode: Either "agent" or "human"
        """
        if mode not in ["agent", "human"]:
            return {"error": "Invalid mode. Must be 'agent' or 'human'"}
        
        self.control_mode = mode
        self.metadata["control_mode"] = mode
        self.last_activity = time.time()
        self.metadata["last_activity"] = self.last_activity
        self._save_metadata()
        
        logger.info(f"Transferred control of session {self.session_id} to {mode}")
        return {
            "session_id": self.session_id,
            "control_mode": mode,
            "status": self.status
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the browser session."""
        # Update process status if needed
        if self.process:
            if self.process.poll() is not None and self.status == "running":
                self.status = "stopped"
                self.metadata["status"] = self.status
                self.metadata["exit_code"] = self.process.returncode
                self._save_metadata()
        
        return {
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "status": self.status,
            "control_mode": self.control_mode,
            "debug_url": f"http://localhost:{self.debug_port}",
            "control_url": f"/browser-control/{self.agent_id}/{self.session_id}",
            "uptime": time.time() - self.start_time,
            "last_activity": time.time() - self.last_activity
        }


class BrowserManager:
    """
    Manages browser sessions for agents.
    """
    
    def __init__(self):
        """Initialize the browser manager."""
        self.sessions = {}  # Map of session_id to BrowserSession
        self.agent_sessions = {}  # Map of agent_id to list of session_ids
        
        # Create sessions directory
        self.sessions_dir = os.path.join(config.BASE_DIR, "data", "browser_sessions")
        os.makedirs(self.sessions_dir, exist_ok=True)
        
        logger.info("Initialized Browser Manager")
    
    def create_session(self, agent_id: int, headless: bool = True) -> Dict[str, Any]:
        """Create a new browser session for an agent."""
        session = BrowserSession(agent_id, headless=headless)
        
        # Store session
        self.sessions[session.session_id] = session
        if agent_id not in self.agent_sessions:
            self.agent_sessions[agent_id] = []
        self.agent_sessions[agent_id].append(session.session_id)
        
        # Start session
        result = session.start()
        return result
    
    def get_session(self, session_id: str) -> Optional[BrowserSession]:
        """Get a browser session by ID."""
        return self.sessions.get(session_id)
    
    def get_agent_sessions(self, agent_id: int) -> List[Dict[str, Any]]:
        """Get all browser sessions for an agent."""
        if agent_id not in self.agent_sessions:
            return []
        
        sessions = []
        for session_id in self.agent_sessions[agent_id]:
            if session_id in self.sessions:
                sessions.append(self.sessions[session_id].get_status())
        
        return sessions
    
    def stop_session(self, session_id: str) -> Dict[str, Any]:
        """Stop a browser session."""
        if session_id in self.sessions:
            return self.sessions[session_id].stop()
        return {"error": f"Session {session_id} not found"}
    
    def stop_agent_sessions(self, agent_id: int) -> List[Dict[str, Any]]:
        """Stop all browser sessions for an agent."""
        if agent_id not in self.agent_sessions:
            return []
        
        results = []
        for session_id in self.agent_sessions[agent_id]:
            if session_id in self.sessions:
                results.append(self.stop_session(session_id))
        
        return results
    
    def transfer_control(self, session_id: str, mode: str) -> Dict[str, Any]:
        """Transfer control of a browser session between agent and human."""
        if session_id in self.sessions:
            return self.sessions[session_id].transfer_control(mode)
        return {"error": f"Session {session_id} not found"}


# Create a singleton instance
browser_manager = BrowserManager()
