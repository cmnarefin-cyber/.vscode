import os
import json
import requests
from flask import Flask, request, redirect, session, url_for
import secrets
import logging
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

# --- CONFIGURATION ---
# Note: Set these environment variables (or put them in a .env file):
# GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET. Register an OAuth app at
# https://github.com/settings/developers to get these values.
CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:5000/callback")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


@app.route('/')
def index():
    """Initial page with a login button."""
    if not CLIENT_ID or not CLIENT_SECRET:
        return ("<h1>GitHub App Auth</h1>" 
                "<p style='color:darkred'>Error: GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET must be set.</p>"
                "<p>See .env.example for details.</p>"), 500

    # Create and persist a random state for CSRF protection
    state = secrets.token_hex(16)
    session['oauth_state'] = state

    github_auth_url = (
        f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&state={state}&scope=read:user"
    )
    return f'<h1>GitHub App Auth</h1><a href="{github_auth_url}">Login with GitHub</a>'


@app.route('/callback')
def callback():
    """OAuth callback handler to exchange code for token."""
    code = request.args.get('code')

    # Basic validations
    if not code:
        return "Error: No code received from GitHub.", 400

    received_state = request.args.get('state')
    expected_state = session.pop('oauth_state', None)
    if not expected_state or received_state != expected_state:
        return "Error: invalid state parameter (possible CSRF).", 400

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
        response = requests.post(token_url, data=payload, headers=headers, timeout=10)
        response.raise_for_status()
        token_data = response.json()

        if "access_token" not in token_data:
            return f"Error exchanging code: {token_data.get('error_description', token_data)}", 400

        access_token = token_data["access_token"]
        session['access_token'] = access_token

        return redirect(url_for('user_info'))

    except Exception as e:
        logger.exception("Failed to exchange token")
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
        response = requests.get(user_url, headers=headers, timeout=10)
        response.raise_for_status()
        user_data = response.json()

        pretty = json.dumps(user_data, indent=2)
        return f"""
        <h1>Authenticated Successfully</h1>
        <p>Logged in as: <strong>{user_data.get('login')}</strong></p>
        <p>User Access Token: <code>{token[:10]}...[HIDDEN]</code></p>
        <hr>
        <h3>Your GitHub Profile:</h3>
        <pre>{pretty}</pre>
        <br>
        <a href="/logout">Logout</a>
        """
    except Exception as e:
        logger.exception("Failed to fetch user info")
        return f"Failed to fetch user info: {e}", 500


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


if __name__ == "__main__":
    print("[*] Starting GitHub App Auth server on http://localhost:5000")
    print("[!] Ensure your GitHub App Callback URL is set to: http://localhost:5000/callback")
    app.run(port=5000, debug=True)
