import unicodedata
import re
import spotipy # For Spotify client and potential exceptions
import requests # For Deezer API calls
from googleapiclient.errors import HttpError # For YouTube API errors
import logging

# Import data fetching functions from client modules
from . import spotify_client as sp_client_module
from . import youtube_client as yt_client_module

# Get logger for this module
logger = logging.getLogger(__name__)

# --- Normalization Helper ---
def normalize_text(text: str) -> str:
    if not text: return ""
    text = text.lower()
    text = re.sub(r'\([^)]*\)', '', text) # Remove content in parentheses
    text = re.sub(r'\[[^)]*\]', '', text) # Remove content in brackets
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'\b(a|an|the)\b', '', text)
    text = re.sub(r'[^\w\s-]', '', text) 
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# --- Song Finder Functions (from previous step, condensed for brevity) ---
def find_song_on_spotify(sp_client: spotipy.Spotify, isrc: str = None, title: str = None, artist: str = None) -> str | None:
    """Find a song on Spotify by ISRC or title/artist."""
    if not sp_client: 
        logger.warning("No Spotify client provided to find_song_on_spotify")
        return None
    
    try:
        if isrc:
            logger.debug(f"Searching Spotify by ISRC: {isrc}")
            results = sp_client.search(q=f"isrc:{isrc}", type='track', limit=1)
            if results and results['tracks']['items']: 
                track_id = results['tracks']['items'][0]['id']
                logger.debug(f"Found Spotify track by ISRC {isrc}: {track_id}")
                return track_id
        
        if title:
            query = f"track:{normalize_text(title)}"
            if artist: 
                query += f" artist:{normalize_text(artist)}"
            
            logger.debug(f"Searching Spotify with query: {query}")
            results = sp_client.search(q=query, type='track', limit=1)
            if results and results['tracks']['items']: 
                track_id = results['tracks']['items'][0]['id']
                logger.debug(f"Found Spotify track by search: {track_id}")
                return track_id
                
    except spotipy.SpotifyException as e: 
        logger.error(f"Spotify API error in find_song_on_spotify: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in find_song_on_spotify: {e}")
    
    logger.debug(f"No Spotify track found for ISRC:{isrc}, title:'{title}', artist:'{artist}'")
    return None

def find_song_on_youtube(youtube_service, title: str, artist: str = None) -> str | None:
    """Find a song on YouTube by title and artist."""
    if not youtube_service or not title: 
        logger.warning("No YouTube service or title provided to find_song_on_youtube")
        return None
    
    query = f"{normalize_text(title)}"
    if artist: 
        query = f"{normalize_text(artist)} - {query}"
    
    logger.debug(f"Searching YouTube with query: {query}")
    
    try:
        search_response = youtube_service.search().list(
            q=query, 
            part="snippet", 
            type="video", 
            videoCategoryId="10",  # Music category
            maxResults=1
        ).execute()
        
        if search_response and search_response.get("items"): 
            video_id = search_response["items"][0]["id"]["videoId"]
            logger.debug(f"Found YouTube video by search: {video_id}")
            return video_id
            
    except HttpError as e: 
        logger.error(f"YouTube API error in find_song_on_youtube: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in find_song_on_youtube: {e}")
    
    logger.debug(f"No YouTube video found for title:'{title}', artist:'{artist}'")
    return None

