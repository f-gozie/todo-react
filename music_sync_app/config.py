import os
from dotenv import load_dotenv

load_dotenv()

# Spotify API Credentials
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# Apple Music API Credentials
APPLE_TEAM_ID = "YOUR_APPLE_TEAM_ID"
APPLE_KEY_ID = "YOUR_APPLE_KEY_ID"
APPLE_PRIVATE_KEY_PATH = "PATH_TO_YOUR_APPLE_PRIVATE_KEY_FILE.p8"

# Deezer API Credentials
DEEZER_APP_ID = os.getenv("DEEZER_APP_ID")
DEEZER_APP_SECRET = os.getenv("DEEZER_APP_SECRET")
DEEZER_REDIRECT_URI = os.getenv("DEEZER_REDIRECT_URI")

GOOGLE_OAUTH_CLIENT_SECRETS_FILE = os.getenv("GOOGLE_OAUTH_CLIENT_SECRETS_FILE", "client_secret_youtube.json")
YOUTUBE_REDIRECT_URI = os.getenv("YOUTUBE_REDIRECT_URI")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# YouTube OAuth scopes
YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube"
]
