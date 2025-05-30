import unicodedata
import re
import spotipy
import requests
from googleapiclient.errors import HttpError
import logging # New import

# Import client modules to access their data fetching functions
from . import spotify_client as sp_client_module
from . import deezer_client as dz_client_module
from . import youtube_client as yt_client_module

logger = logging.getLogger(__name__)

# --- Normalization Helper ---
def normalize_text(text: str) -> str:
    if not text: return ""
    text = text.lower()
    text = re.sub(r'\([^)]*\)', '', text)
    text = re.sub(r'\[[^)]*\]', '', text)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'\b(a|an|the)\b', '', text)
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# --- Song Finder Functions ---
def find_song_on_spotify(sp_client: spotipy.Spotify, isrc: str = None, title: str = None, artist: str = None) -> str | None:
    if not sp_client: logger.error("Spotify client not provided to find_song_on_spotify."); return None
    logger.debug(f"Spotify: Searching for song - ISRC: {isrc}, Title: {title}, Artist: {artist}")
    try:
        if isrc:
            results = sp_client.search(q=f"isrc:{isrc}", type='track', limit=1)
            if results and results['tracks']['items']: logger.debug(f"Spotify: Found via ISRC."); return results['tracks']['items'][0]['id']
        if title: # Fallback or primary search if no ISRC
            query = f"track:{normalize_text(title)}"
            if artist: query += f" artist:{normalize_text(artist)}"
            results = sp_client.search(q=query, type='track', limit=1)
            if results and results['tracks']['items']: logger.debug(f"Spotify: Found via Title/Artist."); return results['tracks']['items'][0]['id']
    except spotipy.SpotifyException as e: logger.error(f"Spotify API error in find_song_on_spotify: {e}", exc_info=True)
    except Exception as e: logger.error(f"Unexpected error in find_song_on_spotify: {e}", exc_info=True)
    logger.debug(f"Spotify: Song not found (ISRC: {isrc}, Title: {title}, Artist: {artist})")
    return None

def find_song_on_deezer(access_token: str, isrc: str = None, title: str = None, artist: str = None) -> str | None:
    if not access_token: logger.error("Deezer access token not provided to find_song_on_deezer."); return None
    logger.debug(f"Deezer: Searching for song - ISRC: {isrc}, Title: {title}, Artist: {artist}")
    try:
        if isrc:
            search_url = f"https://api.deezer.com/search/track?q=isrc:\"{isrc}\"&limit=1&access_token={access_token}"
            response = requests.get(search_url); response.raise_for_status(); results = response.json()
            if results and results.get('data') and len(results['data']) > 0: logger.debug(f"Deezer: Found via ISRC."); return str(results['data'][0]['id'])
        if title:
            query_parts = []
            if artist: query_parts.append(f"artist:\"{normalize_text(artist)}\"")
            query_parts.append(f"track:\"{normalize_text(title)}\"")
            query_str = " ".join(query_parts)
            search_url = f"https://api.deezer.com/search/track?q={query_str}&limit=1&access_token={access_token}"
            response = requests.get(search_url); response.raise_for_status(); results = response.json()
            if results and results.get('data') and len(results['data']) > 0: logger.debug(f"Deezer: Found via Title/Artist."); return str(results['data'][0]['id'])
    except requests.exceptions.RequestException as e: logger.error(f"Deezer API error in find_song_on_deezer: {e}", exc_info=True)
    except ValueError as e: logger.error(f"JSON decode error find_song_on_deezer: {e}", exc_info=True) # JSON decode error
    logger.debug(f"Deezer: Song not found (ISRC: {isrc}, Title: {title}, Artist: {artist})")
    return None

def find_song_on_youtube(youtube_service, title: str, artist: str = None) -> str | None:
    if not youtube_service or not title: logger.error("YouTube service or title not provided to find_song_on_youtube."); return None
    logger.debug(f"YouTube: Searching for video - Title: {title}, Artist: {artist}")
    query = f"{normalize_text(title)}"
    if artist: query = f"{normalize_text(artist)} - {query}"
    try:
        search_response = youtube_service.search().list(q=query, part="snippet", type="video", videoCategoryId="10", maxResults=1).execute()
        if search_response and search_response.get("items"): logger.debug(f"YouTube: Found video."); return search_response["items"][0]["id"]["videoId"]
    except HttpError as e: logger.error(f"YouTube API error in find_song_on_youtube: {e._get_reason()}", exc_info=True)
    logger.debug(f"YouTube: Video not found (Title: {title}, Artist: {artist})")
    return None

