"""
Post to YouTube - Individual Platform Script
Upload videos to YouTube
"""
import sys
import yaml
from platforms.youtube import YouTubeAutomation

def load_config():
    """Load configuration"""
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        return config.get('youtube', {})
    except Exception as e:
        print(f"[ERROR] Could not load config.yaml: {e}")
        return None

def upload_video(video_path, title, description="", tags=None, privacy_status="public"):
    """Upload video to YouTube"""
    config = load_config()
    if not config:
        return False
    
    if not config.get('enabled', False):
        print("[ERROR] YouTube is disabled in config.yaml")
        return False
    
    client_secrets = config.get('client_secrets_file', 'client_secrets.json')
    credentials_file = config.get('credentials_file', 'youtube_credentials.json')
    
    print(f"Uploading to YouTube...")
    print(f"Video: {video_path}")
    print(f"Title: {title}")
    if description:
        print(f"Description: {description[:100]}{'...' if len(description) > 100 else ''}")
    if tags:
        print(f"Tags: {', '.join(tags)}")
    
    youtube = YouTubeAutomation(client_secrets, credentials_file)
    if not youtube.authenticate():
        print("[ERROR] YouTube authentication failed")
        return False
    
    result = youtube.upload_video(
        video_path,
        title,
        description,
        tags or [],
        category_id='22',
        privacy_status=privacy_status
    )
    
    if result and result.get('success'):
        print(f"\n[SUCCESS] Video uploaded!")
        print(f"Video ID: {result.get('video_id', 'N/A')}")
        print(f"URL: {result.get('video_url', 'N/A')}")
        return True
    else:
        print(f"\n[ERROR] Failed to upload")
        print(f"Error: {result.get('error', 'Unknown error') if result else 'No result'}")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 3 or '--help' in sys.argv or '-h' in sys.argv:
        print("Usage:")
        print("  python post_youtube.py \"Video Title\" --video path/to/video.mp4")
        print("  python post_youtube.py \"Video Title\" --video video.mp4 --description \"Description\" --tags tag1 tag2")
        print("\nExample:")
        print("  python post_youtube.py \"My Video\" --video video.mp4")
        print("  python post_youtube.py \"My Video\" --video video.mp4 --description \"Video description\" --tags tech tutorial")
        sys.exit(1)
    
    title = sys.argv[1]
    
    if '--video' not in sys.argv:
        print("[ERROR] YouTube requires a video. Use --video flag")
        sys.exit(1)
    
    video_index = sys.argv.index('--video')
    if video_index + 1 >= len(sys.argv):
        print("[ERROR] --video flag requires a video path")
        sys.exit(1)
    
    video_path = sys.argv[video_index + 1]
    
    description = ""
    if '--description' in sys.argv:
        desc_index = sys.argv.index('--description')
        if desc_index + 1 < len(sys.argv):
            description = sys.argv[desc_index + 1]
    
    tags = None
    if '--tags' in sys.argv:
        tags_index = sys.argv.index('--tags')
        if tags_index + 1 < len(sys.argv):
            tags = sys.argv[tags_index + 1:]
    
    privacy = "public"
    if '--privacy' in sys.argv:
        priv_index = sys.argv.index('--privacy')
        if priv_index + 1 < len(sys.argv):
            privacy = sys.argv[priv_index + 1]
    
    success = upload_video(video_path, title, description, tags, privacy)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

