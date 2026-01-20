"""
YouTube Post Automation Module
Handles uploading videos and scheduling for YouTube
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']


class YouTubeAutomation:
    """YouTube automation class for uploading videos and scheduling"""
    
    def __init__(self, client_secrets_file: str, credentials_file: str = "youtube_credentials.json"):
        """
        Initialize YouTube client
        
        Args:
            client_secrets_file: Path to OAuth2 client secrets JSON file
            credentials_file: Path to store credentials after authentication
        """
        self.client_secrets_file = client_secrets_file
        self.credentials_file = credentials_file
        self.youtube = None
        self.authenticated = False
        
    def authenticate(self) -> bool:
        """
        Authenticate with YouTube API

        Returns:
            bool: True if authentication successful
        """
        try:
            print(f"YouTube Auth: Checking file: {self.credentials_file}", flush=True)
            creds = None

            # Load existing credentials
            if os.path.exists(self.credentials_file):
                print(f"YouTube Auth: File exists, loading...", flush=True)
                with open(self.credentials_file, 'rb') as token:
                    creds = pickle.load(token)
                print(f"YouTube Auth: Credentials loaded successfully", flush=True)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    logger.info("Refreshing YouTube credentials")
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.client_secrets_file):
                        logger.error(f"Client secrets file not found: {self.client_secrets_file}")
                        logger.error("Please download it from Google Cloud Console")
                        return False
                    
                    logger.info("Starting YouTube OAuth flow")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.client_secrets_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(self.credentials_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            # Build YouTube service
            self.youtube = build('youtube', 'v3', credentials=creds)
            self.authenticated = True
            logger.info("Successfully authenticated with YouTube")
            return True
            
        except Exception as e:
            logger.error(f"Error authenticating with YouTube: {e}")
            return False
    
    def upload_video(self, video_path: str, title: str, description: str = "",
                    tags: Optional[list] = None, category_id: str = "22",
                    privacy_status: str = "private", scheduled_time: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Upload video to YouTube
        
        Args:
            video_path: Path to the video file
            title: Video title
            description: Video description
            tags: List of tags
            category_id: YouTube category ID (default: 22 for People & Blogs)
            privacy_status: "private", "unlisted", or "public"
            scheduled_time: ISO format datetime string for scheduling (optional)
            
        Returns:
            dict: Video information if successful, None otherwise
        """
        if not self.authenticated:
            logger.error("Not authenticated. Please authenticate first.")
            return None
        
        try:
            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return None
            
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status
                }
            }
            
            # Add schedule if provided
            if scheduled_time:
                from datetime import datetime as dt
                dt_obj = dt.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                # YouTube requires RFC 3339 format
                schedule_time = dt_obj.strftime('%Y-%m-%dT%H:%M:%S.000Z')
                body['status']['publishAt'] = schedule_time
                body['status']['privacyStatus'] = 'private'  # Must be private when scheduled
            
            # Create media upload
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            
            logger.info(f"Uploading video to YouTube: {video_path}")
            insert_request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            # Execute upload
            response = self._resumable_upload(insert_request)
            
            if response:
                logger.info(f"Successfully uploaded video to YouTube. Video ID: {response['id']}")
                return {
                    'success': True,
                    'video_id': response['id'],
                    'title': response['snippet']['title'],
                    'url': f"https://www.youtube.com/watch?v={response['id']}",
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error("Failed to upload video to YouTube")
                return {
                    'success': False,
                    'error': 'Upload failed'
                }
                
        except Exception as e:
            logger.error(f"Error uploading video to YouTube: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _resumable_upload(self, insert_request) -> Optional[Dict]:
        """
        Execute resumable upload for large files
        
        Args:
            insert_request: YouTube API insert request
            
        Returns:
            dict: Response from API or None if error
        """
        response = None
        error = None
        retry = 0
        
        while response is None:
            try:
                status, response = insert_request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        return response
                    else:
                        raise Exception(f"Upload failed: {response}")
            except Exception as e:
                if error is None:
                    error = e
                retry += 1
                if retry > 3:
                    logger.error(f"Max retries exceeded. Error: {error}")
                    return None
                logger.warning(f"Retry {retry} after error: {e}")
        
        return None
    
    def validate_credentials(self) -> bool:
        """
        Validate YouTube credentials
        
        Returns:
            bool: True if credentials are valid
        """
        if not self.authenticated:
            return self.authenticate()
        
        try:
            # Test API access - try to get channel info
            # Note: youtube.upload scope might not allow reading channel info
            # So we'll just check if the service is initialized
            if self.youtube is not None:
                logger.info("YouTube credentials valid (service initialized)")
                return True
            else:
                logger.error("YouTube service not initialized")
                return False
                
        except Exception as e:
            logger.warning(f"Could not fully validate YouTube credentials: {e}")
            # If service is initialized, consider it valid
            if self.youtube is not None:
                logger.info("YouTube service initialized - credentials likely valid")
                return True
            return False

