"""
Manus Bridge API Server.

This module provides a FastAPI server that exposes the Manus Bridge functionality
to the manus-manager application.
"""

import os
import sys
import json
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from . import config
from .manus_bridge import bridge

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