# --- Liked Songs Synchronization Logic ---
def sync_liked_songs(sp_client: spotipy.Spotify, youtube_service):
    """
    Analyzes liked songs across Spotify and YouTube.
    Returns proposed actions for synchronizing liked songs.
    """
    logger.info("Starting liked songs synchronization analysis")
    
    results = {
        "missing_on_spotify": [],
        "missing_on_youtube": [],
        "errors": []
    }
    all_services_data = {}

    # A. Fetch liked songs from each service
    logger.info("Fetching liked songs from Spotify...")
    try:
        spotify_liked = sp_client_module.get_liked_songs(sp_client)
        all_services_data["spotify"] = spotify_liked
        logger.info(f"Fetched {len(spotify_liked)} liked songs from Spotify")
    except Exception as e:
        logger.error(f"Error fetching Spotify liked songs: {e}")
        results["errors"].append({"message": f"Error fetching Spotify liked songs: {str(e)}", "service": "spotify"})
        all_services_data["spotify"] = []
    
    print("Fetching liked videos from YouTube...")
    try:
        youtube_liked = yt_client_module.get_liked_videos(youtube_service)
        all_services_data["youtube"] = youtube_liked
        print(f"Fetched {len(youtube_liked)} liked videos from YouTube.")
    except Exception as e:
        results["errors"].append({"message": f"Error fetching YouTube liked videos: {str(e)}", "service": "youtube"})
        all_services_data["youtube"] = []
    
    # B. Normalize and create track sets for comparison
    service_track_sets = {}
    track_metadata = {}  # Store original track info for each normalized identifier
    
    for service_name, tracks in all_services_data.items():
        current_set = set()
        for track_item in tracks:
            if not track_item:
                continue
                
            # Extract track information based on service
            if service_name == "spotify":
                title = track_item.get('name', '')
                artist = track_item.get('artists', [{}])[0].get('name', '') if track_item.get('artists') else ''
                isrc = track_item.get('external_ids', {}).get('isrc')
            elif service_name == "youtube":
                # YouTube liked videos - extract from snippet
                snippet = track_item.get('snippet', {})
                raw_title = snippet.get('title', '')
                raw_artist_channel = snippet.get('videoOwnerChannelTitle', '') or snippet.get('channelTitle', '')
                
                # Parse artist and title from YouTube video title
                parsed_artist = None
                title_to_normalize = raw_title
                
                if ' - ' in raw_title:
                    parts = raw_title.split(' - ', 1)
                    # Simple heuristic: if channel seems like a label, artist might be in title
                    if any(generic in raw_artist_channel.lower() for generic in ["vevo", "topic", "official", "records", "music"]):
                        parsed_artist = parts[0]
                        title_to_normalize = parts[1]
                    else:
                        parsed_artist = parts[0]
                        title_to_normalize = parts[1]
                else:
                    # If channel title seems like an artist name (not generic)
                    if not any(generic in raw_artist_channel.lower() for generic in ["vevo", "topic", "official", "records", "music"]) and len(raw_artist_channel) < 35:
                        parsed_artist = raw_artist_channel
                
                title = title_to_normalize
                artist = parsed_artist if parsed_artist else raw_artist_channel
                isrc = None  # YouTube doesn't provide ISRC directly
            else:
                continue
            
            # Create normalized identifier
            normalized_title = normalize_text(title)
            normalized_artist = normalize_text(artist)
            
            # Use ISRC as primary identifier if available, otherwise use normalized title+artist
            if isrc:
                primary_id = isrc
            elif normalized_title and normalized_artist:
                primary_id = (normalized_title, normalized_artist)
            elif normalized_title:
                primary_id = (normalized_title, '')
            else:
                continue  # Skip if we can't identify the track
            
            current_set.add(primary_id)
            
            # Store metadata for this track (keep first occurrence)
            if primary_id not in track_metadata:
                track_metadata[primary_id] = {
                    "title": title,
                    "artist": artist,
                    "isrc": isrc,
                    "source_service": service_name,
                    "identifier_used": primary_id
                }
        
        service_track_sets[service_name] = current_set
        print(f"Normalized {len(current_set)} unique tracks from {service_name}")
    
    # C. Find missing tracks for each service
    all_track_ids = set()
    for track_set in service_track_sets.values():
        all_track_ids.update(track_set)
    
    logger.info(f"Total unique tracks across all services: {len(all_track_ids)}")
    logger.info("Analyzing missing tracks for each service...")
    
    # Find what's missing on each service
    for service_name in ["spotify", "youtube"]:
        if service_name not in service_track_sets:
            continue
            
        service_tracks = service_track_sets[service_name]
        missing_tracks = all_track_ids - service_tracks
        
        missing_list = []
        for track_id in missing_tracks:
            if track_id in track_metadata:
                track_info = track_metadata[track_id]
                # Don't suggest adding a track from the same service to itself
                if track_info["source_service"] != service_name:
                    missing_list.append(track_info)
        
        results[f"missing_on_{service_name}"] = missing_list
        print(f"Found {len(missing_list)} tracks missing on {service_name}")
    
    # Log final summary
    total_missing = sum(len(results[key]) for key in ["missing_on_spotify", "missing_on_youtube"])
    logger.info(f"Liked songs analysis complete. Total actions proposed: {total_missing}, Errors: {len(results['errors'])}")
    
    return results