# --- Liked Songs Synchronization Logic ---
def sync_liked_songs(sp_client: spotipy.Spotify, deezer_access_token: str, youtube_service):
    logger.info("Starting liked songs synchronization analysis.")
    proposed_actions = {"missing_on_spotify": [], "missing_on_deezer": [], "missing_on_youtube": [], "errors": [] }
    original_items_map = {} # To store metadata for proposals

    # Fetch Spotify
    logger.info("Fetching liked songs from Spotify...")
    spotify_songs_raw = sp_client_module.get_liked_songs(sp_client) # Assumes client module functions use logging
    logger.info(f"Fetched {len(spotify_songs_raw)} liked songs from Spotify.")
    spotify_ids_set = set()
    for track in spotify_songs_raw:
        if not track: continue
        isrc = track.get('external_ids', {}).get('isrc')
        title = normalize_text(track.get('name', ''))
        artist = normalize_text(track.get('artists', [{}])[0].get('name', '')) if track.get('artists') else ''
        primary_id = isrc if isrc else (title, artist) if title and artist else None
        if primary_id: spotify_ids_set.add(primary_id); original_items_map[primary_id] = {'title': track.get('name'), 'artist': track.get('artists')[0].get('name') if track.get('artists') else None, 'isrc': isrc, 'source_service': 'Spotify', 'original_track': track}
    logger.info(f"Normalized {len(spotify_ids_set)} unique items for Spotify.")

    # Fetch Deezer
    logger.info("Fetching liked songs from Deezer...")
    deezer_songs_raw = dz_client_module.get_liked_songs(deezer_access_token)
    logger.info(f"Fetched {len(deezer_songs_raw)} liked songs from Deezer.")
    deezer_ids_set = set()
    for track in deezer_songs_raw:
        if not track: continue
        isrc = track.get('isrc')
        title = normalize_text(track.get('title', ''))
        artist = normalize_text(track.get('artist', {}).get('name', ''))
        primary_id = isrc if isrc else (title, artist) if title and artist else None
        if primary_id: deezer_ids_set.add(primary_id);
        if primary_id and primary_id not in original_items_map: original_items_map[primary_id] = {'title': track.get('title'), 'artist': track.get('artist',{}).get('name'), 'isrc': isrc, 'source_service': 'Deezer', 'original_track': track}
    logger.info(f"Normalized {len(deezer_ids_set)} unique items for Deezer.")

    # Fetch YouTube
    logger.info("Fetching liked videos from YouTube...")
    youtube_videos_raw = yt_client_module.get_liked_videos(youtube_service)
    logger.info(f"Fetched {len(youtube_videos_raw)} liked videos from YouTube.")
    youtube_ids_set = set()
    # ... (Normalization logic for YouTube as in previous step, using normalize_text) ...
    for video in youtube_videos_raw:
        if not video or not video.get('snippet'): continue
        raw_title = video['snippet'].get('title', '')
        raw_artist_channel = video['snippet'].get('videoOwnerChannelTitle', video['snippet'].get('channelTitle', ''))
        parsed_artist, title_to_normalize = None, raw_title
        if ' - ' in raw_title:
            parts = raw_title.split(' - ', 1)
            if any(generic in raw_artist_channel.lower() for generic in ["vevo", "topic", "official", "records", "music", "lyric"]): parsed_artist = parts[0]; title_to_normalize = parts[1]
            else: parsed_artist = parts[0]; title_to_normalize = parts[1] # Simplified default
        else:
            if not any(generic in raw_artist_channel.lower() for generic in ["vevo", "topic", "official", "records", "music"]) and len(raw_artist_channel) < 35 : parsed_artist = raw_artist_channel
        title = normalize_text(title_to_normalize)
        artist = normalize_text(parsed_artist if parsed_artist else raw_artist_channel)
        if title and artist:
            primary_id = (title, artist) # YouTube primarily uses title/artist
            youtube_ids_set.add(primary_id)
            if primary_id not in original_items_map: original_items_map[primary_id] = {'title': video['snippet'].get('title'), 'artist': parsed_artist if parsed_artist else raw_artist_channel, 'isrc': None, 'source_service': 'YouTube', 'original_track': video}
    logger.info(f"Normalized {len(youtube_ids_set)} unique items for YouTube.")

    all_unique_ids = spotify_ids_set | deezer_ids_set | youtube_ids_set
    logger.info(f"Total unique liked items across all services: {len(all_unique_ids)}")

    # Prepare Proposed Actions (logic as before, ensuring logging for errors)
    for item_id in (all_unique_ids - spotify_ids_set):
        if item_id in original_items_map: proposed_actions["missing_on_spotify"].append({**original_items_map[item_id], "identifier_used": item_id})
        else: logger.error(f"Original item not found for ID {item_id} missing on Spotify."); proposed_actions["errors"].append({"message": "Original data missing", "id": str(item_id), "target": "spotify"})
    for item_id in (all_unique_ids - deezer_ids_set):
        if item_id in original_items_map: proposed_actions["missing_on_deezer"].append({**original_items_map[item_id], "identifier_used": item_id})
        else: logger.error(f"Original item not found for ID {item_id} missing on Deezer."); proposed_actions["errors"].append({"message": "Original data missing", "id": str(item_id), "target": "deezer"})
    for item_id in (all_unique_ids - youtube_ids_set):
        if item_id in original_items_map: proposed_actions["missing_on_youtube"].append({**original_items_map[item_id], "identifier_used": item_id})
        else: logger.error(f"Original item not found for ID {item_id} missing on YouTube."); proposed_actions["errors"].append({"message": "Original data missing", "id": str(item_id), "target": "youtube"})

    logger.info(f"Proposed actions for liked songs: Spotify Missing: {len(proposed_actions['missing_on_spotify'])}, Deezer Missing: {len(proposed_actions['missing_on_deezer'])}, YouTube Missing: {len(proposed_actions['missing_on_youtube'])}")
    if proposed_actions["errors"]: logger.warning(f"Encountered {len(proposed_actions['errors'])} errors during liked songs proposal generation.")
    return proposed_actions

