"""
Unified Scheduler for Social Media Posts
Handles scheduling posts across all platforms
"""

import os
import json
import logging
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import yaml

from platforms.instagram import InstagramAutomation
from platforms.facebook import FacebookAutomation
from platforms.youtube import YouTubeAutomation
from platforms.linkedin import LinkedInAutomation

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SocialMediaScheduler:
    """Unified scheduler for all social media platforms"""
    
    def __init__(self, config_file: str = "config.yaml"):
        """
        Initialize scheduler with configuration
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.platforms = {}
        self.scheduled_posts_file = "scheduled_posts.json"
        self.scheduled_posts = self._load_scheduled_posts()
        
        # Initialize platforms
        self._initialize_platforms()
    
    def _load_config(self) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {self.config_file}")
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return {}
    
    def _load_scheduled_posts(self) -> List[Dict]:
        """Load scheduled posts from JSON file"""
        if os.path.exists(self.scheduled_posts_file):
            try:
                with open(self.scheduled_posts_file, 'r') as f:
                    posts = json.load(f)
                logger.info(f"Loaded {len(posts)} scheduled posts")
                return posts
            except Exception as e:
                logger.error(f"Error loading scheduled posts: {e}")
                return []
        return []
    
    def _save_scheduled_posts(self):
        """Save scheduled posts to JSON file"""
        try:
            with open(self.scheduled_posts_file, 'w') as f:
                json.dump(self.scheduled_posts, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving scheduled posts: {e}")
    
    def _initialize_platforms(self):
        """Initialize all enabled platforms"""
        # Instagram
        if self.config.get('instagram', {}).get('enabled', False):
            try:
                username = self.config['instagram'].get('username', '')
                password = self.config['instagram'].get('password', '')
                if username and password:
                    self.platforms['instagram'] = InstagramAutomation(username, password)
                    if self.platforms['instagram'].login():
                        logger.info("Instagram initialized successfully")
                    else:
                        logger.warning("Instagram login failed")
                else:
                    logger.warning("Instagram credentials not provided")
            except Exception as e:
                logger.error(f"Error initializing Instagram: {e}")
        
        # Facebook
        if self.config.get('facebook', {}).get('enabled', False):
            try:
                access_token = self.config['facebook'].get('access_token', '')
                page_id = self.config['facebook'].get('page_id', '')
                if access_token and page_id:
                    self.platforms['facebook'] = FacebookAutomation(access_token, page_id)
                    if self.platforms['facebook'].validate_credentials():
                        logger.info("Facebook initialized successfully")
                    else:
                        logger.warning("Facebook credentials invalid")
                else:
                    logger.warning("Facebook credentials not provided")
            except Exception as e:
                logger.error(f"Error initializing Facebook: {e}")
        
        # YouTube
        if self.config.get('youtube', {}).get('enabled', False):
            try:
                client_secrets = self.config['youtube'].get('client_secrets_file', 'client_secrets.json')
                credentials_file = self.config['youtube'].get('credentials_file', 'youtube_credentials.json')
                if os.path.exists(client_secrets):
                    self.platforms['youtube'] = YouTubeAutomation(client_secrets, credentials_file)
                    if self.platforms['youtube'].authenticate():
                        logger.info("YouTube initialized successfully")
                    else:
                        logger.warning("YouTube authentication failed")
                else:
                    logger.warning(f"YouTube client secrets file not found: {client_secrets}")
            except Exception as e:
                logger.error(f"Error initializing YouTube: {e}")
        
        # LinkedIn
        if self.config.get('linkedin', {}).get('enabled', False):
            try:
                access_token = self.config['linkedin'].get('access_token', '')
                person_urn = self.config['linkedin'].get('person_urn', '')
                if access_token and person_urn:
                    self.platforms['linkedin'] = LinkedInAutomation(access_token, person_urn)
                    if self.platforms['linkedin'].validate_credentials():
                        logger.info("LinkedIn initialized successfully")
                    else:
                        logger.warning("LinkedIn credentials invalid")
                else:
                    logger.warning("LinkedIn credentials not provided")
            except Exception as e:
                logger.error(f"Error initializing LinkedIn: {e}")
    
    def schedule_post(self, platform: str, post_type: str, content: Dict, scheduled_time: str) -> bool:
        """
        Schedule a post for a specific platform
        
        Args:
            platform: Platform name (instagram, facebook, youtube, linkedin)
            post_type: Type of post (photo, text, video, etc.)
            content: Post content dictionary
            scheduled_time: ISO format datetime string
            
        Returns:
            bool: True if scheduled successfully
        """
        if platform not in self.platforms:
            logger.error(f"Platform {platform} not initialized or not available")
            return False
        
        post_data = {
            'id': f"{platform}_{int(time.time())}",
            'platform': platform,
            'post_type': post_type,
            'content': content,
            'scheduled_time': scheduled_time,
            'status': 'scheduled',
            'created_at': datetime.now().isoformat()
        }
        
        self.scheduled_posts.append(post_data)
        self._save_scheduled_posts()
        logger.info(f"Scheduled {post_type} post for {platform} at {scheduled_time}")
        return True
    
    def _execute_post(self, post: Dict) -> bool:
        """
        Execute a scheduled post
        
        Args:
            post: Post dictionary
            
        Returns:
            bool: True if posted successfully
        """
        platform_name = post['platform']
        post_type = post['post_type']
        content = post['content']
        
        if platform_name not in self.platforms:
            logger.error(f"Platform {platform_name} not available")
            return False
        
        platform = self.platforms[platform_name]
        result = None
        
        try:
            if platform_name == 'instagram':
                if post_type == 'photo':
                    result = platform.post_photo(
                        content.get('image_path', ''),
                        content.get('caption', '')
                    )
                elif post_type == 'carousel':
                    result = platform.post_carousel(
                        content.get('image_paths', []),
                        content.get('caption', '')
                    )
            
            elif platform_name == 'facebook':
                if post_type == 'text':
                    result = platform.post_text(
                        content.get('message', ''),
                        post.get('scheduled_time')
                    )
                elif post_type == 'photo':
                    result = platform.post_photo(
                        content.get('image_path', ''),
                        content.get('message', ''),
                        post.get('scheduled_time')
                    )
            
            elif platform_name == 'youtube':
                if post_type == 'video':
                    result = platform.upload_video(
                        content.get('video_path', ''),
                        content.get('title', ''),
                        content.get('description', ''),
                        content.get('tags', []),
                        content.get('category_id', '22'),
                        content.get('privacy_status', 'private'),
                        post.get('scheduled_time')
                    )
            
            elif platform_name == 'linkedin':
                if post_type == 'text':
                    result = platform.post_text(content.get('text', ''))
                elif post_type == 'image':
                    result = platform.post_with_image(
                        content.get('text', ''),
                        content.get('image_path', '')
                    )
            
            if result and result.get('success'):
                post['status'] = 'posted'
                post['posted_at'] = datetime.now().isoformat()
                post['result'] = result
                logger.info(f"Successfully posted to {platform_name}")
                return True
            else:
                post['status'] = 'failed'
                post['error'] = result.get('error', 'Unknown error') if result else 'No result'
                logger.error(f"Failed to post to {platform_name}: {post.get('error')}")
                return False
                
        except Exception as e:
            post['status'] = 'failed'
            post['error'] = str(e)
            logger.error(f"Error executing post to {platform_name}: {e}")
            return False
        finally:
            self._save_scheduled_posts()
    
    def check_and_execute_posts(self):
        """Check scheduled posts and execute if time has come"""
        from datetime import timezone
        now = datetime.now(timezone.utc)
        posts_to_execute = []
        
        for post in self.scheduled_posts:
            if post['status'] != 'scheduled':
                continue
            
            try:
                # Parse scheduled time - handle both with and without timezone
                scheduled_time_str = post['scheduled_time']
                
                # Try to parse with timezone first
                if 'Z' in scheduled_time_str or '+' in scheduled_time_str:
                    scheduled_time = datetime.fromisoformat(scheduled_time_str.replace('Z', '+00:00'))
                else:
                    # No timezone info - treat as local time (naive datetime)
                    scheduled_time = datetime.fromisoformat(scheduled_time_str)
                
                # Compare times - if scheduled_time is naive, compare with local now
                # If scheduled_time is timezone-aware, compare with UTC now
                if scheduled_time.tzinfo is None:
                    # Naive datetime - compare with local time
                    compare_now = datetime.now()
                    time_diff = (compare_now - scheduled_time).total_seconds()
                    should_execute = scheduled_time <= compare_now and time_diff < 600  # Within 10 minutes
                else:
                    # Timezone-aware - compare with UTC
                    compare_now = datetime.now(timezone.utc)
                    time_diff = (compare_now - scheduled_time).total_seconds()
                    should_execute = scheduled_time <= compare_now and time_diff < 600  # Within 10 minutes
                
                if should_execute:
                    posts_to_execute.append(post)
                    logger.info(f"Found post to execute: {post['id']} (scheduled: {scheduled_time_str}, {time_diff:.0f}s ago)")
                elif scheduled_time.tzinfo is None and scheduled_time > datetime.now():
                    # Future post (local time)
                    time_until = (scheduled_time - datetime.now()).total_seconds()
                    if time_until < 120:  # Less than 2 minutes away
                        logger.debug(f"Post {post['id']} scheduled in {time_until:.0f} seconds (local time)")
                elif scheduled_time.tzinfo and scheduled_time > datetime.now(timezone.utc):
                    # Future post (UTC)
                    time_until = (scheduled_time - datetime.now(timezone.utc)).total_seconds()
                    if time_until < 120:  # Less than 2 minutes away
                        logger.debug(f"Post {post['id']} scheduled in {time_until:.0f} seconds (UTC)")
            except Exception as e:
                logger.error(f"Error parsing scheduled time for post {post.get('id')}: {e}")
        
        for post in posts_to_execute:
            logger.info(f"Executing scheduled post: {post['id']}")
            self._execute_post(post)
    
    def run(self):
        """Run the scheduler"""
        check_interval = self.config.get('scheduler', {}).get('check_interval', 60)
        
        logger.info("Starting social media scheduler...")
        logger.info(f"Checking for scheduled posts every {check_interval} seconds")
        
        # Schedule the check function
        schedule.every(check_interval).seconds.do(self.check_and_execute_posts)
        
        # Run immediately to check for any overdue posts
        self.check_and_execute_posts()
        
        # Main loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")