# --- Playlist Synchronization Logic ---
def _get_track_primary_id(track_info: dict, service_name: str):
    """Helper to get ISRC or (title, artist) tuple for a track."""
    isrc = None
    title = ''
    artist = ''

    if service_name == "spotify":
        isrc = track_info.get('external_ids', {}).get('isrc')
        title = normalize_text(track_info.get('name', ''))
        artist = normalize_text(track_info.get('artists', [{}])[0].get('name', '')) if track_info.get('artists') else ''
    elif service_name == "youtube": # YouTube playlist items
        raw_title = track_info.get('snippet', {}).get('title', '')
        # For YouTube, videoOwnerChannelTitle might be the artist, or it's in the title
        # This part needs careful handling as in sync_liked_songs
        raw_artist_channel = track_info.get('snippet', {}).get('videoOwnerChannelTitle', '') # Preferred over channelTitle for playlistItems
        
        parsed_artist = None
        title_to_normalize = raw_title
        if ' - ' in raw_title:
            parts = raw_title.split(' - ', 1)
            # A simple heuristic: if channel title sounds like a label or is generic, artist might be in title part
            if any(generic in raw_artist_channel.lower() for generic in ["vevo", "topic", "official", "records", "music"]):
                parsed_artist = parts[0]
                title_to_normalize = parts[1]
            else: # Otherwise, channel title might be the artist
                parsed_artist = raw_artist_channel # Or parts[0] - this is tricky
                # title_to_normalize remains full if channel is artist
                # This is a simplification; more advanced parsing might be needed.
                # Let's try using parts[0] as artist and parts[1] as title if " - " is present
                parsed_artist = parts[0]
                title_to_normalize = parts[1]

        else: # No " - " in title
             # If channel title seems like an artist name (not generic)
            if not any(generic in raw_artist_channel.lower() for generic in ["vevo", "topic", "official", "records", "music"]) and len(raw_artist_channel) < 35:
                parsed_artist = raw_artist_channel
        
        title = normalize_text(title_to_normalize)
        artist = normalize_text(parsed_artist if parsed_artist else raw_artist_channel)


    if isrc: return isrc
    if title and artist: return (title, artist)
    # if title: return (title, '') # Fallback if artist is missing, less reliable
    return None


