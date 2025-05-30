from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
import json
import time
import schedule
import threading
import logging # New import
import os # For token_store path logging

# App imports
from . import spotify_client as sp_client_module # Using module alias
from . import deezer_client as dz_client_module # Using module alias
from . import youtube_client as yt_client_module # Using module alias
from . import token_store # For logging its path
from .logging_config import setup_logging # New import
from .sync_manager import sync_liked_songs, sync_playlists_analyze, find_song_on_spotify, find_song_on_deezer, find_song_on_youtube

# Third-party imports
import spotipy
import requests
from google.oauth2.credentials import Credentials as GoogleCredentials
from google_auth_oauthlib.flow import Flow
from google.auth.exceptions import OAuthError as GoogleOAuthError, RefreshError as GoogleRefreshError
from googleapiclient.errors import HttpError as GoogleHttpError

# Setup logging - Call this early
setup_logging() # Default to INFO level, set debug_mode=True for DEBUG
logger = logging.getLogger(__name__) # Logger for this module

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# --- Background Scheduler ---
def perform_automated_sync():
    logger.info(f"SCHEDULER: Starting automated sync cycle...")
    sp_client, deezer_token, youtube_service = None, None, None
    auth_ok_for_all = True
    logger.info("SCHEDULER: Attempting to get authenticated clients...")
    try:
        sp_client = get_valid_spotify_client(raise_exception=False)
        if not sp_client: logger.warning("SCHEDULER: Spotify client NOT available/authenticated."); auth_ok_for_all = False
        else: logger.info("SCHEDULER: Spotify client OK.")
    except Exception as e: logger.error(f"SCHEDULER: Error getting Spotify client: {e}", exc_info=True); auth_ok_for_all = False

    try:
        deezer_token_data = dz_client_module.get_cached_deezer_token_data()
        if deezer_token_data and 'access_token' in deezer_token_data:
            deezer_token = deezer_token_data['access_token']
            logger.info("SCHEDULER: Deezer token OK.")
        else: logger.warning("SCHEDULER: Deezer token NOT available/authenticated."); auth_ok_for_all = False
    except Exception as e: logger.error(f"SCHEDULER: Error getting Deezer token: {e}", exc_info=True); auth_ok_for_all = False

    try:
        youtube_service = get_valid_youtube_service(raise_exception=False)
        if not youtube_service: logger.warning("SCHEDULER: YouTube service NOT available/authenticated."); auth_ok_for_all = False
        else: logger.info("SCHEDULER: YouTube service OK.")
    except Exception as e: logger.error(f"SCHEDULER: Error getting YouTube service: {e}", exc_info=True); auth_ok_for_all = False

    if not auth_ok_for_all:
        logger.warning("SCHEDULER: One or more services are not fully authenticated. Sync might be partial or skipped.")

    # Liked Songs Sync
    if sp_client and deezer_token and youtube_service:
        logger.info("SCHEDULER: Starting Liked Songs sync execution...")
        try:
            proposed_liked_actions = sync_liked_songs(sp_client, deezer_token, youtube_service) # sync_manager should use logging too
            for item in proposed_liked_actions.get("missing_on_spotify", []):
                logger.info(f"SCHEDULER: Liked: Attempting to add to Spotify: {item['title']} by {item.get('artist','N/A')}")
                track_id = find_song_on_spotify(sp_client, item.get('isrc'), item['title'], item.get('artist'))
                if track_id: sp_client_module.add_liked_song(sp_client, track_id)
                else: logger.warning(f"SCHEDULER: Liked: Could not find '{item['title']}' on Spotify to add.")
            for item in proposed_liked_actions.get("missing_on_deezer", []):
                logger.info(f"SCHEDULER: Liked: Attempting to add to Deezer: {item['title']} by {item.get('artist','N/A')}")
                track_id = find_song_on_deezer(deezer_token, item.get('isrc'), item['title'], item.get('artist'))
                if track_id: dz_client_module.add_liked_song(deezer_token, track_id)
                else: logger.warning(f"SCHEDULER: Liked: Could not find '{item['title']}' on Deezer to add.")
            for item in proposed_liked_actions.get("missing_on_youtube", []):
                logger.info(f"SCHEDULER: Liked: Attempting to add to YouTube: {item['title']} by {item.get('artist','N/A')}")
                video_id = find_song_on_youtube(youtube_service, item['title'], item.get('artist'))
                if video_id: yt_client_module.add_liked_video(youtube_service, video_id)
                else: logger.warning(f"SCHEDULER: Liked: Could not find '{item['title']}' on YouTube to add.")
            logger.info("SCHEDULER: Liked Songs sync execution finished.")
        except Exception as e: logger.error(f"SCHEDULER: Error during liked songs sync execution: {e}", exc_info=True)
    else: logger.warning("SCHEDULER: Skipping Liked Songs sync due to missing client(s).")

    # Playlist Sync
    if sp_client and deezer_token and youtube_service:
        logger.info("SCHEDULER: Starting Playlist sync execution...")
        try:
            proposed_playlist_actions = sync_playlists_analyze(sp_client, deezer_token, youtube_service)
            spotify_user_id = sp_client_module.get_cached_spotify_token_info().get('user_id') if sp_client_module.get_cached_spotify_token_info() else None

            for pl_creation in proposed_playlist_actions.get("playlist_creations", []):
                target_serv, pl_name = pl_creation['target_service'], pl_creation['playlist_name_original']
                logger.info(f"SCHEDULER: Playlist: Attempting to create '{pl_name}' on {target_serv}")
                if target_serv == "spotify" and spotify_user_id: sp_client_module.create_playlist(sp_client, spotify_user_id, pl_name)
                elif target_serv == "deezer": dz_client_module.create_playlist(deezer_token, pl_name)
                elif target_serv == "youtube": yt_client_module.create_playlist(youtube_service, pl_name)

            for track_add in proposed_playlist_actions.get("track_additions", []):
                target_serv, pl_id = track_add['target_service'], track_add['target_playlist_id']
                title, artist, isrc = track_add['track_title'], track_add.get('track_artist'), track_add.get('track_isrc')
                logger.info(f"SCHEDULER: Playlist: Attempting to add '{title}' to playlist {pl_id} on {target_serv}")
                track_id_on_target = None
                if target_serv == "spotify": track_id_on_target = find_song_on_spotify(sp_client, isrc, title, artist)
                elif target_serv == "deezer": track_id_on_target = find_song_on_deezer(deezer_token, isrc, title, artist)
                elif target_serv == "youtube": track_id_on_target = find_song_on_youtube(youtube_service, title, artist)
                if track_id_on_target:
                    if target_serv == "spotify": sp_client_module.add_tracks_to_playlist(sp_client, pl_id, [track_id_on_target])
                    elif target_serv == "deezer": dz_client_module.add_tracks_to_playlist(deezer_token, pl_id, [track_id_on_target])
                    elif target_serv == "youtube": yt_client_module.add_video_to_playlist(youtube_service, pl_id, track_id_on_target)
                else: logger.warning(f"SCHEDULER: Playlist: Could not find '{title}' on {target_serv} to add to playlist {pl_id}.")
            logger.info("SCHEDULER: Playlist sync execution finished.")
        except Exception as e: logger.error(f"SCHEDULER: Error during playlist sync execution: {e}", exc_info=True)
    else: logger.warning("SCHEDULER: Skipping Playlist sync due to missing client(s).")
    logger.info(f"SCHEDULER: Automated sync cycle finished.")