# --- Playlist Synchronization Logic ---
def _get_track_primary_id(track_info: dict, service_name: str):
    # ... (implementation from previous step, ensure logging if errors occur here) ...
    isrc, title, artist = None, '', ''
    try:
        if service_name == "spotify": isrc = track_info.get('external_ids', {}).get('isrc'); title = normalize_text(track_info.get('name', '')); artist = normalize_text(track_info.get('artists', [{}])[0].get('name', '')) if track_info.get('artists') else ''
        elif service_name == "deezer": isrc = track_info.get('isrc'); title = normalize_text(track_info.get('title', '')); artist = normalize_text(track_info.get('artist', {}).get('name', ''))
        elif service_name == "youtube":
            raw_title = track_info.get('snippet', {}).get('title', '')
            raw_artist_channel = track_info.get('snippet', {}).get('videoOwnerChannelTitle', track_info.get('snippet', {}).get('channelTitle', ''))
            parsed_artist, title_to_normalize = None, raw_title
            if ' - ' in raw_title: parts = raw_title.split(' - ', 1); parsed_artist = parts[0]; title_to_normalize = parts[1]
            else:
                if not any(generic in raw_artist_channel.lower() for generic in ["vevo", "topic", "official", "records", "music"]) and len(raw_artist_channel) < 35 : parsed_artist = raw_artist_channel
            title = normalize_text(title_to_normalize); artist = normalize_text(parsed_artist if parsed_artist else raw_artist_channel)
    except Exception as e: logger.error(f"Error normalizing track for _get_track_primary_id (service: {service_name}): {track_info.get('id', 'N/A')}", exc_info=True); return None # Log and return None
    if isrc: return isrc
    if title and artist: return (title, artist)
    return None # Or (title, '') if allowing title-only match, but can be risky

