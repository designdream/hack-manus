from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Any, List, Optional
from datetime import datetime

from app.db.session import get_db
from app.schemas.schemas import Agent, AgentCreate, AgentUpdate
from app.services.agent_service import (
    create_agent,
    get_agent,
    get_agents,
    update_agent,
    delete_agent,
    start_agent,
    stop_agent,
    pause_agent
)
from app.services.user_service import get_current_user
from app.schemas.schemas import User

router = APIRouter()

@router.post("/", response_model=Agent)
async def create_new_agent(
    agent_in: AgentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create new agent
    """
    # Only allow creating agents for the current user or if superuser
    if agent_in.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create agent for another user"
        )
    return create_agent(db=db, obj_in=agent_in)

@router.get("/", response_model=List[Agent])
async def read_agents(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve agents
    """
    # If superuser, can see all agents, otherwise only own agents
    if current_user.is_superuser:
        return get_agents(db, skip=skip, limit=limit, status=status)
    return get_agents(
        db, skip=skip, limit=limit, status=status, owner_id=current_user.id
    )

@router.get("/{agent_id}", response_model=Agent)
async def read_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get agent by ID
    """
    agent = get_agent(db, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    # Check permissions
    if agent.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this agent"
        )
    return agent

@router.put("/{agent_id}", response_model=Agent)
async def update_agent_details(
    agent_id: int,
    agent_in: AgentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update agent
    """
    agent = get_agent(db, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    # Check permissions
    if agent.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this agent"
        )
    return update_agent(db=db, db_obj=agent, obj_in=agent_in)

@router.delete("/{agent_id}", response_model=Agent)
async def delete_agent_by_id(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Delete agent
    """
    agent = get_agent(db, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    # Check permissions
    if agent.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this agent"
        )
    return delete_agent(db=db, id=agent_id)

@router.post("/{agent_id}/start", response_model=Agent)
async def start_agent_by_id(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Start agent
    """
    agent = get_agent(db, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    # Check permissions
    if agent.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to start this agent"
        )
    return start_agent(db=db, agent=agent)

@router.post("/{agent_id}/stop", response_model=Agent)
async def stop_agent_by_id(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Stop agent
    """
    agent = get_agent(db, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    # Check permissions
    if agent.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to stop this agent"
        )
    return stop_agent(db=db, agent=agent)

@router.post("/{agent_id}/pause", response_model=Agent)
async def pause_agent_by_id(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Pause agent
    """
    agent = get_agent(db, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    # Check permissions
    if agent.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to pause this agent"
        )
    return pause_agent(db=db, agent=agent)
