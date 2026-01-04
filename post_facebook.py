"""
Post to Facebook - Individual Platform Script
Post text or images to Facebook
"""
import sys
import yaml
from platforms.facebook import FacebookAutomation

def load_config():
    """Load configuration"""
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        return config.get('facebook', {})
    except Exception as e:
        print(f"[ERROR] Could not load config.yaml: {e}")
        return None

def post_text(message):
    """Post text to Facebook"""
    config = load_config()
    if not config:
        return False
    
    if not config.get('enabled', False):
        print("[ERROR] Facebook is disabled in config.yaml")
        return False
    
    access_token = config.get('access_token', '')
    page_id = config.get('page_id', '')
    
    if not access_token or not page_id:
        print("[ERROR] Facebook credentials not found in config.yaml")
        return False
    
    print(f"Posting to Facebook...")
    print(f"Message: {message[:100]}{'...' if len(message) > 100 else ''}")
    
    facebook = FacebookAutomation(access_token, page_id)
    result = facebook.post_text(message)
    
    if result and result.get('success'):
        print(f"\n[SUCCESS] Post created!")
        print(f"Post ID: {result.get('post_id', 'N/A')}")
        return True
    else:
        print(f"\n[ERROR] Failed to post")
        print(f"Error: {result.get('error', 'Unknown error') if result else 'No result'}")
        return False

def post_photo(image_path, message):
    """Post photo to Facebook"""
    config = load_config()
    if not config:
        return False
    
    if not config.get('enabled', False):
        print("[ERROR] Facebook is disabled in config.yaml")
        return False
    
    access_token = config.get('access_token', '')
    page_id = config.get('page_id', '')
    
    if not access_token or not page_id:
        print("[ERROR] Facebook credentials not found in config.yaml")
        return False
    
    print(f"Posting to Facebook with image...")
    print(f"Message: {message[:100]}{'...' if len(message) > 100 else ''}")
    print(f"Image: {image_path}")
    
    facebook = FacebookAutomation(access_token, page_id)
    result = facebook.post_photo(image_path, message)
    
    if result and result.get('success'):
        print(f"\n[SUCCESS] Post created!")
        print(f"Post ID: {result.get('post_id', 'N/A')}")
        return True
    else:
        print(f"\n[ERROR] Failed to post")
        print(f"Error: {result.get('error', 'Unknown error') if result else 'No result'}")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 2 or '--help' in sys.argv or '-h' in sys.argv:
        print("Usage:")
        print("  python post_facebook.py \"Your message here\"")
        print("  python post_facebook.py \"Your message\" --image path/to/image.jpg")
        print("\nExample:")
        print("  python post_facebook.py \"Hello Facebook!\"")
        print("  python post_facebook.py \"Check this out!\" --image photo.jpg")
        sys.exit(1)
    
    message = sys.argv[1]
    
    if '--image' in sys.argv:
        image_index = sys.argv.index('--image')
        if image_index + 1 < len(sys.argv):
            image_path = sys.argv[image_index + 1]
            success = post_photo(image_path, message)
        else:
            print("[ERROR] --image flag requires an image path")
            sys.exit(1)
    else:
        success = post_text(message)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

