from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
import json 

# Spotify imports
from .spotify_client import create_spotify_oauth as create_spotify_oauth_util
from .spotify_client import get_spotify_client as get_spotify_client_util
from .spotify_client import temporary_token_cache as spotify_temporary_token_cache
from .spotify_client import get_liked_songs as get_spotify_liked_songs
from .spotify_client import get_playlists as get_spotify_playlists
from .spotify_client import get_playlist_tracks as get_spotify_playlist_tracks
from .spotify_client import add_liked_song as add_spotify_liked_song # New
import spotipy 

# Deezer imports
from .deezer_client import get_deezer_auth_url as get_deezer_auth_url_util
from .deezer_client import get_deezer_access_token as get_deezer_access_token_util
from .deezer_client import get_deezer_user_info as get_deezer_user_info_util
from .deezer_client import temporary_token_cache as deezer_temporary_token_cache
from .deezer_client import get_liked_songs as get_deezer_liked_songs
from .deezer_client import get_playlists as get_deezer_playlists
from .deezer_client import get_playlist_tracks as get_deezer_playlist_tracks
from .deezer_client import add_liked_song as add_deezer_liked_song # New
import requests

# YouTube (Google) imports
from .youtube_client import create_youtube_flow as create_youtube_flow_util
from .youtube_client import get_youtube_client_service as get_youtube_service_util 
from .youtube_client import temporary_token_cache as youtube_temporary_token_cache
from .youtube_client import temporary_state_cache as youtube_temporary_state_cache 
from .youtube_client import get_liked_videos as get_youtube_liked_videos
from .youtube_client import get_playlists as get_youtube_playlists
from .youtube_client import get_playlist_items as get_youtube_playlist_items
from .youtube_client import add_liked_video as add_youtube_liked_video # New
from .config import YOUTUBE_SCOPES 
from google.oauth2.credentials import Credentials as GoogleCredentials
from google_auth_oauthlib.flow import Flow 
from google.auth.exceptions import OAuthError as GoogleOAuthError, RefreshError as GoogleRefreshError
from googleapiclient.errors import HttpError as GoogleHttpError

# Sync Manager import
from .sync_manager import sync_liked_songs
from .sync_manager import find_song_on_spotify, find_song_on_deezer, find_song_on_youtube # New


app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request): return templates.TemplateResponse("index.html", {"request": request, "title": "Home"})

# --- Client Getters with Auth Check (condensed) ---
def get_valid_spotify_client(raise_exception=True):
    token_info = spotify_temporary_token_cache.get('spotify_token_info')
    if not token_info:
        if raise_exception: raise HTTPException(status_code=401, detail="Not authenticated with Spotify.") # 401 for API
        return None
    return get_spotify_client_util(token_info)
def get_valid_deezer_token(raise_exception=True):
    access_token = deezer_temporary_token_cache.get('deezer_access_token')
    if not access_token:
        if raise_exception: raise HTTPException(status_code=401, detail="Not authenticated with Deezer.")
        return None
    return access_token
def get_valid_youtube_service(raise_exception=True):
    credentials_json_str = youtube_temporary_token_cache.get('youtube_credentials')
    if not credentials_json_str:
        if raise_exception: raise HTTPException(status_code=401, detail="Not authenticated with YouTube.")
        return None
    try: return get_youtube_service_util(credentials_json_str)
    except GoogleRefreshError as e: youtube_temporary_token_cache.pop('youtube_credentials', None); 
    if raise_exception: raise HTTPException(status_code=401, detail=f"YouTube token refresh failed: {e}.")
    return None
    except Exception as e: youtube_temporary_token_cache.pop('youtube_credentials', None); 
    if raise_exception: raise HTTPException(status_code=401, detail=f"Invalid YouTube credentials: {e}.")
    return None

# --- Auth Routes (condensed for brevity, no changes) ---
@app.get("/login/spotify")
async def login_spotify(): sp_oauth = create_spotify_oauth_util(); return RedirectResponse(sp_oauth.get_authorize_url())
@app.get("/callback/spotify")
async def callback_spotify(request: Request, code: str = None): 
    sp_oauth = create_spotify_oauth_util()
    if not code: return HTMLResponse(f"<html><body>Spotify login failed: {request.query_params.get('error', 'No code provided.')} <a href='/login/spotify'>Try again</a></body></html>", status_code=400)
    try: spotify_temporary_token_cache['spotify_token_info'] = sp_oauth.get_access_token(code, check_cache=False)
    except spotipy.SpotifyOauthError as e: return HTMLResponse(f"<html><body>Spotify Auth Error: {e} <a href='/'>Home</a></body></html>", status_code=400)
    return HTMLResponse("<html><body>Spotify Login Successful! <a href='/'>Home</a></body></html>")
