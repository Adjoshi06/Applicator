"""Google Drive API client for resume fetching."""
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import Config

SCOPES = ['https://www.googleapis.com/auth/documents.readonly']


class DriveClient:
    """Client for accessing Google Drive/Docs."""
    
    def __init__(self):
        self.service = None
        self.creds = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Drive API."""
        creds = None
        token_file = "drive_token.json"
        
        if os.path.exists(token_file):
            creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    Config.GMAIL_CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.creds = creds
        self.service = build('docs', 'v1', credentials=creds)
    
    def get_resume_text(self, document_id: str) -> str:
        """Fetch resume text from Google Doc."""
        try:
            doc = self.service.documents().get(documentId=document_id).execute()
            text_content = []
            
            for element in doc.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    for elem in element['paragraph'].get('elements', []):
                        if 'textRun' in elem:
                            text_content.append(elem['textRun'].get('content', ''))
            
            return ''.join(text_content)
        except HttpError as error:
            print(f"Error fetching resume: {error}")
            return ""

