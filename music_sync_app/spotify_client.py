import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI
from . import token_store
import logging

logger = logging.getLogger(__name__)
SCOPES = "user-library-read user-library-modify playlist-read-private playlist-modify-public playlist-modify-private"

def create_spotify_oauth() -> SpotifyOAuth:
    return SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=SPOTIFY_REDIRECT_URI, scope=SCOPES, cache_path=None)

def get_cached_spotify_token_info() -> dict | None:
    logger.debug("Attempting to load Spotify token info from store.")
    return token_store.load_tokens("spotify")

def save_spotify_token_info(token_info: dict) -> bool:
    logger.debug("Attempting to save Spotify token info to store.")
    if token_info: return token_store.save_tokens("spotify", token_info)
    logger.warning("Attempted to save None as Spotify token_info.")
    return False

def delete_spotify_token_info() -> bool:
    logger.info("Attempting to delete Spotify token info from store.")
    return token_store.delete_tokens("spotify")

def get_spotify_client(token_info: dict) -> spotipy.Spotify | None:
    if not token_info or "access_token" not in token_info:
        logger.error("Invalid or missing token_info for get_spotify_client.")
        return None
    logger.debug("Initializing Spotipy client with provided token_info.")
    return spotipy.Spotify(auth=token_info.get('access_token'))

def create_playlist(sp_client: spotipy.Spotify, user_id: str, playlist_name: str, public: bool = False, collaborative: bool = False, description: str = '') -> dict | None:
    if not all([sp_client, user_id, playlist_name]):
        logger.error("Spotify client, user_id, or playlist_name not provided for create_playlist.")
        return None
    try:
        playlist = sp_client.user_playlist_create(user=user_id, name=playlist_name, public=public, collaborative=collaborative, description=description)
        logger.info(f"Spotify: Created playlist '{playlist_name}' (ID: {playlist['id']})")
        return playlist
    except spotipy.SpotifyException as e: logger.error(f"Spotify API error creating playlist '{playlist_name}': {e}", exc_info=True)
    except Exception as e: logger.error(f"Unexpected error Spotify create_playlist '{playlist_name}': {e}", exc_info=True)
    return None

def add_liked_song(sp_client: spotipy.Spotify, track_id: str) -> bool:
    if not sp_client or not track_id: logger.error("Spotify client or track_id not provided for add_liked_song."); return False
    try:
        sp_client.current_user_saved_tracks_add(tracks=[track_id])
        logger.info(f"Spotify: Added liked song {track_id}.")
        return True
    except spotipy.SpotifyException as e: logger.error(f"Spotify API error adding liked song {track_id}: {e}", exc_info=True)
    except Exception as e: logger.error(f"Unexpected error Spotify add_liked_song {track_id}: {e}", exc_info=True)
    return False

def add_tracks_to_playlist(sp_client: spotipy.Spotify, playlist_id: str, track_ids: list[str]) -> bool:
    if not all([sp_client, playlist_id, track_ids]): logger.error("Spotify client, playlist_id, or track_ids not provided."); return False
    success = True
    for i in range(0, len(track_ids), 100):
        batch = track_ids[i:i + 100]
        try:
            sp_client.playlist_add_items(playlist_id, batch)
            logger.info(f"Spotify: Added {len(batch)} tracks to playlist {playlist_id}.")
        except spotipy.SpotifyException as e: logger.error(f"Spotify API error adding tracks to playlist {playlist_id} (batch starting {i}): {e}", exc_info=True); success = False
        except Exception as e: logger.error(f"Unexpected error Spotify add_tracks_to_playlist {playlist_id} (batch starting {i}): {e}", exc_info=True); success = False
    return success

def get_liked_songs(sp_client: spotipy.Spotify) -> list:
    items = [];
    try:
        results = sp_client.current_user_saved_tracks(limit=50)
        while results:
            items.extend(item['track'] for item in results['items'] if item.get('track'))
            if results['next']: results = sp_client.next(results)
            else: results = None
    except spotipy.SpotifyException as e: logger.error(f"Spotify API error fetching liked songs: {e}", exc_info=True)
    except Exception as e: logger.error(f"Unexpected error fetching Spotify liked songs: {e}", exc_info=True)
    return items

def get_playlists(sp_client: spotipy.Spotify) -> list:
    items = [];
    try:
        results = sp_client.current_user_playlists(limit=50)
        while results:
            items.extend(results['items'])
            if results['next']: results = sp_client.next(results)
            else: results = None
    except spotipy.SpotifyException as e: logger.error(f"Spotify API error fetching playlists: {e}", exc_info=True)
    except Exception as e: logger.error(f"Unexpected error fetching Spotify playlists: {e}", exc_info=True)
    return items

def get_playlist_tracks(sp_client: spotipy.Spotify, playlist_id: str) -> list:
    items = [];
    try:
        results = sp_client.playlist_items(playlist_id, limit=100, fields="items(track(id,name,artists,album(name),external_ids)),next")
        while results:
            items.extend(item['track'] for item in results['items'] if item.get('track'))
            if results['next']: results = sp_client.next(results)
            else: results = None
    except spotipy.SpotifyException as e: logger.error(f"Spotify API error fetching playlist tracks for {playlist_id}: {e}", exc_info=True)
    except Exception as e: logger.error(f"Unexpected error fetching Spotify playlist tracks for {playlist_id}: {e}", exc_info=True)
    return items

if __name__ == '__main__':
    # Minimal logging for standalone test, assuming logging_config is adjacent for testing
    # from logging_config import setup_logging
    # setup_logging(debug_mode=True)
    logger.info("Spotify client module using token_store and logging.")