@app.get("/login/deezer")
async def login_deezer(): return RedirectResponse(get_deezer_auth_url_util())
@app.get("/callback/deezer")
async def callback_deezer(request: Request, code: str = None, error_reason: str = None):
    if error_reason: return HTMLResponse(f"<html><body>Deezer login failed: {error_reason} <a href='/login/deezer'>Try again</a></body></html>", status_code=400)
    if not code: return HTMLResponse("<html><body>Deezer login failed: No code. <a href='/login/deezer'>Try again</a></body></html>", status_code=400)
    token = get_deezer_access_token_util(code)
    if not token: return HTMLResponse("<html><body>Deezer Token Error. <a href='/'>Home</a></body></html>", status_code=400)
    deezer_temporary_token_cache['deezer_access_token'] = token
    return HTMLResponse("<html><body>Deezer Login Successful! <a href='/'>Home</a></body></html>")
@app.get("/login/youtube")
async def login_youtube():
    try: flow = create_youtube_flow_util(); auth_url, state = flow.authorization_url(access_type='offline', prompt='consent'); youtube_temporary_state_cache['oauth_state'] = state; return RedirectResponse(auth_url)
    except Exception as e: return HTMLResponse(f"YouTube Login Error: {e}. Ensure 'client_secret_youtube.json' is configured. <a href='/'>Home</a>", status_code=500)
@app.get("/callback/youtube")
async def callback_youtube(request: Request, code: str = None, state: str = None, error: str = None):
    if error: return HTMLResponse(f"<html><body>YouTube login failed: {error} <a href='/login/youtube'>Try again</a></body></html>", status_code=400)
    if not code: return HTMLResponse("<html><body>YouTube login failed: No code. <a href='/login/youtube'>Try again</a></body></html>", status_code=400)
    try: flow = create_youtube_flow_util(); flow.fetch_token(code=code); youtube_temporary_token_cache['youtube_credentials'] = flow.credentials.to_json()
    except GoogleOAuthError as e: return HTMLResponse(f"<html><body>YouTube OAuth Error: {e} <a href='/'>Home</a></body></html>", status_code=400)
    return HTMLResponse("<html><body>YouTube Login Successful! <a href='/'>Home</a></body></html>")

# --- Data Endpoints (/me/*, /service/data/* - condensed for brevity, no changes) ---
@app.get("/me/spotify", response_class=HTMLResponse)
async def show_spotify_me(): 
    try: sp = get_valid_spotify_client(); user = sp.current_user(); return HTMLResponse(f"<h1>Hello, {user['display_name']}!</h1><pre>{json.dumps(user, indent=2)}</pre><a href='/'>Home</a>")
    except HTTPException: return RedirectResponse("/login/spotify") # Redirect if auth error from helper
    except Exception as e: return HTMLResponse(f"Error: {e} <a href='/'>Home</a>", status_code=500)
@app.get("/spotify/liked-songs", response_class=JSONResponse)
async def spotify_liked_songs(): 
    try: sp = get_valid_spotify_client(); return get_spotify_liked_songs(sp)
    except HTTPException as e: return JSONResponse(status_code=e.status_code, content={"detail": e.detail, "login_url":"/login/spotify"})
    except Exception as e: return JSONResponse(status_code=500, content={'detail': str(e)})
@app.get("/spotify/playlists", response_class=JSONResponse)
async def spotify_playlists():
    try: sp = get_valid_spotify_client(); return get_spotify_playlists(sp)
    except HTTPException as e: return JSONResponse(status_code=e.status_code, content={"detail": e.detail, "login_url":"/login/spotify"})
    except Exception as e: return JSONResponse(status_code=500, content={'detail': str(e)})
@app.get("/spotify/playlists/{playlist_id}/tracks", response_class=JSONResponse)
async def spotify_playlist_tracks_route(playlist_id: str):
    try: sp = get_valid_spotify_client(); return get_spotify_playlist_tracks(sp, playlist_id)
    except HTTPException as e: return JSONResponse(status_code=e.status_code, content={"detail": e.detail, "login_url":"/login/spotify"})
    except Exception as e: return JSONResponse(status_code=500, content={'detail': str(e)})
