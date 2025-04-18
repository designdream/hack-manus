from typing import Any, Dict, List, Optional, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.models import Task, TaskStatus
from app.db.base_class import Base

class TaskService:
    def create_task(self, db: Session, *, obj_in: Any) -> Task:
        """
        Create a new task
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = Task(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_task(self, db: Session, id: int) -> Optional[Task]:
        """
        Get task by ID
        """
        return db.query(Task).filter(Task.id == id).first()

    def get_tasks(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        agent_id: Optional[int] = None,
        owner_id: Optional[int] = None
    ) -> List[Task]:
        """
        Get multiple tasks with optional filtering
        """
        query = db.query(Task)
        if status:
            query = query.filter(Task.status == status)
        if agent_id:
            query = query.filter(Task.agent_id == agent_id)
        if owner_id:
            query = query.filter(Task.owner_id == owner_id)
        return query.offset(skip).limit(limit).all()

    def update_task(
        self, 
        db: Session, 
        *, 
        db_obj: Task, 
        obj_in: Union[BaseModel, Dict[str, Any]]
    ) -> Task:
        """
        Update task
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        # Update timestamps based on status changes
        if 'status' in update_data:
            if update_data['status'] == TaskStatus.IN_PROGRESS and not db_obj.started_at:
                db_obj.started_at = datetime.now()
            elif update_data['status'] in [TaskStatus.COMPLETED, TaskStatus.FAILED] and not db_obj.completed_at:
                db_obj.completed_at = datetime.now()
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_task(self, db: Session, *, id: int) -> Task:
        """
        Delete task
        """
        obj = db.query(Task).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def assign_task_to_agent(self, db: Session, *, task_id: int, agent_id: int) -> Task:
        """
        Assign task to agent
        """
        task = db.query(Task).get(task_id)
        if not task:
            return None
        
        # Update task with agent_id
        task.agent_id = agent_id
        
        # If task was pending, set to in_progress
        if task.status == TaskStatus.PENDING:
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now()
        
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

# Create a singleton instance
task_service = TaskService()

# Export functions for easier imports
def create_task(db: Session, *, obj_in: Any) -> Task:
    return task_service.create_task(db=db, obj_in=obj_in)

def get_task(db: Session, id: int) -> Optional[Task]:
    return task_service.get_task(db=db, id=id)

def get_tasks(
    db: Session, 
    *, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None,
    agent_id: Optional[int] = None,
    owner_id: Optional[int] = None
) -> List[Task]:
    return task_service.get_tasks(
        db=db, skip=skip, limit=limit, status=status, 
        agent_id=agent_id, owner_id=owner_id
    )

def update_task(
    db: Session, 
    *, 
    db_obj: Task, 
    obj_in: Union[BaseModel, Dict[str, Any]]
) -> Task:
    return task_service.update_task(db=db, db_obj=db_obj, obj_in=obj_in)

def delete_task(db: Session, *, id: int) -> Task:
    return task_service.delete_task(db=db, id=id)

def assign_task_to_agent(db: Session, *, task_id: int, agent_id: int) -> Task:
    return task_service.assign_task_to_agent(db=db, task_id=task_id, agent_id=agent_id)
