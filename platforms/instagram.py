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
    
    def post_video(self, video_path: str, caption: str = "") -> Optional[Dict[str, Any]]:
        """
        Post a video to Instagram (regular video post)

        Args:
            video_path: Path to the video file
            caption: Caption for the video

        Returns:
            dict: Post information if successful, None otherwise
        """
        if not self.authenticated:
            logger.error("Not authenticated. Please login first.")
            return None

        try:
            # Validate video file
            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return None

            # Check file size (Instagram limit is 4GB for regular videos)
            file_size = os.path.getsize(video_path)
            if file_size > 4 * 1024 * 1024 * 1024:  # 4GB
                logger.error("Video file too large. Maximum size is 4GB.")
                return None

            logger.info(f"Uploading video to Instagram: {video_path}")
            media = self.client.video_upload(
                path=video_path,
                caption=caption
            )

            logger.info(f"Successfully posted video to Instagram. Media ID: {media.id}")
            return {
                'success': True,
                'media_id': media.id,
                'code': media.code,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error posting video to Instagram: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def post_reels(self, video_path: str, caption: str = "") -> Optional[Dict[str, Any]]:
        """
        Post a video to Instagram Reels

        Args:
            video_path: Path to the video file
            caption: Caption for the Reels video

        Returns:
            dict: Post information if successful, None otherwise
        """
        if not self.authenticated:
            logger.error("Not authenticated. Please login first.")
            return None

        try:
            # Validate video file
            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return None

            # Check file size (Instagram Reels limit is 4GB)
            file_size = os.path.getsize(video_path)
            if file_size > 4 * 1024 * 1024 * 1024:  # 4GB
                logger.error("Video file too large. Maximum size is 4GB.")
                return None

            logger.info(f"Uploading Reels video to Instagram: {video_path}")

            # Try different methods that might be available in instagrapi
            try:
                # Try clip_upload for Reels with basic metadata
                media = self.client.clip_upload(
                    path=video_path,
                    caption=caption,
                    extra_data={
                        "clips_metadata": {
                            "original_sound_info": {
                                "ig_artist": {
                                    "profile_pic_id": "default",
                                    "username": self.username
                                },
                                "audio_filter_infos": []
                            }
                        }
                    }
                )
            except (AttributeError, Exception) as e:
                logger.warning(f"Reels upload failed: {e}, trying regular video upload")
                try:
                    # Try video_upload with extra parameters for Reels
                    media = self.client.video_upload(
                        path=video_path,
                        caption=caption,
                        extra_data={"reels": True}
                    )
                except Exception as e2:
                    logger.warning(f"Reels video upload also failed: {e2}, using regular video upload")
                    # Fallback to regular video upload
                    media = self.client.video_upload(
                        path=video_path,
                        caption=caption
                    )

            logger.info(f"Successfully posted Reels to Instagram. Media ID: {media.id}")
            return {
                'success': True,
                'media_id': media.id,
                'code': media.code,
                'timestamp': datetime.now().isoformat(),
                'type': 'reels'
            }

        except Exception as e:
            logger.error(f"Error posting Reels to Instagram: {e}")
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








