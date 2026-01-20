"""
Facebook Post Automation Module
Handles posting text, images, and scheduling for Facebook Pages
"""

import os
import logging
import requests
from datetime import datetime
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FacebookAutomation:
    """Facebook automation class for posting and scheduling"""
    
    def __init__(self, access_token: str, page_id: str):
        """
        Initialize Facebook client
        
        Args:
            access_token: Facebook User Access Token or Page Access Token
            page_id: Facebook Page ID
        """
        self.user_access_token = access_token  # Store original token
        self.access_token = access_token  # Will be updated to page token if needed
        self.page_id = page_id
        self.base_url = "https://graph.facebook.com/v18.0"
        self._page_token_fetched = False
        self._check_token_expiration()
        
    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make API request to Facebook Graph API
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            data: Request data
            
        Returns:
            dict: API response or None if error
        """
        url = f"{self.base_url}/{endpoint}"
        params = {"access_token": self.access_token}
        
        try:
            if method == "GET":
                response = requests.get(url, params=params)
            elif method == "POST":
                params.update(data or {})
                response = requests.post(url, params=params)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Facebook API request failed: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            return None
    
    def _check_token_expiration(self):
        """Check if token is expired or expiring soon, and warn user"""
        try:
            url = f"{self.base_url}/debug_token"
            params = {
                "input_token": self.user_access_token,
                "access_token": self.user_access_token
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                token_data = data.get('data', {})
                expires_at = token_data.get('expires_at', 0)
                
                if expires_at > 0:
                    from datetime import datetime
                    expires_datetime = datetime.fromtimestamp(expires_at)
                    time_until_expiry = expires_datetime - datetime.now()
                    days_until_expiry = time_until_expiry.total_seconds() / 86400
                    
                    if days_until_expiry < 0:
                        logger.warning("⚠️ Facebook token has EXPIRED!")
                        logger.warning("Run: python get_long_lived_facebook_token.py")
                    elif days_until_expiry < 7:
                        logger.warning(f"⚠️ Facebook token expires in {days_until_expiry:.1f} days")
                        logger.warning("Consider refreshing: python get_long_lived_facebook_token.py")
                    elif days_until_expiry < 30:
                        logger.info(f"ℹ️ Facebook token expires in {days_until_expiry:.1f} days")
        except:
            pass  # Don't fail if we can't check expiration
    
    def _ensure_page_token(self):
        """Ensure we have a page access token for posting"""
        if not self._page_token_fetched:
            try:
                # Get page token using user token
                url = f"{self.base_url}/me/accounts"
                params = {
                    "access_token": self.user_access_token,
                    "fields": "id,name,access_token"
                }
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    pages = data.get('data', [])
                    page_info = next((p for p in pages if p["id"] == self.page_id), None)
                    if page_info and "access_token" in page_info:
                        self.access_token = page_info["access_token"]
                        self._page_token_fetched = True
                        logger.info("Fetched and using page-specific access token for posting")
                        return True
                    else:
                        logger.warning(f"Page {self.page_id} not found in accessible pages")
                else:
                    logger.warning(f"Could not fetch pages: {response.text}")
            except Exception as e:
                logger.warning(f"Could not fetch page token: {e}. Using provided token.")
        return self._page_token_fetched
    
    def post_text(self, message: str, scheduled_time: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Post text to Facebook Page
        
        Args:
            message: Text message to post
            scheduled_time: ISO format datetime string for scheduling (optional)
            
        Returns:
            dict: Post information if successful, None otherwise
        """
        try:
            # Always ensure we have page token for posting
            self._ensure_page_token()
            
            endpoint = f"{self.page_id}/feed"
            data = {"message": message}
            
            if scheduled_time:
                # Convert to Unix timestamp
                from datetime import datetime as dt, timezone
                dt_obj = dt.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                # If no timezone info, assume local time
                if dt_obj.tzinfo is None:
                    dt_obj = dt_obj.replace(tzinfo=timezone.utc)
                timestamp = int(dt_obj.timestamp())
                
                # Facebook requires scheduled posts to be at least 10 minutes in the future
                current_timestamp = int(dt.now(timezone.utc).timestamp())
                min_future_timestamp = current_timestamp + (10 * 60)  # 10 minutes
                
                if timestamp < current_timestamp:
                    logger.error(f"Scheduled time {scheduled_time} is in the past")
                    return {
                        'success': False,
                        'error': f'Scheduled time is in the past. Current time: {dt.now(timezone.utc).isoformat()}'
                    }
                
                if timestamp < min_future_timestamp:
                    logger.error(f"Scheduled time must be at least 10 minutes in the future. Minimum: {dt.fromtimestamp(min_future_timestamp, tz=timezone.utc).isoformat()}")
                    return {
                        'success': False,
                        'error': 'Facebook requires scheduled posts to be at least 10 minutes in the future'
                    }
                
                data["published"] = False
                data["scheduled_publish_time"] = timestamp
                logger.info(f"Scheduling post for {scheduled_time} (timestamp: {timestamp}, {((timestamp - current_timestamp) / 60):.1f} minutes from now)")
            
            logger.info(f"Posting text to Facebook Page: {self.page_id}")
            result = self._make_request(endpoint, method="POST", data=data)
            
            if result and "id" in result:
                logger.info(f"Successfully posted to Facebook. Post ID: {result['id']}")
                return {
                    'success': True,
                    'post_id': result['id'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error("Failed to post to Facebook")
                return {
                    'success': False,
                    'error': 'Unknown error'
                }
                
        except Exception as e:
            logger.error(f"Error posting text to Facebook: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def post_photo(self, image_path: str, message: str = "", scheduled_time: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Post photo to Facebook Page

        Args:
            image_path: Path to the image file
            message: Caption for the photo
            scheduled_time: ISO format datetime string for scheduling (optional)

        Returns:
            dict: Post information if successful, None otherwise
        """
        try:
            # Always ensure we have page token for posting
            self._ensure_page_token()

            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None

            # Step 1: Upload photo
            endpoint = f"{self.page_id}/photos"
            files = {'file': open(image_path, 'rb')}
            data = {}

            if message:
                data['message'] = message

            if scheduled_time:
                from datetime import datetime as dt, timezone
                dt_obj = dt.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                # If no timezone info, assume local time
                if dt_obj.tzinfo is None:
                    dt_obj = dt_obj.replace(tzinfo=timezone.utc)
                timestamp = int(dt_obj.timestamp())

                # Facebook requires scheduled posts to be at least 10 minutes in the future
                current_timestamp = int(dt.now(timezone.utc).timestamp())
                min_future_timestamp = current_timestamp + (10 * 60)  # 10 minutes

                if timestamp < current_timestamp:
                    logger.error(f"Scheduled time {scheduled_time} is in the past")
                    files['file'].close()
                    return {
                        'success': False,
                        'error': f'Scheduled time is in the past. Current time: {dt.now(timezone.utc).isoformat()}'
                    }

                if timestamp < min_future_timestamp:
                    logger.error(f"Scheduled time must be at least 10 minutes in the future. Minimum: {dt.fromtimestamp(min_future_timestamp, tz=timezone.utc).isoformat()}")
                    files['file'].close()
                    return {
                        'success': False,
                        'error': 'Facebook requires scheduled posts to be at least 10 minutes in the future'
                    }

                data['published'] = False
                data['scheduled_publish_time'] = timestamp
                logger.info(f"Scheduling photo post for {scheduled_time} (timestamp: {timestamp}, {((timestamp - current_timestamp) / 60):.1f} minutes from now)")

            url = f"{self.base_url}/{endpoint}"
            params = {"access_token": self.access_token}
            params.update(data)

            logger.info(f"Uploading photo to Facebook Page: {self.page_id}")
            response = requests.post(url, params=params, files=files)
            files['file'].close()
            response.raise_for_status()
            result = response.json()

            if result and "id" in result:
                logger.info(f"Successfully posted photo to Facebook. Post ID: {result['id']}")
                return {
                    'success': True,
                    'post_id': result['id'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error("Failed to post photo to Facebook")
                return {
                    'success': False,
                    'error': 'Unknown error'
                }

        except Exception as e:
            logger.error(f"Error posting photo to Facebook: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def post_video(self, video_path: str, message: str = "", scheduled_time: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Post video to Facebook Page

        Args:
            video_path: Path to the video file
            message: Caption for the video
            scheduled_time: ISO format datetime string for scheduling (optional)

        Returns:
            dict: Post information if successful, None otherwise
        """
        try:
            # Always ensure we have page token for posting
            self._ensure_page_token()

            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return None

            # Facebook video upload endpoint
            endpoint = f"{self.page_id}/videos"
            files = {'file': open(video_path, 'rb')}
            data = {}

            if message:
                data['description'] = message

            if scheduled_time:
                from datetime import datetime as dt, timezone
                dt_obj = dt.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                # If no timezone info, assume local time
                if dt_obj.tzinfo is None:
                    dt_obj = dt_obj.replace(tzinfo=timezone.utc)
                timestamp = int(dt_obj.timestamp())

                # Facebook requires scheduled posts to be at least 10 minutes in the future
                current_timestamp = int(dt.now(timezone.utc).timestamp())
                min_future_timestamp = current_timestamp + (10 * 60)  # 10 minutes

                if timestamp < current_timestamp:
                    logger.error(f"Scheduled time {scheduled_time} is in the past")
                    files['file'].close()
                    return {
                        'success': False,
                        'error': f'Scheduled time is in the past. Current time: {dt.now(timezone.utc).isoformat()}'
                    }

                if timestamp < min_future_timestamp:
                    logger.error(f"Scheduled time must be at least 10 minutes in the future. Minimum: {dt.fromtimestamp(min_future_timestamp, tz=timezone.utc).isoformat()}")
                    files['file'].close()
                    return {
                        'success': False,
                        'error': 'Facebook requires scheduled posts to be at least 10 minutes in the future'
                    }

                data['published'] = False
                data['scheduled_publish_time'] = timestamp
                logger.info(f"Scheduling video post for {scheduled_time} (timestamp: {timestamp}, {((timestamp - current_timestamp) / 60):.1f} minutes from now)")

            url = f"{self.base_url}/{endpoint}"
            params = {"access_token": self.access_token}
            params.update(data)

            logger.info(f"Uploading video to Facebook Page: {self.page_id}")
            response = requests.post(url, params=params, files=files)
            files['file'].close()
            response.raise_for_status()
            result = response.json()

            if result and "id" in result:
                logger.info(f"Successfully posted video to Facebook. Post ID: {result['id']}")
                return {
                    'success': True,
                    'post_id': result['id'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error("Failed to post video to Facebook")
                return {
                    'success': False,
                    'error': 'Unknown error'
                }

        except Exception as e:
            logger.error(f"Error posting video to Facebook: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_credentials(self) -> bool:
        """
        Validate Facebook credentials
        
        Returns:
            bool: True if credentials are valid
        """
        try:
            # First, try to get pages to see if token is valid
            pages_endpoint = "me/accounts?fields=id,name"
            pages_result = self._make_request(pages_endpoint)
            
            if pages_result and "data" in pages_result:
                pages = pages_result["data"]
                page_ids = [page["id"] for page in pages]
                
                if self.page_id not in page_ids:
                    logger.error(f"Page ID '{self.page_id}' not found in your accessible pages")
                    logger.error(f"Available page IDs: {', '.join(page_ids)}")
                    logger.error("💡 Tip: Run 'python debug_facebook.py' to get the correct Page ID and Page Access Token")
                    return False
                
                # Get the page token for this specific page
                page_info = next((p for p in pages if p["id"] == self.page_id), None)
                if page_info and "access_token" in page_info:
                    # Update to use page-specific token (more reliable)
                    self.access_token = page_info["access_token"]
                    self._page_token_fetched = True
                    logger.info("Using page-specific access token")
            
            # Now validate the specific page
            endpoint = f"{self.page_id}?fields=id,name"
            result = self._make_request(endpoint)
            
            if result and "id" in result:
                logger.info(f"Facebook credentials valid. Page: {result.get('name', 'Unknown')}")
                return True
            else:
                logger.error("Facebook credentials invalid")
                logger.error("💡 Possible issues:")
                logger.error("   - Page ID is incorrect")
                logger.error("   - Access token doesn't have 'pages_manage_posts' permission")
                logger.error("   - Access token is expired")
                logger.error("   - You're using a User Token instead of Page Token")
                logger.error("💡 Run 'python debug_facebook.py' to diagnose the issue")
                return False
                
        except Exception as e:
            logger.error(f"Error validating Facebook credentials: {e}")
            logger.error("💡 Run 'python debug_facebook.py' to diagnose the issue")
            return False