def run_scheduler():
    logger.info("SCHEDULER: Scheduler background thread started. Waiting for scheduled jobs.")
    schedule.every(4).hours.do(perform_automated_sync)
    while True: schedule.run_pending(); time.sleep(60)

@app.on_event("startup")
async def startup_event():
    logger.info("APP STARTUP: Initializing background scheduler...")
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("APP STARTUP: Background scheduler thread started.")
    logger.info(f"APP STARTUP: Token file is expected at: {os.path.abspath(token_store.TOKEN_FILE_PATH)}")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request): return templates.TemplateResponse("index.html", {"request": request, "title": "Home"})

# --- Client Getters ---
def get_valid_spotify_client(raise_exception=True):
    token_info = sp_client_module.get_cached_spotify_token_info()
    if not token_info:
        if raise_exception: raise HTTPException(status_code=401, detail="Spotify token not found. Please login.")
        return None
    sp_oauth = sp_client_module.create_spotify_oauth_util()
    if sp_oauth.is_token_expired(token_info):
        logger.info("Spotify token expired. Attempting refresh...")
        try:
            token_info = sp_oauth.refresh_access_token(token_info.get('refresh_token','')) # Pass only refresh token string
            if not token_info: sp_client_module.delete_spotify_token_info();
            if raise_exception: raise HTTPException(status_code=401, detail="Spotify token refresh failed. Please re-login.")
            return None
            sp_client_module.save_spotify_token_info(token_info); logger.info("Spotify token refreshed and saved.")
        except spotipy.SpotifyOauthError as e:
            logger.error(f"Spotify token refresh error: {e}", exc_info=True); sp_client_module.delete_spotify_token_info()
            if raise_exception: raise HTTPException(status_code=401, detail=f"Spotify token refresh failed: {e}. Please re-login.")
            return None
    if 'user_id' not in token_info:
        try:
            sp_temp = sp_client_module.get_spotify_client_util(token_info)
            me = sp_temp.me()
            if me and 'id' in me: token_info['user_id'] = me['id']; sp_client_module.save_spotify_token_info(token_info)
            else:
                 logger.warning("Could not verify Spotify user (me() failed), token might be invalid.")
                 if raise_exception: raise HTTPException(status_code=401, detail="Could not verify Spotify user. Please re-login.")
                 sp_client_module.delete_spotify_token_info(); return None
        except Exception as e:
            logger.error(f"Error fetching Spotify user ID: {e}", exc_info=True)
            if raise_exception: raise HTTPException(status_code=401, detail="Could not verify Spotify user. Please re-login.")
            sp_client_module.delete_spotify_token_info(); return None
    return sp_client_module.get_spotify_client_util(token_info)