@app.get("/me/deezer", response_class=HTMLResponse)
async def show_deezer_me():
    try: token = get_valid_deezer_token(); user_info = get_deezer_user_info_util(token); return HTMLResponse(f"<h1>Hello, {user_info.get('name', 'User')}!</h1><pre>{json.dumps(user_info, indent=2)}</pre><a href='/'>Home</a>")
    except HTTPException: return RedirectResponse("/login/deezer")
    except Exception as e: return HTMLResponse(f"Error: {e} <a href='/'>Home</a>", status_code=500)
@app.get("/deezer/liked-songs", response_class=JSONResponse)
async def deezer_liked_songs():
    try: token = get_valid_deezer_token(); return get_deezer_liked_songs(token)
    except HTTPException as e: return JSONResponse(status_code=e.status_code, content={"detail": e.detail, "login_url":"/login/deezer"})
    except Exception as e: return JSONResponse(status_code=500, content={'detail': str(e)})
@app.get("/deezer/playlists", response_class=JSONResponse)
async def deezer_playlists():
    try: token = get_valid_deezer_token(); return get_deezer_playlists(token)
    except HTTPException as e: return JSONResponse(status_code=e.status_code, content={"detail": e.detail, "login_url":"/login/deezer"})
    except Exception as e: return JSONResponse(status_code=500, content={'detail': str(e)})
@app.get("/deezer/playlists/{playlist_id}/tracks", response_class=JSONResponse)
async def deezer_playlist_tracks_route(playlist_id: str):
    try: token = get_valid_deezer_token(); return get_deezer_playlist_tracks(token, playlist_id)
    except HTTPException as e: return JSONResponse(status_code=e.status_code, content={"detail": e.detail, "login_url":"/login/deezer"})
    except Exception as e: return JSONResponse(status_code=500, content={'detail': str(e)})
@app.get("/me/youtube", response_class=HTMLResponse)
async def show_youtube_me():
    try: service = get_valid_youtube_service(); response = service.channels().list(part="snippet", mine=True).execute(); return HTMLResponse(f"<h1>YouTube Channel</h1><pre>{json.dumps(response, indent=2)}</pre><a href='/'>Home</a>")
    except HTTPException: return RedirectResponse("/login/youtube")
    except GoogleHttpError as e: return HTMLResponse(f"YouTube API Error: {e._get_reason()} <a href='/login/youtube'>Login again</a>", status_code=e.resp.status)
    except Exception as e: return HTMLResponse(f"Error: {e} <a href='/'>Home</a>", status_code=500)
@app.get("/youtube/liked-videos", response_class=JSONResponse)
async def youtube_liked_videos():
    try: service = get_valid_youtube_service(); return get_youtube_liked_videos(service)
    except HTTPException as e: return JSONResponse(status_code=e.status_code, content={"detail": e.detail, "login_url":"/login/youtube"})
    except GoogleHttpError as e: return JSONResponse(status_code=e.resp.status, content={'detail': e._get_reason()})
    except Exception as e: return JSONResponse(status_code=500, content={'detail': str(e)})
@app.get("/youtube/playlists", response_class=JSONResponse)
async def youtube_playlists():
    try: service = get_valid_youtube_service(); return get_youtube_playlists(service)
    except HTTPException as e: return JSONResponse(status_code=e.status_code, content={"detail": e.detail, "login_url":"/login/youtube"})
    except GoogleHttpError as e: return JSONResponse(status_code=e.resp.status, content={'detail': e._get_reason()})
    except Exception as e: return JSONResponse(status_code=500, content={'detail': str(e)})
@app.get("/youtube/playlists/{playlist_id}/items", response_class=JSONResponse)
async def youtube_playlist_items_route(playlist_id: str):
    try: service = get_valid_youtube_service(); return get_youtube_playlist_items(service, playlist_id)
    except HTTPException as e: return JSONResponse(status_code=e.status_code, content={"detail": e.detail, "login_url":"/login/youtube"})
    except GoogleHttpError as e: return JSONResponse(status_code=e.resp.status, content={'detail': e._get_reason()})
    except Exception as e: return JSONResponse(status_code=500, content={'detail': str(e)})

