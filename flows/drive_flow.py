import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

# Scopes for Drive access
SCOPES = ['https://www.googleapis.com/auth/drive.file']

FOLDER_NAME = "Gemini Generated Content"

class DriveManager:
    def __init__(self, creds_path, allow_interactive=True):
        self.creds = None
        self.auth_dir = os.path.dirname(creds_path)
        token_path = os.path.join(self.auth_dir, 'token.pickle')
        # token.pickle stores your personal login so you only log in once
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("Attempting to refresh Google Drive token...")
                try:
                    self.creds.refresh(Request())
                    print("Token refreshed successfully!")
                except Exception as e:
                    print(f"Token refresh failed: {e}")
                    if not allow_interactive:
                        raise Exception("Google Drive authentication expired and interactive login not allowed")
                    self.creds = None
            if not self.creds and allow_interactive:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                self.creds = flow.run_local_server(port=0)
            elif not self.creds:
                raise Exception("No valid Google Drive credentials found and interactive login not allowed")

            if self.creds:
                with open(token_path, 'wb') as token:
                    pickle.dump(self.creds, token)

        if not self.creds or not self.creds.valid:
            raise Exception("Failed to obtain valid Google Drive credentials")

        self.service = build('drive', 'v3', credentials=self.creds)

    def get_or_create_folder(self, folder_name=FOLDER_NAME):
        """Get existing folder or create new one"""
        try:
            # Search for existing folder
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
            items = results.get('files', [])

            if items:
                folder_id = items[0]['id']
                print(f"Using existing folder: {folder_name} (ID: {folder_id})")
                return folder_id

            # Create new folder
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = self.service.files().create(body=file_metadata, fields='id').execute()
            folder_id = folder.get('id')
            print(f"Created new folder: {folder_name} (ID: {folder_id})")
            return folder_id

        except Exception as e:
            print(f"Error with folder operation: {e}")
            return None

    def upload_file(self, file_path, folder_id=None):
        # Handle both string paths and dict results from Gemini
        if isinstance(file_path, dict) and 'video_path' in file_path:
            actual_path = file_path['video_path']
        else:
            actual_path = file_path

        # Ensure it's a string path
        if not isinstance(actual_path, str):
            raise ValueError(f"Invalid file path type: {type(actual_path)}")

        # Get or create folder if not provided
        if folder_id is None:
            folder_id = self.get_or_create_folder()
            if not folder_id:
                raise Exception("Could not get or create Drive folder")

        file_metadata = {
            'name': os.path.basename(actual_path),
            'parents': [folder_id]
        }
        media = MediaFileUpload(actual_path, resumable=True)
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()

        print(f"Successfully uploaded: {file.get('webViewLink')}")
        return file.get('webViewLink')