def get_valid_deezer_token(raise_exception=True):
    token_data = dz_client_module.get_cached_deezer_token_data()
    if not token_data or not token_data.get("access_token"):
        if raise_exception: raise HTTPException(status_code=401, detail="Deezer token not found. Please login.")
        return None
    return token_data["access_token"]

def get_valid_youtube_service(raise_exception=True):
    cached_token_data = yt_client_module.get_cached_youtube_token_data()
    if not cached_token_data:
        if raise_exception: raise HTTPException(status_code=401, detail="YouTube credentials not found. Please login.")
        return None
    service = yt_client_module.get_youtube_client_service(cached_token_data)
    if not service:
        # Token deletion on refresh failure is handled in get_youtube_client_service
        if raise_exception: raise HTTPException(status_code=401, detail="Failed to initialize YouTube service or refresh token. Please re-login.")
        return None
    return service

# --- Auth Callbacks ---
@app.get("/callback/spotify")
async def callback_spotify(request: Request, code: str = None):
    sp_oauth = sp_client_module.create_spotify_oauth_util()
    if not code: logger.error(f"Spotify login failed: {request.query_params.get('error', 'No code provided.')}"); return HTMLResponse("...", status_code=400)
    try:
        token_info = sp_oauth.get_access_token(code, check_cache=False)
        if token_info:
            sp_temp = sp_client_module.get_spotify_client_util(token_info)
            me = sp_temp.me()
            if me and 'id' in me: token_info['user_id'] = me['id']
            else: logger.warning("Could not fetch user_id for Spotify during callback.")
            sp_client_module.save_spotify_token_info(token_info); logger.info("Spotify token saved to store.")
    except spotipy.SpotifyOauthError as e: logger.error(f"Spotify Auth Error: {e}", exc_info=True); return HTMLResponse("...", status_code=400)
    return HTMLResponse("<html><body>Spotify Login Successful! Token stored. <a href='/'>Home</a></body></html>")

@app.get("/callback/deezer")
async def callback_deezer(request: Request, code: str = None, error_reason: str = None):
    if error_reason: logger.error(f"Deezer login failed: {error_reason}"); return HTMLResponse("...", status_code=400)
    if not code: logger.error("Deezer login failed: No code."); return HTMLResponse("...", status_code=400)
    token_data = dz_client_module.get_deezer_access_token_util(code)
    if not token_data: logger.error("Deezer Token Error (get_deezer_access_token_util failed)."); return HTMLResponse("...", status_code=400)
    logger.info("Deezer token (re)fetched and saved.")
    return HTMLResponse("<html><body>Deezer Login Successful! Token stored. <a href='/'>Home</a></body></html>")