# --- Sync Endpoints ---
@app.post("/sync/liked/analyze", response_class=HTMLResponse)
async def analyze_liked_songs_sync(request: Request):
    auth_error_services = []
    sp_client, deezer_token, youtube_service = None, None, None
    try: sp_client = get_valid_spotify_client(raise_exception=False)
    except HTTPException: pass # Already handled by returning None
    try: deezer_token = get_valid_deezer_token(raise_exception=False)
    except HTTPException: pass
    try: youtube_service = get_valid_youtube_service(raise_exception=False)
    except HTTPException: pass

    if not sp_client: auth_error_services.append("Spotify")
    if not deezer_token: auth_error_services.append("Deezer")
    if not youtube_service: auth_error_services.append("YouTube")
    
    if auth_error_services:
        return templates.TemplateResponse("_proposed_sync_actions.html", {"request": request, "auth_error_services": auth_error_services, "proposed_actions": None})
    try:
        proposed_actions = sync_liked_songs(sp_client, deezer_token, youtube_service)
        return templates.TemplateResponse("_proposed_sync_actions.html", {"request": request, "proposed_actions": proposed_actions, "auth_error_services": None})
    except Exception as e:
        print(f"Error during sync_liked_songs analysis: {e}")
        return templates.TemplateResponse("_proposed_sync_actions.html", {"request": request, "proposed_actions": None, "analysis_error": f"An unexpected error occurred: {str(e)}."})

@app.post("/sync/liked/add", response_class=HTMLResponse)
async def add_liked_song_route(
    request: Request,
    isrc: str = Form(None), 
    title: str = Form(...),
    artist: str = Form(None), # Artist might be None for some YouTube videos
    target_service: str = Form(...)
):
    item_details = f"'{title}' by '{artist if artist else 'N/A'}' (ISRC: {isrc if isrc else 'N/A'})"
    target_id = None
    
    try:
        if target_service == "spotify":
            sp = get_valid_spotify_client() # Raises HTTPException if not authed, caught by FastAPI
            target_id = find_song_on_spotify(sp, isrc=isrc, title=title, artist=artist)
            if target_id:
                if add_spotify_liked_song(sp, target_id):
                    return HTMLResponse(f"<span style='color:green;'>Successfully added {item_details} to Spotify.</span>")
                else:
                    return HTMLResponse(f"<span style='color:red;'>Failed to add {item_details} to Spotify (already liked or error).</span>")
            else:
                return HTMLResponse(f"<span style='color:orange;'>Song {item_details} not found on Spotify.</span>")

        elif target_service == "deezer":
            token = get_valid_deezer_token()
            target_id = find_song_on_deezer(token, isrc=isrc, title=title, artist=artist)
            if target_id:
                if add_deezer_liked_song(token, target_id):
                    return HTMLResponse(f"<span style='color:green;'>Successfully added {item_details} to Deezer.</span>")
                else:
                    return HTMLResponse(f"<span style='color:red;'>Failed to add {item_details} to Deezer (already liked or error).</span>")
            else:
                return HTMLResponse(f"<span style='color:orange;'>Song {item_details} not found on Deezer.</span>")

        elif target_service == "youtube":
            yt_service = get_valid_youtube_service()
            # YouTube finding doesn't use ISRC directly in find_song_on_youtube
            target_id = find_song_on_youtube(yt_service, title=title, artist=artist)
            if target_id:
                if add_youtube_liked_video(yt_service, target_id):
                    return HTMLResponse(f"<span style='color:green;'>Successfully liked video for {item_details} on YouTube.</span>")
                else:
                    return HTMLResponse(f"<span style='color:red;'>Failed to like video for {item_details} on YouTube (already liked or error).</span>")
            else:
                return HTMLResponse(f"<span style='color:orange;'>Video for {item_details} not found on YouTube.</span>")
        else:
            return HTMLResponse(f"<span style='color:red;'>Invalid target service: {target_service}.</span>", status_code=400)
            
    except HTTPException as e: # Handles auth errors from get_valid_* helpers
        # For HTMX, we want to return a user-friendly message in the target span, not a full redirect.
        login_url = f"/login/{target_service}"
        return HTMLResponse(f"<span style='color:red;'>Please <a href='{login_url}' target='_blank'>login to {target_service.capitalize()}</a> first.</span> ({e.detail})")
    except Exception as e:
        print(f"Error in /sync/liked/add for {target_service} adding {item_details}: {e}")
        return HTMLResponse(f"<span style='color:red;'>An unexpected error occurred: {str(e)}.</span>", status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
