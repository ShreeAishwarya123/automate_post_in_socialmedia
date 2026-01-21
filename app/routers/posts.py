"""
Posts router - manage social media posts and publishing
"""

print("DEBUG: Loading posts router...")

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
import shutil
import time

from ..database import get_db
from ..models import User, Post, PostPlatform, SocialMediaCredential
from ..auth import get_current_user
from ..config import settings

# Import Gemini components
import sys
import os
GEMINI_ROOT = os.path.dirname(os.path.dirname(__file__))  # Root hive directory
if GEMINI_ROOT not in sys.path:
    sys.path.insert(0, GEMINI_ROOT)

try:
    from flows.gemini_flow import run_gemini_task
    from flows.drive_flow import DriveManager
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: Gemini components not available")

# Import scheduler
from scheduler import get_scheduler

# Import video utilities
from video_utils import ensure_video_playable, validate_video_file

router = APIRouter()

# Pydantic models
class PostCreate(BaseModel):
    title: Optional[str] = None
    content: str
    content_type: str  # text, image, video
    platforms: List[str]  # List of platform names
    scheduled_at: Optional[datetime] = None
    use_gemini: bool = False
    gemini_prompt: Optional[str] = None

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    platforms: Optional[List[str]] = None
    scheduled_at: Optional[datetime] = None

class PostResponse(BaseModel):
    id: int
    title: Optional[str]
    content: str
    content_type: str
    media_url: Optional[str]
    media_type: Optional[str]
    status: str
    platforms: List[str]
    scheduled_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class PlatformStatus(BaseModel):
    platform: str
    status: str
    post_url: Optional[str]
    error_message: Optional[str]

def get_user_credentials_for_platforms(user_id: int, platforms: List[str], db: Session) -> dict:
    """Get user credentials for specified platforms"""
    credentials = {}
    for platform in platforms:
        cred = db.query(SocialMediaCredential).filter(
            SocialMediaCredential.user_id == user_id,
            SocialMediaCredential.platform == platform,
            SocialMediaCredential.is_active == True
        ).first()

        if cred:
            credentials[platform] = cred

    return credentials

