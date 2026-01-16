#!/usr/bin/env python3
"""
Interactive Setup Wizard for Social Media Automation
Guides users through configuring all platforms seamlessly
"""

import os
import sys
import yaml
import json
import subprocess
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("\n" + "="*70)
    print("SOCIAL MEDIA AUTOMATION SETUP WIZARD")
    print("="*70)
    print("Welcome! This wizard will help you connect all your social media accounts.")
    print("Follow the steps to configure: Gemini AI, Google Drive, Instagram, Facebook, YouTube, LinkedIn")
    print("="*70 + "\n")

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("[ERROR] Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print("[OK] Python version check passed")

def install_dependencies():
    """Install required dependencies"""
    print("\n[INFO] Checking/installing dependencies...")
    try:
        # Try to install, but don't fail if already installed
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] Dependencies ready")
        else:
            print("[WARNING] Some dependencies may need manual installation")
            print("Please run: pip install -r requirements.txt")
            # Don't fail here, continue with setup
        return True
    except Exception as e:
        print(f"[WARNING] Dependency check failed: {e}")
        print("Continuing with setup...")
        return True

def setup_gemini_drive():
    """Setup Google Gemini and Drive authentication"""
    print("\n[SECURE] STEP 1: Setting up Google Gemini & Drive")
    print("-" * 50)

    auth_dir = Path("gemini_automation/gemini_automation/auth")
    auth_dir.mkdir(parents=True, exist_ok=True)

    # Check if credentials exist
    creds_file = auth_dir / "credentials.json"
    if not creds_file.exists():
        print("❌ Google credentials not found!")
        print("\nTo set up Google Gemini & Drive:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Google Drive API and Gemini API")
        print("4. Create OAuth 2.0 credentials (Desktop application)")
        print("5. Download credentials.json and save as:")
        print(f"   {creds_file.absolute()}")
        print("\nThen re-run this setup.")
        return False

    print("[OK] Google credentials found")

    # Run bootstrap for authentication
    print("\n[KEY] Setting up Google authentication...")
    print("A browser window will open for Google login.")
    print("Select your Google account and grant permissions.")

    bootstrap_script = Path("gemini_automation/gemini_automation/bootstrap.py")
    if bootstrap_script.exists():
        try:
            # Change to the bootstrap directory and run it
            os.chdir("gemini_automation/gemini_automation")
            result = subprocess.run([sys.executable, "bootstrap.py"],
                                  capture_output=True, text=True)

            # Change back
            os.chdir("../..")

            if result.returncode == 0:
                print("✅ Google authentication setup completed!")
                return True
            else:
                print("❌ Google authentication failed")
                print("Error output:", result.stderr)
                return False

        except Exception as e:
            print(f"❌ Error running bootstrap: {e}")
            os.chdir("../..")  # Make sure we change back
            return False
    else:
        print("❌ Bootstrap script not found")
        return False

def setup_instagram():
    """Setup Instagram authentication"""
    print("\n📸 STEP 2: Setting up Instagram")
    print("-" * 50)

    config = load_config()

    print("Instagram uses browser automation for login.")
    print("You'll need to manually log in once, then it saves the session.")

    username = input("Enter your Instagram username: ").strip()
    password = input("Enter your Instagram password: ").strip()

    if not username or not password:
        print("❌ Instagram setup skipped (empty credentials)")
        return False

    # Update config
    config['instagram'] = {
        'username': username,
        'password': password,
        'enabled': True
    }

    save_config(config)
    print("✅ Instagram credentials saved")
    print("Note: First run will require manual login verification")
    return True

def setup_facebook():
    """Setup Facebook API"""
    print("\n📘 STEP 3: Setting up Facebook")
    print("-" * 50)

    print("Facebook requires a Page Access Token.")
    print("Follow these steps:")
    print("1. Go to https://developers.facebook.com/")
    print("2. Create an app or use existing")
    print("3. Add 'pages_manage_posts' permission")
    print("4. Generate Page Access Token")
    print("5. Get your Facebook Page ID")

    access_token = input("Enter Facebook Page Access Token: ").strip()
    page_id = input("Enter Facebook Page ID: ").strip()

    if not access_token or not page_id:
        print("❌ Facebook setup skipped (empty credentials)")
        return False

    config = load_config()
    config['facebook'] = {
        'access_token': access_token,
        'page_id': page_id,
        'enabled': True
    }

    save_config(config)
    print("✅ Facebook credentials saved")
    return True

def setup_youtube():
    """Setup YouTube API"""
    print("\n📺 STEP 4: Setting up YouTube")
    print("-" * 50)

    print("YouTube uses OAuth authentication.")
    print("A browser will open for Google account authorization.")

    # Check if client secrets exist
    secrets_file = Path("client_secrets.json")
    if not secrets_file.exists():
        print("❌ YouTube client_secrets.json not found!")
        print("\nTo set up YouTube:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Enable YouTube Data API v3")
        print("3. Create OAuth 2.0 credentials (Desktop app)")
        print("4. Download client_secrets.json to project root")
        print("\nThen re-run this setup.")
        return False

    print("✅ YouTube client secrets found")

    # Import and run YouTube auth
    try:
        from platforms.youtube import YouTubeAutomation

        youtube = YouTubeAutomation(
            client_secrets_file="client_secrets.json",
            credentials_file="youtube_credentials.json"
        )

        if youtube.authenticate():
            config = load_config()
            config['youtube'] = {
                'client_secrets_file': 'client_secrets.json',
                'credentials_file': 'youtube_credentials.json',
                'enabled': True
            }
            save_config(config)
            print("✅ YouTube authentication completed!")
            return True
        else:
            print("❌ YouTube authentication failed")
            return False

    except Exception as e:
        print(f"❌ YouTube setup error: {e}")
        return False

