"""Gmail API client for email monitoring."""
import os
import base64
import re
from email import message_from_bytes
from html.parser import HTMLParser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import Config

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class HTMLTextExtractor(HTMLParser):
    """Extract text from HTML emails."""
    
    def __init__(self):
        super().__init__()
        self.text = []
    
    def handle_data(self, data):
        self.text.append(data)
    
    def get_text(self):
        return ' '.join(self.text)


class GmailClient:
    """Client for accessing Gmail."""
    
    def __init__(self):
        self.service = None
        self.creds = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API."""
        creds = None
        token_file = "gmail_token.json"
        
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
        self.service = build('gmail', 'v1', credentials=creds)
    
    def get_unread_job_emails(self, max_results: int = 50) -> list:
        """Get unread emails that might be job alerts."""
        try:
            # Search for unread emails from common job sites
            query = 'is:unread (from:linkedin.com OR from:indeed.com OR from:glassdoor.com OR from:ziprecruiter.com OR from:monster.com OR subject:"job" OR subject:"position" OR subject:"opportunity")'
            
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            email_data = []
            
            for msg in messages:
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                email_body = self._extract_email_body(message)
                email_data.append({
                    'id': msg['id'],
                    'subject': self._get_header(message, 'Subject'),
                    'from': self._get_header(message, 'From'),
                    'body': email_body
                })
            
            return email_data
        except HttpError as error:
            print(f"Error fetching emails: {error}")
            return []
    
    def mark_as_read(self, message_id: str):
        """Mark an email as read."""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
        except HttpError as error:
            print(f"Error marking email as read: {error}")
    
    def _get_header(self, message, name):
        """Get header value from email."""
        headers = message['payload'].get('headers', [])
        for header in headers:
            if header['name'] == name:
                return header['value']
        return ""
    
    def _extract_email_body(self, message) -> str:
        """Extract text body from email."""
        body = ""
        payload = message.get('payload', {})
        
        if 'parts' in payload:
            for part in payload['parts']:
                mime_type = part.get('mimeType', '')
                body_data = part.get('body', {}).get('data', '')
                
                if mime_type == 'text/plain' and body_data:
                    body += base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                elif mime_type == 'text/html' and body_data:
                    html_content = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                    parser = HTMLTextExtractor()
                    parser.feed(html_content)
                    body += parser.get_text()
        else:
            # Simple message
            body_data = payload.get('body', {}).get('data', '')
            if body_data:
                body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
        
        return body

