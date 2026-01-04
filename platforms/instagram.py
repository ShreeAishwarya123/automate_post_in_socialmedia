"""
Instagram Post Automation Module
Handles posting images, captions, and scheduling for Instagram
"""

import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InstagramAutomation:
    """Instagram automation class for posting and scheduling"""
    
    def __init__(self, username: str, password: str):
        """
        Initialize Instagram client
        
        Args:
            username: Instagram username
            password: Instagram password
        """
        self.username = username
        self.password = password
        self.client = Client()
        self.authenticated = False
        
    def login(self) -> bool:
        """
        Login to Instagram account
        
        Returns:
            bool: True if login successful, False otherwise
        """
        try:
            logger.info(f"Attempting to login to Instagram as {self.username}")
            
            # Try to load session if exists
            session_file = f"instagram_session_{self.username}.json"
            if os.path.exists(session_file):
                try:
                    self.client.load_settings(session_file)
                    self.client.login(self.username, self.password)
                    logger.info("Logged in using saved session")
                    self.authenticated = True
                    return True
                except Exception as e:
                    logger.warning(f"Failed to load session: {e}. Creating new session.")
                    os.remove(session_file)
            
            # New login
            self.client.login(self.username, self.password)
            self.client.dump_settings(session_file)
            logger.info("Successfully logged in to Instagram")
            self.authenticated = True
            return True
            
        except ChallengeRequired:
            logger.error("Instagram requires challenge verification. Please verify manually.")
            return False
        except LoginRequired:
            logger.error("Login failed. Please check your credentials.")
            return False
        except Exception as e:
            logger.error(f"Error during Instagram login: {e}")
            return False
    
    def post_photo(self, image_path: str, caption: str = "") -> Optional[Dict[str, Any]]:
        """
        Post a photo to Instagram
        
        Args:
            image_path: Path to the image file
            caption: Caption for the post
            
        Returns:
            dict: Post information if successful, None otherwise
        """
        if not self.authenticated:
            logger.error("Not authenticated. Please login first.")
            return None
        
        try:
            # Validate image
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None
            
            # Validate and optimize image
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Instagram requires specific dimensions
            width, height = img.size
            if width < 320 or height < 320:
                logger.error("Image dimensions too small. Minimum 320x320 required.")
                return None
            
            logger.info(f"Uploading photo to Instagram: {image_path}")
            media = self.client.photo_upload(
                path=image_path,
                caption=caption
            )
            
            logger.info(f"Successfully posted to Instagram. Media ID: {media.id}")
            return {
                'success': True,
                'media_id': media.id,
                'code': media.code,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error posting photo to Instagram: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def post_carousel(self, image_paths: list, caption: str = "") -> Optional[Dict[str, Any]]:
        """
        Post a carousel (multiple images) to Instagram
        
        Args:
            image_paths: List of paths to image files
            caption: Caption for the post
            
        Returns:
            dict: Post information if successful, None otherwise
        """
        if not self.authenticated:
            logger.error("Not authenticated. Please login first.")
            return None
        
        try:
            if len(image_paths) < 2 or len(image_paths) > 10:
                logger.error("Carousel must contain 2-10 images")
                return None
            
            # Validate all images
            for img_path in image_paths:
                if not os.path.exists(img_path):
                    logger.error(f"Image file not found: {img_path}")
                    return None
            
            logger.info(f"Uploading carousel to Instagram with {len(image_paths)} images")
            media = self.client.album_upload(
                paths=image_paths,
                caption=caption
            )
            
            logger.info(f"Successfully posted carousel to Instagram. Media ID: {media.id}")
            return {
                'success': True,
                'media_id': media.id,
                'code': media.code,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error posting carousel to Instagram: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_credentials(self) -> bool:
        """
        Validate Instagram credentials
        
        Returns:
            bool: True if credentials are valid
        """
        return self.login()


