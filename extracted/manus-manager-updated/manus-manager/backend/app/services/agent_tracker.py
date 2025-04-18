from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio

from app.models.models import Agent, Task, AgentLog, TaskLog
from app.schemas.schemas import AgentStatus, TaskStatus

class AgentTracker:
    """
    Service for tracking agent activities and status
    """
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: int):
        """
        Connect a user to the agent tracker
        """
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """
        Disconnect a user from the agent tracker
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def broadcast_agent_update(self, user_id: int, agent_data: Dict):
        """
        Broadcast agent update to all connected clients for a user
        """
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json({
                    "type": "agent_update",
                    "data": agent_data
                })
    
    async def broadcast_task_update(self, user_id: int, task_data: Dict):
        """
        Broadcast task update to all connected clients for a user
        """
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json({
                    "type": "task_update",
                    "data": task_data
                })
    
    async def broadcast_log_update(self, user_id: int, log_data: Dict):
        """
        Broadcast log update to all connected clients for a user
        """
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json({
                    "type": "log_update",
                    "data": log_data
                })
    
    def log_agent_activity(self, db: Session, agent_id: int, message: str, level: str = "INFO", details: Optional[str] = None):
        """
        Log agent activity
        """
        log = AgentLog(
            agent_id=agent_id,
            message=message,
            level=level,
            details=details
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        
        # Get the agent to find the owner_id
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if agent:
            # Create a task to broadcast the log update
            asyncio.create_task(self.broadcast_log_update(
                agent.owner_id,
                {
                    "id": log.id,
                    "agent_id": log.agent_id,
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.level,
                    "message": log.message,
                    "details": log.details
                }
            ))
        
        return log
    
    def log_task_activity(self, db: Session, task_id: int, message: str, level: str = "INFO", details: Optional[str] = None):
        """
        Log task activity
        """
        log = TaskLog(
            task_id=task_id,
            message=message,
            level=level,
            details=details
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        
        # Get the task to find the owner_id
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            # Create a task to broadcast the log update
            asyncio.create_task(self.broadcast_log_update(
                task.owner_id,
                {
                    "id": log.id,
                    "task_id": log.task_id,
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.level,
                    "message": log.message,
                    "details": log.details
                }
            ))
        
        return log
    
    def update_agent_status(self, db: Session, agent_id: int, status: AgentStatus):
        """
        Update agent status
        """
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            return None
        
        agent.status = status
        agent.last_active = datetime.now()
        db.add(agent)
        db.commit()
        db.refresh(agent)
        
        # Log the status change
        self.log_agent_activity(
            db, 
            agent_id, 
            f"Agent status changed to {status}",
            "INFO"
        )
        
        # Create a task to broadcast the agent update
        asyncio.create_task(self.broadcast_agent_update(
            agent.owner_id,
            {
                "id": agent.id,
                "name": agent.name,
                "status": agent.status,
                "last_active": agent.last_active.isoformat()
            }
        ))
        
        return agent
    
    def update_task_progress(self, db: Session, task_id: int, progress: int, status: Optional[TaskStatus] = None):
        """
        Update task progress
        """
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None
        
        task.progress = progress
        if status:
            task.status = status
            
            # Update timestamps based on status
            if status == TaskStatus.IN_PROGRESS and not task.started_at:
                task.started_at = datetime.now()
            elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED] and not task.completed_at:
                task.completed_at = datetime.now()
        
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # Log the progress update
        self.log_task_activity(
            db, 
            task_id, 
            f"Task progress updated to {progress}%" + (f" with status {status}" if status else ""),
            "INFO"
        )
        
        # Create a task to broadcast the task update
        asyncio.create_task(self.broadcast_task_update(
            task.owner_id,
            {
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "progress": task.progress,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
        ))
        
        return task
    
    def get_agent_logs(self, db: Session, agent_id: int, limit: int = 100):
        """
        Get logs for an agent
        """
        return db.query(AgentLog).filter(AgentLog.agent_id == agent_id).order_by(AgentLog.timestamp.desc()).limit(limit).all()
    
    def get_task_logs(self, db: Session, task_id: int, limit: int = 100):
        """
        Get logs for a task
        """
        return db.query(TaskLog).filter(TaskLog.task_id == task_id).order_by(TaskLog.timestamp.desc()).limit(limit).all()

# Create a singleton instance
agent_tracker = AgentTracker()
