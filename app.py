import os
import pickle
from flask import Flask, redirect, url_for, request, session
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Setup
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# Define API Scopes
SCOPES = ['https://www.googleapis.com/auth/drive']

# Path to the credentials.json file
CLIENT_SECRETS_FILE = 'credentials.json'

# Redirect URI for OAuth
REDIRECT_URI = '/oauth2callback'

# Authentication Flow Setup
def create_flow():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    return flow

@app.route('/')
def index():
    """Display the page with the 'Give Access' button."""
    return '''
        <html>
            <body>
                <h1>Google Drive Access</h1>
                <button onclick="window.location.href='/authorize'">Give Access</button>
            </body>
        </html>
    '''

@app.route('/authorize')
def authorize():
    """Redirect user to the Google authentication page."""
    flow = create_flow()
    authorization_url, state = flow.authorization_url(prompt='consent')
    session['state'] = state
    return redirect(authorization_url)

@app.route(REDIRECT_URI)
def oauth2callback():
    """Handle the OAuth 2.0 callback."""
    flow = create_flow()
    flow.fetch_token(
        authorization_response=request.url,
        client_secret=CLIENT_SECRETS_FILE,
        state=session['state'],
    )

    # Save the credentials for the session
    creds = flow.credentials
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

    # Build the Google Drive API service
    service = build('drive', 'v3', credentials=creds)

    # List the first 10 files in the Google Drive
    results = service.files().list(pageSize=10, fields="files(id, name)").execute()
    files = results.get('files', [])

    if not files:
        return 'No files found.'

    # Display the files
    output = '<h1>Your Google Drive Files:</h1>'
    output += '<ul>'
    for file in files:
        output += f'<li>{file["name"]} (ID: {file["id"]})</li>'
    output += '</ul>'

    return output

if __name__ == '__main__':
    app.run(debug=True)
