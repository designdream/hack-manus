from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Any, List, Optional
from datetime import datetime

from app.db.session import get_db
from app.schemas.schemas import Task, TaskCreate, TaskUpdate
from app.services.task_service import (
    create_task,
    get_task,
    get_tasks,
    update_task,
    delete_task,
    assign_task_to_agent
)
from app.services.user_service import get_current_user
from app.schemas.schemas import User

router = APIRouter()

@router.post("/", response_model=Task)
async def create_new_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create new task
    """
    # Only allow creating tasks for the current user or if superuser
    if task_in.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create task for another user"
        )
    return create_task(db=db, obj_in=task_in)

@router.get("/", response_model=List[Task])
async def read_tasks(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    agent_id: Optional[int] = None,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve tasks
    """
    # If superuser, can see all tasks, otherwise only own tasks
    if current_user.is_superuser:
        return get_tasks(db, skip=skip, limit=limit, status=status, agent_id=agent_id)
    return get_tasks(
        db, skip=skip, limit=limit, status=status, agent_id=agent_id, owner_id=current_user.id
    )

@router.get("/{task_id}", response_model=Task)
async def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get task by ID
    """
    task = get_task(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    # Check permissions
    if task.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this task"
        )
    return task

@router.put("/{task_id}", response_model=Task)
async def update_task_details(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update task
    """
    task = get_task(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    # Check permissions
    if task.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this task"
        )
    return update_task(db=db, db_obj=task, obj_in=task_in)

@router.delete("/{task_id}", response_model=Task)
async def delete_task_by_id(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Delete task
    """
    task = get_task(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    # Check permissions
    if task.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this task"
        )
    return delete_task(db=db, id=task_id)

@router.post("/{task_id}/assign/{agent_id}", response_model=Task)
async def assign_task(
    task_id: int,
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Assign task to agent
    """
    task = get_task(db, id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    # Check permissions
    if task.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to assign this task"
        )
    return assign_task_to_agent(db=db, task_id=task_id, agent_id=agent_id)
