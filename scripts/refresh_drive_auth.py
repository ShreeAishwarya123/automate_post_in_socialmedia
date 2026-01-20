#!/usr/bin/env python3
"""
Refresh Google Drive authentication
"""

from flows.drive_flow import DriveManager
import os

def refresh_drive_auth():
    """Refresh Google Drive authentication interactively"""
    print("Refreshing Google Drive Authentication...")
    print("=" * 50)

    creds_path = 'gemini_automation/gemini_automation/auth/credentials.json'

    if not os.path.exists(creds_path):
        print("ERROR: Google credentials file not found!")
        print("Please run setup.py first")
        return False

    try:
        print("Connecting to Google Drive...")
        # This will try to refresh tokens or prompt for new authentication
        drive = DriveManager(creds_path, allow_interactive=True)
        print("SUCCESS: Google Drive authentication successful!")
        return True

    except Exception as e:
        print(f"ERROR: Authentication failed: {e}")
        return False

if __name__ == "__main__":
    success = refresh_drive_auth()
    if success:
        print("\nSUCCESS: You can now use the web interface!")
        print("Go to http://localhost:8000 and try creating a post.")
    else:
        print("\nFAILED: Please check your internet connection and try again.")