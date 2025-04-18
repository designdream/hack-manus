from typing import Any, Dict, List, Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.security import verify_password, get_password_hash, SECRET_KEY, ALGORITHM
from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import TokenPayload, UserCreate, UserUpdate

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class UserService:
    def get_user(self, db: Session, *, id: Optional[int] = None, email: Optional[str] = None) -> Optional[User]:
        """
        Get user by ID or email
        """
        if id:
            return db.query(User).filter(User.id == id).first()
        if email:
            return db.query(User).filter(User.email == email).first()
        return None

    def get_users(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get multiple users
        """
        return db.query(User).offset(skip).limit(limit).all()

    def create_user(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Create new user
        """
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_user(self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
        """
        Update user
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        
        for field in update_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_user(self, db: Session, *, id: int) -> User:
        """
        Delete user
        """
        user = db.query(User).get(id)
        db.delete(user)
        db.commit()
        return user

    def authenticate_user(self, db: Session, *, username: str, password: str) -> Optional[User]:
        """
        Authenticate user by username and password
        """
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def get_current_user(self, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
        """
        Get current user from JWT token
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            token_data = TokenPayload(**payload)
        except (JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        
        user = self.get_user(db, id=token_data.sub)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    async def get_current_active_user(self, current_user: User = Depends(get_current_user)) -> User:
        """
        Get current active user
        """
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )
        return current_user

    async def get_current_active_superuser(self, current_user: User = Depends(get_current_user)) -> User:
        """
        Get current active superuser
        """
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return current_user

# Create a singleton instance
user_service = UserService()

# Export functions for easier imports
def get_user(db: Session, *, id: Optional[int] = None, email: Optional[str] = None) -> Optional[User]:
    return user_service.get_user(db=db, id=id, email=email)

def get_users(db: Session, *, skip: int = 0, limit: int = 100) -> List[User]:
    return user_service.get_users(db=db, skip=skip, limit=limit)

def create_user(db: Session, *, obj_in: UserCreate) -> User:
    return user_service.create_user(db=db, obj_in=obj_in)

def update_user(db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
    return user_service.update_user(db=db, db_obj=db_obj, obj_in=obj_in)

def delete_user(db: Session, *, id: int) -> User:
    return user_service.delete_user(db=db, id=id)

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    return user_service.authenticate_user(db=db, username=username, password=password)

# Export dependency functions
get_current_user = user_service.get_current_user
get_current_active_user = user_service.get_current_active_user
get_current_active_superuser = user_service.get_current_active_superuser
