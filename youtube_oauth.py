#!/usr/bin/env python3
"""
Manual YouTube OAuth Setup Script
Run this directly to authenticate YouTube without the web interface
"""

import os
import sys
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle

# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def setup_youtube_oauth():
    """Perform YouTube OAuth setup manually"""

    # Path to your client secrets file
    client_secrets_file = r'C:\Users\aishu\Desktop\hive\config\youtube_client_secrets.json'

    # Path where credentials will be saved
    credentials_file = r'C:\Users\aishu\Desktop\hive\config\youtube_credentials.json'

    print("🎥 YouTube OAuth Setup")
    print("=" * 50)

    # Check if client secrets file exists
    if not os.path.exists(client_secrets_file):
        print(f"❌ Client secrets file not found: {client_secrets_file}")
        print("\n📋 To fix:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create/select project 'gemini-automation-483705'")
        print("3. Enable YouTube Data API v3")
        print("4. Create OAuth 2.0 Client ID (Desktop application)")
        print("5. Download JSON and save as: config/youtube_client_secrets.json")
        return False

    print(f"✅ Found client secrets: {client_secrets_file}")

    # Check if credentials already exist
    if os.path.exists(credentials_file):
        print(f"⚠️  Credentials file already exists: {credentials_file}")
        overwrite = input("Overwrite existing credentials? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("Using existing credentials...")
            return True

    try:
        print("\n🔄 Starting YouTube OAuth flow...")
        print("A browser window will open for authentication.")
        print("Sign in with your Google/YouTube account and grant permissions.")
        print("")

        # Create OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, SCOPES
        )

        # Run OAuth flow
        creds = flow.run_local_server(port=0)

        # Save credentials
        print(f"\n💾 Saving credentials to: {credentials_file}")
        os.makedirs(os.path.dirname(credentials_file), exist_ok=True)

        with open(credentials_file, 'wb') as token:
            pickle.dump(creds, token)

        print("✅ YouTube OAuth completed successfully!")

        # Test the connection
        print("\n🔍 Testing YouTube connection...")
        youtube = build('youtube', 'v3', credentials=creds)

        # Try to get channel info (this might fail due to scope limitations)
        try:
            channels_response = youtube.channels().list(
                part='snippet',
                mine=True
            ).execute()

            if 'items' in channels_response and channels_response['items']:
                channel = channels_response['items'][0]
                channel_title = channel['snippet']['title']
                print(f"✅ Connected to YouTube channel: {channel_title}")
            else:
                print("✅ YouTube authentication successful (channel info not available with current scope)")

        except Exception as e:
            print(f"⚠️  Authentication successful but channel info unavailable: {e}")
            print("This is normal for upload-only scope.")

        print("\n🎉 YouTube is now ready for video uploads!")
        return True

    except Exception as e:
        print(f"❌ YouTube OAuth failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you selected 'Desktop application' when creating OAuth credentials")
        print("2. Ensure your Google account has YouTube access")
        print("3. Try deleting the credentials file and running again")
        return False

if __name__ == "__main__":
    success = setup_youtube_oauth()
    if success:
        print("\n✅ You can now use YouTube in your Hive application!")
    else:
        print("\n❌ YouTube setup failed. Please check the errors above.")

    input("\nPress Enter to exit...")