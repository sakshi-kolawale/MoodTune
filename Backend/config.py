import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:5173/callback")

# Print credentials check
print("=" * 50)
print("SPOTIFY CREDENTIALS CHECK:")
print("=" * 50)
print("SPOTIFY_CLIENT_ID:", SPOTIFY_CLIENT_ID)
print("SPOTIFY_CLIENT_SECRET:", "SET" if SPOTIFY_CLIENT_SECRET else "MISSING!")
print("SPOTIFY_REDIRECT_URI:", SPOTIFY_REDIRECT_URI)
print("=" * 50)

# Check credentials
if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    raise ValueError("❌ Spotify credentials are missing! Please check your .env file.")

# Spotify OAuth scope
SPOTIFY_SCOPE = "user-library-read user-top-read playlist-modify-public playlist-modify-private user-read-private"

# Initialize Spotify clients
def get_public_spotify_client():
    """Get public Spotify client for non-authenticated requests"""
    return spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET
        )
    )

def get_oauth_manager():
    """Get Spotify OAuth manager"""
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE
    )

def get_user_spotify_client(access_token):
    """Get authenticated Spotify client for user-specific requests"""
    return spotipy.Spotify(auth=access_token)

def test_spotify_connection():
    """Test if we can connect to Spotify API"""
    try:
        # Create a temporary client to test connection
        test_sp = get_public_spotify_client()
        # Simple API call to test connection
        test_sp.search(q='test', type='track', limit=1)
        print("✅ Spotify API connection successful!")
        return True
    except Exception as e:
        print(f"❌ Spotify API connection failed: {str(e)}")
        return False

# Initialize public client on import
sp_public = get_public_spotify_client()
sp_oauth = get_oauth_manager()

# Test connection on import
test_spotify_connection()