def sync_playlists_analyze(sp_client: spotipy.Spotify, youtube_service):
    """
    Analyzes playlists across Spotify and YouTube.
    Proposes actions: create missing playlists, add missing tracks to existing playlists.
    """
    logger.info("Starting playlist synchronization analysis")
    
    results = {
        "playlist_creations": [],
        "track_additions": [],
        "errors": [],
        "debug_info": {} 
    }
    all_services_data = {}

    # A. Fetch All Playlists
    logger.info("Fetching playlists from Spotify...")
    try: 
        all_services_data["spotify"] = sp_client_module.get_playlists(sp_client)
        logger.info(f"Fetched {len(all_services_data.get('spotify', []))} playlists from Spotify")
    except Exception as e: 
        logger.error(f"Error fetching Spotify playlists: {e}")
        results["errors"].append({"service": "spotify", "action": "fetch_playlists", "error": str(e)})
        all_services_data["spotify"] = []
    print(f"Fetched {len(all_services_data.get('spotify', []))} playlists from Spotify.")

    print("Fetching playlists from YouTube...")
    try: all_services_data["youtube"] = yt_client_module.get_playlists(youtube_service)
    except Exception as e: results["errors"].append({"service": "youtube", "action": "fetch_playlists", "error": str(e)}); all_services_data["youtube"] = []
    print(f"Fetched {len(all_services_data.get('youtube', []))} playlists from YouTube.")

    # B. Map Playlists by Normalized Name
    unified_playlists_map = {} # { "normalized_name": {"spotify": obj, "youtube": obj} }
    service_playlist_name_map = {"spotify": "name", "youtube": "title"} # YT playlist snippet.title

    for service_name, playlists in all_services_data.items():
        for pl in playlists:
            raw_name = ""
            if service_name == "youtube": raw_name = pl.get('snippet', {}).get(service_playlist_name_map[service_name], "")
            else: raw_name = pl.get(service_playlist_name_map[service_name], "")
            
            if not raw_name:
                results["errors"].append({"service": service_name, "action": "map_playlist_name", "error": "Playlist name is empty", "playlist_obj": pl})
                continue

            norm_name = normalize_text(raw_name)
            if not norm_name: # Skip if normalized name is empty (e.g. playlist name was just symbols)
                 results["errors"].append({"service": service_name, "action": "map_playlist_name", "error": "Normalized playlist name is empty", "original_name": raw_name})
                 continue

            if norm_name not in unified_playlists_map:
                unified_playlists_map[norm_name] = {}
            unified_playlists_map[norm_name][service_name] = pl
    
    results["debug_info"]["unified_playlist_count"] = len(unified_playlists_map)
    print(f"Created a unified map of {len(unified_playlists_map)} unique playlist names.")

    # C. Identify Playlists to Create
    available_services = ["spotify", "youtube"]
    for norm_name, service_map in unified_playlists_map.items():
        # Determine a source service (prefer Spotify > YouTube for original name)
        source_service_for_name = "spotify" if "spotify" in service_map else ("youtube" if "youtube" in service_map else None)
        
        original_name_for_creation = ""
        if source_service_for_name:
            pl_obj = service_map[source_service_for_name]
            if source_service_for_name == "youtube": original_name_for_creation = pl_obj.get('snippet', {}).get('title', norm_name)
            else: original_name_for_creation = pl_obj.get(service_playlist_name_map[source_service_for_name], norm_name)


        for service_to_check in available_services:
            if service_to_check not in service_map:
                results["playlist_creations"].append({
                    "action": "create_playlist",
                    "target_service": service_to_check,
                    "playlist_name_normalized": norm_name, # Use normalized for matching, but provide original for creation
                    "playlist_name_original": original_name_for_creation if original_name_for_creation else norm_name,
                    "source_example_service": source_service_for_name if source_service_for_name else list(service_map.keys())[0] # First available as example
                })
    print(f"Proposed {len(results['playlist_creations'])} playlist creations.")

    # D. For Each Matched Playlist (existing on at least one service), Analyze Tracks
    for norm_name, service_map in unified_playlists_map.items():
        playlist_tracks_data = {} # { "spotify": [tracks], "youtube": [tracks] }
        original_track_item_map = {} # { primary_id: {"title": ..., "artist": ..., "isrc": ..., "source_service": ...}, ... }
        
        # Fetch tracks for this playlist from each service it exists on
        print(f"\nAnalyzing playlist: '{norm_name}'")
        for service_name, pl_obj in service_map.items():
            pl_id = pl_obj.get('id')
            print(f"  Fetching tracks for '{norm_name}' from {service_name} (ID: {pl_id})...")
            try:
                if service_name == "spotify": tracks = sp_client_module.get_playlist_tracks(sp_client, pl_id)
                elif service_name == "youtube": tracks = yt_client_module.get_playlist_items(youtube_service, pl_id) # These are playlistItems
                else: tracks = []
                playlist_tracks_data[service_name] = tracks
                print(f"    Fetched {len(tracks)} tracks from {service_name}.")
            except Exception as e:
                results["errors"].append({"service": service_name, "action": "fetch_playlist_tracks", "playlist_name": norm_name, "playlist_id": pl_id, "error": str(e)})
                playlist_tracks_data[service_name] = []

        # Normalize tracks and build sets for comparison for this specific playlist
        service_track_id_sets = {} # { "spotify": {ids}, "youtube": {ids} }
        current_playlist_all_track_ids = set()

        for service_name, tracks in playlist_tracks_data.items():
            current_set = set()
            for track_item in tracks:
                if not track_item: continue
                # YouTube playlistItems have track data under snippet.resourceId.videoId for videos
                # and snippet.title etc.
                track_for_id_logic = track_item
                if service_name == "youtube" and track_item.get('snippet', {}).get('resourceId', {}).get('kind') == 'youtube#video':
                    # For YouTube, the actual track-like data is in snippet of playlistItem
                    # We need to pass the snippet to _get_track_primary_id
                    track_for_id_logic = {'snippet': track_item.get('snippet')} 
                    # Add videoId for later direct use if needed for adding to other services
                    track_for_id_logic['snippet']['videoId'] = track_item.get('snippet',{}).get('resourceId',{}).get('videoId')


                primary_id = _get_track_primary_id(track_for_id_logic, service_name)
                if primary_id:
                    current_set.add(primary_id)
                    if primary_id not in original_track_item_map: # Keep first encountered version as source
                        original_track_item_map[primary_id] = {
                            "title": track_item.get('snippet',{}).get('title') if service_name == "youtube" else track_item.get('name') if service_name == "spotify" else track_item.get('title'),
                            "artist": track_item.get('snippet',{}).get('videoOwnerChannelTitle') if service_name == "youtube" else track_item.get('artists',[{}])[0].get('name') if service_name == "spotify" and track_item.get('artists') else track_item.get('artist',{}).get('name') if service_name == "youtube" else "N/A",
                            "isrc": track_item.get('external_ids',{}).get('isrc') if service_name == "spotify" else track_item.get('isrc') if service_name == "youtube" else None,
                            "source_service": service_name,
                            "original_item": track_item # Full item for potential deeper inspection
                        }
            service_track_id_sets[service_name] = current_set
            current_playlist_all_track_ids.update(current_set)
        
        if not current_playlist_all_track_ids: # Skip if no tracks found in any version of this playlist
            print(f"  No tracks found or identified in any version of playlist '{norm_name}'. Skipping track comparison.")
            continue 
            
        print(f"  Total unique tracks in '{norm_name}' across services: {len(current_playlist_all_track_ids)}")

        # Identify missing tracks for each service's version of this playlist
        for target_service in available_services:
            if target_service not in service_map: continue # Playlist doesn't exist on target, creation handled above

            target_playlist_id = service_map[target_service].get('id')
            tracks_on_target_service = service_track_id_sets.get(target_service, set())
            missing_track_ids_for_target = current_playlist_all_track_ids - tracks_on_target_service

            if missing_track_ids_for_target:
                print(f"    Found {len(missing_track_ids_for_target)} tracks missing from {target_service}'s version of '{norm_name}'.")
            
            for track_id_tuple_or_isrc in missing_track_ids_for_target:
                if track_id_tuple_or_isrc in original_track_item_map:
                    item_info = original_track_item_map[track_id_tuple_or_isrc]
                    # Ensure we don't try to add a song to a playlist from itself if sets are somehow misaligned
                    if item_info["source_service"] == target_service and track_id_tuple_or_isrc in service_track_id_sets.get(target_service, set()):
                        continue

                    results["track_additions"].append({
                        "action": "add_track_to_playlist",
                        "playlist_name_normalized": norm_name,
                        "playlist_name_original": service_map[target_service].get('snippet',{}).get('title') if target_service == "youtube" else service_map[target_service].get(service_playlist_name_map[target_service]),
                        "target_service": target_service,
                        "target_playlist_id": target_playlist_id,
                        "track_title": item_info["title"],
                        "track_artist": item_info["artist"],
                        "track_isrc": item_info["isrc"],
                        "source_service_of_track": item_info["source_service"],
                        "identifier_used": track_id_tuple_or_isrc # for debugging
                    })
                else:
                     results["errors"].append({"service": target_service, "action": "propose_track_addition", "playlist_name": norm_name, "error": "Original track item not found for ID", "track_id": str(track_id_tuple_or_isrc)})
    
    print(f"\nProposed {len(results['track_additions'])} track additions to existing playlists.")
    if results["errors"]: print(f"Encountered {len(results['errors'])} errors during playlist sync analysis.")
    return results

if __name__ == '__main__':
    print("Sync Manager - Playlist Synchronization Analysis")
    # Conceptual test (similar to sync_liked_songs) would go here
    pass
