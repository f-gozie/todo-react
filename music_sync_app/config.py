import os
from dotenv import load_dotenv
from typing import Optional
import logging

load_dotenv()

# --- Spotify Configuration ---
SPOTIFY_CLIENT_ID: str = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET: str = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI: str = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8000/auth/spotify/callback")

# Apple Music API Credentials
APPLE_TEAM_ID = "YOUR_APPLE_TEAM_ID"
APPLE_KEY_ID = "YOUR_APPLE_KEY_ID"
APPLE_PRIVATE_KEY_PATH = "PATH_TO_YOUR_APPLE_PRIVATE_KEY_FILE.p8"

# --- Google/YouTube Configuration ---
GOOGLE_OAUTH_CLIENT_SECRETS_FILE: str = os.getenv("GOOGLE_OAUTH_CLIENT_SECRETS_FILE", "client_secret_youtube.json")
YOUTUBE_REDIRECT_URI: str = os.getenv("YOUTUBE_REDIRECT_URI", "http://localhost:8000/auth/youtube/callback")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# YouTube OAuth scopes
YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube"
]

# --- Security Configuration ---
SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

# --- Application Configuration ---
DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE: str = os.getenv("LOG_FILE", "music_sync_app.log")

# --- Logging Configuration ---
def setup_logging():
    """Set up logging configuration for the application."""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure logging
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # File handler
    file_handler = logging.FileHandler(f"logs/{LOG_FILE}")
    file_handler.setFormatter(logging.Formatter(log_format))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # Root logger configuration
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        handlers=[file_handler, console_handler],
        format=log_format
    )
    
    # Reduce noise from external libraries in production
    if not DEBUG:
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("googleapiclient").setLevel(logging.WARNING)

# Initialize logging
setup_logging()

# Get logger for this module
logger = logging.getLogger(__name__)

# --- Session Management Configuration ---
SESSION_LIFETIME_HOURS: int = int(os.getenv("SESSION_LIFETIME_HOURS", "24"))
TOKEN_REFRESH_BUFFER_MINUTES: int = int(os.getenv("TOKEN_REFRESH_BUFFER_MINUTES", "10"))