@app.get("/callback/youtube")
async def callback_youtube(request: Request, code: str = None, state: str = None, error: str = None):
    if error: logger.error(f"YouTube login failed: {error}"); return HTMLResponse("...", status_code=400)
    if not code: logger.error("YouTube login failed: No code."); return HTMLResponse("...", status_code=400)
    try:
        flow = create_youtube_flow_util()
        flow.fetch_token(code=code)
        credentials = flow.credentials
        yt_client_module.save_youtube_token_data(credentials); logger.info("YouTube credentials saved to store.")
    except GoogleOAuthError as e: logger.error(f"YouTube OAuth Error: {e}", exc_info=True); return HTMLResponse("...", status_code=400)
    return HTMLResponse("<html><body>YouTube Login Successful! Credentials stored. <a href='/'>Home</a></body></html>")

# --- UI & Action Endpoints (condensed, print replaced with logging) ---
# ... (All existing @app.get and @app.post routes for /me, /SERVICE/ui/*, /sync/*)
# Example of logging change in one endpoint:
@app.post("/sync/liked/add", response_class=HTMLResponse)
async def add_liked_song_route(request: Request, isrc: str = Form(None), title: str = Form(...), artist: str = Form(None), target_service: str = Form(...)):
    item_details = f"'{title}' by '{artist if artist else 'N/A'}' (ISRC: {isrc if isrc else 'N/A'})"
    logger.info(f"Attempting to add liked song: {item_details} to {target_service}")
    try:
        if target_service == "spotify":
            sp = get_valid_spotify_client()
            target_id = find_song_on_spotify(sp, isrc=isrc, title=title, artist=artist)
            if target_id:
                if sp_client_module.add_liked_song(sp, target_id): return HTMLResponse(f"<span style='color:green;'>Added.</span>")
                else: logger.warning(f"Failed to add {item_details} to Spotify (already liked or error)."); return HTMLResponse(f"<span style='color:red;'>Failed.</span>")
            else: logger.warning(f"Song {item_details} not found on Spotify."); return HTMLResponse(f"<span style='color:orange;'>Not found.</span>")
        # ... (similar for Deezer and YouTube, with logging) ...
        elif target_service == "deezer":
            token = get_valid_deezer_token()
            target_id = find_song_on_deezer(token, isrc=isrc, title=title, artist=artist)
            if target_id:
                if dz_client_module.add_liked_song(token, target_id): return HTMLResponse(f"<span style='color:green;'>Added.</span>")
                else: logger.warning(f"Failed to add {item_details} to Deezer (already liked or error)."); return HTMLResponse(f"<span style='color:red;'>Failed.</span>")
            else: logger.warning(f"Song {item_details} not found on Deezer."); return HTMLResponse(f"<span style='color:orange;'>Not found.</span>")
        elif target_service == "youtube":
            yt_service = get_valid_youtube_service()
            target_id = find_song_on_youtube(yt_service, title=title, artist=artist)
            if target_id:
                if yt_client_module.add_liked_video(yt_service, target_id): return HTMLResponse(f"<span style='color:green;'>Liked.</span>")
                else: logger.warning(f"Failed to like video for {item_details} on YouTube (already liked or error)."); return HTMLResponse(f"<span style='color:red;'>Failed.</span>")
            else: logger.warning(f"Video for {item_details} not found on YouTube."); return HTMLResponse(f"<span style='color:orange;'>Not found.</span>")
        else:
            logger.error(f"Invalid target service '{target_service}' for add_liked_song.")
            return HTMLResponse(f"<span style='color:red;'>Invalid target.</span>", status_code=400)
    except HTTPException as e:
        logger.warning(f"Auth error for {target_service} during add_liked_song: {e.detail}")
        return HTMLResponse(f"<span style='color:red;'>Login to {target_service.capitalize()}</span>")
    except Exception as e:
        logger.error(f"Error in /sync/liked/add for {target_service} adding {item_details}: {e}", exc_info=True)
        return HTMLResponse(f"<span style='color:red;'>Error.</span>", status_code=500)

