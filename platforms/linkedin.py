import os
import logging
import requests
from datetime import datetime
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LinkedInAutomation:
    """LinkedIn automation class for posting and scheduling"""
    
    def __init__(self, access_token: str, person_urn: str):
        """
        Initialize LinkedIn client
        
        Args:
            access_token: LinkedIn Access Token
            person_urn: LinkedIn Person URN or Organization URN
                       (e.g., urn:li:person:xxxxx or urn:li:organization:xxxxx)
        """
        self.access_token = access_token
        self.person_urn = person_urn  # Can be member, person, organization, or fsd_company URN
        self.base_url = "https://api.linkedin.com/v2"
        # Detect URN type
        if person_urn:
            self.is_organization = person_urn.startswith("urn:li:organization:") or person_urn.startswith("urn:li:fsd_company:") or person_urn.startswith("urn:li:fsd_organizationalPage:")
            self.is_member = person_urn.startswith("urn:li:member:") or person_urn.startswith("urn:li:person:")
        else:
            self.is_organization = False
            self.is_member = False
        
    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make API request to LinkedIn API
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            data: Request data
            
        Returns:
            dict: API response or None if error
        """
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedIn API request failed: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            return None
    
    def post_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Post text to LinkedIn
        
        Args:
            text: Text content to post
            
        Returns:
            dict: Post information if successful, None otherwise
        """
        try:
            # LinkedIn requires specific format for posts
            endpoint = "ugcPosts"
            data = {
                "author": self.person_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            logger.info("Posting text to LinkedIn")
            result = self._make_request(endpoint, method="POST", data=data)
            
            if result and "id" in result:
                logger.info(f"Successfully posted to LinkedIn. Post ID: {result['id']}")
                return {
                    'success': True,
                    'post_id': result['id'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error("Failed to post to LinkedIn")
                return {
                    'success': False,
                    'error': 'Unknown error'
                }
                
        except Exception as e:
            logger.error(f"Error posting text to LinkedIn: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def post_with_image(self, text: str, image_path: str) -> Optional[Dict[str, Any]]:
        """
        Post text with image to LinkedIn

        Args:
            text: Text content to post
            image_path: Path to the image file

        Returns:
            dict: Post information if successful, None otherwise
        """
        try:
            if not os.path.exists(image_path):
                logger.error(f"Image file not found: {image_path}")
                return None

            # Step 1: Register upload
            register_endpoint = "assets?action=registerUpload"
            register_data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": self.person_urn,
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }

            logger.info("Registering image upload to LinkedIn")
            register_result = self._make_request(register_endpoint, method="POST", data=register_data)

            if not register_result or "value" not in register_result:
                logger.error("Failed to register image upload")
                return None

            upload_url = register_result["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
            asset_urn = register_result["value"]["asset"]

            # Step 2: Upload image
            logger.info("Uploading image to LinkedIn")
            with open(image_path, 'rb') as img_file:
                upload_headers = {
                    "Authorization": f"Bearer {self.access_token}"
                }
                upload_response = requests.put(upload_url, headers=upload_headers, data=img_file)
                upload_response.raise_for_status()

            # Step 3: Create post with image
            endpoint = "ugcPosts"
            data = {
                "author": self.person_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "IMAGE",
                        "media": [
                            {
                                "status": "READY",
                                "description": {
                                    "text": text[:200]  # Description limited to 200 chars
                                },
                                "media": asset_urn,
                                "title": {
                                    "text": "Image"
                                }
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            logger.info("Creating LinkedIn post with image")
            result = self._make_request(endpoint, method="POST", data=data)

            if result and "id" in result:
                logger.info(f"Successfully posted to LinkedIn with image. Post ID: {result['id']}")
                return {
                    'success': True,
                    'post_id': result['id'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error("Failed to post to LinkedIn")
                return {
                    'success': False,
                    'error': 'Unknown error'
                }

        except Exception as e:
            logger.error(f"Error posting to LinkedIn: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def post_with_video(self, text: str, video_path: str) -> Optional[Dict[str, Any]]:
        """
        Post text with video to LinkedIn

        Args:
            text: Text content to post
            video_path: Path to the video file

        Returns:
            dict: Post information if successful, None otherwise
        """
        try:
            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return None

            # Step 1: Register upload for video
            register_endpoint = "assets?action=registerUpload"
            register_data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-video"],
                    "owner": self.person_urn,
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }

            logger.info("Registering video upload to LinkedIn")
            register_result = self._make_request(register_endpoint, method="POST", data=register_data)

            if not register_result or "value" not in register_result:
                logger.error("Failed to register video upload")
                return None

            upload_url = register_result["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
            asset_urn = register_result["value"]["asset"]

            # Step 2: Upload video
            logger.info("Uploading video to LinkedIn")
            with open(video_path, 'rb') as video_file:
                upload_headers = {
                    "Authorization": f"Bearer {self.access_token}"
                }
                upload_response = requests.put(upload_url, headers=upload_headers, data=video_file)
                upload_response.raise_for_status()

            # Step 3: Create post with video
            endpoint = "ugcPosts"
            data = {
                "author": self.person_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "VIDEO",
                        "media": [
                            {
                                "status": "READY",
                                "description": {
                                    "text": text[:200]  # Description limited to 200 chars
                                },
                                "media": asset_urn,
                                "title": {
                                    "text": "Video"
                                }
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }

            logger.info("Creating LinkedIn post with video")
            result = self._make_request(endpoint, method="POST", data=data)

            if result and "id" in result:
                logger.info(f"Successfully posted to LinkedIn with video. Post ID: {result['id']}")
                return {
                    'success': True,
                    'post_id': result['id'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error("Failed to post to LinkedIn")
                return {
                    'success': False,
                    'error': 'Unknown error'
                }

        except Exception as e:
            logger.error(f"Error posting to LinkedIn: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_credentials(self) -> bool:
        """
        Validate LinkedIn credentials
        
        Returns:
            bool: True if credentials are valid
        """
        # For Pages, we might not have /me access, so try a different approach
        if self.is_organization:
            # For Pages, try to validate by attempting to get organization info
            # or just check if token format is valid
            logger.info("Validating LinkedIn Page credentials...")
            # Token validation for Pages - we'll test by trying to post
            # For now, just check if URN format is correct
            if self.person_urn and ("organization" in self.person_urn or "fsd_company" in self.person_urn):
                logger.info(f"LinkedIn Page URN format valid: {self.person_urn}")
                logger.info("Note: Full validation requires posting test. Token permissions will be checked when posting.")
                return True
            else:
                logger.error("Invalid LinkedIn Page URN format")
                return False
        else:
            # For personal profiles or member URNs, try /me endpoint
            # But if it fails (no r_liteprofile permission), we'll validate by URN format
            try:
                endpoint = "me"
                result = self._make_request(endpoint)
                
                if result and "id" in result:
                    logger.info(f"LinkedIn credentials valid. User ID: {result.get('id', 'Unknown')}")
                    return True
                else:
                    logger.warning("Could not validate via /me endpoint, but will check URN format")
                    # Fall through to URN format check
                    
            except Exception as e:
                logger.warning(f"Could not validate via /me endpoint: {e}")
                logger.info("This is normal if token lacks r_liteprofile permission. Will validate by URN format.")
                # Fall through to URN format check
            
            # Validate by URN format (works even without /me permission)
            if self.person_urn and (self.is_organization or self.is_member):
                logger.info(f"LinkedIn URN format valid: {self.person_urn}")
                logger.info("Note: Full validation requires posting test. Token permissions will be checked when posting.")
                return True
            else:
                logger.error(f"Invalid LinkedIn URN format: {self.person_urn}")
                return False

