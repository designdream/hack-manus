from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status, Query
from sqlalchemy.orm import Session
from typing import Any, List, Optional

from app.db.session import get_db
from app.schemas.schemas import AgentLog as AgentLogSchema, TaskLog as TaskLogSchema
from app.services.agent_tracker import agent_tracker
from app.services.user_service import get_current_user, get_current_active_user
from app.schemas.schemas import User

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time agent tracking
    """
    # Authenticate the WebSocket connection
    # In a real implementation, you would validate a token here
    # For now, we just check if the user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    await agent_tracker.connect(websocket, user_id)
    try:
        while True:
            # Wait for messages from the client
            data = await websocket.receive_text()
            # Process messages if needed
    except WebSocketDisconnect:
        agent_tracker.disconnect(websocket, user_id)

@router.get("/agents/{agent_id}/logs", response_model=List[AgentLogSchema])
async def read_agent_logs(
    agent_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get logs for an agent
    """
    # Check if the agent belongs to the current user
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    if agent.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this agent's logs"
        )
    
    return agent_tracker.get_agent_logs(db, agent_id, limit)

@router.get("/tasks/{task_id}/logs", response_model=List[TaskLogSchema])
async def read_task_logs(
    task_id: int,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get logs for a task
    """
    # Check if the task belongs to the current user
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this task's logs"
        )
    
    return agent_tracker.get_task_logs(db, task_id, limit)

@router.post("/agents/{agent_id}/status/{status}")
async def update_agent_status(
    agent_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update agent status
    """
    # Check if the agent belongs to the current user
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    if agent.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this agent's status"
        )
    
    # Validate status
    try:
        agent_status = AgentStatus(status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {status}"
        )
    
    return agent_tracker.update_agent_status(db, agent_id, agent_status)

@router.post("/tasks/{task_id}/progress/{progress}")
async def update_task_progress(
    task_id: int,
    progress: int,
    task_status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update task progress
    """
    # Check if the task belongs to the current user
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    if task.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this task's progress"
        )
    
    # Validate progress
    if progress < 0 or progress > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Progress must be between 0 and 100"
        )
    
    # Validate status if provided
    task_status_enum = None
    if task_status:
        try:
            task_status_enum = TaskStatus(task_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {task_status}"
            )
    
    return agent_tracker.update_task_progress(db, task_id, progress, task_status_enum)
