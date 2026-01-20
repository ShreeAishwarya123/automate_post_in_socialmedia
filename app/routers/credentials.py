"""
Credentials router - manage social media platform credentials
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Any, Optional
import json

from ..database import get_db
from ..models import User, SocialMediaCredential
from ..auth import get_current_user

router = APIRouter()

# Pydantic models
class CredentialCreate(BaseModel):
    platform: str  # instagram, facebook, youtube, linkedin
    credential_type: str  # api_key, access_token, username_password
    credential_data: Dict[str, Any]  # The actual credentials
    account_name: Optional[str] = None
    account_id: Optional[str] = None

class CredentialUpdate(BaseModel):
    credential_data: Optional[Dict[str, Any]] = None
    account_name: Optional[str] = None
    account_id: Optional[str] = None
    is_active: Optional[bool] = None

class CredentialResponse(BaseModel):
    id: int
    platform: str
    credential_type: str
    account_name: Optional[str]
    account_id: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True

# Platform configurations
PLATFORM_CONFIGS = {
    "instagram": {
        "required_fields": ["username", "password"],
        "credential_type": "username_password"
    },
    "facebook": {
        "required_fields": ["access_token", "page_id"],
        "credential_type": "access_token"
    },
    "youtube": {
        "required_fields": ["client_secrets_file", "credentials_file"],
        "credential_type": "oauth2_files"
    },
    "linkedin": {
        "required_fields": ["access_token", "person_urn"],
        "credential_type": "access_token"
    }
}

@router.post("", response_model=CredentialResponse)
async def create_credential(
    credential_data: CredentialCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new social media credential"""

    # Validate platform
    if credential_data.platform not in PLATFORM_CONFIGS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported platform: {credential_data.platform}"
        )

    platform_config = PLATFORM_CONFIGS[credential_data.platform]

    # Check if credential already exists for this platform
    existing = db.query(SocialMediaCredential).filter(
        SocialMediaCredential.user_id == current_user.id,
        SocialMediaCredential.platform == credential_data.platform
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Credential already exists for {credential_data.platform}"
        )

    # Validate required fields
    required_fields = platform_config["required_fields"]
    for field in required_fields:
        if field not in credential_data.credential_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )

    # Create credential (in a real app, encrypt the credential_data)
    db_credential = SocialMediaCredential(
        user_id=current_user.id,
        platform=credential_data.platform,
        credential_type=credential_data.credential_type,
        credential_data=credential_data.credential_data,  # TODO: Encrypt this
        account_name=credential_data.account_name,
        account_id=credential_data.account_id
    )

    db.add(db_credential)
    db.commit()
    db.refresh(db_credential)

    return db_credential

@router.get("", response_model=list[CredentialResponse])
async def get_credentials(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all credentials for the current user"""
    credentials = db.query(SocialMediaCredential).filter(
        SocialMediaCredential.user_id == current_user.id
    ).all()

    return credentials

@router.get("/{credential_id}", response_model=CredentialResponse)
async def get_credential(
    credential_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific credential"""
    credential = db.query(SocialMediaCredential).filter(
        SocialMediaCredential.id == credential_id,
        SocialMediaCredential.user_id == current_user.id
    ).first()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found"
        )

    return credential

@router.put("/{credential_id}", response_model=CredentialResponse)
async def update_credential(
    credential_id: int,
    updates: CredentialUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a credential"""
    credential = db.query(SocialMediaCredential).filter(
        SocialMediaCredential.id == credential_id,
        SocialMediaCredential.user_id == current_user.id
    ).first()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found"
        )

    # Update fields
    if updates.credential_data is not None:
        # TODO: Encrypt the new credential data
        credential.credential_data = updates.credential_data

    if updates.account_name is not None:
        credential.account_name = updates.account_name

    if updates.account_id is not None:
        credential.account_id = updates.account_id

    if updates.is_active is not None:
        credential.is_active = updates.is_active

    db.commit()
    db.refresh(credential)

    return credential

@router.delete("/{credential_id}")
async def delete_credential(
    credential_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a credential"""
    credential = db.query(SocialMediaCredential).filter(
        SocialMediaCredential.id == credential_id,
        SocialMediaCredential.user_id == current_user.id
    ).first()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found"
        )

    db.delete(credential)
    db.commit()

    return {"message": "Credential deleted successfully"}

@router.get("/platforms/config")
async def get_platform_configs():
    """Get configuration for all supported platforms"""
    return PLATFORM_CONFIGS