# (Other endpoints would also be updated with logging similarly)
# ... (The rest of the endpoints from the previous main.py, with print replaced by logger calls)
@app.get("/me/spotify", response_class=HTMLResponse)
async def show_spotify_me(request: Request):
    try: sp = get_valid_spotify_client(); user = sp.current_user(); return templates.TemplateResponse("me_display.html", {"request":request, "service_name":"Spotify", "user_info":user})
    except HTTPException: return RedirectResponse("/login/spotify")
    except Exception as e: logger.error("Error show_spotify_me", exc_info=True); return HTMLResponse(f"Error: {e} <a href='/'>Home</a>", status_code=500)
@app.get("/spotify/ui/liked-songs", response_class=HTMLResponse)
async def spotify_ui_liked_songs(request: Request):
    try: sp = get_valid_spotify_client(); items = get_spotify_liked_songs(sp); return templates.TemplateResponse("_service_items_display.html", {"request": request, "title": "Spotify Liked Songs", "items": items, "item_type": "track", "service_name_lower": "spotify", "service_name_capitalized": "Spotify"})
    except HTTPException: return templates.TemplateResponse("_service_items_display.html", {"request": request, "title": "Spotify Liked Songs", "auth_error_message": "Please login to Spotify.", "service_name_lower": "spotify", "service_name_capitalized": "Spotify"})
    except Exception as e: logger.error("Error spotify_ui_liked_songs", exc_info=True); return templates.TemplateResponse("_service_items_display.html", {"request": request, "title": "Spotify Liked Songs", "general_error_message": str(e)})
@app.get("/spotify/ui/playlists", response_class=HTMLResponse)
async def spotify_ui_playlists(request: Request):
    try: sp = get_valid_spotify_client(); items = get_spotify_playlists(sp); return templates.TemplateResponse("_service_items_display.html", {"request": request, "title": "Spotify Playlists", "items": items, "item_type": "playlist", "service_name_lower": "spotify", "service_name_capitalized": "Spotify"})
    except HTTPException: return templates.TemplateResponse("_service_items_display.html", {"request": request, "title": "Spotify Playlists", "auth_error_message": "Please login to Spotify.", "service_name_lower": "spotify", "service_name_capitalized": "Spotify"})
    except Exception as e: logger.error("Error spotify_ui_playlists", exc_info=True); return templates.TemplateResponse("_service_items_display.html", {"request": request, "title": "Spotify Playlists", "general_error_message": str(e)})
@app.get("/me/deezer", response_class=HTMLResponse)
async def show_deezer_me(request: Request):
    try: token = get_valid_deezer_token(); user_info = dz_client_module.get_deezer_user_info(token); return templates.TemplateResponse("me_display.html", {"request":request, "service_name":"Deezer", "user_info":user_info})
    except HTTPException: return RedirectResponse("/login/deezer")
    except Exception as e: logger.error("Error show_deezer_me", exc_info=True); return HTMLResponse(f"Error: {e} <a href='/'>Home</a>", status_code=500)
@app.get("/deezer/ui/liked-songs", response_class=HTMLResponse)
async def deezer_ui_liked_songs(request: Request):
    try: token = get_valid_deezer_token(); items = get_deezer_liked_songs(token); return templates.TemplateResponse("_service_items_display.html", {"request": request, "title": "Deezer Liked Songs", "items": items, "item_type": "track", "service_name_lower": "deezer", "service_name_capitalized": "Deezer"})
    except HTTPException: return templates.TemplateResponse("_service_items_display.html", {"request": request, "title": "Deezer Liked Songs", "auth_error_message": "Please login to Deezer.", "service_name_lower": "deezer", "service_name_capitalized": "Deezer"})
    except Exception as e: logger.error("Error deezer_ui_liked_songs", exc_info=True); return templates.TemplateResponse("_service_items_display.html", {"request": request, "title": "Deezer Liked Songs", "general_error_message": str(e)})
