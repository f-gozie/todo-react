import requests
from .config import DEEZER_APP_ID, DEEZER_APP_SECRET, DEEZER_REDIRECT_URI

DEEZER_PERMISSIONS = "basic_access,manage_library,offline_access,email"
temporary_token_cache = {} 

def get_deezer_auth_url() -> str:
    auth_url = (
        f"https://connect.deezer.com/oauth/auth.php?"
        f"app_id={DEEZER_APP_ID}"
        f"&redirect_uri={DEEZER_REDIRECT_URI}"
        f"&perms={DEEZER_PERMISSIONS}"
        f"&response_type=code"
    )
    return auth_url

def get_deezer_access_token(code: str) -> str | None:
    token_url = "https://connect.deezer.com/oauth/access_token.php"
    params = { "app_id": DEEZER_APP_ID, "secret": DEEZER_APP_SECRET, "code": code, "output": "json" }
    try:
        response = requests.get(token_url, params=params)
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data.get('access_token')
        if access_token:
            temporary_token_cache['deezer_token_data'] = {'access_token': access_token, 'expires_in': token_data.get('expires')}
            temporary_token_cache['deezer_access_token'] = access_token
            return access_token
        else:
            print(f"Deezer token exchange error: 'access_token' not found. Response: {token_data}")
            return None
    except requests.RequestException as e:
        print(f"Error fetching Deezer access token: {e}")
        if hasattr(e, 'response') and e.response is not None: print(f"Response content: {e.response.content}")
        return None
    except ValueError as e: print(f"Error decoding JSON from Deezer token response: {e}"); return None

def add_liked_song(access_token: str, track_id: str) -> bool:
    """
    Adds a song to the current user's liked/favorite tracks on Deezer.
    Returns True on success, False on failure.
    """
    if not access_token or not track_id:
        print("Error: Deezer access_token or track_id not provided for add_liked_song.")
        return False
    
    url = f"https://api.deezer.com/user/me/tracks"
    params = {
        'access_token': access_token,
        'track_id': track_id
    }
    try:
        # Note: Deezer documentation says POST for adding tracks to user/me/tracks.
        # Some resources might show GET with songs_ids param, but that's usually for playlists.
        # For user favorites, it's typically POST with track_id.
        # The track_id should be passed as `songs` according to some docs for user/me/tracks (plural)
        # but most consistent is `track_id` for `/user/me/tracks` POST.
        # Let's try with `track_id` first as per common interpretation.
        # If it fails, check if `songs` (with the ID as a string) is expected.
        # Official doc: POST https://api.deezer.com/user/{user_id}/tracks?access_token=...&track_id=...
        # Using /user/me/tracks means user_id is inferred from token.
        
        response = requests.post(url, params={'access_token': access_token}, data={'track_id': track_id}) # Try track_id in data
        # Alternative if above fails: response = requests.post(url, params={'access_token': access_token, 'track_id': track_id})
        # Or: response = requests.post(url, params={'access_token': access_token, 'songs': track_id})
        
        response.raise_for_status() # Check for HTTP errors
        
        # Deezer API returns `true` (boolean) on success for this call, not JSON `{"status": true}`
        if response.text.lower() == 'true':
            print(f"Successfully added track {track_id} to Deezer liked songs.")
            return True
        else:
            print(f"Deezer API did not return true for adding track {track_id}. Response: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"Deezer API error while adding liked song {track_id}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Deezer error response: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred in Deezer add_liked_song for {track_id}: {e}")
    return False

def _deezer_paginated_request(url: str, access_token: str, params: dict = None) -> list:
    data_list = []
    if params is None: params = {}
    params['access_token'] = access_token
    current_url = url
    while current_url:
        try:
            response = requests.get(current_url, params=params if current_url == url else {'access_token': access_token})
            response.raise_for_status()
            json_response = response.json()
            if 'data' in json_response: data_list.extend(json_response['data'])
            elif isinstance(json_response, list): data_list.extend(json_response)
            if 'error' in json_response: print(f"Error from Deezer API at {current_url}: {json_response['error']}"); break
            current_url = json_response.get('next')
            params = {} 
        except requests.RequestException as e: print(f"Error during Deezer API request to {current_url}: {e}"); break
        except ValueError as e: print(f"Error decoding JSON from Deezer API response at {current_url}: {e}"); break
    return data_list

def get_deezer_user_info(access_token: str) -> dict | None:
    url = "https://api.deezer.com/user/me"
    try: response = requests.get(url, params={'access_token': access_token}); response.raise_for_status(); return response.json()
    except requests.RequestException as e: print(f"Error fetching Deezer user info: {e}"); return None
    except ValueError as e: print(f"Error decoding JSON from Deezer user info: {e}"); return None

def get_liked_songs(access_token: str) -> list:
    return _deezer_paginated_request("https://api.deezer.com/user/me/tracks", access_token)

def get_playlists(access_token: str) -> list:
    return _deezer_paginated_request("https://api.deezer.com/user/me/playlists", access_token)

def get_playlist_tracks(access_token: str, playlist_id: str) -> list:
    return _deezer_paginated_request(f"https://api.deezer.com/playlist/{playlist_id}/tracks", access_token)

if __name__ == '__main__':
    print("Deezer client module with add_liked_song.")