@router.post("", response_model=PostResponse)
async def create_post(
    title: Optional[str] = Form(None),
    content: str = Form(...),
    content_type: str = Form(...),
    platforms: str = Form(...),  # JSON string of platform list
    scheduled_at: Optional[str] = Form(None),
    use_gemini: bool = Form(False),
    gemini_prompt: Optional[str] = Form(None),
    media_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new post"""

    # Parse platforms JSON
    import json
    try:
        platforms_list = json.loads(platforms)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid platforms format"
        )

    # Handle file upload
    media_url = None
    media_filename = None

    if media_file:
        # Validate file size
        if media_file.file.seek(0, 2) > settings.max_upload_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {settings.max_upload_size} bytes"
            )
        media_file.file.seek(0)

        # Create upload directory
        os.makedirs(settings.upload_dir, exist_ok=True)

        # Save file
        file_path = os.path.join(settings.upload_dir, f"{current_user.id}_{datetime.utcnow().timestamp()}_{media_file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(media_file.file, buffer)

        media_url = file_path
        media_filename = media_file.filename

    # Parse scheduled_at
    scheduled_datetime = None
    if scheduled_at:
        try:
            scheduled_datetime = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid scheduled_at format"
            )

    # Create post
    db_post = Post(
        user_id=current_user.id,
        title=title,
        content=content,
        content_type=content_type,
        media_url=media_url,
        media_filename=media_filename,
        use_gemini=use_gemini,
        gemini_prompt=gemini_prompt,
        scheduled_at=scheduled_datetime,
        is_scheduled=scheduled_datetime is not None
    )

    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    # Create platform entries
    for platform in platforms_list:
        db_platform = PostPlatform(
            post_id=db_post.id,
            platform=platform
        )
        db.add(db_platform)

    db.commit()

    # Return response
    return PostResponse(
        id=db_post.id,
        title=db_post.title,
        content=db_post.content,
        content_type=db_post.content_type,
        media_url=db_post.media_url,
        media_type=db_post.media_type,
        status=db_post.status,
        platforms=platforms_list,
        scheduled_at=db_post.scheduled_at,
        created_at=db_post.created_at
    )

@router.get("", response_model=List[PostResponse])
async def get_posts(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's posts"""
    posts = db.query(Post).filter(Post.user_id == current_user.id).offset(skip).limit(limit).all()

    result = []
    for post in posts:
        platforms = [p.platform for p in post.platforms]
        result.append(PostResponse(
            id=post.id,
            title=post.title,
            content=post.content,
            content_type=post.content_type,
            media_url=post.media_url,
            media_type=post.media_type,
            status=post.status,
            platforms=platforms,
            scheduled_at=post.scheduled_at,
            created_at=post.created_at
        ))

    return result

@router.post("/{post_id}/publish")
async def publish_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Publish a post to all specified platforms"""

    # Get post
    post = db.query(Post).filter(
        Post.id == post_id,
        Post.user_id == current_user.id
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # Get platforms
    platforms = [p.platform for p in post.platforms]

    # Get user credentials
    credentials = get_user_credentials_for_platforms(current_user.id, platforms, db)

    results = []

    # Import and use the existing posting logic
    for platform in platforms:
        if platform not in credentials:
            results.append({
                "platform": platform,
                "status": "failed",
                "error_message": "No credentials configured for this platform"
            })
            continue

        try:
            # Integrate with the real posting logic
            cred = credentials[platform]
            print(f"DEBUG: Posting to {platform} with content_type={post.content_type}, media_url={post.media_url}")

            if platform == "instagram":
                # Import Instagram automation
                from platforms.instagram import InstagramAutomation

                # Initialize Instagram client
                instagram = InstagramAutomation(
                    cred.credential_data.get("username"),
                    cred.credential_data.get("password")
                )

                # Login
                if not instagram.login():
                    raise Exception("Instagram login failed")

                # Post based on content type
                if post.content_type == "text":
                    result_api = instagram.post_video(post.content, "") if post.media_url else instagram.post_text(post.content)
                elif post.content_type == "image" and post.media_url and os.path.exists(post.media_url):
                    result_api = instagram.post_photo(post.media_url, post.content)
                elif post.content_type == "video" and post.media_url and os.path.exists(post.media_url):
                    result_api = instagram.post_reels(post.media_url, post.content)
                else:
                    raise Exception(f"Unsupported content type: {post.content_type}")

                if result_api and result_api.get("success"):
                    result = {
                        "platform": platform,
                        "status": "posted",
                        "post_url": f"https://instagram.com/p/{result_api.get('code', post.id)}",
                        "post_id": result_api.get("media_id", f"{platform}_{post.id}")
                    }
                else:
                    raise Exception(result_api.get("error", "Unknown posting error") if result_api else "Posting failed")

            elif platform == "facebook":
                # Import Facebook automation
                from platforms.facebook import FacebookAutomation

                # Initialize Facebook client
                facebook = FacebookAutomation(
                    cred.credential_data.get("access_token"),
                    cred.credential_data.get("page_id")
                )

                # Post based on content type
                if post.content_type == "text":
                    result_api = facebook.post_text(post.content)
                elif post.content_type == "image" and post.media_url and os.path.exists(post.media_url):
                    result_api = facebook.post_photo(post.media_url, post.content)
                elif post.content_type == "video" and post.media_url and os.path.exists(post.media_url):
                    result_api = facebook.post_video(post.media_url, post.content)
                else:
                    raise Exception(f"Unsupported content type: {post.content_type}")

                if result_api and result_api.get("success"):
                    result = {
                        "platform": platform,
                        "status": "posted",
                        "post_url": f"https://facebook.com/{result_api.get('post_id', post.id)}",
                        "post_id": result_api.get("post_id", f"{platform}_{post.id}")
                    }
                else:
                    raise Exception("Facebook posting failed")

            elif platform == "linkedin":
                # Import LinkedIn automation
                from platforms.linkedin import LinkedInAutomation

                # Initialize LinkedIn client
                linkedin = LinkedInAutomation(
                    cred.credential_data.get("access_token"),
                    cred.credential_data.get("person_urn")
                )

                # Post based on content type
                if post.content_type == "text":
                    result_api = linkedin.post_text(post.content)
                elif post.content_type == "image" and post.media_url and os.path.exists(post.media_url):
                    result_api = linkedin.post_with_image(post.content, post.media_url)
                elif post.content_type == "video" and post.media_url and os.path.exists(post.media_url):
                    result_api = linkedin.post_with_video(post.content, post.media_url)
                else:
                    raise Exception(f"Unsupported content type: {post.content_type}")

                if result_api and result_api.get("success"):
                    result = {
                        "platform": platform,
                        "status": "posted",
                        "post_url": f"https://linkedin.com/feed/update/{result_api.get('post_id', post.id)}",
                        "post_id": result_api.get("post_id", f"{platform}_{post.id}")
                    }
                else:
                    raise Exception("LinkedIn posting failed")

            elif platform == "youtube":
                # Import YouTube automation
                from platforms.youtube import YouTubeAutomation

                # Initialize YouTube client
                youtube = YouTubeAutomation(
                    cred.credential_data.get("client_secrets_file"),
                    cred.credential_data.get("credentials_file")
                )

                if not youtube.authenticate():
                    raise Exception("YouTube authentication failed")

                # YouTube only supports videos
                if post.content_type == "video" and post.media_url and os.path.exists(post.media_url):
                    # Extract title and description from post content
                    title = f"Video Post {post.id}"  # You could enhance this to extract from content
                    description = post.content

                    result_api = youtube.upload_video(
                        post.media_url,
                        title,
                        description,
                        [],  # tags
                        category_id='22'  # People & Blogs
                    )

                    if result_api and result_api.get("success"):
                        result = {
                            "platform": platform,
                            "status": "posted",
                            "post_url": f"https://youtube.com/watch?v={result_api.get('video_id', '')}",
                            "post_id": result_api.get("video_id", f"{platform}_{post.id}")
                        }
                    else:
                        raise Exception("YouTube upload failed")
                else:
                    raise Exception("YouTube only supports video content")

            else:
                raise Exception(f"Platform {platform} not implemented yet")

            # Update platform status
            platform_entry = db.query(PostPlatform).filter(
                PostPlatform.post_id == post.id,
                PostPlatform.platform == platform
            ).first()

            if platform_entry:
                platform_entry.status = "posted"
                platform_entry.post_url = result["post_url"]
                platform_entry.platform_post_id = result["post_id"]
                platform_entry.posted_at = datetime.utcnow()

            results.append(result)

        except Exception as e:
            results.append({
                "platform": platform,
                "status": "failed",
                "error_message": str(e)
            })

    # Update post status
    successful_posts = [r for r in results if r["status"] == "posted"]
    if successful_posts:
        post.status = "posted" if len(successful_posts) == len(platforms) else "partially_posted"
    else:
        post.status = "failed"

    db.commit()

    return {"results": results}

@router.post("/generate-and-post")
async def generate_and_post_with_gemini(
    prompt: str = Form(...),
    content_type: str = Form(..., description="IMAGE, VIDEO, or PPT"),
    platforms: str = Form(..., description="JSON array of platforms"),
    caption: Optional[str] = Form(None),
    scheduled_at: Optional[str] = Form(None, description="ISO datetime string for scheduling, or 'now' for immediate posting"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate content with Gemini AI and post to specified platforms (immediately or scheduled)"""

    try:
        print("DEBUG: Function generate_and_post_with_gemini invoked!")
        print(f"DEBUG: prompt type: {type(prompt)}, value: {repr(prompt[:100] if prompt else None)}")
        print(f"DEBUG: content_type: {content_type}")
        print(f"DEBUG: platforms: {platforms}")
        print(f"DEBUG: current_user: {current_user.email if current_user else 'None'}")

        if not GEMINI_AVAILABLE:
            print("DEBUG: Gemini not available")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini AI service not available"
            )

        # Parse platforms JSON
        import json
        try:
            platforms_list = json.loads(platforms)
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid platforms format"
            )

        # Validate content type
        if content_type.upper() not in ["IMAGE", "VIDEO", "PPT"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content type must be IMAGE, VIDEO, or PPT"
            )

        print("DEBUG: Basic validation passed")

        # Parse scheduled_at parameter
        post_now = False
        scheduled_datetime = None

        if scheduled_at is None or scheduled_at.lower() == "now":
            post_now = True
            print("DEBUG: Posting now")
        else:
            try:
                scheduled_datetime = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
                if scheduled_datetime <= datetime.utcnow():
                    post_now = True  # If time is in the past or now, post immediately
                    scheduled_datetime = None
                    print("DEBUG: Time is past/now, posting immediately")
                else:
                    print(f"DEBUG: Scheduling for {scheduled_datetime}")
            except Exception as parse_error:
                print(f"DEBUG: Failed to parse scheduled_at '{scheduled_at}': {parse_error}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid scheduled_at format. Use ISO datetime string or 'now'"
                )

        # Check user credentials for platforms (only if posting now)
        if post_now:
            credentials = get_user_credentials_for_platforms(current_user.id, platforms_list, db)
            missing_platforms = [p for p in platforms_list if p not in credentials]
            if missing_platforms:
                print(f"DEBUG: Missing credentials for platforms: {missing_platforms}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"No credentials configured for platforms: {', '.join(missing_platforms)}"
                )
            print(f"DEBUG: Credentials found for all platforms: {list(credentials.keys())}")

        # Use caption or fallback to prompt
        post_caption = caption or f"AI-generated content: {prompt[:100]}{'...' if len(prompt) > 100 else ''}"
        print(f"DEBUG: Post caption: {post_caption[:50]}...")

        # Create post record
        db_post = Post(
            user_id=current_user.id,
            title=f"Gemini {content_type.title()} Post",
            content=post_caption,
            content_type=content_type.lower(),
            use_gemini=True,
            gemini_prompt=prompt,
            scheduled_at=scheduled_datetime,
            is_scheduled=scheduled_datetime is not None,
            status="scheduled" if scheduled_datetime else "pending"
        )

        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        print(f"DEBUG: Created post record with ID: {db_post.id}")

        # Create platform entries
        for platform in platforms_list:
            db_platform = PostPlatform(
                post_id=db_post.id,
                platform=platform,
                status="scheduled" if scheduled_datetime else "pending"
            )
            db.add(db_platform)

        db.commit()
        print(f"DEBUG: Created platform entries for: {platforms_list}")

        # If posting now, generate content and post immediately
        if post_now:
            print("DEBUG: Starting immediate content generation and posting - about to enter try block")

            try:
                print("DEBUG: Entered the main try block for content generation")
                # Test Gemini availability
                if not GEMINI_AVAILABLE:
                    raise Exception("Gemini components not available")

                print("DEBUG: Testing Gemini imports...")
                from flows.gemini_flow import run_gemini_task
                print("DEBUG: Gemini flow imported successfully")

                # Test Drive manager (optional)
                drive_credentials = os.path.join(GEMINI_ROOT, "gemini_automation", "gemini_automation", "auth", "credentials.json")
                drive = None
                try:
                    print("DEBUG: Testing DriveManager...")
                    from flows.drive_flow import DriveManager
                    drive = DriveManager(drive_credentials, allow_interactive=False)
                    print("DEBUG: DriveManager initialized successfully")
                except Exception as drive_error:
                    print(f"WARNING: DriveManager failed: {drive_error} - continuing without Drive upload")
                    drive = None

                # Create output directory
                output_base_dir = os.path.join(GEMINI_ROOT, "gemini_automation", "gemini_automation", "out")
                os.makedirs(output_base_dir, exist_ok=True)
                print(f"DEBUG: Output directory ready: {output_base_dir}")

                # Generate content with Gemini using synchronous execution to avoid asyncio conflicts
                print("DEBUG: Starting Gemini content generation with sync execution")

                import concurrent.futures
                import asyncio
                from playwright.sync_api import sync_playwright

                def run_gemini_sync():
                    """Run Gemini generation synchronously to avoid async conflicts"""
                    try:
                        print("DEBUG: Inside sync Gemini function")
                        import asyncio

                        async def inner_async():
                            from playwright.async_api import async_playwright
                            async with async_playwright() as p:
                                print("DEBUG: Async Playwright initialized")
                                context = await p.chromium.launch_persistent_context(
                                    os.path.join(GEMINI_ROOT, "auth", "user_data"),
                                    headless=False,  # Show browser for visible automation
                                    args=["--disable-blink-features=AutomationControlled"]
                                )
                                print("DEBUG: Browser context launched")

                                try:
                                    page = await context.new_page()
                                    print(f"DEBUG: Running Gemini task with prompt: {prompt[:50]}...")

                                    result = await run_gemini_task(page, prompt, content_type.upper(), output_base_dir, platforms_list)
                                    print(f"DEBUG: Gemini result: {str(result)[:100]}...")

                                    if not result:
                                        raise Exception("Gemini returned empty result")

                                    return result

                                finally:
                                    await context.close()
                                    print("DEBUG: Browser context closed")

                        # Run the async function synchronously
                        return asyncio.run(inner_async())

                    except Exception as e:
                        print(f"DEBUG: Exception in sync Gemini function: {e}")
                        import traceback
                        print(f"DEBUG: Sync Gemini traceback: {traceback.format_exc()}")
                        raise

                # Run Gemini generation in a thread to avoid asyncio conflicts
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    print("DEBUG: Submitting Gemini task to thread pool")
                    future = executor.submit(run_gemini_sync)
                    result = future.result(timeout=300)  # 5 minute timeout
                    print(f"DEBUG: Gemini generation completed, result: {str(result)[:100]}...")

                # Handle result
                local_path = result
                drive_link = ""

                if result and str(result).startswith("http"):
                    if content_type.upper() == "VIDEO":
                        # Download video from URL for posting
                        import requests
                        print(f"DEBUG: Downloading video from URL: {result}")
                        try:
                            response = requests.get(result, stream=True, timeout=300)
                            response.raise_for_status()

                            video_path = os.path.join(output_base_dir, f"VIDEO_{int(time.time())}.mp4")
                            with open(video_path, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    f.write(chunk)

                            local_path = video_path
                            print(f"DEBUG: Downloaded video to: {local_path}")

                            # Validate and repair video if needed
                            print(f"DEBUG: Validating downloaded video: {local_path}")
                            validated_path = ensure_video_playable(local_path)
                            if validated_path != local_path:
                                print(f"DEBUG: Video was repaired, using: {validated_path}")
                                local_path = validated_path
                            elif validated_path is None:
                                raise Exception(f"Downloaded video is corrupted and could not be repaired: {local_path}")
                            else:
                                print(f"DEBUG: Video validation successful: {local_path}")

                            if drive:
                                drive_link = drive.upload_file(local_path)
                                print(f"DEBUG: Drive link: {drive_link}")
                                db_post.media_url = drive_link
                                db_post.media_filename = os.path.basename(local_path)
                            else:
                                db_post.media_url = local_path
                                db_post.media_filename = os.path.basename(local_path)
                        except Exception as download_err:
                            print(f"ERROR: Failed to download video: {download_err}")
                            raise Exception(f"Failed to download generated video: {download_err}")
                    else:
                        # Direct link (PPT)
                        drive_link = result
                        db_post.media_url = drive_link
                        print(f"DEBUG: Direct link result: {drive_link}")
                elif drive:
                    # Local file - upload to Drive if available
                    print(f"DEBUG: Uploading {result} to Drive")
                    drive_link = drive.upload_file(result)
                    print(f"DEBUG: Drive link: {drive_link}")
                    db_post.media_url = drive_link
                    db_post.media_filename = os.path.basename(local_path)
                else:
                    # No Drive - store local path
                    print(f"DEBUG: Drive not available, storing local path: {result}")
                    db_post.media_url = result
                    db_post.media_filename = os.path.basename(local_path) if result else None

                # Update post with generated content
                db.commit()
                print(f"DEBUG: Post updated with media: {db_post.media_url}")

                # Now post to platforms
                print(f"DEBUG: Publishing to platforms: {platforms_list}")
                results = []

                for platform in platforms_list:
                    try:
                        cred = credentials[platform]
                        print(f"DEBUG: Publishing to {platform}")

                        if platform == "instagram":
                            from platforms.instagram import InstagramAutomation
                            instagram = InstagramAutomation(
                                cred.credential_data.get("username"),
                                cred.credential_data.get("password")
                            )

                            if not instagram.login():
                                raise Exception("Instagram login failed")

                            if content_type.upper() == "IMAGE" and local_path and os.path.exists(local_path):
                                result_api = instagram.post_photo(local_path, post_caption)
                            elif content_type.upper() == "VIDEO" and local_path and os.path.exists(local_path):
                                result_api = instagram.post_reels(local_path, post_caption)
                            else:
                                raise Exception(f"Unsupported content for Instagram: {content_type}")

                            if result_api and result_api.get("success"):
                                results.append({
                                    "platform": platform,
                                    "status": "posted",
                                    "post_url": f"https://instagram.com/p/{result_api.get('code', db_post.id)}",
                                    "post_id": result_api.get("media_id", f"{platform}_{db_post.id}")
                                })
                            else:
                                raise Exception(result_api.get("error", "Instagram posting failed") if result_api else "Posting failed")

                        elif platform == "facebook":
                            from platforms.facebook import FacebookAutomation
                            facebook = FacebookAutomation(
                                cred.credential_data.get("access_token"),
                                cred.credential_data.get("page_id")
                            )

                            if content_type.upper() == "IMAGE" and local_path and os.path.exists(local_path):
                                result_api = facebook.post_photo(local_path, post_caption)
                            elif content_type.upper() == "VIDEO" and local_path and os.path.exists(local_path):
                                result_api = facebook.post_video(local_path, post_caption)
                            elif content_type.upper() == "TEXT":
                                result_api = facebook.post_text(post_caption)
                            else:
                                raise Exception(f"Unsupported content for Facebook: {content_type}")

                            if result_api and result_api.get("success"):
                                results.append({
                                    "platform": platform,
                                    "status": "posted",
                                    "post_url": f"https://facebook.com/{result_api.get('post_id', db_post.id)}",
                                    "post_id": result_api.get("post_id", f"{platform}_{db_post.id}")
                                })
                            else:
                                raise Exception("Facebook posting failed")

                        elif platform == "linkedin":
                            from platforms.linkedin import LinkedInAutomation
                            linkedin = LinkedInAutomation(
                                cred.credential_data.get("access_token"),
                                cred.credential_data.get("person_urn")
                            )

                            if content_type.upper() == "IMAGE" and local_path and os.path.exists(local_path):
                                result_api = linkedin.post_with_image(post_caption, local_path)
                            elif content_type.upper() == "VIDEO" and local_path and os.path.exists(local_path):
                                result_api = linkedin.post_with_video(post_caption, local_path)
                            elif content_type.upper() == "TEXT":
                                result_api = linkedin.post_text(post_caption)
                            else:
                                raise Exception(f"Unsupported content for LinkedIn: {content_type}")

                            if result_api and result_api.get("success"):
                                results.append({
                                    "platform": platform,
                                    "status": "posted",
                                    "post_url": f"https://linkedin.com/feed/update/{result_api.get('post_id', db_post.id)}",
                                    "post_id": result_api.get("post_id", f"{platform}_{db_post.id}")
                                })
                            else:
                                raise Exception("LinkedIn posting failed")

                        elif platform == "youtube":
                            from platforms.youtube import YouTubeAutomation
                            youtube = YouTubeAutomation(
                                cred.credential_data.get("client_secrets_file"),
                                cred.credential_data.get("credentials_file")
                            )

                            if not youtube.authenticate():
                                raise Exception("YouTube authentication failed")

                            if content_type.upper() == "VIDEO" and local_path and os.path.exists(local_path):
                                # Extract title and description from post content
                                title = f"AI Generated Video - {prompt[:50]}{'...' if len(prompt) > 50 else ''}"
                                description = post_caption

                                # Extract tags from Gemini metadata if available
                                tags = []
                                # You could enhance this to extract tags from Gemini response

                                result_api = youtube.upload_video(
                                    local_path,
                                    title,
                                    description,
                                    tags,
                                    category_id='22'  # People & Blogs
                                )

                                if result_api and result_api.get("success"):
                                    results.append({
                                        "platform": platform,
                                        "status": "posted",
                                        "post_url": f"https://youtube.com/watch?v={result_api.get('video_id', '')}",
                                        "post_id": result_api.get("video_id", f"{platform}_{db_post.id}")
                                    })
                                else:
                                    raise Exception("YouTube upload failed")
                            else:
                                raise Exception("YouTube only supports video content")

                        else:
                            raise Exception(f"Platform {platform} not implemented for Gemini posts")

                        # Update platform status in database
                        platform_entry = db.query(PostPlatform).filter(
                            PostPlatform.post_id == db_post.id,
                            PostPlatform.platform == platform
                        ).first()

                        if platform_entry:
                            platform_entry.status = "posted"
                            platform_entry.post_url = results[-1]["post_url"]
                            platform_entry.platform_post_id = results[-1]["post_id"]
                            platform_entry.posted_at = datetime.utcnow()
                            print(f"DEBUG: Updated platform status for {platform}")

                    except Exception as e:
                        print(f"ERROR: Failed to post to {platform}: {e}")
                        results.append({
                            "platform": platform,
                            "status": "failed",
                            "error_message": str(e)
                        })

                # Update post status
                successful_posts = [r for r in results if r["status"] == "posted"]
                if successful_posts:
                    db_post.status = "posted" if len(successful_posts) == len(platforms_list) else "partially_posted"
                else:
                    db_post.status = "failed"

                db.commit()
                print(f"DEBUG: Final post status: {db_post.status}")

                return {
                    "post_id": db_post.id,
                    "gemini_prompt": prompt,
                    "content_type": content_type,
                    "generated_content": drive_link or local_path,
                    "caption": post_caption,
                    "platforms": platforms_list,
                    "scheduled_at": scheduled_datetime.isoformat() if scheduled_datetime else None,
                    "posted_now": True,
                    "results": results
                }

            except Exception as e:
                print(f"ERROR: Failed during content generation: {e}")
                import traceback
                print(f"TRACEBACK: {traceback.format_exc()}")
                db_post.status = "failed"
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Content generation failed: {str(e)}"
                )
        else:
            # Scheduled for later - schedule with background scheduler
            print("DEBUG: Scheduling for later")
            scheduler = get_scheduler()
            scheduler.schedule_post(db_post.id, scheduled_datetime)

            return {
                "post_id": db_post.id,
                "gemini_prompt": prompt,
                "content_type": content_type,
                "caption": post_caption,
                "platforms": platforms_list,
                "scheduled_at": scheduled_datetime.isoformat(),
                "posted_now": False,
                "status": "scheduled",
                "message": f"Post scheduled for {scheduled_datetime.isoformat()}"
            }

    except Exception as e:
        print(f"DEBUG: Exception in generate_and_post_with_gemini: {type(e).__name__}: {e}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        raise

@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a post"""
    post = db.query(Post).filter(
        Post.id == post_id,
        Post.user_id == current_user.id
    ).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # Delete associated file if exists
    if post.media_url and os.path.exists(post.media_url):
        os.remove(post.media_url)

    db.delete(post)
    db.commit()

    return {"message": "Post deleted successfully"}