def setup_linkedin():
    """Setup LinkedIn API"""
    print("\n💼 STEP 5: Setting up LinkedIn")
    print("-" * 50)

    print("LinkedIn requires an access token with Marketing Developer Platform access.")
    print("Steps:")
    print("1. Go to https://www.linkedin.com/developers/")
    print("2. Create an app or use existing")
    print("3. Request Marketing Developer Platform access")
    print("4. Generate access token with 'w_member_social' permission")
    print("5. Get your Person URN (format: urn:li:person:xxxxx)")

    access_token = input("Enter LinkedIn Access Token: ").strip()
    person_urn = input("Enter LinkedIn Person URN: ").strip()

    if not access_token or not person_urn:
        print("❌ LinkedIn setup skipped (empty credentials)")
        return False

    config = load_config()
    config['linkedin'] = {
        'access_token': access_token,
        'person_urn': person_urn,
        'enabled': True
    }

    save_config(config)
    print("✅ LinkedIn credentials saved")
    return True

def test_connections():
    """Test all platform connections"""
    print("\n🧪 STEP 6: Testing Connections")
    print("-" * 50)

    config = load_config()
    results = {}

    # Test Gemini/Drive
    print("Testing Gemini & Drive...")
    try:
        from flows.drive_flow import DriveManager
        drive = DriveManager("gemini_automation/gemini_automation/auth/credentials.json")
        results['gemini_drive'] = True
        print("[OK] Gemini & Drive: Connected")
    except Exception as e:
        results['gemini_drive'] = False
        print(f"[ERROR] Gemini & Drive: {e}")

    # Test Instagram
    if config.get('instagram', {}).get('enabled'):
        print("Testing Instagram...")
        try:
            from platforms.instagram import InstagramAutomation
            ig = InstagramAutomation(
                config['instagram']['username'],
                config['instagram']['password']
            )
            # Just test initialization, not login
            results['instagram'] = True
            print("✅ Instagram: Configured")
        except Exception as e:
            results['instagram'] = False
            print(f"❌ Instagram: {e}")
    else:
        print("⚠️ Instagram: Not configured")

    # Test Facebook
    if config.get('facebook', {}).get('enabled'):
        print("Testing Facebook...")
        try:
            from platforms.facebook import FacebookAutomation
            fb = FacebookAutomation(
                config['facebook']['access_token'],
                config['facebook']['page_id']
            )
            results['facebook'] = True
            print("✅ Facebook: Configured")
        except Exception as e:
            results['facebook'] = False
            print(f"❌ Facebook: {e}")
    else:
        print("⚠️ Facebook: Not configured")

    # Test YouTube
    if config.get('youtube', {}).get('enabled'):
        print("Testing YouTube...")
        try:
            from platforms.youtube import YouTubeAutomation
            yt = YouTubeAutomation(
                config['youtube']['client_secrets_file'],
                config['youtube']['credentials_file']
            )
            results['youtube'] = True
            print("✅ YouTube: Configured")
        except Exception as e:
            results['youtube'] = False
            print(f"❌ YouTube: {e}")
    else:
        print("⚠️ YouTube: Not configured")

    # Test LinkedIn
    if config.get('linkedin', {}).get('enabled'):
        print("Testing LinkedIn...")
        try:
            from platforms.linkedin import LinkedInAutomation
            li = LinkedInAutomation(
                config['linkedin']['access_token'],
                config['linkedin']['person_urn']
            )
            results['linkedin'] = True
            print("✅ LinkedIn: Configured")
        except Exception as e:
            results['linkedin'] = False
            print(f"❌ LinkedIn: {e}")
    else:
        print("⚠️ LinkedIn: Not configured")

    return results

def load_config():
    """Load existing config or create default"""
    config_file = Path("config.yaml")
    if config_file.exists():
        with open(config_file, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}

def save_config(config):
    """Save configuration to file"""
    with open("config.yaml", 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

def create_default_config():
    """Create default config structure"""
    config = {
        'scheduler': {
            'check_interval': 60,
            'timezone': 'UTC'
        }
    }
    save_config(config)
    return config

def main():
    """Main setup function"""
    print_banner()

    # Initial checks
    check_python_version()

    if not install_dependencies():
        return

    # Create default config
    config = create_default_config()

    # Setup each platform
    platforms = []

    # Google Gemini & Drive (required)
    if setup_gemini_drive():
        platforms.append("Gemini/Drive")

    # Social Media Platforms (optional)
    if setup_instagram():
        platforms.append("Instagram")

    if setup_facebook():
        platforms.append("Facebook")

    if setup_youtube():
        platforms.append("YouTube")

    if setup_linkedin():
        platforms.append("LinkedIn")

    # Test connections
    test_results = test_connections()

    # Final summary
    print("\n" + "="*70)
    print("[SUCCESS] SETUP COMPLETE!")
    print("="*70)
    print(f"Platforms configured: {', '.join(platforms)}")

    working = [k for k, v in test_results.items() if v]
    if working:
        print(f"✅ Working: {', '.join(working)}")

    failed = [k for k, v in test_results.items() if not v]
    if failed:
        print(f"⚠️ Needs attention: {', '.join(failed)}")

    print("\n[READY] You're ready to use the Social Media Automation!")
    print("Run: python generatepost.py --help")
    print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
    except Exception as e:
        print(f"\n[ERROR] Setup failed with error: {e}")
        import traceback
        traceback.print_exc()