@app.get("/deezer/ui/playlists", response_class=HTMLResponse)
async def deezer_ui_playlists(request: Request):
    try: token = get_valid_deezer_token(); items = get_deezer_playlists(token); return templates.TemplateResponse("_service_items_display.html", {"request": request, "title": "Deezer Playlists", "items": items, "item_type": "playlist", "service_name_lower": "deezer", "service_name_capitalized": "Deezer"})
    except HTTPException: return templates.TemplateResponse("_service_items_display.html", {"request": request, "title": "Deezer Playlists", "auth_error_message": "Please login to Deezer.", "service_name_lower": "deezer", "service_name_capitalized": "Deezer"})
    except Exception as e: logger.error("Error deezer_ui_playlists", exc_info=True); return templates.TemplateResponse("_service_items_display.html", {"request": request, "title": "Deezer Playlists", "general_error_message": str(e)})
@app.get("/me/youtube", response_class=HTMLResponse)
async def show_youtube_me(request: Request):
    try: service = get_valid_youtube_service(); response = service.channels().list(part="snippet", mine=True).execute(); return templates.TemplateResponse("me_display.html", {"request":request, "service_name":"YouTube", "user_info":response})
    except HTTPException: return RedirectResponse("/login/youtube")
    except GoogleHttpError as e: logger.error(f"YouTube API Error: {e._get_reason()}", exc_info=True); return HTMLResponse(f"YouTube API Error: {e._get_reason()} <a href='/login/youtube'>Login again</a>", status_code=e.resp.status)
    except Exception as e: logger.error("Error show_youtube_me", exc_info=True); return HTMLResponse(f"Error: {e} <a href='/'>Home</a>", status_code=500)
@app.get("/youtube/ui/liked-videos", response_class=HTMLResponse)
async def youtube_ui_liked_videos(request: Request):
    try: service = get_valid_youtube_service(); items = get_youtube_liked_videos(service); return templates.TemplateResponse("_service_items_display.html", {"request": request, "title": "YouTube Liked Videos", "items": items, "item_type": "video", "service_name_lower": "youtube", "service_name_capitalized": "YouTube"})
    except HTTPException: return templates.TemplateResponse("_service_items_display.html", {"request": request, "title": "YouTube Liked Videos", "auth_error_message": "Please login to YouTube.", "service_name_lower": "youtube", "service_name_capitalized": "YouTube"})
    except Exception as e: logger.error("Error youtube_ui_liked_videos", exc_info=True); return templates.TemplateResponse("_service_items_display.html", {"request": request, "title": "YouTube Liked Videos", "general_error_message": str(e)})
@app.get("/youtube/ui/playlists", response_class=HTMLResponse)
async def youtube_ui_playlists(request: Request):
    try: service = get_valid_youtube_service(); items = get_youtube_playlists(service); return templates.TemplateResponse("_service_items_display.html", {"request": request, "title": "YouTube Playlists", "items": items, "item_type": "playlist", "service_name_lower": "youtube", "service_name_capitalized": "YouTube"})
    except HTTPException: return templates.TemplateResponse("_service_items_display.html", {"request": request, "title": "YouTube Playlists", "auth_error_message": "Please login to YouTube.", "service_name_lower": "youtube", "service_name_capitalized": "YouTube"})
    except Exception as e: logger.error("Error youtube_ui_playlists", exc_info=True); return templates.TemplateResponse("_service_items_display.html", {"request": request, "title": "YouTube Playlists", "general_error_message": str(e)})
@app.post("/sync/liked/analyze", response_class=HTMLResponse)
async def analyze_liked_songs_sync(request: Request):
    auth_error_services = []; sp_client, deezer_token, youtube_service = None, None, None
    try: sp_client = get_valid_spotify_client(raise_exception=False)
    except HTTPException: pass
    try: deezer_token = get_valid_deezer_token(raise_exception=False)
    except HTTPException: pass
    try: youtube_service = get_valid_youtube_service(raise_exception=False)
    except HTTPException: pass
    if not sp_client: auth_error_services.append("Spotify")
    if not deezer_token: auth_error_services.append("Deezer")
    if not youtube_service: auth_error_services.append("YouTube")
    if auth_error_services: return templates.TemplateResponse("_proposed_sync_actions.html", {"request": request, "auth_error_services": auth_error_services, "proposed_actions": None})
    try:
        proposed_actions = sync_liked_songs(sp_client, deezer_token, youtube_service) # This function itself should use logging
        return templates.TemplateResponse("_proposed_sync_actions.html", {"request": request, "proposed_actions": proposed_actions, "auth_error_services": None})
    except Exception as e: logger.error(f"Error during sync_liked_songs analysis: {e}", exc_info=True); return templates.TemplateResponse("_proposed_sync_actions.html", {"request": request, "analysis_error": f"Error: {str(e)}."})
