# Spotify API Credentials
SPOTIFY_CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID"
SPOTIFY_CLIENT_SECRET = "YOUR_SPOTIFY_CLIENT_SECRET"
SPOTIFY_REDIRECT_URI = "http://localhost:8000/callback/spotify"

# Apple Music API Credentials
APPLE_TEAM_ID = "YOUR_APPLE_TEAM_ID"
APPLE_KEY_ID = "YOUR_APPLE_KEY_ID"
APPLE_PRIVATE_KEY_PATH = "PATH_TO_YOUR_APPLE_PRIVATE_KEY_FILE.p8"

# Deezer API Credentials
DEEZER_APP_ID = "YOUR_DEEZER_APP_ID"
DEEZER_APP_SECRET = "YOUR_DEEZER_APP_SECRET"
DEEZER_REDIRECT_URI = "http://localhost:8000/callback/deezer"

# YouTube Music / Google API Credentials
# GOOGLE_OAUTH_CLIENT_SECRETS_FILE should be the path to the client secrets JSON file
# downloaded from Google Cloud Console for your OAuth 2.0 Web Application client.
# Place this file in the 'music_sync_app' directory or provide the full path.
GOOGLE_OAUTH_CLIENT_SECRETS_FILE = "client_secret_youtube.json"
YOUTUBE_REDIRECT_URI = "http://localhost:8000/callback/youtube"
# YOUTUBE_API_KEY is generally used for non-OAuth access (e.g. server-to-server for public data)
# and is not directly used in the OAuth flow for user data. It can be kept if needed for other purposes.
YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY" # Optional, if still needed for other calls
