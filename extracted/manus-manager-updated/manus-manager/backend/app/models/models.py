from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
import datetime

from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    
    # Google authentication fields
    google_id = Column(String, nullable=True, unique=True)
    full_name = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    
    # Relationships
    agents = relationship("Agent", back_populates="owner", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    status = Column(String, default="idle")  # idle, running, paused, error, terminated
    owner_id = Column(Integer, ForeignKey("users.id"))
    instance_url = Column(String, nullable=True)
    api_key = Column(String, nullable=True)
    max_tasks = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    last_active = Column(DateTime, nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="agents")
    tasks = relationship("Task", back_populates="agent", cascade="all, delete-orphan")
    logs = relationship("AgentLog", back_populates="agent", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    status = Column(String, default="pending")  # pending, in_progress, completed, failed, cancelled
    owner_id = Column(Integer, ForeignKey("users.id"))
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    priority = Column(Integer, default=0)  # 0: low, 1: medium, 2: high, 3: critical
    progress = Column(Float, default=0)  # 0-100
    
    # Relationships
    owner = relationship("User", back_populates="tasks")
    agent = relationship("Agent", back_populates="tasks")
    logs = relationship("TaskLog", back_populates="task", cascade="all, delete-orphan")

class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    level = Column(String, default="info")  # info, warning, error
    message = Column(Text)
    
    # Relationships
    agent = relationship("Agent", back_populates="logs")

class TaskLog(Base):
    __tablename__ = "task_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    level = Column(String, default="info")  # info, warning, error
    message = Column(Text)
    
    # Relationships
    task = relationship("Task", back_populates="logs")