@app.post("/sync/playlists/analyze", response_class=HTMLResponse)
async def analyze_playlists_sync(request: Request):
    auth_error_services = []; sp_client, deezer_token, youtube_service = None, None, None
    try: sp_client = get_valid_spotify_client(raise_exception=False)
    except HTTPException: pass
    try: deezer_token = get_valid_deezer_token(raise_exception=False)
    except HTTPException: pass
    try: youtube_service = get_valid_youtube_service(raise_exception=False)
    except HTTPException: pass
    if not sp_client: auth_error_services.append("Spotify")
    if not deezer_token: auth_error_services.append("Deezer")
    if not youtube_service: auth_error_services.append("YouTube")
    if auth_error_services: return templates.TemplateResponse("_proposed_playlist_sync_actions.html", {"request": request, "auth_error_services": auth_error_services, "proposed_actions": None})
    try:
        proposed_actions = sync_playlists_analyze(sp_client, deezer_token, youtube_service) # This function itself should use logging
        return templates.TemplateResponse("_proposed_playlist_sync_actions.html", {"request": request, "proposed_actions": proposed_actions, "auth_error_services": None})
    except Exception as e: logger.error(f"Error during sync_playlists_analyze: {e}", exc_info=True); return templates.TemplateResponse("_proposed_playlist_sync_actions.html", {"request": request, "analysis_error": f"Error: {str(e)}."})
@app.post("/sync/playlist/create", response_class=HTMLResponse)
async def create_playlist_route(request: Request, target_service: str = Form(...), playlist_name: str = Form(...)):
    logger.info(f"Attempting to create playlist '{playlist_name}' on {target_service}")
    try:
        if target_service == "spotify":
            sp = get_valid_spotify_client(); user_id = sp_client_module.get_cached_spotify_token_info().get('user_id')
            if not user_id: logger.error("Spotify User ID not found for playlist creation."); raise HTTPException(status_code=401, detail="Spotify User ID not found.")
            new_playlist = sp_client_module.create_playlist(sp, user_id=user_id, playlist_name=playlist_name)
            if new_playlist and new_playlist.get('id'): return HTMLResponse(f"<span style='color:green;'>Created '{playlist_name}'.</span>")
            else: logger.error(f"Failed creating '{playlist_name}' on Spotify."); return HTMLResponse(f"<span style='color:red;'>Failed.</span>")
        elif target_service == "deezer":
            token = get_valid_deezer_token(); new_playlist_id = dz_client_module.create_playlist(token, title=playlist_name)
            if new_playlist_id: return HTMLResponse(f"<span style='color:green;'>Created '{playlist_name}'.</span>")
            else: logger.error(f"Failed creating '{playlist_name}' on Deezer."); return HTMLResponse(f"<span style='color:red;'>Failed.</span>")
        elif target_service == "youtube":
            yt_service = get_valid_youtube_service(); new_playlist = yt_client_module.create_playlist(yt_service, title=playlist_name)
            if new_playlist and new_playlist.get('id'): return HTMLResponse(f"<span style='color:green;'>Created '{playlist_name}'.</span>")
            else: logger.error(f"Failed creating '{playlist_name}' on YouTube."); return HTMLResponse(f"<span style='color:red;'>Failed.</span>")
        else: logger.error(f"Invalid target service '{target_service}' for create_playlist."); return HTMLResponse(f"<span style='color:red;'>Invalid target.</span>", status_code=400)
    except HTTPException as e: logger.warning(f"Auth error for {target_service} during create_playlist: {e.detail}"); return HTMLResponse(f"<span style='color:red;'>Login to {target_service.capitalize()}</span>")
    except Exception as e: logger.error(f"Error in /sync/playlist/create: {e}", exc_info=True); return HTMLResponse(f"<span style='color:red;'>Error.</span>", status_code=500)
