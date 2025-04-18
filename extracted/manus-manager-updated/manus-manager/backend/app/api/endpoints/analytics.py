from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List, Dict
import json

from app.db.session import get_db
from app.models.models import Agent, Task
from app.schemas.schemas import AgentStatus, TaskStatus
from app.services.agent_tracker import agent_tracker
from app.services.user_service import get_current_active_user
from app.schemas.schemas import User

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get dashboard data for the current user
    """
    # Get agents owned by the current user
    agents_query = db.query(Agent).filter(Agent.owner_id == current_user.id)
    agents = agents_query.all()
    
    # Get tasks owned by the current user
    tasks_query = db.query(Task).filter(Task.owner_id == current_user.id)
    tasks = tasks_query.all()
    
    # Count agents by status
    agent_status_counts = {status.value: 0 for status in AgentStatus}
    for agent in agents:
        agent_status_counts[agent.status] += 1
    
    # Count tasks by status
    task_status_counts = {status.value: 0 for status in TaskStatus}
    for task in tasks:
        task_status_counts[task.status] += 1
    
    # Calculate overall task progress
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.status == TaskStatus.COMPLETED)
    failed_tasks = sum(1 for task in tasks if task.status == TaskStatus.FAILED)
    in_progress_tasks = sum(1 for task in tasks if task.status == TaskStatus.IN_PROGRESS)
    pending_tasks = sum(1 for task in tasks if task.status == TaskStatus.PENDING)
    
    overall_progress = 0
    if total_tasks > 0:
        overall_progress = int((completed_tasks / total_tasks) * 100)
    
    return {
        "agent_count": len(agents),
        "task_count": total_tasks,
        "agent_status_counts": agent_status_counts,
        "task_status_counts": task_status_counts,
        "overall_progress": overall_progress,
        "completed_tasks": completed_tasks,
        "failed_tasks": failed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "pending_tasks": pending_tasks
    }

@router.get("/agents/stats")
async def get_agent_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get statistics for all agents owned by the current user
    """
    # Get agents owned by the current user
    agents_query = db.query(Agent).filter(Agent.owner_id == current_user.id)
    agents = agents_query.all()
    
    agent_stats = []
    for agent in agents:
        # Get tasks assigned to this agent
        tasks = db.query(Task).filter(Task.agent_id == agent.id).all()
        
        # Calculate task statistics
        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks if task.status == TaskStatus.COMPLETED)
        failed_tasks = sum(1 for task in tasks if task.status == TaskStatus.FAILED)
        in_progress_tasks = sum(1 for task in tasks if task.status == TaskStatus.IN_PROGRESS)
        
        # Calculate success rate
        success_rate = 0
        if completed_tasks + failed_tasks > 0:
            success_rate = int((completed_tasks / (completed_tasks + failed_tasks)) * 100)
        
        agent_stats.append({
            "id": agent.id,
            "name": agent.name,
            "status": agent.status,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "success_rate": success_rate,
            "last_active": agent.last_active.isoformat() if agent.last_active else None
        })
    
    return agent_stats

@router.get("/tasks/stats")
async def get_task_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get statistics for all tasks owned by the current user
    """
    # Get tasks owned by the current user
    tasks_query = db.query(Task).filter(Task.owner_id == current_user.id)
    tasks = tasks_query.all()
    
    # Calculate average completion time for completed tasks
    completed_tasks = [task for task in tasks if task.status == TaskStatus.COMPLETED and task.started_at and task.completed_at]
    avg_completion_time_seconds = 0
    if completed_tasks:
        completion_times = [(task.completed_at - task.started_at).total_seconds() for task in completed_tasks]
        avg_completion_time_seconds = sum(completion_times) / len(completion_times)
    
    # Group tasks by priority
    tasks_by_priority = {}
    for task in tasks:
        priority = task.priority
        if priority not in tasks_by_priority:
            tasks_by_priority[priority] = 0
        tasks_by_priority[priority] += 1
    
    return {
        "total_tasks": len(tasks),
        "completed_tasks": sum(1 for task in tasks if task.status == TaskStatus.COMPLETED),
        "failed_tasks": sum(1 for task in tasks if task.status == TaskStatus.FAILED),
        "in_progress_tasks": sum(1 for task in tasks if task.status == TaskStatus.IN_PROGRESS),
        "pending_tasks": sum(1 for task in tasks if task.status == TaskStatus.PENDING),
        "avg_completion_time_seconds": avg_completion_time_seconds,
        "tasks_by_priority": tasks_by_priority
    }

@router.get("/agents/{agent_id}/performance")
async def get_agent_performance(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get detailed performance metrics for a specific agent
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
            detail="Not enough permissions to access this agent's performance"
        )
    
    # Get tasks assigned to this agent
    tasks = db.query(Task).filter(Task.agent_id == agent_id).all()
    
    # Calculate task completion times
    task_completion_times = []
    for task in tasks:
        if task.status == TaskStatus.COMPLETED and task.started_at and task.completed_at:
            completion_time = (task.completed_at - task.started_at).total_seconds()
            task_completion_times.append({
                "task_id": task.id,
                "title": task.title,
                "completion_time_seconds": completion_time
            })
    
    # Get agent logs
    logs = agent_tracker.get_agent_logs(db, agent_id, limit=100)
    log_data = [
        {
            "id": log.id,
            "timestamp": log.timestamp.isoformat(),
            "level": log.level,
            "message": log.message
        }
        for log in logs
    ]
    
    return {
        "agent_id": agent.id,
        "name": agent.name,
        "status": agent.status,
        "total_tasks": len(tasks),
        "completed_tasks": sum(1 for task in tasks if task.status == TaskStatus.COMPLETED),
        "failed_tasks": sum(1 for task in tasks if task.status == TaskStatus.FAILED),
        "in_progress_tasks": sum(1 for task in tasks if task.status == TaskStatus.IN_PROGRESS),
        "task_completion_times": task_completion_times,
        "recent_logs": log_data,
        "last_active": agent.last_active.isoformat() if agent.last_active else None
    }
