import os
import requests
from flask import Flask, request, redirect, session, url_for
import secrets
import logging

# --- CONFIGURATION ---
# Note: You MUST update these with your GitHub App credentials from:
# https://github.com/settings/apps/YOUR_APP_NAME
CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "YOUR_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "YOUR_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:5000/callback"

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route('/')
def index():
    """Initial page with a login button."""
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&state={session.get('state', secrets.token_hex(8))}"
    )
    session['state'] = secrets.token_hex(8)
    return f'<h1>GitHub App Auth</h1><a href="{github_auth_url}">Login with GitHub</a>'

@app.route('/callback')
def callback():
    """OAuth callback handler to exchange code for token."""
    code = request.args.get('code')
    state = request.args.get('state')

    # Basic state validation (can be more robust)
    if not code:
        return "Error: No code received from GitHub.", 400

    # Exchange the code for a User Access Token
    token_url = "https://github.com/login/oauth/access_token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    headers = {"Accept": "application/json"}

    try:
        response = requests.post(token_url, json=payload, headers=headers)
        response.raise_for_status()
        token_data = response.json()
        
        if "access_token" not in token_data:
            return f"Error exchanging code: {token_data.get('error_description', 'Unknown error')}", 400

        access_token = token_data["access_token"]
        session['access_token'] = access_token
        
        return redirect(url_for('user_info'))

    except Exception as e:
        logger.error(f"Failed to exchange token: {e}")
        return f"Authentication failed: {e}", 500

@app.route('/user')
def user_info():
    """Fetches user info using the generated User Access Token."""
    token = session.get('access_token')
    if not token:
        return redirect(url_for('index'))

    # API Request on behalf of the user
    user_url = "https://api.github.com/user"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    try:
        response = requests.get(user_url, headers=headers)
        response.raise_for_status()
        user_data = response.json()
        
        return f"""
        <h1>Authenticated Successfully</h1>
        <p>Logged in as: <strong>{user_data.get('login')}</strong></p>
        <p>User Access Token: <code>{token[:10]}...[HIDDEN]</code></p>
        <hr>
        <h3>Your GitHub Profile:</h3>
        <pre>{requests.utils.json.dumps(user_data, indent=2)}</pre>
        <br>
        <a href="/logout">Logout</a>
        """
    except Exception as e:
        return f"Failed to fetch user info: {e}", 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    print("[*] Starting GitHub App Auth server on http://localhost:5000")
    print("[!] Ensure your GitHub App Callback URL is set to: http://localhost:5000/callback")
    app.run(port=5000, debug=True)
