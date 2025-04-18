from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

class TokenPayload(BaseModel):
    sub: Optional[str] = None

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None

class UserCreate(UserBase):
    password: str
    google_id: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    google_id: Optional[str] = None

    class Config:
        orm_mode = True

# Agent schemas
class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "idle"
    max_tasks: int = 5
    instance_url: Optional[str] = None
    api_key: Optional[str] = None

class AgentCreate(AgentBase):
    owner_id: int

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    max_tasks: Optional[int] = None
    instance_url: Optional[str] = None
    api_key: Optional[str] = None

class AgentResponse(AgentBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_active: Optional[datetime] = None

    class Config:
        orm_mode = True

# Task schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "pending"
    priority: int = 0
    progress: float = 0

class TaskCreate(TaskBase):
    owner_id: int
    agent_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    progress: Optional[float] = None
    agent_id: Optional[int] = None

class TaskResponse(TaskBase):
    id: int
    owner_id: int
    agent_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True

# Log schemas
class LogBase(BaseModel):
    level: str
    message: str

class AgentLogCreate(LogBase):
    agent_id: int

class TaskLogCreate(LogBase):
    task_id: int

class LogResponse(LogBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class AgentLogResponse(LogResponse):
    agent_id: int

    class Config:
        orm_mode = True

class TaskLogResponse(LogResponse):
    task_id: int

    class Config:
        orm_mode = True

# Google Auth schemas
class GoogleAuthRequest(BaseModel):
    token: str

class GoogleAuthResponse(BaseModel):
    auth_url: str
