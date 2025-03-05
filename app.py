import os
import pickle
from flask import Flask, redirect, url_for, request, session
from flask_session import Session
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Flask Setup
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management
app.config['SESSION_TYPE'] = 'filesystem'  # Store session data in files
Session(app)

# Google API Setup
SCOPES = ['openai', 'https://www.googleapis.com/auth/drive']
CLIENT_SECRETS_FILE = 'credentials.json'
REDIRECT_URI = '/oauth2callback'

# Dictionary to store user credentials (in-memory, use DB for production)
user_credentials = {}

def create_flow():
    """Create an OAuth 2.0 flow instance for Google authentication."""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=url_for('oauth2callback', _external=True)
    )
    return flow

@app.route('/')
def index():
    """Home page with 'Give Access' button."""
    if 'user_id' in session and session['user_id'] in user_credentials:
        return redirect(url_for('list_drive_files'))  # Redirect if user is already authenticated

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
    """Redirect user to Google authentication."""
    flow = create_flow()
    authorization_url, state = flow.authorization_url(prompt='consent')
    session['state'] = state
    return redirect(authorization_url)

@app.route(REDIRECT_URI)
def oauth2callback():
    """Handle OAuth 2.0 callback and store credentials."""
    flow = create_flow()
    try:
        # Fetch the token using the authorization response and state from session
        flow.fetch_token(
            authorization_response=request.url,
            state=session.get('state')
        )
    except Exception as e:
        app.logger.error(f"Error fetching token: {e}")
        return f"Error fetching token: {e}", 500

    creds = flow.credentials

    # Check if credentials and id_token are available
    if not creds or not creds.id_token:
        error_msg = "No valid credentials or ID token received. Please try again."
        app.logger.error(error_msg)
        return error_msg, 400

    # Safely extract the user id
    user_id = creds.id_token.get('sub')
    if not user_id:
        error_msg = "User ID not found in token."
        app.logger.error(error_msg)
        return error_msg, 400

    # Store credentials in-memory (consider a database for production use)
    user_credentials[user_id] = creds
    session['user_id'] = user_id  # Save user id in session

    return redirect(url_for('list_drive_files'))

@app.route('/files')
def list_drive_files():
    """Display authenticated user's Google Drive files."""
    user_id = session.get('user_id')
    
    if not user_id or user_id not in user_credentials:
        return redirect(url_for('index'))  # Redirect to login if not authenticated

    creds = user_credentials[user_id]
    print(creds)
    service = build('drive', 'v3', credentials=creds)

    results = service.files().list(pageSize=10, fields="files(id, name)").execute()
    files = results.get('files', [])

    output = '<h1>Your Google Drive Files:</h1>'
    output += '<ul>'
    for file in files:
        output += f'<li>{file["name"]} (ID: {file["id"]})</li>'
    output += '</ul>'

    return output

@app.route('/logout')
def logout():
    """Log out the user."""
    user_id = session.pop('user_id', None)
    if user_id and user_id in user_credentials:
        del user_credentials[user_id]  # Remove credentials from storage

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
