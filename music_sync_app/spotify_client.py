import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

SCOPES = "user-library-read user-library-modify playlist-read-private playlist-modify-private playlist-modify-public"
temporary_token_cache = {} 

def create_spotify_oauth() -> SpotifyOAuth:
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPES,
        cache_path=None 
    )

def get_spotify_client(token_info: dict) -> spotipy.Spotify:
    if not token_info or "access_token" not in token_info:
        raise ValueError("Invalid or missing token_info provided.")
    return spotipy.Spotify(auth=token_info.get('access_token'))

def add_liked_song(sp_client: spotipy.Spotify, track_id: str) -> bool:
    """
    Adds a song to the current user's liked/saved tracks on Spotify.
    Returns True on success, False on failure.
    """
    if not sp_client or not track_id:
        print("Error: Spotify client or track_id not provided for add_liked_song.")
        return False
    try:
        sp_client.current_user_saved_tracks_add(tracks=[track_id])
        print(f"Successfully added track {track_id} to Spotify liked songs.")
        return True
    except spotipy.SpotifyException as e:
        print(f"Spotify API error while adding liked song {track_id}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in Spotify add_liked_song for {track_id}: {e}")
    return False

def get_liked_songs(sp_client: spotipy.Spotify) -> list:
    all_liked_songs = []
    try:
        results = sp_client.current_user_saved_tracks(limit=50)
        if results and results.get('items'):
            for item in results['items']:
                if item.get('track'): all_liked_songs.append(item['track'])
            while results and results.get('next'):
                results = sp_client.next(results)
                if results and results.get('items'):
                    for item in results['items']:
                        if item.get('track'): all_liked_songs.append(item['track'])
    except spotipy.SpotifyException as e:
        print(f"Spotify API error while fetching liked songs: {e}")
        return all_liked_songs 
    return all_liked_songs

def get_playlists(sp_client: spotipy.Spotify) -> list:
    all_playlists = []
    try:
        results = sp_client.current_user_playlists(limit=50)
        if results and results.get('items'): all_playlists.extend(results['items'])
        while results and results.get('next'):
            results = sp_client.next(results)
            if results and results.get('items'): all_playlists.extend(results['items'])
    except spotipy.SpotifyException as e:
        print(f"Spotify API error while fetching playlists: {e}")
    return all_playlists

def get_playlist_tracks(sp_client: spotipy.Spotify, playlist_id: str) -> list:
    all_playlist_tracks = []
    try:
        results = sp_client.playlist_items(playlist_id, limit=100, fields="items(track(id,name,artists,album(name),external_ids)),next")
        if results and results.get('items'):
            for item in results['items']:
                if item.get('track'): all_playlist_tracks.append(item['track'])
            while results and results.get('next'):
                results = sp_client.next(results)
                if results and results.get('items'):
                    for item in results['items']:
                        if item.get('track'): all_playlist_tracks.append(item['track'])
    except spotipy.SpotifyException as e:
        print(f"Spotify API error while fetching playlist tracks for {playlist_id}: {e}")
    return all_playlist_tracks

if __name__ == '__main__':
    # ... (existing __main__ for testing, if any)
    print("Spotify client module with add_liked_song.")

def create_playlist_on_spotify(sp_client: spotipy.Spotify, name: str, description: str = "", public: bool = False) -> str | None:
    """
    Creates a new playlist on Spotify for the current user.
    Returns the playlist ID on success, None on failure.
    """
    if not sp_client or not name:
        print("Error: Spotify client or playlist name not provided for create_playlist.")
        return None
    
    try:
        # Get current user to create playlist
        user = sp_client.current_user()
        user_id = user.get('id')
        if not user_id:
            print("Error: Could not get current user ID from Spotify.")
            return None
        
        # Create the playlist
        playlist = sp_client.user_playlist_create(
            user=user_id,
            name=name,
            public=public,
            collaborative=False,
            description=description
        )
        
        if playlist and playlist.get('id'):
            print(f"Successfully created Spotify playlist '{name}' with ID: {playlist['id']}")
            return playlist['id']
        else:
            print(f"Error: Failed to create Spotify playlist '{name}' - no ID returned")
            return None
            
    except spotipy.SpotifyException as e:
        print(f"Spotify API error while creating playlist '{name}': {e}")
    except Exception as e:
        print(f"Unexpected error occurred while creating Spotify playlist '{name}': {e}")
    
    return None


def add_track_to_spotify_playlist(sp_client: spotipy.Spotify, playlist_id: str, track_id: str) -> bool:
    """
    Adds a track to a specific Spotify playlist.
    Returns True on success, False on failure.
    """
    if not sp_client or not playlist_id or not track_id:
        print("Error: Spotify client, playlist_id, or track_id not provided for add_track_to_playlist.")
        return False
    
    try:
        # Add track to playlist
        sp_client.playlist_add_items(playlist_id, [track_id])
        print(f"Successfully added track {track_id} to Spotify playlist {playlist_id}")
        return True
        
    except spotipy.SpotifyException as e:
        print(f"Spotify API error while adding track {track_id} to playlist {playlist_id}: {e}")
    except Exception as e:
        print(f"Unexpected error occurred while adding track {track_id} to Spotify playlist {playlist_id}: {e}")
    
    return False
