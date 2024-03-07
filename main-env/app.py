from flask import Flask, request, session, redirect, url_for
import requests
import spotipy
import os
from dotenv import load_dotenv
from urllib.parse import urlencode

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a secret key for session management

# Environment variables
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')

@app.route('/')
def login():
    # Define the scopes your application requires
    scopes = 'user-read-private user-top-read'

    # Redirect user to Spotify authorization page
    auth_url = f'https://accounts.spotify.com/authorize?{urlencode({"client_id": CLIENT_ID, "response_type": "code", "redirect_uri": REDIRECT_URI, "scope": scopes, "show_dialog": "true"})}'
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    error = request.args.get('error')

    if error:
        return f"Error during authentication: {error}", 400

    # Exchange the code for an access token and refresh token
    token_response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }).json()

    access_token = token_response.get('access_token')
    refresh_token = token_response.get('refresh_token')

    if not access_token:
        return "Error fetching access token.", 400

    # Store the tokens in the session for later use
    session['access_token'] = access_token
    session['refresh_token'] = refresh_token

    # Redirect to another endpoint or return a response
    return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    """Fetch and display the current user's Spotify profile."""
    access_token = session.get('access_token')
    
    if not access_token or not test_access_token_validity(access_token):
        if not refresh_access_token():
            # Redirect to login if unable to refresh the access token
            return redirect(url_for('login'))

    # Create a Spotipy client with the refreshed or valid access token
    sp = spotipy.Spotify(auth=access_token)

    # Fetch the current user's profile
    try:
        user_profile = sp.current_user()
        # For demonstration, return the profile as JSON
        # In a real application, you might render a template here
        return jsonify(user_profile)
    except spotipy.SpotifyException as e:
        # Handle specific Spotipy exceptions (e.g., token expired) if needed
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Generic exception handling
        return jsonify({"error": "An error occurred while fetching profile."}), 500

if __name__ == '__main__':
    load_dotenv()  # Load environment variables from .env file
    app.run(port=8888)

def refresh_access_token():
    refresh_token = session.get('refresh_token')
    if not refresh_token:
        return False  # Handle the case where there is no refresh token

    response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }).json()

    access_token = response.get('access_token')

    if access_token:
        session['access_token'] = access_token
        return True
    else:
        return False

def test_access_token_validity(access_token):
    # Attempt a lightweight request with the current access token
    test_response = requests.get('https://api.spotify.com/v1/me', headers={
        'Authorization': f'Bearer {access_token}'
    })
    return test_response.ok  # Returns True if the status code is 200-399

