from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle

# Define API Scopes (Full Access)
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_drive():
    creds = None
    # Load existing credentials if available
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, authenticate the user
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Specify the path to your credentials.json file
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)

            # This will prompt you to select a Google account to authenticate with
            creds = flow.run_local_server(port=0)  # Port 0 automatically selects an available port

        # Save the credentials for future use (to avoid re-authentication)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)
