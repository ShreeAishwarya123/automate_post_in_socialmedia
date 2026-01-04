"""
Post to Instagram - Individual Platform Script
Post photos or carousels to Instagram
"""
import sys
import yaml
from platforms.instagram import InstagramAutomation

def load_config():
    """Load configuration"""
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        return config.get('instagram', {})
    except Exception as e:
        print(f"[ERROR] Could not load config.yaml: {e}")
        return None

def post_photo(image_path, caption):
    """Post single photo to Instagram"""
    config = load_config()
    if not config:
        return False
    
    if not config.get('enabled', False):
        print("[ERROR] Instagram is disabled in config.yaml")
        return False
    
    username = config.get('username', '')
    password = config.get('password', '')
    
    if not username or not password:
        print("[ERROR] Instagram credentials not found in config.yaml")
        return False
    
    print(f"Posting to Instagram...")
    print(f"Image: {image_path}")
    print(f"Caption: {caption[:100]}{'...' if len(caption) > 100 else ''}")
    
    instagram = InstagramAutomation(username, password)
    if not instagram.login():
        print("[ERROR] Instagram login failed")
        return False
    
    result = instagram.post_photo(image_path, caption)
    
    if result and result.get('success'):
        print(f"\n[SUCCESS] Post created!")
        print(f"Post ID: {result.get('post_id', 'N/A')}")
        return True
    else:
        print(f"\n[ERROR] Failed to post")
        print(f"Error: {result.get('error', 'Unknown error') if result else 'No result'}")
        return False

def post_carousel(image_paths, caption):
    """Post carousel to Instagram"""
    config = load_config()
    if not config:
        return False
    
    if not config.get('enabled', False):
        print("[ERROR] Instagram is disabled in config.yaml")
        return False
    
    username = config.get('username', '')
    password = config.get('password', '')
    
    if not username or not password:
        print("[ERROR] Instagram credentials not found in config.yaml")
        return False
    
    print(f"Posting carousel to Instagram...")
    print(f"Images: {len(image_paths)} images")
    print(f"Caption: {caption[:100]}{'...' if len(caption) > 100 else ''}")
    
    instagram = InstagramAutomation(username, password)
    if not instagram.login():
        print("[ERROR] Instagram login failed")
        return False
    
    result = instagram.post_carousel(image_paths, caption)
    
    if result and result.get('success'):
        print(f"\n[SUCCESS] Carousel created!")
        print(f"Post ID: {result.get('post_id', 'N/A')}")
        return True
    else:
        print(f"\n[ERROR] Failed to post")
        print(f"Error: {result.get('error', 'Unknown error') if result else 'No result'}")
        return False

def main():
    """Main function"""
    if len(sys.argv) < 3 or '--help' in sys.argv or '-h' in sys.argv:
        print("Usage:")
        print("  python post_instagram.py \"Caption text\" --image path/to/image.jpg")
        print("  python post_instagram.py \"Caption text\" --images img1.jpg img2.jpg img3.jpg")
        print("\nExample:")
        print("  python post_instagram.py \"My awesome post!\" --image photo.jpg")
        print("  python post_instagram.py \"Carousel post!\" --images img1.jpg img2.jpg img3.jpg")
        sys.exit(1)
    
    caption = sys.argv[1]
    
    if '--images' in sys.argv:
        image_index = sys.argv.index('--images')
        if image_index + 1 < len(sys.argv):
            image_paths = sys.argv[image_index + 1:]
            success = post_carousel(image_paths, caption)
        else:
            print("[ERROR] --images flag requires at least one image path")
            sys.exit(1)
    elif '--image' in sys.argv:
        image_index = sys.argv.index('--image')
        if image_index + 1 < len(sys.argv):
            image_path = sys.argv[image_index + 1]
            success = post_photo(image_path, caption)
        else:
            print("[ERROR] --image flag requires an image path")
            sys.exit(1)
    else:
        print("[ERROR] Instagram requires an image. Use --image or --images")
        sys.exit(1)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

