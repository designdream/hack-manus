from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base_class import Base
from app.models.models import Agent, AgentStatus

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class AgentService:
    def create_agent(self, db: Session, *, obj_in: CreateSchemaType) -> Agent:
        """
        Create a new agent
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = Agent(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_agent(self, db: Session, id: int) -> Optional[Agent]:
        """
        Get agent by ID
        """
        return db.query(Agent).filter(Agent.id == id).first()

    def get_agents(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        owner_id: Optional[int] = None
    ) -> List[Agent]:
        """
        Get multiple agents with optional filtering
        """
        query = db.query(Agent)
        if status:
            query = query.filter(Agent.status == status)
        if owner_id:
            query = query.filter(Agent.owner_id == owner_id)
        return query.offset(skip).limit(limit).all()

    def update_agent(
        self, 
        db: Session, 
        *, 
        db_obj: Agent, 
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Agent:
        """
        Update agent
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_agent(self, db: Session, *, id: int) -> Agent:
        """
        Delete agent
        """
        obj = db.query(Agent).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def start_agent(self, db: Session, *, agent: Agent) -> Agent:
        """
        Start agent
        """
        # Here we would implement the actual logic to start a Manus agent
        # For now, we just update the status
        agent.status = AgentStatus.RUNNING
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent

    def stop_agent(self, db: Session, *, agent: Agent) -> Agent:
        """
        Stop agent
        """
        # Here we would implement the actual logic to stop a Manus agent
        # For now, we just update the status
        agent.status = AgentStatus.IDLE
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent

    def pause_agent(self, db: Session, *, agent: Agent) -> Agent:
        """
        Pause agent
        """
        # Here we would implement the actual logic to pause a Manus agent
        # For now, we just update the status
        agent.status = AgentStatus.PAUSED
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent

# Create a singleton instance
agent_service = AgentService()

# Export functions for easier imports
def create_agent(db: Session, *, obj_in: CreateSchemaType) -> Agent:
    return agent_service.create_agent(db=db, obj_in=obj_in)

def get_agent(db: Session, id: int) -> Optional[Agent]:
    return agent_service.get_agent(db=db, id=id)

def get_agents(
    db: Session, 
    *, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None,
    owner_id: Optional[int] = None
) -> List[Agent]:
    return agent_service.get_agents(db=db, skip=skip, limit=limit, status=status, owner_id=owner_id)

def update_agent(
    db: Session, 
    *, 
    db_obj: Agent, 
    obj_in: Union[UpdateSchemaType, Dict[str, Any]]
) -> Agent:
    return agent_service.update_agent(db=db, db_obj=db_obj, obj_in=obj_in)

def delete_agent(db: Session, *, id: int) -> Agent:
    return agent_service.delete_agent(db=db, id=id)

def start_agent(db: Session, *, agent: Agent) -> Agent:
    return agent_service.start_agent(db=db, agent=agent)

def stop_agent(db: Session, *, agent: Agent) -> Agent:
    return agent_service.stop_agent(db=db, agent=agent)

def pause_agent(db: Session, *, agent: Agent) -> Agent:
    return agent_service.pause_agent(db=db, agent=agent)
