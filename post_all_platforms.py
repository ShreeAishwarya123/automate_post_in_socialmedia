"""
Post to All Platforms - Unified Script
Post to Instagram, Facebook, YouTube, and LinkedIn in one command
"""
import sys
import os
import yaml
import argparse
from datetime import datetime
from typing import Dict, List, Optional

# Import platform modules
from platforms.instagram import InstagramAutomation
from platforms.facebook import FacebookAutomation
from platforms.youtube import YouTubeAutomation
from platforms.linkedin import LinkedInAutomation

# Import LinkedIn constants
try:
    from linkedin_constants import LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_URN
    USE_LINKEDIN_CONSTANTS = True
except ImportError:
    USE_LINKEDIN_CONSTANTS = False

def load_config():
    """Load configuration from config.yaml"""
    try:
        with open('config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"[ERROR] Could not load config.yaml: {e}")
        return None

def post_to_instagram(text: str, image_path: Optional[str] = None, image_paths: Optional[List[str]] = None):
    """Post to Instagram"""
    config = load_config()
    if not config:
        return {'success': False, 'error': 'Could not load config'}
    
    instagram_config = config.get('instagram', {})
    if not instagram_config.get('enabled', False):
        return {'success': False, 'error': 'Instagram is disabled'}
    
    try:
        instagram = InstagramAutomation(
            instagram_config.get('username', ''),
            instagram_config.get('password', '')
        )
        
        if not instagram.login():
            return {'success': False, 'error': 'Instagram login failed'}
        
        if image_paths and len(image_paths) > 1:
            # Carousel post
            result = instagram.post_carousel(image_paths, text)
        elif image_path:
            # Single photo post
            result = instagram.post_photo(image_path, text)
        else:
            return {'success': False, 'error': 'Instagram requires an image'}
        
        if result and result.get('success'):
            return {'success': True, 'platform': 'Instagram', 'result': result}
        else:
            return {'success': False, 'error': result.get('error', 'Unknown error') if result else 'No result'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def post_to_facebook(text: str, image_path: Optional[str] = None):
    """Post to Facebook"""
    config = load_config()
    if not config:
        return {'success': False, 'error': 'Could not load config'}
    
    facebook_config = config.get('facebook', {})
    if not facebook_config.get('enabled', False):
        return {'success': False, 'error': 'Facebook is disabled'}
    
    try:
        facebook = FacebookAutomation(
            facebook_config.get('access_token', ''),
            facebook_config.get('page_id', '')
        )
        
        if image_path:
            result = facebook.post_photo(image_path, text)
        else:
            result = facebook.post_text(text)
        
        if result and result.get('success'):
            return {'success': True, 'platform': 'Facebook', 'result': result}
        else:
            return {'success': False, 'error': result.get('error', 'Unknown error') if result else 'No result'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def post_to_youtube(video_path: str, title: str, description: str = "", tags: Optional[List[str]] = None):
    """Post to YouTube"""
    config = load_config()
    if not config:
        return {'success': False, 'error': 'Could not load config'}
    
    youtube_config = config.get('youtube', {})
    if not youtube_config.get('enabled', False):
        return {'success': False, 'error': 'YouTube is disabled'}
    
    try:
        youtube = YouTubeAutomation(
            youtube_config.get('client_secrets_file', 'client_secrets.json'),
            youtube_config.get('credentials_file', 'youtube_credentials.json')
        )
        
        if not youtube.authenticate():
            return {'success': False, 'error': 'YouTube authentication failed'}
        
        result = youtube.upload_video(
            video_path,
            title,
            description,
            tags or [],
            category_id='22',
            privacy_status='public'
        )
        
        if result and result.get('success'):
            return {'success': True, 'platform': 'YouTube', 'result': result}
        else:
            return {'success': False, 'error': result.get('error', 'Unknown error') if result else 'No result'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def post_to_linkedin(text: str, image_path: Optional[str] = None):
    """Post to LinkedIn"""
    config = load_config()
    if not config:
        return {'success': False, 'error': 'Could not load config'}
    
    linkedin_config = config.get('linkedin', {})
    if not linkedin_config.get('enabled', False):
        return {'success': False, 'error': 'LinkedIn is disabled'}
    
    try:
        # Use constants if available, otherwise use config
        if USE_LINKEDIN_CONSTANTS:
            token = LINKEDIN_ACCESS_TOKEN
            urn = LINKEDIN_PERSON_URN
        else:
            token = linkedin_config.get('access_token', '')
            urn = linkedin_config.get('person_urn', '')
        
        if not token or not urn:
            return {'success': False, 'error': 'LinkedIn credentials not found'}
        
        linkedin = LinkedInAutomation(token, urn)
        
        if image_path:
            result = linkedin.post_with_image(text, image_path)
        else:
            result = linkedin.post_text(text)
        
        if result and result.get('success'):
            return {'success': True, 'platform': 'LinkedIn', 'result': result}
        else:
            return {'success': False, 'error': result.get('error', 'Unknown error') if result else 'No result'}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def post_to_all(text: str, image_path: Optional[str] = None, video_path: Optional[str] = None,
                platforms: Optional[List[str]] = None, title: str = "", description: str = "",
                tags: Optional[List[str]] = None, image_paths: Optional[List[str]] = None):
    """
    Post to all specified platforms
    
    Args:
        text: Text content for the post
        image_path: Path to single image (for Instagram, Facebook, LinkedIn)
        video_path: Path to video (for YouTube)
        platforms: List of platforms to post to (default: all enabled)
        title: Title for YouTube video
        description: Description for YouTube video
        tags: Tags for YouTube video
        image_paths: Multiple images for Instagram carousel
    """
    if platforms is None:
        platforms = ['instagram', 'facebook', 'linkedin']
        if video_path:
            platforms.append('youtube')
    
    results = {}
    
    print("=" * 70)
    print("  POSTING TO ALL PLATFORMS")
    print("=" * 70)
    print(f"\nText: {text[:100]}{'...' if len(text) > 100 else ''}")
    if image_path:
        print(f"Image: {image_path}")
    if video_path:
        print(f"Video: {video_path}")
    if image_paths:
        print(f"Images (carousel): {len(image_paths)} images")
    print(f"\nPlatforms: {', '.join(platforms)}")
    print("\n" + "-" * 70)
    
    # Post to each platform
    for platform in platforms:
        platform_lower = platform.lower()
        print(f"\n[{platform_lower.upper()}] Posting...")
        
        try:
            if platform_lower == 'instagram':
                if image_paths:
                    result = post_to_instagram(text, image_paths=image_paths)
                elif image_path:
                    result = post_to_instagram(text, image_path=image_path)
                else:
                    result = {'success': False, 'error': 'Instagram requires an image'}
                    
            elif platform_lower == 'facebook':
                result = post_to_facebook(text, image_path)
                
            elif platform_lower == 'youtube':
                if not video_path:
                    result = {'success': False, 'error': 'YouTube requires a video'}
                else:
                    result = post_to_youtube(video_path, title or text, description, tags)
                    
            elif platform_lower == 'linkedin':
                result = post_to_linkedin(text, image_path)
                
            else:
                result = {'success': False, 'error': f'Unknown platform: {platform}'}
            
            results[platform_lower] = result
            
            if result.get('success'):
                print(f"[OK] Posted successfully to {platform_lower}")
                if 'result' in result and 'post_id' in result['result']:
                    print(f"     Post ID: {result['result'].get('post_id', 'N/A')}")
            else:
                print(f"[FAIL] Failed to post to {platform_lower}")
                print(f"     Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            results[platform_lower] = {'success': False, 'error': str(e)}
            print(f"[ERROR] Exception posting to {platform_lower}: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    
    successful = [p for p, r in results.items() if r.get('success')]
    failed = [p for p, r in results.items() if not r.get('success')]
    
    if successful:
        print(f"\n[SUCCESS] Posted to: {', '.join(successful)}")
    
    if failed:
        print(f"\n[FAILED] Failed on: {', '.join(failed)}")
        for platform in failed:
            error = results[platform].get('error', 'Unknown error')
            print(f"  - {platform}: {error}")
    
    print("\n" + "=" * 70)
    
    return results

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Post to all social media platforms',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Post text to all platforms
  python post_all_platforms.py "Hello from all platforms!"

  # Post text with image to all platforms
  python post_all_platforms.py "Check this out!" --image photo.jpg

  # Post to specific platforms only
  python post_all_platforms.py "Hello!" --platforms facebook linkedin

  # Post video to YouTube
  python post_all_platforms.py "My video" --video video.mp4 --title "Video Title"

  # Post Instagram carousel
  python post_all_platforms.py "Carousel post" --images img1.jpg img2.jpg img3.jpg
        """
    )
    
    parser.add_argument('text', help='Text content for the post')
    parser.add_argument('--image', '-i', help='Path to image file (for Instagram, Facebook, LinkedIn)')
    parser.add_argument('--images', nargs='+', help='Multiple images for Instagram carousel')
    parser.add_argument('--video', '-v', help='Path to video file (for YouTube)')
    parser.add_argument('--platforms', '-p', nargs='+', 
                       choices=['instagram', 'facebook', 'youtube', 'linkedin'],
                       help='Platforms to post to (default: all enabled)')
    parser.add_argument('--title', help='Title for YouTube video (default: uses text)')
    parser.add_argument('--description', help='Description for YouTube video')
    parser.add_argument('--tags', nargs='+', help='Tags for YouTube video')
    
    args = parser.parse_args()
    
    # Validate inputs
    if args.video and not os.path.exists(args.video):
        print(f"[ERROR] Video file not found: {args.video}")
        sys.exit(1)
    
    if args.image and not os.path.exists(args.image):
        print(f"[ERROR] Image file not found: {args.image}")
        sys.exit(1)
    
    if args.images:
        for img in args.images:
            if not os.path.exists(img):
                print(f"[ERROR] Image file not found: {img}")
                sys.exit(1)
    
    # Post to all platforms
    results = post_to_all(
        text=args.text,
        image_path=args.image,
        video_path=args.video,
        platforms=args.platforms,
        title=args.title,
        description=args.description,
        tags=args.tags,
        image_paths=args.images
    )
    
    # Exit with error code if any failed
    if any(not r.get('success') for r in results.values()):
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == '__main__':
    main()

