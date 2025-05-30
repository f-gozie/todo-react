"""
Synchronization router for Music Sync Hub.

This module handles analyzing and synchronizing liked songs across different music platforms.
"""

from typing import Optional
from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# Internal imports
from ..utils.dependencies import (
    get_valid_spotify_client,
    get_valid_deezer_token,
    get_valid_youtube_service
)
from ..sync_manager import (
    sync_liked_songs,
    find_song_on_spotify,
    find_song_on_deezer,
    find_song_on_youtube
)
from ..spotify_client import add_liked_song as add_spotify_liked_song
from ..deezer_client import add_liked_song as add_deezer_liked_song
from ..youtube_client import add_liked_video as add_youtube_liked_video


router = APIRouter(prefix="/sync", tags=["synchronization"])
templates = Jinja2Templates(directory="templates")


@router.post("/liked/analyze", response_class=HTMLResponse)
async def analyze_liked_songs_sync(request: Request) -> HTMLResponse:
    """
    Analyze liked songs across all connected services and propose sync actions.
    
    Returns an HTML fragment for HTMX to update the sync results section.
    """
    auth_error_services = []
    
    # Check authentication for each service
    sp_client = get_valid_spotify_client(raise_exception=False)
    deezer_token = get_valid_deezer_token(raise_exception=False)
    youtube_service = get_valid_youtube_service(raise_exception=False)
    
    # Collect services that need authentication
    if not sp_client:
        auth_error_services.append("Spotify")
    # Deezer is currently disabled in sync
    # if not deezer_token:
    #     auth_error_services.append("Deezer")
    if not youtube_service:
        auth_error_services.append("YouTube")
    
    # Return auth error template if any services need authentication
    if auth_error_services:
        return templates.TemplateResponse(
            "_proposed_sync_actions.html",
            {
                "request": request,
                "auth_error_services": auth_error_services,
                "proposed_actions": None
            }
        )
    
    # Perform sync analysis
    try:
        proposed_actions = sync_liked_songs(sp_client, deezer_token, youtube_service)
        return templates.TemplateResponse(
            "_proposed_sync_actions.html",
            {
                "request": request,
                "proposed_actions": proposed_actions,
                "auth_error_services": None
            }
        )
    except Exception as e:
        print(f"Error during sync_liked_songs analysis: {e}")
        return templates.TemplateResponse(
            "_proposed_sync_actions.html",
            {
                "request": request,
                "proposed_actions": None,
                "analysis_error": f"An unexpected error occurred: {str(e)}."
            }
        )


@router.post("/liked/add", response_class=HTMLResponse)
async def add_liked_song_route(
    request: Request,
    isrc: Optional[str] = Form(None),
    title: str = Form(...),
    artist: Optional[str] = Form(None),
    target_service: str = Form(...)
) -> HTMLResponse:
    """
    Add a liked song to a specific service.
    
    Returns an HTML fragment for HTMX to update the action status.
    """
    item_details = f"'{title}' by '{artist if artist else 'N/A'}' (ISRC: {isrc if isrc else 'N/A'})"
    
    try:
        if target_service == "spotify":
            sp = get_valid_spotify_client()
            target_id = find_song_on_spotify(sp, isrc=isrc, title=title, artist=artist)
            
            if target_id:
                if add_spotify_liked_song(sp, target_id):
                    return HTMLResponse(
                        f"<span style='color:green;'>Successfully added {item_details} to Spotify.</span>"
                    )
                else:
                    return HTMLResponse(
                        f"<span style='color:red;'>Failed to add {item_details} to Spotify "
                        f"(already liked or error).</span>"
                    )
            else:
                return HTMLResponse(
                    f"<span style='color:orange;'>Song {item_details} not found on Spotify.</span>"
                )
                
        elif target_service == "deezer":
            token = get_valid_deezer_token()
            target_id = find_song_on_deezer(token, isrc=isrc, title=title, artist=artist)
            
            if target_id:
                if add_deezer_liked_song(token, target_id):
                    return HTMLResponse(
                        f"<span style='color:green;'>Successfully added {item_details} to Deezer.</span>"
                    )
                else:
                    return HTMLResponse(
                        f"<span style='color:red;'>Failed to add {item_details} to Deezer "
                        f"(already liked or error).</span>"
                    )
            else:
                return HTMLResponse(
                    f"<span style='color:orange;'>Song {item_details} not found on Deezer.</span>"
                )
                
        elif target_service == "youtube":
            yt_service = get_valid_youtube_service()
            target_id = find_song_on_youtube(yt_service, title=title, artist=artist)
            
            if target_id:
                if add_youtube_liked_video(yt_service, target_id):
                    return HTMLResponse(
                        f"<span style='color:green;'>Successfully liked video for {item_details} "
                        f"on YouTube.</span>"
                    )
                else:
                    return HTMLResponse(
                        f"<span style='color:red;'>Failed to like video for {item_details} "
                        f"on YouTube (already liked or error).</span>"
                    )
            else:
                return HTMLResponse(
                    f"<span style='color:orange;'>Video for {item_details} not found on YouTube.</span>"
                )
        else:
            return HTMLResponse(
                f"<span style='color:red;'>Invalid target service: {target_service}.</span>",
                status_code=400
            )
            
    except HTTPException as e:
        # For HTMX, return a user-friendly message instead of redirect
        login_url = f"/auth/{target_service}/login"
        return HTMLResponse(
            f"<span style='color:red;'>Please <a href='{login_url}' target='_blank'>"
            f"login to {target_service.capitalize()}</a> first.</span> ({e.detail})"
        )
    except Exception as e:
        print(f"Error in /sync/liked/add for {target_service} adding {item_details}: {e}")
        return HTMLResponse(
            f"<span style='color:red;'>An unexpected error occurred: {str(e)}.</span>",
            status_code=500
        ) 