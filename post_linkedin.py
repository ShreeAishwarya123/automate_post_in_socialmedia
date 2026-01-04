"""
Simple LinkedIn Post Script
Post text or text with image to LinkedIn
"""
import sys
import yaml
from platforms.linkedin import LinkedInAutomation

# Import centralized constants
try:
    from linkedin_constants import LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_URN, get_linkedin_token, get_linkedin_urn
    USE_CONSTANTS = True
except ImportError:
    USE_CONSTANTS = False

def load_config():
    """Load configuration from constants file or config.yaml"""
    if USE_CONSTANTS:
        return {
            'access_token': get_linkedin_token(),
            'person_urn': get_linkedin_urn(),
            'enabled': True
        }
    else:
        try:
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
            return config.get('linkedin', {})
        except Exception as e:
            print(f"[ERROR] Could not load config.yaml: {e}")
            return None

def post_text(text):
    """Post text to LinkedIn"""
    config = load_config()
    if not config:
        return False
    
    if not config.get('enabled', False):
        print("[ERROR] LinkedIn is disabled in config.yaml")
        return False
    
    token = config.get('access_token', '')
    urn = config.get('person_urn', '')
    
    if not token or not urn:
        print("[ERROR] LinkedIn credentials not found in config.yaml")
        return False
    
    print(f"Posting to LinkedIn...")
    print(f"Text: {text[:100]}{'...' if len(text) > 100 else ''}")
    
    linkedin = LinkedInAutomation(token, urn)
    result = linkedin.post_text(text)
    
    if result and result.get('success'):
        print(f"\n[SUCCESS] Post created!")
        print(f"Post ID: {result.get('post_id', 'N/A')}")
        return True
    else:
        print(f"\n[ERROR] Failed to post")
        print(f"Error: {result.get('error', 'Unknown error') if result else 'No result'}")
        return False

def post_with_image(text, image_path):
    """Post text with image to LinkedIn"""
    import os
    
    config = load_config()
    if not config:
        return False
    
    if not config.get('enabled', False):
        print("[ERROR] LinkedIn is disabled in config.yaml")
        return False
    
    token = config.get('access_token', '')
    urn = config.get('person_urn', '')
    
    if not token or not urn:
        print("[ERROR] LinkedIn credentials not found in config.yaml")
        return False
    
    if not os.path.exists(image_path):
        print(f"[ERROR] Image file not found: {image_path}")
        return False
    
    print(f"Posting to LinkedIn with image...")
    print(f"Text: {text[:100]}{'...' if len(text) > 100 else ''}")
    print(f"Image: {image_path}")
    
    linkedin = LinkedInAutomation(token, urn)
    result = linkedin.post_with_image(text, image_path)
    
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
        print("  python post_linkedin.py \"Your post text here\"")
        print("  python post_linkedin.py \"Your post text\" --image path/to/image.jpg")
        print("\nExample:")
        print("  python post_linkedin.py \"Hello LinkedIn! This is a test post.\"")
        print("  python post_linkedin.py \"Check this out!\" --image test.jpg")
        sys.exit(1)
    
    text = sys.argv[1]
    
    if '--image' in sys.argv:
        image_index = sys.argv.index('--image')
        if image_index + 1 < len(sys.argv):
            image_path = sys.argv[image_index + 1]
            success = post_with_image(text, image_path)
        else:
            print("[ERROR] --image flag requires an image path")
            sys.exit(1)
    else:
        success = post_text(text)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