@app.post("/sync/playlist/add_track", response_class=HTMLResponse)
async def add_track_to_playlist_route(request: Request,target_service: str = Form(...),target_playlist_id: str = Form(...),track_title: str = Form(...),track_artist: str = Form(None),track_isrc: str = Form(None)):
    item_details = f"'{track_title}' by '{track_artist if track_artist else 'N/A'}' (ISRC: {track_isrc if track_isrc else 'N/A'})"
    logger.info(f"Attempting to add track {item_details} to playlist {target_playlist_id} on {target_service}")
    try:
        if target_service == "spotify":
            sp = get_valid_spotify_client(); found_track_id = find_song_on_spotify(sp, isrc=track_isrc, title=track_title, artist=track_artist)
            if found_track_id: return HTMLResponse(f"<span style='color:green;'>Added.</span>" if sp_client_module.add_tracks_to_playlist(sp, target_playlist_id, [found_track_id]) else f"<span style='color:red;'>Failed.</span>")
            else: logger.warning(f"Track {item_details} not found on Spotify for add to playlist."); return HTMLResponse(f"<span style='color:orange;'>Not found.</span>")
        elif target_service == "deezer":
            token = get_valid_deezer_token(); found_track_id = find_song_on_deezer(token, isrc=track_isrc, title=track_title, artist=track_artist)
            if found_track_id: return HTMLResponse(f"<span style='color:green;'>Added.</span>" if dz_client_module.add_tracks_to_playlist(token, target_playlist_id, [found_track_id]) else f"<span style='color:red;'>Failed.</span>")
            else: logger.warning(f"Track {item_details} not found on Deezer for add to playlist."); return HTMLResponse(f"<span style='color:orange;'>Not found.</span>")
        elif target_service == "youtube":
            yt_service = get_valid_youtube_service(); found_track_id = find_song_on_youtube(yt_service, title=track_title, artist=track_artist)
            if found_track_id: return HTMLResponse(f"<span style='color:green;'>Added.</span>" if yt_client_module.add_video_to_playlist(yt_service, target_playlist_id, found_track_id) else f"<span style='color:red;'>Failed.</span>")
            else: logger.warning(f"Video for {item_details} not found on YouTube for add to playlist."); return HTMLResponse(f"<span style='color:orange;'>Not found.</span>")
        else: logger.error(f"Invalid target service '{target_service}' for add_track_to_playlist."); return HTMLResponse(f"<span style='color:red;'>Invalid target.</span>", status_code=400)
    except HTTPException as e: logger.warning(f"Auth error for {target_service} during add_track_to_playlist: {e.detail}"); return HTMLResponse(f"<span style='color:red;'>Login to {target_service.capitalize()}</span>")
    except Exception as e: logger.error(f"Error in /sync/playlist/add_track: {e}", exc_info=True); return HTMLResponse(f"<span style='color:red;'>Error.</span>", status_code=500)
@app.get("/me_display_page/{service_name}", response_class=HTMLResponse)
async def show_me_page(request: Request, service_name: str):
    # ... (condensed, assumed logging is added if/when this template is made more robust)
    user_info, error_msg = None, None
    try:
        if service_name == "spotify": sp = get_valid_spotify_client(); user_info = sp.me()
        elif service_name == "deezer": token = get_valid_deezer_token(); user_info = dz_client_module.get_deezer_user_info(token) # Corrected: get_deezer_user_info_util
        elif service_name == "youtube": service = get_valid_youtube_service(); user_info = service.channels().list(part="snippet", mine=True).execute()
        else: raise HTTPException(status_code=404, detail="Service not found")
    except HTTPException as e: error_msg = f"Please login to {service_name.capitalize()}." if e.status_code == 401 else e.detail
    except Exception as e: error_msg = str(e); logger.error(f"Error in me_display_page for {service_name}: {e}", exc_info=True)
    return templates.TemplateResponse("me_display.html", {"request": request, "service_name_capitalized": service_name.capitalize(), "user_info": user_info, "error_message": error_msg, "service_name_lower": service_name})

if __name__ == "__main__":
    import uvicorn
    logger.info(f"FastAPI app starting. Token file will be stored at: {os.path.abspath(token_store.TOKEN_FILE_PATH)}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
