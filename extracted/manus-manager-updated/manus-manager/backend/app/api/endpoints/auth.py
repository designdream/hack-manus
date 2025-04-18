from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Any, Dict

from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import Token, UserCreate, UserResponse
from app.core.security import (
    create_access_token, 
    verify_password, 
    ACCESS_TOKEN_EXPIRE_MINUTES,
    verify_google_token,
    GOOGLE_CLIENT_ID,
    GOOGLE_REDIRECT_URI
)
from app.services.user_service import get_user_by_email, create_user, get_current_active_user

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }

@router.post("/google", response_model=Token)
async def login_with_google(
    request: Dict[str, str],
    db: Session = Depends(get_db)
) -> Any:
    """
    Login with Google OAuth2
    """
    # Verify the Google token
    token = request.get("token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google token is required",
        )
    
    # Verify the token and get user info
    google_user = verify_google_token(token)
    
    # Check if user exists
    user = get_user_by_email(db, email=google_user["email"])
    
    # If user doesn't exist, create a new one
    if not user:
        user_in = UserCreate(
            username=google_user["email"].split("@")[0],
            email=google_user["email"],
            password="",  # No password for Google users
            is_active=True,
            is_superuser=False,
            google_id=google_user["sub"],
            full_name=google_user.get("name", ""),
            profile_picture=google_user.get("picture", "")
        )
        user = create_user(db, user_in, is_google_user=True)
    elif not user.google_id:
        # Update existing user with Google ID if they didn't have one
        user.google_id = google_user["sub"]
        user.profile_picture = google_user.get("picture", user.profile_picture)
        user.full_name = google_user.get("name", user.full_name)
        db.commit()
        db.refresh(user)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }

@router.get("/google/auth-url")
async def get_google_auth_url() -> Dict[str, str]:
    """
    Get Google OAuth2 authorization URL
    """
    if not GOOGLE_CLIENT_ID or not GOOGLE_REDIRECT_URI:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth2 is not configured",
        )
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?response_type=token&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope=email%20profile"
    
    return {"auth_url": auth_url}

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user
    """
    return current_user
