import json
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials as GoogleCredentials
from .config import GOOGLE_OAUTH_CLIENT_SECRETS_FILE, YOUTUBE_REDIRECT_URI, YOUTUBE_SCOPES 

temporary_token_cache = {} 
temporary_state_cache = {} 

def create_youtube_flow() -> Flow:
    try:
        return Flow.from_client_secrets_file(
            client_secrets_file=GOOGLE_OAUTH_CLIENT_SECRETS_FILE,
            scopes=YOUTUBE_SCOPES,
            redirect_uri=YOUTUBE_REDIRECT_URI
        )
    except FileNotFoundError: print(f"ERROR: Google OAuth Client Secrets File not found at {GOOGLE_OAUTH_CLIENT_SECRETS_FILE}"); raise
    except Exception as e: print(f"Error creating YouTube OAuth flow: {e}"); raise

def get_youtube_client_service(credentials_json_str: str):
    if not credentials_json_str: raise ValueError("Credentials JSON string is empty.")
    try:
        credentials_info = json.loads(credentials_json_str)
        loaded_scopes = credentials_info.get('scopes', YOUTUBE_SCOPES)
        if isinstance(loaded_scopes, str): loaded_scopes = loaded_scopes.split(' ')
        credentials = GoogleCredentials.from_authorized_user_info(credentials_info, scopes=loaded_scopes)
        if credentials.expired and credentials.refresh_token:
            try:
                from google.auth.transport.requests import Request as GoogleAuthRequest
                credentials.refresh(GoogleAuthRequest())
                temporary_token_cache['youtube_credentials'] = credentials.to_json()
            except Exception as refresh_exception:
                print(f"Failed to refresh YouTube token: {refresh_exception}")
        return build('youtube', 'v3', credentials=credentials)
    except json.JSONDecodeError as e: print(f"Error decoding credentials JSON: {e}"); raise
    except Exception as e: print(f"Error creating YouTube client from credentials: {e}"); raise

def add_liked_video(youtube_service, video_id: str) -> bool:
    """
    Adds a "like" rating to a YouTube video.
    Returns True on success, False on failure.
    """
    if not youtube_service or not video_id:
        print("Error: YouTube service or video_id not provided for add_liked_video.")
        return False
    try:
        youtube_service.videos().rate(id=video_id, rating="like").execute()
        print(f"Successfully liked YouTube video {video_id}.")
        return True
    except HttpError as e:
        print(f"YouTube API HttpError while liking video {video_id}: {e.resp.status} - {e._get_reason()}")
        # Common errors: 403 (Forbidden) if already liked or other permission issue, 404 (Not Found) if video_id is invalid.
    except Exception as e:
        print(f"An unexpected error occurred in YouTube add_liked_video for {video_id}: {e}")
    return False

def _youtube_paginated_request(api_request_method, **kwargs):
    all_items = []
    try:
        response = api_request_method(**kwargs).execute()
        all_items.extend(response.get('items', []))
        next_page_token = response.get('nextPageToken')
        while next_page_token:
            kwargs['pageToken'] = next_page_token
            response = api_request_method(**kwargs).execute()
            all_items.extend(response.get('items', []))
            next_page_token = response.get('nextPageToken')
    except HttpError as e:
        print(f"YouTube API error: {e.resp.status} - {e._get_reason()}")
        if e.resp.status in [401, 403]: raise 
    return all_items

def get_liked_videos(youtube_service) -> list:
    try:
        channels_response = youtube_service.channels().list(part="contentDetails", mine=True).execute()
        if not channels_response.get("items"): print("No channels found for the user."); return []
        likes_playlist_id = channels_response["items"][0]["contentDetails"]["relatedPlaylists"]["likes"]
        return _youtube_paginated_request(
            youtube_service.playlistItems().list,
            part="snippet,contentDetails", playlistId=likes_playlist_id, maxResults=50
        )
    except HttpError as e: print(f"YouTube API error in get_liked_videos: {e}");
    except KeyError: print("Could not find 'likes' playlist ID."); return []
    return []


def get_playlists(youtube_service) -> list:
    return _youtube_paginated_request(
        youtube_service.playlists().list, part="snippet,contentDetails", mine=True, maxResults=50
    )

def get_playlist_items(youtube_service, playlist_id: str) -> list:
    return _youtube_paginated_request(
        youtube_service.playlistItems().list, part="snippet,contentDetails", playlistId=playlist_id, maxResults=50
    )

if __name__ == '__main__':
    print("YouTube client module with add_liked_video.")
