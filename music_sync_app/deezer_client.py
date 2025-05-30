import requests
from .config import DEEZER_APP_ID, DEEZER_APP_SECRET, DEEZER_REDIRECT_URI
from . import token_store
import logging

logger = logging.getLogger(__name__)
DEEZER_PERMISSIONS = "basic_access,manage_library,offline_access,email"

def get_deezer_auth_url() -> str:
    return (f"https://connect.deezer.com/oauth/auth.php?app_id={DEEZER_APP_ID}&redirect_uri={DEEZER_REDIRECT_URI}&perms={DEEZER_PERMISSIONS}&response_type=code")

def get_cached_deezer_token_data() -> dict | None:
    logger.debug("Attempting to load Deezer token data from store.")
    return token_store.load_tokens("deezer")

def save_deezer_token_data(token_data: dict) -> bool:
    logger.debug("Attempting to save Deezer token data to store.")
    if token_data and 'access_token' in token_data:
        return token_store.save_tokens("deezer", token_data)
    logger.warning("Attempted to save invalid or None as Deezer token_data.")
    return False

def delete_deezer_token_data() -> bool:
    logger.info("Attempting to delete Deezer token data from store.")
    return token_store.delete_tokens("deezer")

def get_deezer_access_token_util(code: str) -> dict | None: # Renamed from get_deezer_access_token to avoid conflict if used elsewhere
    logger.info(f"Attempting to get Deezer access token with code: {code[:10]}...") # Log part of code
    params = { "app_id": DEEZER_APP_ID, "secret": DEEZER_APP_SECRET, "code": code, "output": "json" }
    try:
        response = requests.get("https://connect.deezer.com/oauth/access_token.php", params=params)
        response.raise_for_status()
        token_data = response.json()
        if 'expires' in token_data and 'expires_in' not in token_data :
            token_data['expires_in'] = token_data.pop('expires')
        if token_data.get('access_token'):
            if save_deezer_token_data(token_data): logger.info(f"Deezer: Token data saved successfully.")
            else: logger.warning(f"Deezer: Failed to save token data.")
            return token_data
        else:
            logger.error(f"Deezer token exchange error: 'access_token' not found. Response: {token_data}")
            return None
    except requests.RequestException as e: logger.error(f"Deezer API error in get_deezer_access_token: {e}", exc_info=True); return None
    except ValueError as e: logger.error(f"JSON decoding error in Deezer get_deezer_access_token: {e}", exc_info=True); return None # JSON decode error

def create_playlist(access_token: str, title: str) -> str | None:
    if not access_token or not title: logger.error("Deezer access_token or title not provided for create_playlist."); return None
    params = {'access_token': access_token, 'title': title}
    try:
        response = requests.post("https://api.deezer.com/user/me/playlists", params=params)
        response.raise_for_status(); playlist_data = response.json(); playlist_id = playlist_data.get('id')
        if playlist_id: logger.info(f"Deezer: Created playlist '{title}' (ID: {playlist_id})"); return str(playlist_id)
        else: logger.error(f"Deezer API no ID for created playlist '{title}': {playlist_data}"); return None
    except requests.RequestException as e: logger.error(f"Deezer API error creating playlist '{title}': {e}", exc_info=True); return None
    except ValueError as e: logger.error(f"JSON error Deezer create_playlist '{title}': {e}", exc_info=True); return None


def add_liked_song(access_token: str, track_id: str) -> bool:
    if not access_token or not track_id: logger.error("Deezer access_token or track_id not provided."); return False
    try:
        response = requests.post(f"https://api.deezer.com/user/me/tracks", params={'access_token': access_token, 'track_id': str(track_id)})
        response.raise_for_status()
        if response.text.lower() == 'true': logger.info(f"Deezer: Added liked song {track_id}."); return True
        else: logger.warning(f"Deezer: Failed to add liked song {track_id}, response: {response.text}"); return False
    except requests.RequestException as e: logger.error(f"Deezer API error adding liked song {track_id}: {e}", exc_info=True); return False

def add_tracks_to_playlist(access_token: str, playlist_id: str, track_ids: list[str]) -> bool:
    if not all([access_token, playlist_id, track_ids]): logger.error("Deezer: Args missing for add_tracks_to_playlist."); return False
    songs_param = ",".join(map(str, track_ids))
    params = {'access_token': access_token, 'songs': songs_param}
    try:
        response = requests.post(f"https://api.deezer.com/playlist/{playlist_id}/tracks", params=params)
        response.raise_for_status()
        if response.text.lower() == 'true': logger.info(f"Deezer: Added {len(track_ids)} tracks to playlist {playlist_id}."); return True
        else: logger.warning(f"Deezer API failed adding tracks to playlist {playlist_id}. Response: {response.text}"); return False
    except requests.RequestException as e: logger.error(f"Deezer API error adding tracks to playlist {playlist_id}: {e}", exc_info=True); return False

def _deezer_paginated_request(url: str, access_token: str, params: dict = None) -> list:
    items = [];
    if params is None: params = {}
    current_url = url; first_request = True
    while current_url:
        request_params = params.copy() if first_request else {}
        request_params['access_token'] = access_token
        first_request = False
        try:
            response = requests.get(current_url, params=request_params)
            response.raise_for_status(); json_response = response.json()
            if 'data' in json_response: items.extend(json_response['data'])
            elif isinstance(json_response, list) and current_url == url : items.extend(json_response)
            if 'error' in json_response: logger.error(f"Error from Deezer API {current_url}: {json_response['error']}"); break
            current_url = json_response.get('next')
        except (requests.RequestException, ValueError) as e: logger.error(f"Error Deezer paginated request {current_url}: {e}", exc_info=True); break
    return items

def get_deezer_user_info(access_token: str) -> dict | None: # Renamed from get_deezer_user_info_util
    logger.debug("Fetching Deezer user info.")
    try:
        response = requests.get("https://api.deezer.com/user/me", params={'access_token': access_token})
        response.raise_for_status(); return response.json()
    except (requests.RequestException, ValueError) as e: logger.error(f"Error Deezer get_user_info: {e}", exc_info=True); return None

def get_liked_songs(access_token: str) -> list:
    logger.debug("Fetching Deezer liked songs.")
    return _deezer_paginated_request("https://api.deezer.com/user/me/tracks", access_token)
def get_playlists(access_token: str) -> list:
    logger.debug("Fetching Deezer playlists.")
    return _deezer_paginated_request("https://api.deezer.com/user/me/playlists", access_token)
def get_playlist_tracks(access_token: str, playlist_id: str) -> list:
    logger.debug(f"Fetching Deezer tracks for playlist {playlist_id}.")
    return _deezer_paginated_request(f"https://api.deezer.com/playlist/{playlist_id}/tracks", access_token)

if __name__ == '__main__':
    # from logging_config import setup_logging
    # setup_logging(debug_mode=True)
    logger.info("Deezer client module using token_store and logging.")
