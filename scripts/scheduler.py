#!/usr/bin/env python3
"""
Background Scheduler for Social Media Automation
Handles scheduled posts and automated publishing
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.memory import MemoryJobStore

from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Post, PostPlatform, SocialMediaCredential
from flows.gemini_flow import run_gemini_task
from flows.drive_flow import DriveManager
from playwright.sync_api import sync_playwright

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Gemini components
GEMINI_ROOT = os.path.dirname(__file__)
if GEMINI_ROOT not in sys.path:
    sys.path.insert(0, GEMINI_ROOT)

try:
    from flows.gemini_flow import run_gemini_task
    from flows.drive_flow import DriveManager
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("Gemini components not available")

class SocialMediaScheduler:
    """Background scheduler for processing scheduled social media posts"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            jobstores={
                'default': MemoryJobStore()
            },
            job_defaults={
                'coalesce': True,
                'max_instances': 1,
                'misfire_grace_time': 30
            },
            timezone='UTC'
        )

    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Social Media Scheduler started")

            # Schedule the periodic check for due posts
            self.scheduler.add_job(
                self._process_due_posts,
                'interval',
                seconds=60,  # Check every minute
                id='process_due_posts',
                name='Process Due Posts',
                replace_existing=True
            )

    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Social Media Scheduler stopped")

    def schedule_post(self, post_id: int, scheduled_time: datetime):
        """Schedule a post for publishing at a specific time"""
        try:
            self.scheduler.add_job(
                self._publish_scheduled_post,
                trigger=DateTrigger(run_date=scheduled_time),
                args=[post_id],
                id=f'post_{post_id}',
                name=f'Publish Post {post_id}',
                replace_existing=True
            )
            logger.info(f"Scheduled post {post_id} for {scheduled_time}")
        except Exception as e:
            logger.error(f"Failed to schedule post {post_id}: {e}")

    def _process_due_posts(self):
        """Check for posts that are due to be published"""
        try:
            # Get database session
            db = next(get_db())

            # Find posts that are scheduled and due (within the last 5 minutes to account for timing)
            due_time = datetime.utcnow() - timedelta(minutes=5)
            due_posts = db.query(Post).filter(
                Post.status == "scheduled",
                Post.scheduled_at <= datetime.utcnow(),
                Post.scheduled_at >= due_time
            ).all()

            for post in due_posts:
                logger.info(f"Processing due post: {post.id}")
                self._publish_scheduled_post(post.id)

            db.close()

        except Exception as e:
            logger.error(f"Error processing due posts: {e}")

    def _publish_scheduled_post(self, post_id: int):
        """Publish a scheduled post"""
        db = None
        try:
            # Get database session
            db = next(get_db())

            # Get the post
            post = db.query(Post).filter(Post.id == post_id).first()
            if not post:
                logger.error(f"Post {post_id} not found")
                return

            if post.status != "scheduled":
                logger.warning(f"Post {post_id} is not in scheduled status")
                return

            logger.info(f"Publishing scheduled post {post_id}")

            # Update post status to processing
            post.status = "processing"
            db.commit()

            # Get platforms for this post
            platform_entries = db.query(PostPlatform).filter(
                PostPlatform.post_id == post_id
            ).all()

            platforms = [p.platform for p in platform_entries]

            # Get user credentials
            credentials = self._get_user_credentials(post.user_id, platforms, db)
            missing_platforms = [p for p in platforms if p not in credentials]

            if missing_platforms:
                logger.error(f"Missing credentials for platforms: {missing_platforms}")
                post.status = "failed"
                db.commit()
                return

            # Generate content with Gemini if not already generated
            if not post.media_url:
                logger.info(f"Generating content for post {post_id}")
                content_url = self._generate_content_for_post(post, db)
                if not content_url:
                    post.status = "failed"
                    db.commit()
                    return
            else:
                content_url = post.media_url

            # Publish to platforms
            results = self._publish_to_platforms(post, platforms, credentials, content_url, db)

            # Update post and platform status
            successful_posts = [r for r in results if r["status"] == "posted"]
            if successful_posts:
                post.status = "posted" if len(successful_posts) == len(platforms) else "partially_posted"
            else:
                post.status = "failed"

            post.posted_at = datetime.utcnow()
            db.commit()

            logger.info(f"Post {post_id} publishing completed. Status: {post.status}")

        except Exception as e:
            logger.error(f"Error publishing scheduled post {post_id}: {e}")
            if db:
                try:
                    post = db.query(Post).filter(Post.id == post_id).first()
                    if post:
                        post.status = "failed"
                        db.commit()
                except:
                    pass
        finally:
            if db:
                db.close()

    def _generate_content_for_post(self, post: Post, db: Session) -> str:
        """Generate content for a scheduled post using Gemini"""
        try:
            # Setup Gemini environment
            from playwright.sync_api import sync_playwright

            # Initialize Drive manager
            drive_credentials = os.path.join(GEMINI_ROOT, "gemini_automation", "gemini_automation", "auth", "credentials.json")
            if not os.path.exists(drive_credentials):
                logger.error("Google Drive credentials not configured")
                return None

            drive = DriveManager(drive_credentials)

            # Create output directory
            output_base_dir = os.path.join(GEMINI_ROOT, "gemini_automation", "gemini_automation", "out")
            os.makedirs(output_base_dir, exist_ok=True)

            # Get platforms for content generation
            platform_entries = db.query(PostPlatform).filter(
                PostPlatform.post_id == post.id
            ).all()
            platforms = [p.platform for p in platform_entries]

            # Generate content with Gemini
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(
                    os.path.join(GEMINI_ROOT, "gemini_automation", "gemini_automation", "auth", "user_data"),
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                page = context.new_page()

                try:
                    logger.info(f"Generating {post.content_type} content for post {post.id}")
                    result = run_gemini_task(page, post.gemini_prompt, post.content_type.upper(), output_base_dir, platforms)

                    if not result:
                        logger.error("Gemini returned empty result")
                        return None

                    # Handle result
                    if result and str(result).startswith("http"):
                        # Direct link (PPT)
                        content_url = result
                        post.media_url = content_url
                    else:
                        # Local file - upload to Drive
                        logger.info(f"Uploading generated content to Drive")
                        content_url = drive.upload_file(result)
                        post.media_url = content_url
                        post.media_filename = os.path.basename(result)

                    db.commit()
                    return content_url

                finally:
                    context.close()

        except Exception as e:
            logger.error(f"Error generating content for post {post.id}: {e}")
            return None

    def _publish_to_platforms(self, post: Post, platforms: List[str], credentials: Dict, content_url: str, db: Session) -> List[Dict]:
        """Publish content to specified platforms"""
        results = []

        for platform in platforms:
            try:
                cred = credentials[platform]
                logger.info(f"Publishing post {post.id} to {platform}")

                if platform == "instagram":
                    from platforms.instagram import InstagramAutomation
                    instagram = InstagramAutomation(
                        cred.credential_data.get("username"),
                        cred.credential_data.get("password")
                    )

                    if not instagram.login():
                        raise Exception("Instagram login failed")

                    if post.content_type.lower() == "image" and content_url:
                        # Download file from Drive if needed
                        local_path = self._download_from_drive(content_url) if content_url.startswith("http") else content_url
                        if local_path and os.path.exists(local_path):
                            result_api = instagram.post_photo(local_path, post.content)
                        else:
                            raise Exception("Could not access image file")
                    elif post.content_type.lower() == "video" and content_url:
                        local_path = self._download_from_drive(content_url) if content_url.startswith("http") else content_url
                        if local_path and os.path.exists(local_path):
                            result_api = instagram.post_reels(local_path, post.content)
                        else:
                            raise Exception("Could not access video file")
                    else:
                        raise Exception(f"Unsupported content for Instagram: {post.content_type}")

                    if result_api and result_api.get("success"):
                        results.append({
                            "platform": platform,
                            "status": "posted",
                            "post_url": f"https://instagram.com/p/{result_api.get('code', post.id)}",
                            "post_id": result_api.get("media_id", f"{platform}_{post.id}")
                        })
                    else:
                        raise Exception(result_api.get("error", "Instagram posting failed") if result_api else "Posting failed")

                # Add other platforms here as needed...

                else:
                    raise Exception(f"Platform {platform} not implemented for scheduled posts")

                # Update platform status
                platform_entry = db.query(PostPlatform).filter(
                    PostPlatform.post_id == post.id,
                    PostPlatform.platform == platform
                ).first()

                if platform_entry:
                    platform_entry.status = "posted"
                    platform_entry.post_url = results[-1]["post_url"]
                    platform_entry.platform_post_id = results[-1]["post_id"]
                    platform_entry.posted_at = datetime.utcnow()

            except Exception as e:
                logger.error(f"Failed to post to {platform}: {e}")
                results.append({
                    "platform": platform,
                    "status": "failed",
                    "error_message": str(e)
                })

        return results

    def _get_user_credentials(self, user_id: int, platforms: List[str], db: Session) -> Dict:
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

    def _download_from_drive(self, drive_url: str) -> str:
        """Download file from Google Drive URL"""
        try:
            # This is a placeholder - implement actual Drive download logic
            logger.warning("Drive download not implemented yet")
            return None
        except Exception as e:
            logger.error(f"Error downloading from Drive: {e}")
            return None

# Global scheduler instance
scheduler = SocialMediaScheduler()

def get_scheduler() -> SocialMediaScheduler:
    """Get the global scheduler instance"""
    return scheduler

def start_scheduler():
    """Start the background scheduler"""
    scheduler.start()

def stop_scheduler():
    """Stop the background scheduler"""
    scheduler.stop()