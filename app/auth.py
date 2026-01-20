"""
Authentication and authorization utilities
"""

import hashlib
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_password_hash(password: str) -> str:
    """Hash a password using SHA-256 with salt"""
    salt = "social_media_automation_salt"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return get_password_hash(plain_password) == hashed_password

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get the current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        print(f"DEBUG: Decoding token: {token[:20]}...")
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        print(f"DEBUG: Token payload: {payload}")
        email: str = payload.get("sub")
        if email is None:
            print("DEBUG: No 'sub' field in token payload")
            raise credentials_exception
        print(f"DEBUG: Extracted email: {email}")
    except JWTError as e:
        print(f"DEBUG: JWT decode error: {e}")
        raise credentials_exception
    except Exception as e:
        print(f"DEBUG: Unexpected error in token validation: {e}")
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        print(f"DEBUG: User not found for email: {email}")
        raise credentials_exception

    if not user.is_active:
        print(f"DEBUG: User {email} is not active")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    print(f"DEBUG: Authentication successful for user: {email}")
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user (alias for get_current_user)"""
    return current_user