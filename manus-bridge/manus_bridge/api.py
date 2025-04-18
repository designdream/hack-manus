"""
Manus Bridge API Server.

This module provides a FastAPI server that exposes the Manus Bridge functionality
to the manus-manager application.
"""

import os
import sys
import json
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Depends, status, Body, WebSocket, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

from . import config
from .manus_bridge import bridge
from .browser_control import browser_manager

# Define API models
class AgentConfig(BaseModel):
    """Configuration for a Manus agent."""
    id: int
    name: str
    description: Optional[str] = None
    owner_id: int
    api_key: Optional[str] = None
    instance_url: Optional[str] = None
    max_tasks: int = 5

class AgentStatus(BaseModel):
    """Status information for a Manus agent."""
    agent_id: int
    status: str
    process_id: Optional[int] = None
    error: Optional[str] = None
    message: Optional[str] = None

class Template(BaseModel):
    """Information about a Manus agent template."""
    name: str
    path: str
    version: Optional[str] = None
    description: Optional[str] = None
    dependencies: Optional[Dict[str, str]] = None

# Create FastAPI app
app = FastAPI(
    title="Manus Bridge API",
    description="API for connecting manus-manager to Manus",
    version="0.1.0",
)

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up templates and static files
templates_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
templates = Jinja2Templates(directory=templates_path)

static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Manus Bridge API",
        "version": "0.1.0",
        "status": "online"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy"
    }

@app.post("/agents/start", response_model=AgentStatus)
async def start_agent(agent_config: AgentConfig):
    """
    Start a Manus agent.
    
    Args:
        agent_config: Configuration for the agent
        
    Returns:
        Status information for the agent
    """
    result = bridge.start_agent(agent_config.dict())
    return result

@app.post("/agents/{agent_id}/stop", response_model=AgentStatus)
async def stop_agent(agent_id: int):
    """
    Stop a Manus agent.
    
    Args:
        agent_id: ID of the agent to stop
        
    Returns:
        Status information for the agent
    """
    result = bridge.stop_agent(agent_id)
    return result

@app.post("/agents/{agent_id}/pause", response_model=AgentStatus)
async def pause_agent(agent_id: int):
    """
    Pause a Manus agent.
    
    Args:
        agent_id: ID of the agent to pause
        
    Returns:
        Status information for the agent
    """
    result = bridge.pause_agent(agent_id)
    return result

@app.post("/agents/{agent_id}/resume", response_model=AgentStatus)
async def resume_agent(agent_id: int):
    """
    Resume a paused Manus agent.
    
    Args:
        agent_id: ID of the agent to resume
        
    Returns:
        Status information for the agent
    """
    result = bridge.resume_agent(agent_id)
    return result

@app.get("/agents/{agent_id}/status", response_model=AgentStatus)
async def get_agent_status(agent_id: int):
    """
    Get the status of a Manus agent.
    
    Args:
        agent_id: ID of the agent
        
    Returns:
        Status information for the agent
    """
    result = bridge.get_agent_status(agent_id)
    return result

@app.get("/templates", response_model=List[Template])
async def list_templates():
    """
    List available templates for Manus agents.
    
    Returns:
        List of template information
    """
    templates = bridge.list_templates()
    return templates

# Browser Control Endpoints

@app.post("/agents/{agent_id}/assist")
async def request_human_assistance(agent_id: int):
    """
    Request human assistance for an agent that is stuck.
    
    This will pause the agent and create a browser session that a human can take control of.
    
    Args:
        agent_id: ID of the agent that needs assistance
        
    Returns:
        Information about the browser session created for human assistance
    """
    # Pause the agent
    bridge.pause_agent(agent_id)
    
    # Create a browser session
    session = browser_manager.create_session(agent_id, headless=False)
    
    # Return session information with control URL
    return {
        "message": "Agent paused, awaiting human assistance",
        "agent_id": agent_id,
        "session": session,
        "control_url": f"/browser-control?agent_id={agent_id}&session_id={session['session_id']}"
    }

@app.get("/browser-control", response_class=HTMLResponse)
async def browser_control_page(request: Request, agent_id: int, session_id: str):
    """
    Render the browser control page for human intervention.
    
    Args:
        request: FastAPI request object
        agent_id: ID of the agent
        session_id: ID of the browser session
        
    Returns:
        HTML page for controlling the browser
    """
    return templates.TemplateResponse(
        "browser_control.html",
        {"request": request, "agent_id": agent_id, "session_id": session_id}
    )

@app.get("/browser-control/sessions/{session_id}/status")
async def get_browser_session_status(session_id: str):
    """
    Get the status of a browser session.
    
    Args:
        session_id: ID of the browser session
        
    Returns:
        Status information for the browser session
    """
    session = browser_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Browser session {session_id} not found")
    
    return session.get_status()

@app.post("/browser-control/sessions/{session_id}/control/{mode}")
async def transfer_browser_control(session_id: str, mode: str):
    """
    Transfer control of a browser session between agent and human.
    
    Args:
        session_id: ID of the browser session
        mode: Either "agent" or "human"
        
    Returns:
        Updated status of the browser session
    """
    if mode not in ["agent", "human"]:
        raise HTTPException(status_code=400, detail=f"Invalid mode: {mode}. Must be 'agent' or 'human'")
    
    result = browser_manager.transfer_control(session_id, mode)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@app.post("/browser-control/sessions/{session_id}/stop")
async def stop_browser_session(session_id: str):
    """
    Stop a browser session.
    
    Args:
        session_id: ID of the browser session
        
    Returns:
        Status information for the stopped browser session
    """
    result = browser_manager.stop_session(session_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return result

@app.get("/agents/{agent_id}/browser-sessions")
async def get_agent_browser_sessions(agent_id: int):
    """
    Get all browser sessions for an agent.
    
    Args:
        agent_id: ID of the agent
        
    Returns:
        List of browser sessions for the agent
    """
    sessions = browser_manager.get_agent_sessions(agent_id)
    return {"agent_id": agent_id, "sessions": sessions}

def start_server():
    """Start the API server."""
    uvicorn.run(
        "manus_bridge.api:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )

if __name__ == "__main__":
    start_server()
