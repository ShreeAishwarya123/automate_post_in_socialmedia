"""
Platforms router - platform operations and testing
"""

import os
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..models import User, SocialMediaCredential
from ..auth import get_current_user

router = APIRouter()

# Import platform automation classes
from platforms.instagram import InstagramAutomation
from platforms.facebook import FacebookAutomation
from platforms.youtube import YouTubeAutomation
from platforms.linkedin import LinkedInAutomation

class TestCredentialResponse(BaseModel):
    platform: str
    success: bool
    message: str
    account_info: dict = None

@router.post("/test-credential/{credential_id}")
async def test_credential(
    credential_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test if a credential is working"""

    # Get credential
    credential = db.query(SocialMediaCredential).filter(
        SocialMediaCredential.id == credential_id,
        SocialMediaCredential.user_id == current_user.id
    ).first()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found"
        )

    try:
        success = False
        message = ""
        account_info = {}

        if credential.platform == "instagram":
            automation = InstagramAutomation(
                credential.credential_data.get("username"),
                credential.credential_data.get("password")
            )
            success = automation.login()
            if success:
                message = "Instagram login successful"
                account_info = {"username": credential.credential_data.get("username")}
            else:
                message = "Instagram login failed"

        elif credential.platform == "facebook":
            automation = FacebookAutomation(
                credential.credential_data.get("access_token"),
                credential.credential_data.get("page_id")
            )
            success = automation.validate_credentials()
            if success:
                message = "Facebook credentials valid"
                account_info = {"page_id": credential.account_id, "page_name": credential.account_name}
            else:
                message = "Facebook credentials invalid"

        elif credential.platform == "youtube":
            print(f"DEBUG: Testing YouTube for credential {credential.id}", flush=True)
            client_secrets = credential.credential_data.get("client_secrets_file")
            credentials_file = credential.credential_data.get("credentials_file")
            print(f"DEBUG: YouTube client_secrets: {client_secrets}", flush=True)
            print(f"DEBUG: YouTube credentials_file: {credentials_file}", flush=True)

            automation = YouTubeAutomation(client_secrets, credentials_file)
            print("DEBUG: YouTube automation created, calling authenticate()", flush=True)
            success = automation.authenticate()
            print(f"DEBUG: YouTube authenticate() returned: {success}", flush=True)

            if success:
                message = "YouTube authentication successful"
                account_info = {"channel_id": credential.account_id, "channel_name": credential.account_name}
                print("DEBUG: YouTube auth successful", flush=True)
            else:
                message = "YouTube authentication failed"
                print("DEBUG: YouTube auth failed", flush=True)

        elif credential.platform == "linkedin":
            automation = LinkedInAutomation(
                credential.credential_data.get("access_token"),
                credential.credential_data.get("person_urn")
            )
            success = automation.validate_credentials()
            if success:
                message = "LinkedIn credentials valid"
                account_info = {"person_urn": credential.account_id, "profile_name": credential.account_name}
            else:
                message = "LinkedIn credentials invalid"

        else:
            message = f"Testing not implemented for {credential.platform}"

        return TestCredentialResponse(
            platform=credential.platform,
            success=success,
            message=message,
            account_info=account_info
        )

    except Exception as e:
        return TestCredentialResponse(
            platform=credential.platform,
            success=False,
            message=f"Test failed: {str(e)}"
        )

class PlatformConnectionStatus(BaseModel):
    platform: str
    connected: bool
    configured: bool
    last_tested: str = None
    account_info: dict = None
    error_message: str = ""

@router.get("/connection-status")
async def get_platform_connection_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get connection status for all platforms for the current user"""

    supported_platforms = ["instagram", "facebook", "youtube", "linkedin"]
    status_results = []

    for platform in supported_platforms:
        # Check if user has credentials configured
        credential = db.query(SocialMediaCredential).filter(
            SocialMediaCredential.user_id == current_user.id,
            SocialMediaCredential.platform == platform,
            SocialMediaCredential.is_active == True
        ).first()

        if credential:
            # Test the connection
            test_result = await test_credential(credential.id, current_user, db)
            status_results.append(PlatformConnectionStatus(
                platform=platform,
                connected=test_result.success,
                configured=True,
                last_tested="now",  # Could be enhanced to store last test time
                account_info=test_result.account_info or {},
                error_message="" if test_result.success else test_result.message
            ))
        else:
            status_results.append(PlatformConnectionStatus(
                platform=platform,
                connected=False,
                configured=False,
                account_info={},
                error_message="Not configured"
            ))

    return {"platforms": status_results}

@router.post("/setup/{platform}")
async def setup_platform_connection(
    platform: str,
    credential_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Setup connection for a specific platform"""

    print(f"DEBUG: Setting up {platform} for user {current_user.email}", flush=True)
    print(f"DEBUG: Credential data received: {credential_data}", flush=True)

    supported_platforms = ["instagram", "facebook", "youtube", "linkedin"]
    if platform not in supported_platforms:
        print(f"DEBUG: Unsupported platform: {platform}", flush=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Platform {platform} not supported"
        )

    # Check if platform is already configured
    existing_credential = db.query(SocialMediaCredential).filter(
        SocialMediaCredential.user_id == current_user.id,
        SocialMediaCredential.platform == platform,
        SocialMediaCredential.is_active == True
    ).first()

    if existing_credential:
        print(f"DEBUG: Platform {platform} already configured", flush=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{platform} is already configured"
        )

    # Validate credential data based on platform
    if platform == "instagram":
        if not credential_data.get("username") or not credential_data.get("password"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Instagram requires username and password"
            )
        credential_type = "username_password"
        account_name = credential_data.get("username")

    elif platform == "facebook":
        if not credential_data.get("access_token") or not credential_data.get("page_id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Facebook requires access_token and page_id"
            )
        credential_type = "access_token"
        account_name = credential_data.get("page_name", f"Page {credential_data.get('page_id')}")

    elif platform == "youtube":
        client_secrets_path = credential_data.get("client_secrets_file")
        if not client_secrets_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="YouTube requires client_secrets_file path"
            )

        # For YouTube, we skip file validation and let the OAuth flow handle it
        # The credentials file will be created during OAuth
        credential_type = "oauth2"
        account_name = credential_data.get("channel_name", "YouTube Channel")

        # Validate file exists only after basic setup
        if not os.path.exists(client_secrets_path):
            # Don't fail here - let the OAuth test handle it
            print(f"DEBUG: YouTube client secrets file not found yet: {client_secrets_path}")
        else:
            # Quick validation if file exists
            try:
                with open(client_secrets_path, 'r') as f:
                    secrets_data = json.load(f)
                print(f"DEBUG: YouTube client secrets file validated")
            except Exception as e:
                print(f"DEBUG: YouTube client secrets validation warning: {e}")
                # Don't fail - let OAuth handle it

    elif platform == "linkedin":
        if not credential_data.get("access_token") or not credential_data.get("person_urn"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="LinkedIn requires access_token and person_urn"
            )
        credential_type = "access_token"
        account_name = credential_data.get("profile_name", "LinkedIn Profile")

    # Create the credential
    db_credential = SocialMediaCredential(
        user_id=current_user.id,
        platform=platform,
        credential_type=credential_type,
        credential_data=credential_data,
        account_name=account_name,
        account_id=credential_data.get("page_id") or credential_data.get("person_urn") or credential_data.get("channel_id"),
        is_active=True
    )

    db.add(db_credential)
    db.commit()
    db.refresh(db_credential)

    # Test the connection
    test_result = await test_credential(db_credential.id, current_user, db)

    return {
        "platform": platform,
        "credential_id": db_credential.id,
        "status": "configured",
        "connection_test": {
            "success": test_result.success,
            "message": test_result.message,
            "account_info": test_result.account_info
        }
    }

@router.delete("/connection/{platform}")
async def disconnect_platform(
    platform: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect/remove platform connection"""

    credential = db.query(SocialMediaCredential).filter(
        SocialMediaCredential.user_id == current_user.id,
        SocialMediaCredential.platform == platform,
        SocialMediaCredential.is_active == True
    ).first()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active connection found for {platform}"
        )

    # Soft delete by setting inactive
    credential.is_active = False
    db.commit()

    return {"message": f"{platform} connection removed successfully"}

@router.get("/onboarding-status")
async def get_onboarding_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's onboarding status - which platforms are connected"""

    connection_status = await get_platform_connection_status(current_user, db)

    # Count connected platforms
    connected_count = sum(1 for p in connection_status["platforms"] if p.connected)

    return {
        "user_id": current_user.id,
        "onboarding_complete": connected_count > 0,
        "connected_platforms": connected_count,
        "total_platforms": len(connection_status["platforms"]),
        "platforms": connection_status["platforms"],
        "next_steps": [
            "Connect at least one social media platform" if connected_count == 0 else None,
            "Test your connections" if connected_count > 0 else None,
            "Create your first AI-generated post" if connected_count > 0 else None
        ]
    }

@router.get("/supported")
async def get_supported_platforms():
    """Get list of supported platforms"""
    return {
        "platforms": [
            {
                "name": "instagram",
                "display_name": "Instagram",
                "supports": ["text", "image", "video"],
                "features": ["posts", "reels", "carousel"],
                "setup_requirements": ["username", "password"],
                "description": "Share photos and videos with your followers"
            },
            {
                "name": "facebook",
                "display_name": "Facebook",
                "supports": ["text", "image", "video"],
                "features": ["posts", "pages", "scheduling"],
                "setup_requirements": ["access_token", "page_id"],
                "description": "Post to your Facebook page or profile"
            },
            {
                "name": "youtube",
                "display_name": "YouTube",
                "supports": ["video"],
                "features": ["videos", "titles", "descriptions", "tags"],
                "setup_requirements": ["client_secrets.json", "credentials.json"],
                "description": "Upload videos to your YouTube channel"
            },
            {
                "name": "linkedin",
                "display_name": "LinkedIn",
                "supports": ["text", "image", "video"],
                "features": ["posts", "articles", "professional_networking"],
                "setup_requirements": ["access_token", "person_urn"],
                "description": "Share professional content with your network"
            }
        ]
    }