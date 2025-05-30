import json
import time
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials as GoogleCredentials
from google.auth.transport.requests import Request as GoogleAuthRequest
from .config import GOOGLE_OAUTH_CLIENT_SECRETS_FILE, YOUTUBE_REDIRECT_URI, YOUTUBE_SCOPES
from . import token_store
import logging

logger = logging.getLogger(__name__)
temporary_state_cache = {}

def create_youtube_flow() -> Flow:
    try: return Flow.from_client_secrets_file(client_secrets_file=GOOGLE_OAUTH_CLIENT_SECRETS_FILE, scopes=YOUTUBE_SCOPES, redirect_uri=YOUTUBE_REDIRECT_URI)
    except FileNotFoundError: logger.error(f"Google OAuth Client Secrets File not found at {GOOGLE_OAUTH_CLIENT_SECRETS_FILE}", exc_info=True); raise
    except Exception as e: logger.error(f"Error creating YouTube OAuth flow: {e}", exc_info=True); raise

def get_cached_youtube_token_data() -> dict | None:
    logger.debug("Attempting to load YouTube token data from store.")
    return token_store.load_tokens("youtube")

def save_youtube_token_data(credentials: GoogleCredentials) -> bool:
    logger.debug("Attempting to save YouTube token data to store.")
    if credentials:
        token_data_to_save = {"credentials_json": credentials.to_json()}
        return token_store.save_tokens("youtube", token_data_to_save)
    logger.warning("Attempted to save None as YouTube credentials.")
    return False

def delete_youtube_token_data() -> bool:
    logger.info("Attempting to delete YouTube token data from store.")
    return token_store.delete_tokens("youtube")

def get_youtube_client_service(cached_token_data: dict | None): # Renamed from get_youtube_client_service_util
    if not cached_token_data or "credentials_json" not in cached_token_data:
        logger.warning("YouTube: No cached credentials JSON found.")
        return None
    credentials_json_str = cached_token_data["credentials_json"]
    try:
        credentials_info = json.loads(credentials_json_str)
        loaded_scopes = credentials_info.get('scopes', YOUTUBE_SCOPES)
        if isinstance(loaded_scopes, str): loaded_scopes = loaded_scopes.split(' ')
        credentials = GoogleCredentials.from_authorized_user_info(credentials_info, scopes=loaded_scopes)
        if credentials.expired and credentials.refresh_token:
            logger.info("YouTube: Credentials expired, attempting refresh...")
            try:
                credentials.refresh(GoogleAuthRequest())
                if save_youtube_token_data(credentials): logger.info("YouTube: Successfully refreshed and saved new credentials.")
                else: logger.warning("YouTube: Failed to save refreshed credentials after successful refresh.")
            except Exception as refresh_exception:
                logger.error(f"YouTube: Failed to refresh token: {refresh_exception}", exc_info=True)
                delete_youtube_token_data(); return None
        logger.debug("YouTube client service initialized/refreshed.")
        return build('youtube', 'v3', credentials=credentials)
    except json.JSONDecodeError as e: logger.error(f"Error decoding YouTube credentials JSON: {e}", exc_info=True); return None
    except Exception as e: logger.error(f"Error creating YouTube client from credentials: {e}", exc_info=True); return None

def create_playlist(youtube_service, title: str, description: str = '', privacy_status: str = 'private') -> dict | None:
    if not all([youtube_service, title]): logger.error("YouTube service or title missing for create_playlist."); return None
    try:
        playlist_body = {"snippet": {"title": title, "description": description}, "status": {"privacyStatus": privacy_status}}
        playlist = youtube_service.playlists().insert(part="snippet,status", body=playlist_body).execute()
        logger.info(f"YouTube: Created playlist '{title}' (ID: {playlist['id']})")
        return playlist
    except HttpError as e: logger.error(f"YouTube API error creating playlist '{title}': {e._get_reason()}", exc_info=True); return None
    except Exception as e: logger.error(f"Unexpected error YouTube create_playlist '{title}': {e}", exc_info=True); return None

def add_liked_video(youtube_service, video_id: str) -> bool:
    if not youtube_service or not video_id: logger.error("YouTube service or video_id not provided for add_liked_video."); return False
    try:
        youtube_service.videos().rate(id=video_id, rating="like").execute()
        logger.info(f"YouTube: Liked video {video_id}.")
        return True
    except HttpError as e: logger.error(f"YouTube API HttpError liking video {video_id}: {e._get_reason()}", exc_info=True); return False

def add_video_to_playlist(youtube_service, playlist_id: str, video_id: str) -> dict | None:
    if not all([youtube_service, playlist_id, video_id]): logger.error("YouTube: Args missing for add_video_to_playlist."); return None
    try:
        playlist_item_body = {"snippet": {"playlistId": playlist_id, "resourceId": {"kind": "youtube#video", "videoId": video_id}}}
        playlist_item = youtube_service.playlistItems().insert(part="snippet", body=playlist_item_body).execute()
        logger.info(f"YouTube: Added video {video_id} to playlist {playlist_id}. Item ID: {playlist_item['id']}")
        return playlist_item
    except HttpError as e:
        reason = e._get_reason(); logger.error(f"YouTube API HttpError adding video {video_id} to playlist {playlist_id}: {reason}", exc_info=True)
        if e.resp.status == 409 : logger.info(f"YouTube: Video {video_id} likely already in playlist {playlist_id}."); return {"id": "already_exists"}
    except Exception as e: logger.error(f"Unexpected error YouTube add_video_to_playlist {video_id} to {playlist_id}: {e}", exc_info=True)
    return None

def _youtube_paginated_request(api_request_method, **kwargs):
    items = [];
    try:
        response = api_request_method(**kwargs).execute()
        items.extend(response.get('items', []))
        next_page_token = response.get('nextPageToken')
        while next_page_token:
            kwargs['pageToken'] = next_page_token
            response = api_request_method(**kwargs).execute()
            items.extend(response.get('items', []))
            next_page_token = response.get('nextPageToken')
    except HttpError as e:
        logger.error(f"YouTube API error during pagination for {api_request_method._methodName}: {e._get_reason()}", exc_info=True)
        if hasattr(e, 'resp') and e.resp.status in [401, 403]: raise
    return items

def get_liked_videos(youtube_service) -> list:
    logger.debug("Fetching YouTube liked videos.")
    try:
        channels_response = youtube_service.channels().list(part="contentDetails", mine=True).execute()
        if not channels_response.get("items"): logger.warning("No channels found for YouTube user."); return []
        likes_playlist_id = channels_response["items"][0]["contentDetails"]["relatedPlaylists"]["likes"]
        return _youtube_paginated_request(youtube_service.playlistItems().list, part="snippet,contentDetails", playlistId=likes_playlist_id, maxResults=50)
    except (HttpError, KeyError) as e: logger.error(f"YouTube API error get_liked_videos: {e}", exc_info=True); return []

def get_playlists(youtube_service) -> list:
    logger.debug("Fetching YouTube playlists.")
    return _youtube_paginated_request(youtube_service.playlists().list, part="snippet,contentDetails", mine=True, maxResults=50)

def get_playlist_items(youtube_service, playlist_id: str) -> list:
    logger.debug(f"Fetching YouTube items for playlist {playlist_id}.")
    return _youtube_paginated_request(youtube_service.playlistItems().list, part="snippet,contentDetails", playlistId=playlist_id, maxResults=50)

if __name__ == '__main__':
    # from logging_config import setup_logging
    # setup_logging(debug_mode=True)
    logger.info("YouTube client module using token_store and logging.")