def sync_playlists_analyze(sp_client: spotipy.Spotify, deezer_access_token: str, youtube_service):
    logger.info("Starting playlist synchronization analysis.")
    results = {"playlist_creations": [], "track_additions": [], "errors": [], "debug_info": {}}
    all_services_data = {}
    service_playlist_name_map = {"spotify": "name", "deezer": "title", "youtube": "title"}

    # Fetch Playlists
    for service_name, client_or_token, fetch_func in [
        ("spotify", sp_client, sp_client_module.get_playlists),
        ("deezer", deezer_access_token, dz_client_module.get_playlists),
        ("youtube", youtube_service, yt_client_module.get_playlists)
    ]:
        logger.info(f"Fetching playlists from {service_name.capitalize()}...")
        try: all_services_data[service_name] = fetch_func(client_or_token)
        except Exception as e: results["errors"].append({"service": service_name, "action": "fetch_playlists", "error": str(e)}); logger.error(f"Error fetching {service_name} playlists.", exc_info=True); all_services_data[service_name] = []
        logger.info(f"Fetched {len(all_services_data.get(service_name, []))} playlists from {service_name.capitalize()}.")

    # Map Playlists
    unified_playlists_map = {}
    for service_name, playlists in all_services_data.items():
        for pl in playlists:
            raw_name = pl.get(service_playlist_name_map[service_name], "") if service_name != "youtube" else pl.get('snippet', {}).get('title', "")
            if not raw_name: logger.warning(f"Playlist from {service_name} has empty name: {pl.get('id')}"); continue
            norm_name = normalize_text(raw_name)
            if not norm_name: logger.warning(f"Normalized playlist name is empty for '{raw_name}' from {service_name}."); continue
            if norm_name not in unified_playlists_map: unified_playlists_map[norm_name] = {}
            unified_playlists_map[norm_name][service_name] = pl
    results["debug_info"]["unified_playlist_count"] = len(unified_playlists_map)
    logger.info(f"Created a unified map of {len(unified_playlists_map)} unique playlist names.")

    # Identify Playlists to Create
    # ... (Logic as before, add logging if an error occurs determining original_name_for_creation) ...
    available_services = ["spotify", "deezer", "youtube"]
    for norm_name, service_map in unified_playlists_map.items():
        source_service_for_name = next((s for s in ["spotify", "deezer", "youtube"] if s in service_map), list(service_map.keys())[0] if service_map else None)
        original_name_for_creation = ""
        if source_service_for_name:
            pl_obj = service_map[source_service_for_name]
            original_name_for_creation = pl_obj.get(service_playlist_name_map[source_service_for_name], norm_name) if source_service_for_name != "youtube" else pl_obj.get('snippet',{}).get('title', norm_name)
        for service_to_check in available_services:
            if service_to_check not in service_map:
                results["playlist_creations"].append({"action": "create_playlist", "target_service": service_to_check, "playlist_name_normalized": norm_name, "playlist_name_original": original_name_for_creation if original_name_for_creation else norm_name, "source_example_service": source_service_for_name})
    logger.info(f"Proposed {len(results['playlist_creations'])} playlist creations.")

    # Analyze Tracks for Matched Playlists
    for norm_name, service_map in unified_playlists_map.items():
        logger.info(f"\nAnalyzing tracks for playlist: '{norm_name}'")
        playlist_tracks_data, original_track_item_map, service_track_id_sets = {}, {}, {}
        current_playlist_all_track_ids = set()
        for service_name, pl_obj in service_map.items():
            pl_id = pl_obj.get('id'); logger.info(f"  Fetching tracks for '{norm_name}' from {service_name} (ID: {pl_id})...")
            try:
                tracks = []
                if service_name == "spotify": tracks = sp_client_module.get_playlist_tracks(sp_client, pl_id)
                elif service_name == "deezer": tracks = dz_client_module.get_playlist_tracks(deezer_access_token, pl_id)
                elif service_name == "youtube": tracks = yt_client_module.get_playlist_items(youtube_service, pl_id)
                playlist_tracks_data[service_name] = tracks
                logger.info(f"    Fetched {len(tracks)} tracks from {service_name}.")
            except Exception as e: results["errors"].append({"service": service_name, "action": "fetch_playlist_tracks", "playlist_name": norm_name, "playlist_id": pl_id, "error": str(e)}); logger.error(f"Error fetching tracks for {norm_name} ({service_name})", exc_info=True); playlist_tracks_data[service_name] = []

            current_set = set()
            for track_item in playlist_tracks_data.get(service_name, []):
                if not track_item: continue
                track_for_id_logic = track_item
                if service_name == "youtube" and track_item.get('snippet', {}).get('resourceId', {}).get('kind') == 'youtube#video': track_for_id_logic = {'snippet': track_item.get('snippet'), 'id': track_item.get('snippet',{}).get('resourceId',{}).get('videoId')} # Pass videoId as 'id' to helper

                primary_id = _get_track_primary_id(track_for_id_logic, service_name)
                if primary_id:
                    current_set.add(primary_id)
                    if primary_id not in original_track_item_map:
                         original_track_item_map[primary_id] = {
                            "title": track_for_id_logic.get('snippet',{}).get('title') if service_name == "youtube" else track_for_id_logic.get('name') if service_name == "spotify" else track_for_id_logic.get('title'),
                            "artist": track_for_id_logic.get('snippet',{}).get('videoOwnerChannelTitle') if service_name == "youtube" else track_for_id_logic.get('artists',[{}])[0].get('name') if service_name == "spotify" and track_for_id_logic.get('artists') else track_for_id_logic.get('artist',{}).get('name') if service_name == "deezer" else "N/A",
                            "isrc": track_for_id_logic.get('external_ids',{}).get('isrc') if service_name == "spotify" else track_for_id_logic.get('isrc') if service_name == "deezer" else None,
                            "source_service": service_name, "original_item": track_item
                        }
            service_track_id_sets[service_name] = current_set
            current_playlist_all_track_ids.update(current_set)

        if not current_playlist_all_track_ids: logger.info(f"  No tracks identified in any version of playlist '{norm_name}'. Skipping track comparison."); continue
        logger.info(f"  Total unique tracks in '{norm_name}' across services: {len(current_playlist_all_track_ids)}")

        for target_service in available_services:
            if target_service not in service_map: continue
            target_playlist_id = service_map[target_service].get('id')
            tracks_on_target_service = service_track_id_sets.get(target_service, set())
            missing_track_ids_for_target = current_playlist_all_track_ids - tracks_on_target_service
            if missing_track_ids_for_target: logger.info(f"    Found {len(missing_track_ids_for_target)} tracks missing from {target_service}'s version of '{norm_name}'.")
            for track_id_tuple_or_isrc in missing_track_ids_for_target:
                if track_id_tuple_or_isrc in original_track_item_map:
                    item_info = original_track_item_map[track_id_tuple_or_isrc]
                    if item_info["source_service"] == target_service and track_id_tuple_or_isrc in service_track_id_sets.get(target_service, set()): continue # Should not happen with correct set logic
                    results["track_additions"].append({"action": "add_track_to_playlist", "playlist_name_normalized": norm_name, "playlist_name_original": service_map[target_service].get('snippet',{}).get('title') if target_service == "youtube" else service_map[target_service].get(service_playlist_name_map[target_service]), "target_service": target_service, "target_playlist_id": target_playlist_id, "track_title": item_info["title"], "track_artist": item_info["artist"], "track_isrc": item_info["isrc"], "source_service_of_track": item_info["source_service"], "identifier_used": track_id_tuple_or_isrc})
                else: logger.error(f"Original track item not found for ID {track_id_tuple_or_isrc} missing on {target_service} playlist '{norm_name}'."); results["errors"].append({"service": target_service, "action": "propose_track_addition", "playlist_name": norm_name, "error": "Original track data missing", "track_id": str(track_id_tuple_or_isrc)})

    logger.info(f"Proposed {len(results['track_additions'])} track additions to existing playlists.")
    if results["errors"]: logger.warning(f"Encountered {len(results['errors'])} errors during playlist sync analysis.")
    return results

if __name__ == '__main__':
    # from logging_config import setup_logging
    # setup_logging(debug_mode=True)
    logger.info("Sync Manager module with logging integrated.")
